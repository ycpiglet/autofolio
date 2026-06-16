# Phase 5 Analysis Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/analysis` page with CandleChart (lightweight-charts candlestick), Backtest form/results, VaR form/results, Scenario table, and a Sankey/attribution flow chart — all backed by real API calls, no fake data, build-safe (ssr:false for DOM charts), Playwright E2E suite fully green in production mode.

**Architecture:** Five domain components live in `web/src/components/domain/`; the `/analysis` page composes them with TanStack Query. All charts that use DOM APIs (lightweight-charts, recharts Sankey) are `"use client"` files imported via `next/dynamic({ ssr: false })` at the page level. The existing `api.ts`, `KpiCard`, `DataTable`, and `AppShell` are reused verbatim.

**Tech Stack:** Next.js 16 (App Router), React 19, TypeScript, TanStack Query v5, lightweight-charts v5, recharts v3, Tailwind CSS v4, Playwright 1.60.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `web/src/components/domain/CandleChart.tsx` | lightweight-charts candlestick; "use client"; DOM only in useEffect |
| Create | `web/src/components/domain/BacktestPanel.tsx` | Form + result KpiCards for backtest endpoint |
| Create | `web/src/components/domain/VarPanel.tsx` | Form + result KpiCards for VaR endpoint |
| Create | `web/src/components/domain/ScenarioPanel.tsx` | Scenario DataTable + optional whatif input |
| Create | `web/src/components/domain/AttributionSankey.tsx` | recharts Sankey (or bar fallback); "use client"; DOM-safe |
| Modify | `web/src/app/analysis/page.tsx` | Replace placeholder; tab/section layout; dynamic imports |
| Modify | `web/src/lib/api.ts` | Add BacktestResult, SimulationResult types + typed helpers |
| Create | `web/e2e/analysis.spec.ts` | Playwright E2E: mocks + assertions for all analysis sections |

---

## Task 1: Branch setup + types in api.ts

**Files:**
- Modify: `web/src/lib/api.ts`

- [ ] **Step 1: Create the feature branch**

```powershell
git switch -c feat/task-049-web-analysis
```

Expected: `Switched to a new branch 'feat/task-049-web-analysis'`

- [ ] **Step 2: Add domain types and typed helpers to api.ts**

Open `web/src/lib/api.ts`. Append the following block **after** the last existing export (after `apiIcDecisions`):

```typescript
// ── Analysis domain types ─────────────────────────────────────────────────

export interface BacktestResult {
  symbol: string;
  strategy: string;
  start: string;
  end: string;
  total_return_pct: number;
  trade_count: number;
  win_rate_pct: number;
  max_drawdown_pct: number;
}

export interface SimulationResult {
  total_value: number;
  n_simulations: number;
  horizon_days: number;
  var_95: number;
  var_99: number;
  cvar_95: number;
  max_drawdown_pct: number;
  note?: string;
}

// ── Analysis typed helpers ────────────────────────────────────────────────

/** GET /api/market/intraday?symbol=&time_unit=&count= → TableResponse OHLC */
export function apiIntraday(
  symbol: string,
  time_unit = 1,
  count = 80,
): Promise<TableResponse> {
  const q = new URLSearchParams({
    symbol,
    time_unit: String(time_unit),
    count: String(count),
  });
  return apiGet<TableResponse>(`/api/market/intraday?${q}`);
}

/** GET /api/analysis/backtest?symbol=&start=&end=&fast=&slow= */
export function apiBacktest(params: {
  symbol: string;
  start: string;
  end: string;
  fast: number;
  slow: number;
}): Promise<BacktestResult> {
  const q = new URLSearchParams({
    symbol: params.symbol,
    start: params.start,
    end: params.end,
    fast: String(params.fast),
    slow: String(params.slow),
  });
  return apiGet<BacktestResult>(`/api/analysis/backtest?${q}`);
}

/** GET /api/analysis/var?horizon_days=&n_simulations= */
export function apiVar(params: {
  horizon_days: number;
  n_simulations: number;
}): Promise<SimulationResult> {
  const q = new URLSearchParams({
    horizon_days: String(params.horizon_days),
    n_simulations: String(params.n_simulations),
  });
  return apiGet<SimulationResult>(`/api/analysis/var?${q}`);
}

/** GET /api/analysis/scenario → TableResponse */
export function apiScenario(): Promise<TableResponse> {
  return apiGet<TableResponse>("/api/analysis/scenario");
}

/** GET /api/analysis/whatif?symbol=&weight= → dict */
export function apiWhatif(symbol: string, weight: number): Promise<Record<string, unknown>> {
  const q = new URLSearchParams({ symbol, weight: String(weight) });
  return apiGet<Record<string, unknown>>(`/api/analysis/whatif?${q}`);
}

/** GET /api/analysis/attribution → TableResponse */
export function apiAttribution(): Promise<TableResponse> {
  return apiGet<TableResponse>("/api/analysis/attribution");
}
```

- [ ] **Step 3: Verify TypeScript compiles (no new errors)**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: zero lines of error output (warnings OK).

- [ ] **Step 4: Commit**

```powershell
git add web/src/lib/api.ts
git commit -m "feat(web): analysis API types + typed helpers (TASK-049)"
```

---

## Task 2: CandleChart component

**Files:**
- Create: `web/src/components/domain/CandleChart.tsx`

This component uses `lightweight-charts` candlestick series. It must be `"use client"` and only touch the DOM inside `useEffect`. Follow the exact same pattern as `EquityChart.tsx`.

- [ ] **Step 1: Create the component**

Create `web/src/components/domain/CandleChart.tsx`:

