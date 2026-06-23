---
type: task
id: TASK-128
display_id: TASK-128
task_uid: 35fd3499-fa45-490c-af20-0051b5e45a1c
registered_at: 2026-06-19T22:45:26+09:00
created_at: 2026-06-19T22:45:26+09:00
updated_at: 2026-06-19T22:45:26+09:00
started_at: 2026-06-19T22:45:26+09:00
completed_at: 2026-06-19T22:45:26+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Compliance Officer, Business Planner, Regulatory Admin, Marketing Growth, QA]
priority: High
difficulty: 낮
est_hours: 1
est_tokens: 12000
tags: [business-plan, compliance, agents, routing, marketing, regulatory]
gate: docs/routing/tests only; no legal advice, public posting, official filing, external account action, secret, KIS/order/risk/prod/deploy change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-040
created: 2026-06-19
---

# TASK-128 Compliance business routing alignment

작업 ID: TASK-128
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-19T22:45:26+09:00
기록 시각: 2026-06-19T22:45:26+09:00
요청자: Owner
수행자: Lead Engineer, Compliance Officer, Business Planner, Regulatory Admin, Marketing Growth, QA
검토자: Lead Engineer self-review + Compliance Officer perspective + QA focused role-routing tests + Doc Steward perspective
routing_ref: TASKSET-MARKETING-GROWTH / TASK-128
협업 waiver(사유): single-session scope with role-perspective review and deterministic routing tests; no external worker dispatch was needed for this docs/routing-only slice.
의도: 사업계획/행정/마케팅 lane에서 투자자문, 유료 시그널, 자동매매, KIS 상용/멀티유저, 공개 claim 경계를 Compliance Officer로 안정적으로 라우팅한다.
대상: `agents/compliance_officer/SKILL.md`, `agents/roles.yml`, `scripts/agent_orchestrator.py`, `scripts/agent_worker.py`, `scripts/test_role_mentions.py`
방법: 기존 Compliance Officer role을 새로 만들지 않고, 누락된 alias/routing과 사업/마케팅 claim review contract를 보강한다.
감사 로그: AUDIT-2026-06-19-040
완료 시각: 2026-06-19T22:45:26+09:00
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): unknown

## 범위

포함:

- `@compliance`, `@co`, `/compliance`, `/co`, worker `--role compliance`를 `compliance-officer`로 라우팅.
- Compliance Officer 스킬에 사업계획/행정/마케팅 claim review 범위 추가.
- role registry의 Compliance Officer 입력/출력 계약을 사업 claim까지 확장.
- role mention focused tests 보강.
- 생성 task/report/work-item views 갱신.

제외:

- 법률, 세무, 증권 규제 확정 자문.
- 공공기관 로그인, 인증, 서명, 제출, 결제.
- 공개 게시, paid ads, 고객 연락, SNS/API upload, 외부 계정 변경.
- KIS/order/risk/prod/deploy/secret/product DB 변경.

## 완료 내용

- `scripts/agent_orchestrator.py`에 `Compliance Officer` owner mapping과 compliance aliases를 추가했다.
- `scripts/agent_worker.py`에 동일한 worker role aliases를 추가했다.
- `scripts/test_role_mentions.py`에 business/admin/marketing/compliance mention routing과 `@co` alias 테스트를 추가했다.
- `agents/compliance_officer/SKILL.md`에 사업/마케팅 claim review 입력, 출력, 금지 행동, Owner-only boundary를 추가했다.
- `agents/roles.yml`의 Compliance Officer required inputs와 output contract를 business/admin/marketing claim review까지 확장했다.

## 완료 기록

완료일: 2026-06-19
결과: 사업계획, 행정문서, 마케팅 초안에서 금융규제/투자자문성 claim이 나오면 별도 기억에 의존하지 않고 Compliance Officer worker로 라우팅할 수 있다.
변경 파일: `agents/compliance_officer/SKILL.md`, `agents/roles.yml`, `scripts/agent_orchestrator.py`, `scripts/agent_worker.py`, `scripts/test_role_mentions.py`, task/report/status/generated views.
이슈: 기존 `TASK-095`는 완료 파일이 있었지만 generated board가 stale 상태였으므로, 이번 closeout에서 생성 뷰를 다시 만들었다.
다음 담당자 인수 사항: TASK-096 Promotion Publishing Pipeline은 `@marketing @compliance` 흐름으로 approval queue를 설계해야 하며 live posting은 Owner/R3이다.

## 증거

- `agents/compliance_officer/SKILL.md`
- `agents/roles.yml`
- `scripts/agent_orchestrator.py`
- `scripts/agent_worker.py`
- `scripts/test_role_mentions.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-038.md`

## 검증

- `python -m pytest scripts/test_role_mentions.py -q`
- `python -m py_compile scripts/agent_orchestrator.py scripts/agent_worker.py scripts/role_mentions.py`
- `python -c "import sys; sys.path.insert(0, 'scripts'); import agent_orchestrator as ao, agent_worker as aw; assert ao.normalize_role('compliance') == 'compliance-officer'; assert aw.normalize_role('co') == 'compliance-officer'"`
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/work_item_classifier.py --check`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/validate_task_schema.py`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`

## 리뷰

- Lead Engineer review: 기존 role registry와 worker runtime의 불일치를 작은 routing patch로 맞췄다.
- Compliance Officer perspective: 사업/마케팅 claim review는 legal/tax/securities final advice가 아니라 draft classification으로 제한했다.
- QA perspective: raw mentions remain hints only; `@compliance`와 `@co`가 worker role로 분석되는지 focused test로 고정했다.
- Doc Steward perspective: Business Planner, Regulatory Admin, Marketing Growth, Compliance Officer의 책임 분리가 문서에 남았다.

## Independent Audit

판정: 통과
- Same-session audit note: 변경은 local docs/routing/tests/governance records에 한정됐다.
- No public posting, customer contact, official filing, external login/upload, legal/tax/securities conclusion, secret, KIS/order/risk/prod/deploy, or production-data boundary was crossed.
