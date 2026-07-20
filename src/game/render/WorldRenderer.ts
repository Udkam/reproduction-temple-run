import {
  ACESFilmicToneMapping,
  AmbientLight,
  BoxGeometry,
  BufferGeometry,
  Color,
  CylinderGeometry,
  DirectionalLight,
  DodecahedronGeometry,
  DynamicDrawUsage,
  FogExp2,
  Float32BufferAttribute,
  HemisphereLight,
  IcosahedronGeometry,
  InstancedMesh,
  MathUtils,
  Matrix4,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  PerspectiveCamera,
  Points,
  PointsMaterial,
  PCFShadowMap,
  RingGeometry,
  Scene,
  ShapeUtils,
  SRGBColorSpace,
  TorusGeometry,
  Vector3,
  Vector2,
  Vector4,
  WebGLRenderer,
} from 'three';
import {
  getCurrentSection,
  headingVector,
  headingYaw,
  rightVector,
  sampleCoursePosition,
  sampleRunnerPosition,
  sectionEnd,
  type CourseEvent,
  type CourseSection,
  type RunnerEvent,
  type RunnerState,
  type TurnDirection,
} from '../core';
import { PURSUER_RIG_BOUNDS, createPursuerRig, updatePursuerRig, type PursuerRig } from './pursuerRig';
import { RUNNER_RIG_BOUNDS, createRunnerRig, updateRunnerRig, type RunnerRig } from './runnerRig';
import { TideScarWorld } from './tideScarWorld';
import { d4MinimumPursuerGapPx, d4ProfileForViewport, type D4Profile } from './d4Profile';
import { loadD4Assets, selectD4Assets, type D4LoadedAssets } from './d4Assets';
import { TideScarRoad, type TideScarRoadSnapshot, type TideScarWorldSegment } from './tideScarRoad';
import { PALETTE, WORLD_METRICS } from './theme';
import { turnLaneOffset } from './turnPresentation';

export interface RenderOptions {
  highContrast: boolean;
  reducedMotion: boolean;
}

export interface ClippedScreenBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
  area: number;
}

export interface HazardScreenBounds {
  eventId: string;
  kind: "beam" | "ring" | "column" | "gap";
  bounds: ClippedScreenBounds;
}

export interface TideScarScreenSegment {
  sectionId: string;
  intervalIndex: number;
  segmentIndex: number;
  polygonCss: readonly { x: number; y: number }[];
  pixelBounds: { left: number; top: number; right: number; bottom: number };
  visibleAreaPx: number;
}

export interface RenderSnapshot {
  canvas: { width: number; height: number; resolution: number };
  options: RenderOptions;
  presentationAlpha: number;
  presentedDistance: number;
  presentedLanePosition: number;
  runnerWorld: { x: number; y: number; z: number; yaw: number };
  runnerScreen: { x: number; y: number; visible: boolean; bounds?: ClippedScreenBounds | null };
  pursuerScreen: { x: number; y: number; visible: boolean; bounds: ClippedScreenBounds | null };
  /** Positive vertical separation between courier and pursuer in non-capture frames. */
  pursuerGapPx?: number | null;
  /** Clipped CSS-pixel geometry for every visible unresolved hazard. */
  hazardScreens: HazardScreenBounds[];
  tideScarSegments?: readonly TideScarScreenSegment[];
  camera: { x: number; y: number; z: number; fov: number; yaw: number };
  lanePosition: number;
  posture: 'run' | 'jump' | 'slide';
  visibleSectionIds: string[];
  visibleObstacleCount: number;
  drawCalls: number;
  triangles: number;
  turnProgress: number | null;
  contextLossCount: number;
  d4?: {
    profile: 'desktop' | 'portrait' | 'landscape';
    fogDensity: number;
    assetTier: 'desktop' | 'mobile' | 'fallback' | 'loading';
    requestedAssets: readonly string[];
    textureBytes: number;
    tideScarVertices: number;
    tideScarCoverage: number;
    pursuerPlacementError: string | null;
    composition: {
      pitchDegrees: number;
      horizonY: number;
      vanishingPoint: { x: number; y: number };
      bottomRoadWidth: number;
      runnerCenterY: number;
    };
  };
}

interface TurnMotion {
  direction: TurnDirection;
  fromSectionId: string;
  toSectionId: string;
  fromYaw: number;
  toYaw: number;
  baseLanePosition: number;
  progress: number;
  override: number | null;
  start: Vector3;
  controlOne: Vector3;
  controlTwo: Vector3;
  end: Vector3;
}

const MAX_SECTIONS = 8;
const MAX_RAILS = MAX_SECTIONS * 2;
const MAX_PILLARS = MAX_SECTIONS * 6;
const MAX_ROCKS = MAX_SECTIONS * 8;
const MAX_CORAL = MAX_SECTIONS * 4;
const MAX_ROAD_MODULES_PER_SIGNATURE = MAX_SECTIONS * 8;
const MAX_EVENTS = 96;
const MAX_SHARDS = 160;
const TURN_VISUAL_RADIUS = 1.45;
const TR4_FOG_COLOR = 0x9aa7a8, TR4_FOG_DENSITY = 0.0035;
export const TR4_RUNTIME_CAMERA = {
  portrait: { height: 6.2, back: 15.2, targetAhead: 16.8, targetY: 0.55, fov: 40, lensShiftY: -0.055 },
  desktop: { height: 6.06, back: 13.6, targetAhead: 13.3, targetY: 0.6, fov: 43, lensShiftY: -0.025 },
  landscape: { height: 6.15, back: 12.8, targetAhead: 12.56, targetY: 0.55, fov: 46, lensShiftY: -0.02 },
} as const;
function canyonFogDensity(profile: D4Profile, highContrast: boolean): number { void profile; return highContrast ? .003 : TR4_FOG_DENSITY; }

function easeInOut(progress: number): number {
  const value = MathUtils.clamp(progress, 0, 1);
  return value * value * (3 - 2 * value);
}

function shortestAngle(from: number, to: number, progress: number): number {
  let delta = (to - from + Math.PI) % (Math.PI * 2) - Math.PI;
  if (delta < -Math.PI) delta += Math.PI * 2;
  return from + delta * progress;
}

function cubicBezier(
  start: Vector3,
  controlOne: Vector3,
  controlTwo: Vector3,
  end: Vector3,
  progress: number,
): Vector3 {
  const p = MathUtils.clamp(progress, 0, 1);
  const inverse = 1 - p;
  return new Vector3(
    inverse ** 3 * start.x + 3 * inverse ** 2 * p * controlOne.x + 3 * inverse * p ** 2 * controlTwo.x + p ** 3 * end.x,
    inverse ** 3 * start.y + 3 * inverse ** 2 * p * controlOne.y + 3 * inverse * p ** 2 * controlTwo.y + p ** 3 * end.y,
    inverse ** 3 * start.z + 3 * inverse ** 2 * p * controlOne.z + 3 * inverse * p ** 2 * controlTwo.z + p ** 3 * end.z,
  );
}

function postureOf(state: RunnerState): 'run' | 'jump' | 'slide' {
  if (state.runner.slideTicksRemaining > 0) return 'slide';
  if (!state.runner.grounded) return 'jump';
  return 'run';
}

function seededUnit(index: number, salt: number): number {
  let value = Math.imul(index + 1, 0x45d9f3b) ^ Math.imul(salt + 11, 0x27d4eb2d);
  value ^= value >>> 16;
  value = Math.imul(value, 0x45d9f3b);
  value ^= value >>> 16;
  return (value >>> 0) / 0xffffffff;
}

export function presentationRoadStart(sectionIndex: number): number { return sectionIndex === 0 ? -18 : 0; }

