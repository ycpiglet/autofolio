/**
 * candle-series.ts — pure, testable helpers for the K-line candlestick chart.
 *
 * No React / DOM / klinecharts import here: these transform OHLCV candle data
 * into the shape KLineCharts v10 expects (`KLineData`) and expose the
 * KR-convention candle colors. The chart component (CandleChartKline.tsx)
 * consumes these.
 *
 * KR PnL convention (mirrors pnlColor in format.ts, SSR values):
 *   상승=빨강 #F04452 · 하락=파랑 #3182F6 · 보합=회색 #8B95A1
 * This is the OPPOSITE of KLineCharts' Western default (up=green/down=red),
 * so CandleChartKline applies KR_CANDLE_COLORS to the chart's candle styles.
 */

/**
 * A single OHLCV candle.
 *
 * `t` is a unix timestamp in **milliseconds** (matches KLineCharts' `timestamp`
 * field, which is also unix ms). `v` (volume) is optional.
 */
export interface Candle {
  /** Unix timestamp in milliseconds. */
  t: number;
  /** Open price. */
  o: number;
  /** High price. */
  h: number;
  /** Low price. */
  l: number;
  /** Close price. */
  c: number;
  /** Volume (optional). */
  v?: number;
}

/**
 * The data shape KLineCharts v10 consumes (a subset of its `KLineData`):
 * `{ timestamp, open, high, low, close, volume }`, timestamp in unix ms.
 *
 * The `[key: string]: unknown` index signature mirrors KLineCharts' own
 * `KLineData`, so a `KlineDatum[]` is assignable to `KLineData[]` without
 * importing klinecharts into this pure module.
 */
export interface KlineDatum {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  [key: string]: unknown;
}

/**
 * Map OHLCV candles to KLineCharts' `KLineData` shape, preserving order.
 * `volume` is only included when the candle carries one. Empty input → [].
 */
export function toKlineData(candles: Candle[]): KlineDatum[] {
  return candles.map((candle) => {
    const datum: KlineDatum = {
      timestamp: candle.t,
      open: candle.o,
      high: candle.h,
      low: candle.l,
      close: candle.c,
    };
    if (candle.v !== undefined) {
      datum.volume = candle.v;
    }
    return datum;
  });
}

/**
 * KR-convention candlestick colors (up=빨강, down=파랑, 보합=회색).
 * Exported for reuse in the chart's style config and for tests.
 */
export const KR_CANDLE_COLORS = {
  up: "#F04452",
  down: "#3182F6",
  noChange: "#8B95A1",
} as const;
