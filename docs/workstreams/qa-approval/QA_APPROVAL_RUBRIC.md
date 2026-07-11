# Independent Approval, QA, and Release Gates

Status: baseline audit complete; Stage 6 is **rejected for release** pending the
blocking gates below. This document is an independent QA contract for the
frontend-design, gameplay-rules-engine, and level-design workstreams. It does
not approve production implementation.

## Decision Rules

- **P0 — release blocker:** no candidate may be accepted while open.
- **P1 — acceptance blocker:** the owning workstream must resolve it in its
  approved slice, or the coordinator must explicitly defer it with a bounded
  follow-up gate and no affected feature enabled.
- **P2 — required before feature-complete or public-ready acceptance:** may be
  deferred only from a narrowly scoped stability slice, never silently.
- **P3 — quality debt:** record an owner and a target gate before integration.

An implementation workstream may propose a patch; only independent QA records
an acceptance decision. A green unit-test run alone is never an acceptance.

## Stage 6 Baseline Findings

| Severity | Finding | Evidence | Required disposition |
| --- | --- | --- | --- |
| P0 | The checked-in dependency lock is not reproducible. | `npm.cmd ci` fails because `package-lock.json` lacks `@emnapi/core@1.11.1` and `@emnapi/runtime@1.11.1`. The clean worktree initially had no `node_modules`; `npm.cmd run typecheck` therefore could not find `tsc`. A non-lock-writing temporary install subsequently left `pixi.js` invalid, and current `typecheck`/`build` cannot resolve `pixi.js`. | Restore a committed lockfile that passes `npm ci` in a clean worktree. Then pass typecheck, test, and production build from that install. |
| P1 | Entering an invalid or occupied entrance is not a safe rejected command. | `src/core/recursiveTransitions.ts` writes the actor to the chosen entrance and calls `assertValidSimulationState()` without checking entrance bounds or solid occupancy. An invalid setup can therefore throw instead of returning an unchanged session and a structured blocked result. | Gameplay workstream must make every invalid enter/exit path total and deterministic: no uncaught exception, no history record, no state/hash change, and one documented rejection result. |
| P1 | Runtime recursive control is tied to `container-b`. | `src/runtime/GameRuntime.ts` chooses `Enter("container-b")`/`Exit("container-b")`; `src/render/PixiApp.ts` also derives transition geometry only for root `container-b`. New containers, levels, and recursive addresses cannot participate correctly. | Replace fixed IDs with a validated active interaction target and projection-instance address. Add tests for two containers and nested focus. |
| P1 | Transition locking does not cover the full recursive visual transition. | `PixiApp.isAnimating` reports only `animatedProjection`; the event plan ends at 560/500 ms, while `RecursiveTransitionRenderer` runs a 980 ms timeline. The completion callback can flush a queued command while the recursive camera still transitions. | Use one authoritative command-lock lifecycle that lasts until all visual/camera transition work reaches a commit-safe state. Prove it with an input-spam test and middle-frame capture. |
| P1 | Projection animation identity is entity-ID-only, not recursive-instance/path-aware. | `mapProjectionEntities()` in `src/render/PixiApp.ts` stores projections in `Map<string, EntityProjection>`, while a bounded recursive projection can show the same canonical entity through more than one address. One map entry overwrites another. | Define and carry a stable projection-instance ID (root plus container path) through projection, animation events, renderer lookup, screenshots, and tests. |
| P2 | Cycle/self-containment behavior is neither implemented nor bounded by an approved policy. | Core rejects cycles unless `allowsRecursiveCycle` is set, but projection recursion only uses `maxDepth` and has no repeated-address/cycle policy test. | Gameplay workstream must publish one explicit supported policy and test validation, bounded projection, replay, and undo for it before enabling related level content. |
| P2 | No repeatable browser visual-regression workflow is checked in. | `package.json` has no screenshot or browser-test script; there is no `scripts/` directory. The sole Stage 6 artifact is a static desktop-like PNG. | Frontend workstream must add deterministic capture and analysis under an approved slice, including desktop/mobile and transition middle frames. |
| P2 | Current visual evidence is insufficient for the claimed fidelity gate. | Visual inspection of `docs/screenshots/stage6-render-fidelity.png` confirms a nonblank single scene with one parent slab and one recursive aperture, but not input response, animation, mobile composition, or comparison against a reference target. | Capture reproducible baseline/after evidence at specified viewports and transition phases; include objective pixel/geometry checks and a written visual review. |
| P2 | Render performance and allocation behavior are unmeasured. | During an active animation, `PixiApp.tick()` calls `draw(frame)` and `draw()` removes/recreates render-layer children. The Stage 4 note says redraws are not every frame, but Stage 5 code makes them frame-driven. | Profile desktop and mobile emulation; publish frame-time and heap/object-churn budgets before accepting deeper recursion or content. |
| P2 | Input is keyboard-only and accessibility coverage is incomplete. | `InteractionPrototype` registers a global `keydown`; the canvas has an `aria-label`, but there is no focus contract, pointer/touch path, reduced-motion handling, or accessibility/browser test. | Add command-equivalent keyboard, pointer/touch, and assistive/reduced-motion behavior with tests. Do not accept mobile gameplay without it. |
| P2 | Documentation has stage-status drift. | `docs/recursive-box-lab/GAME_RULES.md` says “Stage 4 rule specification before gameplay-kernel implementation” even though the current status declares Stage 6 implemented; Stage 8’s planned browser workflow does not exist. | Coordinator must consolidate status after accepted integration; owners must update their scoped contracts in the same accepted slice. |
| P3 | Existing unit coverage does not exercise the observed integration risks. | The 9 Vitest files / 35 tests cover deterministic core helpers and limited animation math, but do not prove `npm ci`, browser rendering, mobile input, mid-transition command locking, invalid entrance rejection, duplicate projection addresses, or performance budgets. | Add the listed regression coverage as the owning slices are approved. |

