# TEMPLE-TR4 asset diagnostic thread log

Status: **IN PROGRESS**

Writer: `/root/tr4_asset_proof_writer_v2`

Authorized scope:

- `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`
- `tools/temple-asset-pipeline/evaluate_tide_scar_tr4_pack.py`
- `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py`
- `docs/workstreams/temple-tr4-asset/**`

## 2026-07-16 intake

- Read the repository collaboration agreement, current TR4 slice, visual contract,
  executable preflight schema, reference analysis, and the complete
  `blender-webgl-asset-proof` skill/reference set.
- Confirmed that all three authorized TR4 scripts and the TR4 asset evidence root were
  absent before this writer started. No existing TR4 asset file is being overwritten.
- Frozen rule: pure-Python closed-schema preflight must pass before the sole authorized
  Blender 4.5.5 background process. Any failure stops without retry, GLB export, runtime,
  browser, npm, build, test, or Git activity.

## 2026-07-16 implementation checkpoint

- Added the pure-Python runner with closed canonical JSON, finite/type/order checks,
  exact reference and script hashes, computed WebGL view/projection matrices, closed
  construction hash, Windows containment/reparse rejection, and the ordered 20-output
  plan. It creates `diagnostic-001` only after every in-memory gate is green.
- Added a standard-library PNG evaluator for exact ordered files, dimensions, bit depth,
  binary road masks, semantic object IDs, ordinary-run pursuer absence, closeup pursuer
  presence, hazard presence, normals/depth variation, luminance, route luminance, file
  hashes, and manifest binding. Its maximum result is `READY_FOR_MANUAL_REVIEW`.
- Added the Blender generator for 16 thick fractured sandstone modules and one actual
  missing span, separate near/mid/far basalt signatures, an editable clipped Tide Scar
  and separate near loop, articulated run/failure courier poses, an original four-contact
  rock-armoured pursuer, and four action-readable mineral hazards. Frozen cameras are
  verified from Blender's principal-offset response before rendering.
- Static AST parsing passed for all three scripts. The non-writing pure-Python dry
  preflight produced `READY_FOR_BLENDER`, 20 outputs, and construction SHA-256
  `344f6cee493455c20e41981023233f652fa4d94107682251a2efe9efbcb5e90d` before the
  final generator sampling correction; executable script hashes remain launch-time facts.

## 2026-07-16 diagnostic-001 terminal result

Verdict: **DIAGNOSTIC_BLOCKED**. Per contract, there was no retry, evaluator, export,
runtime work, browser activity, npm/test/build activity, or Git activity after failure.

Exact sole launch command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

The pure runner created the exact diagnostic root and bound preflight, then launched one
Blender process. Blender identified itself as `Blender 4.5.5 LTS` and exited `1` before
the first `write_still`. The first and terminal cause was:

```text
RuntimeError: camera shift response is degenerate for portrait
```

The failing required expression was the contract's
`calc_matrix_camera(...)[1][2]` zero/unit `shift_y` response in `set_camera`; in this
Blender process `b1-b0` was below `1e-9`. The generator correctly rejected the camera
instead of tuning framing or rendering with an unbound principal offset. This is a
camera-contract/API-coordinate blocker, not a pixel-quality verdict.

Evidence:

- `diagnostic-001/preflight.json`: 13,994 bytes, SHA-256
  `50d9c5bd2b59f6475e8ddd87ab6b404260fe3bb19f7132ff866d3e3d679fea12`
- `diagnostic-001/planned-manifest.json`: 3,770 bytes, SHA-256
  `dc57b641ad824a84dcfb27299e7ebdb5fbe9a6e35a2d96bd099cde1877a830bf`
- `diagnostic-001/blender.log`: 984 bytes, SHA-256
  `aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343`
- `diagnostic-001/diagnostic-status.json`: 66 bytes, SHA-256
  `551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9`
- PNG count: `0`; `evaluation.json` and `manifest.json`: absent by design because
  Blender did not complete.

Launch-bound script hashes:

- runner: `2a6e10516855d2dca31aeb9f7e2764157e14606d8acbfcb0d3b1954b011373f6`
- generator: `063f1b0709d3982b2bea89f2b8e07796779126dd0dfb8058cadb9695374cbdf7`
- evaluator: `09408ebc75cb32cb815b346ce8dd7ee13c86fba143eebf335946f01f54719b38`

Recommended next bounded coordinator action: resolve which Blender matrix element is the
normative `shift_y` response and how it maps to the WebGL `m[9]` target, then authorize a
new diagnostic ID and one fresh Blender process. `diagnostic-001` must remain immutable;
it cannot be deleted or reused as a retry directory.

## 2026-07-16 diagnostic-002 authorization intake

- Coordinator authorization: `docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_002_AUTHORIZATION.md`.
- Independent read-only contract verdict: `READY_FOR_DIAGNOSTIC_002_CONTRACT`.
- C2 changes are exact and bounded: preflight schema version `2`, contract
  `TEMPLE-TR4-C2`, new root `diagnostic-002`, output filename prefix
  `tr4-diagnostic-002-`, planned/evaluation/manifest `diagnosticId="002"`, and Blender
  vertical shift response/validation at `calc_matrix_camera(...)[2][1]`.
- Scene IDs, construction hash inputs, geometry, materials, lights, camera records,
  thresholds, pass order, dimensions, one-process/one-evaluator rule, and manual visual
  bar remain unchanged. All `diagnostic-001` files remain immutable.
- Updated only the three authorized scripts using `apply_patch`; no C1 string,
  diagnostic-001 path/output prefix, or `[1][2]` response remains in executable scripts.
- Static AST parsing passed for all three C2 scripts. A non-writing dry preflight returned
  `C2_DRY_READY READY_FOR_BLENDER 20` with the unchanged construction SHA-256
  `344f6cee493455c20e41981023233f652fa4d94107682251a2efe9efbcb5e90d`.
