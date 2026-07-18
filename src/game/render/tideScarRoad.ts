import {
  BufferGeometry,
  DoubleSide,
  Float32BufferAttribute,
  Mesh,
  MeshStandardMaterial,
  Vector3,
} from 'three';
import {
  rightVector,
  sampleCoursePosition,
  type CourseEvent,
  type CourseSection,
} from '../core';
import { PALETTE, WORLD_METRICS } from './theme';

export interface TideScarInterval {
  start: number;
  end: number;
}

export interface TideScarWorldSegment {
  sectionId: string;
  intervalIndex: number;
  segmentIndex: number;
  /** Clockwise, road-surface quad corners before camera/frustum clipping. */
  points: readonly [Vector3, Vector3, Vector3, Vector3];
}

export interface TideScarSectionPlan {
  sectionId: string;
  /** The deterministic 2–5 pre-clip interval count. */
  intervalCount: number;
  /** Requested fraction of the section before presentation-only masks. */
  coverage: number;
  /** Coverage remaining after local gap, dry-edge, and hazard clipping. */
  postClipCoverage: number;
  intervals: readonly TideScarInterval[];
  vertexCount: number;
}

export interface TideScarRoadSnapshot {
  sections: readonly TideScarSectionPlan[];
  vertexCount: number;
  /** Requested coverage averaged per rendered section; never a summed pseudo-percent. */
  coverage: number;
  segments: readonly TideScarWorldSegment[];
}

function hashString(value: string): number {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0) / 0xffffffff;
}

export function stableTideScarHash(sectionId: string): number {
  return hashString(`tide-scar-v1:${sectionId}`);
}

function subtract(intervals: readonly TideScarInterval[], blocked: TideScarInterval): TideScarInterval[] {
  return intervals.flatMap((interval) => {
    if (blocked.end <= interval.start || blocked.start >= interval.end) return [interval];
    const remaining: TideScarInterval[] = [];
    if (blocked.start - interval.start >= 0.025) {
      remaining.push({ start: interval.start, end: Math.min(interval.end, blocked.start) });
    }
    if (interval.end - blocked.end >= 0.025) {
      remaining.push({ start: Math.max(interval.start, blocked.end), end: interval.end });
    }
    return remaining;
  });
}

function blocksFor(section: CourseSection, unresolved: ReadonlySet<string>): TideScarInterval[] {
  const intervals: TideScarInterval[] = [];
  for (const event of section.events) {
    if (unresolved.has(event.id) === false) continue;
    if (event.kind === 'gap') {
      intervals.push({
        start: Math.max(0, event.at / section.length),
        end: Math.min(1, (event.at + event.length) / section.length),
      });
      continue;
    }
    if (event.kind !== 'beam' && event.kind !== 'ring' && event.kind !== 'column') continue;
    const halfLength = event.kind === 'ring' ? 0.72 : event.kind === 'column' ? 0.82 : 0.68;
    intervals.push({
      start: Math.max(0, (event.at - halfLength) / section.length),
      end: Math.min(1, (event.at + halfLength) / section.length),
    });
  }
  return intervals;
}

/**
 * A presentation-only right-edge route mark. It derives from public course
 * events but never changes their geometry, resolution, or collision meaning.
 */
export function planTideScarSection(section: CourseSection, unresolved: ReadonlySet<string>): TideScarSectionPlan {
  const blocks = blocksFor(section, unresolved);
  const hash = stableTideScarHash(section.id);
  const intervalCount = 2 + Math.floor(hash * 4);
  const coverageTarget = 0.42 + ((hash * 13.37) % 1) * 0.22;
  const usableSpan = 0.88;
  const intervalLength = coverageTarget / intervalCount;
  const stride = usableSpan / intervalCount;
  let intervals: TideScarInterval[] = [];
  for (let index = 0; index < intervalCount; index += 1) {
    const jitter = (((hash * (index + 3) * 17.31) % 1) - 0.5) * 0.045;
    const start = MathUtilsClamp(0.04, 0.94, 0.06 + index * stride + jitter);
    intervals.push({ start, end: Math.min(0.95, start + intervalLength) });
  }
  const dryGapCount = Math.floor(((hash * 71.13) % 1) * 3);
  for (let index = 0; index < dryGapCount; index += 1) {
    const start = 0.13 + ((hash * (index + 7) * 19.71) % 1) * 0.7;
    const length = 0.018 + ((hash * (index + 11) * 7.13) % 1) * 0.026;
    blocks.push({ start, end: Math.min(0.95, start + length) });
  }
  for (const blocked of blocks) intervals = subtract(intervals, blocked);
  const postClipCoverage = intervals.reduce((total, interval) => total + interval.end - interval.start, 0);
  return {
    sectionId: section.id,
    intervalCount,
    coverage: coverageTarget,
    postClipCoverage,
    intervals,
    vertexCount: intervals.reduce((count, interval) => count + Math.max(1, Math.ceil((interval.end - interval.start) * section.length / 1.2)) * 6, 0),
  };
}

