import {
  BatchedMesh,
  Box3,
  BufferGeometry,
  CylinderGeometry,
  DoubleSide,
  Float32BufferAttribute,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshStandardMaterial,
  Matrix4,
  RingGeometry,
  Vector3,
} from 'three';
import { PALETTE } from './theme';

/** Ground-anchored visual extent used only for renderer screen evidence. */
export const RUNNER_RIG_BOUNDS = { width: 0.96, height: 2.58, depth: 0.82 } as const;

export interface RunnerRig {
  root: Group;
  body: Group;
  pelvis: Group;
  chest: Group;
  leftArm: Group;
  rightArm: Group;
  leftForearm: Group;
  rightForearm: Group;
  leftLeg: Group;
  rightLeg: Group;
  leftShin: Group;
  rightShin: Group;
  leftFoot: Group;
  rightFoot: Group;
  coatLeft: Mesh;
  coatRight: Mesh;
  core: Mesh;
  shield: Mesh;
  shadow: Mesh;
  shadowCaster: BatchedMesh;
  batches: readonly RigBatch[];
  modelMeshes: readonly Mesh[];
}

interface RigBatch {
  batch: BatchedMesh;
  sources: readonly Mesh[];
  instanceIds: readonly number[];
}

function batchRigMeshes(root: Group, meshes: readonly Mesh[]): RigBatch[] {
  const byMaterial = new Map<MeshStandardMaterial, Mesh[]>();
  for (const mesh of meshes) {
    const material = mesh.material;
    if (!(material instanceof MeshStandardMaterial)) continue;
    const group = byMaterial.get(material) ?? [];
    group.push(mesh);
    byMaterial.set(material, group);
  }
  return [...byMaterial.values()].map((sources, index) => {
    const vertexCount = sources.reduce((total, mesh) => total + mesh.geometry.getAttribute('position').count, 0);
    const indexCount = sources.reduce((total, mesh) => total + (mesh.geometry.getIndex()?.count ?? mesh.geometry.getAttribute('position').count), 0);
    const batch = new BatchedMesh(sources.length, vertexCount, indexCount, sources[0]!.material as MeshStandardMaterial);
    batch.name = `courier-material-batch-${index}`;
    batch.frustumCulled = false;
    batch.perObjectFrustumCulled = false;
    const instanceIds = sources.map((mesh) => {
      const geometry = mesh.geometry.getIndex() ? mesh.geometry : mesh.geometry.clone();
      if (!geometry.getIndex()) {
        const positions = geometry.getAttribute('position');
        geometry.setIndex(Array.from({ length: positions.count }, (_, position) => position));
      }
      const geometryId = batch.addGeometry(geometry);
      if (geometry !== mesh.geometry) geometry.dispose();
      return batch.addInstance(geometryId);
    });
    for (const mesh of sources) mesh.visible = false;
    root.add(batch);
    return { batch, sources, instanceIds };
  });
}

function syncRigBatches(root: Group, batches: readonly RigBatch[]): void {
  root.updateMatrixWorld(true);
  const rootInverse = new Matrix4().copy(root.matrixWorld).invert();
  for (const { batch, sources, instanceIds } of batches) {
    for (let index = 0; index < sources.length; index += 1) {
      const source = sources[index];
      const instanceId = instanceIds[index];
      if (!source || instanceId === undefined) continue;
      batch.setMatrixAt(instanceId, new Matrix4().multiplyMatrices(rootInverse, source.matrixWorld));
    }
  }
}

interface JointedLimb {
  upper: Group;
  lower: Group;
  end: Group;
}

const BASE_PELVIS_Y = 1.02;
const COAT_LEFT_Z = -0.1;
const COAT_RIGHT_Z = 0.12;

