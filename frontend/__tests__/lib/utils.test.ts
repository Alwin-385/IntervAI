/**
 * Tests for shared UI utility functions.
 */

import { cn } from "@/lib/utils";

describe("cn (className utility)", () => {
  it("returns a string", () => {
    expect(typeof cn("foo", "bar")).toBe("string");
  });

  it("combines class names", () => {
    const result = cn("flex", "items-center");
    expect(result).toContain("flex");
    expect(result).toContain("items-center");
  });

  it("merges conflicting tailwind classes (last wins)", () => {
    // tailwind-merge should collapse conflicting utilities
    const result = cn("p-2", "p-4");
    expect(result).not.toContain("p-2");
    expect(result).toContain("p-4");
  });

  it("handles undefined and null gracefully", () => {
    expect(() => cn(undefined, null as any, "flex")).not.toThrow();
  });

  it("handles conditional classes", () => {
    const active = true;
    const result = cn("base", active && "active");
    expect(result).toContain("active");
  });

  it("excludes falsy conditional classes", () => {
    const active = false;
    const result = cn("base", active && "active");
    expect(result).not.toContain("active");
  });
});
