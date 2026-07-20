import { BufferGeometry, Color, Float32BufferAttribute, Group, Mesh, MeshStandardMaterial, ShapeUtils, Texture, Vector2, Vector3 } from 'three';
import type { D4ProfileName } from './d4Profile';
import { PALETTE } from './theme';

type CanyonLayerName = 'near' | 'mid' | 'far';
type Side = -1 | 1;
interface ShelfRun { side: Side; z: readonly number[]; inner: number; width: number; top: number; foot: number; seed: number }
interface ShelfLayer { name: CanyonLayerName; objectName: string; color: number; runs: readonly ShelfRun[]; profile: readonly [number, number][] }
const SHELF_LAYERS: readonly ShelfLayer[] = [
  { name: 'near', objectName: 'tide-scar-near-fractured-inner-lips', color: 0x9cabb0,
    profile: [[0, 1], [.34, 1.02], [.3, .76], [.58, .72], [.75, .8], [1, .4], [.82, 0], [.12, 0], [.12, .22], [.28, .22], [.22, .42], [.06, .42], [.06, .7]],
    runs: [
      { side: -1, z: [-5, -12, -19, -26, -33], inner: 12, width: 6.5, top: 3, foot: -13, seed: 11 }, { side: 1, z: [-39, -47, -55, -63], inner: 11, width: 7, top: 3.8, foot: -15, seed: 17 },
      { side: -1, z: [-69, -77, -85, -93], inner: 14, width: 5.8, top: 2.8, foot: -12, seed: 23 },
    ] },
  { name: 'mid', objectName: 'tide-scar-mid-interrupted-buttress-recesses', color: 0x657985,
    profile: [[0, 1], [.2, 1], [.22, .68], [.48, .66], [.6, .84], [.9, .82], [1, .35], [.74, 0], [.08, 0], [.08, .24], [.22, .24], [.16, .48], [.04, .48], [.04, .74]],
    runs: [
      { side: -1, z: [-24, -33, -42, -51], inner: 18, width: 10, top: 5.4, foot: -17, seed: 41 }, { side: 1, z: [-44, -53, -62, -71], inner: 22, width: 12, top: 6, foot: -18, seed: 47 },
      { side: -1, z: [-66, -76, -86, -96], inner: 26, width: 13, top: 6.5, foot: -19, seed: 53 }, { side: 1, z: [-91, -101, -111, -121], inner: 30, width: 14, top: 5.6, foot: -18, seed: 59 },
    ] },
  { name: 'far', objectName: 'tide-scar-far-low-ridge-mesa-chains', color: 0x87979d,
    profile: [[0, 1], [.32, 1], [.45, .72], [.72, .7], [1, .38], [.86, 0], [.1, 0], [.1, .28], [.24, .28], [.08, .55], [.04, .76]],
    runs: [
      { side: -1, z: [-78, -90, -102, -114], inner: 28, width: 18, top: 3.8, foot: -12, seed: 89 }, { side: 1, z: [-96, -108, -120, -132], inner: 34, width: 20, top: 4.8, foot: -14, seed: 97 },
      { side: -1, z: [-126, -139, -152, -165], inner: 40, width: 22, top: 6, foot: -17, seed: 101 }, { side: 1, z: [-150, -164, -178, -192], inner: 46, width: 23, top: 5.2, foot: -16, seed: 103 },
    ] },
] as const;

