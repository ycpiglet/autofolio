import { describe, expect, it } from "vitest";

import {
  EMPTY_ILLUSTRATIONS,
  type EmptyIllustration,
} from "./empty-illustration";

describe("EMPTY_ILLUSTRATIONS", () => {
  it("lists exactly the three supported illustration keys", () => {
    expect(EMPTY_ILLUSTRATIONS).toHaveLength(3);
  });

  it("contains no-data, no-results and error", () => {
    expect(EMPTY_ILLUSTRATIONS).toContain<EmptyIllustration>("no-data");
    expect(EMPTY_ILLUSTRATIONS).toContain<EmptyIllustration>("no-results");
    expect(EMPTY_ILLUSTRATIONS).toContain<EmptyIllustration>("error");
  });
});
