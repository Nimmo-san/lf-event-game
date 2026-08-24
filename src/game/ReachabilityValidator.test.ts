import { describe, expect, it } from "vitest";

import {
  getReachableLanes,
  validateReachability,
  validateSequence,
} from "./ReachabilityValidator";
import type { CellType } from "./types";

const EMPTY_ROW: CellType[] = [
  "empty",
  "empty",
  "empty",
  "empty",
  "empty",
];

const WALL_ROW: CellType[] = [
  "obstacle",
  "obstacle",
  "obstacle",
  "obstacle",
  "obstacle",
];

describe("getReachableLanes", () => {
  it("includes a lane's neighbours on both sides", () => {
    expect(getReachableLanes([2])).toEqual([1, 2, 3]);
  });

  it("clamps at the left edge — there's no lane -1", () => {
    expect(getReachableLanes([0])).toEqual([0, 1]);
  });

  it("clamps at the right edge — LANE_COUNT - 1 is the last lane", () => {
    expect(getReachableLanes([4])).toEqual([3, 4]);
  });

  it("unions and de-duplicates across multiple starting lanes", () => {
    expect(getReachableLanes([2, 3])).toEqual([1, 2, 3, 4]);
  });
});

describe("validateReachability", () => {
  it("is reachable when nothing blocks the neighbouring lanes", () => {
    const result = validateReachability([2], EMPTY_ROW);

    expect(result).toEqual({ reachable: true, reachableLanes: [1, 2, 3] });
  });

  it("filters out a reachable lane that the next row blocks", () => {
    const nextCells: CellType[] = [
      "empty",
      "empty",
      "obstacle",
      "empty",
      "empty",
    ];

    const result = validateReachability([2], nextCells);

    expect(result).toEqual({ reachable: true, reachableLanes: [1, 3] });
  });

  it("is unreachable when every reachable lane is blocked", () => {
    const result = validateReachability([2], WALL_ROW);

    expect(result).toEqual({ reachable: false, reachableLanes: [] });
  });
});

describe("validateSequence", () => {
  it("passes a sequence of fully open rows", () => {
    expect(validateSequence([EMPTY_ROW, EMPTY_ROW, EMPTY_ROW])).toBe(true);
  });

  it("stays true when each row narrows the path but always leaves one", () => {
    const narrowFromLeft: CellType[] = [
      "obstacle",
      "empty",
      "empty",
      "empty",
      "empty",
    ];

    const narrowFromRight: CellType[] = [
      "empty",
      "empty",
      "empty",
      "empty",
      "obstacle",
    ];

    expect(validateSequence([narrowFromLeft, narrowFromRight])).toBe(true);
  });

  it("fails as soon as a row walls off every currently-safe lane", () => {
    expect(validateSequence([EMPTY_ROW, WALL_ROW, EMPTY_ROW])).toBe(false);
  });
});
