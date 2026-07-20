import { Mesh, MeshStandardMaterial, PerspectiveCamera, Texture, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import { TideScarWorld } from './tideScarWorld';
import { applyTR4RuntimeLensShift, createDeckCapGeometry, presentationRoadStart, shouldShowPursuer, TR4_RUNTIME_CAMERA } from './WorldRenderer';
import { d4ProfileForViewport } from './d4Profile';

const LAYERS = [['tide-scar-near-fractured-inner-lips', 'near', 3, 13, 10],
  ['tide-scar-mid-interrupted-buttress-recesses', 'mid', 4, 14, 12],
  ['tide-scar-far-low-ridge-mesa-chains', 'far', 4, 11, 12]] as const;
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
    for (const [name, layer, runCount, profilePointCount, signatureCount] of LAYERS) {
      const object = world.root.getObjectByName(name);
      expect(object).toBeInstanceOf(Mesh);
      const mesh = object as Mesh;
      mesh.geometry.computeBoundingBox();
      const bounds = mesh.geometry.boundingBox!;
      expect(bounds.max.x - bounds.min.x).toBeGreaterThan(10);
      expect(bounds.max.y - bounds.min.y).toBeGreaterThan(10);
      expect(bounds.max.z - bounds.min.z).toBeGreaterThan(40);
      const expectedSideTriangles = signatureCount * profilePointCount * 2, expectedCapTriangles = runCount * (profilePointCount - 2) * 2;
      expect(mesh.geometry.userData).toMatchObject({ canyonLayer: layer, runCount, profilePointCount, signatureCount,
        closedProfile: true, capCount: runCount * 2, sideTriangleCount: expectedSideTriangles,
        capTriangleCount: expectedCapTriangles,
        construction: 'closed-segmented-longitudinal-shelf-recess-buttress-foot-talus' });
      expect(mesh.geometry.userData.endpointAreaRatio).toBeLessThan(.2);
      expect(mesh.geometry.getIndex()!.count / 3).toBe(expectedSideTriangles + expectedCapTriangles);
      expect(mesh.geometry.getAttribute('uv').count).toBe(mesh.geometry.getAttribute('position').count);
      topologySizes.push(mesh.geometry.getAttribute('position').count);
    }
    expect(new Set(topologySizes).size).toBe(3);
    const farBounds = (world.root.getObjectByName(LAYERS[2][0]) as Mesh).geometry.boundingBox!;
    expect(farBounds.max.z).toBeLessThan(-55);
    expect(farBounds.min.z).toBeGreaterThan(-230);
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
