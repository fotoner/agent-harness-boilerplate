---
name: init-project
description: >-
  프로젝트 플랜 또는 자연어 설명을 받아서 보일러플레이트의 placeholder를 자동으로 채운다.
  새 프로젝트 시작 시 하네스 문서를 프로젝트에 맞게 초기화하는 스킬.

  사용 시나리오:
  - 새 프로젝트 시작 시 하네스 초기화
  - 프로젝트 플랜 문서를 기반으로 자동 채움
  - 대화형으로 프로젝트 정보를 수집하여 채움
---

# init-project

보일러플레이트의 `{{PLACEHOLDER}}`를 프로젝트 정보로 치환하여 하네스를 초기화하는 스킬.

## 사용법

```
/init-project                     # 대화형으로 정보 수집
/init-project "<plan-file-path>"  # 플랜 문서에서 자동 추출
```

## Placeholder 목록

| Placeholder | 위치 | 설명 |
|-------------|------|------|
| `{{PROJECT_NAME}}` | CLAUDE.md | 프로젝트 이름 |
| `{{PROJECT_DESCRIPTION}}` | CLAUDE.md | 프로젝트 한 줄 설명 |
| `{{TECH_STACK}}` | CLAUDE.md | 기술 스택 목록 |
| `{{ARCHITECTURE_STYLE}}` | CLAUDE.md, docs/ARCHITECTURE.md | 아키텍처 패턴 이름 |
| `{{ARCHITECTURE_DESCRIPTION}}` | docs/ARCHITECTURE.md | 아키텍처 패턴 상세 설명 |
| `{{LAYER_DIAGRAM}}` | CLAUDE.md, docs/ARCHITECTURE.md | 의존성 방향 다이어그램 |
| `{{DIRECTORY_STRUCTURE}}` | CLAUDE.md | 소스 디렉토리 구조 |
| `{{DOMAINS}}` | docs/REQUIREMENTS.md | MECE 도메인 분해 + 요구사항 골격 |
| `{{DOMAIN_TABLE}}` | docs/CONVENTIONS.md | 도메인 코드 매핑 테이블 |
| `{{ENV_VARS}}` | docs/SECURITY.md | 필수 환경 변수 목록 |
| `{{ERROR_POLICIES}}` | docs/RELIABILITY.md | 외부 연동별 에러 처리 정책 |
| `{{REVIEW_PERSPECTIVES}}` | docs/CODE_REVIEW.md | 프로젝트 특화 코드 리뷰 관점 |

## 처리 절차

### Step 0: 스택 자동 감지 (신규)

프로젝트 루트에서 매니페스트 파일을 탐색하여 기술 스택을 자동 감지한다.

**탐색 대상**: package.json, go.mod, pyproject.toml, Cargo.toml, build.gradle, pom.xml, Gemfile

**처리 방식**:
1. `Glob` 도구로 프로젝트 루트에서 위 파일들을 탐색
2. 발견된 파일을 `Read` 도구로 읽어서 언어, 프레임워크, 주요 의존성 추출
3. 추출 결과를 Step 1의 기본값으로 사용

**모노레포 처리**:
- 루트에 매니페스트가 없으면 1단계 하위 디렉토리(`*/package.json` 등) 스캔
- 복수 매니페스트 발견 시 사용자에게 "메인 프로젝트를 선택하세요" 프롬프트 표시

**감지 실패**: 매니페스트 파일이 없으면 Step 1의 대화형 모드로 폴백 (전부 질문)

### Step 1: 프로젝트 정보 수집

**대화형 모드** (인자 없이 호출):
Step 0에서 감지된 값을 기본값으로 표시하고, 사용자에게 확인/수정을 요청한다:
1. 프로젝트 이름
2. 프로젝트 설명 (한 줄)
3. 기술 스택 (언어, 프레임워크, 주요 라이브러리) — Step 0 감지 결과가 있으면 기본값으로 제안
4. 주요 외부 연동 (DB, API, 서비스 등)

**플랜 문서 모드** (파일 경로 제공):
1. 지정된 파일을 `Read` 도구로 읽는다
2. 프로젝트 이름, 설명, 기술 스택, 외부 연동을 자동 추출한다
3. 추출 결과를 사용자에게 확인받는다

### Step 2: 도메인 분해

1. 프로젝트 설명과 기술 스택을 바탕으로 MECE 도메인을 제안한다
2. 각 도메인에 코드(D1, D2, ...)를 할당하고 간단한 설명을 붙인다
3. 사용자에게 확인/수정을 요청한다

**출력 형식**:
```
제안된 도메인 분해:
- D1: {도메인명} ({설명})
- D2: {도메인명} ({설명})
- D3: {도메인명} ({설명})

수정이 필요하면 알려주세요. 없으면 이대로 진행합니다.
```

### Step 3: 아키텍처 결정

**아키텍처 패턴은 사전 매핑이 아닌, 프로젝트 생성 시점에 리서치하여 결정한다.**

1. 사용자가 지정한 스택/프레임워크를 기반으로 `WebSearch` 도구를 사용하여 해당 생태계에서 권장하는 아키텍처 패턴을 리서치한다
2. 리서치 결과를 바탕으로 2-3개 후보를 제안한다:
   - 각 후보의 이름, 핵심 원칙, 의존성 방향 다이어그램
   - 해당 생태계에서의 채택 현황
   - 프로젝트 규모/복잡도에 대한 적합성
