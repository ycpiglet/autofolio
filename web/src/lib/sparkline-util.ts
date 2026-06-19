/**
 * sparkline-util.ts — pure, testable helpers for the inline table-cell sparkline.
 *
 * No React / DOM here. This derives the KR-convention trend color for a tiny
 * inline sparkline from the first-vs-last value of its series. The chart
 * component (components/domain/Sparkline.tsx) consumes this and passes the
 * color as the SVG stroke.
 *
 * KR PnL convention (mirrors pnlColor in format.ts SSR fallbacks, and
 * equityLineColor in equity-series.ts):
 *   상승=빨강 #F04452 · 하락=파랑 #3182F6 · 보합/데이터부족=회색 #8B95A1
 */

/** Up (rising trend) — 빨강. */
export const SPARKLINE_UP_COLOR = "#F04452";
/** Down (falling trend) — 파랑. */
export const SPARKLINE_DOWN_COLOR = "#3182F6";
/** Flat / insufficient data — 회색. */
export const SPARKLINE_FLAT_COLOR = "#8B95A1";

/**
 * KR-convention trend color for a sparkline series, judged by endpoints.
 *
 * With fewer than 2 points there is no trend to draw, so this returns the
 * muted gray. Otherwise it compares the last value to the first:
 *   - last >= first → rising → #F04452 (빨강/up). Note equality counts as up,
 *     matching the inclusive ">=" boundary in the spec.
 *   - last <  first → falling → #3182F6 (파랑/down).
 *
 * `first` is values[0] and `last` is values[values.length - 1].
 */
export function sparklineTrendColor(values: number[]): string {
  if (values.length < 2) return SPARKLINE_FLAT_COLOR;
  const first = values[0];
  const last = values[values.length - 1];
  return last >= first ? SPARKLINE_UP_COLOR : SPARKLINE_DOWN_COLOR;
}
