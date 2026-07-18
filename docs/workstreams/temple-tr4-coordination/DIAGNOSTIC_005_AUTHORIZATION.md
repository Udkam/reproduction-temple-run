# TEMPLE-TR4 diagnostic 005 orientation and illumination correction

Status: **AUTHORIZED.** Independent contract-consistency and numeric/geometry reviews both returned `READY_FOR_DIAGNOSTIC_005_CONTRACT` with no remaining P0/P1. This permits only the exact C5 script deltas, non-writing dry preflight, one new diagnostic directory, one Blender 4.5.5 process, 20 ordered PNGs, and at most one evaluator under the closed gates below. It does not authorize retry, export, runtime action, browser, test, build, Git, commit, or push.

## Frozen C4 evidence and disposition

Diagnostic `004` is immutable `DIAGNOSTIC_BLOCKED`. Its sole Blender 4.5.5 process returned `0`, passed all four inherited camera-shift calibrations, and made exactly 20 ordered `write_still` calls. The runner then stopped before the evaluator because Blender serialized the canonical pursuer root `2.4` as `2.4000000953674316`; exact list equality rejected the scene metrics. The directory contains exactly 27 frozen files. Its terminal status is `diagnostic-status.json` SHA-256 `f10fea75788c3a1c434b6461c99be1cf01b5ba0e86bfa4bd1f9843a2b16883a6`; all 27 hashes remain binding in `docs/workstreams/temple-tr4-asset/THREAD_LOG.md` and must be rechecked before and after C5.

Independent manual inspection of the frozen C4 images is `MANUAL_BLOCKED`, regardless of the runner stopping before evaluator. The four beauty frames have 71-93% near-black pixels; road and semantic masks show an approximately 180-degree rolled composition, courier at the top/cropped, reversed route and Tide Scar, no usable far-horizon hierarchy, primitive hazards/courier, and a closeup pursuer that reads as a black blob. C4 is evidence of a failed scene, never an accepted visual baseline and never reusable output.

## Exact C5 identity and unchanged scope

C5 inherits every C4 source boundary, seed, reference, tool version, scene IDs/states, collision rule, material identity/PBR value, semantic-root order, mesh/triangle/material budget, construction geometry/topology, pose, hazard, Tide Scar control point, output pass/order/resolution/format, allowlist, provenance, single-process, single-evaluator, no-retry, and manual-review gate except the exact deltas below.

Identity changes are exactly:

- preflight `schemaVersion=5` and `contractVersion="TEMPLE-TR4-C5"`;
- diagnostic root `docs\workstreams\temple-tr4-asset\diagnostic-005`;
- `diagnosticId="005"` in planned manifest, camera binding, evaluation, manifest, and status; `render-order.json` remains the exact schema-less 20-name array and `scene-metrics.json` remains the exact C3/C4 closed object without an invented identity field;
- output prefix `tr4-diagnostic-005-` for the same 20 ordered profile/pass records.

Geometry, material records, semantic roots, runner/pursuer/hazard meshes, route modules, canyon clusters, Tide Scar splines, transforms other than the camera and lights below, and every collision/fairness value are byte-for-byte construction-equivalent to C4. C5 is only an orientation/illumination proof. Even numeric success can be manually blocked for model quality and cannot authorize export.

## Explicit Y-up camera binding

The four exact C5 camera records are:

| Profile | Resolution | Position | Target | Up | FOV | Near/Far | Lens shift Y |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| portrait | `540x960` | `(0,6.20,15.20)` | `(0,.55,-16.80)` | `(0,1,0)` | `40` | `.08/520` | `-.055` |
| desktop | `960x540` | `(0,6.06,13.60)` | `(0,.60,-13.30)` | `(0,1,0)` | `43` | `.08/520` | `-.025` |
| landscape | `844x390` | `(0,6.15,12.80)` | `(0,.55,-12.56)` | `(0,1,0)` | `46` | `.08/520` | `-.020` |
| closeup | `640x480` | `(0,5.40,9.80)` | `(0,1.15,-3.40)` | `(0,1,0)` | `48` | `.05/180` | `0` |

