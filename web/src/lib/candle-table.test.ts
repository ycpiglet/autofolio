import { describe, expect, it } from "vitest";

import type { TableResponse } from "./api";
import type { Candle } from "./candle-series";
import { tableToCandles } from "./candle-table";

describe("tableToCandles", () => {
  it("returns [] for undefined input", () => {
    expect(tableToCandles(undefined)).toEqual([]);
  });

  it("returns [] for an empty table", () => {
    expect(tableToCandles({ columns: ["시간", "종가"], rows: [] })).toEqual([]);
  });

  it("maps KR columns and sorts ascending by time (t in ms)", () => {
    // Two rows, the LATER timestamp listed first, to prove ascending sort.
    const data: TableResponse = {
      columns: ["시간", "시가", "고가", "저가", "종가"],
      rows: [
        {
          시간: "2026-06-19 10:01",
          시가: 100,
          고가: 110,
          저가: 95,
          종가: 105,
        },
        {
          시간: "2026-06-19 10:00",
          시가: 90,
          고가: 102,
          저가: 88,
          종가: 100,
        },
      ],
    };

    // Expected ms computed with the SAME normalisation tableToCandles uses
    // ("YYYY-MM-DD HH:mm" → replace " " with "T" then getTime()).
    const tEarlier = new Date("2026-06-19T10:00").getTime();
    const tLater = new Date("2026-06-19T10:01").getTime();

    const expected: Candle[] = [
      { t: tEarlier, o: 90, h: 102, l: 88, c: 100 },
      { t: tLater, o: 100, h: 110, l: 95, c: 105 },
    ];

    expect(tableToCandles(data)).toEqual(expected);
  });

  it("parses a date-only (YYYY-MM-DD) time via Date.parse", () => {
    const data: TableResponse = {
      columns: ["date", "open", "high", "low", "close"],
      rows: [{ date: "2026-06-19", open: 1, high: 2, low: 0.5, close: 1.5 }],
    };

    const result = tableToCandles(data);
    expect(result).toHaveLength(1);
    expect(result[0].t).toBe(Date.parse("2026-06-19"));
    expect(result[0]).toMatchObject({ o: 1, h: 2, l: 0.5, c: 1.5 });
  });

  it("drops rows whose time is unparseable", () => {
    const data: TableResponse = {
      columns: ["시간", "시가", "고가", "저가", "종가"],
      rows: [
        { 시간: "not-a-date", 시가: 1, 고가: 2, 저가: 0, 종가: 1 },
        {
          시간: "2026-06-19 09:00",
          시가: 10,
          고가: 12,
          저가: 9,
          종가: 11,
        },
      ],
    };

    const result = tableToCandles(data);
    expect(result).toHaveLength(1);
    expect(result[0].t).toBe(new Date("2026-06-19T09:00").getTime());
    expect(result[0].c).toBe(11);
  });
});
