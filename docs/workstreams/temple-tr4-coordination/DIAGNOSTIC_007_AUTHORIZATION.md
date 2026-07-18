# TEMPLE-TR4 diagnostic 007 contract review request

Status: **DRAFT / CONTRACT REVIEW REQUESTED — NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

This document is a proposed C7 overlay on the immutable C1 schema and the consumed C2-C6 authorizations. It does not authorize a source edit, diagnostic directory, Blender process, evaluator, render, export, runtime integration, browser capture, test, build, commit beyond coordinator documentation, or push. An independent read-only review must return `READY_FOR_DIAGNOSTIC_007_CONTRACT`, after which the coordinator must record a separate explicit authorization before the asset writer starts.

## Frozen evidence and baseline

- baseline: `ecd5de640362a6e30c5d0157ecd1590be7673318`;
- frozen inherited-backlog anchor: `52ae9ae631fa3761f8f8737978af1840ba2df8a4`;
- C1-C6 plus both probes are immutable; C6 contributes 27 files and the older diagnostic/probe set contributes 51 files, for 78 frozen files total;
- C6 remains `DIAGNOSTIC_BLOCKED; MANUAL_BLOCKED`. Its 20 PNGs cannot be rerun, reused as C7 output, deleted, re-evaluated, or described as acceptance evidence;
- the five backup/cache paths listed in `BACKLOG_SPLIT_PLAN.md` remain untracked, untouched, and never-stage.

## C7 identity and closed output set

- schema ID remains `tide-relay.temple-tr4.asset-preflight`;
- schema version is integer `7`; contract version is `TEMPLE-TR4-C7`;
- diagnostic root is exactly `docs\workstreams\temple-tr4-asset\diagnostic-007`;
- output prefix is exactly `tr4-diagnostic-007-`;
- gameplay scene ID is `tr4-diagnostic-running-007`; bookend scene ID is `tr4-diagnostic-game-over-007`;
- the construction hash must be new and must cover every C7 geometry, node-graph, light, compositor, depth, semantic-root, collision, camera, and output record;
- output order, profiles, passes, and dimensions remain exactly the C1 order: four profiles `portrait,desktop,landscape,closeup`, each with `beauty,object-id,road-mask,normal,linear-depth`, for exactly 20 PNGs named `tr4-diagnostic-007-{profile}-{pass}.png`;
- all four frozen camera positions, targets, up vectors, FOV, near/far, lens shifts, projection matrices, view matrices, and analytic screen gates remain unchanged.

No C7 output path may exist before the authorized runner completes its in-memory checks. A pre-existing root, extra output, changed camera, changed output order, unchanged C6 construction hash, or technical-only predicate rerender is `PRECHECK_BLOCKED`.

## Stable camera evidence predicate

The camera construction and generator's recorded-axis calculation remain valid. Runner and evaluator replace only the unstable direct-radian equality comparison:

1. require recorded axis angle `<=1e-5`;
2. require independently recomputed axis angle `<=1e-5`;
3. require `abs(cos(recorded)-cos(recomputed))<=1e-12`;
4. retain every determinant, basis, view-matrix, projection, lens-shift, finite-value, and screen-order gate.

A non-writing dry predicate test must accept the frozen C6 landscape pair `2.1073424255447017e-08` / `2.580956827951785e-08` and reject an injected sample with an axis angle greater than `1e-5`. The dry test may not import `bpy`, create `diagnostic-007`, launch Blender, invoke the evaluator, or mutate evidence.

## Mandatory substantive reconstruction

C7 is not a validator retry. Before its sole render, the new construction hash must prove all of these authored changes:

- **Causeway:** rebuild the road cap as a subdivided irregular warm-sandstone surface with real thickness, fractured lips, darker break faces, undercuts, side aprons, strata, cracks, dust, contact shadow, and rubble. At least six deterministic macro signatures remain, with no signature repeated more than twice. A vista bend may begin only beyond the frozen gap proof distance.
- **Canyon:** replace the repeated column corridor with layered ridge, terrace, ledge, recess, and overhang meshes. Near/mid/far bands retain at least `8/10/12` unique signatures, three negative spaces, two occlusion boundaries, asymmetric skylines, and monotonic atmospheric loss. No visible flat water band, wall slab, panorama cap, or corridor repetition is allowed.
- **Courier:** retain named articulated parts while replacing joined primitive readability with modeled torso, head, clothing, hands, legs, feet, and split coat tails. Eight gait phases plus jump/slide/stumble/failure must keep non-adjacent parts disjoint, feet grounded within `.03m`, silhouettes readable, and contact shadows present.
- **Bookend pursuer:** model separated pelvis/rib/shoulder plates, neck, head, jaw, four upper/lower limbs, four paws, and a restrained coral dorsal seam. It appears in the opening state and game-over closeup only, remains absent from ordinary-running profiles, and cannot read as a black blob. In capture framing the runner and creature body cores remain separated while forelimbs may bracket the runner without intersecting it.
- **Canonical hazards:** keep simulation and collision rules unchanged. `beam` becomes the grounded Fault Lip jump threshold; `ring` the two-supported Coral Throat slide arch with true clearance; `column` the single-lane Basalt Splitter; `gap` the genuinely missing Tidebreak span; turn the route-ending Sundered Elbow. Bases embed `0.08-.15m`, visible/proxy discrepancy remains `<=.06m`, no co-planar faces exist, and no visual part invents a false safe or blocked lane.
- **Tide Scar:** remain editable curve geometry. The longitudinal line stays outside `X=2.92m`; the near loop is moved ahead of the runner into the supported right shoulder, wholly visible in portrait, outside the safety corridor, clipped against hazards/gaps/actors, and never baked into a texture or UI strip.

