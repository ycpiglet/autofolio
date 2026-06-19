import { describe, it, expect } from "vitest";

import {
  categoricalOrder,
  pnlDivergingColor,
  sequentialColor,
  sequentialBlues,
  brandBlueDark,
} from "./chart-palette";

const HEX6 = /^#[0-9A-Fa-f]{6}$/;

describe("categoricalOrder", () => {
  it("has 7 colors", () => {
    expect(categoricalOrder).toHaveLength(7);
  });

  it("every entry is a 6-digit hex color", () => {
    for (const color of categoricalOrder) {
      expect(color).toMatch(HEX6);
    }
  });
});

describe("pnlDivergingColor", () => {
  it("returns the neutral midpoint at zero", () => {
    expect(pnlDivergingColor(0, 100)).toBe("#f7f7f7");
  });

  it("returns the strongest up color at +maxAbs", () => {
    expect(pnlDivergingColor(100, 100)).toBe("#ca0020");
  });

  it("returns the strongest down color at -maxAbs", () => {
    expect(pnlDivergingColor(-100, 100)).toBe("#0571b0");
  });

  it("maps a mid-positive value to the light-up class", () => {
    expect(pnlDivergingColor(50, 100)).toBe("#f4a582");
  });

  it("maps a mid-negative value to the light-down class", () => {
    expect(pnlDivergingColor(-50, 100)).toBe("#92c5de");
  });

  it("clamps values above the range to the strongest up color", () => {
    expect(pnlDivergingColor(200, 100)).toBe("#ca0020");
  });

  it("guards against a non-positive maxAbs (zero)", () => {
    expect(pnlDivergingColor(5, 0)).toBe("#f7f7f7");
  });

  it("guards against a negative maxAbs", () => {
    expect(pnlDivergingColor(5, -3)).toBe("#f7f7f7");
  });
});

describe("sequentialColor", () => {
  it("returns the first viridis stop at t=0", () => {
    expect(sequentialColor(0)).toBe("#440154");
  });

  it("returns the last viridis stop at t=1", () => {
    expect(sequentialColor(1)).toBe("#FDE725");
  });

  it("returns the middle viridis stop at t=0.5", () => {
    expect(sequentialColor(0.5)).toBe("#21908C");
  });

  it("clamps t above 1 to the last stop", () => {
    expect(sequentialColor(2)).toBe("#FDE725");
  });

  it("clamps t below 0 to the first stop", () => {
    expect(sequentialColor(-1)).toBe("#440154");
  });

  it("honors a custom ramp (sequentialBlues)", () => {
    expect(sequentialColor(1, sequentialBlues)).toBe("#084594");
  });
});

describe("brandBlueDark", () => {
  it("exposes the expected dark solid9 token", () => {
    expect(brandBlueDark.solid9).toBe("#0090ff");
  });
});
