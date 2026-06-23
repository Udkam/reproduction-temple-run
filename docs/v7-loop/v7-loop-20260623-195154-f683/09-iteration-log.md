# Iteration Log

## Stage 1: Project reset and audit docs

Goal:

- Create v7 run directory and required documentation skeleton.
- Record current failure premise and baseline audit.
- Record agent roster and strict push-per-stage rule.

Actual changes:

- Added `docs/v7-loop/CURRENT_RUN_ID.txt`.
- Added required v7 loop documentation files.
- Added required agent log files.
- Added repo-local `codex.md`.

Verification:

- `git status --short`: only Stage 1 documentation files are untracked.
- `npm run typecheck`: passed.
- `npm run verify`: passed. Current baseline remains 60/60 current levels, including rejected v6 3D levels.
- `npm run smoke:api`: passed. API still returns 60 current levels; Node emitted a non-fatal `node:sqlite` ExperimentalWarning.
- `npm run smoke:ui`: passed. Existing blind spot remains: current 3D levels report `crates=0` because the old UI smoke only counts `.board .crate`.

Failure items:

- No Stage 1 blocker.
- Carry-forward risk: current visual/UI smoke is insufficient for v7 acceptance.

Next step:

- Commit Stage 1 and push to `origin main`.

## Stage 2: Project reset and route cleanup

Goal:

- Retire the user-visible v6 2.5D route without yet rewriting the whole game.
- Remove public 3D level exposure and dev demo entry.
- Update current top-level docs so v6 is not promoted as the active success path.

Actual changes:

- Removed `LEVEL3D_DEFS` from the runtime `LEVEL_DEFS` catalog.
- Removed the visible `立体演示 (dev)` menu button.
- Replaced `README.md` with v7-loop current status and retired-v6 language.
- Replaced `claude.md` with v7-loop current work report.
- Updated `package.json` description.
- Updated the top comment in `src/engine/levels.ts`.

Verification:

- `npm run typecheck`: passed.
- `npm run verify`: passed, current exposed catalog is 52/52.
- `npm run smoke:api`: passed, `/api/levels` now returns 52 levels.
- `npm run smoke:ui`: passed, all current exposed levels win through jsdom.
- `npx tsx -e ...LEVELS check...`: passed with `{"count":52,"ids":[],"is3D":[]}`.
- `npm run build`: passed.
- Discarded check: direct `node` import of TS/JS source failed due extension/runtime mismatch; replaced by the `tsx` catalog check above.

Failure items:

- No Stage 2 blocker.
- Carry-forward risk: unused v6 2.5D source still exists as historical code, but it is no longer in the user-visible runtime catalog.

Next step:

- Commit Stage 2 and push to `origin main`.

## Stage 3: New sci-fi art system and navigation shell

Goal:

- Replace the old paper/wood visual language with a clear 2D sci-fi shell.
- Rebuild the home screen into a command deck with first-class navigation.
- Add user-facing entries for chapter star map, mechanism archive, records, and settings.
- Keep the current 52-level runtime stable while the v7 level/engine rebuild is still pending.

Actual changes:

- Replaced `src/web/styles.css` with a new dark sci-fi 2D visual system: neon grid background, hologram panels, command buttons, chapter map styling, HUD styling, board states, overlays, and responsive mobile rules.
- Rebuilt `showMenu()` in `src/web/ui.ts` into a command-deck home screen.
- Added `章节星图`, `机制档案`, `挑战记录`, and `设置` navigation surfaces.
- Added `showRecords()` and `showSettings()` overlays.
- Removed remaining visible 3D divider/badge handling from the home/level list flow.
- Changed `package.json` description to ASCII-only text after confirming PowerShell had rendered UTF-8 symbols as mojibake in console output.

Verification:

- `npm run typecheck`: passed.
- `npm run verify`: passed, current exposed catalog remains 52/52.
- `npm run smoke:api`: passed, `/api/levels` returns 52 levels.
- `npm run smoke:ui`: passed, all current exposed levels still win through jsdom.
- `npm run build`: passed.
- Temporary DOM audit with `npx tsx -`: passed for `.home-deck`, primary continue button, `#chapter-map`, mechanism archive button, records button, settings button, and no visible `立体演示` / `2.5D` entry.

Failure items:

- Initial temporary DOM audit failed because PowerShell piping converted Chinese regex text into `????`; root cause was ad-hoc script transport encoding, not repo source encoding. Re-ran the same assertions with Unicode escapes and passed.
- Stage 3 is not final v7 acceptance. It still uses the old 52 exposed level data and old mechanics while establishing the new shell.
- Carry-forward risk: no real-browser screenshot audit exists yet; `smoke:visual` is still pending for later stages.
- Carry-forward risk: CSS currently uses local/system font stack names only. Final font decision and license record are still pending.

Next step:

- Commit Stage 3 and push to `origin main`.
- Begin Stage 4 mechanism/data/test foundation.

## Stage 4: Engine mechanism and verification foundation

Goal:

- Add a v7-compatible level metadata contract without breaking current replay.
- Add deterministic time-shadow state support as the first new v7 mechanism foundation.
- Add blocked-reason plumbing for later UI feedback.
- Upgrade verification output to the v7-required fields.

Actual changes:

- Extended `src/engine/types.ts` with `V7Mechanic`, `LevelDesignNote`, `SolverStatus`, `ValidationMethod`, `SpaceProfile`, and typed configs for `timeShadow`, `chain`, `spatialSwap`, and `recursiveRoom`.
- Extended `LevelDef` / `Level` parsing to carry v7 metadata and chapter/mechanic fields.
- Added `history` and `shadow` to `GameState`; old levels default to empty history and no shadow.
- Implemented deterministic `timeShadow` advancement in `rules.ts`: delayed player copy, optional player/crate blocking, optional plate pressure, and state-key participation.
- Added `blockedReason` to `MoveResult`, and exposed `lastBlockedReason` from `Game` / `DiptychGame`.
- Added a visible `time-shadow` renderer piece and CSS styling.
- Upgraded `npm run verify` output to print `id`, `title`, `chapter`, `solverStatus`, `solutionLength`, `par`, `validation`, and pass/fail.
- Added server `/api/levels` metadata fields for chapter, mechanics, solver status, and validation method.

Verification:

- `npm run typecheck`: passed.
- `npm run verify`: passed, current exposed catalog remains 52/52 and output now includes v7 verification fields.
- Temporary `npx tsx -` timeShadow engine check: passed; a delay-1 shadow appeared at the previous player position and blocked the player from stepping back into it.
- `npm run smoke:api`: passed; server replay and bogus-solution rejection still work.
- `npm run smoke:ui`: passed for all current exposed levels.
- `npm run build`: passed.

Failure items:

- No Stage 4 blocker.
- Carry-forward risk: `chain`, `spatialSwap`, and `recursiveRoom` are typed config surfaces only in this stage. They are not yet complete gameplay implementations.
- Carry-forward risk: blocked-reason UI feedback is plumbed in the game wrapper but not yet rendered to the player.
- Carry-forward risk: the runtime catalog is still 52 transitional levels, not the final 70 v7 levels.

Next step:

- Commit Stage 4 and push to `origin main`.
- Begin Stage 5 level data format upgrade and 15-level vertical slice.
