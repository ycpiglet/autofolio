---
type: task
id: TASK-093
display_id: TASK-093
task_uid: 12bf4d1f-e16a-4ff8-8f0b-992b808b3494
registered_at: 2026-06-19T00:04:30+09:00
created_at: 2026-06-19T00:04:30+09:00
started_at: 2026-06-19T12:03:45+09:00
updated_at: 2026-06-19T13:08:02+09:00
completed_at: 2026-06-19T13:08:02+09:00
status: 완료
owner: Business Planner
assignees: [Business Planner, Requirements Interviewer, Regulatory Admin, Marketing Growth, Compliance Officer]
priority: High
difficulty: 중-상
est_hours: 4
est_tokens: 60000
tags: [business-plan, vision, strategy, owner-interview, go-to-market, marketing]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: plan/docs only; requires Owner answers before v1 can be marked complete; no external filing/submission/public marketing; marketing assets wait for approved claim bank
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-007
created: 2026-06-19
---

# TASK-093 Business Plan v1

작업 ID: TASK-093
상태: 완료
Owner: Business Planner
요청 시각: 2026-06-19T00:04:30+09:00
기록 시각: 2026-06-19T00:10:57+09:00
요청자: Owner
수행자: Business Planner, Requirements Interviewer, Regulatory Admin, Marketing Growth, Compliance Officer
검토자: Business Planner self-review + Marketing Growth perspective + Regulatory Admin perspective + Compliance Officer perspective
협업 waiver: 단일 Codex 세션의 문서/계획 작업으로 외부 subagent dispatch 없이 역할별 관점 검토와 deterministic docs gates로 대체.
routing_ref: TASKSET-MARKETING-GROWTH / TASK-093
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 docs-only lane; AGENTS.md §16 Autofolio R3 surface avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: Owner의 비전과 방향성을 정리해 Autofolio 사업계획서 v1을 만든다.
대상: `agents/project/BUSINESS-PLAN.md`, `BUSINESS-ADMIN-REGISTER.md`, `MARKETING-BRIEF.md`, Owner interview answers
방법: Requirements Interviewer 질문으로 Owner 결정을 수집하고, Business Planner가 가설/확정/결정/전문가 검토 필요 항목을 분리해 v1을 작성한다.
완료 시각: 2026-06-19T13:08:02+09:00
감사 로그: AUDIT-2026-06-19-007

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`

## 범위

포함:

- Requirements Interviewer 질문 세트로 Owner 결정사항 수집.
- `agents/project/BUSINESS-PLAN.md` v1 작성.
- 고객, 문제, 솔루션, 사업모델, 가격 가설, GTM, 운영 준비, 리스크 경계 정리.
- Business Planner 요약을 다른 에이전트가 읽을 수 있는 Agent Context Summary로 작성.
- Marketing Growth와 Regulatory Admin이 사용할 입력 구간 명확화.
- 초기 홍보 대상은 early external users로 두고, 마케팅/세일즈 분리 기준을 정리.
- TASK-095 Marketing Materials v1과 TASK-096 Promotion Publishing Pipeline이
  사용할 claim bank, 채널, CTA, 공개 승인 경계를 확정.

제외:

- 실제 사업자등록, 세무/법률 제출, 외부 계정 로그인, 결제.
- HWPX generator 구현.
- 제품 코드, KIS/order/risk/prod 경로 변경.
- 공개 홍보물 게시.
- SNS/API 자동 게시 구현.

## 완료 조건

- [x] Owner가 핵심 결정 질문에 답했다.
- [x] `agents/project/BUSINESS-PLAN.md`에 v1 섹션이 갱신됐다.
- [x] 가설, 확정 사실, Owner 결정, professional review 필요 항목이 구분되어 있다.
- [x] `agents/project/MARKETING-BRIEF.md`와 `BUSINESS-ADMIN-REGISTER.md`에 필요한 입력이 연결됐다.
- [x] early-user GTM, safe claim bank, banned claim list, public posting gate가
      `MARKETING-BRIEF.md`에 연결됐다.
- [x] BRIEF와 검증 기록이 남았다.

## 완료 기록

완료일: 2026-06-19
결과: Business Plan v1 방향을 membership-gated subscription web service로 확정하고, 마케팅/행정 후속 작업의 입력을 정리했다.
변경 파일: `BUSINESS-PLAN.md`, `MARKETING-BRIEF.md`, `BUSINESS-ADMIN-REGISTER.md`, `BRIEF-2026-06-19-006.md`, 운영 포인터/보드.
이슈: 추천 기능을 포함하기로 했으므로 public/paid recommendation claim은 Compliance Officer와 professional/regulator review 전까지 막아야 한다.
다음 담당자 인수 사항: TASK-095 Marketing Materials v1은 draft-only 홍보물 작성부터 시작하고, public/SNS posting은 TASK-096 이전에 진행하지 않는다.

## 완료 내용

- Owner 답변을 Business Plan v1 decision table로 반영했다.
- 제품 형태를 구독형 웹 서비스로 정리했다.
- 첫 대상은 지인/선별 사용자로 정리했다.
- 첫 가치 우선순위는 안정장치 > 포트폴리오 > 워크플로 > live-readiness로 정리했다.
- 사용자의 SNS/LLM 계정·토큰으로 에이전트 추천 흐름을 제공하되, Autofolio는 에이전트 성격/하네스/workflow/safety gate를 제공하는 구조로 정리했다.
- CTA는 invitation-only signup / private pilot account request로 해석했다.
- Sales/Revenue lane은 유료 전환, CRM/customer-record 필요, 지인 외 lead flow가 보일 때 재검토하도록 정리했다.

## 결과

TASK-093은 완료됐다. TASK-095 Marketing Materials v1을 다음 draft-only 후보로 진행할 수 있다.

## 증거

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/BUSINESS-ADMIN-REGISTER.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-006.md`
- `agents/project/NEXT-SESSION-POINTER.yml`