function seededUnit(index: number, salt: number): number {
  let value = Math.imul(index + 1, 0x45d9f3b) ^ Math.imul(salt + 17, 0x27d4eb2d);
  value ^= value >>> 16;
  value = Math.imul(value, 0x45d9f3b);
  value ^= value >>> 16;
  return (value >>> 0) / 0xffffffff;
}
function createLayerGeometry(layer: ShelfLayer): BufferGeometry {
  const positions: number[] = [], colors: number[] = [], uvs: number[] = [], indices: number[] = [];
  const tint = new Color(layer.color);
  const capFaces = ShapeUtils.triangulateShape(layer.profile.map(([x, y]) => new Vector2(x, y)), []);
  const signatureCount = layer.runs.reduce((count, run) => count + run.z.length - 1, 0);
  let endpointAreaRatio = 0;
  const addVertex = (point: readonly [number, number, number], uv: readonly [number, number], tone = 1) => {
    const index = positions.length / 3, shade = (.82 + Math.max(0, point[1] + 33) / 48 * .18) * tone;
    positions.push(...point); colors.push(tint.r * shade, tint.g * shade, tint.b * shade); uvs.push(...uv); return index;
  };
  for (const run of layer.runs) {
    const stations = run.z.map((z, station) => {
      const terminal = station === 0 || station === run.z.length - 1, innerUnit = seededUnit(run.seed + station * 17, 211), widthUnit = seededUnit(run.seed + station * 19, 223);
      const span = run.top - run.foot, inner = run.inner + (terminal ? run.width * .32 : (innerUnit - .5) * 2.4), width = run.width * (terminal ? .3 + widthUnit * .08 : .82 + widthUnit * .3);
      const top = terminal ? run.top - span * .22 : run.top + (seededUnit(run.seed + station * 23, 227) - .5) * 2.4, foot = terminal ? run.foot + span * .38 : run.foot + (seededUnit(run.seed + station * 29, 229) - .5) * 1.6;
      return layer.profile.map(([outward, height], step) => { const o = outward + (seededUnit(run.seed + station * 31, step + 239) - .5) * .16 * Math.sin(Math.PI * outward), h = height + (seededUnit(run.seed + station * 37, step + 251) - .5) * .07 * Math.sin(Math.PI * height); return [run.side * (inner + o * width), foot + (top - foot) * h, z] as const; });
    });
    const areas = stations.map((station) => Math.abs(ShapeUtils.area(station.map(([x, y]) => new Vector2(x, y)))));
    endpointAreaRatio = Math.max(endpointAreaRatio, Math.max(areas[0]!, areas.at(-1)!) / Math.max(...areas.slice(1, -1)));
    for (let station = 0; station < stations.length - 1; station += 1) {
      for (let step = 0; step < layer.profile.length; step += 1) {
        const next = (step + 1) % layer.profile.length;
        const quad = [stations[station]![step]!, stations[station + 1]![step]!, stations[station + 1]![next]!, stations[station]![next]!];
        const horizontal = Math.abs(quad[3][1] - quad[0][1]) <= Math.abs(quad[3][0] - quad[0][0]) * .45, innerWall = step >= layer.profile.length - 5 || step === layer.profile.length - 1, tone = horizontal ? 1.12 : innerWall ? .94 : step > layer.profile.length * .38 ? .78 : .98;
        const vertex = quad.map((point) => addVertex(point, horizontal ? [point[0] * .08, -point[2] * .055] : [-point[2] * .055, point[1] * .08], tone));
        if (run.side < 0) indices.push(vertex[0]!, vertex[1]!, vertex[2]!, vertex[0]!, vertex[2]!, vertex[3]!);
        else indices.push(vertex[0]!, vertex[2]!, vertex[1]!, vertex[0]!, vertex[3]!, vertex[2]!);
      }
    }
    for (const [stationIndex, targetNormalZ] of [[0, 1], [stations.length - 1, -1]] as const) {
      const station = stations[stationIndex]!;
      for (const face of capFaces) {
        const triangle = face.map((index) => station[index]!) as [readonly [number, number, number], readonly [number, number, number], readonly [number, number, number]];
        const crossZ = (triangle[1][0] - triangle[0][0]) * (triangle[2][1] - triangle[0][1])
          - (triangle[1][1] - triangle[0][1]) * (triangle[2][0] - triangle[0][0]);
        const oriented = crossZ * targetNormalZ < 0 ? [triangle[0], triangle[2], triangle[1]] : triangle;
        indices.push(...oriented.map((point) => addVertex(point, [point[0] * .08, point[1] * .08], 1.06)));
      }
    }
  }
  const geometry = new BufferGeometry();
  geometry.name = `${layer.objectName}-geometry`;
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3));
  geometry.setAttribute('uv', new Float32BufferAttribute(uvs, 2)); geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  geometry.userData = { canyonLayer: layer.name, runCount: layer.runs.length, profilePointCount: layer.profile.length,
    signatureCount, endpointAreaRatio, closedProfile: true, capCount: layer.runs.length * 2,
    sideTriangleCount: signatureCount * layer.profile.length * 2,
    capTriangleCount: layer.runs.length * capFaces.length * 2, construction: 'closed-segmented-longitudinal-shelf-recess-buttress-foot-talus' };
  return geometry;
}
function createAbyssGeometry(): BufferGeometry {
  const xSamples = [-120, -78, -45, -20, -7, 7, 20, 45, 78, 120];
  const zSamples = [30, 5, -25, -60, -95, -130, -165, -200, -240];
  const positions: number[] = [], colors: number[] = [], uvs: number[] = [];
  for (const [zIndex, z] of zSamples.entries()) {
    for (const [xIndex, x] of xSamples.entries()) {
      const edgeRise = Math.min(7, Math.abs(x) * 0.055);
      const y = -29 + edgeRise - seededUnit(zIndex * xSamples.length + xIndex, 509) * 4.5;
      positions.push(x, y, z);
      uvs.push(x * .02, -z * .02);
      const shade = 0.52 + seededUnit(xIndex, zIndex + 521) * 0.16;
      const color = new Color(PALETTE.tideDeep).multiplyScalar(shade);
      colors.push(color.r, color.g, color.b);
    }
  }
  const indices: number[] = [];
  for (let z = 0; z < zSamples.length - 1; z += 1) {
    for (let x = 0; x < xSamples.length - 1; x += 1) {
      const a = z * xSamples.length + x;
      const b = a + 1;
      const c = a + xSamples.length;
      const d = c + 1;
      if ((x + z) % 2 === 0) indices.push(a, d, c, a, b, d);
      else indices.push(a, b, c, b, d, c);
    }
  }
  const geometry = new BufferGeometry();
  geometry.name = 'tide-scar-faceted-abyss-bed-geometry';
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3));
  geometry.setAttribute('uv', new Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return geometry;
}
/**
 * Presentation-only deterministic canyon. Every visible depth band is solid,
 * faceted geometry; the root follows course presentation without touching
 * generated sections, canonical state, or collision data.
 */
