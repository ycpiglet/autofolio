"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  apiGet,
  getInvestorProfile,
  postLogout,
  type InvestorProfileResponse,
} from "@/lib/api";
import { useAuthSession } from "@/hooks/useAuthSession";
import { clearCsrfCache } from "@/lib/csrf";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EnvBadge } from "@/components/safety/EnvBadge";
import { KillSwitchButton } from "@/components/safety/KillSwitchButton";
import { AutoTradingToggle } from "@/components/safety/AutoTradingToggle";
import { cn } from "@/lib/utils";

interface EngineStatus {
  env: string;
  auto_trading_enabled: boolean;
  kill_switch_active: boolean;
  circuit_breaker: {
    triggered: boolean;
    threshold_pct: number;
    consecutive_failures: number;
    today_pnl: number;
  };
}

interface TopStatusBarProps {
  className?: string;
}

export function TopStatusBar({ className }: TopStatusBarProps) {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);

  // Gate data queries on confirmed session so TopStatusBar does not fire
  // /api/engine/status or /api/profile/investor while unauthenticated.
  // Shares the ["auth-me"] cache with home/page.tsx — zero extra requests.
  const { isAuthenticated } = useAuthSession();

  const { data: status, refetch } = useQuery<EngineStatus>({
    queryKey: ["engine-status"],
    queryFn: () => apiGet<EngineStatus>("/api/engine/status"),
    staleTime: 30_000,
    retry: 1,
    enabled: isAuthenticated,
  });
  const { data: profile } = useQuery<InvestorProfileResponse>({
    queryKey: ["investor-profile"],
    queryFn: getInvestorProfile,
    staleTime: 60_000,
    retry: 1,
    enabled: isAuthenticated,
  });

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await postLogout();
    } catch {
      // Even if the request fails, clear local state and send the user to /login.
    } finally {
      clearCsrfCache();
      router.replace("/login");
    }
  }

  return (
    <header
      className={cn(
        "flex h-12 items-center justify-between border-b border-border bg-surface px-4 shadow-soft",
        className
      )}
      aria-label="상태 표시줄"
    >
      <div className="flex flex-1 items-center gap-2">
        {profile && (
          profile.completed ? (
            <Badge variant="secondary">
              {profile.risk_type}
            </Badge>
          ) : (
            <Badge variant="outline" render={<Link href="/onboarding/investor-profile" />}>
              성향 진단
            </Badge>
          )
        )}
      </div>

      {/* StatusCluster */}
      <div
        className="flex items-center gap-2"
        aria-label="상태 클러스터"
      >
        {status ? (
          <>
            <EnvBadge env={status.env} />
            <AutoTradingToggle
              enabled={status.auto_trading_enabled}
              onToggled={() => void refetch()}
            />
            <KillSwitchButton
              isActive={status.kill_switch_active}
              onActivated={() => void refetch()}
            />
          </>
        ) : (
          <>
            <span className="h-5 w-12 animate-pulse rounded-full bg-muted" />
            <span className="h-7 w-20 animate-pulse rounded-lg bg-muted" />
            <span className="h-7 w-24 animate-pulse rounded-lg bg-muted" />
          </>
        )}
        <Button
          variant="ghost"
          size="sm"
          aria-label="로그아웃"
          onClick={handleLogout}
          disabled={loggingOut}
        >
          {loggingOut ? "로그아웃 중…" : "로그아웃"}
        </Button>
      </div>
    </header>
  );
}