- Rechecked the four frozen diagnostic-001 evidence hashes before launch; every hash
  matched the recorded C1 value. `diagnostic-002` did not exist before the green C2
  preflight.

## 2026-07-16 diagnostic-002 terminal result

Verdict: **DIAGNOSTIC_BLOCKED**. Per the C2 authorization, the writer stopped after the
single new Blender process and did not retry, call the evaluator, export, or run any
browser/npm/test/build/Git activity.

Exact sole C2 launch command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

Blender again identified itself as `4.5.5 LTS` and exited `1` before the first
`write_still`. The C2-authorized upstream element `[2][1]` also produced
`abs(b1-b0)<1e-9` in the live camera calculation, so the first and terminal error remained:

```text
RuntimeError: camera shift response is degenerate for portrait
```

The generator correctly refused to infer or tune a fallback. Diagnostic `002` contains:

- `preflight.json`: 13,994 bytes, SHA-256
  `a43a26447924f4c6a6e07ebf7ad9de4273bb28eeb142393d9a14007eda63b294`
- `planned-manifest.json`: 3,791 bytes, SHA-256
  `5325ca93cef20d3201c9e20a8bcfb45beebeec79a382b965fc208754373a8df1`
- `blender.log`: 984 bytes, SHA-256
  `aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343`
- `diagnostic-status.json`: 66 bytes, SHA-256
  `551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9`
- PNG count `0`; evaluator `evaluation.json` and `manifest.json` absent.

C2 launch-bound script hashes:

- runner: `27b92b639c99f099eac2f17b849f8b2a010bc1d32da2864dc6b2de0920928fa7`
- generator: `736ebb59d6350dde97fe5dac0c2b4839c91a62541683ca3a88742c26793e72e0`
- evaluator: `656ace4f6b1c73e33352523fe36a55ad37f67df99aa4e52db608ee4b391af9a1`

The frozen diagnostic-001 hashes were rechecked after C2 failure and remain unchanged.
Any new authorization must use a new diagnostic ID and resolve why camera datablock
`shift_y` changes are not reflected by the measured matrix response in this live process
(including dependency-graph update/evaluated-object semantics) before another render.

## 2026-07-16 camera-probe-001 authorization intake

- Coordinator authorization: `docs/workstreams/temple-tr4-coordination/CAMERA_PROBE_001_AUTHORIZATION.md`.
- Independent read-only contract verdict: `READY_FOR_CAMERA_PROBE_001_CONTRACT`.
- This is a no-model/no-render Blender API probe, not diagnostic `003`. Authorized writes
  are generator, runner, this log, and new `camera-probe-001/**`; evaluator and both
  blocked diagnostic directories remain read-only.
- Added runner `--camera-probe` pure preflight/root-containment mode and generator
  `--camera-probe` mode. The generator creates one temporary camera and performs the exact
  four-profile sequence `shift -> data.update_tag() -> view_layer.update() -> fresh
  evaluated_depsgraph_get() -> calc_matrix_camera()[2][1]`, then atomically writes only
  `camera-response.json`. The runner permits only plan/log/response/status files and
  rejects any PNG/EXR/JPG/GLB/GLTF.
- Generator/runner AST parsing passed. Non-writing dry preflight returned
  `READY_FOR_CAMERA_PROBE` with four frozen cameras. Dry-bound hashes were generator
  `e84598618d8dbb0df03c9b7c33d9a1c556d304433b71729a9605d0ab8bba4877` and runner
  `4972c7d209da0bd8dec9e118a546cbeb05b0786e0673f8fe71afd9567d4e0fdc`.
- Evaluator SHA-256 remained
  `656ace4f6b1c73e33352523fe36a55ad37f67df99aa4e52db608ee4b391af9a1`.
  All eight diagnostic-001/002 evidence hashes were rechecked unchanged. Probe root and
  diagnostic-003 did not exist before the green dry preflight.

## 2026-07-16 camera-probe-001 terminal result

Verdict: **CAMERA_PROBE_BLOCKED**. The sole Blender 4.5.5 probe process exited `1` and
was not retried. It performed zero render calls, created zero image/export files, did not
model the TR4 scene, did not call the evaluator, and did not create diagnostic `003`.

