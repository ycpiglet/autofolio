import { describe, it, expect } from "vitest";

import { maxAbs } from "./heatmap-util";

describe("maxAbs", () => {
  it("returns 0 for an empty array", () => {
    expect(maxAbs([])).toBe(0);
  });

  it("returns the largest absolute value (positive dominates)", () => {
    expect(maxAbs([1, -5, 3])).toBe(5);
  });

  it("returns the largest absolute value (all negative)", () => {
    expect(maxAbs([-2, -1])).toBe(2);
  });

  it("returns 0 when the only value is 0", () => {
    expect(maxAbs([0])).toBe(0);
  });
});
