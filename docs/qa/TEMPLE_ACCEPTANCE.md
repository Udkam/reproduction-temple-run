# TIDE//RELAY Acceptance Matrix

## Rules

- Same seed produces identical sections, turns, events, RNG state, and replay hash.
- Lane changes remain in bounds and turn-window priority prevents accidental lane movement.
- Jump arc rises, peaks, falls, and lands exactly; beam and gap thresholds agree with posture.
- Slide duration and collision volume agree; rings are safe only during the active slide.
- Columns require another lane.
- Correct turns advance once; wrong or missing turns fail with the correct reason.
- Shards and shields collect once; a shield absorbs exactly one non-gap obstacle and applies deterministic recovery/chase pressure.
- Pause freezes all canonical state; restart resets clocks, input, score, consumed events, and course.
- Generator fairness checks reject impossible patterns.
- Safe travel opens the bounded canonical pursuer gap; shielded and unshielded non-gap stumbles close it; repeated misses can reach a command-reproducible capture at the threshold.
- Every 250 m milestone emits once, displays the canonical whole-meter boundary, and never alters replay determinism.
- Stored QA traces retain their accepted public-command sequence and replay hash. The milestone, close-chase, beam, ring, column, and gap records must expose that proof alongside the rendered canonical snapshot.

## Runtime and input

- Fixed-step simulation is independent of display refresh rate and caps catch-up work.
- Real keyboard and touch gestures each emit one semantic action.
- CSS-pixel swipe thresholds behave identically at DPR1 and DPR3.
- UI button presses cannot leak into the gesture surface.
- Blur and hidden documents pause active play without resuming an already-paused run.
- Unmount removes listeners, animation frames, WebGL resources, and audio voices.

## Visual evidence

- TR3 desktop (1440 x 900 DPR1): normal run, close chase, 250 m milestone, paused, beam, ring, column, and gap.
- TR3 portrait (390 x 844 DPR3): normal run, close chase, and 250 m milestone.
- TR3 landscape (844 x 390 DPR3): running with score, distance, flow, and shards all visible.
- Keyboard and DPR3 touch input, reduced motion, and lifecycle cleanup continue to be exercised from the real runtime.

## Browser hard gates

- Exactly one WebGL canvas and zero gameplay DOM entities.
- No horizontal overflow; HUD and controls remain inside safe areas.
- Runner lane endpoint error is at most 0.01 world unit.
- Turn midpoint shows both incoming and outgoing route geometry.
- Obstacles remain visually distinct in normal, mobile, and high-contrast contexts.
- The HUD's structured score, floored distance, shards, and flow values exactly equal the canonical snapshot values.
- Historical TR3 close-chase evidence reported positive pursuer bounds. TR4 close-pressure evidence instead requires `visible=false` and null pursuer position/bounds/area/gap.
- Beam, ring, column, and gap evidence each reports the expected canonical kind and positive clipped CSS-pixel bounds; the combined fixed desktop/mobile/high-contrast matrix proves all four silhouettes.
- Milestone, close-chase, and hazard-preview evidence states replay from real public commands to the recorded canonical hash; direct state fabrication is a hard failure.
- The milestone scenario visibly renders both the exact canonical score and `250 m`.
- The articulated runner retains readable leg/arm action under normal motion and semantic jump/slide poses under reduced motion.
- Eight adjacent gait-phase samples prove continuously interpolated limb endpoints: no phase boundary jump, limb-side flip, crossed legs, foot slide, or same-side arm/leg synchronization.
- The production Tide Scar world has a narrow readable sandstone/black-basalt causeway, deep tide-blue canyon, fogged far/mid/near contour layers, one right-edge white scar, sparse coral edge scars, and no visual decoration that masks canonical lane/collision meaning.
- The pursuer is a bookend-only original black-rock quadruped. Historical continuous TR3 visibility/gap assertions are superseded by the exact TR4 lifecycle gate below; canonical `chaseGap` remains unchanged while the mesh is hidden.
- TR4 render metrics are no more than 60 draw calls and no more than 150,000 triangles in normal desktop capture; preparation p95 remains below 8 ms desktop and 12 ms mobile.
- Console errors, unhandled rejections, and WebGL context loss count are zero.
- Every screenshot has seed, tick, viewport, DPR, state/render snapshot, and SHA-256 evidence.
- Scene-preparation CPU p95 is below 8 ms desktop and 12 ms mobile.

