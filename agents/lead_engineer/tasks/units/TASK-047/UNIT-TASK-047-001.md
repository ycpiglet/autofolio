---
unit_id: UNIT-TASK-047-001
task_id: TASK-047
task_set_id: TASKSET-UI-OVERHAUL
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure, safety_gate]
context: "UI 대개편 Phase 3 (최고 리스크, Owner 명시 승인 완료) — state-changing 엔드포인트 + 안전 게이트(require_owner+CSRF, ack_token 2단계, single-flight) + 매매/내역/설정 화면. 직접 주문 엔드포인트 신설 금지 — 주문경로는 run-once→OrderFlow→SafetyChecker 유일. 실주문 비활성(paper/mock) 유지."
inputs:
  - agents/lead_engineer/tasks/TASK-047-ui-overhaul-phase3-trade-settings-gates.md
  - docs/superpowers/specs/2026-06-13-ui-overhaul-design.md
  - app/services/trading.py
  - app/api/deps.py
  - app/api/security.py
target_files:
  - app/api/deps.py
  - app/api/security.py
  - app/api/routers/engine.py
  - app/api/routers/trade.py
  - app/api/routers/settings.py
  - tests/api/test_phase3_state.py
  - web/src/lib/csrf.ts
  - web/src/components/safety/KillSwitchButton.tsx
  - web/src/components/safety/AutoTradingToggle.tsx
  - web/src/components/domain/OrderForm.tsx
  - web/src/app/trade/page.tsx
  - web/src/app/settings/page.tsx
  - web/e2e/phase3.spec.ts
scope: "state-changing 엔드포인트(kill-switch·auto-trading·run-once·trade/conditions POST·settings PUT) + require_owner+CSRF + ack_token 2단계 + single-flight + 매매/내역/설정 화면 + 킬/자동 활성화. 직접 주문/실주문/브로커env/SafetyChecker 변경 금지."
acceptance:
  - "모든 state-changing 엔드포인트 require_owner(guest 403)+CSRF(상수시간) 강제"
  - "무세션 401, guest 403 전수"
  - "POST /trade/conditions GateResult 매핑(saved 201/공시 422/거부 422/CAUTION 409+ack_token/error 500)"
  - "ack_token 변조·만료·불일치 fail-closed(raw boolean ack 불허)"
  - "run-once single-flight 락(중복 409, 예외 시 해제)"
  - "직접 주문 엔드포인트 없음(POST /trade/orders 404)"
  - "kill-switch/auto-trading DB-backed"
  - "프론트: 킬/자동 ConfirmModal 활성(실패 가시화), OrderForm 2단계 ack(자동 미재제출), CSRF 헤더 전 write, run-once 확인"
  - "Playwright 게이트 시나리오 프로덕션 모드 통과 + 기존 pytest green"
verification:
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "cd web && npm run lint && npm run build && CI=1 npx playwright test"
  - "python scripts/check_agent_docs.py"
handoff: "백엔드 PR(#78) 머지 후 프론트 화면+게이트 Playwright. 보안 리뷰 2라운드(백엔드 CSRF 상수시간/무세션/만료ack, 프론트 CSRF fail-safe/킬실패 가시화/run-once 확인) 반영."
stop_condition: "Phase 3 state-changing + 게이트 + 화면 완료 후 중단. paper 수동검증은 Owner 영역. Phase 4/5는 별도 태스크."
depends_on: [UNIT-TASK-045-001, UNIT-TASK-046-001]
---

# UNIT-TASK-047-001 — UI 대개편 Phase 3 (매매·내역·설정 state-changing + 안전 게이트)

## Context

최고 리스크 단계. Owner 명시 승인 후 진행. state-changing 엔드포인트와 안전 게이트를 구현하되,
직접 주문 엔드포인트는 신설하지 않는다 — 주문경로는 `run-once → OrderFlow → SafetyChecker` 유일.
실주문은 비활성(paper/mock) 유지, 브로커 env·SafetyChecker 무변경.

## Scope

In scope: kill-switch·auto-trading·run-once·trade/conditions POST·settings PUT(require_owner+CSRF),
ack_token 2단계, single-flight, 매매/내역/설정 화면, 킬/자동 활성화.

Out of scope: 직접 주문/실주문 활성화, 브로커 env, SafetyChecker/OrderFlow 변경, Phase 4(에이전트/SSE)·Phase 5(은퇴).

