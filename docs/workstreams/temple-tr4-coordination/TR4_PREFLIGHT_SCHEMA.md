# TEMPLE-TR4 executable preflight and diagnostic schema

This file is the immutable C1 baseline first made normative for diagnostic `001`. Later diagnostic authorizations inherit every unchanged closed field and state their exact schema/ID/root/value deltas. C5 and C6 are frozen `DIAGNOSTIC_BLOCKED`; `DIAGNOSTIC_006_AUTHORIZATION.md` is the consumed historical overlay that governed the immutable 27-file C6 result. `DIAGNOSTIC_007_AUTHORIZATION.md` now proposes a schema-version-7 overlay, but its status is `CONTRACT REVIEW REQUESTED`: it is not accepted Blender input and creates no execution authority until an independent ready verdict and a separate coordinator authorization are recorded.

## Canonical JSON

- Schema ID: `tide-relay.temple-tr4.asset-preflight`; schema version: integer `1`; contract version: `TEMPLE-TR4-C1`.
- UTF-8 without BOM, one trailing LF, keys sorted lexicographically, separators `,` and `:`, `ensure_ascii=false`, and `allow_nan=false`.
- Every object rejects unknown keys. Every listed field is required. Numbers must be finite JSON numbers; dimensions/counts are integers; paths are normalized absolute Windows paths.
- SHA-256 is lowercase 64-character hexadecimal. Script hashes are calculated after the final script write and before the diagnostic directory exists. `constructionHash` is SHA-256 of the canonical `construction` object only.

The exact top-level fields are:

`schemaId`, `schemaVersion`, `contractVersion`, `seed`, `reference`, `tools`, `scripts`, `scene`, `cameras`, `construction`, `collision`, `materials`, `semanticRoots`, `budgets`, `outputs`, `constructionHash`, `verdict`.

Required records:

- `seed`: integer `1414090053`.
- `reference`: exact `path`, `width=941`, `height=1672`, and approved `sha256`. The runner rechecks existence, regular-file type, dimensions, and hash immediately before launch.
- `tools`: exact `blenderExecutable`, `blenderVersion="4.5.5 LTS"`, `pythonVersion`, and later export-only `gltfTransformVersion`/`ktxVersion` strings.
- `scripts`: exact absolute path and SHA-256 for generator, evaluator, and runner.
- `scene`: exact `gameplay` and `bookend` records. `gameplay` is `id="tr4-diagnostic-running-001"`, `status="running"`, `tick=240`, `elapsedTicks=240`, `distance=32.0`, `lane=0`, `posture="run"`, `gaitPhase=0.25`, `runnerRoot=[0,0,0]`, `pursuerPresent=false`, and ordered hazards `beam/ring/column/gap` at course distances `18/36/54/72m`. `bookend` is `id="tr4-diagnostic-game-over-001"`, `status="game-over"`, `tick=420`, `elapsedTicks=420`, `distance=63.0`, `failureReason="pursuer-caught"`, `posture="failure"`, `runnerRoot=[0,0,0]`, `pursuerPresent=true`, and `pursuerRoot=[0,0,2.40]`. Portrait/desktop/landscape bind `gameplay`; closeup binds `bookend`.
- `cameras`: the four exact profile records from `TR4_VISUAL_CONTRACT.md`, including aspect, vertical FOV, near/far, `lensShiftY`, view matrix, and projection matrix as 16 finite numbers each.
- `construction`: exact road/canyon/module/signature counts, metre dimensions, material parameters, light records, Tide Scar control points, runner part/contact records, hazard sockets, and pursuer part/contact records. No value is read dynamically after normalization.
- `collision`: `laneWidth=2.35`, `laneCenters=[-2.35,0,2.35]`, `laneTolerance=0.42`, `roadBounds=[-3.2,3.2]`, `visualSafetyBounds=[-2.92,2.92]`, `beamClearanceHeight=0.82`, `gapClearanceHeight=0.52`, `slideTicks=31`, `ringLowestSolidY=1.05`, `slidePoseMaxY=0.90`, and `visualPadding=0.15`.
- `materials`: exactly the named sandstone, fresh-break, basalt, basalt-strata, Tide Scar, coral mineral, skin, cloth/leather, and rock-armour records; total material count is at most ten.
- `semanticRoots`: exactly the ordered nine roots from `TR4_VISUAL_CONTRACT.md`; each record has `parent=null`, `translation=[0,0,0]`, `rotation=[0,0,0,1]`, and `scale=[1,1,1]`.
- `budgets`: exact source/optimized/runtime triangle, draw-call, material, GLB-byte, and decoded-texture ceilings from `TR4_VISUAL_CONTRACT.md`.
- `verdict`: only `READY_FOR_BLENDER` is accepted as Blender input. Other allowed values are `PRECHECK_BLOCKED`, `DIAGNOSTIC_BLOCKED`, `READY_FOR_MANUAL_REVIEW`, `MANUAL_BLOCKED`, `ACCEPTED_FOR_EXPORT`, `EXPORT_BLOCKED`, and `ACCEPTED_FOR_RUNTIME_INTEGRATION`.