Exact command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py --camera-probe
```

The authorized tag/update/fresh-depsgraph sequence executed for portrait and returned:

- `b0=0.0`
- `b1=0.0`
- `response=0.0`
- `solvedShift`: not computed because the required response gate failed
- `actual`: not computed
- `error`: not computed

The process stopped at the first profile as required, so desktop, landscape, and closeup
were not attempted. First and terminal error:

```text
RuntimeError: camera probe response is degenerate for portrait: b0=0.0, b1=0.0
```

Because the closed response requires all four successful profile records,
`camera-response.json` was not written. Frozen evidence is:

- `probe-plan.json`: 2,911 bytes, SHA-256
  `4cf25d218366661f01cab8ff6d3cd66809b9883b25a57b74548b9d99d65a5802`
- `blender.log`: 877 bytes, SHA-256
  `e32fb009d0c551faaaaa8d76f314aeadfb03fee696e226a6ca01b115435519cf`
- `probe-status.json`: 490 bytes, SHA-256
  `feaec46ada7ab64e579751d884d68b22a7a96f4467d59037feb373d59b8979dc`
- generator: SHA-256
  `e84598618d8dbb0df03c9b7c33d9a1c556d304433b71729a9605d0ab8bba4877`
- runner: SHA-256
  `4972c7d209da0bd8dec9e118a546cbeb05b0786e0673f8fe71afd9567d4e0fdc`
- evaluator remained unchanged at SHA-256
  `656ace4f6b1c73e33352523fe36a55ad37f67df99aa4e52db608ee4b391af9a1`

Forbidden PNG/EXR/JPG/GLB/GLTF count was `0`; diagnostic-003 remained absent. All eight
diagnostic-001/002 evidence hashes were rechecked unchanged after the probe. A later
contract should first resolve the actual nonzero shift-dependent matrix component from
the full matrix delta, rather than authorize another render or assume a fixed index.

## 2026-07-16 matrix-probe-001 authorization and dry gate

- Coordinator authorization: `docs/workstreams/temple-tr4-coordination/MATRIX_PROBE_001_AUTHORIZATION.md`.
- Independent read-only verdict: `READY_FOR_MATRIX_PROBE_001_CONTRACT`; coordinator log
  status: `TEMPLE-TR4-MATRIX-PROBE-001 AUTHORIZED`.
- This probe is observation-only. Generator and runner gained isolated
  `--matrix-probe` modes; evaluator, camera-probe-001, diagnostics 001/002, contracts,
  runtime, assets, package/configuration, and diagnostic-003 remain frozen.
- Pure Python preflight parsed both authorized scripts, required the exact repository,
  verified all 12 frozen evidence hashes, verified matrix-probe-001 and diagnostic-003
  absent, and hashed the fixed Blender executable without launching it or any version
  subprocess.
- Dry result: `READY_FOR_MATRIX_PROBE`, ordered profiles
  `portrait/desktop/landscape/closeup`, matrix-probe root absent.
- Pre-launch SHA-256 values: Blender executable
  `597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c`;
  generator `6d9d5c47c99e5cd33d8490757b95b4bd4db3e22f0becefba612900879d3a50f5`;
  runner `3273f89208f48ab53702f0352f3624ef53ca44ee651251658ef739d1a544afe1`;
  evaluator remained
  `656ace4f6b1c73e33352523fe36a55ad37f67df99aa4e52db608ee4b391af9a1`.

## 2026-07-16 matrix-probe-001 terminal result

Verdict: **MATRIX_PROBE_BLOCKED** under the frozen exact-significance gate. The sole
Blender 4.5.5 process completed with return code `0`, observed all four profiles, made
zero render calls, and was not retried.

Exact command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py --matrix-probe
```

Every profile recorded `originalShift0=0.0`, `evaluatedShift0=0.0`,
`originalShift1=1.0`, and `evaluatedShift1=1.0`. The intended Python row-major index `6`
binding was present in every profile and mapped to WebGL column-major index `9`:

- portrait `[row=1,column=2,rowMajorIndex=6,webglColumnMajorIndex=9]` response
  `2.000000238418579`; it was the only `abs(delta)>1e-8` element;
- desktop row `1`, column `2` response `2.000000238418579`, plus row `1`, column `1`,
  row-major/WebGL index `5` drift `+2.384185791015625e-07`;
- landscape row `1`, column `2` response `1.999999761581421`, plus index `5` drift
  `-2.384185791015625e-07`;
- closeup row `1`, column `2` response `1.9999998807907104`, plus index `5` drift
  `-2.384185791015625e-07`.

All four index-6 responses are finite and within `1e-6` of `+2.0`. However, the frozen
contract defines every `abs(delta)>1e-8` element as significant and requires exactly one
per profile. The three `2.384185791015625e-07` index-5 floating-point differences therefore
made `consistentBinding=null` and required `MATRIX_PROBE_BLOCKED`; no threshold was changed
or reinterpreted.

The frozen four-file directory contains only:

- `matrix-probe-plan.json`: 2,486 bytes, SHA-256
  `85f11d7a986e8bc5f9ebfed6b240ec13285fa45bf54a12f9af166c0cd2c24ae8`
- `matrix-response.json`: 3,248 bytes, SHA-256
  `40ee6316d267444a8f1874200e8782885fc47d2ad437d8eb2df5ef2eb7ed8f34`
- `blender.log`: 80 bytes, SHA-256
  `505e414d7fa2eb6336d47ed6eeeff397a1e482042ee4ffc322550611e40f3dd5`
- `matrix-probe-status.json`: 679 bytes, SHA-256
  `f6fa513d161f16d9be5cc1347696c15d0900de3cdc2a58f8be0383af92662d0e`

Forbidden image/render/model/export output count was `0`; diagnostic-003 remains absent.
Post-process verification matched all 12 frozen diagnostic/camera-probe/evaluator hashes
and the Blender executable hash. Generator, runner, and evaluator hashes remain the
pre-launch values above. No render, model, export, evaluator, test, build, browser, Git,
or runtime action followed.

## 2026-07-16 diagnostic-003 authorization intake and dry gate

- Coordinator authorization: `docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_003_AUTHORIZATION.md`;
  independent contract verdict `READY_FOR_DIAGNOSTIC_003_CONTRACT`; coordination status
  `TEMPLE-TR4-DIAGNOSTIC-003 AUTHORIZED`.
- C3 changes are limited to the three asset-pipeline scripts and this asset evidence tree.
  Diagnostics `001`/`002`, camera-probe `001`, and matrix-probe `001` remain immutable.
- Generator/runner/evaluator AST parsing passed. The non-writing pure-Python preflight
  machine-verified the authorization files, exact repository/root absence, approved
  reference hash and `941x1672` dimensions, all 15 frozen historical artifact hashes,
  Blender executable SHA-256
  `597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c`,
  construction SHA-256
  `344f6cee493455c20e41981023233f652fa4d94107682251a2efe9efbcb5e90d`,
  C3 schema/order, and 20 exact `tr4-diagnostic-003-*` output records without starting
  Blender or any version subprocess.
