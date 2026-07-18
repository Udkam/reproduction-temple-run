# TEMPLE-TR4 no-render full-matrix mapping probe 001

Status: **AUTHORIZED.** Independent read-only review returned `READY_FOR_MATRIX_PROBE_001_CONTRACT` after all preflight-process, nested-schema, and evidence-consistency findings were closed. This permits only the single zero-render observation process below; it is not permission to render, model, export, evaluate, test, build, capture a browser, or create diagnostic `003`.

## Frozen evidence and corrected premise

- Diagnostic `001` and `002` remain immutable `DIAGNOSTIC_BLOCKED`; each stopped before its first `write_still`, produced zero PNG, and did not invoke the evaluator.
- Camera probe `001` remains immutable `CAMERA_PROBE_BLOCKED`. Its sole Blender 4.5.5 process performed `shift_y write -> Camera.update_tag -> view_layer.update -> fresh evaluated_depsgraph_get -> calc_matrix_camera`, then stopped at portrait because Python `matrix[2][1]` was `0.0` for both shifts. It made zero render calls and created only `probe-plan.json` (`4cf25d218366661f01cab8ff6d3cd66809b9883b25a57b74548b9d99d65a5802`), `blender.log` (`e32fb009d0c551faaaaa8d76f314aeadfb03fee696e226a6ca01b115435519cf`), and `probe-status.json` (`feaec46ada7ab64e579751d884d68b22a7a96f4467d59037feb373d59b8979dc`).
- Blender's RNA function copies the internal `params.winmat` into an RNA `PROP_MATRIX`, while Python exposes a `mathutils.Matrix` whose default indexed access is by rows. The previous contracts did not prove that an internal C/C++ subscript pair could be copied unchanged into Python access. This proposal observes the complete matrix before selecting a binding.
- All diagnostic `001`/`002` and camera-probe `001` artifact hashes, plus the evaluator hash, must match `docs/workstreams/temple-tr4-asset/THREAD_LOG.md` before and after the probe.

## Exact writer scope

The existing Temple TR4 asset writer may modify only:

- `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`
- `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py`
- `docs/workstreams/temple-tr4-asset/THREAD_LOG.md`
- new `docs/workstreams/temple-tr4-asset/matrix-probe-001/**`

`evaluate_tide_scar_tr4_pack.py`, every diagnostic directory, camera-probe `001`, source assets, runtime/UI/core files, packages, configuration, root changelog, and all other paths are read-only.

## Preflight and single-process limit

A pure-Python non-writing dry preflight must parse both authorized scripts, require the exact repository root, verify the frozen Blender executable path plus its byte-level SHA-256 without launching it, verify every frozen evidence hash, verify that `diagnostic-003` and `matrix-probe-001` do not exist, and freeze the four camera records in order `portrait`, `desktop`, `landscape`, `closeup`. The preflight may not start Blender, run `blender --version`, or launch any version-probe subprocess. The expected version remains `4.5.5 LTS`; the sole background process must verify `bpy.app.version_string` internally before any observation and record the actual version in the response. A mismatch is terminal `MATRIX_PROBE_BLOCKED` with no retry. Only an independent verdict of `READY_FOR_MATRIX_PROBE_001_CONTRACT` followed by a coordinator status change to `AUTHORIZED` may permit the runner to atomically create `matrix-probe-plan.json` and start exactly one Blender background process. No retry is allowed.

`matrix-probe-plan.json` has exactly `schemaId="tide-relay.temple-tr4.matrix-probe-plan"`, `schemaVersion=1`, `probeId="001"`, `repoRoot`, `blenderExecutable`, `blenderExecutableSha256`, `expectedBlenderVersion="4.5.5 LTS"`, `scripts`, `frozenEvidence`, `cameras`, and `verdict="READY_FOR_MATRIX_PROBE"`. `scripts` contains exactly generator and runner absolute paths plus pre-launch hashes. `frozenEvidence` contains exactly the named hashes for all diagnostic `001`/`002` artifacts, camera-probe `001` artifacts, and evaluator. Every ordered camera record has exactly `profile`, `diagnosticResolution`, `position`, `target`, `verticalFovDegrees`, `near`, and `far`, copied from the accepted C2 plan; `diagnosticResolution` is exactly two positive integers `[width,height]`, `position` and `target` are exactly three finite numbers, and no target projection or selected matrix index is included.

The process may create one temporary Camera object only. It must not create scene geometry, materials, lights, worlds, images, render settings beyond the frozen resolution fields, animation, `.blend`, GLB/GLTF, or textures, and it must never call a render operator.