## Closed construction object

`construction` has exactly these keys in canonical sort order: `axis`, `canyon`, `hazards`, `lighting`, `pursuer`, `road`, `runner`, `tideScar`, `unitMeters`. `axis` is `{"forward":"-Z","right":"+X","up":"+Y"}` and `unitMeters` is `1.0`.

`road` has exactly:

- `surfaceY=0.0`, `width=6.4`, `bounds=[-3.2,3.2]`, `visualSafetyBounds=[-2.92,2.92]`;
- `moduleCount=16`, `moduleLengthRange=[6.0,11.0]`, `thicknessRange=[0.55,1.2]`, `sideDepthRange=[2.5,8.0]`;
- `signatureOrder=["terrace-fracture","buttress-recess","collapsed-lip","strata-undercut","rubble-shoulder","split-ledge"]`, `maxConsecutiveSignatureRepeats=2`, `strataEventsPerModule=2`, `rubbleEventsPerModule=1`;
- `nearLoopShoulder={"rightOuterX":4.45,"zRange":[2.8,5.2]}`. This is decorative support outside the gameplay lip and never changes the `6.4m` canonical deck.

`canyon` has exactly `bandOrder=["near","mid","far"]`, `near`, `mid`, `far`, `negativeSpaceCount=3`, `occlusionBoundaryCount=2`, and `fullWidthWaterVisible=false`. Band records have exactly `count`, `absXRange`, `yRange`, `zRange`, `saturation`, and `contrast`, with values:

- `near={"absXRange":[8.0,16.0],"contrast":0.86,"count":8,"saturation":0.72,"yRange":[-8.0,10.0],"zRange":[-100.0,-10.0]}`;
- `mid={"absXRange":[18.0,34.0],"contrast":0.58,"count":10,"saturation":0.48,"yRange":[-12.0,18.0],"zRange":[-140.0,-20.0]}`;
- `far={"absXRange":[38.0,70.0],"contrast":0.30,"count":12,"saturation":0.24,"yRange":[-16.0,30.0],"zRange":[-180.0,-35.0]}`.

`tideScar` has exactly `mainWidthRange=[0.075,0.11]`, `mainCenterXRange=[3.0,3.06]`, `surfaceOffsetY=0.035`, `mainControlPoints`, `loopControlPoints`, `gapClipPadding=0.35`, and `hazardClipPadding=0.25`. Ordered `mainControlPoints` are:

`[[3.03,0.035,8.0],[3.05,0.035,0.0],[3.01,0.035,-10.0],[3.06,0.035,-22.0],[3.02,0.035,-36.0],[3.04,0.035,-52.0],[3.00,0.035,-70.0],[3.05,0.035,-92.0],[3.02,0.035,-120.0]]`.

Ordered `loopControlPoints` are a separate editable spline supported by the near right shoulder:

`[[3.00,0.035,4.00],[3.09,0.035,4.33],[3.33,0.035,4.56],[3.65,0.035,4.65],[3.98,0.035,4.56],[4.22,0.035,4.33],[4.30,0.035,4.00],[4.22,0.035,3.68],[3.98,0.035,3.44],[3.65,0.035,3.35],[3.33,0.035,3.44],[3.09,0.035,3.68],[3.00,0.035,4.00]]`.

`runner` has exactly `partOrder`, `contactSocketOrder`, `poseOrder`, `root`, `height`, `maxGroundError`, and `triangleCeiling`. Values are:

