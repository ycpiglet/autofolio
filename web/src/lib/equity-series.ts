/**
 * equity-series.ts — pure, testable helpers for the equity-curve chart.
 *
 * No React / DOM here: these transform equity-point data into the columnar
 * shape uPlot expects and derive the KR-convention line color from the
 * period's return. The chart component (EquityChartUplot.tsx) consumes these.
 *
 * KR PnL convention (mirrors pnlColor in format.ts, SSR values):
 *   상승=빨강 #F04452 · 하락=파랑 #3182F6 · 보합=회색 #8B95A1
 */

/** A single equity-curve sample. t = unix seconds, v = value. */
export interface EquityPoint {
  t: number;
  v: number;
}

/**
 * Convert equity points to uPlot's columnar AlignedData: [xs, ys].
 * xs are taken from `t`, ys from `v`, preserving order. Empty input → [[], []].
 */
export function toUplotData(points: EquityPoint[]): [number[], number[]] {
  const xs: number[] = [];
  const ys: number[] = [];
  for (const p of points) {
    xs.push(p.t);
    ys.push(p.v);
  }
  return [xs, ys];
}

/**
 * Period return as a percentage: (last.v / first.v - 1) * 100.
 * Returns 0 for fewer than 2 points or when first.v is 0 (avoid div-by-zero).
 */
export function periodReturnPct(points: EquityPoint[]): number {
  if (points.length < 2) return 0;
  const first = points[0].v;
  const last = points[points.length - 1].v;
  if (first === 0) return 0;
  return (last / first - 1) * 100;
}

/**
 * KR-convention line color for the equity curve, by the period's sign:
 *   positive → #F04452 (빨강/up) · negative → #3182F6 (파랑/down) ·
 *   flat → #8B95A1 (회색). Mirrors format.ts pnlColor SSR fallbacks.
 */
export function equityLineColor(points: EquityPoint[]): string {
  const ret = periodReturnPct(points);
  if (ret > 0) return "#F04452";
  if (ret < 0) return "#3182F6";
  return "#8B95A1";
}
