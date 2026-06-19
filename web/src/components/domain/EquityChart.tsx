// web/src/components/domain/EquityChart.tsx
"use client";

import { cn } from "@/lib/utils";
import type { TableResponse } from "@/lib/api";
import { tableToEquityPoints } from "@/lib/equity-table";
import { EquityChartUplot } from "./EquityChartUplot";

interface EquityChartProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

/**
 * EquityChart — asset-curve chart for the home/portfolio surfaces.
 *
 * Renders via the self-hosted uPlot engine (EquityChartUplot) internally; the
 * line/area is colored by the period's sign per KR convention (up=빨강, down=
 * 파랑, flat=회색). Public API and error/loading states are unchanged from the
 * prior lightweight-charts implementation; the accessible label now comes from
 * EquityChartUplot (the success wrapper keeps data-testid="equity-chart"), so
 * importing pages keep working untouched.
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
    <div data-testid="equity-chart">
      <EquityChartUplot
        points={tableToEquityPoints(data)}
        height={240}
        className={cn("h-60 w-full rounded-xl overflow-visible", className)}
      />
    </div>
  );
}

export default EquityChart;
