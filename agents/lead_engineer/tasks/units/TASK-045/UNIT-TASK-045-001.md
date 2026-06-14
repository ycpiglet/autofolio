---
unit_id: UNIT-TASK-045-001
task_id: TASK-045
task_set_id: TASKSET-UI-OVERHAUL
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "UI 대개편 Phase 1 — FastAPI 기초 레이어(인증+읽기 API) + Next.js 16 스캐폴드 + 코어 셸/안전 컴포넌트 + 로그인 화면 + Playwright E2E + 프론트엔드 CI. Streamlit 스트랭글러 병행 유지(무변경). 상태변경/주문 엔드포인트는 신설 금지(Phase 3)."
inputs:
  - agents/lead_engineer/tasks/TASK-045-ui-overhaul-phase1-api-foundation-login.md
  - docs/superpowers/specs/2026-06-13-ui-overhaul-design.md
  - app/ui/backend.py
  - app/services/auth_service.py
target_files:
  - app/api/main.py
  - app/api/deps.py
  - app/api/security.py
  - app/api/serializers.py
  - app/api/routers/auth.py
  - app/api/routers/engine.py
  - app/api/routers/portfolio.py
  - app/api/routers/market.py
  - app/api/routers/trade.py
  - tests/api/test_gate.py
  - web/src/app/login/page.tsx
  - web/src/app/home/page.tsx
  - web/src/components/layout/AppShell.tsx
  - web/src/components/safety/KillSwitchButton.tsx
  - web/e2e/login.spec.ts
  - .github/workflows/frontend.yml
scope: "app/api/ 신설(읽기+세션 인증), web/ 스캐폴드+토큰+lib+프록시, 코어 레이아웃·안전 컴포넌트, 로그인/홈 셸, Playwright 로그인 E2E, frontend CI. app/ui·app/services·엔진/리스크 로직 무변경. 직접 주문/상태변경 엔드포인트 금지."
acceptance:
  - "app/api/ FastAPI 앱(factory) + itsdangerous httpOnly 서명 세션 구현"
  - "읽기 엔드포인트 11종(auth/engine/portfolio/market/trade) 200 응답"
  - "df_records()→TableResponse, 한국어 컬럼 보존"
  - "직접 주문 엔드포인트 없음(POST /trade/orders→404, 테스트 강제)"
  - "require_owner 게스트 403 / 무세션 401 게이트 테스트 통과"
  - "변조·만료 쿠키 fail-closed 401"
  - "web/ npm run lint + npm run build 그린"
  - "로그인 화면 §4.4(55:45, 헤드라인, 안전 스트립, ID/PW+게스트, Google/Kakao/Naver 미노출)"
  - "킬스위치/자동매매토글 Phase1 비활성(상태표시만, 상태변경 호출 없음)"
  - "Playwright login.spec.ts 통과(게스트+로컬+실패)"
  - "frontend.yml CI(web 경로 한정, lint+build+playwright)"
  - "기존 pytest green + coverage ≥50%, check_agent_docs 0 error"
verification:
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "cd web && npm run lint && npm run build && npx playwright test"
  - "python scripts/check_agent_docs.py"
  - "python scripts/build_task_index.py --check"
handoff: "백엔드 PR(#73) 머지 후 프론트엔드 브랜치에서 스캐폴드→컴포넌트/로그인→Playwright/CI 순차. 엔드포인트 매핑·게이트 결과·빌드/E2E 결과 보고."
stop_condition: "Phase 1 읽기 API + 로그인/셸 + E2E/CI 완료 후 중단. Phase 2(홈/포트폴리오 데이터)·Phase 3(상태변경/주문 게이트)로 확장 금지."
depends_on: []
---

# UNIT-TASK-045-001 — UI 대개편 Phase 1 (FastAPI 기초 + 인증 + 읽기 API / Next.js 스캐폴드 + 로그인)

## Context

Streamlit 스트랭글러 패턴 유지 하에 FastAPI 기초 레이어와 Next.js 16 프론트엔드를
신설하고 로그인 화면을 완성한다. Phase 0(services 추출) 완료 상태에서
`app/ui/backend.py`/`app/services/*` 공유 코어를 HTTP로 재노출한다.

## Scope