## Exact observation sequence

For each frozen profile, apply only its diagnostic resolution, pixel aspect, position, look target, perspective type, vertical sensor fit, 32 mm sensor height, calculated vertical-FOV lens, and near/far planes. Then perform both observations without early exit:

1. Set original `camera.data.shift_y=0.0`; call `camera.data.update_tag()`; call `bpy.context.view_layer.update()`; obtain a fresh dependency graph; obtain `camera.evaluated_get(depsgraph)`; record original and evaluated `shift_y`; call `camera.calc_matrix_camera` with that same dependency graph; record all 16 Python `matrix[row][column]` values in row-major index order.
2. Repeat the exact sequence with original `camera.data.shift_y=1.0` and record the second original/evaluated values and full matrix.
3. Compute all 16 finite `matrix1-matrix0` values in row-major index order. Record every and only significant element with `abs(delta)>1e-8` as exactly `{row,column,rowMajorIndex,webglColumnMajorIndex,delta}`, ordered by `rowMajorIndex`, where `rowMajorIndex=row*4+column`, `webglColumnMajorIndex=column*4+row`, and each `delta` equals that same `difference[rowMajorIndex]` within `1e-12`.

The probe observes mapping only. It must not solve a production `camera.data.shift_y`, mutate the frozen target projection values, or claim render correctness.

## Closed outputs and verdict

The new directory may contain only these four files; a completed Blender observation has all four, while a process-level failure before atomic response writing may omit only `matrix-response.json`:

- `matrix-probe-plan.json`
- `matrix-response.json`
- `blender.log`
- `matrix-probe-status.json`

`matrix-response.json` has closed top-level keys `schemaId="tide-relay.temple-tr4.matrix-probe"`, `schemaVersion=1`, `probeId="001"`, `blenderVersion="4.5.5 LTS"`, `generatorSha256`, `runnerSha256`, `profiles`, `consistentBinding`, `renderCallCount=0`, and `verdict`. Each of exactly four ordered profile records has only `profile`, `resolution`, `originalShift0`, `evaluatedShift0`, `originalShift1`, `evaluatedShift1`, `matrix0`, `matrix1`, `difference`, and `significantElements`; `resolution` is exactly the profile's two positive diagnostic integers, every shift is finite, and every matrix/difference is an ordered list of 16 finite numbers. Each `difference[i]` must equal `matrix1[i]-matrix0[i]` within `1e-12`.

`consistentBinding` is either `null` or exactly `{row,column,rowMajorIndex,webglColumnMajorIndex,responses}`. `responses` is exactly four ordered records `{profile,response}` for `portrait`, `desktop`, `landscape`, `closeup`. It is non-null only when every profile has both original and evaluated shifts `0.0` and `1.0` within `1e-8`; has exactly one significant element; uses the same Python binding `row=1,column=2,rowMajorIndex=6`; maps to `webglColumnMajorIndex=9`; has its response exactly equal to the bound `difference[6]` within `1e-12`; and has a finite response within `1e-6` of the Blender 4.5.5 vertical-fit prediction `+2.0`. The maximum success verdict is `READY_FOR_CAMERA_BINDING_CONTRACT`; otherwise the verdict is `MATRIX_PROBE_BLOCKED`. The response is written even on a blocked mapping so the complete observation is preserved.

The runner captures stdout/stderr in `blender.log`, rejects any file outside the four-name allowlist and any PNG/EXR/JPG/JPEG/BLEND/GLB/GLTF/KTX/KTX2/DDS/TGA/TIFF texture or export output, verifies `renderCallCount=0`, and writes `matrix-probe-status.json`. That status has exactly `schemaId="tide-relay.temple-tr4.matrix-probe-status"`, `schemaVersion=1`, `probeId="001"`, `processReturnCode`, `outputs`, `consistentBinding`, `renderCallCount=0`, `reason`, and `verdict`; `outputs` contains ordered records exactly `{relativePath,byteCount,sha256}` for every file that existed before the status itself. A ready status requires process return code `0`, a response that independently passes every matrix invariant above, byte-for-byte identical response/status `consistentBinding`, and matching `READY_FOR_CAMERA_BINDING_CONTRACT` verdicts. Any script/process/schema/path failure is `MATRIX_PROBE_BLOCKED`. Diagnostic `003` remains unauthorized after this probe; success only permits a separately reviewed camera-binding and diagnostic-C3 contract.
