"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiGet, ApiError } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/safety/EmptyState";

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

export default function HomePage() {
  const router = useRouter();

  const { error, isError, isPending } = useQuery<SessionResponse>({
    queryKey: ["auth-me"],
    queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
    retry: false,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (isError && error instanceof ApiError && error.status === 401) {
      router.replace("/login");
    }
  }, [isError, error, router]);

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-page">
        <div className="h-8 w-8 animate-pulse rounded-full bg-muted" aria-label="로딩 중" />
      </div>
    );
  }

  return (
    <AppShell>
      <EmptyState
        title="홈 대시보드"
        description="홈 대시보드는 Phase 2에서 구현됩니다."
        phase="Phase 2 예정"
      />
    </AppShell>
  );
}
