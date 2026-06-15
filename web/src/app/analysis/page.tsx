// web/src/app/analysis/page.tsx
"use client";

import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { apiAttribution, type TableResponse } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";

// ── Client-only chart components (ssr:false — DOM access) ─────────────────
const CandleChart = dynamic(
  () =>
    import("@/components/domain/CandleChart").then((m) => m.CandleChart),
  {
    ssr: false,
    loading: () => (
      <div className="h-[280px] animate-pulse rounded-xl bg-muted" />
    ),
  },
);

const AttributionSankey = dynamic(
  () =>
    import("@/components/domain/AttributionSankey").then(
      (m) => m.AttributionSankey,
    ),
  {
    ssr: false,
    loading: () => <div className="h-60 animate-pulse rounded-xl bg-muted" />,
  },
);

// ── Server-compatible components (no DOM needed at top-level) ─────────────
// BacktestPanel, VarPanel, ScenarioPanel are "use client" but don't need
// ssr:false — recharts/form inputs are safe during SSR as static HTML.
// However, to keep the pattern consistent and avoid any subtle recharts issue
// we load them lazily too.
const BacktestPanel = dynamic(
  () =>
    import("@/components/domain/BacktestPanel").then((m) => m.BacktestPanel),
  { ssr: false },
);

const VarPanel = dynamic(
  () => import("@/components/domain/VarPanel").then((m) => m.VarPanel),
  { ssr: false },
);

const ScenarioPanel = dynamic(
  () =>
    import("@/components/domain/ScenarioPanel").then((m) => m.ScenarioPanel),
  { ssr: false },
);

export default function AnalysisPage() {
  const attributionQuery = useQuery<TableResponse>({
    queryKey: ["analysis-attribution"],
    queryFn: apiAttribution,
    staleTime: 60_000,
  });

  return (
    <AppShell>
      <div className="space-y-8">
        <h1 className="text-lg font-semibold">분석</h1>

        {/* ── 1. 캔들차트 ─────────────────────────────────────────────── */}
        <section aria-label="캔들차트">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            분봉 차트
          </h2>
          <CandleChart />
        </section>

        {/* ── 2. 백테스트 ─────────────────────────────────────────────── */}
        <section aria-label="백테스트" data-testid="backtest-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            백테스트
          </h2>
          <BacktestPanel />
        </section>

        {/* ── 3. VaR ──────────────────────────────────────────────────── */}
        <section aria-label="VaR 분석" data-testid="var-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            VaR (Value at Risk)
          </h2>
          <VarPanel />
        </section>

        {/* ── 4. 시나리오 ─────────────────────────────────────────────── */}
        <section aria-label="시나리오 분석" data-testid="scenario-section">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            시나리오 / What-if
          </h2>
          <ScenarioPanel />
        </section>

        {/* ── 5. 기여도 (Sankey) ──────────────────────────────────────── */}
        <section aria-label="기여도 분석">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">
            기여도 (Attribution)
          </h2>
          <AttributionSankey
            data={attributionQuery.data}
            isLoading={attributionQuery.isPending}
            error={attributionQuery.error as Error | null}
          />
        </section>
      </div>
    </AppShell>
  );
}
