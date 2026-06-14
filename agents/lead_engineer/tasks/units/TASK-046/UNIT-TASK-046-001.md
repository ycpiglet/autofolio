---
unit_id: UNIT-TASK-046-001
task_id: TASK-046
task_set_id: TASKSET-UI-OVERHAUL
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "UI 대개편 Phase 2 — 홈 대시보드 + 포트폴리오 읽기 화면 + 데이터 컴포넌트 7종. Phase2 추가 읽기 엔드포인트(market/trade/analysis) 소비. 데모 스코프 서버 강제(폴백 금지, 에러는 에러로 표시). 상태변경 없음."
inputs:
  - agents/lead_engineer/tasks/TASK-046-ui-overhaul-phase2-home-portfolio.md
  - docs/superpowers/specs/2026-06-13-ui-overhaul-design.md
  - app/api/routers/portfolio.py
  - app/api/routers/market.py
  - web/src/lib/api.ts
target_files:
  - app/api/routers/market.py
  - app/api/routers/trade.py
  - app/api/routers/analysis.py
  - web/src/components/domain/KpiCard.tsx
  - web/src/components/domain/HoldingsTable.tsx
  - web/src/components/domain/EquityChart.tsx
  - web/src/components/domain/AllocationChart.tsx
  - web/src/app/home/page.tsx
  - web/src/app/portfolio/page.tsx
  - web/e2e/dashboard.spec.ts
scope: "백엔드 추가 읽기 엔드포인트 11종(market/trade/analysis) + 프론트 데이터 컴포넌트(KpiCard·PnlText·DataTable·HoldingsTable·EquityChart·AllocationChart·ProposalCard) + 홈/포트폴리오 화면 + Playwright. 상태변경/주문 엔드포인트 금지(Phase 3). app/ui·services·엔진/리스크 무변경."
acceptance:
  - "백엔드 읽기 엔드포인트 11종 200 응답 + 무세션 401 + fail-loud(예외→500)"
  - "데이터 컴포넌트 7종 구현(토큰/접근성/PnL 토글)"
  - "홈 대시보드: KPI + EquityChart + 지수 + 보유 미리보기 + 최근체결"
  - "포트폴리오: HoldingsTable + AllocationChart + KPI + EquityChart"
  - "폴백 금지 — fetch 에러 시 가시적 error state(role=alert), 가짜 데이터 없음"
  - "차트 client-only, npm run build 빌드세이프(SSR 무파손)"
  - "Playwright dashboard.spec.ts 프로덕션 모드(CI=1) 통과 + login 유지"
  - "기존 pytest green + coverage ≥50%, check_agent_docs 0 error"
verification:
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "cd web && npm run lint && npm run build && CI=1 npx playwright test"
  - "python scripts/check_agent_docs.py"
handoff: "백엔드 읽기 엔드포인트 PR(#75) 머지 후 프론트 컴포넌트+화면+Playwright. 엔드포인트 매핑·빌드/프로덕션 E2E 결과 보고."
stop_condition: "Phase 2 읽기 화면 완료 후 중단. Phase 3(상태변경/주문 게이트)로 확장 금지."
depends_on: [UNIT-TASK-045-001]
---

# UNIT-TASK-046-001 — UI 대개편 Phase 2 (홈 + 포트폴리오 읽기 화면)

## Context

Phase 1 셸 위에 실데이터 읽기 화면을 구현한다. 백엔드는 Phase2 추가 읽기 엔드포인트
(market/trade/analysis)를 노출하고, 프론트는 데이터 컴포넌트 7종으로 홈/포트폴리오를 채운다.
데모 스코프는 서버가 강제하며, fetch 에러는 폴백 없이 가시적으로 표시한다.

## Scope

In scope: 읽기 엔드포인트 11종 + 데이터 컴포넌트 + 홈/포트폴리오 화면 + Playwright.

Out of scope: 상태변경/주문 엔드포인트(Phase 3, Owner 게이트), 에이전트/SSE(Phase 4),
분석 폼/CandleChart(Phase 5), Streamlit 변경.

## 실행 단위 (2 서브유닛)

1. **백엔드** (PR #75, merged): market price·fundamental·order-book·intraday·sectors·disclosures,
   trade conditions·orders(GET), analysis attribution·retro·daily-pnl. READ-ONLY + fail-loud. pytest 917 / app/api 94.9%.
2. **프론트**: KpiCard·PnlText·DataTable·HoldingsTable·EquityChart(lightweight-charts)·AllocationChart(recharts)·ProposalCard,
   홈 대시보드 + 포트폴리오 화면, dashboard.spec.ts. 차트 client-only/build-safe, 폴백 금지 error state.

## Verification

```powershell
python -m pytest tests/ -q --cov=app --cov-fail-under=50
cd web; npm run lint; npm run build; $env:CI=1; npx playwright test
python scripts/check_agent_docs.py
```

## Stop Boundary

Phase 2 완료 후 중단. Phase 3로 확장 금지.

## 완료 기록

완료 시각: 2026-06-15T00:36:09+09:00
검토자: UI/UX Designer + Backend Engineer

**변경 내용:**
- **백엔드** (PR #75): 읽기 엔드포인트 11종 추가(market 6 / trade 2 / analysis 3), 기존 `backend.py` 함수 매핑, READ-ONLY, symbol 입력검증, 예외→500(fail-loud). `tests/api/` 신규 45건.
- **프론트** (`web/`): `components/domain/` 7종 — KpiCard(.kpi tabular-nums), PnlText(KR/Western 토글), DataTable(TableResponse+에러/빈 상태), HoldingsTable(PnL 컬러), EquityChart(lightweight-charts v5, client-only), AllocationChart(recharts 도넛, client-only), ProposalCard(제안 없으면 EmptyState). 홈 대시보드(KPI+EquityChart+지수+보유미리보기+최근체결), 포트폴리오(HoldingsTable+AllocationChart+KPI+EquityChart). 차트는 `next/dynamic ssr:false`+`useEffect` DOM접근으로 빌드세이프. fetch 에러 시 `role=alert` 가시적 표시(폴백/가짜데이터 없음).
- **E2E**: `web/e2e/dashboard.spec.ts` — 홈/포트폴리오 route-mock 렌더 검증, login 유지.

**검증 결과:**
- `python -m pytest tests/ -q --cov=app` → 917 passed, coverage 78.8%(app/api 94.9%)
- `npm run lint` clean / `npm run build` 그린(차트 SSR 무파손) / `CI=1 npx playwright test` → 9 passed ×2(비플레이키)
- `python scripts/check_agent_docs.py` → 0 error

## Independent Audit

판정: 통과 — 읽기 화면 실데이터 렌더 + 폴백금지 에러상태 + 프로덕션 E2E 그린. 상태변경 엔드포인트 부재 확인.
