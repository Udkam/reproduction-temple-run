# TEMPLE-TR4 diagnostic 004 Blender look-value correction

Status: **AUTHORIZED.** Independent read-only review returned `READY_FOR_DIAGNOSTIC_004_CONTRACT` with no P0/P1. This permits only the exact look-value correction, one C4 Blender process, 20 ordered PNGs, and one evaluator under the inherited C3 gates; it does not authorize export, runtime integration, tests, builds, browser capture, Git, commit, or push.

## Frozen C3 evidence and exact root cause

Diagnostic `003` is immutable `DIAGNOSTIC_BLOCKED`. Its sole Blender 4.5.5 process completed all four camera-binding calibrations, wrote no PNG, did not invoke the evaluator, and stopped before the first `write_still`. Its exact five files are:

- `preflight.json`: `4963f1aac82cea6a57d1c0872db980530c30cec38d1686ab4a49016484216008`
- `planned-manifest.json`: `b89b2e91d4ab90d3ece2157c00a9c346593ac0a03486d8885a587d36ec6da676`
- `camera-binding.json`: `c75c33086a343b1e473613c4fa7a69bc005d8610fa8163d1f1b9c94ec672c0e8`
- `blender.log`: `9ec64ef0b9988ae156fcfa4ae94eec472891141891c9c9bdebe370f27ce1b31c`
- `diagnostic-status.json`: `a9aea45e9842e437c1b459be56d27da6ae5bf7d514ed10939dc425843aab71ba`

The terminal traceback is `TypeError: ... enum "NONE" not found in ('None', 'AgX - Punchy', ..., 'AgX - Medium High Contrast', ...)`. The C3 code inspected static RNA enum items and selected identifier `"NONE"`, but this runtime property accepts display values such as `"None"` and the named AgX looks. Camera math, scene construction, geometry, materials, lighting, and evaluator gates did not cause this failure.

## Exact C4 changes

C4 inherits every C3 field, construction hash, camera-binding sequence/tolerance, ancillary schema/hash, allowlist, metric gate, output pass, pixel threshold, failure rule, manual-review requirement, and single-process/single-evaluator boundary, with exactly these changes:

1. Preflight `schemaVersion=4`, `contractVersion="TEMPLE-TR4-C4"`, diagnostic root `docs\workstreams\temple-tr4-asset\diagnostic-004`, `diagnosticId="004"`, and output prefix `tr4-diagnostic-004-` in all 20 ordered records.
2. `camera-binding.json`, planned manifest, evaluation, manifest, and diagnostic status identify diagnostic `004`; schema IDs and all other closed keys remain unchanged.
3. `set_view_transform("beauty")` sets exposure `0.0`, gamma `1.0`, dither `0.0`, `view_transform="AgX"`, and `look="AgX - Medium High Contrast"`, then requires exact readback of both strings.
4. `set_view_transform` for `object-id`, `road-mask`, `normal`, and `linear-depth` sets the same exposure/gamma/dither, `view_transform="Raw"`, and `look="None"`, then requires exact readback of both strings.
5. Executable diagnostic code must not inspect `scene.view_settings.bl_rna...enum_items`, use `preferred`, assign `"NONE"`, choose a fallback, or silently retain a previous pass's look. Static preflight rejects those patterns in the diagnostic view-transform function.
6. The three launch script hashes are recomputed after this correction and must remain unchanged through post-process validation. All historical diagnostic/probe artifact hashes, including the five C3 hashes above, remain frozen and are rechecked before creating C4 and after the process.

No other generator, evaluator, runner, scene, camera, render, output, metric, or threshold behavior may change.

## Bounded execution

The existing asset writer may modify only the three TR4 asset-pipeline scripts and append `docs/workstreams/temple-tr4-asset/**`. Prior diagnostic/probe directories and every other repository path are read-only.

The pure-Python non-writing dry preflight must parse all three scripts; verify repository/reference/Blender executable/construction/frozen-artifact hashes; verify C4 IDs, exact view strings and forbidden patterns; require `diagnostic-004` absent; and machine-check this file says `AUTHORIZED` with `READY_FOR_DIAGNOSTIC_004_CONTRACT`, `docs/CURRENT_TASK.md` names diagnostic `004` as authorized, and the coordination log reports `TEMPLE-TR4-DIAGNOSTIC-004 AUTHORIZED`. It must not launch Blender or a version subprocess. The sole Blender process verifies `bpy.app.version_string == "4.5.5 LTS"` before construction.

Only `READY_FOR_BLENDER` permits exactly one Blender background process. It must complete all four C3 camera calibrations before the first render, then perform exactly 20 ordered `write_still` calls with the C4 prefix. Only return code `0`, valid camera/order/scene ancillary evidence, exact PNG names/dimensions/bit depths/nonzero bytes, and unchanged launch hashes permit exactly one evaluator invocation. The evaluator applies the inherited C3 closed evidence and raster gates with diagnostic ID `004`.

Any failure is `DIAGNOSTIC_BLOCKED`; there is no retry, output reuse, alternate look, fallback, threshold change, second Blender process, export, runtime action, browser, npm, test, build, Git, commit, or push. Numeric success remains at most `READY_FOR_MANUAL_REVIEW` and cannot replace independent visual inspection of all 20 outputs.
