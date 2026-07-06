import type { Container } from "pixi.js";
import type { Rect2D, Size2D } from "../projection/types";

export interface CameraState {
  x: number;
  y: number;
  scale: number;
}

export interface FitWorldOptions {
  margin: number;
  minScale?: number;
  maxScale?: number;
}

interface CameraTransition {
  from: CameraState;
  to: CameraState;
  elapsedMs: number;
  durationMs: number;
}

export class Camera2D {
  private state: CameraState = { x: 0, y: 0, scale: 1 };
  private transition: CameraTransition | null = null;

  get current() {
    return { ...this.state };
  }

  fitWorld(viewport: Size2D, worldBounds: Rect2D, options: FitWorldOptions) {
    const next = this.getFitState(viewport, worldBounds, options);
    this.setState(next);
    return next;
  }

  getFitState(viewport: Size2D, worldBounds: Rect2D, options: FitWorldOptions): CameraState {
    const availableWidth = Math.max(1, viewport.width - options.margin * 2);
    const availableHeight = Math.max(1, viewport.height - options.margin * 2);
    const rawScale = Math.min(availableWidth / worldBounds.width, availableHeight / worldBounds.height);
    const minScale = options.minScale ?? 0.05;
    const maxScale = options.maxScale ?? 2;
    const scale = Math.min(maxScale, Math.max(minScale, rawScale));

    return {
      x: viewport.width * 0.5 - (worldBounds.x + worldBounds.width * 0.5) * scale,
      y: viewport.height * 0.5 - (worldBounds.y + worldBounds.height * 0.5) * scale,
      scale,
    };
  }

  setState(state: CameraState) {
    this.state = { ...state };
    this.transition = null;
  }

  beginZoomTransition(target: CameraState, durationMs: number) {
    this.transition = {
      from: this.current,
      to: { ...target },
      elapsedMs: 0,
      durationMs: Math.max(1, durationMs),
    };
  }

  stepTransition(deltaMs: number) {
    if (!this.transition) {
      return false;
    }

    const transition = this.transition;
    transition.elapsedMs = Math.min(transition.durationMs, transition.elapsedMs + Math.max(0, deltaMs));
    const t = transition.elapsedMs / transition.durationMs;
    const eased = t * t * (3 - 2 * t);

    this.state = {
      x: lerp(transition.from.x, transition.to.x, eased),
      y: lerp(transition.from.y, transition.to.y, eased),
      scale: lerp(transition.from.scale, transition.to.scale, eased),
    };

    if (transition.elapsedMs >= transition.durationMs) {
      this.transition = null;
    }

    return true;
  }

  applyTo(container: Container) {
    container.position.set(this.state.x, this.state.y);
    container.scale.set(this.state.scale);
  }
}

function lerp(from: number, to: number, t: number) {
  return from + (to - from) * t;
}
