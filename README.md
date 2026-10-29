# agent-harness-boilerplate

에이전트와 함께 운영하는 저장소의 시작 틀. 할 일은 GitHub 이슈, 작업은 PR, 지침은 AGENTS.md 하나다.

## 시작

```bash
git clone --depth 1 https://github.com/fotoner/agent-harness-boilerplate my-project
cd my-project && rm -rf .git && git init
```

1. `AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `.github/ISSUE_TEMPLATE/config.yml`의 `{{…}}`를 채운다.
2. `scripts/check.sh` 위쪽의 명령(린트·타입·시험·빌드)을 채우고, `.github/workflows/check.yml`의 브랜치 이름을 기본 브랜치에 맞춘다.
3. GitHub 저장소를 만든 뒤 `scripts/labels.sh <영역…>`으로 라벨을 만든다.

[fstack](https://github.com/fotoner/fstack)이 있으면 `harness` 스킬이 1·2를 채운다.

## 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| `AGENTS.md` | 정본 지침: 안전 불변식, 명령, 검증, 지도, 구조, 작업 규칙. 12KiB 목표, 16KiB 한도 |
| `CLAUDE.md` | `@AGENTS.md`와 Claude Code 전용 두 줄 |
| `CONTRIBUTING.md` | 기여 절차 |
| `docs/issues.md` | 이슈 제목·라벨·본문·조사 근거 표기·흐름 |
| `docs/architecture.md` | 의존 방향, 모듈, 쓰기 관문 |
| `.github/ISSUE_TEMPLATE/` | 기능·버그·조사·상위 이슈 템플릿. 빈 이슈는 막는다 |
| `.github/pull_request_template.md` | 무엇을 바꿨나 · 확인한 것 · 위험 경로 · 관련 이슈 |
| `.github/workflows/check.yml` | PR은 `check.sh --changed`, 기본 브랜치는 전체 검사 |
| `.github/workflows/pr-body.yml` | PR 본문의 필수 헤딩 검사 |
| `scripts/check.sh` | 검사 사다리 `--quick` / `--changed` / 전체 |
| `scripts/check-docs.py` | AGENTS.md 크기, 문서 링크, 남은 자리표시자 |
| `scripts/labels.sh` | 종류·우선순위·`needs:`·영역 라벨 |

커밋·PR·리뷰·QA·인계·교정 기록은 이 저장소가 아니라 에이전트 쪽 스킬(fstack)이 맡는다. 이 저장소는 그 스킬이 읽는 저장소 쪽 규칙을 준다.

## 라이선스

[MIT](LICENSE)
