#!/usr/bin/env python3
"""work-log 자동 기록 훅 (Claude Code + Codex CLI 공용).

도입 사유(점진적 하네스): 세션 마무리 시 work-log 작성이 수동(/work-log)이라
누락이 반복됨. Stop 훅으로
  (1) Layer 1 — 매 turn 원시 레코드를 docs/work-log/raw/YYYY-MM-DD.jsonl 에 적재
  (2) Layer 2 — 의미 있는 파일 변경이 있으면 세션당 최대 2회, 모델에게
      work-log 작성을 nudge ({"decision":"block","reason":...})
를 자동화한다. 안정성 장치: flock 단일 write, 오프셋 inode/size 검증 + resync,
빈 turn 메타 레코드, secrets redaction, stdout 은 decision JSON 외 무출력,
nudge 2회 캡 + 재무장 조건.

호출 형태:
  Claude Code Stop:        worklog_capture.py --harness claude --nudge
  Claude Code StopFailure: worklog_capture.py --harness claude
  Codex Stop:              worklog_capture.py --harness codex
어떤 실패에도 세션을 방해하지 않도록 모든 경로에서 exit 0.

프로젝트 루트는 CLAUDE_PROJECT_DIR 환경변수 → (없으면) 스크립트 위치로 도출한다.
비활성화: WORKLOG_HOOK_DISABLE=1.
"""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트: Claude Code 는 CLAUDE_PROJECT_DIR 을 준다. Codex 등 미설정
# 환경에서는 스크립트 위치(<root>/.claude/hooks/worklog_capture.py)로 도출.
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or str(Path(__file__).resolve().parents[2])
ROOT = os.path.realpath(ROOT)
STATE_DIR = Path(ROOT) / ".claude" / "state" / "worklog"
RAW_DIR = Path(ROOT) / "docs" / "work-log" / "raw"
STATE_TTL_DAYS = 7
PROMPT_MAX = 300

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

# Bash로만 파일을 바꾸는 세션 누락 보완용 휴리스틱 (Layer 2).
BASH_WRITE_RE = re.compile(r"git commit|mv |cp |rm |sed -i|tee |>>")

# Codex apply_patch 마커
APPLY_PATCH_RE = re.compile(r"\*\*\* (?:Update|Add|Delete) File: ([^\n\\\"]+)")

# raw 로그가 docs/ 아래에 남으므로 프롬프트 발췌의 secrets는 치환한다.
REDACT_RE = re.compile(
    r"(sk-[A-Za-z0-9_\-]{8,}"
    r"|ghp_[A-Za-z0-9]{8,}"
    r"|github_pat_[A-Za-z0-9_]{8,}"
    r"|xox[a-z]-[A-Za-z0-9\-]+"
    r"|AKIA[0-9A-Z]{12,}"
    r"|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}"
    r"|(?i:bearer)\s+[A-Za-z0-9._\-]{8,}"
    r"|(?i:password|token|secret|api[_-]?key)\s*[=:]\s*\S+)"
)

NUDGE_REASON = """[work-log 훅] 이번 세션에서 파일 변경(Edit/Write)이 감지되었으나 docs/work-log/ 아래에
작업일지가 아직 없습니다. 아래 중 하나로 스스로 판단해 행동하세요.

1) 사용자가 요청한 작업이 완결된 상태라면 — .claude/skills/work-log/SKILL.md 의 형식과
   절차(4개 섹션, docs/work-log/YYYY/MM/"YYYY-MM-DD - 작업이름.md", 중복 시 -2 접미사)에
   따라 작업일지를 작성하고, 저장 경로를 1줄로 보고한 뒤 멈추세요.
   docs/work-log/raw/<오늘날짜>.jsonl 이 있으면 변경 파일 목록과 타임라인 확인용
   소스로만 활용하고, 그 경로를 본문에 링크하거나 언급하지 마세요.

2) 작업이 아직 진행 중이거나, 변경이 일지로 남길 가치가 없는 잡무(설정 토글, 오타 수정 등)
   라면 — 작업일지를 작성하지 말고, 한 줄로 사유만 남기고 멈추세요(진행 중이면 계속하세요).

이 알림은 세션당 최대 2회만 발생합니다."""


def log_err(msg):
    print(f"worklog_capture: {msg}", file=sys.stderr)


def redact(text):
    return REDACT_RE.sub("[REDACTED]", text)


def rel_path(p):
    if p.startswith(ROOT + "/"):
        return p[len(ROOT) + 1:]
    return p


def cleanup_old_state():
    cutoff = time.time() - STATE_TTL_DAYS * 86400
    try:
        for f in STATE_DIR.iterdir():
            try:
                if f.is_file() and f.stat().st_mtime < cutoff:
                    f.unlink()
            except OSError:
                pass
    except OSError:
        pass


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, obj):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(obj), encoding="utf-8")
    tmp.replace(path)


