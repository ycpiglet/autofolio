// web/src/components/domain/CandleChart.tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
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

  const { data, isPending, error } = useQuery<TableResponse>({
    queryKey: ["market-intraday", symbol],
    queryFn: () => apiIntraday(symbol, 1, 80),
    staleTime: 30_000,
  });

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
          차트를 불러오지 못했습니다: {(error as Error).message}
        </div>
      ) : isPending ? (
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
