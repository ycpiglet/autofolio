# BACKLOG — 의사결정 보드 (repo-canonical)

> **이것이 "지금 무엇이 열려 있고 다음에 무엇을 하나"의 단일 출처다.**
> 어느 세션/PC/OS/에이전트/사용자든 작업 시작 시 `git pull` 후 이 파일과
> `python scripts/backlog_sweep.py`(due-check 등 런타임 신호 포함)를 본다.
> `scripts/generate_views.py` 가 TASK frontmatter 에서 생성 → 드리프트 불가. **직접 수정 금지.**
> **규칙(COMPOUND-032): 열린 작업은 전부 TASK 로 존재해야 한다** — 메모리·프로세 "다음:" 한 줄에만 두지 말 것
> (로컬 메모리는 PC/사용자별이라 공유 불가 → 다른 세션이 못 봐서 중복작업이 생긴다).
> 생성 시각: `2026-06-14T10:29:15+09:00` · 열린 작업 31건

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
| 열린 작업 | 31건 / 203 ph | frontmatter 기준 |
| 진행 중 WIP | 0건 | WIP 적정 |
| 대기 | 21건 | 최상위 자율 후보: TASK-058 (fix history live mode early return) |
| 보류 | 10건 | Owner/외부 조건 또는 의도적 defer |
| 실행성 | ACT 17 / REVIEW 4 / ASK 10 / DEFER 0 | ACT는 승인 없이 진행 가능, ASK/DEFER는 멈춤 |

**빠른 판단:** 새로 하나를 고른다면 **TASK-058**. 다만 현재 WIP가 0건이라, 먼저 진행 중 항목을 줄이는 편이 흐름에 유리하다.

## 결정 레인

### ACT — 자율 진행

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-058](TASK-058-fix-history-live-mode-early-return.md) fix history live mode early return | ACT | 대기 | High / score 41 | XS · 1 ph | 높은 가치 | 바로 착수 후보 |
| 2 | [TASK-053](TASK-053-product-maturity-assessment.md) product maturity assessment | ACT | 대기 | High / score 40 | S · 2 ph | 높은 가치 | 바로 착수 후보 |
| 3 | [TASK-067](TASK-067-fix-intraday-no-try-except.md) fix intraday no try except | ACT | 대기 | High / score 40 | S · 2 ph | 높은 가치 | 바로 착수 후보 |
| 4 | [TASK-055](TASK-055-fix-home-proposal-buttons-noop.md) fix home proposal buttons noop | ACT | 대기 | High / score 39 | M · 3 ph | 높은 가치 | 바로 착수 후보 |
| 5 | [TASK-056](TASK-056-fix-backend-allocation-gap.md) fix backend allocation gap | ACT | 대기 | High / score 39 | M · 3 ph | 높은 가치 | 바로 착수 후보 |
| 6 | [TASK-038](TASK-038-watchlist-screener-alert-expansion.md) watchlist screener alert expansion | ACT | 대기 | High / score 38 | M · 4 ph | 높은 가치 | 바로 착수 후보 |
| 7 | [TASK-054](TASK-054-fix-alerts-settings-no-persist.md) fix alerts settings no persist | ACT | 대기 | High / score 38 | M · 4 ph | 높은 가치 | 바로 착수 후보 |
| 8 | [TASK-057](TASK-057-fix-kpi-returns-hardcoded-zero.md) fix kpi returns hardcoded zero | ACT | 대기 | High / score 36 | L · 6 ph | 높은 가치 | 바로 착수 후보 |
| 9 | [TASK-062](TASK-062-feat-krx-holiday-calendar.md) feat krx holiday calendar | ACT | 대기 | High / score 36 | L · 6 ph | 높은 가치 | 바로 착수 후보 |
| 10 | [TASK-061](TASK-061-feat-price-alert-engine-loop.md) feat price alert engine loop | ACT | 대기 | High / score 34 | L · 8 ph | 높은 가치 | 바로 착수 후보 |
| 11 | [TASK-059](TASK-059-fix-logout-incomplete-state-reset.md) fix logout incomplete state reset | ACT | 대기 | Medium / score 30 | S · 2 ph | 중간 가치 | 바로 착수 후보 |
| 12 | [TASK-065](TASK-065-feat-log-rotation.md) feat log rotation | ACT | 대기 | Medium / score 30 | S · 2 ph | 중간 가치 | 바로 착수 후보 |
| 13 | [TASK-066](TASK-066-test-coverage-60pct.md) test coverage 60pct | ACT | 대기 | High / score 30 | XL · 12 ph | 높은 가치 | 바로 착수 후보 |
| 14 | [TASK-041](TASK-041-broker-capability-feature-parity-matrix.md) broker capability feature parity matrix | ACT | 대기 | Medium / score 29 | M · 3 ph | 회귀 리스크 감소 | 바로 착수 후보 |
| 15 | [TASK-060](TASK-060-sqlite-wal-fk-enforcement.md) sqlite wal fk enforcement | ACT | 대기 | Medium / score 29 | M · 3 ph | 중간 가치 | 바로 착수 후보 |
| 16 | [TASK-039](TASK-039-backtest-research-report-hardening.md) backtest research report hardening | ACT | 대기 | Medium / score 28 | M · 4 ph | 회귀 리스크 감소 | 바로 착수 후보 |
| 17 | [TASK-040](TASK-040-portfolio-performance-tax-lot-reporting.md) portfolio performance tax lot reporting | ACT | 대기 | Medium / score 28 | M · 4 ph | 중간 가치 | 바로 착수 후보 |

