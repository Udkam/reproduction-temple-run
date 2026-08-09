# Temple R1H coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

Branch: `main`. Pushed baseline: `056b68701d71bb2c618e131d24039f53d646caff`. Preserved unpushed blocked source candidate: `8112156c8dd90bdd1821fbce5314b125cf912ebf`.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1G/R1G-E1 is accepted and pushed only for the volumetric courier and hidden-pursuer snapshot schema. Its 14-frame evidence at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-candidate-8de73c1-20260809T201927156\` remains the visual baseline, not evidence that the complete game is finished.

An independent visual-director pass inspected all 14 original-resolution frames and selected canyon macro silhouette as the next P0. Repeated giant shelf blocks, straight/equal roofs, empty gray skyline, weak near/mid/far occlusion, and unstructured black side void persist in every viewport and action state and occupy more screen area than the still-primitive hazards or opening/game-over pursuer. R1H therefore changes real environment geometry first; it may not substitute lighting, texture, fog, exposure, or camera changes for modeling.

Candidate `8112156` completed bounded source review as `READY`, but R1H remains `BLOCKED`. Its preserved evidence directory is `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-candidate-8112156-20260809T220359291\`, with failed manifest SHA-256 `29360C33992B48CCE62ED1C42AE2335363C2F563AE8ADE6F8A883B63C8D981BF`. The landscape runner measured `59.96653025884419 px` instead of `84-91 px`, and independent visual review found the required macro defects still present in all 14 frames. This candidate is not pushed or accepted.

## Exact source authority

After the R1H-C1 contract checkpoint is committed locally, one writer may edit exactly:

- `src/game/render/tideScarWorld.ts`
- `src/game/render/tideScarWorld.test.ts`

The original R1H source limit remains cumulative at 500 hand-authored added or modified lines. Candidate `8112156` consumes `171`; C1 may add or modify at most `320` more (`90` production / `230` direct-test). Only deterministic positions of existing shelf-run stations/profile steps and the 12 existing horizon islands' ring/crown vertices may change. All other source, tests, assets, scripts, packages, Blender/probe paths, evidence, and documentation are read-only for the writer.

R1H supersedes and closes all earlier R1/R1E source authority for these two paths. Those older clauses are historical only; no parallel or follow-on writer may use them.

## Frozen and reopened proof

R1H preserves four existing meshes (abyss plus near/mid/far), one existing material per mesh, zero groups/instancing/new scene objects, all vertex/index counts and index bytes, object names, 12 horizon components with eight stations/six tiers/96 triangles each, cut/shoulder factors, the near/mid `.04` final radial bridge, the 128 near/mid upper-riser triangles within `.045 <= normalY < .55`, shelf ratios, far overhang, surface attributes and face treatment, zero emissive, map strengths/floors and non-ownership, hemisphere correction bounds, quantized world placement, real gaps, route clearance, render calls/triangles, and disposal. The abyss geometry and far index SHA remain byte-frozen.

Near/mid/far position, normal, UV, colour, bounding, raw-position, and combined geometry fingerprints are deliberately reopened only because deterministic position movement recomputes them, including far raw-position SHA. Their old R1E values remain the historical baseline; tests must replace hash-only position freezing with stronger reconstruction of actual stations, closed topology, crown profiles, actual-triangle screen projection, and independent-world determinism. No index, topology, V7 radial/normal, shelf, overhang, or gap gate may be loosened.

Two independent read-only audits found that the first uncommitted scanline helper did not implement the contract: it projected from camera-behind `z=30m`, let one bank hide the other's void, and compared raw x-NDC to a height-relative limit. The corrected contract clips the real protected route edges from `-18m` to `-240m`, evaluates left/right independently, normalizes horizontal gaps by camera aspect, rejects needle contacts below `.02` height-normalized NDC, and requires each bank's own occupied-union height. Uncovered rows reduce that union but are not recast as an infinite horizontal interval, preserving genuine negative space. The earlier pre-candidate attribution to only middle-left seed `53` is historical and superseded by actual-triangle raycasts against the blocked frames: near seed `11` owns the long left wall, mid seed `47` station 0/front-cap/segment 0-1 owns the main right void edge and desktop seam, seed `17` is secondary, and the visible horizon stays flat because relief reached hidden tier 0 but not the visible outer ring. The unreliable first ROI rasterization is discarded as a gate, not converted into a false threshold.

C1 direct proof adds seed `11` interior lateral/elevation ranges `>=1.25/1.50m` and both interior adjacent-pair changes `>=.75/.75m`; every four-station interior pair `>=.75/.50m`; a crown-versus-shoulder differential per run `>=.35m` lateral or `>=.30m` vertical; visible upper-outer ring relief `>=.55/.40/.26m` near/mid/far and `<1.35m`; three visible profiles and roof-mean span `>=.50m` per band. The landscape right void and desktop right seam remain manual hard rejects even when numeric tests pass.

## Verification and evidence

Development runs only:

`npm.cmd run test -- src/game/render/tideScarWorld.test.ts`

After the final source edit, run exactly one typecheck, one complete Vitest suite, one no-delete production build, and one candidate-bound browser pass. The complete 14-record matrix uses seed `1414087749`: desktop gait `60/64/68/72/76/80/84/88`, portrait/landscape/reduced-motion run `60`, portrait jump `21`, landscape slide `15`, and desktop game-over `336`. All 11 ordinary records remain `31/23,574` calls/triangles, jump `36/24,810`, slide `37/24,890`, and game-over `34/24,236`. Every frame binds candidate SHA, canonical/replay state and screenshot hashes, one canvas, and zero gameplay DOM, overflow, browser problems, or context loss. The capture first verifies accepted R1G manifest SHA-256 `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`, then waits fail-closed for the unchanged runtime camera to reach each baseline position within `.05m` per axis with exact FOV/yaw. It may observe but never set the camera, scale, canonical state, or courier gate; fixed sleep alone is invalid.

Independent source and visual QA starts only after a candidate SHA. Numeric green gates cannot override unchanged block massing, repeated roofs/walls, flat/clipped skyline, structureless side void, filled genuine gaps, occlusion, floating/intersecting rock, or a change visible only through materials/lighting. A failed visual result is preserved as `BLOCKED`; it is not rewritten into acceptance.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited dirty backlog, every old candidate/evidence directory, failed diagnostic, and both material-socket probe scripts remain preserved and unstaged.

Historical next action (completed before candidate `8112156`): commit and push the three-path projection-gate correction, then return the sole geometry writer to the two authorized source paths.

Current next action: independently review and commit the four-path R1H-C1 documentation checkpoint locally without pushing the blocked stack. Then one sole geometry writer changes only the two authorized source paths, satisfies the direct gates, and runs only the targeted Tide Scar test. No final typecheck, full suite, build, browser capture, acceptance documentation, or push starts until that targeted result is green, source is checkpointed, and independent source QA is ready. Full C1 scope is in `docs/agent-runs/temple-r1h/CORRECTION.md`.
