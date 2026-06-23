# Codex Work Log

## v7-loop-20260623-195154-f683

### Stage 1: Project reset and audit docs

Phase: documentation and loop setup.

Actions taken:

- Confirmed `main` is up to date with `origin/main`.
- Created the v7 loop directory structure.
- Added required v7 planning and audit files.
- Added required agent log files.
- Recorded the rule that every stage must verify, commit, and push to `origin main`.

Verification commands and results:

- `git status --short`: only Stage 1 documentation files are untracked.
- `npm run typecheck`: passed.
- `npm run verify`: passed, current baseline still reports 60/60 existing levels.
- `npm run smoke:api`: passed; `node:sqlite` ExperimentalWarning is non-fatal.
- `npm run smoke:ui`: passed; known blind spot remains for current 3D crate counting.

Changed files:

- `docs/v7-loop/CURRENT_RUN_ID.txt`
- `docs/v7-loop/v7-loop-20260623-195154-f683/*`
- `codex.md`

Risks:

- Stage 1 only establishes documentation and process; product code is not changed yet.

Next steps:

- Commit and push Stage 1.
- Begin Stage 2 route/runtime cleanup.

### Stage 2: Project reset and route cleanup

Phase: runtime v6 retirement.

Actions taken:

- Removed v6 3D level definitions from the exposed runtime catalog.
- Removed the visible `立体演示 (dev)` menu entry.
- Updated README, claude.md, and package description to mark v6 2.5D as retired and v7 as the current rebuild.
- Kept old 2.5D source code as unreachable historical reference for now.

Verification commands and results:

- `npm run typecheck`: passed.
- `npm run verify`: passed, 52/52 current exposed levels.
- `npm run smoke:api`: passed, `/api/levels` returns 52 levels.
- `npm run smoke:ui`: passed for all exposed levels.
- `npx tsx -e "...LEVELS check..."`: passed with `count=52`, no `3d*`, no `is3D`.
- `npm run build`: passed.
- A direct `node` import check failed because TypeScript source imports use `.js` specifiers before build; replaced with the `tsx` check.

Changed files:

- `README.md`
- `claude.md`
- `package.json`
- `src/engine/levels.ts`
- `src/web/ui.ts`
- v7 loop docs and agent logs

Risks:

- Old 2.5D source still exists but is not visible in the runtime catalog. Later stages should remove or archive it as the v7 shell replaces legacy UI.

Next steps:

- Commit and push Stage 2.
- Begin Stage 3 sci-fi art system and UI shell.

### Stage 3: New sci-fi art system and navigation shell

Phase: product shell and visual reset.

Actions taken:

- Replaced the old paper/wood CSS with a dark 2D sci-fi visual system.
- Rebuilt the home view as a command deck with progress, recent level, continue, chapter star map, mechanism archive, challenge records, and settings.
- Added records and settings overlays.
- Removed remaining visible 3D divider/badge handling from the home flow.
- Converted the package description to ASCII-only punctuation after confirming PowerShell console mojibake was only display/script-pipe related.

Verification commands and results:

- `npm run typecheck`: passed.
- `npm run verify`: passed, 52/52 current exposed levels.
- `npm run smoke:api`: passed, `/api/levels` returns 52 levels.
- `npm run smoke:ui`: passed for all exposed levels.
- `npm run build`: passed.
- Temporary `npx tsx -` DOM audit: passed for `.home-deck`, `#chapter-map`, primary continue, mechanism archive, records, settings, and no visible `立体演示` / `2.5D`.

Changed files:

- `package.json`
- `src/web/ui.ts`
- `src/web/styles.css`
- v7 loop docs and agent logs
- `codex.md`

Risks:

- Stage 3 is not final v7 acceptance. The app still runs the old 52 exposed level set and old mechanics.
- `smoke:visual`, `audit:ui`, `audit:levels`, and `audit:content` are still pending.
- Final self-hosted font/license choice is still pending.

Next steps:

- Commit and push Stage 3.
- Begin Stage 4 mechanism/data/test foundation.

### Stage 4: Engine mechanism and verification foundation

Phase: shared engine contract and replay foundation.

Actions taken:

- Added v7 typed metadata: `V7Mechanic`, `LevelDesignNote`, `SolverStatus`, `ValidationMethod`, `SpaceProfile`, and typed configs for time shadow, chain, spatial swap, and recursive room.
- Extended `LevelDef` / `Level` parsing with chapter, mechanics, v7 design notes, and validation method fields.
- Added deterministic `timeShadow` support to engine state/rules: delayed player copy, optional player/crate blocking, optional plate pressure, and state-key participation.
- Added `blockedReason` to `MoveResult` and exposed `lastBlockedReason` on `Game` / `DiptychGame`.
- Added renderer/CSS support for a visible `time-shadow` piece.
- Upgraded `npm run verify` output to include v7 acceptance fields.
- Added v7 metadata fields to `/api/levels`.

Verification commands and results:

- `npm run typecheck`: passed.
- `npm run verify`: passed, 52/52 current exposed levels; output now lists `id`, `title`, `chapter`, `solverStatus`, `solutionLength`, `par`, and `validation`.
- Temporary `npx tsx -` timeShadow check: passed, delay-1 shadow appeared and blocked re-entry.
- `npm run smoke:api`: passed.
- `npm run smoke:ui`: passed for all exposed levels.
- `npm run build`: passed.

Changed files:

- `scripts/verify-levels.ts`
- `server/index.ts`
- `src/engine/types.ts`
- `src/engine/level.ts`
- `src/engine/rules.ts`
- `src/web/game.ts`
- `src/web/render.ts`
- `src/web/styles.css`
- v7 loop docs and agent logs
- `codex.md`

Risks:

- Stage 4 is a foundation milestone, not final gameplay acceptance.
- `chain`, `spatialSwap`, and `recursiveRoom` still need concrete rules and UI behavior.
- The catalog remains the transitional 52-level set until Stage 5/7.

Next steps:

- Commit and push Stage 4.
- Begin Stage 5 level data upgrade and first 15-level vertical slice.
