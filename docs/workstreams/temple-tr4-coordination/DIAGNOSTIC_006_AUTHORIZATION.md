# TEMPLE-TR4 diagnostic 006 canonical anchor key-set correction

Terminal disposition: **CONSUMED — DIAGNOSTIC_BLOCKED.** The historical authorization
below governed one completed C6 process. Blender returned `0` and wrote 20 PNGs, but the
runner stopped before evaluator on a near-zero landscape angle arithmetic-agreement
mischeck; independent visual inspection also returned `MANUAL_BLOCKED`. C6 is immutable
and this file grants no retry or successor implementation.

Status: **AUTHORIZED.** Both independent reviews closed with no P0/P1:

- root-cause and implementation-boundary review: `READY_FOR_DIAGNOSTIC_006_CONTRACT`;
- contract-consistency review: `READY_FOR_DIAGNOSTIC_006_CONTRACT`.

This permits only the exact C6 identity/key-set/dry deltas, non-writing dry preflight, one new diagnostic directory, one Blender 4.5.5 process, 20 ordered PNGs, and at most one evaluator under the inherited C5 gates. It does not authorize retry, export, runtime action, browser, test, build, Git, commit, or push.

## Frozen C5 terminal evidence

Diagnostic `005` is immutable `DIAGNOSTIC_BLOCKED`. Its sole Blender 4.5.5 process exited `1` during generator `validate_input`, before scene construction, camera binding, or the first `write_still`. It produced zero PNG and did not invoke the evaluator. Its directory contains exactly four files and no subdirectory:

- `preflight.json`: SHA-256 `3f7997793ea9629cc17bdb4cfe186eed4d505273363105f90e9bec3778662659`;
- `planned-manifest.json`: SHA-256 `933890d49f728410b11c723be7c7ffbfe6f724d27018dabda85fc2ba45035437`;
- `blender.log`: SHA-256 `68f20d179729ff363aa142e76f55a530690ce156a6378552b981c0afa1abdd94`;
- `diagnostic-status.json`: SHA-256 `e31e89d92fc5a5ed0f3e93acda637ee15ab384141ba49f29bbe487f178431752`.

The C5 launch-bound hashes were generator `653fea54fc08a339d7c847e841a4577e59a56641e761bf07ee2a71b601302612`, evaluator `414cfdc2ca90c113172a9984f09feadc69daa6ee15e197f517c1e8c5eeebcd07`, and runner `52222668baac8555a4dfecd7cd32dc90db7aef946c304f93549791fd1c164faf`. All four C5 files plus all 47 older frozen artifacts form an exact 51-file frozen set and are rechecked before and after C6; the three historical C5 launch hashes remain recorded provenance. C5 may not be retried, reused, deleted, renamed, or rewritten.

## Exact root cause

Canonical preflight JSON is serialized with `sort_keys=true`. Therefore the valid `projectionAnchors` object is parsed in lexical key order:

`beam`, `column`, `farRoute`, `gap`, `ring`, `routeCenter`, `runnerAnchor`, `runnerFootL`, `runnerFootR`, `runnerHead`, `scar`.

The C5 generator correctly required the exact eleven names but incorrectly used insertion-order comparison:

```python
list(record["projectionAnchors"].keys()) != anchor_keys
```

Its local `anchor_keys` declaration used authoring order beginning with `runnerAnchor`, so it rejected a canonical object with no missing, extra, or invalid key. This was a schema-validator defect, not a camera, geometry, material, light, fog, raster, or visual verdict. The non-writing dry preflight did not execute Blender-only generator `validate_input` and lacked an exact canonical-round-trip mirror of this child predicate.

## Exact C6 changes

