# 아키텍처

## 아키텍처 패턴

{{ARCHITECTURE_STYLE}}

<!-- init-project가 스택/프레임워크 생태계를 리서치하여 결정.
     프로젝트 생성 시점에 최신 권장 패턴을 조사한 뒤 2-3개 후보를 제안하고 사용자와 함께 선택.
     예: React → FSD, Spring → MVC, Flutter → Clean Architecture, Node.js 백엔드 → Layered 등 -->

## 구조

{{ARCHITECTURE_DESCRIPTION}}

```
{{LAYER_DIAGRAM}}
```

## 의존성 규칙

### 불변 원칙 (모든 아키텍처 패턴에 공통)

1. **단방향 의존성**: 정의된 의존성 방향만 허용. 역방향 의존성 금지
2. **경계 검증**: 시스템 경계(API 응답, 파일 파싱, 사용자 입력)에서 반드시 데이터 검증
3. **동일 레이어/모듈 간 참조 허용**: 같은 수준의 모듈끼리는 상호 참조 가능

### 프로젝트 특화 규칙

<!-- init-project가 선택된 아키텍처 패턴에 맞는 구체적 규칙을 채움. 예시:

레이어드 아키텍처:
4. DB 직접 호출 금지: 상위 레이어에서 DB 클라이언트를 직접 임포트하지 않고, DB 레이어의 함수를 통해서만 접근

FSD:
4. Cross-import 금지: feature 간 직접 import 금지. shared 레이어를 통해서만 공유
5. Public API: 각 slice는 index.ts를 통해서만 export

Clean Architecture:
4. Domain은 외부 의존성 금지: Domain 레이어는 프레임워크, DB, API에 의존하지 않음
-->

## 교차 관심사

유틸리티 모듈은 모든 레이어/모듈에서 임포트 가능:
- 로거 — 구조화된 로깅
- HTTP 클라이언트 — 재시도 로직 포함 (필요 시)

## 데이터 흐름

<!-- init-project가 프로젝트의 데이터 흐름에 맞춰 채움. 예시:

```
[외부 데이터] → Import(파싱/검증) → DB(저장) → Processing(가공)
                                        ↓
[클라이언트] → Server → Handler(처리) → DB(조회) → [응답]
```
-->
