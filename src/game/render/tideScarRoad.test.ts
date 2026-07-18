import { describe, expect, it } from 'vitest';
import { type CourseSection } from '../core';
import { planTideScarSection, stableTideScarHash } from './tideScarRoad';

const base = {
  id: 'section-3',
  index: 3,
  origin: { x: 0, y: 0, z: 0 },
  heading: 'north',
  length: 48,
  events: [],
} as unknown as CourseSection;

describe('analytic Tide Scar road plan', () => {
  it('is section-hash stable, broken into two to five right-edge intervals, and keeps coverage readable', () => {
    const first = planTideScarSection(base, new Set());
    const second = planTideScarSection(base, new Set());
    expect(stableTideScarHash(base.id)).toBe(stableTideScarHash(base.id));
    expect(first).toEqual(second);
    expect(first.intervalCount).toBeGreaterThanOrEqual(2);
    expect(first.intervalCount).toBeLessThanOrEqual(5);
    expect(first.coverage).toBeGreaterThanOrEqual(0.42 - 0.001);
    expect(first.coverage).toBeLessThanOrEqual(0.64 + 0.001);
    expect(first.vertexCount).toBeGreaterThan(0);
  });

  it('removes only the authored local gap span and clips every unresolved hazard silhouette', () => {
    const gap = { ...base, events: [{ id: 'gap', kind: 'gap', at: 15, length: 4, lane: 'all' }] } as unknown as CourseSection;
    const gapPlan = planTideScarSection(gap, new Set(['gap']));
    expect(gapPlan.intervalCount).toBeGreaterThanOrEqual(2);
    expect(gapPlan.vertexCount).toBeGreaterThan(0);
    expect(gapPlan.postClipCoverage).toBeLessThan(gapPlan.coverage);
    for (const interval of gapPlan.intervals) {
      expect(interval.end * gap.length <= 15 || interval.start * gap.length >= 19).toBe(true);
    }

    const beam = { ...base, events: [{ id: 'beam', kind: 'beam', at: 24, lane: 'all' }] } as unknown as CourseSection;
    const clipped = planTideScarSection(beam, new Set(['beam']));
    for (const interval of clipped.intervals) {
      expect(interval.end * beam.length <= 23.32 || interval.start * beam.length >= 24.68).toBe(true);
    }
  });
});