export function createDeckCapGeometry(profile: number): BufferGeometry {
  const signature = ((profile % 6) + 6) % 6;
  const edgeEvents = [
    { name: 'collapsed-shoulder', points: [[0, 0], [.06, -.28], [.14, -.38], [.06, -1.2], [.19, -1]] },
    { name: 'stepped-ledge', points: [[0, 0], [.05, -.22], [.16, -.22], [.16, -.56], [.3, -.56], [.22, -1]] },
    { name: 'deep-recess', points: [[0, 0], [.05, -.24], [.24, -.44], [.1, -.8], [.38, -1.12], [.16, -1.75], [.24, -1]] },
    { name: 'outer-buttress', points: [[0, 0], [.06, -.22], [.14, -.43], [.32, -.55], [.45, -.9], [.32, -1.25], [.52, -1.65], [.36, -1]] },
    { name: 'undercut', points: [[0, 0], [.04, -.23], [.2, -.3], [.08, -.55], [-.006, -.82], [.18, -1.08], [.38, -1.45], [.26, -1.9], [.34, -1]] },
    { name: 'outer-rubble', points: [[0, 0], [.08, -.2], [.18, -.42], [.33, -.62], [.26, -.85], [.55, -1.05], [.43, -1.35], [.72, -1.7], [.5, -2.05], [.62, -1]] },
  ] as const;
  const sideEvents = [edgeEvents[signature]!, edgeEvents[(signature + 3) % 6]!] as const;
  const stationCount = 5 + signature % 3;
  const positions: number[] = [];
  const colors: number[] = [];
  const indices: number[] = [];
  const stations = Array.from({ length: stationCount }, (_, station) => {
    const z = -0.5 + station / (stationCount - 1);
    const terminal = station === 0 || station === stationCount - 1, left = terminal ? -.462 : -.475 + seededUnit(signature * 19 + station, 701) * .028;
    const right = terminal ? .462 : .475 - seededUnit(signature * 23 + station, 703) * .028, crown = terminal ? 0 : (seededUnit(signature * 29 + station, 709) - .5) * .045;
    return { z, left, right, crown, xs: [left, -0.17 + crown * 0.3, 0.17 - crown * 0.2, right] };
  });
  const topRows = stations.map(() => [-1, -1, -1, -1]);
  const addTop = (station: number, column: number) => {
    const point = stations[station]!;
    topRows[station]![column] = positions.length / 3;
    positions.push(point.xs[column]!, point.crown + (column === 1 || column === 2 ? .025 : -.012), point.z);
    colors.push(1, 1, 1);
  };
  for (const [station, column] of [[0, 0], [0, 3], [stationCount - 1, 0], [stationCount - 1, 3]] as const) addTop(station, column);
  for (let station = 0; station < stationCount; station += 1) {
    for (let column = 0; column < 4; column += 1) if (topRows[station]![column] === -1) addTop(station, column);
  }
  const sideRows: [number[][], number[][]] = [[], []];
  for (const [station, point] of stations.entries()) {
    for (const [sideIndex, edge] of [point.left, point.right].entries()) {
      const sign = sideIndex === 0 ? -1 : 1;
      const sideEvent = sideEvents[sideIndex as 0 | 1], structuralDepth = 3.2 + signature * .46 + seededUnit(station, 719 + signature) * .38;
      const sideRow: number[] = [];
      for (const [depthIndex, [outward, depth]] of sideEvent.points.entries()) {
        sideRow.push(positions.length / 3);
        positions.push(edge + sign * outward, depth === 0 ? point.crown - .012 : depth === -1 ? -structuralDepth : depth, point.z);
        const shade = 0.82 - depthIndex * 0.075;
        colors.push(shade, shade * 0.94, shade * 0.86);
      }
      sideRows[sideIndex as 0 | 1].push(sideRow);
    }
  }
  for (let station = 0; station < stationCount - 1; station += 1) {
    for (let column = 0; column < 3; column += 1) {
      const a = topRows[station]![column]!;
      const b = topRows[station]![column + 1]!;
      const c = topRows[station + 1]![column]!;
      const d = topRows[station + 1]![column + 1]!;
      indices.push(a, c, d, a, d, b);
    }
    for (const [sideIndex, rows] of sideRows.entries()) {
      for (let depth = 0; depth < sideEvents[sideIndex as 0 | 1].points.length - 1; depth += 1) {
        const a = rows[station]![depth]!;
        const b = rows[station]![depth + 1]!;
        const c = rows[station + 1]![depth]!;
        const d = rows[station + 1]![depth + 1]!;
        if (sideIndex === 0) indices.push(a, b, d, a, d, c);
        else indices.push(a, d, b, a, c, d);
      }
    }
    const leftBottom = sideEvents[0].points.length - 1, rightBottom = sideEvents[1].points.length - 1;
    const leftBase = sideRows[0][station]![leftBottom]!, rightBase = sideRows[1][station]![rightBottom]!;
    const nextLeftBase = sideRows[0][station + 1]![leftBottom]!, nextRightBase = sideRows[1][station + 1]![rightBottom]!;
    indices.push(leftBase, nextRightBase, nextLeftBase, leftBase, rightBase, nextRightBase);
  }
  let capTriangleCount = 0;
  for (const [station, targetNormalZ] of [[0, -1], [stationCount - 1, 1]] as const) {
    const perimeter = [...topRows[station]!, ...sideRows[1][station]!.slice(1), ...sideRows[0][station]!.slice(1).reverse()];
    const faces = ShapeUtils.triangulateShape(perimeter.map((vertex) => new Vector2(positions[vertex * 3]!, positions[vertex * 3 + 1]!)), []);
    for (const face of faces) {
      const triangle = face.map((index) => perimeter[index]!) as [number, number, number],
        [a, b, c] = triangle.map((vertex) => new Vector2(positions[vertex * 3]!, positions[vertex * 3 + 1]!));
      const crossZ = (b!.x - a!.x) * (c!.y - a!.y) - (b!.y - a!.y) * (c!.x - a!.x);
      indices.push(...(crossZ * targetNormalZ < 0 ? [triangle[0], triangle[2], triangle[1]] : triangle));
      capTriangleCount += 1;
    }
  }
  const geometry = new BufferGeometry();
  geometry.name = `tide-scar-causeway-module-${signature}`;
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.userData = { signature, edgeEvent: sideEvents[0].name, oppositeEdgeEvent: sideEvents[1].name, profilePointCounts: sideEvents.map((event) => event.points.length), capTriangleCount,
    sideWinding: 'outward-x', moduleLength: [6, 11], protectedHalfWidth: .44, structure: 'fractured-top-authored-edge-event-side-mass' };
  return geometry;
}

function worldMappedMaterial(
  parameters: ConstructorParameters<typeof MeshStandardMaterial>[0],
  texelMeters: number,
): MeshStandardMaterial {
  const material = new MeshStandardMaterial(parameters);
  material.onBeforeCompile = (shader) => {
    shader.vertexShader = `varying vec3 tideWorldPosition;\n${shader.vertexShader}`.replace(
      '#include <worldpos_vertex>',
      '#include <worldpos_vertex>\n  tideWorldPosition = worldPosition.xyz;',
    );
    shader.fragmentShader = `varying vec3 tideWorldPosition;\n${shader.fragmentShader}`.replace(
      '#include <map_fragment>',
      `#ifdef USE_MAP
        vec2 tideWorldUv = fract(tideWorldPosition.xz / ${texelMeters.toFixed(3)});
        vec4 sampledDiffuseColor = texture2D( map, tideWorldUv );
        diffuseColor *= sampledDiffuseColor;
      #endif`,
    );
  };
  material.customProgramCacheKey = () => `tide-world-map-${texelMeters}`;
  return material;
}

export interface RigDimensions {
  width: number;
  height: number;
  depth: number;
}

/**
 * Rigs are positioned from their feet/ground root. Keep screen evidence above
 * that root instead of projecting a symmetric box through the road surface.
 */
export function groundAnchoredBounds(root: Vector3, dimensions: RigDimensions, scale = 1): {
  center: Vector3;
  halfExtent: Vector3;
} {
  const width = dimensions.width * scale;
  const height = dimensions.height * scale;
  const depth = dimensions.depth * scale;
  return {
    center: root.clone().add(new Vector3(0, height / 2, 0)),
    halfExtent: new Vector3(width / 2, height / 2, depth / 2),
  };
}

export function pursuerScreenGapPx(
  runnerBounds: ClippedScreenBounds | null,
  pursuerBounds: ClippedScreenBounds | null,
  captured: boolean,
): number | null {
  if (captured || !runnerBounds || !pursuerBounds) return null;
  return pursuerBounds.top - runnerBounds.bottom;
}

export function projectOrientedBounds(
  camera: PerspectiveCamera,
  center: Vector3,
  halfExtent: Vector3,
  width: number,
  height: number,
  yaw: number,
): ClippedScreenBounds | null {
  const points: Vector3[] = [];
  const cosine = Math.cos(yaw);
  const sine = Math.sin(yaw);
  for (const x of [-halfExtent.x, halfExtent.x]) {
    for (const y of [-halfExtent.y, halfExtent.y]) {
      for (const z of [-halfExtent.z, halfExtent.z]) {
        points.push(new Vector3(
          center.x + x * cosine + z * sine,
          center.y + y,
          center.z - x * sine + z * cosine,
        ));
      }
    }
  }
  const projected = points.map((point) => point.project(camera));
  if (!projected.some((point) => point.z >= -1 && point.z <= 1)) return null;
  const left = Math.max(0, Math.min(...projected.map((point) => (point.x * 0.5 + 0.5) * width)));
  const right = Math.min(width, Math.max(...projected.map((point) => (point.x * 0.5 + 0.5) * width)));
  const top = Math.max(0, Math.min(...projected.map((point) => (-point.y * 0.5 + 0.5) * height)));
  const bottom = Math.min(height, Math.max(...projected.map((point) => (-point.y * 0.5 + 0.5) * height)));
  const clippedWidth = Math.max(0, right - left);
  const clippedHeight = Math.max(0, bottom - top);
  const area = clippedWidth * clippedHeight;
  return area > 0 ? { left, top, right, bottom, width: clippedWidth, height: clippedHeight, area } : null;
}

function polygonArea(points: readonly { x: number; y: number }[]): number {
  if (points.length < 3) return 0;
  let area = 0;
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index]!;
    const next = points[(index + 1) % points.length]!;
    area += current.x * next.y - next.x * current.y;
  }
  return Math.abs(area) / 2;
}