Each C5 preflight camera retains the exact C4 keys `profile`, `resolution`, `diagnosticResolution`, `position`, `target`, `up`, `verticalFovDegrees`, `aspect`, `near`, `far`, `lensShiftY`, `viewMatrix`, and `projectionMatrix`, and adds exactly `projectionAnchors`. That object has exactly `runnerAnchor`, `runnerHead`, `runnerFootL`, `runnerFootR`, `beam`, `ring`, `column`, `gap`, `scar`, `routeCenter`, and `farRoute`, each an exact three-number world-space point. The frozen values are:

| Bound profiles | runnerAnchor | runnerHead | runnerFootL | runnerFootR |
| --- | --- | --- | --- | --- |
| portrait/desktop/landscape (`run`) | `(0,1.20,0)` | `(0,2.05,-.25)` | `(-.25,.085,-.56)` | `(.25,.08,.22)` |
| closeup (`failure`) | `(.46,1.08,-.34)` | `(.57,1.46,-.62)` | `(-.48,.075,-.72)` | `(1.02,.075,.48)` |

All four profiles use `beam=(0,.72,-18)`, `ring=(0,1.05,-36)`, `column=(0,1.12,-54)`, `gap=(0,0,-74)`, `scar=(3.03,.035,0)`, `routeCenter=(0,.035,0)`, and `farRoute=(0,0,-120)`. These are analytic projection anchors only; they do not replace the evaluator's independent object-ID pixel centroids or change mesh/collision transforms.

The pure-Python preflight computes and freezes each canonical view/projection matrix before any `bpy` import. Blender must not use `to_track_quat` or ignore the record's `up`. For each record it computes:

```text
forward = normalize(target - position)
worldUp = normalize(up)
right = normalize(forward cross worldUp)
trueUp = normalize(right cross forward)
rotation = Matrix((right, trueUp, -forward)).transposed().to_quaternion()
```

Before the first render and again on each profile replay, all components are finite; vector lengths equal one and pairwise dot products equal zero within `5e-7`; determinant equals `+1` within `5e-7`; camera local `-Z` aligns to `forward` and local `+Y` aligns to `trueUp` within `1e-5` radians; and the evaluated camera's actual 16-value view matrix matches the pure-Python canonical view matrix with maximum element error `<=5e-6`. The C3/C4 shift calibration remains: target Python row-major index `6` / WebGL column-major index `9`, response `2 +/-5e-7`, off-target delta `<=5e-7`, dominance `>=1e6`, and solved projection maximum error `<=5e-7`.

Static pre-render projection gates use top-left normalized coordinates and fail before the first `write_still` if any record violates them:

- finite/in-frustum runner visual anchor `(0,1.20,0)`; portrait Y `.61-.72`, desktop/landscape `.62-.76`;
- runner head projects above both feet;
- ordinary-running frozen preview anchors satisfy `runnerY > beamY > ringY > columnY > gapY`;
- Tide Scar point `(3.03,.035,0)` projects strictly right of route-centre point `(0,.035,0)` at the same depth;
- analytic horizon target is inside `.17-.31H` for portrait/desktop/landscape;
- frozen far-route sample `(0,0,-120)` projects in-frame and records its top-left `farRouteY` independently from the analytic horizon.

`camera-binding.json` is the sole extended C5 ancillary record. Its top-level key set is exactly `schemaId`, `schemaVersion`, `diagnosticId`, `blenderVersion`, `profiles`, `lightingBinding`, `atmosphereBinding`, `renderCallCountAtWrite`, and `verdict`; values are `schemaId="tide-relay.temple-tr4.camera-binding"`, `schemaVersion=2`, `diagnosticId="005"`, Blender `4.5.5 LTS`, four ordered profiles, `renderCallCountAtWrite=0`, and `verdict="READY_FOR_DIAGNOSTIC_RENDER"`.

