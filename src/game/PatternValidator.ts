import { type CellType, LANE_COUNT } from "./types";

export function validateRow(cells: CellType[]): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (cells.length !== LANE_COUNT) {
    errors.push(`Expected ${LANE_COUNT} lanes.`);
  }

  const obstacleLanes = cells
    .map((cell, index) => (cell === "obstacle" ? index : -1))
    .filter((index) => index !== -1);

  const lightningLanes = cells
    .map((cell, index) => (cell === "lightning" ? index : -1))
    .filter((index) => index !== -1);

  /*
   * An obstacle and lightning
   * cannot occupy the same cell.
   *
   * This is technically guaranteed
   * by our CellType model, but we
   * explicitly validate it because
   * future procedural generation
   * may construct rows differently.
   */
  for (const lightningLane of lightningLanes) {
    if (obstacleLanes.includes(lightningLane)) {
      errors.push(`Lightning overlaps obstacle in lane ${lightningLane}.`);
    }
  }

  /*
   * There must always be
   * at least one safe lane.
   */
  if (obstacleLanes.length >= LANE_COUNT) {
    errors.push("No safe lane exists.");
  }

  return {
    valid: errors.length === 0,

    errors,
  };
}
