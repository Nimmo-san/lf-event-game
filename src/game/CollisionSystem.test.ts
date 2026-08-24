import { describe, expect, it } from "vitest";

import {
  detectRowCollision,
  getLaneX,
  getObjectHitbox,
  rectanglesOverlap,
} from "./CollisionSystem";
import type { Rectangle } from "./types";

describe("rectanglesOverlap", () => {
  it("is true for overlapping rectangles", () => {
    const a: Rectangle = { x: 0, y: 0, width: 10, height: 10 };
    const b: Rectangle = { x: 5, y: 5, width: 10, height: 10 };

    expect(rectanglesOverlap(a, b)).toBe(true);
  });

  it("is false for rectangles far apart", () => {
    const a: Rectangle = { x: 0, y: 0, width: 10, height: 10 };
    const b: Rectangle = { x: 100, y: 100, width: 10, height: 10 };

    expect(rectanglesOverlap(a, b)).toBe(false);
  });

  it("is false for rectangles that only touch at an edge", () => {
    const a: Rectangle = { x: 0, y: 0, width: 10, height: 10 };
    const b: Rectangle = { x: 10, y: 0, width: 10, height: 10 };

    expect(rectanglesOverlap(a, b)).toBe(false);
  });
});

describe("getLaneX", () => {
  it("centers each of the 5 lanes evenly across the canvas width", () => {
    expect(getLaneX(0, 500)).toBe(50);
    expect(getLaneX(2, 500)).toBe(250);
    expect(getLaneX(4, 500)).toBe(450);
  });
});

describe("getObjectHitbox", () => {
  it("centers a square hitbox on the lane's x position and given y", () => {
    expect(getObjectHitbox(2, 300, 500, 40)).toEqual({
      x: 230,
      y: 280,
      width: 40,
      height: 40,
    });
  });
});

describe("detectRowCollision", () => {
  const canvasWidth = 500;
  const obstacleSize = 40;
  const lightningSize = 20;
  const rowY = 300;

  // Obstacle at lane 1 (center x=150), lightning at lane 3 (center x=350).
  const cells = ["empty", "obstacle", "empty", "lightning", "empty"];

  it("detects an obstacle collision at the correct lane", () => {
    const playerHitbox: Rectangle = { x: 140, y: 290, width: 20, height: 20 };

    expect(
      detectRowCollision(
        playerHitbox,
        cells,
        rowY,
        canvasWidth,
        obstacleSize,
        lightningSize,
      ),
    ).toEqual({ type: "obstacle", lane: 1 });
  });

  it("detects a lightning collision at the correct lane", () => {
    const playerHitbox: Rectangle = { x: 345, y: 295, width: 10, height: 10 };

    expect(
      detectRowCollision(
        playerHitbox,
        cells,
        rowY,
        canvasWidth,
        obstacleSize,
        lightningSize,
      ),
    ).toEqual({ type: "lightning", lane: 3 });
  });

  it("reports no collision when the player overlaps nothing", () => {
    const playerHitbox: Rectangle = { x: 0, y: 0, width: 5, height: 5 };

    expect(
      detectRowCollision(
        playerHitbox,
        cells,
        rowY,
        canvasWidth,
        obstacleSize,
        lightningSize,
      ),
    ).toEqual({ type: "none", lane: null });
  });
});