In scope: `app/api/` 읽기 API + 세션 인증, `web/` 스캐폴드/토큰/lib/프록시,
코어 레이아웃·안전 컴포넌트, 로그인/홈 셸, Playwright 로그인 E2E, frontend CI.

Out of scope: Streamlit 뷰/서비스/엔진/리스크 로직 변경, 상태변경·직접 주문 엔드포인트
(Phase 3), 홈/포트폴리오 데이터 화면(Phase 2), OIDC Google 활성화(Phase 1b).

## 실행 단위 (4 서브유닛, subagent-driven-development)

1. **백엔드** (PR #73, merged): `app/api/`(main/deps/security/serializers/schemas/routers),
   세션 인증(local+guest), 읽기 엔드포인트 11종, `df_records`→`TableResponse`, `tests/api/` 66+건.
2. **프론트 스캐폴드**: `web/` create-next-app + shadcn, 디자인 토큰(`@theme`), Pretendard self-host,
   `lib/{api,format,query}`, Next rewrites 프록시, run_frontend.bat.
3. **레이아웃·로그인**: AppShell/SidebarNav(3그룹 8메뉴)/TopStatusBar + 안전 컴포넌트
   (KillSwitchButton·ModeBadge·EnvBadge·AutoTradingToggle·ConfirmModal·EmptyState) + 로그인 화면(§4.4) + 홈 셸.
4. **E2E·CI**: Playwright login.spec.ts(게스트+로컬+실패, route-mock) + `.github/workflows/frontend.yml`.

## 안전 불변식 (스펙 §3)

- 직접 주문 엔드포인트 금지 — `POST /trade/orders` 없음(404 테스트 강제).
- 상태변경 엔드포인트 0건(읽기+인증만). 킬스위치/자동매매토글은 상태표시만, Phase1 비활성.
- KIS 키 응답 미노출. 세션키 `.autofolio/`(gitignored). 변조/만료 쿠키 fail-closed.

## Verification

```powershell
python -m pytest tests/ -q --cov=app --cov-fail-under=50
cd web; npm run lint; npm run build; npx playwright test
python scripts/check_agent_docs.py
python scripts/build_task_index.py --check
```

## Stop Boundary

Phase 1 완료 후 중단. Phase 2/3로 확장 금지.

## 완료 기록

완료 시각: 2026-06-14T22:23:41+09:00
검토자: Backend Engineer + UI/UX Designer (spec/security review subagent)

**변경 내용:**
- **백엔드** (PR #73): `app/api/` FastAPI factory + itsdangerous 서명 httpOnly 세션,
  읽기 엔드포인트 11종(auth/login·logout·me, engine/status, portfolio/holdings·kpis·asset-curve·allocation-gap,
  market/indices·watchlist, trade/fills/recent), `df_records`→`TableResponse`(한국어 컬럼 보존),
  `require_owner` 게스트 403 시임, `tests/api/` 66+건. asset-curve 날짜 인덱스 보존·쿠키 대칭·키 캐싱·변조쿠키 테스트(리뷰 반영).
- **프론트** (`web/`): Next.js 16 + Tailwind v4 + shadcn, 디자인 토큰(`@theme`), Pretendard self-host,
  `lib/{api,format,query}`, `/api/:path*`→127.0.0.1:8000 rewrites, AppShell/SidebarNav/TopStatusBar,
  안전 컴포넌트 6종(Phase1 비활성), 로그인 화면(55:45·헤드라인·안전 스트립·ID/PW+게스트, Google/Kakao/Naver 미노출),
  홈 셸(auth 가드 + engine/status 배지), 8메뉴 placeholder.
- **E2E·CI**: Playwright login.spec.ts 3건(게스트+로컬+실패, route-mock), `.github/workflows/frontend.yml`(web 경로 한정, lint+build+playwright).

**검증 결과:**
- `python -m pytest tests/ -q --cov=app` → 875 passed, coverage 78.5% (app/api 92%)
- `npm run lint` → clean / `npm run build` → 13 routes 그린 / `npx playwright test` → 3 passed
- `python scripts/check_agent_docs.py` → 0 error
- 안전: 직접 주문 엔드포인트 없음(404 테스트), require_owner 403, 킬/토글 Phase1 비활성

## Independent Audit

판정: 통과 (읽기 API + 인증 게이트 + 로그인 E2E 그린; 상태변경/주문 엔드포인트 부재 확인; CI 분리 게이트 추가).
