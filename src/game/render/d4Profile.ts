export type D4ProfileName = 'desktop' | 'portrait' | 'landscape';

export interface D4Profile {
  name: D4ProfileName;
  fov: number;
  cameraBack: number;
  cameraHeight: number;
  cameraLaneBias: number;
  lookAhead: number;
  lookHeight: number;
  fogDensity: number;
  runnerBand: number;
  pursuerNormalTopBand: number;
  pursuerCloseTopBand: number;
  /** Presentation-only vertical projection offset in CSS-pixel fractions. */
  lensShiftY: number;
  mobileQuality: boolean;
}

const PROFILES: Record<D4ProfileName, D4Profile> = {
  desktop: {
    name: 'desktop', fov: 43, cameraBack: 13.6, cameraHeight: 13.2, cameraLaneBias: 0.08,
    lookAhead: 18, lookHeight: 0.6, fogDensity: 0.0185, runnerBand: 0.67,
    pursuerNormalTopBand: 0.83, pursuerCloseTopBand: 0.76, lensShiftY: -0.56, mobileQuality: false,
  },
  portrait: {
    name: 'portrait', fov: 40, cameraBack: 15.2, cameraHeight: 15, cameraLaneBias: 0.06,
    lookAhead: 17.2, lookHeight: 0.55, fogDensity: 0.0205, runnerBand: 0.64,
    pursuerNormalTopBand: 0.84, pursuerCloseTopBand: 0.78, lensShiftY: -0.61, mobileQuality: true,
  },
  landscape: {
    name: 'landscape', fov: 46, cameraBack: 12.8, cameraHeight: 10.6, cameraLaneBias: 0.08,
    lookAhead: 18, lookHeight: 0.55, fogDensity: 0.0185, runnerBand: 0.70,
    pursuerNormalTopBand: 0.85, pursuerCloseTopBand: 0.79, lensShiftY: -0.36, mobileQuality: true,
  },
};

/** D4 profile order is deliberate: short landscape wins before portrait. */
export function d4ProfileForViewport(width: number, height: number): D4Profile {
  const safeWidth = Math.max(1, width);
  const safeHeight = Math.max(1, height);
  const aspect = safeWidth / safeHeight;
  if (safeHeight <= 520 && aspect > 1.5) return PROFILES.landscape;
  if (aspect < 0.72) return PROFILES.portrait;
  return PROFILES.desktop;
}

export function d4MinimumPursuerGapPx(height: number): number {
  return Math.max(6, Math.round(Math.max(1, height) * 0.015));
}
