import {
  BoxGeometry,
  CapsuleGeometry,
  CylinderGeometry,
  DoubleSide,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshStandardMaterial,
  PlaneGeometry,
  RingGeometry,
} from 'three';
import { PALETTE } from './theme';

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

function applyLegPhase(upper: Group, lower: Group, foot: Group, phase: number, amplitude: number): void {
  upper.rotation.x = phase * 0.72 * amplitude - 0.08;
  const recovery = Math.max(0, -phase);
  const drive = Math.max(0, phase);
  lower.rotation.x = 0.12 + recovery * 1.08 * amplitude + drive * 0.18 * amplitude;
  foot.rotation.x = -upper.rotation.x - lower.rotation.x * 0.62 + (phase > 0 ? 0.16 : -0.05);
}

export function updateRunnerRig(rig: RunnerRig, pose: RunnerPose): void {
  const speedMix = Math.max(0, Math.min(1, (pose.speed - 9) / 10));
  const cyclesPerSecond = 1.7 + speedMix * 1.35;
  const cycle = pose.elapsed * cyclesPerSecond * Math.PI * 2;
  const leftPhase = Math.sin(cycle);
  const semanticAmplitude = pose.reducedMotion ? 0.24 : 1;
  const running = pose.posture === 'run' && !pose.dead;

  rig.body.position.set(0, 0, 0);
  rig.body.rotation.set(0, 0, Math.max(-0.14, Math.min(0.14, -pose.laneDelta * 0.14)));
  rig.pelvis.position.set(0, 0.91, 0);
  rig.pelvis.rotation.set(0, 0, 0);
  rig.chest.rotation.set(-0.08, 0, 0);
  rig.leftForearm.rotation.set(0, 0, 0);
  rig.rightForearm.rotation.set(0, 0, 0);

  if (running) {
    applyLegPhase(rig.leftLeg, rig.leftShin, rig.leftFoot, leftPhase, semanticAmplitude);
    applyLegPhase(rig.rightLeg, rig.rightShin, rig.rightFoot, -leftPhase, semanticAmplitude);
    rig.leftArm.rotation.x = -leftPhase * 0.62 * semanticAmplitude - 0.2;
    rig.rightArm.rotation.x = leftPhase * 0.62 * semanticAmplitude - 0.2;
    rig.leftForearm.rotation.x = -0.34 - Math.max(0, leftPhase) * 0.25 * semanticAmplitude;
    rig.rightForearm.rotation.x = -0.34 - Math.max(0, -leftPhase) * 0.25 * semanticAmplitude;
    if (!pose.reducedMotion) {
      rig.pelvis.position.y += Math.abs(Math.cos(cycle)) * 0.038;
      rig.pelvis.rotation.y = leftPhase * 0.055;
      rig.chest.rotation.y = -leftPhase * 0.075;
      rig.chest.rotation.z = Math.cos(cycle) * 0.018;
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

  const coatWave = pose.reducedMotion ? 0.22 : 0.34 + Math.sin(cycle * 0.5) * 0.12 + speedMix * 0.08;
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
}
