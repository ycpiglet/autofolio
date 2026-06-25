// web/src/app/home/page.tsx
"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import {
  apiGet,
  apiTable,
  getInvestorProfile,
  type InvestorProfileResponse,
  type TableResponse,
} from "@/lib/api";
import { useAuthSession, isUnauthorized } from "@/hooks/useAuthSession";
import { fmtWon, fmtPct } from "@/lib/format";
import { holdingsToTreemapItems } from "@/lib/holdings-treemap";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";
import { KpiCard } from "@/components/domain/KpiCard";
import { HoldingsTable } from "@/components/domain/HoldingsTable";
import { AllocationTreemap } from "@/components/domain/AllocationTreemap";
import { DataTable } from "@/components/domain/DataTable";
import { Button } from "@/components/ui/button";

// Dynamic imports — ssr: false prevents lightweight-charts / recharts DOM errors
const EquityChart = dynamic(
  () => import("@/components/domain/EquityChart").then((m) => m.EquityChart),
  { ssr: false, loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" /> },
);

interface KpiResponse {
  총평가금액?: number;
  일간손익?: number;
  일간수익률?: number;
  월간수익률?: number;
  [key: string]: number | undefined;
}

export default function HomePage() {
  const router = useRouter();

  // ── Auth guard — shared hook; query key ["auth-me"] deduplicates with ────
  // TopStatusBar and other consumers. Data queries below are gated on this.
  const { isAuthenticated, isPending: isAuthPending, isAuthError, authError, refetchAuth } =
    useAuthSession();

  useEffect(() => {
    if (isAuthError && isUnauthorized(authError)) {
      router.replace("/login");
    }
  }, [isAuthError, authError, router]);

  // ── Data queries — all gated on confirmed session (enabled: isAuthenticated)
  // so no fetch fires while unauthenticated or while the auth check is pending.
  const kpiQuery = useQuery<KpiResponse>({
    queryKey: ["portfolio-kpis"],
    queryFn: () => apiGet<KpiResponse>("/api/portfolio/kpis"),
    staleTime: 30_000,
    enabled: isAuthenticated,
  });

  const curveQuery = useQuery<TableResponse>({
    queryKey: ["asset-curve", 90],
    queryFn: () => apiTable("/api/portfolio/asset-curve?days=90"),
    staleTime: 60_000,
    enabled: isAuthenticated,
  });

  const indicesQuery = useQuery<TableResponse>({
    queryKey: ["market-indices"],
    queryFn: () => apiTable("/api/market/indices"),
    staleTime: 30_000,
    enabled: isAuthenticated,
  });

  const holdingsQuery = useQuery<TableResponse>({
    queryKey: ["portfolio-holdings"],
    queryFn: () => apiTable("/api/portfolio/holdings"),
    staleTime: 30_000,
    enabled: isAuthenticated,
  });

  const fillsQuery = useQuery<TableResponse>({
    queryKey: ["fills-recent"],
    queryFn: () => apiTable("/api/trade/fills/recent?limit=10"),
    staleTime: 30_000,
    enabled: isAuthenticated,
  });

  const profileQuery = useQuery<InvestorProfileResponse>({
    queryKey: ["investor-profile"],
    queryFn: getInvestorProfile,
    staleTime: 60_000,
    enabled: isAuthenticated,
  });

  // ── Loading / auth pending ───────────────────────────────────────────────
  if (isAuthPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-page">
        <div className="h-8 w-8 animate-pulse rounded-full bg-muted" aria-label="로딩 중" />
      </div>
    );
  }

  // ── Non-401 auth error (backend down / 500) — show recovery UI, not data body ──
  // This prevents rendering data-dependent components with undefined data, which
  // would throw and trigger an error-boundary remount loop (~40 auth-me req/s).
  if (isAuthError && !isUnauthorized(authError)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-page">
        <div
          role="alert"
          data-testid="auth-connection-error"
          className="flex max-w-sm flex-col items-center gap-4 rounded-xl border border-destructive/40 bg-destructive/5 p-8 text-center"
        >
          <p className="text-sm font-medium text-destructive">연결 오류</p>
          <p className="text-xs text-muted-foreground">
            서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.
          </p>
          <Button
            size="sm"
            onClick={refetchAuth}
            data-testid="auth-retry-btn"
          >
            재시도
          </Button>
        </div>
      </div>
    );
  }

  const kpi = kpiQuery.data;

  return (
    <AppShell>
      <div className="space-y-6">
        {profileQuery.data && !profileQuery.data.completed && (
          <section
            aria-label="투자 프로필 안내"
            className="flex flex-col gap-3 rounded-lg border border-amber-400/40 bg-amber-50 p-4 text-sm text-amber-900 dark:bg-amber-900/20 dark:text-amber-200 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <div className="font-medium">투자 프로필이 필요합니다.</div>
              <p className="mt-1 text-amber-800 dark:text-amber-300">
                조회는 가능하지만 조건 저장과 자동화 실행은 프로필 완료 후 사용할 수 있습니다.
              </p>
            </div>
            <Button size="sm" nativeButton={false} render={<Link href="/onboarding/investor-profile" />}>
              프로필 작성
            </Button>
          </section>
        )}

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
            isDemo={curveQuery.data?.is_demo}
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

        {/* ── Concentration Treemap (additive; hidden when no usable data) ── */}
        {(() => {
          const items = holdingsToTreemapItems(holdingsQuery.data);
          return items.length > 0 ? (
            <section aria-label="종목 집중도">
              <h2 className="mb-2 text-sm font-medium text-muted-foreground">종목 집중도</h2>
              <AllocationTreemap items={items} className="w-full" />
            </section>
          ) : null;
        })()}

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
