# VIEW — TASK by Priority

> 이 파일은 `scripts/generate_views.py` 가 자동 생성한다. 직접 수정하지 말 것.
> 생성 시각: `2026-06-26T21:02:58+09:00`
> 원본: `agents/lead_engineer/tasks/TASK-*.md` 의 YAML frontmatter

필터링은 `python scripts/query_tasks.py --help` 참조.

---

## Critical

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-064](TASK-064-fix-condition-toctou-race.md) | 완료 | Critical | 상 | 8 ph / ~60000 tok | Backend Engineer | bug,safety,race-condition,database,order-flow |

## High

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-010](TASK-010-kis-websocket-realtime.md) | 완료 | High | 상 | 8 ph / ~50000 tok | KIS API Engineer | kis,websocket,realtime |
| [TASK-011](TASK-011-kis-intraday-chart.md) | 완료 | High | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,chart,intraday |
| [TASK-023](TASK-023-kis-engine-e2e-validation.md) | 완료 | High | 중 | 2 ph / ~50000 tok | KIS API Engineer | kis,engine,e2e,validation |
| [TASK-024](TASK-024-paper-scenario-matrix-validation.md) | 완료 | High | 중 | 1 ph / ~20000 tok | QA | paper,qa,scenario-matrix,engine,risk,ui |
| [TASK-025](TASK-025-quant-trading-scenario-catalog.md) | 완료 | High | 중 | 1 ph / ~25000 tok | QA | qa,quant,paper,scenario-catalog,engine |
| [TASK-029](TASK-029-fix-style-order-lifecycle-tests.md) | 완료 | High | 중 | 4 ph / ~45000 tok | Backend Engineer | qa,order-lifecycle,partial-fill,fix,mock |
| [TASK-031](TASK-031-market-halt-vi-risk-gates.md) | 완료 | High | 중 | 5 ph / ~50000 tok | Compliance Officer | qa,risk,compliance,halt,vi,disclosure |
| [TASK-035](TASK-035-market-hours-kis-ui-verification.md) | 완료 | High | 중 | 2 ph / ~30000 tok | QA | qa,kis,ui,paper,market-hours,verification |
| [TASK-036](TASK-036-paper-transaction-ui-sync-soak.md) | 완료 | High | 중 | 2 ph / ~35000 tok | QA | qa,kis,paper,transaction,ui-sync,soak |
| [TASK-037](TASK-037-feature-landscape-research.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Research Agent | research,feature-landscape,backlog,planning |
| [TASK-038](TASK-038-watchlist-screener-alert-expansion.md) | 완료 | High | 중 | 4 ph / ~45000 tok | UI/UX Designer | feature-landscape,watchlist,screener,alerts,ui,read-only |
| [TASK-042](TASK-042-asset-universe-decision-record.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Research Agent | research,asset-universe,approval-record,capability,backlog |
| [TASK-043](TASK-043-external-app-api-decision-record.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Research Agent | research,external-api,integrations,approval-record,capability,backlog |
| [TASK-044](TASK-044-external-api-owner-setup-manual.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Doc Steward | docs,external-api,integrations,owner-manual,setup,secrets |
| [TASK-045](TASK-045-ui-overhaul-phase1-api-foundation-login.md) | 완료 | High | 상 | 16 ph / ~120000 tok | Backend Engineer | ui-overhaul,fastapi,next-js,authentication,login,phase1 |
| [TASK-047](TASK-047-ui-overhaul-phase3-trade-settings-gates.md) | 완료 | High | 상 | 20 ph / ~150000 tok | Backend Engineer | ui-overhaul,fastapi,trade,settings,safety-gates,phase3,r3-adjacent |
| [TASK-050](TASK-050-fix-daily-limit-utc-localtime.md) | 완료 | High | 중 | 3 ph / ~25000 tok | Backend Engineer | bug,safety,daily-limit,utc,localtime,database |
| [TASK-051](TASK-051-fix-compliance-gate-fail-open.md) | 완료 | High | 중 | 4 ph / ~30000 tok | Backend Engineer | bug,safety,compliance,gate,fail-open,trading |
| [TASK-053](TASK-053-product-maturity-assessment.md) | 완료 | High | 중 | 2 ph / ~15000 tok | Lead Engineer | assessment,metrics,reporting |
| [TASK-054](TASK-054-fix-alerts-settings-no-persist.md) | 완료 | High | 중 | 4 ph / ~30000 tok | UI/UX Designer | bug,ui,alerts,persistence |
| [TASK-055](TASK-055-fix-home-proposal-buttons-noop.md) | 완료 | High | 중 | 3 ph / ~20000 tok | UI/UX Designer | bug,ui,home,ic,proposals |
| [TASK-056](TASK-056-fix-backend-allocation-gap.md) | 완료 | High | 중 | 3 ph / ~25000 tok | Backend Engineer | bug,backend,portfolio,allocation |
| [TASK-057](TASK-057-fix-kpi-returns-hardcoded-zero.md) | 완료 | High | 중-상 | 6 ph / ~40000 tok | Backend Engineer | bug,backend,kpi,performance |
| [TASK-058](TASK-058-fix-history-live-mode-early-return.md) | 완료 | High | 낮 | 1 ph / ~10000 tok | UI/UX Designer | bug,ui,history,pnl |
| [TASK-061](TASK-061-feat-price-alert-engine-loop.md) | 완료 | High | 중-상 | 8 ph / ~50000 tok | Backend Engineer | feature,engine,alerts,notifications |
| [TASK-062](TASK-062-feat-krx-holiday-calendar.md) | 완료 | High | 중 | 6 ph / ~40000 tok | Backend Engineer | feature,safety,trading-window,holidays |
| [TASK-063](TASK-063-fix-circuit-breaker-pnl-logic.md) | 완료 | High | 중 | 4 ph / ~30000 tok | Backend Engineer | bug,safety,circuit-breaker,pnl |
| [TASK-066](TASK-066-test-coverage-60pct.md) | 완료 | High | 중 | 12 ph / ~80000 tok | QA | testing,coverage,safety |
| [TASK-067](TASK-067-fix-intraday-no-try-except.md) | 완료 | High | 낮 | 2 ph / ~12000 tok | UI/UX Designer | bug,ui,analysis,error-handling |
| [TASK-070](TASK-070-sso-sns-premarket-agent-summary.md) | 완료 | High | 중-상 | 5 ph / ~45000 tok | Lead Engineer | authentication,sso,sns-login,agents,premarket,lint,ui-overhaul |
| [TASK-071](TASK-071-stop-hook-owner-governance-host-mode.md) | 완료 | High | 중 | 1 ph / ~12000 tok | Lead Engineer | governance,hooks,owner-gate,host-mode |
| [TASK-074](TASK-074-investor-profile-survey.md) | 완료 | High | 중 | 4 ph / ~80000 tok | Lead Engineer | profile,survey,onboarding,personalization,database,ui,safety |
| [TASK-087](TASK-087-web-deploy-membership-gating.md) | 대기 | High | 상 | 24 ph / ~200000 tok | Lead Engineer | deploy,web,auth,membership,payment,multitenant,compliance,supabase,vercel |
| [TASK-088](TASK-088-presale-regulatory-clearance.md) | 보류 | High | 상 | 16 ph / ~120000 tok | Lead Engineer | compliance,regulatory,legal,gate,deferred,deploy |
| [TASK-092](TASK-092-business-plan-agent-lane.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Lead Engineer | business-plan,agents,regulatory-admin,marketing,hwpx,governance |
| [TASK-093](TASK-093-business-plan-v1.md) | 완료 | High | 중-상 | 4 ph / ~60000 tok | Business Planner | business-plan,vision,strategy,owner-interview,go-to-market,marketing |
| [TASK-095](TASK-095-marketing-materials-v1.md) | 완료 | High | 중 | 4 ph / ~50000 tok | Marketing Growth | marketing,go-to-market,campaign,pdf,pptx,early-users |
| [TASK-098](TASK-098-membership-access-manual-deposit-plan.md) | 완료 | High | 중 | 1 ph / ~12000 tok | Lead Engineer | membership,payment,bank-transfer,approval,signup,taskset |
| [TASK-099](TASK-099-membership-local-autoregister-fail-closed.md) | 완료 | High | 중 | 1 ph / ~16000 tok | Backend Engineer | auth,membership,approval,safety,tests |
| [TASK-100](TASK-100-membership-local-request-approval-prototype.md) | 완료 | High | 상 | 2 ph / ~30000 tok | Backend Engineer | auth,membership,approval,signup,local-prototype,tests |
| [TASK-101](TASK-101-membership-admin-settings-tab.md) | 완료 | High | 중 | 1 ph / ~18000 tok | UI/UX Designer | auth,membership,approval,admin-ui,settings,local-prototype |
| [TASK-102](TASK-102-membership-local-account-grant.md) | 완료 | High | 중 | 1 ph / ~22000 tok | Backend Engineer | auth,membership,approval,account-grant,subscription,local-prototype |
| [TASK-103](TASK-103-membership-local-deposit-recognition.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,deposit-recognition,bank-transfer,approval,local-prototype |
| [TASK-104](TASK-104-membership-member-admin-boundary.md) | 완료 | High | 중 | 1 ph / ~16000 tok | Backend Engineer | auth,membership,authorization,member-boundary,local-prototype |
| [TASK-105](TASK-105-membership-guest-demo-fail-closed.md) | 완료 | High | 중 | 1 ph / ~14000 tok | Backend Engineer | auth,membership,guest-demo,fail-closed,local-prototype |
| [TASK-106](TASK-106-membership-app-user-read-boundary.md) | 완료 | High | 중 | 1 ph / ~16000 tok | Backend Engineer | auth,membership,read-scope,app-user,local-prototype |
| [TASK-108](TASK-108-membership-production-readiness-gate.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,readiness,deploy-gate,production,local-prototype |
| [TASK-109](TASK-109-membership-supabase-rls-contract.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,supabase,rls,production-contract,deploy-gate |
| [TASK-110](TASK-110-membership-applicant-deposit-status-lookup.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,signup,deposit-instructions,applicant-status,local-prototype |
| [TASK-111](TASK-111-membership-payment-evidence-policy.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,payment-evidence,policy,quality-gate,production-readiness |
| [TASK-112](TASK-112-membership-production-secret-policy.md) | 완료 | High | 중 | 1 ph / ~20000 tok | Backend Engineer | membership,secrets,policy,quality-gate,production-readiness |
| [TASK-113](TASK-113-membership-per-user-engine-safety-contract.md) | 완료 | High | 중 | 1 ph / ~22000 tok | Lead Engineer | membership,engine-safety,multitenant,contract,production-readiness |
| [TASK-114](TASK-114-membership-tenant-isolation-matrix.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Backend Engineer | membership,supabase,rls,tenant-isolation,deploy-gate |
| [TASK-115](TASK-115-membership-production-implementation-plan.md) | 완료 | High | 중 | 1 ph / ~16000 tok | Lead Engineer | membership,production-readiness,implementation-plan,taskset |
| [TASK-116](TASK-116-membership-supabase-staging-schema-field-map.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Backend Engineer | membership,supabase,rls,schema,field-map,production-readiness |
| [TASK-118](TASK-118-membership-production-secret-store-implementation-plan.md) | 완료 | High | 중 | 2 ph / ~30000 tok | Backend Engineer | membership,secrets,oauth,kis,production-readiness |
| [TASK-125](TASK-125-membership-kis-commercial-terms-review-packet.md) | 완료 | High | 중 | 1 ph / ~18000 tok | Compliance Officer | membership,kis,open-api,terms,compliance |
| [TASK-128](TASK-128-compliance-business-routing-alignment.md) | 완료 | High | 낮 | 1 ph / ~12000 tok | Lead Engineer | business-plan,compliance,agents,routing,marketing,regulatory |
| [TASK-140](TASK-140-ui-visual-assets-expansion-adoption.md) | 완료 | High | 상 | 16 ph / ~180000 tok | UI/UX Designer | ui,dataviz,assets,icons,fonts,illustration,avatar,opensource,license |
| [TASK-166](TASK-166-marketing-team-operating-model.md) | 완료 | High | 중 | 2 ph / ~25000 tok | Lead Engineer | marketing,agents,operating-model,routing,go-to-market |
| [TASK-167](TASK-167-promotion-campaign-backlog-calendar-v1.md) | 완료 | High | 중 | 3 ph / ~35000 tok | Marketing Growth | marketing,campaign,content-calendar,claim-bank,early-users |
| [TASK-171](TASK-171-finance-accounting-planning-support-lane.md) | 완료 | High | 중 | 3 ph / ~45000 tok | Finance Accounting | finance,accounting,portfolio,planning,operations,roadmap |
| [TASK-172](TASK-172-finance-scenario-input-contract.md) | 완료 | High | 중 | 3 ph / ~45000 tok | Finance Accounting | finance,accounting,scenario,portfolio,planning |

## Medium

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-002](TASK-002-kis-reference-pack.md) | 완료 | Medium | 중 | 1 ph / ~10000 tok | Lead Engineer | kis,docs |
| [TASK-004](TASK-004-runtime-update-gate.md) | 완료 | Medium | 중 | 1 ph / ~10000 tok | Lead Engineer | agent-runtime,sync |
| [TASK-012](TASK-012-kis-long-term-order-history.md) | 완료 | Medium | 낮 | 2 ph / ~50000 tok | KIS API Engineer | kis,history |
| [TASK-013](TASK-013-kis-batch-price.md) | 완료 | Medium | 낮 | 2 ph / ~50000 tok | KIS API Engineer | kis,price,performance |
| [TASK-014](TASK-014-kis-after-hours-order.md) | 완료 | Medium | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,order,after-hours |
| [TASK-026](TASK-026-krx-alternative-products-test-support.md) | 완료 | Medium | 상 | 5 ph / ~50000 tok | KIS API Engineer | kis,qa,asset-class,bond,reit,elw,etn |
| [TASK-028](TASK-028-advanced-order-types-test-support.md) | 완료 | Medium | 상 | 8 ph / ~70000 tok | Backend Engineer | qa,order-types,stop,trailing,ioc,fok,moo,moc |
| [TASK-032](TASK-032-data-quality-corporate-action-tests.md) | 완료 | Medium | 중 | 5 ph / ~45000 tok | Data Engineer | qa,data-quality,corporate-actions,holiday,stale-data |
| [TASK-033](TASK-033-portfolio-reality-model-tests.md) | 완료 | Medium | 중 | 5 ph / ~45000 tok | Performance Analyst | qa,portfolio,cash,fees,slippage,concentration |
| [TASK-034](TASK-034-scheduled-strategy-pattern-tests.md) | 완료 | Medium | 중 | 6 ph / ~55000 tok | Quant Researcher | qa,strategy,scheduler,dca,pairs,volatility,rebalance |
| [TASK-039](TASK-039-backtest-research-report-hardening.md) | 완료 | Medium | 중 | 4 ph / ~45000 tok | Quant Researcher | feature-landscape,backtest,research,reports,qa |
| [TASK-040](TASK-040-portfolio-performance-tax-lot-reporting.md) | 완료 | Medium | 중 | 4 ph / ~45000 tok | Performance Analyst | feature-landscape,portfolio,performance,reporting,read-only |
| [TASK-041](TASK-041-broker-capability-feature-parity-matrix.md) | 완료 | Medium | 중 | 3 ph / ~35000 tok | Lead Engineer | feature-landscape,broker-capability,parity,docs,qa |
| [TASK-046](TASK-046-ui-overhaul-phase2-home-portfolio.md) | 완료 | Medium | 중 | 12 ph / ~90000 tok | UI/UX Designer | ui-overhaul,next-js,home,portfolio,phase2 |
| [TASK-048](TASK-048-ui-overhaul-phase4-agents-sse.md) | 완료 | Medium | 중 | 12 ph / ~90000 tok | Backend Engineer | ui-overhaul,sse,agents,ic,notifications,phase4 |
| [TASK-049](TASK-049-ui-overhaul-phase5-analysis-parity-retire.md) | 완료 | Medium | 상 | 16 ph / ~120000 tok | UI/UX Designer | ui-overhaul,analysis,parity,streamlit-retire,phase5 |
| [TASK-059](TASK-059-fix-logout-incomplete-state-reset.md) | 완료 | Medium | 낮 | 2 ph / ~15000 tok | Backend Engineer | bug,security,session,logout |
| [TASK-060](TASK-060-sqlite-wal-fk-enforcement.md) | 완료 | Medium | 중 | 3 ph / ~20000 tok | Backend Engineer | database,performance,integrity,sqlite |
| [TASK-065](TASK-065-feat-log-rotation.md) | 완료 | Medium | 낮 | 2 ph / ~12000 tok | Backend Engineer | ops,logging,maintenance |
| [TASK-068](TASK-068-agent-runtime-eval-pilot.md) | 완료 | Medium | 중 | 3 ph / ~20000 tok | Performance Analyst | agent-runtime,eval,benchmark,pilot,dogfooding |
| [TASK-069](TASK-069-product-maturity-reassessment-2026-12.md) | 보류 | Medium | 중 | 2 ph / ~15000 tok | Lead Engineer | assessment,metrics,reporting,semi-annual,deferred,scheduled |
| [TASK-072](TASK-072-dev-mock-sso-provider.md) | 완료 | Medium | 낮 | 1 ph / ~12000 tok | Lead Engineer | authentication,sso,mock,dev-mode,ui-overhaul |
| [TASK-073](TASK-073-defer-future-maturity-reassessment.md) | 완료 | Medium | 낮 | 0.5 ph / ~6000 tok | Lead Engineer | backlog,governance,deferred,scheduling |
| [TASK-096](TASK-096-promotion-publishing-pipeline.md) | 완료 | Medium | 상 | 8 ph / ~80000 tok | Marketing Growth | marketing,sns,external-api,publishing,automation,audit-log |
| [TASK-097](TASK-097-sales-revenue-lane-decision.md) | 완료 | Medium | 중 | 3 ph / ~40000 tok | Business Planner | sales,revenue,go-to-market,agents,pricing,crm |
| [TASK-117](TASK-117-membership-payment-recognition-decision-packet.md) | 완료 | Medium | 중 | 2 ph / ~35000 tok | Regulatory Admin | membership,payment,bank-transfer,recognition,decision-packet |
| [TASK-119](TASK-119-membership-staging-deploy-preflight-checklist.md) | 완료 | Medium | 중 | 2 ph / ~25000 tok | CI/CD Engineer | membership,deploy,staging,preflight,vercel,railway,supabase |
| [TASK-120](TASK-120-membership-staging-env-inventory-template.md) | 완료 | Medium | 중 | 1 ph / ~16000 tok | CI/CD Engineer | membership,deploy,staging,env,preflight |
| [TASK-121](TASK-121-membership-railway-port-healthcheck-readiness.md) | 완료 | Medium | 중 | 1 ph / ~16000 tok | Backend Engineer | membership,deploy,railway,healthcheck,preflight |
| [TASK-122](TASK-122-membership-staging-persistent-storage-decision.md) | 완료 | Medium | 중 | 2 ph / ~22000 tok | Backend Engineer | membership,deploy,storage,staging,preflight |
| [TASK-123](TASK-123-membership-supabase-staging-migration-rls-review-packet.md) | 완료 | Medium | 중 | 2 ph / ~26000 tok | Backend Engineer | membership,supabase,staging,rls,migration-review |
| [TASK-124](TASK-124-membership-supabase-backup-apply-evidence-checklist.md) | 완료 | Medium | 중 | 1 ph / ~16000 tok | Backend Engineer | membership,supabase,staging,backup,evidence |
| [TASK-126](TASK-126-membership-readiness-surface-sync.md) | 완료 | Medium | 낮 | 1 ph / ~12000 tok | Lead Engineer | membership,readiness,governance,owner-surface |
| [TASK-127](TASK-127-business-admin-document-packet-schema.md) | 완료 | Medium | 중 | 1 ph / ~18000 tok | Regulatory Admin | business-admin,document-packet,hwpx,business-registration,governance |
| [TASK-129](TASK-129-promotion-channel-policy-matrix.md) | 완료 | Medium | 중 | 2 ph / ~30000 tok | Marketing Growth | marketing,sns,external-api,publishing,policy,research |
| [TASK-130](TASK-130-promotion-publishing-state-machine-contract.md) | 완료 | Medium | 중 | 2 ph / ~25000 tok | Marketing Growth | marketing,sns,publishing,state-machine,audit-log |
| [TASK-131](TASK-131-promotion-dry-run-audit-preview.md) | 완료 | Medium | 중 | 3 ph / ~40000 tok | Backend Engineer | marketing,sns,publishing,dry-run,audit-log |
| [TASK-132](TASK-132-promotion-asset-rendering-contract.md) | 완료 | Medium | 중 | 2 ph / ~25000 tok | Marketing Growth | marketing,assets,pdf,pptx,rendering,gate |
| [TASK-133](TASK-133-promotion-asset-preview-manifest.md) | 완료 | Medium | 중 | 3 ph / ~35000 tok | Marketing Growth | marketing,assets,pdf,pptx,rendering,preview |
| [TASK-168](TASK-168-promotion-asset-generator-readiness-map.md) | 완료 | Medium | 중 | 3 ph / ~35000 tok | Doc Steward | marketing,assets,pdf,pptx,rendering,readiness |
| [TASK-169](TASK-169-sns-publishing-automation-readiness-backlog.md) | 완료 | Medium | 중-상 | 4 ph / ~45000 tok | Backend Engineer | marketing,sns,publishing,automation,external-api,readiness |
| [TASK-170](TASK-170-sales-handoff-readiness-checklist.md) | 완료 | Medium | 중 | 2 ph / ~25000 tok | Business Planner | marketing,sales,revenue,handoff,crm,pricing |
| [TASK-173](TASK-173-portfolio-goal-gap-read-model.md) | 완료 | Medium | 중 | 5 ph / ~70000 tok | Backend Engineer | finance,accounting,portfolio,backend,read-model |
| [TASK-174](TASK-174-finance-roadmap-ui-preview.md) | 완료 | Medium | 중 | 5 ph / ~70000 tok | UI/UX Designer | finance,accounting,portfolio,ui,roadmap |

## Low

| ID | 상태 | 우선순위 | 난이도 | 예상 비용 | Owner | Tags |
|----|------|----------|--------|-----------|-------|------|
| [TASK-003](TASK-003-bilingual-readme.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | docs,readme |
| [TASK-005](TASK-005-doc-and-backlog-link-hygiene.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | docs,backlog |
| [TASK-006](TASK-006-cycle-review-sequencing.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | cycle,review |
| [TASK-007](TASK-007-roles-due-alignment.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | roles,governance |
| [TASK-008](TASK-008-streamlit-legacy-wrapper.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | streamlit,compatibility |
| [TASK-009](TASK-009-orchestrator-import-check.md) | 완료 | Low | 중 | 1 ph / ~10000 tok | Lead Engineer | agent-runtime,import |
| [TASK-015](TASK-015-kis-index-price.md) | 완료 | Low | 낮 | 1 ph / ~50000 tok | KIS API Engineer | kis,index |
| [TASK-016](TASK-016-kis-fundamental-data.md) | 완료 | Low | 중 | 4 ph / ~50000 tok | KIS API Engineer | kis,fundamental,research |
| [TASK-017](TASK-017-kis-dividend-info.md) | 완료 | Low | 낮 | 2 ph / ~50000 tok | KIS API Engineer | kis,dividend |
| [TASK-018](TASK-018-kis-order-book.md) | 완료 | Low | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,orderbook,realtime |
| [TASK-019](TASK-019-kis-sector-price.md) | 완료 | Low | 낮 | 2 ph / ~50000 tok | KIS API Engineer | kis,sector |
| [TASK-020](TASK-020-kis-disclosure.md) | 완료 | Low | 중 | 3 ph / ~50000 tok | KIS API Engineer | kis,disclosure,compliance |
| [TASK-021](TASK-021-kis-margin-short.md) | 완료 | Low | 상 | 6 ph / ~50000 tok | KIS API Engineer | kis,margin,short |
| [TASK-022](TASK-022-kis-overseas-order.md) | 완료 | Low | 상 | 8 ph / ~50000 tok | KIS API Engineer | kis,overseas,us-stocks |
| [TASK-027](TASK-027-krx-derivatives-test-support.md) | 완료 | Low | 상 | 10 ph / ~80000 tok | KIS API Engineer | kis,qa,derivatives,futures,options,fx-futures |
| [TASK-030](TASK-030-block-basket-execution-tests.md) | 완료 | Low | 상 | 8 ph / ~70000 tok | Backend Engineer | qa,basket,block-trade,multi-leg,execution |
| [TASK-052](TASK-052-fix-trade-ack-checkbox-loop.md) | 완료 | Low | 중 | 2 ph / ~15000 tok | UI/UX Designer | bug,ui,streamlit,trade,acknowledgement,checkbox |

