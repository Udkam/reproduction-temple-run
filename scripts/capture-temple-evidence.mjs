import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');

const DEFAULT_BASE_URL = 'http://127.0.0.1:5173/';

export function parseCaptureCli(argv) {
  let explicitBaseUrl = null;
  let labels = [];
  let selfTest = false;
  let d4Dev = false;
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--labels') {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error('--labels requires a comma-separated value');
      labels = value.split(',').map((label) => label.trim()).filter(Boolean);
      index += 1;
      continue;
    }
    if (argument === '--self-test-cli') {
      selfTest = true;
      continue;
    }
    if (argument === '--d4-dev') {
      d4Dev = true;
      continue;
    }
    if (argument.startsWith('--')) throw new Error(`Unknown capture flag: ${argument}`);
    if (explicitBaseUrl !== null) throw new Error(`Only one baseUrl is allowed; received ${argument}`);
    explicitBaseUrl = argument;
  }
  return {
    resolvedBaseUrl: explicitBaseUrl ?? DEFAULT_BASE_URL,
    explicitBaseUrl: explicitBaseUrl !== null,
    labels,
    selfTest,
    d4Dev,
  };
}

function runCliRegression() {
  const cases = [
    { args: ['http://127.0.0.1:5193/'], labels: [] },
    { args: ['http://127.0.0.1:5193/', '--labels', 'desktop-normal'], labels: ['desktop-normal'] },
    { args: ['--labels', 'desktop-normal', 'http://127.0.0.1:5193/'], labels: ['desktop-normal'] },
  ];
  for (const testCase of cases) {
    const parsed = parseCaptureCli(testCase.args);
    if (parsed.resolvedBaseUrl !== 'http://127.0.0.1:5193/' || JSON.stringify(parsed.labels) !== JSON.stringify(testCase.labels)) {
      throw new Error(`CLI regression failed for ${JSON.stringify(testCase.args)}`);
    }
  }
  console.log('capture CLI regression passed (3 cases)');
}

const cli = parseCaptureCli(process.argv.slice(2));
const baseUrl = cli.resolvedBaseUrl;
const selectedLabels = new Set(cli.labels);
const root = process.cwd();
const diagnosticMode = selectedLabels.size > 0;
const d4DevMode = cli.d4Dev;
if (d4DevMode && !diagnosticMode) throw new Error('--d4-dev requires explicit --labels');
const d4DevDir = path.join(root, 'docs', 'screenshots', 'temple', 'tr3-d4-dev');
const screenshotDir = d4DevMode
  ? d4DevDir
  : path.join(root, 'docs', 'screenshots', 'temple', diagnosticMode ? 'tr3-diagnostic' : 'tr3');
const evidencePath = path.join(root, 'docs', 'qa', 'temple-tr3-browser-evidence.json');
const diagnosticPath = d4DevMode
  ? path.join(d4DevDir, 'summary.json')
  : path.join(root, 'docs', 'qa', 'temple-tr3-browser-diagnostic.json');
const failurePath = d4DevMode
  ? path.join(d4DevDir, 'failure.json')
  : path.join(root, 'docs', 'qa', 'temple-tr3-browser-failure.json');
const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const records = [];
let browser = null;
let currentPhase = 'bootstrap';
let activeScenario = null;
let activeLabel = null;
const head = (() => {
  try {
    return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
  } catch {
    return 'unavailable';
  }
})();

function verifyResolvedBaseUrl() {
  let url;
  try {
    url = new URL(baseUrl);
  } catch {
    throw new Error(`Invalid resolvedBaseUrl: ${baseUrl}`);
  }
  if (cli.explicitBaseUrl && !['5193', '5194', '5195', '5196', '5197', '5198', '5199'].includes(url.port)) {
    throw new Error(`Resolved baseUrl must use an authorized dev port 5193-5199, received ${baseUrl}`);
  }
}

function shouldRun(label) {
  return selectedLabels.size === 0 || selectedLabels.has(label);
}

async function writeFailure(error) {
  const message = error instanceof Error ? error.message : String(error);
  const assertion = message.startsWith('Temple evidence gate failed:')
    ? message.split('\n- ').slice(1)
    : [];
  const completedScreenshots = records.filter((record) => record.screenshot).length;
  await writeFile(failurePath, `${JSON.stringify({
    status: 'failed',
    generatedAt: new Date().toISOString(),
    head,
    resolvedBaseUrl: baseUrl,
    diagnosticMode,
    d4DevMode,
    labels: [...selectedLabels],
    phase: currentPhase,
    scenario: activeScenario,
    label: activeLabel,
    assertion,
    message,
    stack: error instanceof Error ? error.stack ?? null : null,
    completedRecords: records.length,
    completedScreenshots,
    // Preserve the actual browser console/page errors and measurement payloads
    // that led to a fail-closed run; do not leave a later correction blind.
    records: records.map((record) => ({
      id: record.id,
      screenshot: record.screenshot ?? null,
      consoleProblems: record.consoleProblems ?? [],
      render: record.render ?? null,
      viewport: record.viewport ?? null,
      ui: record.ui ?? null,
    })),
  }, null, 2)}\n`, 'utf8');
}