## Architecture Boundary Gate

All three workstreams must preserve these non-negotiable contracts:

1. `src/core/**` remains deterministic TypeScript with no PixiJS, React, DOM,
   camera, viewport, timing, audio-playback, or mutable renderer imports.
2. The renderer consumes bounded projections; it never owns canonical world,
   history, or rules state.
3. Runtime is the only dependency-wiring layer. It may queue validated commands
   but cannot hard-code a level/container identity.
4. React remains host/shell-only: no gameplay cell, entity, world, or animation
   tree in DOM.
5. Every visible recursive occurrence has an address/path identity distinct from
   the canonical entity ID.
6. Original procedural art and original layouts only; no proprietary game
   assets, copied layouts, audio, names, or copy.

## Gate Matrix By Workstream

### Frontend-design — visual/runtime acceptance

Accept only when all applicable items hold:

- Projection-instance/path identity is rendered and animated without fixed
  `container-b` conditions.
- A single command-lock reports the combined entity, camera, and recursive
  transition lifecycle. Repeated keyboard, pointer, and touch input cannot
  commit a second command until the first transition is safe.
- Browser evidence exists for 1440x900 DPR 1 desktop and 390x844 DPR 3 mobile:
  initial, action-start, 50% enter, settled-inner, 50% exit, settled-outer.
- Every capture reports canvas count, gameplay-DOM count, console errors and
  warnings, screenshot dimensions, nonblank/palette metrics, and the exact
  command sequence and timing used.
- Visual review confirms parent/child context remains legible in every
  middle-frame capture and at mobile width; it must not substitute a route or
  blank frame for recursion.
- Reduced motion shortens/snaps visual transitions without changing core
  commands or hashes. Keyboard focus, pointer/touch action, and canvas label
  are browser-tested.
- A performance report on both viewports shows p95 frame time under 16.7 ms for
  the agreed demo scene, no monotonic heap growth over 30 enter/exit cycles,
  and a documented recursion-depth/render-object budget. If the target device
  cannot meet 60 fps, the coordinator must approve a different budget before
  acceptance.

Reject when a renderer patch reintroduces DOM gameplay, mutable core state,
fixed container IDs, unbounded recursive drawing, untested visual snapshots,
or console errors.

### Gameplay-rules-engine — deterministic recursive correctness

Accept only when all applicable items hold:

- The published rule contract states normal movement, push chains, entrance and
  exit selection, blocked behavior, push-in/push-out scope, parent updates,
  cycle/self-containment policy, focus addressing, goals, reset, undo/redo,
  replay, and invalid data behavior.
- State validation, reducers, projection, history, and replay use the same
  explicit cycle/recursion policy. Unsupported behavior is rejected as a
  structured command/data error, never by accidental exception or silent
  mutation.
- For every blocked or invalid command: `accepted === false`, session identity
  or canonical hash is unchanged, history is unchanged, and the rejection is
  deterministic.
- Enter/exit checks world ownership, focus-path legality, entrance bounds,
  entrance occupancy, exit bounds, exit occupancy, and applicable parent state
  before committing. Tests include each branch.
- Replaying an approved command trace from the same state yields identical
  accepted count, final hash, event sequence, focus path, and projection
  addresses. Undo/redo/reset restore the relevant hashes and do not reuse stale
  animation state.
- A deterministic seeded stress suite covers at least 1,000 valid/invalid
  command sequences and reports no uncaught errors, invalid positions, solid
  overlaps, divergent hashes, or focus-path violations.
