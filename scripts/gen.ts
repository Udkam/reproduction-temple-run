// Reverse-pull level generator. Classic-push only (no special tiles).
//
// Idea: a Sokoban level is solvable iff its solved state can be reached by
// *pushes*. Equivalently, any state reachable from the solved state by *pulls*
// is solvable. So: start with boxes on the goals, randomly pull them around the
// (hand-drawn, irregular) outline, and the reversed pull sequence is a guaranteed
// forward solution — which we replay through the real engine to be certain.
//
// For each outline we try many random scrambles and keep the hardest valid one
// (by optimal par when the solver can find it within a cap, else by the length of
// the guaranteed solution). The chosen levels are written to src/engine/generated.ts.
//
// Run with:  npm run gen

import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import type { Dir } from '../src/engine/types.js';
import { parseLevel, initialState } from '../src/engine/level.js';
import { applyMove, isSolved } from '../src/engine/rules.js';
import { solve } from '../src/engine/solver.js';

const D: Record<Dir, { dx: number; dy: number }> = {
  up: { dx: 0, dy: -1 },
  down: { dx: 0, dy: 1 },
  left: { dx: -1, dy: 0 },
  right: { dx: 1, dy: 0 },
};
const OPP: Record<Dir, Dir> = { up: 'down', down: 'up', left: 'right', right: 'left' };
const DLIST: Dir[] = ['up', 'down', 'left', 'right'];

interface Outline {
  id: string;
  name: string;
  subtitle: string;
  chapter: string;
  rows: string[];
}

function rng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

interface Candidate {
  map: string[];
  solution: Dir[];
  scattered: number; // boxes NOT on a goal at start
  goals: number;
  displacement: number; // sum of each box's Manhattan distance to its nearest goal
}

function scramble(o: Outline, seed: number, steps: number): Candidate {
  const H = o.rows.length;
  const W = Math.max(...o.rows.map((r) => r.length));
  // Any unspecified cell (ragged short rows) counts as wall, so borders stay solid.
  const wall = (x: number, y: number) => {
    const ch = o.rows[y]?.[x];
    return ch === undefined || ch === '#';
  };
  const inb = (x: number, y: number) => x >= 0 && y >= 0 && x < W && y < H;

  const goals: number[] = [];
  let px = 0;
  let py = 0;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const ch = o.rows[y]?.[x] ?? ' ';
      if (ch === '.') goals.push(y * W + x);
      if (ch === '@') {
        px = x;
        py = y;
      }
    }
  }
  const boxes = new Set(goals);
  const boxAt = (x: number, y: number) => boxes.has(y * W + x);
  const free = (x: number, y: number) => inb(x, y) && !wall(x, y) && !boxAt(x, y);
  const rand = rng(seed);
  const moves: Dir[] = [];

  for (let i = 0; i < steps; i++) {
    const order = [...DLIST].sort(() => rand() - 0.5);
    let did = false;
    // Prefer a pull: player steps to player+m (free) dragging a box at player-m.
    for (const m of order) {
      const d = D[m];
      const fx = px + d.dx;
      const fy = py + d.dy;
      const bx = px - d.dx;
      const by = py - d.dy;
      if (free(fx, fy) && boxAt(bx, by) && rand() < 0.75) {
        boxes.delete(by * W + bx);
        boxes.add(py * W + px);
        px = fx;
        py = fy;
        moves.push(m);
        did = true;
        break;
      }
    }
    if (did) continue;
    for (const m of order) {
      const d = D[m];
      const fx = px + d.dx;
      const fy = py + d.dy;
      if (free(fx, fy)) {
        px = fx;
        py = fy;
        moves.push(m);
        did = true;
        break;
      }
    }
  }

  const grid: string[][] = [];
  for (let y = 0; y < H; y++) {
    grid.push(Array.from({ length: W }, (_, x) => (wall(x, y) ? '#' : ' ')));
  }
  for (const g of goals) grid[Math.floor(g / W)]![g % W] = '.';
  for (const b of boxes) {
    const x = b % W;
    const y = Math.floor(b / W);
    grid[y]![x] = grid[y]![x] === '.' ? '*' : '$';
  }
  grid[py]![px] = grid[py]![px] === '.' ? '+' : '@';

  const scattered = [...boxes].filter((b) => !goals.includes(b)).length;
  let displacement = 0;
  for (const b of boxes) {
    if (goals.includes(b)) continue;
    const bx = b % W;
    const by = Math.floor(b / W);
    let nearest = Infinity;
    for (const g of goals) nearest = Math.min(nearest, Math.abs(bx - (g % W)) + Math.abs(by - Math.floor(g / W)));
    displacement += nearest;
  }
  return {
    map: grid.map((r) => r.join('')),
    solution: [...moves].reverse().map((m) => OPP[m]),
    scattered,
    goals: goals.length,
    displacement,
  };
}

