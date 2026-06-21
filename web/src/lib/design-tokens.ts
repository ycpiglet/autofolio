/**
 * TypeScript token bridge for libraries that need concrete color strings.
 *
 * CSS-first tokens live in app/globals.css. Canvas/SVG chart libraries often
 * need serializable values, so repeatable chart/status values are mirrored here.
 */

export const chartColors = {
  primary: "#3182F6",
  negative: "#F04452",
  positive: "#34C759",
  warning: "#FF9500",
  neutral: "#8E8E93",
  textMuted: "#8B95A1",
  accentPurple: "#AF52DE",
  accentCyan: "#5AC8FA",
  accentYellow: "#FFCC00",
  grid: "#DDE1E7",
} as const;

export const chartSeriesPalette = [
  chartColors.primary,
  chartColors.negative,
  chartColors.positive,
  chartColors.warning,
  chartColors.neutral,
  chartColors.accentPurple,
  chartColors.accentCyan,
  chartColors.accentYellow,
] as const;

export const compactChartSeriesPalette = [
  chartColors.primary,
  chartColors.negative,
  chartColors.positive,
  chartColors.warning,
  chartColors.accentPurple,
  chartColors.accentCyan,
] as const;

export const lightweightChartTheme = {
  background: "transparent",
  textColor: chartColors.textMuted,
  gridColor: chartColors.grid,
  borderColor: chartColors.grid,
} as const;

export const candleSeriesColors = {
  up: chartColors.negative,
  down: chartColors.primary,
} as const;

export const equityAreaColors = {
  line: chartColors.primary,
  topFill: "rgba(49, 130, 246, 0.3)",
  bottomFill: "rgba(49, 130, 246, 0.0)",
} as const;

export const pnlColorTokens = {
  kr: {
    up: chartColors.negative,
    down: chartColors.primary,
  },
  western: {
    up: chartColors.positive,
    down: chartColors.negative,
  },
  flat: chartColors.textMuted,
} as const;
