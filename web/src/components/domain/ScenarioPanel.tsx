// web/src/components/domain/ScenarioPanel.tsx
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiScenario, apiWhatif } from "@/lib/api";
import { DataTable } from "@/components/domain/DataTable";
import type { TableResponse } from "@/lib/api";

/**
 * ScenarioPanel — scenario table (GET /api/analysis/scenario) +
 * optional whatif input (GET /api/analysis/whatif).
 */
export function ScenarioPanel() {
  const scenarioQuery = useQuery<TableResponse>({
    queryKey: ["analysis-scenario"],
    queryFn: apiScenario,
    staleTime: 60_000,
  });

  // Whatif form
  const [wiSymbol, setWiSymbol] = useState("005930");
  const [wiWeight, setWiWeight] = useState(10);
  const [wiSubmitted, setWiSubmitted] = useState<{ symbol: string; weight: number } | null>(null);

  const whatifQuery = useQuery<Record<string, unknown>>({
    queryKey: ["analysis-whatif", wiSubmitted],
    queryFn: () => apiWhatif(wiSubmitted!.symbol, wiSubmitted!.weight),
    enabled: wiSubmitted !== null,
    retry: 1,
  });

  function handleWhatifSubmit(e: React.FormEvent) {
    e.preventDefault();
    setWiSubmitted({ symbol: wiSymbol, weight: wiWeight });
  }

  return (
    <div className="space-y-6" data-testid="scenario-panel">
      {/* Scenario table */}
      <section aria-label="시나리오 분석">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground">시나리오 분석</h3>
        <DataTable
          data={scenarioQuery.data}
          isLoading={scenarioQuery.isPending}
          error={scenarioQuery.error as Error | null}
          caption="시나리오별 포트폴리오 영향"
        />
      </section>

      {/* What-if section */}
      <section aria-label="가정 분석 (What-if)">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground">가정 분석 (What-if)</h3>
        <form onSubmit={handleWhatifSubmit} className="flex flex-wrap gap-3 items-end mb-3">
          <div className="flex flex-col gap-1">
            <label htmlFor="wi-symbol" className="text-xs font-medium text-muted-foreground">
              종목 코드
            </label>
            <input
              id="wi-symbol"
              type="text"
              value={wiSymbol}
              onChange={(e) => setWiSymbol(e.target.value)}
              placeholder="005930"
              className="w-28 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="wi-weight" className="text-xs font-medium text-muted-foreground">
              비중 (%)
            </label>
            <input
              id="wi-weight"
              type="number"
              min={0}
              max={100}
              value={wiWeight}
              onChange={(e) => setWiWeight(Number(e.target.value))}
              className="w-20 rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            disabled={whatifQuery.isFetching}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {whatifQuery.isFetching ? "계산 중..." : "가정 실행"}
          </button>
        </form>

        {whatifQuery.error && (
          <div
            role="alert"
            className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive"
          >
            What-if 오류: {(whatifQuery.error as Error).message}
          </div>
        )}

        {whatifQuery.data && !whatifQuery.isFetching && (
          <div
            className="rounded-xl border border-border bg-muted/20 p-4 text-sm"
            data-testid="whatif-result"
          >
            <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs text-foreground">
              {JSON.stringify(whatifQuery.data, null, 2)}
            </pre>
          </div>
        )}
      </section>
    </div>
  );
}

export default ScenarioPanel;