```typescript
// web/src/components/domain/CandleChart.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
  type IChartApi,
} from "lightweight-charts";
import { cn } from "@/lib/utils";
import { apiIntraday } from "@/lib/api";
import type { TableResponse } from "@/lib/api";

const SYMBOLS = [
  { label: "삼성전자", value: "005930" },
  { label: "SK하이닉스", value: "000660" },
  { label: "NAVER", value: "035420" },
  { label: "카카오", value: "035720" },
];

interface CandleChartProps {
  className?: string;
}

/**
 * CandleChart — lightweight-charts candlestick series.
 *
 * IMPORTANT: Must be imported via next/dynamic with ssr: false at the page level.
 * DOM access only happens inside useEffect.
 */
export function CandleChart({ className }: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [symbol, setSymbol] = useState(SYMBOLS[0].value);
  const [data, setData] = useState<TableResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch intraday data when symbol changes
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);
    apiIntraday(symbol, 1, 80)
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err);
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [symbol]);

  // Mount/update chart when data changes
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    // Destroy previous chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    if (!data || data.rows.length === 0) return;

    const chart = createChart(el, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#8B95A1",
      },
      grid: {
        vertLines: { color: "#DDE1E7" },
        horzLines: { color: "#DDE1E7" },
      },
      rightPriceScale: { borderColor: "#DDE1E7" },
      timeScale: { borderColor: "#DDE1E7", timeVisible: true },
      width: el.clientWidth,
      height: 280,
    });
    chartRef.current = chart;

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#F04452",
      downColor: "#3182F6",
      borderUpColor: "#F04452",
      borderDownColor: "#3182F6",
      wickUpColor: "#F04452",
      wickDownColor: "#3182F6",
    });

    // Map TableResponse rows to lightweight-charts candlestick format
    // Expected columns: time (or date), open, high, low, close
    const timeCol =
      data.columns.find((c) => c === "time" || c === "date" || c === "시간") ??
      data.columns[0];
    const openCol =
      data.columns.find((c) => c === "open" || c === "시가") ?? data.columns[1];
    const highCol =
      data.columns.find((c) => c === "high" || c === "고가") ?? data.columns[2];
    const lowCol =
      data.columns.find((c) => c === "low" || c === "저가") ?? data.columns[3];
    const closeCol =
      data.columns.find((c) => c === "close" || c === "종가") ?? data.columns[4];

    const candles = data.rows
      .map((row) => ({
        time: String(row[timeCol] ?? ""),
        open: Number(row[openCol] ?? 0),
        high: Number(row[highCol] ?? 0),
        low: Number(row[lowCol] ?? 0),
        close: Number(row[closeCol] ?? 0),
      }))
      .filter((c) => c.time.length > 0)
      .sort((a, b) => (a.time < b.time ? -1 : 1));

    if (candles.length > 0) {
      series.setData(candles as Parameters<typeof series.setData>[0]);
      chart.timeScale().fitContent();
    }

    const handleResize = () => {
      if (el && chartRef.current) {
        chartRef.current.applyOptions({ width: el.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data]);

  return (
    <div className={cn("space-y-3", className)} data-testid="candle-chart-section">
      {/* Symbol selector */}
      <div className="flex items-center gap-2">
        <label htmlFor="candle-symbol" className="text-sm font-medium text-muted-foreground">
          종목
        </label>
        <select
          id="candle-symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {SYMBOLS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label} ({s.value})
            </option>
          ))}
        </select>
      </div>

      {/* Chart area */}
      {error ? (
        <div
          role="alert"
          className="flex h-[280px] items-center justify-center rounded-xl border border-destructive/40 bg-destructive/10 text-sm text-destructive"
        >
          차트를 불러오지 못했습니다: {error.message}
        </div>
      ) : isLoading ? (
        <div
          className="h-[280px] animate-pulse rounded-xl bg-muted"
          aria-label="차트 로딩 중"
        />
      ) : (
        <div
          ref={containerRef}
          className="h-[280px] w-full overflow-hidden rounded-xl"
          aria-label="캔들차트"
          data-testid="candle-chart"
        />
      )}
    </div>
  );
}

export default CandleChart;
```

- [ ] **Step 2: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Commit**

```powershell
git add web/src/components/domain/CandleChart.tsx
git commit -m "feat(web): CandleChart — lightweight-charts candlestick, ssr:false (TASK-049)"
```

---

## Task 3: BacktestPanel component

**Files:**
- Create: `web/src/components/domain/BacktestPanel.tsx`

- [ ] **Step 1: Create BacktestPanel.tsx**