## Current result

Result: **TEMPLE-TR4 in progress; C7 dry preflight blocked before Blender, exact C7-T2F validator correction authorized.** C7-T1 `a9acb0a` and C7-T2 `51fdbab` passed independent source review, but the first non-writing dry preflight returned `PRECHECK_BLOCKED` on order-sensitive keys at `$.construction.atmosphere`; `diagnostic-007` remained absent. C7-T2F may correct only the runner dictionary comparison to use exact key sets without changing values or lowering unknown/missing-key rejection. A fresh dry preflight is required before Blender. TR2 remains the accepted simulation/runtime baseline described below. TR3/A3-A6 and C1-C6 are historical, unintegrated or blocked visual attempts and do not supply TR4 acceptance evidence.

## TEMPLE-TR4 visual and lifecycle gates

- The user-approved `941x1672` visual north star is used only as an external high-level reference. No reference frame or commercial asset is present in runtime or evidence outputs.
- Portrait, desktop, and landscape use the exact C5 camera records and explicit right-handed `+Y`-up basis in `docs/workstreams/temple-tr4-coordination/TR4_VISUAL_CONTRACT.md`. Their analytic horizon is near `.23H`; portrait proves runner center `.61-.72H`, desktop/landscape `.62-.76H`, portrait bottom road width `>=.74W`, desktop/landscape `>=.44W`, frozen `Z=-120m` far-route width `.06-.19W` portrait / `.015-.08W` desktop-landscape, bottom/far-route width ratio `>=2.5`, correct top-left ordering `runner > beam > ring > column > gap`, and distinct near/mid/far canyon layers.
- The causeway has real thickness, broken lips, undercuts, strata, buttresses/recesses/rubble, and at least six deterministic module signatures. Flat water, full-width walls, repeated rock corridors, thin road planes, and featureless strips are hard failures.
- Sandstone, basalt, Tide Scar, coral mineral, cloth, skin, leather, and rock armor differ by surface response. C5 beauty uses AgX / Medium High Contrast, a warm key with surface-to-light vector `(-.51966,.77949,.34977)`, an opposite cool fill `(.48019,.62025,-.62025)`, an explicitly aimed contact bounce, world `#6E8294` strength `.55`, and fog `#9AA7A8` density `.0035` / anisotropy `.18`. Static fog transmittance must be at least `.90` at `20m`, between `.55-.72` at `120m`, and at least `.12` at `520m`; no fog card or shadowing panorama cap is allowed.
- Courier body parts remain connected but non-intersecting across eight gait phases, jump, slide, stumble, and failure. Ground/contact error is `<=.03m`; detached limbs, floating supports, z-fighting, coat/limb penetration, hidden gap floors, or camera near-plane clipping fail.
- The pursuer is required in `ready`; required in `running` only while `elapsedTicks < 54 AND distance < 6.0m`; hidden at tick `54` or distance `6.0m` and throughout later running/close-pressure/milestone/hazard-preview/pause; and required throughout every `game-over`. Hidden snapshot fields are null and `visible=false`. Canonical `chaseGap` and capture behavior remain unchanged.
- `beam`, `ring`, `column`, `gap`, and turn silhouettes retain the exact canonical action and collision semantics while using the original TR4 mineral-causeway models. Their visual bounds cannot invent a false safe lane or block a valid one.
- The optimized asset pack retains all nine required semantic roots and passes GLB validation after optimization. Visible runtime budgets are `<=150k/100k` desktop/mobile triangles, `<=60/45` draw calls, `<=38/18 MiB` decoded textures, and zero console/WebGL errors.
- One Blender 4.5.5 process emits exactly the 20 ordered diagnostic PNGs and at most one evaluator described by `TR4_PREFLIGHT_SCHEMA.md` plus the active diagnostic authorization, followed by manual review of every exact complete set. C5 keeps global beauty luminance `p50>=.12`, `p95>=.55`, near-black pixels `<10%`, and route ROI `p50>=.25`; additionally the runner beauty ROI has `p50>=.12`, closeup pursuer ROI has `p50>=.08` and `p95>=.20`, the road-normal median encodes `+Y` (`G>=240`, `R/B=112-144`), linear depth has at least 64 distinct foreground values with runner-to-gap distance increasing, and pursuer pixels are zero in all three running profiles. Passing these gates cannot override a manual `BLOCKED` verdict for low-quality modeling, unreadable subjects, weak depth, reversed composition, or clipping.
- C4 is an immutable failure baseline, not visual evidence: it wrote 20 PNGs but did not run the evaluator; manual inspection found a rolled composition, 71-93% near-black beauty pixels, no readable far-horizon hierarchy, a reversed/thin Tide Scar, primitive hazards and courier, and a closeup pursuer that reads as a black blob. C5 may prove orientation and illumination only; unchanged geometry can still be manually blocked and cannot be exported.
- C5 is also immutable failed evidence, not a render: its sole process stopped in canonical preflight ingestion on an insertion-order/key-set mismatch, produced zero PNG, and skipped the evaluator. A later ID may correct that validator predicate only; no C5 output may be reused or described as image evidence.
- C6 is immutable `DIAGNOSTIC_BLOCKED` evidence. Its sole Blender process returned `0` and wrote 20 PNGs, but runner stopped before evaluator when two valid landscape near-zero axis angles (`2.1073424255447017e-08` recorded and `2.580956827951785e-08` recomputed) were compared by direct radians at `1e-12`; their difference is `4.736144024070833e-09` and both pass the actual `1e-5` alignment gate. Independent inspection is also `MANUAL_BLOCKED`: beauty is mostly black, route/canyon/characters/hazards remain blockout primitives, the Scar loop is cropped, and linear depth is visually white. No C6 pixel, technical, or manual result authorizes export or runtime.
- C7 is an authorized substantive reconstruction, not a technical retry. It must preserve the exact camera records while changing the faulty angle-agreement predicate to cosine-domain agreement, remove the black world-volume failure, construct real road/canyon/character/hazard geometry, connect procedural material coordinates, bind the exact Tide Scar loop as actual world geometry with identity transforms, keep its full tube visible and outside the safety corridor, and emit bounded visible-depth passes. Source work is exact-path checkpointed; the one diagnostic process remains gated by both source commits and a green non-writing dry preflight.
- C7 manual review is binding in this order: camera/horizon; road macro/medium structure; canyon depth and negative spaces; runner/hazard silhouettes and supports; pursuer anatomy and separation; PBR/material/light/fog; Tide Scar loop; normals/depth/masks. Repeated primitives, a flat strip, wall corridor, cropped Scar, black beauty, white depth, unreadable anatomy, floating support, z-fighting, or any interpenetration is `MANUAL_BLOCKED` even when every numeric gate passes.
- C7 diagnostic evidence proves the ordinary-running pursuer is absent and the game-over bookend model is present/readable. Opening visibility, exact tick `53/54`, distance `5.99/6.00m`, pause hiding, and every game-over failure branch remain deferred to targeted runtime tests and final browser evidence; they cannot be claimed from the fixed 20-image diagnostic.
- Final browser evidence uses real public commands and fixed ticks, records one canvas/zero gameplay DOM entities, hashes screenshots, proves the exact four HUD values, and includes opening/ordinary-running/game-over lifecycle records plus all four hazard actions.

