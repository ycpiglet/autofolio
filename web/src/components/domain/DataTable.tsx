"use client";

import { useState, Fragment } from "react";
import { cn } from "@/lib/utils";
import { symbolLabel } from "@/lib/format";
import type { TableResponse } from "@/lib/api";

interface DataTableProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  /** Max rows to render (undefined = all) */
  maxRows?: number;
  className?: string;
  caption?: string;
  /** Optional code→name map for symbol columns */
  symbolMap?: Record<string, string>;
}

// Keywords that indicate a column holds numeric content (right-align)
const NUMERIC_KEYWORDS = [
  "가격", "단가", "수량", "금액", "손익", "수익", "비중", "비율", "평균",
  "현재", "평가", "체결", "목표", "총", "율", "%",
  "price", "qty", "amount", "rate", "pnl", "count", "value", "total",
];

function isNumericColumn(col: string, sampleValue?: unknown): boolean {
  const lower = col.toLowerCase();
  if (NUMERIC_KEYWORDS.some((kw) => lower.includes(kw.toLowerCase()))) return true;
  if (typeof sampleValue === "number") return true;
  if (
    typeof sampleValue === "string" &&
    sampleValue !== "" &&
    !isNaN(Number(sampleValue))
  )
    return true;
  return false;
}

const CODE_COLUMNS = new Set(["symbol", "종목코드", "티커", "종목"]);
function isCodeColumn(col: string): boolean {
  return CODE_COLUMNS.has(col) || CODE_COLUMNS.has(col.toLowerCase());
}

function SkeletonRow({ cols }: { cols: number }) {
  return (
    <tr aria-hidden>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-3 py-2">
          <div className="h-4 animate-pulse rounded bg-muted" />
        </td>
      ))}
    </tr>
  );
}

/**
 * DataTable — generic renderer for TableResponse (Korean column keys).
 *
 * Features:
 * - Right-aligns numeric columns; left-aligns text columns
 * - Truncates long cell content (full value shown in expand panel)
 * - Expandable rows: click row → detail panel with all field/value pairs
 * - Zebra row striping, sticky header
 * - Optional symbolMap prop: formats symbol codes as "종목명 (코드)"
 *
 * States:
 * - isLoading=true  → skeleton rows
 * - error truthy    → visible error panel (NOT silent, per spec §Phase2 "no-fallback")
 * - data present    → table
 * - data empty      → "데이터 없음" empty state
 */
export function DataTable({
  data,
  isLoading,
  error,
  maxRows,
  className,
  caption,
  symbolMap = {},
}: DataTableProps) {
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  if (error) {
    return (
      <div
        role="alert"
        className="rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive"
      >
        <strong>데이터를 불러오지 못했습니다.</strong>
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
  const colCount = columns.length || 4;

  // Sample first row to help detect numeric columns
  const firstRow = rows[0];

  function formatCell(col: string, value: unknown): string {
    const str = String(value ?? "");
    if (isCodeColumn(col) && Object.keys(symbolMap).length > 0) {
      return symbolLabel(str, symbolMap);
    }
    return str;
  }

  function toggleRow(ri: number) {
    setExpandedRow((prev) => (prev === ri ? null : ri));
  }

  return (
    <div className={cn("rounded-xl border border-border overflow-hidden", className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm table-fixed">
          {caption && <caption className="sr-only">{caption}</caption>}
          <thead className="sticky top-0 z-10">
            <tr className="border-b border-border bg-muted/60">
              {isLoading
                ? Array.from({ length: colCount }).map((_, i) => (
                    <th
                      key={i}
                      className="px-3 py-2.5 text-left font-medium text-muted-foreground"
                    >
                      <div className="h-3 w-16 animate-pulse rounded bg-muted" />
                    </th>
                  ))
                : columns.map((col) => (
                    <th
                      key={col}
                      scope="col"
                      className={cn(
                        "px-3 py-2.5 font-medium text-muted-foreground text-xs uppercase tracking-wide",
                        isNumericColumn(col, firstRow?.[col])
                          ? "text-right"
                          : "text-left",
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
                <SkeletonRow key={i} cols={colCount} />
              ))
            ) : rows.length === 0 ? (
              <tr>
                <td
                  colSpan={colCount}
                  className="px-3 py-8 text-center text-sm text-muted-foreground"
                >
                  데이터 없음
                </td>
              </tr>
            ) : (
              rows.map((row, ri) => (
                <Fragment key={ri}>
                  <tr
                    onClick={() => toggleRow(ri)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        toggleRow(ri);
                      }
                    }}
                    tabIndex={0}
                    aria-expanded={expandedRow === ri}
                    className={cn(
                      "border-b border-border/60 last:border-0 cursor-pointer select-none transition-colors",
                      ri % 2 === 0
                        ? "bg-background hover:bg-muted/30"
                        : "bg-muted/10 hover:bg-muted/30",
                      expandedRow === ri && "bg-muted/20",
                    )}
                  >
                    {columns.map((col) => (
                      <td
                        key={col}
                        className={cn(
                          "px-3 py-2 text-foreground max-w-0",
                          isNumericColumn(col, firstRow?.[col])
                            ? "text-right font-mono tabular-nums"
                            : "text-left",
                        )}
                      >
                        <span
                          className="block truncate"
                          title={String(row[col] ?? "")}
                        >
                          {formatCell(col, row[col])}
                        </span>
                      </td>
                    ))}
                  </tr>
                  {expandedRow === ri && (
                    <tr className="bg-muted/5 border-b border-border/60">
                      <td colSpan={colCount} className="px-4 py-3">
                        <dl className="grid grid-cols-2 gap-x-6 gap-y-1 sm:grid-cols-3 text-xs">
                          {columns.map((col) => (
                            <div key={col} className="flex gap-1">
                              <dt className="text-muted-foreground shrink-0">
                                {col}:
                              </dt>
                              <dd className="text-foreground font-medium break-all">
                                {formatCell(col, row[col])}
                              </dd>
                            </div>
                          ))}
                        </dl>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
