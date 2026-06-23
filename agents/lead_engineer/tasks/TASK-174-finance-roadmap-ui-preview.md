---
type: task
id: TASK-174
display_id: TASK-174
task_uid: fdbdc675-6b4b-43a0-97f3-d331439e0b82
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-21T16:30:12+09:00
status: 대기
owner: UI/UX Designer
assignees: [UI/UX Designer, Finance Accounting, Compliance Officer, QA, Beta Tester]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 70000
tags: [finance, accounting, portfolio, ui, roadmap]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: local UI preview only; no recommendation wording, no customer/payment action, no order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-001
created: 2026-06-21
---

# TASK-174 Finance Roadmap UI Preview

작업 ID: TASK-174
상태: 대기
Owner: UI/UX Designer
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
요청자: Owner
수행자: UI/UX Designer, Finance Accounting, Compliance Officer, QA, Beta Tester
의도: Finance/accounting planning support를 사용자가 읽을 수 있는 preview로 보여주되,
추천/주문/세무회계 자문 문구를 넣지 않는다.
대상: finance roadmap read model, portfolio UI, roadmap panel
방법: TASK-173 read model을 기반으로 local UI preview와 E2E/wording checks를 만든다.
감사 로그: AUDIT-2026-06-21-001

## 범위

포함:

- plan-vs-expected summary.
- gap matrix.
- timeline candidate list.
- operations support gaps.
- blocked action and review-required labels.

제외:

- buy/sell/rebalance/profit-taking CTA.
- customer payment request.
- public performance claim.
- final tax/accounting/securities advice.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [ ] UI preview displays scenario and gaps without recommendation wording.
- [ ] Mobile/desktop text does not overlap.
- [ ] Compliance wording check passes.
- [ ] Focused E2E verifies the panel loads with fixture data.

## 다음

Start after TASK-173 is complete.
