export interface GameSpriteSizes {
  plane: number;
  obstacle: number;
  lightning: number;
}

export interface GameHitboxSizes {
  plane: number;
  obstacle: number;
  lightning: number;
}

export interface GameSizes {
  sprites: GameSpriteSizes;
  hitboxes: GameHitboxSizes;
}

export function getGameSizes(
  canvasWidth: number,
  canvasHeight: number,
): GameSizes {
  const laneWidth = canvasWidth / 5;

  const shortestSide = Math.min(canvasWidth, canvasHeight);

  const maximumSize = laneWidth * 0.72;

  const plane = Math.min(clamp(shortestSide * 0.105, 32, 64), maximumSize);

  const obstacle = Math.min(clamp(shortestSide * 0.105, 34, 64), maximumSize);

  const lightning = Math.min(clamp(shortestSide * 0.095, 30, 58), maximumSize);

  return {
    sprites: {
      plane,
      obstacle,
      lightning,
    },

    hitboxes: {
      /*
       * Slightly smaller than the
       * visual sprite so collisions
       * don't feel unfair.
       */
      plane: plane * 0.62,

      obstacle: obstacle * 0.72,

      lightning: lightning * 0.62,
    },
  };
}

export function getSpriteSizes(
  canvasWidth: number,
  canvasHeight: number,
): GameSpriteSizes {
  const laneWidth = canvasWidth / 5;

  const shortestSide = Math.min(canvasWidth, canvasHeight);

  const maximumSize = laneWidth * 0.72;

  const plane = Math.min(clamp(shortestSide * 0.105, 32, 64), maximumSize);

  const obstacle = Math.min(clamp(shortestSide * 0.105, 34, 64), maximumSize);

  const lightning = Math.min(clamp(shortestSide * 0.095, 30, 58), maximumSize);

  return {
    plane,
    obstacle,
    lightning,
  };
}

export function fitSprite(
  image: HTMLImageElement,
  maximumWidth: number,
  maximumHeight: number,
) {
  const aspectRatio = image.naturalWidth / image.naturalHeight;

  let width = maximumWidth;

  let height = width / aspectRatio;

  if (height > maximumHeight) {
    height = maximumHeight;

    width = height * aspectRatio;
  }

  return {
    width,
    height,
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}