- `partOrder=["pelvis","chest","head","upperArm.L","forearm.L","hand.L","upperArm.R","forearm.R","hand.R","thigh.L","shin.L","foot.L","thigh.R","shin.R","foot.R","coatTail.L","coatTail.R"]`;
- `contactSocketOrder=["ground.foot.L","ground.foot.R","camera.target"]`;
- `poseOrder=["run.0","run.1","run.2","run.3","run.4","run.5","run.6","run.7","jump","slide","stumble","failure"]`;
- `root=[0.0,0.0,0.0]`, `height=2.32`, `maxGroundError=0.03`, `triangleCeiling=18000`.

`pursuer` has exactly `partOrder`, `contactSocketOrder`, `bookendRoot`, `height`, `maxGroundError`, and `triangleCeiling`. Values are:

- `partOrder=["pelvisPlate","ribPlate","shoulderPlate","neck","head","jaw","foreleg.L.upper","foreleg.L.lower","paw.L.front","foreleg.R.upper","foreleg.R.lower","paw.R.front","hindleg.L.upper","hindleg.L.lower","paw.L.rear","hindleg.R.upper","hindleg.R.lower","paw.R.rear","dorsalSeam"]`;
- `contactSocketOrder=["ground.front.L","ground.front.R","ground.rear.L","ground.rear.R","capture.target"]`;
- `bookendRoot=[0.0,0.0,2.4]`, `height=1.78`, `maxGroundError=0.03`, `triangleCeiling=24000`.

`hazards` has exactly `order=["beam","ring","column","gap"]` plus one record for each ordered kind. Every record has exactly `semanticRoot`, `action`, `collisionProxy`, `visualBounds`, and `socketOrder`:

- `beam`: root `TR4_Hazard_Beam`, action `jump`, proxy `{"height":0.82,"widthAll":5.84,"widthLane":0.84}`, visual `{"topYRange":[0.68,0.76],"widthLaneMax":1.55}`, sockets `["entry","apex.clearance","exit","ground.L","ground.R"]`;
- `ring`: root `TR4_Hazard_Ring`, action `slide`, proxy `{"laneWidth":0.84,"requiresSlide":true}`, visual `{"lowestSolidY":1.05,"openingHeight":0.90,"widthLaneMax":1.55}`, sockets `["entry","slide.clearance","exit","ground.L","ground.R"]`;
- `column`: root `TR4_Hazard_Column`, action `lane-change`, proxy `{"laneWidth":0.84}`, visual `{"widthLaneMax":1.55}`, sockets `["entry","safe.left","safe.right","exit","ground"]`;
- `gap`: root `TR4_Gap_Lips`, action `jump`, proxy `{"clearanceHeight":0.52,"lengthFromCanonicalEvent":true}`, visual `{"hiddenFloor":false,"lipDepthMin":0.55}`, sockets `["takeoff","apex.clearance","landing"]`.

`lighting` has exactly `worldColor="#425466"`, `worldStrength=0.22`, `key`, `fill`, `fogColor="#9AA7A8"`, and `fogDensity=0.016`. `key` and `fill` each have exactly `color`, `energy`, `rotationEulerDegrees`, and `shadow`; values are `key={"color":"#FFD7A3","energy":4.2,"rotationEulerDegrees":[38.0,-24.0,-32.0],"shadow":true}` and `fill={"color":"#7EA6C4","energy":1.1,"rotationEulerDegrees":[62.0,18.0,148.0],"shadow":false}`.

## Closed materials and budgets

`materials` is an ordered array of exactly ten records. Every record has exactly `name`, `baseColor`, `roughness`, `metallic`, and `normalStrength`, in this order:

1. `sandstone`, `#D8B98C`, `.82`, `.01`, `.42`;
2. `fresh-break`, `#8F7659`, `.90`, `.00`, `.58`;
3. `basalt`, `#1B2935`, `.78`, `.02`, `.48`;
4. `basalt-strata`, `#334653`, `.86`, `.01`, `.62`;
5. `tide-scar`, `#F2EAD7`, `.90`, `.00`, `.12`;
6. `coral-mineral`, `#B44A38`, `.74`, `.03`, `.36`;
7. `skin`, `#8A5B45`, `.70`, `.00`, `.18`;
8. `cloth`, `#203746`, `.88`, `.00`, `.24`;
9. `leather`, `#2A3338`, `.76`, `.02`, `.32`;
10. `rock-armour`, `#111A20`, `.72`, `.04`, `.54`.

`budgets` has exactly these integer byte/count keys and values:

