---
type: work_item_classification
id: WORK-ITEM-CLASSIFICATION-agent-runtime
audience: owner
status: pass
signal: pass
score: 95
priority: High
tags: [work-items, hierarchy, numbering, generated-index]
generated_at: 2026-06-26T21:32:50+09:00
record_count: 196
---

# Work Item Classification

## Bottom Line
- Summary: generated Owner-facing numbers for `196` initiative/taskset/task/unit records.
- Result: planners can register stable records without manually reserving human task numbers.

## Signal
| Metric | State | Evidence |
| --- | --- | --- |
| Initiatives | pass | `29` records |
| Tasksets | pass | `14` records |
| Tasks | pass | `125` records |
| Units | pass | `28` records |
| Findings | pass | `0` findings |

## Insight
- Human-readable numbers are generated views, not canonical identities.
- Canonical identity remains stable IDs plus UUID metadata; this avoids concurrent pane number collisions.
- `0.*` numbers are legacy/unassigned work that predates initiative metadata.

## Decision
- Decision: use generated `Initiative N -> Taskset N.N -> Task N.N.N -> Unit N.N.N.N` labels for Owner-facing recognition.
- Decision: do not let planners hand-allocate display ordinals during registration.
- Decision: keep `scripts/work_item_classifier.py --check` in governance so stale classification is blocked.

