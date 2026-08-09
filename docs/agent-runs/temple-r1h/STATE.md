# Temple R1H coordinator state

Updated: 2026-08-09 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

Branch and pushed source baseline: `main` at R1H contract commit `b0be63f1af2be01b556834ce123c8bd24eeddc19`.

## Objective and disposition

The full objective remains a real high-fidelity 3D TIDE//RELAY game. R1G/R1G-E1 is accepted and pushed only for the volumetric courier and hidden-pursuer snapshot schema. Its 14-frame evidence at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-candidate-8de73c1-20260809T201927156\` remains the visual baseline, not evidence that the complete game is finished.

An independent visual-director pass inspected all 14 original-resolution frames and selected canyon macro silhouette as the next P0. Repeated giant shelf blocks, straight/equal roofs, empty gray skyline, weak near/mid/far occlusion, and unstructured black side void persist in every viewport and action state and occupy more screen area than the still-primitive hazards or opening/game-over pursuer. R1H therefore changes real environment geometry first; it may not substitute lighting, texture, fog, exposure, or camera changes for modeling.

## Exact source authority

After this contract checkpoint is committed and pushed, one writer may edit exactly:

- `src/game/render/tideScarWorld.ts`
- `src/game/render/tideScarWorld.test.ts`

The source checkpoint limit is 500 hand-authored added or modified lines. Only existing shelf-run station positions and the 12 existing horizon islands' ring/crown positions may change. All other source, tests, assets, scripts, packages, Blender/probe paths, evidence, and documentation are read-only for the writer.

R1H supersedes and closes all earlier R1/R1E source authority for these two paths. Those older clauses are historical only; no parallel or follow-on writer may use them.

## Frozen and reopened proof

R1H preserves four existing meshes (abyss plus near/mid/far), one existing material per mesh, zero groups/instancing/new scene objects, all vertex/index counts and index bytes, object names, 12 horizon components with eight stations/six tiers/96 triangles each, cut/shoulder factors, the near/mid `.04` final radial bridge, the 128 near/mid upper-riser triangles within `.045 <= normalY < .55`, shelf ratios, far overhang, surface attributes and face treatment, zero emissive, map strengths/floors and non-ownership, hemisphere correction bounds, quantized world placement, real gaps, route clearance, render calls/triangles, and disposal. The abyss geometry and far index SHA remain byte-frozen.

Near/mid/far position, normal, UV, colour, bounding, raw-position, and combined geometry fingerprints are deliberately reopened only because deterministic position movement recomputes them, including far raw-position SHA. Their old R1E values remain the historical baseline; tests must replace hash-only position freezing with stronger reconstruction of actual stations, closed topology, crown profiles, actual-triangle screen projection, and independent-world determinism. No index, topology, V7 radial/normal, shelf, overhang, or gap gate may be loosened.

Two independent read-only audits found that the first uncommitted scanline helper did not implement the contract: it projected from camera-behind `z=30m`, let one bank hide the other's void, and compared raw x-NDC to a height-relative limit. The corrected contract clips the real protected route edges from `-18m` to `-240m`, evaluates left/right independently, normalizes horizontal gaps by camera aspect, rejects needle contacts below `.02` height-normalized NDC, and requires each bank's own occupied-union height. Uncovered rows reduce that union but are not recast as an infinite horizontal interval, preserving genuine negative space. The read-only geometry diagnosis then identifies only the middle left shelf run with seed `53` as the true gap owner; the failed `±13m` inner-island experiment does not affect that gap and violates island clearance.

## Verification and evidence

Development runs only:

`npm.cmd run test -- src/game/render/tideScarWorld.test.ts`

After the final source edit, run exactly one typecheck, one complete Vitest suite, one no-delete production build, and one candidate-bound browser pass. The complete 14-record matrix uses seed `1414087749`: desktop gait `60/64/68/72/76/80/84/88`, portrait/landscape/reduced-motion run `60`, portrait jump `21`, landscape slide `15`, and desktop game-over `336`. All 11 ordinary records remain `31/23,574` calls/triangles, jump `36/24,810`, slide `37/24,890`, and game-over `34/24,236`. Every frame binds candidate SHA, canonical/replay state and screenshot hashes, one canvas, and zero gameplay DOM, overflow, browser problems, or context loss.

Independent source and visual QA starts only after a candidate SHA. Numeric green gates cannot override unchanged block massing, repeated roofs/walls, flat/clipped skyline, structureless side void, filled genuine gaps, occlusion, floating/intersecting rock, or a change visible only through materials/lighting. A failed visual result is preserved as `BLOCKED`; it is not rewritten into acceptance.

## Preservation and next action

No file may be deleted, reverted, cleaned, overwritten, or lost. The inherited dirty backlog, every old candidate/evidence directory, failed diagnostic, and both material-socket probe scripts remain preserved and unstaged.

Next action: commit and push this exact three-path gate correction, then return the sole geometry writer to the two authorized source paths. The writer must first repair the projection helper, restore the inner middle islands' safe centres, move only the diagnosed seed-`53` shelf run enough to satisfy the corrected gate, and run only the targeted Tide Scar test. No final typecheck, full suite, build, browser capture, candidate commit, or push starts until that targeted result is green and independently reviewed.
