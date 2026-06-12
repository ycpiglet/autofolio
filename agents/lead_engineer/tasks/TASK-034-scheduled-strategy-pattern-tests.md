---
type: task
id: TASK-034
status: 완료
owner: Quant Researcher
assignees: [Quant Researcher, Backtest Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 6
est_tokens: 55000
tags: [qa, strategy, scheduler, dca, pairs, volatility, rebalance]
gate: mock/backtest first; live scheduler or order execution requires Owner review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-001
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-13T00:05:22+09:00
---

# TASK-034 Scheduled Strategy Pattern Tests

작업 ID: TASK-034
상태: 완료
Owner: Quant Researcher
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 DCA, pairs, volatility breakout, calendar rebalance, end-of-day liquidation, persistent scheduled event 케이스는 현재 dry-run one-shot 수준만 실행된다.

## 왜 아직 실행 못하는가

- persistent scheduler와 deterministic clock replay가 없다.
- strategy intent와 executable trade condition 생성 경계가 분리되어 있지 않다.

## 완료 기록

완료 시각: 2026-06-13T00:05:22+09:00
검토자: Quant Researcher + QA (Codex self-review)
감사 로그: AUDIT-2026-06-13-001
실측 비용 (시간): 약 0.25h
실측 비용 (LLM 토큰): unknown

- 원 요청: DCA, calendar rebalance, pairs, volatility breakout, EOD liquidation, persistent scheduled event 전략 패턴을 mock/backtest first 범위에서 실행 가능하게 만든다.
- 실제 작업:
  - `tests/integration/test_scheduled_strategy_patterns.py`를 추가했다.
  - test-local deterministic clock과 persistent scheduler harness로 due event replay, once-only 실행, DCA emission을 검증했다.
  - strategy intent를 mock trade condition으로 변환하는 test harness를 추가하고 `target_env="prod"` guard를 고정했다.
  - calendar rebalance, pairs, volatility breakout, EOD liquidation 패턴을 mock condition intent로 검증했다.
  - closure gate 중 발견한 기존 daily-limit scenario fixture의 UTC/KST midnight mismatch를 test-only helper로 안정화했다.
- 결과:
  - scheduled strategy harness 7 passed.
  - generated quant/paper scenario regression 119 passed.
  - live scheduler, production order execution, KIS broker, risk policy, schema/migration은 변경하지 않았다.
- 남은 이슈:
  - 실제 운영 scheduler 지속 실행, live order 연결, order execution 자동화는 Owner review가 필요한 R3 surface다.
  - 이번 TASK는 "mock/backtest first" 완료로 닫고, production scheduler/real order semantics는 별도 R3 follow-up으로 남긴다.

## Done When

- deterministic clock 기반 scheduler test harness가 생긴다.
- strategy intent가 mock trade condition으로 안전하게 변환된다.
- DCA/rebalance/pairs/volatility/EOD liquidation이 mock/backtest에서 먼저 검증된다.

## Verification

- `pytest tests/integration/test_scheduled_strategy_patterns.py -q` -> 7 passed.
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` -> 119 passed.
- `python -m py_compile tests/integration/test_scheduled_strategy_patterns.py` -> OK.
- `git diff --check` -> OK.
