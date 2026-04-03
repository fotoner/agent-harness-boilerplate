---
name: manage-cycle
description: >-
  docs/cycle 기반 스프린트/이슈 관리 스킬. EARS 형식으로 이슈를 생성하고,
  1주 단위 스프린트를 마크다운 파일로 관리한다.

  사용 시나리오:
  - 새 이슈/작업 생성 (EARS 형식)
  - 스프린트 생성 및 작업 할당
  - 현재 스프린트 상태 확인
  - 작업 상태 업데이트
  - 백로그 조회
  - 스프린트 회고 및 문서 동기화
  - 스프린트 전환 (회고 → 다음 계획)
---

# manage-cycle

docs/cycle 기반 마크다운 스프린트/이슈 관리 스킬.

## 파일 구조

```
docs/cycle/
├── backlog.md           # 미할당 이슈 목록 (source of truth)
├── current-sprint.md    # 활성 스프린트 보드
└── sprints/             # 완료된 스프린트 아카이브
    ├── sprint-01.md
    ├── sprint-02.md
    └── sprint-00-template.md  # 스프린트 파일 템플릿
```

## 스프린트 라이프사이클

```
plan-sprint → (실행: 자동 규칙 적용) → retrospective → next-sprint
     ↑                                                      │
     └──────────────────────────────────────────────────────┘
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| **1. 계획** | `plan-sprint` | 백로그에서 작업 선택 → 현재 스프린트에 할당 |
| **2. 실행** | (자동) | 작업 착수/완료 시 마크다운 상태 자동 전이 + 구현 메모 동기화 |
| **3. 회고** | `retrospective` | 스프린트 결과 리뷰 + 문서 동기화 + 회고 기록 |
| **4. 전환** | `next-sprint` | 현재 스프린트 종료 → 회고 → 다음 스프린트 생성 → 계획 |

> **`next-sprint`는 전체 사이클을 한 번에 수행하는 통합 명령이다.**

## 이슈 ID 규칙

이슈 ID는 자동 증분한다:
1. `backlog.md`와 `current-sprint.md`의 모든 테이블에서 가장 큰 ID를 찾는다
2. `sprints/` 디렉토리의 아카이브 파일도 검색하여 최대 ID를 찾는다
3. 최대 ID + 1을 새 이슈의 ID로 할당한다

## 작업 실행 시 자동 규칙

에이전트가 이슈에 해당하는 작업을 수행할 때, **명시적 `/manage-cycle` 호출 없이도** 다음 규칙을 자동으로 따른다.

### 규칙 1: 실시간 상태 전이

작업 라이프사이클에 맞춰 `current-sprint.md` Board의 이슈 행을 이동한다.

| 이벤트 | 상태 변경 | 시점 |
|--------|----------|------|
| 작업 착수 | `시작 전` → `진행 중` 섹션으로 행 이동 | feature 브랜치에서 해당 이슈의 코드를 작성하기 시작할 때 |
| 작업 완료 | `진행 중` → `완료` 섹션으로 행 이동 | 테스트 통과 + feature 브랜치에 커밋 완료 후 |
| 작업 차단 | 상태 유지, Board 아래에 차단 사유 기록 | 블로커 발견 시 |

**처리 방식**: `Edit` 도구로 `current-sprint.md`에서 해당 이슈 행을 삭제하고 대상 섹션의 테이블에 추가.

**일괄 처리**: 여러 이슈를 동시에 완료한 경우, 모든 이슈를 한 번에 이동한다.

### 규칙 2: 구현-문서 차이 동기화

구현 중 이슈의 기술 내용(수용 기준, 관련 파일)과 실제 구현이 다를 경우, `current-sprint.md`에 `## Implementation Diffs` 섹션을 추가하여 차이점을 기록한다.

**동기화 대상**:
- 패키지명/API 변경
- 추가된 파일 또는 예상과 다른 파일 구조
- 수용 기준 중 스킵되거나 변경된 항목

**동기화 시점**: **작업 완료 즉시** (커밋 직후, 상태를 "완료"로 이동할 때 함께 수행).

**서브에이전트 사용 시 (subagent-driven-development)**:
1. 서브에이전트 프롬프트에 "Report Format에 **Implementation Diffs** 섹션을 추가하라" 포함
2. 서브에이전트 완료 보고를 받으면, 코디네이터가 `current-sprint.md`에 기록
3. 커밋과 상태 이동을 수행

