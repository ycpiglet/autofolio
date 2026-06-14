"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
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
  const { data: status } = useQuery<EngineStatus>({
    queryKey: ["engine-status"],
    queryFn: () => apiGet<EngineStatus>("/api/engine/status"),
    staleTime: 30_000,
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
      {/* Left spacer — title could go here in Phase 2 */}
      <div className="flex-1" />

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
              phase1Disabled={true}
            />
            <KillSwitchButton
              isActive={status.kill_switch_active}
              phase1Disabled={true}
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