function clipHomogeneousPolygon(
  polygon: readonly Vector4[],
  distance: (point: Vector4) => number,
): Vector4[] {
  if (polygon.length === 0) return [];
  const output: Vector4[] = [];
  let previous = polygon.at(-1)!;
  let previousDistance = distance(previous);
  for (const current of polygon) {
    const currentDistance = distance(current);
    const previousInside = previousDistance >= 0;
    const currentInside = currentDistance >= 0;
    if (previousInside !== currentInside) {
      const ratio = previousDistance / (previousDistance - currentDistance);
      output.push(previous.clone().lerp(current, ratio));
    }
    if (currentInside) output.push(current.clone());
    previous = current;
    previousDistance = currentDistance;
  }
  return output;
}

/** Projects one real Tide Scar quad through full clip-space/frustum clipping. */
export function projectTideScarSegment(
  camera: PerspectiveCamera,
  segment: TideScarWorldSegment,
  width: number,
  height: number,
  pixelRatio: number,
): TideScarScreenSegment | null {
  let polygon = segment.points.map((point) => new Vector4(point.x, point.y, point.z, 1)
    .applyMatrix4(camera.matrixWorldInverse)
    .applyMatrix4(camera.projectionMatrix));
  const planes = [
    (point: Vector4) => point.x + point.w,
    (point: Vector4) => point.w - point.x,
    (point: Vector4) => point.y + point.w,
    (point: Vector4) => point.w - point.y,
    (point: Vector4) => point.z + point.w,
    (point: Vector4) => point.w - point.z,
  ];
  for (const plane of planes) polygon = clipHomogeneousPolygon(polygon, plane);
  if (polygon.length < 3) return null;
  const polygonCss = polygon.map((point) => ({
    x: MathUtils.clamp((point.x / point.w * 0.5 + 0.5) * width, 0, width),
    y: MathUtils.clamp((-point.y / point.w * 0.5 + 0.5) * height, 0, height),
  }));
  const visibleAreaPx = polygonArea(polygonCss);
  if (visibleAreaPx <= 0) return null;
  return {
    sectionId: segment.sectionId,
    intervalIndex: segment.intervalIndex,
    segmentIndex: segment.segmentIndex,
    polygonCss,
    pixelBounds: {
      left: Math.floor(Math.min(...polygonCss.map((point) => point.x)) * pixelRatio),
      top: Math.floor(Math.min(...polygonCss.map((point) => point.y)) * pixelRatio),
      right: Math.ceil(Math.max(...polygonCss.map((point) => point.x)) * pixelRatio),
      bottom: Math.ceil(Math.max(...polygonCss.map((point) => point.y)) * pixelRatio),
    },
    visibleAreaPx,
  };
}

export interface D4CompositionMeasurement {
  pitchDegrees: number;
  horizonY: number;
  vanishingPoint: { x: number; y: number };
  bottomRoadWidth: number;
}

export function applyD4LensShift(camera: PerspectiveCamera, profile: D4Profile): void {
  camera.projectionMatrix.elements[9] = profile.lensShiftY;
  camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
}

export function applyTR4RuntimeLensShift(camera: PerspectiveCamera, profile: D4Profile): void {
  camera.projectionMatrix.elements[9] = TR4_RUNTIME_CAMERA[profile.name].lensShiftY;
  camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
}
function screenPoint(camera: PerspectiveCamera, point: Vector3, width: number, height: number): { x: number; y: number } {
  const projected = point.clone().project(camera);
  return { x: (projected.x * 0.5 + 0.5) * width, y: (-projected.y * 0.5 + 0.5) * height };
}

function intersectScreenBottom(points: readonly { x: number; y: number }[], height: number): number | null {
  for (let index = 1; index < points.length; index += 1) {
    const previous = points[index - 1]!;
    const current = points[index]!;
    const previousOffset = previous.y - height;
    const currentOffset = current.y - height;
    if (previousOffset === 0) return previous.x;
    if (previousOffset * currentOffset > 0) continue;
    const fraction = previousOffset / (previousOffset - currentOffset);
    return MathUtils.lerp(previous.x, current.x, fraction);
  }
  return null;
}

/** Renderer-only camera evidence for the frozen D4 profile bands. */
export function measureD4Composition(
  camera: PerspectiveCamera,
  runnerPosition: Vector3,
  yaw: number,
  width: number,
  height: number,
  profile: D4Profile,
): D4CompositionMeasurement {
  const direction = camera.getWorldDirection(new Vector3());
  const pitchDegrees = Math.atan2(-direction.y, Math.hypot(direction.x, direction.z)) * 180 / Math.PI;
  const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
  const vanishingPoint = screenPoint(camera, runnerPosition.clone().addScaledVector(forward, 400), width, height);
  const leftRoad: { x: number; y: number }[] = [];
  const rightRoad: { x: number; y: number }[] = [];
  for (let distance = -2; distance <= 96; distance += 2) {
    const center = runnerPosition.clone().addScaledVector(forward, distance);
    leftRoad.push(screenPoint(camera, center.clone().addScaledVector(right, -WORLD_METRICS.roadWidth / 2), width, height));
    rightRoad.push(screenPoint(camera, center.clone().addScaledVector(right, WORLD_METRICS.roadWidth / 2), width, height));
  }
  const left = intersectScreenBottom(leftRoad, height);
  const rightEdge = intersectScreenBottom(rightRoad, height);
  let closestRoadWidth = 0;
  let closestRoadDistance = Number.POSITIVE_INFINITY;
  for (let index = 0; index < leftRoad.length; index += 1) {
    const roadY = (leftRoad[index]!.y + rightRoad[index]!.y) / 2;
    const distance = Math.abs(roadY - height);
    if (distance < closestRoadDistance) {
      closestRoadDistance = distance;
      closestRoadWidth = Math.abs(rightRoad[index]!.x - leftRoad[index]!.x);
    }
  }
  return {
    pitchDegrees,
    horizonY: MathUtils.clamp(vanishingPoint.y, 0, height),
    vanishingPoint: { x: MathUtils.clamp(vanishingPoint.x, 0, width), y: MathUtils.clamp(vanishingPoint.y, 0, height) },
    bottomRoadWidth: left === null || rightEdge === null ? closestRoadWidth : Math.abs(rightEdge - left),
  };
}

export interface PursuerProjectionCandidate {
  worldGap: number;
  scale: number;
  bounds: ClippedScreenBounds;
  screenGapPx: number;
}

/**
 * Presentation-only search over grounded positions. It intentionally derives
 * the final placement from the same rig extent and camera projection that QA
 * reports, so a missing candidate is observable rather than a hidden fallback.
 */
export function selectPursuerProjection(
  camera: PerspectiveCamera,
  viewport: { width: number; height: number },
  profile: D4Profile,
  runnerPosition: Vector3,
  yaw: number,
  chaseGap: number,
  scale: number,
): PursuerProjectionCandidate | null {
  const runner = groundAnchoredBounds(runnerPosition, RUNNER_RIG_BOUNDS);
  const runnerBounds = projectOrientedBounds(camera, runner.center, runner.halfExtent, viewport.width, viewport.height, yaw);
  if (!runnerBounds) return null;
  const normalized = MathUtils.clamp((chaseGap - 0.65) / 7.35, 0, 1);
  const targetTop = viewport.height * MathUtils.lerp(profile.pursuerCloseTopBand, profile.pursuerNormalTopBand, normalized);
  const minimumGap = d4MinimumPursuerGapPx(viewport.height);
  const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  let selected: PursuerProjectionCandidate | null = null;
  let bestScore = Number.POSITIVE_INFINITY;
  const bottomInset = Math.max(4, Math.round(viewport.height * 0.012));
  const profileScales = profile.mobileQuality
    ? [Math.min(scale, 0.8), 0.7, 0.62, 0.55]
    : [scale, 0.82, 0.7, 0.62];
  for (const candidateScale of [...new Set(profileScales)]) {
    for (let index = 0; index <= 80; index += 1) {
      const worldGap = 0.45 + index * 0.15;
      const root = runnerPosition.clone().addScaledVector(forward, -worldGap).add(new Vector3(0, 0.03, 0));
      const rig = groundAnchoredBounds(root, PURSUER_RIG_BOUNDS, candidateScale);
      const bounds = projectOrientedBounds(camera, rig.center, rig.halfExtent, viewport.width, viewport.height, yaw);
      const screenGapPx = pursuerScreenGapPx(runnerBounds, bounds, false);
      if (!bounds || screenGapPx === null || screenGapPx < minimumGap || bounds.bottom > viewport.height - bottomInset) continue;
      const score = Math.abs(bounds.top - targetTop) + (scale - candidateScale) * viewport.height * 0.12;
      if (score < bestScore) {
        bestScore = score;
        selected = { worldGap, scale: candidateScale, bounds, screenGapPx };
      }
    }
  }
  return selected;
}

export interface PursuerPresentation {
  visibleGap: number;
  scale: number;
  danger: number;
}

/**
 * Camera-only mapping for the grounded pursuer. Wide follow views have just a
 * narrow lower-road strip after the runner, whereas portrait holds more road.
 * Keep the root distance monotonic with canonical chaseGap in either view.
 */
