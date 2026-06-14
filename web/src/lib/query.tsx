"use client";

/**
 * query.tsx — TanStack Query client + Providers wrapper
 *
 * Mount <Providers> in the root layout to enable React Query throughout the app.
 * All data fetching should go through useQuery / useMutation hooks.
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

/** Create a fresh QueryClient with sensible defaults for Autofolio */
function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Stale time: 30s — balances freshness vs. request volume
        staleTime: 30_000,
        // Retry once on failure; avoid hammering a down backend
        retry: 1,
        // Don't refetch on window focus in dev to reduce noise
        refetchOnWindowFocus: process.env.NODE_ENV === "production",
      },
    },
  });
}

/**
 * <Providers> — client component that wraps the app with QueryClientProvider.
 * Place this in the root layout so all server/client components can use hooks.
 */
export function Providers({ children }: { children: ReactNode }) {
  // useState ensures each request gets its own QueryClient on the server
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
