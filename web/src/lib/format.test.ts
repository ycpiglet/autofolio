import { describe, it, expect } from "vitest";

import {
  fmtWon,
  fmtUsd,
  fmtPct,
  fmtTabular,
  fmtPnlWon,
  symbolLabel,
  pnlColorClass,
  pnlColor,
  fmtWonShort,
  fmtWonShortSigned,
} from "./format";

// Expected values mirror the verified oracle in scripts/verify-format.mjs.
// This vitest suite is the primary unit-test surface; verify-format.mjs is kept
// as a zero-dependency Node fallback.

describe("fmtWon", () => {
  it("formats an integer KRW amount with the ₩ symbol and grouping", () => {
    expect(fmtWon(1234567)).toBe("₩1,234,567");
  });

  it("rounds fractional values to the nearest won", () => {
    expect(fmtWon(1234.6)).toBe("₩1,235");
  });
});

describe("fmtUsd", () => {
  it("formats a USD amount with two fraction digits", () => {
    expect(fmtUsd(1234.5)).toBe("$1,234.50");
  });
});

describe("fmtPct", () => {
  it("prefixes a positive value with +", () => {
    expect(fmtPct(3.14)).toBe("+3.14%");
  });

  it("keeps the - sign for negative values", () => {
    expect(fmtPct(-2)).toBe("-2.00%");
  });

  it("renders zero without a sign", () => {
    expect(fmtPct(0)).toBe("0.00%");
  });
});

describe("fmtTabular", () => {
  it("formats an integer with thousands separators and no symbol", () => {
    expect(fmtTabular(1234567)).toBe("1,234,567");
  });
});

describe("fmtPnlWon", () => {
  it("combines a won amount and a signed percentage", () => {
    expect(fmtPnlWon(1000, 1.5)).toBe("₩1,000 (+1.50%)");
  });
});

describe("symbolLabel", () => {
  it("renders 'name (code)' when the code is in the map", () => {
    expect(symbolLabel("005930", { "005930": "삼성전자" })).toBe(
      "삼성전자 (005930)",
    );
  });

  it("falls back to the bare code when not in the map", () => {
    expect(symbolLabel("005930", {})).toBe("005930");
  });
});

describe("pnlColorClass", () => {
  it("returns the up class for positive values", () => {
    expect(pnlColorClass(5)).toBe("text-pnl-up");
  });

  it("returns the down class for negative values", () => {
    expect(pnlColorClass(-5)).toBe("text-pnl-down");
  });

  it("returns the muted class for zero", () => {
    expect(pnlColorClass(0)).toBe("text-muted-foreground");
  });
});

describe("pnlColor", () => {
  // No `document` exists in the node test environment, so these exercise the
  // SSR fallback branch, which returns the KR-convention colors.
  it("returns the KR up color (red) for positive values", () => {
    expect(pnlColor(5)).toBe("#F04452");
  });

  it("returns the KR down color (blue) for negative values", () => {
    expect(pnlColor(-5)).toBe("#3182F6");
  });

  it("returns the neutral gray for zero", () => {
    expect(pnlColor(0)).toBe("#8B95A1");
  });
});

describe("fmtWonShort", () => {
  it("renders zero as ₩0", () => {
    expect(fmtWonShort(0)).toBe("₩0");
  });

  it("keeps sub-만 values as plain won", () => {
    expect(fmtWonShort(5000)).toBe("₩5,000");
  });

  it("abbreviates 만 with one decimal", () => {
    expect(fmtWonShort(12345)).toBe("₩1.2만");
  });

  it("abbreviates hundreds of 만", () => {
    expect(fmtWonShort(1234500)).toBe("₩123.5만");
  });

  it("keeps grouping for thousands of 만", () => {
    expect(fmtWonShort(12345678)).toBe("₩1,234.6만");
  });

  it("abbreviates 억 at the 1e8 boundary", () => {
    expect(fmtWonShort(123456789)).toBe("₩1.2억");
  });

  it("abbreviates tens of 억", () => {
    expect(fmtWonShort(1234567890)).toBe("₩12.3억");
  });

  it("places the sign after ₩ for negative values", () => {
    expect(fmtWonShort(-98765)).toBe("₩-9.9만");
  });
});

describe("fmtWonShortSigned", () => {
  it("prefixes a positive delta with + before ₩", () => {
    expect(fmtWonShortSigned(123456789)).toBe("+₩1.2억");
  });

  it("prefixes a negative delta with - before ₩", () => {
    expect(fmtWonShortSigned(-98765)).toBe("-₩9.9만");
  });

  it("renders zero as ₩0 with no sign", () => {
    expect(fmtWonShortSigned(0)).toBe("₩0");
  });
});