async function clearFailure() {
  await writeFile(failurePath, `${JSON.stringify({
    status: 'cleared',
    generatedAt: new Date().toISOString(),
    head,
    resolvedBaseUrl: baseUrl,
    diagnosticMode,
    d4DevMode,
    labels: [...selectedLabels],
  }, null, 2)}\n`, 'utf8');
}

function assertEvidence(condition, message, failures) {
  if (!condition) failures.push(message);
}

function boundsOverlap(first, second) {
  if (!first || !second) return false;
  return first.left < second.right && first.right > second.left && first.top < second.bottom && first.bottom > second.top;
}

function pointInRect(point, rect) {
  return point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom;
}

function pointInPolygon(point, polygon) {
  let inside = false;
  for (let index = 0, previous = polygon.length - 1; index < polygon.length; previous = index++) {
    const a = polygon[index];
    const b = polygon[previous];
    const crosses = (a.y > point.y) !== (b.y > point.y)
      && point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x;
    if (crosses) inside = !inside;
  }
  return inside;
}

function orientation(a, b, c) {
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

function segmentsIntersect(a, b, c, d) {
  const abC = orientation(a, b, c);
  const abD = orientation(a, b, d);
  const cdA = orientation(c, d, a);
  const cdB = orientation(c, d, b);
  return abC * abD <= 0 && cdA * cdB <= 0;
}

/** Exact screen polygon / visible-content-rect intersection; no HUD hull shortcut. */
function polygonIntersectsRect(polygon, rect) {
  if (!polygon || polygon.length < 3 || !rect) return false;
  const bounds = {
    left: Math.min(...polygon.map((point) => point.x)), right: Math.max(...polygon.map((point) => point.x)),
    top: Math.min(...polygon.map((point) => point.y)), bottom: Math.max(...polygon.map((point) => point.y)),
  };
  if (!boundsOverlap(bounds, rect)) return false;
  if (polygon.some((point) => pointInRect(point, rect))) return true;
  const corners = [
    { x: rect.left, y: rect.top }, { x: rect.right, y: rect.top },
    { x: rect.right, y: rect.bottom }, { x: rect.left, y: rect.bottom },
  ];
  if (corners.some((corner) => pointInPolygon(corner, polygon))) return true;
  for (let index = 0; index < polygon.length; index += 1) {
    const a = polygon[index];
    const b = polygon[(index + 1) % polygon.length];
    for (let edge = 0; edge < corners.length; edge += 1) {
      if (segmentsIntersect(a, b, corners[edge], corners[(edge + 1) % corners.length])) return true;
    }
  }
  return false;
}

function expectedD4Profile(viewport) {
  const aspect = viewport.width / viewport.height;
  if (viewport.height <= 520 && aspect > 1.5) return { name: 'landscape', fov: 46, mobile: true };
  if (aspect < 0.72) return { name: 'portrait', fov: 40, mobile: true };
  return { name: 'desktop', fov: 43, mobile: false };
}

function expectedD4Assets(mobile) {
  return mobile
    ? ['tide-sandstone-base-mobile-512.webp', 'tide-basalt-base-mobile-512.webp', 'tide-distant-canyon-mobile-1024x512.webp', 'tide-coral-mask-512.png']
    : ['tide-sandstone-base-1024.webp', 'tide-basalt-base-1024.webp', 'tide-distant-canyon-2048x1024.webp', 'tide-coral-mask-512.png'];
}

function validateEvidence(entries) {
  const failures = [];
  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  const captures = entries.filter((entry) => entry.screenshot);
  const expectedStatus = {
    'ready-desktop': 'ready',
    'running-desktop': 'running',
    'lane-mid': 'running',
    'lane-end': 'running',
    'jump-apex': 'running',
    'slide-mid': 'running',
    'turn-mid': 'running',
    'turn-lane-change': 'running',
    milestone: 'running',
    'chase-close': 'running',
    collision: 'game-over',
    'beam-preview': 'running',
    'ring-preview': 'running',
    'column-preview': 'running',
    'gap-preview': 'running',
    'pause-high-contrast': 'paused',
    'mobile-portrait': 'running',
    'mobile-landscape': 'running',
    'reduced-motion': 'running',
    'desktop-normal': 'running',
    'desktop-close-chase': 'running',
    'desktop-milestone': 'running',
    'desktop-paused': 'paused',
    'desktop-beam': 'running',
    'desktop-ring': 'running',
    'desktop-column': 'running',
    'desktop-gap': 'running',
    'mobile-normal': 'running',
    'mobile-close-chase': 'running',
    'mobile-milestone': 'running',
    'landscape-running': 'running',
  };

  for (const entry of captures) {
    assertEvidence(entry.consoleProblems.length === 0, `${entry.id}: console problems`, failures);
    assertEvidence(entry.dom.canvasCount === 1, `${entry.id}: expected one canvas`, failures);
    assertEvidence(entry.dom.gameplayEntityCount === 0, `${entry.id}: gameplay leaked into DOM`, failures);
    assertEvidence(entry.dom.overflowX === 0, `${entry.id}: horizontal overflow ${entry.dom.overflowX}`, failures);
    assertEvidence(entry.render.contextLossCount === 0, `${entry.id}: WebGL context loss`, failures);
    assertEvidence(entry.render.drawCalls <= 60, `${entry.id}: ${entry.render.drawCalls} draw calls`, failures);
    assertEvidence(entry.render.triangles <= 150_000, `${entry.id}: ${entry.render.triangles} triangles`, failures);
    assertEvidence(entry.simulation.status === expectedStatus[entry.id], `${entry.id}: unexpected status`, failures);
    assertEvidence(Number.isInteger(entry.simulation.seed), `${entry.id}: seed missing`, failures);
    assertEvidence(Math.abs(entry.render.presentationAlpha - 1) < 1e-9, `${entry.id}: non-canonical presentation alpha`, failures);
    assertEvidence(
      Math.abs(entry.render.presentedDistance - entry.simulation.distance) < 1e-9,
      `${entry.id}: presented distance differs from canonical state`,
      failures,
    );
    assertEvidence(
      Math.abs(entry.render.presentedLanePosition - entry.simulation.lanePosition) < 1e-9,
      `${entry.id}: presented lane differs from canonical state`,
      failures,
    );
    assertEvidence(entry.ui.hud.score === entry.simulation.score, `${entry.id}: HUD score differs from canonical state`, failures);
    assertEvidence(entry.ui.hud.distance === Math.floor(entry.simulation.distance), `${entry.id}: HUD distance differs from canonical state`, failures);
    assertEvidence(entry.ui.hud.shards === entry.simulation.shards, `${entry.id}: HUD shards differ from canonical state`, failures);
    assertEvidence(entry.ui.hud.flow === entry.simulation.multiplier, `${entry.id}: HUD flow differs from canonical state`, failures);
    assertEvidence(entry.ui.hudText.score === entry.simulation.score.toLocaleString('en-US'), `${entry.id}: score text differs from canonical state`, failures);
    assertEvidence(entry.ui.hudText.distance === `${Math.floor(entry.simulation.distance).toLocaleString('en-US')} m`, `${entry.id}: distance text differs from canonical state`, failures);
    assertEvidence(entry.ui.hudText.flow === `×${entry.simulation.multiplier}`, `${entry.id}: flow text differs from canonical state`, failures);
    assertEvidence(entry.ui.hudText.shards === String(entry.simulation.shards), `${entry.id}: shards text differs from canonical state`, failures);
    for (const area of entry.safeAreas) {
      assertEvidence(area.insideViewport, `${entry.id}: ${area.selector} leaves the safe viewport`, failures);
    }
    if (entry.id !== 'ready-desktop') {
      assertEvidence(entry.render.runnerScreen.visible, `${entry.id}: runner not visible`, failures);
      assertEvidence(
        entry.render.runnerScreen.x >= 0 && entry.render.runnerScreen.x <= entry.viewport.width,
        `${entry.id}: runner outside viewport horizontally`,
        failures,
      );
      assertEvidence(
        entry.render.runnerScreen.y >= 0 && entry.render.runnerScreen.y <= entry.viewport.height,
        `${entry.id}: runner outside viewport vertically`,
        failures,
      );
    }
    if (entry.viewport.width <= 900) {
      assertEvidence(entry.render.canvas.resolution <= 1.750_001, `${entry.id}: DPR cap exceeded`, failures);
    }
    const isPursuerCapture = entry.simulation.failureReason?.kind === 'pursuer-caught';
    if (entry.simulation.status !== 'ready' && !isPursuerCapture) {
      assertEvidence(entry.render.pursuerScreen?.bounds?.area > 0, `${entry.id}: pursuer bounds are unavailable`, failures);
      assertEvidence(entry.render.pursuerGapPx !== null && entry.render.pursuerGapPx !== undefined, `${entry.id}: pursuer gap is unavailable`, failures);
      assertEvidence(entry.render.pursuerGapPx >= Math.max(6, Math.round(entry.viewport.height * 0.015)), `${entry.id}: pursuer gap below D4 minimum`, failures);
    }
    if (d4DevMode) {
      const expected = expectedD4Profile(entry.viewport);
      assertEvidence(entry.render.d4?.profile === expected.name, `${entry.id}: D4 profile mismatch`, failures);
      assertEvidence(Math.abs((entry.render.camera?.fov ?? 0) - expected.fov) < 0.001, `${entry.id}: D4 fixed FOV mismatch`, failures);
      assertEvidence(entry.render.d4?.assetTier !== 'loading' && entry.render.d4?.assetTier !== 'fallback', `${entry.id}: D4 assets not loaded`, failures);
      assertEvidence(JSON.stringify(entry.render.d4?.requestedAssets ?? []) === JSON.stringify(expectedD4Assets(expected.mobile)), `${entry.id}: D4 requested asset set is not the selected tier`, failures);
      const textureBudget = expected.mobile ? 18 : 38;
      assertEvidence((entry.render.d4?.textureBytes ?? Number.POSITIVE_INFINITY) <= textureBudget * 1024 * 1024, `${entry.id}: D4 texture estimate exceeds ${textureBudget} MiB`, failures);
      assertEvidence(entry.render.drawCalls <= (expected.mobile ? 38 : 46), `${entry.id}: D4 draw-call budget exceeded`, failures);
      assertEvidence(entry.render.triangles <= (expected.mobile ? 115_000 : 190_000), `${entry.id}: D4 triangle budget exceeded`, failures);
      assertEvidence((entry.render.tideScarSegments ?? []).some((segment) => segment.visibleAreaPx > 0) && (entry.render.d4?.tideScarVertices ?? 0) > 0, `${entry.id}: analytic Tide Scar is not visible`, failures);
      assertEvidence(entry.render.d4?.pursuerPlacementError === null, `${entry.id}: ${entry.render.d4?.pursuerPlacementError ?? 'pursuer placement failed'}`, failures);
      const intersectsHudContent = (bounds) => (entry.ui.hudContent ?? []).some((area) => boundsOverlap(bounds, area));
      const scarIntersects = (rect) => (entry.render.tideScarSegments ?? []).some((segment) => polygonIntersectsRect(segment.polygonCss, rect));
      assertEvidence(!intersectsHudContent(entry.render.runnerScreen?.bounds), `${entry.id}: runner overlaps HUD content`, failures);
      assertEvidence(!intersectsHudContent(entry.render.pursuerScreen?.bounds), `${entry.id}: pursuer overlaps HUD content`, failures);
      assertEvidence(!(entry.ui.hudContent ?? []).some(scarIntersects), `${entry.id}: Tide Scar overlaps HUD content`, failures);
      for (const hazard of entry.render.hazardScreens ?? []) {
        assertEvidence(!intersectsHudContent(hazard.bounds), `${entry.id}: ${hazard.kind} overlaps HUD content`, failures);
        assertEvidence(!scarIntersects(hazard.bounds), `${entry.id}: Tide Scar overlaps ${hazard.kind}`, failures);
      }
      const composition = entry.render.d4?.composition;
      const profileBands = expected.name === 'desktop'
        ? { pitch: [21, 23], horizon: [0.20, 0.25], road: [0.54, 0.62], runner: 0.67 }
        : expected.name === 'portrait'
          ? { pitch: [24, 26], horizon: [0.27, 0.32], road: [0.82, 0.92], runner: 0.64 }
          : { pitch: [18, 20], horizon: [0.27, 0.32], road: [0.50, 0.58], runner: 0.70 };
      assertEvidence(composition?.pitchDegrees >= profileBands.pitch[0] && composition?.pitchDegrees <= profileBands.pitch[1], `${entry.id}: D4 camera pitch outside profile band`, failures);
      assertEvidence(Number.isFinite(composition?.horizonY) && composition.horizonY >= 0 && composition.horizonY <= entry.viewport.height, `${entry.id}: D4 horizon measurement unavailable`, failures);
      assertEvidence(Number.isFinite(composition?.bottomRoadWidth) && composition.bottomRoadWidth > 0, `${entry.id}: D4 bottom road width measurement unavailable`, failures);
      assertEvidence(Math.abs((composition?.runnerCenterY ?? -1) - profileBands.runner) <= 0.03, `${entry.id}: D4 runner band mismatch`, failures);
    }
  }

  if (diagnosticMode) {
    if (failures.length > 0) {
      throw new Error(`Temple evidence gate failed:\n- ${failures.join('\n- ')}`);
    }
    return;
  }

  const turn = byId.get('turn-mid');
  assertEvidence(Math.abs((turn?.render.turnProgress ?? -1) - 0.5) < 0.001, 'turn-mid: not at 50%', failures);
  assertEvidence((turn?.render.visibleSectionIds.length ?? 0) >= 2, 'turn-mid: route continuity not visible', failures);

  const laneEnd = byId.get('lane-end');
  assertEvidence(
    Math.abs((laneEnd?.render.presentedLanePosition ?? 99) - (laneEnd?.simulation.targetLane ?? 0)) <= 0.01,
    'lane-end: endpoint error exceeds 0.01 world lane unit',
    failures,
  );

  const turnLane = byId.get('turn-lane-change');
  assertEvidence(
    (turnLane?.render.turnProgress ?? 0) > 0.5 && (turnLane?.render.turnProgress ?? 1) < 1,
    'turn-lane-change: not captured during the outgoing turn half',
    failures,
  );
  assertEvidence(
    (turnLane?.simulation.targetLane ?? 0) > (turnLane?.simulation.lanePosition ?? 0) &&
      Math.abs(
        (turnLane?.simulation.lanePosition ?? 0) -
          (turnLane?.simulation.previousLanePosition ?? 0),
      ) > 0.001,
    'turn-lane-change: lane transition did not advance toward its canonical target',
    failures,
  );

  const milestone = byId.get('milestone');
  assertEvidence(milestone?.simulation.lastDistanceMilestone === 250, 'milestone: canonical marker missing', failures);
  assertEvidence((milestone?.simulation.score ?? 0) > 0, 'milestone: score did not progress', failures);
  assertEvidence(milestone?.ui.milestone?.includes('250 m'), 'milestone: visible 250 m callout missing', failures);

  const traceScenarios = ['milestone', 'chase-close', 'beam-preview', 'ring-preview', 'column-preview', 'gap-preview'];
  for (const id of traceScenarios) {
    const entry = byId.get(id);
    assertEvidence(entry?.simulation.scenarioTrace?.name === entry?.scenario, `${id}: missing matching command trace`, failures);
    assertEvidence(entry?.simulation.scenarioTrace?.replayHash === entry?.simulation.hash, `${id}: trace hash differs from canonical state`, failures);
    assertEvidence((entry?.simulation.scenarioTrace?.commands.length ?? 0) > 0, `${id}: command trace is empty`, failures);
  }

  const chaseClose = byId.get('chase-close');
  assertEvidence((chaseClose?.simulation.chaseGap ?? 99) <= 1.2, 'chase-close: canonical gap is not threatening', failures);
  assertEvidence(chaseClose?.render.pursuerScreen?.visible === true, 'chase-close: pursuer is not visible', failures);
  assertEvidence(
    (chaseClose?.render.pursuerScreen?.bounds?.area ?? 0) > 64,
    'chase-close: pursuer lacks meaningful clipped visible area',
    failures,
  );

  const hazardKinds = {
    'beam-preview': 'beam',
    'ring-preview': 'ring',
    'column-preview': 'column',
    'gap-preview': 'gap',
  };
  for (const [id, kind] of Object.entries(hazardKinds)) {
    const matching = byId.get(id)?.render.hazardScreens?.find((hazard) => hazard.kind === kind);
    assertEvidence(Boolean(matching), `${id}: canonical ${kind} has no renderer bounds`, failures);
    assertEvidence((matching?.bounds?.area ?? 0) > 64, `${id}: ${kind} bounds have no meaningful clipped area`, failures);
  }

  const highContrast = byId.get('pause-high-contrast');
  assertEvidence(highContrast?.appearance.highContrast === true, 'high contrast class not active', failures);
  assertEvidence(highContrast?.render.options.highContrast === true, 'renderer high contrast not active', failures);

  const reduced = byId.get('reduced-motion');
  assertEvidence(reduced?.appearance.reducedMotion === true, 'reduced-motion media query not active', failures);
  assertEvidence(reduced?.render.options.reducedMotion === true, 'renderer reduced motion not active', failures);

  const landscape = byId.get('landscape-running');
  for (const metric of landscape?.ui.hudMetrics ?? []) {
    assertEvidence(metric.insideViewport, `landscape-running: ${metric.selector} is outside the viewport`, failures);
  }
  assertEvidence((landscape?.ui.hudMetrics?.length ?? 0) === 4, 'landscape-running: a canonical HUD metric is hidden', failures);

  const desktop = byId.get('real-desktop-input');
  assertEvidence(desktop?.state.status === 'paused', 'desktop input: Escape did not pause', failures);
  assertEvidence(desktop?.state.targetLane === -1, 'desktop input: left command missing', failures);
  assertEvidence(desktop?.state.grounded === false, 'desktop input: jump command missing', failures);
  assertEvidence(desktop?.activeElement === 'CANVAS', 'desktop input: canvas focus missing', failures);
  assertEvidence(desktop?.consoleProblems.length === 0, 'desktop input: console problems', failures);
  const desktopEventTypes = desktop?.actions.map((action) => action.events.map((event) => event.type)) ?? [];
  assertEvidence(
    JSON.stringify(desktopEventTypes) === JSON.stringify([[], ['lane-shifted'], ['jump-started'], ['paused']]),
    'desktop input: one-input/one-event trace mismatch',
    failures,
  );

  const touch = byId.get('real-touch-input');
  assertEvidence(touch?.state.status === 'running', 'touch input: run not active', failures);
  assertEvidence(touch?.state.targetLane === -1, 'touch input: left swipe missing', failures);
  assertEvidence(touch?.consoleProblems.length === 0, 'touch input: console problems', failures);
  assertEvidence(
    JSON.stringify(touch?.swipe.events.map((event) => event.type)) === JSON.stringify(['lane-shifted']),
    'touch input: one-swipe/one-event trace mismatch',
    failures,
  );

  const benchmark = byId.get('desktop-scene-benchmark');
  assertEvidence(benchmark?.benchmark.p95Ms < 8, `benchmark: p95 ${benchmark?.benchmark.p95Ms}ms`, failures);
  assertEvidence(benchmark?.consoleProblems.length === 0, 'desktop benchmark: console problems', failures);
  const mobileBenchmark = byId.get('mobile-scene-benchmark');
  assertEvidence(mobileBenchmark?.benchmark.p95Ms < 12, `mobile benchmark: p95 ${mobileBenchmark?.benchmark.p95Ms}ms`, failures);
  assertEvidence(mobileBenchmark?.consoleProblems.length === 0, 'mobile benchmark: console problems', failures);

  const deterministicIds = ['running-desktop', 'mobile-portrait', 'mobile-landscape', 'reduced-motion'];
  const deterministicHashes = new Set(deterministicIds.map((id) => byId.get(id)?.simulation.hash));
  assertEvidence(deterministicHashes.size === 1 && !deterministicHashes.has(undefined), 'viewport changed simulation hash', failures);

  if (failures.length > 0) {
    throw new Error(`Temple evidence gate failed:\n- ${failures.join('\n- ')}`);
  }
}

function digest(buffer) {
  return createHash('sha256').update(buffer).digest('hex');
}

function compactSimulation(snapshot) {
  const state = snapshot.state;
  return {
    seed: state.seed,
    hash: snapshot.hash,
    frozen: snapshot.frozen,
    previousDistance: snapshot.previousState.distance,
    previousLanePosition: snapshot.previousState.runner.lanePosition,
    status: state.status,
    tick: state.tick,
    distance: state.distance,
    sectionIndex: state.sectionIndex,
    sectionDistance: state.sectionDistance,
    lanePosition: state.runner.lanePosition,
    targetLane: state.runner.targetLane,
    height: state.runner.height,
    grounded: state.runner.grounded,
    slideTicksRemaining: state.runner.slideTicksRemaining,
    shieldCharges: state.runner.shieldCharges,
    score: state.score,
    shards: state.shards,
    multiplier: state.multiplier,
    chaseGap: state.chaseGap,
    lastDistanceMilestone: state.lastDistanceMilestone,
    failureReason: state.failureReason,
    events: snapshot.events,
    scenarioTrace: snapshot.scenarioTrace,
  };
}

async function capture({
  id,
  scenario,
  viewport = { width: 1440, height: 900 },
  deviceScaleFactor = 1,
  isMobile = false,
  hasTouch = false,
  reducedMotion = 'no-preference',
  highContrast = false,
  pause = false,
  turnProgress = null,
  advanceTicks = 0,
  keys = [],
}) {
  if (!shouldRun(id)) return;
  currentPhase = 'capture';
  activeLabel = id;
  activeScenario = scenario ?? id;
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor,
    isMobile,
    hasTouch,
    reducedMotion,
    colorScheme: 'dark',
  });
  const page = await context.newPage();
  const problems = [];
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') {
      problems.push({ type: message.type(), text: message.text() });
    }
  });
  page.on('pageerror', (error) => problems.push({ type: 'pageerror', text: error.message }));
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.__TIDE_RELAY_QA__));
  if (highContrast) {
    await page.getByRole('button', { name: 'contrast' }).click();
    await page.waitForFunction(() => document.querySelector('main')?.classList.contains('is-high-contrast'));
  }
  if (scenario) {
    await page.evaluate((name) => window.__TIDE_RELAY_QA__.loadScenario(name), scenario);
  }
  if (keys.length > 0) {
    await page.locator('canvas').focus();
  }
  for (const key of keys) {
    await page.keyboard.press(key);
  }
  if (advanceTicks > 0) {
    await page.evaluate((count) => window.__TIDE_RELAY_QA__.advanceTicks(count), advanceTicks);
  }
  if (turnProgress !== null) {
    await page.evaluate((progress) => window.__TIDE_RELAY_QA__.setTurnProgress(progress), turnProgress);
  }
  if (pause) {
    await page.locator('canvas').focus();
    await page.keyboard.press('Escape');
  }
  await page.waitForTimeout(90);
  const structured = await page.evaluate(() => {
    const qa = window.__TIDE_RELAY_QA__;
    const visibleSafeArea = (selector) => {
      const element = document.querySelector(selector);
      if (!(element instanceof HTMLElement)) return null;
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      if (
        style.display === 'none' ||
        style.visibility === 'hidden' ||
        Number(style.opacity) <= 0.01 ||
        rect.width <= 0 ||
        rect.height <= 0
      ) return null;
      return {
        selector,
        left: rect.left,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        insideViewport:
          rect.left >= -0.5 &&
          rect.top >= -0.5 &&
          rect.right <= innerWidth + 0.5 &&
          rect.bottom <= innerHeight + 0.5,
      };
    };
    return {
      simulation: qa.getSimulationSnapshot(),
      render: qa.getRenderSnapshot(),
      dom: {
        canvasCount: document.querySelectorAll('canvas').length,
        gameplayEntityCount: document.querySelectorAll('[data-game-entity],[data-cell]').length,
        overflowX: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
      },
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio,
      },
      appearance: {
        highContrast: document.querySelector('main')?.classList.contains('is-high-contrast') ?? false,
        reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
      },
      ui: {
        hud: (() => {
          const hud = document.querySelector('.hud');
          return {
            score: Number(hud?.getAttribute('data-score')),
            distance: Number(hud?.getAttribute('data-distance')),
            shards: Number(hud?.getAttribute('data-shards')),
            flow: Number(hud?.getAttribute('data-flow')),
          };
        })(),
        hudText: {
          score: document.querySelector('.metric--score strong')?.textContent?.trim() ?? '',
          distance: document.querySelector('.metric--distance strong')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
          flow: document.querySelector('.metric--flow strong')?.textContent?.trim() ?? '',
          shards: document.querySelector('.metric--shards strong')?.textContent?.trim() ?? '',
        },
        hudMetrics: ['.metric--score', '.metric--distance', '.metric--flow', '.metric--shards']
          .map(visibleSafeArea)
          .filter(Boolean),
        // The HUD wrapper has intentionally translucent empty space: evidence
        // protects only visible copy/actions, never that full background hull.
        hudContent: ['.brandbar', '.metric--score', '.metric--distance', '.metric--flow', '.metric--shards', '.pause-control', '.gesture-hint', '.distance-milestone', '.turn-cue']
          .map(visibleSafeArea)
          .filter(Boolean),
        milestone: document.querySelector('.distance-milestone')?.textContent ?? null,
      },
      safeAreas: ['.brandbar', '.hud', '.pause-control', '.turn-cue', '.gesture-hint', '.touch-controls', '.settings']
        .map(visibleSafeArea)
        .filter(Boolean),
    };
  });
  const png = await page.screenshot({ type: 'png' });
  const screenshotPath = path.join(screenshotDir, `${id}.png`);
  await writeFile(screenshotPath, png);
  records.push({
    id,
    scenario,
    screenshot: path.relative(root, screenshotPath).replaceAll('\\', '/'),
    screenshotSha256: digest(png),
    viewport: structured.viewport,
    dom: structured.dom,
    appearance: structured.appearance,
    ui: structured.ui,
    safeAreas: structured.safeAreas,
    simulation: compactSimulation(structured.simulation),
    render: structured.render,
    consoleProblems: problems,
  });
  await context.close();
  currentPhase = 'captured';
}

