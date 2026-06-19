import { describe, it, expect } from "vitest";

import {
  sparklineTrendColor,
  SPARKLINE_UP_COLOR,
  SPARKLINE_DOWN_COLOR,
  SPARKLINE_FLAT_COLOR,
} from "./sparkline-util";

describe("sparklineTrendColor", () => {
  it("returns muted gray for fewer than 2 points", () => {
    expect(sparklineTrendColor([])).toBe(SPARKLINE_FLAT_COLOR); // "#8B95A1"
    expect(sparklineTrendColor([])).toBe("#8B95A1");
    expect(sparklineTrendColor([5])).toBe("#8B95A1");
  });

  it("returns red (up) for a rising series", () => {
    expect(sparklineTrendColor([1, 2, 3])).toBe(SPARKLINE_UP_COLOR); // "#F04452"
    expect(sparklineTrendColor([1, 2, 3])).toBe("#F04452");
  });

  it("returns blue (down) for a falling series", () => {
    expect(sparklineTrendColor([3, 2, 1])).toBe(SPARKLINE_DOWN_COLOR); // "#3182F6"
    expect(sparklineTrendColor([3, 2, 1])).toBe("#3182F6");
  });

  it("treats equal endpoints as up (inclusive >= boundary)", () => {
    // last(2) >= first(2) → up/red, even though the path dips/rises between.
    expect(sparklineTrendColor([2, 5, 2])).toBe("#F04452");
    expect(sparklineTrendColor([3, 1, 3])).toBe("#F04452");
  });

  it("returns blue for a clearly-down two-point series", () => {
    expect(sparklineTrendColor([10, 5])).toBe("#3182F6");
  });
});
