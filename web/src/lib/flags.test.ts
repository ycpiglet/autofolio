import { describe, it, expect } from "vitest";
import { FLAG_CODES } from "./flags";

describe("FLAG_CODES", () => {
  it("includes the core KRW-investor markets", () => {
    expect(FLAG_CODES).toContain("kr");
    expect(FLAG_CODES).toContain("us");
  });

  it("has the expected length", () => {
    expect(FLAG_CODES).toHaveLength(5);
  });
});