Each profile has exactly `profile`, `lensShiftY`, `originalShift0`, `evaluatedShift0`, `originalShift1`, `evaluatedShift1`, `matrix0`, `matrix1`, `difference`, `b0`, `b1`, `response`, `maxOffTargetCalibrationDelta`, `dominanceRatio`, `solvedShift`, `evaluatedSolvedShift`, `matrixSolved`, `solvedDifference`, `actual`, `targetError`, `maxOffTargetSolvedDelta`, `webglMatrix`, `maxProjectionError`, `orientation`, and `screenProjection`. The inherited projection matrices/differences use 16 finite Python row-major values except `webglMatrix`, which is the 16-value Three/WebGL column-major transpose. `orientation` has exactly `position`, `target`, `up`, `forward`, `right`, `trueUp`, `vectorLengths`, `pairwiseDots`, `determinant`, `canonicalViewMatrix`, `actualViewMatrix`, `maxViewMatrixError`, `localForwardAngleRadians`, and `localUpAngleRadians`. Its vectors have three finite numbers; its matrices have 16 finite row-major numbers; `vectorLengths` is `[right,trueUp,forward]`; `pairwiseDots` is `[rightDotTrueUp,rightDotForward,trueUpDotForward]`; all values satisfy the tolerances above and are arithmetically recomputed by runner and evaluator. `screenProjection` has exactly `runnerAnchor`, `runnerHeadY`, `runnerFootLY`, `runnerFootRY`, `beamY`, `ringY`, `columnY`, `gapY`, `scarX`, `routeCenterX`, `horizonY`, `farRouteY`, and `verdict`. `runnerAnchor` is exactly a two-number normalized `[x,y]`; every other coordinate field is one finite normalized scalar; `verdict="READY_FOR_DIAGNOSTIC_RENDER"`. Every coordinate is independently recomputed from the corresponding preflight `projectionAnchors` and canonical matrices. `horizonY` alone projects homogeneous world direction `(0,0,-1,0)` through the view/projection pair and performs the perspective divide; it is not derived from a finite mesh point. Only the three ordinary profiles receive the runner-band/horizon/far-route/preview-order gates; all four receive head-above-feet and Scar-right-of-centre gates.

## Road-facing lighting, world, and fog

C5 replaces C4's light rotations with closed surface-to-light vectors:

- key: `color="#FFD7A3"`, `energy=4.2`, `surfaceToLight=[-.51966,.77949,.34977]`, `shadow=true`;
- fill: `color="#7EA6C4"`, `energy=1.1`, `surfaceToLight=[.48019,.62025,-.62025]`, `shadow=false`;
- contact bounce: disk area light `color="#E7C79C"`, `energy=430`, `size=9`, `shadow=false`, `location=[0,7.5,4.0]`, `target=[0,0,-4.0]`.

The C5 preflight `construction.lighting` object has exactly `worldColor`, `worldStrength`, `fogColor`, `fogDensity`, `fogAnisotropy`, `key`, `fill`, and `contact`. `key` and `fill` each have exactly `color`, `energy`, `surfaceToLight`, and `shadow`. `contact` has exactly `color`, `energy`, `shape="DISK"`, `size`, `shadow`, `location`, and `target`. These fields replace the C4 Euler records; unknown/missing keys are rejected, every number is finite, arrays have exactly three components, and the C5 `constructionHash` is recomputed from the complete canonical C5 construction object after this replacement.

Both directional vectors must be normalized by the implementation and read back finite/unit within `5e-7`; key/fill Y are at least `.75/.55`; their X signs oppose. For each sun, actual world-space local `-Z` aligns with `-surfaceToLight` within `1e-5` radians. The contact light's actual local `-Z` aligns from its location to its target within `1e-5` radians. Boolean/string readbacks are exact; finite Blender float/color/vector readbacks match the closed or normalized record component-wise within `1e-6`. No fallback Euler angles are allowed.

Beauty world is `worldColor="#6E8294"`, `worldStrength=.55`, `fogColor="#9AA7A8"`, `fogDensity=.0035`, and `fogAnisotropy=.18`. `exp(-density*distance)` must be `>=.90` at `20m`, `.55-.72` at `120m`, and `>=.12` at `520m` before Blender. Beauty view remains exact `AgX` / `AgX - Medium High Contrast`, exposure `0`, gamma `1`, dither `0`; data passes remain exact `Raw` / `None`. Exposure lifts, emissive material substitutions, shadow disabling, volume removal, fog cards, panorama caps, and threshold lowering are forbidden.

