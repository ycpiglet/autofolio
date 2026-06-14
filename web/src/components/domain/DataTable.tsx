// web/src/components/domain/DataTable.tsx
import { cn } from "@/lib/utils";
import type { TableResponse } from "@/lib/api";

interface DataTableProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  /** Max rows to render (undefined = all) */
  maxRows?: number;
  className?: string;
  caption?: string;
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
}: DataTableProps) {
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

  return (
    <div
      className={cn("overflow-x-auto rounded-xl border border-border", className)}
    >
      <table className="w-full text-sm">
        {caption && (
          <caption className="sr-only">{caption}</caption>
        )}
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
              <tr
                key={ri}
                className="border-b border-border last:border-0 hover:bg-muted/20"
              >
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2 text-foreground">
                    {String(row[col] ?? "")}
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
