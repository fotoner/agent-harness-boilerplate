# docs/mistake/

`session-retrospective` 스킬이 관리하는 세션 회고 기록 디렉토리. **점진적 하네스(Progressive Harness)** 의 기계적 엔진이다 — 세션에서 반복된 실수를 카운트하고, 임계치에 도달하면 규칙/린터/훅 승격을 제안한다.

## 구조

```
docs/mistake/
├── README.md           # 이 문서
├── INDEX.md            # 패턴 태그별 누적 카운터 + 회고 목록
└── YYYY/MM/
    └── YYYY-MM-DD - <session-slug>.md   # 세션별 회고 기록
```

## 동작

1. `session-retrospective` 스킬은 회고 시작 시 `INDEX.md` 를 읽어 패턴 태그별 누적 횟수를 확인한다.
2. 이번 세션 실수를 A/B/C/D 로 분류하되, 같은 패턴 태그가 누적되어 있으면 분류를 자동 격상한다:
   - 누적 2회 + 활성 규칙 없음 → 신규 규칙 제안 (D)
   - 누적 2회 + 활성 규칙 있음 → 기존 규칙 보강 (C)
   - 누적 3회 + 활성 규칙 있음 → 린터/훅 승격 후보
3. C/D 제안은 **사용자 승인 후에만** 규칙 파일에 반영된다. `docs/mistake/` 기록만은 승인 없이 저장된다 (스킬의 자기 영역).

## 규칙

- 회고 파일은 **덮어쓰지 않는다.** 같은 날짜·slug 충돌 시 `-2`, `-3` 인덱스.
- 패턴 태그는 kebab-case. 기존 태그를 우선 재사용하고, 같은 의미를 새 태그로 중복 생성하지 않는다.
- 형식과 절차의 정본은 `.agents/skills/session-retrospective/SKILL.md`.
