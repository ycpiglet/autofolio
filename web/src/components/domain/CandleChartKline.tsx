"use client";

import { useEffect, useMemo, useRef } from "react";

import { cn } from "@/lib/utils";
import {
  KR_CANDLE_COLORS,
  toKlineData,
  type Candle,
} from "../../lib/candle-series";

interface CandleChartKlineProps {
  candles: Candle[];
  height?: number;
  className?: string;
}

/**
 * CandleChartKline — self-hosted KLineCharts (v10) candlestick chart
 * (net-new alternative to CandleChart.tsx, which uses lightweight-charts).
 *
 * KLineCharts touches `window` at MODULE-IMPORT time (not just on init), so a
 * static top-level `import "klinecharts"` would crash during SSR/prerender.
 * The idiomatic Next 16 fix used here keeps this a plain "use client" component
 * and dynamically `import("klinecharts")` INSIDE the mount effect — the library
 * is therefore only evaluated in the browser, while the container/placeholder
 * shell still server-renders (no layout shift, no SSR canvas crash).
 *
 * Candles are colored by KR convention (up=빨강 #F04452, down=파랑 #3182F6,
 * 보합=회색 #8B95A1), the opposite of KLineCharts' Western green/red default,
 * by applying KR_CANDLE_COLORS to styles.candle.bar.
 *
 * KLineCharts auto-resizes to its container, so the container just needs the
 * given height + full width. Re-applies data whenever `candles` changes.
 */
export function CandleChartKline({
  candles,
  height = 320,
  className,
}: CandleChartKlineProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Stable KLineData for the effect's dependency (recomputed when candles change).
  const data = useMemo(() => toKlineData(candles), [candles]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el || data.length === 0) return;

    let disposed = false;
    // chart is created asynchronously (klinecharts is dynamically imported), so
    // hold the dispose fn in a ref-like closure variable for cleanup.
    let cleanup: (() => void) | undefined;

    // Dynamic import keeps klinecharts out of the SSR bundle eval (it reads
    // `window` at import time). Only runs in the browser.
    void import("klinecharts").then(({ init, dispose }) => {
      // The effect may have been torn down before the import resolved.
      if (disposed) return;

      const chart = init(el, {
        styles: {
          candle: {
            bar: {
              // KR convention: up=red, down=blue, flat=gray (incl. borders/wicks).
              upColor: KR_CANDLE_COLORS.up,
              downColor: KR_CANDLE_COLORS.down,
              noChangeColor: KR_CANDLE_COLORS.noChange,
              upBorderColor: KR_CANDLE_COLORS.up,
              downBorderColor: KR_CANDLE_COLORS.down,
              noChangeBorderColor: KR_CANDLE_COLORS.noChange,
              upWickColor: KR_CANDLE_COLORS.up,
              downWickColor: KR_CANDLE_COLORS.down,
              noChangeWickColor: KR_CANDLE_COLORS.noChange,
            },
          },
        },
      });
      if (!chart) return;

      // v10 loads data via a DataLoader (there is no applyNewData). For a static
      // in-memory series, supply all bars on the "init" load and report no more
      // data in either direction so KLineCharts does not request more pages.
      chart.setSymbol({ ticker: "CANDLE", pricePrecision: 2, volumePrecision: 0 });
      chart.setPeriod({ type: "day", span: 1 });
      chart.setDataLoader({
        getBars: ({ type, callback }) => {
          callback(type === "init" ? data : [], false);
        },
      });

      cleanup = () => dispose(el);
    });

    return () => {
      disposed = true;
      cleanup?.();
    };
  }, [data]);

  if (candles.length === 0) {
    return (
      <div
        className={cn(
          "flex w-full items-center justify-center rounded-xl bg-muted/40 text-sm text-muted-foreground",
          className,
        )}
        style={{ height }}
        aria-label="캔들차트 (데이터 없음)"
        data-testid="candle-chart-kline-empty"
      >
        표시할 데이터가 없습니다
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("w-full rounded-xl overflow-hidden", className)}
      style={{ height }}
      aria-label="캔들차트"
      data-testid="candle-chart-kline"
    />
  );
}

export default CandleChartKline;