### REVIEW — 자율 가능 + 경계 확인

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-045](TASK-045-ui-overhaul-phase1-api-foundation-login.md) ui overhaul phase1 api foundation login | REVIEW | 대기 | High / score 24 | XL · 16 ph | 높은 가치; gate: no live orders; paper-safe; Owner 승인 전 prod 전환 금지 | R2 범위 진행, R3 전 확인 |
| 2 | [TASK-046](TASK-046-ui-overhaul-phase2-home-portfolio.md) ui overhaul phase2 home portfolio | REVIEW | 대기 | Medium / score 14 | XL · 12 ph | 중간 가치; gate: 선행 TASK-045 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요; no live orders | R2 범위 진행, R3 전 확인 |
| 3 | [TASK-048](TASK-048-ui-overhaul-phase4-agents-sse.md) ui overhaul phase4 agents sse | REVIEW | 대기 | Medium / score 14 | XL · 12 ph | 중간 가치; gate: 선행 TASK-047 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 | R2 범위 진행, R3 전 확인 |
| 4 | [TASK-049](TASK-049-ui-overhaul-phase5-analysis-parity-retire.md) ui overhaul phase5 analysis parity retire | REVIEW | 대기 | Medium / score 14 | XL · 16 ph | 중간 가치; gate: 선행 TASK-048 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 | R2 범위 진행, R3 전 확인 |

### ASK — Owner/외부 게이트

