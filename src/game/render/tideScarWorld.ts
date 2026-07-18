import {
  BackSide,
  Color,
  CylinderGeometry,
  DodecahedronGeometry,
  Group,
  InstancedMesh,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  PlaneGeometry,
  Texture,
  Vector3,
} from 'three';
import type { D4ProfileName } from './d4Profile';
import { PALETTE } from './theme';

const FAR_MESA_COUNT = 14;
const STACK_COUNT = 46;
const MIST_BAND_COUNTS = [36, 26, 18] as const;

function seededUnit(index: number, salt: number): number {
  let value = Math.imul(index + 1, 0x45d9f3b) ^ Math.imul(salt + 17, 0x27d4eb2d);
  value ^= value >>> 16;
  value = Math.imul(value, 0x45d9f3b);
  value ^= value >>> 16;
  return (value >>> 0) / 0xffffffff;
}

/**
 * Presentation-only canyon: inward panorama, three mineral contour depths and
 * 36/26/18 procedural mist bands. It follows the runner without touching the
 * generated course or canonical state.
 */
export class TideScarWorld {
  readonly root = new Group();
  private readonly farMesas: InstancedMesh;
  private readonly stacks: InstancedMesh;
  private readonly mistBands: InstancedMesh;
  private readonly panoramaMaterial = new MeshBasicMaterial({
    color: 0xffffff,
    side: BackSide,
    transparent: true,
    opacity: 0.94,
    depthWrite: false,
    fog: false,
  });
  private readonly panorama = new Mesh(new CylinderGeometry(156, 156, 82, 36, 1, true, 0.35, Math.PI * 1.5), this.panoramaMaterial);
  private readonly dummy = new Object3D();

  constructor() {
    this.root.name = 'tide-scar-canyon';
    this.farMesas = new InstancedMesh(
      new PlaneGeometry(1, 1),
      new MeshBasicMaterial({ color: PALETTE.tideLight, transparent: true, opacity: 0.46, depthWrite: false, fog: false, vertexColors: true }),
      FAR_MESA_COUNT,
    );
    this.farMesas.name = 'tide-scar-far-mesa-cards';
    this.farMesas.frustumCulled = false;
    this.stacks = new InstancedMesh(
      new DodecahedronGeometry(1, 0),
      new MeshStandardMaterial({ color: PALETTE.basaltEdge, roughness: 0.94, metalness: 0, vertexColors: true }),
      STACK_COUNT,
    );
    this.stacks.name = 'tide-scar-mid-stacks-near-cliff-lips';
    this.stacks.frustumCulled = false;
    const mistMaterial = new MeshBasicMaterial({
      color: PALETTE.mist,
      transparent: true,
      opacity: 0.075,
      depthWrite: false,
    });
    this.mistBands = new InstancedMesh(new PlaneGeometry(1, 1, 1, 1), mistMaterial, MIST_BAND_COUNTS.reduce((total, count) => total + count, 0));
    this.mistBands.name = 'tide-scar-far-middle-near-mist-bands';
    this.mistBands.frustumCulled = false;
    this.panorama.name = 'tide-scar-inward-canyon-panorama';
    this.panorama.visible = false;
    this.root.add(this.panorama, this.farMesas, this.stacks, this.mistBands);
  }

  setPanorama(texture: Texture | null): void {
    this.panoramaMaterial.map = texture;
    this.panoramaMaterial.color.set(0xffffff);
    this.panoramaMaterial.needsUpdate = true;
    this.panorama.visible = texture !== null;
  }

  get hasPanorama(): boolean {
    return this.panorama.visible;
  }

  update(anchor: Vector3, yaw: number, profile: D4ProfileName): void {
    const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
    for (let index = 0; index < FAR_MESA_COUNT; index += 1) {
      const u = seededUnit(index, 1);
      const v = seededUnit(index, 2);
      const side = index % 2 === 0 ? -1 : 1;
      this.dummy.position.copy(anchor)
        .addScaledVector(forward, 72 + u * 74)
        .addScaledVector(right, side * (38 + v * 58));
      this.dummy.position.y = 9 + v * 12;
      this.dummy.rotation.set(0, yaw, 0);
      this.dummy.scale.set(18 + u * 38, 8 + v * 15, 1);
      this.dummy.updateMatrix();
      this.farMesas.setMatrixAt(index, this.dummy.matrix);
      this.farMesas.setColorAt(index, new Color().setHex(index % 3 === 0 ? PALETTE.mist : PALETTE.tideLight));
    }
    this.farMesas.instanceMatrix.needsUpdate = true;
    if (this.farMesas.instanceColor) this.farMesas.instanceColor.needsUpdate = true;
    for (let index = 0; index < STACK_COUNT; index += 1) {
      const layer = index < 22 ? 0 : 1;
      const u = seededUnit(index, 31);
      const v = seededUnit(index, 32);
      const w = seededUnit(index, 33);
      const side = index % 2 === 0 ? -1 : 1;
      this.dummy.position.copy(anchor)
        .addScaledVector(forward, layer === 0 ? 33 + u * 42 : 9 + u * 25)
        .addScaledVector(right, side * (layer === 0 ? 14 + v * 30 : 5.1 + v * 4.4));
      this.dummy.position.y = layer === 0 ? -1.8 - w * 4 : -2.6 - w * 6;
      this.dummy.rotation.set(w * 0.18, yaw + (u - 0.5) * 0.52, (v - 0.5) * 0.12);
      this.dummy.scale.set(layer === 0 ? 2.8 + w * 4.6 : 1.8 + w * 3.2, layer === 0 ? 3.2 + u * 6.8 : 4.2 + u * 8.2, layer === 0 ? 2.4 + v * 4.2 : 2.2 + v * 3.8);
      this.dummy.updateMatrix();
      this.stacks.setMatrixAt(index, this.dummy.matrix);
      this.stacks.setColorAt(index, new Color().setHex(layer === 0 ? PALETTE.basaltEdge : PALETTE.basalt));
    }
    this.stacks.instanceMatrix.needsUpdate = true;
    if (this.stacks.instanceColor) this.stacks.instanceColor.needsUpdate = true;
    let bandIndex = 0;
    for (const [layer, count] of MIST_BAND_COUNTS.entries()) {
      for (let index = 0; index < count; index += 1) {
        const u = seededUnit(index, 101 + layer * 7);
        const v = seededUnit(index, 103 + layer * 7);
        const side = index % 2 === 0 ? -1 : 1;
        this.dummy.position.copy(anchor)
          .addScaledVector(forward, [104, 57, 27][layer]! * (0.34 + u * 0.8))
          .addScaledVector(right, side * [74, 36, 18][layer]! * (0.32 + v * 0.56));
        this.dummy.position.y = 1.2 + v * (7.6 - layer * 1.35);
        this.dummy.rotation.set(0, yaw, 0);
        this.dummy.scale.set(10 + u * 17, 1.2 + v * 2.6, 1);
        this.dummy.updateMatrix();
        this.mistBands.setMatrixAt(bandIndex++, this.dummy.matrix);
      }
    }
    this.mistBands.count = bandIndex;
    this.mistBands.instanceMatrix.needsUpdate = true;
    this.panorama.position.copy(anchor).addScaledVector(forward, 145);
    // The high rear camera's asymmetric lens keeps the physical road low; put
    // the inward panorama's visible canyon band behind that road, not above it.
    this.panorama.position.y = profile === 'portrait' ? -67 : profile === 'landscape' ? -36 : -49;
    this.panorama.rotation.y = yaw + Math.PI;
  }
}
