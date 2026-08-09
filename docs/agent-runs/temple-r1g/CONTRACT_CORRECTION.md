# R1G evidence and hidden-snapshot contract correction

Date: 2026-08-09 Asia/Shanghai

Status: **contract correction and R1G-E1 source repair authorized; R1G remains in progress and is not accepted**

## Immutable input

- Source candidate: `f08a17044bd1c677857f732bffb7f5b38342dad4`
- Failed manifest: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-v2-candidate-f08a170-20260809T193900\candidate-f08a170-browser-evidence.json`
- Manifest SHA-256: `0CA07D549173FE12A367AE2C9EA55A5E393759561D845CAEC99B4DBBB92D06D1`
- Independent source disposition: `READY`, no P0/P1/P2
- Independent visual disposition: `VISUAL_READY`, no P0/P1
- Independent evidence disposition under the old predicate: `BLOCKED`

The 14 PNG hashes, candidate bindings, replay hashes, one-canvas boundary, zero gameplay DOM, zero overflow/problems/context loss, and triangle counts are valid. The manifest declares three failures for fixed jump, slide, and game-over scenes being compared to an all-frame `31`-call predicate. Independent audit finds an additional omitted conformance failure: all 11 hidden-pursuer records serialize sentinel `x/y=-1`, while the global TR4 contract requires null position/bounds/area/gap. The failed manifest and all PNGs remain immutable failure history.

## Contradiction being corrected

The original R1G evidence wording applied the ordinary-running `31`-call composition to every required record. The same contract requires a visible jump/slide hazard and the lifecycle-required pursuer in opening and every game-over state, while the R1G source scope forbids changes to `WorldRenderer.ts`, hazards, or pursuer code. Hiding those entities to force `31` calls would violate scene semantics and reduce visual fidelity.

This checkpoint corrects the evidence predicate and authorizes only the minimum production change needed to make hidden snapshots conform to the already-authoritative null schema. It does not relax the `28,000`-triangle ceiling, change the courier's six batches or one caster, alter pursuer lifecycle/placement, or permit a required object to be omitted.

## R1G-E1 exact source repair

Only `src/game/render/WorldRenderer.ts` and `src/game/render/WorldRenderer.test.ts` may change, within 80 hand-authored added or modified lines. `pursuerScreen.x/y` widen to `number | null`; initial and live hidden snapshots use null x/y; and at most one pure pursuer-screen constructor may be added when the live snapshot uses it. Direct tests exercise both hidden and visible constructor results. No lifecycle, canonical/simulation state, geometry, camera, placement, draw-call, triangle, courier, hazard, or material behavior may change.

## Binding fixed matrix

- Every record uses seed `1414087749`.
- Eight desktop gait records at ticks `60/64/68/72/76/80/84/88`: exactly `31` calls each; phase 0 also serves as the desktop ordinary-running record.
- Portrait and landscape ordinary running at tick `60`: exactly `31` calls each.
- Portrait reduced motion at tick `60`: exactly `31` calls.
- Every one of those 11 ordinary-composition records proves the post-opening pursuer is hidden with `x=null`, `y=null`, `visible=false`, `bounds=null`, and `pursuerGapPx=null`.
- Portrait jump apex at tick `21`: exactly `36` calls, canonical jump posture, `elapsedTicks < 54`, `distance < 6`, opening pursuer `visible=true` with positive bounds width/height/area, and exact event `section-0:jump-beam` with positive bounds width/height/area.
- Landscape slide at tick `15`: exactly `37` calls, canonical slide posture, `elapsedTicks < 54`, `distance < 6`, opening pursuer `visible=true` with positive bounds width/height/area, and exact event `section-0:slide-ring` with positive bounds width/height/area.
- Desktop public-trace game-over at tick `336`: exactly `34` calls, canonical game-over status and pursuer `visible=true` with positive bounds width/height/area.
- Every record: `<=28,000` whole-frame triangles, one canvas, zero gameplay DOM/overflow/problems/context loss, exact candidate SHA, canonical state/replay equality, and screenshot SHA-256.

The numbers above are exact whole-scene constants for the named seed/tick records, not general upper bounds. Any future seed, tick, or constant change requires a new coordinator contract before capture.

## Required continuation

This contract checkpoint is stacked above the unaccepted local courier source range `43ba6a3..f08a170`; pushing it alone would also publish that unaccepted range. Per `docs/COMMIT_POLICY.md`, it remains local until the complete source/evidence/QA chain is accepted, and no history rewrite or duplicate branch is used to manufacture an isolated push.

1. Commit this correction and R1G-E1 authorization without product source, generated evidence, QA disposition, or unrelated dirty paths.
2. Implement and target-test the exact two-path R1G-E1 repair, then commit it as a separate source checkpoint.
3. Preserve the old failed evidence directory byte-for-byte.
4. Because R1G-E1 edits product source, run exactly one new final typecheck, complete Vitest suite, no-delete production build, and browser evidence pass after its last source edit.
5. Create a unique new evidence directory and bind its manifest to the new source-candidate SHA.
6. Obtain independent source/evidence QA before any coordinator acceptance, changelog update, archive commit, or push.
