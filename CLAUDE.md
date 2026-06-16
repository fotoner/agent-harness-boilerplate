# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## 기술 스택

{{TECH_STACK}}

## 아키텍처

{{ARCHITECTURE_STYLE}}

{{LAYER_DIAGRAM}}

교차 관심사(로깅, HTTP 등)는 유틸리티 모듈을 통해서만 접근.

상세: `docs/ARCHITECTURE.md`

## 핵심 규칙

### TDD 필수
1. 실패하는 테스트 먼저 작성
2. 테스트를 통과하는 최소한의 코드만 구현
3. 리팩토링 시 테스트가 여전히 통과하는지 확인
- 단위 테스트가 어려운 영역(인프라 IaC 등)은 plan/apply diff 확인으로 갈음한다.

### 브랜치 전략
- `main`에 직접 커밋 금지. 모든 작업은 feature 브랜치에서 수행
- 관련 이슈를 논리적 단위로 묶어 1개 브랜치로 작업
- **squash merge 전 코드 리뷰 필수** (`/review`)
- 완료 후 squash and merge로 main에 통합
- 상세: `docs/CONVENTIONS.md`

### 코딩
- 타입 안전성 위반 금지 — 명시적 타입 선언
- 디버그 출력 금지 — 구조화된 로거 사용
- 외부 데이터는 경계에서 검증
- 파일 최대 300줄, 함수 최대 50줄

### 점진적 하네스
- 에이전트가 같은 실수 2회 반복 → 이 파일 또는 QUALITY_RULES.md에 규칙 추가
- 문서 규칙으로도 위반 반복 → `.claude/settings.json` 훅으로 승격하여 기계적 강제
- 훅으로도 부족 → CI 린터로 최종 승격
- 규칙 추가 시 **어떤 실패가 반복되었는지**를 `(트리거: ...)` 주석으로 기록한다. 반복 패턴 추적·격상은 `session-retrospective` 스킬 + `docs/mistake/` 가 자동화한다.

## 에이전트 운영 규율

### 커밋·PR 게이트
커밋과 PR 은 `commit` / `pr` 스킬 절차로만 수행한다. 에이전트가 자체 판단으로 `git commit` / `gh pr create` 를 직접 실행하지 않으며, 두 스킬의 **초안 승인 게이트**를 생략하지 않는다. 도구 실행 승인(권한 모드 / approval policy)은 초안 콘텐츠 승인을 대체하지 않는다.
- **예외**: 사용자가 승인한 플랜에 **커밋 단위와 메시지 형식**이 함께 명시된 경우, 그 플랜 실행 중의 task 커밋은 게이트를 충족한 것으로 본다 — 단 커밋 후 금지 패턴 grep 검증(아래)을 수행한다.

### Subagent 결과 검증
큰 task 를 implementer subagent 에 dispatch 할 때, prompt 에 규칙을 적는 것만으로 충분하지 않다. subagent 작업이 끝나면 dispatcher 가 결과물을 직접 검증한다 — 변경된 commit subject/body/파일명/코드/주석에서 프로젝트 금지 패턴(`docs/QUALITY_RULES.md`)이 잔존하는지 grep 한다. 활성 제약은 매 subagent prompt 에 다시 포함한다.

### 대량 스캔·감사 교차 검증
병렬 에이전트가 생성한 다건 발견 스캔/감사/리뷰 보고서는 독립 교차 검증(`cross-review` 스킬 — 다른 모델 또는 독립 세션)을 거친 뒤에만 정본 문서로 저장하거나 의사결정에 사용한다.

### 구현 플랜 전제 검증
구현 플랜을 작성·리뷰할 때 플랜이 딛는 핵심 전제(기존 모듈 존재, 라우트 실존, API 시그니처, 테스트 인프라 유무)를 grep/read 로 실제 코드에서 확인한다. 스펙 문서만 보고 구조를 가정하지 않는다. 기존 유사 모듈이 있으면 신규 추상화 대신 그 위에서 확장한다.

### 작업일지 자동 기록
세션 작업 기록은 Stop 훅(`.claude/hooks/worklog_capture.py`)이 자동화한다 — 매 turn 원시 레코드를 `docs/work-log/raw/` 에 적재하고, 파일 변경 후 작업일지가 없으면 세션당 최대 2회 작성을 nudge 한다. nudge 를 받으면: 작업이 완결됐으면 `work-log` 스킬 형식으로 작성하고 경로를 1줄 보고, 진행 중·잡무면 한 줄 사유만 남기고 멈춘다. 훅 일시 중지는 `WORKLOG_HOOK_DISABLE=1`.