- Dry verdict: `READY_FOR_BLENDER`; `diagnostic-003` remained absent. Launch-bound script
  SHA-256 values were generator
  `8eee61e2b9706658a9e77b9ae403d763bb3cb66eb3f05a1ec306d664667a42d0`, evaluator
  `c3b1aecccea5aed3ad8e563ac4d060f0e4f17cdac82daae0d49a37e34e51abdd`, and runner
  `983accdcce00ea9927ca4dcdedeb40105a9fb9a8c4e465e180093e40099ceec5`.
- No Blender, evaluator, render, export, browser, test, build, Git, commit, or push action
  occurred during this dry gate.

## 2026-07-18 C7-T1 generator reconstruction checkpoint

- Coordinator authority is C7-D4 commit `a4d4155`, following independent
  `READY_FOR_DIAGNOSTIC_007_LOOP_CONTRACT` on exact C7-D3 commit `d66e1a5`. The asset
  writer changed only `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`.
- Source checkpoint `a9acb0a343bbd6947ad69064aeca6f283284be3a` reconstructs the C7 road,
  layered canyon, twelve courier poses, game-over pursuer, four canonical hazard
  silhouettes, procedural material graphs, Beer-Lambert beauty compositor, capped
  linear depth, and twenty-output fail-closed scene metrics. File blob SHA-1 is
  `2f386319c15fe320a7e36302b2f28b132d49593b`; canonical construction SHA-256 is
  `6a9735277c29ec32b3e22432b240385bc33993325aaf3422c60ac4f82e0dbd45`.
- The corrected Tide Scar loop uses the thirteen exact actual-world controls from C7-D3,
  identity curve/root transforms, actual world control readback, and projection/safety
  checks over every vertex of the evaluated NURBS/bevel tube. The pursuer audit covers
  all renderable mesh/curve descendants, including the three ridge meshes and
  `dorsalSeam`, for evaluated triangles, world height, unique data, modeling mode, radial
  quality, and primitive separation while retaining exact named-part coverage.
- UTF-8 AST parsing passed at 2,846 lines; `git diff --check` passed; canonical
  construction replay reproduced the SHA-256 above; static output audit found one render
  call site, exactly twenty ordered output records, and no retry path. Independent source
  review found no P0/P1 and returned `SOURCE_READY` against the stable `+1328/-324` diff.
  Its sole residual P2 is that canyon occlusion witnesses use conservative projected AABB
  overlap and AABB-center Euclidean depth; this cannot override the later full manual
  beauty/mask/depth review.
- No Blender import/process, runner, evaluator, diagnostic-007 path, render, export,
  runtime, browser, test, build, push, or unrelated file action occurred. C7-T2 remains
  the next exact runner/evaluator source checkpoint; Blender stays blocked until C7-T2
  and the authorized non-writing dry preflight are both green.

## 2026-07-16 diagnostic-006 terminal result

Verdict: **DIAGNOSTIC_BLOCKED** at stage `render-set`. After coordinator review of the
sole dry result, the one authorized standard command was executed exactly once:

