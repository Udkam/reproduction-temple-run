import { BufferGeometry, Color, Float32BufferAttribute, Group, Mesh, MeshStandardMaterial, ShapeUtils, Texture, Vector2, Vector3 } from 'three';
import type { D4ProfileName } from './d4Profile';
import { PALETTE } from './theme';

type CanyonLayerName = 'near' | 'mid' | 'far';
type Side = -1 | 1;
interface ShelfRun { side: Side; z: readonly number[]; inner: number; width: number; top: number; foot: number; seed: number }
interface ShelfLayer { name: CanyonLayerName; objectName: string; runs: readonly ShelfRun[]; profile: readonly [number, number][] }
type Point3 = readonly [number, number, number];
interface DetailSpec { kind: 'talus' | 'strata'; anchor: Point3; side: Side; runSeed: number; hostDepth: number; points: readonly Point3[]; faces: readonly (readonly [number, number, number])[]; tone: number }
type HorizonBand = 'near' | 'mid' | 'far';
interface HorizonIsland { x: number; z: number; radiusX: number; radiusZ: number; top: number; skirt: number; seed: number; band: HorizonBand }
type SurfaceFace = 'top' | 'shelf' | 'wall' | 'return' | 'underside';
interface SurfaceTreatment {
  tint: number; uvScale: number; frequency: number; variation: number;
  values: Readonly<Record<SurfaceFace, number>>;
  roughness: number; mapStrength: number; mapFloor: number;
}
const SURFACE_TREATMENTS: Readonly<Record<CanyonLayerName, SurfaceTreatment>> = {
  near: { tint: 0xd4dfe1, uvScale: .09, frequency: .36, variation: .09,
    values: { top: 1.15, shelf: 1.08, wall: 1, return: .94, underside: .86 },
    roughness: .84, mapStrength: .78, mapFloor: .1 },
  mid: { tint: 0xd4dfe1, uvScale: .07, frequency: .22, variation: .052,
    values: { top: 1.1, shelf: 1.04, wall: .98, return: .94, underside: .89 },
    roughness: .89, mapStrength: .58, mapFloor: .14 },
  far: { tint: 0xd4dfe1, uvScale: .052, frequency: .12, variation: .024,
    values: { top: 1.065, shelf: 1.03, wall: .99, return: .96, underside: .92 },
    roughness: .9, mapStrength: .38, mapFloor: .18 },
  } as const;
