---
type: task
id: TASK-037
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer]
priority: High
difficulty: 상
est_hours: 16
est_tokens: 120000
tags: [ui-overhaul, fastapi, next-js, authentication, login, phase1]
gate: no live orders; paper-safe; Owner 승인 전 prod 전환 금지
trigger_meeting: Phase 0 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-001
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-037 UI 대개편 Phase 1 — FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인

작업 ID: TASK-037
상태: 대기
Owner: Backend Engineer
기록 시각: 2026-06-13T01:33:29+09:00

## 배경 및 목적

UI 대개편 Phase 1. Streamlit 스트랭글러 패턴 유지 하에 FastAPI 기초 레이어와 Next.js 스캐폴드를 신설하고, 로그인 화면을 완성한다.

Phase 0(services 추출)이 완료된 상태에서 진행. `app/services/*`가 FastAPI와 Streamlit의 공유 서비스 레이어 역할을 한다.

## 작업 범위

### 백엔드 (`app/api/`)

- `app/api/` 디렉토리 신설: `main.py`, `deps.py`, `security.py`, `serializers.py`, `schemas/`, `routers/`
- 세션 인증: local ID/PW(기존 vault PBKDF2 재사용) + guest(`role=guest`, `data_source=demo`) 고정. OIDC는 1b.
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

- 마스터 플랜: `.claude/plans/glimmering-waddling-spring.md` §Phase 1
- 디자인 스펙: `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md`
- 서비스 레이어: `app/services/` (Phase 0 산출)
- 안전 불변식: 스펙 §3

## Done When

- `/login` → 게스트 로그인 → `/home`(빈 셸) 브라우저 확인
- API `GET /api/engine/status` 응답 200
- `tests/api/` 신규 계약 테스트 green
- `npm run build` 오류 없음
