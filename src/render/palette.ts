import type { PaletteId } from "../projection/types";

export interface RenderPalette {
  voidBackground: number;
  voidParticle: number;
  voidParticleAlpha: number;
  shell: number;
  shellDark: number;
  shellShadow: number;
  rim: number;
  rimBright: number;
  interior: number;
  interiorShade: number;
  player: number;
  playerAccent: number;
  box: number;
  boxSide: number;
  container: number;
  containerWindow: number;
  goal: number;
  goalDot: number;
}

const palettes: Record<PaletteId, RenderPalette> = {
  "void-lab": {
    voidBackground: 0x020409,
    voidParticle: 0x777f88,
    voidParticleAlpha: 0.72,
    shell: 0x94aed0,
    shellDark: 0x5f7084,
    shellShadow: 0x10151c,
    rim: 0x253142,
    rimBright: 0xc5e5ff,
    interior: 0x3c4b5d,
    interiorShade: 0x334051,
    player: 0xc73a7b,
    playerAccent: 0x19131b,
    box: 0x35aee0,
    boxSide: 0x237ea4,
    container: 0x35f59b,
    containerWindow: 0x1c7657,
    goal: 0x9fb6d6,
    goalDot: 0x8ea9c7,
  },
  "inner-mint": {
    voidBackground: 0x020409,
    voidParticle: 0x777f88,
    voidParticleAlpha: 0.72,
    shell: 0x48d19b,
    shellDark: 0x2f7667,
    shellShadow: 0x10151c,
    rim: 0x173a36,
    rimBright: 0xb9ffe0,
    interior: 0x244743,
    interiorShade: 0x1d3937,
    player: 0xc73a7b,
    playerAccent: 0x19131b,
    box: 0xf5a64c,
    boxSide: 0x935628,
    container: 0x35aee0,
    containerWindow: 0x245e7a,
    goal: 0xaee8ce,
    goalDot: 0x90cab2,
  },
};

export function getPalette(paletteId: PaletteId) {
  return palettes[paletteId];
}