export function pursuerPresentation(chaseGap: number, aspect: number, captured: boolean): PursuerPresentation {
  const normalizedGap = MathUtils.clamp((chaseGap - 0.65) / 7.35, 0, 1);
  const danger = MathUtils.clamp((4.5 - chaseGap) / 3.85, 0, 1);
  if (captured) return { visibleGap: 0.76, scale: 0.88, danger };

  const portrait = 1 - MathUtils.smoothstep(aspect, 0.5, 0.78);
  const nearGap = MathUtils.lerp(3.58, 4.18, portrait);
  const farGap = MathUtils.lerp(3.66, 5.1, portrait);
  return {
    visibleGap: MathUtils.lerp(nearGap, farGap, normalizedGap),
    // A stable silhouette keeps the grounded, scale-aware screen bounds real
    // in the shallow lower-road band without changing canonical chase distance.
    scale: MathUtils.lerp(0.9, 0.92, danger),
    danger,
  };
}

export function shouldShowPursuer(status: RunnerState['status'], elapsedTicks: number, distance: number): boolean {
  return status === 'ready' || status === 'game-over' || status === 'running' && elapsedTicks < 54 && distance < 6;
}

export class WorldRenderer {
  private renderer: WebGLRenderer | null = null;
  private readonly scene = new Scene();
  private readonly camera = new PerspectiveCamera(47, 16 / 9, 0.08, 520);
  private resizeObserver: ResizeObserver | null = null;
  private runner: RunnerRig | null = null;
  private elapsed = 0;
  private impact = 0;
  private pickupPulse = 0;
  private turnMotion: TurnMotion | null = null;
  private options: RenderOptions = { highContrast: false, reducedMotion: false };
  private readonly dummy = new Object3D();
  private readonly cameraLook = new Vector3();
  private readonly floorMaterial = worldMappedMaterial({ color: PALETTE.sandstone, roughness: 0.9, metalness: 0.01, vertexColors: true }, 2.7);
  private readonly railMaterial = worldMappedMaterial({ color: PALETTE.basaltEdge, roughness: 0.9, metalness: 0.02 }, 1.8);
  private readonly seamMaterial = new MeshStandardMaterial({ color: PALETTE.tideScar, roughness: 0.92, metalness: 0 });
  private readonly guideMaterial = new MeshStandardMaterial({ color: PALETTE.brass, roughness: 0.76, metalness: 0.12 });
  private readonly porcelainMaterial = new MeshStandardMaterial({ color: PALETTE.sandstoneShade, roughness: 0.94, metalness: 0 });
  private readonly rockMaterial = worldMappedMaterial({ color: PALETTE.basalt, roughness: 0.98, metalness: 0 }, 2.2);
  private readonly coralMaterial = new MeshStandardMaterial({ color: PALETTE.hazard, roughness: 0.88, metalness: 0 });
  private readonly beamMaterial = new MeshStandardMaterial({ color: PALETTE.sandstoneShade, roughness: 0.92, metalness: 0 });
  private readonly gateMaterial = new MeshStandardMaterial({ color: PALETTE.sandstoneShade, roughness: 0.86, metalness: 0.04 });
  private readonly columnMaterial = new MeshStandardMaterial({ color: PALETTE.sandstone, roughness: 0.96, metalness: 0 });
  private readonly dangerMaterial = new MeshStandardMaterial({ color: PALETTE.hazard, emissive: 0x2d0906, emissiveIntensity: 0.08, roughness: 0.86 });
  private readonly shardMaterial = new MeshStandardMaterial({ color: PALETTE.tideScar, emissive: PALETTE.tideScar, emissiveIntensity: 0.48, roughness: 0.4, metalness: 0.02 });
  private readonly shieldMaterial = new MeshBasicMaterial({ color: PALETTE.tideScar, transparent: true, opacity: 0.52, wireframe: true });
  private readonly floors = this.instances(new BoxGeometry(1, 1, 1), this.floorMaterial, MAX_SECTIONS);
  private readonly deckCaps = [0, 1, 2, 3, 4, 5].map((profile) => this.instances(createDeckCapGeometry(profile), this.floorMaterial, MAX_ROAD_MODULES_PER_SIGNATURE));
  private readonly rails = this.instances(new BoxGeometry(1, 1, 1), this.railMaterial, MAX_RAILS);
  private readonly seams = this.instances(new BoxGeometry(1, 1, 1), this.seamMaterial, MAX_SECTIONS * 3);
  private readonly laneGuides = this.instances(new BoxGeometry(1, 1, 1), this.guideMaterial, MAX_SECTIONS * 2);
  private readonly platforms = this.instances(new BoxGeometry(1, 1, 1), this.floorMaterial, MAX_SECTIONS + 1);
  private readonly pillars = this.instances(new CylinderGeometry(1, 1.18, 1, 7), this.porcelainMaterial, MAX_PILLARS);
  private readonly rocks = this.instances(new DodecahedronGeometry(1, 0), this.rockMaterial, MAX_ROCKS);
  private readonly coral = this.instances(new DodecahedronGeometry(1, 0), this.coralMaterial, MAX_CORAL);
  private readonly beams = this.instances(new BoxGeometry(1, 1, 1), this.beamMaterial, MAX_EVENTS);
  private readonly beamCuts = this.instances(new BoxGeometry(1, 1, 1), this.dangerMaterial, MAX_EVENTS * 4);
  private readonly rings = this.instances(new TorusGeometry(1, 0.14, 7, 18), this.gateMaterial, MAX_EVENTS);
  private readonly gatePosts = this.instances(new CylinderGeometry(0.12, 0.18, 1, 6), this.gateMaterial, MAX_EVENTS * 2);
  private readonly columns = this.instances(new DodecahedronGeometry(0.76, 0), this.columnMaterial, MAX_EVENTS);
  private readonly columnCaps = this.instances(new DodecahedronGeometry(0.64, 0), this.dangerMaterial, MAX_EVENTS);
  private readonly columnRubble = this.instances(new DodecahedronGeometry(0.34, 0), this.columnMaterial, MAX_EVENTS * 3);
  private readonly gapLips = this.instances(new BoxGeometry(1, 1, 1), this.dangerMaterial, MAX_EVENTS * 2);
  /** Invisible-to-color shared proxy: the one key-light shadow pass for near hazards. */
  private readonly hazardShadow = this.instances(new BoxGeometry(1, 1, 1), new MeshBasicMaterial({ colorWrite: false }), MAX_EVENTS);
  private readonly shards = this.instances(new IcosahedronGeometry(0.26, 0), this.shardMaterial, MAX_SHARDS);
  private readonly shields = this.instances(new IcosahedronGeometry(0.72, 1), this.shieldMaterial, 16);
  private readonly pursuer: PursuerRig = createPursuerRig();
  private readonly canyon = new TideScarWorld();
  private readonly tideScarRoad = new TideScarRoad();
  private readonly mist = this.createMist();
  private host: HTMLElement | null = null;
  private d4Assets: D4LoadedAssets | null = null;
  private d4AssetsLoading = false;
  private pendingD4AssetDimensions: { width: number; height: number } | null = null;
  private activeD4Profile: D4Profile = d4ProfileForViewport(1600, 900);
  private tideScarSnapshot: TideScarRoadSnapshot = { sections: [], vertexCount: 0, coverage: 0, segments: [] };
  private pursuerPlacementError: string | null = null;
  private visibleSections: CourseSection[] = [];
  private contextLossCount = 0;
  private snapshot: RenderSnapshot = {
    canvas: { width: 0, height: 0, resolution: 1 },
    options: { highContrast: false, reducedMotion: false },
    presentationAlpha: 1,
    presentedDistance: 0,
    presentedLanePosition: 0,
    runnerWorld: { x: 0, y: 0, z: 0, yaw: 0 },
    runnerScreen: { x: 0, y: 0, visible: false },
    pursuerScreen: { x: 0, y: 0, visible: false, bounds: null },
    pursuerGapPx: null,
    hazardScreens: [],
    tideScarSegments: [],
    camera: { x: 0, y: 0, z: 0, fov: 47, yaw: 0 },
    lanePosition: 0,
    posture: 'run',
    visibleSectionIds: [],
    visibleObstacleCount: 0,
    drawCalls: 0,
    triangles: 0,
    turnProgress: null,
    contextLossCount: 0,
    d4: {
      profile: 'desktop',
      fogDensity: TR4_FOG_DENSITY,
      assetTier: 'loading',
      requestedAssets: [],
      textureBytes: 0,
      tideScarVertices: 0,
      tideScarCoverage: 0,
      pursuerPlacementError: null,
      composition: { pitchDegrees: 0, horizonY: 0, vanishingPoint: { x: 0, y: 0 }, bottomRoadWidth: 0, runnerCenterY: 0 },
    },
  };