Public gameplay sources inform only generic turn/jump/slide/gap/lane-readability grammar. No commercial frame, name, logo, character, creature, road mesh, texture, UI, sound, exact obstacle arrangement, or trade dress may enter C7.

## Procedural PBR and atmosphere repair

- No external texture file is allowed. Each sandstone, fresh-break, basalt, strata, cloth, leather, and rock-armour node graph explicitly connects Object or Generated coordinates through Mapping into bounded macro and micro Noise/Voronoi fields, colour ramps, roughness modulation, and bump. Every node link and scale is serialized in construction metadata.
- Procedural surface response supplements authored macro/medium geometry; it cannot replace fractures, strata, ledges, plates, limbs, or supports.
- The raw beauty scene uses Principled BSDF materials, the frozen warm key/cool fill/contact bounce, AgX `AgX - Medium High Contrast`, exposure `0`, and world surface `#6E8294` at strength `.55`. World volume is disabled.
- The beauty compositor uses rendered visible depth to compute `T(d)=exp(-.0035*d)` and mixes fog `#9AA7A8` by `1-T`; background is the same fog colour. Fog cards, panorama caps, emission lift, exposure lift, and pixel-threshold shortcuts are forbidden.

## Visible-depth repair

The C1 far-plane-normalized depth mapping is superseded only for C7:

- portrait/desktop/landscape ceiling: `160m`; closeup ceiling: `80m`;
- foreground value: `round(65535 * .94 * clamp((distance-near)/(ceiling-near),0,1))`;
- true background: `65535`;
- at least 64 distinct foreground values per profile;
- foreground `p10 < p50 < p90 < 62000`;
- ordinary-running semantic median depth strictly increases `runner < beam < ring < column < gap`;
- every pass remains PNG16 with its exact camera matrix and dimensions.

A nearly uniform white depth image, background/foreground ambiguity, inverted ordering, eight-bit truncation, or fewer than 64 foreground values is `DIAGNOSTIC_BLOCKED`.

## Manual visual review

Numeric or pixel success can emit at most `READY_FOR_MANUAL_REVIEW`. The independent reviewer must inspect all 20 outputs, in this order:

1. global camera, portrait hierarchy, horizon, vanishing depth, and road bands;
2. road primary mass and medium fractures/strata/undercuts/rubble;
3. canyon near/mid/far layers, negative spaces, occlusion, and atmospheric falloff;
4. courier and hazard silhouettes, supports, contact, and canonical clearance;
5. closeup pursuer anatomy, grounded limbs, runner separation, and no clipping;
6. PBR material variation, warm/cool light, contact shadows, and fog integration;
7. complete editable Tide Scar longitudinal path and near loop;
8. object-ID, road-mask, normal, and linear-depth correctness.

Any flat strip road, low-poly blockout, repeated primitive, wall corridor, black beauty frame, white depth frame, cropped Scar loop, unreadable anatomy, floating/detached support, hidden gap floor, z-fighting, interpenetration, near-plane clipping, or material-only detail returns `MANUAL_BLOCKED`. Pixel gates never override that result.

## Checkpoint and execution order

1. **C7-D1 coordinator contract:** this review-request commit only. No implementation or process launch.
2. **Independent contract review:** read-only against the exact C7-D1 SHA and these coordinator documents. It returns `READY_FOR_DIAGNOSTIC_007_CONTRACT` or exact P0/P1 findings; it cannot edit production or evidence.
3. **C7-D2 coordinator authorization:** only after a ready verdict, a separate docs-only commit records execution authority and exact accepted review provenance.
4. **C7-T1 generator reconstruction:** the single asset writer changes exactly `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`; AST/static checks only. Its size is an explicit atomic exception because this self-hashed scene generator cannot be partially staged without falsifying construction provenance.
5. **C7-T2 evidence predicate/depth evaluation:** the same writer changes exactly `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py` and `evaluate_tide_scar_tr4_pack.py`; AST/static checks plus the non-writing positive/negative dry predicate test only.
6. **Authorized dry preflight:** only after C7-T1 and C7-T2 are committed and hashes are stable. It must stop before Blender on any mismatch.
7. **C7-E1 diagnostic evidence:** one Blender 4.5.5 background process, exactly 20 PNG writes, then at most one evaluator. New `diagnostic-007/**` plus its exact ignored `blender.log` form a separate evidence commit. No retry.
8. **C7-V1 independent visual review:** docs-only `TR4_DIAGNOSTIC_REVIEW.md` and visual-review `THREAD_LOG.md`; no repair or rerender.

Every asset step appends `docs/workstreams/temple-tr4-asset/THREAD_LOG.md`. Every commit stages exact paths and separates coordinator docs, source, generated evidence, and independent review. Export, runtime adoption, browser work, final typecheck/full Vitest/build, independent candidate QA, changelog acceptance, and push remain blocked regardless of C7 numeric success.
