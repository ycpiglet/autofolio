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
import { compactChartSeriesPalette } from "@/lib/design-tokens";

const CHART_COLORS = compactChartSeriesPalette;

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
