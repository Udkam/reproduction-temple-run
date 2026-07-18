# TEMPLE-TR4 visual reconstruction contract

Status: **C7 CONTRACT READY; EXACT SOURCE IMPLEMENTATION AUTHORIZED.** Independent review of corrected contract `614d280` returned `READY_FOR_DIAGNOSTIC_007_CONTRACT`. The single asset writer may execute C7-T1/T2 only; the diagnostic process remains blocked until both source checkpoints and the non-writing dry preflight pass. This contract does not accept any A3/A4/A5/A6/C1-C6 proof, and it does not permit those historical files to be rewritten.

Diagnostic status: C1/`001` through C6/`006` plus both probes are immutable. C4 wrote all 20 PNGs but failed its scene-metric runner gate and independent manual review. C5 stopped before scene construction with zero PNG because generator validation compared a canonical JSON child object's insertion order instead of its exact key set; evaluator was not invoked. C6 wrote all 20 PNGs but stopped before evaluator when runner directly compared two valid near-zero landscape axis angles at `1e-12`; independent inspection also returned `MANUAL_BLOCKED` for black beauty frames, a flat strip road, repeated low-poly canyon masses, primitive semantic models, a cropped Scar loop, and white depth output. `DIAGNOSTIC_006_AUTHORIZATION.md` is consumed historical authority only. Backlog recovery completed at `ecd5de640362a6e30c5d0157ecd1590be7673318`; `DIAGNOSTIC_007_AUTHORIZATION.md` is the active exact source/process overlay. Export and runtime remain blocked.

## Source boundary

- Approved visual north star: temporary local PNG `C:\Users\ALEXCH~1\AppData\Local\Temp\codex-clipboard-ca70825b-99a6-4290-8307-4d90b2077d48.png`, `941x1672`, SHA-256 `8fc0c6a7f7fc8d7e5b65fd3d256dee33ccfeede0e4aba4a04657c66a93e33074`.
- Gameplay reference: `https://www.bilibili.com/video/BV1ce41137n2/` and other player footage may inform only timing, reaction grammar, camera readability, and obstacle categories.
- No image frame, mesh, texture, character, UI, logo, trade dress, or proprietary content from a commercial game or player video may enter the repository or runtime.
- The reference PNG remains external and non-runtime. If it disappears, the user must reattach it; no substitute reference may be invented.

## Composition hierarchy

1. A narrow, broken but continuous warm sandstone causeway begins below the camera, occupies most of the lower portrait frame, bends with a readable centerline, and recedes into a fogged canyon horizon.
2. Near, mid, and far basalt masses are separate asymmetric silhouettes with negative spaces, scale changes, occlusion, saturation loss, and atmospheric falloff. A flat water band, full-width wall, panorama cap, or repeated rock corridor is a hard failure.
3. The courier is small but immediately readable near the lower center. The route, next hazard, and turn remain legible before surface detail.
4. A procedural chalk-white Tide Scar follows the road longitudinally and may form one restrained near-camera loop. It is editable world geometry, never a baked line or UI stripe.
5. Coral/mineral red appears only in broken lips, deposits, hazard cuts, and the pursuer dorsal seam.

## Frozen camera records

World convention: right-handed, metres, `+Y` up, course forward `-Z`; road top and the runner ground socket are `Y=0`, and the runner root is `(0,0,0)` in the diagnostic record. Camera records are runner-relative before turn yaw. Vertical FOV is degrees. Projection uses WebGL NDC, clips against near/far planes, maps top-left to normalized `(0,0)`, and rounds evidence outward to 0.01 CSS pixel. `lensShiftY` is assigned directly to Three.js `projectionMatrix.elements[9]`. Blender derives `Camera.shift_y` deterministically from its calculated zero/unit-shift projection response as specified by the preflight schema, then must match the normalized target element within `5e-7` before the first render.

