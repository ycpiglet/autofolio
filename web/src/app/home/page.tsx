// web/src/app/home/page.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { apiGet, apiTable, ApiError, type TableResponse } from "@/lib/api";
import { fmtWon, fmtPct } from "@/lib/format";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
import { KpiCard } from "@/components/domain/KpiCard";
import { HoldingsTable } from "@/components/domain/HoldingsTable";
import { DataTable } from "@/components/domain/DataTable";

// Dynamic imports — ssr: false prevents lightweight-charts / recharts DOM errors
const EquityChart = dynamic(
  () => import("@/components/domain/EquityChart").then((m) => m.EquityChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" /> },
);

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

interface KpiResponse {
  총평가금액?: number;
  일간손익?: number;
  일간수익률?: number;
  월간수익률?: number;
  [key: string]: number | undefined;
}

export default function HomePage() {
  const router = useRouter();

  // ── Auth guard ───────────────────────────────────────────────────────────
  const { error: authError, isError: isAuthError, isPending: isAuthPending } =
    useQuery<SessionResponse>({
      queryKey: ["auth-me"],
      queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
      retry: false,
      staleTime: 60_000,
    });

  useEffect(() => {
    if (isAuthError && authError instanceof ApiError && authError.status === 401) {
      router.replace("/login");
    }
  }, [isAuthError, authError, router]);

  // ── Data queries ─────────────────────────────────────────────────────────
  const kpiQuery = useQuery<KpiResponse>({
    queryKey: ["portfolio-kpis"],
    queryFn: () => apiGet<KpiResponse>("/api/portfolio/kpis"),
    staleTime: 30_000,
  });

  const curveQuery = useQuery<TableResponse>({
    queryKey: ["asset-curve"],
    queryFn: () => apiTable("/api/portfolio/asset-curve?days=90"),
    staleTime: 60_000,
  });

  const indicesQuery = useQuery<TableResponse>({
    queryKey: ["market-indices"],
    queryFn: () => apiTable("/api/market/indices"),
    staleTime: 30_000,
  });

  const holdingsQuery = useQuery<TableResponse>({
    queryKey: ["portfolio-holdings"],
    queryFn: () => apiTable("/api/portfolio/holdings"),
    staleTime: 30_000,
  });

  const fillsQuery = useQuery<TableResponse>({
    queryKey: ["fills-recent"],
    queryFn: () => apiTable("/api/trade/fills/recent?limit=10"),
    staleTime: 30_000,
  });

  // ── Loading / auth pending ───────────────────────────────────────────────
  if (isAuthPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-page">
        <div className="h-8 w-8 animate-pulse rounded-full bg-muted" aria-label="로딩 중" />
      </div>
    );
  }

  const kpi = kpiQuery.data;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* ── KPI Row ─────────────────────────────────────────────────── */}
        <section aria-label="핵심 지표">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <KpiCard
              label="총평가금액"
              value={kpi?.총평가금액 !== undefined ? fmtWon(kpi.총평가금액) : "—"}
              delta={kpi?.일간수익률}
              deltaMode="pct"
            />
            <KpiCard
              label="일간손익"
              value={kpi?.일간손익 !== undefined ? fmtWon(kpi.일간손익) : "—"}
              delta={kpi?.일간손익}
              deltaMode="won"
            />
            <KpiCard
              label="일간수익률"
              value={kpi?.일간수익률 !== undefined ? fmtPct(kpi.일간수익률) : "—"}
            />
            <KpiCard
              label="월간수익률"
              value={kpi?.월간수익률 !== undefined ? fmtPct(kpi.월간수익률) : "—"}
            />
          </div>
          {kpiQuery.error && (
            <div role="alert" className="mt-2 rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
              KPI를 불러오지 못했습니다: {(kpiQuery.error as Error).message}
            </div>
          )}
        </section>

        {/* ── Equity Chart ────────────────────────────────────────────── */}
        <section aria-label="자산 추이">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">자산 추이 (90일)</h2>
          <EquityChart
            data={curveQuery.data}
            isLoading={curveQuery.isPending}
            error={curveQuery.error as Error | null}
          />
        </section>

        {/* ── Market Indices ───────────────────────────────────────────── */}
        <section aria-label="시장 지수">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">시장 지수</h2>
          <DataTable
            data={indicesQuery.data}
            isLoading={indicesQuery.isPending}
            error={indicesQuery.error as Error | null}
            caption="주요 시장 지수"
          />
        </section>

        {/* ── Holdings Preview ─────────────────────────────────────────── */}
        <section aria-label="보유 종목 (상위 5)">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">보유 종목</h2>
          <HoldingsTable
            data={holdingsQuery.data}
            isLoading={holdingsQuery.isPending}
            error={holdingsQuery.error as Error | null}
            maxRows={5}
          />
        </section>

        {/* ── Recent Fills ─────────────────────────────────────────────── */}
        <section aria-label="최근 체결">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">최근 체결</h2>
          <DataTable
            data={fillsQuery.data}
            isLoading={fillsQuery.isPending}
            error={fillsQuery.error as Error | null}
            caption="최근 체결 내역"
          />
        </section>

        {/* ── Proposal Area (Phase 2: no endpoint — always EmptyState) ── */}
        <section aria-label="투자 제안">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">투자 제안</h2>
          <EmptyState
            title="제안 없음"
            description="현재 활성 투자 제안이 없습니다."
          />
        </section>
      </div>
    </AppShell>
  );
}
