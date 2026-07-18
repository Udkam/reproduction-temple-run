import { PerspectiveCamera, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import { PURSUER_RIG_BOUNDS } from './pursuerRig';
import { RUNNER_RIG_BOUNDS } from './runnerRig';
import {
  groundAnchoredBounds,
  applyD4LensShift,
  createDeckCapGeometry,
  projectTideScarSegment,
  pursuerPresentation,
  pursuerScreenGapPx,
  selectPursuerProjection,
  type ClippedScreenBounds,
} from './WorldRenderer';
import { d4MinimumPursuerGapPx, d4ProfileForViewport } from './d4Profile';

function bounds(top: number, bottom: number): ClippedScreenBounds {
  return { left: 100, top, right: 160, bottom, width: 60, height: bottom - top, area: 60 * (bottom - top) };
}

function projectedBounds(
  camera: PerspectiveCamera,
  root: Vector3,
  dimensions: { width: number; height: number; depth: number },
  scale: number,
  width: number,
  height: number,
): ClippedScreenBounds | null {
  const { center, halfExtent } = groundAnchoredBounds(root, dimensions, scale);
  const xs: number[] = [];
  const ys: number[] = [];
  for (const x of [-halfExtent.x, halfExtent.x]) {
    for (const y of [-halfExtent.y, halfExtent.y]) {
      for (const z of [-halfExtent.z, halfExtent.z]) {
        const projected = center.clone().add(new Vector3(x, y, z)).project(camera);
        xs.push((projected.x * 0.5 + 0.5) * width);
        ys.push((-projected.y * 0.5 + 0.5) * height);
      }
    }
  }
  const left = Math.max(0, Math.min(...xs));
  const right = Math.min(width, Math.max(...xs));
  const top = Math.max(0, Math.min(...ys));
  const bottom = Math.min(height, Math.max(...ys));
  if (right <= left || bottom <= top) return null;
  return { left, top, right, bottom, width: right - left, height: bottom - top, area: (right - left) * (bottom - top) };
}

function representativePursuit(width: number, height: number, chaseGap: number) {
  const aspect = width / height;
  const portraitFactor = aspect < 0.7 ? 1.42 : 1;
  const camera = new PerspectiveCamera(47, aspect, 0.08, 520);
  camera.position.set(0, 6.15 + (portraitFactor - 1) * 1.65, 9.45 * portraitFactor);
  const lookAhead = (11 + 10 * 0.38) * (aspect < 0.7 ? 0.74 : 1);
  camera.lookAt(0, 0.88, -lookAhead);
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();

  const presentation = pursuerPresentation(chaseGap, aspect, false);
  const runner = projectedBounds(camera, new Vector3(), RUNNER_RIG_BOUNDS, 1, width, height);
  const pursuer = projectedBounds(
    camera,
    new Vector3(0, 0.03, presentation.visibleGap),
    PURSUER_RIG_BOUNDS,
    presentation.scale,
    width,
    height,
  );
  return { presentation, runner, pursuer, gap: pursuerScreenGapPx(runner, pursuer, false) };
}

describe('renderer pursuit screen evidence', () => {
  it('keeps deck cap start/end cross-sections continuous and projects real scar quads through clip space', () => {
    const geometry = createDeckCapGeometry(2);
    const positions = geometry.getAttribute('position');
    const z = Array.from({ length: 4 }, (_, index) => positions.getZ(index));
    expect(Math.min(...z)).toBe(-0.5);
    expect(Math.max(...z)).toBe(0.5);

    const camera = new PerspectiveCamera(43, 16 / 9, 0.08, 520);
    camera.position.set(0, 4, 7);
    camera.lookAt(0, 0, -6);
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
    const projected = projectTideScarSegment(camera, {
      sectionId: 'scar-section', intervalIndex: 1, segmentIndex: 2,
      points: [new Vector3(1, 0.04, -4), new Vector3(1.1, 0.04, -4), new Vector3(1, 0.04, -6), new Vector3(1.1, 0.04, -6)],
    }, 1440, 900, 1);
    expect(projected?.visibleAreaPx).toBeGreaterThan(0);
    expect(projected?.polygonCss.length).toBeGreaterThanOrEqual(3);
  });

  it('anchors rig bounds at the ground root and applies pursuer scale to the real extent', () => {
    const runner = groundAnchoredBounds(new Vector3(4, 0, 8), RUNNER_RIG_BOUNDS);
    expect(runner.center.y - runner.halfExtent.y).toBe(0);
    expect(runner.center.y + runner.halfExtent.y).toBeCloseTo(RUNNER_RIG_BOUNDS.height, 10);

    const root = new Vector3(-2, 0.03, 7);
    const scale = 0.84;
    const pursuer = groundAnchoredBounds(root, PURSUER_RIG_BOUNDS, scale);
    expect(pursuer.center.y - pursuer.halfExtent.y).toBeCloseTo(root.y, 10);
    expect(pursuer.center.y + pursuer.halfExtent.y).toBeCloseTo(root.y + PURSUER_RIG_BOUNDS.height * scale, 10);
    expect(pursuer.halfExtent.x).toBeCloseTo(PURSUER_RIG_BOUNDS.width * scale / 2, 10);
  });

  it('keeps normal and close gaps ordered, fails closed for missing bounds, and exempts capture overlap', () => {
    const runner = bounds(300, 420);
    const normal = pursuerScreenGapPx(runner, bounds(510, 610), false);
    const close = pursuerScreenGapPx(runner, bounds(428, 528), false);
    expect(normal).toBeGreaterThan(close!);
    expect(close).toBeGreaterThanOrEqual(6);
    expect(pursuerScreenGapPx(runner, null, false)).toBeNull();
    expect(pursuerScreenGapPx(runner, bounds(412, 512), true)).toBeNull();
  });

  it('keeps desktop, portrait-close, and landscape pursuers grounded, visible, and separated', () => {
    const desktopNormal = representativePursuit(1440, 900, 4.5);
    const portraitClose = representativePursuit(390, 844, 1.2);
    const landscapeClose = representativePursuit(844, 390, 1.2);

    for (const representative of [desktopNormal, portraitClose, landscapeClose]) {
      expect(representative.pursuer?.area).toBeGreaterThan(0);
      expect(representative.gap).toBeGreaterThanOrEqual(6);
    }

    for (const aspect of [1440 / 900, 390 / 844, 844 / 390]) {
      expect(pursuerPresentation(1.2, aspect, false).visibleGap).toBeLessThanOrEqual(
        pursuerPresentation(4.5, aspect, false).visibleGap,
      );
      expect(pursuerPresentation(4.5, aspect, false).visibleGap).toBeLessThanOrEqual(
        pursuerPresentation(8, aspect, false).visibleGap,
      );
    }
  });

  it('selects real grounded D4 projections for normal and close pursuit in every profile', () => {
    const viewports = [[1440, 900], [390, 844], [844, 390]] as const;
    for (const [width, height] of viewports) {
      const profile = d4ProfileForViewport(width, height);
      const camera = new PerspectiveCamera(profile.fov, width / height, 0.08, 520);
      camera.position.set(0, profile.cameraHeight, profile.cameraBack);
      camera.lookAt(0, profile.lookHeight, -profile.lookAhead);
      camera.updateProjectionMatrix();
      applyD4LensShift(camera, profile);
      camera.updateMatrixWorld();
      const normal = selectPursuerProjection(
        camera,
        { width, height },
        profile,
        new Vector3(),
        0,
        4.5,
        pursuerPresentation(4.5, width / height, false).scale,
      );
      const close = selectPursuerProjection(
        camera,
        { width, height },
        profile,
        new Vector3(),
        0,
        1.2,
        pursuerPresentation(1.2, width / height, false).scale,
      );
      expect(normal?.bounds.area).toBeGreaterThan(0);
      expect(close?.bounds.area).toBeGreaterThan(0);
      expect(normal?.screenGapPx).toBeGreaterThanOrEqual(d4MinimumPursuerGapPx(height));
      expect(close?.screenGapPx).toBeGreaterThanOrEqual(d4MinimumPursuerGapPx(height));
      expect(close?.worldGap).toBeLessThanOrEqual(normal!.worldGap);
      expect(close?.screenGapPx).toBeLessThanOrEqual(normal!.screenGapPx);
    }
  });
});
