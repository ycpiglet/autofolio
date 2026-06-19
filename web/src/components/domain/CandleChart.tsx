// web/src/components/domain/CandleChart.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import { apiIntraday } from "@/lib/api";
import type { TableResponse } from "@/lib/api";
import { tableToCandles } from "@/lib/candle-table";
import { CandleChartKline } from "./CandleChartKline";

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
 * CandleChart — candlestick chart rendered via the self-hosted KLineCharts
 * engine (CandleChartKline), with KR candle colors (up=red #F04452 /
 * down=blue #3182F6). Owns the symbol selector + intraday data query; the
 * pure TableResponse→Candle[] mapping lives in lib/candle-table.ts.
 *
 * Still imported via next/dynamic with ssr: false at the page level —
 * CandleChartKline dynamically imports klinecharts (which touches `window`
 * at import time) only in the browser.
 */
export function CandleChart({ className }: CandleChartProps) {
  const [symbol, setSymbol] = useState(SYMBOLS[0].value);

  const { data, isPending, error } = useQuery<TableResponse>({
    queryKey: ["market-intraday", symbol],
    queryFn: () => apiIntraday(symbol, 1, 80),
    staleTime: 30_000,
  });

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
          차트를 불러오지 못했습니다: {(error as Error).message}
        </div>
      ) : isPending ? (
        <div
          className="h-[280px] animate-pulse rounded-xl bg-muted"
          aria-label="차트 로딩 중"
        />
      ) : (
        <div aria-label="캔들차트" data-testid="candle-chart">
          <CandleChartKline
            candles={tableToCandles(data)}
            height={280}
            className="h-[280px] w-full overflow-visible rounded-xl"
          />
        </div>
      )}
    </div>
  );
}

export default CandleChart;
