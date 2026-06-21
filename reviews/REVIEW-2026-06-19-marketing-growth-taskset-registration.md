---
type: review
id: REVIEW-2026-06-19-marketing-growth-taskset-registration
status: pass
signal: pass
score: 92
priority: High
tags: [planning-record, taskset, marketing, go-to-market, sales, sns]
created_at: 2026-06-19T12:01:06+09:00
taskset: TASKSET-MARKETING-GROWTH
related_tasks: [TASK-093, TASK-095, TASK-096, TASK-097]
---

# Marketing Growth Taskset Registration Review

## Bottom Line

Owner가 요청한 "plan 기반 taskset"을 `TASKSET-MARKETING-GROWTH`로 등록한다.
이 taskset은 Business Plan v1을 선행 gate로 두고, 홍보물 v1, 게시 파이프라인,
Sales/Revenue 분리 결정을 하나의 marketing-growth work lane으로 묶는다.

## Decision

1. `TASK-093`, `TASK-095`, `TASK-096`, `TASK-097`을
   `INIT-MARKETING-GROWTH` / `TASKSET-MARKETING-GROWTH` 아래로 묶는다.
2. `TASK-094` Admin/HWPX packet은 같은 business lane과 관련은 있지만 이번
   marketing-growth taskset에는 포함하지 않는다.
3. SNS 자동 게시와 sales automation은 즉시 구현하지 않고, approval queue,
   official API/policy research, audit log, rollback gate가 생긴 뒤 별도 실행한다.

## Scope

Included:

- initiative/taskset work-item files under `agents/project/initiatives/`;
- task frontmatter hierarchy metadata for the included tasks;
- review/evidence index refresh;
- work item classification refresh.

Excluded:

- 실제 PDF/PPTX 생성기;
- 실제 SNS 게시, paid ads, customer contact, external login;
- KIS/order/risk/prod/secret/production DB changes;
- Sales/Revenue role creation before TASK-097.

## Sequence

```text
TASK-093 Business Plan v1
  -> TASK-095 Marketing Materials v1
       -> TASK-096 Promotion Publishing Pipeline
       -> TASK-097 Sales/Revenue Lane Decision
```

## Safety Boundary

Do not build or approve viewbots, fake traffic/engagement, spam, unauthorized
bulk posting, ToS evasion, platform manipulation, unsourced lead scraping,
investment-performance guarantees, or public investment-advice claims.

## Verification Plan

- `python scripts/evidence_index_generator.py --write`
- `python scripts/evidence_index_generator.py --check`
- `python scripts/generate_views.py`
- `python scripts/generate_views.py --check`
- `python scripts/work_item_classifier.py --write`
- `python scripts/work_item_classifier.py --check`
- `python scripts/check_agent_docs.py`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