## Action Board
| Number | Label | Level | ID | Parent | Status | Path | Title |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Initiative 0 | initiative | `INIT-UNASSIGNED` | - | synthetic | `-` | Unassigned / legacy work |
| 0.1 | Taskset 0.1 | taskset | `TASKSET-AR-UNCLASSIFIED` | `INIT-UNASSIGNED` | active | `BACKLOG-BOARD.md` | Unclassified |
| 0.1.1 | Task 0.1.1 | task | `TASK-002` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-002-kis-reference-pack.md` | 상태: 완료 |
| 0.1.2 | Task 0.1.2 | task | `TASK-003` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-003-bilingual-readme.md` | 상태: 완료 |
| 0.1.3 | Task 0.1.3 | task | `TASK-004` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-004-runtime-update-gate.md` | 상태: 완료 |
| 0.1.4 | Task 0.1.4 | task | `TASK-005` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-005-doc-and-backlog-link-hygiene.md` | 상태: 완료 |
| 0.1.5 | Task 0.1.5 | task | `TASK-006` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-006-cycle-review-sequencing.md` | 상태: 완료 |
| 0.1.6 | Task 0.1.6 | task | `TASK-007` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-007-roles-due-alignment.md` | 상태: 완료 |
| 0.1.7 | Task 0.1.7 | task | `TASK-008` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-008-streamlit-legacy-wrapper.md` | 상태: 완료 |
| 0.1.8 | Task 0.1.8 | task | `TASK-009` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-009-orchestrator-import-check.md` | 상태: 완료 |
| 0.1.9 | Task 0.1.9 | task | `TASK-010` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-010-kis-websocket-realtime.md` | 작업 ID: TASK-010 |
| 0.1.10 | Task 0.1.10 | task | `TASK-011` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-011-kis-intraday-chart.md` | 작업 ID: TASK-011 |
| 0.1.11 | Task 0.1.11 | task | `TASK-012` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-012-kis-long-term-order-history.md` | 작업 ID: TASK-012 |
| 0.1.12 | Task 0.1.12 | task | `TASK-013` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-013-kis-batch-price.md` | 작업 ID: TASK-013 |
| 0.1.13 | Task 0.1.13 | task | `TASK-014` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-014-kis-after-hours-order.md` | 작업 ID: TASK-014 |
| 0.1.14 | Task 0.1.14 | task | `TASK-015` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-015-kis-index-price.md` | 작업 ID: TASK-015 |
| 0.1.15 | Task 0.1.15 | task | `TASK-016` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-016-kis-fundamental-data.md` | 작업 ID: TASK-016 |
| 0.1.16 | Task 0.1.16 | task | `TASK-017` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-017-kis-dividend-info.md` | 작업 ID: TASK-017 |
| 0.1.17 | Task 0.1.17 | task | `TASK-018` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-018-kis-order-book.md` | 작업 ID: TASK-018 |
| 0.1.18 | Task 0.1.18 | task | `TASK-019` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-019-kis-sector-price.md` | 작업 ID: TASK-019 |
| 0.1.19 | Task 0.1.19 | task | `TASK-020` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-020-kis-disclosure.md` | 작업 ID: TASK-020 |
| 0.1.20 | Task 0.1.20 | task | `TASK-021` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-021-kis-margin-short.md` | 작업 ID: TASK-021 |
| 0.1.21 | Task 0.1.21 | task | `TASK-022` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-022-kis-overseas-order.md` | 작업 ID: TASK-022 |
| 0.1.22 | Task 0.1.22 | task | `TASK-023` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-023-kis-engine-e2e-validation.md` | 작업 ID: TASK-023 |
| 0.1.23 | Task 0.1.23 | task | `TASK-024` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-024-paper-scenario-matrix-validation.md` | 작업 ID: TASK-024 |
| 0.1.24 | Task 0.1.24 | task | `TASK-025` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-025-quant-trading-scenario-catalog.md` | 작업 ID: TASK-025 |
| 0.1.25 | Task 0.1.25 | task | `TASK-026` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-026-krx-alternative-products-test-support.md` | 작업 ID: TASK-026 |
| 0.1.26 | Task 0.1.26 | task | `TASK-027` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-027-krx-derivatives-test-support.md` | 작업 ID: TASK-027 |
| 0.1.27 | Task 0.1.27 | task | `TASK-028` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-028-advanced-order-types-test-support.md` | 작업 ID: TASK-028 |
| 0.1.28 | Task 0.1.28 | task | `TASK-029` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-029-fix-style-order-lifecycle-tests.md` | 작업 ID: TASK-029 |
| 0.1.29 | Task 0.1.29 | task | `TASK-030` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-030-block-basket-execution-tests.md` | 작업 ID: TASK-030 |
| 0.1.30 | Task 0.1.30 | task | `TASK-031` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-031-market-halt-vi-risk-gates.md` | 작업 ID: TASK-031 |
| 0.1.31 | Task 0.1.31 | task | `TASK-032` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-032-data-quality-corporate-action-tests.md` | 작업 ID: TASK-032 |
| 0.1.32 | Task 0.1.32 | task | `TASK-033` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-033-portfolio-reality-model-tests.md` | 작업 ID: TASK-033 |
| 0.1.33 | Task 0.1.33 | task | `TASK-034` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-034-scheduled-strategy-pattern-tests.md` | 작업 ID: TASK-034 |
| 0.1.34 | Task 0.1.34 | task | `TASK-035` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-035-market-hours-kis-ui-verification.md` | 작업 ID: TASK-035 |
| 0.1.35 | Task 0.1.35 | task | `TASK-036` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-036-paper-transaction-ui-sync-soak.md` | 작업 ID: TASK-036 |
| 0.1.36 | Task 0.1.36 | task | `TASK-037` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-037-feature-landscape-research.md` | 작업 ID: TASK-037 |
| 0.1.37 | Task 0.1.37 | task | `TASK-038` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-038-watchlist-screener-alert-expansion.md` | 작업 ID: TASK-038 |
| 0.1.37.1 | Unit 0.1.37.1 | unit | `UNIT-TASK-038-001` | `TASK-038` | completed | `agents/lead_engineer/tasks/units/TASK-038/UNIT-TASK-038-001.md` | UNIT-TASK-038-001 — Watchlist/Screener/Alert dry-run UI (read-only) |
| 0.1.38 | Task 0.1.38 | task | `TASK-039` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md` | 작업 ID: TASK-039 |
| 0.1.38.1 | Unit 0.1.38.1 | unit | `UNIT-TASK-039-001` | `TASK-039` | completed | `agents/lead_engineer/tasks/units/TASK-039/UNIT-TASK-039-001.md` | UNIT-TASK-039-001 — Backtest Research Report Hardening |
| 0.1.39 | Task 0.1.39 | task | `TASK-040` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md` | 작업 ID: TASK-040 |
| 0.1.39.1 | Unit 0.1.39.1 | unit | `UNIT-TASK-040-001` | `TASK-040` | completed | `agents/lead_engineer/tasks/units/TASK-040/UNIT-TASK-040-001.md` | UNIT-TASK-040-001 — 포트폴리오 성과·귀속·tax-lot 읽기전용 리포트 |
| 0.1.40 | Task 0.1.40 | task | `TASK-041` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-041-broker-capability-feature-parity-matrix.md` | 작업 ID: TASK-041 |
| 0.1.40.1 | Unit 0.1.40.1 | unit | `UNIT-TASK-041-001` | `TASK-041` | completed | `agents/lead_engineer/tasks/units/TASK-041/UNIT-TASK-041-001.md` | UNIT-TASK-041-001 — Broker Capability Parity Matrix |
| 0.1.41 | Task 0.1.41 | task | `TASK-042` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-042-asset-universe-decision-record.md` | 작업 ID: TASK-042 |
| 0.1.42 | Task 0.1.42 | task | `TASK-045` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-045-ui-overhaul-phase1-api-foundation-login.md` | 작업 ID: TASK-045 |
| 0.1.42.1 | Unit 0.1.42.1 | unit | `UNIT-TASK-045-001` | `TASK-045` | completed | `agents/lead_engineer/tasks/units/TASK-045/UNIT-TASK-045-001.md` | UNIT-TASK-045-001 — UI 대개편 Phase 1 (FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인) |
| 0.1.43 | Task 0.1.43 | task | `TASK-046` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-046-ui-overhaul-phase2-home-portfolio.md` | 작업 ID: TASK-046 |
| 0.1.43.1 | Unit 0.1.43.1 | unit | `UNIT-TASK-046-001` | `TASK-046` | completed | `agents/lead_engineer/tasks/units/TASK-046/UNIT-TASK-046-001.md` | UNIT-TASK-046-001 — UI 대개편 Phase 2 (홈 + 포트폴리오 읽기 화면) |
| 0.1.44 | Task 0.1.44 | task | `TASK-047` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-047-ui-overhaul-phase3-trade-settings-gates.md` | 작업 ID: TASK-047 |
| 0.1.44.1 | Unit 0.1.44.1 | unit | `UNIT-TASK-047-001` | `TASK-047` | completed | `agents/lead_engineer/tasks/units/TASK-047/UNIT-TASK-047-001.md` | UNIT-TASK-047-001 — UI 대개편 Phase 3 (매매·내역·설정 state-changing + 안전 게이트) |
| 0.1.45 | Task 0.1.45 | task | `TASK-048` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-048-ui-overhaul-phase4-agents-sse.md` | 작업 ID: TASK-048 |
| 0.1.45.1 | Unit 0.1.45.1 | unit | `UNIT-TASK-048-001` | `TASK-048` | completed | `agents/lead_engineer/tasks/units/TASK-048/UNIT-TASK-048-001.md` | UNIT-TASK-048-001 — UI 대개편 Phase 4 (에이전트/IC + 알림 + SSE) |
| 0.1.46 | Task 0.1.46 | task | `TASK-049` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-049-ui-overhaul-phase5-analysis-parity-retire.md` | 작업 ID: TASK-049 |
| 0.1.46.1 | Unit 0.1.46.1 | unit | `UNIT-TASK-049-001` | `TASK-049` | completed | `agents/lead_engineer/tasks/units/TASK-049/UNIT-TASK-049-001.md` | UNIT-TASK-049-001 — UI 대개편 Phase 5 빌드아웃 (분석 화면 + 패리티 감사) |
| 0.1.47 | Task 0.1.47 | task | `TASK-050` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-050-fix-daily-limit-utc-localtime.md` | 작업 ID: TASK-050 |
| 0.1.47.1 | Unit 0.1.47.1 | unit | `UNIT-TASK-050-001` | `TASK-050` | completed | `agents/lead_engineer/tasks/units/TASK-050/UNIT-TASK-050-001.md` | UNIT-TASK-050-001 — 일일 주문한도 UTC/KST 불일치 버그 수정 |
| 0.1.48 | Task 0.1.48 | task | `TASK-051` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-051-fix-compliance-gate-fail-open.md` | 작업 ID: TASK-051 |
| 0.1.48.1 | Unit 0.1.48.1 | unit | `UNIT-TASK-051-001` | `TASK-051` | completed | `agents/lead_engineer/tasks/units/TASK-051/UNIT-TASK-051-001.md` | UNIT-TASK-051-001 — compliance 게이트 fail-open 버그 수정 |
| 0.1.49 | Task 0.1.49 | task | `TASK-052` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-052-fix-trade-ack-checkbox-loop.md` | 작업 ID: TASK-052 |
| 0.1.49.1 | Unit 0.1.49.1 | unit | `UNIT-TASK-052-001` | `TASK-052` | completed | `agents/lead_engineer/tasks/units/TASK-052/UNIT-TASK-052-001.md` | UNIT-TASK-052-001 — trade 뷰 ack 체크박스 영구 루프 수정 |
| 0.1.50 | Task 0.1.50 | task | `TASK-043` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-043-external-app-api-decision-record.md` | 작업 ID: TASK-043 |
| 0.1.51 | Task 0.1.51 | task | `TASK-044` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-044-external-api-owner-setup-manual.md` | 작업 ID: TASK-044 |
| 0.1.52 | Task 0.1.52 | task | `TASK-053` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-053-product-maturity-assessment.md` | 작업 ID: TASK-053 |
| 0.1.52.1 | Unit 0.1.52.1 | unit | `UNIT-TASK-053-001` | `TASK-053` | completed | `agents/lead_engineer/tasks/units/TASK-053/UNIT-TASK-053-001.md` | UNIT-TASK-053-001 — 제품 성숙도 평가 문서 등록 + 반기 재평가 일정 |
| 0.1.53 | Task 0.1.53 | task | `TASK-054` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-054-fix-alerts-settings-no-persist.md` | 작업 ID: TASK-054 |
| 0.1.53.1 | Unit 0.1.53.1 | unit | `UNIT-TASK-054-001` | `TASK-054` | completed | `agents/lead_engineer/tasks/units/TASK-054/UNIT-TASK-054-001.md` | UNIT-TASK-054-001 — 알림 채널/규칙 설정 영속화 |
| 0.1.54 | Task 0.1.54 | task | `TASK-055` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-055-fix-home-proposal-buttons-noop.md` | 작업 ID: TASK-055 |
| 0.1.54.1 | Unit 0.1.54.1 | unit | `UNIT-TASK-055-001` | `TASK-055` | completed | `agents/lead_engineer/tasks/units/TASK-055/UNIT-TASK-055-001.md` | UNIT-TASK-055-001 — 홈 IC 제안 버튼 핸들러 구현 |
| 0.1.55 | Task 0.1.55 | task | `TASK-056` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-056-fix-backend-allocation-gap.md` | 작업 ID: TASK-056 |
| 0.1.55.1 | Unit 0.1.55.1 | unit | `UNIT-TASK-056-001` | `TASK-056` | completed | `agents/lead_engineer/tasks/units/TASK-056/UNIT-TASK-056-001.md` | UNIT-TASK-056-001 — allocation_gap silent fallback 제거 + regression pin |
| 0.1.56 | Task 0.1.56 | task | `TASK-057` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md` | 작업 ID: TASK-057 |
| 0.1.56.1 | Unit 0.1.56.1 | unit | `UNIT-TASK-057-001` | `TASK-057` | completed | `agents/lead_engineer/tasks/units/TASK-057/UNIT-TASK-057-001.md` | UNIT-TASK-057-001 — KPI 일손익률/누적손익률 실계산 |
| 0.1.57 | Task 0.1.57 | task | `TASK-058` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-058-fix-history-live-mode-early-return.md` | 작업 ID: TASK-058 |
| 0.1.57.1 | Unit 0.1.57.1 | unit | `UNIT-TASK-058-001` | `TASK-058` | 완료 | `agents/lead_engineer/tasks/units/TASK-058/UNIT-TASK-058-001.md` | UNIT-TASK-058-001: history.py 라이브 모드 조기 return 제거 |
| 0.1.58 | Task 0.1.58 | task | `TASK-059` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-059-fix-logout-incomplete-state-reset.md` | 작업 ID: TASK-059 |
| 0.1.58.1 | Unit 0.1.58.1 | unit | `UNIT-TASK-059-001` | `TASK-059` | completed | `agents/lead_engineer/tasks/units/TASK-059/UNIT-TASK-059-001.md` | UNIT-TASK-059-001 — logout() 완전 세션 초기화 |
| 0.1.59 | Task 0.1.59 | task | `TASK-060` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-060-sqlite-wal-fk-enforcement.md` | 작업 ID: TASK-060 |
| 0.1.59.1 | Unit 0.1.59.1 | unit | `UNIT-TASK-060-001` | `TASK-060` | completed | `agents/lead_engineer/tasks/units/TASK-060/UNIT-TASK-060-001.md` | UNIT-TASK-060-001 — SQLite WAL 모드 + FK 제약 적용 |
| 0.1.60 | Task 0.1.60 | task | `TASK-061` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md` | 작업 ID: TASK-061 |
| 0.1.60.1 | Unit 0.1.60.1 | unit | `UNIT-TASK-061-001` | `TASK-061` | completed | `agents/lead_engineer/tasks/units/TASK-061/UNIT-TASK-061-001.md` | UNIT-TASK-061-001 — 가격 알림 엔진 평가 루프 구현 |
| 0.1.61 | Task 0.1.61 | task | `TASK-062` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md` | 작업 ID: TASK-062 |
| 0.1.61.1 | Unit 0.1.61.1 | unit | `UNIT-TASK-062-001` | `TASK-062` | completed | `agents/lead_engineer/tasks/units/TASK-062/UNIT-TASK-062-001.md` | UNIT-TASK-062-001 — KRX 휴장일 캘린더 SafetyChecker 연동 |
| 0.1.62 | Task 0.1.62 | task | `TASK-063` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md` | 작업 ID: TASK-063 |
| 0.1.62.1 | Unit 0.1.62.1 | unit | `UNIT-TASK-063-001` | `TASK-063` | completed | `agents/lead_engineer/tasks/units/TASK-063/UNIT-TASK-063-001.md` | UNIT-TASK-063-001 — 서킷브레이커 실현손익 계산 수정 |
| 0.1.63 | Task 0.1.63 | task | `TASK-064` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md` | 작업 ID: TASK-064 |
| 0.1.63.1 | Unit 0.1.63.1 | unit | `UNIT-TASK-064-001` | `TASK-064` | completed | `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md` | UNIT-TASK-064-001 — 주문 조건 TOCTOU 레이스 제거 (atomic CAS claim) |
| 0.1.64 | Task 0.1.64 | task | `TASK-065` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-065-feat-log-rotation.md` | 작업 ID: TASK-065 |
| 0.1.64.1 | Unit 0.1.64.1 | unit | `UNIT-TASK-065-001` | `TASK-065` | completed | `agents/lead_engineer/tasks/units/TASK-065/UNIT-TASK-065-001.md` | UNIT-TASK-065-001 — 로그 로테이션 + 절대 경로 |
| 0.1.65 | Task 0.1.65 | task | `TASK-066` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-066-test-coverage-60pct.md` | 작업 ID: TASK-066 |
| 0.1.66 | Task 0.1.66 | task | `TASK-067` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-067-fix-intraday-no-try-except.md` | 작업 ID: TASK-067 |
| 0.1.66.1 | Unit 0.1.66.1 | unit | `UNIT-TASK-067-001` | `TASK-067` | completed | `agents/lead_engineer/tasks/units/TASK-067/UNIT-TASK-067-001.md` | UNIT-TASK-067-001 — 분석 탭 _intraday_section try/except 추가 |
| 0.1.67 | Task 0.1.67 | task | `TASK-068` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-068-agent-runtime-eval-pilot.md` | 작업 ID: TASK-068 |
| 0.1.67.1 | Unit 0.1.67.1 | unit | `UNIT-TASK-068-001` | `TASK-068` | completed | `agents/lead_engineer/tasks/units/TASK-068/UNIT-TASK-068-001.md` | UNIT-TASK-068-001 — agent_runtime 평가 파일럿 보고서 작성 |
| 0.1.68 | Task 0.1.68 | task | `TASK-069` | `TASKSET-AR-UNCLASSIFIED` | 보류 | `agents/lead_engineer/tasks/TASK-069-product-maturity-reassessment-2026-12.md` | 작업 ID: TASK-069 |
| 0.1.68.1 | Unit 0.1.68.1 | unit | `UNIT-EXAMPLE-001` | `TASK-069` | worker_ready | `agents/lead_engineer/tasks/units/examples/UNIT-EXAMPLE-001.md` | UNIT-EXAMPLE-001 - Worker-Ready Unit Example |
| 0.1.69 | Task 0.1.69 | task | `TASK-070` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-070-sso-sns-premarket-agent-summary.md` | 작업 ID: TASK-070 |
| 0.1.70 | Task 0.1.70 | task | `TASK-071` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-071-stop-hook-owner-governance-host-mode.md` | 작업 ID: TASK-071 |
| 0.1.71 | Task 0.1.71 | task | `TASK-072` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-072-dev-mock-sso-provider.md` | 작업 ID: TASK-072 |
| 0.1.72 | Task 0.1.72 | task | `TASK-073` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-073-defer-future-maturity-reassessment.md` | 작업 ID: TASK-073 |
| 0.1.73 | Task 0.1.73 | task | `TASK-074` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-074-investor-profile-survey.md` | 작업 ID: TASK-074 |
| 0.1.74 | Task 0.1.74 | task | `TASK-087` | `TASKSET-AR-UNCLASSIFIED` | 대기 | `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md` | 작업 ID: TASK-087 |
| 0.1.75 | Task 0.1.75 | task | `TASK-092` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-092-business-plan-agent-lane.md` | 작업 ID: TASK-092 |
| 0.1.76 | Task 0.1.76 | task | `TASK-088` | `TASKSET-AR-UNCLASSIFIED` | 보류 | `agents/lead_engineer/tasks/TASK-088-presale-regulatory-clearance.md` | 작업 ID: TASK-088 |
| 0.1.77 | Task 0.1.77 | task | `TASK-140` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-140-ui-visual-assets-expansion-adoption.md` | 작업 ID: TASK-140 |
| 0.1.78 | Task 0.1.78 | task | `TASK-128` | `TASKSET-AR-UNCLASSIFIED` | 완료 | `agents/lead_engineer/tasks/TASK-128-compliance-business-routing-alignment.md` | 작업 ID: TASK-128 |
| 1 | Initiative 1 | initiative | `INIT-AUTOFOLIO-SAFETY-FIXES` | - | planned | `agents/project/initiatives/INIT-AUTOFOLIO-SAFETY-FIXES.md` | INIT-AUTOFOLIO-SAFETY-FIXES — 안전 버그 수정 이니셔티브 |
| 2 | Initiative 2 | initiative | `TASKSET-AUTOFOLIO-SAFETY-FIXES` | - | planned | `agents/project/initiatives/TASKSET-AUTOFOLIO-SAFETY-FIXES.md` | TASKSET-AUTOFOLIO-SAFETY-FIXES — 안전 버그 3건 |
| 3 | Initiative 3 | initiative | `INIT-PRODUCT-MATURITY` | - | active | `agents/project/initiatives/INIT-PRODUCT-MATURITY.md` | INIT-PRODUCT-MATURITY — 제품 성숙도 버그 수정 및 품질 향상 이니셔티브 |
| 4 | Initiative 4 | initiative | `INIT-R3-ORDER-SURFACE` | - | blocked | `agents/project/initiatives/INIT-R3-ORDER-SURFACE.md` | INIT-R3-ORDER-SURFACE — R3 주문 서피스 이니셔티브 |
| 5 | Initiative 5 | initiative | `INIT-RESEARCH-REPORTING` | - | planned | `agents/project/initiatives/INIT-RESEARCH-REPORTING.md` | INIT-RESEARCH-REPORTING — 리서치 및 보고 이니셔티브 |
| 6 | Initiative 6 | initiative | `INIT-UI-OVERHAUL` | - | planned | `agents/project/initiatives/INIT-UI-OVERHAUL.md` | INIT-UI-OVERHAUL — UI 대개편 이니셔티브 |
| 7 | Initiative 7 | initiative | `TASKSET-PRODUCT-MATURITY` | - | active | `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md` | TASKSET-PRODUCT-MATURITY — 제품 성숙도 버그 수정 15건 |
| 8 | Initiative 8 | initiative | `TASKSET-R3-ORDER-SURFACE` | - | completed | `agents/project/initiatives/TASKSET-R3-ORDER-SURFACE.md` | TASKSET-R3-ORDER-SURFACE — R3 주문 서피스 9건 |
| 9 | Initiative 9 | initiative | `TASKSET-RESEARCH-REPORTING` | - | planned | `agents/project/initiatives/TASKSET-RESEARCH-REPORTING.md` | TASKSET-RESEARCH-REPORTING — 리서치 및 보고 4건 |
| 10 | Initiative 10 | initiative | `TASKSET-UI-OVERHAUL` | - | completed | `agents/project/initiatives/TASKSET-UI-OVERHAUL.md` | TASKSET-UI-OVERHAUL — UI 대개편 5단계 |
| 11 | Initiative 11 | initiative | `INIT-PLATFORM-EVAL` | - | active | `agents/project/initiatives/INIT-PLATFORM-EVAL.md` | INIT-PLATFORM-EVAL — agent_runtime 플랫폼 평가·도그푸딩 이니셔티브 |
| 12 | Initiative 12 | initiative | `TASKSET-PLATFORM-EVAL` | - | active | `agents/project/initiatives/TASKSET-PLATFORM-EVAL.md` | TASKSET-PLATFORM-EVAL — agent_runtime 평가 파일럿 태스크셋 |
| 13 | Initiative 13 | initiative | `INIT-MARKETING-GROWTH` | - | active | `agents/project/initiatives/INIT-MARKETING-GROWTH.md` | INIT-MARKETING-GROWTH — early-user 홍보 이니셔티브 |
| 13.1 | Taskset 13.1 | taskset | `TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION` | `INIT-MARKETING-GROWTH` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 13.1.1 | Task 13.1.1 | task | `TASK-127` | `TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION` | 완료 | `agents/lead_engineer/tasks/TASK-127-business-admin-document-packet-schema.md` | 작업 ID: TASK-127 |
| 13.2 | Taskset 13.2 | taskset | `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` | `INIT-MARKETING-GROWTH` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 13.2.1 | Task 13.2.1 | task | `TASK-132` | `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` | 완료 | `agents/lead_engineer/tasks/TASK-132-promotion-asset-rendering-contract.md` | 작업 ID: TASK-132 |
| 13.2.2 | Task 13.2.2 | task | `TASK-133` | `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` | 완료 | `agents/lead_engineer/tasks/TASK-133-promotion-asset-preview-manifest.md` | 작업 ID: TASK-133 |
| 13.3 | Taskset 13.3 | taskset | `TASKSET-MARKETING-GROWTH` | `INIT-MARKETING-GROWTH` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 13.3.1 | Task 13.3.1 | task | `TASK-093` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-093-business-plan-v1.md` | 작업 ID: TASK-093 |
| 13.3.2 | Task 13.3.2 | task | `TASK-095` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-095-marketing-materials-v1.md` | 작업 ID: TASK-095 |
| 13.3.3 | Task 13.3.3 | task | `TASK-096` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-096-promotion-publishing-pipeline.md` | 작업 ID: TASK-096 |
| 13.3.4 | Task 13.3.4 | task | `TASK-097` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-097-sales-revenue-lane-decision.md` | 작업 ID: TASK-097 |
| 13.3.5 | Task 13.3.5 | task | `TASK-129` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-129-promotion-channel-policy-matrix.md` | 작업 ID: TASK-129 |
| 13.3.6 | Task 13.3.6 | task | `TASK-130` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-130-promotion-publishing-state-machine-contract.md` | 작업 ID: TASK-130 |
| 13.3.7 | Task 13.3.7 | task | `TASK-131` | `TASKSET-MARKETING-GROWTH` | 완료 | `agents/lead_engineer/tasks/TASK-131-promotion-dry-run-audit-preview.md` | 작업 ID: TASK-131 |
| 13.4 | Taskset 13.4 | taskset | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | `INIT-MARKETING-GROWTH` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 13.4.1 | Task 13.4.1 | task | `TASK-166` | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | 완료 | `agents/lead_engineer/tasks/TASK-166-marketing-team-operating-model.md` | Marketing Growth plan을 실행 가능한 team operating model로 바꾼다. |
| 13.4.2 | Task 13.4.2 | task | `TASK-167` | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | 완료 | `agents/lead_engineer/tasks/TASK-167-promotion-campaign-backlog-calendar-v1.md` | 기존 marketing brief를 실행 가능한 campaign backlog와 content calendar로 쪼갠다. |
| 13.4.3 | Task 13.4.3 | task | `TASK-168` | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | 완료 | `agents/lead_engineer/tasks/TASK-168-promotion-asset-generator-readiness-map.md` | PDF/PPTX 등 홍보물 자동 생성으로 가기 전 필요한 source, renderer, review gate를 정리한다. |
| 13.4.4 | Task 13.4.4 | task | `TASK-169` | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | 완료 | `agents/lead_engineer/tasks/TASK-169-sns-publishing-automation-readiness-backlog.md` | SNS 자동 업로드를 나중에 구현할 수 있도록 local readiness backlog를 만든다. |
| 13.4.5 | Task 13.4.5 | task | `TASK-170` | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | 완료 | `agents/lead_engineer/tasks/TASK-170-sales-handoff-readiness-checklist.md` | Marketing Growth와 future Sales/Revenue lane 사이의 handoff 조건을 checklist로 만든다. |
| 14 | Initiative 14 | initiative | `TASKSET-MARKETING-GROWTH` | - | completed | `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md` | TASKSET-MARKETING-GROWTH — early-user 홍보 운영 태스크셋 |
| 15 | Initiative 15 | initiative | `INIT-MEMBERSHIP-ACCESS` | - | active | `agents/project/initiatives/INIT-MEMBERSHIP-ACCESS.md` | INIT-MEMBERSHIP-ACCESS — verified signup and manual deposit approval |
| 15.1 | Taskset 15.1 | taskset | `TASKSET-MEMBERSHIP-ACCESS` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.1.1 | Task 15.1.1 | task | `TASK-098` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-098-membership-access-manual-deposit-plan.md` | 작업 ID: TASK-098 |
| 15.1.2 | Task 15.1.2 | task | `TASK-099` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-099-membership-local-autoregister-fail-closed.md` | 작업 ID: TASK-099 |
| 15.1.3 | Task 15.1.3 | task | `TASK-100` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-100-membership-local-request-approval-prototype.md` | 작업 ID: TASK-100 |
| 15.1.4 | Task 15.1.4 | task | `TASK-101` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-101-membership-admin-settings-tab.md` | 작업 ID: TASK-101 |
| 15.1.5 | Task 15.1.5 | task | `TASK-102` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-102-membership-local-account-grant.md` | 작업 ID: TASK-102 |
| 15.1.6 | Task 15.1.6 | task | `TASK-103` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-103-membership-local-deposit-recognition.md` | 작업 ID: TASK-103 |
| 15.1.7 | Task 15.1.7 | task | `TASK-104` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-104-membership-member-admin-boundary.md` | 작업 ID: TASK-104 |
| 15.1.8 | Task 15.1.8 | task | `TASK-105` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-105-membership-guest-demo-fail-closed.md` | 작업 ID: TASK-105 |
| 15.1.9 | Task 15.1.9 | task | `TASK-106` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-106-membership-app-user-read-boundary.md` | 작업 ID: TASK-106 |
| 15.1.10 | Task 15.1.10 | task | `TASK-108` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-108-membership-production-readiness-gate.md` | 작업 ID: TASK-108 |
| 15.1.11 | Task 15.1.11 | task | `TASK-109` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-109-membership-supabase-rls-contract.md` | 작업 ID: TASK-109 |
| 15.1.12 | Task 15.1.12 | task | `TASK-110` | `TASKSET-MEMBERSHIP-ACCESS` | 완료 | `agents/lead_engineer/tasks/TASK-110-membership-applicant-deposit-status-lookup.md` | 작업 ID: TASK-110 |
| 15.2 | Taskset 15.2 | taskset | `TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.2.1 | Task 15.2.1 | task | `TASK-120` | `TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION` | 완료 | `agents/lead_engineer/tasks/TASK-120-membership-staging-env-inventory-template.md` | 작업 ID: TASK-120 |
| 15.2.2 | Task 15.2.2 | task | `TASK-121` | `TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION` | 완료 | `agents/lead_engineer/tasks/TASK-121-membership-railway-port-healthcheck-readiness.md` | 작업 ID: TASK-121 |
| 15.2.3 | Task 15.2.3 | task | `TASK-122` | `TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION` | 완료 | `agents/lead_engineer/tasks/TASK-122-membership-staging-persistent-storage-decision.md` | 작업 ID: TASK-122 |
| 15.3 | Taskset 15.3 | taskset | `TASKSET-MEMBERSHIP-KIS-TERMS-REVIEW` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.3.1 | Task 15.3.1 | task | `TASK-125` | `TASKSET-MEMBERSHIP-KIS-TERMS-REVIEW` | 완료 | `agents/lead_engineer/tasks/TASK-125-membership-kis-commercial-terms-review-packet.md` | 작업 ID: TASK-125 |
| 15.4 | Taskset 15.4 | taskset | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.4.1 | Task 15.4.1 | task | `TASK-115` | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | 완료 | `agents/lead_engineer/tasks/TASK-115-membership-production-implementation-plan.md` | TASKSET-MEMBERSHIP-PROD-READINESS 완료 이후 남은 production 전환 작업을 Owner 승인 없이 가능한 R2 plann… |
| 15.4.2 | Task 15.4.2 | task | `TASK-116` | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | 완료 | `agents/lead_engineer/tasks/TASK-116-membership-supabase-staging-schema-field-map.md` | 작업 ID: TASK-116 |
| 15.4.3 | Task 15.4.3 | task | `TASK-117` | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | 완료 | `agents/lead_engineer/tasks/TASK-117-membership-payment-recognition-decision-packet.md` | 작업 ID: TASK-117 |
| 15.4.4 | Task 15.4.4 | task | `TASK-118` | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | 완료 | `agents/lead_engineer/tasks/TASK-118-membership-production-secret-store-implementation-plan.md` | 작업 ID: TASK-118 |
| 15.4.5 | Task 15.4.5 | task | `TASK-119` | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | 완료 | `agents/lead_engineer/tasks/TASK-119-membership-staging-deploy-preflight-checklist.md` | 작업 ID: TASK-119 |
| 15.5 | Taskset 15.5 | taskset | `TASKSET-MEMBERSHIP-PROD-READINESS` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.5.1 | Task 15.5.1 | task | `TASK-111` | `TASKSET-MEMBERSHIP-PROD-READINESS` | 완료 | `agents/lead_engineer/tasks/TASK-111-membership-payment-evidence-policy.md` | Local payment evidence policy and gate define minimal retained fields, forbidden evid… |
| 15.5.2 | Task 15.5.2 | task | `TASK-112` | `TASKSET-MEMBERSHIP-PROD-READINESS` | 완료 | `agents/lead_engineer/tasks/TASK-112-membership-production-secret-policy.md` | Local secret-management policy and gate define write-only token handling, rotation/de… |
| 15.5.3 | Task 15.5.3 | task | `TASK-113` | `TASKSET-MEMBERSHIP-PROD-READINESS` | 완료 | `agents/lead_engineer/tasks/TASK-113-membership-per-user-engine-safety-contract.md` | Local per-user engine/safety contract defines tenant-owned runtime state and launch-b… |
| 15.5.4 | Task 15.5.4 | task | `TASK-114` | `TASKSET-MEMBERSHIP-PROD-READINESS` | 완료 | `agents/lead_engineer/tasks/TASK-114-membership-tenant-isolation-matrix.md` | 작업 ID: TASK-114 |
| 15.6 | Taskset 15.6 | taskset | `TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.6.1 | Task 15.6.1 | task | `TASK-126` | `TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC` | 완료 | `agents/lead_engineer/tasks/TASK-126-membership-readiness-surface-sync.md` | 작업 ID: TASK-126 |
| 15.7 | Taskset 15.7 | taskset | `TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.7.1 | Task 15.7.1 | task | `TASK-124` | `TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE` | 완료 | `agents/lead_engineer/tasks/TASK-124-membership-supabase-backup-apply-evidence-checklist.md` | 작업 ID: TASK-124 |
| 15.8 | Taskset 15.8 | taskset | `TASKSET-MEMBERSHIP-SUPABASE-STAGING-REVIEW` | `INIT-MEMBERSHIP-ACCESS` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 15.8.1 | Task 15.8.1 | task | `TASK-123` | `TASKSET-MEMBERSHIP-SUPABASE-STAGING-REVIEW` | 완료 | `agents/lead_engineer/tasks/TASK-123-membership-supabase-staging-migration-rls-review-packet.md` | 작업 ID: TASK-123 |
| 16 | Initiative 16 | initiative | `TASKSET-MEMBERSHIP-ACCESS` | - | active | `agents/project/initiatives/TASKSET-MEMBERSHIP-ACCESS.md` | TASKSET-MEMBERSHIP-ACCESS — verified signup and deposit approval |
| 17 | Initiative 17 | initiative | `TASKSET-MEMBERSHIP-PROD-READINESS` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-READINESS.md` | TASKSET-MEMBERSHIP-PROD-READINESS — local contracts before launch |
| 18 | Initiative 18 | initiative | `TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING.md` | TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING |
| 19 | Initiative 19 | initiative | `TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION.md` | TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION |
| 20 | Initiative 20 | initiative | `TASKSET-MEMBERSHIP-SUPABASE-STAGING-REVIEW` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-SUPABASE-STAGING-REVIEW.md` | TASKSET-MEMBERSHIP-SUPABASE-STAGING-REVIEW |
| 21 | Initiative 21 | initiative | `TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE.md` | TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE |
| 22 | Initiative 22 | initiative | `TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC.md` | TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC |
| 23 | Initiative 23 | initiative | `TASKSET-MEMBERSHIP-KIS-TERMS-REVIEW` | - | completed | `agents/project/initiatives/TASKSET-MEMBERSHIP-KIS-TERMS-REVIEW.md` | TASKSET-MEMBERSHIP-KIS-TERMS-REVIEW |
| 24 | Initiative 24 | initiative | `TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION` | - | completed | `agents/project/initiatives/TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION.md` | TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION |
| 25 | Initiative 25 | initiative | `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` | - | completed | `agents/project/initiatives/TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION.md` | TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION |
| 26 | Initiative 26 | initiative | `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` | - | completed | `agents/project/initiatives/TASKSET-MARKETING-TEAM-OPERATING-SYSTEM.md` | TASKSET-MARKETING-TEAM-OPERATING-SYSTEM |
| 27 | Initiative 27 | initiative | `INIT-FINANCE-ACCOUNTING` | - | completed | `agents/project/initiatives/INIT-FINANCE-ACCOUNTING.md` | INIT-FINANCE-ACCOUNTING |
| 27.1 | Taskset 27.1 | taskset | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | `INIT-FINANCE-ACCOUNTING` | complete | `BACKLOG-BOARD.md` | Unclassified |
| 27.1.1 | Task 27.1.1 | task | `TASK-171` | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | 완료 | `agents/lead_engineer/tasks/TASK-171-finance-accounting-planning-support-lane.md` | Finance/accounting lane을 등록하고, 향후 "계획 5% 대비 예상 10%" 같은 질문을 안전한 scenario planning과 Own… |
| 27.1.2 | Task 27.1.2 | task | `TASK-172` | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | 완료 | `agents/lead_engineer/tasks/TASK-172-finance-scenario-input-contract.md` | 작업 ID: TASK-172 |
| 27.1.3 | Task 27.1.3 | task | `TASK-173` | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | 완료 | `agents/lead_engineer/tasks/TASK-173-portfolio-goal-gap-read-model.md` | 작업 ID: TASK-173 |
| 27.1.4 | Task 27.1.4 | task | `TASK-174` | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | 완료 | `agents/lead_engineer/tasks/TASK-174-finance-roadmap-ui-preview.md` | 작업 ID: TASK-174 |
| 28 | Initiative 28 | initiative | `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT` | - | completed | `agents/project/initiatives/TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT.md` | TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT |

## Risks / Blockers
- Risk: legacy `0.*` work stays readable but should gradually receive `initiative_id` when touched.
- Risk: this generated view prevents human number collisions, but task file creation still needs the planned reservation API for strict concurrent writes.

## Next Steps
- Run `python scripts/work_item_classifier.py --write` after hierarchy metadata changes.
- Run `python scripts/work_item_classifier.py --check` before closeout or owner-facing handoff.
