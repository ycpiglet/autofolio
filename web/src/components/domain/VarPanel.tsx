// web/src/components/domain/VarPanel.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiVar, type SimulationResult } from "@/lib/api";
import { KpiCard } from "@/components/domain/KpiCard";
import { fmtWon, fmtPct } from "@/lib/format";

interface VarParams {
  horizon_days: number;
  n_simulations: number;
}

const DEFAULT_PARAMS: VarParams = { horizon_days: 10, n_simulations: 10000 };

/**
 * VarPanel — form + result KPIs for GET /api/analysis/var.
 * Shows `note` field when data is empty/placeholder. No fabrication.
 */
export function VarPanel() {
  const [params, setParams] = useState<VarParams>(DEFAULT_PARAMS);
  const [submitted, setSubmitted] = useState<VarParams | null>(null);

  const query = useQuery<SimulationResult>({
    queryKey: ["analysis-var", submitted],
    queryFn: () => apiVar(submitted!),
    enabled: submitted !== null,
    retry: 1,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted({ ...params });
  }

  return (
    <div className="space-y-4" data-testid="var-panel">
      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <label htmlFor="var-horizon" className="text-xs font-medium text-muted-foreground">
            보유 기간 (일)
          </label>
          <input
            id="var-horizon"
            type="number"
            min={1}
            value={params.horizon_days}
            onChange={(e) =>
              setParams((p) => ({ ...p, horizon_days: Number(e.target.value) }))
            }
            className="w-28 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="var-sims" className="text-xs font-medium text-muted-foreground">
            시뮬레이션 횟수
          </label>
          <input
            id="var-sims"
            type="number"
            min={100}
            step={100}
            value={params.n_simulations}
            onChange={(e) =>
              setParams((p) => ({ ...p, n_simulations: Number(e.target.value) }))
            }
            className="w-32 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          type="submit"
          disabled={query.isFetching}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {query.isFetching ? "계산 중..." : "VaR 계산"}
        </button>
      </form>

      {/* Error */}
      {query.error && (
        <div
          role="alert"
          className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
        >
          VaR 계산 오류: {(query.error as Error).message}
        </div>
      )}

      {/* Loading skeleton */}
      {query.isFetching && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-muted" />
          ))}
        </div>
      )}

      {/* Results */}
      {query.data && !query.isFetching && (
        <div className="space-y-3">
          {/* Note banner: show when backend signals data is empty */}
          {query.data.note && (
            <div
              role="status"
              className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800"
            >
              {query.data.note}
            </div>
          )}
          <div
            className="grid grid-cols-2 gap-3 sm:grid-cols-4"
            data-testid="var-result"
            aria-label="VaR 결과"
          >
            <KpiCard
              label="VaR 95% (원)"
              value={fmtWon(query.data.var_95)}
            />
            <KpiCard
              label="VaR 99% (원)"
              value={fmtWon(query.data.var_99)}
            />
            <KpiCard
              label="CVaR 95% (원)"
              value={fmtWon(query.data.cvar_95)}
            />
            <KpiCard
              label="최대 낙폭"
              value={fmtPct(query.data.max_drawdown_pct)}
              delta={-Math.abs(query.data.max_drawdown_pct)}
              deltaMode="pct"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default VarPanel;
