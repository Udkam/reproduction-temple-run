import {
  BatchedMesh,
  BoxGeometry,
  CapsuleGeometry,
  CylinderGeometry,
  DoubleSide,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshStandardMaterial,
  Matrix4,
  PlaneGeometry,
  RingGeometry,
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
  /** One real animated material batch is the rig's key-light shadow caster. */
  shadowCaster: BatchedMesh;
  batches: readonly RigBatch[];
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

function segment(
  material: MeshStandardMaterial,
  upperLength: number,
  lowerLength: number,
  radius: number,
  endScale: readonly [number, number, number],
): JointedLimb {
  const upper = new Group();
  const upperMesh = new Mesh(
    new CapsuleGeometry(radius, Math.max(0.02, upperLength - radius * 2), 4, 7),
    material,
  );
  upperMesh.position.y = -upperLength * 0.5;
  upper.add(upperMesh);

  const lower = new Group();
  lower.position.y = -upperLength;
  const lowerMesh = new Mesh(
    new CapsuleGeometry(radius * 0.9, Math.max(0.02, lowerLength - radius * 1.8), 4, 7),
    material,
  );
  lowerMesh.position.y = -lowerLength * 0.5;
  lower.add(lowerMesh);
  upper.add(lower);

  const end = new Group();
  end.position.y = -lowerLength;
  const endMesh = new Mesh(new BoxGeometry(...endScale), material);
  endMesh.position.z = -endScale[2] * 0.28;
  end.add(endMesh);
  lower.add(end);
  return { upper, lower, end };
}

export function createRunnerRig(): RunnerRig {
  const porcelain = new MeshStandardMaterial({ color: PALETTE.porcelain, roughness: 0.76, metalness: 0.02 });
  const cloth = new MeshStandardMaterial({ color: PALETTE.runnerCloth, roughness: 0.92, metalness: 0 });
  const leather = new MeshStandardMaterial({ color: PALETTE.runnerLeather, roughness: 0.82, metalness: 0.02 });
  const jade = new MeshStandardMaterial({ color: PALETTE.verdigris, roughness: 0.62, metalness: 0.16 });
  const signal = new MeshStandardMaterial({
    color: PALETTE.signal,
    emissive: PALETTE.signal,
    emissiveIntensity: 0.72,
    roughness: 0.36,
  });

  const root = new Group();
  root.name = 'courier';
  const body = new Group();
  const pelvis = new Group();
  const chest = new Group();
  root.add(body);
  body.add(pelvis);
  pelvis.position.y = 0.91;
  pelvis.add(chest);
  chest.position.y = 0.44;

  const hip = new Mesh(new BoxGeometry(0.43, 0.28, 0.3), leather);
  pelvis.add(hip);
  const torso = new Mesh(new CapsuleGeometry(0.27, 0.34, 5, 9), cloth);
  torso.position.y = 0.27;
  torso.rotation.x = -0.08;
  chest.add(torso);
  const chestPanel = new Mesh(new BoxGeometry(0.36, 0.4, 0.055), jade);
  chestPanel.position.set(0, 0.29, -0.185);
  chest.add(chestPanel);

  const neck = new Mesh(new CylinderGeometry(0.105, 0.12, 0.18, 8), porcelain);
  neck.position.y = 0.7;
  chest.add(neck);
  const hood = new Mesh(new IcosahedronGeometry(0.275, 1), cloth);
  hood.position.set(0, 0.91, 0.055);
  hood.scale.set(1, 1.08, 0.84);
  chest.add(hood);
  const face = new Mesh(new IcosahedronGeometry(0.205, 1), porcelain);
  face.position.set(0, 0.89, -0.095);
  face.scale.set(0.92, 1.04, 0.72);
  chest.add(face);

  const leftArmParts = segment(porcelain, 0.37, 0.34, 0.075, [0.12, 0.14, 0.13]);
  const rightArmParts = segment(porcelain, 0.37, 0.34, 0.075, [0.12, 0.14, 0.13]);
  leftArmParts.upper.position.set(-0.36, 0.54, 0);
  rightArmParts.upper.position.set(0.36, 0.54, 0);
  chest.add(leftArmParts.upper, rightArmParts.upper);

  const leftLegParts = segment(leather, 0.46, 0.44, 0.105, [0.18, 0.12, 0.34]);
  const rightLegParts = segment(leather, 0.46, 0.44, 0.105, [0.18, 0.12, 0.34]);
  leftLegParts.upper.position.set(-0.16, -0.06, 0);
  rightLegParts.upper.position.set(0.16, -0.06, 0);
  pelvis.add(leftLegParts.upper, rightLegParts.upper);

  const coatMaterial = new MeshStandardMaterial({
    color: PALETTE.verdigris,
    roughness: 0.8,
    metalness: 0.02,
    side: DoubleSide,
  });
  const coatGeometry = new PlaneGeometry(0.2, 0.56, 1, 3);
  const coatLeft = new Mesh(coatGeometry, coatMaterial);
  const coatRight = new Mesh(coatGeometry, coatMaterial);
  coatLeft.position.set(-0.12, -0.24, 0.2);
  coatRight.position.set(0.12, -0.24, 0.2);
  coatLeft.rotation.x = 0.24;
  coatRight.rotation.x = 0.24;
  coatLeft.rotation.z = 0.16;
  coatRight.rotation.z = -0.16;
  pelvis.add(coatLeft, coatRight);

  const core = new Mesh(new IcosahedronGeometry(0.13, 1), signal);
  core.position.set(0, 0.28, 0.23);
  chest.add(core);

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

  const batches = batchRigMeshes(root, [
    hip, torso, chestPanel, neck, hood, face,
    ...leftArmParts.upper.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightArmParts.upper.children.filter((child): child is Mesh => child instanceof Mesh),
    ...leftArmParts.lower.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightArmParts.lower.children.filter((child): child is Mesh => child instanceof Mesh),
    ...leftArmParts.end.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightArmParts.end.children.filter((child): child is Mesh => child instanceof Mesh),
    ...leftLegParts.upper.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightLegParts.upper.children.filter((child): child is Mesh => child instanceof Mesh),
    ...leftLegParts.lower.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightLegParts.lower.children.filter((child): child is Mesh => child instanceof Mesh),
    ...leftLegParts.end.children.filter((child): child is Mesh => child instanceof Mesh),
    ...rightLegParts.end.children.filter((child): child is Mesh => child instanceof Mesh),
    coatLeft, coatRight, core,
  ]);
  const shadowCaster = batches.find((batch) => batch.sources.includes(hip))?.batch ?? batches[0]!.batch;
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
  lower.rotation.x = 0.1 + gait.shin * amplitude;
  foot.rotation.x = gait.foot * amplitude;
}

export function updateRunnerRig(rig: RunnerRig, pose: RunnerPose): void {
  const speedMix = Math.max(0, Math.min(1, (pose.speed - 9) / 10));
  const cyclesPerSecond = 1.7 + speedMix * 1.35;
  const animationElapsed = pose.reducedMotion ? Math.floor(pose.elapsed * 6) / 6 : pose.elapsed;
  const cycle = animationElapsed * cyclesPerSecond;
  const semanticAmplitude = pose.reducedMotion ? 0.42 : 1;
  const running = pose.posture === 'run' && !pose.dead;

  rig.body.position.set(0, 0, 0);
  rig.body.rotation.set(0, 0, Math.max(-0.14, Math.min(0.14, -pose.laneDelta * 0.14)));
  rig.pelvis.position.set(0, 0.91, 0);
  rig.pelvis.rotation.set(0, 0, 0);
  rig.chest.rotation.set(-0.08, 0, 0);
  rig.leftForearm.rotation.set(0, 0, 0);
  rig.rightForearm.rotation.set(0, 0, 0);

  if (running) {
    const leftGait = sampleRunnerGait(cycle);
    const rightGait = sampleRunnerGait(cycle + 0.5);
    applyGaitSide(rig.leftLeg, rig.leftShin, rig.leftFoot, leftGait, semanticAmplitude);
    applyGaitSide(rig.rightLeg, rig.rightShin, rig.rightFoot, rightGait, semanticAmplitude);
    rig.leftArm.rotation.x = leftGait.arm * semanticAmplitude - 0.2;
    rig.rightArm.rotation.x = rightGait.arm * semanticAmplitude - 0.2;
    rig.leftForearm.rotation.x = leftGait.forearm * semanticAmplitude;
    rig.rightForearm.rotation.x = rightGait.forearm * semanticAmplitude;
    rig.pelvis.position.y -= Math.max(leftGait.compression, rightGait.compression) * 0.044;
    if (!pose.reducedMotion) {
      rig.pelvis.rotation.y = (leftGait.thigh - rightGait.thigh) * 0.06;
      rig.chest.rotation.y = -rig.pelvis.rotation.y * 1.32;
      rig.chest.rotation.z = (leftGait.compression - rightGait.compression) * 0.028;
    }
  } else if (pose.posture === 'slide' && !pose.dead) {
    rig.body.rotation.x = -0.64;
    rig.body.position.set(0, -0.3, -0.22);
    rig.leftLeg.rotation.x = 1.08;
    rig.rightLeg.rotation.x = 0.22;
    rig.leftShin.rotation.x = 0.5;
    rig.rightShin.rotation.x = 1.12;
    rig.leftArm.rotation.x = -1.04;
    rig.rightArm.rotation.x = -0.72;
    rig.leftForearm.rotation.x = -0.62;
    rig.rightForearm.rotation.x = -0.48;
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
  } else if (pose.dead) {
    rig.body.rotation.set(-0.34, 0, 0.72);
    rig.leftArm.rotation.x = 1.08;
    rig.rightArm.rotation.x = -0.76;
    rig.leftLeg.rotation.x = 0.55;
    rig.rightLeg.rotation.x = -0.28;
  }

  const coatWave = pose.reducedMotion ? 0.22 : 0.34 + Math.sin(cycle * Math.PI) * 0.12 + speedMix * 0.08;
  rig.coatLeft.rotation.x = coatWave;
  rig.coatRight.rotation.x = coatWave * 1.08;
  rig.core.rotation.x = pose.reducedMotion ? 0.18 : pose.elapsed * 0.72;
  rig.core.rotation.y = pose.reducedMotion ? 0.28 : pose.elapsed * 1.08;
  rig.shield.visible = pose.shield;
  rig.shield.rotation.z = pose.reducedMotion ? 0.15 : pose.elapsed * 0.8;
  rig.shadow.visible = pose.height < 4;
  rig.shadow.position.y = 0.015 - pose.height;
  const shadowScale = Math.max(0.46, 1 - pose.height * 0.14);
  rig.shadow.scale.set(shadowScale, 1, shadowScale * 0.58);
  syncRigBatches(rig.root, rig.batches);
}
