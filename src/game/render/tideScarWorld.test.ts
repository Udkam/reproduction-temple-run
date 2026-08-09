import { Matrix4, Mesh, MeshStandardMaterial, PerspectiveCamera, Texture, Vector3, Vector4 } from 'three';
import { describe, expect, it } from 'vitest';
import { TideScarWorld } from './tideScarWorld';
import { applyTR4RuntimeLensShift, createCausewayMaterial, createDeckCapGeometry, presentationRoadStart, shouldShowPursuer, TR4_RUNTIME_CAMERA, WorldRenderer } from './WorldRenderer';
import { d4ProfileForViewport } from './d4Profile';
import { WORLD_METRICS } from './theme';

const LAYERS = [['tide-scar-near-fractured-inner-lips', 'near', 3, 13, 10, 6, 0],
  ['tide-scar-mid-interrupted-buttress-recesses', 'mid', 4, 14, 12, 8, 0],
  ['tide-scar-far-low-ridge-mesa-chains', 'far', 4, 11, 12, 8, 12]] as const;
async function geometryFingerprint(mesh: Mesh): Promise<string> {
  const views = [mesh.geometry.getAttribute('position').array, mesh.geometry.getIndex()!.array]
    .map((array) => new Uint8Array(array.buffer, array.byteOffset, array.byteLength));
  const payload = new Uint8Array(8 + views[0]!.byteLength + views[1]!.byteLength), header = new DataView(payload.buffer);
  header.setUint32(0, views[0]!.byteLength, true); header.setUint32(4, views[1]!.byteLength, true);
  payload.set(views[0]!, 8); payload.set(views[1]!, 8 + views[0]!.byteLength);
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', payload));
  return Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('');
}
async function rawArrayFingerprint(array: { readonly buffer: ArrayBufferLike; readonly byteOffset: number; readonly byteLength: number }): Promise<string> {
  const view = new Uint8Array(array.buffer, array.byteOffset, array.byteLength), payload = new Uint8Array(view.byteLength);
  payload.set(view);
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', payload));
  return Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('');
}
const HORIZON_GEOMETRY_CASES = [
  { x: -52, z: -54, radiusX: 13, radiusZ: 18, seed: 401, band: 'near' }, { x: -14, z: -62, radiusX: 8, radiusZ: 16, seed: 409, band: 'near' },
  { x: 15, z: -55, radiusX: 8, radiusZ: 17, seed: 419, band: 'near' }, { x: 52, z: -61, radiusX: 13, radiusZ: 20, seed: 421, band: 'near' },
  { x: -42, z: -84, radiusX: 12, radiusZ: 18, seed: 431, band: 'mid' }, { x: -16, z: -91, radiusX: 7, radiusZ: 15, seed: 433, band: 'mid' },
  { x: 16, z: -86, radiusX: 7, radiusZ: 16, seed: 439, band: 'mid' }, { x: 42, z: -94, radiusX: 12, radiusZ: 18, seed: 443, band: 'mid' },
  { x: -34, z: -122, radiusX: 11, radiusZ: 17, seed: 449, band: 'far' }, { x: -12, z: -130, radiusX: 5, radiusZ: 14, seed: 457, band: 'far' },
  { x: 12, z: -124, radiusX: 5, radiusZ: 15, seed: 461, band: 'far' }, { x: 34, z: -132, radiusX: 11, radiusZ: 17, seed: 463, band: 'far' },
] as const;
const SHELF_RUN_CASES = [
  { seed: 11, side: -1, stations: 5 }, { seed: 17, side: 1, stations: 4 }, { seed: 23, side: -1, stations: 4 },
  { seed: 41, side: -1, stations: 4 }, { seed: 47, side: 1, stations: 4 }, { seed: 53, side: -1, stations: 4 }, { seed: 59, side: 1, stations: 4 },
  { seed: 89, side: -1, stations: 4 }, { seed: 97, side: 1, stations: 4 }, { seed: 101, side: -1, stations: 4 }, { seed: 103, side: 1, stations: 4 },
] as const;
type ActualTriangle = [Vector3, Vector3, Vector3];
type NdcPoint = { x: number; y: number };
function actualTriangles(mesh: Mesh, start = 0, end = mesh.geometry.getIndex()!.count): ActualTriangle[] {
  const position = mesh.geometry.getAttribute('position'), index = mesh.geometry.getIndex()!;
  mesh.updateWorldMatrix(true, false);
  const triangles: ActualTriangle[] = [];
  for (let offset = start; offset < end; offset += 3) triangles.push([0, 1, 2].map((step) => new Vector3().fromBufferAttribute(position, index.getX(offset + step)).applyMatrix4(mesh.matrixWorld)) as ActualTriangle);
  return triangles;
}
function clipTriangleToNdc(triangle: ActualTriangle, viewProjection: Matrix4): NdcPoint[] {
  let polygon = triangle.map((point) => new Vector4(point.x, point.y, point.z, 1).applyMatrix4(viewProjection));
  const planes = [(point: Vector4) => point.x + point.w, (point: Vector4) => point.w - point.x, (point: Vector4) => point.y + point.w,
    (point: Vector4) => point.w - point.y, (point: Vector4) => point.z + point.w, (point: Vector4) => point.w - point.z];
  for (const distance of planes) {
    const clipped: Vector4[] = [];
    for (let index = 0; index < polygon.length; index += 1) {
      const from = polygon[(index + polygon.length - 1) % polygon.length]!, to = polygon[index]!, fromDistance = distance(from), toDistance = distance(to), fromInside = fromDistance >= 0, toInside = toDistance >= 0;
      if (fromInside !== toInside) clipped.push(from.clone().lerp(to, fromDistance / (fromDistance - toDistance)));
      if (toInside) clipped.push(to);
    }
    polygon = clipped;
    if (polygon.length === 0) break;
  }
  return polygon.filter((point) => point.w > 1e-7).map((point) => ({ x: point.x / point.w, y: point.y / point.w }));
}
function bandTriangles(world: TideScarWorld, bandIndex: number): ActualTriangle[] {
  world.root.updateMatrixWorld(true);
  const primary = world.root.getObjectByName(LAYERS[bandIndex]![0]) as Mesh, far = world.root.getObjectByName(LAYERS[2][0]) as Mesh, farIndex = far.geometry.getIndex()!, horizonStart = farIndex.count - 12 * 96 * 3;
  const triangles = actualTriangles(primary, 0, bandIndex === 2 ? horizonStart : primary.geometry.getIndex()!.count), islandStart = horizonStart + bandIndex * 4 * 96 * 3;
  triangles.push(...actualTriangles(far, islandStart, islandStart + 4 * 96 * 3));
  return triangles;
}
function clipSegmentToNdc(start: Vector3, end: Vector3, viewProjection: Matrix4): [NdcPoint, NdcPoint] | null {
  let from = new Vector4(start.x, start.y, start.z, 1).applyMatrix4(viewProjection), to = new Vector4(end.x, end.y, end.z, 1).applyMatrix4(viewProjection);
  const planes = [(point: Vector4) => point.x + point.w, (point: Vector4) => point.w - point.x, (point: Vector4) => point.y + point.w,
    (point: Vector4) => point.w - point.y, (point: Vector4) => point.z + point.w, (point: Vector4) => point.w - point.z];
  for (const distance of planes) {
    const fromDistance = distance(from), toDistance = distance(to);
    if (fromDistance < 0 && toDistance < 0) return null;
    if (fromDistance < 0 || toDistance < 0) { const intersection = from.clone().lerp(to, fromDistance / (fromDistance - toDistance)); if (fromDistance < 0) from = intersection; else to = intersection; }
  }
  if (from.w <= 1e-7 || to.w <= 1e-7) return null;
  return [{ x: from.x / from.w, y: from.y / from.w }, { x: to.x / to.w, y: to.y / to.w }];
}
function mergeIntervals(intervals: [number, number][]): [number, number][] {
  const sorted = intervals.filter(([start, end]) => end > start).sort((a, b) => a[0] - b[0]), merged: [number, number][] = [];
  for (const interval of sorted) { const previous = merged.at(-1); if (previous && interval[0] <= previous[1] + 1e-7) previous[1] = Math.max(previous[1], interval[1]); else merged.push([...interval]); }
  return merged;
}
function scanlineSilhouette(triangles: ActualTriangle[], camera: PerspectiveCamera): readonly { height: number; maxGap: number; maxGapY: number; maxGapTriangle: number }[] {
  camera.updateMatrixWorld();
  const viewProjection = new Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse), polygons = triangles.map((triangle, triangleIndex) => ({ triangleIndex, side: triangle.reduce((sum, point) => sum + point.x, 0) < 0 ? 0 as const : 1 as const, points: clipTriangleToNdc(triangle, viewProjection) })).filter((entry) => entry.points.length >= 3);
  const roadLines = ([-1, 1] as const).map((side) => clipSegmentToNdc(new Vector3(side * (WORLD_METRICS.roadWidth / 2 + .4), 0, presentationRoadStart(0)), new Vector3(side * (WORLD_METRICS.roadWidth / 2 + .4), 0, -240), viewProjection));
  if (roadLines.some((line) => line === null)) throw new Error('protected route edge did not survive homogeneous clipping');
  const cells = 2048, step = 2 / cells;
  return ([0, 1] as const).map((side) => {
    const line = roadLines[side]!, routeMinY = Math.max(-1, Math.min(line[0].y, line[1].y)), routeMaxY = Math.min(1, Math.max(line[0].y, line[1].y)), roadX = (y: number) => line[0].x + (line[1].x - line[0].x) * (y - line[0].y) / (line[1].y - line[0].y); let occupied = 0, maxGap = -Infinity, maxGapY = Number.NaN, maxGapTriangle = -1;
    for (let scan = 0; scan < cells; scan += 1) {
      const y = -1 + (scan + .5) * step; if (y < routeMinY || y > routeMaxY) continue; const road = roadX(y), intervals: { range: [number, number]; triangleIndex: number }[] = [];
      for (const polygon of polygons) {
        if (polygon.side !== side) continue; const crossings: number[] = [];
        for (let edge = 0; edge < polygon.points.length; edge += 1) { const a = polygon.points[edge]!, b = polygon.points[(edge + 1) % polygon.points.length]!; if ((a.y <= y && b.y > y) || (b.y <= y && a.y > y)) crossings.push(a.x + (b.x - a.x) * (y - a.y) / (b.y - a.y)); }
        if (crossings.length < 2) continue; const low = Math.max(-1, Math.min(...crossings)), high = Math.min(1, Math.max(...crossings)), interval: [number, number] = side === 0 ? [low, Math.min(high, road)] : [Math.max(low, road), high]; if (interval[1] > interval[0]) intervals.push({ range: interval, triangleIndex: polygon.triangleIndex });
      }
      const substantial = mergeIntervals(intervals.map((entry) => entry.range)).filter(([start, end]) => (end - start) * camera.aspect >= .02); if (substantial.length === 0) continue; occupied += 1;
      const boundary = side === 0 ? substantial.at(-1)![1] : substantial[0]![0], owner = intervals.find((entry) => Math.abs(entry.range[side === 0 ? 1 : 0] - boundary) < 1e-7)?.triangleIndex ?? -1;
      const rawGap = side === 0 ? road - boundary : boundary - road, gap = Math.max(0, rawGap) * camera.aspect; if (gap > maxGap) { maxGap = gap; maxGapY = y; maxGapTriangle = owner; }
    }
    return { height: occupied * step, maxGap, maxGapY, maxGapTriangle };
  });
}
function testSeededUnit(index: number, salt: number): number {
  let value = Math.imul(index + 1, 0x45d9f3b) ^ Math.imul(salt + 17, 0x27d4eb2d);
  value ^= value >>> 16; value = Math.imul(value, 0x45d9f3b); value ^= value >>> 16;
  return (value >>> 0) / 0xffffffff;
}
describe('Tide Scar geometric canyon presentation', () => {
  it('builds thick, distinct near/mid/far topology without panorama, plane, or instanced-card geometry', async () => {
    const world = new TideScarWorld();
    const topologySizes: number[] = [];
    const abyss = world.root.getObjectByName('tide-scar-faceted-abyss-bed') as Mesh;
    abyss.geometry.computeBoundingBox();
    const abyssNormals = abyss.geometry.getAttribute('normal');
    const averageAbyssNormalY = Array.from({ length: abyssNormals.count }, (_, index) => abyssNormals.getY(index))
      .reduce((sum, value) => sum + value, 0) / abyssNormals.count;
    expect(averageAbyssNormalY).toBeGreaterThan(.7);
    for (const [name, layer, runCount, profilePointCount, signatureCount, detailFragmentCount, horizonIslandCount] of LAYERS) {
      const object = world.root.getObjectByName(name);
      expect(object).toBeInstanceOf(Mesh);
      const mesh = object as Mesh;
      mesh.geometry.computeBoundingBox();
      const bounds = mesh.geometry.boundingBox!;
      expect(bounds.max.x - bounds.min.x).toBeGreaterThan(10);
      expect(bounds.max.y - bounds.min.y).toBeGreaterThan(10);
      expect(bounds.max.z - bounds.min.z).toBeGreaterThan(40);
      const expectedSideTriangles = signatureCount * profilePointCount * 2, expectedCapTriangles = runCount * (profilePointCount - 2) * 2;
      const detailTriangleCount = detailFragmentCount * 8, horizonTriangleCount = horizonIslandCount * 96;
      expect(mesh.geometry.userData).toMatchObject({ canyonLayer: layer, runCount, profilePointCount, signatureCount, detailFragmentCount, detailTriangleCount, horizonIslandCount, horizonTriangleCount,
        closedProfile: true, capCount: runCount * 2, sideTriangleCount: expectedSideTriangles,
        capTriangleCount: expectedCapTriangles,
        construction: 'closed-segmented-longitudinal-shelf-recess-buttress-foot-talus-strata-detail' });
      expect(mesh.geometry.userData.endpointAreaRatio).toBeLessThan(.2);
      expect(mesh.geometry.getIndex()!.count / 3).toBe(expectedSideTriangles + expectedCapTriangles + detailTriangleCount + horizonTriangleCount);
      expect(mesh.geometry.userData.horizonIndexStart - mesh.geometry.userData.detailIndexStart).toBe(detailTriangleCount * 3);
      expect(mesh.geometry.getAttribute('uv').count).toBe(mesh.geometry.getAttribute('position').count);
      const position = mesh.geometry.getAttribute('position'), fragments = mesh.geometry.userData.detailFragments as { kind: string; anchor: readonly number[]; side: number; runSeed: number; hostDepth: number; vertexStart: number; vertexCount: number }[];
      for (const fragment of fragments) {
        expect(['talus', 'strata']).toContain(fragment.kind); expect(fragment.vertexCount).toBe(24);
        const points = Array.from({ length: fragment.vertexCount }, (_, offset) => new Vector3().fromBufferAttribute(position, fragment.vertexStart + offset));
        const unique = [...new Map(points.map((point) => [point.toArray().join(','), point])).values()], center = unique.reduce((sum, point) => sum.add(point), new Vector3()).multiplyScalar(1 / unique.length);
        expect(unique).toHaveLength(6);
        for (const axis of ['x', 'y', 'z'] as const) expect(Math.max(...unique.map((point) => point[axis])) - Math.min(...unique.map((point) => point[axis]))).toBeGreaterThan(.04);
        const contact = unique.map((point) => (point.x - fragment.anchor[0]!) * fragment.side); expect(Math.min(...contact)).toBeLessThan(0); expect(Math.min(...contact)).toBeGreaterThanOrEqual(-fragment.hostDepth * .13); expect(contact.filter((offset) => offset > 0).length).toBeGreaterThan(unique.length / 2);
        for (let offset = 0; offset < points.length; offset += 3) {
          const [a, b, c] = points.slice(offset, offset + 3), normal = b!.clone().sub(a!).cross(c!.clone().sub(a!)), centroid = a!.clone().add(b!).add(c!).multiplyScalar(1 / 3);
          expect(normal.length()).toBeGreaterThan(1e-4); expect(normal.dot(centroid.sub(center))).toBeGreaterThan(0);
        }
      }
      const runDetails = new Map<number, string[]>(); for (const fragment of fragments) runDetails.set(fragment.runSeed, [...runDetails.get(fragment.runSeed) ?? [], fragment.kind]); expect(runDetails.size).toBe(runCount);
      for (const details of runDetails.values()) expect(details.sort()).toEqual(['strata', 'talus']);
      topologySizes.push(mesh.geometry.getAttribute('position').count);
    }
    expect(new Set(topologySizes).size).toBe(3);
    let runCase = 0;
    for (const [name, layer, runCount, profilePointCount] of LAYERS) {
      const mesh = world.root.getObjectByName(name) as Mesh, position = mesh.geometry.getAttribute('position'), index = mesh.geometry.getIndex()!, fingerprints = new Set<string>(); let indexCursor = 0;
      for (let run = 0; run < runCount; run += 1) {
        const spec = SHELF_RUN_CASES[runCase++]!, stationProfiles: Vector3[][] = [];
        for (let pair = 0; pair < spec.stations - 1; pair += 1) {
          const pairStart = indexCursor + pair * profilePointCount * 6;
          const current = Array.from({ length: profilePointCount }, (_, step) => new Vector3().fromBufferAttribute(position, index.getX(pairStart + step * 6)));
          const next = Array.from({ length: profilePointCount }, (_, step) => new Vector3().fromBufferAttribute(position, index.getX(pairStart + step * 6 + (spec.side < 0 ? 1 : 2))));
          if (pair === 0) stationProfiles.push(current);
          stationProfiles.push(next);
        }
        const stations = stationProfiles.map((profile) => profile[0]!);
        expect(stations).toHaveLength(spec.stations); expect(stations.every((point) => point.toArray().every(Number.isFinite))).toBe(true);
        const breaks = stations.slice(1).map((point, station) => ({ lateral: Math.abs(point.x - stations[station]!.x), elevation: Math.abs(point.y - stations[station]!.y) }));
        expect(breaks.filter((entry) => entry.lateral >= .35 || entry.elevation >= .28)).toHaveLength(spec.stations - 1); expect(breaks.some((entry) => entry.lateral >= .35 && entry.elevation >= .28)).toBe(true);
        const interior = stations.slice(1, -1), interiorBreaks = interior.slice(1).map((point, station) => ({ lateral: Math.abs(point.x - interior[station]!.x), elevation: Math.abs(point.y - interior[station]!.y) }));
        if (spec.seed === 11) { expect(Math.max(...interior.map((point) => point.x)) - Math.min(...interior.map((point) => point.x)), 'seed 11 interior lateral range').toBeGreaterThanOrEqual(1.25); expect(Math.max(...interior.map((point) => point.y)) - Math.min(...interior.map((point) => point.y)), 'seed 11 interior elevation range').toBeGreaterThanOrEqual(1.50); expect(interiorBreaks.every((entry) => entry.lateral >= .75 && entry.elevation >= .75)).toBe(true); }
        else { expect(interior).toHaveLength(2); expect(interiorBreaks[0]!.lateral, `seed ${spec.seed} interior lateral break`).toBeGreaterThanOrEqual(.75); expect(interiorBreaks[0]!.elevation, `seed ${spec.seed} interior elevation break`).toBeGreaterThanOrEqual(.50); }
        const shoulderStep = stationProfiles[1]!.map((point, step) => ({ step, outward: spec.side * (point.x - stationProfiles[1]![0]!.x) })).sort((a, b) => b.outward - a.outward)[0]!.step;
        const crownMove = stationProfiles[2]![0]!.clone().sub(stationProfiles[1]![0]!), shoulderMove = stationProfiles[2]![shoulderStep]!.clone().sub(stationProfiles[1]![shoulderStep]!);
        expect(Math.abs(shoulderMove.x - crownMove.x) >= .35 || Math.abs(shoulderMove.y - crownMove.y) >= .30, `seed ${spec.seed} actual crown-versus-shoulder displacement`).toBe(true);
        fingerprints.add(stations.map((point) => `${(Math.abs(point.x) - Math.abs(stations[0]!.x)).toFixed(3)}:${(point.y - stations[0]!.y).toFixed(3)}`).join('|'));
        indexCursor += (spec.stations - 1) * profilePointCount * 6 + (profilePointCount - 2) * 6;
      }
      expect(fingerprints.size).toBe(runCount);
    }
    const farMesh = world.root.getObjectByName(LAYERS[2][0]) as Mesh, farBounds = farMesh.geometry.boundingBox!;
    expect(farBounds.max.z).toBeLessThan(-25);
    expect(farBounds.min.z).toBeGreaterThan(-230);
    const position = farMesh.geometry.getAttribute('position'), index = farMesh.geometry.getIndex()!;
    const welded = new Map<string, Vector3>(), adjacency = new Map<string, Set<string>>();
    type HorizonTriangle = { keys: [string, string, string]; points: [Vector3, Vector3, Vector3] };
    const triangles: HorizonTriangle[] = [], keyOf = (point: Vector3) => point.toArray().map((value) => Math.round(value * 1e5)).join(':');
    for (let offset = 0; offset < index.count; offset += 3) {
      const points = [0, 1, 2].map((step) => new Vector3().fromBufferAttribute(position, index.getX(offset + step))) as [Vector3, Vector3, Vector3], keys = points.map(keyOf) as [string, string, string]; triangles.push({ keys, points });
      for (let step = 0; step < 3; step += 1) { const a = keys[step]!, b = keys[(step + 1) % 3]!; welded.set(a, points[step]!); welded.set(b, points[(step + 1) % 3]!); if (!adjacency.has(a)) adjacency.set(a, new Set()); if (!adjacency.has(b)) adjacency.set(b, new Set()); adjacency.get(a)!.add(b); adjacency.get(b)!.add(a); }
    }
    const remaining = new Set(adjacency.keys()), allComponents: Set<string>[] = [];
    while (remaining.size > 0) { const component = new Set<string>(), queue = [remaining.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!remaining.delete(key)) continue; component.add(key); queue.push(...adjacency.get(key)!); } allComponents.push(component); }
    const components = allComponents.filter((component) => component.size === 50 && triangles.filter((triangle) => triangle.keys.every((key) => component.has(key))).length === 96);
    expect(components).toHaveLength(12);
    expect(components.reduce((sum, component) => sum + triangles.filter((triangle) => triangle.keys.every((key) => component.has(key))).length, 0)).toBe(12 * 96);
    const actual = components.map((component) => {
      const points = [...component].map((key) => welded.get(key)!), center = points.reduce((sum, point) => sum.add(point), new Vector3()).multiplyScalar(1 / points.length), componentTriangles = triangles.filter((triangle) => triangle.keys.every((key) => component.has(key))), edgeUse = new Map<string, number>();
      const bounds = { min: new Vector3(...(['x', 'y', 'z'] as const).map((axis) => Math.min(...points.map((point) => point[axis]))) as [number, number, number]), max: new Vector3(...(['x', 'y', 'z'] as const).map((axis) => Math.max(...points.map((point) => point[axis]))) as [number, number, number]) };
      expect(points).toHaveLength(50); expect(componentTriangles).toHaveLength(96);
      for (const triangle of componentTriangles) { const [a, b, c] = triangle.points, normal = b.clone().sub(a).cross(c.clone().sub(a)); expect(normal.length()).toBeGreaterThan(1e-4); for (const [u, v] of [[0, 1], [1, 2], [2, 0]] as const) { const edge = [triangle.keys[u], triangle.keys[v]].sort().join('|'); edgeUse.set(edge, (edgeUse.get(edge) ?? 0) + 1); } }
      const openEdges = [...edgeUse.entries()].filter(([, count]) => count !== 2);
      expect(openEdges, `canyon component non-manifold edges ${JSON.stringify(openEdges.slice(0, 12))}`).toEqual([]);
      const capKeys = [...component].filter((key) => adjacency.get(key)!.size === 8); expect(capKeys).toHaveLength(2);
      const capRecords = capKeys.map((key) => { const faces = componentTriangles.filter((triangle) => triangle.keys.includes(key)), normalsY = faces.map((triangle) => triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).y); expect(faces).toHaveLength(8); return { key, faces, normalsY }; });
      const topCaps = capRecords.filter((record) => record.normalsY.every((normalY) => normalY > 1e-4)), bottomCaps = capRecords.filter((record) => record.normalsY.every((normalY) => normalY < -1e-4));
      expect(topCaps).toHaveLength(1); expect(bottomCaps).toHaveLength(1); expect([...topCaps[0]!.faces, ...bottomCaps[0]!.faces]).toHaveLength(16);
      const topCapKey = topCaps[0]!.key, bottomCapKey = bottomCaps[0]!.key, ringKeys: Set<string>[] = [new Set(adjacency.get(topCapKey)!)], covered = new Set([topCapKey, bottomCapKey, ...adjacency.get(topCapKey)!]);
      expect(ringKeys[0]!.size).toBe(8);
      for (let tier = 1; tier < 6; tier += 1) { const next = new Set([...ringKeys[tier - 1]!].flatMap((key) => [...adjacency.get(key)!]).filter((key) => component.has(key) && !covered.has(key))); expect(next.size, `topology ring ${tier}`).toBe(8); ringKeys.push(next); for (const key of next) covered.add(key); }
      expect(ringKeys[5]).toEqual(new Set(adjacency.get(bottomCapKey)!)); expect(covered.size).toBe(50); expect(ringKeys.flatMap((ring) => [...ring])).toHaveLength(48);
      type RingPlan = { keys: Set<string>; boundary: Vector3[]; center: Vector3; extentX: number; extentZ: number; area: number; meanY: number; radialBreak: number; notchBin: number };
      const ringPlan = (keys: Set<string>): RingPlan => { const boundary = [...keys].map((key) => welded.get(key)!), planCenter = boundary.reduce((sum, point) => sum.add(new Vector3(point.x, 0, point.z)), new Vector3()).multiplyScalar(1 / boundary.length), ordered = boundary.sort((a, b) => Math.atan2(a.z - planCenter.z, a.x - planCenter.x) - Math.atan2(b.z - planCenter.z, b.x - planCenter.x)), extentX = Math.max(...ordered.map((point) => point.x)) - Math.min(...ordered.map((point) => point.x)), extentZ = Math.max(...ordered.map((point) => point.z)) - Math.min(...ordered.map((point) => point.z)), radii = ordered.map((point) => Math.hypot((point.x - planCenter.x) / extentX, (point.z - planCenter.z) / extentZ)), notchStep = radii.indexOf(Math.min(...radii)), notchAngle = Math.atan2(ordered[notchStep]!.z - planCenter.z, ordered[notchStep]!.x - planCenter.x), area = Math.abs(ordered.reduce((sum, point, step) => sum + point.x * ordered[(step + 1) % ordered.length]!.z - ordered[(step + 1) % ordered.length]!.x * point.z, 0)) / 2; expect(ordered).toHaveLength(8); for (const [step, point] of ordered.entries()) { const linked = [...adjacency.get(keyOf(point))!].filter((key) => keys.has(key)).sort(), expected = [keyOf(ordered[(step + 7) % 8]!), keyOf(ordered[(step + 1) % 8]!)].sort(); expect(linked).toEqual(expected); } return { keys, boundary: ordered, center: planCenter, extentX, extentZ, area, meanY: ordered.reduce((sum, point) => sum + point.y, 0) / ordered.length, radialBreak: Math.max(...radii) - Math.min(...radii), notchBin: (Math.round((notchAngle + Math.PI) / (Math.PI / 4)) + 8) % 8 }; };
      const ringPlans = ringKeys.map(ringPlan), strips = Array.from({ length: 5 }, (_, strip) => { const pair = new Set([...ringKeys[strip]!, ...ringKeys[strip + 1]!]), faces = componentTriangles.filter((triangle) => triangle.keys.every((key) => pair.has(key))); expect(faces, `ring strip ${strip}`).toHaveLength(16); return faces; });
      const stripNormalYs = strips.map((faces) => faces.map((triangle) => triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y));
      const shelfStripIndices = stripNormalYs.map((normalYs, strip) => normalYs.every((normalY) => normalY > .55) ? strip : -1).filter((strip) => strip >= 0); expect(shelfStripIndices, `component ${center.x.toFixed(2)},${center.z.toFixed(2)} strip minima ${stripNormalYs.map((normalYs) => Math.min(...normalYs).toFixed(4)).join('/')}`).toEqual([0, 2]);
      const shelves = [[0, 1], [2, 3]].map(([innerIndex, outerIndex], shelfIndex) => { const inner = ringPlans[innerIndex]!, outer = ringPlans[outerIndex]!; expect(outer.area / inner.area, `component ${center.x.toFixed(2)},${center.z.toFixed(2)} shelf ${shelfIndex}`).toBeGreaterThan(1.23); expect(Math.abs(outer.meanY - inner.meanY)).toBeLessThan(.05); expect(outer.center.distanceTo(inner.center)).toBeGreaterThan(.03); expect(outer.radialBreak).toBeGreaterThan(.1); return { inner, outer }; });
      const orderedCrown = ringPlans[0]!.boundary, deepRing = ringPlans[4]!, bottomRing = ringPlans[5]!;
      expect(welded.get(topCapKey)!.y).toBeCloseTo(ringPlans[0]!.meanY, 5); expect(welded.get(bottomCapKey)!.y).toBeCloseTo(bottomRing.meanY, 5);
      for (const [upper, lower] of [[1, 2], [3, 4], [4, 5]] as const) expect(ringPlans[upper]!.meanY - ringPlans[lower]!.meanY, `ring ${upper}-${lower} mean elevation gap`).toBeGreaterThan(1.2);
      const xzRadius = (point: Vector3, plan: RingPlan) => Math.hypot(point.x - plan.center.x, point.z - plan.center.z);
      const spec = [...HORIZON_GEOMETRY_CASES].sort((a, b) => Math.hypot(center.x - a.x, center.z - a.z) - Math.hypot(center.x - b.x, center.z - b.z))[0]!;
      const proveRiser = (upper: RingPlan, lower: RingPlan, requireNearPlan = true) => { const ringKeys = new Set([...upper.keys, ...lower.keys]), faces = componentTriangles.filter((triangle) => triangle.keys.every((key) => ringKeys.has(key))), verticality = faces.map((triangle) => Math.abs(triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y)).sort((a, b) => a - b), matches = Array.from({ length: 8 }, (_, offset) => ({ offset, changes: upper.boundary.map((point, step) => Math.hypot(point.x - lower.boundary[(step + offset) % 8]!.x, point.z - lower.boundary[(step + offset) % 8]!.z)).sort((a, b) => a - b) })).sort((a, b) => a.changes[3]! - b.changes[3]!), match = matches[0]!, meanRadius = upper.boundary.reduce((sum, point) => sum + xzRadius(point, upper), 0) / upper.boundary.length, riserCenter = upper.center.clone().add(lower.center).multiplyScalar(.5); expect(faces).toHaveLength(16); for (const triangle of faces) { const normal = triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])), centroid = triangle.points[0].clone().add(triangle.points[1]).add(triangle.points[2]).multiplyScalar(1 / 3); expect(normal.x * (centroid.x - riserCenter.x) + normal.z * (centroid.z - riserCenter.z)).toBeGreaterThan(0); } expect(verticality[7]).toBeLessThan(.45); expect(upper.meanY - lower.meanY).toBeGreaterThan(1.2); if (requireNearPlan) expect(match.changes[3]! / meanRadius).toBeLessThan(.12); return upper.boundary.map((point, step) => xzRadius(point, upper) - xzRadius(lower.boundary[(step + match.offset) % 8]!, lower)); };
      const upperOverhang = proveRiser(shelves[0]!.outer, shelves[1]!.inner); proveRiser(shelves[1]!.outer, deepRing); proveRiser(deepRing, bottomRing, false); const minOverhang = Math.min(...upperOverhang), maxOverhang = Math.max(...upperOverhang), localMeanRadius = [...shelves[0]!.outer.boundary.map((point) => xzRadius(point, shelves[0]!.outer)), ...shelves[1]!.inner.boundary.map((point) => xzRadius(point, shelves[1]!.inner))].reduce((sum, radius) => sum + radius, 0) / 16; if (spec.band === 'far') { expect(maxOverhang).toBeGreaterThan(.35); expect(maxOverhang).toBeLessThan(8); expect(maxOverhang / localMeanRadius).toBeLessThan(.65); } else { expect(minOverhang, `seed ${spec.seed} bridge radial minimum`).toBeGreaterThan(-1); expect(maxOverhang, `seed ${spec.seed} bridge radial maximum`).toBeLessThan(-.2); } const notchDistance = (shelves[1]!.outer.notchBin - shelves[0]!.outer.notchBin + 8) % 8; expect(notchDistance).toBeGreaterThanOrEqual(2); expect(notchDistance).toBeLessThanOrEqual(6);
      const crownRange = Math.max(...orderedCrown.map((point) => point.y)) - Math.min(...orderedCrown.map((point) => point.y)), visibleOuter = shelves[0]!.outer.boundary, visibleOuterRange = Math.max(...visibleOuter.map((point) => point.y)) - Math.min(...visibleOuter.map((point) => point.y)), requiredCrownRange = spec.band === 'near' ? .55 : spec.band === 'mid' ? .40 : .26;
      expect(crownRange).toBeGreaterThanOrEqual(requiredCrownRange); expect(crownRange).toBeLessThan(1.35); expect(visibleOuterRange, `seed ${spec.seed} visible outer-ring relief`).toBeGreaterThanOrEqual(requiredCrownRange); expect(visibleOuterRange).toBeLessThan(1.35);
      const width = bounds.max.x - bounds.min.x, depth = bounds.max.z - bounds.min.z, height = bounds.max.y - bounds.min.y; expect(height).toBeGreaterThan(7); expect(height / Math.max(width, depth)).toBeLessThan(.55); expect(width / depth).toBeGreaterThan(.24); expect(width / depth).toBeLessThan(1.6);
      const profile = [(shelves[0]!.outer.meanY - shelves[1]!.inner.meanY).toFixed(1), (shelves[1]!.outer.meanY - deepRing.meanY).toFixed(1), (shelves[0]!.outer.area / shelves[0]!.inner.area).toFixed(2), (shelves[1]!.outer.area / shelves[1]!.inner.area).toFixed(2), shelves[0]!.outer.notchBin, shelves[1]!.outer.notchBin].join(':');
      expect(shelves[0]!.outer.area / shelves[0]!.inner.area, `seed ${spec.seed} upper shelf`).toBeGreaterThan(1.25);
      expect(shelves[1]!.outer.area / shelves[1]!.inner.area, `seed ${spec.seed} lower shelf`).toBeGreaterThan(spec.band === 'far' ? 1.25 : 1.23);
      const range = spec.band === 'near' ? { cut: [.60, .72], shoulder: [.84, .92] } : spec.band === 'mid' ? { cut: [.50, .60], shoulder: [.80, .88] } : { cut: [.38, .48], shoulder: [.74, .84] };
      const ringSize = 8, upperNotch = Math.floor(testSeededUnit(spec.seed, 399) * ringSize), lowerNotch = (upperNotch + 2 + Math.floor(testSeededUnit(spec.seed, 397) * 5)) % ringSize;
      const upperCutDirection = testSeededUnit(spec.seed, 547) > .5 ? 1 : -1, lowerCutDirection = testSeededUnit(spec.seed + 13, 547) > .5 ? 1 : -1;
      const ringDistance = (a: number, b: number) => Math.min((a - b + ringSize) % ringSize, (b - a + ringSize) % ringSize), cutStations = [upperNotch, (upperNotch + upperCutDirection + ringSize) % ringSize, lowerNotch, (lowerNotch + lowerCutDirection + ringSize) % ringSize], overhang = Array.from({ length: ringSize }, (_, step) => step).filter((step) => !cutStations.includes(step)).sort((a, b) => Math.min(...cutStations.map((cut) => ringDistance(b, cut))) - Math.min(...cutStations.map((cut) => ringDistance(a, cut))) || testSeededUnit(spec.seed, b + 571) - testSeededUnit(spec.seed, a + 571))[0]!;
      const angles = Array.from({ length: ringSize }, (_, step) => Math.PI * 2 * step / ringSize + (testSeededUnit(spec.seed, step + 401) - .5) * .13), baseRadius = angles.map((_, step) => .86 + testSeededUnit(spec.seed, step + 419) * .2);
      const direction = spec.seed % 4 === 1 ? 1 : -1, upperX = (testSeededUnit(spec.seed, 449) - .5) * spec.radiusX * .1, upperZ = (testSeededUnit(spec.seed, 457) - .5) * spec.radiusZ * .1, lowerX = upperX - direction * spec.radiusX * (.012 + testSeededUnit(spec.seed, 461) * .013), lowerZ = upperZ + direction * spec.radiusZ * (.008 + testSeededUnit(spec.seed, 463) * .012);
      const upperOuter = .7 + testSeededUnit(spec.seed, 487) * .14, lowerInner = upperOuter + (testSeededUnit(spec.seed, 499) - .5) * .1, lowerOuter = Math.min(1.06, lowerInner + .16 + testSeededUnit(spec.seed, 509) * .1);
      const recoverFactors = (boundary: Vector3[], offsetX: number, offsetZ: number, scale: number) => {
        const matches = angles.map((angle) => boundary.map((point, index) => { const actualAngle = Math.atan2((point.z - spec.z - offsetZ) / spec.radiusZ, (point.x - spec.x - offsetX) / spec.radiusX); return { index, delta: Math.abs(Math.atan2(Math.sin(actualAngle - angle), Math.cos(actualAngle - angle))) }; }).sort((a, b) => a.delta - b.delta)[0]!);
        expect(new Set(matches.map((match) => match.index)).size).toBe(ringSize);
        return matches.map((match, step) => { const point = boundary[match.index]!, x = (point.x - spec.x - offsetX) / spec.radiusX, z = (point.z - spec.z - offsetZ) / spec.radiusZ; return Math.hypot(x, z) / (scale * baseRadius[step]!); });
      };
      const bridgeX = upperX + direction * spec.radiusX * .01, bridgeZ = upperZ - direction * spec.radiusZ * .008;
      const upperFactors = recoverFactors(shelves[0]!.outer.boundary, upperX, upperZ, upperOuter), lowerFactors = recoverFactors(shelves[1]!.outer.boundary, lowerX, lowerZ, lowerOuter), upperScales = recoverFactors(shelves[0]!.outer.boundary, upperX, upperZ, 1), bridgeScales = recoverFactors(shelves[1]!.inner.boundary, bridgeX, bridgeZ, 1);
      const cutFactors = [upperFactors[upperNotch]!, lowerFactors[lowerNotch]!], shoulderFactors = [upperFactors[(upperNotch + upperCutDirection + ringSize) % ringSize]!, lowerFactors[(lowerNotch + lowerCutDirection + ringSize) % ringSize]!];
      const expectedCuts = [range.cut[0] + testSeededUnit(spec.seed, 557) * (range.cut[1] - range.cut[0]), range.cut[0] + testSeededUnit(spec.seed + 17, 557) * (range.cut[1] - range.cut[0])], expectedShoulders = [range.shoulder[0] + testSeededUnit(spec.seed, 563) * (range.shoulder[1] - range.shoulder[0]), range.shoulder[0] + testSeededUnit(spec.seed + 19, 563) * (range.shoulder[1] - range.shoulder[0])];
      for (const [actualFactor, expectedFactor] of [...cutFactors.map((factor, index) => [factor, expectedCuts[index]!] as const), ...shoulderFactors.map((factor, index) => [factor, expectedShoulders[index]!] as const)]) expect(actualFactor).toBeCloseTo(expectedFactor, 5);
      for (const factor of cutFactors) { expect(factor).toBeGreaterThanOrEqual(range.cut[0] - 1e-5); expect(factor).toBeLessThan(range.cut[1] + 1e-5); }
      for (const factor of shoulderFactors) { expect(factor).toBeGreaterThanOrEqual(range.shoulder[0] - 1e-5); expect(factor).toBeLessThan(range.shoulder[1] + 1e-5); }
      const upperRiserKeys = new Set([...shelves[0]!.outer.keys, ...shelves[1]!.inner.keys]), upperRiserFaces = componentTriangles.filter((triangle) => triangle.keys.every((key) => upperRiserKeys.has(key)));
      expect(upperRiserFaces).toHaveLength(16);
      if (spec.band !== 'far') {
        expect(upperFactors[overhang], `seed ${spec.seed} upper overhang`).toBeCloseTo(1.14, 5);
        for (let step = 0; step < ringSize; step += 1) expect(bridgeScales[step]! - upperScales[step]!, `seed ${spec.seed} bridge step ${step}`).toBeCloseTo(.04, 5);
        for (const triangle of upperRiserFaces) { const normalY = triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y; expect(normalY).toBeGreaterThanOrEqual(.045); expect(normalY).toBeLessThan(.55); }
      }
      const crownMean = orderedCrown.reduce((sum, point) => sum + point.y, 0) / orderedCrown.length, visibleRoofMean = visibleOuter.reduce((sum, point) => sum + point.y, 0) / visibleOuter.length, crownProfile = orderedCrown.map((point) => (point.y - crownMean).toFixed(3)).join(':'), visibleCrownProfile = visibleOuter.map((point) => (point.y - visibleRoofMean).toFixed(3)).join(':');
      return { points, center, bounds, profile, crownProfile, visibleCrownProfile, visibleRoofMean, seed: spec.seed, band: spec.band, upperRiserCount: spec.band === 'far' ? 0 : upperRiserFaces.length };
    }).sort((a, b) => b.center.z - a.center.z || a.center.x - b.center.x);
    expect(new Set(actual.map((island) => island.profile)).size).toBe(12); expect(new Set(actual.map((island) => island.seed)).size).toBe(HORIZON_GEOMETRY_CASES.length); expect(actual.reduce((sum, island) => sum + island.upperRiserCount, 0)).toBe(128); for (let island = 1; island < actual.length; island += 1) expect(actual[island]!.profile).not.toBe(actual[island - 1]!.profile);
    expect(Math.min(...actual.map((island) => island.bounds.min.x))).toBeLessThan(-60); expect(Math.max(...actual.map((island) => island.bounds.max.x))).toBeGreaterThan(60);
    const depthGroups = [actual.slice(0, 4), actual.slice(4, 8), actual.slice(8, 12)]; expect(depthGroups.every((group) => group.length === 4)).toBe(true); expect(Math.min(...depthGroups[0]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[1]!.map((island) => island.center.z))); expect(Math.min(...depthGroups[1]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[2]!.map((island) => island.center.z)));
    for (const group of depthGroups) { const intervals = group.map((island) => [island.bounds.min.x, island.bounds.max.x] as const).sort((a, b) => a[0] - b[0]), gaps = intervals.slice(1).map((interval, offset) => interval[0] - intervals[offset]![1]); expect(gaps.filter((gap) => gap > 0).length).toBeGreaterThanOrEqual(2); }
    const viewports = [[1440, 900], [390, 844], [844, 390]] as const, safeRoadHalfWidth = WORLD_METRICS.roadWidth / 2 + .4, trianglesByBand = [0, 1, 2].map((band) => bandTriangles(world, band));
    for (const [band, bandGeometry] of trianglesByBand.entries()) for (const [triangleIndex, triangle] of bandGeometry.entries()) { const side = triangle.reduce((sum, point) => sum + point.x, 0) < 0 ? -1 : 1, inward = side < 0 ? Math.max(...triangle.map((point) => point.x)) : Math.min(...triangle.map((point) => point.x)); expect(side < 0 ? inward < -safeRoadHalfWidth : inward > safeRoadHalfWidth, `band ${band} triangle ${triangleIndex} crosses protected route`).toBe(true); }
    for (const [width, height] of viewports) { const profile = d4ProfileForViewport(width, height), record = TR4_RUNTIME_CAMERA[profile.name], camera = new PerspectiveCamera(record.fov, width / height, .08, 520); camera.position.set(0, record.height, record.back); camera.lookAt(0, record.targetY, -record.targetAhead); camera.updateProjectionMatrix(); applyTR4RuntimeLensShift(camera, profile); camera.updateMatrixWorld();
      for (const island of actual) { const projected = island.points.map((point) => point.clone().project(camera)).filter((point) => point.z >= -1 && point.z <= 1), roadEdge = new Vector3(island.center.x < 0 ? -safeRoadHalfWidth : safeRoadHalfWidth, 0, island.center.z).project(camera).x, closest = island.center.x < 0 ? Math.max(...projected.map((point) => point.x)) : Math.min(...projected.map((point) => point.x)); expect(island.center.x < 0 ? closest < roadEdge - .015 : closest > roadEdge + .015, `${profile.name} island ${island.seed} route clearance`).toBe(true); }
      const measurements = trianglesByBand.map((triangles) => scanlineSilhouette(triangles, camera));
      for (const [band, minimum] of [.16, .10, .055].entries()) for (const side of [0, 1] as const) { const measure = measurements[band]![side]!, label = `${profile.name} band ${band} ${side === 0 ? 'left' : 'right'}`; expect(measure.height, `${label} occupied union height`).toBeGreaterThanOrEqual(minimum); expect(Number.isFinite(measure.maxGap), `${label} must not be empty`).toBe(true); expect(measure.maxGap, `${label} route-edge gap at y=${measure.maxGapY} triangle=${measure.maxGapTriangle}`).toBeLessThanOrEqual(.32); }
    }
    for (const band of depthGroups) { expect(new Set(band.map((island) => island.crownProfile)).size).toBeGreaterThanOrEqual(3); expect(new Set(band.map((island) => island.visibleCrownProfile)).size).toBeGreaterThanOrEqual(3); expect(Math.max(...band.map((island) => island.visibleRoofMean)) - Math.min(...band.map((island) => island.visibleRoofMean))).toBeGreaterThanOrEqual(.50); }
    world.root.traverse((object) => {
      if (!(object instanceof Mesh)) return;
      expect(object.geometry.type).not.toBe('PlaneGeometry');
      expect(object.geometry.type).not.toBe('CylinderGeometry');
      expect(object.type).not.toBe('InstancedMesh');
    });
    for (const forbidden of ['tide-scar-inward-canyon-panorama', 'tide-scar-far-mesa-cards',
      'tide-scar-far-middle-near-mist-bands']) expect(world.root.getObjectByName(forbidden)).toBeUndefined();
    world.dispose();
  });
  it('preserves frozen topology and material treatment while R1H positions replay independently', async () => {
    const first = new TideScarWorld(), second = new TideScarWorld();
    const collectMeshes = (world: TideScarWorld) => { const meshes: Mesh[] = []; world.root.traverse((object) => { if (object instanceof Mesh) meshes.push(object); }); return meshes; };
    const firstMeshes = collectMeshes(first), secondMeshes = collectMeshes(second);
    expect(firstMeshes).toHaveLength(4); expect(secondMeshes).toHaveLength(4);
    const fingerprints = await Promise.all(firstMeshes.map(async (mesh) => { mesh.geometry.computeBoundingBox(); return [mesh.name, await geometryFingerprint(mesh), mesh.geometry.getAttribute('position').count, mesh.geometry.getIndex()!.count, mesh.geometry.boundingBox!.min.toArray(), mesh.geometry.boundingBox!.max.toArray()]; }));
    expect(fingerprints[0]).toEqual(['tide-scar-faceted-abyss-bed', '4f4032aa4676afa4d2b6f92367b309c7e952500b7743df3d0e82db1e7f8c4b52', 90, 432, [-120, -33.034568786621094, -240], [120, -22.416658401489258, 30]]);
    expect(fingerprints.map((entry) => entry.slice(2, 4))).toEqual([[90, 432], [862, 1122], [1152, 1488], [4392, 4656]]);
    expect(fingerprints.slice(1).every((entry) => (entry[4] as number[]).every(Number.isFinite) && (entry[5] as number[]).every(Number.isFinite))).toBe(true);
    const rawPositionFingerprints = await Promise.all(firstMeshes.map((mesh) => rawArrayFingerprint(mesh.geometry.getAttribute('position').array))), indexFingerprints = await Promise.all(firstMeshes.map((mesh) => rawArrayFingerprint(mesh.geometry.getIndex()!.array)));
    expect(rawPositionFingerprints[0]).toBe('7bcce39ce56b41f6a43673cae1aff35e062bacfc0449adeca09a17a2db60b914');
    expect(indexFingerprints).toEqual(['6ab6aabd412f420db9a53fab4659ee2903423794a4e196b21ec8501d362bd0f5', 'e5f9d9a95e17d5bacc311b27824c985da14b83818b0f5feeb31e8dfefd18baf3', 'be62178d76ac81d82175dbee2a715e179701d3f383563f808d02192386e75e2a', '15c61b15613bc21f5aba67e4b5ba4b6c22ebe80f80c40e640b5c480ebb12c402']);
    const hemisphereShifts = { unchanged: new Set<string>(), returns: new Set<string>(), undersides: new Set<string>() }, hemisphereWeightDeltas = { unchanged: [] as number[], returns: [] as number[], undersides: [] as number[] };
    const recordHemisphereShift = (normalY: number, faceLift: number, faceShift: number) => {
      const baseWeight = Math.min(1, Math.max(0, .5 * normalY + .5)), cappedShift = Math.min(.15, faceShift), effectiveWeight = Math.min(1, baseWeight + cappedShift), lift = faceLift.toFixed(5), shift = faceShift.toFixed(5);
      if (lift === '0.00000') { expect(shift).toBe('0.00000'); hemisphereShifts.unchanged.add(shift); hemisphereWeightDeltas.unchanged.push(effectiveWeight - baseWeight); }
      else if (lift === '0.02500') { expect(shift).toBe('0.10000'); hemisphereShifts.returns.add(shift); hemisphereWeightDeltas.returns.push(effectiveWeight - baseWeight); }
      else if (lift === '0.03000') { expect(shift).toBe('0.15000'); hemisphereShifts.undersides.add(shift); hemisphereWeightDeltas.undersides.push(effectiveWeight - baseWeight); }
      else expect.unreachable(`unexpected surface face lift ${lift}`);
      expect(cappedShift).toBeLessThanOrEqual(.15); expect(effectiveWeight).toBeLessThanOrEqual(1);
    };
    for (const [meshIndex, mesh] of firstMeshes.entries()) {
      expect(Array.isArray(mesh.material)).toBe(false); expect(mesh.geometry.groups).toHaveLength(0);
      const replay = secondMeshes[meshIndex]!;
      expect(Array.from(mesh.geometry.getAttribute('position').array)).toEqual(Array.from(replay.geometry.getAttribute('position').array));
      expect(Array.from(mesh.geometry.getIndex()!.array)).toEqual(Array.from(replay.geometry.getIndex()!.array));
      expect(Array.from(mesh.geometry.getAttribute('uv').array)).toEqual(Array.from(replay.geometry.getAttribute('uv').array));
      expect(Array.from(mesh.geometry.getAttribute('color').array)).toEqual(Array.from(replay.geometry.getAttribute('color').array));
      expect(Array.from(mesh.geometry.getAttribute('normal').array)).toEqual(Array.from(replay.geometry.getAttribute('normal').array));
      if (LAYERS.some(([name]) => name === mesh.name)) for (const attributeName of ['surfaceBandStrength', 'surfaceBandFloor', 'surfaceFaceLift', 'surfaceHemisphereShift']) { const attribute = mesh.geometry.getAttribute(attributeName), replayAttribute = replay.geometry.getAttribute(attributeName); expect(attribute.count).toBe(mesh.geometry.getAttribute('position').count); expect(Array.from(attribute.array)).toEqual(Array.from(replayAttribute.array)); }
      const material = mesh.material as MeshStandardMaterial, replayMaterial = replay.material as MeshStandardMaterial;
      expect({ color: material.color.getHex(), emissive: material.emissive.getHex(), emissiveIntensity: material.emissiveIntensity,
        roughness: material.roughness, metalness: material.metalness, vertexColors: material.vertexColors, flatShading: material.flatShading,
        program: material.customProgramCacheKey() }).toEqual({ color: replayMaterial.color.getHex(), emissive: replayMaterial.emissive.getHex(), emissiveIntensity: replayMaterial.emissiveIntensity,
        roughness: replayMaterial.roughness, metalness: replayMaterial.metalness, vertexColors: replayMaterial.vertexColors, flatShading: replayMaterial.flatShading,
        program: replayMaterial.customProgramCacheKey() });
    }
    const programKeys = firstMeshes.filter((mesh) => LAYERS.some(([name]) => name === mesh.name)).map((mesh) => (mesh.material as MeshStandardMaterial).customProgramCacheKey()), replayProgramKeys = secondMeshes.filter((mesh) => LAYERS.some(([name]) => name === mesh.name)).map((mesh) => (mesh.material as MeshStandardMaterial).customProgramCacheKey());
    expect(programKeys).toEqual(['tide-scar-r1e-v5-hemi-shift-0.78-0.1', 'tide-scar-r1e-v5-hemi-shift-0.58-0.14', 'tide-scar-r1e-v5-hemi-shift-0.38-0.18']); expect(programKeys.every((key) => key.includes('r1e-v5-hemi-shift'))).toBe(true);
    expect(new Set(programKeys).size).toBe(3); expect(replayProgramKeys).toEqual(programKeys);
    for (const [name, layer] of LAYERS) {
      const mesh = first.root.getObjectByName(name) as Mesh, meshPosition = mesh.geometry.getAttribute('position'), meshUv = mesh.geometry.getAttribute('uv'), meshIndex = mesh.geometry.getIndex()!;
      const end = layer === 'far' ? meshIndex.count - 12 * 96 * 3 : meshIndex.count, scales: number[] = [], strengths = new Set<string>(), floors = new Set<string>(), faceLifts = { upward: new Set<string>(), vertical: new Set<string>(), underside: new Set<string>() }, faceShifts = { upward: new Set<string>(), vertical: new Set<string>(), underside: new Set<string>() }, coverage = { upward: 0, vertical: 0, underside: 0 }, strengthAttribute = mesh.geometry.getAttribute('surfaceBandStrength'), floorAttribute = mesh.geometry.getAttribute('surfaceBandFloor'), faceLiftAttribute = mesh.geometry.getAttribute('surfaceFaceLift'), hemisphereShiftAttribute = mesh.geometry.getAttribute('surfaceHemisphereShift');
      for (let offset = 0; offset < end; offset += 3) {
        const vertices = [0, 1, 2].map((step) => meshIndex.getX(offset + step)), points = vertices.map((vertex) => new Vector3().fromBufferAttribute(meshPosition, vertex)) as [Vector3, Vector3, Vector3], texture = vertices.map((vertex) => [meshUv.getX(vertex), meshUv.getY(vertex)] as const);
        expect(texture.flat().every(Number.isFinite)).toBe(true);
        for (const vertex of vertices) { const strength = strengthAttribute.getX(vertex), floor = floorAttribute.getX(vertex), faceLift = faceLiftAttribute.getX(vertex), faceShift = hemisphereShiftAttribute.getX(vertex); expect(Number.isFinite(strength) && Number.isFinite(floor) && Number.isFinite(faceLift) && Number.isFinite(faceShift)).toBe(true); strengths.add(strength.toFixed(5)); floors.add(floor.toFixed(5)); }
        const normal = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])), length = normal.length(), uvArea = Math.abs((texture[1]![0] - texture[0]![0]) * (texture[2]![1] - texture[0]![1]) - (texture[1]![1] - texture[0]![1]) * (texture[2]![0] - texture[0]![0])) / 2;
        expect(length).toBeGreaterThan(1e-4); expect(uvArea).toBeGreaterThan(1e-7);
        const normalY = normal.y / length, scale = Math.sqrt(uvArea / (Math.max(Math.abs(normal.x), Math.abs(normal.y), Math.abs(normal.z)) / 2)); scales.push(scale);
        const category = normalY > .55 ? 'upward' : normalY < -.55 ? 'underside' : 'vertical'; coverage[category] += 1; const triangleLifts = new Set(vertices.map((vertex) => faceLiftAttribute.getX(vertex).toFixed(5))), triangleShifts = new Set(vertices.map((vertex) => hemisphereShiftAttribute.getX(vertex).toFixed(5))); expect(triangleLifts.size).toBe(1); expect(triangleShifts.size).toBe(1); faceLifts[category].add([...triangleLifts][0]!); faceShifts[category].add([...triangleShifts][0]!); recordHemisphereShift(normalY, faceLiftAttribute.getX(vertices[0]!), hemisphereShiftAttribute.getX(vertices[0]!));
      }
      expect(Object.values(coverage).every((count) => count > 0)).toBe(true);
      const meanScale = scales.reduce((sum, scale) => sum + scale, 0) / scales.length, range = layer === 'near' ? [.08, .1] : layer === 'mid' ? [.06, .08] : [.045, .06];
      expect(meanScale).toBeGreaterThanOrEqual(range[0]!); expect(meanScale).toBeLessThanOrEqual(range[1]!);
      expect([...strengths]).toEqual([(layer === 'near' ? .78 : layer === 'mid' ? .58 : .38).toFixed(5)]); expect([...floors]).toEqual([(layer === 'near' ? .1 : layer === 'mid' ? .14 : .18).toFixed(5)]);
      expect([...faceLifts.upward]).toEqual(['0.00000']); expect(faceLifts.underside.has('0.03000')).toBe(true); expect([...faceLifts.underside].every((lift) => lift === '0.03000' || lift === '0.02500')).toBe(true); expect(faceLifts.vertical).toEqual(new Set(['0.00000', '0.02500']));
      expect([...faceShifts.upward]).toEqual(['0.00000']); expect(faceShifts.underside.has('0.15000')).toBe(true); expect([...faceShifts.underside].every((shift) => shift === '0.15000' || shift === '0.10000')).toBe(true); expect(faceShifts.vertical).toEqual(new Set(['0.00000', '0.10000']));
    }
    const farMesh = first.root.getObjectByName(LAYERS[2][0]) as Mesh, position = farMesh.geometry.getAttribute('position'), uv = farMesh.geometry.getAttribute('uv'), color = farMesh.geometry.getAttribute('color'), surfaceBand = farMesh.geometry.getAttribute('surfaceBandStrength'), surfaceFloor = farMesh.geometry.getAttribute('surfaceBandFloor'), surfaceFaceLift = farMesh.geometry.getAttribute('surfaceFaceLift'), surfaceHemisphereShift = farMesh.geometry.getAttribute('surfaceHemisphereShift'), index = farMesh.geometry.getIndex()!;
    type Face = { keys: [string, string, string]; value: number; scale: number; normalY: number; strength: number; floor: number; faceLift: number; hemisphereShift: number };
    const horizonStart = index.count - 12 * 96 * 3, keyOf = (point: Vector3) => point.toArray().map((value) => Math.round(value * 1e5)).join(':'), welded = new Map<string, Vector3>(), adjacency = new Map<string, Set<string>>(), faces: Face[] = [];
    for (let offset = horizonStart; offset < index.count; offset += 3) {
      const vertices = [0, 1, 2].map((step) => index.getX(offset + step)), points = vertices.map((vertex) => new Vector3().fromBufferAttribute(position, vertex)) as [Vector3, Vector3, Vector3], keys = points.map(keyOf) as [string, string, string];
      const normal = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])), normalLength = normal.length(); expect(normalLength).toBeGreaterThan(1e-4);
      const texture = vertices.map((vertex) => [uv.getX(vertex), uv.getY(vertex)] as const), uvArea = Math.abs((texture[1]![0] - texture[0]![0]) * (texture[2]![1] - texture[0]![1]) - (texture[1]![1] - texture[0]![1]) * (texture[2]![0] - texture[0]![0])) / 2;
      const projectedArea = Math.max(Math.abs(normal.x), Math.abs(normal.y), Math.abs(normal.z)) / 2, scale = Math.sqrt(uvArea / projectedArea);
      expect(Number.isFinite(scale)).toBe(true); expect(uvArea).toBeGreaterThan(1e-7);
      const value = vertices.map((vertex) => color.getX(vertex) * .2126 + color.getY(vertex) * .7152 + color.getZ(vertex) * .0722).reduce((sum, entry) => sum + entry, 0) / 3;
      const strengths = vertices.map((vertex) => surfaceBand.getX(vertex)), floors = vertices.map((vertex) => surfaceFloor.getX(vertex)), faceLifts = vertices.map((vertex) => surfaceFaceLift.getX(vertex)), hemisphereShifts = vertices.map((vertex) => surfaceHemisphereShift.getX(vertex)); expect(new Set(strengths).size).toBe(1); expect(new Set(floors).size).toBe(1); expect(new Set(faceLifts).size).toBe(1); expect(new Set(hemisphereShifts).size).toBe(1);
      faces.push({ keys, value, scale, normalY: normal.y / normalLength, strength: strengths[0]!, floor: floors[0]!, faceLift: faceLifts[0]!, hemisphereShift: hemisphereShifts[0]! }); recordHemisphereShift(normal.y / normalLength, faceLifts[0]!, hemisphereShifts[0]!);
      for (let step = 0; step < 3; step += 1) { const a = keys[step]!, b = keys[(step + 1) % 3]!; welded.set(a, points[step]!); welded.set(b, points[(step + 1) % 3]!); if (!adjacency.has(a)) adjacency.set(a, new Set()); if (!adjacency.has(b)) adjacency.set(b, new Set()); adjacency.get(a)!.add(b); adjacency.get(b)!.add(a); }
    }
    const pending = new Set(adjacency.keys()), components: Set<string>[] = [];
    while (pending.size > 0) { const component = new Set<string>(), queue = [pending.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!pending.delete(key)) continue; component.add(key); queue.push(...adjacency.get(key)!); } components.push(component); }
    expect(components).toHaveLength(12);
    const actual = components.map((component) => {
      const points = [...component].map((key) => welded.get(key)!), componentFaces = faces.filter((face) => face.keys.every((key) => component.has(key))), capCenters = [...component].filter((key) => adjacency.get(key)!.size === 8).sort((a, b) => welded.get(b)!.y - welded.get(a)!.y), topCenter = capCenters[0]!, bottomCenter = capCenters[1]!;
      expect(capCenters).toHaveLength(2); expect(componentFaces).toHaveLength(96);
      const samples = { top: [] as number[], shelf: [] as number[], vertical: [] as number[], underside: [] as number[] }, minimumSamples = { top: [] as number[], shelf: [] as number[], vertical: [] as number[], underside: [] as number[] }, faceLifts = { top: new Set<string>(), shelf: new Set<string>(), vertical: new Set<string>(), underside: new Set<string>() }, faceShifts = { top: new Set<string>(), shelf: new Set<string>(), vertical: new Set<string>(), underside: new Set<string>() };
      for (const face of componentFaces) { const category = face.normalY > .55 ? face.keys.includes(topCenter) ? 'top' : 'shelf' : face.normalY < -.55 ? 'underside' : 'vertical', semanticFace = face.keys.includes(topCenter) ? 'top' : face.keys.includes(bottomCenter) ? 'underside' : face.normalY > .55 ? 'shelf' : 'vertical'; samples[category].push(face.value); minimumSamples[semanticFace].push(face.value * (face.floor + .16 + face.faceLift)); faceLifts[semanticFace].add(face.faceLift.toFixed(5)); faceShifts[semanticFace].add(face.hemisphereShift.toFixed(5)); }
      for (const values of Object.values(samples)) expect(values.length).toBeGreaterThan(0);
      expect([...faceLifts.top]).toEqual(['0.00000']); expect([...faceLifts.shelf]).toEqual(['0.00000']); expect(faceLifts.vertical).toEqual(new Set(['0.00000', '0.02500'])); expect([...faceLifts.underside]).toEqual(['0.03000']);
      expect([...faceShifts.top]).toEqual(['0.00000']); expect([...faceShifts.shelf]).toEqual(['0.00000']); expect(faceShifts.vertical).toEqual(new Set(['0.00000', '0.10000'])); expect([...faceShifts.underside]).toEqual(['0.15000']);
      const means = Object.fromEntries(Object.entries(samples).map(([kind, values]) => [kind, values.reduce((sum, value) => sum + value, 0) / values.length])) as Record<keyof typeof samples, number>;
      expect(means.top).toBeGreaterThan(means.shelf); expect(means.shelf).toBeGreaterThan(means.vertical); expect(means.vertical).toBeGreaterThan(means.underside);
      const minimumMeans = Object.fromEntries(Object.entries(minimumSamples).map(([kind, values]) => [kind, values.reduce((sum, value) => sum + value, 0) / values.length])) as Record<keyof typeof minimumSamples, number>;
      expect(minimumMeans.top).toBeGreaterThan(minimumMeans.shelf); expect(minimumMeans.shelf).toBeGreaterThan(minimumMeans.vertical); expect(minimumMeans.vertical).toBeGreaterThan(minimumMeans.underside);
      const normalized = Object.entries(samples).flatMap(([kind, values]) => values.map((value) => value / means[kind as keyof typeof samples])), variation = Math.sqrt(normalized.reduce((sum, value) => sum + (value - 1) ** 2, 0) / normalized.length);
      expect(Math.min(...componentFaces.map((face) => face.value))).toBeGreaterThan(.12); expect(Math.max(...componentFaces.map((face) => face.scale)) / Math.min(...componentFaces.map((face) => face.scale))).toBeLessThan(1.001);
      return { centerZ: points.reduce((sum, point) => sum + point.z, 0) / points.length, means, variation, scale: componentFaces.reduce((sum, face) => sum + face.scale, 0) / componentFaces.length, strength: componentFaces[0]!.strength, floor: componentFaces[0]!.floor };
    }).sort((a, b) => b.centerZ - a.centerZ);
    const bands = [actual.slice(0, 4), actual.slice(4, 8), actual.slice(8, 12)].map((band) => ({
      scale: band.reduce((sum, component) => sum + component.scale, 0) / band.length,
      variation: band.reduce((sum, component) => sum + component.variation, 0) / band.length,
      contrast: band.reduce((sum, component) => sum + (component.means.top - component.means.underside) / component.means.shelf, 0) / band.length,
      strength: band.reduce((sum, component) => sum + component.strength, 0) / band.length,
      floor: band.reduce((sum, component) => sum + component.floor, 0) / band.length,
    }));
    expect(bands[0]!.scale).toBeGreaterThan(bands[1]!.scale); expect(bands[1]!.scale).toBeGreaterThan(bands[2]!.scale); expect(bands[0]!.scale / bands[2]!.scale).toBeLessThan(2);
    expect(bands[0]!.scale).toBeGreaterThanOrEqual(.08); expect(bands[0]!.scale).toBeLessThanOrEqual(.1); expect(bands[1]!.scale).toBeGreaterThanOrEqual(.06); expect(bands[1]!.scale).toBeLessThanOrEqual(.08); expect(bands[2]!.scale).toBeGreaterThanOrEqual(.045); expect(bands[2]!.scale).toBeLessThanOrEqual(.06);
    expect(bands[0]!.variation).toBeGreaterThan(bands[1]!.variation); expect(bands[1]!.variation).toBeGreaterThan(bands[2]!.variation);
    expect(bands[0]!.contrast).toBeGreaterThan(bands[1]!.contrast); expect(bands[1]!.contrast).toBeGreaterThan(bands[2]!.contrast); expect(bands[2]!.contrast).toBeGreaterThan(.12);
    expect(bands.map((band) => band.strength)).toEqual([expect.closeTo(.78, 5), expect.closeTo(.58, 5), expect.closeTo(.38, 5)]); expect(bands.map((band) => band.floor)).toEqual([expect.closeTo(.1, 5), expect.closeTo(.14, 5), expect.closeTo(.18, 5)]);
    expect(hemisphereShifts).toEqual({ unchanged: new Set(['0.00000']), returns: new Set(['0.10000']), undersides: new Set(['0.15000']) });
    expect(hemisphereWeightDeltas.unchanged.every((delta) => delta === 0)).toBe(true); expect(Math.min(...hemisphereWeightDeltas.returns)).toBeGreaterThan(0); expect(Math.min(...hemisphereWeightDeltas.undersides)).toBeGreaterThan(0);
    expect(Math.max(...hemisphereWeightDeltas.returns)).toBeLessThanOrEqual(.1 + 1e-7); expect(Math.max(...hemisphereWeightDeltas.undersides)).toBeLessThanOrEqual(.15 + 1e-7);
    first.dispose(); second.dispose();
  });
  it('uses six closed deterministic causeway signatures with connected panels and real asymmetric returns', () => {
    const signatureFingerprints = new Set<string>(); let terminalReference: string | null = null;
    const keyOf = (point: Vector3) => point.toArray().map((value) => Math.round(value * 1e5)).join(':');
    const containsXZ = (points: readonly [Vector3, Vector3, Vector3], x: number, z: number) => {
      const [a, b, c] = points, denominator = (b.z - c.z) * (a.x - c.x) + (c.x - b.x) * (a.z - c.z);
      const u = ((b.z - c.z) * (x - c.x) + (c.x - b.x) * (z - c.z)) / denominator;
      const v = ((c.z - a.z) * (x - c.x) + (a.x - c.x) * (z - c.z)) / denominator;
      return u >= -1e-6 && v >= -1e-6 && u + v <= 1 + 1e-6;
    };
    for (let signature = 0; signature < 6; signature += 1) {
      const geometry = createDeckCapGeometry(signature), replay = createDeckCapGeometry(signature);
      geometry.computeBoundingBox();
      const bounds = geometry.boundingBox!;
      expect(bounds.min.y).toBeLessThan(-2.5);
      expect(bounds.max.x).toBeGreaterThan(0.44);
      expect([bounds.min.z, bounds.max.z]).toEqual([-0.5, 0.5]);
      expect(geometry.type).toBe('BufferGeometry');
      const position = geometry.getAttribute('position'), index = geometry.getIndex()!, normal = geometry.getAttribute('normal'), uv = geometry.getAttribute('uv'), color = geometry.getAttribute('color'), joint = geometry.getAttribute('causewayJoint');
      expect([normal.count, uv.count, color.count, joint.count]).toEqual([position.count, position.count, position.count, position.count]);
      for (const attributeName of ['position', 'normal', 'uv', 'color', 'causewayJoint']) {
        const values = Array.from(geometry.getAttribute(attributeName).array), replayValues = Array.from(replay.getAttribute(attributeName).array);
        expect(values.every(Number.isFinite)).toBe(true); expect(values).toEqual(replayValues);
      }
      expect(Array.from(index.array)).toEqual(Array.from(replay.getIndex()!.array));
      for (let vertex = 0; vertex < normal.count; vertex += 1) expect(new Vector3().fromBufferAttribute(normal, vertex).length()).toBeCloseTo(1, 5);
      const edgeUse = new Map<string, number>(), sideNormals: [number[], number[]] = [[], []], capFaces = [0, 0],
        topFaces: { points: [Vector3, Vector3, Vector3]; keys: [string, string, string]; joints: [number, number, number]; plane: string }[] = [], luminance = { top: [] as number[], worn: [] as number[], return: [] as number[] };
      for (let offset = 0; offset < index.count; offset += 3) {
        const vertices = [index.getX(offset), index.getX(offset + 1), index.getX(offset + 2)];
        expect(vertices.every((vertex) => vertex >= 0 && vertex < position.count)).toBe(true);
        const points = vertices.map((vertex) => new Vector3().fromBufferAttribute(position, vertex)) as [Vector3, Vector3, Vector3], keys = points.map(keyOf) as [string, string, string],
          xs = points.map((point) => point.x), ys = points.map((point) => point.y), zs = points.map((point) => point.z), faceNormal = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])), faceLength = faceNormal.length(),
          worldPoints = points.map((point) => new Vector3(point.x * WORLD_METRICS.roadWidth, point.y, point.z * 6)) as [Vector3, Vector3, Vector3],
          worldFaceNormal = worldPoints[1].clone().sub(worldPoints[0]).cross(worldPoints[2].clone().sub(worldPoints[0])), worldNormalY = worldFaceNormal.y / worldFaceNormal.length();
        expect(faceLength).toBeGreaterThan(1e-7);
        const texture = vertices.map((vertex) => [uv.getX(vertex), uv.getY(vertex)] as const), uvArea = Math.abs((texture[1]![0] - texture[0]![0]) * (texture[2]![1] - texture[0]![1]) - (texture[1]![1] - texture[0]![1]) * (texture[2]![0] - texture[0]![0])) / 2;
        expect(uvArea).toBeGreaterThan(1e-8);
        for (const [from, to] of [[0, 1], [1, 2], [2, 0]] as const) { const edge = [keys[from], keys[to]].sort().join('|'); edgeUse.set(edge, (edgeUse.get(edge) ?? 0) + 1); }
        if (zs.every((z) => z === -.5)) capFaces[0]! += 1; if (zs.every((z) => z === .5)) capFaces[1]! += 1;
        if (zs.every((z) => z === -.5)) expect(faceNormal.z).toBeLessThan(-1e-7); if (zs.every((z) => z === .5)) expect(faceNormal.z).toBeGreaterThan(1e-7);
        const side = xs.every((x) => x < -.44) ? 0 : xs.every((x) => x > .44) ? 1 : -1;
        if (side >= 0 && Math.max(...zs) > Math.min(...zs) && Math.abs(faceNormal.x) > 1e-7) sideNormals[side as 0 | 1].push(faceNormal.x);
        const normalY = worldNormalY, value = vertices.map((vertex) => color.getX(vertex) * .2126 + color.getY(vertex) * .7152 + color.getZ(vertex) * .0722).reduce((sum, entry) => sum + entry, 0) / 3,
          centroidY = ys.reduce((sum, value) => sum + value, 0) / 3;
        if (normalY > .55 && centroidY > -.1) {
          const unit = worldFaceNormal.normalize(), plane = unit.dot(worldPoints[0]);
          topFaces.push({ points, keys, joints: vertices.map((vertex) => joint.getX(vertex)) as [number, number, number], plane: [unit.x, unit.y, unit.z, plane].map((value) => Math.round(value * 200)).join(':') }); luminance.top.push(value);
        } else if (centroidY > -.65) luminance.worn.push(value); else luminance.return.push(value);
      }
      const openEdges = [...edgeUse.entries()].filter(([, count]) => count !== 2);
      expect(openEdges, `signature ${signature} non-manifold edges ${JSON.stringify(openEdges.slice(0, 12))}`).toEqual([]);
      expect(Math.max(...sideNormals[0])).toBeLessThan(0); expect(Math.min(...sideNormals[1])).toBeGreaterThan(0);
      expect(capFaces.every((count) => count > 4)).toBe(true);
      const terminalSection = (z: number) => [...new Set(Array.from({ length: position.count }, (_, vertex) => Math.abs(position.getZ(vertex) - z) < 1e-6 ? `${position.getX(vertex).toFixed(5)}:${position.getY(vertex).toFixed(5)}` : '').filter(Boolean))].sort();
      expect(terminalSection(-.5)).toEqual(terminalSection(.5)); const terminal = terminalSection(-.5).join('|'); if (terminalReference === null) terminalReference = terminal; else expect(terminal).toBe(terminalReference);
      expect(Array.from({ length: 4 }, (_, vertex) => [position.getX(vertex), position.getY(vertex), position.getZ(vertex)].map((value) => Number(value.toFixed(3))))).toEqual([[-.462, -.012, -.5], [.462, -.012, -.5], [-.462, -.012, .5], [.462, -.012, .5]]);
      const topKeys = new Set(topFaces.flatMap((face) => face.keys)), adjacency = new Map<string, Set<string>>();
      for (const key of topKeys) adjacency.set(key, new Set());
      for (const face of topFaces) for (const [from, to] of [[0, 1], [1, 2], [2, 0]] as const) { adjacency.get(face.keys[from])!.add(face.keys[to]); adjacency.get(face.keys[to])!.add(face.keys[from]); }
      const pending = new Set(topKeys); let components = 0; while (pending.size > 0) { components += 1; const queue = [pending.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!pending.delete(key)) continue; queue.push(...adjacency.get(key)!); } }
      expect(components).toBe(1);
      for (let zStep = 0; zStep <= 24; zStep += 1) for (let xStep = 0; xStep <= 16; xStep += 1) {
        const x = -.43 + xStep * .86 / 16, z = -.49 + zStep * .98 / 24;
        expect(topFaces.some((face) => containsXZ(face.points, x, z)), `signature ${signature} protected point ${x},${z}`).toBe(true);
      }
      const planes = new Set(topFaces.filter((face) => {
        const xs = face.points.map((point) => point.x), zs = face.points.map((point) => point.z);
        return Math.max(...xs) - Math.min(...xs) >= .14 && Math.max(...zs) - Math.min(...zs) >= .14;
      }).map((face) => face.plane));
      expect(planes.size).toBeGreaterThanOrEqual(6); signatureFingerprints.add([...planes].sort().join('|'));
      const jointEdges = new Map<string, [Vector3, Vector3]>();
      for (const face of topFaces) for (const [from, to] of [[0, 1], [1, 2], [2, 0]] as const) if (face.joints[from] > .99 && face.joints[to] > .99) {
        const edge = [face.points[from], face.points[to]] as [Vector3, Vector3], absX = edge.map((point) => Math.abs(point.x)), dz = Math.abs(edge[0].z - edge[1].z);
        if (Math.max(...absX) > .4 && Math.min(...absX) < .12 && dz > .01 && dz < .06) jointEdges.set(edge.map(keyOf).sort().join('|'), edge);
      }
      expect(jointEdges.size).toBe(3);
      for (const edge of jointEdges.values()) expect(Math.abs(edge[0].x - edge[1].x)).toBeLessThan(.56);
      const profileFingerprint = (side: -1 | 1) => {
        const groups = new Map<string, Vector3[]>();
        for (let vertex = 0; vertex < position.count; vertex += 1) { const point = new Vector3().fromBufferAttribute(position, vertex); if (side * point.x <= .44 || Math.abs(Math.abs(point.z) - .5) < 1e-5) continue; const key = point.z.toFixed(5); if (!groups.has(key)) groups.set(key, []); groups.get(key)!.push(point); }
        const profiles = [...groups.values()].map((points) => [...new Map(points.map((point) => [`${point.x.toFixed(5)}:${point.y.toFixed(5)}`, point])).values()].sort((a, b) => b.y - a.y)).filter((points) => points.length >= 8);
        expect(profiles.length).toBeGreaterThan(0); const profile = profiles[Math.floor(profiles.length / 2)]!, topX = profile[0]!.x, outward = profile.map((point) => side * (point.x - topX)), maximum = Math.max(...outward), maximumIndex = outward.indexOf(maximum);
        expect(maximumIndex).toBeLessThan(outward.length - 1); expect(maximum - Math.min(...outward.slice(maximumIndex + 1))).toBeGreaterThan(.025);
        return outward.map((value) => value.toFixed(4)).join(':');
      };
      expect(profileFingerprint(-1)).not.toBe(profileFingerprint(1));
      const mean = (values: number[]) => values.reduce((sum, value) => sum + value, 0) / values.length;
      expect(Math.min(luminance.top.length, luminance.worn.length, luminance.return.length)).toBeGreaterThan(0);
      expect(mean(luminance.top) - mean(luminance.worn)).toBeGreaterThan(.035); expect(mean(luminance.worn) - mean(luminance.return)).toBeGreaterThan(.035);
      geometry.dispose(); replay.dispose();
    }
    expect(signatureFingerprints.size).toBeGreaterThanOrEqual(3);
    expect([presentationRoadStart(0), presentationRoadStart(1)]).toEqual([-18, 0]);
  });
  it('uses a zero-emissive world-anchored two-scale causeway material without owning its sandstone map', () => {
    const material = createCausewayMaterial(), shader: { vertexShader: string; fragmentShader: string } = {
      vertexShader: '#include <worldpos_vertex>', fragmentShader: '#include <map_fragment>\n#include <roughnessmap_fragment>',
    };
    material.onBeforeCompile(shader as never, {} as never);
    expect({ color: material.color.getHex(), emissive: material.emissive.getHex(), emissiveIntensity: material.emissiveIntensity, vertexColors: material.vertexColors })
      .toEqual({ color: 0xffffff, emissive: 0, emissiveIntensity: 0, vertexColors: true });
    expect(material.customProgramCacheKey()).toContain('causeway-triplanar'); expect(shader.vertexShader).toContain('tideWorldPosition = worldPosition.xyz');
    for (const token of ['tideCausewaySample', 'worldPoint.zy', 'worldPoint.xz', 'worldPoint.xy', '3.200', '0.850', 'tideCausewayTop', 'tideCausewayJointWear', 'roughnessFactor = clamp']) expect(shader.fragmentShader).toContain(token);
    expect(shader.vertexShader).toContain('tideCausewayJoint = causewayJoint');
    expect(shader.fragmentShader).not.toContain('#include <map_fragment>');
    const texture = new Texture(); let textureDisposals = 0; texture.addEventListener('dispose', () => { textureDisposals += 1; }); material.map = texture; material.map = null; material.dispose(); expect(textureDisposals).toBe(0);
    const renderer = new WorldRenderer() as unknown as { causewayMaterial: MeshStandardMaterial; destroy(): void };
    renderer.causewayMaterial.map = texture; renderer.destroy(); expect(renderer.causewayMaterial.map).toBeNull(); expect(textureDisposals).toBe(0); texture.dispose();
  });
  it('shows the pursuer only for ready, the bounded opening, and every game-over state', () => {
    expect([shouldShowPursuer('ready', 999, 999), shouldShowPursuer('running', 53, 5.99), shouldShowPursuer('game-over', 999, 999)]).toEqual([true, true, true]);
    expect([shouldShowPursuer('running', 54, 5.99), shouldShowPursuer('running', 53, 6), shouldShowPursuer('paused', 0, 0)]).toEqual([false, false, false]);
  });
  it('binds the exact yaw-relative TR4 cameras and lens shifts for each viewport profile', () => {
    const viewports = [[390, 844], [1440, 900], [844, 390]] as const;
    for (const [width, height] of viewports) {
      const profile = d4ProfileForViewport(width, height);
      const record = TR4_RUNTIME_CAMERA[profile.name];
      const camera = new PerspectiveCamera(record.fov, width / height, 0.08, 520);
      camera.position.set(0, record.height, record.back);
      camera.lookAt(0, record.targetY, -record.targetAhead);
      camera.updateProjectionMatrix();
      applyTR4RuntimeLensShift(camera, profile);
      expect({ fov: camera.fov, lens: camera.projectionMatrix.elements[9], position: camera.position.toArray() })
        .toEqual({ fov: record.fov, lens: record.lensShiftY, position: [0, record.height, record.back] });
    }
    expect(TR4_RUNTIME_CAMERA.portrait).toEqual({ height: 8.4, back: 22, targetAhead: 21, targetY: .7, fov: 46, lensShiftY: -.04 });
    const projectionScale = (record: { height: number; back: number; targetAhead: number; targetY: number; fov: number }) => {
      const camera = new PerspectiveCamera(record.fov, 390 / 844, .08, 520); camera.position.set(0, record.height, record.back); camera.lookAt(0, record.targetY, -record.targetAhead); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
      const project = (point: Vector3) => point.project(camera), left = project(new Vector3(-3, 0, 0)), right = project(new Vector3(3, 0, 0)), feet = project(new Vector3(0, 0, 0)), head = project(new Vector3(0, 2, 0));
      return { road: Math.abs(right.x - left.x) * 195, runner: Math.abs(head.y - feet.y) * 422 };
    };
    const old = { height: 6.2, back: 15.2, targetAhead: 16.8, targetY: .55, fov: 40 }, next = projectionScale(TR4_RUNTIME_CAMERA.portrait), previous = projectionScale(old);
    expect(next.road / previous.road).toBeGreaterThan(.55); expect(next.road / previous.road).toBeLessThan(.7);
    expect(next.runner / previous.runner).toBeGreaterThan(.55); expect(next.runner / previous.runner).toBeLessThan(.7);
    expect(Math.atan2(8.4 - .7, 22 + 21)).toBeCloseTo(Math.atan2(6.2 - .55, 15.2 + 16.8), 2);
  });
  it('replays identical geometry and holds a quantized world cell across all three profiles', () => {
    const first = new TideScarWorld();
    const second = new TideScarWorld();
    for (const [name] of LAYERS) {
      const firstMesh = first.root.getObjectByName(name) as Mesh;
      const secondMesh = second.root.getObjectByName(name) as Mesh;
      expect(Array.from(firstMesh.geometry.getAttribute('position').array))
        .toEqual(Array.from(secondMesh.geometry.getAttribute('position').array));
    }
    for (const profile of ['desktop', 'portrait', 'landscape'] as const) {
      first.update(new Vector3(47.9, 7, -47.9), Math.PI / 2, profile);
      expect(first.root.position.toArray()).toEqual([0, 0, 0]);
      expect(first.root.rotation.y).toBeCloseTo(Math.PI / 2, 10);
      const worldForward = new Vector3(0, 0, -1).applyQuaternion(first.root.quaternion);
      expect(worldForward.x).toBeCloseTo(-1, 10);
      expect(worldForward.z).toBeCloseTo(0, 10);
    }
    first.update(new Vector3(48.1, -3, -48.1), 0, 'desktop');
    expect(first.root.position.toArray()).toEqual([96, 0, -96]);
    first.dispose();
    second.dispose();
  });
  it('binds and clears one non-owning basalt map across all canyon bands, then releases only owned resources', () => {
    const world = new TideScarWorld();
    const texture = new Texture();
    let textureDisposals = 0; let geometryDisposals = 0; let materialDisposals = 0;
    texture.addEventListener('dispose', () => { textureDisposals += 1; });
    world.setPanorama(texture);
    expect(world.hasPanorama).toBe(false);
    for (const [name] of LAYERS) expect(((world.root.getObjectByName(name) as Mesh).material as MeshStandardMaterial).map).toBeNull();
    world.setSurfaceMap(texture);
    const remaps: { strength: number; floor: number }[] = [], roughnesses: number[] = [];
    world.root.traverse((object) => {
      if (!(object instanceof Mesh)) return;
      object.geometry.addEventListener('dispose', () => { geometryDisposals += 1; });
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        const surface = material as MeshStandardMaterial, isCanyonBand = LAYERS.some(([name]) => name === object.name);
        expect(surface.map).toBe(isCanyonBand ? texture : null);
        if (isCanyonBand) {
          const shader: { uniforms: Record<string, { value: number }>; vertexShader: string; fragmentShader: string } = { uniforms: {}, vertexShader: '#include <begin_vertex>', fragmentShader: '#include <map_fragment>\n#include <lights_fragment_begin>\n#include <lights_fragment_maps>\n#include <lights_fragment_end>\n#include <aomap_fragment>' };
          surface.onBeforeCompile(shader as never, {} as never);
          expect(surface.color.getHex()).toBe(0xffffff); expect(surface.vertexColors).toBe(true); expect(surface.emissive.getHex()).toBe(0); expect(surface.emissiveIntensity).toBe(0);
          expect(shader.vertexShader).toContain('attribute float surfaceBandStrength'); expect(shader.vertexShader).toContain('attribute float surfaceFaceLift'); expect(shader.vertexShader).toContain('attribute float surfaceHemisphereShift'); expect(shader.vertexShader).toContain('vCanyonFaceLift = surfaceFaceLift'); expect(shader.vertexShader).toContain('vCanyonHemisphereShift = surfaceHemisphereShift'); expect(shader.vertexShader).toContain('vCanyonObjectPosition = position');
          expect(shader.fragmentShader).toContain('texture2D( map, vMapUv * 1.65 )'); expect(shader.fragmentShader).toContain('microValue - 0.039'); expect(shader.fragmentShader).toContain('max(vCanyonBandStrength, canyonMapStrength)'); expect(shader.fragmentShader).toContain('min(vCanyonBandFloor, canyonMapFloor)'); expect(shader.fragmentShader).toContain('faceMinimum = bandFloor + 0.16 + vCanyonFaceLift'); expect(shader.fragmentShader).toContain('textureDetail + worldDetail'); expect(shader.fragmentShader).toContain('diffuseColor *= sampledDiffuseColor'); expect(shader.fragmentShader).not.toContain('#include <map_fragment>');
          const lightBegin = shader.fragmentShader.indexOf('#include <lights_fragment_begin>'), hemiGuard = shader.fragmentShader.indexOf('#if defined(RE_IndirectDiffuse) && (NUM_HEMI_LIGHTS > 0)'), lightMaps = shader.fragmentShader.indexOf('#include <lights_fragment_maps>'), lightEnd = shader.fragmentShader.indexOf('#include <lights_fragment_end>'), ao = shader.fragmentShader.indexOf('#include <aomap_fragment>');
          expect(shader.fragmentShader.slice(lightBegin, hemiGuard)).toBe('#include <lights_fragment_begin>\n'); expect(lightBegin).toBeGreaterThan(-1); expect(hemiGuard).toBeGreaterThan(lightBegin); expect(lightMaps).toBeGreaterThan(hemiGuard); expect(lightEnd).toBeGreaterThan(lightMaps); expect(ao).toBeGreaterThan(lightEnd);
          const guardedDelta = shader.fragmentShader.slice(hemiGuard, lightMaps);
          expect(guardedDelta).toContain('canyonHemisphereShift = min(0.15, vCanyonHemisphereShift)'); expect(guardedDelta).toContain('canyonBaseWeight = saturate(0.5 * dot(geometryNormal, hemisphereLights[i].direction) + 0.5)'); expect(guardedDelta).toContain('canyonEffectiveWeight = min(1.0, canyonBaseWeight + canyonHemisphereShift)'); expect(guardedDelta).toContain('mix(hemisphereLights[i].groundColor, hemisphereLights[i].skyColor, canyonBaseWeight)'); expect(guardedDelta).toContain('mix(hemisphereLights[i].groundColor, hemisphereLights[i].skyColor, canyonEffectiveWeight)'); expect(guardedDelta).toContain('irradiance += canyonEffectiveIrradiance - canyonBaseIrradiance'); expect(guardedDelta.match(/irradiance \+=/g)).toHaveLength(1);
          expect(guardedDelta).not.toContain('canyonWeightFloor'); expect(guardedDelta).not.toContain('canyonLiftedWeight'); expect(guardedDelta).not.toContain('0.135');
          for (const assignment of [/\bnormal\s*(?:\+|-|\*|\/)?=/, /\bgeometryNormal\s*(?:\+|-|\*|\/)?=/, /\bdirectLight\s*(?:\+|-|\*|\/)?=/, /reflectedLight\.directDiffuse\s*(?:\+|-|\*|\/)?=/, /reflectedLight\.directSpecular\s*(?:\+|-|\*|\/)?=/, /reflectedLight\.indirectSpecular\s*(?:\+|-|\*|\/)?=/, /\bshadow\w*\s*(?:\+|-|\*|\/)?=/i, /\bdiffuseColor\s*(?:\+|-|\*|\/)?=/, /\boutgoingLight\s*(?:\+|-|\*|\/)?=/, /\btotalEmissiveRadiance\s*(?:\+|-|\*|\/)?=/, /\bemissive\w*\s*(?:\+|-|\*|\/)?=/i, /\btoneMappingExposure\s*(?:\+|-|\*|\/)?=/, /\bgl_FragColor\s*(?:\+|-|\*|\/)?=/]) expect(guardedDelta).not.toMatch(assignment);
          remaps.push({ strength: shader.uniforms.canyonMapStrength!.value, floor: shader.uniforms.canyonMapFloor!.value }); roughnesses.push(surface.roughness);
        }
        material.addEventListener('dispose', () => { materialDisposals += 1; });
      }
    });
    expect(remaps).toEqual([{ strength: .78, floor: .1 }, { strength: .58, floor: .14 }, { strength: .38, floor: .18 }]);
    expect(roughnesses.every((roughness) => roughness >= .64 && roughness <= .9)).toBe(true);
    for (let band = 1; band < remaps.length; band += 1) { expect(remaps[band - 1]!.strength - remaps[band]!.strength).toBeGreaterThanOrEqual(.15); expect(remaps[band]!.floor - remaps[band - 1]!.floor).toBeGreaterThanOrEqual(.03); }
    expect(Math.max(...remaps.map((remap) => remap.floor))).toBeLessThanOrEqual(.25);
    world.setSurfaceMap(null);
    for (const [name] of LAYERS) expect(((world.root.getObjectByName(name) as Mesh).material as MeshStandardMaterial).map).toBeNull();
    world.setSurfaceMap(texture);
    world.dispose();
    world.dispose();
    expect(geometryDisposals).toBe(4);
    expect(materialDisposals).toBe(4);
    expect(textureDisposals).toBe(0);
    texture.dispose();
  });
});
