import { LANE_WIDTH } from '../core';

export const PALETTE = {
  void: 0x2c3029,
  sky: 0xc7d8d1,
  mist: 0x9fb7af,
  basalt: 0x4b5148,
  basaltEdge: 0x777a69,
  porcelain: 0xe7dfca,
  verdigris: 0x315b4a,
  signal: 0x12ae9d,
  hazard: 0xc9513a,
  brass: 0xe7c68a,
  ink: 0xf7f4ea,
  blackTide: 0x111410,
  soil: 0x342d25,
  foliage: 0x315b4a,
  runnerCloth: 0x243933,
  runnerLeather: 0x342d25,
} as const;

export const WORLD_METRICS = {
  laneWidth: LANE_WIDTH,
  roadWidth: 7.6,
  roadHeight: 0.48,
  railInset: 0.22,
  runnerHeight: 1.85,
} as const;