## 리뷰

- Business Planner self-review: Owner 답변은 제품형태, 대상, 가격, 가치 우선순위, 추천 포함 여부를 결정 가능한 상태로 제공했다.
- Marketing Growth perspective: TASK-095는 draft-only 홍보물 작성으로 시작 가능하지만, 추천/시그널/성과 claim은 금지 또는 compliance-review 상태로 유지해야 한다.
- Regulatory Admin perspective: 회원가입, 결제, 환불, 개인정보, 사용자 토큰 처리, 사업자등록 정보는 별도 admin 입력으로 남아 있다.
- Compliance Officer perspective: agent recommendation 포함은 가장 큰 watch 항목이며 public/paid claim 전에 professional/regulator review가 필요하다.

## Independent Audit

판정: 통과
Same-session audit note: 외부 independent worker는 dispatch하지 않았다. 대신 High priority 문서 작업에 대해 role-perspective review와 deterministic gates로 보강했다. R3 경계인 실제 회원가입/결제 구현, 외부 계정 로그인, SNS 게시, 고객 연락, KIS/order/risk/prod/secret 변경은 수행하지 않았다.

## 검증

계획 문서 작업이므로 코드 테스트 대신 문서/거버넌스 게이트를 사용했다.

- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/conversation_work_audit.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`
- `git diff --check`

## 진행 로그

### 2026-06-19T12:03:45+09:00 — intake/draft packet started

Owner 요청 "remember에 있는 내용 확인해서 작업 시작해줘"에 따라
`.remember/now.md`, `NEXT-SESSION-POINTER.yml`, `STATUS.md`, BACKLOG, TASK-093,
Business Planner/Regulatory Admin/Compliance 역할 문서를 확인했다.

진행 내용:

- `BUSINESS-PLAN.md`에 TASK-093 Work State와 Business Plan V1 Draft Packet을
  추가했다.
- 확정 사실, working hypotheses, product form options, first offer draft,
  pricing/revenue draft, early-user GTM, Owner Decision List, professional
  review 필요 항목, Agent Context Summary를 분리했다.
- `MARKETING-BRIEF.md`에 TASK-093 입력 상태와 출판 전 금지 경계를 연결했다.
- `BUSINESS-ADMIN-REGISTER.md`에 TASK-094가 기다려야 할 Business Plan V1
  admin input map을 추가했다.

현재 판정:

- 문서/계획 R2 범위는 진행 중이다.
- TASK-093 완료에는 Owner의 핵심 결정 답변이 필요하다.
- 실제 사업자등록, 외부 제출, 로그인, 서명, 결제, 공개 게시, 고객 연락,
  제품 코드, KIS/order/risk/prod/secret 변경은 하지 않았다.

### 2026-06-19T13:08:02+09:00 — Owner answers recorded and v1 closed

Owner 답변:

1. 첫 상품 형태: 구독.
2. 첫 대상: 지인.
3. 가치 우선순위: 안정장치 > 포트폴리오 > 워크플로 > live.
4. 추천/시그널/전략팩: 포함.
5. CTA 질문은 정확히 이해되지 않음.
6. 제품/지원 범위: 웹 서비스로 제작하고 선별 회원가입을 받는다. 계정이
   있는 사람만 이용 가능하다. SNS 및 LLM 연동은 사용자의 토큰/계정을
   사용하고, Autofolio는 에이전트 성격과 하네스를 제공한다.
7. 가격: 일단 무료 또는 약 2만원 수준의 저가.
8. Sales lane trigger 질문은 정확히 이해되지 않음.

Business Planner 해석:

- v1은 membership-gated subscription web service로 둔다.
- 첫 CTA는 `invitation-only signup / private pilot account request`로 해석한다.
- 추천 기능은 포함하되, user-owned LLM/SNS/broker account boundary와 user
  approval을 전제로 한다. 공개 claim, 유료 추천, paid signal, model
  portfolio, personalized advice 문구는 Compliance Officer와 professional /
  regulator review 전까지 공개 마케팅에 쓰지 않는다.
- 별도 Sales/Revenue lane은 지금 만들지 않는다. 유료 전환, 지인 외 lead,
  CRM/customer-record 필요, 결제/환불 운영이 보일 때 TASK-097에서 재검토한다.

변경 파일:

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/BUSINESS-ADMIN-REGISTER.md`
- `agents/lead_engineer/tasks/TASK-093-business-plan-v1.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-006.md`
- `agents/lead_engineer/STATUS.md`
- `agents/lead_engineer/AUDIT-LOG.md`
- `agents/project/NEXT-SESSION-POINTER.yml`

