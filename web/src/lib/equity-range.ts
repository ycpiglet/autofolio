/**
 * equity-range.ts — pure, testable helpers for the equity-chart period selector.
 *
 * No React / DOM here: this defines the selectable time ranges (1D…ALL) and a
 * windowing function that slices an equity series down to the chosen range.
 * The ranged chart component (EquityChartRanged.tsx) consumes these alongside
 * equity-series.ts (periodReturnPct / equityLineColor).
 */

import type { EquityPoint } from "./equity-series";

/** Selectable equity-chart time ranges, shortest → longest (ALL = full series). */
export type EquityRange = "1D" | "1W" | "1M" | "3M" | "1Y" | "ALL";

/** Ordered list of ranges for rendering the segmented control. */
export const EQUITY_RANGES: readonly EquityRange[] = [
  "1D",
  "1W",
  "1M",
  "3M",
  "1Y",
  "ALL",
];

/**
 * Window length in seconds per range. ALL is open-ended (no lower bound).
 * Months/years use round calendar approximations (30d / 90d / 365d) since the
 * series carries unix-second timestamps, not calendar dates.
 */
const RANGE_SECONDS: Record<Exclude<EquityRange, "ALL">, number> = {
  "1D": 86_400, // 1 day
  "1W": 604_800, // 7 days
  "1M": 2_592_000, // 30 days
  "3M": 7_776_000, // 90 days
  "1Y": 31_536_000, // 365 days
};

/**
 * Slice `points` down to those within the window ending at the anchor time.
 *
 * The anchor is `nowSec` when provided, otherwise the LATEST point's `t`. Points
 * are kept when `t >= anchor - window`. Input is assumed sorted ascending by `t`.
 *
 * - `range === "ALL"` returns all points (no lower bound).
 * - Empty input returns `[]`.
 *
 * @param points  equity samples (unix seconds in `t`), ascending by `t`
 * @param range   selected window
 * @param nowSec  optional explicit anchor (unix seconds); defaults to last point's `t`
 */
export function sliceByRange(
  points: EquityPoint[],
  range: EquityRange,
  nowSec?: number,
): EquityPoint[] {
  if (points.length === 0) return [];
  if (range === "ALL") return points.slice();

  const anchor = nowSec ?? points[points.length - 1].t;
  const cutoff = anchor - RANGE_SECONDS[range];
  return points.filter((p) => p.t >= cutoff);
}
