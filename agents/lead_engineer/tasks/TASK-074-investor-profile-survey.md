---
type: task
id: TASK-074
display_id: TASK-074
task_uid: 93c748b6-4d52-4a8b-b93e-cad9964dfc33
registered_at: 2026-06-17T00:25:23+09:00
created_at: 2026-06-17T00:25:23+09:00
started_at: 2026-06-17T00:25:23+09:00
updated_at: 2026-06-17T00:25:23+09:00
completed_at: 2026-06-17T00:25:23+09:00
status: 완료
owner: Lead Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 80000
tags: [profile, survey, onboarding, personalization, database, ui, safety]
gate: Owner direct request approved DB schema change; no KIS, live order, app/risk, secret, prod, or CI workflow changes
trigger_meeting: Owner direct request 2026-06-17
audit_log: AUDIT-2026-06-17-001
created: 2026-06-17
---

# TASK-074 Investor profile survey and satisfaction loop

작업 ID: TASK-074
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-17T00:25:23+09:00
기록 시각: 2026-06-17T00:25:23+09:00
요청자: Owner
수행자: Lead Engineer, Backend Engineer, UI/UX Designer, QA, Doc Steward
의도: Owner가 승인한 계획에 따라 투자 성향, 지식수준, 만족 기준, 자동화 선호를 수집하는 설문과 재평가 루프를 구현한다.
대상: FastAPI profile API, SQLite profile tables, Next.js onboarding/settings/trade/home surfaces, API/E2E tests
방법: 신규 profile service/router/schema 추가, 실행성 액션 profile gate, 온보딩 UI, 설정 체크인 UI, focused API/E2E regression
감사 로그: AUDIT-2026-06-17-001

## 범위

포함:

- 신규 투자 프로필 설문 API와 SQLite 테이블.
- 12-15문항 실용형 설문 정의와 5단계 성향/4단계 지식수준 산출.
- 프로필 미완료 시 조건 저장, 엔진 1회 실행, 자동매매 ON 차단.
- 홈/상태바/매매/설정/온보딩 화면 연결.
- 월간/이벤트 만족도 체크인 저장 API와 설정 UI.
- 성향 초과 진행 확인 기록 API.

제외:

- KIS 주문 경로, 실주문, `app/brokers/kis/**`, `app/engine/order_flow.py`, `app/risk/**`.
- 법적 투자자문/투자권유 적합성 완료 표시.
- 실제 리스크 한도 자동 변경.
- production deployment, secrets, CI workflow 변경.

## 완료 내용

- `investor_profiles`, `investor_survey_responses`, `investor_override_acknowledgements`, `investor_checkins` 테이블을 추가했다.
- `app/services/investor_profile.py`에 설문 정의, 응답 검증, 점수 계산, 프로필 저장, override/check-in 기록을 구현했다.
- `/api/profile/investor`, `/api/profile/survey`, `/api/profile/override-ack`, `/api/profile/checkin`을 추가했다.
- 조건 저장, 엔진 1회 실행, 자동매매 ON 전환에 프로필 완료 게이트를 추가했다.
- `/onboarding/investor-profile` 화면, 홈 CTA, 상태바 프로필 배지, 매매 실행성 액션 guard, 설정의 투자 프로필/체크인 탭을 추가했다.
- API 테스트와 Playwright 온보딩 E2E를 추가했다.

## 변경 파일

- `app/database/schema.sql`
- `app/services/investor_profile.py`
- `app/api/routers/profile.py`
- `app/api/routers/engine.py`, `app/api/routers/trade.py`, `app/api/main.py`, `app/api/schemas/__init__.py`
- `web/src/app/onboarding/investor-profile/page.tsx`
- `web/src/app/home/page.tsx`, `web/src/app/trade/page.tsx`, `web/src/app/settings/page.tsx`
- `web/src/components/domain/OrderForm.tsx`, `web/src/components/layout/*`, `web/src/components/safety/AutoTradingToggle.tsx`, `web/src/lib/api.ts`
- `tests/api/test_profile_survey.py`, `tests/api/test_phase3_state.py`
- `web/e2e/investor-profile.spec.ts`

