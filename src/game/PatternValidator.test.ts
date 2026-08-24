import { describe, expect, it } from "vitest";

import { validateRow } from "./PatternValidator";
import type { CellType } from "./types";

describe("validateRow", () => {
  it("accepts a row with a safe lane and a lightning bolt", () => {
    const cells: CellType[] = [
      "empty",
      "obstacle",
      "empty",
      "lightning",
      "empty",
    ];

    expect(validateRow(cells)).toEqual({ valid: true, errors: [] });
  });

  it("rejects a row with the wrong number of lanes", () => {
    const cells: CellType[] = ["empty", "empty", "empty", "empty"];

    const result = validateRow(cells);

    expect(result.valid).toBe(false);
    expect(result.errors).toContain("Expected 5 lanes.");
  });

  it("rejects a row where every lane is an obstacle", () => {
    const cells: CellType[] = [
      "obstacle",
      "obstacle",
      "obstacle",
      "obstacle",
      "obstacle",
    ];

    const result = validateRow(cells);

    expect(result.valid).toBe(false);
    expect(result.errors).toContain("No safe lane exists.");
  });

  it("can report multiple errors on the same row", () => {
    const cells: CellType[] = [
      "obstacle",
      "obstacle",
      "obstacle",
      "obstacle",
      "obstacle",
      "obstacle",
    ];

    const result = validateRow(cells);

    expect(result.errors).toEqual([
      "Expected 5 lanes.",
      "No safe lane exists.",
    ]);
  });
});
