export const spritePaths = {
  plane: "/sprites/plane.png",

  obstacle: "/sprites/obstacle.png",

  lightning: "/sprites/glowbolt.svg",
} as const;

export type SpriteName = keyof typeof spritePaths;

const cache = new Map<SpriteName, HTMLImageElement>();

export function loadSprite(name: SpriteName): Promise<HTMLImageElement> {
  const cached = cache.get(name);

  if (cached) {
    return Promise.resolve(cached);
  }

  return new Promise((resolve, reject) => {
    const image = new Image();

    image.onload = () => {
      cache.set(name, image);

      resolve(image);
    };

    image.onerror = () => {
      reject(new Error(`Failed to load sprite: ${name}`));
    };

    image.src = spritePaths[name];
  });
}
