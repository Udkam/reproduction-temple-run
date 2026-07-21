import { Mesh, MeshStandardMaterial, PerspectiveCamera, Texture, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import { TideScarWorld } from './tideScarWorld';
import { applyTR4RuntimeLensShift, createDeckCapGeometry, presentationRoadStart, shouldShowPursuer, TR4_RUNTIME_CAMERA } from './WorldRenderer';
import { d4ProfileForViewport } from './d4Profile';
import { WORLD_METRICS } from './theme';

const LAYERS = [['tide-scar-near-fractured-inner-lips', 'near', 3, 13, 10, 6, 0],
  ['tide-scar-mid-interrupted-buttress-recesses', 'mid', 4, 14, 12, 8, 0],
  ['tide-scar-far-low-ridge-mesa-chains', 'far', 4, 11, 12, 8, 12]] as const;
describe('Tide Scar geometric canyon presentation', () => {
  it('builds thick, distinct near/mid/far topology without panorama, plane, or instanced-card geometry', () => {
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
      const shelves = shelfGroups.map((group) => { const upward = group.map((triangle) => triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y); expect(Math.min(...upward)).toBeGreaterThan(.55); const uses = new Map<string, { count: number; ends: [string, string] }>(); for (const triangle of group) for (const [u, v] of [[0, 1], [1, 2], [2, 0]] as const) { const ends = [triangle.keys[u], triangle.keys[v]].sort() as [string, string], edge = ends.join('|'), previous = uses.get(edge); uses.set(edge, { count: (previous?.count ?? 0) + 1, ends }); } const boundaryAdjacency = new Map<string, Set<string>>(); for (const { count, ends } of uses.values()) if (count === 1) { for (const [from, to] of [ends, [ends[1], ends[0]]] as [string, string][]) { if (!boundaryAdjacency.has(from)) boundaryAdjacency.set(from, new Set()); boundaryAdjacency.get(from)!.add(to); } } expect([...boundaryAdjacency.values()].every((links) => links.size === 2)).toBe(true); const ringKeys: Set<string>[] = [], pending = new Set(boundaryAdjacency.keys()); while (pending.size > 0) { const keys = new Set<string>(), queue = [pending.values().next().value as string]; while (queue.length > 0) { const key = queue.pop()!; if (!pending.delete(key)) continue; keys.add(key); queue.push(...boundaryAdjacency.get(key)!); } ringKeys.push(keys); } expect(ringKeys.map((keys) => keys.size)).toEqual([8, 8]); const plans = ringKeys.map(ringPlan).sort((a, b) => a.area - b.area), [inner, outer] = plans; expect(outer!.area / inner!.area).toBeGreaterThan(1.25); expect(Math.abs(outer!.meanY - inner!.meanY)).toBeLessThan(.05); expect(outer!.center.distanceTo(inner!.center)).toBeGreaterThan(.08); expect(outer!.radialBreak).toBeGreaterThan(.175); return { inner: inner!, outer: outer! }; }).sort((a, b) => b.outer.meanY - a.outer.meanY);
      const deepBand = elevationBands.find((band) => band.length === 8)!, deepRing = ringPlan(new Set(deepBand.map(keyOf))), bottomRing = ringPlan(new Set(elevationBands[0]!.map(keyOf).filter((key) => !capKeys.has(key))));
      const xzRadius = (point: Vector3, plan: RingPlan) => Math.hypot(point.x - plan.center.x, point.z - plan.center.z);
      const proveRiser = (upper: RingPlan, lower: RingPlan, requireNearPlan = true) => { const ringKeys = new Set([...upper.keys, ...lower.keys]), faces = componentTriangles.filter((triangle) => triangle.keys.every((key) => ringKeys.has(key))), verticality = faces.map((triangle) => Math.abs(triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])).normalize().y)).sort((a, b) => a - b), matches = Array.from({ length: 8 }, (_, offset) => ({ offset, changes: upper.boundary.map((point, step) => Math.hypot(point.x - lower.boundary[(step + offset) % 8]!.x, point.z - lower.boundary[(step + offset) % 8]!.z)).sort((a, b) => a - b) })).sort((a, b) => a.changes[3]! - b.changes[3]!), match = matches[0]!, meanRadius = upper.boundary.reduce((sum, point) => sum + xzRadius(point, upper), 0) / upper.boundary.length, riserCenter = upper.center.clone().add(lower.center).multiplyScalar(.5); expect(faces).toHaveLength(16); for (const triangle of faces) { const normal = triangle.points[1].clone().sub(triangle.points[0]).cross(triangle.points[2].clone().sub(triangle.points[0])), centroid = triangle.points[0].clone().add(triangle.points[1]).add(triangle.points[2]).multiplyScalar(1 / 3); expect(normal.x * (centroid.x - riserCenter.x) + normal.z * (centroid.z - riserCenter.z)).toBeGreaterThan(0); } expect(verticality[7]).toBeLessThan(.45); expect(upper.meanY - lower.meanY).toBeGreaterThan(1.2); if (requireNearPlan) expect(match.changes[3]! / meanRadius).toBeLessThan(.12); return upper.boundary.map((point, step) => xzRadius(point, upper) - xzRadius(lower.boundary[(step + match.offset) % 8]!, lower)); };
      const upperOverhang = proveRiser(shelves[0]!.outer, shelves[1]!.inner); proveRiser(shelves[1]!.outer, deepRing); proveRiser(deepRing, bottomRing, false); const maxOverhang = Math.max(...upperOverhang), localMeanRadius = [...shelves[0]!.outer.boundary.map((point) => xzRadius(point, shelves[0]!.outer)), ...shelves[1]!.inner.boundary.map((point) => xzRadius(point, shelves[1]!.inner))].reduce((sum, radius) => sum + radius, 0) / 16; expect(maxOverhang).toBeGreaterThan(.35); expect(maxOverhang).toBeLessThan(8); expect(maxOverhang / localMeanRadius).toBeLessThan(.65); const notchDistance = (shelves[1]!.outer.notchBin - shelves[0]!.outer.notchBin + 8) % 8; expect(notchDistance).toBeGreaterThanOrEqual(2); expect(notchDistance).toBeLessThanOrEqual(6);
      expect(Math.max(...elevationBands[3]!.map((point) => point.y)) - Math.min(...elevationBands[3]!.map((point) => point.y))).toBeGreaterThan(.05);
      const width = bounds.max.x - bounds.min.x, depth = bounds.max.z - bounds.min.z, height = bounds.max.y - bounds.min.y; expect(height).toBeGreaterThan(7); expect(height / Math.max(width, depth)).toBeLessThan(.55); expect(width / depth).toBeGreaterThan(.24); expect(width / depth).toBeLessThan(1.6);
      const profile = [(shelves[0]!.outer.meanY - shelves[1]!.inner.meanY).toFixed(1), (shelves[1]!.outer.meanY - deepRing.meanY).toFixed(1), (shelves[0]!.outer.area / shelves[0]!.inner.area).toFixed(2), (shelves[1]!.outer.area / shelves[1]!.inner.area).toFixed(2), shelves[0]!.outer.notchBin, shelves[1]!.outer.notchBin].join(':'); return { points, center, bounds, profile };
    }).sort((a, b) => b.center.z - a.center.z || a.center.x - b.center.x);
    expect(new Set(actual.map((island) => island.profile)).size).toBe(12); for (let island = 1; island < actual.length; island += 1) expect(actual[island]!.profile).not.toBe(actual[island - 1]!.profile);
    expect(farMesh.geometry.userData.horizonIslandCount).toBe(actual.length); expect(farMesh.geometry.userData.horizonTriangleCount).toBe(triangles.length);
    expect(Math.min(...actual.map((island) => island.bounds.min.x))).toBeLessThan(-60); expect(Math.max(...actual.map((island) => island.bounds.max.x))).toBeGreaterThan(60);
    const depthGroups = [actual.slice(0, 4), actual.slice(4, 8), actual.slice(8, 12)]; expect(depthGroups.every((group) => group.length === 4)).toBe(true); expect(Math.min(...depthGroups[0]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[1]!.map((island) => island.center.z))); expect(Math.min(...depthGroups[1]!.map((island) => island.center.z))).toBeGreaterThan(Math.max(...depthGroups[2]!.map((island) => island.center.z)));
    for (const group of depthGroups) { const intervals = group.map((island) => [island.bounds.min.x, island.bounds.max.x] as const).sort((a, b) => a[0] - b[0]), gaps = intervals.slice(1).map((interval, offset) => interval[0] - intervals[offset]![1]); expect(gaps.filter((gap) => gap > 0).length).toBeGreaterThanOrEqual(2); }
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
  it('keeps setPanorama as a non-owning no-op and releases every owned geometry and material', () => {
    const world = new TideScarWorld();
    const texture = new Texture();
    let textureDisposals = 0; let geometryDisposals = 0; let materialDisposals = 0;
    texture.addEventListener('dispose', () => { textureDisposals += 1; });
    world.setPanorama(texture);
    expect(world.hasPanorama).toBe(false);
    world.setSurfaceMap(texture);
    world.root.traverse((object) => {
      if (!(object instanceof Mesh)) return;
      object.geometry.addEventListener('dispose', () => { geometryDisposals += 1; });
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      for (const material of materials) {
        expect((material as MeshStandardMaterial).map).toBe(object.name === LAYERS[0][0] ? texture : null);
        material.addEventListener('dispose', () => { materialDisposals += 1; });
      }
    });
    world.dispose();
    world.dispose();
    expect(geometryDisposals).toBe(4);
    expect(materialDisposals).toBe(4);
    expect(textureDisposals).toBe(0);
    texture.dispose();
  });
});
