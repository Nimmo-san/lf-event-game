import { type CellType, LANE_COUNT, type GameRow } from "./types";

// Empty row creator
export function createEmptyRow(): CellType[] {
  return Array(LANE_COUNT).fill("empty");
}

// 
export function getSafeLanes(cells: CellType[]): number[] {
  return cells
    .map((cell, index) => (cell === "obstacle" ? -1 : index))
    .filter((lane) => lane !== -1);
}

export function createGameRow(id: number, cells: CellType[]): GameRow {
  return {
    id,
    cells,

    safeLanes: getSafeLanes(cells),

    lightningLanes: cells
      .map((cell, index) => (cell === "lightning" ? index : -1))
      .filter((lane) => lane !== -1),

    obstacleLanes: cells
      .map((cell, index) => (cell === "obstacle" ? index : -1))
      .filter((lane) => lane !== -1),
  };
}
