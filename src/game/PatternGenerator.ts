import { type CellType, type Pattern } from "./types"; // todo: celltype might not be a necessary import

import { validateReachability } from "./ReachabilityValidator";

export const PATTERNS: Pattern[] = [
  {
    name: "single-left",
    cells: ["obstacle", "empty", "empty", "empty", "empty"],
  },

  {
    name: "single-middle",
    cells: ["empty", "empty", "obstacle", "empty", "empty"],
  },

  {
    name: "single-right",
    cells: ["empty", "empty", "empty", "empty", "obstacle"],
  },

  {
    name: "lightning-middle",
    cells: ["empty", "obstacle", "empty", "lightning", "empty"],
  },

  {
    name: "lightning-left",
    cells: ["lightning", "empty", "obstacle", "empty", "empty"],
  },

  {
    name: "lightning-right",
    cells: ["empty", "empty", "obstacle", "empty", "lightning"],
  },

  {
    name: "split",
    cells: ["obstacle", "empty", "lightning", "empty", "obstacle"],
  },

  {
    name: "double-obstacle",
    cells: ["obstacle", "empty", "obstacle", "empty", "empty"],
  },

  {
    name: "double-obstacle-lightning",
    cells: ["obstacle", "empty", "obstacle", "lightning", "empty"],
  },
];

let rowId = 0;

export function getRandomPattern(difficulty: number): Pattern {
  const availablePatterns = PATTERNS.filter((pattern) => {
    const obstacleCount = pattern.cells.filter(
      (cell) => cell === "obstacle",
    ).length;

    if (difficulty < 2) {
      return obstacleCount <= 1;
    }

    if (difficulty < 3) {
      return obstacleCount <= 2;
    }

    return true;
  });

  const index = Math.floor(Math.random() * availablePatterns.length);

  return availablePatterns[index] ?? PATTERNS[0];
}

export function generateValidRow(previousSafeLanes: number[], difficulty = 1) {
  const candidates = PATTERNS.map((pattern) => ({
    pattern,

    validation: validateReachability(previousSafeLanes, pattern.cells),
  })).filter((candidate) => candidate.validation.reachable);

  if (candidates.length === 0) {
    /*
     * This should never happen
     * with our current five-lane
     * system, but we still provide
     * a safe fallback.
     */
    return {
      id: rowId++,

      patternName: "fallback",

      cells: ["empty", "empty", "empty", "empty", "empty"] as CellType[],
    };
  }

  /*
   * Difficulty controls which
   * patterns are eligible.
   */
  const difficultyCandidates = candidates.filter((candidate) => {
    const obstacleCount = candidate.pattern.cells.filter(
      (cell) => cell === "obstacle",
    ).length;

    if (difficulty <= 1) {
      return obstacleCount <= 1;
    }

    if (difficulty === 2) {
      return obstacleCount <= 2;
    }

    return true;
  });

  const pool =
    difficultyCandidates.length > 0 ? difficultyCandidates : candidates;

  const selected = pool[Math.floor(Math.random() * pool.length)];

  return {
    id: rowId++,

    patternName: selected.pattern.name,

    cells: [...selected.pattern.cells],
  };
}