- Events identify both the canonical entity and affected projection path(s), so
  the renderer can animate repeated recursive occurrences correctly.

Reject when rules are inferred from render order, core imports presentation
modules, an invalid entrance can throw, or a test passes only through a
hard-coded Stage 6 fixture.

### Level-design — original, solvable, schema-gated content

Accept only when all applicable items hold:

- The gameplay-rules-engine contract and schema version are accepted first.
  Level work must not freeze semantics while the cycle, entrance, or push
  policy remains unresolved.
- Each level has an original-layout attestation, `schemaVersion`, explicit
  world/entity IDs, graph references, start focus, intended mechanics, visual
  staging notes, and a scripted solution trace through the public command API.
- Validation rejects unknown references, impossible positions, unsupported
  recursion, malformed goals, and non-serializable values before the level is
  playable.
- A solver/replay verifies solution determinism and final win state. Any claim
  of uniqueness/minimum move count states the search bounds and method.
- Campaign order teaches one approved mechanic at a time, never relies on
  copied layouts, and has desktop/mobile screenshot evidence for legibility.
- Level content does not work around engine defects with fixtures or special
  IDs; it uses generic addresses and declared schema fields only.

Reject levels added before an accepted rules/schema gate, levels without replay
proof, or content that depends on renderer-specific coordinates or copied work.

## Common Release Gate

The coordinator may accept an integrated candidate only after:

1. A clean worktree passes `npm.cmd ci`, `npm.cmd run typecheck`, `npm.cmd run
   test`, and `npm.cmd run build` with exit code 0. Test totals and environment
   are recorded.
2. Source-boundary checks find no forbidden `core` presentation imports and no
   React gameplay DOM. Browser evidence has one canvas, zero gameplay DOM
   nodes, and zero unexpected console errors/warnings.
3. Required desktop/mobile and transition-middle screenshots are attached to
   the exact candidate SHA, not a prior baseline.
4. Performance, memory, accessibility/input, and deterministic replay evidence
   meet the applicable workstream gates.
5. Every accepted workstream commit is independently reviewed by QA by SHA;
   workers do not self-approve.
6. `git status --short` is clean apart from deliberate, reviewed files;
   `.codex/`, `.serena/`, `node_modules/`, build output, logs, and local browser
   state are not staged. No `git add .` is used.
7. Scoped docs are updated consistently. Only the coordinator updates
   `docs/logs/CHANGELOG.md` when integrating approved work.

## Required Evidence Template

Use this template in every implementation PR-equivalent review request and
workstream handoff.

```text
Candidate
- Workstream thread ID:
- Coordinator thread ID: 019f4deb-7e83-7583-8cd5-8e6f075bc331
- Base SHA / candidate SHA:
- Scope / explicitly excluded scope:
- Owner and independent QA reviewer:

Contract
- Changed public types, schema version, projection-address rules, or none:
- Architecture-boundary check command and result:
- Compatibility/migration decision and rollback path:

Deterministic correctness (if core/levels changed)
- Command traces and initial/final hashes:
- Invalid/blocked cases and unchanged-state evidence:
- Undo/redo/reset/replay evidence:
- Recursive/cycle/focus-path cases and policy:
- Stress-suite seed, count, and result:

Browser and visual evidence (if runtime/renderer/levels changed)
- Browser/version, operating system, candidate SHA:
- Desktop: 1440x900 DPR 1 screenshot paths and metrics:
- Mobile: 390x844 DPR 3 screenshot paths and metrics:
- Command sequence, deterministic timestamps, start/50%/settled frames for
  enter and exit:
- canvas count / gameplay DOM count / console error+warning count:
- Reference-comparison observations and known visual deviations:

Performance and accessibility
- p50/p95 frame time, 30-cycle heap result, render-object/depth count:
- Keyboard/focus, pointer/touch, reduced-motion, and canvas-label results:

Toolchain and repository hygiene
- `npm ci`, typecheck, test, build commands with exit codes and test totals:
- `git diff --check`, `git status --short`, staged path list:
- Documentation paths updated; CHANGELOG owner confirmation:

Decision
- QA verdict: accept / reject / conditional rejection
- Open findings by severity, owner, and required follow-up gate:
```

## Approval Sequence

1. Resolve P0 reproducibility first; no browser or production approval can rely
   on an ad-hoc dependency installation.
2. Coordinator approves a smallest stability slice for the P1 recursive
   semantics/runtime defects, after the gameplay and frontend contracts agree
   on projection addressing and transition-lock ownership.
3. QA reviews that slice by candidate SHA using this rubric. No level content
   begins until its rule/schema dependencies are accepted.
4. Visual and content slices follow only with fresh evidence; each is reviewed
   independently before coordinator integration and CHANGELOG consolidation.
