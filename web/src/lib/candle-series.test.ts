import { describe, it, expect } from "vitest";

import { toKlineData, KR_CANDLE_COLORS, type Candle } from "./candle-series";

describe("toKlineData", () => {
  it("returns [] for empty input", () => {
    expect(toKlineData([])).toEqual([]);
  });

  it("maps an OHLCV candle to the KLineData shape", () => {
    const candles: Candle[] = [{ t: 1000, o: 10, h: 12, l: 9, c: 11, v: 100 }];
    expect(toKlineData(candles)).toEqual([
      { timestamp: 1000, open: 10, high: 12, low: 9, close: 11, volume: 100 },
    ]);
  });

  it("omits volume when the candle has none", () => {
    const candles: Candle[] = [{ t: 2000, o: 5, h: 6, l: 4, c: 5.5 }];
    expect(toKlineData(candles)).toEqual([
      { timestamp: 2000, open: 5, high: 6, low: 4, close: 5.5 },
    ]);
  });

  it("preserves order across multiple candles", () => {
    const candles: Candle[] = [
      { t: 1000, o: 1, h: 2, l: 1, c: 2 },
      { t: 2000, o: 2, h: 3, l: 2, c: 3 },
    ];
    expect(toKlineData(candles).map((d) => d.timestamp)).toEqual([1000, 2000]);
  });
});

describe("KR_CANDLE_COLORS", () => {
  it("uses KR up-red", () => {
    expect(KR_CANDLE_COLORS.up).toBe("#F04452");
  });

  it("uses KR down-blue", () => {
    expect(KR_CANDLE_COLORS.down).toBe("#3182F6");
  });

  it("uses neutral gray for no change", () => {
    expect(KR_CANDLE_COLORS.noChange).toBe("#8B95A1");
  });
});
