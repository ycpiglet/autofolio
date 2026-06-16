"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";

/** Fetch {code: name} symbol map from /api/market/symbols. */
export function useSymbols(): Record<string, string> {
  const { data } = useQuery<Record<string, string>>({
    queryKey: ["market-symbols"],
    queryFn: () => apiGet<Record<string, string>>("/api/market/symbols"),
    staleTime: 5 * 60 * 1_000, // 5 min — whitelist rarely changes
  });
  return data ?? {};
}