```powershell
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

The runner returned `1` and emitted one JSON line with the terminal reason:

```text
DIAGNOSTIC_BLOCKED local camera axis alignment failed: cameraBinding.profiles[2].orientation
```

Runner stderr was empty. The single Blender 4.5.5 LTS background process returned `0`,
completed all 20 ordered `write_still` calls, and left an empty Blender stderr section.
The evaluator was not invoked because the inherited camera-binding validation failed
before the evaluator gate. There was no retry or second process.

The failing record is the `landscape` orientation. Both serialized local angles were
`2.1073424255447017e-08`; independent recomputation from the serialized actual view
matrix and frozen expected basis produced `2.580956827951785e-08`. The difference for
each angle was `4.736144024070833e-09`, which exceeds the frozen arithmetic-record
agreement tolerance `1e-12` even though both angles are below the separate `1e-5` axis
alignment ceiling. No tolerance was changed or reinterpreted.

The immutable terminal directory contains exactly 27 files, zero directories, and 20
PNGs. Ancillary/status evidence is:

- `preflight.json`: 15,462 bytes, SHA-256
  `f739ff0cbf7d11a100678f9d37cee5ca3f2cc071181359b125f46b615ce3585e`;
- `planned-manifest.json`: 3,791 bytes, SHA-256
  `6912ecee8b60ee77c22eaa1e6e5a9ab26a73e6e9b185423a5e4819ed8807274c`;
- `camera-binding.json`: 11,976 bytes, SHA-256
  `87bf4713b06380f5715b585f3698749f0cb778384ad7f700f3db40c6906202d2`;
- `render-order.json`: 865 bytes, SHA-256
  `4f354bf772f3a7d70fb4131515850ed35503b4a647f4b76dc8de38604ed714a9`;
- `scene-metrics.json`: 876 bytes, SHA-256
  `7f89c5ea9d4457d285a75fbb4cb8aad4cd94dce3598e4773d6a0152e0707ebe6`;
- `blender.log`: 5,010 bytes, SHA-256
  `5ab26ba8855d15e505140588918a171f7ef514581a98673057cc3c3031d495a7`;
- `diagnostic-status.json`: 609 bytes, SHA-256
  `709955632cde56d890d0be378a0ce6d32fa994bf27aa45ad17bfe9f2ab6beb0d`.

Ordered PNG SHA-256 evidence by profile/pass:

- portrait beauty `6835d148278e052bb807c9abde6aa88a2c3d6ca1e5ef065bdd43c50f37e7ffb4`;
  object-id `f9ca7aab496ccc5bc182c788dfd644ef54179786705851fd3ffd9deeb6a54462`;
  road-mask `3b377785b62567a0e14b32bc7e2222ea9eb73e1b8b31e84517e3b2ad36540391`;
  normal `06ece6f8104a47822266525a35add77a99dadfdf294c7acd6ef10f9e48317866`;
  linear-depth `00e1e94fbd2242ddce4ab5f5f95311766ebbb434b97db15594ce692e366ea13f`;
- desktop beauty `ce855424fcc59324668bbd780a6aac56a2ec793b819746c3cda0ef68fdc6e086`;
  object-id `4095c0c6c97e7100677aeb00ef6eaa455999dd6b8a6325b8bbff8a58465eaa6b`;
  road-mask `fd42a94ca16204f94dcf24daeec074d1db4286e474a0ed4601a9d102658109ac`;
  normal `f30253f354ca5770fea3f4027698e0072e04610da6c341d949ecf26d9b8cf066`;
  linear-depth `c0f1bf2a5384bdbb5c84657027ef4306507f970d5f3f96d24111cc9a112e6ca8`;
- landscape beauty `6bb3bf3073fb735148d322c3df09b6ef6d8c914f926a17f97fdd72ef19c2a911`;
  object-id `6a95bc66694e14a6d933633c161c9dbb3f32d9297c6616615e5fb56ef1b64992`;
  road-mask `de62ceb25bd89ab57429d09bfac070e16a4b1a93ac71b1e50122724bbcfa811f`;
  normal `b21fd54af2b0f8ea8f6f4a7d3f3a1c9124920caed95086dbcd051d5ef652b97c`;
  linear-depth `e7ddc3163f841f48eb98b070d4a84edab1f16419a25e4e86cb2283a5c308ac60`;
- closeup beauty `acb211e2fad2fc5729efde5e36df549deec1cb6557abba88f9997e5029d54d7a`;
  object-id `29f066be8252654afb1c2d6a83813b716dbd20cbd35e0b13662ce5884d2ce89e`;
  road-mask `60e11ced6dd27f18d85715c380c77682b0e60af26881de595f0ade02ebe35b64`;
  normal `f61052830945ddce269ab5e14bb126cc3020faa0a4428ea253f7d9f726f87506`;
  linear-depth `158daa1261289d025a38b23f4355a5a5608154d08566f45682f724a31c2b0144`.

The terminal status records `blenderReturnCode=0`, `evaluatorReturnCode=null`, stage
`render-set`, verdict `DIAGNOSTIC_BLOCKED`, the three available ancillary hashes above,
and null evaluation/manifest hashes. `evaluator.log`, `evaluation.json`, and
`manifest.json` are absent by design.

Post-process provenance recheck passed all exact 51 frozen evidence hashes and directory
closures, the reference, authorization, Blender executable SHA-256
`597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c`, and unchanged
launch hashes: generator
`044ce0a47e57cd369693c7b86537d72de53a92ec70474640a89c9891046953a7`, evaluator
`5f400e460657ac848b2037f7ddef545a401601621244f89d4e3d8add90e1681f`, and runner
`4442c44d35ac3dcd47e1c1d70804971f496c47861a8a188efd1d2b23a3e629a9`.
Diagnostic `006` is now immutable. No retry, repair, cleanup, evaluator, export, runtime,
browser, npm/test/build, Git, commit, or push followed.

## 2026-07-16 diagnostic-006 authorization intake and dry gate

- Coordinator authorization:
  `docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_006_AUTHORIZATION.md`;
  coordination status `TEMPLE-TR4-DIAGNOSTIC-006 AUTHORIZED`; the root audit and an
  independent asset-script audit found no P0/P1 and returned dry-only readiness.
- C6 changes are limited to schema/contract/diagnostic/root/output identity, freezing the
  four diagnostic-005 terminal files alongside the 47 older artifacts, replacing the
  insertion-order-dependent anchor guard with an exact key-set guard in all three scripts,
  and validating/returning the fresh object parsed from canonical sorted UTF-8 JSON bytes.
  The canonical C6 object was machine-compared with frozen C5: camera and anchor values,
  matrices, construction, geometry-facing records, materials, lighting, fog, counts,
  evaluator gates, output order, dimensions, and construction SHA-256
  `2ab30e4580a7bdf6b8eeddf8dcd2acc5d17fa3c101aecc9d530cbea535c79c10`
  remain unchanged; output paths differ only by `005` to `006`.
- Generator/evaluator/runner AST and static gates passed. The exact frozen set contained
  51 files (`27` diagnostic-004 and `4` diagnostic-005), all hashes matched before and
  after the non-writing preflight, and the canonical parsed projection-anchor objects used
  lexical key order while passing the insertion-order-insensitive exact-set validators in
  runner, generator, and evaluator.
- The sole non-writing command
  `python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py --dry-preflight` returned
  code `0` and emitted only `READY_FOR_BLENDER`; `diagnostic-006` remained absent.
  Launch-bound SHA-256 values are generator
  `044ce0a47e57cd369693c7b86537d72de53a92ec70474640a89c9891046953a7`, evaluator
  `5f400e460657ac848b2037f7ddef545a401601621244f89d4e3d8add90e1681f`, and runner
  `4442c44d35ac3dcd47e1c1d70804971f496c47861a8a188efd1d2b23a3e629a9`.
- No Blender, evaluator, render, export, runtime, browser, npm/test/build, Git, commit, or
  push action occurred during this dry gate. The sole Blender process remains blocked
  until the coordinator explicitly authorizes it after reviewing this dry result.

## 2026-07-16 diagnostic-005 authorization intake and dry gate

- Coordinator authorization:
  `docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_005_AUTHORIZATION.md`;
  coordination status `TEMPLE-TR4-DIAGNOSTIC-005 AUTHORIZED`; two independent contract
  reviews returned `READY_FOR_DIAGNOSTIC_005_CONTRACT` with no P0/P1.
- C5 changes are limited to schema/contract/diagnostic/root/output identity, the four
  exact camera records and eleven projection anchors, explicit Y-up camera basis and
  camera-binding schema v2, closed key/fill/contact orientation, world/fog records,
  placement-only `abs_tol=1e-6`, and the added evaluator raster/ROI/perspective gates.
  Geometry, topology, materials, poses, semantic roots, output order/count, and all C4
  evidence remain frozen.
- Generator/evaluator/runner AST parsing passed. The pure-Python static audit verified
  C5 authorization/current-task/coordination state, reference hash and `941x1672`
  dimensions, Blender executable hash, all 47 frozen historical artifacts including the
  exact 27-file diagnostic-004 directory, construction SHA-256
  `2ab30e4580a7bdf6b8eeddf8dcd2acc5d17fa3c101aecc9d530cbea535c79c10`,
  all camera projection/basis/order gates, light/fog/transmittance records, and absence of
  `diagnostic-005` without starting Blender or any version subprocess.
- Independent post-patch review found two P1 closure gaps before Blender: exact C4 scene
  counts/ordered root-child counts and arithmetic binding of the two local-camera angles.
  Both were corrected; scene metrics now require exact `400` mesh objects, `45224` source
  triangles, `10` beauty materials, and children `[215,90,46,27,12,10,11,21,2]`, while
  camera and light alignment fields are independently recomputed from serialized matrices
  and vectors. The continued audit found one additional P1: runner Python provenance was
  dynamic. C5 now freezes runner/evaluator Python `3.12.0` and rejects any runtime or
  preflight mismatch before Blender.
- Final non-writing command
  `python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py --dry-preflight`
  returned the sole stdout line `READY_FOR_BLENDER`; `diagnostic-005` remained absent.
  Launch-bound SHA-256 values are generator
  `653fea54fc08a339d7c847e841a4577e59a56641e761bf07ee2a71b601302612`, evaluator
  `414cfdc2ca90c113172a9984f09feadc69daa6ee15e197f517c1e8c5eeebcd07`, and runner
  `52222668baac8555a4dfecd7cd32dc90db7aef946c304f93549791fd1c164faf`.
- No Blender, evaluator, render, export, runtime, browser, npm/test/build, Git, commit, or
  push action occurred during the C5 static/dry gate. The sole Blender process remains
  blocked until final independent post-patch review is `READY`.

## 2026-07-16 diagnostic-005 terminal result

Verdict: **DIAGNOSTIC_BLOCKED** at stage `blender`. After independent final review
returned `READY_FOR_C5_BLENDER`, the sole authorized standard command was executed once:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

The runner exited `1`. Its one Blender 4.5.5 LTS background process exited `1` during
generator input validation, before scene construction and before the first
`write_still`. It was not retried. The evaluator was not invoked. First and terminal
Blender error:

```text
RuntimeError: camera/anchor schema mismatch: portrait
```

The frozen `preflight.json` is canonical JSON with lexicographically sorted object keys.
Consequently the `projectionAnchors` object read by Blender has sorted keys, while the
generator's C5 input guard compared `list(record["projectionAnchors"].keys())` to the
authored insertion-order list. That order-sensitive comparison rejected the otherwise
closed portrait anchor key set. This is a terminal generator/schema-boundary defect for
C5; the no-retry contract forbids repairing or relaunching diagnostic `005`.

The immutable diagnostic directory contains exactly four files, zero directories, and
zero PNGs:

- `preflight.json`: 15,462 bytes, SHA-256
  `3f7997793ea9629cc17bdb4cfe186eed4d505273363105f90e9bec3778662659`;
- `planned-manifest.json`: 3,791 bytes, SHA-256
  `933890d49f728410b11c723be7c7ffbfe6f724d27018dabda85fc2ba45035437`;
- `blender.log`: 907 bytes, SHA-256
  `68f20d179729ff363aa142e76f55a530690ce156a6378552b981c0afa1abdd94`;
- `diagnostic-status.json`: 363 bytes, SHA-256
  `e31e89d92fc5a5ed0f3e93acda637ee15ab384141ba49f29bbe487f178431752`.

The terminal status records `blenderReturnCode=1`, `evaluatorReturnCode=null`, stage
`blender`, verdict `DIAGNOSTIC_BLOCKED`, and all camera/render/scene/evaluation/manifest
hash fields `null`. `camera-binding.json`, `render-order.json`, `scene-metrics.json`,
`evaluator.log`, `evaluation.json`, and `manifest.json` are absent by design.

Launch-bound script hashes remained unchanged: generator
`653fea54fc08a339d7c847e841a4577e59a56641e761bf07ee2a71b601302612`, evaluator
`414cfdc2ca90c113172a9984f09feadc69daa6ee15e197f517c1e8c5eeebcd07`, and runner
`52222668baac8555a4dfecd7cd32dc90db7aef946c304f93549791fd1c164faf`.
The runner's failure path completed post-process script/reference/authorization/Blender
executable and 47-file frozen-evidence provenance checks without appending any provenance
failure. No retry, script repair, threshold change, export, runtime, browser,
npm/test/build, Git, commit, or push followed.

Recommended next bounded coordinator action: freeze all four C5 hashes above, review the
canonical-key-order defect, and authorize a fresh diagnostic ID only if a new contract
permits replacing the order-sensitive anchor-key comparison with an exact key-set check.
Diagnostic `005` must remain immutable.

## 2026-07-16 diagnostic-004 terminal result

Verdict: **DIAGNOSTIC_BLOCKED** at stage `render-set`. The sole Blender 4.5.5 process
returned `0`, completed the four inherited camera-binding calibrations, and performed all
20 ordered `write_still` calls. It was not retried. The runner accepted the closed camera
binding and render order, then stopped on the inherited exact scene-metrics placement gate;
the evaluator was not invoked.

Exact command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

First and terminal error:

```text
DIAGNOSTIC_BLOCKED scene semantic root placement mismatch: TR4_Pursuer_Cinematic
```

The frozen construction value is `[0,0,2.4]`; Blender serialized both the semantic-root
translation and separate `pursuerBookendRoot` as `[0.0,0.0,2.4000000953674316]`. Mesh
count `400`, source triangles `45224`, beauty materials `10`, all nine root names/order,
runner root, road top, and metrics verdict were otherwise present. No tolerance was added
and no output was reused or passed to the evaluator.

The terminal directory contains exactly 27 files: seven ancillary/status files plus the
20 C4 PNGs. Ancillary evidence is:

- `preflight.json`: 13,994 bytes, SHA-256
  `b497e349ca936cd83bc84fcfc5b2cd7d03bbf5ff92665b29902cd66d9bd4c6ae`;
- `planned-manifest.json`: 3,791 bytes, SHA-256
  `d94c51550da7157d64f6f2979d3d8f7c9fa5dbdc260c67b147cdbbc51dd5e524`;
- `camera-binding.json`: 5,322 bytes, SHA-256
  `c25715dfa1766be1299a9f8aa51ff236badb16bed7107b752a296e28fa1d5196`;
- `render-order.json`: 865 bytes, SHA-256
  `b0fe59a3a2576c9dd671cb2f32821854c75a466a55875b763c528a2898444810`;
- `scene-metrics.json`: 876 bytes, SHA-256
  `7f89c5ea9d4457d285a75fbb4cb8aad4cd94dce3598e4773d6a0152e0707ebe6`;
- `blender.log`: 5,010 bytes, SHA-256
  `014611394e378b600c646b066641a250ec597a1ecc1fc25d20be8da471c89783`;
- `diagnostic-status.json`: 597 bytes, SHA-256
  `f10fea75788c3a1c434b6461c99be1cf01b5ba0e86bfa4bd1f9843a2b16883a6`.

Ordered PNG SHA-256 evidence by profile/pass:

- portrait beauty `1bfb7de64fc27042f03b952313a2b7b5af89fb306b394521f109c8f710001be3`;
  object-id `835b7828fa6de0c8332d173e74301e55e98727ec707e21d6d8861ba81a3d5341`;
  road-mask `0b1c192346f9219dc717f1a28201c7a66a7ced6a95096ad7b2587506873a9e73`;
  normal `37eb27c447a7f3cd2c8d61bd88ad003dc94a3eb0edf51a0a914877b58da6fc03`;
  linear-depth `834ee04024806454850a55bac5d46193311f3a9ae1a3679d2354ff2929581876`;
- desktop beauty `0c863ea2e4ed258f0c5536fb6241a78ff729a3af7a201b9d2bedbc1daa89ffdd`;
  object-id `2823a2bf1082934af1e54bf2e205277ee8a4d88fb7495b784e3c5ddbe99d4e27`;
  road-mask `5b234cdef30661af186514ae6279f23f1a90ea7b97ebbf043eca439a04bc3be9`;
  normal `9f270e33c893a9620bfbf0dd2e05867e1dbed414698f8289b5e1ee4259d10cb6`;
  linear-depth `29842153c9a0dd2492f554413d7dcf784e890ddcba5e636a712de7b8d9f3a504`;
- landscape beauty `c2e85329435a559d5f00ba78216cf2203e3c76e813c4aa64478902b99f6a4aa3`;
  object-id `8fefcbe7f9f5180400487280fa188c25228ca9e06472844cccfc350070f06843`;
  road-mask `820ee913f1e8b86237a28f5c27960c0ee3f8bd865718c06a784a1792dec93425`;
  normal `3001e4f5bab4179e62f6b225a29e19c302ddabec7568515ff91de59612a72b03`;
  linear-depth `26fde0d06dc75e91825aaff13aa4b324be4fbb1e17dc4c1a25f9b4ce61773b58`;
- closeup beauty `baf0402bdc4c1e383a9160650d9658c14823613170b264005d9ef2104843a6fe`;
  object-id `7c6fe7a705a785b1f254048f6e3fec5d692587a9c9b04ba4d0934b09f6449504`;
  road-mask `b158134b6d635a42401aa0dd516e6d41c43e6c21180ed8b091401af3bac134fd`;
  normal `2bf07d60cf796331231aaaaf2dbae6dd1a15a3448ff95b0f0e9035527a95fc7b`;
  linear-depth `9c05e52d6efcd4be832b2fa6f8551c00bebfa77e4ca61c660e23f939d63c40a8`.

The terminal status records Blender return code `0`, evaluator return code `null`, all
three available ancillary hashes, stage `render-set`, and verdict `DIAGNOSTIC_BLOCKED`;
evaluation/manifest hashes remain `null`. `evaluator.log`, `evaluation.json`, and
`manifest.json` are absent. Launch hashes remained unchanged, all 20 historical frozen
artifacts including diagnostic-003 revalidated, and no export, runtime, browser, test,
build, Git, commit, push, or manual visual acceptance followed. Diagnostic `004` is now
immutable; any metric-policy correction or fresh evaluation path requires a new bounded
coordinator authorization and diagnostic ID.

Dry-gate correction before launch: a final fail-path closure moved preflight/plan writes
inside the terminal-status guard, so the runner changed after the first dry record. AST
parsing and the full non-writing preflight were rerun green with `diagnostic-003` still
absent. The final launch-bound runner SHA-256 is
`75bb844985bc48ac3e401a399753ca00acc3fb1020dbf4d679d342db1d6e84ad`;
generator/evaluator hashes remain `8eee61e2b9706658a9e77b9ae403d763bb3cb66eb3f05a1ec306d664667a42d0`
and `c3b1aecccea5aed3ad8e563ac4d060f0e4f17cdac82daae0d49a37e34e51abdd`.

Final pre-launch correction: closed-schema integer typing and failure-status raw ancillary
hash capture were added after the preceding audit note. The complete AST and non-writing
preflight gates were rerun green with the root absent. The actual final launch hashes are
generator `d602d3467595893330cf97e84e5d8613884defebb2e7d2d111c89f6c252e3c57`, evaluator
`72c3d4d07db63ff7f9fff377e3c81fa2f34cba04c652b7c933367690a56e8f7f`, and runner
`3a1af661e814c69dbf74868053afed15d75242a66e7a22d9b387687fbf4a7044`.

## 2026-07-16 diagnostic-003 terminal result

Verdict: **DIAGNOSTIC_BLOCKED** at stage `blender`. The sole Blender 4.5.5 process
exited `1` and was not retried. It completed all four closed camera calibrations and
atomically wrote `camera-binding.json` with `renderCallCountAtWrite=0`, then stopped
before the first `write_still`; PNG count is `0` and the evaluator was not invoked.

Exact command:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py
```

