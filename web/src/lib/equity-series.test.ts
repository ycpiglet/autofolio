import { describe, it, expect } from "vitest";

import {
  toUplotData,
  periodReturnPct,
  equityLineColor,
  type EquityPoint,
} from "./equity-series";

describe("toUplotData", () => {
  it("returns [[], []] for empty input", () => {
    expect(toUplotData([])).toEqual([[], []]);
  });

  it("splits points into columnar [xs, ys]", () => {
    const points: EquityPoint[] = [
      { t: 1, v: 10 },
      { t: 2, v: 20 },
    ];
    expect(toUplotData(points)).toEqual([
      [1, 2],
      [10, 20],
    ]);
  });
});

describe("periodReturnPct", () => {
  it("computes (last/first - 1) * 100", () => {
    expect(
      periodReturnPct([
        { t: 1, v: 100 },
        { t: 2, v: 150 },
      ]),
    ).toBe(50);
  });

  it("returns 0 for fewer than 2 points", () => {
    expect(periodReturnPct([])).toBe(0);
    expect(periodReturnPct([{ t: 1, v: 100 }])).toBe(0);
  });

  it("returns 0 when first value is 0 (avoids div-by-zero)", () => {
    expect(
      periodReturnPct([
        { t: 1, v: 0 },
        { t: 2, v: 5 },
      ]),
    ).toBe(0);
  });
});

describe("equityLineColor", () => {
  it("returns KR up-red for a positive period", () => {
    expect(
      equityLineColor([
        { t: 1, v: 100 },
        { t: 2, v: 150 },
      ]),
    ).toBe("#F04452");
  });

  it("returns KR down-blue for a negative period", () => {
    expect(
      equityLineColor([
        { t: 1, v: 150 },
        { t: 2, v: 100 },
      ]),
    ).toBe("#3182F6");
  });

  it("returns neutral gray for a flat period", () => {
    expect(
      equityLineColor([
        { t: 1, v: 100 },
        { t: 2, v: 100 },
      ]),
    ).toBe("#8B95A1");
  });
});
