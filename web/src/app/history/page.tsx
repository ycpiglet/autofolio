"use client";

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { DataTable } from "@/components/domain/DataTable";
import { apiTable, type TableResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useSymbols } from "@/hooks/useSymbols";

// Korean column header map
const KO_HEADERS: Record<string, string> = {
  id: "번호",
  symbol: "종목코드",
  side: "구분",
  target_price: "목표가",
  quantity: "수량",
  order_type: "주문유형",
  auto_enabled: "자동",
  created_by: "등록자",
  status: "상태",
  order_price: "주문가",
  order_status: "주문상태",
  created_at: "등록일시",
};

function koHeader(col: string): string {
  return KO_HEADERS[col] ?? col;
}

function applyKoHeaders(data?: TableResponse): TableResponse | undefined {
  if (!data) return undefined;
  return {
    columns: data.columns.map(koHeader),
    rows: data.rows.map((row) => {
      const newRow: Record<string, unknown> = {};
      for (const col of data.columns) {
        newRow[koHeader(col)] = row[col];
      }
      return newRow;
    }),
  };
}

type SortDir = "asc" | "desc" | null;

interface SortState {
  col: string | null;
  dir: SortDir;
}

interface PaginatedTableProps {
  data?: TableResponse;
  isLoading?: boolean;
  error?: Error | null;
  caption?: string;
  symbolMap?: Record<string, string>;
}