First and terminal error:

```text
TypeError: bpy_struct: item.attr = val: enum "NONE" not found in ('None', 'AgX - Punchy', 'AgX - Greyscale', 'AgX - Very High Contrast', 'AgX - High Contrast', 'AgX - Medium High Contrast', 'AgX - Base Contrast', 'AgX - Medium Low Contrast', 'AgX - Low Contrast', 'AgX - Very Low Contrast')
```

The error occurred in `set_view_transform("beauty")` when the Blender RNA enum
identifier fallback returned `"NONE"` but the accepted property value was `"None"`.
No fallback, threshold change, script repair, second process, or evaluator call followed.

The four camera-binding records independently established the intended C3 mapping:

- portrait: response `2.000000238418579`, max calibration off-target `0`, dominance
  `2000000238418.579`, target error `7.74860382107834e-09`, max projection error
  `3.580185783391699e-07`;
- desktop: response `2.000000238418579`, max calibration off-target
  `2.384185791015625e-07`, dominance `8388609`, target error
  `2.086162566999893e-08`, max projection error `7.764082377015313e-08`;
- landscape: response `1.999999761581421`, max calibration off-target
  `2.384185791015625e-07`, dominance `8388607`, target error
  `6.005167961162239e-08`, max projection error `7.755377051665846e-08`;
