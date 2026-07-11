# Frontend and Visual Fidelity Workstream Log

## Workstream Identity

- Thread ID: `019f4e80-145a-7520-81e1-41a45b2bec13`
- Coordinator thread ID: `019f4deb-7e83-7583-8cd5-8e6f075bc331`
- Coordinator deep link: `codex://threads/019f4deb-7e83-7583-8cd5-8e6f075bc331`
- Scope: frontend and visual fidelity; audit/design only in this first phase.
- Base commit: `3b23df3be86df568d5aa6a0bef7e1652ff502ef0`
- Started: `2026-07-11 08:00:00 +08:00`
- Proposal completed: `2026-07-11 08:18:28 +08:00`
- Coordination update consumed: `2026-07-11 08:20:54 +08:00`

## 2026-07-11 — Stage 6 Visual Audit and Redesign Contract

### Coordination and revisions consumed

- Read coordinator protocol and log at `ab58d75` with:
  - `git show ab58d75:docs/workstreams/README.md`
  - `git show ab58d75:docs/workstreams/coordinator/THREAD_LOG.md`
- Do not merge or rebase `ab58d75` during this audit. The coordinator owns
  integration and `docs/logs/CHANGELOG.md` consolidation.
- Read latest coordinator decision from `715b039` without rebasing:
  - `git show 715b039:docs/workstreams/coordinator/THREAD_LOG.md`
  - `git show 715b039:docs/workstreams/qa-approval/QA_APPROVAL_RUBRIC.md`
  It records the accepted QA governance integration (`c781c31`), reproduces
  P0 lockfile failure, rejects Stage 6 for release, and freezes all frontend
  implementation. Only the gameplay workstream may make the bounded P0
  package-lock-plus-log candidate.
- Read peer workstream records before making cross-workstream dependency
  recommendations:
  - Level Design range
    `42f9ca197905e3363551c25e91faa8a6ed25527e..fa4d0ef1906098a332e515ba96cede5f600ac4f7`:
    `docs/workstreams/level-design/THREAD_LOG.md` and
    `LEVEL_DESIGN_PROPOSAL.md`.
  - Independent QA `7a99506db46b54131b89473b67a86b5d5675577d`:
    `docs/workstreams/qa-approval/THREAD_LOG.md` and
    `QA_APPROVAL_RUBRIC.md`.
  - Gameplay Rules and Engine `175ca5e3b251c0485f9603925b0cfda221c11aa1`:
    `docs/workstreams/gameplay-rules-engine/THREAD_LOG.md` and
    `RULES_ENGINE_AUDIT.md`.

### Decisions

- Preserve PixiJS canvas ownership, deterministic core/projection separation,
  renderer-owned cell metrics, masked recursive children, procedural art, void
  particles, and command-driven animation.
- Partially reboot composition, material grammar, recursive aperture
  readability, projection-instance addressing, transition lifetime, mobile
  behavior, and active-frame allocation strategy.
- Treat the observed missing middle-frame geometry as a P1 acceptance blocker;
  do not accept a cosmetic renderer pass before generic address/transition-lock
  ownership is resolved.
- Treat clean `npm ci` as an upstream P0 release prerequisite. Temporary
  local dependency installation enabled audit commands only and is not a fix.
- Align future renderer/runtime work with the committed gameplay proposal:
  projection occurrence identity is keyed by addressed path, renderer events
  carry the occurrence route, and one command lock owns entity, camera, and
  portal transitions. No `container-b` hard-coding is acceptable.
- Keep the level workstream's four tutorial visual-staging needs provisional.
  They guide future screenshot needs but do not authorize level data, schema,
  camera metadata, or content.
- Do not implement product code, modify the root changelog, push, merge, or
  self-approve this proposal. Frontend implementation remains frozen until QA
  accepts P0 and the coordinator grants a new bounded approval.

### Evidence reviewed

- Shared handoff: `C:\Users\Alex Chen\AppData\Local\Temp\codex-handoff-game1-20260711-080600.md`.
- Core contracts: `ARCHITECTURE.md`, `DESIGN_REFERENCE.md`,
  `IMPLEMENTATION_PLAN.md`, `docs/reboot/CURRENT_STATUS.md`,
  `docs/qa/STAGE6_RENDER_ALIGNMENT.md`, and
  `docs/recursive-box-lab/GAME_RULES.md`.
- Renderer/runtime: `src/render/PixiApp.ts`, `Camera2D.ts`,
  `RecursiveTransitionRenderer.ts`, `metrics.ts`, material and primitive
  modules, `src/runtime/GameRuntime.ts`, `InteractionPrototype.ts`, and
  animation/projection modules.