## TR3-005C D4 development gate

- Runtime profiles classify landscape first (`height <= 520 && aspect > 1.5`), then portrait (`aspect < .72`), then desktop, with frozen FOV `46/40/43`. Speed must not alter FOV.
- The approved D4A environment selects exactly one pre-upload desktop/mobile derivative set. Capture asserts exact files: desktop sandstone/basalt/panorama 1024/1024/2048x1024 plus shared coral, or mobile sandstone/basalt/panorama 512/512/1024x512 plus shared coral. Desktop `22.667 MiB` is within `38 MiB`; mobile/low-GPU `6.667 MiB` is within `18 MiB`; all selected textures release on destroy. Albedo/panorama are sRGB; coral mask is `NoColorSpace`.
- Real-runtime development records at 1440x900, 390x844 normal/close, 844x390, and desktop column must report profile/FOV, camera pitch/horizon/vanishing point/bottom-road width/runner band, current asset tier/exact request set, texture estimate, one canvas, zero gameplay DOM, zero overflow/errors, and renderer calls/triangles including all three shadow passes.
- D4 road/canyon proof requires continuous irregular deterministic deck caps, attached downward cliff aprons, occupancy-clipped outer teeth, sparse outer-lip coral, visible far/mid/near canyon haze, and a right-edge analytic scar. Renderer-only deck/hazard/gap masks clip scar geometry before render: a gap removes only its local span, unresolved hazard overlap is zero, and each scar segment reports a clipped polygon/DPR-outward pixel bounds/visible area rather than a global AABB.
- Each non-capture pursuer record has positive clipped bounds and `pursuerGapPx >= max(6, round(.015 * viewportHeight))`; HUD, runner, pursuer, hazards, scar, and milestone do not overlap. Capture remains the sole exception.
- Development budgets are `<=46` desktop calls, `<=38` mobile calls, `<=190k` desktop triangles, `<=115k` mobile triangles, and p95 `<12ms`. These gates do not replace the later final TR3 matrix or candidate verification.