- closeup: response `1.9999998807907104`, max calibration off-target
  `2.384185791015625e-07`, dominance `8388607.5`, target error `0`, max projection
  error `6.406311081619265e-08`.

The frozen diagnostic directory contains exactly five files:

- `preflight.json`: 13,994 bytes, SHA-256
  `4963f1aac82cea6a57d1c0872db980530c30cec38d1686ab4a49016484216008`;
- `planned-manifest.json`: 3,791 bytes, SHA-256
  `b89b2e91d4ab90d3ece2157c00a9c346593ac0a03486d8885a587d36ec6da676`;
- `camera-binding.json`: 5,322 bytes, SHA-256
  `c75c33086a343b1e473613c4fa7a69bc005d8610fa8163d1f1b9c94ec672c0e8`;
- `blender.log`: 1,202 bytes, SHA-256
  `9ec64ef0b9988ae156fcfa4ae94eec472891141891c9c9bdebe370f27ce1b31c`;
- `diagnostic-status.json`: 425 bytes, SHA-256
  `a9aea45e9842e437c1b459be56d27da6ae5bf7d514ed10939dc425843aab71ba`.

The terminal status records Blender return code `1`, evaluator return code `null`, the
camera-binding hash above, all unavailable downstream hashes as `null`, stage `blender`,
and verdict `DIAGNOSTIC_BLOCKED`. `render-order.json`, `scene-metrics.json`,
`evaluator.log`, `evaluation.json`, and `manifest.json` are absent. Launch script hashes
remain the final preflight values; the runner's post-process provenance and all 15 frozen
historical artifact checks passed. No render, export, browser, test, build, Git, commit,
push, runtime action, or manual visual acceptance followed. Diagnostic `003` is now
immutable; any correction requires a new coordinator-authored diagnostic ID and bounded
authorization.