`{"desktopDecodedTextureBytes":39845888,"desktopDrawCalls":60,"desktopVisibleTriangles":150000,"materialCount":10,"mobileDecodedTextureBytes":18874368,"mobileDrawCalls":45,"mobileVisibleTriangles":100000,"optimizedGlbBytes":8388608,"optimizedTriangles":110000,"sourceTriangles":150000}`.

## Closed outputs array

`outputs` is an array of exactly 20 records. Every record has exactly `index`, `profile`, `pass`, `sceneId`, `relativePath`, `width`, and `height`. `relativePath` is relative to diagnostic root and equals the filename. The exact ordered records are:

| Index | Profile | Pass | Scene | Filename | Size |
| ---: | --- | --- | --- | --- | --- |
| 0 | portrait | beauty | tr4-diagnostic-running-001 | `tr4-diagnostic-001-portrait-beauty.png` | 270x480 |
| 1 | portrait | object-id | tr4-diagnostic-running-001 | `tr4-diagnostic-001-portrait-object-id.png` | 270x480 |
| 2 | portrait | road-mask | tr4-diagnostic-running-001 | `tr4-diagnostic-001-portrait-road-mask.png` | 270x480 |
| 3 | portrait | normal | tr4-diagnostic-running-001 | `tr4-diagnostic-001-portrait-normal.png` | 270x480 |
| 4 | portrait | linear-depth | tr4-diagnostic-running-001 | `tr4-diagnostic-001-portrait-linear-depth.png` | 270x480 |
| 5 | desktop | beauty | tr4-diagnostic-running-001 | `tr4-diagnostic-001-desktop-beauty.png` | 480x270 |
| 6 | desktop | object-id | tr4-diagnostic-running-001 | `tr4-diagnostic-001-desktop-object-id.png` | 480x270 |
| 7 | desktop | road-mask | tr4-diagnostic-running-001 | `tr4-diagnostic-001-desktop-road-mask.png` | 480x270 |
| 8 | desktop | normal | tr4-diagnostic-running-001 | `tr4-diagnostic-001-desktop-normal.png` | 480x270 |
| 9 | desktop | linear-depth | tr4-diagnostic-running-001 | `tr4-diagnostic-001-desktop-linear-depth.png` | 480x270 |
| 10 | landscape | beauty | tr4-diagnostic-running-001 | `tr4-diagnostic-001-landscape-beauty.png` | 422x195 |
| 11 | landscape | object-id | tr4-diagnostic-running-001 | `tr4-diagnostic-001-landscape-object-id.png` | 422x195 |
| 12 | landscape | road-mask | tr4-diagnostic-running-001 | `tr4-diagnostic-001-landscape-road-mask.png` | 422x195 |
| 13 | landscape | normal | tr4-diagnostic-running-001 | `tr4-diagnostic-001-landscape-normal.png` | 422x195 |
| 14 | landscape | linear-depth | tr4-diagnostic-running-001 | `tr4-diagnostic-001-landscape-linear-depth.png` | 422x195 |
| 15 | closeup | beauty | tr4-diagnostic-game-over-001 | `tr4-diagnostic-001-closeup-beauty.png` | 320x240 |
| 16 | closeup | object-id | tr4-diagnostic-game-over-001 | `tr4-diagnostic-001-closeup-object-id.png` | 320x240 |
| 17 | closeup | road-mask | tr4-diagnostic-game-over-001 | `tr4-diagnostic-001-closeup-road-mask.png` | 320x240 |
| 18 | closeup | normal | tr4-diagnostic-game-over-001 | `tr4-diagnostic-001-closeup-normal.png` | 320x240 |
| 19 | closeup | linear-depth | tr4-diagnostic-game-over-001 | `tr4-diagnostic-001-closeup-linear-depth.png` | 320x240 |

The validator constructs these objects itself and deep-compares normalized input by key set, type, order, and frozen value before accepting `constructionHash` or `READY_FOR_BLENDER`.

Every output except the external reference must resolve inside `E:\Proj\Game-1-temple`. The three script paths must resolve to their exact authorized filenames. The diagnostic root must be exactly `docs\workstreams\temple-tr4-asset\diagnostic-001`, must not exist before successful in-memory validation, and is then created once to atomically write `preflight.json` and `planned-manifest.json`. Existing output, symlink/reparse escape, path traversal, unwritable parent, reference mismatch, unsupported version, unknown field, non-finite number, hash mismatch, or construction mismatch is `PRECHECK_BLOCKED` before Blender.

## Frozen cameras and projection

