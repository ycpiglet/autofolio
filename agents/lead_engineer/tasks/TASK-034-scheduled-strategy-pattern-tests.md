---
type: task
id: TASK-034
status: 대기
owner: Quant Researcher
assignees: [Quant Researcher, Backtest Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 6
est_tokens: 55000
tags: [qa, strategy, scheduler, dca, pairs, volatility, rebalance]
gate: mock/backtest first; live scheduler or order execution requires Owner review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-034 Scheduled Strategy Pattern Tests

작업 ID: TASK-034
상태: 대기
Owner: Quant Researcher
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 DCA, pairs, volatility breakout, calendar rebalance, end-of-day liquidation, persistent scheduled event 케이스는 현재 dry-run one-shot 수준만 실행된다.

## 왜 아직 실행 못하는가

- persistent scheduler와 deterministic clock replay가 없다.
- strategy intent와 executable trade condition 생성 경계가 분리되어 있지 않다.

## Done When

- deterministic clock 기반 scheduler test harness가 생긴다.
- strategy intent가 mock trade condition으로 안전하게 변환된다.
- DCA/rebalance/pairs/volatility/EOD liquidation이 mock/backtest에서 먼저 검증된다.

## Verification

- scheduler unit tests
- strategy-to-condition integration tests
- no-prod guard tests
