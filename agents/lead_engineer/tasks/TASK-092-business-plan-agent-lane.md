---
type: task
id: TASK-092
display_id: TASK-092
task_uid: 5f3cc8fd-9f0f-4b3b-a2d5-862e98d764f2
registered_at: 2026-06-19T00:04:30+09:00
created_at: 2026-06-19T00:04:30+09:00
started_at: 2026-06-19T00:04:30+09:00
updated_at: 2026-06-19T00:04:30+09:00
completed_at: 2026-06-19T00:04:30+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Research Agent, Business Planner, Regulatory Admin, Marketing Growth, Doc Steward]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [business-plan, agents, regulatory-admin, marketing, hwpx, governance]
gate: docs and agent-routing only; no legal filing, no public submission, no secrets, no product code, no KIS/order/risk/prod changes
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-003
created: 2026-06-19
---

# TASK-092 business plan agent lane

작업 ID: TASK-092
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-19T00:04:30+09:00
기록 시각: 2026-06-19T00:04:30+09:00
요청자: Owner
수행자: Lead Engineer, Research Agent, Business Planner, Regulatory Admin, Marketing Growth, Doc Steward
의도: Autofolio 사업계획서, 사업자등록/행정서류, HWPX 문서화, 마케팅 파생물까지 이어지는 에이전트/스킬 구조를 만든다.
대상: business/admin/marketing role docs, role registry, orchestrator aliases, project business docs, TASK/BRIEF/EVIDENCE records
방법: 공식 출처 조사 후 역할 책임을 분리하고, 프로젝트 정본 문서와 후속 TASK를 등록한다.
감사 로그: AUDIT-2026-06-19-003

## 범위

포함:

- Business Planner, Regulatory Admin, Marketing Growth role 정의.
- `agents/roles.yml`, `scripts/agent_orchestrator.py`, `scripts/agent_worker.py`,
  role mention test 연결.
- `agents/project/BUSINESS-PLAN.md`, `BUSINESS-ADMIN-REGISTER.md`,
  `MARKETING-BRIEF.md` 초기 정본 작성.
- 공식 출처 기반 research evidence note 작성.
- 후속 TASK-093/TASK-094 등록.

제외:

- 실제 사업자등록, 홈택스/정부24 로그인, 서명, 제출, 결제.
- 법률/세무/증권 규제 최종 자문.
- HWPX generator 구현.
- 제품 코드, KIS, 주문, risk gate, production DB, secret, deployment 변경.

## 완료 내용

- Business Planner 역할을 추가해 비전, 사업모델, 고객, GTM, 사업계획서 정본을 관리하게 했다.
- Regulatory Admin 역할을 추가해 공식 출처 기반 행정/법규/서식/HWPX 문서 패킷을 관리하게 했다.
- Marketing Growth 역할을 추가해 승인된 사업계획서를 홍보물/claim bank로 변환하게 했다.
- `agents/project/BUSINESS-PLAN.md`에 현재 확인된 Autofolio 사업 방향, 가설, Owner 결정사항, 운영 준비 항목을 기록했다.
- `agents/project/BUSINESS-ADMIN-REGISTER.md`에 사업자등록, 온라인 제출, HWPX, 금융서비스 규제 watch list를 기록했다.
- `agents/project/MARKETING-BRIEF.md`에 안전한 claim bank와 금지 claim을 초기화했다.
- 공식 출처 evidence를 `EVIDENCE-2026-06-19-003`으로 남겼다.
- 후속 `TASK-093`(Business Plan v1)과 `TASK-094`(HWPX/admin document packet prototype)을 등록했다.

## 변경 파일

- `agents/business_planner/SKILL.md`
- `agents/regulatory_admin/SKILL.md`
- `agents/marketing_growth/SKILL.md`
- `agents/roles.yml`
- `scripts/agent_orchestrator.py`
- `scripts/agent_worker.py`
- `scripts/test_role_mentions.py`
- `agents/project/BUSINESS-PLAN.md`
- `agents/project/BUSINESS-ADMIN-REGISTER.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/research_agent/notes/EVIDENCE-2026-06-19-003-business-plan-admin-agent-research.md`
- `agents/lead_engineer/tasks/TASK-092-business-plan-agent-lane.md`
- `agents/lead_engineer/tasks/TASK-093-business-plan-v1.md`
- `agents/lead_engineer/tasks/TASK-094-admin-document-packet-hwpx-prototype.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-003.md`
- `agents/lead_engineer/AUDIT-LOG.md`
- `agents/lead_engineer/STATUS.md`
- `agents/project/NEXT-SESSION-POINTER.yml`
- generated task views/index/backlog

## 완료 기록

완료 시각: 2026-06-19T00:04:30+09:00
검토자: Lead Engineer perspective + Research Agent evidence + Doc Steward perspective
협업 waiver: 단일 세션의 docs/role routing task. 별도 subagent dispatch 없이 official-source research, role registry checks, generated-view checks, Doc Steward perspective로 대체.
실측 비용 (시간): 약 1.5h
실측 비용 (LLM 토큰): Codex session local meter unavailable
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 official-source evidence와 focused checks로 대체했다.

## 검증

- `python -m pytest scripts/test_role_mentions.py -q`
- `python -m py_compile scripts/agent_orchestrator.py scripts/agent_worker.py scripts/role_mentions.py`
- `python scripts/validate_task_schema.py`
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/check_agent_docs.py`

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-19-003-business-plan-admin-agent-research.md`
- `agents/project/BUSINESS-PLAN.md`
- `agents/project/BUSINESS-ADMIN-REGISTER.md`
- `agents/project/MARKETING-BRIEF.md`

## 남은 이슈 / 한계

- Business Plan v1은 Owner 결정/인터뷰가 필요해 TASK-093으로 분리했다.
- HWPX 실제 생성기는 대상 공식 서식과 데이터 모델이 정해진 뒤 TASK-094에서 구현해야 한다.
- 금융서비스/투자자문 경계는 professional/regulator confirmation 없이 확정하지 않는다.

## 리뷰

- Lead Engineer review: 요청을 chat-only가 아니라 역할, 정본 문서, 후속 TASK로 고정했다.
- Research Agent review: 사업자등록/서류/HWPX/규제 경계는 공식 출처 중심으로 근거를 남겼다.
- Doc Steward review: 새 역할은 기존 Compliance Officer를 과확장하지 않고, Business Planner -> Regulatory Admin -> Marketing Growth 흐름으로 분리됐다.

## Independent Audit

판정: 통과
- Same-session audit note: 변경은 role/docs/routing 표면에 한정됐고 KIS/order/risk/secret/prod DB/외부 제출 경계를 넘지 않았다.
- Evidence: official-source research note, generated task views, role mention routing test, task schema checks.
- Residual risk: Business Plan v1과 HWPX generator는 Owner 입력과 공식 서식 확정 전까지 별도 TASK에서만 진행한다.