- Final verification: `npm.cmd run typecheck`, `npm.cmd run test` (11 files / 47 tests), and `npm.cmd run build` passed. The build's only advisory is Vite's non-blocking 500 kB chunk warning.
- Official Chrome 150.0.7871.115 evidence pass produced 23 records and 19 screenshots. Every capture recorded one canvas, zero gameplay DOM entities, no horizontal overflow, zero console/page errors, zero context losses, and render budgets no higher than 56 draw calls / 9,040 triangles.
- Exact HUD comparison passed for every capture. The 250 m milestone record has replay hash `78bd1dc3`, score 5,101, distance 250.0899 m, flow 2, one shard, and a visible `250 m` callout.
- The public-command close-chase record has replay hash `fa85830e`, canonical `chaseGap` 1.194 m, and pursuer clipped visible area 64,374.2 CSS px². Beam/ring/column/gap previews expose matching canonical kinds and positive clipped areas of 18,510.5 / 25,497.2 / 2,952.2 / 29,607.6 CSS px².
- Desktop and mobile scene-preparation p95 values are both 0.10 ms, within the 8 ms and 12 ms limits. Keyboard and DPR3 CDP touch evidence each show one semantic input event.
- Evidence manifest: `docs/qa/temple-browser-evidence.json`; reviewed captures: `docs/screenshots/temple/final/milestone.png`, `docs/screenshots/temple/final/chase-close.png`, `docs/screenshots/temple/final/gap-preview.png`, and `docs/screenshots/temple/final/ring-preview.png`.

TR1 evidence remains historical only; this candidate's counts, screenshots, command traces, and hashes are the sole TR2 evidence.

Independent QA accepted candidate `c5b3db041175c19c71bd0086baf1e034fc97caf0` in log-only commit `b974810fc4b0ba93fb5ed7d6012e22c67b0606a5`. QA reproduced clean install, typecheck, the complete 11-file / 47-test suite, and build; matched all 19 PNG hashes; and independently audited the 23 structured browser records, rules, public-command traces, canonical HUD, pursuer visibility, obstacle bounds, cleanup, input, and reduced-motion behavior. Its isolated fresh-capture attempt generated no artifacts after one safe retry; that environment-only limitation is recorded in the QA log and is not presented as fresh browser evidence.

Acceptance freezes this commit as the stable TR2 rules/engine baseline. It does not approve the separate visual-restart design work or authorize production visual changes.

## TEMPLE-TR3-A3 IN PROGRESS — not integrated

A3 supplies no runtime acceptance evidence. It is one deterministic offline Blender clay proof for structural composition only: the required source geometry, metadata, verifier evidence, portrait/desktop/closeup images, and mandatory manual review must remain outside the game runtime. A3 preserves canonical rules, replay hashes, renderer/UI behavior, and all existing browser evidence. It stops before final materials, GLB/KTX2 delivery, runtime/browser capture, candidate commit, push, or independent QA regardless of a clay gate pass.