function taperedVolume(
  topWidth: number,
  bottomWidth: number,
  height: number,
  topDepth: number,
  bottomDepth: number,
  bottomX = 0,
  bottomZ = 0,
): BufferGeometry {
  const positions = [
    -topWidth / 2, 0, -topDepth / 2,
    topWidth / 2, 0, -topDepth / 2,
    topWidth / 2, 0, topDepth / 2,
    -topWidth / 2, 0, topDepth / 2,
    bottomX - bottomWidth / 2, -height, bottomZ - bottomDepth / 2,
    bottomX + bottomWidth / 2, -height, bottomZ - bottomDepth / 2,
    bottomX + bottomWidth / 2, -height, bottomZ + bottomDepth / 2,
    bottomX - bottomWidth / 2, -height, bottomZ + bottomDepth / 2,
  ];
  const indices = [
    0, 3, 2, 0, 2, 1,
    4, 5, 6, 4, 6, 7,
    0, 1, 5, 0, 5, 4,
    1, 2, 6, 1, 6, 5,
    2, 3, 7, 2, 7, 6,
    3, 0, 4, 3, 4, 7,
  ];
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setAttribute('uv', new Float32BufferAttribute([
    0, 0, 1, 0, 1, 1, 0, 1,
    0, 0, 1, 0, 1, 1, 0, 1,
  ], 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  return geometry;
}

function courierMesh(name: string, geometry: BufferGeometry, material: MeshStandardMaterial): Mesh {
  const mesh = new Mesh(geometry, material);
  mesh.name = name;
  return mesh;
}

function segment(
  name: string,
  materials: {
    upper: MeshStandardMaterial;
    lower: MeshStandardMaterial;
    joint: MeshStandardMaterial;
    end: MeshStandardMaterial;
  },
  upperLength: number,
  lowerLength: number,
  radius: number,
  endScale: readonly [number, number, number],
): JointedLimb {
  const upper = new Group();
  upper.name = `${name}-upper-joint`;
  const upperMesh = courierMesh(
    `${name}-upper`,
    new CylinderGeometry(radius * 0.78, radius, upperLength, 8, 2),
    materials.upper,
  );
  upperMesh.position.y = -upperLength * 0.5;
  upperMesh.scale.z = 0.82;
  upper.add(upperMesh);

  const lower = new Group();
  lower.name = `${name}-lower-joint`;
  lower.position.y = -upperLength;
  const joint = courierMesh(
    `${name}-joint-guard`,
    new CylinderGeometry(radius * 0.74, radius * 0.82, radius > 0.1 ? 0.06 : 0.045, 8, 1),
    materials.joint,
  );
  joint.position.y = -0.018;
  joint.scale.z = 0.82;
  const lowerMesh = courierMesh(
    `${name}-lower`,
    new CylinderGeometry(radius * 0.62, radius * 0.82, lowerLength, 8, 2),
    materials.lower,
  );
  lowerMesh.position.y = -lowerLength * 0.5;
  lowerMesh.scale.z = 0.78;
  lower.add(joint, lowerMesh);
  upper.add(lower);

  const end = new Group();
  end.name = `${name}-end-joint`;
  end.position.y = -lowerLength;
  const endMesh = courierMesh(
    `${name}-end`,
    taperedVolume(
      endScale[0] * 0.8,
      endScale[0],
      endScale[1],
      endScale[2] * 0.58,
      endScale[2],
      0,
      -endScale[2] * 0.14,
    ),
    materials.end,
  );
  end.add(endMesh);
  lower.add(end);
  return { upper, lower, end };
}

export function createRunnerRig(): RunnerRig {
  const porcelain = new MeshStandardMaterial({ color: PALETTE.porcelain, roughness: 0.76, metalness: 0.02 });
  const cloth = new MeshStandardMaterial({ color: 0x3a6674, roughness: 0.96, metalness: 0 });
  const leather = new MeshStandardMaterial({ color: 0x4b4136, roughness: 0.84, metalness: 0.01 });
  const jade = new MeshStandardMaterial({ color: 0x4f7b86, roughness: 0.56, metalness: 0.14 });
  const signal = new MeshStandardMaterial({
    color: PALETTE.hazard,
    emissive: PALETTE.hazard,
    emissiveIntensity: 0.14,
    roughness: 0.48,
  });
  const coatMaterial = new MeshStandardMaterial({
    color: 0x5e8990,
    roughness: 0.94,
    metalness: 0,
  });
  porcelain.name = 'courier-skin';
  cloth.name = 'courier-cloth'; leather.name = 'courier-leather';
  jade.name = 'courier-mineral-hardware'; signal.name = 'courier-signal-inset';
  coatMaterial.name = 'courier-coat';

  const root = new Group();
  root.name = 'courier';
  const body = new Group();
  body.name = 'courier-body';
  const pelvis = new Group();
  pelvis.name = 'courier-pelvis-joint';
  const chest = new Group();
  chest.name = 'courier-chest-joint';
  root.add(body);
  body.add(pelvis);
  pelvis.position.y = BASE_PELVIS_Y;
  pelvis.add(chest);
  chest.position.y = 0.43;

  const hip = courierMesh('courier-hip-shell', taperedVolume(0.4, 0.34, 0.28, 0.28, 0.24), leather);
  hip.position.y = 0.1;
  const waist = courierMesh('courier-waist-harness', taperedVolume(0.36, 0.39, 0.14, 0.24, 0.26), leather);
  waist.position.y = 0.22;
  pelvis.add(hip, waist);

  const torso = courierMesh('courier-tapered-torso', taperedVolume(0.54, 0.34, 0.76, 0.3, 0.24), cloth);
  torso.position.y = 0.6;
  const mantle = courierMesh('courier-shoulder-mantle', taperedVolume(0.64, 0.44, 0.2, 0.34, 0.27), jade);
  mantle.position.y = 0.61;
  chest.add(torso, mantle);

  for (const side of [-1, 1] as const) {
    const strap = courierMesh(
      `courier-harness-${side < 0 ? 'left' : 'right'}`,
      taperedVolume(0.072, 0.062, 0.44, 0.045, 0.04, side * 0.015),
      leather,
    );
    strap.position.set(side * 0.18, 0.5, 0.185); strap.rotation.z = -side * 0.18;
    chest.add(strap);
  }

  const relayHousing = courierMesh(
    'courier-relay-housing',
    taperedVolume(0.2, 0.15, 0.28, 0.08, 0.095, 0, 0.014),
    jade,
  );
  relayHousing.position.set(0.16, 0.5, 0.195);
  const relayCollar = courierMesh(
    'courier-relay-collar',
    taperedVolume(0.14, 0.11, 0.045, 0.055, 0.045),
    jade,
  );
  relayCollar.position.set(0.16, 0.31, 0.255);
  relayCollar.rotation.x = Math.PI / 2;
  const core = courierMesh('courier-signal-core', taperedVolume(0.085, 0.065, 0.035, 0.026, 0.022), signal);
  core.position.set(0.16, 0.42, 0.27);
  chest.add(relayHousing, relayCollar, core);

  const neck = courierMesh('courier-neck', new CylinderGeometry(0.1, 0.115, 0.16, 8), porcelain);
  neck.position.y = 0.66;
  const cowl = courierMesh('courier-layered-cowl', new CylinderGeometry(0.22, 0.3, 0.18, 10, 1), jade);
  cowl.position.y = 0.7;
  cowl.scale.z = 0.84;
  const hood = courierMesh('courier-hood-shell', new IcosahedronGeometry(0.19, 1), cloth);
  hood.position.set(0, 0.84, 0.035);
  hood.scale.set(0.92, 1.08, 0.78);
  const hoodRidge = courierMesh('courier-hood-ridge', taperedVolume(0.11, 0.07, 0.48, 0.06, 0.045, 0.02, 0.02), coatMaterial);
  hoodRidge.position.set(0.1, 0.96, 0.19); hoodRidge.rotation.z = 0.28;
  const face = courierMesh('courier-face', new IcosahedronGeometry(0.17, 1), porcelain);
  face.position.set(0, 0.81, -0.115);
  face.scale.set(0.9, 1.03, 0.68);
  chest.add(neck, cowl, hood, hoodRidge, face);

  const armMaterials = { upper: cloth, lower: cloth, joint: leather, end: leather };
  const leftArmParts = segment('courier-left-arm', armMaterials, 0.37, 0.34, 0.09, [0.13, 0.14, 0.15]);
  const rightArmParts = segment('courier-right-arm', armMaterials, 0.37, 0.34, 0.09, [0.13, 0.14, 0.15]);
  leftArmParts.upper.position.set(-0.31, 0.52, 0);
  rightArmParts.upper.position.set(0.31, 0.52, 0);
  chest.add(leftArmParts.upper, rightArmParts.upper);

  const legMaterials = { upper: cloth, lower: leather, joint: jade, end: leather };
  const leftLegParts = segment('courier-left-leg', legMaterials, 0.49, 0.44, 0.115, [0.19, 0.11, 0.36]);
  const rightLegParts = segment('courier-right-leg', legMaterials, 0.49, 0.44, 0.115, [0.19, 0.11, 0.36]);
  leftLegParts.upper.position.set(-0.16, -0.02, 0);
  rightLegParts.upper.position.set(0.16, -0.02, 0);
  pelvis.add(leftLegParts.upper, rightLegParts.upper);

  const coatLeft = courierMesh(
    'courier-coat-left',
    taperedVolume(0.26, 0.16, 0.7, 0.105, 0.07, -0.12, 0.02),
    coatMaterial,
  );
  const coatRight = courierMesh(
    'courier-coat-right',
    taperedVolume(0.23, 0.14, 0.57, 0.1, 0.07, 0.09, 0.018),
    coatMaterial,
  );
  coatLeft.position.set(-0.14, 0.12, 0.12); coatRight.position.set(0.14, 0.11, 0.13);
  coatLeft.rotation.set(-0.12, -0.12, COAT_LEFT_Z); coatRight.rotation.set(-0.15, 0.16, COAT_RIGHT_Z);
  pelvis.add(coatLeft, coatRight);

  const shieldMaterial = new MeshStandardMaterial({
    color: PALETTE.signal,
    emissive: PALETTE.signal,
    emissiveIntensity: 0.45,
    transparent: true,
    opacity: 0.42,
    side: DoubleSide,
  });
  const shield = new Mesh(new RingGeometry(0.84, 0.89, 32), shieldMaterial);
  shield.position.y = 0.95;
  shield.rotation.x = Math.PI / 2;
  shield.visible = false;
  root.add(shield);

  const shadowMaterial = new MeshStandardMaterial({ color: 0x10120f, transparent: true, opacity: 0.33, depthWrite: false });
  const shadow = new Mesh(new CylinderGeometry(0.52, 0.72, 0.012, 24), shadowMaterial);
  shadow.scale.z = 0.55;
  shadow.position.y = 0.015;
  root.add(shadow);

  const modelMeshes: Mesh[] = [];
  body.traverse((child) => {
    if (child instanceof Mesh) modelMeshes.push(child);
  });
  const batches = batchRigMeshes(root, modelMeshes);
  const shadowCaster = batches.find((batch) => batch.sources.includes(hip))?.batch ?? batches[0]!.batch; shadowCaster.castShadow = true;
  return {
    root,
    body,
    pelvis,
    chest,
    leftArm: leftArmParts.upper,
    rightArm: rightArmParts.upper,
    leftForearm: leftArmParts.lower,
    rightForearm: rightArmParts.lower,
    leftLeg: leftLegParts.upper,
    rightLeg: rightLegParts.upper,
    leftShin: leftLegParts.lower,
    rightShin: rightLegParts.lower,
    leftFoot: leftLegParts.end,
    rightFoot: rightLegParts.end,
    coatLeft,
    coatRight,
    core,
    shield,
    shadow,
    shadowCaster,
    batches,
    modelMeshes,
  };
}

export interface RunnerPose {
  elapsed: number;
  speed: number;
  laneDelta: number;
  height: number;
  posture: 'run' | 'jump' | 'slide';
  shield: boolean;
  reducedMotion: boolean;
  dead: boolean;
}

export const RUNNER_GAIT_PHASE_COUNT = 8;

export interface RunnerGaitSample {
  phase: number;
  thigh: number;
  shin: number;
  foot: number;
  arm: number;
  forearm: number;
  compression: number;
}

const GAIT_KEYFRAMES: readonly Omit<RunnerGaitSample, 'phase'>[] = [
  { thigh: 0.46, shin: 0.30, foot: -0.22, arm: -0.39, forearm: -0.42, compression: 0.02 },
  { thigh: 0.30, shin: 0.94, foot: -0.38, arm: -0.27, forearm: -0.54, compression: 1 },
  { thigh: 0.02, shin: 0.58, foot: -0.10, arm: -0.04, forearm: -0.37, compression: 0.48 },
  { thigh: -0.36, shin: 0.18, foot: 0.20, arm: 0.33, forearm: -0.25, compression: 0 },
  { thigh: -0.52, shin: 0.32, foot: 0.24, arm: 0.44, forearm: -0.43, compression: 0.02 },
  { thigh: -0.31, shin: 0.90, foot: -0.34, arm: 0.29, forearm: -0.54, compression: 1 },
  { thigh: -0.02, shin: 0.57, foot: -0.09, arm: 0.03, forearm: -0.36, compression: 0.48 },
  { thigh: 0.35, shin: 0.17, foot: 0.21, arm: -0.31, forearm: -0.24, compression: 0 },
] as const;

function smoothstep(value: number): number {
  const clamped = Math.max(0, Math.min(1, value));
  return clamped * clamped * (3 - 2 * clamped);
}

function interpolate(from: number, to: number, progress: number): number {
  return from + (to - from) * smoothstep(progress);
}

/** Continuous interpolation across the authored eight contact/load/passing/flight phases. */
export function sampleRunnerGait(phase: number): RunnerGaitSample {
  const normalized = ((phase % 1) + 1) % 1;
  const scaled = normalized * RUNNER_GAIT_PHASE_COUNT;
  const index = Math.floor(scaled) % RUNNER_GAIT_PHASE_COUNT;
  const next = (index + 1) % RUNNER_GAIT_PHASE_COUNT;
  const progress = scaled - Math.floor(scaled);
  const from = GAIT_KEYFRAMES[index] ?? GAIT_KEYFRAMES[0];
  const to = GAIT_KEYFRAMES[next] ?? GAIT_KEYFRAMES[0];
  return {
    phase: normalized,
    thigh: interpolate(from.thigh, to.thigh, progress),
    shin: interpolate(from.shin, to.shin, progress),
    foot: interpolate(from.foot, to.foot, progress),
    arm: interpolate(from.arm, to.arm, progress),
    forearm: interpolate(from.forearm, to.forearm, progress),
    compression: interpolate(from.compression, to.compression, progress),
  };
}

function applyGaitSide(upper: Group, lower: Group, foot: Group, gait: RunnerGaitSample, amplitude: number): void {
  upper.rotation.x = gait.thigh * amplitude - 0.08;
  upper.position.y += Math.max(0, gait.thigh) * 0.62 * amplitude;
  lower.rotation.x = 0.12 + gait.shin * amplitude * 1.1 + Math.max(0, gait.thigh) * 0.12;
  foot.rotation.x = gait.foot * amplitude - Math.max(0, gait.thigh) * 0.08;
}

export interface RunnerMotionProfile {
  cyclesPerSecond: number;
  strideAmplitude: number;
  armAmplitude: number;
  compressionAmplitude: number;
}

export function runnerMotionProfile(speed: number): RunnerMotionProfile {
  const speedMix = Math.max(0, Math.min(1, (speed - 9) / 10));
  return {
    cyclesPerSecond: 1.7 + speedMix * 1.35,
    strideAmplitude: 0.54 + speedMix * 0.13,
    armAmplitude: 0.53 + speedMix * 0.12,
    compressionAmplitude: 0.72 + speedMix * 0.38,
  };
}

function resetRigPose(rig: RunnerRig): void {
  rig.body.position.set(0, 0, 0);
  rig.body.rotation.set(0, 0, 0);
  rig.pelvis.position.set(0, BASE_PELVIS_Y, 0);
  rig.pelvis.rotation.set(0, 0, 0);
  rig.chest.rotation.set(-0.14, 0, 0);
  for (const joint of [
    rig.leftArm, rig.rightArm, rig.leftForearm, rig.rightForearm,
    rig.leftLeg, rig.rightLeg, rig.leftShin, rig.rightShin,
    rig.leftFoot, rig.rightFoot,
  ]) joint.rotation.set(0, 0, 0);
  rig.coatLeft.rotation.set(-0.12, -0.12, COAT_LEFT_Z); rig.coatRight.rotation.set(-0.15, 0.16, COAT_RIGHT_Z);
  rig.leftLeg.position.y = -0.02; rig.rightLeg.position.y = -0.02;
}

function modelBounds(rig: RunnerRig): Box3 {
  rig.root.updateMatrixWorld(true);
  const bounds = new Box3();
  const transformed = new Box3();
  for (const mesh of rig.modelMeshes) {
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    if (!mesh.geometry.boundingBox) continue;
    transformed.copy(mesh.geometry.boundingBox).applyMatrix4(mesh.matrixWorld);
    bounds.union(transformed);
  }
  return bounds;
}

function alignGroundedModel(rig: RunnerRig): void {
  const bounds = modelBounds(rig);
  if (!Number.isFinite(bounds.min.y)) return;
  rig.body.position.y += rig.root.position.y - bounds.min.y;
}

export function updateRunnerRig(rig: RunnerRig, pose: RunnerPose): void {
  const motion = runnerMotionProfile(pose.speed);
  const cycle = pose.elapsed * motion.cyclesPerSecond;
  const primaryScale = pose.reducedMotion ? 0.48 : 1;
  const running = pose.posture === 'run' && !pose.dead;

  resetRigPose(rig);
  rig.body.rotation.set(running ? -0.06 : 0, 0, Math.max(-0.14, Math.min(0.14, -pose.laneDelta * 0.14)));

  if (running) {
    const leftGait = sampleRunnerGait(cycle);
    const rightGait = sampleRunnerGait(cycle + 0.5);
    const stride = motion.strideAmplitude * primaryScale;
    const arm = motion.armAmplitude * primaryScale;
    applyGaitSide(rig.leftLeg, rig.leftShin, rig.leftFoot, leftGait, stride);
    applyGaitSide(rig.rightLeg, rig.rightShin, rig.rightFoot, rightGait, stride);
    rig.leftArm.rotation.x = leftGait.arm * arm - 0.08;
    rig.rightArm.rotation.x = rightGait.arm * arm - 0.08;
    rig.leftForearm.rotation.x = leftGait.forearm * arm;
    rig.rightForearm.rotation.x = rightGait.forearm * arm;
    rig.leftArm.rotation.z = -0.04 - Math.max(0, leftGait.arm) * 0.9; rig.rightArm.rotation.z = 0.04 + Math.max(0, rightGait.arm) * 0.9;
    rig.leftForearm.rotation.z = 0.16 + Math.max(0, leftGait.arm) * 0.9; rig.rightForearm.rotation.z = -0.16 - Math.max(0, rightGait.arm) * 0.9;
    rig.leftLeg.rotation.z = -0.055 - Math.max(0, leftGait.thigh) * 0.32; rig.rightLeg.rotation.z = 0.055 + Math.max(0, rightGait.thigh) * 0.32;
    rig.leftShin.rotation.z = -rig.leftLeg.rotation.z * 0.5; rig.rightShin.rotation.z = -rig.rightLeg.rotation.z * 0.5;
    rig.pelvis.position.y -= Math.max(leftGait.compression, rightGait.compression)
      * 0.044 * motion.compressionAmplitude * primaryScale;
    if (!pose.reducedMotion) {
      rig.pelvis.rotation.y = (leftGait.thigh - rightGait.thigh) * 0.06;
      rig.chest.rotation.y = -rig.pelvis.rotation.y * 1.32;
      rig.pelvis.rotation.z = (leftGait.thigh - rightGait.thigh) * 0.022;
      rig.chest.rotation.z = -rig.pelvis.rotation.z * 1.25;
    }
  } else if (pose.posture === 'slide' && !pose.dead) {
    rig.body.rotation.x = -0.56;
    rig.body.position.set(0, -0.26, -0.2);
    rig.pelvis.rotation.z = -0.08;
    rig.chest.rotation.set(-0.22, 0.06, 0.08);
    rig.leftLeg.rotation.x = 1.02;
    rig.rightLeg.rotation.x = 0.26;
    rig.leftShin.rotation.x = 0.58;
    rig.rightShin.rotation.x = 1.16;
    rig.leftFoot.rotation.x = -0.34;
    rig.rightFoot.rotation.x = -0.16;
    rig.leftArm.rotation.x = -1.02;
    rig.rightArm.rotation.x = -0.7;
    rig.leftForearm.rotation.x = -0.64;
    rig.rightForearm.rotation.x = -0.46;
  } else if (pose.posture === 'jump' && !pose.dead) {
    const airbornePhase = Math.max(-1, Math.min(1, pose.height / 1.7));
    rig.chest.rotation.x = -0.14 + airbornePhase * 0.08;
    rig.leftArm.rotation.x = -0.78;
    rig.rightArm.rotation.x = -0.64;
    rig.leftForearm.rotation.x = -0.52;
    rig.rightForearm.rotation.x = -0.46;
    rig.leftLeg.rotation.x = 0.38;
    rig.rightLeg.rotation.x = 0.12;
    rig.leftShin.rotation.x = 0.88;
    rig.rightShin.rotation.x = 0.58;
    rig.leftFoot.rotation.x = -0.42;
    rig.rightFoot.rotation.x = -0.3;
  } else if (pose.dead) {
    rig.body.rotation.set(-0.26, 0, 0.2);
    rig.body.position.z = -0.08;
    rig.pelvis.position.y = 0.76;
    rig.pelvis.rotation.set(0.08, -0.12, -0.08);
    rig.chest.rotation.set(-0.42, 0.12, 0.18);
    rig.leftArm.rotation.x = 0.74;
    rig.rightArm.rotation.x = -0.92;
    rig.leftForearm.rotation.x = -0.82;
    rig.rightForearm.rotation.x = -0.38;
    rig.leftLeg.rotation.x = 0.8;
    rig.rightLeg.rotation.x = 0.34;
    rig.leftShin.rotation.x = 1.18;
    rig.rightShin.rotation.x = 1.02;
    rig.leftFoot.rotation.x = -0.46;
    rig.rightFoot.rotation.x = -0.36;
  }

  if (pose.dead) {
    rig.coatLeft.rotation.set(0.1, -0.12, COAT_LEFT_Z); rig.coatRight.rotation.set(0.12, 0.16, COAT_RIGHT_Z);
  } else if (pose.posture !== 'run') {
    const coatAngle = pose.posture === 'jump' ? -0.34 : -0.06; rig.coatLeft.rotation.x = coatAngle; rig.coatRight.rotation.x = coatAngle * 1.06;
  } else if (!pose.reducedMotion) {
    const coatWave = -0.15 - Math.sin(cycle * Math.PI * 2) * 0.025 - (motion.strideAmplitude - 0.46) * 0.32;
    rig.coatLeft.rotation.x = coatWave;
    rig.coatRight.rotation.x = coatWave * 1.06;
  }
  rig.core.rotation.x = pose.reducedMotion ? 0.18 : pose.elapsed * 0.72;
  rig.core.rotation.y = pose.reducedMotion ? 0.28 : pose.elapsed * 1.08;
  rig.shield.visible = pose.shield;
  rig.shield.rotation.z = pose.reducedMotion ? 0.15 : pose.elapsed * 0.8;
  rig.shadow.visible = pose.height < 4;
  rig.shadow.position.y = 0.015 - pose.height;
  const shadowScale = Math.max(0.46, 1 - pose.height * 0.14);
  rig.shadow.scale.set(shadowScale, 1, shadowScale * 0.58);
  if (pose.posture !== 'jump' || pose.dead) alignGroundedModel(rig);
  const shadowCenter = rig.leftFoot.getWorldPosition(new Vector3()).add(rig.rightFoot.getWorldPosition(new Vector3())).multiplyScalar(0.5);
  rig.root.worldToLocal(shadowCenter); rig.shadow.position.x = 0; rig.shadow.position.z = shadowCenter.z;
  syncRigBatches(rig.root, rig.batches);
}
