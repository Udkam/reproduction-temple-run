import { BufferGeometry, Color, Float32BufferAttribute, Group, Mesh, MeshStandardMaterial, ShapeUtils, Texture, Vector2, Vector3 } from 'three';
import type { D4ProfileName } from './d4Profile';
import { PALETTE } from './theme';

type CanyonLayerName = 'near' | 'mid' | 'far';
type Side = -1 | 1;
interface ShelfRun { side: Side; z: readonly number[]; inner: number; width: number; top: number; foot: number; seed: number }
interface ShelfLayer { name: CanyonLayerName; objectName: string; color: number; runs: readonly ShelfRun[]; profile: readonly [number, number][] }
type Point3 = readonly [number, number, number];
interface DetailSpec { kind: 'talus' | 'strata'; anchor: Point3; side: Side; runSeed: number; hostDepth: number; points: readonly Point3[]; faces: readonly (readonly [number, number, number])[]; tone: number }
type HorizonBand = 'near' | 'mid' | 'far';
interface HorizonIsland { x: number; z: number; radiusX: number; radiusZ: number; top: number; skirt: number; seed: number; band: HorizonBand }
const TALUS_FACES = [[0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2], [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5]] as const;
const STRATA_FACES = [[0, 2, 1], [3, 4, 5], [0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4], [2, 0, 3], [2, 3, 5]] as const;
const HORIZON_ISLANDS: readonly HorizonIsland[] = [
  { x: -52, z: -54, radiusX: 13, radiusZ: 18, top: 5.1, skirt: -5.4, seed: 401, band: 'near' }, { x: -15, z: -62, radiusX: 8, radiusZ: 16, top: 4.3, skirt: -5.1, seed: 409, band: 'near' },
  { x: 15, z: -55, radiusX: 8, radiusZ: 17, top: 5, skirt: -5.6, seed: 419, band: 'near' }, { x: 52, z: -61, radiusX: 13, radiusZ: 20, top: 4.6, skirt: -5.8, seed: 421, band: 'near' },
  { x: -42, z: -84, radiusX: 12, radiusZ: 18, top: 5.8, skirt: -6.2, seed: 431, band: 'mid' }, { x: -16, z: -91, radiusX: 7, radiusZ: 15, top: 4.8, skirt: -5.9, seed: 433, band: 'mid' },
  { x: 16, z: -86, radiusX: 7, radiusZ: 16, top: 5.4, skirt: -6.1, seed: 439, band: 'mid' }, { x: 42, z: -94, radiusX: 12, radiusZ: 18, top: 5.1, skirt: -6.5, seed: 443, band: 'mid' },
  { x: -34, z: -122, radiusX: 11, radiusZ: 17, top: 6.2, skirt: -7.1, seed: 449, band: 'far' }, { x: -12, z: -130, radiusX: 5, radiusZ: 14, top: 4.9, skirt: -6.6, seed: 457, band: 'far' },
  { x: 12, z: -124, radiusX: 5, radiusZ: 15, top: 5.5, skirt: -6.8, seed: 461, band: 'far' }, { x: 34, z: -132, radiusX: 11, radiusZ: 17, top: 5.7, skirt: -7.3, seed: 463, band: 'far' },
] as const;
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
      { side: -1, z: [-24, -33, -42, -51], inner: 14, width: 8, top: 5.4, foot: -17, seed: 41 }, { side: 1, z: [-44, -53, -62, -71], inner: 18, width: 10, top: 6, foot: -18, seed: 47 },
      { side: -1, z: [-66, -76, -86, -96], inner: 22, width: 12, top: 6.5, foot: -19, seed: 53 }, { side: 1, z: [-91, -101, -111, -121], inner: 26, width: 14, top: 5.6, foot: -18, seed: 59 },
    ] },
  { name: 'far', objectName: 'tide-scar-far-low-ridge-mesa-chains', color: 0x87979d,
    profile: [[0, 1], [.32, 1], [.45, .72], [.72, .7], [1, .38], [.86, 0], [.1, 0], [.1, .28], [.24, .28], [.08, .55], [.04, .76]],
    runs: [
      { side: -1, z: [-78, -90, -102, -114], inner: 12, width: 12, top: 3.8, foot: -12, seed: 89 }, { side: 1, z: [-96, -108, -120, -132], inner: 16, width: 15, top: 4.8, foot: -14, seed: 97 },
      { side: -1, z: [-126, -139, -152, -165], inner: 22, width: 18, top: 6, foot: -17, seed: 101 }, { side: 1, z: [-150, -164, -178, -192], inner: 28, width: 20, top: 5.2, foot: -16, seed: 103 },
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
  const detailSpecs: DetailSpec[] = [], detailFragments: { kind: DetailSpec['kind']; anchor: Point3; side: Side; runSeed: number; hostDepth: number; vertexStart: number; vertexCount: number }[] = [];
  const horizonFragments: { band: HorizonBand; seed: number; ringSize: number; topHeightRange: number; center: Point3; vertexStart: number; vertexCount: number; indexStart: number; indexCount: number; bounds: { min: Point3; max: Point3 } }[] = [];
  const tint = new Color(layer.color);
  const capFaces = ShapeUtils.triangulateShape(layer.profile.map(([x, y]) => new Vector2(x, y)), []);
  const signatureCount = layer.runs.reduce((count, run) => count + run.z.length - 1, 0);
  let endpointAreaRatio = 0;
  const addVertex = (point: readonly [number, number, number], uv: readonly [number, number], tone = 1) => {
    const index = positions.length / 3, shade = (.82 + Math.max(0, point[1] + 33) / 48 * .18) * tone;
    positions.push(...point); colors.push(tint.r * shade, tint.g * shade, tint.b * shade); uvs.push(...uv); return index;
  };
  const appendFacets = (source: readonly Point3[], faces: readonly (readonly [number, number, number])[], baseTone: number) => {
    const center = source.reduce((sum, point) => sum.add(new Vector3(...point)), new Vector3()).multiplyScalar(1 / source.length), vertexStart = positions.length / 3, indexStart = indices.length;
    for (const face of faces) {
      const points = face.map((index) => new Vector3(...source[index]!)) as [Vector3, Vector3, Vector3];
      const normal = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])), centroid = points[0].clone().add(points[1]).add(points[2]).multiplyScalar(1 / 3);
      if (normal.dot(centroid.sub(center)) < 0) [points[1], points[2]] = [points[2], points[1]];
      normal.copy(points[1]).sub(points[0]).cross(points[2].clone().sub(points[0])).normalize();
      const abs = [Math.abs(normal.x), Math.abs(normal.y), Math.abs(normal.z)], tone = baseTone * (normal.y > .45 ? 1.12 : normal.y < -.25 ? .78 : 1);
      indices.push(...points.map((point) => addVertex([point.x, point.y, point.z], abs[1]! >= Math.max(abs[0]!, abs[2]!) ? [point.x * .08, -point.z * .055] : abs[0]! >= abs[2]! ? [-point.z * .055, point.y * .08] : [point.x * .08, point.y * .08], tone)));
    }
    return { center: [center.x, center.y, center.z] as Point3, vertexStart, vertexCount: positions.length / 3 - vertexStart, indexStart, indexCount: indices.length - indexStart };
  };
  const appendDetail = (spec: DetailSpec) => { const added = appendFacets(spec.points, spec.faces, spec.tone); detailFragments.push({ kind: spec.kind, anchor: spec.anchor, side: spec.side, runSeed: spec.runSeed, hostDepth: spec.hostDepth, vertexStart: added.vertexStart, vertexCount: added.vertexCount }); };
  const footStep = layer.profile.reduce((best, point, index) => point[1] < layer.profile[best]![1] || point[1] === layer.profile[best]![1] && point[0] < layer.profile[best]![0] ? index : best, 0);
  const detailScale = layer.name === 'near' ? [1, 1, 3.4] : layer.name === 'mid' ? [1.35, 1.05, 5.2] : [2, .75, 8];
  for (const run of layer.runs) {
    const stations = run.z.map((z, station) => {
      const terminal = station === 0 || station === run.z.length - 1, innerUnit = seededUnit(run.seed + station * 17, 211), widthUnit = seededUnit(run.seed + station * 19, 223);
      const span = run.top - run.foot, inner = run.inner + (terminal ? run.width * .32 : (innerUnit - .5) * 2.4), width = run.width * (terminal ? .3 + widthUnit * .08 : .82 + widthUnit * .3);
      const top = terminal ? run.top - span * .22 : run.top + (seededUnit(run.seed + station * 23, 227) - .5) * 2.4, foot = terminal ? run.foot + span * .38 : run.foot + (seededUnit(run.seed + station * 29, 229) - .5) * 1.6;
      return layer.profile.map(([outward, height], step) => { const o = outward + (seededUnit(run.seed + station * 31, step + 239) - .5) * .16 * Math.sin(Math.PI * outward), h = height + (seededUnit(run.seed + station * 37, step + 251) - .5) * .07 * Math.sin(Math.PI * height); return [run.side * (inner + o * width), foot + (top - foot) * h, z] as const; });
    });
    const areas = stations.map((station) => Math.abs(ShapeUtils.area(station.map(([x, y]) => new Vector2(x, y)))));
    endpointAreaRatio = Math.max(endpointAreaRatio, Math.max(areas[0]!, areas.at(-1)!) / Math.max(...areas.slice(1, -1)));
    const detailStation = 1 + Math.min(stations.length - 3, Math.floor(seededUnit(run.seed, 317) * (stations.length - 2)));
    const foot = stations[detailStation]![footStep]!, upper = stations[detailStation]!.at(-1)!, unit = seededUnit(run.seed + detailStation * 41, 307);
    const radius = detailScale[0]! * (.9 + unit * .28), height = detailScale[1]! * (.95 + seededUnit(run.seed, 311) * .3), zRadius = radius * (.85 + seededUnit(run.seed, 313) * .32);
    const talusAnchor: Point3 = [foot[0], foot[1], foot[2] + (unit - .5) * 1.2], embed = .45 + seededUnit(run.seed, 319) * .1, cx = talusAnchor[0] + run.side * radius * embed, cy = talusAnchor[1] + height * .36;
    detailSpecs.push({ kind: 'talus', anchor: talusAnchor, side: run.side, runSeed: run.seed, hostDepth: radius, tone: .91, faces: TALUS_FACES, points: [[cx - run.side * radius * (embed + .07), cy, talusAnchor[2]], [cx + run.side * radius * .9, cy, talusAnchor[2]], [cx, cy + height * .72, talusAnchor[2]], [cx, talusAnchor[1] - .04, talusAnchor[2]], [cx, cy, talusAnchor[2] - zRadius], [cx, cy, talusAnchor[2] + zRadius]] });
    const ledgeAnchor: Point3 = [upper[0], upper[1], upper[2] + (unit - .5) * 1.4], depth = detailScale[0]! * (.95 + unit * .25), ledgeHeight = detailScale[1]! * (.62 + unit * .18), halfZ = detailScale[2]! * (.82 + unit * .22) / 2;
    const section = [[ledgeAnchor[0] + run.side * depth * 1.05, ledgeAnchor[1] - ledgeHeight * .25], [ledgeAnchor[0] - run.side * depth * .08, ledgeAnchor[1] - ledgeHeight * .18], [ledgeAnchor[0] + run.side * depth * .5, ledgeAnchor[1] + ledgeHeight * .55]] as const;
    const frontShift = (seededUnit(run.seed, 331) - .5) * depth * .06, backShift = (seededUnit(run.seed, 337) - .5) * depth * .06;
    detailSpecs.push({ kind: 'strata', anchor: ledgeAnchor, side: run.side, runSeed: run.seed, hostDepth: depth, tone: .93, faces: STRATA_FACES, points: [...section.map(([x, y]) => [x + run.side * frontShift, y, ledgeAnchor[2] - halfZ] as Point3), ...section.map(([x, y]) => [x + run.side * backShift, y, ledgeAnchor[2] + halfZ] as Point3)] });
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
  const detailIndexStart = indices.length;
  for (const spec of detailSpecs) appendDetail(spec);
  const horizonIndexStart = indices.length;
  if (layer.name === 'far') for (const island of HORIZON_ISLANDS) {
    const ringSize = 8, phase = seededUnit(island.seed, 397) * Math.PI * 2, notch = Math.floor(seededUnit(island.seed, 399) * ringSize);
    const top = Array.from({ length: ringSize }, (_, step) => { const angle = Math.PI * 2 * step / ringSize + (seededUnit(island.seed, step + 401) - .5) * .14, radius = .82 + seededUnit(island.seed, step + 419) * .25; const shoulder = Math.sin(angle * 2 + phase) * 1.25 + Math.sin(angle * 3 - phase) * .65 - (step === notch ? 1.6 : 0); return [island.x + Math.cos(angle) * island.radiusX * radius, island.top + shoulder + (seededUnit(island.seed, step + 431) - .5) * .7, island.z + Math.sin(angle) * island.radiusZ * radius] as Point3; });
    const points = [...top, ...top.map(([x, , z], step) => [island.x + (x - island.x) * 1.16, island.skirt + (seededUnit(island.seed, step + 443) - .5) * 1.1, island.z + (z - island.z) * 1.16] as Point3)];
    const faces: [number, number, number][] = [];
    for (let step = 1; step < ringSize - 1; step += 1) { faces.push([0, step, step + 1], [ringSize, ringSize + step + 1, ringSize + step]); }
    for (let step = 0; step < ringSize; step += 1) { const next = (step + 1) % ringSize; faces.push([step, next, ringSize + next], [step, ringSize + next, ringSize + step]); }
    const added = appendFacets(points, faces, island.band === 'near' ? .84 : island.band === 'mid' ? .96 : 1.06);
    const axes = [0, 1, 2] as const, min = axes.map((axis) => Math.min(...points.map((point) => point[axis]))) as [number, number, number], max = axes.map((axis) => Math.max(...points.map((point) => point[axis]))) as [number, number, number];
    horizonFragments.push({ band: island.band, seed: island.seed, ringSize, topHeightRange: Math.max(...top.map((point) => point[1])) - Math.min(...top.map((point) => point[1])), ...added, bounds: { min, max } });
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
    capTriangleCount: layer.runs.length * capFaces.length * 2, detailFragmentCount: detailFragments.length,
    detailTriangleCount: detailSpecs.reduce((count, spec) => count + spec.faces.length, 0), detailIndexStart, detailFragments,
    horizonIslandCount: horizonFragments.length, horizonTriangleCount: horizonFragments.reduce((count, fragment) => count + fragment.indexCount / 3, 0), horizonIndexStart, horizonFragments,
    construction: 'closed-segmented-longitudinal-shelf-recess-buttress-foot-talus-strata-detail' };
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