C5 does not use `to_track_quat`. For every profile, `forward=normalize(target-position)`, `worldUp=normalize(up)`, `right=normalize(forward.cross(worldUp))`, and `trueUp=normalize(right.cross(forward))`; Blender rotation is `Matrix((right,trueUp,-forward)).transposed().to_quaternion()`. All basis vectors are finite/unit within `5e-7`, all pairwise dot products are `<=5e-7`, determinant is `+1` within `5e-7`, and the actual evaluated camera inverse/world view matrix matches the pure-Python canonical 16-value view matrix within `5e-6`. The explicit record `up` is binding and cannot be ignored or replaced by Blender's Z-up helper convention.

| Profile | Resolution | Camera position `(x,y,z)` | Look target `(x,y,z)` | Up | FOV | Near/Far | Lens shift Y |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| portrait | `540x960` | `(0,6.20,15.20)` | `(0,.55,-16.80)` | `(0,1,0)` | `40` | `.08/520` | `-.055` |
| desktop | `960x540` | `(0,6.06,13.60)` | `(0,.60,-13.30)` | `(0,1,0)` | `43` | `.08/520` | `-.025` |
| landscape | `844x390` | `(0,6.15,12.80)` | `(0,.55,-12.56)` | `(0,1,0)` | `46` | `.08/520` | `-.020` |
| closeup | `640x480` | `(0,5.40,9.80)` | `(0,1.15,-3.40)` | `(0,1,0)` | `48` | `.05/180` | `0` |

Portrait gates: horizon `y=.17-.31H` with analytic target near `.23H`, runner center `y=.61-.72H`, bottom road width `>=.74W`, road width at the projected frozen far-route point `(0,0,-120)` `.06-.19W`, bottom/far-route road-width ratio `>=2.5`, and at least three non-contiguous depth layers. Desktop/landscape require runner center `.62-.76H`, bottom road width `>=.44W`, far-route width `.015-.08W`, the same ratio gate, and a visible far silhouette that does not fill the width. The analytic horizon remains a camera-direction gate and is not a road-mask sampling row. In top-left coordinates every ordinary-running profile has `runnerY > beamY > ringY > columnY > gapY`, runner head above feet, and the Tide Scar at the runner-depth test point strictly right of the route centre. Closeup contains the pursuer with `.02` normalized margin and width `>=48px`.

## Modeling and material contract

### Causeway

- Gameplay top width is `6.40m`, spanning local `X=[-3.20,3.20]`. Canonical lane centres are `-2.35/0/2.35m`; the collision envelope is `+/-0.42m`, and the decoration-free visual safety corridor is `X=[-2.92,2.92]`, including `.15m` padding beyond the outer collision envelopes. Decorative geometry may never intrude into that safety corridor.
- Every module has a real top, `0.55-1.20m` structural thickness, `2.5-8m` downward side mass, broken lips, undercuts, and at least two strata/debris events. It cannot be a thin plane or an unbroken rectangular extrusion.
- Module lengths are `6-11m`. At least six signatures combine terrace, fracture, buttress, recess, collapsed lip, and rubble-cluster events; no signature repeats more than twice consecutively.
- Cracks, edge wear, dust, aggregate, and stone response are geometry, normal/roughness response, or bounded decals. Texture noise alone cannot substitute for medium-scale structure.
- C7 rebuilds the cap as a subdivided irregular surface with real fracture boundaries rather than a planar strip. A far-vista bend may begin only beyond the frozen `gap` proof distance, so it cannot displace or hide the straight canonical near-course hazards used by the diagnostic.

### Canyon

- Near, mid, and far clusters use at least `8/10/12` unique signatures. Each cluster has ledges, strata, overhangs, recesses, and a broken skyline.
- No generic full-width water plane is visible from a frozen camera. A dark abyss surface may exist below sightlines only to receive fog/reflection.
- Near silhouettes overlap the route in screen space without entering the canonical corridor; mid/far silhouettes lose contrast and saturation monotonically.

### Materials and light

