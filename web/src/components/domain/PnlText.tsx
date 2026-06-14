import { pnlColorClass, fmtPct, fmtWon } from "@/lib/format";
import { cn } from "@/lib/utils";

interface PnlTextProps {
  /** Raw numeric value (positive = gain, negative = loss) */
  value: number;
  /** Display mode: "pct" shows +3.14%, "won" shows ₩1,234,567, "raw" shows the number as-is */
  mode?: "pct" | "won" | "raw";
  className?: string;
}

/**
 * PnlText — signed value colored per KR/Western convention.
 * Color is driven by CSS vars (`text-pnl-up` / `text-pnl-down`) so the
 * html[data-pnl="western"] toggle works without JS.
 */
export function PnlText({ value, mode = "pct", className }: PnlTextProps) {
  let display: string;
  if (mode === "pct") display = fmtPct(value);
  else if (mode === "won") display = fmtWon(value);
  else display = String(value);

  return (
    <span
      className={cn(pnlColorClass(value), "font-mono tabular-nums", className)}
      aria-label={`손익 ${display}`}
    >
      {display}
    </span>
  );
}
