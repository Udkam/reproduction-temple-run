# Temple R1H coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

Branch: `main`. Pushed baseline: `056b68701d71bb2c618e131d24039f53d646caff`. Local contract checkpoint: `0186e81b39d4643dd398e535a218550e1fc7e3e4`. Current unpushed source candidate: `de636bc0d036f6d8916d5a19517387987bd40bc5`.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1G/R1G-E1 is accepted and pushed only for the volumetric courier and hidden-pursuer snapshot schema. Its 14-frame evidence at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-candidate-8de73c1-20260809T201927156\` remains the visual baseline, not evidence that the complete game is finished.

An independent visual-director pass inspected all 14 original-resolution frames and selected canyon macro silhouette as the next P0. Repeated giant shelf blocks, straight/equal roofs, empty gray skyline, weak near/mid/far occlusion, and unstructured black side void persist in every viewport and action state and occupy more screen area than the still-primitive hazards or opening/game-over pursuer. R1H therefore changes real environment geometry first; it may not substitute lighting, texture, fog, exposure, or camera changes for modeling.

Candidate `8112156` completed bounded source review as `READY`, but R1H remains `BLOCKED`. Its preserved evidence directory is `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-candidate-8112156-20260809T220359291\`, with failed manifest SHA-256 `29360C33992B48CCE62ED1C42AE2335363C2F563AE8ADE6F8A883B63C8D981BF`. The landscape runner measured `59.96653025884419 px` instead of `84-91 px`, and independent visual review found the required macro defects still present in all 14 frames. This candidate is not pushed or accepted.

Candidate `de636bc` completes the bounded C1 source correction in exactly `tideScarWorld.ts` and its direct test. Targeted `8/8`, independent source QA, and cumulative churn `286/500` are green. The final full suite is `17 files / 75 tests`; the valid no-delete build produced 31 files in `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c1-build-de636bc-20260809T232247032\`. A preceding Windows argument-quoting attempt failed before resolving the project entry and created no build directory; both failed and corrected logs are preserved. The typecheck process completed with zero diagnostics/stderr, although its outer one-second observer ended before returning the child exit code; it was not rerun.

The first C1 browser pass is evidence-`BLOCKED`, not a product or visual acceptance result. Directory `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c1-candidate-de636bc-20260809T232247032\` preserves script SHA-256 `597E6E4ACA286025DC7BD7737CF5B1E75A3FCACE712ADFA2530B77BE051A7BBD`, all gate logs, and one first-frame PNG SHA-256 `4A2E005D504DB64BCAB36672D7DB5A9951E1902D8199A2EEB8745AB25736326F`. The pre-screenshot camera matched R1G, but unpaused presentation RAF advanced during screenshot and post-screenshot `z` differed by `2.7262248793828983m`. Exit was `1`, no manifest was written, and port `4210` closed. Nothing in this directory may be overwritten or relabelled.

## Exact source authority

The completed C1 writer edited exactly:

- `src/game/render/tideScarWorld.ts`
- `src/game/render/tideScarWorld.test.ts`

The original R1H source limit remains cumulative at 500 hand-authored added or modified lines. Candidate `8112156` consumes `171`; C1 adds `115`, for cumulative `286/500`. Source authority is now closed. C2 reopens no source, tests, assets, packages, Blender/probe paths, camera, renderer, simulation, or evidence constants.

R1H supersedes and closes all earlier R1/R1E source authority for these two paths. Those older clauses are historical only; no parallel or follow-on writer may use them.

## Frozen and reopened proof

R1H preserves four existing meshes (abyss plus near/mid/far), one existing material per mesh, zero groups/instancing/new scene objects, all vertex/index counts and index bytes, object names, 12 horizon components with eight stations/six tiers/96 triangles each, cut/shoulder factors, the near/mid `.04` final radial bridge, the 128 near/mid upper-riser triangles within `.045 <= normalY < .55`, shelf ratios, far overhang, surface attributes and face treatment, zero emissive, map strengths/floors and non-ownership, hemisphere correction bounds, quantized world placement, real gaps, route clearance, render calls/triangles, and disposal. The abyss geometry and far index SHA remain byte-frozen.

Near/mid/far position, normal, UV, colour, bounding, raw-position, and combined geometry fingerprints are deliberately reopened only because deterministic position movement recomputes them, including far raw-position SHA. Their old R1E values remain the historical baseline; tests must replace hash-only position freezing with stronger reconstruction of actual stations, closed topology, crown profiles, actual-triangle screen projection, and independent-world determinism. No index, topology, V7 radial/normal, shelf, overhang, or gap gate may be loosened.

Two independent read-only audits found that the first uncommitted scanline helper did not implement the contract: it projected from camera-behind `z=30m`, let one bank hide the other's void, and compared raw x-NDC to a height-relative limit. The corrected contract clips the real protected route edges from `-18m` to `-240m`, evaluates left/right independently, normalizes horizontal gaps by camera aspect, rejects needle contacts below `.02` height-normalized NDC, and requires each bank's own occupied-union height. Uncovered rows reduce that union but are not recast as an infinite horizontal interval, preserving genuine negative space. The earlier pre-candidate attribution to only middle-left seed `53` is historical and superseded by actual-triangle raycasts against the blocked frames: near seed `11` owns the long left wall, mid seed `47` station 0/front-cap/segment 0-1 owns the main right void edge and desktop seam, seed `17` is secondary, and the visible horizon stays flat because relief reached hidden tier 0 but not the visible outer ring. The unreliable first ROI rasterization is discarded as a gate, not converted into a false threshold.

C1 direct proof adds seed `11` interior lateral/elevation ranges `>=1.25/1.50m` and both interior adjacent-pair changes `>=.75/.75m`; every four-station interior pair `>=.75/.50m`; a crown-versus-shoulder differential per run `>=.35m` lateral or `>=.30m` vertical; visible upper-outer ring relief `>=.55/.40/.26m` near/mid/far and `<1.35m`; three visible profiles and roof-mean span `>=.50m` per band. The landscape right void and desktop right seam remain manual hard rejects even when numeric tests pass.

## Verification and evidence

Development runs only:

`npm.cmd run test -- src/game/render/tideScarWorld.test.ts`

The completed source gate set is not rerun because C2 changes no repo source. The corrected browser pass alone reuses the complete 14-record matrix and exact calls/triangles constants. It verifies the R1G manifest bytes, installs Playwright Clock before navigation, enters a verified paused state while the application is still `ready`, then loads the candidate scenario and advances the actual GameRuntime `requestAnimationFrame` loop in bounded `16ms` steps until each baseline camera is reached within `.05m` per axis with exact FOV/yaw. The clock stays paused through the viewport screenshot. Pre/post page clock and camera coordinates must be identical, as must canonical hash/tick/status/elapsedTicks; direct camera/renderer mutation is forbidden.

Independent source and visual QA starts only after a candidate SHA. Numeric green gates cannot override unchanged block massing, repeated roofs/walls, flat/clipped skyline, structureless side void, filled genuine gaps, occlusion, floating/intersecting rock, or a change visible only through materials/lighting. A failed visual result is preserved as `BLOCKED`; it is not rewritten into acceptance.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited dirty backlog, every old candidate/evidence directory, failed diagnostic, and both material-socket probe scripts remain preserved and unstaged.

Historical next action (completed before candidate `8112156`): commit and push the three-path projection-gate correction, then return the sole geometry writer to the two authorized source paths.

Current next action: independently review and commit the four-path R1H-C2 documentation checkpoint locally without pushing the blocked stack. Then copy the failed capture script into one new unique evidence directory, apply only the authorized Playwright-clock correction, obtain independent static script QA, and run exactly one corrected browser pass. If its manifest and all 14 frames pass independent evidence and visual QA, the coordinator archives acceptance and pushes the full linear stack. Full C2 scope is in `docs/agent-runs/temple-r1h/CAPTURE_CORRECTION.md`.
