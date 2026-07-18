import {
  BatchedMesh,
  CapsuleGeometry,
  CylinderGeometry,
  DodecahedronGeometry,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshStandardMaterial,
  Matrix4,
} from 'three';
import { PALETTE } from './theme';

/** Unscaled ground-anchored visual extent used only for renderer screen evidence. */
export const PURSUER_RIG_BOUNDS = { width: 1.9, height: 1.46, depth: 2.1 } as const;

export interface PursuerRig {
  root: Group;
  body: Group;
  shoulders: Group;
  head: Group;
  legs: readonly Group[];
  dorsalScars: readonly Mesh[];
  shadow: Mesh;
  shadowCaster: BatchedMesh;
  batches: readonly PursuerBatch[];
}

interface PursuerBatch {
  batch: BatchedMesh;
  sources: readonly Mesh[];
  instanceIds: readonly number[];
}

function batchPursuerMeshes(root: Group, meshes: readonly Mesh[]): PursuerBatch[] {
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
    batch.name = `pursuer-material-batch-${index}`;
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

function syncPursuerBatches(root: Group, batches: readonly PursuerBatch[]): void {
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

export interface PursuerPose {
  elapsed: number;
  danger: number;
  reducedMotion: boolean;
  stumble: boolean;
  captured: boolean;
}

export function createPursuerRig(): PursuerRig {
  const tide = new MeshStandardMaterial({ color: PALETTE.blackTide, roughness: 0.94, metalness: 0.03 });
  const tideLight = new MeshStandardMaterial({ color: PALETTE.basaltEdge, roughness: 0.9, metalness: 0 });
  const coral = new MeshStandardMaterial({ color: PALETTE.hazard, roughness: 0.84, metalness: 0.02 });
  const shadowMaterial = new MeshStandardMaterial({ color: PALETTE.tideDeep, transparent: true, opacity: 0.38, depthWrite: false });

  const root = new Group();
  root.name = 'black-rock-pursuer';
  const body = new Group();
  body.position.y = 0.64;
  root.add(body);
  const torso = new Mesh(new DodecahedronGeometry(0.69, 0), tide);
  torso.scale.set(1.32, 0.7, 1.28);
  body.add(torso);
  const shoulders = new Group();
  shoulders.position.set(0, 0.16, -0.48);
  body.add(shoulders);
  const shoulderMass = new Mesh(new DodecahedronGeometry(0.48, 0), tideLight);
  shoulderMass.scale.set(1.45, 0.76, 0.78);
  shoulders.add(shoulderMass);
  const head = new Group();
  head.position.set(0, 0.11, -0.82);
  const snout = new Mesh(new DodecahedronGeometry(0.34, 0), tide);
  snout.scale.set(0.92, 0.72, 1.2);
  head.add(snout);
  shoulders.add(head);

  const legs: Group[] = [];
  for (const [index, [x, z]] of [[-0.52, -0.44], [0.52, -0.44], [-0.56, 0.47], [0.56, 0.47]].entries()) {
    const leg = new Group();
    leg.position.set(x, -0.16, z);
    const upper = new Mesh(new CapsuleGeometry(0.105, 0.48, 4, 6), tide);
    upper.position.y = -0.34;
    upper.rotation.x = index < 2 ? -0.38 : 0.28;
    const foot = new Mesh(new DodecahedronGeometry(0.16, 0), tideLight);
    foot.position.set(0, -0.68, -0.09);
    foot.scale.set(1.24, 0.48, 1.55);
    leg.add(upper, foot);
    body.add(leg);
    legs.push(leg);
  }

  const dorsalScars: Mesh[] = [];
  for (const [index, x] of [-0.25, 0, 0.25].entries()) {
    const scar = new Mesh(new CylinderGeometry(0.05, 0.09, 0.43, 4), coral);
    scar.position.set(x, 0.53 + (index % 2) * 0.06, 0.03 - index * 0.08);
    scar.rotation.z = Math.PI * 0.5;
    body.add(scar);
    dorsalScars.push(scar);
  }
  const shadow = new Mesh(new CylinderGeometry(0.8, 1.05, 0.012, 20), shadowMaterial);
  shadow.scale.z = 0.56;
  shadow.position.y = 0.012;
  root.add(shadow);
  const legMeshes = legs.flatMap((leg) => leg.children.flatMap((child) => child instanceof Mesh ? [child] : child.children.filter((nested): nested is Mesh => nested instanceof Mesh)));
  const batches = batchPursuerMeshes(root, [torso, shoulderMass, snout, ...legMeshes, ...dorsalScars]);
  const shadowCaster = batches.find((batch) => batch.sources.includes(torso))?.batch ?? batches[0]!.batch;
  return { root, body, shoulders, head, legs, dorsalScars, shadow, shadowCaster, batches };
}

export function updatePursuerRig(rig: PursuerRig, pose: PursuerPose): void {
  const phaseTime = pose.reducedMotion ? Math.floor(pose.elapsed * 6) / 6 : pose.elapsed;
  const phase = phaseTime * (5.15 + pose.danger * 1.8) * Math.PI * 2 + Math.PI * 0.3;
  const stride = Math.sin(phase);
  const lift = Math.max(0, stride);
  rig.body.position.y = 0.64 + (pose.reducedMotion ? 0 : Math.abs(stride) * 0.055);
  rig.body.rotation.x = -0.12 - pose.danger * 0.08 + (pose.stumble ? 0.16 : 0);
  rig.shoulders.rotation.y = stride * 0.065;
  rig.head.rotation.x = -0.16 + Math.cos(phase) * (pose.reducedMotion ? 0.015 : 0.06);
  rig.legs.forEach((leg, index) => {
    const diagonal = index === 0 || index === 3 ? 1 : -1;
    const motion = Math.sin(phase + (diagonal > 0 ? 0 : Math.PI));
    leg.rotation.x = motion * (0.45 + pose.danger * 0.1);
    leg.position.y = -0.16 + Math.max(0, motion) * (pose.reducedMotion ? 0.018 : 0.075);
  });
  rig.dorsalScars.forEach((scar, index) => {
    scar.rotation.y = pose.reducedMotion ? 0 : Math.sin(phase + index) * 0.08;
  });
  rig.shadow.scale.set(1 + lift * 0.14, 1, (1 + lift * 0.14) * 0.56);
  rig.shadow.visible = !pose.captured;
  syncPursuerBatches(rig.root, rig.batches);
}
