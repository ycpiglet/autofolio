// web/src/components/domain/OrderBookLadder.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { fmtWon, fmtTabular } from "@/lib/format";
import { cn } from "@/lib/utils";

interface OrderBookEntry {
  price: number;
  quantity: number;
}

interface OrderBookResponse {
  symbol: string;
  asks: OrderBookEntry[];
  bids: OrderBookEntry[];
}

interface OrderBookLadderProps {
  symbol: string;
  className?: string;
}

export function OrderBookLadder({ symbol, className }: OrderBookLadderProps) {
  const { data, isLoading, error } = useQuery<OrderBookResponse>({
    queryKey: ["order-book", symbol],
    queryFn: () => apiGet<OrderBookResponse>(`/api/market/order-book?symbol=${encodeURIComponent(symbol)}`),
    enabled: !!symbol,
    staleTime: 5_000,
    refetchInterval: 10_000,
  });

  if (!symbol) {
    return (
      <div className={cn("rounded-xl border border-border p-4 text-sm text-muted-foreground", className)}>
        종목 코드를 입력하면 호가가 표시됩니다.
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className={cn("rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive", className)}>
        호가를 불러오지 못했습니다: {(error as Error).message}
      </div>
    );
  }

  const asks = data?.asks ?? [];
  const bids = data?.bids ?? [];
  const maxQty = Math.max(
    ...asks.map((a) => a.quantity),
    ...bids.map((b) => b.quantity),
    1,
  );

  return (
    <div className={cn("rounded-xl border border-border overflow-hidden", className)} aria-label="호가창">
      <div className="border-b border-border bg-muted/40 px-3 py-2 text-xs font-medium text-muted-foreground">
        호가 — {symbol || "—"}
      </div>

      {isLoading ? (
        <div className="p-4 space-y-1">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-5 animate-pulse rounded bg-muted" />
          ))}
        </div>
      ) : (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border">
              <th scope="col" className="px-2 py-1.5 text-right font-medium text-destructive/80">수량(매도)</th>
              <th scope="col" className="px-2 py-1.5 text-center font-medium text-muted-foreground">가격</th>
              <th scope="col" className="px-2 py-1.5 text-left font-medium text-blue-600/80">수량(매수)</th>
            </tr>
          </thead>
          <tbody>
            {[...asks].reverse().map((ask, i) => (
              <tr key={`ask-${i}`} className="border-b border-border/50">
                <td className="relative px-2 py-1 text-right">
                  <span
                    className="absolute inset-y-0 right-0 bg-destructive/10"
                    style={{ width: `${(ask.quantity / maxQty) * 100}%` }}
                    aria-hidden
                  />
                  <span className="relative text-destructive/90">{fmtTabular(ask.quantity)}</span>
                </td>
                <td className="px-2 py-1 text-center font-medium text-destructive/90">
                  {fmtWon(ask.price)}
                </td>
                <td className="px-2 py-1" />
              </tr>
            ))}
            {bids.map((bid, i) => (
              <tr key={`bid-${i}`} className="border-b border-border/50">
                <td className="px-2 py-1" />
                <td className="px-2 py-1 text-center font-medium text-blue-600">
                  {fmtWon(bid.price)}
                </td>
                <td className="relative px-2 py-1 text-left">
                  <span
                    className="absolute inset-y-0 left-0 bg-blue-500/10"
                    style={{ width: `${(bid.quantity / maxQty) * 100}%` }}
                    aria-hidden
                  />
                  <span className="relative text-blue-600">{fmtTabular(bid.quantity)}</span>
                </td>
              </tr>
            ))}
            {asks.length === 0 && bids.length === 0 && (
              <tr>
                <td colSpan={3} className="px-3 py-4 text-center text-muted-foreground">
                  호가 데이터 없음
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