### 세션 회고 (점진적 하네스 엔진)
반복된 실수는 `session-retrospective` 스킬로 회고하고 규칙 승격을 제안한다. 회고 기록은 `docs/mistake/` 에 누적되며, 같은 패턴 태그가 임계치를 넘으면 규칙 보강 → 린터/훅 승격으로 자동 격상된다.

## 프로젝트 관리

- **이슈/스프린트**: `docs/cycle/` (마크다운 기반)
- **스프린트**: 1주 단위 (월요일 시작)
- **작업 제목 형식**: `[D{도메인}.{번호}][EARS패턴] 요구사항 설명`
- **스킬**: `/manage-cycle` 로 이슈/스프린트 관리

## 문서 참조

| 문서 | 내용 |
|------|------|
| `docs/ARCHITECTURE.md` | 아키텍처 맵, 의존성 방향 규칙 |
| `docs/REQUIREMENTS.md` | EARS 기반 요구사항 (MECE 도메인별) |
| `docs/QUALITY_RULES.md` | TDD + 코딩 + 아키텍처 제약 규칙 |
| `docs/CONVENTIONS.md` | 작업/커밋/PR 컨벤션 |
| `docs/CODE_REVIEW.md` | 코드 리뷰 필수 규칙, 리뷰 관점 |
| `docs/RELIABILITY.md` | 에러 처리 정책, 데이터 무결성 |
| `docs/SECURITY.md` | 환경 변수 관리, 데이터 보호 |
| `docs/DECISIONS.md` | ADR (Architecture Decision Records) |
| `docs/work-log/` | 세션 작업일지 + 일별 종합 (`work-log` / `work-log-daily` 스킬) |
| `docs/mistake/` | 세션 회고·실수 인덱스 (`session-retrospective` 스킬, 점진적 하네스 엔진) |

## 디렉토리 구조

{{DIRECTORY_STRUCTURE}}

## Skill routing

사용자 요청이 가용 스킬과 매칭되면, 항상 Skill 도구로 먼저 호출한다.
직접 답변하지 말고, 다른 도구를 먼저 쓰지 않는다.

주요 라우팅 규칙:
- 제품 아이디어, "이거 만들 가치 있어?", 브레인스토밍 → office-hours
- 버그, 에러, "왜 안 돼", 500 에러 → investigate
- 배포·전체 릴리스 통합 → ship (단, 커밋/PR 생성은 아래 게이트 스킬 `commit`/`pr` 가 우선)
- QA, 사이트 테스트, 버그 찾기 → qa
- 코드 리뷰, diff 확인 → review
- 배포 후 문서 업데이트 → document-release
- 주간 회고 → retro
- 디자인 시스템, 브랜드 → design-consultation
- 시각적 검수, 디자인 폴리시 → design-review
- 아키텍처 리뷰 → plan-eng-review
- 진행 상황 저장, 체크포인트 → checkpoint
- 코드 품질, 헬스 체크 → health

### 게이트·세션 스킬 (이 레포 정본)

아래 스킬은 이 하네스가 직접 제공하며, 커밋/PR 생성 등에서는 gstack `ship` 보다 **우선**한다 (초안 승인 게이트를 거치기 때문).

- 커밋 → `commit` (초안 검수 게이트 — 직접 `git commit` 금지)
- PR 생성 → `pr` (브랜치명·본문 검수 게이트 — 직접 `gh pr create` 금지)
- 교차 리뷰 / "다른 모델한테도 리뷰시켜" → `cross-review`
- 병렬 에이전트 스캔/감사 보고서를 정본화·저장하기 전 → `cross-review` 로 교차 검증
- 세션 마무리 / "컨텍스트 저장하고 메타프롬프트" → `handoff`
- 첫 메시지가 "# 세션 핸드오프"로 시작하면 → 그 안의 컨텍스트 복원 지시와 작업 순서를 그대로 실행
- 세션 작업일지 → `work-log`, 하루 종합 → `work-log-daily`
- 세션 회고 / "CLAUDE.md 보강할 것 있어?" → `session-retrospective`

> 스킬 정본은 `.agents/skills/`, `.claude/skills/` 의 동명 항목은 symlink 노출본이다. **스킬 수정은 항상 `.agents/` 쪽에서** 한다.