C6 inherits every C5 closed field, value, construction hash `2ab30e4580a7bdf6b8eeddf8dcd2acc5d17fa3c101aecc9d530cbea535c79c10`, camera record, projection anchor/value, camera-binding v2 schema, light/atmosphere record, scene/placement gate, output pass/order/resolution/format, raster/evaluator algorithm, evidence allowlist, script provenance rule, single-process/single-evaluator boundary, no-retry rule, and manual-review requirement, with exactly these changes:

1. Preflight `schemaVersion=6`, `contractVersion="TEMPLE-TR4-C6"`, diagnostic root `docs\workstreams\temple-tr4-asset\diagnostic-006`, `diagnosticId="006"`, and output prefix `tr4-diagnostic-006-` in the same 20 ordered records.
2. Planned manifest, camera binding, evaluation, manifest, and diagnostic status identify `006`; `render-order.json` remains the exact schema-less 20-name array and `scene-metrics.json` remains the exact inherited eight-key object.
3. In generator `validate_input`, each camera still requires exactly the inherited fourteen top-level keys. It first requires `projectionAnchors` to be a `dict`, then requires exact set equality only:

```python
sorted(record.keys()) == sorted(camera_keys)
sorted(record["projectionAnchors"].keys()) == sorted(anchor_keys)
```

Missing, extra, duplicate-after-parse, wrong-type, non-finite, or wrong-valued fields remain rejected by the inherited deep comparison. `list(record["projectionAnchors"].keys())`, direct dictionary-order equality, fallback order normalization, reordering an in-memory input to make the old check pass, or weakening any other schema/value gate is forbidden.
4. Runner dry preflight canonicalizes the complete C6 preflight to UTF-8 JSON bytes with sorted keys, parses those bytes into a fresh object, and applies the same complete C6 validator plus exact top-level and anchor key-set predicates to all four parsed camera records. The parsed-and-validated object, not the pre-round-trip object, is returned for formal writing after dry. Runner and evaluator also independently require `projectionAnchors` to be a dictionary with the exact insertion-order-insensitive key set and reject any missing or extra key before matrix/binding/raster validation.
5. Static gates require generator `validate_input`, runner canonical validation, and evaluator preflight validation each to contain the logically exact `sorted(projectionAnchors.keys()) == sorted(anchor_keys)` predicate or its `!=` fail form. They reject any `list(projectionAnchors.keys())` comparison or other insertion-order dependency in all three scripts. Ordered JSON arrays, including profiles, semantic roots, outputs, passes, and manifest records, remain order-sensitive.
6. Generator, evaluator, and runner hashes are recomputed after only these identity/predicate/dry changes and become the C6 launch hashes. No camera, anchor coordinate, matrix, geometry, topology, transform, material, light, world/fog, view setting, tolerance, evaluator metric, threshold, count, or manual gate may change.

## Bounded execution

The existing asset writer may modify only the three TR4 asset-pipeline scripts and append its `THREAD_LOG.md` plus new `diagnostic-006/**`. Every C1-C5 diagnostic/probe file, coordinator file, production/runtime path, and other workstream path is read-only.

Before authorization, an independent review must return exactly `READY_FOR_DIAGNOSTIC_006_CONTRACT` with no P0/P1. After authorization, the writer runs AST/static checks and the non-writing `--dry-preflight`; it must emit only `READY_FOR_BLENDER`, return `0`, prove `diagnostic-006` remains absent, verify the approved reference/tool/frozen evidence/construction/new script hashes, round-trip the canonical camera/anchor object, and machine-check this file, `docs/CURRENT_TASK.md`, and the coordination log all authorize `006`.

Only that dry verdict permits one Blender 4.5.5 background process, exactly 20 ordered PNG writes, and at most one evaluator. Any failure is terminal `DIAGNOSTIC_BLOCKED`; there is no retry, reuse, second process, alternate schema/camera/light/fog, threshold change, cleanup, export, runtime integration, browser, test, build, Git, commit, or push. Numeric success is at most `READY_FOR_MANUAL_REVIEW` and still requires independent inspection of all 20 outputs.
