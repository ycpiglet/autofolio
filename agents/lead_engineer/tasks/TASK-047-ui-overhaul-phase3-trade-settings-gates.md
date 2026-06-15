---
type: task
id: TASK-047
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 상
est_hours: 20
est_tokens: 150000
tags: [ui-overhaul, fastapi, trade, settings, safety-gates, phase3, r3-adjacent]
gate: Owner 명시 승인 필수 — state-changing 엔드포인트, R3 인접; blocked by TASK-046
trigger_meeting: Owner 명시 승인 후 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-047 UI 대개편 Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) ⚠ 최고 리스크

작업 ID: TASK-047
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: UI 대개편 Phase 3 — state-changing 엔드포인트와 안전 게이트 구현 범위를 사전 정의
대상: app/services/trading.py, app/ui/views/trade.py, app/ui/views/history.py, app/ui/views/settings.py (Phase 3 범위)
방법: require_owner 데코레이터·CSRF 미들웨어 추가, DB-backed kill-switch/auto-trading, OrderForm 2단계 ack 구현
감사 로그: AUDIT-2026-06-13-007

## ⚠ 보류 사유

이 태스크는 state-changing 엔드포인트와 안전 게이트를 포함해 **Autofolio R3 인접** 작업이다. Owner 명시 승인 없이 구현을 시작하지 않는다.

**시작 전 TASK-050, TASK-051 완료 필수** — 일일 한도 UTC 버그 및 fail-open 버그가 이 Phase 전에 수정되어야 한다.

## 배경 및 목적

UI 대개편 Phase 3. 가장 리스크가 높은 state-changing 엔드포인트와 안전 게이트를 구현한다. 모든 엔드포인트에 `require_owner`(guest 403) + CSRF 헤더 필수.

## 작업 범위

### state-changing 엔드포인트

- `POST /api/engine/kill-switch` — DB-backed (세션 전용 갭 수정)
- `POST /api/engine/auto-trading` — DB-backed, `require_owner`
- `POST /api/engine/run-once` — single-flight 락 + 409 conflict
- `POST /api/trade/conditions` — 공시 422 / 컴플라이언스 CAUTION 409+ack_token 2단계
- `PUT /api/settings/*`

### 안전 게이트

- 킬스위치/심볼모드 DB-backed 통일: Streamlit에도 동일 PR 적용
- `require_owner` 데코레이터 — guest 403 전수
- CSRF 헤더 검증 미들웨어

### 프론트

- `OrderForm` — 조건 저장 2단계(공시 차단→ack 팝업→재제출)
- `OrderBookLadder`
- `SecretField`
- 설정 5탭
- `/trade`, `/history`, `/settings` 화면

## 완료 기준

- 게이트 테스트: guest 403 전수, kill-switch 200/409, 공시 422, 컴플라이언스 409+ack_token
- paper 환경 수동 검증 (Owner 실행)
- `python -m pytest tests/ -q` green
- `npm run build` 오류 없음
- TASK-050, TASK-051 선행 완료

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 3, §안전 불변식 (원 플랜은 세션 로컬)
- trade 게이트 구현: `app/services/trading.py` (Phase 0 완료)

## Done When

- Owner 명시 승인 수령
- 게이트 테스트 전수 통과
- paper 수동 검증 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-047/UNIT-TASK-047-001.md`

## 완료 기록

완료 시각: 2026-06-15T13:15:46+09:00
검토자: Backend Engineer + Compliance Officer + QA (보안 리뷰 2라운드)
승인: Owner 명시 승인 수령 (Phase 3 진행 결정)

## 증거

- **백엔드** (PR #78, merged): state-changing 엔드포인트 5종 — `POST /engine/kill-switch`·`/auto-trading`(DB-backed), `POST /engine/run-once`(single-flight 락, 중복 409, finally 해제), `POST /trade/conditions`(GateResult→saved 201/공시 422/거부 422/CAUTION 409+ack_token/error 500), `PUT /settings/risk-limits`. 전부 `require_owner`(guest 403)+CSRF(상수시간 hmac). `GET /auth/me`에 csrf_token. ack_token=itsdangerous 서명+TTL+파라미터 정확일치(변조/만료/불일치 fail-closed, raw boolean 불허). 게이트 테스트 55건. **직접 주문 엔드포인트 없음**(POST /trade/orders 404 강제).
- **프론트** (`web/`): `lib/csrf.ts` fail-safe + `X-CSRF-Token` 전 write. 킬스위치/자동매매 활성화(ConfirmModal + POST 실패 가시화, 성공 시에만 상태 갱신). OrderForm=조건 생성(주문 아님) + 409 CAUTION 2단계 ack(자동 미재제출). OrderBookLadder, SecretField(시크릿 미노출), 매매/내역/설정 5탭, run-once 확인모달. phase3.spec.ts 게이트 시나리오.
- 검증: pytest 1015 passed/coverage 78.3%, npm lint·build 그린, `CI=1 npx playwright test` 게이트 시나리오 프로덕션 모드 ×2, check_agent_docs 0 error.

## 리뷰

- **안전 불변식(§3) 준수**: 직접 주문 엔드포인트 없음(주문경로 run-once→OrderFlow→SafetyChecker 유일). 실주문 비활성(paper/mock), 브로커 env·SafetyChecker 무변경. 모든 state-changing require_owner+CSRF, 무세션 401·guest 403 전수. fail-closed(ack/CSRF/gate 예외).
- **보안 리뷰 2라운드**: (1) 백엔드 — CSRF 상수시간 비교, 무세션 401 테스트, ack 만료 테스트, 스키마 제약, secure 쿠키 prod 가드. (2) 프론트 — CSRF fail-safe(빈 토큰 캐싱 제거), 킬스위치/자동매매 POST 실패 가시화(중단 실패 오인 방지), run-once 확인모달, E2E CSRF/ack callCount 단언.
- **한계(정직)**: paper 환경 **수동 검증은 Owner 실행 영역**(Done When 항목, 미완) — 실 KIS paper 계정 연동 수기 확인 필요. Playwright는 route-mock(실 백엔드 미기동). 048·049는 이 PR 머지로 의존성 해제.

## Independent Audit

판정: 통과 — Owner 승인 + 게이트 전수 + 보안 2라운드. 직접 주문/실주문 부재 확인. paper 수동검증만 Owner 잔여.

