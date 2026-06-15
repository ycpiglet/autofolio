---
unit_id: UNIT-TASK-049-001
task_id: TASK-049
task_set_id: TASKSET-UI-OVERHAUL
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "UI 대개편 Phase 5 빌드아웃 — 분석 화면(CandleChart/백테스트/VaR/시나리오/Sankey) + 분석 읽기 엔드포인트 + 8화면 패리티 감사. Streamlit 은퇴(파괴적: AppTest 32개 제거 + backend→services 역파사드 해소)는 새 앱 paper 검증 전이라 본 유닛에서 제외(Owner 게이트)."
inputs:
  - agents/lead_engineer/tasks/TASK-049-ui-overhaul-phase5-analysis-parity-retire.md
  - docs/superpowers/specs/2026-06-13-ui-overhaul-design.md
  - app/quant/backtest.py
  - app/quant/risk_sim.py
target_files:
  - app/api/routers/analysis.py
  - web/src/components/domain/CandleChart.tsx
  - web/src/components/domain/BacktestPanel.tsx
  - web/src/components/domain/VarPanel.tsx
  - web/src/components/domain/AttributionSankey.tsx
  - web/src/app/analysis/page.tsx
  - web/e2e/analysis.spec.ts
  - docs/reports/UI-PARITY-AUDIT-2026-06-15.md
scope: "분석 읽기 엔드포인트(backtest/VaR/scenario/whatif) + 분석 화면(CandleChart/백테스트/VaR/시나리오/Sankey) + 8화면 패리티 감사 문서. Streamlit 은퇴/AppTest 제거/backend→services 이동은 제외(Owner paper 검증 후 별도)."
acceptance:
  - "분석 읽기 엔드포인트 4종(GET, require_session, READ-ONLY, fail-loud, n_sim 캡)"
  - "분석 화면 5섹션(CandleChart·백테스트·VaR·시나리오·Sankey), 차트 client-only·build-safe"
  - "8화면 패리티 감사 문서 작성(8/8 빌드아웃 완료, 안전 패리티 확보)"
  - "Playwright 분석 스펙 프로덕션 모드 통과 + 전체 스위트 green"
  - "기존 pytest green + coverage ≥50%, check_agent_docs 0 error"
  - "Streamlit 은퇴는 본 유닛 범위 밖(Owner 게이트로 보류 기록)"
verification:
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "cd web && npm run lint && npm run build && CI=1 npx playwright test"
  - "python scripts/check_agent_docs.py"
handoff: "백엔드 분석 엔드포인트 PR(#82) 머지 후 분석 화면 + 패리티 감사. Streamlit 은퇴는 paper 검증 후 별도 태스크."
stop_condition: "분석 화면 + 패리티 감사 완료 후 중단. Streamlit 은퇴(파괴적)는 Owner paper 검증·승인 전 금지."
depends_on: [UNIT-TASK-046-001, UNIT-TASK-047-001, UNIT-TASK-048-001]
---

# UNIT-TASK-049-001 — UI 대개편 Phase 5 빌드아웃 (분석 화면 + 패리티 감사)

## Context

UI 대개편 최종 화면(분석)을 완성하고 8화면 패리티를 감사한다. Streamlit 은퇴는
파괴적(AppTest 32개 제거, backend→services 역파사드 해소, 26개 테스트 재배선)이고
새 Next.js 앱의 실 paper 검증이 미완이므로 본 유닛에서 제외하고 Owner 게이트로 남긴다.

## Scope

In scope: 분석 읽기 엔드포인트 + 분석 화면 5섹션 + 패리티 감사 문서.
Out of scope: Streamlit 은퇴, AppTest 제거, backend→services 실이동, docker-compose 정리 (모두 Owner paper 검증 후 별도).

## 실행 단위

1. **백엔드** (PR #82, merged): `analysis.py`에 backtest/VaR/scenario/whatif GET 추가(READ-ONLY, 검증, n_sim 캡). 테스트 29건.
2. **프론트**: CandleChart(lightweight-charts 캔들)·BacktestPanel·VarPanel·ScenarioPanel·AttributionSankey(recharts) + `/analysis` 5섹션. 차트 client-only(`ssr:false`)·build-safe. analysis.spec.ts.
3. **패리티 감사**: `docs/reports/UI-PARITY-AUDIT-2026-06-15.md` — 8/8 화면 빌드아웃 + 안전 패리티 + 은퇴 보류 근거/조건.

## 안전

- 분석은 READ-ONLY(상태변경/주문 무관). 은퇴 미실행(안전망 UI 보존).

## Verification

```powershell
python -m pytest tests/ -q --cov=app --cov-fail-under=50
cd web; npm run lint; npm run build; $env:CI=1; npx playwright test
python scripts/check_agent_docs.py
```

## Stop Boundary

분석 화면 + 패리티 감사 완료 후 중단. Streamlit 은퇴는 Owner paper 검증·승인 전 금지.

## 완료 기록

완료 시각: 2026-06-15T18:27:03+09:00
검토자: UI/UX Designer + Backend Engineer

**변경 내용:**
- **백엔드** (PR #82): `app/api/routers/analysis.py`에 `GET /analysis/backtest`(run_sma_crossover)·`/var`(compute_var)·`/scenario`(scenario_analysis)·`/whatif`(whatif_weight_change) — READ-ONLY, 입력 검증, n_simulations ≤50000 캡, fail-loud. 테스트 29건.
- **프론트** (`web/`): CandleChart(lightweight-charts 캔들, /market/intraday)·BacktestPanel·VarPanel(note 배너)·ScenarioPanel·AttributionSankey(recharts) + `/analysis` 5섹션. 차트 `dynamic ssr:false`·DOM-only-in-useEffect로 build-safe. 폴백 없는 에러 상태.
- **패리티 감사**: `docs/reports/UI-PARITY-AUDIT-2026-06-15.md` — 8/8 화면 빌드아웃 완료, 안전 불변식 패리티 확보, Streamlit 은퇴 보류 근거(미검증·파괴적·되돌리기 비용)·진행 조건 명시.

**검증 결과:**
- `python -m pytest tests/ -q` → 1067 passed, coverage 78.6%
- `npm run lint` clean / `npm run build` 그린 / `CI=1 npx playwright test` 전체 29 passed ×2(login/dashboard/phase3/phase4/analysis)
- `python scripts/check_agent_docs.py` → 0 error

## Independent Audit

판정: 통과(빌드아웃 범위) — 분석 화면 + 패리티 감사 완료. Streamlit 은퇴는 의도적 제외(Owner paper 검증·승인 게이트). TASK-049는 은퇴 잔여로 보류 유지.
