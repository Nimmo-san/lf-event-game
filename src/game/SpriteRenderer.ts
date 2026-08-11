import { loadSprite, type SpriteName } from "./SpriteAssets";
import { fitSprite } from "./SpriteSizing";


export interface SpriteSize {
  width: number;
  height: number;
}

export class SpriteRenderer {
  private sprites = new Map<SpriteName, HTMLImageElement>();

  async preload() {
    const names: SpriteName[] = ["plane", "obstacle", "lightning"]; // todo: refactor to type maybe

    await Promise.all(
      names.map(async (name) => {
        const image = await loadSprite(name);

        this.sprites.set(name, image);
      }),
    );
  }

  draw(
    context: CanvasRenderingContext2D,
    name: SpriteName,
    x: number,
    y: number,
    maximumWidth: number,
    maximumHeight: number,
  ) {
    const image = this.sprites.get(name);

    if (!image) {
      return;
    }

    const { width, height } = fitSprite(image, maximumWidth, maximumHeight);

    context.drawImage(image, x - width / 2, y - height / 2, width, height);
  }
}
