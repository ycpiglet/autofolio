// web/src/components/domain/OrderForm.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ConfirmModal } from "@/components/safety/ConfirmModal";
import {
  postCondition,
  ApiError,
  type ConditionPayload,
  type ConditionResponse,
  type NeedsAckResponse,
} from "@/lib/api";
import { cn } from "@/lib/utils";

type FormStatus =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; condition: ConditionResponse }
  | { kind: "disclosure"; message: string }
  | { kind: "rejected"; message: string }
  | { kind: "error"; message: string };

interface OrderFormProps {
  /** Called after successful condition creation so parent can refresh the list */
  onCreated?: () => void;
  className?: string;
  /** Optional prefill (e.g. from an agent research proposal). Pre-fills the
   *  form fields only — it does NOT auto-submit. */
  initialSymbol?: string;
  initialSide?: "BUY" | "SELL";
  initialTargetPrice?: string;
  initialQuantity?: string;
}

export function OrderForm({
  onCreated,
  className,
  initialSymbol = "",
  initialSide = "BUY",
  initialTargetPrice = "",
  initialQuantity = "",
}: OrderFormProps) {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [side, setSide] = useState<"BUY" | "SELL">(initialSide);
  const [targetPrice, setTargetPrice] = useState(initialTargetPrice);
  const [quantity, setQuantity] = useState(initialQuantity);
  const [status, setStatus] = useState<FormStatus>({ kind: "idle" });

  // 2-step ack state
  const [pendingAck, setPendingAck] = useState<{
    verdict: string;
    ack_token: string;
    payload: ConditionPayload;
  } | null>(null);

  async function submit(payload: ConditionPayload) {
    setStatus({ kind: "submitting" });
    try {
      const result = await postCondition(payload);
      setStatus({ kind: "success", condition: result });
      onCreated?.();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          const body = err.body as NeedsAckResponse;
          // Show CAUTION modal — do not auto-acknowledge
          setPendingAck({ verdict: body.verdict, ack_token: body.ack_token, payload });
          setStatus({ kind: "idle" });
          return;
        }
        if (err.status === 422) {
          const body = err.body as { detail?: string; reason?: string };
          const msg = body.detail ?? body.reason ?? "요청이 거부되었습니다.";
          const isDisclosure = msg.includes("공시") || msg.includes("disclosure");
          setStatus(isDisclosure ? { kind: "disclosure", message: msg } : { kind: "rejected", message: msg });
          return;
        }
        setStatus({ kind: "error", message: `서버 오류: ${err.message}` });
        return;
      }
      setStatus({ kind: "error", message: "알 수 없는 오류가 발생했습니다." });
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const price = parseFloat(targetPrice);
    const qty = parseInt(quantity, 10);
    if (!symbol.trim() || isNaN(price) || isNaN(qty) || qty < 1) return;

    const payload: ConditionPayload = {
      symbol: symbol.trim().toUpperCase(),
      side,
      target_price: price,
      quantity: qty,
    };
    void submit(payload);
  }

  async function handleAckConfirm() {
    if (!pendingAck) return;
    const payload: ConditionPayload = {
      ...pendingAck.payload,
      ack_token: pendingAck.ack_token,
    };
    setPendingAck(null);
    await submit(payload);
  }

  const isSubmitting = status.kind === "submitting";

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className={cn("space-y-4 rounded-xl border border-border p-4", className)}
        aria-label="매매 조건 등록"
      >
        <h2 className="text-sm font-medium text-foreground">조건 등록 (예약 주문)</h2>

        {/* Symbol */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="order-symbol">종목 코드</Label>
          <Input
            id="order-symbol"
            placeholder="예: 005930"
            value={symbol}
            onChange={(e) => setSymbol((e.target as HTMLInputElement).value)}
            disabled={isSubmitting}
            required
          />
        </div>

        {/* Side */}
        <div className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-foreground">매수/매도</span>
          <div className="flex gap-2">
            <Button
              type="button"
              variant={side === "BUY" ? "default" : "outline"}
              size="sm"
              onClick={() => setSide("BUY")}
              aria-pressed={side === "BUY"}
            >
              매수
            </Button>
            <Button
              type="button"
              variant={side === "SELL" ? "destructive" : "outline"}
              size="sm"
              onClick={() => setSide("SELL")}
              aria-pressed={side === "SELL"}
            >
              매도
            </Button>
          </div>
        </div>

        {/* Target price */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="order-price">목표가 (원)</Label>
          <Input
            id="order-price"
            type="number"
            min={1}
            step={1}
            placeholder="예: 74000"
            value={targetPrice}
            onChange={(e) => setTargetPrice((e.target as HTMLInputElement).value)}
            disabled={isSubmitting}
            required
          />
        </div>

        {/* Quantity */}
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="order-qty">수량 (주)</Label>
          <Input
            id="order-qty"
            type="number"
            min={1}
            step={1}
            placeholder="예: 10"
            value={quantity}
            onChange={(e) => setQuantity((e.target as HTMLInputElement).value)}
            disabled={isSubmitting}
            required
          />
        </div>

        {/* Submit */}
        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "등록 중…" : "조건 등록"}
        </Button>

        {/* Status feedback */}
        {status.kind === "success" && (
          <p role="status" className="rounded-lg bg-muted p-3 text-sm text-foreground">
            조건이 등록되었습니다. (ID: {status.condition.id})
          </p>
        )}
        {status.kind === "disclosure" && (
          <p role="alert" className="rounded-lg border border-amber-400/40 bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
            공시 차단: {status.message}
          </p>
        )}
        {status.kind === "rejected" && (
          <p role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            거부됨: {status.message}
          </p>
        )}
        {status.kind === "error" && (
          <p role="alert" className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
            오류: {status.message}
          </p>
        )}
      </form>

      {/* 2-step acknowledgement CAUTION modal */}
      <ConfirmModal
        open={pendingAck !== null}
        onOpenChange={(open) => { if (!open) setPendingAck(null); }}
        title="⚠️ 주의 — 검토 필요"
        description={pendingAck?.verdict ?? ""}
        confirmLabel="확인 후 제출"
        cancelLabel="취소"
        onConfirm={() => { void handleAckConfirm(); }}
        dangerous
      />
    </>
  );
}