```typescript
// web/src/components/domain/BacktestPanel.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiBacktest, type BacktestResult } from "@/lib/api";
import { KpiCard } from "@/components/domain/KpiCard";
import { fmtPct } from "@/lib/format";

interface BacktestParams {
  symbol: string;
  start: string;
  end: string;
  fast: number;
  slow: number;
}

const DEFAULT_PARAMS: BacktestParams = {
  symbol: "005930",
  start: "2025-01-01",
  end: "2025-12-31",
  fast: 5,
  slow: 20,
};

/**
 * BacktestPanel — form + result KPIs for GET /api/analysis/backtest.
 * No fake data: result only shown after real fetch; errors shown visibly.
 */
export function BacktestPanel() {
  const [params, setParams] = useState<BacktestParams>(DEFAULT_PARAMS);
  const [submitted, setSubmitted] = useState<BacktestParams | null>(null);

  const query = useQuery<BacktestResult>({
    queryKey: ["analysis-backtest", submitted],
    queryFn: () => apiBacktest(submitted!),
    enabled: submitted !== null,
    retry: 1,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted({ ...params });
  }

  return (
    <div className="space-y-4" data-testid="backtest-panel">
      {/* Form */}
      <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <div className="flex flex-col gap-1">
          <label htmlFor="bt-symbol" className="text-xs font-medium text-muted-foreground">종목 코드</label>
          <input
            id="bt-symbol"
            type="text"
            value={params.symbol}
            onChange={(e) => setParams((p) => ({ ...p, symbol: e.target.value }))}
            placeholder="005930"
            className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="bt-start" className="text-xs font-medium text-muted-foreground">시작일</label>
          <input
            id="bt-start"
            type="date"
            value={params.start}
            onChange={(e) => setParams((p) => ({ ...p, start: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="bt-end" className="text-xs font-medium text-muted-foreground">종료일</label>
          <input
            id="bt-end"
            type="date"
            value={params.end}
            onChange={(e) => setParams((p) => ({ ...p, end: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="bt-fast" className="text-xs font-medium text-muted-foreground">단기 이동평균</label>
          <input
            id="bt-fast"
            type="number"
            min={1}
            value={params.fast}
            onChange={(e) => setParams((p) => ({ ...p, fast: Number(e.target.value) }))}
            className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="bt-slow" className="text-xs font-medium text-muted-foreground">장기 이동평균</label>
          <input
            id="bt-slow"
            type="number"
            min={1}
            value={params.slow}
            onChange={(e) => setParams((p) => ({ ...p, slow: Number(e.target.value) }))}
            className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="col-span-2 flex items-end sm:col-span-3 lg:col-span-5">
          <button
            type="submit"
            disabled={query.isFetching}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {query.isFetching ? "분석 중..." : "백테스트 실행"}
          </button>
        </div>
      </form>

      {/* Error */}
      {query.error && (
        <div
          role="alert"
          className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
        >
          백테스트 오류: {(query.error as Error).message}
        </div>
      )}

      {/* Loading skeleton */}
      {query.isFetching && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      )}

      {/* Results */}
      {query.data && !query.isFetching && (
        <div
          className="grid grid-cols-2 gap-3 sm:grid-cols-4"
          data-testid="backtest-result"
          aria-label="백테스트 결과"
        >
          <KpiCard
            label="총 수익률"
            value={fmtPct(query.data.total_return_pct)}
            delta={query.data.total_return_pct}
            deltaMode="pct"
          />
          <KpiCard
            label="승률"
            value={fmtPct(query.data.win_rate_pct)}
          />
          <KpiCard
            label="최대 낙폭"
            value={fmtPct(query.data.max_drawdown_pct)}
            delta={-Math.abs(query.data.max_drawdown_pct)}
            deltaMode="pct"
          />
          <KpiCard
            label="거래 횟수"
            value={String(query.data.trade_count)}
          />
        </div>
      )}
    </div>
  );
}

export default BacktestPanel;
```

- [ ] **Step 2: Check format.ts exports `fmtPct`**

```powershell
Select-String -Path "web\src\lib\format.ts" -Pattern "fmtPct"
```

Expected: at least one match showing `export function fmtPct` or `export const fmtPct`.

If `fmtPct` is missing, open `web/src/lib/format.ts` and add:
```typescript
export function fmtPct(value: number, decimals = 2): string {
  return `${value.toFixed(decimals)}%`;
}
```

- [ ] **Step 3: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 4: Commit**

```powershell
git add web/src/components/domain/BacktestPanel.tsx web/src/lib/format.ts
git commit -m "feat(web): BacktestPanel — form + KpiCard results (TASK-049)"
```

---

## Task 4: VarPanel component

**Files:**
- Create: `web/src/components/domain/VarPanel.tsx`

- [ ] **Step 1: Create VarPanel.tsx**

```typescript
// web/src/components/domain/VarPanel.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiVar, type SimulationResult } from "@/lib/api";
import { KpiCard } from "@/components/domain/KpiCard";
import { fmtWon, fmtPct } from "@/lib/format";

interface VarParams {
  horizon_days: number;
  n_simulations: number;
}

const DEFAULT_PARAMS: VarParams = { horizon_days: 10, n_simulations: 10000 };

/**
 * VarPanel — form + result KPIs for GET /api/analysis/var.
 * Shows `note` field when data is empty/placeholder. No fabrication.
 */
export function VarPanel() {
  const [params, setParams] = useState<VarParams>(DEFAULT_PARAMS);
  const [submitted, setSubmitted] = useState<VarParams | null>(null);

  const query = useQuery<SimulationResult>({
    queryKey: ["analysis-var", submitted],
    queryFn: () => apiVar(submitted!),
    enabled: submitted !== null,
    retry: 1,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted({ ...params });
  }

  return (
    <div className="space-y-4" data-testid="var-panel">
      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <label htmlFor="var-horizon" className="text-xs font-medium text-muted-foreground">
            보유 기간 (일)
          </label>
          <input
            id="var-horizon"
            type="number"
            min={1}
            value={params.horizon_days}
            onChange={(e) =>
              setParams((p) => ({ ...p, horizon_days: Number(e.target.value) }))
            }
            className="w-28 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="var-sims" className="text-xs font-medium text-muted-foreground">
            시뮬레이션 횟수
          </label>
          <input
            id="var-sims"
            type="number"
            min={100}
            step={100}
            value={params.n_simulations}
            onChange={(e) =>
              setParams((p) => ({ ...p, n_simulations: Number(e.target.value) }))
            }
            className="w-32 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          type="submit"
          disabled={query.isFetching}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {query.isFetching ? "계산 중..." : "VaR 계산"}
        </button>
      </form>

      {/* Error */}
      {query.error && (
        <div
          role="alert"
          className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
        >
          VaR 계산 오류: {(query.error as Error).message}
        </div>
      )}

      {/* Loading skeleton */}
      {query.isFetching && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      )}

      {/* Results */}
      {query.data && !query.isFetching && (
        <div className="space-y-3">
          {/* Note banner: show when backend signals data is empty */}
          {query.data.note && (
            <div
              role="status"
              className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800"
            >
              {query.data.note}
            </div>
          )}
          <div
            className="grid grid-cols-2 gap-3 sm:grid-cols-4"
            data-testid="var-result"
            aria-label="VaR 결과"
          >
            <KpiCard
              label="VaR 95% (원)"
              value={fmtWon(query.data.var_95)}
            />
            <KpiCard
              label="VaR 99% (원)"
              value={fmtWon(query.data.var_99)}
            />
            <KpiCard
              label="CVaR 95% (원)"
              value={fmtWon(query.data.cvar_95)}
            />
            <KpiCard
              label="최대 낙폭"
              value={fmtPct(query.data.max_drawdown_pct)}
              delta={-Math.abs(query.data.max_drawdown_pct)}
              deltaMode="pct"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default VarPanel;
```