- Sandstone: warm albedo family around `#d8b98c`, roughness `.72-.94`, visible normal/aggregate response, darker fresh breaks, and dust accumulation.
- Basalt: blue-charcoal family around `#1b2935`, roughness `.64-.90`, non-crushed highlights, separate edge/strata response.
- Tide Scar: chalk `#f2ead7`, roughness `.82-.96`, no emissive glow, width `.075-.11m`, with the main spline centre `X=3.00-3.06m` (`.14-.20m` inward from the true right lip). Its inner edge remains outside `X=2.92m`. One separate editable near loop may occupy the contract's widened right shoulder at `X=3.00-4.30m`; it remains wholly outside the gameplay safety corridor and does not alter the canonical deck width.
- Coral/mineral deposit: `#b44a38`, sparse coverage below `4%` of road pixels.
- Beauty uses AgX with `AgX - Medium High Contrast`, exposure `0`, gamma `1`, and no emissive/exposure shortcut. The warm key has source surface-to-light vector `(-.51966,.77949,.34977)`, energy `4.2`, color `#FFD7A3`, and shadows on; the cool fill source vector is `(.48019,.62025,-.62025)`, energy `1.1`, color `#7EA6C4`, and shadows off. Each source vector is finite and is normalized before use; each normalized record is unit within `5e-7`, has `Y>=.75/.55` respectively, and the X signs oppose. A sun's actual local `-Z` direction must align with the negative normalized surface-to-light vector within `1e-5` radians. The contact bounce remains a shadowless `430`-energy, size-`9` disk at `(0,7.5,4.0)`, explicitly aimed from local `-Z` at road target `(0,0,-4.0)` within `1e-5` radians.
- Every C7 stone/cloth/armour procedural material must explicitly connect Object or Generated coordinates through a Mapping node into bounded macro and micro Noise/Voronoi fields, then into colour-ramp, roughness, and bump response. An unconnected texture vector, constant-colour surface, external texture file, or noise-only substitute for geometry is a hard failure.
- Beauty world surface is `#6E8294` at strength `.55`; no world volume is used. The raw PBR scene remains AgX / Medium High Contrast at exposure `0`. The beauty compositor applies depth-derived Beer-Lambert atmosphere with `T(d)=exp(-.0035*d)` and mixes fog colour `#9AA7A8` by `1-T`; background uses the fog colour. Static transmittance must be `>=.90` at `20m`, `.55-.72` at `120m`, and `>=.12` at `520m` (nominal `.932/.657/.162`). There is no translucent fog card, panorama shadow cap, emission lift, exposure shortcut, or threshold lowering.

## Character contract

- Courier has separate pelvis, chest, head, upper/lower arms, hands, thighs, shins, feet, and split coat tails. Elbows, knees, feet, coat, and torso must not intersect in any run/jump/slide/failure pose.
- At gameplay scale the head/torso/limbs, forward lean, alternating gait, foot plant, and contact shadow must read in silhouette. Skin/cloth/leather/mineral-core differ by physical response, not color alone.
- The pursuer is an original rock-armored multi-limbed creature with readable head direction, shoulder mass, four grounded limbs, paws, separated body plates, contact shadow, and one restrained coral dorsal seam. It must not read as a black blob or joined primitives.

## Pursuer lifecycle

- `ready`: the pursuer is required and uses the opening pose.
- `running`: the pursuer is required only while `elapsedTicks < 54 AND distance < 6.0m`. The fixed 60 Hz canonical tick is the sole time source. At either boundary (`elapsedTicks >= 54` OR `distance >= 6.0m`) it is hidden.
- `paused`: the pursuer is always hidden, including a pause during the opening window.
- `game-over`: the pursuer is required for the entire state. `pursuer-caught` closes into the courier; gap/turn/obstacle failures keep it separated from the failed body and road geometry.
- Hidden means the scene root is not rendered, no projection search or placement error is executed, mist/dust owned by the creature is hidden, and snapshot position/bounds/area/gap are `null` with `visible=false`. Canonical `chaseGap` remains deterministic pressure data and may drive non-creature audio, vignette, dust, or camera cues only.
- QA proves the exact boundaries at ticks `53/54` and distances `5.99/6.00m`. Historical TR2/TR3 continuous-pursuer screenshot gates are superseded for TR4 presentation only.

## Trap grammar

Canonical event types and collision rules remain unchanged; only their original visual language changes.

