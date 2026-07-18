import { LANE_WIDTH } from '../core';

export const PALETTE = {
  void: 0x081724,
  sky: 0xcbd0c7,
  mist: 0x8e9e9e,
  sandstone: 0xe7d6b4,
  sandstoneShade: 0x8f7659,
  basalt: 0x3e4850,
  basaltEdge: 0x242f37,
  tideDeep: 0x10283c,
  tideLight: 0x31536b,
  tideScar: 0xf4ecd8,
  porcelain: 0xf0dfbd,
  verdigris: 0x31536b,
  signal: 0xf4ecd8,
  hazard: 0xb84432,
  brass: 0xb99e72,
  ink: 0x14202b,
  blackTide: 0x111a20,
  soil: 0x10283c,
  foliage: 0x46575e,
  runnerCloth: 0x203746,
  runnerLeather: 0x2a3338,
} as const;

export const WORLD_METRICS = {
  laneWidth: LANE_WIDTH,
  roadWidth: 7.6,
  roadHeight: 0.48,
  railInset: 0.22,
  runnerHeight: 1.85,
} as const;
