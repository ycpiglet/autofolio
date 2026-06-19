/**
 * candle-table.ts — pure, testable mapping from a FastAPI OHLC `TableResponse`
 * to the `Candle[]` shape consumed by CandleChartKline / candle-series.
 *
 * No React / DOM / charting imports: this is the column-detection + time-parsing
 * logic that used to live inline in CandleChart.tsx (lightweight-charts era),
 * lifted out so it can be unit-tested and reused by the KLineCharts engine.
 *
 * IMPORTANT — units: `Candle.t` is a unix timestamp in **milliseconds** (matches
 * KLineCharts' `timestamp`), NOT seconds. (EquityPoint.t elsewhere is seconds —
 * do not confuse the two.) A "YYYY-MM-DD" date parses via Date.parse; a
 * "YYYY-MM-DD HH:mm" / ISO datetime parses by normalising the space to "T".
 */

import type { TableResponse } from "@/lib/api";
import type { Candle } from "./candle-series";

/**
 * Detect the column name to use for a field: the first of `preferred` present
 * in `columns`, else the column at `fallbackIndex` (by position), else
 * `undefined` when the table has too few columns.
 */
function pickColumn(
  columns: string[],
  preferred: string[],
  fallbackIndex: number,
): string | undefined {
  return columns.find((c) => preferred.includes(c)) ?? columns[fallbackIndex];
}

/**
 * Parse a raw time cell into unix **milliseconds**.
 * - "YYYY-MM-DD" (date only) → Date.parse(raw)
 * - "YYYY-MM-DD HH:mm" / ISO → new Date(raw.replace(" ", "T")).getTime()
 * Returns NaN for anything unparseable (caller drops those rows).
 */
function parseTimeMs(raw: string): number {
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return Date.parse(raw);
  }
  return new Date(raw.replace(" ", "T")).getTime();
}

/**
 * Map a FastAPI OHLC `TableResponse` to `Candle[]` (t in unix ms), sorted
 * ascending by time. Rows whose time cannot be parsed are dropped.
 * Undefined / empty input → [].
 */
export function tableToCandles(data: TableResponse | undefined): Candle[] {
  if (!data || data.rows.length === 0) return [];

  const { columns } = data;
  const timeCol = pickColumn(columns, ["time", "date", "시간"], 0);
  const openCol = pickColumn(columns, ["open", "시가"], 1);
  const highCol = pickColumn(columns, ["high", "고가"], 2);
  const lowCol = pickColumn(columns, ["low", "저가"], 3);
  const closeCol = pickColumn(columns, ["close", "종가"], 4);

  const candles: Candle[] = [];
  for (const row of data.rows) {
    const t = parseTimeMs(String((timeCol && row[timeCol]) ?? ""));
    if (!Number.isFinite(t)) continue;
    candles.push({
      t,
      o: Number((openCol && row[openCol]) ?? 0),
      h: Number((highCol && row[highCol]) ?? 0),
      l: Number((lowCol && row[lowCol]) ?? 0),
      c: Number((closeCol && row[closeCol]) ?? 0),
    });
  }

  candles.sort((a, b) => a.t - b.t);
  return candles;
}