Road top and runner ground are `Y=0`; the runner root is `(0,0,0)`. A camera looks from the frozen position to target with up `(0,1,0)`. For vertical FOV `f`, aspect `a`, near `n`, and far `q`, the normalized WebGL column-major projection is the standard perspective matrix with `m[0]=1/(tan(f/2)*a)`, `m[5]=1/tan(f/2)`, `m[10]=-(q+n)/(q-n)`, `m[11]=-1`, `m[14]=-(2*q*n)/(q-n)`, `m[15]=0`, and `m[9]=lensShiftY`; all other unspecified elements are zero. Three's column-major `m[9]` corresponds to row `1`, column `2`. Inside the sole authorized Blender process, the generator evaluates `b0=calc_matrix_camera(shift_y=0)[1][2]` and `b1=calc_matrix_camera(shift_y=1)[1][2]`, rejects `abs(b1-b0)<1e-9`, then sets `Camera.shift_y=(lensShiftY-b0)/(b1-b0)`. It recalculates and requires the same principal-offset element to match within `1e-6` before rendering; it may not tune framing from image output.

## Exactly one diagnostic batch

One Blender 4.5.5 background process builds the one normalized scene and performs exactly 20 `write_still` calls. Profile order is `portrait`, `desktop`, `landscape`, `closeup`; within each profile pass order is `beauty`, `object-id`, `road-mask`, `normal`, `linear-depth`. Filenames are exactly:

`tr4-diagnostic-001-{profile}-{pass}.png`.

Diagnostic resolutions are portrait `270x480`, desktop `480x270`, landscape `422x195`, and closeup `320x240`. Every pass for one profile has identical dimensions and camera matrices.

- `beauty`: AgX high-contrast look, sRGB PNG8, opaque.
- `object-id`: unlit PNG8 with no antialias blending. Palette: background `#000000`, road `#D9B98C`, canyon `#1B2935`, runner `#F2EAD7`, pursuer `#101820`, beam `#B44A38`, ring `#E69648`, column `#6D4834`, gap lips `#7A2221`, Tide Scar `#FFFFFF`. Pursuer pixels must be exactly zero in portrait/desktop/landscape and positive in closeup.
- `road-mask`: binary grayscale PNG8; road top, structural sides, and gap lips are `255`, everything else `0`; the missing gap stays `0`.
- `normal`: opaque PNG8 world-space geometric normal encoded from `[-1,1]` to `[0,255]`; background is `#8080FF`.
- `linear-depth`: grayscale PNG16, `0` at the near plane and `65535` at far/background, with linear world-camera distance normalized by the profile far plane.

After Blender exits successfully, the runner proves the exact 20-name ordered set, dimensions, nonzero bytes, and no additional PNGs, then invokes the evaluator exactly once. The evaluator writes `evaluation.json` plus `manifest.json` with ordered relative path, SHA-256, byte count, width, height, and pass. It may emit at most `READY_FOR_MANUAL_REVIEW`; numeric success never authorizes export. Any launch, render, output, evaluator, or gate failure is `DIAGNOSTIC_BLOCKED`; no automatic retry, alternate camera, threshold change, or second Blender process is permitted in this slice.

## Export boundary

Only a coordinator-authored `EXPORT_AUTHORIZATION.md` containing the accepted diagnostic manifest hash may open export `001`. Source is `docs/workstreams/temple-tr4-asset/export-001/tide-scar-tr4-source.glb`; optimized proof is `docs/workstreams/temple-tr4-asset/export-001/tide-scar-tr4.glb`; runtime copies are `src/assets/tide-scar-tr4/tide-scar-tr4.glb` and `manifest.json`. Source and optimized files must each expose exactly the nine ordered top-level roots, identity transforms, named contact/collision sockets, metre units, and extras. Optimization must not flatten, join named nodes, prune semantic roots, or simplify collision/skin data. `gltf-transform inspect`, the custom semantic validator, byte/triangle/material budgets, and SHA-256 manifest must all pass before the coordinator can record `ACCEPTED_FOR_RUNTIME_INTEGRATION`.

## Proposed C7 overlay — review only

