---
type: task
id: TASK-097
display_id: TASK-097
task_uid: f2546606-b983-4bea-adea-94f78b4b18f3
registered_at: 2026-06-19T00:16:06+09:00
created_at: 2026-06-19T00:16:06+09:00
updated_at: 2026-06-19T23:32:08+09:00
started_at: 2026-06-19T23:32:08+09:00
completed_at: 2026-06-19T23:32:08+09:00
status: 완료
owner: Business Planner
assignees: [Business Planner, Marketing Growth, Compliance Officer, Managing Partner, Lead Engineer]
priority: Medium
difficulty: 중
est_hours: 3
actual_hours: 1
est_tokens: 40000
actual_tokens: 16000
tags: [sales, revenue, go-to-market, agents, pricing, crm]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: start after TASK-093 clarifies pricing, pilot flow, support/refund boundary, and whether CRM/customer records are needed; no customer contact or payment flow
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-003
created: 2026-06-19
---

# TASK-097 Sales/Revenue Lane Decision

작업 ID: TASK-097
상태: 완료
Owner: Business Planner
요청 시각: 2026-06-19T00:16:06+09:00
기록 시각: 2026-06-19T23:32:08+09:00
완료 시각: 2026-06-19T23:32:08+09:00
요청자: Owner
수행자: Business Planner, Marketing Growth, Compliance Officer, Managing Partner, Lead Engineer
검토자: Compliance Officer, Managing Partner, Lead Engineer perspective
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 16000
의도: 홍보와 세일즈의 경계를 정하고, Sales/Revenue 전담 에이전트가 필요한 시점을 결정한다.
대상: Sales/Revenue lane decision, role registry proposal, pricing/CRM/support handoff boundaries
방법: Business Plan v1의 가격/paid product/pilot/support 입력을 기준으로 Marketing Growth와 Sales/Revenue 책임을 분리하고, role 생성 여부와 금지 자동화 경계를 결정한다.
감사 로그: AUDIT-2026-06-19-003

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`

## 시작 조건

- TASK-093 Business Plan v1에서 가격, 첫 paid product, pilot intake, 지원/환불
  범위가 정리됨.
- TASK-095에서 early-user acquisition material이 준비됨.
- 유료 전환, 데모 요청, waitlist, CRM, support handoff 중 하나 이상이 실제
  운영 필요로 확인됨.

## 범위

포함:

- Marketing Growth와 Sales/Revenue 책임 분리안 작성.
- Sales/Revenue role 필요 여부 결정.
- 필요 시 role registry, `agents/sales_revenue/SKILL.md`, orchestrator/worker
  alias, output contract 설계.
- lead qualification, demo request, waitlist, CRM/customer record, pricing,
  conversion, retention, support handoff의 owner 결정.
- prohibited sales automation boundary 작성.

제외:

- 실제 고객 연락, 이메일 발송, 결제 요청, CRM 계정 생성.
- 개인정보/고객정보 저장.
- 법률/세무/투자자문 확정 claim.
- paid signal, discretionary management, managed portfolio 영업.
- 제품 코드, KIS/order/risk/prod, secret, production DB 변경.

## 완료 조건

- [x] Marketing Growth와 Sales/Revenue 경계가 문서화됐다.
- [x] Sales/Revenue role을 만들지, 나중으로 미룰지 결정 근거가 남았다.
- [x] role을 만든다면 required inputs, forbidden inputs, output contract,
      audit/compliance gate가 정의됐다.
- [x] prohibited growth/sales automation이 명시됐다.
- [x] BRIEF와 검증 기록이 남았다.

## 완료 내용

- Sales/Revenue role은 지금 생성/활성화하지 않는 것으로 결정했다.
- Marketing Growth가 계속 맡을 산출물과 Sales/Revenue로 넘겨야 할 조건을
  분리했다.
- Customer contact, CRM/customer record, payment/receipt, support/refund,
  public sales claim, paid ad, billing setup은 Owner/R3 입력 전까지 차단했다.
- Decision packet과 local gate/test를 추가해 lane activation이 기록 없이
  일어나지 않도록 했다.

## 완료 기록

완료일: 2026-06-19

결정:

- Sales/Revenue role은 지금 만들거나 활성화하지 않는다.
- Marketing Growth는 positioning, claim bank, campaign brief, landing copy
  source, PDF/PPTX source, SNS draft bundle, FAQ/disclaimer draft까지만 계속
  맡는다.
- Sales/Revenue는 support/refund policy, privacy/customer-record policy,
  payment/receipt policy, CRM/no-CRM decision, Compliance sales-claim review,
  customer-contact workflow Owner approval, paid-offer admin posture가 준비된
  뒤 별도 lane으로 제안한다.

변경 파일:

- `agents/project/SALES-REVENUE-LANE-DECISION.json`
- `agents/project/SALES-REVENUE-LANE-DECISION.md`
- `scripts/sales_revenue_lane_decision_gate.py`
- `tests/unit/test_sales_revenue_lane_decision_gate.py`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/BUSINESS-PLAN.md`
- `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md`

## 증거

- `agents/project/SALES-REVENUE-LANE-DECISION.json`
- `agents/project/SALES-REVENUE-LANE-DECISION.md`
- `scripts/sales_revenue_lane_decision_gate.py`
- `tests/unit/test_sales_revenue_lane_decision_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-042.md`

## 리뷰

판정: 통과

- Gate rejects role activation, lane activation, customer/private/payment key
  names, unblocked support/refund, missing customer-contact trigger, and
  sales-claim automation holes.
- No Sales/Revenue role file, role registry alias, CRM account, payment flow,
  customer contact, paid ad, external account action, secret, or customer data
  was created.

## Independent Audit

same-session self-review:

- Decision packet is record-only and explicitly `not_role_activation`.
- Sales/Revenue remains inactive until Owner and compliance inputs exist.
- Customer contact, CRM/customer-record system activation, payment request,
  support/refund finalization, public sales copy, paid ads, and billing setup
  remain Owner/R3.

## 검증

- `python scripts/check_agent_docs.py`
- `python scripts/generate_views.py --check`
- `python scripts/sales_revenue_lane_decision_gate.py --check`
- `python -m pytest tests/unit/test_sales_revenue_lane_decision_gate.py -q`
- role을 추가했다면 role mention/orchestrator alias 테스트를 함께 갱신한다.
