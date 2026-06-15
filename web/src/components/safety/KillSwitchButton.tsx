"use client";

import { useState } from "react";
import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { ConfirmModal } from "./ConfirmModal";
import { postKillSwitch } from "@/lib/api";
import { cn } from "@/lib/utils";

interface KillSwitchButtonProps {
  /** Whether the kill switch is currently active (from /api/engine/status) */
  isActive?: boolean;
  /** Set to true only for Phase 1 placeholder mode */
  phase1Disabled?: boolean;
  /** Called after a successful POST so parent can refresh engine status */
  onActivated?: () => void;
  className?: string;
}

export function KillSwitchButton({
  isActive = false,
  phase1Disabled = false,
  onActivated,
  className,
}: KillSwitchButtonProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);

  async function handleConfirm() {
    setPending(true);
    setPostError(null);
    try {
      await postKillSwitch(true);
      onActivated?.();
    } catch (err) {
      setPostError(err instanceof Error ? err.message : "알 수 없는 오류");
    } finally {
      setPending(false);
    }
  }

  const label = isActive ? "중단됨" : "자동매매 중단";

  return (
    <>
      <Tooltip.Provider>
        <Tooltip.Root>
          <Tooltip.Trigger
            render={
              <Button
                variant="destructive"
                size="sm"
                disabled={phase1Disabled || pending}
                aria-disabled={phase1Disabled || pending}
                aria-label={label}
                onClick={() => !phase1Disabled && setConfirmOpen(true)}
                className={cn(isActive && "opacity-50", className)}
              >
                {isActive ? "⛔ 중단됨" : "🛑 " + label}
              </Button>
            }
          />
          {phase1Disabled && (
            <Tooltip.Portal>
              <Tooltip.Positioner>
                <Tooltip.Popup className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-md">
                  Phase 3에서 활성화
                </Tooltip.Popup>
              </Tooltip.Positioner>
            </Tooltip.Portal>
          )}
        </Tooltip.Root>
      </Tooltip.Provider>

      {postError && (
        <p role="alert" className="mt-1 text-xs text-destructive">
          중단 실패 — 재시도: {postError}
        </p>
      )}

      <ConfirmModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="자동매매를 즉시 중단합니까?"
        description="킬스위치를 활성화하면 자동매매가 즉시 중단됩니다. 진행 중인 주문은 취소되지 않습니다."
        confirmLabel="중단"
        cancelLabel="취소"
        onConfirm={handleConfirm}
        dangerous
      />
    </>
  );
}
