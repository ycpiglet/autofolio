// web/src/components/domain/HoldingsTable.tsx
"use client";

import { cn } from "@/lib/utils";
import { pnlColorClass } from "@/lib/format";
import type { TableResponse } from "@/lib/api";

const PNL_COLUMN_KEYWORDS = ["손익", "수익률", "pnl", "return"];

function isPnlColumn(col: string): boolean {
  const lower = col.toLowerCase();
  return PNL_COLUMN_KEYWORDS.some((kw) => lower.includes(kw));
}

interface CellProps {
  col: string;
  value: unknown;
}

function Cell({ col, value }: CellProps) {
  if (isPnlColumn(col)) {
    const num = typeof value === "number" ? value : parseFloat(String(value ?? ""));
    if (!isNaN(num)) {
      const isPercent = col.includes("%") || col.includes("률");
      const display = isPercent
        ? `${num > 0 ? "+" : ""}${num.toFixed(2)}%`
        : `${num > 0 ? "+" : ""}${Math.round(num).toLocaleString("ko-KR")}`;
      return (
        <span
          className={cn("font-mono tabular-nums", pnlColorClass(num))}
          aria-label={`${col}: ${display}`}
        >
          {display}
        </span>
      );
    }
  }
  return <>{String(value ?? "")}</>;
}

interface HoldingsTableProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  maxRows?: number;
  className?: string;
}

/**
 * HoldingsTable — holdings TableResponse renderer with PnL columns colored.
 * Wraps the same table logic as DataTable but with domain-aware cell rendering.
 */
export function HoldingsTable({
  data,
  isLoading,
  error,
  maxRows,
  className,
}: HoldingsTableProps) {
  if (error) {
    return (
      <div
        role="alert"
        className="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive"
      >
        <strong>보유 종목을 불러오지 못했습니다.</strong>
        <p className="mt-1 text-xs opacity-80">{error.message}</p>
      </div>
    );
  }

  const columns = data?.columns ?? [];
  const rows = data
    ? maxRows !== undefined
      ? data.rows.slice(0, maxRows)
      : data.rows
    : [];
  const colCount = columns.length || 5;

  function SkeletonRow() {
    return (
      <tr aria-hidden>
        {Array.from({ length: colCount }).map((_, i) => (
          <td key={i} className="px-3 py-2">
            <div className="h-4 animate-pulse rounded bg-muted" />
          </td>
        ))}
      </tr>
    );
  }

  return (
    <div
      className={cn("overflow-x-auto rounded-xl border border-border", className)}
    >
      <table className="w-full text-sm" aria-label="보유 종목">
        <thead>
          <tr className="border-b border-border bg-muted/40">
            {isLoading
              ? Array.from({ length: colCount }).map((_, i) => (
                  <th key={i} className="px-3 py-2 text-left font-medium text-muted-foreground">
                    <div className="h-3 w-16 animate-pulse rounded bg-muted" />
                  </th>
                ))
              : columns.map((col) => (
                  <th
                    key={col}
                    scope="col"
                    className="px-3 py-2 text-left font-medium text-muted-foreground"
                  >
                    {col}
                  </th>
                ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
          ) : rows.length === 0 ? (
            <tr>
              <td
                colSpan={colCount}
                className="px-3 py-8 text-center text-sm text-muted-foreground"
              >
                보유 종목 없음
              </td>
            </tr>
          ) : (
            rows.map((row, ri) => (
              <tr
                key={ri}
                className="border-b border-border last:border-0 hover:bg-muted/20"
              >
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2 text-foreground">
                    <Cell col={col} value={row[col]} />
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
