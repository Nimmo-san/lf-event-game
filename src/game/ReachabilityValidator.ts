import { type CellType, LANE_COUNT } from "./types";

export interface ReachabilityResult {
  reachable: boolean;
  reachableLanes: number[];
}

/**
 * Determines which lanes the player can
 * reach from the currently available lanes.
 *
 * For now, the plane can move one lane
 * left or right per row.
 */
export function getReachableLanes(currentLanes: number[]): number[] {
  const reachable = new Set<number>();

  for (const lane of currentLanes) {
    reachable.add(lane);

    if (lane > 0) {
      reachable.add(lane - 1);
    }

    if (lane < LANE_COUNT - 1) {
      reachable.add(lane + 1);
    }
  }

  return [...reachable].sort((a, b) => a - b);
}

export function validateReachability(
  previousSafeLanes: number[],
  nextCells: CellType[],
): ReachabilityResult {
  const reachableLanes = getReachableLanes(previousSafeLanes);

  const safeReachableLanes = reachableLanes.filter(
    (lane) => nextCells[lane] !== "obstacle",
  );

  return {
    reachable: safeReachableLanes.length > 0,

    reachableLanes: safeReachableLanes,
  };
}

export function validateSequence(
  rows: CellType[][],
  startingLanes = [0, 1, 2, 3, 4],
): boolean {
  let availableLanes = startingLanes;

  for (const row of rows) {
    const result = validateReachability(availableLanes, row);

    if (!result.reachable) {
      return false;
    }

    availableLanes = result.reachableLanes;
  }

  return true;
}
