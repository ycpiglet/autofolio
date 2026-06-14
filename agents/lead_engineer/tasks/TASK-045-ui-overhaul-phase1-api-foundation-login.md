---
type: task
id: TASK-045
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer]
priority: High
difficulty: 상
est_hours: 16
est_tokens: 120000
tags: [ui-overhaul, fastapi, next-js, authentication, login, phase1]
gate: no live orders; paper-safe; Owner 승인 전 prod 전환 금지
trigger_meeting: Phase 0 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-045 UI 대개편 Phase 1 — FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인

작업 ID: TASK-045
상태: 완료
Owner: Backend Engineer
기록 시각: 2026-06-13T01:33:29+09:00

## 배경 및 목적

UI 대개편 Phase 1. Streamlit 스트랭글러 패턴 유지 하에 FastAPI 기초 레이어와 Next.js 스캐폴드를 신설하고, 로그인 화면을 완성한다.

Phase 0(services 추출)이 완료된 상태에서 진행. `app/services/*`가 FastAPI와 Streamlit의 공유 서비스 레이어 역할을 한다.

## 작업 범위

### 백엔드 (`app/api/`)

- `app/api/` 디렉토리 신설: `main.py`, `deps.py`, `security.py`, `serializers.py`, `schemas/`, `routers/`
- 세션 인증: local ID/PW(기존 vault PBKDF2 재사용) + guest(`role=guest`, `data_source=demo`) 고정. Google CTA 비노출(죽은 버튼 금지 원칙). OIDC는 Phase 1b(스펙 §Phase 1 정의 참조 — Authlib OIDC + Google CTA 활성화, Phase 1 머지 후 즉시 후속).
- httpOnly 서명 쿠키 세션 (`itsdangerous`, 키: `.autofolio/api_session.key`)
- 읽기 엔드포인트:
  - `auth/*` (login, logout, me)
  - `engine/status`
  - `portfolio/holdings`, `portfolio/kpis`, `portfolio/asset-curve`, `portfolio/allocation-gap`
  - `market/indices`, `market/watchlist`
  - `trade/fills/recent`
- `df_records()` 직렬화 헬퍼, 한국어 컬럼 키 유지, `TableResponse{columns, rows}` 스키마
- 의존성 추가: `fastapi`, `uvicorn[standard]`, `httpx`, `itsdangerous`

### 프론트 (`web/`)

- `web/` 스캐폴드: `create-next-app` + `shadcn/ui init`
- 토큰 선언: `globals.css` Tailwind v4 `@theme` (§디자인 시스템 토큰)
- 코어 레이아웃: `AppShell`, `SidebarNav`(3그룹 8메뉴), `TopStatusBar`
- 안전 컴포넌트: `KillSwitchButton`, `ModeBadge`, `EnvBadge`, `AutoTradingToggle`, `ConfirmModal`
- **로그인 화면 완성** (`/login`): 55:45 스플릿, 헤드라인 "투자는 에이전트 팀에게, 결정은 나에게.", Google CTA → ID/PW → 게스트 데모 카드, 안전 스트립, Kakao/Naver 스텁 없음
- `lib/api.ts`, `lib/format.ts`, `lib/query.ts`
- Next `rewrites` 프록시 (`/api/**` → `http://127.0.0.1:8000/**`)

### 실행 스크립트

- `scripts/run_api.py`, `run_api.bat`, `run_frontend.bat`

## 완료 기준

- 게스트/ID·PW 로그인 → `/home`(빈 AppShell) 도달
- Playwright `login.spec.ts` 통과 (게스트+local 2개 케이스)
- API pytest: contract 테스트 + guest 403 게이트 테스트 green
- CI coverage ≥50%
- `python scripts/check_agent_docs.py` 0 error
- Streamlit 동작 무변화 (기존 pytest green)

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 1 (원 플랜은 세션 로컬)
- 서비스 레이어: `app/services/` (Phase 0 산출)
- 서비스 레이어: `app/services/` (Phase 0 산출)
- 안전 불변식: 스펙 §3

