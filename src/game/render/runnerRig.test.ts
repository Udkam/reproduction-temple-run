import { describe, expect, it } from 'vitest';
import { RUNNER_GAIT_PHASE_COUNT, createRunnerRig, sampleRunnerGait, updateRunnerRig } from './runnerRig';

const basePose = {
  speed: 12,
  laneDelta: 0,
  height: 0,
  posture: 'run' as const,
  shield: true,
  dead: false,
};

describe('runner reduced motion', () => {
  it('interpolates all eight authored gait phases without a boundary jump or limb-side flip', () => {
    const keyframes = Array.from({ length: RUNNER_GAIT_PHASE_COUNT }, (_, index) => sampleRunnerGait(index / RUNNER_GAIT_PHASE_COUNT));
    expect(new Set(keyframes.map((sample) => sample.thigh))).toHaveLength(RUNNER_GAIT_PHASE_COUNT);
    expect(keyframes.some((sample) => sample.thigh > 0)).toBe(true);
    expect(keyframes.some((sample) => sample.thigh < 0)).toBe(true);

    const samples = Array.from({ length: 65 }, (_, index) => sampleRunnerGait(index / 64));
    for (let index = 1; index < samples.length; index += 1) {
      const previous = samples[index - 1]!;
      const current = samples[index]!;
      expect(Math.abs(current.thigh - previous.thigh)).toBeLessThan(0.16);
      expect(Math.abs(current.shin - previous.shin)).toBeLessThan(0.2);
      expect(Math.abs(current.arm - previous.arm)).toBeLessThan(0.15);
    }
    expect(Math.abs(samples[0]!.foot - samples.at(-1)!.foot)).toBeLessThan(0.001);
  });

  it('keeps decorative core and shield rotations static', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 1, reducedMotion: true });
    const first = [rig.core.rotation.x, rig.core.rotation.y, rig.shield.rotation.z];
    updateRunnerRig(rig, { ...basePose, elapsed: 9, reducedMotion: true });
    expect([rig.core.rotation.x, rig.core.rotation.y, rig.shield.rotation.z]).toEqual(first);
  });

  it('retains authored rotation while normal motion is enabled', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 1, reducedMotion: false });
    const first = rig.core.rotation.y;
    updateRunnerRig(rig, { ...basePose, elapsed: 2, reducedMotion: false });
    expect(rig.core.rotation.y).not.toBe(first);
  });

  it('uses articulated hips, knees, feet, and counter-rotating torso during a run', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 0.05, reducedMotion: false });
    const first = {
      hip: rig.leftLeg.rotation.x,
      knee: rig.leftShin.rotation.x,
      foot: rig.leftFoot.rotation.x,
      pelvis: rig.pelvis.rotation.y,
      chest: rig.chest.rotation.y,
    };
    updateRunnerRig(rig, { ...basePose, elapsed: 0.19, reducedMotion: false });
    expect(rig.leftLeg.rotation.x).not.toBe(first.hip);
    expect(rig.leftShin.rotation.x).not.toBe(first.knee);
    expect(rig.leftFoot.rotation.x).not.toBe(first.foot);
    expect(rig.pelvis.rotation.y).not.toBe(first.pelvis);
    expect(rig.chest.rotation.y).not.toBe(first.chest);
    expect(Math.sign(rig.pelvis.rotation.y)).toBe(-Math.sign(rig.chest.rotation.y));
  });

  it('batches animated material pieces while retaining one real rig shadow caster', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 0.3, reducedMotion: false });
    expect(rig.batches.length).toBeGreaterThan(1);
    expect(rig.batches.reduce((total, batch) => total + batch.sources.length, 0)).toBeGreaterThan(rig.batches.length);
    expect(rig.shadowCaster.name).toContain('courier-material-batch');
  });

  it('keeps jump and slide as distinct semantic whole-body poses', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 1, posture: 'jump', height: 1.4, reducedMotion: true });
    const jump = [rig.body.position.y, rig.leftShin.rotation.x, rig.body.rotation.x];
    updateRunnerRig(rig, { ...basePose, elapsed: 1, posture: 'slide', height: 0, reducedMotion: true });
    expect([rig.body.position.y, rig.leftShin.rotation.x, rig.body.rotation.x]).not.toEqual(jump);
    expect(rig.body.position.y).toBeLessThan(0);
    expect(rig.body.rotation.x).toBeLessThan(-0.5);
  });
});
