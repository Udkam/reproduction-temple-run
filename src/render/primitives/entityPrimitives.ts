import { Container, Graphics } from "pixi.js";
import type { Rect2D } from "../../projection/types";
import type { RenderPalette } from "../palette";

export interface RecursiveContainerPrimitive {
  container: Container;
  previewLayer: Container;
  previewRect: Rect2D;
}

export function createPlayerPrimitive(rect: Rect2D, palette: RenderPalette) {
  const container = new Container();
  container.label = "player-primitive";

  const body = new Graphics();
  const eyeRadius = Math.max(3, rect.width * 0.08);

  body.rect(rect.x + rect.width * 0.08, rect.y + rect.height * 0.1, rect.width, rect.height).fill({
    color: palette.shellShadow,
    alpha: 0.65,
  });
  body.roundRect(rect.x, rect.y, rect.width, rect.height, 2).fill(palette.player);
  body.circle(rect.x + rect.width * 0.32, rect.y + rect.height * 0.43, eyeRadius).fill(palette.playerAccent);
  body.circle(rect.x + rect.width * 0.68, rect.y + rect.height * 0.43, eyeRadius).fill(palette.playerAccent);

  container.addChild(body);
  return container;
}

export function createBoxPrimitive(rect: Rect2D, palette: RenderPalette) {
  const container = new Container();
  container.label = "box-primitive";

  const body = new Graphics();
  const tab = Math.max(4, rect.width * 0.12);

  body.rect(rect.x + rect.width * 0.08, rect.y + rect.height * 0.08, rect.width, rect.height).fill({
    color: palette.shellShadow,
    alpha: 0.6,
  });
  body.rect(rect.x - tab, rect.y + rect.height * 0.38, tab, rect.height * 0.24).fill(palette.boxSide);
  body.rect(rect.x + rect.width, rect.y + rect.height * 0.38, tab, rect.height * 0.24).fill(palette.boxSide);
  body.rect(rect.x + rect.width * 0.35, rect.y + rect.height, rect.width * 0.3, tab).fill(palette.boxSide);
  body.rect(rect.x, rect.y, rect.width, rect.height).fill(palette.box);
  body.rect(rect.x, rect.y, rect.width, rect.height * 0.08).fill({ color: 0xffffff, alpha: 0.16 });

  container.addChild(body);
  return container;
}

export function createGoalPrimitive(rect: Rect2D, palette: RenderPalette) {
  const container = new Container();
  container.label = "goal-primitive";

  const goal = new Graphics();
  const strokeWidth = Math.max(3, rect.width * 0.06);
  const dotRadius = Math.max(3, rect.width * 0.1);

  goal.rect(rect.x, rect.y, rect.width, rect.height).stroke({
    color: palette.goal,
    width: strokeWidth,
    alpha: 0.95,
  });
  goal.circle(rect.x + rect.width * 0.28, rect.y + rect.height * 0.55, dotRadius).fill(palette.goalDot);
  goal.circle(rect.x + rect.width * 0.72, rect.y + rect.height * 0.55, dotRadius).fill(palette.goalDot);

  container.addChild(goal);
  return container;
}

export function createRecursiveContainerPrimitive(
  rect: Rect2D,
  palette: RenderPalette,
): RecursiveContainerPrimitive {
  const container = new Container();
  container.label = "recursive-container-primitive";

  const body = new Graphics();
  const previewLayer = new Container();
  const mask = new Graphics();
  const inset = rect.width * 0.12;
  const previewRect = {
    x: rect.x + inset,
    y: rect.y + inset,
    width: rect.width - inset * 2,
    height: rect.height - inset * 2,
  };

  body.rect(rect.x + rect.width * 0.09, rect.y + rect.height * 0.1, rect.width, rect.height).fill({
    color: palette.shellShadow,
    alpha: 0.65,
  });
  body.rect(rect.x - rect.width * 0.12, rect.y + rect.height * 0.38, rect.width * 0.12, rect.height * 0.24).fill({
    color: palette.containerWindow,
    alpha: 0.9,
  });
  body.rect(rect.x + rect.width, rect.y + rect.height * 0.38, rect.width * 0.12, rect.height * 0.24).fill({
    color: palette.containerWindow,
    alpha: 0.9,
  });
  body.rect(rect.x, rect.y, rect.width, rect.height).fill(palette.container);
  body.rect(previewRect.x, previewRect.y, previewRect.width, previewRect.height).fill(palette.containerWindow);
  body.rect(previewRect.x, previewRect.y, previewRect.width, previewRect.height).stroke({
    color: palette.rimBright,
    width: Math.max(2, rect.width * 0.035),
  });

  mask.rect(previewRect.x, previewRect.y, previewRect.width, previewRect.height).fill(0xffffff);
  mask.alpha = 0;
  previewLayer.mask = mask;

  container.addChild(body, previewLayer, mask);

  return {
    container,
    previewLayer,
    previewRect,
  };
}