def append_locked(path, record):
    line = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, line)  # 레코드 1개 = write 1회 (동시 append 경합 대비)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def read_new_lines(tpath, offset_file):
    """오프셋 이후의 완결된 라인만 반환. (lines, resync여부)

    transcript 포맷/파일은 비안정 표면 — inode 교체나 축소(rewrite/compaction/
    resume)가 감지되면 중복 적재를 피하기 위해 해당 구간을 포기(resync)하고
    오프셋을 EOF로 재설정한다.
    """
    st = os.stat(tpath)
    state = load_json(offset_file, None)
    if state is not None and (
        state.get("inode") != st.st_ino or st.st_size < state.get("offset", 0)
    ):
        save_json(offset_file, {"offset": st.st_size, "inode": st.st_ino,
                                "size": st.st_size})
        return [], True
    start = state.get("offset", 0) if state else 0
    with open(tpath, "rb") as f:
        f.seek(start)
        chunk = f.read()
    last_nl = chunk.rfind(b"\n")
    if last_nl == -1:
        lines, new_off = [], start
    else:
        lines = chunk[:last_nl].split(b"\n")
        new_off = start + last_nl + 1
    save_json(offset_file, {"offset": new_off, "inode": st.st_ino,
                            "size": st.st_size})
    return lines, False


def new_summary():
    return {"prompt": None, "tool_counts": {}, "files_changed": [],
            "bash_writes": 0, "worklog_written": False}


def parse_claude_lines(lines, summary):
    for raw in lines:
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        rtype = rec.get("type")
        if rtype == "user":
            content = (rec.get("message") or {}).get("content")
            text = None
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                parts = [c.get("text", "") for c in content
                         if isinstance(c, dict) and c.get("type") == "text"]
                text = "\n".join(p for p in parts if p) or None
            # <command-...>/<local-command-...> 등 슬래시 커맨드 잔여물 제외
            if text and not text.lstrip().startswith("<"):
                summary["prompt"] = text
        elif rtype == "assistant":
            content = (rec.get("message") or {}).get("content") or []
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                name = item.get("name", "?")
                summary["tool_counts"][name] = summary["tool_counts"].get(name, 0) + 1
                tool_input = item.get("input") or {}
                if name in EDIT_TOOLS:
                    fp = tool_input.get("file_path") or tool_input.get("notebook_path")
                    if fp:
                        rp = rel_path(fp)
                        if rp not in summary["files_changed"]:
                            summary["files_changed"].append(rp)
                        if ("docs/work-log/" in fp
                                and "docs/work-log/raw/" not in fp):
                            summary["worklog_written"] = True
                elif name == "Bash":
                    cmd = tool_input.get("command") or ""
                    if BASH_WRITE_RE.search(cmd):
                        summary["bash_writes"] += 1
    return summary


def parse_codex_lines(lines, summary):
    for raw in lines:
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        payload = rec.get("payload") or {}
        rtype = rec.get("type")
        if rtype == "event_msg" and payload.get("type") == "user_message":
            msg = payload.get("message")
            if msg:
                summary["prompt"] = msg
        elif rtype == "response_item" and payload.get("type") in (
                "function_call", "custom_tool_call"):
            name = payload.get("name", "?")
            summary["tool_counts"][name] = summary["tool_counts"].get(name, 0) + 1
            args = payload.get("arguments") or payload.get("input") or ""
            if not isinstance(args, str):
                args = json.dumps(args, ensure_ascii=False)
            for fp in APPLY_PATCH_RE.findall(args):
                rp = rel_path(fp.strip())
                if rp not in summary["files_changed"]:
                    summary["files_changed"].append(rp)
                if ("docs/work-log/" in fp
                        and "docs/work-log/raw/" not in fp):
                    summary["worklog_written"] = True
            if name == "exec_command":
                try:
                    cmd = json.loads(args).get("cmd", "")
                except ValueError:
                    cmd = args
                if isinstance(cmd, list):
                    cmd = " ".join(str(c) for c in cmd)
                if BASH_WRITE_RE.search(cmd):
                    summary["bash_writes"] += 1
    return summary


def parse_lines(lines, harness):
    summary = new_summary()
    if harness == "claude":
        return parse_claude_lines(lines, summary)
    return parse_codex_lines(lines, summary)


def scan_full_transcript(tpath, harness):
    with open(tpath, "rb") as f:
        lines = f.read().split(b"\n")
    return parse_lines(lines, harness)