## 실행 단위 (2 서브유닛 + 보안 리뷰 2라운드)

1. **백엔드** (PR #78, merged): CSRF(상수시간 hmac)·require_owner_csrf, kill-switch/auto-trading(DB), run-once(single-flight 409),
   trade/conditions(GateResult→HTTP, ack_token 2단계 fail-closed), settings/risk-limits, 스키마 제약. 게이트 테스트 55건. 보안 리뷰 반영.
2. **프론트**: lib/csrf(fail-safe)·CSRF 헤더 전 write, 킬스위치/자동매매 활성화(ConfirmModal + 실패 가시화),
   OrderForm(조건 생성, 2단계 CAUTION ack — 자동 미재제출), OrderBookLadder, SecretField(시크릿 미노출),
   매매/내역/설정 5탭, run-once 확인모달. phase3.spec.ts 게이트 시나리오. 안전 리뷰 반영.

## 안전 불변식 (절대 위반 금지)

- 직접 주문 엔드포인트 금지(POST /trade/orders 404). run-once만 주문 트리거(→OrderFlow→SafetyChecker).
- 모든 state-changing: require_owner(guest 403)+CSRF. 무세션 401. fail-closed.
- ack_token: 서명+TTL+파라미터 정확일치, 변조/만료/불일치 시 재게이트. raw boolean ack 불허.
- 실주문 비활성(paper/mock), 브로커 env·SafetyChecker 무변경. KIS 키 미노출.

## Verification

```powershell
python -m pytest tests/ -q --cov=app --cov-fail-under=50
cd web; npm run lint; npm run build; $env:CI=1; npx playwright test
python scripts/check_agent_docs.py
```

## Stop Boundary

Phase 3 완료 후 중단. paper 수동검증은 Owner. Phase 4/5는 별도.

## 완료 기록

완료 시각: 2026-06-15T13:15:46+09:00
검토자: Backend Engineer + Compliance Officer + QA (보안 리뷰 2라운드)

**변경 내용:**
- **백엔드** (PR #78): `require_owner_csrf`(CSRF 상수시간 hmac 비교), `POST /engine/kill-switch`·`/auto-trading`(DB-backed), `POST /engine/run-once`(module lock, 중복 409, finally 해제), `POST /trade/conditions`(GateResult→saved 201/공시 422/거부 422/CAUTION 409+ack_token/error 500), `PUT /settings/risk-limits`, `GET /auth/me`에 csrf_token. ack_token=itsdangerous 서명+TTL+파라미터 정확일치(변조/만료/불일치 fail-closed). 스키마 제약(side Literal·qty≥1·price>0), secure 쿠키 prod 가드. 게이트 테스트 55건(guest 403 전수·무세션 401·CSRF·run-once 409·Gate 매핑·ack 만료·스키마 422·no-order 404).
- **프론트** (`web/`): `lib/csrf.ts`(fail-safe — 실패 시 캐시 안 함·throw), `apiPost/apiPut`에 `X-CSRF-Token` 전 write. KillSwitchButton/AutoTradingToggle 활성화(ConfirmModal + POST 실패 가시화, 성공 시에만 상태 갱신). OrderForm(조건 생성, 409 CAUTION→모달→ack_token 재제출, 자동 미재제출). OrderBookLadder, SecretField(서버 시크릿 미노출). 매매/내역/설정 5탭. run-once 확인모달. phase3.spec.ts(킬 CSRF·자동 모달우선·2단계 ack callCount·run-once 409).

**검증 결과:**
- `python -m pytest tests/ -q --cov=app` → 1015 passed, coverage 78.3%
- `npm run lint` clean / `npm run build` 그린 / `CI=1 npx playwright test` 게이트 시나리오 통과(프로덕션 모드 ×2)
- `python scripts/check_agent_docs.py` → 0 error
- 안전: 직접 주문 엔드포인트 없음, 실주문 비활성, ack/CSRF fail-closed, 킬스위치 실패 가시화

## Independent Audit

판정: 통과 — Owner 승인 + 게이트 전수 + 보안 리뷰 2라운드 반영. 직접 주문/실주문 부재 확인. ⚠ paper 환경 수동 검증은 Owner 실행 영역(미완 항목).
