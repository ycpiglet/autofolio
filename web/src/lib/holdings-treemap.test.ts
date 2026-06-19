import { describe, expect, it } from "vitest";

import type { TableResponse } from "@/lib/api";
import { holdingsToTreemapItems } from "./holdings-treemap";

describe("holdingsToTreemapItems", () => {
  it("returns [] for undefined input", () => {
    expect(holdingsToTreemapItems(undefined)).toEqual([]);
  });

  it("maps the detected label + size columns to { label, value }", () => {
    const data: TableResponse = {
      columns: ["종목", "평가금액", "수익률"],
      rows: [
        { 종목: "삼성전자", 평가금액: 4000000, 수익률: 1.2 },
        { 종목: "SK하이닉스", 평가금액: 2500000, 수익률: -0.5 },
      ],
    };

    expect(holdingsToTreemapItems(data)).toEqual([
      { label: "삼성전자", value: 4000000 },
      { label: "SK하이닉스", value: 2500000 },
    ]);
  });

  it("returns [] when no size-like numeric column exists", () => {
    const data: TableResponse = {
      columns: ["종목", "비고"],
      rows: [
        { 종목: "삼성전자", 비고: "보유" },
        { 종목: "SK하이닉스", 비고: "관심" },
      ],
    };

    expect(holdingsToTreemapItems(data)).toEqual([]);
  });

  it("drops rows with value <= 0 or an empty label", () => {
    const data: TableResponse = {
      columns: ["종목", "평가금액"],
      rows: [
        { 종목: "삼성전자", 평가금액: 4000000 },
        { 종목: "제로", 평가금액: 0 },
        { 종목: "마이너스", 평가금액: -100 },
        { 종목: "", 평가금액: 999 },
      ],
    };

    expect(holdingsToTreemapItems(data)).toEqual([
      { label: "삼성전자", value: 4000000 },
    ]);
  });
});