| Canonical kind | Required action | TR4 original modeling language |
| --- | --- | --- |
| `beam` | jump | **Fault Lip / 断层门槛**: a fractured, grounded stone threshold with lifted strata, broken caps, dust, and readable top clearance |
| `ring` | slide | **Coral Throat / 珊瑚喉门**: a double-supported mineral arch/lintel with a real negative-space opening, never copied statues or fire gates |
| `column` | change lane | **Basalt Splitter / 玄武岩劈齿**: an asymmetrical grounded rock tooth with rubble and a lane-contained collision silhouette |
| `gap` | jump | **Tidebreak Gap / 潮裂断阶**: a genuinely missing causeway span with fractured near/far lips, visible thickness, abyss depth, and no hidden collision floor |
| turn window | turn | **Sundered Elbow / 断峡折角**: a route-end cliff and clearly authored outgoing branch; no decorative geometry may imply a false branch |

No three-lane pattern may obscure all valid responses, and decorative silhouettes cannot change canonical fairness.

Frozen visual clearances derive from the unchanged core constants: lane-specific collision proxies are centred on `-2.35/0/2.35m` and span `.84m`; visual lane blockers are at most `1.55m` wide and preserve at least `.15m` from the adjacent runner sweep. A beam top is `.68-.76m` above road top, below the canonical `.82m` jump-clearance threshold. A ring/lintel has a lowest solid face at `1.05m`, an authored slide-pose envelope no higher than `.90m`, and `.15m` visual clearance. A gap removes the actual deck for the canonical event length; it cannot be represented by an overlay.

## Anti-clipping gates

- All semantic parts have named ground/contact sockets and analytic bounds. Ground contacts differ from the road surface by at most `.03m`.
- Runner self-intersection tests cover eight gait phases plus jump, slide, stumble, and failure poses. Dynamic limb/coat AABBs may touch at joints but cannot overlap non-adjacent body parts.
- Hazard presentation bounds remain inside their canonical lane/all-lane footprint and preserve jump/slide clearances. Rubble and deposits stay outside the protected corridor.
- The Tide Scar is clipped against gaps, all unresolved hazard silhouettes, runner opening/ending bounds, and HUD-safe polygons before vertices are emitted.
- Camera near-plane clipping, detached limbs, floating supports, z-fighting, hidden gap floors, and road/canyon intersections are hard failures.

## Asset pack and evidence

Required semantic roots in both source and optimized GLB are exactly these nine top-level children of the glTF scene, in this order, with identity transform, metre units, and no optimizer-created replacement parent:

`TR4_Road_Modules`, `TR4_Canyon_Modules`, `TR4_Runner_Rig`, `TR4_Pursuer_Cinematic`, `TR4_Hazard_Beam`, `TR4_Hazard_Ring`, `TR4_Hazard_Column`, `TR4_Gap_Lips`, and `TR4_TideScar_Path`.