def collect_uncommitted():
    """현재 레포의 미커밋 변경 파일 수. 실패는 조용히 건너뜀 (캡처 비차단).

    커밋/푸시 이월이 다음 세션 브랜치 오염으로 이어지는 패턴을 방어하기 위해
    nudge reason 에 함께 노출한다.
    """
    out = {}
    if not os.path.exists(os.path.join(ROOT, ".git")):  # worktree 는 .git 이 파일(포인터)
        return out
    try:
        r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            n = len([l for l in r.stdout.splitlines() if l.strip()])
            if n:
                out[os.path.basename(ROOT)] = n
    except Exception:
        pass
    return out


def meaningful_count(summary):
    edits = sum(summary["tool_counts"].get(t, 0) for t in EDIT_TOOLS)
    return edits + summary["bash_writes"]


def decide_nudge(data, tpath, sid):
    """nudge 여부 결정. 차단 사유가 없고 의미 있는 작업이 있으면 True."""
    if data.get("stop_hook_active"):
        return False  # block으로 이어진 turn — 루프 방지 1차 가드
    if data.get("permission_mode") == "plan":
        return False
    if data.get("background_tasks"):
        return False  # 대기 중 백그라운드 작업 = 완료 상태 아님
    if not tpath:
        return False
    nudge_file = STATE_DIR / f"nudge-{sid}.json"
    state = load_json(nudge_file, {"count": 0, "confirmed": False,
                                   "meaningful_at_last_nudge": 0})
    if state.get("confirmed"):
        return False
    full = scan_full_transcript(tpath, "claude")
    if full["worklog_written"]:
        state["confirmed"] = True
        save_json(nudge_file, state)
        return False
    count = state.get("count", 0)
    if count >= 2:
        return False
    meaningful = meaningful_count(full)
    if meaningful < 1:
        return False
    # 재무장 조건: 마지막 nudge 이후 새 변경이 있어야 2번째 nudge 허용
    if count == 1 and meaningful <= state.get("meaningful_at_last_nudge", 0):
        return False
    state["count"] = count + 1
    state["meaningful_at_last_nudge"] = meaningful
    save_json(nudge_file, state)
    return True


def main():
    if os.environ.get("WORKLOG_HOOK_DISABLE") == "1":
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", required=True, choices=["claude", "codex"])
    parser.add_argument("--nudge", action="store_true")
    args = parser.parse_args()

    data = json.load(sys.stdin)
    cwd = os.path.realpath(data.get("cwd") or "")
    # 적용 범위: 프로젝트 루트(또는 그 하위)에서 시작한 세션만
    if not (cwd == ROOT or cwd.startswith(ROOT + os.sep)):
        return

    sid = str(data.get("session_id") or "unknown")
    event = data.get("hook_event_name") or "Stop"
    tpath = data.get("transcript_path")
    if tpath:
        tpath = os.path.expanduser(tpath)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_old_state()

    # ---- Layer 1: 캡처 ----
    summary = new_summary()
    if not tpath or not os.path.isfile(tpath):
        status = "meta-only"
    else:
        try:
            offset_file = STATE_DIR / f"offset-{args.harness}-{sid}.json"
            lines, resynced = read_new_lines(tpath, offset_file)
            if resynced:
                status = "resync"
            elif not lines:
                status = "empty-turn"
            else:
                summary = parse_lines(lines, args.harness)
                status = "ok"
        except OSError as e:
            log_err(f"capture read failed: {e}")
            status = "meta-only"
    if event == "StopFailure":
        status = "stop-failure"

    # ---- Layer 2: nudge 결정 (레코드의 nudged 필드에 반영하기 위해 먼저) ----
    nudged = False
    if args.nudge and args.harness == "claude" and status in ("ok", "empty-turn"):
        try:
            nudged = decide_nudge(data, tpath, sid)
        except Exception as e:  # nudge 실패가 캡처를 막으면 안 됨
            log_err(f"nudge decision failed: {e}")

    uncommitted = collect_uncommitted()
    record = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "harness": args.harness,
        "session_id": sid,
        "event": event,
        "status": status,
        "prompt": redact(summary["prompt"][:PROMPT_MAX]) if summary["prompt"] else None,
        "tool_counts": summary["tool_counts"],
        "files_changed": summary["files_changed"],
        "uncommitted": uncommitted,
        "nudged": nudged,
    }
    raw_file = RAW_DIR / f"{datetime.now().astimezone().date().isoformat()}.jsonl"
    append_locked(raw_file, record)

    if nudged:
        reason = NUDGE_REASON
        if uncommitted:
            detail = ", ".join(f"{r} {n}건" for r, n in sorted(uncommitted.items()))
            reason += f"\n\n참고: 미커밋 변경이 남아 있습니다 — {detail}. 작업일지의 남은 작업에 반영하세요."
        # stdout은 decision JSON 단 한 줄만 — 그 외 출력은 하네스 파싱을 깨뜨림
        print(json.dumps({"decision": "block", "reason": reason},
                         ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_err(f"fatal: {e}")
    sys.exit(0)
