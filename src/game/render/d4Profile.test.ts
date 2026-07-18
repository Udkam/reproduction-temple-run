import { describe, expect, it } from 'vitest';
import { d4MinimumPursuerGapPx, d4ProfileForViewport } from './d4Profile';

describe('D4 camera profiles', () => {
  it('classifies landscape before portrait and uses desktop for the middle fallback', () => {
    expect(d4ProfileForViewport(844, 390).name).toBe('landscape');
    expect(d4ProfileForViewport(390, 844).name).toBe('portrait');
    expect(d4ProfileForViewport(844, 844).name).toBe('desktop');
  });

  it('freezes profile FOV independent of speed inputs and preserves the 844x390 mobile quality profile', () => {
    expect(d4ProfileForViewport(1440, 900).fov).toBe(43);
    expect(d4ProfileForViewport(390, 844).fov).toBe(40);
    const landscape = d4ProfileForViewport(844, 390);
    expect(landscape.fov).toBe(46);
    expect(landscape.mobileQuality).toBe(true);
    expect(d4ProfileForViewport(1440, 900).lookAhead).toBe(18);
    expect(d4ProfileForViewport(390, 844).lookAhead).toBe(17.2);
    expect(landscape.lookAhead).toBe(18);
    expect(d4ProfileForViewport(1440, 900).lensShiftY).toBeLessThan(0);
  });

  it('derives the D4 CSS-pixel pursuit minimum from viewport height', () => {
    expect(d4MinimumPursuerGapPx(390)).toBe(6);
    expect(d4MinimumPursuerGapPx(844)).toBe(13);
    expect(d4MinimumPursuerGapPx(900)).toBe(14);
  });
});
