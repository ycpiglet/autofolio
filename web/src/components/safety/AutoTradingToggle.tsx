"use client";

import { useState } from "react";
import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { ConfirmModal } from "./ConfirmModal";
import { cn } from "@/lib/utils";

interface AutoTradingToggleProps {
  /** Current auto-trading state from /api/engine/status */
  enabled?: boolean;
  /** Phase 1: always disabled — no POST until Phase 3 */
  phase1Disabled?: boolean;
  className?: string;
}

export function AutoTradingToggle({
  enabled = false,
  phase1Disabled = true,
  className,
}: AutoTradingToggleProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);

  function handleToggleClick() {
    // Only reachable in Phase 3+ when phase1Disabled = false
    if (!phase1Disabled) {
      setConfirmOpen(true);
    }
  }

  return (
    <>
      <Tooltip.Provider>
        <Tooltip.Root>
          <Tooltip.Trigger
            render={
              <Button
                variant={enabled ? "default" : "outline"}
                size="sm"
                disabled={phase1Disabled}
                aria-disabled={phase1Disabled}
                aria-label={`자동매매 ${enabled ? "ON" : "OFF"}${phase1Disabled ? " (Phase 3에서 활성화)" : ""}`}
                onClick={handleToggleClick}
                className={cn("min-w-[90px]", className)}
              >
                자동매매 {enabled ? "ON" : "OFF"}
              </Button>
            }
          />
          {phase1Disabled && (
            <Tooltip.Positioner>
              <Tooltip.Popup className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-md">
                Phase 3에서 활성화
              </Tooltip.Popup>
            </Tooltip.Positioner>
          )}
        </Tooltip.Root>
      </Tooltip.Provider>

      <ConfirmModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title={enabled ? "자동매매 OFF 확인" : "자동매매 ON 확인"}
        description={
          enabled
            ? "자동매매를 중단합니다. 진행 중인 주문은 취소되지 않습니다."
            : "자동매매를 활성화합니다. 설정된 조건에 따라 자동으로 주문이 실행됩니다."
        }
        confirmLabel={enabled ? "비활성화" : "활성화"}
        onConfirm={() => {
          // Phase 3: call POST /api/engine/auto-trading here
        }}
        dangerous={!enabled}
      />
    </>
  );
}
