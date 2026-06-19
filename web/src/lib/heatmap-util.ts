/**
 * heatmap-util.ts — tiny pure helpers for the holdings PnL heatmap.
 *
 * The heatmap reuses existing primitives for layout (`treemap.ts`) and color
 * (`chart-palette.ts`). The only extra math it needs is the symmetric scale
 * bound: the largest absolute daily move across all holdings, which normalizes
 * the diverging (red=up / blue=down) color ramp so the extremes map to the
 * biggest mover in either direction.
 *
 * Purity: no React, no DOM, no clock — deterministic from its arguments.
 */

/**
 * Maximum absolute value across `values` (0 for an empty array).
 *
 * Used to normalize a diverging color scale to a symmetric ±max range so that
 * `+x` and `-x` get equal color intensity. `maxAbs([])` is 0, which callers
 * treat as "no spread" → neutral midpoint for every tile.
 *
 * @param values Signed magnitudes (e.g. today's % change per holding).
 * @returns The largest |value|, or 0 when `values` is empty.
 */
export function maxAbs(values: number[]): number {
  let max = 0;
  for (const v of values) {
    const a = Math.abs(v);
    if (a > max) max = a;
  }
  return max;
}
