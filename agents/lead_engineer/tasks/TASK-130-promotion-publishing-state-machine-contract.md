---
type: task
id: TASK-130
display_id: TASK-130
task_uid: ff8466c8-1909-45a6-9b07-2d29f96e2c60
registered_at: 2026-06-19T23:07:14+09:00
created_at: 2026-06-19T23:07:14+09:00
updated_at: 2026-06-19T23:08:29+09:00
started_at: 2026-06-19T23:07:14+09:00
completed_at: 2026-06-19T23:07:14+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Compliance Officer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 2
actual_hours: 1
est_tokens: 25000
actual_tokens: 16000
tags: [marketing, sns, publishing, state-machine, audit-log]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: local contract only; no live post, no OAuth, no external API, no token handling, no customer contact, no paid ads
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-042
created: 2026-06-19
---

# TASK-130 Promotion Publishing State Machine Contract

작업 ID: TASK-130
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T23:07:14+09:00
기록 시각: 2026-06-19T23:07:14+09:00
요청자: Owner goal continuation
수행자: Marketing Growth, Compliance Officer, QA, Doc Steward
검토자: Compliance Officer, QA, Doc Steward perspective
routing_ref: `@marketing` -> `@compliance` -> `@qa`
협업 waiver(사유): same-session Codex execution; deterministic local contract gate and focused tests recorded.
의도: TASK-096 Promotion Publishing Pipeline의 draft-first approval queue 상태 전이를 local contract로 고정한다.
대상: promotion publishing state machine, queue record contract, forbidden transitions, local verification gate
방법: local JSON/Markdown state-machine contract, local gate, focused unit tests.
감사 로그: AUDIT-2026-06-19-042
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): ~16000

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`
- Parent task: `TASK-096`

## 범위

포함:

- draft -> copy review -> compliance review -> owner review -> manual export/dry-run -> blocked/archive/live-recorded state model.
- `live_recorded_after_owner_action`을 record-only terminal state로 고정.
- queue record required fields and append-only event names.
- forbidden transitions for auto-publish, OAuth, token storage, customer contact, paid ads, browser automation, lead scraping, fake engagement, investment/performance/KIS clearance publication.
- local validation gate and focused unit tests.

제외:

- live public post, scheduled live post, platform API upload.
- OAuth authorization, external account login, token/secret handling.
- customer email/DM, paid ads, lead scraping, browser automation.
- generated public assets, external URL creation, customer record creation.
- KIS/order/risk/prod/deploy/secret changes.

## 완료 내용

- Promotion publishing local state-machine contract를 작성했다.
- 모든 transition을 `live_action=false`로 고정했다.
- `live_recorded_after_owner_action`을 record-only terminal state로 고정했다.
- Local gate/test로 live transition, non-record-only live state, secret-like key,
  Owner boundary 누락, publish action-like text를 차단했다.

## 완료 기록

완료일: 2026-06-19
완료 시각: 2026-06-19T23:07:14+09:00

결과:

- `PROMOTION-PUBLISHING-STATE-MACHINE.json` and `.md` created.
- `promotion_publishing_state_machine_gate.py` validates all states/transitions remain local and non-live.
- TASK-096 now has official-source policy research and state-machine contract complete; dry-run audit preview remains the next safe local slice.

변경 파일:

- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.md`
- `scripts/promotion_publishing_state_machine_gate.py`
- `tests/unit/test_promotion_publishing_state_machine_gate.py`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md`
- `agents/lead_engineer/tasks/TASK-096-promotion-publishing-pipeline.md`

## 증거

- `PROMOTION-CHANNEL-POLICY-MATRIX.json` provides channel policy input.
- `PROMOTION-PUBLISHING-POLICY-PACKET.json` provides stricter dry-run/live-boundary input.
- `MARKETING-MATERIALS-V1.json` provides draft source material.
- The local gate rejects live transitions, non-record-only live state, secret-like keys, missing Owner boundary, and action-like publish text.

## 검증

- `python -m json.tool agents\project\PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `python scripts\promotion_publishing_state_machine_gate.py --check`
- `python -m pytest tests\unit\test_promotion_publishing_state_machine_gate.py -q`

## 리뷰

판정: 통과

- The contract has no live executor.
- Every transition has `live_action: false`.
- Owner approval and Compliance Officer review are required before public-use records.
- Live state is record-only after external Owner action, not a publication trigger.

## Independent Audit

same-session self-review:

- No external API call, OAuth flow, token handling, customer contact, ad purchase, or browser automation was introduced.
- The local gate covers the high-risk failure modes that would turn a queue contract into a live publisher.
- Remaining dry-run record generation can be implemented as a separate no-network slice.

## Remaining

- TASK-096 still needs local dry-run audit preview generation.
- Actual live posting and external account work remain Owner/R3.
