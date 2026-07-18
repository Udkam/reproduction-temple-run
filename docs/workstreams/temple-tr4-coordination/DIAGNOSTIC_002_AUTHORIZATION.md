# TEMPLE-TR4 diagnostic 002 camera-binding correction

Status: **AUTHORIZED.** Independent read-only review returned `READY_FOR_DIAGNOSTIC_002_CONTRACT`. This is a new bounded diagnostic, not a retry or rewrite of diagnostic `001`.

## Why a new ID is required

Diagnostic `001` is frozen `DIAGNOSTIC_BLOCKED`. Its sole Blender 4.5.5 process exited before the first `write_still` because the C1 contract bound vertical lens shift to `calc_matrix_camera(...)[1][2]`, whose `shift_y` response was zero. It produced no PNG and did not invoke the evaluator. Every file in `docs/workstreams/temple-tr4-asset/diagnostic-001/**` is immutable evidence.

The upstream Blender projection implementation stores the off-centre vertical perspective term at `mat[2][1]`: `projection::perspective()` assigns `(top + bottom) / (top - bottom)` there, while camera `shifty` offsets the viewplane's `ymin/ymax`. Primary source:

- `https://github.com/blender/blender/blob/v4.5.5/source/blender/blenlib/BLI_math_matrix.hh`
- `https://github.com/blender/blender/blob/v4.5.5/source/blender/blenkernel/intern/camera.cc`
- `https://github.com/mrdoob/three.js/blob/dev/src/math/Matrix4.js`

This also corresponds to Three.js column-major `projectionMatrix.elements[9]` (column `2`, row `1`). C2 therefore measures and validates Blender's `[2][1]`, not `[1][2]`.

## Exact C2 schema transformation

`TR4_PREFLIGHT_SCHEMA.md` remains the immutable definition that diagnostic `001` used. Diagnostic `002` inherits every closed field, array order, frozen numeric value, construction object, material record, budget, scene record, camera record, pass definition, manual gate, and fail-closed rule from that file, with exactly these replacements and no others:

1. `schemaVersion` becomes integer `2`.
2. `contractVersion` becomes `TEMPLE-TR4-C2`.
3. Diagnostic root becomes exactly `docs\workstreams\temple-tr4-asset\diagnostic-002` and must not exist before the C2 preflight succeeds.
4. Scene IDs remain unchanged; each of the 20 output records keeps its index/profile/pass/scene/width/height but replaces `tr4-diagnostic-001-` with `tr4-diagnostic-002-` in `relativePath` and filename.
5. Planned/evaluation/manifest records identify `diagnosticId="002"`.
6. Camera response uses `matrix[2][1]`: `b0=calc_matrix_camera(shift_y=0)[2][1]`, `b1=calc_matrix_camera(shift_y=1)[2][1]`, rejects `abs(b1-b0)<1e-9`, sets `Camera.shift_y=(lensShiftY-b0)/(b1-b0)`, and requires `abs(calc_matrix_camera(...)[2][1]-lensShiftY)<=1e-6` before the first render.
7. Script SHA-256 values are recomputed after the C2 correction. Diagnostic `001` script hashes remain only in its frozen preflight.

No threshold, camera pose, FOV, lens-shift target, geometry, material, light, scene state, output count, image resolution, evaluator rule, or manual visual bar changes.

## Bounded execution

- The same asset workstream writer may modify only the three authorized TR4 scripts and append `docs/workstreams/temple-tr4-asset/**`.
- It first performs a non-writing C2 dry preflight and static parse. Only `READY_FOR_BLENDER` permits one new Blender 4.5.5 background process.
- That process still performs exactly 20 ordered `write_still` calls, followed by exactly one evaluator call only after all 20 outputs verify.
- Any C2 failure writes `DIAGNOSTIC_BLOCKED` under `diagnostic-002` and stops. There is no automatic retry, output reuse, fallback camera, export, runtime integration, browser, npm, build, test, or Git activity.
- Success is at most `READY_FOR_MANUAL_REVIEW`; the independent visual-review workstream remains mandatory.
