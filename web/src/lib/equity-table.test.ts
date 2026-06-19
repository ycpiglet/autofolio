import { describe, expect, it } from "vitest";

import type { TableResponse } from "@/lib/api";
import { tableToEquityPoints } from "./equity-table";

describe("tableToEquityPoints", () => {
  it("returns [] for undefined input", () => {
    expect(tableToEquityPoints(undefined)).toEqual([]);
  });

  it("maps rows to { t, v } and sorts ascending by time", () => {
    const data: TableResponse = {
      columns: ["date", "자산"],
      rows: [
        { date: "2026-01-02", 자산: 110 },
        { date: "2026-01-01", 자산: 100 },
      ],
    };

    const t1 = Math.floor(Date.parse("2026-01-01") / 1000);
    const t2 = Math.floor(Date.parse("2026-01-02") / 1000);

    expect(tableToEquityPoints(data)).toEqual([
      { t: t1, v: 100 },
      { t: t2, v: 110 },
    ]);
  });

  it("drops rows with an empty/invalid date", () => {
    const data: TableResponse = {
      columns: ["date", "자산"],
      rows: [
        { date: "2026-01-01", 자산: 100 },
        { date: "", 자산: 999 },
        { date: "not-a-date", 자산: 888 },
      ],
    };

    const t1 = Math.floor(Date.parse("2026-01-01") / 1000);

    expect(tableToEquityPoints(data)).toEqual([{ t: t1, v: 100 }]);
  });
});
