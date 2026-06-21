---
type: task
id: TASK-172
display_id: TASK-172
task_uid: 9d405c6c-5f71-4057-b89a-df674dfee2a2
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
started_at: 2026-06-21T16:55:03+09:00
updated_at: 2026-06-21T17:06:02+09:00
completed_at: 2026-06-21T17:06:02+09:00
status: 완료
owner: Finance Accounting
assignees: [Finance Accounting, Business Planner, Compliance Officer, QA]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 45000
tags: [finance, accounting, scenario, portfolio, planning]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: local fixture/schema only; no real customer/payment data, no tax/accounting final advice, no trade recommendation/order, no KIS/order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-003
created: 2026-06-21
---

# TASK-172 Finance Scenario Input Contract And Sample Fixture

작업 ID: TASK-172
상태: 완료
Owner: Finance Accounting
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
완료 시각: 2026-06-21T17:06:02+09:00
요청자: Owner
수행자: Finance Accounting, Business Planner, Compliance Officer, QA
검토자: Finance Accounting self-review + Business Planner perspective + Compliance Officer perspective + QA focused gate tests + Doc Steward closeout perspective
의도: 계획 수익률, 예상 수익률 범위, gap, allocation drift, cash/payment readiness,
timeline candidate를 deterministic fixture로 검증할 수 있게 한다.
대상: `FINANCE-ACCOUNTING-ROADMAP`, future `FINANCE-SCENARIO-INPUT-CONTRACT`
방법: real customer/payment data 없이 synthetic fixture와 schema/gate를 만든다.
감사 로그: AUDIT-2026-06-21-003
routing_ref: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT / TASK-172
eval_ref: `scripts/finance_scenario_input_contract_gate.py` + `tests/unit/test_finance_scenario_input_contract_gate.py`
협업 증거: multi_agent_v1 reviewer subagent Boyle reviewed TASK-172 requirements, forbidden fields/phrases, likely gate assertions, and closeout files; main agent incorporated the checklist into the contract/gate/test/closeout.

## 범위

포함:

- plan-vs-expected scenario input schema.
- synthetic sample fixture for 5 percent planned vs 10 percent expected scenario.
- assumptions/confidence/evidence/missing-data fields.
- gate/tests that reject guaranteed-return, advice, order, private payment data,
  and secret drift.

제외:

- current portfolio fact claim.
- actual tax/accounting/securities advice.
- buy/sell/profit-taking/rebalancing instruction.
- real bank/payment/customer data.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Scenario input contract JSON/Markdown exists.
- [x] Example fixture is explicitly synthetic.
- [x] Gate rejects advice/action/private-data drift.
- [x] TASK-173 has a stable input to build a read-only model.

## 완료 내용

- `FINANCE-SCENARIO-INPUT-CONTRACT.json`/`.md`를 추가했다.
- synthetic fixture `synthetic_plan_5_expected_around_10`을 정본 입력으로 고정했다.
- fixture는 planned return 5.0 percent, expected range 8.0 to 10.0 percent,
  gap 3.0 to 5.0 percentage points, missing evidence, candidate-only portfolio
  review, timeline candidate를 포함한다.
- `scripts/finance_scenario_input_contract_gate.py`와 focused tests를 추가해
  current portfolio fact, guaranteed return, tax/accounting/investment advice,
  order/trade instruction, real customer/payment/private data, secret/KIS/prod
  drift를 차단한다.
- `FINANCE-ACCOUNTING-ROADMAP`에 scenario input contract와 TASK-172 완료
  상태를 연결했다.

## 완료 기록

완료일: 2026-06-21
실측 비용 (시간): unknown
실측 비용 (LLM 토큰): unknown
결과: TASK-172는 TASK-173이 소비할 수 있는 local synthetic scenario input contract로 완료됐다.
변경 파일: `agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.json`,
`agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.md`,
`agents/project/FINANCE-ACCOUNTING-ROADMAP.json`,
`agents/project/FINANCE-ACCOUNTING-ROADMAP.md`,
`scripts/finance_scenario_input_contract_gate.py`,
`tests/unit/test_finance_scenario_input_contract_gate.py`, generated task/report views, closeout records.
이슈: 기존 worktree에는 이전 세션의 대량 modified/untracked 산출물이 남아 있다. 이번 작업은 finance/accounting scenario fixture와 closeout surfaces에 한정했고 기존 산출물을 되돌리지 않았다.
다음 담당자 인수 사항: TASK-173은 `FINANCE-SCENARIO-INPUT-CONTRACT.json`을 read-only input으로 사용해 portfolio goal-gap read model을 만들 수 있다. 이때 candidate-only wording과 no order/advice/payment/private-data boundary를 유지한다.

## 증거

- `agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.json`
- `agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.md`
- `scripts/finance_scenario_input_contract_gate.py`
- `tests/unit/test_finance_scenario_input_contract_gate.py`
- `agents/project/FINANCE-ACCOUNTING-ROADMAP.json`
- `agents/project/FINANCE-ACCOUNTING-ROADMAP.md`

## 검증

- `python -m json.tool agents\project\FINANCE-SCENARIO-INPUT-CONTRACT.json`
- `python -m py_compile scripts\finance_scenario_input_contract_gate.py`
- `python scripts\finance_scenario_input_contract_gate.py --check`
- `python -m pytest tests\unit\test_finance_scenario_input_contract_gate.py -q`

## 리뷰

- Self-review: TASK-172 scope is limited to local synthetic fixture/schema work.
- Compliance review: candidate-only wording and blocked actions prevent advice, order, payment, private-data, secret, KIS/order/risk/prod/deploy drift.
- QA review: gate and 17 focused tests pass for required buckets, metrics, fixture flags, forbidden keys/phrases, action-permission flags, and TASK-173 handoff.
- Doc Steward review: STATUS, BRIEF, AUDIT, taskset, roadmap, and NEXT pointer are aligned to TASK-173.
- Named reviewer evidence: Explorer subagent Boyle returned a TASK-172 checklist covering required fields, forbidden fields/phrases, gate assertions, and closeout files.

## Independent Audit

판정: 통과
- Finance Accounting perspective: fixture is synthetic and not a current portfolio fact.
- Compliance Officer perspective: outputs remain candidate/evidence wording and do not provide trade, investment, tax, accounting, legal, securities, payment, or production guidance.
- QA perspective: local gate and 17 focused unit tests cover required buckets, metrics, fixture flags, forbidden keys, forbidden advice/action phrases, action-permission flags, and TASK-173 handoff.
- Doc Steward perspective: roadmap and handoff files identify TASK-173 as the next read-only model step.

## 다음

TASK-173 can start after regenerating views and closeout records.
