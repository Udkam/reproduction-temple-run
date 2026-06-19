// Local progress (always works offline) plus best-effort server sync. The server
// is authoritative for the public leaderboard, but the game never blocks on it.

export interface Progress {
  completed: Record<string, boolean>;
  best: Record<string, number>; // best move count per level id
  bestPush: Record<string, number>; // fewest pushes per level id
  parHit: Record<string, boolean>; // cleared at or under the par move count
  clean: Record<string, boolean>; // cleared at least once without using undo
}

const KEY = 'driftbox.progress.v1';
const NAME_KEY = 'driftbox.name';

const EMPTY: Progress = { completed: {}, best: {}, bestPush: {}, parHit: {}, clean: {} };

export function loadProgress(): Progress {
  try {
    const raw = localStorage.getItem(KEY);
    // Spread defaults first so older saves (without the newer maps) stay valid.
    if (raw) return { ...EMPTY, ...JSON.parse(raw) } as Progress;
  } catch {
    /* ignore corrupt storage */
  }
  return { ...EMPTY };
}

export function saveProgress(p: Progress): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch {
    /* storage may be unavailable (private mode) — fine */
  }
}

export interface ClearInfo {
  moves: number;
  pushes: number;
  par: number;
  usedUndo: boolean;
}

export interface ClearOutcome {
  fresh: boolean; // first clear or a new best-move record
  newPush: boolean; // a new fewest-pushes record
  parHit: boolean; // this run reached par
  clean: boolean; // this run used no undo
  firstParHit: boolean; // par medal earned for the first time on this run
  firstClean: boolean; // clean medal earned for the first time on this run
}

/** Record a clear and update every personal record / challenge medal. */
export function recordClear(p: Progress, id: string, info: ClearInfo): ClearOutcome {
  const first = !p.completed[id];
  p.completed[id] = true;

  const prevBest = p.best[id];
  const improved = prevBest === undefined || info.moves < prevBest;
  if (improved) p.best[id] = info.moves;

  const prevPush = p.bestPush[id];
  const newPush = prevPush === undefined || info.pushes < prevPush;
  if (newPush) p.bestPush[id] = info.pushes;

  const parHit = info.moves <= info.par;
  const firstParHit = parHit && !p.parHit[id];
  if (parHit) p.parHit[id] = true;

  const clean = !info.usedUndo;
  const firstClean = clean && !p.clean[id];
  if (clean) p.clean[id] = true;

  saveProgress(p);
  return { fresh: first || improved, newPush, parHit, clean, firstParHit, firstClean };
}

export interface ChapterStat {
  total: number;
  cleared: number;
  parHit: number;
  complete: boolean; // every level cleared
  perfect: boolean; // every level cleared at par
}

/** Per-chapter mastery, derived purely from progress (no extra storage). */
export function chapterStats(
  ids: string[],
  chapterOf: Record<string, string>,
  p: Progress,
): Record<string, ChapterStat> {
  const out: Record<string, ChapterStat> = {};
  for (const id of ids) {
    const ch = chapterOf[id] ?? '';
    const s = (out[ch] ??= { total: 0, cleared: 0, parHit: 0, complete: false, perfect: false });
    s.total++;
    if (p.completed[id]) s.cleared++;
    if (p.parHit[id]) s.parHit++;
  }
  for (const s of Object.values(out)) {
    s.complete = s.cleared === s.total;
    s.perfect = s.parHit === s.total;
  }
  return out;
}

export function isUnlocked(order: string[], id: string, p: Progress): boolean {
  const i = order.indexOf(id);
  if (i <= 0) return true;
  return !!p.completed[order[i - 1]!];
}

export function getName(): string {
  return localStorage.getItem(NAME_KEY) || '旅人';
}
export function setName(name: string): void {
  localStorage.setItem(NAME_KEY, name.slice(0, 24));
}

// ---- server sync (all best-effort; swallow errors so offline play is seamless) ----

export interface ScoreRow {
  name: string;
  moves: number;
  pushes: number;
}

export async function submitScore(
  levelId: string,
  moves: number,
  pushes: number,
  solution: string[],
): Promise<void> {
  try {
    await fetch('/api/scores', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ levelId, name: getName(), moves, pushes, solution }),
    });
  } catch {
    /* offline / no backend — local progress already saved */
  }
}

export async function fetchLeaderboard(levelId: string): Promise<ScoreRow[]> {
  try {
    const res = await fetch(`/api/scores/${encodeURIComponent(levelId)}`);
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.scores) ? data.scores : [];
  } catch {
    return [];
  }
}