- [ ] **Step 2: Verify `fmtWon` exists in format.ts**

```powershell
Select-String -Path "web\src\lib\format.ts" -Pattern "fmtWon"
```

Expected: at least one match. (It already exists from Phase 2 work.)

- [ ] **Step 3: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 4: Commit**

```powershell
git add web/src/components/domain/VarPanel.tsx
git commit -m "feat(web): VarPanel — VaR form + KpiCard results + note banner (TASK-049)"
```

---

## Task 5: ScenarioPanel component

**Files:**
- Create: `web/src/components/domain/ScenarioPanel.tsx`

- [ ] **Step 1: Create ScenarioPanel.tsx**

```typescript
// web/src/components/domain/ScenarioPanel.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiScenario, apiWhatif } from "@/lib/api";
import { DataTable } from "@/components/domain/DataTable";
import type { TableResponse } from "@/lib/api";

/**
 * ScenarioPanel — scenario table (GET /api/analysis/scenario) +
 * optional whatif input (GET /api/analysis/whatif).
 */
export function ScenarioPanel() {
  const scenarioQuery = useQuery<TableResponse>({
    queryKey: ["analysis-scenario"],
    queryFn: apiScenario,
    staleTime: 60_000,
  });

  // Whatif form
  const [wiSymbol, setWiSymbol] = useState("005930");
  const [wiWeight, setWiWeight] = useState(10);
  const [wiSubmitted, setWiSubmitted] = useState<{ symbol: string; weight: number } | null>(null);

  const whatifQuery = useQuery<Record<string, unknown>>({
    queryKey: ["analysis-whatif", wiSubmitted],
    queryFn: () => apiWhatif(wiSubmitted!.symbol, wiSubmitted!.weight),
    enabled: wiSubmitted !== null,
    retry: 1,
  });

  function handleWhatifSubmit(e: React.FormEvent) {
    e.preventDefault();
    setWiSubmitted({ symbol: wiSymbol, weight: wiWeight });
  }

  return (
    <div className="space-y-6" data-testid="scenario-panel">
      {/* Scenario table */}
      <section aria-label="시나리오 분석">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground">시나리오 분석</h3>
        <DataTable
          data={scenarioQuery.data}
          isLoading={scenarioQuery.isPending}
          error={scenarioQuery.error as Error | null}
          caption="시나리오별 포트폴리오 영향"
        />
      </section>

      {/* What-if section */}
      <section aria-label="가정 분석 (What-if)">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground">가정 분석 (What-if)</h3>
        <form onSubmit={handleWhatifSubmit} className="flex flex-wrap gap-3 items-end mb-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="wi-symbol" className="text-xs font-medium text-muted-foreground">
              종목 코드
            </label>
            <input
              id="wi-symbol"
              type="text"
              value={wiSymbol}
              onChange={(e) => setWiSymbol(e.target.value)}
              placeholder="005930"
              className="w-28 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="wi-weight" className="text-xs font-medium text-muted-foreground">
              비중 (%)
            </label>
            <input
              id="wi-weight"
              type="number"
              min={0}
              max={100}
              value={wiWeight}
              onChange={(e) => setWiWeight(Number(e.target.value))}
              className="w-20 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            disabled={whatifQuery.isFetching}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {whatifQuery.isFetching ? "계산 중..." : "가정 실행"}
          </button>
        </form>

        {whatifQuery.error && (
          <div
            role="alert"
            className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
          >
            What-if 오류: {(whatifQuery.error as Error).message}
          </div>
        )}

        {whatifQuery.data && !whatifQuery.isFetching && (
          <div
            className="rounded-xl border border-border bg-muted/20 p-4 text-sm"
            data-testid="whatif-result"
          >
            <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs text-foreground">
              {JSON.stringify(whatifQuery.data, null, 2)}
            </pre>
          </div>
        )}
      </section>
    </div>
  );
}

export default ScenarioPanel;
```

- [ ] **Step 2: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Commit**

```powershell
git add web/src/components/domain/ScenarioPanel.tsx
git commit -m "feat(web): ScenarioPanel — scenario DataTable + whatif input (TASK-049)"
```

---

## Task 6: AttributionSankey component

**Files:**
- Create: `web/src/components/domain/AttributionSankey.tsx`

This uses recharts `Sankey`. It must be `"use client"` and DOM-safe (no top-level DOM access; recharts is already safe as a React component, but we still mark it client-only for the dynamic import pattern used at page level).

