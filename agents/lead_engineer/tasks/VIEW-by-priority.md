# VIEW — TASK by Priority

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-12T23:52:55+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

## High

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-010](TASK-010-kis-websocket-realtime.md) | 완료 | High | 상 | 8 ph / ~50000 tok | KIS API Engineer | kis,websocket,realtime |
| [TASK-011](TASK-011-kis-intraday-chart.md) | 완료 | High | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,chart,intraday |
| [TASK-023](TASK-023-kis-engine-e2e-validation.md) | 완료 | High | 중 | 2 ph / ~50000 tok | KIS API Engineer | kis,engine,e2e,validation |
| [TASK-024](TASK-024-paper-scenario-matrix-validation.md) | 완료 | High | 중 | 1 ph / ~20000 tok | QA | paper,qa,scenario-matrix,engine,risk,ui |
| [TASK-025](TASK-025-quant-trading-scenario-catalog.md) | 완료 | High | 중 | 1 ph / ~25000 tok | QA | qa,quant,paper,scenario-catalog,engine |
| [TASK-029](TASK-029-fix-style-order-lifecycle-tests.md) | 완료 | High | 중 | 4 ph / ~45000 tok | Backend Engineer | qa,order-lifecycle,partial-fill,fix,mock |
| [TASK-031](TASK-031-market-halt-vi-risk-gates.md) | 보류 | High | 중 | 5 ph / ~50000 tok | Compliance Officer | qa,risk,compliance,halt,vi,disclosure |
| [TASK-035](TASK-035-market-hours-kis-ui-verification.md) | 완료 | High | 중 | 2 ph / ~30000 tok | QA | qa,kis,ui,paper,market-hours,verification |
| [TASK-036](TASK-036-paper-transaction-ui-sync-soak.md) | 완료 | High | 중 | 2 ph / ~35000 tok | QA | qa,kis,paper,transaction,ui-sync,soak |

## Medium

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-002](TASK-002-kis-reference-pack.md) | 완료 | Medium | 중 | 1 ph / ~10000 tok | Lead Engineer | kis,docs |
| [TASK-004](TASK-004-runtime-update-gate.md) | 완료 | Medium | 중 | 1 ph / ~10000 tok | Lead Engineer | agent-runtime,sync |
| [TASK-012](TASK-012-kis-long-term-order-history.md) | 완료 | Medium | 하 | 2 ph / ~50000 tok | KIS API Engineer | kis,history |
| [TASK-013](TASK-013-kis-batch-price.md) | 완료 | Medium | 하 | 2 ph / ~50000 tok | KIS API Engineer | kis,price,performance |
| [TASK-014](TASK-014-kis-after-hours-order.md) | 보류 | Medium | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,order,after-hours |
| [TASK-026](TASK-026-krx-alternative-products-test-support.md) | 보류 | Medium | 상 | 5 ph / ~50000 tok | KIS API Engineer | kis,qa,asset-class,bond,reit,elw,etn |
| [TASK-028](TASK-028-advanced-order-types-test-support.md) | 보류 | Medium | 상 | 8 ph / ~70000 tok | Backend Engineer | qa,order-types,stop,trailing,ioc,fok,moo,moc |
| [TASK-032](TASK-032-data-quality-corporate-action-tests.md) | 진행 중 | Medium | 중 | 5 ph / ~45000 tok | Data Engineer | qa,data-quality,corporate-actions,holiday,stale-data |
| [TASK-033](TASK-033-portfolio-reality-model-tests.md) | 완료 | Medium | 중 | 5 ph / ~45000 tok | Performance Analyst | qa,portfolio,cash,fees,slippage,concentration |
| [TASK-034](TASK-034-scheduled-strategy-pattern-tests.md) | 대기 | Medium | 중 | 6 ph / ~55000 tok | Quant Researcher | qa,strategy,scheduler,dca,pairs,volatility,rebalance |

## Low

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-003](TASK-003-bilingual-readme.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | docs,readme |
| [TASK-005](TASK-005-doc-and-backlog-link-hygiene.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | docs,backlog |
| [TASK-006](TASK-006-cycle-review-sequencing.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | cycle,review |
| [TASK-007](TASK-007-roles-due-alignment.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | roles,governance |
| [TASK-008](TASK-008-streamlit-legacy-wrapper.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | streamlit,compatibility |
| [TASK-009](TASK-009-orchestrator-import-check.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | agent-runtime,import |
| [TASK-015](TASK-015-kis-index-price.md) | 완료 | Low | 하 | 1 ph / ~50000 tok | KIS API Engineer | kis,index |
| [TASK-016](TASK-016-kis-fundamental-data.md) | 완료 | Low | 중 | 4 ph / ~50000 tok | KIS API Engineer | kis,fundamental,research |
| [TASK-017](TASK-017-kis-dividend-info.md) | 완료 | Low | 하 | 2 ph / ~50000 tok | KIS API Engineer | kis,dividend |
| [TASK-018](TASK-018-kis-order-book.md) | 완료 | Low | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,orderbook,realtime |
| [TASK-019](TASK-019-kis-sector-price.md) | 완료 | Low | 하 | 2 ph / ~50000 tok | KIS API Engineer | kis,sector |
| [TASK-020](TASK-020-kis-disclosure.md) | 완료 | Low | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,disclosure,compliance |
| [TASK-021](TASK-021-kis-margin-short.md) | 보류 | Low | 상 | 6 ph / ~50000 tok | KIS API Engineer | kis,margin,short |
| [TASK-022](TASK-022-kis-overseas-order.md) | 보류 | Low | 상 | 8 ph / ~50000 tok | KIS API Engineer | kis,overseas,us-stocks |
| [TASK-027](TASK-027-krx-derivatives-test-support.md) | 보류 | Low | 상 | 10 ph / ~80000 tok | KIS API Engineer | kis,qa,derivatives,futures,options,fx-futures |
| [TASK-030](TASK-030-block-basket-execution-tests.md) | 보류 | Low | 상 | 8 ph / ~70000 tok | Backend Engineer | qa,basket,block-trade,multi-leg,execution |

