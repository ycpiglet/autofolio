/**
 * treemap.ts — pure, deterministic treemap layout (slice-and-dice).
 *
 * Computes axis-aligned rectangles ("tiles") whose AREAS are proportional to
 * each item's `value`, packed to fill a `width × height` box. Used to visualize
 * portfolio concentration: bigger area = bigger weight (see AllocationTreemap).
 *
 * Algorithm: slice-and-dice. Items are sorted by value descending, then the box
 * is split with cuts that alternate orientation by recursion depth (depth 0 =
 * vertical cuts → tiles laid left→right; depth 1 = horizontal cuts; …). Each
 * tile receives a slice of the current box proportional to its share of the
 * remaining value. This is intentionally simple and exactly verifiable: the
 * union of tiles tiles the box with no gaps or overlaps, so the areas sum to
 * `width × height` (within floating-point epsilon) for all-positive input.
 *
 * Purity: no React, no DOM, no clock — deterministic from its arguments.
 */

/** One input datum: a label and its non-negative magnitude. */
export interface TreemapItem {
  label: string;
  value: number;
}

/** A laid-out rectangle. `(x, y)` is the top-left corner; `w`/`h` are size. */
export interface TreemapTile {
  label: string;
  value: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

/**
 * Recursively slice `items` (already sorted desc, all values > 0) into `box`,
 * appending tiles to `out`. `horizontal` controls the cut orientation at this
 * depth: when true the box is split top→bottom (rows), otherwise left→right
 * (columns). Orientation alternates each level so tiles stay reasonably square.
 */
function slice(
  items: readonly TreemapItem[],
  x: number,
  y: number,
  w: number,
  h: number,
  horizontal: boolean,
  out: TreemapTile[],
): void {
  if (items.length === 0) return;

  if (items.length === 1) {
    const item = items[0];
    out.push({ label: item.label, value: item.value, x, y, w, h });
    return;
  }

  const total = items.reduce((sum, it) => sum + it.value, 0);
  // Degenerate guard: if every value is zero we cannot proportion the box;
  // callers strip value <= 0 first, so this only protects against bad input.
  if (total <= 0) return;

  // Split the run into a head (first item) and the rest, allocating space by
  // value share along the active axis. Recursing on the remainder with flipped
  // orientation yields the classic slice-and-dice tiling.
  const head = items[0];
  const fraction = head.value / total;

  if (horizontal) {
    const headH = h * fraction;
    out.push({ label: head.label, value: head.value, x, y, w, h: headH });
    slice(items.slice(1), x, y + headH, w, h - headH, false, out);
  } else {
    const headW = w * fraction;
    out.push({ label: head.label, value: head.value, x, y, w: headW, h });
    slice(items.slice(1), x + headW, y, w - headW, h, true, out);
  }
}

/**
 * Lay out `items` as a treemap filling a `width × height` box.
 *
 * Behavior / guarantees (covered by treemap.test.ts):
 * - Empty `items`, or non-positive `width`/`height`, returns `[]`.
 * - Items with `value <= 0` are OMITTED (they would occupy zero area and only
 *   add visual noise). If nothing remains after filtering, returns `[]`.
 * - Tiles are returned in value-descending order; labels/values are preserved.
 * - Every tile lies within `[0, width] × [0, height]`.
 * - For all-positive input the tile areas sum to `width × height` (within fp
 *   epsilon), because the tiles partition the box without gaps or overlaps.
 *
 * @param items  Data to lay out; `value` is treated as unsigned magnitude.
 * @param width  Box width in user units (> 0 required).
 * @param height Box height in user units (> 0 required).
 * @returns Tiles in value-descending order, or `[]` for degenerate input.
 */
export function layoutTreemap(
  items: TreemapItem[],
  width: number,
  height: number,
): TreemapTile[] {
  if (width <= 0 || height <= 0) return [];

  const positive = items
    .filter((it) => it.value > 0)
    .sort((a, b) => b.value - a.value);

  if (positive.length === 0) return [];

  const out: TreemapTile[] = [];
  // Start with vertical cuts (columns) so the largest tile anchors the left.
  slice(positive, 0, 0, width, height, false, out);
  return out;
}