## Done When

- `/login` → 게스트 로그인 → `/home`(빈 셸) 브라우저 확인
- API `GET /api/engine/status` 응답 200
- `tests/api/` 신규 계약 테스트 green
- `npm run build` 오류 없음

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-045/UNIT-TASK-045-001.md`

## 완료 기록

완료 시각: 2026-06-14T22:23:41+09:00
검토자: Backend Engineer + UI/UX Designer (spec/security review subagent)

## 증거

- **백엔드** (PR #73, merged): `app/api/` FastAPI factory + itsdangerous httpOnly 서명 세션. 읽기 엔드포인트 11종(auth/login·logout·me, engine/status, portfolio/holdings·kpis·asset-curve·allocation-gap, market/indices·watchlist, trade/fills/recent), `df_records()`→`TableResponse`(한국어 컬럼 보존). `tests/api/` 66+건(계약 + 무세션 401 + 게스트 require_owner 403 + 직렬화). 리뷰 반영: asset-curve 날짜 인덱스 보존, set/delete 쿠키 대칭, 세션키 캐싱, 변조쿠키 fail-closed 테스트.
- **프론트** (`web/`): Next.js 16 + Tailwind v4 + shadcn 스캐폴드, 디자인 토큰(`@theme`: page #F2F4F6 / surface #FFF / text #191F28 / brand #3182F6, KR PnL 토글), Pretendard self-host, `lib/{api,format,query}`, `/api/:path*`→127.0.0.1:8000 rewrites. 코어 레이아웃(AppShell·SidebarNav 3그룹 8메뉴·TopStatusBar 새로고침버튼 제거) + 안전 컴포넌트 6종(KillSwitchButton·ModeBadge·EnvBadge·AutoTradingToggle·ConfirmModal·EmptyState, **Phase1 비활성**). 로그인 화면(§4.4: 55:45 스플릿, 헤드라인 "투자는 에이전트 팀에게, 결정은 나에게.", 안전 스트립, ID/PW + 게스트, **Google/Kakao/Naver 미노출**), 홈 셸(auth 가드 + engine/status 배지).
- **E2E·CI**: Playwright `web/e2e/login.spec.ts` 3건(게스트+로컬+실패, route-mock — 백엔드 불요), `.github/workflows/frontend.yml`(web 경로 한정, lint+build+playwright, Python CI와 분리).
- 검증: pytest **875 passed**/coverage **78.5%**(app/api 92%), `npm run lint` clean, `npm run build` 13 routes, `npx playwright test` 3 passed, check_agent_docs 0 error.

## 리뷰

- **안전 불변식(스펙 §3) 준수**: 직접 주문 엔드포인트 없음(`POST /trade/orders`→404 테스트 강제). 상태변경 엔드포인트 0건(읽기+인증만). 킬스위치/자동매매토글은 상태표시만·Phase1 비활성(존재하지 않는 엔드포인트 호출 없음 — Phase 3에서 활성). KIS 키 응답 미노출, 세션키 `.autofolio/`(gitignored), 변조/만료 쿠키 fail-closed 401.
- **죽은 버튼 금지**: Phase 1은 Google CTA 비노출(OIDC는 Phase 1b 후속). Kakao/Naver 스텁 제거.
- **스트랭글러 무변경**: app/ui·app/services·엔진/리스크 로직 무수정 — 기존 Streamlit·pytest 그대로.
- **한계(정직)**: Playwright는 route-mock E2E(실 백엔드 미기동) — 실 백엔드 연동 수동검증은 `run_api.bat` + `run_frontend.bat`로 별도. 홈 대시보드 데이터는 Phase 2, 상태변경/주문 게이트는 Phase 3(보류, Owner 승인).

## Independent Audit

판정: 통과 — 읽기 API + 인증 게이트 + 로그인 E2E 그린, 상태변경/주문 엔드포인트 부재 확인, frontend CI 분리 게이트 추가. CI(test.yml + frontend.yml) 그린 확인 후 머지.