## 완료 기록

완료 시각: 2026-06-17T00:25:23+09:00
검토자: Lead Engineer perspective + Backend Engineer perspective + UI/UX Designer perspective + QA perspective + same-session Independent Audit
실측 비용 (시간): 약 1.2h
실측 비용 (LLM 토큰): Codex session local meter unavailable
협업 waiver: single-session env scope. 실제 외부 subagent dispatch는 사용하지 않았고 역할 관점별 self-review와 자동 게이트 증거로 대체했다.
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 focused tests/lint/build/e2e로 대체했다.

## 검증

- `.\\.venv\\Scripts\\python.exe -m py_compile app/services/investor_profile.py app/api/routers/profile.py app/api/routers/trade.py app/api/routers/engine.py app/api/schemas/__init__.py app/api/main.py` -> OK.
- `.\\.venv\\Scripts\\python.exe -m pytest tests/api -q` -> 274 passed, 15 warnings.
- `npm run lint` in `web/` -> pass, 0 warnings/errors.
- `npm run build` in `web/` -> successful.
- `npx playwright test e2e/phase3.spec.ts e2e/investor-profile.spec.ts` in `web/` -> 5 passed.
- `python scripts/validate_task_schema.py` -> OK.
- `python scripts/build_task_index.py --check` -> OK.
- `python scripts/generate_views.py --check` -> OK.
- `python scripts/check_agent_docs.py` -> OK, 0 errors / 121 warnings.
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs` -> pass.
- `git diff --check` -> OK. CRLF normalization warnings only.

## 증거

- `tests/api/test_profile_survey.py`: 프로필 미완료 shape, 설문 제출, final ack 필수, guest 차단, condition/run-once profile gate, check-in, override ack 검증.
- `tests/api/test_phase3_state.py`: 기존 CSRF/compliance ack 계약 유지.
- `web/e2e/phase3.spec.ts`, `web/e2e/investor-profile.spec.ts`: 기존 조건 등록/엔진 실행 confirmation 흐름과 온보딩 설문 저장 후 프로필 요약 렌더링 확인.

## 남은 이슈 / 한계

- 신규 DB schema surface는 Owner direct request로 승인된 범위이며, production DB migration run은 별도 운영 절차가 필요하다.
- v1은 개인화 설문이며 법적 적합성 완료 시스템이 아니다.
- 성향 초과 제안의 override 기록 API는 구현했지만 모든 제안 카드에 자동 연결하는 세부 정책은 후속 단계에서 확장 가능하다.
- 심화 설문은 `needs_advanced_survey` 신호만 제공한다. 별도 심화 문항 세트는 후속 TASK로 분리 가능하다.

## 리뷰

- Lead Engineer review: Owner 요청의 핵심인 "수익률만으로 만족을 판단하지 않는" 구조를 profile + check-in loop로 구현했다.
- Backend Engineer review: DB 테이블은 기존 `schema.sql` 정본에 추가했고, 서비스에서 `CREATE TABLE IF NOT EXISTS`를 보장해 기존 로컬 DB에서도 안전하게 동작한다.
- UI/UX Designer review: 첫 사용자는 온보딩 화면으로 유도하고, 설정 탭에서 재평가/체크인이 가능하다. 조회 화면은 막지 않고 실행성 액션만 제한한다.
- QA review: API gate와 E2E 렌더링을 focused tests로 고정했다.
- Self-review note: 같은 Codex 세션에서 구현과 검증을 수행했으므로 Independent Audit은 evidence-based same-session review로 제한한다.

## Independent Audit

판정: 통과

근거:

- Owner가 명시적으로 계획 구현을 요청해 DB schema R3 변경 승인 근거가 있다.
- KIS, live order, risk policy, secrets, CI workflow를 변경하지 않았다.
- 프로필 미완료 상태에서 실행성 액션은 서버측 428로 fail-closed 된다.
- 킬스위치와 조회는 프로필 없이 계속 가능해 안전 조작을 방해하지 않는다.
- full API tests, lint, build, phase3 + onboarding Playwright E2E가 통과했다.