**Note on recharts Sankey:** recharts v3 `Sankey` expects `data = { nodes: [{name}], links: [{source, target, value}] }`. We derive this from the attribution `TableResponse`. The attribution table is expected to have columns like `["from", "to", "value"]` or `["source", "target", "contribution"]`. If the actual column shape differs, we fall back to a readable bar chart using `BarChart` from recharts.

- [ ] **Step 1: Create AttributionSankey.tsx**

```typescript
// web/src/components/domain/AttributionSankey.tsx
"use client";

import {
  Sankey,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import { cn } from "@/lib/utils";
import type { TableResponse } from "@/lib/api";

const CHART_COLORS = [
  "#3182F6",
  "#F04452",
  "#34C759",
  "#FF9500",
  "#AF52DE",
  "#5AC8FA",
];

interface AttributionSankeyProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

interface SankeyData {
  nodes: { name: string }[];
  links: { source: number; target: number; value: number }[];
}

/**
 * Build Sankey node/link structure from a TableResponse.
 * Looks for columns named (source/from/기여원천) and (target/to/자산군) and (value/contribution/기여도).
 * Returns null if the table doesn't have enough structure for a Sankey.
 */
function buildSankeyData(table: TableResponse): SankeyData | null {
  const srcCol =
    table.columns.find(
      (c) => c === "source" || c === "from" || c === "기여원천" || c === "출처",
    ) ?? null;
  const tgtCol =
    table.columns.find(
      (c) => c === "target" || c === "to" || c === "자산군" || c === "대상",
    ) ?? null;
  const valCol =
    table.columns.find(
      (c) =>
        c === "value" ||
        c === "contribution" ||
        c === "기여도" ||
        c === "기여",
    ) ?? null;

  if (!srcCol || !tgtCol || !valCol) return null;

  const nodeNames: string[] = [];
  const addNode = (name: string): number => {
    const idx = nodeNames.indexOf(name);
    if (idx !== -1) return idx;
    nodeNames.push(name);
    return nodeNames.length - 1;
  };

  const links: { source: number; target: number; value: number }[] = [];
  for (const row of table.rows) {
    const src = String(row[srcCol] ?? "");
    const tgt = String(row[tgtCol] ?? "");
    const val = Math.abs(Number(row[valCol] ?? 0));
    if (src && tgt && val > 0) {
      links.push({ source: addNode(src), target: addNode(tgt), value: val });
    }
  }

  if (links.length === 0) return null;

  return { nodes: nodeNames.map((name) => ({ name })), links };
}

/**
 * AttributionSankey — recharts Sankey for attribution TableResponse.
 * Falls back to a horizontal BarChart when the table lacks source/target columns.
 *
 * IMPORTANT: Must be imported via next/dynamic with ssr: false at the page level.
 */
export function AttributionSankey({
  data,
  isLoading,
  error,
  className,
}: AttributionSankeyProps) {
  if (error) {
    return (
      <div
        role="alert"
        className={cn(
          "flex h-60 items-center justify-center rounded-xl border border-destructive/40 bg-destructive/10 text-sm text-destructive",
          className,
        )}
      >
        기여도 차트를 불러오지 못했습니다: {error.message}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className={cn("h-60 animate-pulse rounded-xl bg-muted", className)}
        aria-label="기여도 차트 로딩 중"
      />
    );
  }

  if (!data || data.rows.length === 0) {
    return (
      <div
        className={cn(
          "flex h-60 items-center justify-center rounded-xl border border-dashed border-border text-sm text-muted-foreground",
          className,
        )}
      >
        기여도 데이터 없음
      </div>
    );
  }

  const sankeyData = buildSankeyData(data);

  if (sankeyData) {
    // Sankey flow chart
    return (
      <div
        className={cn("h-60 w-full", className)}
        aria-label="자산 기여도 Sankey 차트"
        data-testid="attribution-sankey"
      >
        <ResponsiveContainer width="100%" height="100%">
          <Sankey
            data={sankeyData}
            nodePadding={10}
            nodeWidth={10}
            margin={{ top: 8, right: 120, bottom: 8, left: 8 }}
          >
            <Tooltip />
          </Sankey>
        </ResponsiveContainer>
      </div>
    );
  }

  // Fallback: bar chart using first numeric column
  const labelCol = data.columns[0];
  const valueCol =
    data.columns.find((c) => {
      const v = data.rows[0]?.[c];
      return c !== labelCol && typeof v === "number";
    }) ?? data.columns[1];

  const barData = data.rows.map((row) => ({
    name: String(row[labelCol] ?? ""),
    value: Number(row[valueCol] ?? 0),
  }));

  return (
    <div
      className={cn("h-60 w-full", className)}
      aria-label="자산 기여도 차트"
      data-testid="attribution-sankey"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={barData} layout="vertical" margin={{ left: 80, right: 20 }}>
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 11 }}
            width={76}
          />
          <Tooltip />
          <Bar dataKey="value">
            {barData.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AttributionSankey;
```

- [ ] **Step 2: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Commit**

```powershell
git add web/src/components/domain/AttributionSankey.tsx
git commit -m "feat(web): AttributionSankey — recharts Sankey + bar fallback (TASK-049)"
```

---

## Task 7: Replace /analysis page

**Files:**
- Modify: `web/src/app/analysis/page.tsx`

The current placeholder renders an `EmptyState`. Replace it with the full composed page.

- [ ] **Step 1: Overwrite analysis/page.tsx**

