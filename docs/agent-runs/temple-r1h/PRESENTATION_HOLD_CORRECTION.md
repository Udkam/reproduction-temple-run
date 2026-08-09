# Temple R1H-C4 DEV-only presentation hold

Updated: 2026-08-10 Asia/Shanghai

Status: **R1H source candidate `de636bc` is independently source-READY; C1, C2, and C3 evidence mechanisms are BLOCKED; one bounded DEV-only runtime QA seam plus one later evidence pass are authorized; R1H and the complete game remain in progress**

## Immutable history and root cause

- Project root: `E:\Proj\reproduction-temple-run`.
- Pushed baseline: `056b68701d71bb2c618e131d24039f53d646caff`.
- Geometry source candidate: `de636bc0d036f6d8916d5a19517387987bd40bc5`, exact two-path geometry scope, targeted `8/8`, independent source QA `READY`, cumulative R1H geometry churn `286/500`.
- C3 contract checkpoint: `a0aa433d13437daa678f1c40ee86c680365096a6`.
- Immutable R1G same-view manifest SHA-256: `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`.
- C3 directory: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c3-candidate-de636bc-20260810T002256684\`.
- C3 script SHA-256: `38EE8EA5E82DE4A1367FF86735F6467B1BC4EC5E8673DA3B0403A4A2614D72FE`; empty stdout SHA-256: `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`; stderr SHA-256: `C87EC9E8842D988E340D7F4EEBF022E2B442DA20BB724F50AB0D33B87D7F5048`.
- C3 exited `1` on the first record after a 3,000 ms timeout, wrote zero PNGs and no manifest, and closed port `4210`. Canonical state stayed frozen at hash `fa4e69d7`, tick `60`, status `running`, elapsed tick `60`. Tracker identity stayed intact with `held=false`, `holdCalls=0`, `requests=62`, `callbacksStarted=60`, and `pending=2`. Camera ended at `{x:0,y:6.06,z:4.582277164981484,fov:43,yaw:0}` versus baseline `{x:0,y:6.059903550433091,z:7.308502044360709,fov:43,yaw:0}`.

C3 did not deadlock and did not expose a product, geometry, camera, or canonical regression. Its wrapper covered both the product loop and Playwright RAF waiter; their callback load changed the real RAF cadence enough that the transient `.05m` baseline window never appeared. C2 and C3 both converged to the unchanged product target `z≈4.582277`. C1 had once observed the transient baseline through an unwrapped, lightweight native RAF waiter, then drifted during screenshot because the product presentation loop remained active.

C1, C2, and C3 directories, scripts, logs, screenshots, hashes, and dispositions are immutable. They cannot be overwritten, retried in place, deleted, hidden, or relabelled.

## Exact R1H-C4 source authority

One writer may edit exactly:

- `src/game/runtime/GameRuntime.ts`;
- `src/game/runtime/GameRuntime.test.ts`.

The source checkpoint may add or modify at most `80` hand-authored production lines and `120` direct-test lines. It may add one DEV QA API method named `holdPresentation()` and the minimum private presentation-held state needed to cancel and suppress the genuine runtime frame loop. It may not edit the renderer, camera, simulation core, world geometry, assets, package files, evidence thresholds, or any other source/test path.

`holdPresentation()` is a capture/testability seam, not gameplay. Its minimum behavior is:

1. It is reachable only through the existing `import.meta.env.DEV` QA API installation.
2. Each runtime starts with `presentationHeld=false`. The method sets the private latch before attempting cancellation, and the latch is one-way for that runtime lifetime: `start`, pause/resume, restart, QA seed/scenario/freeze/tick helpers, and repeated hold calls cannot clear it or queue a new runtime frame.
3. It sends one cancellation request for the current `frameHandle` through the existing clock adapter when one exists, clears that handle, and returns a structured proof including whether a handle existed and cancellation was requested plus the unchanged simulation and render snapshots. The latch, not a claim about browser queue removal, covers an already-selected callback.
4. `onFrame` checks the latch before any delta calculation, render, notify, or reschedule; `scheduleFrame()` also checks the latch. This covers a callback already selected by the browser when cancellation occurs.
5. It does not call `forceRender`, change camera/renderer state, dispatch a command, change canonical state, change timestamp/delta, or install a new wall-clock dependency.
6. A second call remains held and reports that no additional cancellation was requested; it cannot resume presentation or create a new frame. `destroy()` remains idempotent and cannot issue a second cancel for the already-cleared handle.

The direct fake-clock tests must prove both cancellation paths. An ordinary pending callback receives exactly one cancellation request, a later clock step produces no render/notify/reschedule, and the second hold call requests no additional cancellation. A separate adversarial branch must remove one callback from the clock's cancellable pending queue as though the browser had already selected it, call `holdPresentation()`, explicitly invoke that selected callback after hold, and prove the `onFrame` latch permits zero new render, notify, or `requestFrame`. In both branches canonical hash/tick/status/elapsedTicks/frozen plus the complete camera snapshot are exactly identical before and after hold. Existing lifecycle/dispose behavior remains green.

## Source checkpoint and final gates

The writer runs only the focused `GameRuntime` test while editing. After the last source edit, the coordinator runs exactly one final typecheck, one complete Vitest suite, one no-delete production build into a new unique temporary directory, and later one browser-evidence pass. The two source paths form one reviewable candidate checkpoint. Independent source QA reviews that candidate SHA read-only before any browser pass.

No geometry/source gate is weakened. The new runtime seam does not make R1H visual-READY and does not accept the complete game.

## R1H-C4 evidence authority

Only after the source candidate is committed and independently source-READY may the coordinator create one new unique R1H-C4 evidence directory and copy the real-time C1 harness. The copied script binds the new source candidate and its documentation-only capture HEAD, proves `candidate..HEAD -- src` is empty plus a clean `src` worktree, verifies the immutable R1G manifest bytes, and retains the complete 14-record matrix and every legacy replay, screenshot hash, canvas/DOM/overflow/problem/context-loss, draw-call, triangle, visibility, scenario-trace, hazard, reduced-motion, and `84-91 px` landscape courier gate.

The R1H-C4 script uses the original unwrapped native `waitForFunction({polling:'raf'})` path. Each light predicate reads only the real product camera until the immutable R1G tolerance matches. On match, in the same predicate stack, it reads the canonical identity and camera, calls `qa.holdPresentation()` synchronously, and immediately reads both again. A record fails unless the returned proof says exactly one pending product frame handle existed and received a cancellation request, camera and canonical identity are exact across the call, and subsequent structured pre-screenshot, screenshot, and post-screenshot reads remain exact. Direct camera/renderer/runtime-field assignment, RAF wrapping, Playwright Clock, timer sampling, fixed-delay-only evidence, or a second evidence pass is forbidden.

The capture predicate must remain lightweight before match: it cannot clone canonical state, render snapshots beyond camera, or run diagnostics on every RAF. This preserves the native C1 observation path. Full canonical and hold proof are read only on the matching call. Any timeout, skipped window, missing pending frame, already-selected callback that renders after hold, camera/canonical drift, or legacy-gate failure produces no `captured` claim and returns nonzero.

If the sole R1H-C4 pass does not capture all 14 records, no fifth capture mechanism is authorized. The transient R1G camera baseline is then itself `BLOCKED` as nondeterministic and requires a new contract for a stable deterministic presentation baseline; it cannot be solved by weakening tolerance or adding another capture hack.

## Disposition order

1. Independent contract QA reviews this five-path documentation checkpoint read-only.
2. The coordinator commits only the five contract paths locally; the blocked stack remains unpushed.
3. One writer implements and focused-tests the exact two source paths, then the coordinator runs the single final source gate set and commits the source candidate.
4. Independent source QA reviews the candidate SHA read-only.
5. The copied R1H-C4 script receives syntax validation and independent static QA without browser/test/build execution.
6. Exactly one R1H-C4 14-record browser pass runs in its new directory.
7. Only a `captured` manifest permits independent evidence QA and independent full-resolution visual QA against corresponding R1G frames.
8. Only coordinator acceptance may update the changelog/archive, push the full linear stack, and report branch plus exact SHAs.

No cleanup, reset, deletion, overwrite, force push, C1/C2/C3 retry, Blender/probe process, or unrelated backlog edit is authorized.
