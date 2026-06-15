"use client";

import { useState } from "react";
import { Tooltip } from "@base-ui/react/tooltip";
import { Button } from "@/components/ui/button";
import { ConfirmModal } from "./ConfirmModal";
import { postAutoTrading } from "@/lib/api";
import { cn } from "@/lib/utils";

interface AutoTradingToggleProps {
  /** Current auto-trading state from /api/engine/status */
  enabled?: boolean;
  /** Set to true only for Phase 1 placeholder mode */
  phase1Disabled?: boolean;
  /** Called after successful POST so parent can refresh status */
  onToggled?: () => void;
  className?: string;
}

export function AutoTradingToggle({
  enabled = false,
  phase1Disabled = false,
  onToggled,
  className,
}: AutoTradingToggleProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);

  async function handleConfirm() {
    setPending(true);
    setPostError(null);
    try {
      await postAutoTrading(!enabled);
      onToggled?.();
    } catch (err) {
      setPostError(err instanceof Error ? err.message : "알 수 없는 오류");
    } finally {
      setPending(false);
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
                disabled={phase1Disabled || pending}
                aria-disabled={phase1Disabled || pending}
                aria-label={`자동매매 ${enabled ? "ON" : "OFF"}${phase1Disabled ? " (Phase 3에서 활성화)" : ""}`}
                onClick={() => !phase1Disabled && setConfirmOpen(true)}
                className={cn("min-w-[90px]", className)}
              >
                자동매매 {enabled ? "ON" : "OFF"}
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
          자동매매 변경 실패: {postError}
        </p>
      )}

      <ConfirmModal
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title={enabled ? "자동매매 OFF 확인" : "자동매매 ON 확인"}
        description={
          enabled
            ? "자동매매를 중단합니다. 진행 중인 주문은 취소되지 않습니다."
            : "⚠️ 경고: 자동매매를 활성화하면 설정된 조건에 따라 실제 주문이 자동 실행됩니다. 반드시 리스크 한도를 확인하세요."
        }
        confirmLabel={enabled ? "비활성화" : "활성화"}
        cancelLabel="취소"
        onConfirm={handleConfirm}
        dangerous={!enabled}
      />
    </>
  );
}