function validSolution(map: string[], solution: Dir[]): boolean {
  const lvl = parseLevel({ id: 't', name: 't', subtitle: '', intro: '', map });
  let st = initialState(lvl);
  if (isSolved(lvl, st)) return false; // already solved → trivial
  for (const dir of solution) st = applyMove(lvl, st, dir).state;
  return isSolved(lvl, st);
}

// ── outlines (hand-drawn, irregular, open). '.' goal · '@' player · '#' wall ──
// Keep boxes/goals <= 5: the A* matching heuristic is exponential in goal count.
const OUTLINES: Outline[] = [
  { id: 'g1', name: '盘陀', subtitle: 'Switchback', chapter: '回环', rows: [
    '##########', '##@  .   #', '#   . .  #', '#   .    #', '#    .  ##', '##########' ] },
  { id: 'g2', name: '蛛网', subtitle: 'Webwork', chapter: '回环', rows: [
    '##########', '#@  .  . #', '#   . .  #', '#  .    ##', '##      ##', '##########' ] },
  { id: 'g3', name: '阡陌', subtitle: 'Furrows', chapter: '回环', rows: [
    '###########', '#@   .    #', '#  .   .  #', '#    #    #', '#  .   .  #', '###########' ] },
  { id: 'g4', name: '辐辏', subtitle: 'Spokes', chapter: '回环', rows: [
    '##########', '#@      ##', '#  . .  . #', '#  #  #   #', '#  . .    #', '##########' ] },
  { id: 'g5', name: '错综', subtitle: 'Tangle', chapter: '迷宫', rows: [
    '###########', '#@    .   #', '#  .   .  #', '#   ##    #', '#  .   .  #', '###########' ] },
  { id: 'g6', name: '曲尺', subtitle: 'Carpenter', chapter: '迷宫', rows: [
    '##########', '#@      ##', '#  . .   #', '#  .  .  #', '##  .   ##', '##########' ] },
  { id: 'g7', name: '回纹', subtitle: 'Fretwork', chapter: '迷宫', rows: [
    '##########', '#@   .  ##', '#  .   . #', '#   # #  #', '#  .  .  #', '##########' ] },
  { id: 'g8', name: '枢纽', subtitle: 'Junction', chapter: '迷宫', rows: [
    '###########', '##@   .   #', '#   .  .  #', '#    ##   #', '#   .  .  #', '###########' ] },
  { id: 'g9', name: '叠嶂', subtitle: 'Ranges', chapter: '险峰', rows: [
    '###########', '#@   .    #', '#   .  .  #', '#  .  #   #', '#    .   ##', '###########' ] },
  { id: 'g10', name: '棋枰', subtitle: 'Gridlock', chapter: '险峰', rows: [
    '##########', '#@  . .  #', '#  .   . #', '#    #   #', '#   . .  #', '##########' ] },
  { id: 'g11', name: '迂回', subtitle: 'Detour', chapter: '险峰', rows: [
    '###########', '##@   .   #', '#    . .  #', '#   .   . #', '#     .  ##', '###########' ] },
  { id: 'g12', name: '环堵', subtitle: 'Ringwall', chapter: '险峰', rows: [
    '##########', '#@  .  . #', '#   .  . #', '##  #  # #', '#   . .  #', '##########' ] },
  { id: 'g13', name: '罅隙', subtitle: 'Crevice', chapter: '险峰', rows: [
    '##########', '#@   .   #', '# .   .  #', '#   #    #', '# .   .  #', '##########' ] },
  { id: 'g14', name: '渊薮', subtitle: 'Warren', chapter: '险峰', rows: [
    '###########', '#@  .  .  #', '#  .   .  #', '##   .   ##', '#        ##', '###########' ] },
];

