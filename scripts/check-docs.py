#!/usr/bin/env python3
"""문서 검사. AGENTS.md 크기(목표 12KiB, 한도 16KiB), 문서 안 상대 링크, 채우지 않은 자리표시자({{…}}, 경고)를 본다.
종료 코드: 0 통과, 1 오류."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET, LIMIT = 12 * 1024, 16 * 1024
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

docs = [ROOT / n for n in ("AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "README.md")]
docs += sorted((ROOT / "docs").rglob("*.md")) + sorted((ROOT / ".claude" / "rules").glob("*.md"))
errors, warns = [], []

size = (ROOT / "AGENTS.md").stat().st_size
if size > LIMIT:
    errors.append(f"AGENTS.md {size}B > 한도 {LIMIT}B. 한 경로에만 해당하는 규칙은 .claude/rules/로 옮긴다")
elif size > TARGET:
    warns.append(f"AGENTS.md {size}B > 목표 {TARGET}B")

for path in docs:
    if not path.exists():
        continue
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target):
            continue  # http:, mailto: 등 바깥 주소
        if not (path.parent / target).exists():
            errors.append(f"{rel}: 없는 링크 {target}")
    if "{{" in text:
        warns.append(f"{rel}: 채우지 않은 자리표시자가 있다")

for w in warns:
    print("경고:", w)
for e in errors:
    print("오류:", e)
print("문서 검사 통과" if not errors else f"문서 검사 오류 {len(errors)}개")
sys.exit(1 if errors else 0)