  constructor() {
    this.scene.background = new Color(TR4_FOG_COLOR);
    this.scene.fog = new FogExp2(TR4_FOG_COLOR, TR4_FOG_DENSITY);
    this.camera.position.set(0, 5.35, 8.1);
    this.scene.add(new HemisphereLight(0xd8e0df, PALETTE.tideDeep, 1.5));
    this.scene.add(new AmbientLight(0x708691, .38));
    const key = new DirectionalLight(0xffd7a0, 4.2);
    key.position.set(-10, 16, 7);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.normalBias = 0.02;
    this.scene.add(key);
    const rim = new DirectionalLight(0x638fa4, 1.1);
    rim.position.set(8, 8, 10);
    this.scene.add(rim);
    this.scene.add(
      this.floors,
      ...this.deckCaps,
      this.rails,
      this.seams,
      this.laneGuides,
      this.platforms,
      this.pillars,
      this.rocks,
      this.coral,
      this.beams,
      this.beamCuts,
      this.rings,
      this.gatePosts,
      this.columns,
      this.columnCaps,
      this.columnRubble,
      this.gapLips,
      this.hazardShadow,
      this.shards,
      this.shields,
      this.pursuer.root,
      this.canyon.root,
      this.tideScarRoad.mesh,
      this.mist,
    );
    for (const mesh of [this.floors, ...this.deckCaps, this.rails, this.platforms, this.rocks]) {
      mesh.receiveShadow = true;
    }
    for (const mesh of [this.beams, this.beamCuts, this.rings, this.gatePosts, this.columns, this.columnCaps, this.columnRubble, this.gapLips]) {
      mesh.receiveShadow = true;
    }
    this.hazardShadow.castShadow = true;
    this.pursuer.shadowCaster.castShadow = true;
  }

  async init(host: HTMLElement): Promise<void> {
    const renderer = new WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.94;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = PCFShadowMap;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(host.clientWidth, host.clientHeight, false);
    renderer.domElement.dataset.testid = 'runner-canvas';
    renderer.domElement.setAttribute('aria-label', 'TIDE RELAY third-person endless runner world');
    renderer.domElement.setAttribute('role', 'application');
    renderer.domElement.tabIndex = 0;
    renderer.domElement.addEventListener('webglcontextlost', this.onContextLost);
    host.appendChild(renderer.domElement);
    this.renderer = renderer;
    this.host = host;
    this.runner = createRunnerRig();
    this.runner.shadowCaster.castShadow = true;
    this.scene.add(this.runner.root);
    this.resizeObserver = new ResizeObserver(() => this.resize(host));
    this.resizeObserver.observe(host);
    this.resize(host);
  }

  get canvas(): HTMLCanvasElement | null {
    return this.renderer?.domElement ?? null;
  }

  setOptions(options: Partial<RenderOptions>): void {
    this.options = { ...this.options, ...options };
    this.scene.fog = new FogExp2(this.options.highContrast ? 0x71828a : TR4_FOG_COLOR,
      canyonFogDensity(this.activeD4Profile, this.options.highContrast));
    this.dangerMaterial.emissiveIntensity = this.options.highContrast ? 0.3 : 0.08;
    if (this.options.reducedMotion) {
      this.impact = 0;
      this.pickupPulse = 0;
    }
  }

  render(previous: RunnerState, state: RunnerState, alpha: number, events: readonly RunnerEvent[], deltaMs: number): void {
    const renderer = this.renderer;
    const rig = this.runner;
    if (!renderer || !rig) return;
    this.elapsed += Math.min(0.05, Math.max(0, deltaMs / 1000));
    this.consumeEvents(state, events);
    this.syncTurnMotion(state);
    this.impact = Math.max(0, this.impact - deltaMs / 210);
    this.pickupPulse = Math.max(0, this.pickupPulse - deltaMs / 180);

    const previousSample = sampleRunnerPosition(previous);
    const currentSample = sampleRunnerPosition(state);
    const mix = MathUtils.clamp(alpha, 0, 1);
    const presentedDistance = MathUtils.lerp(previous.distance, state.distance, mix);
    const presentedLanePosition = MathUtils.lerp(
      previous.runner.lanePosition,
      state.runner.lanePosition,
      mix,
    );
    let position = new Vector3(
      MathUtils.lerp(previousSample.x, currentSample.x, mix),
      MathUtils.lerp(previousSample.y, currentSample.y, mix),
      MathUtils.lerp(previousSample.z, currentSample.z, mix),
    );
    let yaw = currentSample.yaw;
    if (this.turnMotion) {
      const motion = this.turnMotion;
      const rawProgress = motion.override ?? motion.progress;
      if (rawProgress >= 1 && motion.override === null) {
        this.turnMotion = null;
      } else {
        const progress = easeInOut(rawProgress);
        const curvePosition = cubicBezier(
          motion.start,
          motion.controlOne,
          motion.controlTwo,
          motion.end,
          progress,
        );
        curvePosition.y = position.y;
        yaw = shortestAngle(motion.fromYaw, motion.toYaw, progress);
        const laneOffset = turnLaneOffset(yaw, motion.baseLanePosition, presentedLanePosition);
        curvePosition.x += laneOffset.x;
        curvePosition.z += laneOffset.z;
        position = curvePosition;
      }
    }
    rig.root.position.copy(position);
    rig.root.rotation.y = yaw;
    const laneDelta = state.runner.targetLane - state.runner.lanePosition;
    rig.core.scale.setScalar(1 + this.pickupPulse * 0.55);
    updateRunnerRig(rig, {
      elapsed: this.elapsed,
      speed: state.speed,
      laneDelta,
      height: position.y,
      posture: postureOf(state),
      shield: state.runner.shieldCharges > 0,
      reducedMotion: this.options.reducedMotion,
      dead: state.status === 'game-over',
    });

    this.updateCourse(state);
    this.updateCamera(state, position, yaw, deltaMs);
    this.canyon.update(position, yaw, this.activeD4Profile.name);
    this.updatePursuer(state, position, yaw);
    renderer.render(this.scene, this.camera);
    this.updateSnapshot(
      state,
      position,
      yaw,
      mix,
      presentedDistance,
      presentedLanePosition,
    );
    if (this.turnMotion?.progress === 1 && this.turnMotion.override === null) this.turnMotion = null;
  }

  setTurnProgress(progress: number): void {
    if (!this.turnMotion) return;
    this.turnMotion.override = MathUtils.clamp(progress, 0, 1);
  }

  clearTurnProgressOverride(): void {
    if (this.turnMotion) this.turnMotion.override = null;
  }

  getSnapshot(): RenderSnapshot {
    return structuredClone(this.snapshot);
  }

  benchmark(state: RunnerState, iterations = 120): { meanMs: number; p95Ms: number; maxMs: number } {
    const samples: number[] = [];
    for (let index = 0; index < Math.max(1, iterations); index += 1) {
      const start = performance.now();
      this.updateCourse(state);
      samples.push(performance.now() - start);
    }
    samples.sort((a, b) => a - b);
    return {
      meanMs: samples.reduce((sum, value) => sum + value, 0) / samples.length,
      p95Ms: samples[Math.min(samples.length - 1, Math.floor(samples.length * 0.95))] ?? 0,
      maxMs: samples.at(-1) ?? 0,
    };
  }

