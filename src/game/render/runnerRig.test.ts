import { Box3, Mesh, MeshStandardMaterial, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import {
  RUNNER_GAIT_PHASE_COUNT,
  RUNNER_RIG_BOUNDS,
  createRunnerRig,
  runnerMotionProfile,
  sampleRunnerGait,
  updateRunnerRig,
  type RunnerRig,
} from './runnerRig';

const basePose = {
  speed: 12,
  laneDelta: 0,
  height: 0,
  posture: 'run' as const,
  shield: true,
  dead: false,
};

function modelMesh(rig: RunnerRig, name: string): Mesh {
  const mesh = rig.modelMeshes.find((candidate) => candidate.name === name);
  expect(mesh, `missing ${name}`).toBeDefined();
  return mesh!;
}

function worldBounds(mesh: Mesh): Box3 {
  mesh.updateWorldMatrix(true, false);
  if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
  return mesh.geometry.boundingBox!.clone().applyMatrix4(mesh.matrixWorld);
}

function modelBounds(rig: RunnerRig): Box3 {
  rig.root.updateMatrixWorld(true);
  const bounds = new Box3();
  for (const mesh of rig.modelMeshes) bounds.union(worldBounds(mesh));
  return bounds;
}

function poseVector(rig: RunnerRig): number[] {
  return [
    rig.body, rig.pelvis, rig.chest,
    rig.leftArm, rig.rightArm, rig.leftForearm, rig.rightForearm,
    rig.leftLeg, rig.rightLeg, rig.leftShin, rig.rightShin,
    rig.leftFoot, rig.rightFoot, rig.coatLeft, rig.coatRight,
  ].flatMap((node) => [
    node.position.x, node.position.y, node.position.z,
    node.rotation.x, node.rotation.y, node.rotation.z,
  ]);
}

function triangleMetrics(mesh: Mesh): { count: number; minimumDoubleArea: number } {
  const position = mesh.geometry.getAttribute('position');
  const index = mesh.geometry.getIndex();
  const count = (index?.count ?? position.count) / 3;
  let minimumDoubleArea = Number.POSITIVE_INFINITY;
  const a = new Vector3();
  const b = new Vector3();
  const c = new Vector3();
  for (let triangle = 0; triangle < count; triangle += 1) {
    const offset = triangle * 3;
    a.fromBufferAttribute(position, index?.getX(offset) ?? offset);
    b.fromBufferAttribute(position, index?.getX(offset + 1) ?? offset + 1);
    c.fromBufferAttribute(position, index?.getX(offset + 2) ?? offset + 2);
    minimumDoubleArea = Math.min(minimumDoubleArea, b.sub(a).cross(c.sub(a)).length());
  }
  return { count, minimumDoubleArea };
}

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

  it('builds a bounded six-material volumetric courier from finite non-degenerate triangles', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 0.2, reducedMotion: false });
    expect(rig.batches).toHaveLength(6);
    expect(new Set(rig.modelMeshes.map((mesh) => mesh.material))).toHaveLength(6);

    let triangles = 0;
    for (const mesh of rig.modelMeshes) {
      for (const attributeName of ['position', 'normal', 'uv']) {
        const attribute = mesh.geometry.getAttribute(attributeName);
        expect(attribute, `${mesh.name} ${attributeName}`).toBeDefined();
        expect(Array.from(attribute.array).every(Number.isFinite), `${mesh.name} ${attributeName} finite`).toBe(true);
      }
      const metrics = triangleMetrics(mesh);
      triangles += metrics.count;
      expect(metrics.minimumDoubleArea, `${mesh.name} non-degenerate`).toBeGreaterThan(1e-8);
    }
    expect(triangles).toBeLessThanOrEqual(3_200);

    for (const name of [
      'courier-tapered-torso', 'courier-shoulder-mantle', 'courier-layered-cowl',
      'courier-relay-housing', 'courier-left-arm-upper', 'courier-left-arm-lower',
      'courier-left-leg-upper', 'courier-left-leg-lower', 'courier-left-leg-end',
      'courier-right-leg-end', 'courier-coat-left', 'courier-coat-right',
    ]) {
      const mesh = modelMesh(rig, name);
      const size = mesh.geometry.boundingBox!.getSize(new Vector3());
      expect(Math.min(size.x, size.y, size.z), `${name} has thickness`).toBeGreaterThan(0.02);
      expect(mesh.geometry.type, `${name} is not a plane`).not.toBe('PlaneGeometry');
    }

    const bounds = modelBounds(rig);
    const size = bounds.getSize(new Vector3());
    const zExtents = rig.modelMeshes.map((mesh) => ({ name: mesh.name, bounds: worldBounds(mesh) }));
    const front = zExtents.reduce((lowest, value) => value.bounds.min.z < lowest.bounds.min.z ? value : lowest);
    const back = zExtents.reduce((highest, value) => value.bounds.max.z > highest.bounds.max.z ? value : highest);
    expect(bounds.min.y).toBeGreaterThanOrEqual(-0.031);
    expect(size.x).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.width);
    expect(size.y).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.height);
    expect(size.z, `${front.name} to ${back.name}`).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.depth);
    expect(worldBounds(modelMesh(rig, 'courier-shoulder-mantle')).getSize(new Vector3()).x / size.y)
      .toBeGreaterThanOrEqual(0.24);
    expect(worldBounds(modelMesh(rig, 'courier-waist-harness')).getSize(new Vector3()).x / size.y)
      .toBeGreaterThanOrEqual(0.16);
    expect(worldBounds(modelMesh(rig, 'courier-left-leg-end')).getSize(new Vector3()).z / size.y)
      .toBeGreaterThanOrEqual(0.11);

    const coreMaterial = modelMesh(rig, 'courier-signal-core').material;
    expect(coreMaterial).toBeInstanceOf(MeshStandardMaterial);
    expect((coreMaterial as MeshStandardMaterial).emissiveIntensity).toBeLessThanOrEqual(0.3);
  });

  it('anchors real boot geometry while preserving alternating swing clearance across eight phases', () => {
    const rig = createRunnerRig();
    const clearances: number[] = [];
    const supportSides = new Set<string>();
    for (let phase = 0; phase < RUNNER_GAIT_PHASE_COUNT; phase += 1) {
      updateRunnerRig(rig, {
        ...basePose,
        speed: 9,
        elapsed: phase / RUNNER_GAIT_PHASE_COUNT / runnerMotionProfile(9).cyclesPerSecond,
        reducedMotion: false,
      });
      const left = worldBounds(modelMesh(rig, 'courier-left-leg-end')).min.y;
      const right = worldBounds(modelMesh(rig, 'courier-right-leg-end')).min.y;
      expect(Math.min(left, right)).toBeLessThanOrEqual(0.031);
      expect(Math.min(left, right)).toBeGreaterThanOrEqual(-0.031);
      clearances.push(Math.max(left, right));
      supportSides.add(left <= right ? 'left' : 'right');
    }
    expect(Math.max(...clearances)).toBeGreaterThan(0.045);
    expect(supportSides).toEqual(new Set(['left', 'right']));
  });

  it('makes jump, slide, and dead matrices independent of their preceding gait phase', () => {
    const semanticPoses = [
      { posture: 'jump' as const, height: 1.35, dead: false },
      { posture: 'slide' as const, height: 0, dead: false },
      { posture: 'run' as const, height: 0, dead: true },
    ];
    for (const semanticPose of semanticPoses) {
      const early = createRunnerRig();
      const late = createRunnerRig();
      updateRunnerRig(early, { ...basePose, elapsed: 0.03, reducedMotion: false });
      updateRunnerRig(late, { ...basePose, elapsed: 0.37, reducedMotion: false });
      early.root.position.y = semanticPose.height;
      late.root.position.y = semanticPose.height;
      updateRunnerRig(early, { ...basePose, ...semanticPose, elapsed: 1, reducedMotion: false });
      updateRunnerRig(late, { ...basePose, ...semanticPose, elapsed: 1, reducedMotion: false });
      expect(poseVector(early)).toEqual(poseVector(late));
      expect(modelBounds(early).min.y).toBeGreaterThanOrEqual(semanticPose.posture === 'jump' ? 1.3 : -0.031);
    }
  });

  it('orders cadence, stride, arm swing, and contact compression by speed', () => {
    const low = runnerMotionProfile(9);
    const high = runnerMotionProfile(19);
    expect(high.cyclesPerSecond).toBeGreaterThan(low.cyclesPerSecond);
    expect(high.strideAmplitude).toBeGreaterThan(low.strideAmplitude);
    expect(high.armAmplitude).toBeGreaterThan(low.armAmplitude);
    expect(high.compressionAmplitude).toBeGreaterThan(low.compressionAmplitude);
  });

  it('keeps decorative core and shield rotations static', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 1, reducedMotion: true });
    const first = [
      rig.core.rotation.x, rig.core.rotation.y, rig.shield.rotation.z,
      rig.coatLeft.rotation.x, rig.coatRight.rotation.x,
    ];
    updateRunnerRig(rig, { ...basePose, elapsed: 9, reducedMotion: true });
    expect([
      rig.core.rotation.x, rig.core.rotation.y, rig.shield.rotation.z,
      rig.coatLeft.rotation.x, rig.coatRight.rotation.x,
    ]).toEqual(first);
  });

  it('keeps reduced-motion primary limbs continuous instead of time-quantized', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 1, reducedMotion: true });
    const first = rig.leftLeg.rotation.x;
    updateRunnerRig(rig, { ...basePose, elapsed: 1.01, reducedMotion: true });
    expect(rig.leftLeg.rotation.x).not.toBe(first);
    expect(Math.abs(rig.leftLeg.rotation.x - first)).toBeLessThan(0.08);
    expect(rig.pelvis.rotation.y).toBe(0);
    expect(rig.chest.rotation.y).toBe(0);
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
    expect(modelBounds(rig).min.y).toBeGreaterThanOrEqual(-0.031);
    expect(rig.body.rotation.x).toBeLessThan(-0.5);
  });
});
