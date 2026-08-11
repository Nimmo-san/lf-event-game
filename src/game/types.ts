// number of lanes shown up on screen
export const LANE_COUNT = 5;

// each grid can be either of these
export type CellType = "empty" | "obstacle" | "lightning";

export type Lane = 0 | 1 | 2 | 3 | 4;

/* each row will have its own:
 - id
 - number of cells
 - safe (for user to get through safely)
 - lightning
 - obstacle lanes
 */
export interface GameRow {
  id: number;
  cells: CellType[];
  safeLanes: number[];
  lightningLanes: number[];
  obstacleLanes: number[];
}

export interface Pattern {
  name: string;
  cells: CellType[];
}

export interface Rectangle {
    x: number
    y: number
    width: number
    height: number
}

export type CollisionType =
    | "none"
    | "obstacle"
    | "lightning"