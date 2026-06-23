# Current Audit

## Baseline commands

- `git pull --ff-only origin main`: already up to date.
- `npm run typecheck`: passed.
- `npm run verify`: passed, current runtime has 60 levels.
- `npm run smoke:api`: passed, `/api/levels` returns 60 levels and server replay rejects bogus submissions.
- `npm run smoke:ui`: passed, all 60 current levels reach a win overlay in jsdom.

These passing checks are technical baseline only. They do not satisfy v7 product acceptance.

## Current stack

- Vite 6, TypeScript, plain DOM/CSS frontend.
- Fastify backend with Node built-in SQLite.
- Shared TypeScript engine under `src/engine`.
- Current UI router is `src/web/ui.ts`, replacing the root DOM through `App.swap`.

## Current level state

- Runtime catalog: 60 levels, 13 chapters.
- Current docs are stale in places and still promote v6 2.5D.
- Current metadata is insufficient for v7. `LevelDef` lacks structured `levelDesignNote`, `solverStatus`, `coreIdea`, `trick`, `fairness`, and duplicate/audit metadata.
- Generated classic levels dominate part of the catalog and do not meet the v7 quality bar.

## Current engine state

- `GameState` is single-player and crate-centric.
- Replay tokens are legacy direction strings plus `@dir` for pull.
- Solver is A* over the current single-board state and does not model v7 structured actions.
- Server score validation is authoritative and must be extended, not bypassed.

## v6 retirement targets

- Remove visible 3D chapters `3d1` through `3d8` from the runtime catalog.
- Remove or unlink `IsoRenderer`, dev demo entry, camera controls, 3D menu dividers, 3D badges, and v6 status copy from the user-facing path.
- Historical v6 notes may remain only as archived failure context, not as current mainline promotion.

## Encoding note

Files are valid UTF-8 when read with Node. PowerShell display can render Chinese as mojibake. Chinese-facing edits must be verified with UTF-8 reads before acceptance.