`camera-binding.json.lightingBinding` has exactly `key`, `fill`, `contact`, and `verdict="READY_FOR_DIAGNOSTIC_RENDER"`. `key` and `fill` each have exactly `colorHex`, `colorLinear`, `energy`, `shadow`, `surfaceToLight`, `normalizedSurfaceToLight`, `actualLocalMinusZ`, and `alignmentRadians`; `contact` has exactly `colorHex`, `colorLinear`, `energy`, `size`, `shadow`, `location`, `target`, `actualLocalMinusZ`, and `alignmentRadians`. `atmosphereBinding` has exactly `worldColorHex`, `worldColorLinear`, `worldStrength`, `fogColorHex`, `fogColorLinear`, `fogDensity`, `fogAnisotropy`, `transmittance20`, `transmittance120`, `transmittance520`, `beautyViewTransform`, `beautyLook`, `exposure`, `gamma`, `dither`, and `verdict="READY_FOR_DIAGNOSTIC_RENDER"`. Linear colors are the existing deterministic sRGB-to-linear conversion and use the same `1e-6` component tolerance; transmittances are independently recomputed within `1e-12`. Required key shadow remains enabled; the contract's explicitly shadowless fill/contact records do not conflict with the ban on disabling the key shadow.

## Scene-metric and evaluator deltas

Only placement-valued floats use `math.isclose(actual, expected, rel_tol=0, abs_tol=1e-6)`: the three coordinates of each semantic-root translation, `pursuerBookendRoot`, `runnerRoot`, and scalar `roadTopY`. Root names/order/count, children counts, object/material/triangle counts, status strings, hashes, schemas, all non-placement values, and list lengths remain exact.

`render-order.json` remains exactly the ordered array of the 20 planned PNG relative names, with no object wrapper or schema/version/ID keys. `scene-metrics.json` remains exactly the eight C3/C4 keys `meshObjects`, `sourceTrianglesBeforeModifiers`, `beautyMaterialCount`, `semanticRoots`, `pursuerBookendRoot`, `runnerRoot`, `roadTopY`, and `verdict="RENDERED_FOR_EVALUATION"`; each semantic-root record remains exactly `{name,translation,children}`. No ancillary file other than `camera-binding.json` changes schema, so the inherited allowlist and the existing `cameraBindingSha256`, `renderOrderSha256`, and `sceneMetricsSha256` manifest/evaluation/status fields remain sufficient and closed.

The evaluator keeps every C4 gate and adds or makes explicit:

- all beauty profiles: luminance `p50>=.12`, `p95>=.55`, pixels with all RGB channels `<=10/255` below `10%`, route ROI `p50>=.25`;
- portrait runner centroid Y `.61-.72`; desktop/landscape `.62-.76`; actor containment margin `>=.02`;
- portrait bottom road width `>=.74W`; desktop/landscape `>=.44W`; at the frozen `Z=-120m` far-route row, portrait road width `.06-.19W` and desktop/landscape `.015-.08W`; bottom/far-route ratio `>=2.5`;
- top-left semantic ordering `runnerY > beamY > ringY > columnY > gapY` and Tide Scar same-depth point right of route centre;
- closeup pursuer containment margin `>=.02`, width `>=48px`, beauty ROI `p50>=.08` and `p95>=.20`; runner beauty ROI `p50>=.12`;
- normal-pass road-mask median `G>=240`, with `R` and `B` each in `112-144`, proving a `+Y` road top rather than inverted normals;
- linear-depth has at least 64 distinct non-background foreground values and increasing representative depth from runner to beam to ring to column to gap;
- pursuer object-ID pixels are exactly zero in portrait/desktop/landscape and positive in closeup.

Pixel algorithms are closed: bounds are the outward pixel-edge box `[xmin/W,ymin/H,(xmax+1)/W,(ymax+1)/H]` of an exact object-ID color; centroid coordinates average pixel centres; containment margin is the minimum distance of that box from the four normalized frame edges; actor beauty ROI quantiles use only beauty pixels at the exact actor-ID pixel positions. Road widths are the longest contiguous `255` run divided by width at row `floor(.98*(H-1))` and at `round(cameraBinding.farRouteY*(H-1))`; the analytic horizon row is never used as a road-mask sampling row. If the far-route row has no `255` run, `roadFarRouteWidthFraction=0.0`, `roadWidthRatio=0.0`, and `roadPerspective=false` without division. Otherwise the ratio is bottom width divided by far-route width. The road normal median uses normal-pass pixels where road-mask is `255`. Representative semantic depth is the median 16-bit depth value at exact object-ID positions, so background cannot enter; ordinary profiles require strict `runner < beam < ring < column < gap-lips` depth values. `depthUniqueValues` counts only depth pixels whose matching object-ID pixel is a known non-background semantic and whose depth is not `65535`; the minimum of 64 applies to that foreground set.

