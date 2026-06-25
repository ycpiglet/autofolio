// web/src/components/domain/HoldingsTable.tsx
"use client";

import { cn } from "@/lib/utils";
import { pnlColorClass } from "@/lib/format";
import type { TableResponse } from "@/lib/api";
import { ErrorState as ErrorIllustration } from "@/components/ui/illustrations/ErrorState";

const PNL_COLUMN_KEYWORDS = ["손익", "수익률", "pnl", "return"];

function isPnlColumn(col: string): boolean {
  const lower = col.toLowerCase();
  return PNL_COLUMN_KEYWORDS.some((kw) => lower.includes(kw));
}

interface CellProps {
  col: string;
  value: unknown;
  pnlClassName?: (value: number) => string;
  emphasizeValues?: boolean;
}

const NUMERIC_COLUMN_KEYWORDS = ["수량", "평단", "현재가", "평가금액", "비중", "배당", "price", "amount", "weight"];

function isNumericColumn(col: string): boolean {
  const lower = col.toLowerCase();
  return NUMERIC_COLUMN_KEYWORDS.some((kw) => lower.includes(kw));
}

function SkeletonRow({ colCount }: { colCount: number }) {
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

function Cell({ col, value, pnlClassName, emphasizeValues = false }: CellProps) {
  if (isPnlColumn(col)) {
    const num = typeof value === "number" ? value : parseFloat(String(value ?? ""));
    if (!isNaN(num)) {
      const isPercent = col.includes("%") || col.includes("률");
      const display = isPercent
        ? `${num > 0 ? "+" : ""}${num.toFixed(2)}%`
        : `${num > 0 ? "+" : ""}${Math.round(num).toLocaleString("ko-KR")}`;
      return (
        <span
          className={cn(
            "font-semibold tabular-nums",
            pnlClassName ? pnlClassName(num) : pnlColorClass(num),
          )}
          aria-label={`${col}: ${display}`}
        >
          {display}
        </span>
      );
    }
  }
  if (emphasizeValues && typeof value === "number" && isNumericColumn(col)) {
    return (
      <span className="font-semibold tabular-nums text-foreground">
        {value.toLocaleString("ko-KR", { maximumFractionDigits: 2 })}
      </span>
    );
  }
  if (emphasizeValues && (col === "종목" || col === "자산군" || col === "지역" || col === "섹터" || col === "전략")) {
    return <strong className="font-bold text-foreground">{String(value ?? "")}</strong>;
  }
  if (emphasizeValues && col === "티커") {
    return <span className="font-semibold tabular-nums text-muted-foreground">{String(value ?? "")}</span>;
  }
  return <>{String(value ?? "")}</>;
}

interface HoldingsTableProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  maxRows?: number;
  className?: string;
  pnlClassName?: (value: number) => string;
  emphasizeValues?: boolean;
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
  pnlClassName,
  emphasizeValues = false,
}: HoldingsTableProps) {
  if (error) {
    return (
      <div
        role="alert"
        className="flex flex-col items-center gap-3 rounded-lg border border-destructive/40 bg-destructive/10 p-6 text-center text-sm text-destructive"
      >
        <ErrorIllustration size={80} />
        <strong>보유 종목을 불러오지 못했습니다.</strong>
        <p className="text-xs opacity-80">{error.message}</p>
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
                    className={cn(
                      "px-3 py-2 font-medium text-muted-foreground",
                      emphasizeValues && (isPnlColumn(col) || isNumericColumn(col)) ? "text-right" : "text-left",
                    )}
                  >
                    {col}
                  </th>
                ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
                  <SkeletonRow key={i} colCount={colCount} />
                ))
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
                  <td
                    key={col}
                    className={cn(
                      "px-3 py-2 text-foreground",
                      emphasizeValues && (isPnlColumn(col) || isNumericColumn(col)) && "text-right",
                    )}
                  >
                    <Cell
                      col={col}
                      value={row[col]}
                      pnlClassName={pnlClassName}
                      emphasizeValues={emphasizeValues}
                    />
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
