import { Application, Graphics } from "pixi.js";
import type { Rect2D, Size2D, WorldProjection } from "../projection/types";
import { createStage2Projection } from "../projection/worldProjection";
import { Camera2D } from "./Camera2D";
import { createRenderLayers, type RenderLayers } from "./layers";
import { getPalette, type RenderPalette } from "./palette";
import {
  createBoxPrimitive,
  createGoalPrimitive,
  createPlayerPrimitive,
  createRecursiveContainerPrimitive,
} from "./primitives/entityPrimitives";
import { createWorldFrame } from "./primitives/worldFrame";

export class PixiApp {
  private readonly host: HTMLElement;
  private readonly camera = new Camera2D();
  private app: Application | null = null;
  private layers: RenderLayers | null = null;
  private projection: WorldProjection = createStage2Projection();
  private lastViewport: Size2D = { width: 0, height: 0 };
  private readonly tick = () => {
    const app = this.app;
    if (!app) {
      return;
    }

    const viewport = { width: app.screen.width, height: app.screen.height };
    const resized = viewport.width !== this.lastViewport.width || viewport.height !== this.lastViewport.height;
    const cameraMoved = this.camera.stepTransition(app.ticker.deltaMS);

    if (resized) {
      this.draw();
      return;
    }

    if (cameraMoved && this.layers) {
      this.camera.applyTo(this.layers.cameraRoot);
    }
  };

  constructor(host: HTMLElement) {
    this.host = host;
  }

  async init() {
    const app = new Application();

    await app.init({
      background: "#020409",
      resizeTo: this.host,
      antialias: true,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1,
      preference: "webgl",
    });

    this.app = app;
    this.layers = createRenderLayers(app.stage);

    app.canvas.setAttribute("data-testid", "pixi-canvas");
    app.canvas.setAttribute("aria-label", "PixiJS renderer foundation");
    this.host.appendChild(app.canvas);
    app.ticker.add(this.tick);

    this.draw();
  }

  render(projection: WorldProjection) {
    this.projection = projection;
    this.draw();
  }

  destroy() {
    if (!this.app) {
      return;
    }

    this.app.ticker.remove(this.tick);
    this.app.destroy({ removeView: true }, { children: true });
    this.app = null;
    this.layers = null;
  }

  private draw() {
    const app = this.app;
    const layers = this.layers;
    if (!app || !layers) {
      return;
    }

    const viewport = { width: app.screen.width, height: app.screen.height };
    this.lastViewport = viewport;
    layers.backgroundLayer.removeChildren();
    layers.recursiveWorldLayer.removeChildren();
    layers.effectLayer.removeChildren();
    layers.overlayLayer.removeChildren();

    this.drawVoid(layers.backgroundLayer, viewport);

    const worldBounds = { x: 0, y: 0, width: 960, height: 768 };
    this.renderWorldProjection(this.projection, worldBounds, layers.recursiveWorldLayer);
    this.camera.fitWorld(viewport, worldBounds, {
      margin: Math.max(44, Math.min(viewport.width, viewport.height) * 0.08),
      maxScale: 1.05,
    });
    this.camera.applyTo(layers.cameraRoot);
  }

  private drawVoid(layer: RenderLayers["backgroundLayer"], viewport: Size2D) {
    const palette = getPalette("void-lab");
    const backdrop = new Graphics();

    backdrop.rect(0, 0, viewport.width, viewport.height).fill(palette.voidBackground);

    for (let i = 0; i < 48; i += 1) {
      const size = i % 5 === 0 ? 18 : i % 3 === 0 ? 10 : 5;
      const x = (i * 181 + 73) % Math.max(1, viewport.width + 80) - 40;
      const y = (i * 113 + 29) % Math.max(1, viewport.height + 80) - 40;
      backdrop.rect(x, y, size, size).fill({
        color: palette.voidParticle,
        alpha: palette.voidParticleAlpha * (i % 4 === 0 ? 0.75 : 0.45),
      });
    }

    layer.addChild(backdrop);
  }

  private renderWorldProjection(projection: WorldProjection, rect: Rect2D, parent: RenderLayers["recursiveWorldLayer"]) {
    const palette = getPalette(projection.world.paletteId);
    const worldFrame = createWorldFrame(rect, palette, projection.depth);

    parent.addChild(worldFrame.container);

    for (const entityProjection of projection.entities) {
      const entityRect = this.projectEntityRect(entityProjection.entity.bounds, projection.world.size, worldFrame.interiorRect);

      if (entityProjection.entity.kind === "player") {
        worldFrame.contentLayer.addChild(createPlayerPrimitive(entityRect, palette));
        continue;
      }

      if (entityProjection.entity.kind === "box") {
        worldFrame.contentLayer.addChild(createBoxPrimitive(entityRect, palette));
        continue;
      }

      if (entityProjection.entity.kind === "goal") {
        worldFrame.contentLayer.addChild(createGoalPrimitive(entityRect, palette));
        continue;
      }

      if (entityProjection.entity.kind === "recursive-container") {
        this.renderRecursiveContainer(entityProjection.childWorld, entityRect, palette, worldFrame.contentLayer);
      }
    }
  }

  private renderRecursiveContainer(
    childWorld: WorldProjection | undefined,
    rect: Rect2D,
    palette: RenderPalette,
    parent: RenderLayers["recursiveWorldLayer"],
  ) {
    const primitive = createRecursiveContainerPrimitive(rect, palette);
    parent.addChild(primitive.container);

    if (childWorld) {
      this.renderWorldProjection(childWorld, primitive.previewRect, primitive.previewLayer);
    }
  }

  private projectEntityRect(entityBounds: Rect2D, worldSize: Size2D, interiorRect: Rect2D): Rect2D {
    return {
      x: interiorRect.x + (entityBounds.x / worldSize.width) * interiorRect.width,
      y: interiorRect.y + (entityBounds.y / worldSize.height) * interiorRect.height,
      width: (entityBounds.width / worldSize.width) * interiorRect.width,
      height: (entityBounds.height / worldSize.height) * interiorRect.height,
    };
  }
}
