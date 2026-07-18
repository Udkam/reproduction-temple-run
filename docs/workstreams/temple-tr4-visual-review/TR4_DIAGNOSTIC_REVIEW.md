# TEMPLE-TR4 diagnostic 006 independent visual review

Review date: 2026-07-18
Reviewer disposition: **MANUAL_BLOCKED**
Evidence role: read-only recovery adjunct; this review does not repair, rerender, evaluate, export, integrate, accept, or upgrade diagnostic `006`.

## Frozen evidence boundary

- Approved external north star: `C:\Users\ALEXCH~1\AppData\Local\Temp\codex-clipboard-ca70825b-99a6-4290-8307-4d90b2077d48.png`, `941x1672`, SHA-256 `8fc0c6a7f7fc8d7e5b65fd3d256dee33ccfeede0e4aba4a04657c66a93e33074` as bound by `TR4_VISUAL_CONTRACT.md`.
- Frozen diagnostic root: `docs/workstreams/temple-tr4-asset/diagnostic-006/`.
- `diagnostic-status.json` is terminal `DIAGNOSTIC_BLOCKED` at stage `render-set`.
- Exact technical reason: `DIAGNOSTIC_BLOCKED local camera axis alignment failed: cameraBinding.profiles[2].orientation`.
- Blender returned `0` and all 20 ordered PNGs were written. The evaluator was not invoked: `evaluatorReturnCode` and `evaluationSha256` are `null`.
- Bound evidence hashes recorded by the frozen status are:
  - camera binding: `87bf4713b06380f5715b585f3698749f0cb778384ad7f700f3db40c6906202d2`;
  - render order: `4f354bf772f3a7d70fb4131515850ed35503b4a647f4b76dc8de38604ed714a9`;
  - scene metrics: `7f89c5ea9d4457d285a75fbb4cb8aad4cd94dce3598e4773d6a0152e0707ebe6`.
- This manual review cannot replace the missing evaluator run or raise the technical verdict to `READY_FOR_MANUAL_REVIEW`.

## Complete image inspection

Every frozen PNG was opened at original resolution and inspected against the external reference and `TR4_VISUAL_CONTRACT.md`.

| Profile | Beauty | Object ID | Road mask | Normal | Linear depth |
| --- | --- | --- | --- | --- | --- |
| portrait | `tr4-diagnostic-006-portrait-beauty.png` | `tr4-diagnostic-006-portrait-object-id.png` | `tr4-diagnostic-006-portrait-road-mask.png` | `tr4-diagnostic-006-portrait-normal.png` | `tr4-diagnostic-006-portrait-linear-depth.png` |
| desktop | `tr4-diagnostic-006-desktop-beauty.png` | `tr4-diagnostic-006-desktop-object-id.png` | `tr4-diagnostic-006-desktop-road-mask.png` | `tr4-diagnostic-006-desktop-normal.png` | `tr4-diagnostic-006-desktop-linear-depth.png` |
| landscape | `tr4-diagnostic-006-landscape-beauty.png` | `tr4-diagnostic-006-landscape-object-id.png` | `tr4-diagnostic-006-landscape-road-mask.png` | `tr4-diagnostic-006-landscape-normal.png` | `tr4-diagnostic-006-landscape-linear-depth.png` |
| closeup | `tr4-diagnostic-006-closeup-beauty.png` | `tr4-diagnostic-006-closeup-object-id.png` | `tr4-diagnostic-006-closeup-road-mask.png` | `tr4-diagnostic-006-closeup-normal.png` | `tr4-diagnostic-006-closeup-linear-depth.png` |

## Per-profile findings

### Portrait

- Positive orientation evidence: the camera is visually upright, the route converges toward the upper centre, and the courier sits near the lower centre. This does not supersede the separate failed local-axis record for landscape.
- The upper half of beauty is almost entirely black. No readable horizon, fog canyon, far mountains, atmospheric falloff, or separated far silhouette survives.
- The road reads as a flat, straight, uniformly amber rectangular strip. Horizontal module seams are visible, but broken lips, fractures, terraces, undercuts, side mass, aggregate, dust, and authored medium-scale structures do not read.
- The courier reads as joined spheres and rectangular slabs. Head, torso, gait, elbows, knees, feet, coat tails, material separation, and contact shadow are not immediately readable at gameplay scale.
- The white Tide Scar hugs the right boundary as an almost straight line. Its required longitudinal meander and near loop do not read in this frame.
- Object-ID and normal reveal repeated faceted side spires that the beauty pass crushes to black. Road-mask shows a straight deck and simple transverse hazard bars. Linear-depth appears nearly uniform white and supplies no manually readable front/mid/far separation.

### Desktop

- The route converges correctly, but most of the beauty frame is black. Canyon structure, horizon and distant atmosphere are absent from the final material/light result.
- The courier is very small and dark and cannot be identified immediately by anatomical silhouette or running pose.
- The near Tide Scar loop is cut by the lower-right frame edge and does not read as a restrained gesture on a widened shoulder.
- Object-ID and normal show a corridor of repeated, similarly faceted rock towers on both sides. Their rhythm is regular and blockout-like rather than an asymmetric near/mid/far canyon hierarchy.
- The road top has an almost constant normal and value response. It lacks physically distinct breaks, roughness variation, edge wear and contact grounding.
- Linear-depth is again visually near-white and cannot prove depth ordering or intersection safety.

