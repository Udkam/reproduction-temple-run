import { Container } from "pixi.js";

export interface RenderLayers {
  backgroundLayer: Container;
  cameraRoot: Container;
  recursiveWorldLayer: Container;
  effectLayer: Container;
  overlayLayer: Container;
}

export function createRenderLayers(stage: Container): RenderLayers {
  stage.removeChildren();
  stage.sortableChildren = true;

  const backgroundLayer = createLayer("background-layer", 0);
  const cameraRoot = createLayer("camera-root", 10);
  const recursiveWorldLayer = createLayer("recursive-world-layer", 0);
  const effectLayer = createLayer("effect-layer", 20);
  const overlayLayer = createLayer("overlay-layer", 30);

  cameraRoot.addChild(recursiveWorldLayer, effectLayer);
  stage.addChild(backgroundLayer, cameraRoot, overlayLayer);

  return {
    backgroundLayer,
    cameraRoot,
    recursiveWorldLayer,
    effectLayer,
    overlayLayer,
  };
}

function createLayer(label: string, zIndex: number) {
  const layer = new Container();
  layer.label = label;
  layer.zIndex = zIndex;
  layer.sortableChildren = true;
  return layer;
}