async function realDesktopInput() {
  if (!shouldRun('real-desktop-input')) return;
  currentPhase = 'real-desktop-input';
  activeLabel = 'real-desktop-input';
  activeScenario = 'interactive-input';
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const problems = [];
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') problems.push(message.text());
  });
  page.on('pageerror', (error) => problems.push(error.message));
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  const actions = [];
  const recordAction = async (input) => {
    const snapshot = await page.evaluate(() => window.__TIDE_RELAY_QA__.getSimulationSnapshot());
    actions.push({
      input,
      hash: snapshot.hash,
      status: snapshot.state.status,
      events: snapshot.events,
    });
  };
  await page.getByRole('button', { name: /start running/i }).click();
  await page.evaluate(() => window.__TIDE_RELAY_QA__.freeze(true));
  await recordAction('Begin relay');
  await page.keyboard.press('ArrowLeft');
  await recordAction('ArrowLeft');
  await page.keyboard.press('Space');
  await recordAction('Space');
  await page.keyboard.press('Escape');
  await recordAction('Escape');
  const state = await page.evaluate(() => window.__TIDE_RELAY_QA__.getSimulationSnapshot().state);
  records.push({
    id: 'real-desktop-input',
    state: {
      status: state.status,
      targetLane: state.runner.targetLane,
      grounded: state.runner.grounded,
      verticalVelocity: state.runner.verticalVelocity,
    },
    actions,
    activeElement: await page.evaluate(() => document.activeElement?.tagName ?? null),
    consoleProblems: problems,
  });
  await context.close();
}