**형식**: `current-sprint.md`의 Board 섹션 아래에 추가:
```markdown
## Implementation Diffs

### Issue #{ID}: {Title}
- <차이점 1>
- <차이점 2>
```

**처리 방식**: `Edit` 도구로 `current-sprint.md`에 섹션 추가.

### 규칙 3: CLAUDE.md 동기화

기술 스택이나 아키텍처에 영향을 주는 변경이 발생하면, `CLAUDE.md`의 관련 내용도 함께 업데이트한다.

**처리 방식**: `Edit` 도구로 `CLAUDE.md` 직접 편집.

### 규칙 4: gstack 스킬 트리거 연동

gstack 스킬과 cycle 이슈를 연동한다. gstack이 생성한 아티팩트(디자인 문서, plan file)는 해당 스킬이 자체 관리하므로, cycle → gstack 방향의 단방향 트리거로 운영한다.

**디자인 문서 위치**:
- 로컬: `docs/designs/specs/`, `docs/designs/plans/`
- gstack: `~/.gstack/projects/{slug}/` (gstack `/office-hours`가 자동 생성)

**gstack 스킬 트리거**:

| 상황 | gstack 스킬 | 트리거 시점 |
|------|-------------|------------|
| 새 기능/설계가 필요한 이슈 생성 | `/office-hours` | `create-issue`에서 복잡도 판단 시 |
| 회고 Try 항목 → 새 작업 도출 | `/office-hours` | `next-sprint` Step 5에서 |
| 복수 Task가 필요한 큰 작업 | `/plan-eng-review` | `/office-hours` 디자인 승인 후 |
| 코드 리뷰 | `/review` | 브랜치 완료 전 |
| 브랜치 완료/merge | `/ship` | 코드 리뷰 통과 후 |

> **흐름**: `/office-hours`(무엇을, 왜) → `/plan-eng-review`(어떻게, 어떤 순서로) → `create-issue`(이슈 등록)

**처리 방식**: `Read` + `Edit` 도구로 `backlog.md` / `current-sprint.md` 편집.

### 규칙 5: 브랜치 기반 작업 관리

모든 작업은 feature 브랜치에서 수행하고, 완료 후 squash and merge로 main에 통합한다.

**브랜치 생성 시점**: 스프린트 작업 착수 시 (규칙 1의 "작업 착수" 시점)

**브랜치 단위 (묶음 기준)**:
- 독립적인 이슈 1개 → 브랜치 1개
- 의존성이 있는 관련 이슈 N개 → 논리적 묶음으로 브랜치 1개
- 판단 기준: squash commit 메시지를 한 문장으로 쓸 수 있으면 적절한 묶음

**브랜치 네이밍**: `<type>/<short-description>`

**완료 시점**: 브랜치 내 모든 이슈가 완료되면:
1. `/review` 스킬로 코드 리뷰 수행
2. Critical/Important 이슈 수정
3. `/ship` 스킬로 PR 생성 및 squash merge 수행

**squash commit 메시지 형식**:
```
<type>: <한 줄 요약>

- [D{n}.{n}] 이슈 설명 1
- [D{n}.{n}] 이슈 설명 2

Co-Authored-By: Claude <noreply@anthropic.com>
```

> **상세 규칙**: `docs/CONVENTIONS.md` > 브랜치 전략 참조

---

## 명령어

### create-issue: 이슈 생성

EARS 형식으로 `backlog.md`에 이슈를 추가한다.

**입력 형식**: `/manage-cycle create-issue "<제목>" [우선순위] [태그]`

**처리 절차**:
1. 제목이 EARS 형식(`[D{n}.{n}][패턴] 설명`)인지 확인
2. **복잡도 판단**: 이슈가 단순 작업/버그인지, 새로운 기능/설계가 필요한 작업인지 판단
   - **단순 작업/버그**: 바로 Step 3으로 진행
   - **새 기능/설계 필요**: `/office-hours` 스킬을 먼저 호출
3. 이슈 ID 자동 할당 (이슈 ID 규칙 참조)
4. `backlog.md`의 Issues 테이블에 행 추가:
   ```
   | {ID} | {제목} | {우선순위} | {YYYY-MM-DD} |
   ```
5. 현재 스프린트에 즉시 할당할지 사용자에게 확인
   - 할당하면: backlog.md에서 해당 행을 삭제하고 `current-sprint.md`의 `시작 전` 섹션에 추가
6. 상세 본문이 필요하면 별도 이슈 파일 생성을 안내 (`docs/CONVENTIONS.md`의 작업 본문 템플릿 참조)

