import { clamp01, easeInOutCubic } from "./easing";

export type TimelineDirection = "forward" | "reverse";

export interface TransitionSnapshot {
  direction: TimelineDirection;
  rawProgress: number;
  easedProgress: number;
  running: boolean;
  complete: boolean;
}

export class TransitionTimeline {
  private readonly durationMs: number;
  private direction: TimelineDirection = "forward";
  private progress = 0;
  private running = false;

  constructor(durationMs: number) {
    this.durationMs = Math.max(1, durationMs);
  }

  get snapshot(): TransitionSnapshot {
    return {
      direction: this.direction,
      rawProgress: this.progress,
      easedProgress: easeInOutCubic(this.progress),
      running: this.running,
      complete: !this.running && (this.progress === 0 || this.progress === 1),
    };
  }

  start(direction: TimelineDirection, fromProgress = this.progress) {
    this.direction = direction;
    this.progress = clamp01(fromProgress);
    this.running = true;
  }

  cancel() {
    this.running = false;
  }

  step(deltaMs: number) {
    if (!this.running) {
      return this.snapshot;
    }

    const delta = Math.max(0, deltaMs) / this.durationMs;
    this.progress = clamp01(this.progress + (this.direction === "forward" ? delta : -delta));

    if (this.progress === 0 || this.progress === 1) {
      this.running = false;
    }

    return this.snapshot;
  }
}
