---
type: task
id: TASK-091
display_id: TASK-091
task_uid: a5778237-dbd2-47d1-9452-feb3074f8263
registered_at: 2026-06-19T00:07:21+09:00
created_at: 2026-06-19T00:07:21+09:00
started_at: 2026-06-19T00:07:21+09:00
updated_at: 2026-06-19T00:07:21+09:00
completed_at: 2026-06-19T00:07:21+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 낮
est_hours: 0.7
est_tokens: 9000
tags: [profile, onboarding, portfolio, ui, qa]
gate: Owner direct UI correction; frontend validation and read-only portfolio display only; no KIS, order, app/risk, secret, prod DB migration, or CI workflow changes
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-002
created: 2026-06-19
---

# TASK-091 Profile confirmation and portfolio KPI polish

작업 ID: TASK-091
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-19T00:07:21+09:00
기록 시각: 2026-06-19T00:07:21+09:00
완료 시각: 2026-06-19T00:07:21+09:00
요청자: Owner
수행자: UI/UX Designer, QA, Doc Steward
검토자: UI/UX Designer self-review + QA perspective + Doc Steward perspective
협업 waiver: 단일 세션의 Owner direct UI correction. 외부 subagent dispatch 없이 focused API tests, lint, build, Playwright로 대체.
의도: 성향 진단 확인 문구를 따라 쓰기 쉽게 유지하고, 틀린 문구는 저장 전에 명확히 막으며, 포트폴리오 상단/진단 탭의 빠진 강조와 지표를 보정한다.
대상: `web/src/app/onboarding/investor-profile/page.tsx`, `web/src/components/domain/PortfolioDashboard.tsx`, `web/e2e/investor-profile.spec.ts`, `web/e2e/demo-walkthrough.spec.ts`
방법: 확인 문구 입력을 persistent guide overlay로 바꾸고, signature validation message를 세분화하며, portfolio KPI/keyword 강조 E2E를 추가했다.
감사 로그: AUDIT-2026-06-19-002
routing_ref: direct-owner-request / TASK-091
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; no order/risk/secret/prod DB migration
실측 비용 (시간): 약 0.7h
실측 비용 (LLM 토큰): unknown

## 원 요청

확인 문구가 입력 중 사라지면 안 되고 배경 글자로 남아 있어야 한다. 틀리게 등록하면 틀렸다는 경고를 띄우고 저장이 안 되어야 한다. 진단 서브탭의 `보유 목적`, `손실 허용 범위` 같은 키워드도 강조되어야 한다. 포트폴리오 상단 평가손익에는 퍼센트가 빠져 있고 현금 탭은 의미가 약하다.

## 완료 내용

- 확인 문구 입력칸을 placeholder 방식에서 회색 guide overlay 방식으로 변경했다.
- 확인 문구가 틀리면 입력칸 아래와 저장 alert 양쪽에 정확한 오류를 표시하고 POST를 막는다.
- 서명 누락 원인을 성명/확인문구/직접서명 단위로 세분화했다.
- 포트폴리오 상단 `평가손익` KPI에 누적손익률 퍼센트 delta를 추가했다.
- 독립 `현금` KPI 카드를 제거하고, 현금/현금비중은 `총자산`/`보유종목` 상세와 배분 분석에 보조 정보로 유지했다.
- 진단 문장 강조 키워드에 `보유 목적`, `손실 허용 범위`, `단일 종목 집중`, `집중도`, `데이터 품질` 등을 추가했다.

## 검증

- `npm run lint` -> pass.
- `npm run test:e2e -- e2e/investor-profile.spec.ts --reporter=line` -> 3 passed.
- `npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` -> 1 passed.
- `npm run build` -> pass.
- `.venv\Scripts\python.exe -m pytest tests/api/test_profile_survey.py -q` -> 12 passed, 4 warnings.
- `.venv\Scripts\python.exe -m pytest tests/api/test_portfolio.py tests/unit/test_portfolio_groups.py -q` -> 22 passed, 1 warning.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-19-002-profile-confirmation-portfolio-kpi-polish.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-002.md`

## 리뷰

- UI/UX Designer: 확인 문구가 계속 보이는 방식이라 따라 쓰기 실패율을 줄인다. 현금은 상단 클릭 KPI에서 제거하고 보조 지표로 유지해 화면 우선순위를 낮췄다.
- QA: wrong confirmation E2E가 POST 차단을 직접 검증하고, portfolio walkthrough가 평가손익 퍼센트와 진단 키워드 bold를 검증한다.
- Doc Steward: TASK/EVIDENCE/BRIEF/AUDIT/STATUS/포인터 기록을 갱신한다.

## Independent Audit

판정: 통과

근거:

- 변경은 onboarding UI와 portfolio read-only display에 제한됐다.
- KIS, order flow, risk gate, secret, production DB migration, CI workflow를 변경하지 않았다.
- 클라이언트 E2E가 잘못된 확인 문구 저장 차단과 포트폴리오 KPI/진단 강조를 확인한다.
- focused API, lint, build, Playwright checks가 통과했다.

## 리스크/메모

- 확인 문구 overlay는 사용성 보강이며, 법적 공인 전자서명/본인인증을 대체하지 않는다.
- 현금 정보는 삭제하지 않고 총자산 상세와 배분/노출 분석에 유지했다.