Every `profileMetrics` record has exactly `luminanceP50`, `luminanceP95`, `nearBlackFraction`, `routeLuminanceP50`, `roadMaskFraction`, `normalUniqueColors`, `depthUniqueValues`, `depthMin`, `depthMax`, `runnerBounds`, `runnerCentroidY`, `runnerMargin`, `runnerBeautyLuminanceP50`, `pursuerBounds`, `pursuerMargin`, `pursuerWidthPixels`, `pursuerBeautyLuminanceP50`, `pursuerBeautyLuminanceP95`, `roadBottomWidthFraction`, `roadFarRouteWidthFraction`, `roadWidthRatio`, `semanticCentroidY`, `roadNormalMedian`, and `representativeDepth`. `semanticCentroidY` and `representativeDepth` each have exactly `runner`, `beam`, `ring`, `column`, and `gap-lips`. Running-profile pursuer fields are exactly `null/null/0/null/null`; closeup fields are finite. Bounds are four finite normalized numbers; medians/centroids/fractions are finite; `roadNormalMedian` is three finite 8-bit channel values. Runner containment is gated in all four profiles; runner band, road perspective, semantic order, and representative-depth order are gated in the three ordinary profiles; pursuer containment/width/ROI are gated only in closeup.

The evaluation top-level key set and `schemaVersion=1` remain C4-exact. Its `gates` object has exactly `exactPngSet`, `pursuerAbsentOrdinary`, `pursuerPresentCloseup`, `hazardsPresentOrdinary`, `orderedManifest`, `cameraBinding`, `globalLuminance`, `routeLuminance`, `nearBlack`, `roadMaskBinaryArea`, `semanticSubjects`, `normalVariation`, `depthVariation`, `runnerBandContainment`, `roadPerspective`, `semanticScreenOrder`, `scarRightOfRoute`, `runnerRoiLuminance`, `pursuerCloseup`, `roadNormalUp`, and `representativeDepthOrder`; every value must be JSON `true` for `READY_FOR_MANUAL_REVIEW`. `semanticPixelCounts` keeps the exact palette-name counts per profile and `hazardPixelTotalsOrdinary` keeps exactly `beam`, `ring`, `column`, and `gap-lips`. Runner and evaluator both independently validate all nested key sets, types, arithmetic, camera-binding hash, and thresholds before accepting an empty `failures` list.

Masks/ROIs use the exact existing semantic colors and outward-rounded bounds; no image-tuned camera search, retry, alternate crop, or post-render threshold change is permitted. Evaluator success is at most `READY_FOR_MANUAL_REVIEW`. Independent manual review must still block low-poly repetition, primitive or blob characters, unreadable hazards, material flatness, weak atmospheric hierarchy, clipping, floating contacts, reversed route/Scar language, or mismatch with the approved high-level visual direction.

## Preflight and bounded execution

The existing asset writer may modify only the three TR4 asset-pipeline scripts and append its own `THREAD_LOG.md` plus new `diagnostic-005/**`. All prior diagnostic/probe directories, coordinator files, production/runtime files, and other workstream evidence are read-only.

Before C5 can be marked authorized, independent review must return exactly `READY_FOR_DIAGNOSTIC_005_CONTRACT` with no P0/P1. After authorization, the writer first runs AST/static checks and a non-writing pure-Python `--dry-preflight`. That preflight must verify this file is `AUTHORIZED`, `CURRENT_TASK.md` names diagnostic `005` as authorized, the coordination log says `TEMPLE-TR4-DIAGNOSTIC-005 AUTHORIZED`, the approved reference exists at `941x1672` with its frozen hash, Blender executable/version hash is frozen without launching a version subprocess, all prior frozen artifact hashes match, the C5 root is absent, all exact identity/camera/basis/light/fog/tolerance/evaluator records match, all output paths remain contained, and launch-bound hashes of all three scripts are fixed. It must leave `diagnostic-005` absent and emit only `READY_FOR_BLENDER` in stdout.

Only that verdict permits one Blender 4.5.5 background process, exactly 20 ordered PNG writes, and at most one evaluator. Any failure is terminal `DIAGNOSTIC_BLOCKED`; there is no retry, reuse, second process, alternate camera/light/fog, threshold change, cleanup, export, runtime integration, browser, test, build, Git, commit, or push. Manual review is mandatory even after numeric success.