검증:

- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/conversation_work_audit.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`
- `git diff --check`

남은 후속:

- TASK-095 Marketing Materials v1을 다음 작업으로 시작할 수 있다.
- TASK-096 public/SNS publishing pipeline은 TASK-095와 channel policy research
  이후에만 진행한다.
- TASK-097 Sales/Revenue lane은 지금은 보류한다.

## 시작 질문 초안

1. 판매하려는 첫 상품은 개인용 소프트웨어 라이선스, 구독, 설치/지원 서비스, 또는 조합 중 무엇인가?
2. 첫 고객은 누구인가: 본인과 비슷한 개인 투자자, 지인/소규모 베타 사용자, 또는 공개 유료 고객?
3. 추천/시그널/전략팩을 제공할 의향이 있는가, 아니면 사용자가 직접 설정하는 도구로만 유지할 것인가?
4. 첫 유료 버전에서 반드시 약속할 결과와 절대 약속하지 않을 결과는 무엇인가?
5. 법인/개인사업자, 사업장 주소, 결제/환불/지원 범위에 대한 현재 선호는 무엇인가?
6. early external users에게 첫 CTA는 waitlist, private pilot 신청, 데모 요청,
   또는 개발기록 구독 중 무엇인가?
7. SNS/외부 채널은 v1에서 초안/수동 export만 할 것인가, Owner 승인형 게시
   queue까지 설계할 것인가, 또는 제한적 자동 게시를 더 뒤 roadmap으로 둘 것인가?
8. 세일즈 역할은 언제 분리할 것인가: pricing 확정 후, pilot intake 후, CRM이
   필요해진 후, 또는 유료 전환 전 별도 검토 후?