## TEMPLE-TR3-A4 IN PROGRESS — not integrated

A4 supplies no runtime acceptance evidence. It is one deterministic offline Blender 4.5.5 clay correction of A3 camera framing, pursuer silhouette/transform, and ring/support readability only, with one portrait/desktop/closeup batch and one deterministic/manual structural gate. It preserves all A3 route/canyon/material/Tide Scar evidence and every runtime, browser, candidate, commit, push, and QA boundary; no final materials, export, optimization, or integration follows this batch.

## TEMPLE-TR3-A5 acceptance contract - offline proof only

A3 and A4 are closed **BLOCKED**. A5 is the sole authorized replacement composition proof and supplies no runtime, candidate, or final visual acceptance evidence. Exactly one Blender 4.5.5 process generates the same chase state as portrait 540x960, desktop 960x540, landscape 844x390 beauty/object-ID/road-mask/depth, and closeup 640x480 beauty. Exactly one evaluator follows, then four beauty images are manually inspected once. No retry, export, texture, GLB/KTX2, browser, build, commit, push, or QA work follows.

Source and provenance must compare exact A3/A4 inputs, preserve A4 failures as baselineFailures, and preserve seed 270803, the fixed six-root order, clay-only values, 16/17/125.949m/120.494deg/5.95m/.68 route facts, canyon 6/10/4 plus three portrait openings/near-wall ceiling/no continuous wall, editable clipped right-edge Tide Scar, and <=45,000 triangles. Geometry must prove 16 decorated modules, >=32 attached side fragments, signature run <=2, 20 unique canyon signatures, no continuous wall, a route-frame quadruped, and one two-support deck-contacting arch with real opening.

Binding raster/mask gates are portrait courier x=.45-.55,y=.60-.68; pursuer x=.43-.57,y=.74-.83, overlap >=.045W, gap .020-.075H, .02 containment, width >=32px; closeup pursuer contained and >=48px; desktop/landscape A5 screen bands; and contained hazard height/opening >.15H/.10W portrait, >.20H/.09W desktop, >.22H/.11W landscape. Tide Scar proof uses the actual editable curve/spline, has two road-right-third runs, and intersects no courier/pursuer/hazard mask. Hero frames require global p50>.12, p95>.55, <=10/255 <10 percent, road ROI p50>.25, positive non-black semantic ROIs, no fog card/panorama cap/full-width fog step, non-contiguous visible near/mid/far masks, and at least two occlusion boundaries.

The evaluator emits READY_FOR_VISUAL_REVIEW only if every source, deterministic, raster, and depth gate passes; any failure is BLOCKED and it cannot claim final visual acceptance. Manual detection of a blockout, featureless route, or low-poly strip wall is BLOCKED. A5 must not modify or integrate any runtime, UI, core, rules, package, config, browser, or non-A5 asset path.

## TEMPLE-TR3-A6 preflight acceptance boundary — no render

A6 is not browser or runtime QA and provides no product acceptance. It is a coordinator-reviewable, pure-data prerequisite for a later offline scene slice. Its result is `READY_FOR_A6_IMPLEMENTATION` only when every compatibility and construction check in `docs/workstreams/temple-a6-preflight/A6_PREFLIGHT_CONTRACT.md` and `A6_COMPOSITION_RECONSTRUCTION.md` is green; otherwise it is `BLOCKED`. Neither result authorizes Blender, a render, export, runtime integration, candidate, commit, or QA.

Required preflight checks include: A3/A4 source hashes and schemas; A4-only complete clay material values; no A5 metadata reconstruction; immutable route/root/Tide Scar facts; frozen profile screen/HUD-safe bands; central corridor chase ordering; three road cross-section event types with preserved `.68` corridor; three canyon depth layers without slab-wall repetition; grounded route-frame pursuer proof; readable supported-arch dimensions; and editable Tide Scar polygon exclusions. A missing key, unknown schema version, non-finite number, dynamic lookup after input normalization, or any threshold regression is an immediate `BLOCKED` result.