function PaginatedTable({
  data,
  isLoading,
  error,
  caption,
  symbolMap,
}: PaginatedTableProps) {
  const [pageSize, setPageSize] = useState(20);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortState>({ col: null, dir: null });
  const [sideFilter, setSideFilter] = useState<string>("all");

  const koData = useMemo(() => applyKoHeaders(data), [data]);
  const columns = koData?.columns ?? [];
  const allRows = koData?.rows ?? [];

  // Detect if we have a "구분" (side) column for filtering
  const hasSide = columns.includes("구분");

  // Filter by search and side
  const filtered = useMemo(() => {
    let rows = allRows;
    if (sideFilter !== "all" && hasSide) {
      rows = rows.filter(
        (row) => String(row["구분"] ?? "").toUpperCase() === sideFilter,
      );
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      rows = rows.filter((row) =>
        columns.some((col) => String(row[col] ?? "").toLowerCase().includes(q)),
      );
    }
    return rows;
  }, [allRows, search, sideFilter, hasSide, columns]);

  // Sort
  const sorted = useMemo(() => {
    if (!sort.col || !sort.dir) return filtered;
    return [...filtered].sort((a, b) => {
      const av = a[sort.col!];
      const bv = b[sort.col!];
      const an = Number(av);
      const bn = Number(bv);
      const numCompare =
        !isNaN(an) && !isNaN(bn)
          ? an - bn
          : String(av ?? "").localeCompare(String(bv ?? ""), "ko");
      return sort.dir === "asc" ? numCompare : -numCompare;
    });
  }, [filtered, sort]);

  // Paginate
  const totalRows = sorted.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  const safePage = Math.min(page, totalPages);
  const pageRows = sorted.slice((safePage - 1) * pageSize, safePage * pageSize);

  function handleSort(col: string) {
    setSort((prev) => {
      if (prev.col !== col) return { col, dir: "asc" };
      if (prev.dir === "asc") return { col, dir: "desc" };
      return { col: null, dir: null };
    });
    setPage(1);
  }

  // Build a TableResponse slice for the current page
  const pageData: TableResponse = { columns, rows: pageRows };

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

  return (
    <div className="space-y-3">
      {/* Controls */}
      <div className="flex flex-wrap gap-2 items-center justify-between">
        <div className="flex gap-2 items-center flex-wrap">
          <input
            type="search"
            placeholder="검색..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="h-8 rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/50 w-48"
            aria-label="내역 검색"
          />
          {hasSide && (
            <select
              value={sideFilter}
              onChange={(e) => {
                setSideFilter(e.target.value);
                setPage(1);
              }}
              className="h-8 rounded-lg border border-input bg-background px-2 text-sm outline-none focus-visible:border-ring"
              aria-label="구분 필터"
            >
              <option value="all">전체</option>
              <option value="BUY">매수</option>
              <option value="SELL">매도</option>
            </select>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>총 {totalRows.toLocaleString("ko-KR")}건</span>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="h-8 rounded-lg border border-input bg-background px-2 text-sm outline-none focus-visible:border-ring"
            aria-label="페이지 크기"
          >
            <option value={10}>10개씩 보기</option>
            <option value={20}>20개씩 보기</option>
            <option value={50}>50개씩 보기</option>
          </select>
        </div>
      </div>

      {/* Sort controls */}
      {!isLoading && columns.length > 0 && (
        <div className="flex gap-1 flex-wrap">
          <span className="text-xs text-muted-foreground self-center mr-1">
            정렬:
          </span>
          {columns.map((col) => (
            <button
              key={col}
              onClick={() => handleSort(col)}
              className={cn(
                "text-xs px-2 py-1 rounded-md border transition-colors",
                sort.col === col
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-foreground/30",
              )}
            >
              {col}
              {sort.col === col ? (sort.dir === "asc" ? " ↑" : " ↓") : ""}
            </button>
          ))}
        </div>
      )}

      {/* Table */}
      <DataTable
        data={pageData}
        isLoading={isLoading}
        caption={caption}
        symbolMap={symbolMap}
      />

      {/* Pagination */}
      {!isLoading && totalRows > 0 && (
        <div className="flex items-center justify-between gap-2 text-sm">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={safePage === 1}
            className="px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:bg-muted/20 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            이전
          </button>
          <div className="flex gap-1">
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              const p = i + 1;
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={cn(
                    "w-8 h-8 rounded-lg text-sm transition-colors",
                    safePage === p
                      ? "bg-primary text-primary-foreground font-semibold"
                      : "border border-border text-muted-foreground hover:bg-muted/20",
                  )}
                >
                  {p}
                </button>
              );
            })}
            {totalPages > 7 && safePage < totalPages - 3 && (
              <>
                <span className="self-center text-muted-foreground">…</span>
                <button
                  onClick={() => setPage(totalPages)}
                  className="w-8 h-8 rounded-lg border border-border text-sm text-muted-foreground hover:bg-muted/20 transition-colors"
                >
                  {totalPages}
                </button>
              </>
            )}
          </div>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={safePage === totalPages}
            className="px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:bg-muted/20 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────

export default function HistoryPage() {
  const symbolMap = useSymbols();

  const ordersQuery = useQuery<TableResponse>({
    queryKey: ["trade-orders"],
    queryFn: () => apiTable("/api/trade/orders"),
    staleTime: 30_000,
  });

  const fillsQuery = useQuery<TableResponse>({
    queryKey: ["fills-recent-history"],
    queryFn: () => apiTable("/api/trade/fills/recent?limit=50"),
    staleTime: 30_000,
  });

  return (
    <AppShell>
      <div className="space-y-8">
        <h1 className="text-base font-semibold text-foreground">거래 내역</h1>

        <section aria-label="주문 내역">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            주문 내역
          </h2>
          <PaginatedTable
            data={ordersQuery.data}
            isLoading={ordersQuery.isPending}
            error={ordersQuery.error as Error | null}
            caption="전체 주문 내역"
            symbolMap={symbolMap}
          />
        </section>

        <section aria-label="최근 체결 내역">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            최근 체결
          </h2>
          <PaginatedTable
            data={fillsQuery.data}
            isLoading={fillsQuery.isPending}
            error={fillsQuery.error as Error | null}
            caption="최근 체결 내역"
            symbolMap={symbolMap}
          />
        </section>
      </div>
    </AppShell>
  );
}
