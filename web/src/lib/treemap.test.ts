import { describe, it, expect } from "vitest";

import { layoutTreemap, type TreemapItem, type TreemapTile } from "./treemap";

// Floating-point slack for area/coordinate comparisons.
const EPS = 1e-6;

/** Assert every tile sits within [0,width] × [0,height] (with fp slack). */
function expectWithinBounds(
  tiles: readonly TreemapTile[],
  width: number,
  height: number,
): void {
  for (const t of tiles) {
    expect(t.x).toBeGreaterThanOrEqual(-EPS);
    expect(t.y).toBeGreaterThanOrEqual(-EPS);
    expect(t.x + t.w).toBeLessThanOrEqual(width + EPS);
    expect(t.y + t.h).toBeLessThanOrEqual(height + EPS);
    expect(t.w).toBeGreaterThanOrEqual(-EPS);
    expect(t.h).toBeGreaterThanOrEqual(-EPS);
  }
}

const sumAreas = (tiles: readonly TreemapTile[]): number =>
  tiles.reduce((acc, t) => acc + t.w * t.h, 0);

describe("layoutTreemap — degenerate input", () => {
  it("returns [] for empty items", () => {
    expect(layoutTreemap([], 100, 100)).toEqual([]);
  });

  it("returns [] when width is zero", () => {
    expect(layoutTreemap([{ label: "a", value: 1 }], 0, 100)).toEqual([]);
  });

  it("returns [] when height is zero", () => {
    expect(layoutTreemap([{ label: "a", value: 1 }], 100, 0)).toEqual([]);
  });

  it("returns [] for negative dimensions", () => {
    expect(layoutTreemap([{ label: "a", value: 1 }], -10, 100)).toEqual([]);
    expect(layoutTreemap([{ label: "a", value: 1 }], 100, -10)).toEqual([]);
  });

  it("omits non-positive items and returns [] if none remain", () => {
    expect(
      layoutTreemap(
        [
          { label: "z", value: 0 },
          { label: "n", value: -5 },
        ],
        100,
        100,
      ),
    ).toEqual([]);
  });
});

describe("layoutTreemap — single item", () => {
  it("fills the whole box", () => {
    const tiles = layoutTreemap([{ label: "a", value: 5 }], 100, 80);
    expect(tiles).toHaveLength(1);
    const [t] = tiles;
    expect(t.label).toBe("a");
    expect(t.value).toBe(5);
    expect(t.x).toBeCloseTo(0, 6);
    expect(t.y).toBeCloseTo(0, 6);
    expect(t.w).toBeCloseTo(100, 6);
    expect(t.h).toBeCloseTo(80, 6);
  });
});

describe("layoutTreemap — two items", () => {
  it("splits area proportionally to value", () => {
    const items: TreemapItem[] = [
      { label: "big", value: 3 },
      { label: "small", value: 1 },
    ];
    const width = 200;
    const height = 100;
    const tiles = layoutTreemap(items, width, height);

    expect(tiles).toHaveLength(2);
    expectWithinBounds(tiles, width, height);

    const big = tiles.find((t) => t.label === "big")!;
    const small = tiles.find((t) => t.label === "small")!;

    const bigArea = big.w * big.h;
    const smallArea = small.w * small.h;

    // area ratio ≈ value ratio (3:1)
    expect(bigArea / smallArea).toBeCloseTo(3, 5);
    // together they cover the box
    expect(bigArea + smallArea).toBeCloseTo(width * height, 4);
  });
});

describe("layoutTreemap — three items", () => {
  const items: TreemapItem[] = [
    { label: "a", value: 50 },
    { label: "b", value: 30 },
    { label: "c", value: 20 },
  ];
  const width = 320;
  const height = 200;

  it("areas sum to width*height (within epsilon)", () => {
    const tiles = layoutTreemap(items, width, height);
    expect(tiles).toHaveLength(3);
    expect(sumAreas(tiles)).toBeCloseTo(width * height, 4);
  });

  it("keeps all tiles within the box", () => {
    const tiles = layoutTreemap(items, width, height);
    expectWithinBounds(tiles, width, height);
  });

  it("allocates area proportional to value for each tile", () => {
    const tiles = layoutTreemap(items, width, height);
    const totalValue = items.reduce((s, it) => s + it.value, 0);
    const totalArea = width * height;
    for (const it of items) {
      const tile = tiles.find((t) => t.label === it.label)!;
      const area = tile.w * tile.h;
      expect(area).toBeCloseTo((it.value / totalValue) * totalArea, 4);
    }
  });
});

describe("layoutTreemap — ordering & preservation", () => {
  it("returns tiles in value-descending order", () => {
    const items: TreemapItem[] = [
      { label: "x", value: 40 },
      { label: "y", value: 25 },
      { label: "z", value: 20 },
      { label: "w", value: 15 },
    ];
    const tiles = layoutTreemap(items, 300, 200);
    expect(tiles.map((t) => t.label)).toEqual(["x", "y", "z", "w"]);
    expect(tiles.map((t) => t.value)).toEqual([40, 25, 20, 15]);
  });

  it("sorts unsorted input into value-descending order", () => {
    const items: TreemapItem[] = [
      { label: "lo", value: 10 },
      { label: "hi", value: 90 },
      { label: "mid", value: 50 },
    ];
    const tiles = layoutTreemap(items, 300, 200);
    expect(tiles.map((t) => t.label)).toEqual(["hi", "mid", "lo"]);
  });

  it("drops only the non-positive items, keeping the rest in order", () => {
    const items: TreemapItem[] = [
      { label: "keep1", value: 60 },
      { label: "drop", value: 0 },
      { label: "keep2", value: 40 },
    ];
    const tiles = layoutTreemap(items, 100, 100);
    expect(tiles.map((t) => t.label)).toEqual(["keep1", "keep2"]);
    expectWithinBounds(tiles, 100, 100);
    expect(sumAreas(tiles)).toBeCloseTo(100 * 100, 4);
  });
});