**처리 방식**: `Read` 도구로 backlog.md 읽기 → `Edit` 도구로 테이블에 행 추가.

**예시**:
```
/manage-cycle create-issue "[D1.1][When] CSV 파일 파싱 시 UTF-8 인코딩 처리" 높음
```

### create-sprint: 스프린트 생성

1주 단위 스프린트를 생성한다.

**입력 형식**: `/manage-cycle create-sprint ["<이름>"] [시작일]`

**처리 절차**:
1. 시작일이 없으면 다가오는 월요일을 시작일로 계산
2. 종료일 = 시작일 + 6일 (일요일)
3. 이름이 없으면 `Sprint YYYY-WNN` 형식으로 자동 생성 (ISO 주 번호)
4. 현재 `current-sprint.md`에 활성 스프린트가 있으면:
   - `sprints/sprint-{N}.md`로 아카이브 (현재 내용을 복사하고 상태를 Past로 변경)
5. `docs/cycle/sprints/sprint-00-template.md`를 기반으로 `current-sprint.md`를 새로 작성:
   - `{N}`: 스프린트 번호 (아카이브에서 최대값 + 1)
   - `{SPRINT_NAME}`: 이름
   - `{START_DATE}`, `{END_DATE}`: 기간
6. 생성된 스프린트 정보를 표시

**처리 방식**: `Read` 도구로 template 읽기 → `Write` 도구로 `current-sprint.md` 작성.

### status: 현재 스프린트 상태

**입력 형식**: `/manage-cycle status`

**처리 절차**:
1. `current-sprint.md`를 `Read` 도구로 읽는다
2. Board의 각 섹션(시작 전, 진행 중, 완료)에서 이슈를 파싱
3. 상태별 요약을 표시:
   - 스프린트 이름, 기간
   - 시작 전 / 진행 중 / 완료 작업 수
   - 완료율
   - 각 작업의 ID, 제목, 브랜치

### update: 작업 상태 업데이트

**입력 형식**: `/manage-cycle update <이슈-ID> "<상태>"`

**처리 절차**:
1. `current-sprint.md`에서 해당 이슈 ID의 행을 `Grep`으로 검색
2. 해당 행을 현재 섹션에서 삭제하고 대상 섹션으로 이동

**유효한 상태값**: 시작 전, 진행 중, 완료

**처리 방식**: `Read` + `Edit` 도구로 행 이동.

### backlog: 백로그 조회

**입력 형식**: `/manage-cycle backlog`

**처리 절차**:
1. `backlog.md`를 `Read` 도구로 읽는다
2. Issues 테이블의 내용을 표시

### plan-sprint: 스프린트 계획

**입력 형식**: `/manage-cycle plan-sprint`

**처리 절차**:

#### Step 1: 스프린트 목적 및 목표 설정
1. 구현 플랜(`docs/designs/plans/`)과 gstack 디자인 문서(`~/.gstack/projects/`)를 읽고, 이번 스프린트 범위 파악
2. 이전 스프린트 아카이브(`sprints/`)에서 최근 회고의 Try 항목 확인
3. 사용자와 함께 다음을 결정:
   - **스프린트 목적** (1문장)
   - **성공 기준** (2~4개, 검증 가능한 조건)
4. `current-sprint.md`의 목적과 성공 기준 필드를 채운다

#### Step 2: 작업 선택 및 할당
1. `backlog.md` 읽기 (스프린트 미할당 작업)
2. 성공 기준 달성에 필요한 작업을 식별, 사용자에게 선택 요청
3. 선택된 이슈를 `backlog.md`에서 삭제하고 `current-sprint.md`의 `시작 전` 섹션에 추가
4. 부족하면 추가 작업 생성 제안 (`create-issue` 호출)

#### Step 3: 브랜치 계획
1. 작업 간 의존성과 도메인 연관성 분석
2. 묶음 기준: "squash commit 메시지를 한 문장으로 쓸 수 있는가?"
3. 사용자와 함께 브랜치 계획 확정
4. `current-sprint.md`의 Branch Plan 테이블에 기록

**처리 방식**: `Read` + `Edit` 도구로 backlog.md와 current-sprint.md 편집.

### retrospective: 스프린트 회고

**입력 형식**: `/manage-cycle retrospective`

**처리 절차**:

#### Phase 0.5: 코드 헬스 체크 (gstack /health 연동)

gstack `/health` 스킬을 호출하여 최신 코드 품질 점수를 수집한다.