### Landscape

- This is the weakest ordinary-running composition. The usable road, courier and next event occupy a small centre wedge surrounded by black; the world does not lead the view laterally or into a fog horizon.
- Repeated rock towers and the featureless road strip are clearest in object-ID/normal. The side masses form a low-poly corridor rather than layered canyon negative space.
- The Tide Scar loop is cropped at the lower-right edge and the longitudinal mark reads as a border stripe.
- Courier and hazard silhouettes are too small and primitive for gameplay recognition.
- Linear-depth is visually near-white. In addition, the frozen technical status specifically rejects `cameraBinding.profiles[2].orientation`, so this profile has both visual and binding evidence failures.

### Closeup

- Lifecycle staging is directionally correct: the pursuer is absent from the three ordinary profiles and present in the game-over bookend closeup.
- The pursuer fails its model gate. It reads as one large black oval/spherical torso, two thick legs, a small head and a thin red line, not as an original rock-armoured creature with head direction, shoulder mass, separated plates, four grounded limbs, paws and a coral dorsal seam.
- The pursuer blocks almost all of the courier. Object-ID leaves a white courier head/upper body immediately behind it, while normal confirms joined primitive masses. The evidence cannot demonstrate a non-intersecting caught pose; the overlap is therefore a hard anti-clipping review failure.
- The black environment, flat road, cropped Tide Scar loop, absent contact shadows and near-white depth pass repeat in closeup.

## Cross-profile gate disposition

### P0 failures

1. **Technical evidence:** the frozen local camera-axis failure prevents evaluator execution. C6 remains `DIAGNOSTIC_BLOCKED` regardless of manual findings.
2. **Lighting and atmosphere:** all beauty frames crush the canyon and horizon to black. There is no visible volumetric depth, warm/cool separation, basalt highlight response, or three-layer atmospheric falloff.
3. **Causeway hierarchy:** the route is a straight, featureless blockout strip rather than a broken, physically thick, winding sandstone causeway with authored medium structure.
4. **Canyon hierarchy:** the side environment is a repeated low-poly rock corridor, with no acceptable near/mid/far signature separation.
5. **Courier:** the character remains joined primitives without a readable anatomical silhouette, gait, ground contact, coat or physical material response.
6. **Hazards:** transverse rectangles and distant blocks do not communicate beam, ring, column and gap actions through supported geometry, negative-space openings, thickness and fractured lips.
7. **Pursuer and anti-clipping:** the closeup creature is a black primitive blob and occludes or potentially intersects the courier. Four grounded limbs, plates, paws and readable caught staging are missing.
8. **Tide Scar:** the line reads as a straight edge stripe; its loop is absent or cropped and it does not reproduce the approved procedural path language.
9. **Depth evidence:** every linear-depth frame is visually near-white and cannot support manual depth-layer or clipping review.

### P1 failures

- Stone and basalt rely on flat colour rather than roughness, normal, fresh-break, edge-wear, aggregate and dust response.
- Coral/mineral deposits, route debris and grounded contact shadows do not establish the approved material hierarchy.
- Object-ID and normal expose repeated faceting, abrupt seams and blockout construction that beauty merely hides.
- No frame provides sufficient visual evidence for runner self-intersection clearance, hazard clearances, floating-support rejection or Tide Scar clipping against hazards/gaps.

## Reusable elements

- The four views are visually upright and share a forward-converging camera direction, subject to the unresolved landscape axis gate.
- Ordinary profiles hide the pursuer and the closeup bookend shows it, preserving the intended lifecycle direction.
- The ordered 20-pass capture, semantic root structure, object-ID, road-mask and normal channels are useful diagnostic infrastructure.
- A slightly broken outer road silhouette and some asymmetric negative spaces are visible in ID/normal.
- The intended warm road, cool side mass, chalk-white Scar and restrained coral accent palette can be retained as direction, but not as finished material work.

## Prioritized bounded successor requirements

1. **C7A — technical evidence only:** correct the landscape local-axis binding inconsistency and make linear-depth manually discriminable, then prove that the evaluator runs exactly once. This slice must not claim visual acceptance.
2. **C7B — environment primary and medium structure:** replace only the road/canyon blockout with thick broken road modules and authored near/mid/far canyon signatures; repair black beauty lighting and atmospheric separation while retaining the frozen composition contract.
3. **C7C — semantic models and clearance:** independently rebuild the courier, beam/ring/column/gap presentations and pursuer with readable anatomy/support/openings/plates/ground contacts, then enforce analytic anti-clipping and pose-clearance gates.
4. **C7D — materials and Tide Scar:** after silhouettes pass, add shared PBR stone/basalt response, dust/break/edge detail, sparse mineral red, and a longitudinal procedural Scar whose loop remains on the widened shoulder and fully inside the intended frame.
5. Only a new, terminally valid diagnostic with an evaluator result and independent inspection of all bound passes may be considered for export authorization. C6 must not enter GLB export or runtime integration.

## Review procedure statement

This review opened the external reference, the frozen status/contract records, and all 20 PNGs read-only. It did **not** run any project script, Blender process, evaluator, test, build, browser session, Git command, staging action, or commit.
