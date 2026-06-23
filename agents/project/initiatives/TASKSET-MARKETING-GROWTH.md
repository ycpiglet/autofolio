---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-GROWTH
work_uid: 375c29c3-9b5d-48ec-9f30-da667426a37a
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Marketing Growth
created_at: 2026-06-19T12:01:06+09:00
updated_at: 2026-06-19T23:32:08+09:00
completed_at: 2026-06-19T23:32:08+09:00
resolution: done
verification_status: passed
origin_type: owner_request
origin_ref: AUDIT-2026-06-19-005
created_by: lead_engineer
title: Marketing Growth Taskset — Business Plan to promotional assets
summary: TASK-093 Business Plan v1, TASK-095 draft marketing materials, TASK-129 promotion channel matrix plus publishing policy packet, TASK-130 local publishing state-machine contract, TASK-131 dry-run audit preview, TASK-096 local publishing design/preview scope, and TASK-097 Sales/Revenue lane decision are complete; live posting, customer contact, CRM, payment, and sales activation remain Owner/R3.
tags: [marketing, go-to-market, early-users, sns, pdf, pptx, sales]
priority: P2
---

# TASKSET-MARKETING-GROWTH — early-user 홍보 운영 태스크셋

## 부모 이니셔티브

`INIT-MARKETING-GROWTH`

## 포함 태스크

tasks:
  - TASK-093
  - TASK-095
  - TASK-129
  - TASK-130
  - TASK-131
  - TASK-096
  - TASK-097

| work_id | 설명 | Owner | 상태 | Gate |
|---------|------|-------|------|------|
| TASK-093 | Business Plan v1 — target user, pricing, GTM, claim boundary 확정 | Business Planner | 완료 | membership-gated subscription web service, selected users, free/low-price pilot |
| TASK-095 | Marketing Materials v1 — landing copy, PDF one-pager source, PPTX deck source, SNS draft bundle | Marketing Growth | 완료 | draft source complete; no publication/export/posting without review |
| TASK-129 | Promotion Channel Policy Matrix and Publishing Policy Packet — channel policy, rollback/delete research, and dry-run handoff | Marketing Growth | 완료 | research-only; no live post, no OAuth, no external account action |
| TASK-130 | Promotion Publishing State Machine — draft/review/approval/dry-run/record-only state contract | Marketing Growth | 완료 | local contract only; every transition `live_action: false` |
| TASK-131 | Promotion Dry-run Audit Preview — local preview record/gate/test without network or token handling | Backend Engineer | 완료 | local dry-run only; no live post, no OAuth, no external API |
| TASK-096 | Promotion Publishing Pipeline — draft-first, approval queue, audit log, rollback 설계 | Marketing Growth | 완료 | local design complete; Owner/R3 approval still required before live post |
| TASK-097 | Sales/Revenue Lane Decision — 세일즈 역할 분리 기준과 금지 자동화 경계 결정 | Business Planner | 완료 | Sales/Revenue role deferred; no CRM, payment, customer contact, or sales activation |

## 의존 관계

```text
TASK-093
  -> TASK-095
       -> TASK-129
            -> TASK-130
                 -> TASK-131
                      -> TASK-096
       -> TASK-097
```

- TASK-093은 taskset 전체의 결정 gate다.
- TASK-095는 claim-safe 홍보물 source를 만든다.
- TASK-129는 channel-specific official API/policy research와 stricter
  publishing policy/dry-run handoff를 live action 없이 완료한다.
- TASK-130은 approval queue state machine을 local-only contract로 고정한다.
- TASK-131은 no-network dry-run audit preview를 만든다.
- TASK-096은 live posting 구현이 아니라 draft-first/approval-queue publishing
  workflow의 local design/preview scope를 완료한다.
- TASK-097은 Marketing Growth와 Sales/Revenue의 책임 경계를 결정하고, 지금은
  Sales/Revenue role을 활성화하지 않는 것으로 닫는다.

## Wave 실행 계획

Wave 1:

- TASK-093 Business Plan v1
- 산출물: target user, value proposition, pricing hypothesis, claim boundary,
  early-user CTA, marketing/sales split criteria

Wave 2:

- TASK-095 Marketing Materials v1
- 산출물: campaign brief, landing copy, PDF source, PPTX source, SNS drafts,
  FAQ/disclaimer draft, claim review map
- 결과: `MARKETING-MATERIALS-V1.json`/`.md` and
  `scripts/marketing_materials_gate.py` completed as draft-only source and
  validation gate.

Wave 2.5:

- TASK-129 Promotion Channel Policy Matrix and Publishing Policy Packet
- 산출물: X, LinkedIn, Instagram, Naver Blog, Owner-controlled blog/dev log
  policy matrix plus Telegram, KakaoTalk, Naver Share/Cafe, Google Business
  Profile policy/dry-run handoff, official-source evidence note, local
  non-publishing gates.
- 결과: `PROMOTION-CHANNEL-POLICY-MATRIX.json`/`.md`,
  `PROMOTION-PUBLISHING-POLICY-PACKET.json`/`.md`,
  `scripts/promotion_channel_policy_gate.py`, and
  `scripts/promotion_publishing_policy_gate.py` completed as research-only
  sources.

Wave 2.75:

- TASK-130 Promotion Publishing State Machine
- 산출물: draft/review/compliance/Owner/manual-export/dry-run/record-only/
  blocked/archive state model, queue record contract, forbidden transitions.
- 결과: `PROMOTION-PUBLISHING-STATE-MACHINE.json`/`.md` and
  `scripts/promotion_publishing_state_machine_gate.py` completed as local-only
  contract.

Wave 3:

- TASK-131 Promotion Dry-run Audit Preview
- TASK-096 Promotion Publishing Pipeline
- TASK-097 Sales/Revenue Lane Decision
- 산출물: dry-run/audit preview, local queue records, channel guard integration,
  sales role creation/defer decision
- 결과: TASK-131 and TASK-096 completed the local no-network dry-run preview
  and promotion publishing design scope. TASK-097 completed the Sales/Revenue
  boundary decision and deferred role activation until Owner/R3 sales inputs
  exist.

## 안전 경계

금지:

- 실제 SNS 게시, paid ads, 고객 연락, 외부 계정 로그인, API secret 저장.
- viewbots, fake traffic/engagement, spam, unauthorized bulk posting, ToS
  evasion, platform manipulation, unsourced lead scraping.
- 수익률 보장, 투자자문, 세무/법률 확정 claim, managed portfolio 또는 paid signal
  판매 claim.
- KIS/order/risk/prod, broker secret, production DB 변경.

Owner 승인 필요:

- public post, paid campaign, customer email/DM, external API upload, channel
  account setting change, live OAuth callback validation.

## 완료 기준

- TASK-093, TASK-095, TASK-129, TASK-130, TASK-131, TASK-096, TASK-097이 완료됨.
- `MARKETING-BRIEF.md`가 taskset 산출물을 링크한다.
- `reviews/INDEX.md`, generated task views, work item classification이 최신이다.
- `python scripts/check_agent_docs.py` 0 error.
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs` pass.
