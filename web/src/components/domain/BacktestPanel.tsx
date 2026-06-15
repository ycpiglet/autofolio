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
