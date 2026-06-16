# BACKLOG — 의사결정 보드 (repo-canonical)

> **이것이 "지금 무엇이 열려 있고 다음에 무엇을 하나"의 단일 출처다.**
> 어느 세션/PC/OS/에이전트/사용자든 작업 시작 시 `git pull` 후 이 파일과
> `python scripts/backlog_sweep.py`(due-check 등 런타임 신호 포함)를 본다.
> `scripts/generate_views.py` 가 TASK frontmatter 에서 생성 → 드리프트 불가. **직접 수정 금지.**
> **규칙(COMPOUND-032): 열린 작업은 전부 TASK 로 존재해야 한다** — 메모리·프로세 "다음:" 한 줄에만 두지 말 것
> (로컬 메모리는 PC/사용자별이라 공유 불가 → 다른 세션이 못 봐서 중복작업이 생긴다).
> 생성 시각: `2026-06-17T01:39:06+09:00` · 열린 작업 11건

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
| 열린 작업 | 11건 / 76 ph | frontmatter 기준 |
| 진행 중 WIP | 0건 | WIP 적정 |
| 대기 | 0건 | 최상위 자율 후보: 대기 중 ACT 후보 없음 |
| 보류 | 11건 | Owner/외부 조건 또는 의도적 defer |
| 실행성 | ACT 0 / REVIEW 0 / ASK 10 / DEFER 1 | ACT는 승인 없이 진행 가능, ASK/DEFER는 멈춤 |

**빠른 판단:** 새 착수보다 진행 중/게이트 항목 정리가 우선이다.

## 결정 레인

### ASK — Owner/외부 게이트

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-031](TASK-031-market-halt-vi-risk-gates.md) market halt vi risk gates | ASK | 보류 | High / score 12 | L · 5 ph | 회귀 리스크 감소; gate: Owner approval required before app/risk or live order-blocking policy ch... | Owner/외부 조건 대기 |
| 2 | [TASK-014](TASK-014-kis-after-hours-order.md) kis after hours order | ASK | 보류 | Medium / score 4 | M · 3 ph | 중간 가치; gate: Owner approval required: changes app/brokers/kis place_order order path,... | Owner/외부 조건 대기 |
| 3 | [TASK-026](TASK-026-krx-alternative-products-test-support.md) krx alternative products test support | ASK | 보류 | Medium / score 2 | L · 5 ph | 회귀 리스크 감소; gate: Owner approval required before any live broker/order-path support; mock ... | Owner/외부 조건 대기 |
| 4 | [TASK-032](TASK-032-data-quality-corporate-action-tests.md) data quality corporate action tests | ASK | 보류 | Medium / score 2 | L · 5 ph | 회귀 리스크 감소; gate: no live orders; risk integration requires review | Owner/외부 조건 대기 |
| 5 | [TASK-028](TASK-028-advanced-order-types-test-support.md) advanced order types test support | ASK | 보류 | Medium / score -1 | L · 8 ph | 회귀 리스크 감소; gate: Owner approval required before broker/order_flow changes that can affect... | Owner/외부 조건 대기 |
| 6 | [TASK-049](TASK-049-ui-overhaul-phase5-analysis-parity-retire.md) ui overhaul phase5 analysis parity retire | ASK | 보류 | Medium / score -5 | XL · 16 ph | 중간 가치; gate: 선행 TASK-048 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 | Owner/외부 조건 대기 |
| 7 | [TASK-021](TASK-021-kis-margin-short.md) kis margin short | ASK | 보류 | Low / score -9 | L · 6 ph | 낮은/위생; gate: 보류 상태 — 해제 조건은 TASK 본문 확인 | Owner/외부 조건 대기 |
| 8 | [TASK-022](TASK-022-kis-overseas-order.md) kis overseas order | ASK | 보류 | Low / score -11 | L · 8 ph | 낮은/위생; gate: 보류 상태 — 해제 조건은 TASK 본문 확인 | Owner/외부 조건 대기 |
| 9 | [TASK-030](TASK-030-block-basket-execution-tests.md) block basket execution tests | ASK | 보류 | Low / score -11 | L · 8 ph | 회귀 리스크 감소; gate: Owner approval required before actual block/basket venue or broker submi... | Owner/외부 조건 대기 |
| 10 | [TASK-027](TASK-027-krx-derivatives-test-support.md) krx derivatives test support | ASK | 보류 | Low / score -13 | XL · 10 ph | 회귀 리스크 감소; gate: Owner approval required; derivatives order routing and risk policy are R... | Owner/외부 조건 대기 |

### DEFER — 보류/낮은 지금 가치

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) product maturity reassessment 2026 12 | DEFER | 보류 | Medium / score -2 | S · 2 ph | 중간 가치; gate: scheduled for 2026-12-14; do not start early unless Owner explicitly req... | 지금은 보류 |

## 흐름 보드

### 보류 (게이트 — 외부/결정 대기)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-031](TASK-031-market-halt-vi-risk-gates.md) | High | Compliance Officer | 5 ph / ~50000 tok | Owner approval required before app/risk or live order-blocking policy changes |
| [TASK-014](TASK-014-kis-after-hours-order.md) | Medium | KIS API Engineer | 3 ph / ~50000 tok | Owner approval required: changes app/brokers/kis place_order order path, app/risk safety gates, and after-hours order policy. |
| [TASK-026](TASK-026-krx-alternative-products-test-support.md) | Medium | KIS API Engineer | 5 ph / ~50000 tok | Owner approval required before any live broker/order-path support; mock catalog tests may be drafted first |
| [TASK-028](TASK-028-advanced-order-types-test-support.md) | Medium | Backend Engineer | 8 ph / ~70000 tok | Owner approval required before broker/order_flow changes that can affect live order behavior |
| [TASK-032](TASK-032-data-quality-corporate-action-tests.md) | Medium | Data Engineer | 5 ph / ~45000 tok | no live orders; risk integration requires review |
| [TASK-049](TASK-049-ui-overhaul-phase5-analysis-parity-retire.md) | Medium | UI/UX Designer | 16 ph / ~120000 tok | 선행 TASK-048 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 |
| [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) | Medium | Lead Engineer | 2 ph / ~15000 tok | scheduled for 2026-12-14; do not start early unless Owner explicitly requests early reassessment |
| [TASK-021](TASK-021-kis-margin-short.md) | Low | KIS API Engineer | 6 ph / ~50000 tok | kis,margin,short |
| [TASK-022](TASK-022-kis-overseas-order.md) | Low | KIS API Engineer | 8 ph / ~50000 tok | kis,overseas,us-stocks |
| [TASK-027](TASK-027-krx-derivatives-test-support.md) | Low | KIS API Engineer | 10 ph / ~80000 tok | Owner approval required; derivatives order routing and risk policy are R3 surfaces |
| [TASK-030](TASK-030-block-basket-execution-tests.md) | Low | Backend Engineer | 8 ph / ~70000 tok | Owner approval required before actual block/basket venue or broker submission support |

