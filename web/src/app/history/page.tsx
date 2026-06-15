// web/src/app/history/page.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { DataTable } from "@/components/domain/DataTable";
import { apiTable, type TableResponse } from "@/lib/api";

export default function HistoryPage() {
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
      <div className="space-y-6">
        <h1 className="text-base font-semibold text-foreground">거래 내역</h1>

        <section aria-label="주문 내역">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">주문 내역</h2>
          <DataTable
            data={ordersQuery.data}
            isLoading={ordersQuery.isPending}
            error={ordersQuery.error as Error | null}
            caption="전체 주문 내역"
          />
        </section>

        <section aria-label="최근 체결 내역">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">최근 체결</h2>
          <DataTable
            data={fillsQuery.data}
            isLoading={fillsQuery.isPending}
            error={fillsQuery.error as Error | null}
            caption="최근 체결 내역"
          />
        </section>
      </div>
    </AppShell>
  );
}
