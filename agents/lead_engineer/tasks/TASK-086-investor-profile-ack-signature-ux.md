---
type: task
id: TASK-086
display_id: TASK-086
task_uid: 78084797-a087-4f30-aa32-ebc21256c77a
registered_at: 2026-06-18T23:40:43+09:00
created_at: 2026-06-18T23:40:43+09:00
started_at: 2026-06-18T23:40:43+09:00
updated_at: 2026-06-18T23:40:43+09:00
completed_at: 2026-06-18T23:40:43+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 10000
tags: [profile, onboarding, ui, safety, qa]
gate: Owner direct UI request; profile survey and acknowledgement UX only; no KIS, order, app/risk, secret, prod DB migration, or CI workflow changes
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-012
created: 2026-06-18
---

# TASK-086 Investor profile acknowledgement and signature UX

작업 ID: TASK-086
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-18T23:40:43+09:00
기록 시각: 2026-06-18T23:40:43+09:00
완료 시각: 2026-06-18T23:40:43+09:00
요청자: Owner
수행자: UI/UX Designer, Backend Engineer, QA, Doc Steward
검토자: UI/UX Designer self-review + Backend Engineer perspective + QA perspective + Doc Steward perspective
협업 waiver: 단일 세션의 Owner direct profile UI refinement. 외부 subagent dispatch 없이 focused tests, lint, build, Playwright로 대체.
의도: 성향 진단에서 미응답 저장 시 사용자가 놓친 질문을 강하게 인식하고, 책임 고지를 더 명확히 확인하도록 직접 서명과 정확한 확인 문구 입력을 추가한다.
대상: `web/src/app/onboarding/investor-profile/page.tsx`, `web/src/app/globals.css`, `app/services/investor_profile.py`, `tests/api/test_profile_survey.py`, `web/e2e/investor-profile.spec.ts`
방법: missing-answer 시각 피드백을 강화하고, signature question payload를 이름/확인문구/서명 이미지/timestamp 객체로 변경해 프론트와 서버 양쪽에서 검증한다.
감사 로그: AUDIT-2026-06-18-012
routing_ref: direct-owner-request / TASK-086
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; no order/risk/secret/prod DB migration
실측 비용 (시간): 약 0.8h
실측 비용 (LLM 토큰): unknown

## 원 요청

성향 진단에서 체크하지 않고 저장하면 질문 블록이 흔들리거나 회색/깜빡임으로 더 강한 임팩트가 있었으면 좋겠다. 서명은 마우스로 직접 서명하고 저장할 수 있어야 하며, "위 항목을 모두 이해했습니다." 같은 문구를 직접 타이핑하게 하고 placeholder는 회색, 입력값은 검은색으로 보이게 한다.

## 범위

포함:

- 미응답 저장 시 누락 질문 블록 전체에 shake + gray pulse + 강조 border 적용.
- 누락 첫 질문으로 스크롤하고 alert 메시지에 누락 개수 표시.
- 전자 서명 항목에 성명 입력, 정확한 확인 문구 입력, canvas 기반 직접 서명, 지우기 버튼 추가.
- 서버 설문 검증에서 `legal_signature`를 이름/확인문구/서명 data URL/timestamp 객체로 요구.
- API/E2E 테스트 갱신.

제외:

- KIS, 주문, 자동매매, `app/risk/**`, production DB migration, secret, CI workflow.
- 법적 전자서명 서비스 또는 외부 본인인증 연동.

## 완료 내용

- `QuestionBlock`에 `data-invalid` 상태와 `animate-missing-answer` 피드백을 추가했다.
- `globals.css`에 missing-answer pulse animation을 추가했다.
- `SignatureField`를 텍스트 성명 입력에서 직접 서명 캔버스 + 확인문구 입력 + 성명 입력으로 확장했다.
- placeholder는 회색, 실제 입력 텍스트는 `text-foreground`로 표시되도록 유지했다.
- `app/services/investor_profile.py`에서 확인 문구가 정확히 `위 항목을 모두 이해했습니다.`인지, canvas PNG data URL이 있는지 검증한다.
- API 테스트에 signature object, missing signature, wrong confirmation text 케이스를 추가했다.
- Playwright 온보딩 E2E가 실제 캔버스 서명, 확인문구 입력, 미응답 block highlight를 검증하도록 갱신했다.

## 완료 기록

- 프롬프트 요구사항: 미응답 저장 feedback 강화, 직접 마우스 서명, 정확 문구 typing confirmation, placeholder/typed color 분리.
- 작업 내용: profile onboarding UI, survey validation service, CSS animation, API/E2E tests를 수정했다.
- 작업 결과: 미응답 저장 시 누락 블록이 흔들리고 회색으로 pulse되며, 전자 서명은 성명/정확 문구/직접 서명이 모두 있어야 저장된다.

## 검증

- `.venv\Scripts\python.exe -m py_compile app\services\investor_profile.py app\api\routers\profile.py app\api\schemas\__init__.py` -> OK.
- `.venv\Scripts\python.exe -m pytest tests/api/test_profile_survey.py -q` -> 12 passed, 4 warnings.
- `npm run lint` -> pass.
- `npm run build` -> pass, `/onboarding/investor-profile` generated.
- `npm run test:e2e -- e2e/investor-profile.spec.ts --reporter=line` -> 2 passed.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-010-investor-profile-ack-signature-ux.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-010.md`

## 리뷰

- UI/UX Designer: 저장 실패가 단순 텍스트 alert로 끝나지 않고 누락 블록 자체가 움직이고 흐려져 사용자가 즉시 위치를 알 수 있다.
- Backend Engineer: signature payload를 서버에서도 강제해 프론트 우회 제출을 막는다.
- QA: focused API test와 Playwright E2E가 signature success/failure와 missing-answer UI를 검증한다.
- Doc Steward: TASK/EVIDENCE/BRIEF/AUDIT/STATUS 기록을 추가하고 generated views를 갱신한다.

## Independent Audit

판정: 통과

근거:

- 변경은 profile onboarding과 survey validation에 제한됐다.
- KIS, order flow, risk gate, secret, production DB migration, CI workflow를 변경하지 않았다.
- 프론트와 서버 양쪽에서 동일한 signature/confirmation 조건을 검증한다.
- focused API, lint, build, E2E가 통과했다.

## 리스크/메모

- canvas 서명은 앱 내부 확인 강화용이며 공인 전자서명/본인인증을 대체하지 않는다.
- 서명 이미지는 설문 응답 JSON에 data URL로 저장된다. 현재 canvas 크기와 서버 size limit으로 과도한 payload는 제한했다.
