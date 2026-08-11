import type { Rectangle, CollisionType } from "./types";

export interface CollisionResult {
  type: CollisionType;
  lane: number | null;
}

export function rectanglesOverlap(a: Rectangle, b: Rectangle): boolean {
  return (
    a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y
  );
}

export function getLaneX(lane: number, canvasWidth: number): number {
  const laneWidth = canvasWidth / 5;

  return lane * laneWidth + laneWidth / 2;
}

export function getObjectHitbox(
  lane: number,
  y: number,
  canvasWidth: number,
  size: number,
): Rectangle {
  const x = getLaneX(lane, canvasWidth);

  return {
    x: x - size / 2,

    y: y - size / 2,

    width: size,

    height: size,
  };
}

export function detectRowCollision(
  playerHitbox: Rectangle,
  cells: string[],
  rowY: number,
  canvasWidth: number,
  obstacleSize: number,
  lightningSize: number,
): CollisionResult {
  for (let lane = 0; lane < cells.length; lane++) {
    const cell = cells[lane];

    if (cell === "empty") {
      continue;
    }

    const hitboxSize = cell === "obstacle" ? obstacleSize : lightningSize;

    const objectHitbox = getObjectHitbox(lane, rowY, canvasWidth, hitboxSize);

    if (rectanglesOverlap(playerHitbox, objectHitbox)) {
      return {
        type: cell === "obstacle" ? "obstacle" : "lightning",

        lane,
      };
    }
  }

  return {
    type: "none",
    lane: null,
  };
}
