# TEMPLE-TR4 no-render camera response probe 001

Status: **AUTHORIZED.** Independent read-only review returned `READY_FOR_CAMERA_PROBE_001_CONTRACT`. This is a narrow Blender API probe, not a diagnostic render and not authorization for diagnostic `003`.

## Evidence and root cause

- Diagnostic `001` and `002` are immutable `DIAGNOSTIC_BLOCKED`; each used exactly one Blender 4.5.5 process, stopped before its first `write_still`, produced zero PNG, and did not call the evaluator.
- C2 corrected the matrix index to `[2][1]`, but b0/b1 remained identical because `Object.calc_matrix_camera(depsgraph, ...)` reads `DEG_get_evaluated(depsgraph, ob)`. The script changed the original camera data twice without tagging/updating the dependency graph, so both calls saw the last evaluated copy.
- Blender 4.5.5 primary source: `https://github.com/blender/blender/blob/v4.5.5/source/blender/makesrna/intern/rna_object_api.cc` (`rna_Object_calc_matrix_camera`), `https://github.com/blender/blender/blob/v4.5.5/source/blender/blenlib/BLI_math_matrix.hh` (`mat[2][1]`), and `https://github.com/blender/blender/blob/v4.5.5/source/blender/blenkernel/intern/camera.cc` (`shifty` viewplane offset).

## Exact write and process scope

The same asset writer may modify only:

- `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`
- `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py`
- `docs/workstreams/temple-tr4-asset/THREAD_LOG.md`
- new `docs/workstreams/temple-tr4-asset/camera-probe-001/**`

The evaluator script, diagnostics `001/002`, contracts, runtime, assets, package/configuration, browser evidence, and all A3-A6 paths are read-only.

One pure-Python preflight first requires the probe root not to exist; rechecks Blender executable/version, generator/runner hashes, four frozen camera records, and path containment; then atomically writes `probe-plan.json`. Only `READY_FOR_CAMERA_PROBE` permits exactly one Blender 4.5.5 background process. No `bpy.ops.render.render`, scene modeling, image, GLB, texture, evaluator, npm, test, build, browser, Git, or runtime action is allowed.

## Exact evaluated-camera sequence

The generator exposes a `--camera-probe` mode. It creates one temporary camera and, for profiles in exact order `portrait`, `desktop`, `landscape`, `closeup`, applies the frozen diagnostic resolution, FOV, sensor fit/height, near/far, position, target, and up vector. For each profile it executes exactly this sequence:

1. Set `camera.data.shift_y=0.0`; call `camera.data.update_tag()`; call `bpy.context.view_layer.update()`; obtain a fresh `bpy.context.evaluated_depsgraph_get()`; calculate `matrix0=camera.calc_matrix_camera(...)`; record `b0=matrix0[2][1]`.
2. Set `camera.data.shift_y=1.0`; repeat `update_tag()`, `view_layer.update()`, and fresh depsgraph lookup; calculate `matrix1`; record `b1=matrix1[2][1]`.
3. Require finite `response=b1-b0` and `abs(response)>=1e-9`.
4. Set `solvedShift=(lensShiftY-b0)/response`; repeat the same tag/update/fresh-depsgraph sequence; calculate `matrixSolved`; record `actual=matrixSolved[2][1]` and `error=actual-lensShiftY`.
5. Require every matrix element and scalar finite, `abs(error)<=1e-6`, and no other camera parameter changed.

The process writes only `camera-response.json` through a temporary sibling plus atomic replace. Its closed top-level keys are `schemaId="tide-relay.temple-tr4.camera-probe"`, `schemaVersion=1`, `blenderVersion="4.5.5 LTS"`, `generatorSha256`, `runnerSha256`, `profiles`, `renderCallCount=0`, and `verdict`. Each ordered profile record has exactly `profile`, `resolution`, `lensShiftY`, `b0`, `b1`, `response`, `solvedShift`, `actual`, `error`, `matrix0`, `matrix1`, and `matrixSolved` (each matrix is a row-major ordered array of 16 finite numbers). Maximum verdict is `READY_FOR_DIAGNOSTIC_003_CONTRACT`.

The runner captures stdout/stderr in `blender.log`, verifies exactly one response JSON and zero PNG/EXR/JPG/GLB/GLTF files, then writes `probe-status.json` with process return code, the four response errors, output hashes/bytes, `renderCallCount=0`, and the same verdict. Any failure is `CAMERA_PROBE_BLOCKED`; the process is not retried. Diagnostic `003` remains unauthorized until independent read-only review verifies these artifacts and the coordinator writes a separate authorization.
