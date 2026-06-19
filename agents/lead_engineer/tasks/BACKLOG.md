# BACKLOG — 의사결정 보드 (repo-canonical)

> **이것이 "지금 무엇이 열려 있고 다음에 무엇을 하나"의 단일 출처다.**
> 어느 세션/PC/OS/에이전트/사용자든 작업 시작 시 `git pull` 후 이 파일과
> `python scripts/backlog_sweep.py`(due-check 등 런타임 신호 포함)를 본다.
> `scripts/generate_views.py` 가 TASK frontmatter 에서 생성 → 드리프트 불가. **직접 수정 금지.**
> **규칙(COMPOUND-032): 열린 작업은 전부 TASK 로 존재해야 한다** — 메모리·프로세 "다음:" 한 줄에만 두지 말 것
> (로컬 메모리는 PC/사용자별이라 공유 불가 → 다른 세션이 못 봐서 중복작업이 생긴다).
> 생성 시각: `2026-06-19T22:18:00+09:00` · 열린 작업 2건

---

## 표시 원칙

- `ACT`: 가역(R1/R2)이라 승인 없이 진행 가능.
- `REVIEW`: 일부는 자율 가능하지만 R3/Owner 경계가 있어 마무리 전 확인 필요.
- `ASK`: Owner 승인, 외부 계정/결제/secret 등 없이는 진행 불가.
- `DEFER`: 지금은 일부러 미루는 것이 안전하거나 가치가 낮음.
- `score`: 우선순위, 실행 가능성, 예상 시간을 섞은 정렬용 휴리스틱이다. 절대값이 아니라 줄세우기 기준이다.

## 한눈에 보기

| 지표 | 값 | 해석 |
|------|----|------|
| 열린 작업 | 2건 / 18 ph | frontmatter 기준 |
| 진행 중 WIP | 0건 | WIP 적정 |
| 대기 | 1건 | 최상위 자율 후보: 대기 중 ACT 후보 없음 |
| 보류 | 1건 | Owner/외부 조건 또는 의도적 defer |
| 실행성 | ACT 0 / REVIEW 1 / ASK 0 / DEFER 1 | ACT는 승인 없이 진행 가능, ASK/DEFER는 멈춤 |

**빠른 판단:** 새 착수보다 진행 중/게이트 항목 정리가 우선이다.

## 결정 레인

### REVIEW — 자율 가능 + 경계 확인

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-140](TASK-140-ui-visual-assets-expansion-adoption.md) ui visual assets expansion adoption | REVIEW | 대기 | High / score 24 | XL · 16 ph | 높은 가치; gate: Owner approval required for new web dependencies; self-host only (runtim... | R2 범위 진행, R3 전 확인 |

### DEFER — 보류/낮은 지금 가치

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) product maturity reassessment 2026 12 | DEFER | 보류 | Medium / score -2 | S · 2 ph | 중간 가치; gate: scheduled for 2026-12-14; do not start early unless Owner explicitly req... | 지금은 보류 |

## 흐름 보드

### 대기 (next)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-140](TASK-140-ui-visual-assets-expansion-adoption.md) | High | UI/UX Designer | 16 ph / ~180000 tok | Owner approval required for new web dependencies; self-host only (runtime CDN 0); no order/risk/secret mutation; UI behavior verified via prod E2E (CI=1) |

### 보류 (게이트 — 외부/결정 대기)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) | Medium | Lead Engineer | 2 ph / ~15000 tok | scheduled for 2026-12-14; do not start early unless Owner explicitly requests early reassessment |