| Rank | Task | 결정 | 상태 | 중요도 | 시간 | 가치/이유 | 다음 행동 |
|------|------|------|------|--------|------|-----------|-----------|
| 1 | [TASK-031](TASK-031-market-halt-vi-risk-gates.md) market halt vi risk gates | ASK | 보류 | High / score 12 | L · 5 ph | 회귀 리스크 감소; gate: Owner approval required before app/risk or live order-blocking policy ch... | Owner/외부 조건 대기 |
| 2 | [TASK-047](TASK-047-ui-overhaul-phase3-trade-settings-gates.md) ui overhaul phase3 trade settings gates | ASK | 보류 | High / score 5 | XL · 20 ph | 높은 가치; gate: Owner 명시 승인 필수 — state-changing 엔드포인트, R3 인접; blocked by TASK-046 | Owner/외부 조건 대기 |
| 3 | [TASK-014](TASK-014-kis-after-hours-order.md) kis after hours order | ASK | 보류 | Medium / score 4 | M · 3 ph | 중간 가치; gate: Owner approval required: changes app/brokers/kis place_order order path,... | Owner/외부 조건 대기 |
| 4 | [TASK-026](TASK-026-krx-alternative-products-test-support.md) krx alternative products test support | ASK | 보류 | Medium / score 2 | L · 5 ph | 회귀 리스크 감소; gate: Owner approval required before any live broker/order-path support; mock ... | Owner/외부 조건 대기 |
| 5 | [TASK-032](TASK-032-data-quality-corporate-action-tests.md) data quality corporate action tests | ASK | 보류 | Medium / score 2 | L · 5 ph | 회귀 리스크 감소; gate: no live orders; risk integration requires review | Owner/외부 조건 대기 |
| 6 | [TASK-028](TASK-028-advanced-order-types-test-support.md) advanced order types test support | ASK | 보류 | Medium / score -1 | L · 8 ph | 회귀 리스크 감소; gate: Owner approval required before broker/order_flow changes that can affect... | Owner/외부 조건 대기 |
| 7 | [TASK-021](TASK-021-kis-margin-short.md) kis margin short | ASK | 보류 | Low / score -9 | L · 6 ph | 낮은/위생; gate: 보류 상태 — 해제 조건은 TASK 본문 확인 | Owner/외부 조건 대기 |
| 8 | [TASK-022](TASK-022-kis-overseas-order.md) kis overseas order | ASK | 보류 | Low / score -11 | L · 8 ph | 낮은/위생; gate: 보류 상태 — 해제 조건은 TASK 본문 확인 | Owner/외부 조건 대기 |
| 9 | [TASK-030](TASK-030-block-basket-execution-tests.md) block basket execution tests | ASK | 보류 | Low / score -11 | L · 8 ph | 회귀 리스크 감소; gate: Owner approval required before actual block/basket venue or broker submi... | Owner/외부 조건 대기 |
| 10 | [TASK-027](TASK-027-krx-derivatives-test-support.md) krx derivatives test support | ASK | 보류 | Low / score -13 | XL · 10 ph | 회귀 리스크 감소; gate: Owner approval required; derivatives order routing and risk policy are R... | Owner/외부 조건 대기 |

## 흐름 보드

### 대기 (next)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-038](TASK-038-watchlist-screener-alert-expansion.md) | High | UI/UX Designer | 4 ph / ~45000 tok | read-only UI/backend only; no order submission, order modification, broker order path, risk policy, schema migration, or prod mutation |
| [TASK-045](TASK-045-ui-overhaul-phase1-api-foundation-login.md) | High | Backend Engineer | 16 ph / ~120000 tok | no live orders; paper-safe; Owner 승인 전 prod 전환 금지 |
| [TASK-053](TASK-053-product-maturity-assessment.md) | High | Lead Engineer | 2 ph / ~15000 tok | - |
| [TASK-054](TASK-054-fix-alerts-settings-no-persist.md) | High | UI/UX Designer | 4 ph / ~30000 tok | - |
| [TASK-055](TASK-055-fix-home-proposal-buttons-noop.md) | High | UI/UX Designer | 3 ph / ~20000 tok | - |
| [TASK-056](TASK-056-fix-backend-allocation-gap.md) | High | Backend Engineer | 3 ph / ~25000 tok | - |
| [TASK-057](TASK-057-fix-kpi-returns-hardcoded-zero.md) | High | Backend Engineer | 6 ph / ~40000 tok | - |
| [TASK-058](TASK-058-fix-history-live-mode-early-return.md) | High | UI/UX Designer | 1 ph / ~10000 tok | - |
| [TASK-061](TASK-061-feat-price-alert-engine-loop.md) | High | Backend Engineer | 8 ph / ~50000 tok | - |
| [TASK-062](TASK-062-feat-krx-holiday-calendar.md) | High | Backend Engineer | 6 ph / ~40000 tok | - |
| [TASK-066](TASK-066-test-coverage-60pct.md) | High | QA | 12 ph / ~80000 tok | Phase 3 전 필수 |
| [TASK-067](TASK-067-fix-intraday-no-try-except.md) | High | UI/UX Designer | 2 ph / ~12000 tok | - |
| [TASK-039](TASK-039-backtest-research-report-hardening.md) | Medium | Quant Researcher | 4 ph / ~45000 tok | backtest/report/mock-only; no live scheduler, broker order path, risk policy, schema migration, or prod mutation |
| [TASK-040](TASK-040-portfolio-performance-tax-lot-reporting.md) | Medium | Performance Analyst | 4 ph / ~45000 tok | read-only reporting only; no tax advice, order submission, broker order path, risk policy, schema migration, or prod mutation |
| [TASK-041](TASK-041-broker-capability-feature-parity-matrix.md) | Medium | Lead Engineer | 3 ph / ~35000 tok | docs/config/test-only; no broker order implementation, order path, risk policy, schema migration, secret, or prod mutation |
| [TASK-046](TASK-046-ui-overhaul-phase2-home-portfolio.md) | Medium | UI/UX Designer | 12 ph / ~90000 tok | 선행 TASK-045 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요; no live orders |
| [TASK-048](TASK-048-ui-overhaul-phase4-agents-sse.md) | Medium | Backend Engineer | 12 ph / ~90000 tok | 선행 TASK-047 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 |
| [TASK-049](TASK-049-ui-overhaul-phase5-analysis-parity-retire.md) | Medium | UI/UX Designer | 16 ph / ~120000 tok | 선행 TASK-048 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요 |
| [TASK-059](TASK-059-fix-logout-incomplete-state-reset.md) | Medium | Backend Engineer | 2 ph / ~15000 tok | - |
| [TASK-060](TASK-060-sqlite-wal-fk-enforcement.md) | Medium | Backend Engineer | 3 ph / ~20000 tok | - |
| [TASK-065](TASK-065-feat-log-rotation.md) | Medium | Backend Engineer | 2 ph / ~12000 tok | - |