- Existing visual artifact:
  `docs/screenshots/stage6-render-fidelity.png`.
- Official primary references: the official press page and screenshots 1, 2,
  and 8 listed by `DESIGN_REFERENCE.md`. They were inspected as temporary
  external files only and were not copied into the worktree.

### Browser and screenshot evidence

- In-app browser loaded `http://127.0.0.1:5173/` after dependencies were made
  available. Desktop result: one Pixi canvas, zero gameplay DOM nodes, viewport
  `1280x720`, DPR `1.25`, canvas CSS `1280x720`, backing store `1600x900`.
- Browser console check after interaction: zero warning/error entries.
- Resting scene was nonblank and exposes player, normal box, goal, and one
  recursive aperture, but has a single symmetric isolated slab rather than
  deliberate parent-context composition.
- A 70 ms movement capture and a 300 ms enter capture visibly lost the world
  frame, leaving a gray field with only the animated player/aperture. The
  settled frame returned. This is reproducible visual evidence of an incomplete
  transition lifecycle, not a screenshot-only concern.
- Requested `390x844` viewport override was attempted twice, including a fresh
  local tab. Both reported the unchanged `1280x720` viewport/canvas; therefore
  no mobile claim is made. The proposal requires a verified mobile capture
  surface before accepting responsive work.
- No screenshot was committed because this audit changes no local visual output.

### Commands and results

- `python .../webapp-testing/scripts/with_server.py --help`: completed before
  local browser testing.
- `npm.cmd ci`: failed reproducibly because `package-lock.json` lacks
  `@emnapi/core@1.11.1` and `@emnapi/runtime@1.11.1`.
- `npm.cmd install --package-lock=false --no-audit --no-fund`: completed only
  to run local audit tooling; tracked manifests remained unchanged.
- `npm.cmd run typecheck`: passed after temporary installation.
- `npm.cmd run test`: passed, 9 files / 35 tests.
- `npm.cmd run build`: passed after temporary installation.
- `git diff --check`: passed before documentation staging.
- `git status --short`: no tracked source/config change before this proposal.

### Files changed

- `docs/workstreams/frontend-design/VISUAL_REDESIGN_PROPOSAL.md`
- `docs/workstreams/frontend-design/THREAD_LOG.md`

### Commit, dependencies, blockers, and handoff

- Initial documentation-only audit commit:
  `2ac2ed058af4ac49d7f5821f64d416b608ed845a`
  (`docs(frontend): audit visual redesign`).
- This follow-up log-only commit records the audit SHA for the coordinator and
  independent QA handoff; it changes no production file.
- Dependencies: generic projection-instance identity and interaction targeting
  from gameplay; schema-approved visual staging from level design; clean
  reproducibility and independent verdict from QA.
- Blockers: lockfile P0, fixed-container/transition-lock P1, unverified mobile
  viewport, and no checked-in deterministic visual-capture tooling.
- Handoff: send the final commit SHA and both workstream document paths to
  coordinator thread `019f4deb-7e83-7583-8cd5-8e6f075bc331`; await an explicit
  approved slice before touching production code.

## 2026-07-11 — D0 Repository-Contract Review

- Review timestamp: `2026-07-11 16:15:48 +08:00`
- Reviewer thread ID: `019f4e80-145a-7520-81e1-41a45b2bec13`
- Coordinator thread ID: `019f4deb-7e83-7583-8cd5-8e6f075bc331`
- Candidate reviewed: `e07808364febb2c6607fb6d962bf53fddd6c2cf3`
  (`docs: define Phase A implementation contracts`)
- Review scope: documentation only. No production source, root contract,
  package, root changelog, branch, push, merge, or rebase change was made in
  this worktree.

### Verdict: CONDITIONAL REJECT

The candidate is clean-room compliant, correctly treats historical Stage 6 as
non-authoritative, and makes the C1 -> QA-C1 -> V1 sequence explicit. It also
correctly adopts the accepted R1 boundary: C1 owns public semantic types while
V1 consumes them without core mutation. `DESIGN.md` is implementable with the
existing PixiJS/projection/metrics foundation: it preserves a single canvas,
procedural materials, bounded projections, shared metrics, and masked child
worlds instead of asking for DOM gameplay or copied assets.

However, D0 is not yet internally executable under its own precedence rules.
The coordinator must correct the clauses below before accepting D0 or opening
C1. These are contract corrections only; they do not authorize V1.

### Required corrections

