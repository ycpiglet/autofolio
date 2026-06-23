/**
 * chart-palette.ts — colorblind-safe chart color tokens for Autofolio.
 *
 * Keeps PnL *semantic* colors (KR: 상승=빨강, 하락=파랑 — see format.ts/globals.css)
 * separate from *categorical* and *sequential* chart colors so series colors never
 * collide with up/down meaning. Source/rationale:
 * docs/research/dataviz-libraries-and-color-expanded.md
 */

// ── categorical (Okabe-Ito CUD, colorblind-safe) ───────────────────────────
export const categoricalPalette = {
  catBlue: "#0072B2", // brand-aligned anchor, CVD-safe
  catOrange: "#E69F00",
  catGreen: "#009E73", // distinct from PnL green (#34C759)
  catPurple: "#CC79A7",
  catSky: "#56B4E9", // ⚠ low contrast on white → fill+border only
  catVermilion: "#D55E00",
  catYellow: "#F0E442", // ⚠ very low contrast → dark fills only
} as const;

export const categoricalOrder: readonly string[] = [
  categoricalPalette.catBlue,
  categoricalPalette.catOrange,
  categoricalPalette.catGreen,
  categoricalPalette.catPurple,
  categoricalPalette.catVermilion,
  categoricalPalette.catSky,
  categoricalPalette.catYellow,
];

// ── PnL diverging ramp (KR: red=up, blue=down) ─────────────────────────────
// ColorBrewer RdBu 5-class, CVD-safe, neutral midpoint. Index 0=큰 하락 … 4=큰 상승.
export const pnlDivergingRampKR: readonly string[] = [
  "#0571b0", // 큰 하락
  "#92c5de",
  "#f7f7f7", // 보합(중립)
  "#f4a582",
  "#ca0020", // 큰 상승
];

/**
 * Map a PnL value (clamped to ±maxAbs) to a 5-class diverging color.
 * Pair with a non-color signal (▲/▼, +/−) — color alone fails WCAG 1.4.1.
 */
export function pnlDivergingColor(value: number, maxAbs: number): string {
  if (maxAbs <= 0 || value === 0) return pnlDivergingRampKR[2];
  const t = Math.max(-1, Math.min(1, value / maxAbs));
  const idx = Math.round((t + 1) * 2);
  return pnlDivergingRampKR[idx];
}

// ── sequential (treemap/heatmap intensity, unsigned magnitude) ─────────────
export const sequentialViridis: readonly string[] = [
  "#440154", "#3B528B", "#21908C", "#5DC863", "#FDE725",
]; // CC0, perceptually uniform
export const sequentialBlues: readonly string[] = [
  "#eff3ff", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594",
]; // brand-aligned single-hue

/** Map a normalized value t∈[0,1] to a discrete sequential color. */
export function sequentialColor(
  t: number,
  ramp: readonly string[] = sequentialViridis,
): string {
  const x = Math.max(0, Math.min(1, t));
  return ramp[Math.round(x * (ramp.length - 1))];
}

// ── dark-mode brand blue (Radix blue dark scale) ───────────────────────────
// light = brand #3182F6 (≈ Tailwind blue-500); dark maps to these for contrast.
export const brandBlueDark = {
  solid9: "#0090ff",
  solid10: "#3b9eff",
  text11: "#70b8ff",
  title12: "#c2e6ff",
  bg2: "#111927",
  border6: "#104d87",
} as const;
