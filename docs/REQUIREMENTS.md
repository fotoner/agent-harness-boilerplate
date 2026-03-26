# 요구사항 (EARS 기반)

EARS(Easy Approach to Requirements Syntax) 패턴으로 작성된 요구사항.
MECE 도메인별로 분류.

## EARS 패턴 참조

| 패턴 | 키워드 | 템플릿 |
|------|--------|--------|
| Ubiquitous | (없음) | "시스템은 {응답}해야 한다" |
| State-driven | While | "While {조건}, 시스템은 {응답}해야 한다" |
| Event-driven | When | "When {트리거}, 시스템은 {응답}해야 한다" |
| Unwanted | If...Then | "If {조건}, Then 시스템은 {응답}해야 한다" |
| Optional | Where | "Where {기능 포함 시}, 시스템은 {응답}해야 한다" |
| Complex | While+When | "While {조건}, When {트리거}, 시스템은 {응답}해야 한다" |

## MECE 도메인 분해 원칙

- 도메인은 **MECE**(Mutually Exclusive, Collectively Exhaustive)로 분해한다
- 각 도메인은 독립적이고 겹치지 않으며, 전체를 빠짐없이 커버한다
- 도메인 코드는 `D{번호}` 형식 (예: D1, D2, D3)
- 각 도메인 내에서 하위 도메인은 `D{번호}.{하위번호}` 형식
- 요구사항 ID는 `[D{n}.{m}-{순번}]` 형식 (예: [D1.1-01])

---

{{DOMAINS}}

<!-- init-project가 프로젝트의 MECE 도메인 분해 결과로 채움. 예시:

## D1: 데이터 수집 (Data Ingestion)

### D1.1: CSV 파싱

- **[D1.1-01][Ubiquitous]** 시스템은 CSV 파일을 UTF-8로 파싱해야 한다
- **[D1.1-02][If...Then]** If 필수 필드가 비어있으면, Then 해당 행을 스킵하고 로그를 기록해야 한다

## D2: 검색 (Search)

### D2.1: 전문 검색

- **[D2.1-01][When]** When 검색어가 입력되면, 시스템은 트라이그램 검색을 수행해야 한다

-->
