# Temple R1G coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

R1G opening baseline: `main` at `f77013f2d002d0132667a5145b384c48ee4fd673`. Current local source candidate: `f08a17044bd1c677857f732bffb7f5b38342dad4`, built as `43ba6a3` then `f08a170`; current `origin/main` remains the pushed contract checkpoint `e468a0deff3befa2d64994b1a397f0880f9388e7`.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1F is accepted and pushed only for causeway presentation. Multi-dialogue source, visual, and test audits identify the always-visible centered courier as the next P0: the accepted seven R1F frames still read as a black ball head, white rod arms, rounded block torso, square legs, flat coat cards, and a white target-like back core. Hazards and broader environment are P1; the pursuer is deferred because normal-running lifecycle correctly hides it.

R1G is a bounded courier geometry and existing-pose fidelity slice. Candidate `f08a170` is independently source `READY` and visual `VISUAL_READY`, with no P0/P1 in the courier scope. Its first formal manifest remains immutable and `failed`: the declared failures are the old all-frame-31 predicate, while independent evidence audit additionally finds the 11 hidden-pursuer records use sentinel `x/y=-1` instead of the globally required null position. R1G is not yet accepted and is not final character, hazard, pursuer, or game acceptance.

## Exact authority

The now-frozen courier writer modified only:

- `src/game/render/runnerRig.ts`
- `src/game/render/runnerRig.test.ts`

The courier checkpoint is frozen at `f08a170`. A separate R1G-E1 corrective writer may now modify exactly:

- `src/game/render/WorldRenderer.ts`
- `src/game/render/WorldRenderer.test.ts`

R1G-E1 is limited to 80 hand-authored added or modified lines and only the hidden pursuer snapshot x/y null conformance plus its direct live-construction test. It may not change lifecycle timing, canonical state, presentation placement, geometry, materials, draw calls, or any courier path.

The frozen courier checkpoint was limited to 500 hand-authored added or modified lines. R1G-E1 is the sole exception for the exact two renderer paths above; all other `WorldRenderer` behavior plus `theme.ts`, runtime/core/input, camera, route/collision, hazards, pursuer, UI, assets, package/configuration, browser scripts, Blender/probe paths, and inherited dirty files remain read-only.

The implementation must retain `RUNNER_RIG_BOUNDS`, existing public joints, six material batches, one shadow caster, and canonical inputs while constructing a closed volumetric Tide courier and making every existing pose independent of the previous gait phase. The exact ordinary-running composition remains `31` calls. At seed `1414087749`, gait ticks `60/64/68/72/76/80/84/88`, portrait/landscape/reduced-motion tick `60`, jump tick `21`, slide tick `15`, and game-over tick `336` bind the exact matrix; the fixed semantic scenes retain their required existing world entities and therefore use exact whole-scene baselines of `36` for portrait jump apex, `37` for landscape slide, and `34` for desktop game-over. Stumble is explicitly deferred because `RunnerPose` has no stumble semantic input.

## Verification checkpoints

The frozen courier development command was:

`npm.cmd run test -- src/game/render/runnerRig.test.ts`

Do not rerun that courier target. R1G-E1 development uses only:

`npm.cmd run test -- src/game/render/WorldRenderer.test.ts`

The prior `f08a170` gates passed targeted `8/8`, final typecheck, final `17 files / 74 tests`, and production build. Because R1G-E1 now adds a product-source edit, after its last edit run exactly one new final typecheck, one complete Vitest suite, one no-delete production build, and one candidate-bound browser pass. Final render budgets use the exact fixed matrix above and at most 28,000 whole-frame triangles; courier geometry remains at most 3,200 triangles in six existing batches.

Browser evidence must include normal running in desktop/portrait/landscape, representative coverage of all eight gait phases across those profiles, portrait jump apex, landscape slide, desktop public-trace game-over, and portrait reduced motion. Every record binds candidate SHA, fixed seed/tick, canonical simulation/render state, screenshot SHA-256, one canvas, and zero gameplay DOM, overflow, console/page errors, or context loss. Independent source/test/visual QA starts only after a candidate SHA exists.

The preserved failed manifest is `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-v2-candidate-f08a170-20260809T193900\candidate-f08a170-browser-evidence.json`, SHA-256 `0CA07D549173FE12A367AE2C9EA55A5E393759561D845CAEC99B4DBBB92D06D1`. Its 14 screenshot hashes and replay hashes are valid. Its own `failures` array lists jump `36`, slide `37`, and game-over `34` against the old all-frame-31 predicate, but the capture script omitted the global hidden-position assertion: all 11 ordinary records contain `x/y=-1` rather than null. It remains failure history and may not be rewritten into acceptance.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited Temple dirty backlog, all historical candidate evidence, failed diagnostics, and both material-socket probe scripts remain preserved and unstaged.

Next action: commit the combined evidence-predicate correction and R1G-E1 source authorization as one bounded local contract checkpoint. It cannot be pushed alone because it is stacked above the unaccepted local courier range `43ba6a3..f08a170`; publishing waits for the accepted linear chain rather than rewriting history. Then implement and target-test the exact two-path snapshot repair, commit it separately, run the single required final gate set, and create a new candidate-bound evidence directory without overwriting any old file. Independent source/evidence QA must review the new candidate before coordinator archive, changelog, push, or an R1G acceptance claim.