```typescript
// web/src/app/analysis/page.tsx
"use client";

import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { apiAttribution, type TableResponse } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";

// ── Client-only chart components (ssr:false — DOM access) ─────────────────
const CandleChart = dynamic(
  () =>
    import("@/components/domain/CandleChart").then((m) => m.CandleChart),
  {
    ssr: false,
    loading: () => (
      <div className="h-[280px] animate-pulse rounded-xl bg-muted" />
    ),
  },
);

const AttributionSankey = dynamic(
  () =>
    import("@/components/domain/AttributionSankey").then(
      (m) => m.AttributionSankey,
    ),
  {
    ssr: false,
    loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" />,
  },
);

// ── Server-compatible components (no DOM needed at top-level) ─────────────
// BacktestPanel, VarPanel, ScenarioPanel are "use client" but don't need
// ssr:false — recharts/form inputs are safe during SSR as static HTML.
// However, to keep the pattern consistent and avoid any subtle recharts issue
// we load them lazily too.
const BacktestPanel = dynamic(
  () =>
    import("@/components/domain/BacktestPanel").then((m) => m.BacktestPanel),
  { ssr: false },
);

const VarPanel = dynamic(
  () => import("@/components/domain/VarPanel").then((m) => m.VarPanel),
  { ssr: false },
);

const ScenarioPanel = dynamic(
  () =>
    import("@/components/domain/ScenarioPanel").then((m) => m.ScenarioPanel),
  { ssr: false },
);

export default function AnalysisPage() {
  const attributionQuery = useQuery<TableResponse>({
    queryKey: ["analysis-attribution"],
    queryFn: apiAttribution,
    staleTime: 60_000,
  });

  return (
    <AppShell>
      <div className="space-y-8">
        <h1 className="text-lg font-semibold">분석</h1>

        {/* ── 1. 캔들차트 ─────────────────────────────────────────────── */}
        <section aria-label="캔들차트">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            분봉 차트
          </h2>
          <CandleChart />
        </section>

        {/* ── 2. 백테스트 ─────────────────────────────────────────────── */}
        <section aria-label="백테스트" data-testid="backtest-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            백테스트
          </h2>
          <BacktestPanel />
        </section>

        {/* ── 3. VaR ──────────────────────────────────────────────────── */}
        <section aria-label="VaR 분석" data-testid="var-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            VaR (Value at Risk)
          </h2>
          <VarPanel />
        </section>

        {/* ── 4. 시나리오 ─────────────────────────────────────────────── */}
        <section aria-label="시나리오 분석" data-testid="scenario-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            시나리오 / What-if
          </h2>
          <ScenarioPanel />
        </section>

        {/* ── 5. 기여도 (Sankey) ──────────────────────────────────────── */}
        <section aria-label="기여도 분석">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            기여도 (Attribution)
          </h2>
          <AttributionSankey
            data={attributionQuery.data}
            isLoading={attributionQuery.isPending}
            error={attributionQuery.error as Error | null}
          />
        </section>
      </div>
    </AppShell>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

```powershell
cd web && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Verify lint**

```powershell
cd web && npm run lint 2>&1 | tail -20
```