- Identity is schema version `7`, contract `TEMPLE-TR4-C7`, diagnostic root `diagnostic-007`, output prefix `tr4-diagnostic-007-`, and new scene/construction hashes. All twenty profiles, passes, dimensions, and their order remain unchanged except for the new identity-bound names.
- `constructionHash` retains its C1 meaning: SHA-256 of canonical `construction` only. It never includes sibling top-level fields. After `preflight.json` is atomically written, `planned-manifest.json.preflightSha256` binds the complete normalized preflight including cameras, collision, materials, roots, budgets, and outputs; evaluator/manifest validation must replay both hashes.
- C7 `construction` has exactly these keys: `atmosphere`, `axis`, `canyon`, `depthEncoding`, `hazards`, `lighting`, `materialGraphs`, `pursuer`, `road`, `runner`, `tideScar`, `unitMeters`. Unknown or missing keys are `PRECHECK_BLOCKED`.
- `lighting` has exactly `worldColor`, `worldStrength`, `key`, `fill`, `contact`; the values are the C6 world surface, key/fill/contact records. `atmosphere` has exactly `mode`, `worldVolumeEnabled`, `depthSource`, `density`, `fogColor`, `backgroundPolicy`, `viewTransform`, `look`, `exposure`, `gamma`, `nodeOrder`, `nodeTypeByName`, `operationByName`, `linkOrder`; values and order are closed in `DIAGNOSTIC_007_AUTHORIZATION.md`.
- `materialGraphs` has exactly `coordinateSource`, `graphOrder`, `template`, `parameters`. `template` has exactly `nodeOrder`, `nodeTypeByName`, `linkOrder`, `rampPositions`, `heightMixBlend`, `roughnessMapClamp`, `parameterBindings`, `fixedNodeProperties`, `fixedSocketValues`; every parameter record has exactly `mappingScale`, `macroScale`, `macroDetail`, `macroRoughness`, `microScale`, `microDetail`, `voronoiScale`, `voronoiRandomness`, `rampLow`, `rampHigh`, `roughnessRange`, `bumpDistance`, `bumpStrength`. Values are the closed C7 table.
- `depthEncoding` has exactly `distanceMetric`, `nearSource`, `ceilingByProfile`, `foregroundScale`, `backgroundValue`, `bitDepth`, `colorType`, `rounding`, `foregroundQuantileSample`, `semanticSampleSource`. The exact formula, values, percentile population, and semantic-mask source are closed in the C7 authorization.
- C7 adds the exact reconstruction fields named under `DIAGNOSTIC_007_AUTHORIZATION.md` to `road`, each canyon band, `runner`, `pursuer`, every hazard record, and `tideScar`. The authorization lists the complete resulting key sets and exact values; C1 key sets are not silently open-ended.
- `camera-binding.json` becomes schema version `3` and has exactly `schemaId`, `schemaVersion`, `diagnosticId`, `blenderVersion`, `profiles`, `lightingBinding`, `atmosphereBinding`, `renderCallCountAtWrite`, `verdict`. `atmosphereBinding` must deep-equal the normalized C7 atmosphere record plus exact `transmittance20/120/520` and `verdict`. `scene-metrics.json` has exactly the C6 keys `meshObjects`, `sourceTrianglesBeforeModifiers`, `beautyMaterialCount`, `semanticRoots`, `pursuerBookendRoot`, `runnerRoot`, `roadTopY`, `verdict` plus `geometryBinding`, `materialGraphBinding`, `depthEncodingBinding`; each new binding is a normalized actual-scene record deep-equal to its construction record plus `verdict`. Any unknown/missing key or inequality blocks before evaluator pixel gates.
- The four frozen C5/C6 camera records, matrices, FOV, near/far, and lens shift remain unchanged. The generator may keep its recorded angle method. Runner and evaluator require both recorded and recomputed local-axis angles `<=1e-5` and require `abs(cos(recorded)-cos(recomputed))<=1e-12`; direct equality of the near-zero radian values is forbidden.
- A non-writing dry predicate test must accept the frozen C6 landscape pair and reject a tampered sample whose axis angle exceeds `1e-5`. A dry result cannot create the diagnostic root or launch Blender.
- C7 changes the construction hash because substantive scene reconstruction is mandatory. Reusing C6 construction or rerendering it with only the predicate fix is `PRECHECK_BLOCKED`.
- Beauty and linear-depth construction follow the exact C7 material, compositor, and capped-visible-depth records in `DIAGNOSTIC_007_AUTHORIZATION.md`; the C1/C6 world-volume and far-plane-normalized depth records are superseded only for diagnostic `007`.
- A successful runner/evaluator can emit at most `READY_FOR_MANUAL_REVIEW`. Export, runtime integration, browser capture, the final typecheck/full suite/build, and acceptance remain blocked.
