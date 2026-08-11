import { LANE_COUNT, type Rectangle } from "./types";

/*
 * How far above the bottom edge the player sits,
 * expressed as a multiple of the plane's own size
 * rather than a fixed pixel value — so it scales
 * correctly across different canvas heights instead
 * of clipping off-screen on some and floating with
 * too much gap on others.
 *
 * Imported by GameCanvas.vue so the drawn sprite and
 * the collision hitbox can never drift apart.
 */
export const PLAYER_BOTTOM_MARGIN_MULTIPLIER = 1.4;

export class Player {
  // starting lane
  lane = 2;

  x = 50;

  readonly movementSpeed = 10;

  update(deltaTime: number) {
    /*
     * Target the center of the lane, not its edge —
     * matches the (lane * laneWidth + laneWidth / 2)
     * formula used for obstacles/lightning in GameCanvas,
     * so the plane never drives to the literal 0%/100%
     * edge of the canvas in the outer lanes.
     */
    const targetX = ((this.lane + 0.5) / LANE_COUNT) * 100;

    const difference = targetX - this.x;

    const movement = this.movementSpeed * 100 * deltaTime;

    if (Math.abs(difference) <= movement) {
      this.x = targetX;

      return;
    }

    this.x += Math.sign(difference) * movement;
  }

  moveLeft() {
    this.lane = Math.max(0, this.lane - 1);
  }

  moveRight() {
    this.lane = Math.min(LANE_COUNT - 1, this.lane + 1);
  }

  getHitbox(
    canvasWidth: number,
    canvasHeight: number,
    spriteSize: number,
    hitboxSize: number,
  ): Rectangle {
    const x = (this.x / 100) * canvasWidth;

    /*
     * Vertical position is always based on the sprite's
     * real size, not the (deliberately smaller) hitbox
     * size — otherwise the collision box and the visible
     * plane drift apart vertically.
     */
    const y = canvasHeight - spriteSize * PLAYER_BOTTOM_MARGIN_MULTIPLIER;

    return {
      x: x - hitboxSize / 2,

      y: y - hitboxSize / 2,

      width: hitboxSize,

      height: hitboxSize,
    };
  }
}