async function realTouchInput() {
  if (!shouldRun('real-touch-input')) return;
  currentPhase = 'real-touch-input';
  activeLabel = 'real-touch-input';
  activeScenario = 'interactive-input';
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    hasTouch: true,
    isMobile: true,
  });
  const page = await context.newPage();
  const problems = [];
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') problems.push(message.text());
  });
  page.on('pageerror', (error) => problems.push(error.message));
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /start running/i }).click();
  await page.evaluate(() => window.__TIDE_RELAY_QA__.freeze(true));
  const beforeSwipe = await page.evaluate(() => window.__TIDE_RELAY_QA__.getSimulationSnapshot());
  const canvas = page.locator('canvas');
  const box = await canvas.boundingBox();
  if (!box) throw new Error('Touch evidence canvas has no bounding box');
  const client = await context.newCDPSession(page);
  const x = box.x + box.width * 0.58;
  const y = box.y + box.height * 0.62;
  await client.send('Input.dispatchTouchEvent', {
    type: 'touchStart',
    touchPoints: [{ x, y, id: 1, radiusX: 4, radiusY: 4, force: 1 }],
  });
  await client.send('Input.dispatchTouchEvent', {
    type: 'touchMove',
    touchPoints: [{ x: x - 110, y, id: 1, radiusX: 4, radiusY: 4, force: 1 }],
  });
  await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  const afterSwipe = await page.evaluate(() => window.__TIDE_RELAY_QA__.getSimulationSnapshot());
  await page.waitForTimeout(50);
  const state = await page.evaluate(() => window.__TIDE_RELAY_QA__.getSimulationSnapshot().state);
  records.push({
    id: 'real-touch-input',
    state: { status: state.status, targetLane: state.runner.targetLane, lanePosition: state.runner.lanePosition },
    swipe: {
      beforeHash: beforeSwipe.hash,
      afterHash: afterSwipe.hash,
      events: afterSwipe.events,
    },
    viewport: await page.evaluate(() => ({ width: innerWidth, height: innerHeight, dpr: devicePixelRatio })),
    consoleProblems: problems,
  });
  await context.close();
}

