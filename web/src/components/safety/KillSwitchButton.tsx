"use client";

import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface KillSwitchButtonProps {
  /** Whether the kill switch is currently active (from /api/engine/status) */
  isActive?: boolean;
  /** Phase 1: always disabled — no POST until Phase 3 */
  phase1Disabled?: boolean;
  className?: string;
}

export function KillSwitchButton({
  isActive = false,
  phase1Disabled = true,
  className,
}: KillSwitchButtonProps) {
  const label = isActive ? "중단됨" : "자동매매 중단";
  const disabledReason = phase1Disabled ? "Phase 3에서 활성화" : undefined;

  return (
    <Tooltip.Provider>
      <Tooltip.Root>
        <Tooltip.Trigger
          render={
            <Button
              variant="destructive"
              size="sm"
              disabled={phase1Disabled}
              aria-disabled={phase1Disabled}
              aria-label={label + (disabledReason ? ` (${disabledReason})` : "")}
              className={cn(
                isActive && "opacity-50",
                className
              )}
            >
              {isActive ? "⛔ 중단됨" : "🛑 " + label}
            </Button>
          }
        />
        {disabledReason && (
          <Tooltip.Positioner>
            <Tooltip.Popup className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-md">
              {disabledReason}
            </Tooltip.Popup>
          </Tooltip.Positioner>
        )}
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
