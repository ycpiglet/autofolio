"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { OrderForm } from "@/components/domain/OrderForm";
import { OrderBookLadder } from "@/components/domain/OrderBookLadder";
import { DataTable } from "@/components/domain/DataTable";
import { Button } from "@/components/ui/button";
import { ConfirmModal } from "@/components/safety/ConfirmModal";
import { apiTable, postRunOnce, ApiError, type TableResponse } from "@/lib/api";
import { useSymbols } from "@/hooks/useSymbols";

type RunOnceStatus =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "busy" }
  | { kind: "done" }
  | { kind: "error"; message: string };

function TradePageInner() {
  const queryClient = useQueryClient();
  const symbolMap = useSymbols();
  const searchParams = useSearchParams();
  const [previewSymbol, setPreviewSymbol] = useState("");

  // Prefill from an agent research proposal (querystring). Pre-fills the
  // OrderForm only — saving still goes through the Phase-3 gate.
  const prefillSymbol = searchParams.get("symbol") ?? "";
  const prefillSideRaw = (searchParams.get("side") ?? "").toUpperCase();
  const prefillSide: "BUY" | "SELL" = prefillSideRaw === "SELL" ? "SELL" : "BUY";
  const prefillPrice = searchParams.get("price") ?? "";
  const prefillQty = searchParams.get("qty") ?? "";
  const [runOnceStatus, setRunOnceStatus] = useState<RunOnceStatus>({ kind: "idle" });
  const [runOnceConfirmOpen, setRunOnceConfirmOpen] = useState(false);

  // Current active conditions
  const conditionsQuery = useQuery<TableResponse>({
    queryKey: ["trade-conditions"],
    queryFn: () => apiTable("/api/trade/conditions"),
    staleTime: 15_000,
  });

  async function handleRunOnce() {
    setRunOnceStatus({ kind: "running" });
    try {
      await postRunOnce();
      setRunOnceStatus({ kind: "done" });
      void queryClient.invalidateQueries({ queryKey: ["trade-conditions"] });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setRunOnceStatus({ kind: "busy" });
        return;
      }
      setRunOnceStatus({
        kind: "error",
        message: err instanceof Error ? err.message : "알 수 없는 오류",
      });
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-base font-semibold text-foreground">매매</h1>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setRunOnceConfirmOpen(true)}
              disabled={runOnceStatus.kind === "running"}
              aria-label="엔진 1회 실행"
            >
              {runOnceStatus.kind === "running" ? "실행 중…" : "엔진 1회 실행"}
            </Button>
            <ConfirmModal
              open={runOnceConfirmOpen}
              onOpenChange={setRunOnceConfirmOpen}
              title="엔진을 1회 실행하시겠습니까?"
              description="충족된 조건이 즉시 처리됩니다."
              confirmLabel="실행"
              cancelLabel="취소"
              onConfirm={() => void handleRunOnce()}
            />
            {runOnceStatus.kind === "busy" && (
              <span role="status" className="text-xs text-amber-600">이미 실행 중</span>
            )}
            {runOnceStatus.kind === "done" && (
              <span role="status" className="text-xs text-muted-foreground">완료</span>
            )}
            {runOnceStatus.kind === "error" && (
              <span role="alert" className="text-xs text-destructive">{runOnceStatus.message}</span>
            )}
          </div>
        </div>

        {/* Main grid */}
        <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
          {/* Left: OrderForm + conditions table */}
          <div className="space-y-6">
            <OrderForm
              key={`${prefillSymbol}-${prefillSide}-${prefillPrice}-${prefillQty}`}
              initialSymbol={prefillSymbol}
              initialSide={prefillSide}
              initialTargetPrice={prefillPrice}
              initialQuantity={prefillQty}
              onCreated={() => {
                void queryClient.invalidateQueries({ queryKey: ["trade-conditions"] });
              }}
            />

            <section aria-label="등록된 조건">
              <h2 className="mb-2 text-sm font-medium text-muted-foreground">등록된 조건</h2>
              <DataTable
                data={conditionsQuery.data}
                isLoading={conditionsQuery.isPending}
                error={conditionsQuery.error as Error | null}
                caption="활성 매매 조건 목록"
                symbolMap={symbolMap}
              />
            </section>
          </div>

          {/* Right: OrderBookLadder */}
          <div className="space-y-2">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="ladder-symbol" className="text-sm font-medium text-muted-foreground">
                호가 조회 종목
              </label>
              <input
                id="ladder-symbol"
                className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                placeholder="종목 코드"
                value={previewSymbol}
                onChange={(e) => setPreviewSymbol(e.target.value.toUpperCase())}
              />
            </div>
            <OrderBookLadder symbol={previewSymbol} />
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default function TradePage() {
  return (
    <Suspense fallback={<AppShell><div className="h-32 animate-pulse rounded-xl bg-muted" /></AppShell>}>
      <TradePageInner />
    </Suspense>
  );
}
