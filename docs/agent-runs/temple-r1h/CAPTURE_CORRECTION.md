# Temple R1H-C2 presentation-clock capture correction

Updated: 2026-08-09 Asia/Shanghai

Status: **R1H source candidate `de636bc` is independently source-READY; its first C1 browser pass is evidence-BLOCKED; one evidence-harness-only C2 correction is authorized; R1H and the complete game remain in progress**

## Immutable candidate and failure history

- Project root: `E:\Proj\reproduction-temple-run`.
- Pushed baseline: `056b68701d71bb2c618e131d24039f53d646caff`.
- C1 contract checkpoint: `0186e81b39d4643dd398e535a218550e1fc7e3e4`.
- Source candidate: `de636bc0d036f6d8916d5a19517387987bd40bc5`.
- Source scope: exactly `src/game/render/tideScarWorld.ts` and `src/game/render/tideScarWorld.test.ts`.
- Source disposition: targeted `8/8`, independent source QA `READY`, C1 churn `115`, cumulative R1H churn `286/500`.
- Full suite: `17 files / 75 tests`, exit `0`.
- Valid no-delete build: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c1-build-de636bc-20260809T232247032\`, 31 files. The earlier unquoted-path invocation failed before resolving the project entry, created no output directory, and remains preserved in its original logs.
- First C1 capture directory: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c1-candidate-de636bc-20260809T232247032\`.
- First C1 capture-script SHA-256: `597E6E4ACA286025DC7BD7737CF5B1E75A3FCACE712ADFA2530B77BE051A7BBD`.
- Preserved first-frame PNG: `gait-phase-0-desktop-tick60-1440x900.png`, SHA-256 `4A2E005D504DB64BCAB36672D7DB5A9951E1902D8199A2EEB8745AB25736326F`.
- Failure: the pre-screenshot camera matched the immutable R1G baseline, but presentation RAF continued while Playwright encoded the screenshot; post-screenshot camera delta was `x=0`, `y=0.00009644956690824102`, `z=2.7262248793828983`, `fov=0`, `yaw=0`.
- Disposition: browser exit `1`, no evidence manifest, no visual acceptance, and no push. The embedded Vite server closed and port `4210` had no remaining listener.

Every path and byte above is immutable history. Nothing may be deleted, overwritten, replaced in place, relabelled as accepted, or hidden from review.

## Exact C2 authority

C2 reopens no repository product source, test, package, config, asset, documentation outside this contract checkpoint, camera behavior, renderer behavior, simulation, canonical state, runner scale, evidence matrix, numeric gate, or visual gate. After this contract is independently reviewed and committed, the coordinator may create one new unique temporary evidence directory, copy `capture_candidate.mjs` from the failed C1 directory, and modify only that copied script.

The copied script retains candidate SHA `de636bc0d036f6d8916d5a19517387987bd40bc5`, contract provenance, project root, strict local Vite server lifecycle, immutable R1G manifest byte hash `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`, complete 14-ID seed/tick/profile matrix, exact calls/triangles, canonical/replay and screenshot hashes, one canvas, zero gameplay DOM/overflow/problems/context loss, and the `84-91 px` landscape courier gate.

## Controlled natural-camera hold

For each fresh browser context, the script installs Playwright Clock before navigation and lets the application reach the QA-ready `ready` state. Before loading a candidate scenario, it moves to one declared future clock instant with `page.clock.pauseAt`, verifies exact `Date.now()` plus finite `performance.now()`, and leaves the presentation clock paused. The future pause may trigger at most one `ready`-state RAF; it occurs before candidate scenario loading and therefore cannot advance candidate canonical state or candidate camera convergence. Once paused, readiness and control use host-driven calls only; no page RAF/timeout polling is allowed.

Only after that pause proof does the script load the fixed scenario, apply explicit canonical tick advancement, call `qa.freeze(true)`, and save a canonical anchor. It then advances the genuine GameRuntime `requestAnimationFrame` path only through bounded `page.clock.runFor(16)` steps, checking the actual runtime render snapshot and unchanged canonical anchor after each step. It fails closed if the corresponding R1G baseline camera is not reached within 3,000 controlled milliseconds. Matching remains `abs(x/y/z delta) <= .05m` with exact FOV and yaw. This is deterministic presentation-time control, not camera control: the script may not assign or patch camera position, quaternion, yaw, FOV, matrices, target, damping, delta, renderer methods, runtime adapters, simulation, scale, canvas, or source.

Once a matching runtime frame exists, the page clock remains paused. The script captures a viewport PNG with `fullPage: false`, then reads runtime snapshots and page-clock values again without advancing the clock. It must prove:

- pre- and post-screenshot camera x/y/z/FOV/yaw are exactly identical;
- both cameras satisfy the unchanged R1G baseline tolerance;
- canonical hash, tick, status, elapsedTicks, and frozen state are exactly identical;
- `Date.now()` and `performance.now()` are exactly identical before and after screenshot;
- screenshot bytes exist only in the new directory and have a valid SHA-256;
- replay produces the same canonical hash after the screenshot;
- no page timer, RAF predicate wait, direct evaluation assignment, or fixed sleep is used to manufacture a camera value.

Each successful record adds the baseline camera, actual held camera, clock epoch, requested paused instant, controlled milliseconds/steps, clock-installed/paused proof, exact pre/post clock values, exact pre/post camera deltas, and post-screenshot canonical fields. The root manifest retains schema version 2 and adds the immutable baseline manifest identity plus the C2 clock-control method. Any setup, convergence, stability, screenshot, replay, matrix, or legacy-gate failure produces no `captured` claim and returns nonzero.

## Verification order and disposition

1. Independent contract QA reviews this checkpoint read-only.
2. The coordinator commits only the four contract paths; the blocked source stack remains local and unpushed.
3. The new copied script receives syntax validation and independent static QA without launching a browser.
4. Exactly one corrected 14-record browser pass runs in the new directory. The failed C1 directory is never reused.
5. If and only if the manifest is `captured`, independent evidence QA validates every record and hash, and independent visual QA inspects all 14 original-resolution frames against the same-view R1G frames.
6. Numeric green cannot override the manual hard rejects in `CORRECTION.md`. A visual `BLOCKED` result remains preserved and opens a new bounded product contract; it is never converted into acceptance.
7. Only coordinator acceptance may update the changelog, archive the evidence/QA disposition, push the linear stack, and report branch plus exact SHAs.

No typecheck, full Vitest suite, production build, product source edit, Blender process, probe process, cleanup, reset, deletion, force push, or evidence replacement is authorized by C2.
