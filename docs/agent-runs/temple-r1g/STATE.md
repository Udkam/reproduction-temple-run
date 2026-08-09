# Temple R1G coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

R1G opening baseline: `main` at `f77013f2d002d0132667a5145b384c48ee4fd673`. Accepted source candidate: `8de73c169d03ce32e15bce2145d64afff8973330`, built as courier checkpoints `43ba6a3` and `f08a170`, contract correction `0e7e8b2`, then snapshot repair `8de73c1`. Evidence and QA checkpoints are `386f23f` and `ca6068f`; the complete coordinator archive is a linear update from the previously pushed contract checkpoint `e468a0deff3befa2d64994b1a397f0880f9388e7`.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1F is accepted only for causeway presentation, and R1G closes the next identified P0 by replacing the always-visible centered courier blockout. A fresh real-frame audit must select the next bounded source slice; hazards, the opening/game-over pursuer, broader environment and animation, lighting/material polish, and final art remain unaccepted.

R1G is accepted as a bounded courier geometry and existing-pose fidelity slice. Courier candidate `f08a170` is independently source `READY` and visual `VISUAL_READY`; R1G-E1 candidate `8de73c1` corrects hidden-pursuer snapshot x/y to null and is independently source, evidence, and visual `READY`, with no P0/P1/P2. The first `f08a170` formal manifest remains immutable and `failed`: its declared failures used the obsolete all-frame-31 predicate, while independent evidence audit also found the 11 hidden-pursuer records used sentinel `x/y=-1`. Acceptance binds only the corrected 14-frame `8de73c1` evidence and does not accept final character art, hazards, pursuer, broader animation, lighting/material polish, or the complete game.

## Exact authority

The frozen courier writer modified only:

- `src/game/render/runnerRig.ts`
- `src/game/render/runnerRig.test.ts`

The courier checkpoint is frozen at `f08a170`. The completed R1G-E1 corrective writer modified exactly:

- `src/game/render/WorldRenderer.ts`
- `src/game/render/WorldRenderer.test.ts`

R1G-E1 remained within its 80 hand-authored added-or-modified-line limit and changed only hidden-pursuer snapshot x/y null conformance plus its direct live-construction test. It did not change lifecycle timing, canonical state, presentation placement, geometry, materials, draw calls, or any courier path.

The frozen courier checkpoint was limited to 500 hand-authored added or modified lines. R1G-E1 is the sole exception for the exact two renderer paths above; all other `WorldRenderer` behavior plus `theme.ts`, runtime/core/input, camera, route/collision, hazards, pursuer, UI, assets, package/configuration, browser scripts, Blender/probe paths, and inherited dirty files remain read-only.

The implementation must retain `RUNNER_RIG_BOUNDS`, existing public joints, six material batches, one shadow caster, and canonical inputs while constructing a closed volumetric Tide courier and making every existing pose independent of the previous gait phase. The exact ordinary-running composition remains `31` calls. At seed `1414087749`, gait ticks `60/64/68/72/76/80/84/88`, portrait/landscape/reduced-motion tick `60`, jump tick `21`, slide tick `15`, and game-over tick `336` bind the exact matrix; the fixed semantic scenes retain their required existing world entities and therefore use exact whole-scene baselines of `36` for portrait jump apex, `37` for landscape slide, and `34` for desktop game-over. Stumble is explicitly deferred because `RunnerPose` has no stumble semantic input.

## Verification checkpoints

The frozen courier development command was:

`npm.cmd run test -- src/game/render/runnerRig.test.ts`

Do not rerun that courier target. R1G-E1 development used only:

`npm.cmd run test -- src/game/render/WorldRenderer.test.ts`

The prior `f08a170` gates passed targeted `8/8`, typecheck, `17 files / 74 tests`, and production build. R1G-E1 targeted `WorldRenderer` verification passed `6/6`. After its last source edit, exactly one new final typecheck, one complete Vitest suite (`17 files / 75 tests`), one no-delete production build at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-build-8de73c1-20260809T201903272\`, and one candidate-bound browser pass all passed. Final render budgets use the exact fixed matrix above and at most 28,000 whole-frame triangles; courier geometry remains at most 3,200 triangles in six existing batches.

Accepted browser evidence at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-candidate-8de73c1-20260809T201927156\` includes normal running in desktop/portrait/landscape, all eight gait phases, portrait jump apex, landscape slide, desktop public-trace game-over, and portrait reduced motion. Manifest SHA-256 `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE` binds candidate SHA, fixed seed/tick, canonical simulation/render state, screenshot SHA-256, one canvas, and zero gameplay DOM, overflow, console/page errors, or context loss for all 14 records. Every state hash equals its replay hash. Independent source, evidence, and visual QA all return `READY`.

The preserved failed manifest is `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-v2-candidate-f08a170-20260809T193900\candidate-f08a170-browser-evidence.json`, SHA-256 `0CA07D549173FE12A367AE2C9EA55A5E393759561D845CAEC99B4DBBB92D06D1`. Its 14 screenshot hashes and replay hashes are valid. Its own `failures` array lists jump `36`, slide `37`, and game-over `34` against the old all-frame-31 predicate, but the capture script omitted the global hidden-position assertion: all 11 ordinary records contain `x/y=-1` rather than null. It remains failure history and may not be rewritten into acceptance.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited Temple dirty backlog, all historical candidate evidence, failed diagnostics, and both material-socket probe scripts remain preserved and unstaged.

Next action: commit this coordinator acceptance record together with the synchronized current-task, design, acceptance, and changelog files, then push the complete linear R1G chain without rewriting history. After that remote milestone, inspect the accepted real frames and open a separate bounded contract for the next highest-impact high-fidelity 3D slice. No further product source may be edited under the closed R1G authority.
