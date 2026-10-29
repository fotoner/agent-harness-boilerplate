# 기여

1. 이슈를 먼저 연다. 템플릿을 쓰고 종류·영역·우선순위 라벨을 붙인다. 규칙: [docs/issues.md](docs/issues.md).
2. `{{DEFAULT_BRANCH}}`에서 `<type>/<이슈 번호>-<짧은-이름>` 브랜치를 딴다.
3. 버그는 실패하는 시험을 먼저 쓴다. 작업 끝에 `scripts/check.sh --changed`를 돌린다.
4. PR은 `{{DEFAULT_BRANCH}}` 대상으로 연다. 템플릿의 네 칸을 채운다. CI가 검사와 본문 헤딩을 확인한다.
5. 안전 불변식([AGENTS.md](AGENTS.md))의 대상에 쓰는 코드는 사본·임시 경로에서 확인한 결과를 PR에 적는다.

기여한 코드는 [MIT](LICENSE)로 배포된다.