### 보류 (게이트 — 외부/결정 대기)

| ID | 우선순위 | Owner | 예상 | 게이트 / 태그 |
|----|----------|-------|------|----------------|
| [TASK-031](TASK-031-market-halt-vi-risk-gates.md) | High | Compliance Officer | 5 ph / ~50000 tok | Owner approval required before app/risk or live order-blocking policy changes |
| [TASK-047](TASK-047-ui-overhaul-phase3-trade-settings-gates.md) | High | Backend Engineer | 20 ph / ~150000 tok | Owner 명시 승인 필수 — state-changing 엔드포인트, R3 인접; blocked by TASK-046 |
| [TASK-014](TASK-014-kis-after-hours-order.md) | Medium | KIS API Engineer | 3 ph / ~50000 tok | Owner approval required: changes app/brokers/kis place_order order path, app/risk safety gates, and after-hours order policy. |
| [TASK-026](TASK-026-krx-alternative-products-test-support.md) | Medium | KIS API Engineer | 5 ph / ~50000 tok | Owner approval required before any live broker/order-path support; mock catalog tests may be drafted first |
| [TASK-028](TASK-028-advanced-order-types-test-support.md) | Medium | Backend Engineer | 8 ph / ~70000 tok | Owner approval required before broker/order_flow changes that can affect live order behavior |
| [TASK-032](TASK-032-data-quality-corporate-action-tests.md) | Medium | Data Engineer | 5 ph / ~45000 tok | no live orders; risk integration requires review |
| [TASK-021](TASK-021-kis-margin-short.md) | Low | KIS API Engineer | 6 ph / ~50000 tok | kis,margin,short |
| [TASK-022](TASK-022-kis-overseas-order.md) | Low | KIS API Engineer | 8 ph / ~50000 tok | kis,overseas,us-stocks |
| [TASK-027](TASK-027-krx-derivatives-test-support.md) | Low | KIS API Engineer | 10 ph / ~80000 tok | Owner approval required; derivatives order routing and risk policy are R3 surfaces |
| [TASK-030](TASK-030-block-basket-execution-tests.md) | Low | Backend Engineer | 8 ph / ~70000 tok | Owner approval required before actual block/basket venue or broker submission support |

