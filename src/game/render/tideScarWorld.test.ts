import { Mesh, MeshStandardMaterial, PerspectiveCamera, Texture, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import { TideScarWorld } from './tideScarWorld';
import { applyTR4RuntimeLensShift, createDeckCapGeometry, presentationRoadStart, shouldShowPursuer, TR4_RUNTIME_CAMERA } from './WorldRenderer';
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
  { x: -52, z: -54, radiusX: 13, radiusZ: 18, seed: 401, band: 'near' }, { x: -15, z: -62, radiusX: 8, radiusZ: 16, seed: 409, band: 'near' },
  { x: 15, z: -55, radiusX: 8, radiusZ: 17, seed: 419, band: 'near' }, { x: 52, z: -61, radiusX: 13, radiusZ: 20, seed: 421, band: 'near' },
  { x: -42, z: -84, radiusX: 12, radiusZ: 18, seed: 431, band: 'mid' }, { x: -16, z: -91, radiusX: 7, radiusZ: 15, seed: 433, band: 'mid' },
  { x: 16, z: -86, radiusX: 7, radiusZ: 16, seed: 439, band: 'mid' }, { x: 42, z: -94, radiusX: 12, radiusZ: 18, seed: 443, band: 'mid' },
  { x: -34, z: -122, radiusX: 11, radiusZ: 17, seed: 449, band: 'far' }, { x: -12, z: -130, radiusX: 5, radiusZ: 14, seed: 457, band: 'far' },
  { x: 12, z: -124, radiusX: 5, radiusZ: 15, seed: 461, band: 'far' }, { x: 34, z: -132, radiusX: 11, radiusZ: 17, seed: 463, band: 'far' },
] as const;
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
    const farMesh = world.root.getObjectByName(LAYERS[2][0]) as Mesh, farBounds = farMesh.geometry.boundingBox!;
    expect(farBounds.max.z).toBeLessThan(-25);
    expect(farBounds.min.z).toBeGreaterThan(-230);
    const position = farMesh.geometry.getAttribute('position'), index = farMesh.geometry.getIndex()!, horizonStart = farMesh.geometry.userData.horizonIndexStart as number;
    const welded = new Map<string, Vector3>(), adjacency = new Map<string, Set<string>>();
    type ActualTriangle = { keys: [string, string, string]; points: [Vector3, Vector3, Vector3] };
    const triangles: ActualTriangle[] = [], keyOf = (point: Vector3) => point.toArray().map((value) => Math.round(value * 1e5)).join(':');
    for (let offset = horizonStart; offset < index.count; offset += 3) {
      const points = [0, 1, 2].map((step) => new Vector3().fromBufferAttribute(position, index.getX(offset + step))) as [Vector3, Vector3, Vector3], keys = points.map(keyOf) as [string, string, string]; triangles.push({ keys, points });
      for (let step = 0; step < 3; step += 1) { const a = keys[step]!, b = keys[(step + 1) % 3]!; welded.set(a, points[step]!); welded.set(b, points[(step + 1) % 3]!); if (!adjacency.has(a)) adjacency.set(a, new Set()); if (!adjacency.has(b)) adjacency.set(b, new Set()); adjacency.get(a)!.add(b); adjacency.get(b)!.add(a); }
    }
    const remaining = new Set(adjacency.keys()), components: Set<string>[] = [];
    while (remaining.size > 0) { const component = new Set<string>(), queue = [remaining.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!remaining.delete(key)) continue; component.add(key); queue.push(...adjacency.get(key)!); } components.push(component); }
    expect(components).toHaveLength(12);
    const actual = components.map((component) => {
      const points = [...component].map((key) => welded.get(key)!), center = points.reduce((sum, point) => sum.add(point), new Vector3()).multiplyScalar(1 / points.length), componentTriangles = triangles.filter((triangle) => triangle.keys.every((key) => component.has(key))), edgeUse = new Map<string, number>();
      const bounds = { min: new Vector3(...(['x', 'y', 'z'] as const).map((axis) => Math.min(...points.map((point) => point[axis]))) as [number, number, number]), max: new Vector3(...(['x', 'y', 'z'] as const).map((axis) => Math.max(...points.map((point) => point[axis]))) as [number, number, number]) };
      expect(points).toHaveLength(50); expect(componentTriangles).toHaveLength(96);
      for (const triangle of componentTriangles) { const [a, b, c] = triangle.points, normal = b.clone().sub(a).cross(c.clone().sub(a)); expect(normal.length()).toBeGreaterThan(1e-4); for (const [u, v] of [[0, 1], [1, 2], [2, 0]] as const) { const edge = [triangle.keys[u], triangle.keys[v]].sort().join('|'); edgeUse.set(edge, (edgeUse.get(edge) ?? 0) + 1); } }
      expect([...edgeUse.values()].every((count) => count === 2)).toBe(true);
      const elevationBands: Vector3[][] = []; for (const point of [...points].sort((a, b) => a.y - b.y)) { const band = elevationBands.at(-1); if (!band || point.y - Math.max(...band.map((member) => member.y)) > .8) elevationBands.push([point]); else band.push(point); }
      expect(elevationBands.map((band) => band.length)).toEqual([9, 8, 16, 17]); for (let band = 1; band < elevationBands.length; band += 1) expect(Math.min(...elevationBands[band]!.map((point) => point.y)) - Math.max(...elevationBands[band - 1]!.map((point) => point.y))).toBeGreaterThan(.8);
      const capKeys = new Set([...component].filter((key) => adjacency.get(key)!.size === 8)); expect(capKeys.size).toBe(2); const capFaces = componentTriangles.filter((triangle) => triangle.keys.some((key) => capKeys.has(key))); expect(capFaces).toHaveLength(16); for (const triangle of capFaces) { const cap = triangle.keys.find((key) => capKeys.has(key))!, normal = triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])); expect(normal.y * (welded.get(cap)!.y > center.y ? 1 : -1)).toBeGreaterThan(1e-4); }
      type RingPlan = { keys: Set<string>; boundary: Vector3[]; center: Vector3; extentX: number; extentZ: number; area: number; meanY: number; radialBreak: number; notchBin: number };
      const ringPlan = (keys: Set<string>): RingPlan => { const boundary = [...keys].map((key) => welded.get(key)!), planCenter = boundary.reduce((sum, point) => sum.add(new Vector3(point.x, 0, point.z)), new Vector3()).multiplyScalar(1 / boundary.length), ordered = boundary.sort((a, b) => Math.atan2(a.z - planCenter.z, a.x - planCenter.x) - Math.atan2(b.z - planCenter.z, b.x - planCenter.x)), extentX = Math.max(...ordered.map((point) => point.x)) - Math.min(...ordered.map((point) => point.x)), extentZ = Math.max(...ordered.map((point) => point.z)) - Math.min(...ordered.map((point) => point.z)), radii = ordered.map((point) => Math.hypot((point.x - planCenter.x) / extentX, (point.z - planCenter.z) / extentZ)), notchStep = radii.indexOf(Math.min(...radii)), notchAngle = Math.atan2(ordered[notchStep]!.z - planCenter.z, ordered[notchStep]!.x - planCenter.x), area = Math.abs(ordered.reduce((sum, point, step) => sum + point.x * ordered[(step + 1) % ordered.length]!.z - ordered[(step + 1) % ordered.length]!.x * point.z, 0)) / 2; expect(ordered).toHaveLength(8); for (const [step, point] of ordered.entries()) { const linked = [...adjacency.get(keyOf(point))!].filter((key) => keys.has(key)).sort(), expected = [keyOf(ordered[(step + 7) % 8]!), keyOf(ordered[(step + 1) % 8]!)].sort(); expect(linked).toEqual(expected); } return { keys, boundary: ordered, center: planCenter, extentX, extentZ, area, meanY: ordered.reduce((sum, point) => sum + point.y, 0) / ordered.length, radialBreak: Math.max(...radii) - Math.min(...radii), notchBin: (Math.round((notchAngle + Math.PI) / (Math.PI / 4)) + 8) % 8 }; };
      const shelfTriangles = componentTriangles.filter((triangle) => !triangle.keys.some((key) => capKeys.has(key)) && Math.max(...triangle.points.map((point) => point.y)) - Math.min(...triangle.points.map((point) => point.y)) < .65).sort((a, b) => a.points.reduce((sum, point) => sum + point.y, 0) - b.points.reduce((sum, point) => sum + point.y, 0)); expect(shelfTriangles).toHaveLength(32);
      const shelfGroups: ActualTriangle[][] = []; for (const triangle of shelfTriangles) { const y = triangle.points.reduce((sum, point) => sum + point.y, 0) / 3, group = shelfGroups.at(-1), groupY = group?.[0]!.points.reduce((sum, point) => sum + point.y, 0)! / 3; if (!group || y - groupY > .8) shelfGroups.push([triangle]); else group.push(triangle); } expect(shelfGroups.map((group) => group.length)).toEqual([16, 16]);
      const shelves = shelfGroups.map((group, shelfIndex) => { const upward = group.map((triangle) => triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y); expect(Math.min(...upward)).toBeGreaterThan(.55); const uses = new Map<string, { count: number; ends: [string, string] }>(); for (const triangle of group) for (const [u, v] of [[0, 1], [1, 2], [2, 0]] as const) { const ends = [triangle.keys[u], triangle.keys[v]].sort() as [string, string], edge = ends.join('|'), previous = uses.get(edge); uses.set(edge, { count: (previous?.count ?? 0) + 1, ends }); } const boundaryAdjacency = new Map<string, Set<string>>(); for (const { count, ends } of uses.values()) if (count === 1) { for (const [from, to] of [ends, [ends[1], ends[0]]] as [string, string][]) { if (!boundaryAdjacency.has(from)) boundaryAdjacency.set(from, new Set()); boundaryAdjacency.get(from)!.add(to); } } expect([...boundaryAdjacency.values()].every((links) => links.size === 2)).toBe(true); const ringKeys: Set<string>[] = [], pending = new Set(boundaryAdjacency.keys()); while (pending.size > 0) { const keys = new Set<string>(), queue = [pending.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!pending.delete(key)) continue; keys.add(key); queue.push(...boundaryAdjacency.get(key)!); } ringKeys.push(keys); } expect(ringKeys.map((keys) => keys.size)).toEqual([8, 8]); const plans = ringKeys.map(ringPlan).sort((a, b) => a.area - b.area), [inner, outer] = plans; expect(outer!.area / inner!.area, `component ${center.x.toFixed(2)},${center.z.toFixed(2)} shelf ${shelfIndex}`).toBeGreaterThan(1.23); expect(Math.abs(outer!.meanY - inner!.meanY)).toBeLessThan(.05); expect(outer!.center.distanceTo(inner!.center)).toBeGreaterThan(.03); expect(outer!.radialBreak).toBeGreaterThan(.1); return { inner: inner!, outer: outer! }; }).sort((a, b) => b.outer.meanY - a.outer.meanY);
      const deepBand = elevationBands.find((band) => band.length === 8)!, deepRing = ringPlan(new Set(deepBand.map(keyOf))), bottomRing = ringPlan(new Set(elevationBands[0]!.map(keyOf).filter((key) => !capKeys.has(key))));
      const xzRadius = (point: Vector3, plan: RingPlan) => Math.hypot(point.x - plan.center.x, point.z - plan.center.z);
      const spec = [...HORIZON_GEOMETRY_CASES].sort((a, b) => Math.hypot(center.x - a.x, center.z - a.z) - Math.hypot(center.x - b.x, center.z - b.z))[0]!;
      const proveRiser = (upper: RingPlan, lower: RingPlan, requireNearPlan = true) => { const ringKeys = new Set([...upper.keys, ...lower.keys]), faces = componentTriangles.filter((triangle) => triangle.keys.every((key) => ringKeys.has(key))), verticality = faces.map((triangle) => Math.abs(triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y)).sort((a, b) => a - b), matches = Array.from({ length: 8 }, (_, offset) => ({ offset, changes: upper.boundary.map((point, step) => Math.hypot(point.x - lower.boundary[(step + offset) % 8]!.x, point.z - lower.boundary[(step + offset) % 8]!.z)).sort((a, b) => a - b) })).sort((a, b) => a.changes[3]! - b.changes[3]!), match = matches[0]!, meanRadius = upper.boundary.reduce((sum, point) => sum + xzRadius(point, upper), 0) / upper.boundary.length, riserCenter = upper.center.clone().add(lower.center).multiplyScalar(.5); expect(faces).toHaveLength(16); for (const triangle of faces) { const normal = triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])), centroid = triangle.points[0].clone().add(triangle.points[1]).add(triangle.points[2]).multiplyScalar(1 / 3); expect(normal.x * (centroid.x - riserCenter.x) + normal.z * (centroid.z - riserCenter.z)).toBeGreaterThan(0); } expect(verticality[7]).toBeLessThan(.45); expect(upper.meanY - lower.meanY).toBeGreaterThan(1.2); if (requireNearPlan) expect(match.changes[3]! / meanRadius).toBeLessThan(.12); return upper.boundary.map((point, step) => xzRadius(point, upper) - xzRadius(lower.boundary[(step + match.offset) % 8]!, lower)); };
      const upperOverhang = proveRiser(shelves[0]!.outer, shelves[1]!.inner); proveRiser(shelves[1]!.outer, deepRing); proveRiser(deepRing, bottomRing, false); const minOverhang = Math.min(...upperOverhang), maxOverhang = Math.max(...upperOverhang), localMeanRadius = [...shelves[0]!.outer.boundary.map((point) => xzRadius(point, shelves[0]!.outer)), ...shelves[1]!.inner.boundary.map((point) => xzRadius(point, shelves[1]!.inner))].reduce((sum, radius) => sum + radius, 0) / 16; if (spec.band === 'far') { expect(maxOverhang).toBeGreaterThan(.35); expect(maxOverhang).toBeLessThan(8); expect(maxOverhang / localMeanRadius).toBeLessThan(.65); } else { expect(minOverhang, `seed ${spec.seed} bridge radial minimum`).toBeGreaterThan(-1); expect(maxOverhang, `seed ${spec.seed} bridge radial maximum`).toBeLessThan(-.2); } const notchDistance = (shelves[1]!.outer.notchBin - shelves[0]!.outer.notchBin + 8) % 8; expect(notchDistance).toBeGreaterThanOrEqual(2); expect(notchDistance).toBeLessThanOrEqual(6);
      expect(Math.max(...elevationBands[3]!.map((point) => point.y)) - Math.min(...elevationBands[3]!.map((point) => point.y))).toBeGreaterThan(.05);
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
      return { points, center, bounds, profile, seed: spec.seed, band: spec.band, upperRiserCount: spec.band === 'far' ? 0 : upperRiserFaces.length };
    }).sort((a, b) => b.center.z - a.center.z || a.center.x - b.center.x);
    expect(new Set(actual.map((island) => island.profile)).size).toBe(12); expect(new Set(actual.map((island) => island.seed)).size).toBe(HORIZON_GEOMETRY_CASES.length); expect(actual.reduce((sum, island) => sum + island.upperRiserCount, 0)).toBe(128); for (let island = 1; island < actual.length; island += 1) expect(actual[island]!.profile).not.toBe(actual[island - 1]!.profile);
    expect(farMesh.geometry.userData.horizonIslandCount).toBe(actual.length); expect(farMesh.geometry.userData.horizonTriangleCount).toBe(triangles.length);
    expect(Math.min(...actual.map((island) => island.bounds.min.x))).toBeLessThan(-60); expect(Math.max(...actual.map((island) => island.bounds.max.x))).toBeGreaterThan(60);
    const depthGroups = [actual.slice(0, 4), actual.slice(4, 8), actual.slice(8, 12)]; expect(depthGroups.every((group) => group.length === 4)).toBe(true); expect(Math.min(...depthGroups[0]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[1]!.map((island) => island.center.z))); expect(Math.min(...depthGroups[1]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[2]!.map((island) => island.center.z)));
    for (const group of depthGroups) { const intervals = group.map((island) => [island.bounds.min.x, island.bounds.max.x] as const).sort((a, b) => a[0] - b[0]), gaps = intervals.slice(1).map((interval, offset) => interval[0] - intervals[offset]![1]); expect(gaps.filter((gap) => gap > 0).length).toBeGreaterThanOrEqual(2); }
    const farBandPositions = new Float32Array(actual.filter((island) => island.band === 'far').sort((a, b) => a.seed - b.seed).flatMap((island) => [...island.points].sort((a, b) => a.x - b.x || a.y - b.y || a.z - b.z).flatMap((point) => point.toArray())));
    expect(await rawArrayFingerprint(farBandPositions)).toBe('37524d8171b4c51d5e3cc4c9e42497f8a635605457f5de33366b1d6f38c3ec0d');
    const viewports = [[1440, 900], [390, 844], [844, 390]] as const, safeRoadHalfWidth = WORLD_METRICS.roadWidth / 2 + .4;
    for (const [width, height] of viewports) { const profile = d4ProfileForViewport(width, height), record = TR4_RUNTIME_CAMERA[profile.name], camera = new PerspectiveCamera(record.fov, width / height, .08, 520); camera.position.set(0, record.height, record.back); camera.lookAt(0, record.targetY, -record.targetAhead); camera.updateProjectionMatrix(); applyTR4RuntimeLensShift(camera, profile); camera.updateMatrixWorld();
      for (const island of actual) { const projected = island.points.map((point) => point.clone().project(camera)).filter((point) => point.z >= -1 && point.z <= 1), roadEdge = new Vector3(island.center.x < 0 ? -safeRoadHalfWidth : safeRoadHalfWidth, 0, island.center.z).project(camera).x, closest = island.center.x < 0 ? Math.max(...projected.map((point) => point.x)) : Math.min(...projected.map((point) => point.x)); expect(island.center.x < 0 ? closest < roadEdge - .015 : closest > roadEdge + .015).toBe(true); }
      for (const group of depthGroups) { const measures = group.map((island) => { const projected = island.points.map((point) => point.clone().project(camera)).filter((point) => point.z >= -1 && point.z <= 1); if (projected.length === 0) return { width: 0, height: 0, area: 0 }; const left = Math.max(-.6, Math.min(...projected.map((point) => point.x))), right = Math.min(.6, Math.max(...projected.map((point) => point.x))), bottom = Math.max(-1, Math.min(...projected.map((point) => point.y))), top = Math.min(1, Math.max(...projected.map((point) => point.y))), clippedWidth = Math.max(0, right - left), clippedHeight = Math.max(0, top - bottom); return { width: clippedWidth, height: clippedHeight, area: clippedWidth * clippedHeight }; }); expect(Math.max(...measures.map((measure) => measure.width))).toBeGreaterThan(.03); expect(Math.max(...measures.map((measure) => measure.height))).toBeGreaterThan(.03); expect(Math.max(...measures.map((measure) => measure.area))).toBeGreaterThan(.002); }
    }
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
  it('preserves R1D massing while actual R1E faces carry deterministic depth-scaled basalt treatment', async () => {
    const first = new TideScarWorld(), second = new TideScarWorld();
    const collectMeshes = (world: TideScarWorld) => { const meshes: Mesh[] = []; world.root.traverse((object) => { if (object instanceof Mesh) meshes.push(object); }); return meshes; };
    const firstMeshes = collectMeshes(first), secondMeshes = collectMeshes(second);
    expect(firstMeshes).toHaveLength(4); expect(secondMeshes).toHaveLength(4);
    const fingerprints = await Promise.all(firstMeshes.map(async (mesh) => { mesh.geometry.computeBoundingBox(); return [mesh.name, await geometryFingerprint(mesh), mesh.geometry.getAttribute('position').count, mesh.geometry.getIndex()!.count, mesh.geometry.boundingBox!.min.toArray(), mesh.geometry.boundingBox!.max.toArray()]; }));
    expect(fingerprints).toEqual([
      ['tide-scar-faceted-abyss-bed', '4f4032aa4676afa4d2b6f92367b309c7e952500b7743df3d0e82db1e7f8c4b52', 90, 432, [-120, -33.034568786621094, -240], [120, -22.416658401489258, 30]],
      ['tide-scar-near-fractured-inner-lips', 'b80bb17b7a162c86e04928d1f919bd6e9857a2323d23ad2d39ae3f43d57e6e68', 862, 1122, [-20.217283248901367, -15.600470542907715, -93], [17.62417221069336, 4.526494979858398, -5]],
      ['tide-scar-mid-interrupted-buttress-recesses', '3013352e2ba6fb5ef670fcaa8e0d724799713011eb054c67557e848966225906', 1152, 1488, [-35.438621520996094, -18.989492416381836, -121], [41.28934860229492, 6.292722225189209, -24]],
      ['tide-scar-far-low-ridge-mesa-chains', '45a7a2684af0a7a70976a3c10dffa6527173a214776410dc17601f10348be4a9', 4392, 4656, [-63.92366027832031, -17.7822322845459, -192], [63.154701232910156, 6.28000020980835, -37.97065734863281]],
    ]);
    const rawPositionFingerprints = await Promise.all(firstMeshes.map((mesh) => rawArrayFingerprint(mesh.geometry.getAttribute('position').array))), farIndexFingerprint = await rawArrayFingerprint(firstMeshes[3]!.geometry.getIndex()!.array);
    expect({ farCombined: fingerprints[3]![1], farBounds: [fingerprints[3]![4], fingerprints[3]![5]], rawPositionFingerprints, farIndexFingerprint }).toEqual({
      farCombined: '45a7a2684af0a7a70976a3c10dffa6527173a214776410dc17601f10348be4a9',
      farBounds: [[-63.92366027832031, -17.7822322845459, -192], [63.154701232910156, 6.28000020980835, -37.97065734863281]],
      rawPositionFingerprints: ['7bcce39ce56b41f6a43673cae1aff35e062bacfc0449adeca09a17a2db60b914', '4f4a56e16b9f0b98b836efdc14153d2872577c54a8bde224500f08635d8a3dae', '0af2a8a06c59ffcd3e166a1641a26ba6ed0cadc9d7a55c025410e9719aac6778', 'dbe115aabfa5bfe8a1f0dbe357e786a747fc49db41b5ca6944a27ba275e3bb7c'],
      farIndexFingerprint: '15c61b15613bc21f5aba67e4b5ba4b6c22ebe80f80c40e640b5c480ebb12c402',
    });
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
  it('uses six deterministic fractured causeway signatures with real side mass', () => {
    const fingerprints = new Set<string>(), vertexCounts = new Set<number>(), edgeEvents = new Set<string>();
    for (let signature = 0; signature < 6; signature += 1) {
      const geometry = createDeckCapGeometry(signature);
      geometry.computeBoundingBox();
      const bounds = geometry.boundingBox!;
      expect(bounds.min.y).toBeLessThan(-2.5);
      expect(bounds.max.x).toBeGreaterThan(0.44);
      expect([bounds.min.z, bounds.max.z]).toEqual([-0.5, 0.5]);
      expect(geometry.type).toBe('BufferGeometry');
      expect(geometry.userData).toMatchObject({ signature, moduleLength: [6, 11], protectedHalfWidth: 0.44 });
      const position = geometry.getAttribute('position'), index = geometry.getIndex()!, sideNormals: [number[], number[]] = [[], []], capFaces = [0, 0];
      for (let offset = 0; offset < index.count; offset += 3) {
        const vertices = [index.getX(offset), index.getX(offset + 1), index.getX(offset + 2)];
        const xs = vertices.map((vertex) => position.getX(vertex)), ys = vertices.map((vertex) => position.getY(vertex)), zs = vertices.map((vertex) => position.getZ(vertex));
        if (zs.every((z) => z === -.5)) capFaces[0]! += 1; if (zs.every((z) => z === .5)) capFaces[1]! += 1;
        const side = xs.every((x) => x < -.44) ? 0 : xs.every((x) => x > .44) ? 1 : -1;
        const normalX = (ys[1]! - ys[0]!) * (zs[2]! - zs[0]!) - (zs[1]! - zs[0]!) * (ys[2]! - ys[0]!);
        if (side >= 0 && Math.max(...zs) > Math.min(...zs) && Math.abs(normalX) > 1e-7) sideNormals[side as 0 | 1].push(normalX);
      }
      expect(Math.max(...sideNormals[0])).toBeLessThan(0); expect(Math.min(...sideNormals[1])).toBeGreaterThan(0);
      expect(capFaces.every((count) => count > 2)).toBe(true); expect(capFaces[0]! + capFaces[1]!).toBe(geometry.userData.capTriangleCount);
      fingerprints.add(Array.from(geometry.getAttribute('position').array).join(',')); vertexCounts.add(position.count); edgeEvents.add(`${geometry.userData.edgeEvent}/${geometry.userData.oppositeEdgeEvent}`);
      expect(Array.from({ length: 4 }, (_, vertex) => [position.getX(vertex), position.getY(vertex), position.getZ(vertex)].map((value) => Number(value.toFixed(3))))).toEqual([[-.462, -.012, -.5], [.462, -.012, -.5], [-.462, -.012, .5], [.462, -.012, .5]]);
      geometry.dispose();
    }
    expect(fingerprints.size).toBe(6); expect(vertexCounts.size).toBeGreaterThanOrEqual(3);
    expect(edgeEvents).toEqual(new Set(['collapsed-shoulder/outer-buttress', 'stepped-ledge/undercut', 'deep-recess/outer-rubble', 'outer-buttress/collapsed-shoulder', 'undercut/stepped-ledge', 'outer-rubble/deep-recess']));
    expect([presentationRoadStart(0), presentationRoadStart(1)]).toEqual([-18, 0]);
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
