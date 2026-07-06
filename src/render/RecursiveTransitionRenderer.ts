import { Container, Graphics } from "pixi.js";
import { lerp } from "../animation/easing";
import { TransitionTimeline, type TimelineDirection } from "../animation/TransitionTimeline";
import type { Rect2D, Size2D } from "../projection/types";
import { Camera2D, type CameraState } from "./Camera2D";

export type RecursiveTransitionDirection = "enter" | "exit";
export type RecursiveViewMode = "outer" | "inner";

export interface RecursiveTransitionGeometry {
  viewport: Size2D;
  outerWorldBounds: Rect2D;
  containerBounds: Rect2D;
  apertureBounds: Rect2D;
}

export class RecursiveTransitionRenderer {
  private readonly timeline = new TransitionTimeline(980);
  private readonly apertureEffect = new Graphics();
  private mode: RecursiveViewMode = "outer";
  private visualProgress = 0;

  constructor(
    private readonly camera: Camera2D,
    private cameraRoot: Container,
    private effectLayer: Container,
  ) {
    this.apertureEffect.label = "recursive-transition-aperture";
    this.effectLayer.addChild(this.apertureEffect);
  }

  get viewMode() {
    return this.mode;
  }

  get isTransitioning() {
    return this.timeline.snapshot.running;
  }

  setLayers(cameraRoot: Container, effectLayer: Container) {
    this.cameraRoot = cameraRoot;
    this.effectLayer = effectLayer;
    this.effectLayer.addChild(this.apertureEffect);
  }

  start(direction: RecursiveTransitionDirection, geometry: RecursiveTransitionGeometry) {
    const timelineDirection: TimelineDirection = direction === "enter" ? "forward" : "reverse";
    this.camera.cancelTransition();
    this.timeline.start(timelineDirection, this.visualProgress);
    this.applyProgress(this.visualProgress, geometry);
  }

  cancel() {
    this.timeline.cancel();
    this.camera.cancelTransition();
  }

  update(deltaMs: number, geometry: RecursiveTransitionGeometry) {
    const snapshot = this.timeline.step(deltaMs);
    this.visualProgress = snapshot.rawProgress;
    this.applyProgress(snapshot.easedProgress, geometry);

    if (!snapshot.running && snapshot.complete) {
      this.mode = snapshot.rawProgress >= 1 ? "inner" : "outer";
      this.apertureEffect.clear();
    }

    return snapshot.running;
  }

  applyRestingCamera(geometry: RecursiveTransitionGeometry) {
    this.visualProgress = this.mode === "inner" ? 1 : 0;
    this.timeline.cancel();
    this.applyProgress(this.visualProgress, geometry);
    this.apertureEffect.clear();
  }

  private applyProgress(progress: number, geometry: RecursiveTransitionGeometry) {
    const cameraState = interpolateCamera(
      getOuterCameraState(this.camera, geometry),
      getInnerCameraState(this.camera, geometry),
      progress,
    );

    this.camera.setState(cameraState);
    this.camera.applyTo(this.cameraRoot);
    this.drawApertureEffect(progress, geometry, cameraState);
  }

  private drawApertureEffect(progress: number, geometry: RecursiveTransitionGeometry, cameraState: CameraState) {
    this.apertureEffect.clear();

    if (progress <= 0 || progress >= 1) {
      return;
    }

    const active = Math.sin(progress * Math.PI);
    const ring = interpolateRect(geometry.containerBounds, geometry.apertureBounds, Math.min(1, progress * 1.25));
    const strokeWidth = Math.max(2, 5 / cameraState.scale);

    this.apertureEffect
      .roundRect(ring.x, ring.y, ring.width, ring.height, Math.max(2, 8 / cameraState.scale))
      .stroke({
        color: 0xc5e5ff,
        width: strokeWidth,
        alpha: 0.3 + active * 0.7,
      });
  }
}

function getOuterCameraState(camera: Camera2D, geometry: RecursiveTransitionGeometry) {
  return camera.getFitState(geometry.viewport, geometry.outerWorldBounds, {
    margin: Math.max(44, Math.min(geometry.viewport.width, geometry.viewport.height) * 0.08),
    maxScale: 1.05,
  });
}

function getInnerCameraState(camera: Camera2D, geometry: RecursiveTransitionGeometry) {
  return camera.getFitState(geometry.viewport, geometry.apertureBounds, {
    margin: Math.max(26, Math.min(geometry.viewport.width, geometry.viewport.height) * 0.1),
    maxScale: 8,
  });
}

function interpolateCamera(from: CameraState, to: CameraState, progress: number): CameraState {
  return {
    x: lerp(from.x, to.x, progress),
    y: lerp(from.y, to.y, progress),
    scale: lerp(from.scale, to.scale, progress),
  };
}

function interpolateRect(from: Rect2D, to: Rect2D, progress: number): Rect2D {
  return {
    x: lerp(from.x, to.x, progress),
    y: lerp(from.y, to.y, progress),
    width: lerp(from.width, to.width, progress),
    height: lerp(from.height, to.height, progress),
  };
}