## 2026-07-16 diagnostic-004 authorization intake and dry gate

- Coordinator authorization: `docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_004_AUTHORIZATION.md`;
  independent contract verdict `READY_FOR_DIAGNOSTIC_004_CONTRACT`; coordination status
  `TEMPLE-TR4-DIAGNOSTIC-004 AUTHORIZED`.
- C4 changes are limited to schema/contract/diagnostic/root/output identity and the exact
  Blender view settings correction. Beauty assigns and reads back `AgX` plus
  `AgX - Medium High Contrast`; the four data passes assign and read back `Raw` plus
  `None`. The diagnostic function contains no RNA enum inspection, `preferred`, `NONE`,
  or fallback selection. All C3 camera, scene, ancillary, evaluator, raster, allowlist,
  status, single-process, and no-retry gates remain unchanged.
- Generator/runner/evaluator AST parsing passed. The non-writing pure-Python preflight
  machine-verified C4 authorization/current-task/coordination status, the approved
  reference and Blender executable, construction SHA-256
  `344f6cee493455c20e41981023233f652fa4d94107682251a2efe9efbcb5e90d`,
  all 20 frozen historical artifact hashes including the five diagnostic-003 files, the
  exact 20 C4 output records, the closed view function, and absence of diagnostic-004.
- Dry verdict: `READY_FOR_BLENDER`; diagnostic-004 remained absent. Final launch-bound
  SHA-256 values are generator
  `0a0a12ff00f85cf222e7e26ace185ef3ae8c8206b8d2c814a06f87448aff4169`, evaluator
  `ce3277cf0a9b65fa97c98c374094254dbd7f5e908b08f1d15c6f273eaa2a64bd`, and runner
  `ec174a6f5e1eca8b8315e6e8c4045542e8c9ade01af3eb6ae1a02f609a1a306d`.
- No Blender, evaluator, render, export, browser, test, build, Git, commit, or push action
  occurred during this dry gate.