async function benchmarkScene(id, contextOptions, iterations, limitMs) {
  if (!shouldRun(id)) return;
  currentPhase = 'benchmark';
  activeLabel = id;
  activeScenario = 'fixed-workload';
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();
  const problems = [];
  page.on('console', (message) => {
    if (message.type() === 'error' || message.type() === 'warning') problems.push(message.text());
  });
  page.on('pageerror', (error) => problems.push(error.message));
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.__TIDE_RELAY_QA__));
  await page.evaluate(() => window.__TIDE_RELAY_QA__.loadScenario('running'));
  const benchmark = await page.evaluate((count) => window.__TIDE_RELAY_QA__.benchmarkFrames(count), iterations);
  records.push({ id, iterations, limitMs, benchmark, consoleProblems: problems });
  await context.close();
}

async function main() {
  try {
  currentPhase = 'browser-launch';
  verifyResolvedBaseUrl();
  await mkdir(screenshotDir, { recursive: true });
  browser = await chromium.launch({ headless: true, executablePath: chromePath });
  currentPhase = 'capture-plan';
  await capture({ id: 'ready-desktop', scenario: 'ready' });
  await capture({ id: 'running-desktop', scenario: 'running' });
  await capture({ id: 'lane-mid', scenario: 'lane-mid' });
  await capture({ id: 'lane-end', scenario: 'lane-mid', advanceTicks: 5 });
  await capture({ id: 'jump-apex', scenario: 'jump-apex' });
  await capture({ id: 'slide-mid', scenario: 'slide-mid' });
  await capture({ id: 'turn-mid', scenario: 'turn-mid', turnProgress: 0.5 });
  await capture({
    id: 'turn-lane-change',
    scenario: 'turn-mid',
    keys: ['ArrowRight'],
    advanceTicks: 5,
  });
  await capture({ id: 'collision', scenario: 'collision' });
  await capture({ id: 'milestone', scenario: 'milestone' });
  await capture({ id: 'chase-close', scenario: 'chase-close' });
  await capture({ id: 'pause-high-contrast', scenario: 'running', highContrast: true, pause: true });
  await capture({ id: 'beam-preview', scenario: 'beam-preview' });
  await capture({
    id: 'ring-preview',
    scenario: 'ring-preview',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({
    id: 'column-preview',
    scenario: 'column-preview',
    viewport: { width: 844, height: 390 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({ id: 'gap-preview', scenario: 'gap-preview', highContrast: true });
  await capture({
    id: 'mobile-portrait',
    scenario: 'running',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({
    id: 'mobile-landscape',
    scenario: 'running',
    viewport: { width: 844, height: 390 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({ id: 'reduced-motion', scenario: 'running', reducedMotion: 'reduce' });
  // Formal TR3 matrix: each screenshot is the real command-derived production runtime.
  await capture({ id: 'desktop-normal', scenario: 'running' });
  await capture({ id: 'desktop-close-chase', scenario: 'chase-close' });
  await capture({ id: 'desktop-milestone', scenario: 'milestone' });
  await capture({ id: 'desktop-paused', scenario: 'running', pause: true });
  await capture({ id: 'desktop-beam', scenario: 'beam-preview' });
  await capture({ id: 'desktop-ring', scenario: 'ring-preview' });
  await capture({ id: 'desktop-column', scenario: 'column-preview' });
  await capture({ id: 'desktop-gap', scenario: 'gap-preview' });
  await capture({
    id: 'mobile-normal',
    scenario: 'running',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({
    id: 'mobile-close-chase',
    scenario: 'chase-close',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({
    id: 'mobile-milestone',
    scenario: 'milestone',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await capture({
    id: 'landscape-running',
    scenario: 'running',
    viewport: { width: 844, height: 390 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  await realDesktopInput();
  await realTouchInput();
  await benchmarkScene(
    'desktop-scene-benchmark',
    { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
    180,
    8,
  );
  await benchmarkScene(
    'mobile-scene-benchmark',
    {
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 3,
      hasTouch: true,
      isMobile: true,
    },
    180,
    12,
  );

  currentPhase = 'validate';
  activeLabel = diagnosticMode ? [...selectedLabels].join(',') : 'full-matrix';
  activeScenario = diagnosticMode ? 'diagnostic-validation' : 'full-validation';
  validateEvidence(records);
  currentPhase = diagnosticMode ? 'write-diagnostic' : 'write-manifest';
  const outputPath = diagnosticMode ? diagnosticPath : evidencePath;
  await writeFile(outputPath, `${JSON.stringify({
    generatedAt: new Date().toISOString(),
    head,
    resolvedBaseUrl: baseUrl,
    browser: await browser.version(),
    diagnosticMode,
    d4DevMode,
    labels: [...selectedLabels],
    records,
  }, null, 2)}\n`, 'utf8');
  await clearFailure();
  console.log(`Captured ${records.length} evidence records to ${outputPath}`);
  } catch (error) {
  await writeFailure(error);
  console.error(error);
  process.exitCode = 1;
  } finally {
  await browser?.close();
  }
}

if (cli.selfTest) {
  runCliRegression();
} else {
  await main();
}
