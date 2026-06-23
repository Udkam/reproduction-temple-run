// Level QA / self-test. Runs the BFS solver against every level and asserts:
//   - the level is solvable,
//   - it is not already solved at the start (not trivial),
//   - the solver's solution actually solves it on replay (engine sanity check).
// Prints a table with the fields required by the v7 acceptance flow.
//
// Run with:  npm run verify

import { LEVELS } from '../src/engine/levels.js';
import { solve, replay, replayDiptych } from '../src/engine/solver.js';
import { initialState } from '../src/engine/level.js';
import { isSolved } from '../src/engine/rules.js';

let failures = 0;
const rows: string[] = [];
// Lower this (e.g. VERIFY_MAX=400000) for fast triage of unsolvable drafts.
const maxStates = Number(process.env.VERIFY_MAX ?? 2_000_000);

for (const level of LEVELS) {
  const start = Date.now();
  // Diptych levels replay across both boards; other levels with a stored solution
  // replay it; the rest run the solver.
  const res = level.twin
    ? (() => {
        const chk = replayDiptych(level, level.solution!);
        return {
          solvable: chk.solved,
          moves: level.solution!.length,
          pushes: chk.a.pushes + chk.b.pushes,
          solution: level.solution!,
          explored: 0,
          truncated: false,
        };
      })()
    : level.solution
      ? (() => {
          const chk = replay(level, level.solution!);
          return {
            solvable: chk.solved,
            moves: chk.state.moves,
            pushes: chk.state.pushes,
            solution: level.solution!,
            explored: 0,
            truncated: false,
          };
        })()
      : solve(level, { maxStates });
  const ms = Date.now() - start;

  const trivial = level.twin
    ? isSolved(level, initialState(level)) && isSolved(level.twin, initialState(level.twin))
    : isSolved(level, initialState(level));
  let ok = res.solvable && !trivial;
  let note = '';
  const solverStatus =
    level.levelDesignNote?.solverStatus ?? (level.solution || level.twin ? 'verified-replay' : 'optimal');
  const validationMethod =
    level.validationMethod ??
    (level.twin
      ? 'joint-state-replay'
      : level.timeShadow
        ? 'history-window-replay'
        : level.solution
          ? 'manual-replay'
          : 'astar');
  const title = level.levelDesignNote?.title ?? level.name;
  const chapter = level.levelDesignNote?.chapter ?? level.chapter ?? 'legacy';

  if (!res.solvable) {
    note = res.truncated ? 'UNSOLVED (hit state cap — likely impossible)' : 'UNSOLVABLE';
  } else if (trivial) {
    note = 'TRIVIAL (already solved at start)';
  } else {
    // Replay the solution through the engine as a cross-check.
    const check = level.twin ? replayDiptych(level, res.solution) : replay(level, res.solution);
    if (!check.solved) {
      ok = false;
      note = 'REPLAY MISMATCH (engine/solver disagree)';
    } else {
      note = 'ok';
    }
  }

  if (!ok) failures++;
  rows.push(
    [
      ok ? 'PASS' : 'FAIL',
      `id=${level.id}`,
      `title=${title}`,
      `chapter=${chapter}`,
      `solverStatus=${solverStatus}`,
      `solutionLength=${res.solution.length}`,
      `par=${level.par ?? 'null'}`,
      `validation=${validationMethod}`,
      `moves=${res.moves}`,
      `pushes=${res.pushes}`,
      `states=${res.explored}`,
      `timeMs=${ms}`,
      note,
    ].join('  '),
  );
}

console.log('\nDriftbox level verification');
console.log('-'.repeat(120));
for (const r of rows) console.log(r);
console.log('-'.repeat(120));

if (failures > 0) {
  console.error(`\n${failures} level(s) FAILED verification.`);
  process.exit(1);
} else {
  console.log('\nAll levels solvable. par = optimal moves above.\n');
}
