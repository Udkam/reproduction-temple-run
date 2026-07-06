import { Container, Graphics } from "pixi.js";
import type { Rect2D } from "../../projection/types";
import type { RenderPalette } from "../palette";

export interface WorldFramePrimitive {
  container: Container;
  contentLayer: Container;
  interiorRect: Rect2D;
}

export function createWorldFrame(rect: Rect2D, palette: RenderPalette, depth: number): WorldFramePrimitive {
  const container = new Container();
  container.label = `world-frame-depth-${depth}`;
  container.position.set(rect.x, rect.y);

  const frame = new Graphics();
  const contentLayer = new Container();
  const mask = new Graphics();

  const shortSide = Math.min(rect.width, rect.height);
  const inset = Math.max(depth === 0 ? 18 : 4, shortSide * (depth === 0 ? 0.12 : 0.08));
  const bevel = Math.max(depth === 0 ? 8 : 2, shortSide * (depth === 0 ? 0.045 : 0.035));
  const interiorRect = {
    x: inset + bevel,
    y: inset + bevel,
    width: Math.max(1, rect.width - (inset + bevel) * 2),
    height: Math.max(1, rect.height - (inset + bevel) * 2),
  };

  frame.rect(14, 16, rect.width, rect.height).fill({ color: palette.shellShadow, alpha: 0.65 });
  frame.roundRect(0, 0, rect.width, rect.height, 6).fill(palette.shell);
  frame.roundRect(inset, inset, rect.width - inset * 2, rect.height - inset * 2, 20).fill(palette.shellDark);
  frame
    .poly([
      inset + bevel,
      inset,
      rect.width - inset,
      inset,
      rect.width - inset - bevel,
      inset + bevel,
      inset + bevel,
      inset + bevel,
    ])
    .fill(palette.rim);
  frame
    .poly([
      rect.width - inset,
      inset,
      rect.width - inset,
      rect.height - inset,
      rect.width - inset - bevel,
      rect.height - inset - bevel,
      rect.width - inset - bevel,
      inset + bevel,
    ])
    .fill(palette.rimBright);
  frame
    .poly([
      inset,
      rect.height - inset,
      rect.width - inset,
      rect.height - inset,
      rect.width - inset - bevel,
      rect.height - inset - bevel,
      inset + bevel,
      rect.height - inset - bevel,
    ])
    .fill(palette.rimBright);
  frame
    .roundRect(interiorRect.x, interiorRect.y, interiorRect.width, interiorRect.height, 3)
    .fill(palette.interior);

  mask
    .roundRect(interiorRect.x, interiorRect.y, interiorRect.width, interiorRect.height, 3)
    .fill(0xffffff);
  mask.alpha = 0;
  contentLayer.mask = mask;

  container.addChild(frame, contentLayer, mask);

  return {
    container,
    contentLayer,
    interiorRect,
  };
}
