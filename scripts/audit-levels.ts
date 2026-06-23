import { LEVEL_DEFS, LEVELS } from '../src/engine/levels.js';
import { initialState } from '../src/engine/level.js';
import { applyToken } from '../src/engine/rules.js';
import type { V7Mechanic } from '../src/engine/types.js';

const EXPECTED_COUNTS: Record<string, number> = {
  '第 1 章：启动序列': 4,
  '第 2 章：量子链接': 3,
  '第 3 章：同步体': 3,
  '第 4 章：时间残影': 3,
  '第 5 章：空间置换': 3,
  '第 6 章：递归舱': 2,
  '第 7 章：误导协议': 2,
};

const REQUIRED_MECHANICS: V7Mechanic[] = [
  'core-push',
  'quantum-portal',
  'sync-actors',
  'time-shadow',
  'spatial-swap',
  'recursive-room',
  'worldline-split',
  'rule-block',
  'misdirection',
];

let failures = 0;
let warnings = 0;

function fail(message: string): void {
  failures++;
  console.error(`FAIL ${message}`);
}

function warn(message: string): void {
  warnings++;
  console.warn(`WARN ${message}`);
}

function pass(message: string): void {
  console.log(`PASS ${message}`);
}

function defSignature(def: (typeof LEVEL_DEFS)[number]): string {
  return JSON.stringify({
    map: def.map,
    twin: def.twin ?? null,
    mirrorTwin: def.mirrorTwin ?? false,
    timeShadow: def.timeShadow ?? null,
    spatialSwap: def.spatialSwap ?? null,
    recursiveRoom: def.recursiveRoom ?? null,
    mechanics: def.mechanics ?? [],
  });
}

console.log('\nDriftbox redesign level audit');
console.log('-'.repeat(72));

if (LEVELS.length !== 20) fail(`expected exactly 20 redesign slice levels, found ${LEVELS.length}`);
else pass('exactly 20 redesign slice levels exposed');

if (LEVEL_DEFS.length !== LEVELS.length) fail('LEVEL_DEFS and LEVELS length mismatch');

const ids = new Set<string>();
for (const level of LEVELS) {
  if (ids.has(level.id)) fail(`duplicate id ${level.id}`);
  ids.add(level.id);
}
if (ids.size === LEVELS.length) pass('level ids are unique');

const counts: Record<string, number> = {};
for (const level of LEVELS) {
  const chapter = level.levelDesignNote?.chapter ?? level.chapter ?? '';
  counts[chapter] = (counts[chapter] ?? 0) + 1;
}
for (const [chapter, expected] of Object.entries(EXPECTED_COUNTS)) {
  const actual = counts[chapter] ?? 0;
  if (actual !== expected) fail(`${chapter} count expected ${expected}, got ${actual}`);
  else pass(`${chapter} count ${actual}`);
}

for (const unexpected of Object.keys(counts).filter((chapter) => !(chapter in EXPECTED_COUNTS))) {
  fail(`unexpected chapter in redesign slice: ${unexpected}`);
}

for (const level of LEVELS) {
  const note = level.levelDesignNote;
  if (!note) {
    fail(`${level.id} missing levelDesignNote`);
    continue;
  }
  const missing: string[] = [];
  if (note.id !== level.id) missing.push('matching id');
  if (!note.title) missing.push('title');
  if (!note.chapter) missing.push('chapter');
  if (!note.mechanics?.length) missing.push('mechanics');
  if (!note.coreIdea || note.coreIdea.length < 18) missing.push('coreIdea');
  if (!note.trick || note.trick.length < 12) missing.push('trick');
  if (!note.fairness || note.fairness.length < 18) missing.push('fairness');
  if (note.difficulty < 1 || note.difficulty > 5) missing.push('difficulty');
  if (!['optimal', 'verified-replay', 'manual-reviewed'].includes(note.solverStatus)) missing.push('solverStatus');
  if (note.par !== level.par) missing.push('par matches runtime');
  if (!note.solution?.length) missing.push('solution');
  if (missing.length) fail(`${level.id} metadata incomplete: ${missing.join(', ')}`);
  if (note.solverStatus !== 'optimal' && note.par !== note.solution.length) {
    fail(`${level.id} replay/manual par must match solution length (${note.par} != ${note.solution.length})`);
  }
  if ((level.solution?.length ?? 0) <= 1) fail(`${level.id} looks like a one-step water level`);
}
pass('metadata and water-level scan complete');

const mechanicSeen = new Set<V7Mechanic>();
for (const level of LEVELS) {
  for (const mech of level.levelDesignNote?.mechanics ?? []) mechanicSeen.add(mech);
}
for (const mech of REQUIRED_MECHANICS) {
  if (!mechanicSeen.has(mech)) fail(`required mechanic missing from corpus: ${mech}`);
  else pass(`mechanic present: ${mech}`);
}

const activeSwap = LEVELS.some((level) =>
  level.spatialSwap?.trigger !== undefined &&
  level.spatialSwap.trigger !== 'replay-only' &&
  !!level.spatialSwap.triggerAt &&
  !!level.spatialSwap.exchange,
);
if (!activeSwap) fail('spatial-swap corpus has no active trigger/exchange rule');
else pass('spatial-swap has at least one active trigger/exchange rule');

const swapProbe = LEVELS.find((level) => level.spatialSwap?.trigger === 'player-step' && level.spatialSwap.exchange);
if (!swapProbe) {
  fail('no runtime level available for spatial-swap behavior probe');
} else {
  const first = swapProbe.solution?.[0];
  const res = first ? applyToken(swapProbe, initialState(swapProbe), first) : null;
  const target = swapProbe.spatialSwap!.exchange![1]!;
  const swapped = !!res?.changed && res.state.crates.some((c) => c.x === target.x && c.y === target.y);
  if (!swapped) fail(`${swapProbe.id} spatial-swap behavior probe did not move a crate to the exchange target`);
  else pass(`${swapProbe.id} spatial-swap behavior probe passed`);
}

const recursiveLevels = LEVELS.filter((level) => level.mechanics?.includes('recursive-room'));
if (!recursiveLevels.every((level) => !!level.recursiveRoom?.entryCrateId || level.recursiveRoom?.entryCrateId === 0)) {
  fail('recursive levels must identify an entry core');
} else {
  pass('recursive levels identify entry cores');
}

const branchLevels = LEVELS.filter((level) => level.mechanics?.includes('worldline-split'));
if (!branchLevels.length || !branchLevels.every((level) => !!level.twin)) {
  fail('worldline split levels must expose a visible branch/twin state');
} else {
  pass('worldline split levels expose visible branch/twin state');
}

const signatures = new Map<string, string[]>();
for (const def of LEVEL_DEFS) {
  const sig = defSignature(def);
  const list = signatures.get(sig) ?? [];
  list.push(def.id);
  signatures.set(sig, list);
}
for (const idsForSig of signatures.values()) {
  if (idsForSig.length > 1) fail(`duplicate exact layout signature: ${idsForSig.join(', ')}`);
}
pass('exact layout duplicate scan complete');

const manualOrReplay = LEVELS.filter((level) =>
  ['verified-replay', 'manual-reviewed'].includes(level.levelDesignNote?.solverStatus ?? ''),
);
if (manualOrReplay.length === LEVELS.length) {
  warn('all redesign slice levels rely on replay/manual status; acceptable for slice, but solver depth remains future work.');
}

console.log('-'.repeat(72));
console.log(`Level audit complete: failures=${failures}, warnings=${warnings}`);
if (failures) process.exit(1);
