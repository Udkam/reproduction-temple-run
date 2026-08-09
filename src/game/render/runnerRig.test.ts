import { Box3, Matrix4, Mesh, MeshStandardMaterial, Triangle, Vector3 } from 'three';
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

function rigMatrices(rig: RunnerRig): number[] {
  rig.root.updateMatrixWorld(true);
  const values = [rig.root, rig.body, rig.pelvis, rig.chest, rig.leftArm, rig.rightArm, rig.leftForearm, rig.rightForearm,
    rig.leftLeg, rig.rightLeg, rig.leftShin, rig.rightShin, rig.leftFoot, rig.rightFoot, rig.coatLeft, rig.coatRight,
  ].flatMap((node) => node.matrixWorld.toArray());
  for (const { batch, instanceIds } of rig.batches) for (const id of instanceIds) values.push(...batch.getMatrixAt(id, new Matrix4()).toArray());
  return values;
}

function instanceMatrix(rig: RunnerRig, sourceName: string): number[] {
  for (const { batch, sources, instanceIds } of rig.batches) {
    const sourceIndex = sources.findIndex(({ name }) => name === sourceName);
    if (sourceIndex >= 0) return batch.getMatrixAt(instanceIds[sourceIndex]!, new Matrix4()).toArray();
  } throw new Error(`missing batch source ${sourceName}`);
}

function surfaceDistance(point: Vector3, mesh: Mesh): number {
  mesh.updateWorldMatrix(true, false); const position = mesh.geometry.getAttribute('position'); const index = mesh.geometry.getIndex();
  const a = new Vector3(); const b = new Vector3(); const c = new Vector3(); const closest = new Vector3();
  let minimum = Number.POSITIVE_INFINITY;
  for (let offset = 0; offset < (index?.count ?? position.count); offset += 3) {
    a.fromBufferAttribute(position, index?.getX(offset) ?? offset).applyMatrix4(mesh.matrixWorld); b.fromBufferAttribute(position, index?.getX(offset + 1) ?? offset + 1).applyMatrix4(mesh.matrixWorld);
    c.fromBufferAttribute(position, index?.getX(offset + 2) ?? offset + 2).applyMatrix4(mesh.matrixWorld);
    new Triangle(a, b, c).closestPointToPoint(point, closest); minimum = Math.min(minimum, closest.distanceTo(point));
  }
  return minimum;
}

function expectConnectedSockets(rig: RunnerRig): void {
  rig.root.updateMatrixWorld(true);
  for (const [name, middle, end] of [
    ['courier-left-arm', rig.leftForearm, modelMesh(rig, 'courier-left-arm-end').parent!],
    ['courier-right-arm', rig.rightForearm, modelMesh(rig, 'courier-right-arm-end').parent!],
    ['courier-left-leg', rig.leftShin, rig.leftFoot], ['courier-right-leg', rig.rightShin, rig.rightFoot],
  ] as const) {
    for (const [socket, first, second] of [[middle, `${name}-upper`, `${name}-lower`], [end, `${name}-lower`, `${name}-end`]] as const) {
      const point = socket.getWorldPosition(new Vector3());
      expect(surfaceDistance(point, modelMesh(rig, first)) + surfaceDistance(point, modelMesh(rig, second)), `${first}/${second} socket gap`).toBeLessThanOrEqual(0.025);
    }
  }
}

