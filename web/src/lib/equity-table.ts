/**
 * equity-table.ts — pure, testable mapping from a FastAPI TableResponse to the
 * columnar EquityPoint shape the uPlot equity chart consumes.
 *
 * No React / DOM here. The backend serves the asset curve as a TableResponse
 * whose rows carry a "date" ("YYYY-MM-DD") column and a "자산" (numeric) column;
 * this turns those rows into sorted unix-seconds samples for EquityChartUplot.
 */

import type { TableResponse } from "@/lib/api";
import type { EquityPoint } from "./equity-series";

/**
 * Map a TableResponse to ascending-by-time EquityPoints.
 *
 * Each row becomes { t: floor(Date.parse(date) / 1000), v: Number(value ?? 0) }.
 * Rows whose date is empty/invalid (NaN timestamp) are dropped. The result is
 * sorted ascending by `t`. Undefined or empty input yields [].
 */
export function tableToEquityPoints(
  data: TableResponse | undefined,
  dateCol = "date",
  valueCol = "자산",
): EquityPoint[] {
  if (!data || !data.rows || data.rows.length === 0) return [];

  const points: EquityPoint[] = [];
  for (const row of data.rows) {
    const t = Math.floor(Date.parse(String(row[dateCol])) / 1000);
    if (Number.isNaN(t)) continue; // drop empty/invalid date rows
    points.push({ t, v: Number(row[valueCol] ?? 0) });
  }

  points.sort((a, b) => a.t - b.t);
  return points;
}
