// web/src/components/domain/AllocationChart.tsx
"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import type { TableResponse } from "@/lib/api";
import { chartSeriesPalette } from "@/lib/design-tokens";

const CHART_COLORS = chartSeriesPalette;

interface AllocationChartProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  className?: string;
}

/**
 * AllocationChart — recharts donut chart for allocation-gap data.
 *
 * IMPORTANT: Must be imported via next/dynamic with ssr: false at the page level.
 *
 * Expects TableResponse with at least 2 columns:
 *   - Column 0: category name (자산군, 섹터, etc.)
 *   - Column 1 (or column named "비중" / "현재비중" / "목표비중"): numeric weight
 */
export function AllocationChart({
  data,
  isLoading,
  error,
  className,
}: AllocationChartProps) {
  if (error) {
    return (
      <div
        role="alert"
        className={cn(
          "flex h-60 items-center justify-center rounded-xl border border-destructive/40 bg-destructive/10 text-sm text-destructive",
          className,
        )}
      >
        배분 차트를 불러오지 못했습니다: {error.message}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className={cn("h-60 animate-pulse rounded-xl bg-muted", className)}
        aria-label="배분 차트 로딩 중"
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
        배분 데이터 없음
      </div>
    );
  }

  // Determine name column (first col) and value column (prefer current weight).
  const nameCol = data.columns[0];
  const valueCol =
    data.columns.find((c) => c.includes("현재")) ??
    data.columns.find((c) => c.includes("비중") || c.toLowerCase().includes("weight")) ??
    data.columns[1] ??
    data.columns[0];

  const chartData = data.rows
    .map((row) => ({
      name: String(row[nameCol] ?? ""),
      value: Math.abs(Number(row[valueCol] ?? 0)),
    }))
    .filter((d) => d.value > 0);

  return (
    <div
      className={cn("h-60 w-full", className)}
      aria-label="자산 배분 차트"
      data-testid="allocation-chart"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius="55%"
            outerRadius="75%"
            dataKey="value"
            nameKey="name"
            paddingAngle={2}
          >
            {chartData.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: unknown) => [`${(value as number).toFixed(1)}%`, "비중"]}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AllocationChart;
