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
.claude/skills/
├── manage-cycle/SKILL.md          # 스프린트/이슈 관리 (/manage-cycle)
└── init-project/SKILL.md          # 하네스 초기화 (/init-project)
docs/
├── ARCHITECTURE.md                # 아키텍처 (리서치 후 결정)
├── REQUIREMENTS.md                # EARS 요구사항
├── QUALITY_RULES.md               # TDD, 코딩 규칙
├── CONVENTIONS.md                 # 브랜치/커밋 컨벤션
├── CODE_REVIEW.md                 # 코드 리뷰 규칙
├── RELIABILITY.md                 # 에러 처리 정책
├── SECURITY.md                    # 보안 정책
├── cycle/                         # 스프린트/이슈 관리
│   ├── backlog.md
│   ├── current-sprint.md
│   └── sprints/
└── superpowers/
    ├── specs/                     # 디자인 문서
    └── plans/                     # 구현 계획서
```

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

## 스킬

### /init-project
프로젝트 플랜을 받아서 `{{PLACEHOLDER}}`를 자동 치환. 대화형 또는 파일 기반.

### /manage-cycle
`docs/cycle/` 마크다운 파일 기반 스프린트 관리. 8개 커맨드: create-issue, create-sprint, status, update, backlog, plan-sprint, retrospective, next-sprint.

## 원칙

- **TDD 필수**: 실패하는 테스트 → 최소 구현 → 리팩토링
- **점진적 하네스**: 실수 2회 반복 → 규칙 추가. 문서로 안 되면 린터로 승격
- **squash merge**: main은 깔끔한 커밋 히스토리. feature 브랜치에서 작업
- **코드 리뷰 필수**: merge 전 `requesting-code-review` 스킬 사용
