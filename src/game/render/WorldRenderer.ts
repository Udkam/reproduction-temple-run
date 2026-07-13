import {
  ACESFilmicToneMapping,
  AdditiveBlending,
  AmbientLight,
  BoxGeometry,
  BufferGeometry,
  Color,
  CylinderGeometry,
  DirectionalLight,
  DodecahedronGeometry,
  DoubleSide,
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
  PlaneGeometry,
  Points,
  PointsMaterial,
  RingGeometry,
  Scene,
  SRGBColorSpace,
  TorusGeometry,
  Vector3,
  Vector2,
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
import { createRunnerRig, updateRunnerRig, type RunnerRig } from './runnerRig';
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

export interface RenderSnapshot {
  canvas: { width: number; height: number; resolution: number };
  options: RenderOptions;
  presentationAlpha: number;
  presentedDistance: number;
  presentedLanePosition: number;
  runnerWorld: { x: number; y: number; z: number; yaw: number };
  runnerScreen: { x: number; y: number; visible: boolean };
  pursuerScreen: { x: number; y: number; visible: boolean; bounds: ClippedScreenBounds | null };
  /** Clipped CSS-pixel geometry for every visible unresolved hazard. */
  hazardScreens: HazardScreenBounds[];
  camera: { x: number; y: number; z: number; fov: number; yaw: number };
  lanePosition: number;
  posture: 'run' | 'jump' | 'slide';
  visibleSectionIds: string[];
  visibleObstacleCount: number;
  drawCalls: number;
  triangles: number;
  turnProgress: number | null;
  contextLossCount: number;
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
const MAX_EVENTS = 96;
const MAX_SHARDS = 160;
const TURN_VISUAL_RADIUS = 1.45;

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
  private readonly ocean = new Mesh(
    new PlaneGeometry(900, 900),
    new MeshBasicMaterial({ color: PALETTE.soil }),
  );
  private readonly horizon = new Mesh(
    new PlaneGeometry(360, 110),
    new MeshBasicMaterial({ color: PALETTE.mist, transparent: true, opacity: 0.34, side: DoubleSide, depthWrite: false }),
  );
  private readonly floorMaterial = new MeshStandardMaterial({ color: PALETTE.basalt, roughness: 0.92, metalness: 0.02 });
  private readonly railMaterial = new MeshStandardMaterial({ color: PALETTE.basaltEdge, roughness: 0.9, metalness: 0.02 });
  private readonly seamMaterial = new MeshStandardMaterial({ color: PALETTE.signal, emissive: PALETTE.signal, emissiveIntensity: 0.32, roughness: 0.48 });
  private readonly guideMaterial = new MeshStandardMaterial({ color: PALETTE.brass, roughness: 0.76, metalness: 0.12 });
  private readonly porcelainMaterial = new MeshStandardMaterial({ color: PALETTE.porcelain, roughness: 0.86, metalness: 0.02 });
  private readonly rockMaterial = new MeshStandardMaterial({ color: PALETTE.foliage, roughness: 0.96, metalness: 0 });
  private readonly beamMaterial = new MeshStandardMaterial({ color: 0x6d4938, roughness: 0.9, metalness: 0.01 });
  private readonly gateMaterial = new MeshStandardMaterial({ color: 0x826f48, roughness: 0.78, metalness: 0.18 });
  private readonly columnMaterial = new MeshStandardMaterial({ color: 0x8f8874, roughness: 0.94, metalness: 0.01 });
  private readonly dangerMaterial = new MeshStandardMaterial({ color: PALETTE.hazard, emissive: 0x3a1009, emissiveIntensity: 0.18, roughness: 0.8 });
  private readonly gapMaterial = new MeshStandardMaterial({ color: 0x18130f, roughness: 0.98 });
  private readonly shardMaterial = new MeshStandardMaterial({ color: PALETTE.signal, emissive: PALETTE.signal, emissiveIntensity: 1.25, roughness: 0.28, metalness: 0.08 });
  private readonly shieldMaterial = new MeshBasicMaterial({ color: PALETTE.signal, transparent: true, opacity: 0.72, wireframe: true });
  private readonly floors = this.instances(new BoxGeometry(1, 1, 1), this.floorMaterial, MAX_SECTIONS);
  private readonly rails = this.instances(new BoxGeometry(1, 1, 1), this.railMaterial, MAX_RAILS);
  private readonly seams = this.instances(new BoxGeometry(1, 1, 1), this.seamMaterial, MAX_SECTIONS * 3);
  private readonly laneGuides = this.instances(new BoxGeometry(1, 1, 1), this.guideMaterial, MAX_SECTIONS * 2);
  private readonly platforms = this.instances(new BoxGeometry(1, 1, 1), this.floorMaterial, MAX_SECTIONS + 1);
  private readonly pillars = this.instances(new CylinderGeometry(1, 1.18, 1, 7), this.porcelainMaterial, MAX_PILLARS);
  private readonly rocks = this.instances(new DodecahedronGeometry(1, 0), this.rockMaterial, MAX_ROCKS);
  private readonly beams = this.instances(new BoxGeometry(1, 1, 1), this.beamMaterial, MAX_EVENTS);
  private readonly beamCuts = this.instances(new BoxGeometry(1, 1, 1), this.dangerMaterial, MAX_EVENTS * 2);
  private readonly rings = this.instances(new TorusGeometry(1, 0.14, 7, 18), this.gateMaterial, MAX_EVENTS);
  private readonly gatePosts = this.instances(new CylinderGeometry(0.12, 0.18, 1, 6), this.gateMaterial, MAX_EVENTS * 2);
  private readonly columns = this.instances(new DodecahedronGeometry(0.76, 0), this.columnMaterial, MAX_EVENTS);
  private readonly columnCaps = this.instances(new DodecahedronGeometry(0.64, 0), this.dangerMaterial, MAX_EVENTS);
  private readonly columnRubble = this.instances(new DodecahedronGeometry(0.34, 0), this.columnMaterial, MAX_EVENTS * 3);
  private readonly gaps = this.instances(new BoxGeometry(1, 1, 1), this.gapMaterial, MAX_EVENTS);
  private readonly gapLips = this.instances(new BoxGeometry(1, 1, 1), this.dangerMaterial, MAX_EVENTS * 2);
  private readonly shards = this.instances(new IcosahedronGeometry(0.26, 0), this.shardMaterial, MAX_SHARDS);
  private readonly shields = this.instances(new IcosahedronGeometry(0.72, 1), this.shieldMaterial, 16);
  private readonly wraith = this.createWraith();
  private readonly mist = this.createMist();
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
    hazardScreens: [],
    camera: { x: 0, y: 0, z: 0, fov: 47, yaw: 0 },
    lanePosition: 0,
    posture: 'run',
    visibleSectionIds: [],
    visibleObstacleCount: 0,
    drawCalls: 0,
    triangles: 0,
    turnProgress: null,
    contextLossCount: 0,
  };

  constructor() {
    this.scene.background = new Color(PALETTE.sky);
    this.scene.fog = new FogExp2(PALETTE.mist, 0.0115);
    this.camera.position.set(0, 4.8, 7.4);
    this.scene.add(new HemisphereLight(0xe3eee9, 0x31382f, 1.82));
    this.scene.add(new AmbientLight(0xa9bdb3, 0.58));
    const key = new DirectionalLight(0xffe1ad, 2.35);
    key.position.set(-8, 15, 6);
    this.scene.add(key);
    const rim = new DirectionalLight(PALETTE.signal, 0.62);
    rim.position.set(7, 6, -12);
    this.scene.add(rim);
    this.ocean.rotation.x = -Math.PI / 2;
    this.ocean.position.y = -4.4;
    this.horizon.position.set(0, 22, -100);
    this.scene.add(this.ocean, this.horizon);
    this.scene.add(
      this.floors,
      this.rails,
      this.seams,
      this.laneGuides,
      this.platforms,
      this.pillars,
      this.rocks,
      this.beams,
      this.beamCuts,
      this.rings,
      this.gatePosts,
      this.columns,
      this.columnCaps,
      this.columnRubble,
      this.gaps,
      this.gapLips,
      this.shards,
      this.shields,
      this.wraith,
      this.mist,
    );
  }

  async init(host: HTMLElement): Promise<void> {
    const renderer = new WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.outputColorSpace = SRGBColorSpace;
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, window.innerWidth <= 900 ? 1.75 : 2));
    renderer.setSize(host.clientWidth, host.clientHeight, false);
    renderer.domElement.dataset.testid = 'runner-canvas';
    renderer.domElement.setAttribute('aria-label', 'TIDE RELAY third-person endless runner world');
    renderer.domElement.setAttribute('role', 'application');
    renderer.domElement.tabIndex = 0;
    renderer.domElement.addEventListener('webglcontextlost', this.onContextLost);
    host.appendChild(renderer.domElement);
    this.renderer = renderer;
    this.runner = createRunnerRig();
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
    this.scene.fog = new FogExp2(this.options.highContrast ? 0x78958c : PALETTE.mist, this.options.highContrast ? 0.009 : 0.0115);
    this.dangerMaterial.emissiveIntensity = this.options.highContrast ? 0.5 : 0.18;
    this.seamMaterial.emissiveIntensity = this.options.highContrast ? 0.72 : 0.32;
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
    rig.core.scale.setScalar(1 + this.pickupPulse * 0.55);

    this.updateCourse(state);
    this.updateWraith(state, position, yaw);
    this.updateCamera(state, position, yaw, deltaMs);
    this.ocean.position.x = position.x;
    this.ocean.position.z = position.z;
    const horizonForward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    this.horizon.position.set(
      position.x + horizonForward.x * 115,
      22,
      position.z + horizonForward.z * 115,
    );
    this.horizon.rotation.y = yaw;
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
    const pixelRatio = Math.min(window.devicePixelRatio || 1, width <= 900 ? 1.75 : 2);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
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
    let railCount = 0;
    let seamCount = 0;
    let laneGuideCount = 0;
    let platformCount = 0;
    let pillarCount = 0;
    let rockCount = 0;
    let beamCount = 0;
    let beamCutCount = 0;
    let ringCount = 0;
    let gatePostCount = 0;
    let columnCount = 0;
    let columnCapCount = 0;
    let columnRubbleCount = 0;
    let gapCount = 0;
    let gapLipCount = 0;
    let shardCount = 0;
    let shieldCount = 0;

    const firstVisible = this.visibleSections[0];
    if (firstVisible) {
      this.setInstance(
        this.platforms,
        platformCount++,
        firstVisible.origin.x,
        -WORLD_METRICS.roadHeight / 2,
        firstVisible.origin.z,
        0,
        WORLD_METRICS.roadWidth,
        WORLD_METRICS.roadHeight,
        WORLD_METRICS.roadWidth,
      );
    }

    for (const section of this.visibleSections) {
      const yaw = headingYaw(section.heading);
      const center = sampleCoursePosition(section, section.length / 2);
      const straightLength = Math.max(1, section.length - WORLD_METRICS.roadWidth);
      this.setInstance(this.floors, floorCount++, center.x, -WORLD_METRICS.roadHeight / 2, center.z, yaw, WORLD_METRICS.roadWidth, WORLD_METRICS.roadHeight, straightLength);
      const right = rightVector(section.heading);
      for (const side of [-1, 1] as const) {
        const offset = side * (WORLD_METRICS.roadWidth / 2 - WORLD_METRICS.railInset);
        this.setInstance(this.rails, railCount++, center.x + right.x * offset, 0.13, center.z + right.z * offset, yaw, 0.25, 0.28, straightLength + 0.12);
      }
      this.setInstance(this.seams, seamCount++, center.x, 0.025, center.z, yaw, 0.1, 0.035, straightLength);
      for (const guideLane of [-0.5, 0.5]) {
        const guide = sampleCoursePosition(section, section.length / 2, guideLane);
        this.setInstance(this.laneGuides, laneGuideCount++, guide.x, 0.012, guide.z, yaw, 0.028, 0.02, straightLength);
      }
      const end = sampleCoursePosition(section, section.length);
      this.setInstance(this.platforms, platformCount++, end.x, -WORLD_METRICS.roadHeight / 2, end.z, 0, WORLD_METRICS.roadWidth, WORLD_METRICS.roadHeight, WORLD_METRICS.roadWidth);
      const next = state.course.sections.find((candidate) => candidate.index === section.index + 1);
      if (next) {
        const incomingSeam = sampleCoursePosition(section, section.length - WORLD_METRICS.roadWidth / 4);
        const outgoingSeam = sampleCoursePosition(next, WORLD_METRICS.roadWidth / 4);
        this.setInstance(this.seams, seamCount++, incomingSeam.x, 0.026, incomingSeam.z, yaw, 0.1, 0.036, WORLD_METRICS.roadWidth / 2);
        this.setInstance(this.seams, seamCount++, outgoingSeam.x, 0.026, outgoingSeam.z, headingYaw(next.heading), 0.1, 0.036, WORLD_METRICS.roadWidth / 2);
      }

      for (let marker = 0; marker < 3; marker += 1) {
        const along = 12 + marker * Math.max(16, (section.length - 24) / 2);
        const sample = sampleCoursePosition(section, Math.min(section.length - 6, along));
        for (const side of [-1, 1] as const) {
          const variance = seededUnit(section.index, marker * 2 + (side > 0 ? 1 : 0));
          const edge = 5.8 + variance * 4.2;
          this.setInstance(this.pillars, pillarCount++, sample.x + right.x * edge * side, 1.35 + variance * 0.65, sample.z + right.z * edge * side, yaw, 0.36 + variance * 0.22, 2.8 + variance * 2.2, 0.36 + variance * 0.22);
          const rockOffset = edge + 1.3 + variance * 2;
          this.setInstance(this.rocks, rockCount++, sample.x + right.x * rockOffset * side, -0.25, sample.z + right.z * rockOffset * side, variance * Math.PI, 0.75 + variance, 0.55 + variance * 0.8, 0.8 + variance * 1.2);
        }
      }

      for (const event of section.events) {
        if (resolved.has(event.id)) continue;
        const sample = sampleCoursePosition(section, event.at, event.lane === 'all' ? 0 : event.lane);
        if (event.kind === 'beam') {
          const width = event.lane === 'all' ? WORLD_METRICS.roadWidth - 0.5 : 1.65;
          this.setInstance(this.beams, beamCount++, sample.x, 0.34, sample.z, yaw, width, 0.48, 0.5);
          const capOffset = Math.max(0.34, width / 2 - 0.14);
          this.setInstance(this.beamCuts, beamCutCount++, sample.x + right.x * capOffset, 0.35, sample.z + right.z * capOffset, yaw, 0.22, 0.52, 0.54);
          this.setInstance(this.beamCuts, beamCutCount++, sample.x - right.x * capOffset, 0.35, sample.z - right.z * capOffset, yaw, 0.22, 0.52, 0.54);
        } else if (event.kind === 'ring') {
          const widthScale = event.lane === 'all' ? WORLD_METRICS.roadWidth / 2.15 : 1;
          const ringY = event.lane === 'all' ? 1.12 : 0.96;
          this.setInstance(this.rings, ringCount++, sample.x, ringY, sample.z, yaw, widthScale, event.lane === 'all' ? 0.86 : 0.68, 1);
          const postOffset = event.lane === 'all' ? WORLD_METRICS.roadWidth / 2 - 0.48 : 0.92;
          this.setInstance(this.gatePosts, gatePostCount++, sample.x + right.x * postOffset, 0.64, sample.z + right.z * postOffset, yaw, 1, 1.28, 1);
          this.setInstance(this.gatePosts, gatePostCount++, sample.x - right.x * postOffset, 0.64, sample.z - right.z * postOffset, yaw, 1, 1.28, 1);
        } else if (event.kind === 'column') {
          this.setInstance(this.columns, columnCount++, sample.x, 0.92, sample.z, yaw + 0.12, 0.94, 1.36, 0.9);
          this.setInstance(this.columnCaps, columnCapCount++, sample.x + right.x * 0.12, 1.83, sample.z + right.z * 0.12, yaw + event.at * 0.07, 0.58, 0.38, 0.58);
          for (const [rubbleIndex, rubbleOffset] of [-0.52, 0.08, 0.55].entries()) {
            const forward = headingVector(section.heading);
            const along = (rubbleIndex - 1) * 0.23;
            this.setInstance(
              this.columnRubble,
              columnRubbleCount++,
              sample.x + right.x * rubbleOffset + forward.x * along,
              0.2,
              sample.z + right.z * rubbleOffset + forward.z * along,
              yaw + rubbleIndex * 0.7,
              0.85 + rubbleIndex * 0.08,
              0.62,
              0.8,
            );
          }
        } else if (event.kind === 'gap') {
          const width = event.lane === 'all' ? WORLD_METRICS.roadWidth - 0.5 : WORLD_METRICS.laneWidth * 0.9;
          const gapCenter = sampleCoursePosition(section, event.at + event.length / 2, event.lane === 'all' ? 0 : event.lane);
          this.setInstance(this.gaps, gapCount++, gapCenter.x, 0.03, gapCenter.z, yaw, width, 0.075, Math.max(1.6, event.length));
          const farSample = sampleCoursePosition(section, event.at + event.length, event.lane === 'all' ? 0 : event.lane);
          this.setInstance(this.gapLips, gapLipCount++, sample.x, 0.08, sample.z, yaw, width, 0.12, 0.18);
          this.setInstance(this.gapLips, gapLipCount++, farSample.x, 0.08, farSample.z, yaw, width, 0.12, 0.18);
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
    this.finishInstances(this.rails, railCount);
    this.finishInstances(this.seams, seamCount);
    this.finishInstances(this.laneGuides, laneGuideCount);
    this.finishInstances(this.platforms, platformCount);
    this.finishInstances(this.pillars, pillarCount);
    this.finishInstances(this.rocks, rockCount);
    this.finishInstances(this.beams, beamCount);
    this.finishInstances(this.beamCuts, beamCutCount);
    this.finishInstances(this.rings, ringCount);
    this.finishInstances(this.gatePosts, gatePostCount);
    this.finishInstances(this.columns, columnCount);
    this.finishInstances(this.columnCaps, columnCapCount);
    this.finishInstances(this.columnRubble, columnRubbleCount);
    this.finishInstances(this.gaps, gapCount);
    this.finishInstances(this.gapLips, gapLipCount);
    this.finishInstances(this.shards, shardCount);
    this.finishInstances(this.shields, shieldCount);
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
    const portraitFactor = this.camera.aspect < 0.7 ? 1.42 : 1;
    const targetPosition = position.clone().addScaledVector(forward, -8.35 * portraitFactor);
    targetPosition.y = 5 + (portraitFactor - 1) * 1.4 + position.y * 0.18 - (state.runner.slideTicksRemaining > 0 ? 0.1 : 0);
    targetPosition.addScaledVector(right, -state.runner.lanePosition * 0.08);
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
    const lookAhead = (10 + state.speed * 0.34) * (this.camera.aspect < 0.7 ? 0.72 : 1);
    this.cameraLook.copy(position).addScaledVector(forward, lookAhead).add(new Vector3(0, 1.15 + position.y * 0.12, 0));
    this.camera.lookAt(this.cameraLook);
    const targetFov = this.options.reducedMotion ? 47 : 47 + ((state.speed - 9) / 10) * 6;
    this.camera.fov = MathUtils.lerp(this.camera.fov, MathUtils.clamp(targetFov, 47, 53), damping * 0.7);
    this.camera.updateProjectionMatrix();
  }

  private createWraith(): Object3D {
    const group = new Object3D();
    group.name = 'black-tide-pursuers';
    const material = new MeshStandardMaterial({
      color: PALETTE.blackTide,
      emissive: 0x182219,
      emissiveIntensity: 0.22,
      transparent: true,
      opacity: 0.92,
      roughness: 0.96,
    });
    const eyeMaterial = new MeshBasicMaterial({ color: PALETTE.hazard });
    for (const [index, offset] of [-0.72, 0.72].entries()) {
      const figure = new Object3D();
      figure.position.set(offset, index === 0 ? 0 : -0.08, Math.abs(offset) * 0.24);
      figure.rotation.z = offset * -0.06;
      const torso = new Mesh(new DodecahedronGeometry(index === 0 ? 0.68 : 0.62, 0), material);
      torso.position.y = 0.92;
      torso.scale.set(0.72, 1.35, 0.62);
      const head = new Mesh(new IcosahedronGeometry(index === 0 ? 0.35 : 0.32, 1), material);
      head.position.y = 1.72;
      const leftClaw = new Mesh(new CylinderGeometry(0.08, 0.13, 1.25, 5), material);
      const rightClaw = leftClaw.clone();
      leftClaw.position.set(-0.52, 0.72, -0.08);
      rightClaw.position.set(0.52, 0.72, -0.08);
      leftClaw.rotation.z = -0.38;
      rightClaw.rotation.z = 0.38;
      figure.add(torso, head, leftClaw, rightClaw);
      for (const eyeX of [-0.11, 0.11]) {
        const eye = new Mesh(new IcosahedronGeometry(0.052, 0), eyeMaterial);
        eye.position.set(eyeX, 1.76, -0.29);
        figure.add(eye);
      }
      group.add(figure);
    }
    return group;
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
    const material = new PointsMaterial({ color: PALETTE.signal, size: 1.4, sizeAttenuation: false, transparent: true, opacity: 0.22, depthWrite: false, blending: AdditiveBlending });
    return new Points(geometry, material);
  }

  private updateWraith(state: RunnerState, position: Vector3, yaw: number): void {
    const forward = new Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const normalizedGap = MathUtils.clamp((state.chaseGap - 0.65) / 7.35, 0, 1);
    const visibleGap = 1.25 + normalizedGap * 4.45;
    const danger = MathUtils.clamp((4.5 - state.chaseGap) / 3.85, 0, 1);
    this.wraith.position.copy(position).addScaledVector(forward, -visibleGap);
    this.wraith.position.y = 0.08 + (this.options.reducedMotion ? 0 : Math.sin(this.elapsed * (3.4 + danger * 2.2)) * 0.1);
    this.wraith.rotation.y = yaw;
    this.wraith.scale.setScalar(0.6 + danger * 0.2);
    for (const [index, figure] of this.wraith.children.entries()) {
      const side = index === 0 ? -1 : 1;
      const stride = this.options.reducedMotion ? 0 : Math.sin(this.elapsed * (7.8 + danger * 2.6) + index * Math.PI);
      figure.position.x = side * 0.72 + stride * 0.035;
      figure.position.y = (index === 0 ? 0 : -0.08) + Math.abs(stride) * 0.075;
      figure.rotation.z = side * -0.043 + stride * 0.025;
    }
    this.wraith.visible = state.status !== 'ready';
    this.mist.position.copy(position).addScaledVector(forward, -Math.min(6.4, visibleGap + 0.7));
    this.mist.visible = !this.options.reducedMotion && state.chaseGap > 2.4;
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
    const pursuer = this.wraith.position.clone().add(new Vector3(0, 1.05, 0)).project(this.camera);
    const size = renderer.getSize(new Vector2());
    const width = size.x;
    const height = size.y;
    const pursuerBounds = this.clippedBounds(this.wraith.position, new Vector3(1.25, 1.25, 0.85), width, height, this.wraith.rotation.y);
    const resolved = new Set([...state.resolvedEventIds, ...state.consumedEventIds]);
    const hazardScreens = this.visibleSections.flatMap((section) => section.events.flatMap((event) => {
      if (resolved.has(event.id) || !this.isSnapshotHazard(event)) return [];
      const projected = this.hazardScreenBounds(section, event, width, height);
      return projected ? [projected] : [];
    }));
    this.snapshot = {
      canvas: { width, height, resolution: renderer.getPixelRatio() },
      options: { ...this.options },
      presentationAlpha,
      presentedDistance,
      presentedLanePosition,
      runnerWorld: { x: position.x, y: position.y, z: position.z, yaw },
      runnerScreen: { x: (screen.x * 0.5 + 0.5) * width, y: (-screen.y * 0.5 + 0.5) * height, visible: screen.z >= -1 && screen.z <= 1 },
      pursuerScreen: {
        x: (pursuer.x * 0.5 + 0.5) * width,
        y: (-pursuer.y * 0.5 + 0.5) * height,
        visible: this.wraith.visible && pursuerBounds !== null,
        bounds: this.wraith.visible ? pursuerBounds : null,
      },
      hazardScreens,
      camera: { x: this.camera.position.x, y: this.camera.position.y, z: this.camera.position.z, fov: this.camera.fov, yaw },
      lanePosition: state.runner.lanePosition,
      posture: postureOf(state),
      visibleSectionIds: this.visibleSections.map((section) => section.id),
      visibleObstacleCount: this.beams.count + this.rings.count + this.columns.count + this.gaps.count,
      drawCalls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      turnProgress: this.turnMotion ? this.turnMotion.override ?? this.turnMotion.progress : null,
      contextLossCount: this.contextLossCount,
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
    const projected = points.map((point) => point.project(this.camera));
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

  private readonly onContextLost = (event: Event): void => {
    event.preventDefault();
    this.contextLossCount += 1;
  };
}
