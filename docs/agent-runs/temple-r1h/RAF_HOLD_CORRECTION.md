# Temple R1H-C3 atomic RAF-hold capture correction

Updated: 2026-08-10 Asia/Shanghai

Status: **R1H source candidate `de636bc` is independently source-READY; C1 and C2 evidence mechanisms are BLOCKED; one evidence-harness-only C3 correction is authorized; R1H and the complete game remain in progress**

## Immutable history and cause

- Project root: `E:\Proj\reproduction-temple-run`.
- Pushed baseline: `056b68701d71bb2c618e131d24039f53d646caff`.
- Source candidate: `de636bc0d036f6d8916d5a19517387987bd40bc5`, exact two-path source scope, targeted `8/8`, independent source QA `READY`, cumulative R1H churn `286/500`.
- R1G same-view manifest SHA-256: `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`.
- C1 failure: real-time camera reached the baseline window, but presentation RAF continued during screenshot and moved z by `2.7262248793828983m`. The immutable C1 directory, one PNG, script, and logs remain recorded in `CAPTURE_CORRECTION.md`.
- C2 failure: paused Playwright Clock retained canonical hash `fa4e69d7`, tick `60`, and frozen state, but its 16 ms RAF lattice skipped the `.05m` z window. Directory `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c2-candidate-de636bc-20260809T235226399\` has script SHA-256 `5C25EFE9E71AD1DEF1710A51EA1B374E748A27A3901D80E203523ECB804BE428`, stderr SHA-256 `C517D6AF8C497170E4ADE766ABED750C6365A71128B486F517222A8CDE104C64`, zero PNGs, and no manifest.

Neither failure is product or visual acceptance. Both directories and every byte in them are immutable. Nothing may be deleted, overwritten, retried in place, hidden, or relabelled.

## Exact C3 authority

C3 reopens no repository source, test, package, config, asset, camera, renderer, runtime adapter, simulation, canonical state, evidence matrix, numeric threshold, courier gate, or visual gate. After this contract is independently reviewed and committed, the coordinator may create one new unique temporary evidence directory, copy the real-time C1 `capture_candidate.mjs`, and modify only that copied script.

The new script retains source candidate `de636bc0d036f6d8916d5a19517387987bd40bc5`, records the current documentation-only capture HEAD, proves `candidate..HEAD -- src` is empty plus a clean `src` worktree, binds the immutable R1G manifest bytes, starts and closes one strict local Vite server, and retains the complete 14-record matrix and every old replay, screenshot-hash, canvas/DOM/overflow/problem/context-loss, draw-call, triangle, visibility, scenario-trace, hazard, reduced-motion, and `84-91 px` landscape courier gate.

Playwright Clock is forbidden in C3. Fixed sleep cannot establish the same-view frame.

## Transparent RAF tracker

For each browser context, before `newPage`, the script installs one main-world init script that captures and binds the native `requestAnimationFrame` and `cancelAnimationFrame`, then exposes one non-configurable capture-only tracker. Before hold:

- wrapped RAF obtains a native handle, adds it to a private pending `Set`, and records request counts;
- at native callback entry it removes its own handle, records the callback, and invokes the original callback with the unchanged timestamp and `window` receiver through `Reflect.apply`;
- wrapped cancel removes the handle from the private set and delegates to native cancel;
- it does not inspect a Three object, camera, renderer, QA snapshot, simulation, callback source, timestamp, delta, or return value.

The tracker exposes only `snapshot()` and `hold()`. `snapshot()` returns counters and latch state without mutation. `hold()` is valid exactly once. It synchronously sets `held=true`, snapshots all other pending handles, clears the set, cancels every copied handle through native cancel, and returns the hold proof. A second hold throws. If a wrapped native callback was already selected for the same display frame, its entry guard sees `held`, records `suppressedAfterHold`, and does not invoke its page callback. Any new RAF request after hold obtains then immediately cancels a native handle and increments `postHoldRequests`; final acceptance requires `postHoldRequests === 0`. Wrapped callbacks invoked after hold must remain exactly zero. All counters cover every main-world RAF that uses the wrapper, including a Playwright waiter if its lazily created injected builtins captured that wrapper; they are not product-only counters.

The script must prove after navigation that the public RAF/cancel functions are still the installed wrappers and the tracker property is intact. Wrapper replacement or missing proof is immediate `BLOCKED`.

## Atomic convergence and capture

The fixed scenario is loaded through the unchanged public QA commands, explicit ticks are applied, `qa.freeze(true)` is called, and a canonical anchor is saved. The product's unchanged real-time RAF drives camera damping.

`page.waitForFunction` runs a main-world predicate with a 3,000 ms timeout. Its lazily created main-world injected builtins may capture the tracker wrapper. At wrapper callback entry, the executing waiter's handle is removed from the pending set before its predicate runs. Every predicate call first compares canonical hash, tick, status, elapsedTicks, and frozen state with the anchor. It then reads the actual camera. A non-match returns false and schedules the next waiter RAF normally. On the first baseline match—`abs(x/y/z delta) <= .05m`, exact FOV and yaw—the same predicate call stack must:

1. save the camera and canonical state before hold;
2. call tracker `hold()` synchronously;
3. read camera, canonical state, and tracker snapshot again;
4. require exact before/after camera and canonical equality;
5. return the complete match/hold proof.

Calling hold after `waitForFunction` returns to Node is forbidden. On success, the executing waiter handle is already absent from pending and the waiter schedules no next RAF. The in-stack hold therefore cancels every other pending main-world handle without canceling or deadlocking the current waiter, whether the waiter captured native RAF or the wrapper.

Immediately after the returned proof, the script reads the full structured snapshot and requires exact equality with the held camera and canonical anchor. It captures one viewport PNG with `fullPage:false`, then reads post-screenshot state. A record passes only if:

- wrapper/tracker identity remains intact;
- `holdCalls === 1`;
- `pendingBeforeHold >= 1`;
- `cancelledByHold === pendingBeforeHold`;
- `pendingAfterHold === 0` before and after screenshot;
- `postHoldRequests === 0` and wrapped main-world callbacks after hold equal zero;
- camera before hold, after hold, pre-screenshot, and post-screenshot are exactly identical and satisfy the unchanged R1G baseline gate;
- canonical hash/tick/status/elapsedTicks/frozen are exactly identical at anchor, before/after hold, pre, and post;
- replay hash and every legacy evidence gate remain green.

The manifest retains schema version 2 and records baseline identity, source candidate, capture HEAD, script SHA checked outside the script, `mechanism: native-raf-cancel-only`, wrapper counters, hold proof, camera deltas, and canonical identities. Static independent QA plus the captured script SHA are the authority that no camera assignment exists; self-reported runtime booleans alone cannot prove that negative claim.

Any timeout, wrapper change, missing pending handle, duplicate hold, incomplete cancellation, post-hold request/callback, camera/canonical drift, screenshot error, replay mismatch, matrix mismatch, or legacy-gate failure produces no `captured` claim and returns nonzero.

## Verification and disposition

1. Independent contract QA reviews this five-path checkpoint read-only.
2. The coordinator commits only the five contract paths; the blocked stack remains local and unpushed.
3. The copied script receives syntax validation and independent static QA without browser, test, or build execution.
4. Exactly one C3 14-record browser pass runs in its new directory. C1 and C2 directories are never reused.
5. Only a `captured` manifest permits independent evidence QA and independent full-resolution visual QA against the corresponding R1G frames.
6. Visual QA still hard-rejects the long wall, repeated blocks/equal roofs, weak depth hierarchy, flat skyline, right void, seam/needle, occlusion, filled gaps, floating/intersecting rock, or a non-geometry workaround. Numeric green cannot override these rejects.
7. Only coordinator acceptance may update the changelog/archive, push the full linear stack, and report branch plus exact SHAs.

No product edit, typecheck, Vitest, build, Blender/probe process, evidence overwrite, cleanup, reset, deletion, force push, or C1/C2 retry is authorized by C3.
