# Temple R1G coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

Branch and contract baseline: `main` at `f77013f2d002d0132667a5145b384c48ee4fd673`, matching `origin/main` when R1G was opened.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1F is accepted and pushed only for causeway presentation. Multi-dialogue source, visual, and test audits identify the always-visible centered courier as the next P0: the accepted seven R1F frames still read as a black ball head, white rod arms, rounded block torso, square legs, flat coat cards, and a white target-like back core. Hazards and broader environment are P1; the pursuer is deferred because normal-running lifecycle correctly hides it.

R1G is a bounded courier geometry and existing-pose fidelity slice. It is not final character, hazard, pursuer, or game acceptance.

## Exact authority

Production writer may modify only:

- `src/game/render/runnerRig.ts`
- `src/game/render/runnerRig.test.ts`

The checkpoint is limited to 500 hand-authored added or modified lines. `WorldRenderer.ts`, `theme.ts`, runtime/core/input, camera, route/collision, hazards, pursuer, UI, assets, package/configuration, browser scripts, Blender/probe paths, and inherited dirty files remain read-only.

The implementation must retain `RUNNER_RIG_BOUNDS`, existing public joints, six material batches, one shadow caster, canonical inputs, and exact 31-call presentation while constructing a closed volumetric Tide courier and making every existing pose independent of the previous gait phase. Stumble is explicitly deferred because `RunnerPose` has no stumble semantic input.

## Verification checkpoints

During development run only:

`npm.cmd run test -- src/game/render/runnerRig.test.ts`

After the last source edit run exactly one final typecheck, one complete Vitest suite, one no-delete production build, and one candidate-bound browser pass. Final render budgets are exactly 31 draw calls and at most 28,000 whole-frame triangles; courier geometry is at most 3,200 triangles in six existing batches.

Browser evidence must include normal running in desktop/portrait/landscape, representative coverage of all eight gait phases across those profiles, portrait jump apex, landscape slide, desktop public-trace game-over, and portrait reduced motion. Every record binds candidate SHA, fixed seed/tick, canonical simulation/render state, screenshot SHA-256, one canvas, and zero gameplay DOM, overflow, console/page errors, or context loss. Independent source/test/visual QA starts only after a candidate SHA exists.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited Temple dirty backlog, all historical candidate evidence, failed diagnostics, and both material-socket probe scripts remain preserved and unstaged.

Next action after this contract is committed and pushed: implement one reviewable R1G source checkpoint in the exact two files, run the targeted test, and inspect real three-viewport frames before any final suite or broader animation work.
