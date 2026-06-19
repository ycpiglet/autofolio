/**
 * holdings-treemap.ts — pure, testable mapping from a FastAPI holdings
 * TableResponse to the TreemapItem[] the AllocationTreemap consumes.
 *
 * No React / DOM here. The holdings endpoint serves columns that are
 * backend-driven (names and order are NOT fixed), so this DETECTS the label
 * and size columns by name pattern rather than hardcoding them, and degrades
 * gracefully (returns []) when no usable numeric size column is present — the
 * caller then hides the section entirely.
 */

import type { TableResponse } from "@/lib/api";
import type { TreemapItem } from "./treemap";

/** Column whose values name the holding (security/ticker). First match wins. */
const LABEL_COL_RE = /종목|name|symbol|티커|ticker/i;
/** Column whose values size the tile (value/weight). First numeric match wins. */
const SIZE_COL_RE = /평가금액|평가액|금액|비중|weight|평가|value|시가총액/i;

/** True when `v` can be read as a finite number (handles numeric strings). */
function isNumericValue(v: unknown): boolean {
  if (typeof v === "number") return Number.isFinite(v);
  if (typeof v === "string" && v.trim() !== "") return Number.isFinite(Number(v));
  return false;
}

/**
 * Map a holdings TableResponse to TreemapItems for AllocationTreemap.
 *
 * Detection (columns are backend-driven, so nothing is hardcoded):
 * - Label column: the first column whose name matches {@link LABEL_COL_RE},
 *   else the first column.
 * - Size column: the first column whose name matches {@link SIZE_COL_RE} AND
 *   whose row values are numeric. If none qualifies → return [] (the section
 *   hides, since there is nothing meaningful to size tiles by).
 *
 * Each row becomes `{ label: String(row[labelCol] ?? ""), value: Number(row[sizeCol]) }`,
 * keeping only finite `value > 0` with a non-empty label. The result is NOT
 * sorted — AllocationTreemap/layoutTreemap sorts internally. Undefined/empty
 * input yields [].
 *
 * @param data Holdings TableResponse (columns + rows), or undefined.
 * @returns TreemapItems to plot, or [] for degenerate / unusable input.
 */
export function holdingsToTreemapItems(
  data: TableResponse | undefined,
): TreemapItem[] {
  if (!data || !data.columns || !data.rows || data.rows.length === 0) return [];

  const { columns, rows } = data;
  if (columns.length === 0) return [];

  // Detect the label column: first name-like column, else the first column.
  const labelCol = columns.find((c) => LABEL_COL_RE.test(c)) ?? columns[0];

  // Detect the size column: first value-like column whose values are numeric.
  const sizeCol = columns.find(
    (c) => SIZE_COL_RE.test(c) && rows.some((row) => isNumericValue(row[c])),
  );
  if (sizeCol === undefined) return []; // graceful: caller hides the section.

  const items: TreemapItem[] = [];
  for (const row of rows) {
    const label = String(row[labelCol] ?? "");
    const value = Number(row[sizeCol]);
    if (label !== "" && Number.isFinite(value) && value > 0) {
      items.push({ label, value });
    }
  }
  return items;
}
