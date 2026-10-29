#!/usr/bin/env bash
# 검사 사다리. AGENTS.md "검증" 표와 CI(.github/workflows/check.yml)가 이 스크립트를 부른다.
#   scripts/check.sh --quick [--filter <시험>]   편집 중: 문서 검사 + 시험(필터)
#   scripts/check.sh --changed [--base <rev>]    작업 끝·PR: 바뀐 것에 닿는 검사(문서만 바뀌면 문서 검사만)
#   scripts/check.sh                             기본 브랜치·릴리스: 전체(린트·타입·시험·빌드)
# 종료 코드: 0 통과, 1 실패, 2 잘못된 인자.
set -euo pipefail
cd "$(dirname "$0")/.."

# ── 프로젝트 명령. 비어 있으면 그 단계는 "미설정"으로 건너뛴다 ──
LINT_CMD=""        # 예: npm run lint
TYPECHECK_CMD=""   # 예: npx tsc --noEmit
TEST_CMD=""        # 예: npx vitest run   (--quick의 필터는 뒤에 붙는다)
BUILD_CMD=""       # 예: npm run build
DOC_ONLY='(\.md$|^docs/|^\.github/ISSUE_TEMPLATE/|^LICENSE$)'

mode=full filter="" base=""
while [ $# -gt 0 ]; do
  case "$1" in
    --quick) mode=quick ;;
    --changed) mode=changed ;;
    --filter) [ $# -ge 2 ] || { echo "--filter 뒤에 값이 필요하다" >&2; exit 2; }; filter="$2"; shift ;;
    --base) [ $# -ge 2 ] || { echo "--base 뒤에 값이 필요하다" >&2; exit 2; }; base="$2"; shift ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 2 ;;
  esac
  shift
done
if [ -n "$filter" ] && [ "$mode" != quick ]; then echo "--filter는 --quick과만 쓴다" >&2; exit 2; fi
if [ -n "$base" ] && [ "$mode" != changed ]; then echo "--base는 --changed와만 쓴다" >&2; exit 2; fi

failed=0
step() {  # step <이름> <명령>
  if [ -z "$2" ]; then echo "── $1: 미설정"; return 0; fi
  echo "── $1: $2"
  if bash -c "$2"; then echo "   통과"; else echo "   실패"; failed=1; fi
}

step "문서" "python3 scripts/check-docs.py"
case "$mode" in
  quick)
    step "시험" "${TEST_CMD:+$TEST_CMD $filter}" ;;
  changed)
    if [ -z "$base" ]; then
      ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)
      base=$(git merge-base HEAD "$ref" 2>/dev/null || echo HEAD)
    fi
    files=$({ git diff --name-only "$base"; git ls-files --others --exclude-standard; } | sort -u)
    echo "── 바뀐 파일 $(printf '%s\n' "$files" | grep -c . || true)개 (기준 $base)"
    if [ -n "$files" ] && ! printf '%s\n' "$files" | grep -qvE "$DOC_ONLY"; then
      echo "── 문서만 바뀌었다. 린트·타입·시험을 건너뛴다"
    else
      step "린트" "$LINT_CMD"; step "타입" "$TYPECHECK_CMD"; step "시험" "$TEST_CMD"
    fi ;;
  full)
    step "린트" "$LINT_CMD"; step "타입" "$TYPECHECK_CMD"; step "시험" "$TEST_CMD"; step "빌드" "$BUILD_CMD" ;;
esac

if [ "$failed" -eq 0 ]; then echo "── 검사 통과"; else echo "── 검사 실패"; fi
exit "$failed"