1. **V1 misses a required owned source file.** `CURRENT_TASK.md` §5 permits
   `src/animation/transitions.ts` but not `src/animation/AnimationSystem.ts`.
   The current `AnimationSystem` exposes `entityProgress` as
   `Record<string, number>` and builds it from `motion.entityId`
   (`src/animation/AnimationSystem.ts:5-10,56-64`), while `PixiApp` reads that
   map by `entityProjection.entity.id` (`src/render/PixiApp.ts:331-337`). This
   is precisely the entity-ID collision V1 must remove for repeated recursive
   occurrences. Add `src/animation/AnimationSystem.ts` and its tests to V1
   ownership, and require occurrence-address keys end-to-end. No `src/core/**`
   change is needed: R1 already freezes `EntityOccurrenceAddress` as the
   consumer contract.

2. **The visual-completion policy is not deterministic enough to test.**
   `CURRENT_TASK.md` §5 says repeated input may "queue/reject
   deterministically" but does not choose one behavior, define FIFO ordering,
   state what happens to Undo/Redo/Reset while locked, or specify cancellation
   and destroy behavior. This is material because `GameRuntime` currently
   queues only while `PixiApp.isAnimating` (`src/runtime/GameRuntime.ts:52-87`)
   and the recursive camera can continue separately
   (`src/render/PixiApp.ts:61-78`; `RecursiveTransitionRenderer.ts:17-68`).
   Freeze one public runtime policy and its tests: command classification while
   locked, ordering/disposition, barrier owner, completion signal, cancellation,
   and teardown. Define the measurable midpoint invariant as well: the exact
   expected set/count of rendered world-frame occurrences and the addressable
   root/target aperture evidence at each capture, not only the phrase "no
   missing world frame."

3. **Global requirements contradict the stated V2-V4 deferrals.**
   `AGENTS.md` §8 makes retained layers, DPR cap plus actual mobile viewport,
   reduced motion, and pointer/touch mandatory frontend requirements. §9 then
   requires every runtime/render candidate to provide mobile and reduced-motion
   browser evidence. In contrast, `CURRENT_TASK.md` §5 accepts V1 using only
   desktop captures, while §6 defers retained scene graph to V3 and DPR,
   mobile, reduced-motion, pointer/touch, and capture automation to V4. The
   current implementation still recreates all layers per animated draw
   (`src/render/PixiApp.ts:175-189`) and uses uncapped
   `window.devicePixelRatio` (`src/render/PixiApp.ts:88-95`), so V1 cannot
   simultaneously preserve its planned boundary and satisfy the higher-priority
   global wording. Amend `AGENTS.md` or `CURRENT_TASK.md` to state the exact
   slice-scoped deferral: V1 must prove desktop occurrence/lock continuity;
   V3 owns retained-graph/performance acceptance; V4 owns DPR/mobile,
   reduced-motion, pointer/touch, and capture acceptance. The global gate must
   then require each item at its owning slice rather than from every V1
   runtime/render candidate.

### Non-blocking implementation notes

- V1's enumerated projection/runtime/render files do cover every current
  `container-b` dependency: prototype graph (`worldProjection.ts:37`), keyboard
  fallback (`InteractionPrototype.ts:47`), runtime selection
  (`GameRuntime.ts:90-92`), and transition geometry
  (`PixiApp.ts:295-324`).
- The R1 contract explicitly owns public `WorldAddress` and
  `EntityOccurrenceAddress` in C1 and directs V1 to consume them. V1 should
  replace the current projection-local `WorldAddress`/delimiter-built
  `projectionId` (`src/projection/types.ts:17-20`,
  `worldProjection.ts:75,111`) rather than define a competing address type.
- `DESIGN.md`'s presentation metadata remains renderer-owned and outside core,
  which is compatible with C1. Before V2 begins, a fresh bounded V2 contract
  must name its configuration source and owned palette/material/primitive
  paths; no additional C1 type needs to be frozen for it now.

### Evidence and checks

- Read the candidate itself at `e078083`, including `AGENTS.md`,
  `CURRENT_TASK.md`, `DESIGN.md`, `docs/reboot/CURRENT_STATUS.md`, and the
  coordinator log; no review conclusion relies on the delegation summary.
- Read the accepted R1 contract at `fee9c5b`, especially its address identity
  and C1/V1 ownership clauses.
- Inspected current projection, runtime, animation, and Pixi renderer code
  with line-numbered UTF-8 reads.
- `git show --check e078083`: passed.
- Candidate paths are documentation-only: `AGENTS.md`, `CURRENT_TASK.md`,
  `DESIGN.md`, `docs/reboot/CURRENT_STATUS.md`, and the coordinator log.

### Handoff

- Changed file for this review: `docs/workstreams/frontend-design/THREAD_LOG.md`
  only.
- Commit the log-only review, report its SHA to the coordinator, and stop.
- Do not begin C1, V1, V2, V3, or V4 from this review.
