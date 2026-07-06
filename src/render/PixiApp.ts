import { Application, Graphics } from "pixi.js";
import type { Rect2D, Size2D, WorldProjection } from "../projection/types";
import { createRecursiveInteractionProjection } from "../projection/worldProjection";
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
import { RecursiveTransitionRenderer, type RecursiveTransitionGeometry } from "./RecursiveTransitionRenderer";

export class PixiApp {
  private readonly host: HTMLElement;
  private readonly camera = new Camera2D();
  private readonly worldBounds: Rect2D = { x: 0, y: 0, width: 960, height: 768 };
  private app: Application | null = null;
  private layers: RenderLayers | null = null;
  private transitionRenderer: RecursiveTransitionRenderer | null = null;
  private transitionGeometry: RecursiveTransitionGeometry | null = null;
  private projection: WorldProjection = createRecursiveInteractionProjection();
  private lastViewport: Size2D = { width: 0, height: 0 };
  private wantsInnerView = false;
  private readonly tick = () => {
    const app = this.app;
    if (!app) {
      return;
    }

    const viewport = { width: app.screen.width, height: app.screen.height };
    const resized = viewport.width !== this.lastViewport.width || viewport.height !== this.lastViewport.height;

    if (resized) {
      this.draw();
    }

    if (this.transitionRenderer?.isTransitioning && this.transitionGeometry) {
      this.transitionRenderer.update(app.ticker.deltaMS, this.transitionGeometry);
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
    this.transitionRenderer = new RecursiveTransitionRenderer(
      this.camera,
      this.layers.cameraRoot,
      this.layers.effectLayer,
    );

    app.canvas.setAttribute("data-testid", "pixi-canvas");
    app.canvas.setAttribute("aria-label", "PixiJS recursive transition prototype");
    this.host.appendChild(app.canvas);
    app.ticker.add(this.tick);

    this.draw();
  }

  render(projection: WorldProjection) {
    this.projection = projection;
    this.draw();
  }

  toggleRecursiveTransition() {
    if (!this.transitionRenderer || !this.transitionGeometry) {
      return;
    }

    this.wantsInnerView = !this.wantsInnerView;
    this.transitionRenderer.start(this.wantsInnerView ? "enter" : "exit", this.transitionGeometry);
  }

  destroy() {
    if (!this.app) {
      return;
    }

    this.app.ticker.remove(this.tick);
    this.transitionRenderer?.cancel();
    this.app.destroy({ removeView: true }, { children: true });
    this.app = null;
    this.layers = null;
    this.transitionRenderer = null;
    this.transitionGeometry = null;
  }

  private draw() {
    const app = this.app;
    const layers = this.layers;
    if (!app || !layers) {
      return;
    }

    const viewport = { width: app.screen.width, height: app.screen.height };
    this.lastViewport = viewport;
    this.transitionGeometry = null;
    layers.backgroundLayer.removeChildren();
    layers.recursiveWorldLayer.removeChildren();
    layers.effectLayer.removeChildren();
    layers.overlayLayer.removeChildren();
    this.transitionRenderer?.setLayers(layers.cameraRoot, layers.effectLayer);

    this.drawVoid(layers.backgroundLayer, viewport);

    this.renderWorldProjection(this.projection, this.worldBounds, layers.recursiveWorldLayer);

    if (this.transitionRenderer && this.transitionGeometry) {
      if (this.transitionRenderer.isTransitioning) {
        this.transitionRenderer.update(0, this.transitionGeometry);
      } else {
        this.transitionRenderer.applyRestingCamera(this.transitionGeometry);
      }
    } else {
      this.camera.fitWorld(viewport, this.worldBounds, {
        margin: Math.max(44, Math.min(viewport.width, viewport.height) * 0.08),
        maxScale: 1.05,
      });
      this.camera.applyTo(layers.cameraRoot);
    }
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
        this.renderRecursiveContainer(
          entityProjection.childWorld,
          entityProjection.entity.id,
          projection.depth,
          entityRect,
          palette,
          worldFrame.contentLayer,
        );
      }
    }
  }

  private renderRecursiveContainer(
    childWorld: WorldProjection | undefined,
    entityId: string,
    projectionDepth: number,
    rect: Rect2D,
    palette: RenderPalette,
    parent: RenderLayers["recursiveWorldLayer"],
  ) {
    const primitive = createRecursiveContainerPrimitive(rect, palette);
    parent.addChild(primitive.container);

    if (projectionDepth === 0 && entityId === "container-b") {
      this.transitionGeometry = {
        viewport: this.lastViewport,
        outerWorldBounds: this.worldBounds,
        containerBounds: rect,
        apertureBounds: primitive.previewRect,
      };
    }

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