const here = dirname(fileURLToPath(import.meta.url));
const OUT = join(here, '..', 'src', 'engine', 'generated.ts');

const ATTEMPTS = 300;
const PER_OUTLINE = 3;
const MIN_PAR = 18;
const SOLVE_CAP = 500_000;

const chosen: { o: Outline; map: string[]; solution: Dir[]; par: number; approx: boolean; suffix: string }[] = [];

for (const o of OUTLINES) {
  // Collect valid, deduped candidates, hardest (by displacement) first.
  const seen = new Set<string>();
  const cands: Candidate[] = [];
  for (let a = 0; a < ATTEMPTS; a++) {
    const steps = 70 + Math.floor((a / ATTEMPTS) * 200);
    const cand = scramble(o, a * 7919 + 13, steps);
    if (cand.scattered === 0) continue;
    const key = cand.map.join('\n');
    if (seen.has(key)) continue;
    if (!validSolution(cand.map, cand.solution)) continue;
    seen.add(key);
    cands.push(cand);
  }
  cands.sort((p, q) => q.displacement - p.displacement);

  const kept: typeof chosen = [];
  for (const cand of cands.slice(0, 12)) {
    const lvl = parseLevel({ id: o.id, name: o.name, subtitle: o.subtitle, intro: '', map: cand.map });
    const res = solve(lvl, { maxStates: SOLVE_CAP });
    if (!res.solvable) continue; // keep only levels with a true optimal par
    if (res.moves < MIN_PAR) continue;
    kept.push({
      o,
      map: cand.map,
      solution: res.solution,
      par: res.moves,
      approx: false,
      suffix: String.fromCharCode(97 + kept.length),
    });
    if (kept.length >= PER_OUTLINE) break;
  }
  if (kept.length === 0) {
    console.log(`✗ ${o.id} ${o.name}: nothing >= par ${MIN_PAR}`);
    continue;
  }
  for (const k of kept) {
    chosen.push(k);
    const boxes = (k.map.join('').match(/[$*]/g) || []).length;
    console.log(`✓ ${o.id}${k.suffix} ${o.name.padEnd(4)} par=${String(k.par).padStart(3)}${k.approx ? '~' : ' '} boxes=${boxes}`);
  }
}

// Emit src/engine/generated.ts
const NUM: Record<string, string> = { a: '', b: '·二', c: '·三', d: '·四' };
const body = chosen
  .map((c) => {
    const map = c.map.map((r) => `      ${JSON.stringify(r)},`).join('\n');
    const sol = JSON.stringify(c.solution);
    const id = c.o.id + c.suffix;
    const name = c.o.name + (NUM[c.suffix] ?? '');
    return `  {\n    id: ${JSON.stringify(id)},\n    name: ${JSON.stringify(name)},\n    subtitle: ${JSON.stringify(c.o.subtitle)},\n    chapter: ${JSON.stringify(c.o.chapter)},\n    par: ${c.par},\n    map: [\n${map}\n    ],\n    solution: ${sol},\n  },`;
  })
  .join('\n');

const file = `// AUTO-GENERATED by scripts/gen.ts — do not edit by hand.
// Reverse-pull classic levels with a verified forward \`solution\` (so even levels
// the A* solver can't crack within its cap stay testable).

export interface GeneratedLevel {
  id: string;
  name: string;
  subtitle: string;
  chapter: string;
  par: number;
  map: string[];
  solution: string[];
}

export const GENERATED: GeneratedLevel[] = [
${body}
];
`;
writeFileSync(OUT, file);
console.log(`\nWrote ${chosen.length} levels to ${OUT}`);
