// web/src/app/portfolio/page.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { apiGet, apiTable, type TableResponse } from "@/lib/api";
import { fmtWon, fmtPct } from "@/lib/format";
import { AppShell } from "@/components/layout/AppShell";
import { KpiCard } from "@/components/domain/KpiCard";
import { HoldingsTable } from "@/components/domain/HoldingsTable";

const EquityChart = dynamic(
  () => import("@/components/domain/EquityChart").then((m) => m.EquityChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" /> },
);

const AllocationChart = dynamic(
  () => import("@/components/domain/AllocationChart").then((m) => m.AllocationChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" /> },
);

interface KpiResponse {
  총평가금액?: number;
  일간손익?: number;
  일간수익률?: number;
  월간수익률?: number;
  [key: string]: number | undefined;
}

export default function PortfolioPage() {
  const kpiQuery = useQuery<KpiResponse>({
    queryKey: ["portfolio-kpis"],
    queryFn: () => apiGet<KpiResponse>("/api/portfolio/kpis"),
    staleTime: 30_000,
  });

  const holdingsQuery = useQuery<TableResponse>({
    queryKey: ["portfolio-holdings"],
    queryFn: () => apiTable("/api/portfolio/holdings"),
    staleTime: 30_000,
  });

  const curveQuery = useQuery<TableResponse>({
    queryKey: ["asset-curve"],
    queryFn: () => apiTable("/api/portfolio/asset-curve?days=90"),
    staleTime: 60_000,
  });

  const allocationQuery = useQuery<TableResponse>({
    queryKey: ["allocation-gap"],
    queryFn: () => apiTable("/api/portfolio/allocation-gap"),
    staleTime: 30_000,
  });

  const kpi = kpiQuery.data;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* ── KPI Summary ───────────────────────────────────────────────── */}
        <section aria-label="포트폴리오 핵심 지표">
          <h1 className="mb-4 text-lg font-semibold">포트폴리오</h1>
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

        {/* ── Full Holdings Table ───────────────────────────────────────── */}
        <section aria-label="전체 보유 종목">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">보유 종목</h2>
          <HoldingsTable
            data={holdingsQuery.data}
            isLoading={holdingsQuery.isPending}
            error={holdingsQuery.error as Error | null}
          />
        </section>

        {/* ── Equity Chart ─────────────────────────────────────────────── */}
        <section aria-label="자산 추이">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">자산 추이 (90일)</h2>
          <EquityChart
            data={curveQuery.data}
            isLoading={curveQuery.isPending}
            error={curveQuery.error as Error | null}
          />
        </section>

        {/* ── Allocation Chart ──────────────────────────────────────────── */}
        <section aria-label="자산 배분">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">자산 배분</h2>
          <AllocationChart
            data={allocationQuery.data}
            isLoading={allocationQuery.isPending}
            error={allocationQuery.error as Error | null}
          />
        </section>
      </div>
    </AppShell>
  );
}