3. 사용자가 선택하면 해당 패턴의 상세 설명과 의존성 규칙을 작성한다

**예시 출력**:
```
스택 기반 아키텍처 리서치 결과:

A) Feature-Sliced Design (FSD)
   - 원칙: app → pages → widgets → features → entities → shared
   - 채택: 2024년 이후 React/Vue 커뮤니티에서 빠르게 성장
   - 적합성: 중규모 이상 프로젝트에 특히 효과적

B) 레이어드 아키텍처
   - 원칙: Presentation → Application → Domain → Infrastructure
   - 채택: 전통적인 패턴, 대부분의 스택에서 지원
   - 적합성: 소~중규모 프로젝트에 무난

C) Clean Architecture
   - 원칙: UI → Controllers → Use Cases → Entities
   - 채택: Robert C. Martin의 원칙 기반, 엔터프라이즈에서 선호
   - 적합성: 복잡한 비즈니스 로직이 있는 프로젝트

추천: A (근거: ...)
어떤 패턴을 선택하시겠어요?
```

### Step 4: Placeholder 일괄 치환

모든 하네스 문서에서 `{{PLACEHOLDER}}`를 결정된 값으로 치환한다.

**치환 순서** (의존성 고려):
1. `CLAUDE.md` — PROJECT_NAME, PROJECT_DESCRIPTION, TECH_STACK, ARCHITECTURE_STYLE, LAYER_DIAGRAM, DIRECTORY_STRUCTURE
2. `docs/ARCHITECTURE.md` — ARCHITECTURE_STYLE, ARCHITECTURE_DESCRIPTION, LAYER_DIAGRAM
3. `docs/REQUIREMENTS.md` — DOMAINS
4. `docs/CONVENTIONS.md` — DOMAIN_TABLE
5. `docs/RELIABILITY.md` — ERROR_POLICIES
6. `docs/SECURITY.md` — ENV_VARS
7. `docs/CODE_REVIEW.md` — REVIEW_PERSPECTIVES

**치환 규칙**:
- `Grep` 도구로 `{{` 패턴을 검색하여 모든 placeholder 위치를 확인
- `Edit` 도구로 각 placeholder를 치환 (replace_all=true 사용)
- 치환 후 각 파일이 자연스럽게 읽히는지 확인
- placeholder 주변의 HTML 주석 (<!-- 힌트 -->)도 함께 제거

### Step 4.5: gstack routing 생성 (신규)

gstack 설치 여부를 확인하고, 설치되어 있으면 CLAUDE.md에 skill routing rules를 추가한다.

**처리 방식**:
1. `ls ~/.claude/skills/gstack/VERSION 2>/dev/null` 으로 gstack 존재 확인
2. **설치됨**: CLAUDE.md의 `## Skill routing` 섹션이 이미 존재하는지 확인. 없으면 파일 하단에 추가
3. **미설치**: CLAUDE.md 하단에 주석 삽입: `<!-- gstack 설치 후 /init-project를 다시 실행하면 skill routing이 추가됩니다 -->`

### Step 4.6: Migration audit (신규)

모든 하네스 문서에서 이전 스킬 팩 참조가 남아있지 않은지 확인한다.

`Grep` 도구로 CLAUDE.md, docs/, .claude/skills/, README.md 범위에서 이전 스킬 팩 이름을 검색한다.

Expected: 0 matches. 잔존 참조가 있으면 사용자에게 목록을 표시하고 수정을 안내한다.

### Step 5: 초기 커밋

치환된 파일만 명시적으로 staging한다 (`git add -A` 사용 금지):

```bash
git add CLAUDE.md docs/ARCHITECTURE.md docs/REQUIREMENTS.md docs/CONVENTIONS.md docs/RELIABILITY.md docs/SECURITY.md docs/CODE_REVIEW.md
git commit -m "chore: init project harness for {PROJECT_NAME}"
```

## 치환 예시

**입력**: 프로젝트 이름 "my-api", TypeScript + Express, PostgreSQL

**CLAUDE.md 치환 전**:
```
# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}
```

**CLAUDE.md 치환 후**:
```
# my-api

Express 기반 REST API 서버. PostgreSQL 데이터베이스 사용.
```

## 검증

치환 완료 후, 모든 하네스 문서에 `{{`가 남아있지 않은지 확인:

```bash
grep -r '{{' CLAUDE.md docs/ --include="*.md"
```

Expected: 0 matches (모든 placeholder가 치환됨)

## 주의사항

- **불변 규칙은 수정하지 않는다**: QUALITY_RULES.md, CONVENTIONS.md의 TDD/브랜치/progressive harness 규칙은 placeholder가 없으므로 그대로 유지
- **brainstorming을 트리거하지 않는다**: 이 스킬은 이미 프로젝트 플랜이 있는 상태에서 호출되므로, 설계 단계를 건너뜀
- **HTML 주석 정리**: placeholder 치환 시 주변의 `<!-- 스택별 힌트: ... -->` 주석도 프로젝트에 맞게 수정하거나 제거
