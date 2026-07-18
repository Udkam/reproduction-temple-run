import { describe, expect, it } from 'vitest';
import { PURSUER_RIG_BOUNDS, createPursuerRig, updatePursuerRig } from './pursuerRig';

describe('black-rock pursuer rig', () => {
  it('keeps all four limbs grounded around diagonal alternating phases', () => {
    const rig = createPursuerRig();
    updatePursuerRig(rig, { elapsed: 0.07, danger: 0.35, reducedMotion: false, stumble: false, captured: false });
    const first = rig.legs.map((leg) => leg.rotation.x);
    updatePursuerRig(rig, { elapsed: 0.17, danger: 0.35, reducedMotion: false, stumble: false, captured: false });
    const second = rig.legs.map((leg) => leg.rotation.x);
    expect(second).not.toEqual(first);
    expect(Math.sign(second[0]!)).toBe(Math.sign(second[3]!));
    expect(Math.sign(second[1]!)).toBe(Math.sign(second[2]!));
    expect(Math.sign(second[0]!)).toBe(-Math.sign(second[1]!));
    expect(rig.shadow.visible).toBe(true);
    expect(PURSUER_RIG_BOUNDS.height).toBeGreaterThan(1);
  });

  it('keeps a readable capture exception without introducing a flying shadow', () => {
    const rig = createPursuerRig();
    updatePursuerRig(rig, { elapsed: 1, danger: 1, reducedMotion: true, stumble: true, captured: true });
    expect(rig.shadow.visible).toBe(false);
    expect(rig.body.position.y).toBeGreaterThan(0);
  });

  it('batches mineral limbs and dorsal scars without collapsing the four-limb rig', () => {
    const rig = createPursuerRig();
    updatePursuerRig(rig, { elapsed: 0.24, danger: 0.6, reducedMotion: false, stumble: false, captured: false });
    expect(rig.batches.length).toBeGreaterThan(1);
    expect(rig.batches.reduce((total, batch) => total + batch.sources.length, 0)).toBeGreaterThan(rig.batches.length);
    expect(rig.shadowCaster.name).toContain('pursuer-material-batch');
  });
});
