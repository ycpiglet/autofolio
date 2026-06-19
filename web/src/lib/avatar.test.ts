import { describe, it, expect } from "vitest";

import { avatarDataUri, avatarSvg } from "./avatar";

describe("avatarDataUri", () => {
  it("returns a data:image/svg+xml URI", () => {
    expect(avatarDataUri("user-1")).toMatch(/^data:image\/svg\+xml,/);
  });

  it("is deterministic for the same seed", () => {
    expect(avatarDataUri("user-1")).toBe(avatarDataUri("user-1"));
  });

  it("produces different output for different seeds", () => {
    expect(avatarDataUri("user-1")).not.toBe(avatarDataUri("user-2"));
  });

  it("produces different output per variant for the same seed", () => {
    expect(avatarDataUri("x", "account")).not.toBe(avatarDataUri("x", "agent"));
  });
});

describe("avatarSvg", () => {
  it("returns a non-empty SVG document string", () => {
    const svg = avatarSvg("user-1");
    expect(svg).toContain("<svg");
    expect(svg.length).toBeGreaterThan(0);
  });
});