function MathUtilsClamp(minimum: number, maximum: number, value: number): number {
  return Math.max(minimum, Math.min(maximum, value));
}

export class TideScarRoad {
  readonly mesh: Mesh<BufferGeometry, MeshStandardMaterial>;
  private readonly geometry = new BufferGeometry();
  private readonly material = new MeshStandardMaterial({
    color: PALETTE.tideScar,
    roughness: 0.94,
    metalness: 0,
    emissive: 0x000000,
    emissiveIntensity: 0,
    side: DoubleSide,
  });
  private signature = '';
  private snapshot: TideScarRoadSnapshot = { sections: [], vertexCount: 0, coverage: 0, segments: [] };

  constructor() {
    this.geometry.setDrawRange(0, 0);
    this.mesh = new Mesh(this.geometry, this.material);
    this.mesh.name = 'analytic-tide-scar-right-edge';
    this.mesh.castShadow = false;
    this.mesh.receiveShadow = true;
    this.mesh.frustumCulled = false;
  }

  update(sections: readonly CourseSection[], unresolved: ReadonlySet<string>): TideScarRoadSnapshot {
    const signature = `${sections.map((section) => section.id).join('|')}::${[...unresolved].sort().join('|')}`;
    if (signature === this.signature) return this.snapshot;
    this.signature = signature;
    const plans = sections.map((section) => planTideScarSection(section, unresolved));
    const positions: number[] = [];
    const segments: TideScarWorldSegment[] = [];
    for (const [index, section] of sections.entries()) {
      const plan = plans[index];
      if (!plan) continue;
      for (const [intervalIndex, interval] of plan.intervals.entries()) {
        const quadCount = Math.max(1, Math.ceil((interval.end - interval.start) * section.length / 1.2));
        for (let step = 0; step < quadCount; step += 1) {
          const start = interval.start + (interval.end - interval.start) * step / quadCount;
          const end = interval.start + (interval.end - interval.start) * (step + 1) / quadCount;
          const points = this.quadFor(section, start, end, intervalIndex, step);
          for (const point of [points[0], points[1], points[2], points[2], points[1], points[3]]) {
            positions.push(point.x, point.y, point.z);
          }
          segments.push({ sectionId: section.id, intervalIndex, segmentIndex: step, points });
        }
      }
    }
    this.geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
    this.geometry.computeVertexNormals();
    this.geometry.computeBoundingSphere();
    this.geometry.setDrawRange(0, positions.length / 3);
    this.snapshot = {
      sections: plans,
      vertexCount: positions.length / 3,
      coverage: plans.length === 0 ? 0 : plans.reduce((total, plan) => total + plan.coverage, 0) / plans.length,
      segments,
    };
    return this.snapshot;
  }

  dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }

  private quadFor(
    section: CourseSection,
    start: number,
    end: number,
    intervalIndex: number,
    segmentIndex: number,
  ): [Vector3, Vector3, Vector3, Vector3] {
    const right = rightVector(section.heading);
    const hash = stableTideScarHash(`${section.id}:${intervalIndex}:${segmentIndex}`);
    const inset = WORLD_METRICS.roadWidth / 2 - (0.32 + hash * 0.14);
    const lateralJitter = ((hash * 17.17) % 1 - 0.5) * 0.036;
    const totalWidth = MathUtilsClamp(0.07, 0.11, (0.08 + ((hash * 7.31) % 1) * 0.02) * (0.88 + ((hash * 31.7) % 1) * 0.24));
    const halfWidth = totalWidth / 2;
    const startSample = sampleCoursePosition(section, start * section.length);
    const endSample = sampleCoursePosition(section, end * section.length);
    const center = inset + lateralJitter;
    const startOuter = new Vector3(startSample.x + right.x * (center + halfWidth), 0.045, startSample.z + right.z * (center + halfWidth));
    const startInner = new Vector3(startSample.x + right.x * (center - halfWidth), 0.045, startSample.z + right.z * (center - halfWidth));
    const endOuter = new Vector3(endSample.x + right.x * (center + halfWidth), 0.045, endSample.z + right.z * (center + halfWidth));
    const endInner = new Vector3(endSample.x + right.x * (center - halfWidth), 0.045, endSample.z + right.z * (center - halfWidth));
    return [startOuter, startInner, endOuter, endInner];
  }
}
