// web/src/components/domain/EquityChart.tsx
"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, type IChartApi } from "lightweight-charts";
import { cn } from "@/lib/utils";
import type { TableResponse } from "@/lib/api";

interface EquityChartProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

/**
 * EquityChart — lightweight-charts area chart for asset curve.
 *
 * IMPORTANT: Must be imported via next/dynamic with ssr: false at the page level.
 * This file is "use client" but lightweight-charts still needs real DOM in useEffect.
 *
 * Expects TableResponse with columns: ["date", "자산"] (or superset).
 * date: "YYYY-MM-DD" string, 자산: numeric value.
 */
export function EquityChart({
  data,
  isLoading,
  error,
  className,
}: EquityChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    // Create chart
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
      timeScale: { borderColor: "#DDE1E7" },
      width: el.clientWidth,
      height: 240,
    });
    chartRef.current = chart;

    const series = chart.addAreaSeries({
      lineColor: "#3182F6",
      topColor: "rgba(49, 130, 246, 0.3)",
      bottomColor: "rgba(49, 130, 246, 0.0)",
      lineWidth: 2,
    });

    if (data) {
      const dateCol = "date";
      const valueCol = "자산";
      const points = data.rows
        .map((row) => ({
          time: String(row[dateCol] ?? ""),
          value: Number(row[valueCol] ?? 0),
        }))
        .filter((p) => p.time.length > 0)
        .sort((a, b) => (a.time < b.time ? -1 : 1));

      if (points.length > 0) {
        // lightweight-charts requires time as string "YYYY-MM-DD" or UTC seconds
        series.setData(points as Parameters<typeof series.setData>[0]);
        chart.timeScale().fitContent();
      }
    }

    const handleResize = () => {
      if (el) chart.applyOptions({ width: el.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [data]);

  if (error) {
    return (
      <div
        role="alert"
        className={cn(
          "flex h-60 items-center justify-center rounded-xl border border-destructive/40 bg-destructive/10 text-sm text-destructive",
          className,
        )}
      >
        차트를 불러오지 못했습니다: {error.message}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className={cn(
          "h-60 animate-pulse rounded-xl bg-muted",
          className,
        )}
        aria-label="차트 로딩 중"
      />
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn("h-60 w-full rounded-xl overflow-hidden", className)}
      aria-label="자산 추이 차트"
      data-testid="equity-chart"
    />
  );
}

export default EquityChart;