  destroy(): void {
    this.resizeObserver?.disconnect();
    this.resizeObserver = null;
    this.host = null;
    this.pendingD4AssetDimensions = null;
    this.clearD4MaterialMaps();
    this.d4Assets?.dispose();
    this.d4Assets = null;
    this.canyon.dispose();
    this.scene.remove(this.canyon.root);
    const renderer = this.renderer;
    this.renderer = null;
    if (renderer) {
      renderer.domElement.removeEventListener('webglcontextlost', this.onContextLost);
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    }
    const geometries = new Set<BufferGeometry>();
    const materials = new Set<MeshStandardMaterial | MeshBasicMaterial | PointsMaterial>();
    this.scene.traverse((object) => {
      if (object instanceof Mesh || object instanceof InstancedMesh || object instanceof Points) {
        geometries.add(object.geometry);
        const values = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of values) materials.add(material as MeshStandardMaterial | MeshBasicMaterial | PointsMaterial);
      }
    });
    for (const geometry of geometries) geometry.dispose();
    for (const material of materials) material.dispose();
  }

  private instances(geometry: BufferGeometry, material: MeshStandardMaterial | MeshBasicMaterial, capacity: number): InstancedMesh {
    const mesh = new InstancedMesh(geometry, material, capacity);
    mesh.instanceMatrix.setUsage(DynamicDrawUsage);
    mesh.count = 0;
    mesh.frustumCulled = false;
    return mesh;
  }

  private resize(host: HTMLElement): void {
    const renderer = this.renderer;
    if (!renderer) return;
    const width = Math.max(1, host.clientWidth);
    const height = Math.max(1, host.clientHeight);
    this.activeD4Profile = d4ProfileForViewport(width, height);
    const pixelRatio = Math.min(window.devicePixelRatio || 1, this.activeD4Profile.mobileQuality ? 1.5 : 2);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.fov = this.activeD4Profile.fov;
    this.camera.updateProjectionMatrix();
    this.requestD4Assets(width, height);
  }

  private requestD4Assets(width: number, height: number): void {
    const coarsePointer = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches;
    const deviceMemory = (typeof navigator !== 'undefined' ? (navigator as Navigator & { deviceMemory?: number }).deviceMemory : undefined);
    const capabilities = { cssWidth: width, cssHeight: height, coarsePointer, deviceMemory };
    const selection = selectD4Assets(capabilities);
    if (this.d4AssetsLoading) {
      this.pendingD4AssetDimensions = { width, height };
      return;
    }
    if (this.d4Assets?.tier === selection.tier) return;
    this.clearD4MaterialMaps();
    this.d4Assets?.dispose();
    this.d4Assets = null;
    this.d4AssetsLoading = true;
    void loadD4Assets(capabilities).then((assets) => {
      if (!this.renderer) {
        assets.dispose();
        return;
      }
      this.d4Assets = assets;
      if (assets.textures) {
        const anisotropy = Math.min(4, this.renderer?.capabilities.getMaxAnisotropy() ?? 1);
        assets.textures.sandstone.anisotropy = anisotropy;
        assets.textures.basalt.anisotropy = anisotropy;
        this.floorMaterial.map = assets.textures.sandstone;
        this.railMaterial.map = assets.textures.basalt;
        this.rockMaterial.map = assets.textures.basalt;
        this.canyon.setSurfaceMap(assets.textures.basalt);
        this.coralMaterial.alphaMap = assets.textures.coral;
        this.coralMaterial.transparent = true;
      } else {
        this.clearD4MaterialMaps();
      }
      this.floorMaterial.needsUpdate = true;
      this.railMaterial.needsUpdate = true;
      this.rockMaterial.needsUpdate = true;
      this.coralMaterial.needsUpdate = true;
    }).finally(() => {
      this.d4AssetsLoading = false;
      const pending = this.pendingD4AssetDimensions;
      this.pendingD4AssetDimensions = null;
      if (pending) this.requestD4Assets(pending.width, pending.height);
    });
  }

  private clearD4MaterialMaps(): void {
    this.floorMaterial.map = null;
    this.railMaterial.map = null;
    this.rockMaterial.map = null;
    this.canyon.setSurfaceMap(null);
    this.coralMaterial.alphaMap = null;
    this.coralMaterial.transparent = false;
    this.floorMaterial.needsUpdate = true;
    this.railMaterial.needsUpdate = true;
    this.rockMaterial.needsUpdate = true;
    this.coralMaterial.needsUpdate = true;
  }

  private consumeEvents(state: RunnerState, events: readonly RunnerEvent[]): void {
    for (const event of events) {
      if (event.type === 'turned') {
        const from = state.course.sections.find((section) => section.id === event.fromSectionId);
        const to = state.course.sections.find((section) => section.id === event.toSectionId);
        if (from && to) {
          if (
            this.turnMotion?.fromSectionId !== from.id ||
            this.turnMotion.toSectionId !== to.id
          ) {
            this.turnMotion = this.createTurnMotion(
              from,
              to,
              event.direction,
              state.runner.lanePosition,
              0.5,
            );
          }
        }
      } else if (event.type === 'collision' || event.type === 'stumbled' || event.type === 'run-failed') {
        this.impact = this.options.reducedMotion ? 0 : 1;
      } else if (event.type === 'pickup-collected') {
        this.pickupPulse = this.options.reducedMotion ? 0 : 1;
      }
    }
  }

  private createTurnMotion(
    from: CourseSection,
    to: CourseSection,
    direction: TurnDirection,
    lanePosition: number,
    progress: number,
  ): TurnMotion {
    const pivot = sectionEnd(from);
    const incoming = headingVector(from.heading);
    const outgoing = headingVector(to.heading);
    const incomingRight = rightVector(from.heading);
    const outgoingRight = rightVector(to.heading);
    const laneOffset = lanePosition * WORLD_METRICS.laneWidth;
    const start = new Vector3(
      pivot.x - incoming.x * TURN_VISUAL_RADIUS + incomingRight.x * laneOffset,
      0,
      pivot.z - incoming.z * TURN_VISUAL_RADIUS + incomingRight.z * laneOffset,
    );
    const end = new Vector3(
      pivot.x + outgoing.x * TURN_VISUAL_RADIUS + outgoingRight.x * laneOffset,
      0,
      pivot.z + outgoing.z * TURN_VISUAL_RADIUS + outgoingRight.z * laneOffset,
    );
    const tangentLength = TURN_VISUAL_RADIUS * 0.72;
    const controlOne = start.clone().add(new Vector3(incoming.x * tangentLength, 0, incoming.z * tangentLength));
    const controlTwo = end.clone().add(new Vector3(-outgoing.x * tangentLength, 0, -outgoing.z * tangentLength));
    return {
      direction,
      fromSectionId: from.id,
      toSectionId: to.id,
      fromYaw: headingYaw(from.heading),
      toYaw: headingYaw(to.heading),
      baseLanePosition: lanePosition,
      progress: MathUtils.clamp(progress, 0, 1),
      override: null,
      start,
      controlOne,
      controlTwo,
      end,
    };
  }

  private syncTurnMotion(state: RunnerState): void {
    const current = getCurrentSection(state);
    if (!this.turnMotion && state.queuedTurn && current.length - state.sectionDistance <= TURN_VISUAL_RADIUS) {
      const next = state.course.sections.find((section) => section.index === current.index + 1);
      if (next) {
        const progress = 0.5 * MathUtils.clamp(
          (state.sectionDistance - (current.length - TURN_VISUAL_RADIUS)) / TURN_VISUAL_RADIUS,
          0,
          1,
        );
        this.turnMotion = this.createTurnMotion(
          current,
          next,
          state.queuedTurn,
          state.runner.lanePosition,
          progress,
        );
      }
    }
    const motion = this.turnMotion;
    if (!motion || motion.override !== null) return;
    const from = state.course.sections.find((section) => section.id === motion.fromSectionId);
    const to = state.course.sections.find((section) => section.id === motion.toSectionId);
    if (!from || !to) {
      this.turnMotion = null;
      return;
    }
    if (state.sectionIndex === from.index) {
      motion.progress = 0.5 * MathUtils.clamp(
        (state.sectionDistance - (from.length - TURN_VISUAL_RADIUS)) / TURN_VISUAL_RADIUS,
        0,
        1,
      );
    } else if (state.sectionIndex === to.index) {
      motion.progress = 0.5 + 0.5 * MathUtils.clamp(state.sectionDistance / TURN_VISUAL_RADIUS, 0, 1);
    } else if (state.sectionIndex > to.index) {
      motion.progress = 1;
    }
  }

  private updateCourse(state: RunnerState): void {
    const resolved = new Set([...state.resolvedEventIds, ...state.consumedEventIds]);
    this.visibleSections = state.course.sections
      .filter((section) => section.index >= state.sectionIndex - 1 && section.index <= state.sectionIndex + 5)
      .slice(0, MAX_SECTIONS);
    let floorCount = 0;
    const deckCapCounts = [0, 0, 0, 0, 0, 0];
    let railCount = 0;
    let seamCount = 0;
    let laneGuideCount = 0;
    let platformCount = 0;
    let pillarCount = 0;
    let rockCount = 0;
    let coralCount = 0;
    let beamCount = 0;
    let beamCutCount = 0;
    let ringCount = 0;
    let gatePostCount = 0;
    let columnCount = 0;
    let columnCapCount = 0;
    let columnRubbleCount = 0;
    let gapLipCount = 0;
    let hazardShadowCount = 0;
    let shardCount = 0;
    let shieldCount = 0;

    for (const section of this.visibleSections) {
      const yaw = headingYaw(section.heading);
      const right = rightVector(section.heading);
      const gapIntervals = section.events
        .filter((event): event is CourseEvent & { kind: 'gap' } => event.kind === 'gap')
        .map((event) => [event.at, Math.min(section.length, event.at + event.length)] as const)
        .sort((a, b) => a[0] - b[0]);
      const roadIntervals: [number, number][] = [];
      let intervalStart = presentationRoadStart(section.index);
      for (const [gapStart, gapEnd] of gapIntervals) {
        if (gapStart > intervalStart) roadIntervals.push([intervalStart, gapStart]);
        intervalStart = Math.max(intervalStart, gapEnd);
      }
      if (intervalStart < section.length) roadIntervals.push([intervalStart, section.length]);
      let moduleIndex = 0;
      for (const [start, end] of roadIntervals) {
        let cursor = start;
        while (end - cursor > 0.2) {
          const remaining = end - cursor;
          let moduleLength = Math.min(11, 6 + seededUnit(section.index * 31 + moduleIndex, 733) * 5);
          if (remaining <= 11) moduleLength = remaining;
          else if (remaining - moduleLength < 6) moduleLength = remaining - 6;
          const signature = Math.floor(seededUnit(section.index * 37 + moduleIndex, 739) * this.deckCaps.length) % this.deckCaps.length;
          const cap = this.deckCaps[signature];
          if (cap) {
            const center = sampleCoursePosition(section, cursor + moduleLength / 2);
            this.setInstance(cap, deckCapCounts[signature]++, center.x, 0, center.z, yaw, WORLD_METRICS.roadWidth, 1, moduleLength + 0.06);
          }
          cursor += moduleLength;
          moduleIndex += 1;
        }
      }

      for (let marker = 0; marker < 3; marker += 1) {
        const along = 12 + marker * Math.max(16, (section.length - 24) / 2);
        const sample = sampleCoursePosition(section, Math.min(section.length - 6, along));
        for (const side of [-1, 1] as const) {
          const variance = seededUnit(section.index, marker * 2 + (side > 0 ? 1 : 0));
          if ((marker + section.index + (side > 0 ? 1 : 0)) % 4 === 0) {
            const coralInset = WORLD_METRICS.roadWidth / 2 + 0.42 + variance * 0.28;
            this.setInstance(this.coral, coralCount++, sample.x + right.x * coralInset * side, 0.16, sample.z + right.z * coralInset * side, variance * Math.PI, 0.18 + variance * 0.16, 0.44 + variance * 0.34, 0.18 + variance * 0.18);
          }
        }
      }

      for (const event of section.events) {
        if (resolved.has(event.id)) continue;
        const sample = sampleCoursePosition(section, event.at, event.lane === 'all' ? 0 : event.lane);
        if (event.kind === 'beam') {
          const width = event.lane === 'all' ? WORLD_METRICS.roadWidth - 0.5 : 1.65;
          this.setInstance(this.beams, beamCount++, sample.x, 0.36, sample.z, yaw, width, 0.56, 0.58);
          const capOffset = Math.max(0.34, width / 2 - 0.14);
          this.setInstance(this.beamCuts, beamCutCount++, sample.x + right.x * capOffset, 0.28, sample.z + right.z * capOffset, yaw, 0.25, 0.62, 0.62);
          this.setInstance(this.beamCuts, beamCutCount++, sample.x - right.x * capOffset, 0.28, sample.z - right.z * capOffset, yaw, 0.25, 0.62, 0.62);
          this.setInstance(this.hazardShadow, hazardShadowCount++, sample.x, 0.31, sample.z, yaw, width, 0.54, 0.56);
        } else if (event.kind === 'ring') {
          const widthScale = event.lane === 'all' ? WORLD_METRICS.roadWidth / 2.15 : 1;
          const ringY = event.lane === 'all' ? 1.12 : 0.96;
          this.setInstance(this.rings, ringCount++, sample.x, ringY, sample.z, yaw, widthScale, event.lane === 'all' ? 0.86 : 0.68, 1);
          const postOffset = event.lane === 'all' ? WORLD_METRICS.roadWidth / 2 - 0.48 : 0.92;
          this.setInstance(this.gatePosts, gatePostCount++, sample.x + right.x * postOffset, 0.64, sample.z + right.z * postOffset, yaw, 1, 1.28, 1);
          this.setInstance(this.gatePosts, gatePostCount++, sample.x - right.x * postOffset, 0.64, sample.z - right.z * postOffset, yaw, 1, 1.28, 1);
          this.setInstance(this.hazardShadow, hazardShadowCount++, sample.x, ringY, sample.z, yaw, widthScale * 2, event.lane === 'all' ? 1.9 : 1.5, 0.32);
        } else if (event.kind === 'column') {
          this.setInstance(this.columns, columnCount++, sample.x, 0.92, sample.z, yaw + 0.12, 0.94, 1.36, 0.9);
          this.setInstance(this.hazardShadow, hazardShadowCount++, sample.x, 0.92, sample.z, yaw, 0.94, 1.36, 0.9);
        } else if (event.kind === 'gap') {
          const width = event.lane === 'all' ? WORLD_METRICS.roadWidth - 0.5 : WORLD_METRICS.laneWidth * 0.9;
          const farSample = sampleCoursePosition(section, event.at + event.length, event.lane === 'all' ? 0 : event.lane);
          this.setInstance(this.gapLips, gapLipCount++, sample.x, 0.08, sample.z, yaw, width, 0.18, 0.22);
          this.setInstance(this.gapLips, gapLipCount++, farSample.x, 0.08, farSample.z, yaw, width, 0.18, 0.22);
        } else if (event.kind === 'shard') {
          const bob = this.options.reducedMotion ? 0 : Math.sin(this.elapsed * 3.2 + event.at) * 0.13;
          const rotation = this.options.reducedMotion ? event.at * 0.17 : this.elapsed * 1.6 + event.at;
          this.setInstance(this.shards, shardCount++, sample.x, 1.05 + bob, sample.z, rotation, 1, 1.4, 1);
        } else if (event.kind === 'shield') {
          const rotation = this.options.reducedMotion ? event.at * 0.11 : this.elapsed * 0.8;
          this.setInstance(this.shields, shieldCount++, sample.x, 1.05, sample.z, rotation, 1, 1, 1);
        }
      }
    }
    this.finishInstances(this.floors, floorCount);
    this.deckCaps.forEach((cap, index) => this.finishInstances(cap, deckCapCounts[index] ?? 0));
    this.finishInstances(this.rails, railCount);
    this.finishInstances(this.seams, seamCount);
    this.finishInstances(this.laneGuides, laneGuideCount);
    this.finishInstances(this.platforms, platformCount);
    this.finishInstances(this.pillars, pillarCount);
    this.finishInstances(this.rocks, rockCount);
    this.finishInstances(this.coral, coralCount);
    this.finishInstances(this.beams, beamCount);
    this.finishInstances(this.beamCuts, beamCutCount);
    this.finishInstances(this.rings, ringCount);
    this.finishInstances(this.gatePosts, gatePostCount);
    this.finishInstances(this.columns, columnCount);
    this.finishInstances(this.columnCaps, columnCapCount);
    this.finishInstances(this.columnRubble, columnRubbleCount);
    this.finishInstances(this.gapLips, gapLipCount);
    this.finishInstances(this.hazardShadow, hazardShadowCount);
    this.finishInstances(this.shards, shardCount);
    this.finishInstances(this.shields, shieldCount);
    const unresolved = new Set(this.visibleSections.flatMap((section) => section.events
      .filter((event) => !resolved.has(event.id))
      .map((event) => event.id)));
    this.tideScarSnapshot = this.tideScarRoad.update(this.visibleSections, unresolved);
  }

  private setInstance(mesh: InstancedMesh, index: number, x: number, y: number, z: number, yaw: number, sx: number, sy: number, sz: number): void {
    if (index >= mesh.instanceMatrix.count) return;
    this.dummy.position.set(x, y, z);
    this.dummy.rotation.set(0, yaw, 0);
    this.dummy.scale.set(sx, sy, sz);
    this.dummy.updateMatrix();
    mesh.setMatrixAt(index, this.dummy.matrix);
  }

  private finishInstances(mesh: InstancedMesh, count: number): void {
    mesh.count = Math.min(count, mesh.instanceMatrix.count);
    mesh.instanceMatrix.needsUpdate = true;
  }

  private updateCamera(state: RunnerState, position: Vector3, yaw: number, deltaMs: number): void {
    const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
    const profile = this.activeD4Profile;
    const cameraRecord = TR4_RUNTIME_CAMERA[profile.name];
    const targetPosition = position.clone().addScaledVector(forward, -cameraRecord.back);
    targetPosition.y = cameraRecord.height + position.y * 0.18 - (state.runner.slideTicksRemaining > 0 ? 0.12 : 0);
    targetPosition.addScaledVector(right, -state.runner.lanePosition * profile.cameraLaneBias);
    if (this.impact > 0 && !this.options.reducedMotion) {
      targetPosition.addScaledVector(right, Math.sin(this.elapsed * 95) * this.impact * 0.12);
      targetPosition.y += Math.cos(this.elapsed * 82) * this.impact * 0.07;
    }
    const damping = 1 - Math.exp(-Math.max(0.001, deltaMs / 1000) * (this.turnMotion ? 7.5 : 10));
    if (
      this.camera.position.lengthSq() < 0.001 ||
      this.camera.position.distanceToSquared(targetPosition) > 12 * 12
    ) this.camera.position.copy(targetPosition);
    else this.camera.position.lerp(targetPosition, damping);
    this.cameraLook.copy(position).addScaledVector(forward, cameraRecord.targetAhead).add(new Vector3(0, cameraRecord.targetY + position.y * 0.1, 0));
    this.camera.lookAt(this.cameraLook);
    this.camera.fov = cameraRecord.fov;
    const fog = this.scene.fog;
    if (fog instanceof FogExp2) fog.density = canyonFogDensity(profile, this.options.highContrast);
    this.camera.updateProjectionMatrix();
    // Preserve the frozen FOV/look target while shifting the asymmetric lens
    // into the documented runner/road bands; presentation only.
    applyTR4RuntimeLensShift(this.camera, profile);
  }

  private createMist(): Points {
    const count = 120;
    const positions = new Float32Array(count * 3);
    for (let index = 0; index < count; index += 1) {
      positions[index * 3] = (seededUnit(index, 1) - 0.5) * 22;
      positions[index * 3 + 1] = seededUnit(index, 2) * 7 - 1;
      positions[index * 3 + 2] = (seededUnit(index, 3) - 0.5) * 42;
    }
    const geometry = new BufferGeometry();
    geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
    const material = new PointsMaterial({ color: PALETTE.tideLight, size: 1.15, sizeAttenuation: false, transparent: true, opacity: 0.13, depthWrite: false });
    return new Points(geometry, material);
  }

  private updatePursuer(state: RunnerState, position: Vector3, yaw: number): void {
    const visible = shouldShowPursuer(state.status, state.elapsedTicks, state.distance);
    if (!visible) {
      this.pursuer.root.visible = false;
      this.mist.visible = false;
      this.pursuerPlacementError = null;
      return;
    }
    const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const captured = state.status === 'game-over' && state.failureReason?.kind === 'pursuer-caught';
    const presentation = pursuerPresentation(state.chaseGap, this.camera.aspect, captured);
    const size = this.renderer?.getSize(new Vector2()) ?? new Vector2(1, 1);
    const placement = captured ? null : selectPursuerProjection(
      this.camera,
      { width: size.x, height: size.y },
      this.activeD4Profile,
      position,
      yaw,
      state.chaseGap,
      presentation.scale,
    );
    this.pursuerPlacementError = !captured && !placement
      ? `No grounded pursuer projection for ${this.activeD4Profile.name} at chaseGap=${state.chaseGap.toFixed(3)}`
      : null;
    const visibleGap = captured ? .42 : placement?.worldGap ?? presentation.visibleGap;
    this.pursuer.root.position.copy(position).addScaledVector(forward, -visibleGap);
    this.pursuer.root.position.y = 0.03;
    this.pursuer.root.rotation.y = yaw;
    this.pursuer.root.scale.setScalar(placement?.scale ?? presentation.scale);
    updatePursuerRig(this.pursuer, {
      elapsed: this.elapsed,
      danger: presentation.danger,
      reducedMotion: this.options.reducedMotion,
      stumble: state.runner.speedPenaltyTicks > 0,
      captured,
    });
    this.pursuer.root.visible = true;
    this.mist.position.copy(position).addScaledVector(forward, -Math.min(6.4, visibleGap + 0.7));
    this.mist.visible = state.status === 'running' && !this.options.reducedMotion && state.chaseGap > 2.4;
  }

  private updateSnapshot(
    state: RunnerState,
    position: Vector3,
    yaw: number,
    presentationAlpha: number,
    presentedDistance: number,
    presentedLanePosition: number,
  ): void {
    const renderer = this.renderer;
    if (!renderer) return;
    const screen = position.clone().add(new Vector3(0, 1, 0)).project(this.camera);
    const pursuer = this.pursuer.root.visible
      ? this.pursuer.root.position.clone().add(new Vector3(0, .9, 0)).project(this.camera)
      : null;
    const size = renderer.getSize(new Vector2());
    const width = size.x;
    const height = size.y;
    const runnerRigBounds = groundAnchoredBounds(position, RUNNER_RIG_BOUNDS);
    const pursuerRigBounds = this.pursuer.root.visible
      ? groundAnchoredBounds(this.pursuer.root.position, PURSUER_RIG_BOUNDS, this.pursuer.root.scale.x)
      : null;
    const runnerBounds = this.clippedBounds(runnerRigBounds.center, runnerRigBounds.halfExtent, width, height, yaw);
    const pursuerBounds = pursuerRigBounds
      ? this.clippedBounds(pursuerRigBounds.center, pursuerRigBounds.halfExtent, width, height, this.pursuer.root.rotation.y)
      : null;
    const captured = state.status === 'game-over' && state.failureReason?.kind === 'pursuer-caught';
    const pursuerGapPx = pursuerScreenGapPx(runnerBounds, pursuerBounds, captured);
    const fallbackSelection = selectD4Assets({
      cssWidth: width,
      cssHeight: height,
      coarsePointer: typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches,
      deviceMemory: typeof navigator !== 'undefined' ? (navigator as Navigator & { deviceMemory?: number }).deviceMemory : undefined,
    });
    const assets = this.d4Assets;
    const resolved = new Set([...state.resolvedEventIds, ...state.consumedEventIds]);
    const hazardScreens = this.visibleSections.flatMap((section) => section.events.flatMap((event) => {
      if (resolved.has(event.id) || !this.isSnapshotHazard(event)) return [];
      const projected = this.hazardScreenBounds(section, event, width, height);
      return projected ? [projected] : [];
    }));
    const tideScarSegments = this.tideScarSnapshot.segments
      .map((segment) => projectTideScarSegment(this.camera, segment, width, height, renderer.getPixelRatio()))
      .filter((segment): segment is TideScarScreenSegment => segment !== null);
    const composition = measureD4Composition(this.camera, position, yaw, width, height, this.activeD4Profile);
    this.snapshot = {
      canvas: { width, height, resolution: renderer.getPixelRatio() },
      options: { ...this.options },
      presentationAlpha,
      presentedDistance,
      presentedLanePosition,
      runnerWorld: { x: position.x, y: position.y, z: position.z, yaw },
      runnerScreen: {
        x: (screen.x * 0.5 + 0.5) * width,
        y: (-screen.y * 0.5 + 0.5) * height,
        visible: screen.z >= -1 && screen.z <= 1,
        bounds: runnerBounds,
      },
      pursuerScreen: {
        x: pursuer ? (pursuer.x * .5 + .5) * width : -1,
        y: pursuer ? (-pursuer.y * .5 + .5) * height : -1,
        visible: pursuerBounds !== null,
        bounds: pursuerBounds,
      },
      pursuerGapPx,
      hazardScreens,
      tideScarSegments,
      camera: { x: this.camera.position.x, y: this.camera.position.y, z: this.camera.position.z, fov: this.camera.fov, yaw },
      lanePosition: state.runner.lanePosition,
      posture: postureOf(state),
      visibleSectionIds: this.visibleSections.map((section) => section.id),
      visibleObstacleCount: this.beams.count + this.rings.count + this.columns.count + Math.ceil(this.gapLips.count / 2),
      drawCalls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      turnProgress: this.turnMotion ? this.turnMotion.override ?? this.turnMotion.progress : null,
      contextLossCount: this.contextLossCount,
      d4: {
        profile: this.activeD4Profile.name,
        fogDensity: canyonFogDensity(this.activeD4Profile, this.options.highContrast),
        assetTier: assets ? (assets.fallback ? 'fallback' : assets.tier) : 'loading',
        requestedAssets: assets?.requestedFiles ?? fallbackSelection.requestedFiles,
        textureBytes: assets?.textureBytes ?? fallbackSelection.textureBytes,
        tideScarVertices: this.tideScarSnapshot.vertexCount,
        tideScarCoverage: this.tideScarSnapshot.coverage,
        pursuerPlacementError: this.pursuerPlacementError,
        composition: {
          ...composition,
          runnerCenterY: runnerBounds ? (runnerBounds.top + runnerBounds.bottom) / (2 * height) : -1,
        },
      },
    };
  }

  private isSnapshotHazard(event: CourseEvent): event is CourseEvent & { kind: HazardScreenBounds["kind"] } {
    return event.kind === "beam" || event.kind === "ring" || event.kind === "column" || event.kind === "gap";
  }

  private hazardScreenBounds(
    section: CourseSection,
    event: CourseEvent & { kind: HazardScreenBounds["kind"] },
    width: number,
    height: number,
  ): HazardScreenBounds | null {
    const lane = event.lane === "all" ? 0 : event.lane;
    const sample = sampleCoursePosition(section, event.kind === "gap" ? event.at + event.length / 2 : event.at, lane);
    const roadWidth = event.lane === "all" ? WORLD_METRICS.roadWidth : WORLD_METRICS.laneWidth;
    let center = new Vector3(sample.x, 0, sample.z);
    let halfExtent = new Vector3(0.5, 0.5, 0.5);
    switch (event.kind) {
      case "beam":
        center.y = 0.34;
        halfExtent = new Vector3((event.lane === "all" ? WORLD_METRICS.roadWidth - 0.5 : 1.65) / 2, 0.3, 0.32);
        break;
      case "ring":
        center.y = event.lane === "all" ? 1.12 : 0.96;
        halfExtent = new Vector3(event.lane === "all" ? WORLD_METRICS.roadWidth / 2.15 : 1.05, event.lane === "all" ? 1.05 : 0.82, 0.42);
        break;
      case "column":
        center.y = 0.98;
        halfExtent = new Vector3(0.82, 1.18, 0.78);
        break;
      case "gap":
        center.y = 0.05;
        halfExtent = new Vector3((roadWidth - 0.5) / 2, 0.14, Math.max(1.6, event.length) / 2);
        break;
    }
    const bounds = this.clippedBounds(center, halfExtent, width, height, headingYaw(section.heading));
    return bounds ? { eventId: event.id, kind: event.kind, bounds } : null;
  }

  private clippedBounds(
    center: Vector3,
    halfExtent: Vector3,
    width: number,
    height: number,
    yaw: number,
  ): ClippedScreenBounds | null {
    return projectOrientedBounds(this.camera, center, halfExtent, width, height, yaw);
  }

  private readonly onContextLost = (event: Event): void => {
    event.preventDefault();
    this.contextLossCount += 1;
  };
}