Expected: no errors (warnings about unused imports are OK only if they don't block).

- [ ] **Step 4: Verify build succeeds**

```powershell
cd web && npm run build 2>&1 | tail -30
```

Expected: `✓ Compiled successfully` or similar. No type errors, no "Module not found" errors.

- [ ] **Step 5: Commit**

```powershell
git add web/src/app/analysis/page.tsx
git commit -m "feat(web): /analysis page — CandleChart/백테스트/VaR/시나리오/Sankey (TASK-049)"
```

---

## Task 8: Playwright E2E spec — analysis.spec.ts

**Files:**
- Create: `web/e2e/analysis.spec.ts`

Follows the exact same LIFO mock pattern as the existing phase4.spec.ts. Mocks all analysis endpoints. Does NOT start a real backend.

- [ ] **Step 1: Create web/e2e/analysis.spec.ts**

```typescript
// web/e2e/analysis.spec.ts
import { test, expect, type Page } from "@playwright/test";

// ── Fixtures ──────────────────────────────────────────────────────────────

const CSRF_TOKEN = "test-csrf-token-phase5";

const OWNER_SESSION = {
  role: "owner",
  username: "admin",
  data_source: "live",
  csrf_token: CSRF_TOKEN,
};

const ENGINE_STATUS = {
  env: "paper",
  auto_trading_enabled: false,
  kill_switch_active: false,
  circuit_breaker: {
    triggered: false,
    threshold_pct: 5,
    consecutive_failures: 0,
    today_pnl: 0,
  },
};

const EMPTY_TABLE = { columns: [], rows: [] };

// OHLC intraday mock — lightweight-charts candlestick format
// time column must be ISO or YYYY-MM-DD strings
const INTRADAY_OHLC = {
  columns: ["time", "open", "high", "low", "close", "volume"],
  rows: [
    { time: "2026-06-12 09:00", open: 74000, high: 74500, low: 73800, close: 74200, volume: 12000 },
    { time: "2026-06-12 09:01", open: 74200, high: 74800, low: 74100, close: 74600, volume: 8000 },
    { time: "2026-06-12 09:02", open: 74600, high: 75000, low: 74400, close: 74900, volume: 9500 },
  ],
};

const BACKTEST_RESULT = {
  symbol: "005930",
  strategy: "MA Crossover (5/20)",
  start: "2025-01-01",
  end: "2025-12-31",
  total_return_pct: 15.42,
  trade_count: 12,
  win_rate_pct: 66.67,
  max_drawdown_pct: 8.21,
};

const VAR_RESULT = {
  total_value: 12345678,
  n_simulations: 10000,
  horizon_days: 10,
  var_95: 450000,
  var_99: 680000,
  cvar_95: 520000,
  max_drawdown_pct: 12.5,
};

const VAR_RESULT_WITH_NOTE = {
  ...VAR_RESULT,
  note: "포트폴리오가 비어있어 시뮬레이션 결과가 제한적입니다.",
};

const SCENARIO_TABLE = {
  columns: ["시나리오", "영향 (%)", "비고"],
  rows: [
    { "시나리오": "금리 +1%p", "영향 (%)": -3.2, "비고": "채권 비중 영향" },
    { "시나리오": "주가 -20%", "영향 (%)": -15.8, "비고": "주식 비중 영향" },
  ],
};

const ATTRIBUTION_TABLE = {
  columns: ["source", "target", "value"],
  rows: [
    { source: "국내주식", target: "총수익", value: 8.5 },
    { source: "채권", target: "총수익", value: 2.1 },
    { source: "현금", target: "총수익", value: 0.3 },
  ],
};

// ── Helpers ────────────────────────────────────────────────────────────────

async function mockBackground(page: Page) {
  // Catch-all: GET /api/** → empty table (lowest LIFO priority)
  await page.route(/\/api\//, (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(EMPTY_TABLE),
      });
    }
    return route.continue();
  });

  // Engine status
  await page.route(/\/api\/engine\/status/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENGINE_STATUS),
    }),
  );

  // Auth me
  await page.route(/\/api\/auth\/me/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  // Intraday OHLC
  await page.route(/\/api\/market\/intraday/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(INTRADAY_OHLC),
    }),
  );

  // Backtest
  await page.route(/\/api\/analysis\/backtest/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(BACKTEST_RESULT),
    }),
  );

  // VaR
  await page.route(/\/api\/analysis\/var/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(VAR_RESULT),
    }),
  );

  // Scenario
  await page.route(/\/api\/analysis\/scenario/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(SCENARIO_TABLE),
    }),
  );

  // What-if
  await page.route(/\/api\/analysis\/whatif/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ expected_return_pct: 1.23, risk_delta_pct: 0.45 }),
    }),
  );

  // Attribution
  await page.route(/\/api\/analysis\/attribution/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ATTRIBUTION_TABLE),
    }),
  );
}

async function loginAsOwner(page: Page) {
  await page.route(/\/api\/auth\/login/, (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(OWNER_SESSION),
    }),
  );

  await page.goto("/login");
  await page.getByLabel("아이디").fill("admin");
  await page.getByLabel("비밀번호").fill("secret");
  await page.getByRole("button", { name: /^로그인$/ }).click();
  await expect(page).toHaveURL(/\/home/, { timeout: 15_000 });
}

// ── Tests ─────────────────────────────────────────────────────────────────

test.describe("Phase 5 — /analysis page", () => {
  test("renders /analysis with AppShell navigation", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Page heading
    await expect(
      page.getByRole("heading", { name: "분석", exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // AppShell nav
    await expect(page.getByRole("navigation")).toBeVisible();
  });

  test("candle chart container appears after intraday fetch", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // The candle-chart-section wrapper appears (symbol selector + chart)
    await expect(
      page.locator('[data-testid="candle-chart-section"]'),
    ).toBeVisible({ timeout: 10_000 });

    // The actual chart div appears once data loads (may take a moment for dynamic import)
    await expect(
      page.locator('[data-testid="candle-chart"]'),
    ).toBeVisible({ timeout: 15_000 });
  });

  test("backtest form submits and shows result KPIs", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Wait for backtest panel to appear
    await expect(page.locator('[data-testid="backtest-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    // Click submit
    await page.getByRole("button", { name: "백테스트 실행" }).click();

    // Result KPIs appear
    await expect(
      page.locator('[data-testid="backtest-result"]'),
    ).toBeVisible({ timeout: 10_000 });

    // Check specific KPI values appear in the page
    await expect(page.getByText(/15.42/)).toBeVisible({ timeout: 5_000 });
  });

  test("VaR form submits and shows VaR result", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Wait for var panel
    await expect(page.locator('[data-testid="var-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    // Submit
    await page.getByRole("button", { name: "VaR 계산" }).click();

    // Result appears
    await expect(page.locator('[data-testid="var-result"]')).toBeVisible({
      timeout: 10_000,
    });
  });

  test("VaR note banner shown when note field present", async ({ page }) => {
    await mockBackground(page);

    // Override VaR route with note version (registered AFTER mockBackground — LIFO priority)
    await page.route(/\/api\/analysis\/var/, (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(VAR_RESULT_WITH_NOTE),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/analysis");

    await expect(page.locator('[data-testid="var-panel"]')).toBeVisible({
      timeout: 10_000,
    });
    await page.getByRole("button", { name: "VaR 계산" }).click();

    await expect(
      page.getByText("포트폴리오가 비어있어 시뮬레이션 결과가 제한적입니다."),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("scenario table renders with Korean column headers", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Scenario DataTable should show the column "시나리오"
    await expect(
      page.getByRole("columnheader", { name: "시나리오" }),
    ).toBeVisible({ timeout: 10_000 });

    // And one data row
    await expect(page.getByRole("cell", { name: "금리 +1%p" })).toBeVisible({
      timeout: 5_000,
    });
  });

  test("attribution Sankey container appears", async ({ page }) => {
    await mockBackground(page);
    await loginAsOwner(page);

    await page.goto("/analysis");

    // Attribution chart (Sankey or bar fallback) container appears
    await expect(
      page.locator('[data-testid="attribution-sankey"]'),
    ).toBeVisible({ timeout: 15_000 });
  });

  test("backtest API error shows visible error message", async ({ page }) => {
    await mockBackground(page);

    // Override backtest with error
    await page.route(/\/api\/analysis\/backtest/, (route) =>
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal server error" }),
      }),
    );

    await loginAsOwner(page);
    await page.goto("/analysis");

    await expect(page.locator('[data-testid="backtest-panel"]')).toBeVisible({
      timeout: 10_000,
    });

    await page.getByRole("button", { name: "백테스트 실행" }).click();

    // Error alert appears
    await expect(
      page.getByRole("alert").filter({ hasText: /백테스트 오류/ }),
    ).toBeVisible({ timeout: 10_000 });
  });
});
```

- [ ] **Step 2: Run lint to verify spec is valid TypeScript**

```powershell
cd web && npm run lint 2>&1 | tail -20
```

Expected: no errors.

- [ ] **Step 3: Commit the spec**

```powershell
git add web/e2e/analysis.spec.ts
git commit -m "test(web): Playwright E2E spec for /analysis Phase 5 (TASK-049)"
```

---

## Task 9: Full production gate — lint + build + E2E (×2)

This is the HARD GATE. Do not mark this task done until both runs are fully green.

**Files:** None created — verification only.

- [ ] **Step 1: Lint**

```powershell
cd web && npm run lint 2>&1
```

Expected: exit code 0, no `error` lines.

- [ ] **Step 2: Production build**

```powershell
cd web && npm run build 2>&1
```

Expected: build succeeds (no type errors, no "Module not found", no SSR-unsafe errors like `window is not defined`).

If you see `window is not defined` or `document is not defined`, it means a chart component is being executed at SSR time. Check that:
1. The component file has `"use client"` at the top.
2. At the import site (`analysis/page.tsx`), it uses `dynamic(..., { ssr: false })`.
3. DOM API calls (`createChart`, `window`, `document`) only appear inside `useEffect`.

- [ ] **Step 3: E2E full suite run 1**

```powershell
cd web && $env:CI="1"; npx playwright test 2>&1
```

Expected: all test files pass — login, dashboard, phase3, phase4, analysis. Report the per-file counts:
```
login.spec.ts     — N passed
dashboard.spec.ts — N passed
phase3.spec.ts    — N passed
phase4.spec.ts    — N passed
analysis.spec.ts  — N passed
```

- [ ] **Step 4: E2E full suite run 2 (non-flaky check)**

```powershell
cd web && $env:CI="1"; npx playwright test 2>&1
```

Expected: same counts as Run 1. If any test is flaky (passes run 1, fails run 2), investigate before proceeding.

- [ ] **Step 5: Final commit**

If all gates pass:

```powershell
git add -p  # verify nothing staged from node_modules or reports
git status  # confirm only web/src and web/e2e files
git commit -m "feat(web): Phase5 분석 화면 — CandleChart/백테스트/VaR/시나리오/Sankey (TASK-049 frontend)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

**Spec coverage:**

| Requirement | Task covering it |
|-------------|-----------------|
| CandleChart from `/api/market/intraday` | Task 2 (CandleChart.tsx) |
| Symbol selector for CandleChart | Task 2 |
| Backtest form + KpiCards | Task 3 (BacktestPanel.tsx) |
| VaR form + KpiCards + note field | Task 4 (VarPanel.tsx) |
| Scenario DataTable | Task 5 (ScenarioPanel.tsx) |
| Whatif input | Task 5 |
| Sankey/flow chart from attribution | Task 6 (AttributionSankey.tsx) |
| /analysis page with all sections | Task 7 |
| `ssr: false` dynamic imports | Task 7 |
| DOM-only in useEffect | Task 2 (CandleChart), Task 6 (recharts is SSR-safe natively) |
| No fake data; errors visible | All panels: error state shown; no hardcoded return values |
| Loading → skeletons | All panels + CandleChart |
| Playwright spec with mocked endpoints | Task 8 |
| Login as guest mock pattern | Task 8 (loginAsOwner follows same pattern) |
| Candle chart container assertion | Task 8 |
| Backtest form submit + result KPI | Task 8 |
| VaR result assertion | Task 8 |
| Scenario table render | Task 8 |
| Existing specs not broken | Task 9 (full suite run) |
| `npm run lint` clean | Task 9 |
| `npm run build` green | Task 9 |
| `CI=1 npx playwright test` ×2 | Task 9 |
| Commit to branch | Task 9 |
| No node_modules/reports staged | Task 9 |
| Commit message format | Task 9 |
| Trailer `Co-Authored-By: Claude Fable 5` | Task 9 |

**Placeholder scan:** No TBD, TODO, "implement later", or "similar to Task N" patterns found. All code blocks are complete.

**Type consistency check:**
- `apiIntraday` returns `Promise<TableResponse>` → CandleChart consumes `TableResponse` ✓
- `apiBacktest` returns `Promise<BacktestResult>` → BacktestPanel uses `BacktestResult` ✓
- `apiVar` returns `Promise<SimulationResult>` → VarPanel uses `SimulationResult` ✓
- `apiScenario`/`apiAttribution` return `Promise<TableResponse>` → consumed as `TableResponse` ✓
- `KpiCard` props (`label`, `value`, `delta`, `deltaMode`) match KpiCard.tsx definition ✓
- `DataTable` props (`data`, `isLoading`, `error`, `caption`) match DataTable.tsx definition ✓
- `AttributionSankey` props (`data`, `isLoading`, `error`, `className`) defined consistently ✓
- `data-testid` values used in spec match values in component implementations ✓
