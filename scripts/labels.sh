#!/usr/bin/env bash
# 표준 라벨을 만든다. 이미 있으면 색·설명만 맞춘다. 규칙: docs/issues.md "라벨".
# 사용: scripts/labels.sh [영역 이름…]   예: scripts/labels.sh app api ci
set -euo pipefail
mk() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null && echo "라벨: $1"; }
mk feature  1d76db "새 기능·기능 개선"
mk bug      d73a4a "잘못 동작함"
mk research 5319e7 "결과가 지식인 일. 결론은 댓글과 docs로"
mk chore    c5def5 "정리·리팩터링·빌드·도구"
mk perf     fbca04 "동작을 유지하는 성능 측정·개선"
mk docs     0075ca "문서"
mk epic     3e4b9e "상위 이슈. 하위 이슈를 묶기만 한다"
mk P0 b60205 "데이터 손실·보안·운영 장애. 먼저"
mk P1 d93f0b "다음에 할 것"
mk P2 fbca04 "할 것, 순서 미정"
mk P3 c2e0c6 "아이디어. 할지 아직 정하지 않음"
mk needs:decision   d4c5f9 "사람이 정할 것이 남음"
mk needs:device     d4c5f9 "실기기·실물 확인이 있어야 진행됨"
mk needs:experiment d4c5f9 "사용자가 직접 해 보는 실험이 있어야 진행됨"
for a in "$@"; do mk "area:$a" ededed "영역: $a"; done
