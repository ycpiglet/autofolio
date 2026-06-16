"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { apiGet, getInvestorProfile, type InvestorProfileResponse } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
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
  const { data: status, refetch } = useQuery<EngineStatus>({
    queryKey: ["engine-status"],
    queryFn: () => apiGet<EngineStatus>("/api/engine/status"),
    staleTime: 30_000,
    retry: 1,
  });
  const { data: profile } = useQuery<InvestorProfileResponse>({
    queryKey: ["investor-profile"],
    queryFn: getInvestorProfile,
    staleTime: 60_000,
    retry: 1,
  });

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
              프로필 작성
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
      </div>
    </header>
  );
}
