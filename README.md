# agent-harness-boilerplate

AI 에이전트와 협업하기 위한 프로젝트 하네스 보일러플레이트. 새 프로젝트를 시작할 때 이 레포를 복제하고 `/init-project` 스킬로 초기화한다.

## 빠른 시작

```bash
# 1. 레포 복제
cp -r ~/dev/agent-harness-boilerplate ~/dev/my-new-project
cd ~/dev/my-new-project
rm -rf .git && git init

# 2. Claude Code에서 초기화
/init-project
# 또는
/init-project "path/to/project-plan.md"
```

## 구조

```
CLAUDE.md                          # 에이전트 진입점
.agents/skills/                    # 스킬 정본 (canonical) — 수정은 항상 여기서
├── init-project/                  # 하네스 초기화 (/init-project)
├── manage-cycle/                  # 스프린트/이슈 관리 (/manage-cycle)
├── commit/  pr/                   # 커밋·PR 게이트 (초안 승인)
├── cross-review/                  # 두 모델 교차 리뷰 + 반영 게이트
├── handoff/                       # 세션 핸드오프 메타프롬프트
├── work-log/  work-log-daily/     # 세션 작업일지 + 일별 종합
└── session-retrospective/         # 세션 회고 + 규칙 승격 (점진적 하네스 엔진)
.claude/
├── settings.json                  # Stop/StopFailure 훅 등록 + PostToolUse 스텁
├── hooks/worklog_capture.py       # work-log 자동 캡처 + nudge
└── skills/                        # .agents/skills/* 로의 symlink (노출본)
docs/
├── ARCHITECTURE.md REQUIREMENTS.md QUALITY_RULES.md CONVENTIONS.md
├── CODE_REVIEW.md RELIABILITY.md SECURITY.md DECISIONS.md
├── cycle/                         # 스프린트/이슈 (backlog, current-sprint, sprints/)
├── designs/                       # specs/ + plans/
├── work-log/                      # 세션 작업일지 (YYYY/MM/) + daily/ + raw/
└── mistake/                       # 회고·실수 인덱스 (INDEX.md, README.md)
```

> 스킬 정본은 `.agents/skills/`, `.claude/skills/` 는 symlink 노출본이다. 스킬을 고칠 땐 항상 `.agents/` 쪽을 수정한다.

## 하네스 문서

| 문서 | 불변/가변 | 설명 |
|------|----------|------|
| QUALITY_RULES.md | 불변 | TDD, progressive harness, 코딩/테스트 규칙 |
| CONVENTIONS.md | 대부분 불변 | 브랜치 전략, 커밋 형식, EARS 패턴 |
| CODE_REVIEW.md | 대부분 불변 | 리뷰 필수 원칙, 심각도 분류 |
| ARCHITECTURE.md | 대부분 가변 | 아키텍처 패턴 (init-project이 리서치 후 결정) |
| REQUIREMENTS.md | 반반 | EARS 참조(불변) + 도메인 분해(가변) |
| RELIABILITY.md | 반반 | 공통 정책(불변) + 프로젝트 특화(가변) |
| SECURITY.md | 반반 | 공통 원칙(불변) + 환경 변수(가변) |
| DECISIONS.md | 가변 | ADR — 기술적 결정과 근거 기록 |

## 스킬

### /init-project
프로젝트 플랜을 받아서 `{{PLACEHOLDER}}`를 자동 치환. 대화형 또는 파일 기반.

### /manage-cycle
`docs/cycle/` 마크다운 파일 기반 스프린트 관리. 8개 커맨드: create-issue, create-sprint, status, update, backlog, plan-sprint, retrospective, next-sprint.

### 게이트·세션 스킬

- **/commit** · **/pr** — 커밋·PR 생성 게이트. 메시지 초안을 사용자에게 검수받고, 금지 패턴을 grep 검증한 뒤에만 실행. 직접 `git commit`/`gh pr create` 를 대체한다.
- **/cross-review** — 서로 다른 두 모델의 독립 리뷰를 교차 실행하고 P1/P2/상충으로 수렴, 반영 게이트까지.
- **/handoff** — 세션 마무리 시 컨텍스트 저장 + "# 세션 핸드오프" 메타프롬프트 생성 + 클립보드 복사.
- **/work-log** · **/work-log-daily** — 세션 작업일지(`docs/work-log/YYYY/MM/`)와 일별 종합. Stop 훅이 작성 누락을 nudge 한다.
- **/session-retrospective** — 세션 실수를 회고해 규칙 승격을 제안하고 `docs/mistake/` 에 누적. 점진적 하네스의 기계적 엔진.

## 원칙

- **TDD 필수**: 실패하는 테스트 → 최소 구현 → 리팩토링
- **점진적 하네스**: 실수 2회 반복 → 규칙 추가. 문서로 안 되면 린터로 승격
- **squash merge**: main은 깔끔한 커밋 히스토리. feature 브랜치에서 작업
- **코드 리뷰 필수**: merge 전 `/review` 스킬 사용 (교차 검증은 `cross-review`)
