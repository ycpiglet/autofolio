"use client";

import { useMemo, useState } from "react";

import { cn } from "@/lib/utils";
import { fmtPct } from "../../lib/format";
import { equityLineColor, periodReturnPct, type EquityPoint } from "../../lib/equity-series";
import {
  EQUITY_RANGES,
  sliceByRange,
  type EquityRange,
} from "../../lib/equity-range";
import { EquityChartUplot } from "./EquityChartUplot";

interface EquityChartRangedProps {
  points: EquityPoint[];
  defaultRange?: EquityRange;
  height?: number;
  className?: string;
}

/** Human-readable labels for the period-return aria-label (accessibility). */
const RANGE_LABEL: Record<EquityRange, string> = {
  "1D": "1일",
  "1W": "1주",
  "1M": "1개월",
  "3M": "3개월",
  "1Y": "1년",
  ALL: "전체",
};

/**
 * Direction glyph for the period return. Non-color cue so the sign is
 * conveyed without relying on color alone (WCAG 1.4.1).
 *   up → ▲ · down → ▼ · flat → → (—-ish neutral)
 */
function trendGlyph(ret: number): string {
  if (ret > 0) return "▲";
  if (ret < 0) return "▼";
  return "→";
}

/**
 * EquityChartRanged — period-selector wrapper around EquityChartUplot.
 *
 * A segmented control (1D/1W/1M/3M/1Y/ALL) slices the equity series to the
 * selected window; the header shows that window's return colored by the KR
 * convention (up=빨강 / down=파랑 / flat=회색) plus a ▲/▼ glyph for
 * color-independent legibility. The chart below renders the sliced series.
 *
 * Client-only ("use client") because it holds the selected-range state and
 * EquityChartUplot mounts a canvas in an effect.
 */
export function EquityChartRanged({
  points,
  defaultRange = "3M",
  height = 240,
  className,
}: EquityChartRangedProps) {
  const [range, setRange] = useState<EquityRange>(defaultRange);

  const sliced = useMemo(() => sliceByRange(points, range), [points, range]);
  const ret = useMemo(() => periodReturnPct(sliced), [sliced]);
  const retColor = useMemo(() => equityLineColor(sliced), [sliced]);
  const glyph = trendGlyph(ret);

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        {/* Period return — colored per KR convention, with a non-color glyph. */}
        <div
          className="flex items-baseline gap-1 font-mono tabular-nums"
          style={{ color: retColor }}
          aria-label={`${RANGE_LABEL[range]} 수익률 ${fmtPct(ret)}`}
          data-testid="equity-ranged-return"
        >
          <span aria-hidden="true">{glyph}</span>
          <span>{fmtPct(ret)}</span>
        </div>

        {/* Segmented range control. */}
        <div
          role="group"
          aria-label="기간 선택"
          className="inline-flex flex-wrap gap-1"
          data-testid="equity-ranged-controls"
        >
          {EQUITY_RANGES.map((r) => {
            const selected = r === range;
            return (
              <button
                key={r}
                type="button"
                onClick={() => setRange(r)}
                aria-pressed={selected}
                className={cn(
                  "rounded-lg border px-3 py-1 text-sm font-medium transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  selected
                    ? "border-primary bg-primary/10 text-foreground"
                    : "border-border text-muted-foreground hover:bg-muted",
                )}
              >
                {r}
              </button>
            );
          })}
        </div>
      </div>

      <EquityChartUplot points={sliced} height={height} />
    </div>
  );
}

export default EquityChartRanged;
