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

    // the bane of my existence, fixed the Vary issue
    // in cors mismatch.
    /* Did this first
     * Workbox installation ->
     * fetches images ->
     * cached using request headers A ->
     * Vary: Accept
    */

    // then tried to retrieve with diff header
    /*
      <img> non-CORS request ->
      request headers B ->
      cached response says Vary: Accept ->
      cache doesn't consider it a valid match ->
      Workbox tries network ->
      you're offline ->
      FAILED
    */
    image.crossOrigin = "anonymous";

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