function validateBatchedGeometry(rig: RunnerRig): number {
  let triangles = 0; rig.root.updateMatrixWorld(true); const rootInverse = new Matrix4().copy(rig.root.matrixWorld).invert();
  for (const { batch, sources, instanceIds } of rig.batches) {
    const position = batch.geometry.getAttribute('position'); const index = batch.geometry.getIndex();
    expect(index, `${batch.name} index`).not.toBeNull();
    for (const attributeName of ['position', 'normal', 'uv']) expect(Array.from(batch.geometry.getAttribute(attributeName).array).every(Number.isFinite), `${batch.name} ${attributeName}`).toBe(true);
    for (let sourceNumber = 0; sourceNumber < sources.length; sourceNumber += 1) {
      const source = sources[sourceNumber]!; const instanceId = instanceIds[sourceNumber]!;
      const sourcePosition = source.geometry.getAttribute('position'); const sourceIndex = source.geometry.getIndex();
      const range = batch.getGeometryRangeAt(batch.getGeometryIdAt(instanceId))!;
      expect(range.vertexCount, `${source.name} vertices`).toBe(sourcePosition.count); expect(range.indexCount, `${source.name} indices`).toBe(sourceIndex?.count ?? sourcePosition.count);
      expect(range.indexCount).toBeGreaterThan(0); expect(range.indexCount % 3).toBe(0); const actualMatrix = batch.getMatrixAt(instanceId, new Matrix4()); expect(actualMatrix.elements.every(Number.isFinite)).toBe(true); expect(actualMatrix.elements).toEqual(new Matrix4().multiplyMatrices(rootInverse, source.matrixWorld).elements.map(Math.fround));
      const center = new Vector3();
      for (let vertex = 0; vertex < range.vertexCount; vertex += 1) {
        const batchedVertex = range.vertexStart + vertex; center.add(new Vector3().fromBufferAttribute(position, batchedVertex));
        expect([position.getX(batchedVertex), position.getY(batchedVertex), position.getZ(batchedVertex)]).toEqual([sourcePosition.getX(vertex), sourcePosition.getY(vertex), sourcePosition.getZ(vertex)]);
      }
      center.multiplyScalar(1 / range.vertexCount);
      const edges = new Map<string, number>(); const a = new Vector3(); const b = new Vector3(); const c = new Vector3();
      const vertexKey = (vertex: number) => [position.getX(vertex), position.getY(vertex), position.getZ(vertex)].map((value) => (Math.abs(value) < 5e-6 ? 0 : value).toFixed(5)).join(',');
      for (let offset = 0; offset < range.indexCount; offset += 3) {
        const ids = [0, 1, 2].map((step) => index!.getX(range.indexStart + offset + step));
        ids.forEach((id, step) => { expect(Number.isInteger(id) && id >= range.vertexStart && id < range.vertexStart + range.vertexCount, `${source.name} index`).toBe(true); expect(id).toBe((sourceIndex?.getX(offset + step) ?? offset + step) + range.vertexStart); });
        a.fromBufferAttribute(position, ids[0]!); b.fromBufferAttribute(position, ids[1]!); c.fromBufferAttribute(position, ids[2]!);
        const outward = b.clone().sub(a).cross(c.clone().sub(a));
        expect(outward.length(), `${source.name} area`).toBeGreaterThan(1e-8);
        expect(outward.dot(a.clone().add(b).add(c).multiplyScalar(1 / 3).sub(center)), `${source.name} outward`).toBeGreaterThan(1e-8);
        for (const [from, to] of [[ids[0]!, ids[1]!], [ids[1]!, ids[2]!], [ids[2]!, ids[0]!]]) {
          const key = [vertexKey(from), vertexKey(to)].sort().join('|'); edges.set(key, (edges.get(key) ?? 0) + 1);
        }
      }
      expect([...edges.values()].every((count) => count === 2), `${source.name} closed`).toBe(true);
      triangles += range.indexCount / 3;
    }
  }
  return triangles;
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

  it('reconstructs closed outward source and batched geometry with one actual caster', () => {
    const rig = createRunnerRig();
    updateRunnerRig(rig, { ...basePose, elapsed: 0.2, reducedMotion: false });
    expect(rig.batches).toHaveLength(6); expect(new Set(rig.modelMeshes.map((mesh) => mesh.material))).toHaveLength(6); expect(validateBatchedGeometry(rig)).toBeLessThanOrEqual(3_200);
    for (const mesh of rig.modelMeshes) {
      const size = mesh.geometry.boundingBox!.getSize(new Vector3());
      expect(Math.min(size.x, size.y, size.z), `${mesh.name} thickness`).toBeGreaterThan(0.02);
      expect(mesh.geometry.type, `${mesh.name} is not a plane`).not.toBe('PlaneGeometry');
    }
    const bounds = modelBounds(rig); const size = bounds.getSize(new Vector3());
    expect(bounds.min.y).toBeGreaterThanOrEqual(-0.031); expect(size.x).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.width);
    expect(size.y).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.height); expect(size.z).toBeLessThanOrEqual(RUNNER_RIG_BOUNDS.depth);
    const casters: Mesh[] = []; rig.root.traverse((node) => { if (node instanceof Mesh && node.castShadow) casters.push(node); });
    expect(casters).toEqual([rig.shadowCaster]);
    const coreMaterial = modelMesh(rig, 'courier-signal-core').material; expect(coreMaterial).toBeInstanceOf(MeshStandardMaterial); expect((coreMaterial as MeshStandardMaterial).emissiveIntensity).toBeLessThanOrEqual(0.3);
  });

  it('keeps connected sockets, grounded half-cycles, and deterministic action matrices', () => {
    const rig = createRunnerRig(); const leftClearance: number[] = []; const rightClearance: number[] = []; const deadMatrices: number[][] = [];
    const actionVector = (candidate: RunnerRig) => [candidate.body.rotation.x, candidate.body.rotation.y, candidate.body.rotation.z, candidate.chest.rotation.x, candidate.chest.rotation.y, candidate.chest.rotation.z, candidate.leftArm.rotation.x, candidate.rightArm.rotation.x, candidate.leftForearm.rotation.x, candidate.rightForearm.rotation.x, candidate.leftLeg.rotation.x, candidate.rightLeg.rotation.x, candidate.leftShin.rotation.x, candidate.rightShin.rotation.x, candidate.leftFoot.rotation.x, candidate.rightFoot.rotation.x, candidate.coatLeft.rotation.x, candidate.coatRight.rotation.x].map((value) => Object.is(value, -0) ? 0 : value);
    const authored = { jump: [0, 0, 0, -0.14 + 1.35 / 1.7 * 0.08, 0, 0, -0.78, -0.64, -0.52, -0.46, 0.38, 0.12, 0.88, 0.58, -0.42, -0.3, -0.34, -0.34 * 1.06], slide: [-0.56, 0, 0, -0.22, 0.06, 0.08, -1.02, -0.7, -0.64, -0.46, 1.02, 0.26, 0.58, 1.16, -0.34, -0.16, -0.06, -0.06 * 1.06], dead: [-0.26, 0, 0.2, -0.42, 0.12, 0.18, 0.74, -0.92, -0.82, -0.38, 0.8, 0.34, 1.18, 1.02, -0.46, -0.36, 0.1, 0.12] } as const;
    const poses = [
      ...Array.from({ length: RUNNER_GAIT_PHASE_COUNT }, (_, phase) => ({ posture: 'run' as const, height: 0, dead: false,
        elapsed: phase / RUNNER_GAIT_PHASE_COUNT / runnerMotionProfile(9).cyclesPerSecond })),
      { posture: 'jump' as const, height: 1.35, dead: false, elapsed: 1 },
      { posture: 'slide' as const, height: 0, dead: false, elapsed: 1 },
      ...(['run', 'jump', 'slide'] as const).map((posture) => ({ posture, height: 0, dead: true, elapsed: 1 })),
    ];
    for (const pose of poses) {
      rig.root.position.y = pose.height; updateRunnerRig(rig, { ...basePose, ...pose, speed: 9, reducedMotion: false });
      const fresh = createRunnerRig(); fresh.root.position.y = pose.height; updateRunnerRig(fresh, { ...basePose, ...pose, speed: 9, reducedMotion: false });
      expect(rigMatrices(rig)).toEqual(rigMatrices(fresh)); expectConnectedSockets(rig); const bounds = modelBounds(rig); const label = JSON.stringify(pose); if (pose.posture === 'jump' && !pose.dead) expect(bounds.min.y, label).toBeGreaterThanOrEqual(1.3); else expect(Math.abs(bounds.min.y), label).toBeLessThanOrEqual(0.03); expect(rig.shadow.getWorldPosition(new Vector3()).y, label).toBeCloseTo(0.015, 3); if (pose.posture !== 'run' || pose.dead) expect(actionVector(rig)).toEqual(authored[pose.dead ? 'dead' : pose.posture === 'jump' ? 'jump' : 'slide']);
      if (pose.posture === 'run' && !pose.dead) {
        const left = worldBounds(modelMesh(rig, 'courier-left-leg-end')).min.y; const right = worldBounds(modelMesh(rig, 'courier-right-leg-end')).min.y;
        expect(Math.abs(Math.min(left, right))).toBeLessThanOrEqual(0.03); leftClearance.push(left); rightClearance.push(right);
      }
      if (pose.dead) deadMatrices.push(rigMatrices(rig));
    }
    expect(Math.max(...leftClearance, ...rightClearance)).toBeGreaterThan(0.045); for (let phase = 0; phase < RUNNER_GAIT_PHASE_COUNT; phase += 1) expect(leftClearance[phase]).toBeCloseTo(rightClearance[(phase + 4) % RUNNER_GAIT_PHASE_COUNT]!, 5);
    expect(deadMatrices[1]).toEqual(deadMatrices[0]); expect(deadMatrices[2]).toEqual(deadMatrices[0]);
  });

  it('orders actual cadence, arm, stride, and compression transforms by speed', () => {
    const low = runnerMotionProfile(9); const high = runnerMotionProfile(19); expect(high.cyclesPerSecond).toBeGreaterThan(low.cyclesPerSecond);
    const lowRig = createRunnerRig(); const highRig = createRunnerRig(); const phase = 1 / RUNNER_GAIT_PHASE_COUNT;
    updateRunnerRig(lowRig, { ...basePose, speed: 9, elapsed: phase / low.cyclesPerSecond, reducedMotion: false });
    updateRunnerRig(highRig, { ...basePose, speed: 19, elapsed: phase / high.cyclesPerSecond, reducedMotion: false });
    expect(Math.abs(highRig.leftArm.rotation.x + 0.08)).toBeGreaterThan(Math.abs(lowRig.leftArm.rotation.x + 0.08));
    expect(Math.abs(highRig.leftLeg.rotation.x + 0.08)).toBeGreaterThan(Math.abs(lowRig.leftLeg.rotation.x + 0.08));
    expect(highRig.pelvis.position.y).toBeLessThan(lowRig.pelvis.position.y);
    expect(instanceMatrix(highRig, 'courier-left-arm-upper')).not.toEqual(instanceMatrix(lowRig, 'courier-left-arm-upper'));
    expect(instanceMatrix(highRig, 'courier-hip-shell')).not.toEqual(instanceMatrix(lowRig, 'courier-hip-shell'));
    for (const [speed, profile] of [[9, low], [19, high]] as const) {
      const start = createRunnerRig(); const cycle = createRunnerRig();
      updateRunnerRig(start, { ...basePose, speed, elapsed: 0, reducedMotion: false }); updateRunnerRig(cycle, { ...basePose, speed, elapsed: 1 / profile.cyclesPerSecond, reducedMotion: false });
      expect(cycle.leftLeg.rotation.x).toBeCloseTo(start.leftLeg.rotation.x, 10); expect(cycle.leftArm.rotation.x).toBeCloseTo(start.leftArm.rotation.x, 10);
    }
  });

  it('keeps reduced secondary motion frozen while all primary limbs remain continuous', () => {
    const rig = createRunnerRig(); updateRunnerRig(rig, { ...basePose, elapsed: 1, reducedMotion: true });
    const secondary = [rig.pelvis.rotation.y, rig.pelvis.rotation.z, rig.chest.rotation.y, rig.chest.rotation.z, rig.core.rotation.x, rig.core.rotation.y,
      rig.shield.rotation.z, rig.coatLeft.rotation.x, rig.coatLeft.rotation.y, rig.coatLeft.rotation.z, rig.coatRight.rotation.x, rig.coatRight.rotation.y, rig.coatRight.rotation.z]; const rotationIndices = [0, 1, 2, 4, 5, 6, 8, 9, 10]; const secondaryNames = ['courier-tapered-torso', 'courier-coat-left', 'courier-coat-right', 'courier-signal-core']; const batchSecondary = secondaryNames.map((name) => rotationIndices.map((index) => instanceMatrix(rig, name)[index]));
    const primaryNames = ['left-arm', 'right-arm', 'left-leg', 'right-leg'].flatMap((limb) => ['upper', 'lower', 'end'].map((part) => `courier-${limb}-${part}`)); const primary = primaryNames.map((name) => instanceMatrix(rig, name)); const normal = createRunnerRig(); updateRunnerRig(normal, { ...basePose, elapsed: 1, reducedMotion: false });
    const magnitude = (candidate: RunnerRig) => Math.abs(candidate.leftArm.rotation.x + 0.08) + Math.abs(candidate.rightArm.rotation.x + 0.08) + Math.abs(candidate.leftLeg.rotation.x + 0.08) + Math.abs(candidate.rightLeg.rotation.x + 0.08) + Math.abs(candidate.leftForearm.rotation.x) + Math.abs(candidate.rightForearm.rotation.x) + Math.abs(candidate.leftShin.rotation.x - 0.12) + Math.abs(candidate.rightShin.rotation.x - 0.12); expect(magnitude(rig)).toBeLessThan(magnitude(normal)); expect(Math.sign(rig.leftLeg.rotation.x + 0.08)).toBe(-Math.sign(rig.rightLeg.rotation.x + 0.08));
    updateRunnerRig(rig, { ...basePose, elapsed: 1.01, reducedMotion: true }); const nextPrimary = primaryNames.map((name) => instanceMatrix(rig, name)); nextPrimary.forEach((matrix, matrixIndex) => { expect(matrix).not.toEqual(primary[matrixIndex]); expect(Math.max(...matrix.map((value, index) => Math.abs(value - primary[matrixIndex]![index]!)))).toBeLessThan(0.08); });
    updateRunnerRig(rig, { ...basePose, elapsed: 9, reducedMotion: true }); expect([rig.pelvis.rotation.y, rig.pelvis.rotation.z, rig.chest.rotation.y, rig.chest.rotation.z,
      rig.core.rotation.x, rig.core.rotation.y, rig.shield.rotation.z, rig.coatLeft.rotation.x, rig.coatLeft.rotation.y, rig.coatLeft.rotation.z, rig.coatRight.rotation.x, rig.coatRight.rotation.y, rig.coatRight.rotation.z]).toEqual(secondary); expect(secondaryNames.map((name) => rotationIndices.map((index) => instanceMatrix(rig, name)[index]))).toEqual(batchSecondary);
    for (const posture of ['jump', 'slide', 'run'] as const) {
      const normal = createRunnerRig(); const reduced = createRunnerRig(); const dead = posture === 'run'; const expected = dead ? [0.1, 0.12] : posture === 'jump' ? [-0.34, -0.34 * 1.06] : [-0.06, -0.06 * 1.06];
      updateRunnerRig(normal, { ...basePose, posture, dead, elapsed: 2, reducedMotion: false }); updateRunnerRig(reduced, { ...basePose, posture, dead, elapsed: 2, reducedMotion: true });
      expect([normal.coatLeft.rotation.x, normal.coatRight.rotation.x]).toEqual(expected); expect([reduced.coatLeft.rotation.x, reduced.coatRight.rotation.x]).toEqual(expected);
    }
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