**$SLUG 계산**: `eval "$(~/.claude/skills/gstack/bin/gstack-slug 2>/dev/null)"` 사용. gstack-slug 미설치 시 `basename $(git rev-parse --show-toplevel)` 폴백.

**처리 절차**:
1. `/health` 스킬을 호출하여 최신 코드 품질 데이터 생성
2. `~/.gstack/projects/$SLUG/health-history.jsonl`에서 최신 엔트리를 읽어서 composite score + 카테고리별 점수 추출
3. 점수 < 7인 카테고리를 Phase 3의 Problem 섹션에 자동 표면화
4. 점수 < 7인 카테고리에 대해 `docs/QUALITY_RULES.md`에 구체적 규칙 추가를 **제안** (사용자 확인 후 추가, progressive harness 원칙 유지)

**파싱 실패 폴백**: JSONL 파일이 없거나 파싱 결과가 0건이면 "⚠ /health 점수를 수집하지 못했습니다. gstack /health를 먼저 실행하거나 출력 형식을 확인하세요." 경고를 표시하고 이 단계를 건너뜀.

#### Phase 1: 스프린트 결과 수집
1. `current-sprint.md`를 `Read`로 읽어서 목적, 성공 기준, Board 파싱
2. 완료/미완료 작업 분류
3. 완료율 계산

#### Phase 1.5: 스프린트 목표 달성 평가
1. 각 성공 기준을 하나씩 평가 (검증 가능한 기준은 실제 검증)
2. ✅ 달성 / ❌ 미달성 / ⚠️ 부분 달성 표시
3. 미달성 원인 분석

#### Phase 2: 구현-문서 차이 감지 및 동기화
1. 완료된 작업의 관련 파일이 실제로 존재하는지 확인 (`Glob`)
2. 프로젝트 문서(`CLAUDE.md`, `docs/*.md`) 업데이트 필요 여부 식별 및 수정

#### Phase 3: 회고 기록
1. 사용자에게 Keep/Problem/Try 질문
2. `current-sprint.md`의 Retrospective 섹션에 기록:

```markdown
## Retrospective

### 목표 달성 평가
**목적**: {스프린트 목적}
**달성도**: N/M 성공 기준 달성
**코드 헬스**: {composite score}/10 (typecheck: {N}, lint: {N}, test: {N}, deadcode: {N}, shell: {N})

| 성공 기준 | 결과 | 비고 |
|----------|------|------|
| {기준 1} | ✅/❌/⚠️ | {검증 결과} |

### 결과 요약
- 완료: N개 / 전체: M개 (완료율: X%)
- 미완료 작업: [목록]

### Keep
- ...

### Problem
- ...

### Try
- ...
```

**처리 방식**: `Read` + `Edit` 도구로 `current-sprint.md` 편집.

### next-sprint: 스프린트 전환

**입력 형식**: `/manage-cycle next-sprint ["<스프린트 이름>"]`

**처리 절차**:

#### Step 1: 회고 실행
1. `retrospective` 명령을 내부 호출

#### Step 2: 미완료 작업 처리
미완료 작업에 대해 사용자에게 각각 처리 방법을 확인:
- **이월**: 다음 스프린트에 포함 (current-sprint.md에 유지)
- **백로그**: `backlog.md`로 이동
- **보관**: 삭제 (아카이브에 기록은 남음)

#### Step 3: 현재 스프린트 아카이브
1. `current-sprint.md`의 전체 내용을 `sprints/sprint-{N}.md`로 복사
2. 상태를 Past로 변경

#### Step 4: 새 스프린트 생성
1. `create-sprint` 명령을 내부 호출
2. 이월된 작업을 새 `current-sprint.md`의 `시작 전` 섹션에 추가

#### Step 5: 회고 Try → 새 작업 도출
1. 회고 Try 항목 중 구체적 작업으로 전환할 수 있는 것이 있으면:
   - 단순 이슈: `create-issue` 호출
   - 새 기능/설계: `/office-hours` → `/plan-eng-review` → `create-issue`

#### Step 6: 다음 스프린트 계획
1. `plan-sprint` 명령을 내부 호출

**처리 방식**: 위 명령어들의 조합. 모든 변경은 `Read` + `Edit` + `Write` 도구로 수행.

---

## EARS 제목 형식 참조

```
[D{도메인}.{번호}][{EARS패턴}] {요구사항 설명}
```

도메인: `docs/CONVENTIONS.md`의 도메인 코드 테이블 참조
패턴: Ubiquitous, While, When, If...Then, Where, While+When
