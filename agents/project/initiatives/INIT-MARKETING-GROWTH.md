---
schema_version: agent-runtime-work-item/v1
work_id: INIT-MARKETING-GROWTH
work_uid: f4764999-ee66-408e-915b-99611a175ec5
kind: initiative
status: active
owner: Business Planner
created_at: 2026-06-19T12:01:06+09:00
updated_at: 2026-06-19T12:03:45+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-19-005
created_by: lead_engineer
title: Marketing Growth — Early-user promotion and publishing governance
summary: Business Plan v1에서 early-user GTM과 claim boundary를 확정한 뒤 홍보물, 게시 파이프라인, Sales/Revenue 분리 결정을 순차 진행한다.
tags: [marketing, go-to-market, early-users, sns, sales, campaign]
priority: P2
---

# INIT-MARKETING-GROWTH — early-user 홍보 이니셔티브

## 목적

Autofolio를 early external users에게 설명하고 검증할 수 있는 홍보 체계를 만든다.
사업계획/claim boundary가 확정되기 전에는 공개 게시와 판매 활동을 하지 않고,
Marketing Growth가 안전한 positioning, campaign source, 홍보물 초안, 게시 승인
흐름을 준비한다.

## 포함 작업

| ID | 설명 | Owner | 순서 |
|----|------|-------|------|
| TASK-093 | Business Plan v1 — target user, pricing, GTM, claim boundary 확정 | Business Planner | 1 |
| TASK-095 | Marketing Materials v1 — landing copy, PDF/PPTX source, SNS drafts | Marketing Growth | 2 |
| TASK-096 | Promotion Publishing Pipeline — draft-first / approval-queue 게시 설계 | Marketing Growth | 3 |
| TASK-097 | Sales/Revenue Lane Decision — 마케팅과 세일즈 분리 기준 결정 | Business Planner | 3 |

## 실행 특성

- TASK-093이 선행 gate다. TASK-095는 TASK-093 완료와 approved claim bank 없이는 시작하지 않는다.
- TASK-096은 TASK-095 완료와 채널별 공식 API/policy research 없이는 시작하지 않는다.
- TASK-097은 pricing, pilot flow, CRM/customer-record 필요, support/refund scope가
  보일 때 시작한다.
- TASK-096과 TASK-097은 TASK-095 이후 병렬 검토 가능하지만, live posting이나
  customer contact는 Owner 승인 전까지 금지한다.

## 완료 기준

- `agents/project/MARKETING-BRIEF.md`가 Business Plan v1과 연결된 marketing SSoT가 된다.
- early-user 홍보물 source가 reviewable text artifact로 존재한다.
- SNS/외부 게시 자동화는 dry-run, approval, audit log, rollback gate를 갖춘다.
- Sales/Revenue 전담 role 생성 여부와 조건이 결정된다.
- `python scripts/check_agent_docs.py` 0 error.
