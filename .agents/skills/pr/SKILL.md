---
name: pr
description: >-
  PR 을 생성하는 게이트 스킬. 브랜치 컨벤션과 base 브랜치를 확인하고,
  브랜치명·PR 제목·본문 초안을 사용자에게 검수받은 뒤 push 와 PR 생성을 수행한다.

  사용 시나리오:
  - "PR 올려줘" / "푸시하고 PR ㄱ" / 구현·리뷰 완료 후 PR 을 만들 때
  - 에이전트가 gh pr create 를 실행해야 하는 모든 경우 (CLAUDE.md "커밋·PR 게이트" — 직접 PR 금지)
---

# pr

PR 생성을 **브랜치명·PR 메시지 검수 게이트**를 거쳐 수행한다.
에이전트는 이 스킬의 절차를 거치지 않고 `gh pr create` 를 직접 실행하지 않는다
(CLAUDE.md "커밋·PR 게이트").

## 핵심 원칙

1. **초안 승인은 콘텐츠 승인이다**: 도구 실행 승인과 별개로, PR 제목·본문 초안에 대한 명시적 사용자 승인을 받은 뒤에만 생성한다.
2. **base 브랜치를 기본값으로 가정하지 않는다**: base 브랜치는 `docs/CONVENTIONS.md` 의 브랜치 전략을 확인해 결정한다 (기본 `main`). 확인 없이 기본값으로 PR 을 만들지 않는다.
3. **자기완결 본문**: PR 본문은 외부 plan/spec 문서를 참조하지 않고 그 자체로 변경의 의도·내용·검증을 설명한다. 본문 크기는 변경 크기에 비례.

## 절차 (체크리스트)

1. **base 브랜치 + 컨벤션 확인**
   - base 브랜치를 `docs/CONVENTIONS.md` 기준으로 확인한다 (기본 `main`).
   - 현재 브랜치가 base 에서 분기됐는지, stale 하지 않은지 확인한다 (`git log --oneline -5`, base 와의 diverge).

2. **(필요 시) 브랜치 생성 — 브랜치명 검수**
   - 새 브랜치가 필요하면 브랜치명 후보(`<type>/<short-description>`, ASCII)를 제시하고 승인받는다. 브랜치명에도 금지 패턴(`docs/QUALITY_RULES.md`) 비포함.

3. **커밋 상태 확인**
   - 미커밋 변경이 있으면 먼저 `commit` 스킬 절차로 처리한다.

4. **push**
   - `git push -u origin <branch>` 로 upstream 을 명시한다 (잘못된 upstream 으로 인한 오푸시 방어).

5. **PR 초안 제시 → 승인 게이트**
   - 제목 + 본문 초안을 제시하고 승인을 기다린다. 본문 구성: 변경 요약 / 주요 결정 / 검증한 것(미검증 항목 명시) / 리뷰 포인트.
   - 초안에서 프로젝트 금지 패턴(`docs/QUALITY_RULES.md` `{{BANNED_PATTERNS}}`) 0건 확인.
   - AI attribution 여부는 `docs/CONVENTIONS.md` 규칙을 따른다.

6. **생성 + 보고**
   - `gh pr create` (base 명시) 실행 후 PR URL 을 1줄로 보고한다.
   - merge 는 이 스킬 범위 밖 — merge 전 코드 리뷰 필수 규칙(CLAUDE.md 브랜치 전략)을 상기시킨다.

## 자주 하는 실수

| 실수 | 교정 |
|------|------|
| base 브랜치 확인 없이 기본값으로 PR 생성 | CONVENTIONS.md 의 브랜치 전략 확인. |
| 초안 검수 없이 PR 생성 | 승인 게이트 생략 불가. |
| 본문에 "자세한 내용은 plan 참고" | 본문에 직접 서술. 외부 문서 참조 금지. |
| 무인자 `git push` (잘못된 upstream) | `-u origin <branch>` 명시. |
| 미커밋 변경을 둔 채 PR 생성 | commit 스킬 먼저. |

## Red Flags

- base 브랜치를 확인하지 않고 기본값으로 PR 을 만들려 한다.
- 사용자가 보지 않은 본문으로 `gh pr create` 를 실행하려 한다.
- 브랜치명을 에이전트 임의로 정해 push 까지 진행했다.
