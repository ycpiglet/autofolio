import { describe, it, expect } from "vitest";

import { sliceByRange, EQUITY_RANGES, type EquityRange } from "./equity-range";
import type { EquityPoint } from "./equity-series";

// Fixed series with a known anchor so no wall clock is needed.
const POINTS: EquityPoint[] = [
  { t: 0, v: 100 },
  { t: 86_400, v: 110 }, // +1 day
  { t: 172_800, v: 120 }, // +2 days
  { t: 1_000_000, v: 130 }, // ~+11.57 days
];

// Anchor at the latest point's t; used for explicit, clock-free windowing.
const NOW = 1_000_000;

describe("EQUITY_RANGES", () => {
  it("lists the six ranges shortest → longest", () => {
    expect(EQUITY_RANGES).toEqual(["1D", "1W", "1M", "3M", "1Y", "ALL"]);
  });
});

describe("sliceByRange", () => {
  it("returns [] for empty input (any range)", () => {
    expect(sliceByRange([], "1M")).toEqual([]);
    expect(sliceByRange([], "ALL")).toEqual([]);
  });

  it('"ALL" keeps every point', () => {
    expect(sliceByRange(POINTS, "ALL", NOW)).toEqual(POINTS);
  });

  it('"1D" keeps only points within 86400s of the anchor', () => {
    // cutoff = 1_000_000 - 86_400 = 913_600 → only the t=1_000_000 point.
    expect(sliceByRange(POINTS, "1D", NOW)).toEqual([{ t: 1_000_000, v: 130 }]);
  });

  it('"1W" (mid range) keeps the last 7 days from the anchor', () => {
    // cutoff = 1_000_000 - 604_800 = 395_200 → only the t=1_000_000 point.
    expect(sliceByRange(POINTS, "1W", NOW)).toEqual([{ t: 1_000_000, v: 130 }]);
  });

  it('"1M" (mid range) keeps the last 30 days → the whole series here', () => {
    // cutoff = 1_000_000 - 2_592_000 < 0 → all points qualify.
    expect(sliceByRange(POINTS, "1M", NOW)).toEqual(POINTS);
  });

  it("defaults the anchor to the latest point's t when nowSec is omitted", () => {
    // Anchor = 1_000_000 (last point). "1D" cutoff 913_600 → just that point.
    expect(sliceByRange(POINTS, "1D")).toEqual([{ t: 1_000_000, v: 130 }]);
  });

  it("includes a point sitting exactly on the cutoff (>= boundary)", () => {
    // Dedicated 2-point series so the boundary is isolated: anchor at the last
    // point (172_800) → "1D" cutoff == 86_400, exactly the first point's t,
    // which must be kept because the boundary is inclusive (>=).
    const series: EquityPoint[] = [
      { t: 86_400, v: 110 },
      { t: 172_800, v: 120 },
    ];
    expect(sliceByRange(series, "1D")).toEqual(series);
  });

  it("never returns more points than the input for any range", () => {
    for (const range of EQUITY_RANGES as readonly EquityRange[]) {
      expect(sliceByRange(POINTS, range, NOW).length).toBeLessThanOrEqual(
        POINTS.length,
      );
    }
  });
});