- Before any `bpy` import or Blender launch, one UTF-8 normalized input and metadata skeleton bind this contract version, reference hash, script hashes, camera matrices, construction hash, collision values, materials, roots, budgets, and exact output paths. The executable schema and rejection rules are binding in `TR4_PREFLIGHT_SCHEMA.md`.
- One low-resolution diagnostic is exactly one Blender 4.5.5 process and exactly 20 ordered PNG writes: four profiles in `portrait, desktop, landscape, closeup` order, each in `beauty, object-id, road-mask, normal, linear-depth` order. Portrait/desktop/landscape use the frozen ordinary-running record with no pursuer; closeup uses the frozen game-over bookend record so the pursuer model receives explicit visual and mask review. It then invokes the evaluator at most once. Missing, extra, pre-existing, duplicate, or out-of-order output is `BLOCKED`; there is no automatic retry. If the process leaves the exact complete 20-PNG set but the runner blocks before evaluator, the set is still frozen and receives independent manual review; an incomplete set does not.
- C7 linear depth is capped visible depth, not far-plane-normalized depth: portrait/desktop/landscape use a `160m` ceiling and closeup `80m`. Foreground maps `clamp((d-near)/(ceiling-near),0,1)*.94` to PNG16; true background is `65535`. Each profile has at least 64 distinct foreground values, foreground `p10<p50<p90<62000`, and median semantic distances strictly increase `runner < beam < ring < column < gap` for ordinary-running profiles.
- Manual inspection follows the fixed order: global camera/horizon; road primary and medium structure; canyon near/mid/far layers and negative spaces; runner/hazard silhouettes and physical supports; closeup pursuer anatomy and separation; PBR/material/light/fog response; the complete editable Tide Scar loop; normals/depth/masks. Flat water, repeated walls/primitives, featureless strip roads, cropped Scar geometry, black beauty, white depth, primitive-looking characters/hazards, weak material response, unreadable silhouettes, floating supports, z-fighting, clipping, or material-only detail is `MANUAL_BLOCKED`.
- Pack budget: unoptimized `<=150,000` triangles, optimized `<=110,000`, `<=10` shared materials, `<=8 MiB` optimized GLB. Runtime visible budget remains `<=150,000` desktop / `<=100,000` mobile triangles, `<=60/45` calls, and decoded texture memory `<=38/18 MiB`.
- The evaluator can emit at most `READY_FOR_MANUAL_REVIEW`. Only a coordinator-authored `docs/workstreams/temple-tr4-coordination/EXPORT_AUTHORIZATION.md` may open a separate export/optimization pass. That pass may write `docs/workstreams/temple-tr4-asset/export-001/**` and `src/assets/tide-scar-tr4/**`, producing `tide-scar-tr4-source.glb`, `tide-scar-tr4.glb`, and hash/validator manifests. Runtime integration starts only after both GLBs retain all nine exact roots and the coordinator records `ACCEPTED_FOR_RUNTIME_INTEGRATION`.

## Workstream boundaries

- Coordinator: `DESIGN.md`, `CURRENT_TASK.md`, `docs/rules/RUNNER_RULES.md`, `docs/qa/TEMPLE_ACCEPTANCE.md`, `docs/logs/CHANGELOG.md` only at final acceptance, and `docs/workstreams/temple-tr4-coordination/**`.
- Asset diagnostic writer: new `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`, `tools/temple-asset-pipeline/evaluate_tide_scar_tr4_pack.py`, `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py`, and `docs/workstreams/temple-tr4-asset/**` only. After a separate export authorization, the same writer may additionally create `src/assets/tide-scar-tr4/**`.
- Independent diagnostic visual reviewer starts after the runner stops whenever an exact complete 20-PNG set exists, regardless of whether the evaluator was invoked or passed. It may write only `docs/workstreams/temple-tr4-visual-review/TR4_DIAGNOSTIC_REVIEW.md` and `docs/workstreams/temple-tr4-visual-review/THREAD_LOG.md`; all asset, tool, contract, runtime, and evidence images are read-only. It inspects the four beauty frames and their bound masks/depth, and cannot repair or rerender. An incomplete set is not manually reviewed.
- Diagnostic C7 proves only ordinary-running pursuer absence and game-over bookend model presence. Opening visibility, tick/distance boundaries, pause hiding, and failure-branch lifecycle behavior are runtime/test/browser obligations after asset acceptance.
- Runtime remains blocked until the coordinator records the current SHA-256 and disposition of every inherited dirty path in `RUNTIME_ADOPTION.md` and records `ACCEPTED_FOR_RUNTIME_INTEGRATION`. Its exact files are `src/game/render/WorldRenderer.ts`, `WorldRenderer.test.ts`, `runnerRig.ts`, `runnerRig.test.ts`, `pursuerRig.ts`, `pursuerRig.test.ts`, `theme.ts`, new `tr4AssetPack.ts`/`.test.ts`, `tr4Environment.ts`/`.test.ts`, `tr4Hazards.ts`/`.test.ts`, `tr4Lifecycle.ts`/`.test.ts`, `src/App.tsx`, `src/styles.css`, `scripts/capture-temple-evidence.mjs`, and `docs/workstreams/temple-tr4-runtime/THREAD_LOG.md`. It may read but not write the accepted `src/assets/tide-scar-tr4/**` pack.
- Independent QA is read-only after a candidate SHA. No workstream may edit A3/A4/A5/A6 evidence or `src/game/core/**` / `src/game/runtime/**`.