const SURFACE_FACE_LIFT: Readonly<Record<SurfaceFace, number>> = { top: 0, shelf: 0, wall: 0, return: .025, underside: .03 };
const SURFACE_HEMISPHERE_SHIFT: Readonly<Record<SurfaceFace, number>> = { top: 0, shelf: 0, wall: 0, return: .1, underside: .15 };
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
  { name: 'near', objectName: 'tide-scar-near-fractured-inner-lips',
    profile: [[0, 1], [.34, 1.02], [.3, .76], [.58, .72], [.75, .8], [1, .4], [.82, 0], [.12, 0], [.12, .22], [.28, .22], [.22, .42], [.06, .42], [.06, .7]],
    runs: [
      { side: -1, z: [-5, -12, -19, -26, -33], inner: 12, width: 6.5, top: 3, foot: -13, seed: 11 }, { side: 1, z: [-39, -47, -55, -63], inner: 11, width: 7, top: 3.8, foot: -15, seed: 17 },
      { side: -1, z: [-69, -77, -85, -93], inner: 14, width: 5.8, top: 2.8, foot: -12, seed: 23 },
    ] },
  { name: 'mid', objectName: 'tide-scar-mid-interrupted-buttress-recesses',
    profile: [[0, 1], [.2, 1], [.22, .68], [.48, .66], [.6, .84], [.9, .82], [1, .35], [.74, 0], [.08, 0], [.08, .24], [.22, .24], [.16, .48], [.04, .48], [.04, .74]],
    runs: [
      { side: -1, z: [-24, -33, -42, -51], inner: 14, width: 8, top: 5.4, foot: -17, seed: 41 }, { side: 1, z: [-44, -53, -62, -71], inner: 18, width: 10, top: 6, foot: -18, seed: 47 },
      { side: -1, z: [-66, -76, -86, -96], inner: 22, width: 12, top: 6.5, foot: -19, seed: 53 }, { side: 1, z: [-91, -101, -111, -121], inner: 26, width: 14, top: 5.6, foot: -18, seed: 59 },
    ] },
  { name: 'far', objectName: 'tide-scar-far-low-ridge-mesa-chains',
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
const SURFACE_TINTS: Readonly<Record<CanyonLayerName, Color>> = {
  near: new Color(SURFACE_TREATMENTS.near.tint),
  mid: new Color(SURFACE_TREATMENTS.mid.tint),
  far: new Color(SURFACE_TREATMENTS.far.tint),
};
function surfaceUv(point: Point3, normal: Vector3, band: CanyonLayerName): readonly [number, number] {
  const scale = SURFACE_TREATMENTS[band].uvScale, ax = Math.abs(normal.x), ay = Math.abs(normal.y), az = Math.abs(normal.z);
  if (ay >= Math.max(ax, az)) return [point[0] * scale, -point[2] * scale];
  return ax >= az ? [-point[2] * scale, point[1] * scale] : [point[0] * scale, point[1] * scale];
}
function surfaceShade(point: Point3, band: CanyonLayerName, face: SurfaceFace, baseTone: number): number {
  const treatment = SURFACE_TREATMENTS[band], frequency = treatment.frequency;
  const broad = Math.sin((point[0] * .83 + point[2] * .56 + point[1] * .31) * frequency);
  const cross = Math.sin((point[0] * -.29 + point[2] * .91 - point[1] * .17) * frequency * .73 + 1.4);
  return Math.max(.48, Math.min(1.22, baseTone * treatment.values[face] * (1 + treatment.variation * (broad * .62 + cross * .38))));
}
function createSurfaceMaterial(treatment: SurfaceTreatment): MeshStandardMaterial {
  const material = new MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: treatment.roughness, metalness: 0, flatShading: true, emissive: 0, emissiveIntensity: 0 });
  material.onBeforeCompile = (shader) => {
    shader.uniforms.canyonMapStrength = { value: treatment.mapStrength };
    shader.uniforms.canyonMapFloor = { value: treatment.mapFloor };
    shader.vertexShader = `attribute float surfaceBandStrength;\nattribute float surfaceBandFloor;\nattribute float surfaceFaceLift;\nattribute float surfaceHemisphereShift;\nvarying float vCanyonBandStrength;\nvarying float vCanyonBandFloor;\nvarying float vCanyonFaceLift;\nvarying float vCanyonHemisphereShift;\nvarying vec3 vCanyonObjectPosition;\n${shader.vertexShader}`.replace('#include <begin_vertex>', '#include <begin_vertex>\n  vCanyonBandStrength = surfaceBandStrength;\n  vCanyonBandFloor = surfaceBandFloor;\n  vCanyonFaceLift = surfaceFaceLift;\n  vCanyonHemisphereShift = surfaceHemisphereShift;\n  vCanyonObjectPosition = position;');
    shader.fragmentShader = `uniform float canyonMapStrength;\nuniform float canyonMapFloor;\nvarying float vCanyonBandStrength;\nvarying float vCanyonBandFloor;\nvarying float vCanyonFaceLift;\nvarying float vCanyonHemisphereShift;\nvarying vec3 vCanyonObjectPosition;\n${shader.fragmentShader.replace('#include <map_fragment>', `
#ifdef USE_MAP
  vec4 sampledDiffuseColor = texture2D( map, vMapUv * 1.65 );
  vec4 broadBasalt = texture2D( map, vMapUv * 0.38 + vec2(0.17, 0.31) );
  #ifdef DECODE_VIDEO_TEXTURE
    sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
    broadBasalt = sRGBTransferEOTF( broadBasalt );
  #endif
  const vec3 basaltLuma = vec3(0.2126, 0.7152, 0.0722);
  float microValue = dot(sampledDiffuseColor.rgb, basaltLuma);
  float macroValue = dot(broadBasalt.rgb, basaltLuma);
  float bandStrength = max(vCanyonBandStrength, canyonMapStrength);
  float bandFloor = min(vCanyonBandFloor, canyonMapFloor);
  float strata = sin(vCanyonObjectPosition.y * 1.08 + sin(vCanyonObjectPosition.x * 0.11 + vCanyonObjectPosition.z * 0.08) * 1.15);
  float mineralBreak = sin(vCanyonObjectPosition.x * 0.13 - vCanyonObjectPosition.z * 0.09 + vCanyonObjectPosition.y * 0.27);
  float textureDetail = (microValue - 0.039) * (3.2 + 6.8 * bandStrength) + (macroValue - 0.039) * (1.6 + 4.2 * bandStrength);
  float worldDetail = (strata * 0.68 + mineralBreak * 0.32) * (0.012 + 0.07 * bandStrength);
  float faceMinimum = bandFloor + 0.16 + vCanyonFaceLift;
  float basaltValue = clamp(0.38 + bandFloor * 0.42 + textureDetail + worldDetail, faceMinimum, 0.7);
  vec3 basaltHue = mix(vec3(1.0), sampledDiffuseColor.rgb / max(microValue, 0.02), 0.58);
  sampledDiffuseColor.rgb = basaltHue * basaltValue;
  diffuseColor *= sampledDiffuseColor;
#endif`).replace('#include <lights_fragment_begin>', `#include <lights_fragment_begin>
#if defined(RE_IndirectDiffuse) && (NUM_HEMI_LIGHTS > 0)
  float canyonHemisphereShift = min(0.15, vCanyonHemisphereShift);
  #pragma unroll_loop_start
  for (int i = 0; i < NUM_HEMI_LIGHTS; i ++) {
    float canyonBaseWeight = saturate(0.5 * dot(geometryNormal, hemisphereLights[i].direction) + 0.5);
    float canyonEffectiveWeight = min(1.0, canyonBaseWeight + canyonHemisphereShift);
    vec3 canyonBaseIrradiance = mix(hemisphereLights[i].groundColor, hemisphereLights[i].skyColor, canyonBaseWeight);
    vec3 canyonEffectiveIrradiance = mix(hemisphereLights[i].groundColor, hemisphereLights[i].skyColor, canyonEffectiveWeight);
    irradiance += canyonEffectiveIrradiance - canyonBaseIrradiance;
  }
  #pragma unroll_loop_end
#endif`)}`;
  };
  material.customProgramCacheKey = () => `tide-scar-r1e-v5-hemi-shift-${treatment.mapStrength}-${treatment.mapFloor}`;
  return material;
}
function createLayerGeometry(layer: ShelfLayer): BufferGeometry {
  const positions: number[] = [], colors: number[] = [], uvs: number[] = [], surfaceBands: number[] = [], surfaceFloors: number[] = [], surfaceFaceLifts: number[] = [], surfaceHemisphereShifts: number[] = [], indices: number[] = [];
  const detailSpecs: DetailSpec[] = [], detailFragments: { kind: DetailSpec['kind']; anchor: Point3; side: Side; runSeed: number; hostDepth: number; vertexStart: number; vertexCount: number }[] = [];
  const horizonFragments: { band: HorizonBand; seed: number; ringSize: number; topHeightRange: number; center: Point3; vertexStart: number; vertexCount: number; indexStart: number; indexCount: number; bounds: { min: Point3; max: Point3 } }[] = [];
  const capFaces = ShapeUtils.triangulateShape(layer.profile.map(([x, y]) => new Vector2(x, y)), []);
  const signatureCount = layer.runs.reduce((count, run) => count + run.z.length - 1, 0);
  let endpointAreaRatio = 0;
  const addVertex = (point: Point3, normal: Vector3, face: SurfaceFace, band: CanyonLayerName = layer.name, baseTone = 1) => {
    const index = positions.length / 3, tint = SURFACE_TINTS[band], shade = surfaceShade(point, band, face, baseTone);
    positions.push(...point); colors.push(tint.r * shade, tint.g * shade, tint.b * shade); uvs.push(...surfaceUv(point, normal, band)); surfaceBands.push(SURFACE_TREATMENTS[band].mapStrength); surfaceFloors.push(SURFACE_TREATMENTS[band].mapFloor); surfaceFaceLifts.push(SURFACE_FACE_LIFT[face]); surfaceHemisphereShifts.push(SURFACE_HEMISPHERE_SHIFT[face]); return index;
  };
  const appendFacets = (source: readonly Point3[], faces: readonly (readonly [number, number, number])[], baseTone: number, preserveWinding = false, band: CanyonLayerName = layer.name, faceKinds?: readonly SurfaceFace[]) => {
    const center = source.reduce((sum, point) => sum.add(new Vector3(...point)), new Vector3()).multiplyScalar(1 / source.length), vertexStart = positions.length / 3, indexStart = indices.length;
    for (const [faceIndex, face] of faces.entries()) {
      const points = face.map((index) => new Vector3(...source[index]!)) as [Vector3, Vector3, Vector3];
      const normal = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])), centroid = points[0].clone().add(points[1]).add(points[2]).multiplyScalar(1 / 3);
      if (!preserveWinding && normal.dot(centroid.sub(center)) < 0) [points[1], points[2]] = [points[2], points[1]];
      normal.copy(points[1]).sub(points[0]).cross(points[2].clone().sub(points[0])).normalize();
      const kind = faceKinds?.[faceIndex] ?? (normal.y > .55 ? 'shelf' : normal.y < -.55 ? 'underside' : 'wall');
      indices.push(...points.map((point) => addVertex([point.x, point.y, point.z], normal, kind, band, baseTone)));
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
        const normalOrder = run.side < 0 ? [quad[0]!, quad[1]!, quad[2]!] : [quad[0]!, quad[2]!, quad[1]!];
        const normal = new Vector3(...normalOrder[1]).sub(new Vector3(...normalOrder[0])).cross(new Vector3(...normalOrder[2]).sub(new Vector3(...normalOrder[0]))).normalize();
        const secondOrder = run.side < 0 ? [quad[0]!, quad[2]!, quad[3]!] : [quad[0]!, quad[3]!, quad[2]!];
        const secondNormal = new Vector3(...secondOrder[1]).sub(new Vector3(...secondOrder[0])).cross(new Vector3(...secondOrder[2]).sub(new Vector3(...secondOrder[0]))).normalize();
        const innerWall = step >= layer.profile.length - 5 || step === layer.profile.length - 1;
        const minNormalY = Math.min(normal.y, secondNormal.y), maxNormalY = Math.max(normal.y, secondNormal.y);
        const kind: SurfaceFace = minNormalY > .55 ? step === 0 ? 'top' : 'shelf' : maxNormalY < -.55 ? 'underside' : minNormalY < -.55 || innerWall ? 'return' : 'wall';
        const vertex = quad.map((point) => addVertex(point, normal, kind));
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
        const normal = new Vector3(...oriented[1]).sub(new Vector3(...oriented[0])).cross(new Vector3(...oriented[2]).sub(new Vector3(...oriented[0]))).normalize();
        indices.push(...oriented.map((point) => addVertex(point, normal, 'return', layer.name, 1.02)));
      }
    }
  }
  const detailIndexStart = indices.length;
  for (const spec of detailSpecs) appendDetail(spec);
  const horizonIndexStart = indices.length;
  if (layer.name === 'far') for (const island of HORIZON_ISLANDS) {
    const ringSize = 8, upperNotch = Math.floor(seededUnit(island.seed, 399) * ringSize), lowerNotch = (upperNotch + 2 + Math.floor(seededUnit(island.seed, 397) * 5)) % ringSize, ringDistance = (a: number, b: number) => Math.min((a - b + ringSize) % ringSize, (b - a + ringSize) % ringSize);
    const angles = Array.from({ length: ringSize }, (_, step) => Math.PI * 2 * step / ringSize + (seededUnit(island.seed, step + 401) - .5) * .13);
    const baseRadius = angles.map((_, step) => .86 + seededUnit(island.seed, step + 419) * .2);
    const direction = island.seed % 4 === 1 ? 1 : -1, upperX = (seededUnit(island.seed, 449) - .5) * island.radiusX * .1, upperZ = (seededUnit(island.seed, 457) - .5) * island.radiusZ * .1, lowerX = upperX - direction * island.radiusX * (.012 + seededUnit(island.seed, 461) * .013), lowerZ = upperZ + direction * island.radiusZ * (.008 + seededUnit(island.seed, 463) * .012);
    const upperDrop = 1.3 + seededUnit(island.seed, 467) * 1.5, lowerDrop = 1.3 + seededUnit(island.seed, 479) * 1.5, upperOuter = .7 + seededUnit(island.seed, 487) * .14, topInner = upperOuter - .18 - seededUnit(island.seed, 491) * .14, lowerInner = upperOuter + (seededUnit(island.seed, 499) - .5) * .1, lowerOuter = Math.min(1.06, lowerInner + .16 + seededUnit(island.seed, 509) * .1), deepScale = lowerOuter * (.97 + seededUnit(island.seed, 521) * .05), skirtScale = Math.min(1.08, deepScale + .02 + seededUnit(island.seed, 523) * .04);
    const notchRange = island.band === 'near' ? { cut: .60, cutVariation: .12, shoulder: .84, shoulderVariation: .08 }
      : island.band === 'mid' ? { cut: .50, cutVariation: .10, shoulder: .80, shoulderVariation: .08 }
        : { cut: .38, cutVariation: .10, shoulder: .74, shoulderVariation: .10 };
    const upperCutDirection = seededUnit(island.seed, 547) > .5 ? 1 : -1, lowerCutDirection = seededUnit(island.seed + 13, 547) > .5 ? 1 : -1, upperCut = notchRange.cut + seededUnit(island.seed, 557) * notchRange.cutVariation, lowerCut = notchRange.cut + seededUnit(island.seed + 17, 557) * notchRange.cutVariation, upperShoulder = notchRange.shoulder + seededUnit(island.seed, 563) * notchRange.shoulderVariation, lowerShoulder = notchRange.shoulder + seededUnit(island.seed + 19, 563) * notchRange.shoulderVariation;
    const cutStations = [upperNotch, (upperNotch + upperCutDirection + ringSize) % ringSize, lowerNotch, (lowerNotch + lowerCutDirection + ringSize) % ringSize], overhang = Array.from({ length: ringSize }, (_, step) => step).filter((step) => !cutStations.includes(step)).sort((a, b) => Math.min(...cutStations.map((cut) => ringDistance(b, cut))) - Math.min(...cutStations.map((cut) => ringDistance(a, cut))) || seededUnit(island.seed, b + 571) - seededUnit(island.seed, a + 571))[0]!;
    const heights = [island.top, island.top - upperDrop, island.top - upperDrop - lowerDrop, island.skirt].map((height, band) => angles.map((_, step) => height + (Math.floor(seededUnit(island.seed + band * 29, step + 541) * 3) - 1) * (band === 0 ? .08 : band === 1 ? .06 : .08)));
    const tiers = [
      { scale: topInner, band: 0, cuts: 0, x: upperX - direction * island.radiusX * (.012 + seededUnit(island.seed, 527) * .013), z: upperZ + direction * island.radiusZ * (.009 + seededUnit(island.seed, 529) * .009) },
      { scale: upperOuter, band: 0, cuts: 0, x: upperX, z: upperZ },
      { scale: lowerInner, band: 1, cuts: 1, x: upperX + direction * island.radiusX * .01, z: upperZ - direction * island.radiusZ * .008 },
      { scale: lowerOuter, band: 1, cuts: 2, x: lowerX, z: lowerZ },
      { scale: deepScale, band: 2, cuts: 2, x: lowerX - direction * island.radiusX * .01, z: lowerZ + direction * island.radiusZ * .008 },
      { scale: skirtScale, band: 3, cuts: 2, x: (seededUnit(island.seed, 533) - .5) * island.radiusX * .04, z: (seededUnit(island.seed, 537) - .5) * island.radiusZ * .04 },
    ] as const;
    const rings = tiers.map((tier, tierIndex) => angles.map((angle, step) => {
      const upperFactor = step === upperNotch ? upperCut : step === (upperNotch + upperCutDirection + ringSize) % ringSize ? upperShoulder : 1, lowerFactor = step === lowerNotch ? lowerCut : step === (lowerNotch + lowerCutDirection + ringSize) % ringSize ? lowerShoulder : 1, notchScale = tier.cuts === 0 ? upperFactor : tier.cuts === 2 ? lowerFactor : Math.min(upperFactor, Math.max(.8, lowerFactor));
      const ledgeScale = step === overhang ? tierIndex === 1 ? 1.14 : tierIndex === 2 ? .92 : 1 : 1, radius = tier.scale * baseRadius[step]! * notchScale * ledgeScale;
      return [island.x + tier.x + Math.cos(angle) * island.radiusX * radius, heights[tier.band]![step]!, island.z + tier.z + Math.sin(angle) * island.radiusZ * radius] as Point3;
    }));
    const points = rings.flat(), topCenter = points.length, bottomCenter = points.length + 1;
    points.push([rings[0]!.reduce((sum, point) => sum + point[0], 0) / ringSize, rings[0]!.reduce((sum, point) => sum + point[1], 0) / ringSize, rings[0]!.reduce((sum, point) => sum + point[2], 0) / ringSize], [rings[5]!.reduce((sum, point) => sum + point[0], 0) / ringSize, rings[5]!.reduce((sum, point) => sum + point[1], 0) / ringSize, rings[5]!.reduce((sum, point) => sum + point[2], 0) / ringSize]);
    const faces: [number, number, number][] = [], faceKinds: SurfaceFace[] = [];
    const pushHorizonFace = (face: [number, number, number], direction: 'up' | 'down' | 'out', kind: SurfaceFace) => { const [a, b, c] = face.map((index) => new Vector3(...points[index]!)) as [Vector3, Vector3, Vector3], normal = b.clone().sub(a).cross(c.clone().sub(a)), centroid = a.clone().add(b).add(c).multiplyScalar(1 / 3), facing = direction === 'up' ? normal.y : direction === 'down' ? -normal.y : normal.x * (centroid.x - island.x) + normal.z * (centroid.z - island.z); if (facing < 0) [face[1], face[2]] = [face[2], face[1]]; faces.push(face); faceKinds.push(kind); };
    for (let step = 0; step < ringSize; step += 1) { const next = (step + 1) % ringSize; pushHorizonFace([topCenter, next, step], 'up', 'top'); pushHorizonFace([bottomCenter, ringSize * 5 + step, ringSize * 5 + next], 'down', 'underside'); for (let tier = 0; tier < tiers.length - 1; tier += 1) { const upper = tier * ringSize + step, upperNext = tier * ringSize + next, lower = upper + ringSize, lowerNext = upperNext + ringSize, shelf = tier === 0 || tier === 2, kind: SurfaceFace = shelf ? 'shelf' : cutStations.includes(step) || cutStations.includes(next) ? 'return' : 'wall', direction = shelf ? 'up' : 'out'; pushHorizonFace([upper, upperNext, lowerNext], direction, kind); pushHorizonFace([upper, lowerNext, lower], direction, kind); } }
    const added = appendFacets(points, faces, island.band === 'near' ? .84 : island.band === 'mid' ? .96 : 1.06, true, island.band, faceKinds);
    const axes = [0, 1, 2] as const, min = axes.map((axis) => Math.min(...points.map((point) => point[axis]))) as [number, number, number], max = axes.map((axis) => Math.max(...points.map((point) => point[axis]))) as [number, number, number];
    horizonFragments.push({ band: island.band, seed: island.seed, ringSize, topHeightRange: Math.max(...rings[0]!.map((point) => point[1])) - Math.min(...rings[0]!.map((point) => point[1])), ...added, bounds: { min, max } });
  }
  const geometry = new BufferGeometry();
  geometry.name = `${layer.objectName}-geometry`;
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3));
  geometry.setAttribute('surfaceBandStrength', new Float32BufferAttribute(surfaceBands, 1));
  geometry.setAttribute('surfaceBandFloor', new Float32BufferAttribute(surfaceFloors, 1));
  geometry.setAttribute('surfaceFaceLift', new Float32BufferAttribute(surfaceFaceLifts, 1));
  geometry.setAttribute('surfaceHemisphereShift', new Float32BufferAttribute(surfaceHemisphereShifts, 1));
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
      const treatment = SURFACE_TREATMENTS[layer.name];
      const mesh = new Mesh(
        createLayerGeometry(layer),
        createSurfaceMaterial(treatment),
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
  /** Non-owning clean-room basalt map shared by every canyon depth layer. */
  setSurfaceMap(texture: Texture | null): void {
    for (const mesh of this.shelfLayers) {
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
