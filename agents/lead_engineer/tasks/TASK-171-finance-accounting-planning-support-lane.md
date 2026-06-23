---
type: task
id: TASK-171
display_id: TASK-171
task_uid: 0d993fd7-9986-4049-ab17-ef5f5f716b84
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-21T16:30:12+09:00
started_at: 2026-06-21T16:30:12+09:00
completed_at: 2026-06-21T16:30:12+09:00
status: 완료
owner: Finance Accounting
assignees: [Finance Accounting, Business Planner, Regulatory Admin, Compliance Officer, Backend Engineer, UI/UX Designer, QA, Doc Steward, Scribe, Lead Engineer]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 45000
tags: [finance, accounting, portfolio, planning, operations, roadmap]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: local planning-support lane only; no tax/accounting final advice, no trade recommendation/order, no customer payment action, no secrets, no KIS/order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-001
created: 2026-06-21
---

# TASK-171 Finance Accounting Planning Support Lane

작업 ID: TASK-171
상태: 완료
Owner: Finance Accounting
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
요청자: Owner
수행자: Finance Accounting, Business Planner, Regulatory Admin, Compliance Officer, Backend Engineer, UI/UX Designer, QA, Doc Steward, Scribe, Lead Engineer
의도: 회계/재무 파트를 단순 PnL이 아니라 계획 대비 예상, 부족분, 포트폴리오 후보 로드맵, 운영 지원 gap을 다루는 local planning-support lane으로 만든다.
대상: Finance Accounting role, FINANCE-ACCOUNTING-ROADMAP, taskset, gate/tests, role aliases
방법: existing business/membership/payment/portfolio sources를 입력으로 삼아 safe packet contract와 deterministic gate를 만들고, 후속 TASK-172~174를 등록한다.
감사 로그: AUDIT-2026-06-21-001
완료 시각: 2026-06-21T16:30:12+09:00
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
검토자: Finance Accounting self-review + Business Planner perspective + Regulatory Admin perspective + Compliance Officer perspective + Backend/UI feasibility perspective + QA focused gate tests + Doc Steward/Scribe closeout perspective
협업 waiver(사유): 단일 세션 범위의 local planning-support lane/gate 작업이다. 외부 subagent 결과는 explorer로 보조 확인했고, 역할별 관점 검토와 deterministic local gate/tests로 대체했으며 tax/accounting final advice, trade/order, customer payment, secret, KIS/prod/deploy 경계는 건드리지 않았다.
routing_ref: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT / TASK-171
selected_model: Codex coding agent

## 목표

Finance/accounting lane을 등록하고, 향후 "계획 5% 대비 예상 10%" 같은 질문을
안전한 scenario planning과 Owner review candidate로 처리할 수 있게 한다.

## 범위

포함:

- `Finance Accounting` 역할 추가.
- role registry, orchestrator, worker alias 연결.
- plan-vs-expected / gap matrix / timeline candidate / operations support
  roadmap contract 작성.
- finance/accounting roadmap JSON/Markdown 작성.
- gate와 focused tests 작성.
- taskset/initiative 등록.

제외:

- 세무/회계/법률/증권 final advice.
- 매수/매도/수익실현/추가투자/리밸런싱 지시.
- 주문 실행, KIS/order/risk/prod/deploy 변경.
- 실제 고객 결제 요청, 영수증/환불/세무 신고, 은행/PG/Open Banking API.
- 원문 명세, 계좌번호, 고객 결제기록, secret/token 저장.

## 완료 조건

- [x] Finance Accounting role and aliases exist.
- [x] FINANCE-ACCOUNTING-ROADMAP JSON/Markdown exists.
- [x] The roadmap distinguishes observed/planned/expected/missing/blocked.
- [x] The gate rejects advice, order, payment, secret, and production drift.
- [x] Follow-up tasks are registered in a taskset.

## 완료 내용

- `agents/finance_accounting/SKILL.md`를 추가했다.
- `agents/roles.yml`, `scripts/agent_orchestrator.py`,
  `scripts/agent_worker.py`, `scripts/test_role_mentions.py`에
  `finance-accounting` alias를 연결했다.
- `FINANCE-ACCOUNTING-ROADMAP.json`/`.md`로 planned vs expected return,
  gap categories, required metric contract, roadmap outputs, blocked actions를
  고정했다.
- `INIT-FINANCE-ACCOUNTING` 및
  `TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT`를 등록했다.
- `scripts/finance_accounting_roadmap_gate.py`와 focused tests를 추가했다.

## 완료 기록

완료일: 2026-06-21
결과: TASK-171은 finance/accounting planning-support lane foundation으로 완료됐다.
변경 파일: `agents/finance_accounting/SKILL.md`,
`agents/project/FINANCE-ACCOUNTING-ROADMAP.json`,
`agents/project/FINANCE-ACCOUNTING-ROADMAP.md`,
`agents/project/initiatives/INIT-FINANCE-ACCOUNTING.md`,
`agents/project/initiatives/TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT.md`,
`scripts/finance_accounting_roadmap_gate.py`,
`tests/unit/test_finance_accounting_roadmap_gate.py`, role alias files, generated views.
이슈: 기존 worktree에는 이전 세션의 대량 modified/untracked 산출물이 남아 있다. 이번 작업은 새 finance/accounting lane 파일과 role alias/gate/test에 한정했고 기존 산출물을 되돌리지 않았다.
다음 담당자 인수 사항: TASK-172는 real customer/payment data 없이 local scenario fixture를 만든다. TASK-173은 fixture 이후 read-only portfolio goal-gap model을 만든다.

## 증거

- `agents/project/FINANCE-ACCOUNTING-ROADMAP.json`
- `agents/project/FINANCE-ACCOUNTING-ROADMAP.md`
- `agents/finance_accounting/SKILL.md`
- `scripts/finance_accounting_roadmap_gate.py`
- `tests/unit/test_finance_accounting_roadmap_gate.py`

## 검증

- `python -m json.tool agents\project\FINANCE-ACCOUNTING-ROADMAP.json`
- `python -m py_compile scripts\finance_accounting_roadmap_gate.py`
- `python scripts\finance_accounting_roadmap_gate.py --check`
- `python -m pytest tests\unit\test_finance_accounting_roadmap_gate.py scripts\test_role_mentions.py -q`

## 리뷰

- Finance Accounting perspective: the lane now covers planned/expected/gap/timeline support and keeps action output as Owner review candidates.
- Business Planner perspective: business-plan and membership/payment assumptions remain sources, not invented facts.
- Regulatory Admin perspective: payment, receipt, refund, tax, filing, and professional-review boundaries remain blocked.
- Compliance Officer perspective: return/rebalancing language is routed to candidate review and cannot become investment advice or public claim.
- Backend/UI perspective: TASK-172/173/174 preserve a fixture -> read model -> UI preview sequence.
- QA perspective: focused tests cover forbidden status drift, missing metrics, action enablement, and forbidden private/payment/secret keys.
- Doc Steward/Scribe perspective: the lane has a canonical roadmap and taskset, so later cleanup can preserve source links instead of chat-only state.

## Independent Audit

판정: 통과

- Same-session audit note: this was a local docs/JSON/gate/test/role-alias change.
- No tax/accounting/legal/securities final advice, trade recommendation, order
  execution, profit-taking instruction, customer payment action, receipt/refund/
  tax execution, bank/PG/Open Banking call, raw statement persistence, secret or
  token handling, KIS/order/risk/prod, or deploy boundary was crossed.