export class TideScarWorld {
  readonly root = new Group();
  private readonly layers: Mesh[];
  private readonly shelfLayers: Mesh[];
  private disposed = false;

  constructor() {
    this.root.name = 'tide-scar-geometric-canyon';
    const abyss = new Mesh(
      createAbyssGeometry(),
      new MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: 1, metalness: 0, flatShading: true }),
    );
    abyss.name = 'tide-scar-faceted-abyss-bed';
    abyss.receiveShadow = true;
    this.shelfLayers = SHELF_LAYERS.map((layer) => {
      const mesh = new Mesh(
        createLayerGeometry(layer),
        new MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: layer.name === 'near' ? .82 : .88, metalness: 0, flatShading: true,
          emissive: layer.name === 'near' ? 0x526d78 : 0, emissiveIntensity: layer.name === 'near' ? .32 : 0 }),
      );
      mesh.name = layer.objectName;
      mesh.castShadow = layer.name === 'near';
      mesh.receiveShadow = true;
      return mesh;
    });
    this.layers = [abyss, ...this.shelfLayers];
    this.root.add(...this.layers);
  }
  /**
   * Kept for D4 caller compatibility. Panorama textures are deliberately not
   * attached: R1 has no cylinder, card, or background mesh to receive one.
   */
  setPanorama(texture: Texture | null): void {
    void texture;
  }
  /** Non-owning clean-room basalt map for the nearest shelf only. */
  setSurfaceMap(texture: Texture | null): void {
    for (const mesh of this.shelfLayers.slice(0, 1)) {
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const material of materials) {
        if (!(material instanceof MeshStandardMaterial)) continue;
        material.map = texture;
        material.needsUpdate = true;
      }
    }
  }
  get hasPanorama(): boolean {
    return false;
  }

  update(anchor: Vector3, yaw: number, profile: D4ProfileName): void {
    void profile;
    const cellSize = 96;
    const cellX = Math.round(anchor.x / cellSize) * cellSize || 0;
    const cellZ = Math.round(anchor.z / cellSize) * cellSize || 0;
    this.root.position.set(cellX, 0, cellZ);
    this.root.rotation.set(0, yaw, 0);
  }
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    for (const mesh of this.layers) {
      mesh.geometry.dispose();
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const material of materials) material.dispose();
    }
  }
}
