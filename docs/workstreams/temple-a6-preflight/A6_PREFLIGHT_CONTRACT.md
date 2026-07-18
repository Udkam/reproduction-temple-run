# TEMPLE-TR3-A6 — no-render recovery preflight contract

Status: **READY_FOR_COORDINATOR_REVIEW, documentation only.** This contract creates no Blender scene, proof image, asset, source code, evaluator, or runtime behavior. It is a required precondition for any later coordinator-authorized offline scene implementation. A5 is closed **BLOCKED**: its generator, 13 emitted image passes, verifier, snapshot, review files, and missing metadata remain historical evidence and are never reconstructed or edited.

## Purpose and boundary

The A5 process failed after image emission and before `a5-clay-metadata.json` existed because its generator attempted `a3["materialValues"]`. A3 never defined that key; A4 added the frozen clay material map. The failure shows why provenance must be normalized before scene construction rather than queried dynamically after a render has begun.

This is an original clean-room contract. It permits only broad principles: a physical warm mineral causeway, a cool layered canyon, an unambiguous pursuit line, a supported readable obstacle, and an editable edge annotation. It does not permit copying commercial characters, assets, layouts, names, art, or trade dress.

The eventual implementation remains offline-only until separately authorized. It must not change `src/**`, rules, canonical state, replay/hash, UI, runtime, browser evidence, assets, package/configuration, root changelog, Git state, or any A3/A4/A5 path. A green preflight is not a Blender authorization, render result, visual acceptance, runtime candidate, or QA result.

## Versioned input authority

The future preflight is a pure UTF-8 Python/data operation. It reads complete JSON documents with `Path.read_text(encoding="utf-8")`, parses them once, validates them, and produces an immutable normalized record *before* `bpy` import, output-directory creation, scene reset, object construction, camera creation, image path creation, or any render call.

| Source | Role | Required fields | Optional diagnostic fields | Forbidden use |
| --- | --- | --- | --- | --- |
| A3 metadata `a3-clay-metadata.json` | Structural invariant authority | `schema`, `seed`, `semanticRoots`, `stage`, `cleanRoom`, `route`, `canyon`, `tideScar`, `triangles`, `nonGoals` | `compositionTargets`, `projections`, `ring`, `gateFailures`, `generator` | `materialValues` is absent and must never be looked up. |
| A3 verifier `a3-clay-verifier.json` | Historical failure authority | `schema`, `passed`, `failures`, `sourceChecks`, `frames` | ROI/luminance diagnostics | It cannot become an A6 success source. |
| A4 metadata `a4-clay-metadata.json` | Clay-material and A3-derived provenance authority | all A3 invariant fields plus `materialValues`, `derivedFrom`, `a3StructuralComparison`, `ring`, `cameras`, `apertureProjections` | `projections`, `permittedDifferences`, `gateFailures` | Its failed screen placement and camera values are baseline evidence, not targets. |
| A4 verifier `a4-clay-verifier.json` | Frozen threshold/baseline-failure authority | `schema`, `passed`, `failures`, `sourceChecks`, `portraitActorSeparationPx`, `portraitHorizontalRoadBandOverlap`, `frames`, `ring` | `manualReview`, notes | No A6 threshold may be lower than an A4 threshold. |
| A5 verifier `a5-clay-verifier.json` | Failed-batch terminal evidence | `schema`, `verdict`, `passed`, `failures`, `manualReview` | empty check maps | It proves `a5-clay-metadata.json` is absent; images are not accepted as metadata or reconstructed evidence. |

### Required source identity

The normalized input must record and re-hash every listed source before use. Current reference hashes are A3 metadata `49929e04a418b3441bf888b299796f66a01618a4f40e13dde1172671fd7f8c40`, A3 verifier `121f2c5d48d141c39aa9eb5675f68c0411488fec6b630637558c96262a50307d`, A4 metadata `36ba3a021d1a7d29ff557f09882b166389b4d06faeef5d2c45309cadbe253025`, A4 verifier `5ed32dd582297cdcdff8268f9d6148fb33d853ff10bba20ec9aa39cb00392580`, and A5 verifier `7ef21ab843fc1c28220de7b35d2e4544f4cf609a21b62cf40ad32346fd9d73d6`. A source hash mismatch, unknown schema, malformed JSON, missing required key, unexpected root order, or a present A5 metadata file is `BLOCKED`.

### Frozen material adapter

`ClayMaterialAuthority` is constructed from **only** `A4.materialValues` before all later work. It must contain exactly these ten RGBA finite-number arrays, each of length four: `deck`, `strata`, `near`, `mid`, `far`, `courier`, `pursuer`, `ridge`, `ring`, and `scar`. The adapter rejects missing, extra, non-finite, out-of-range, or non-array values. A3's absent key is represented only as `materialAuthority="a4"` in the normalized record; it is not a nullable fallback and cannot be accessed.

After normalization, later scene code receives one frozen `PreflightInput` object. It has no raw JSON documents, no dictionary of untyped sources, and no `get`/subscript access to source metadata. Any post-normalization dynamic key access is a contract violation and `BLOCKED`. The initial metadata skeleton, source hashes, resolved material adapter, and planned output manifest must be serializable before a future Blender process is allowed to start, so an exception cannot leave image files without provenance.

## Formal pre-render input and result

These are schema contracts for a later pure-data preflight implementation; A6 does **not** create either file now.

### `temple-tr3-a6-preflight-input-v1`

Required top-level fields:

- `schema`, `preflightVersion`, `sourceHashes`, and fixed `base` SHA;
- `invariants`: seed `270803`; the exact six-root order; `stage="clay-only"`; route equal to A3 (16 modules, 17 samples, 125.949 m, 120.494 degrees, 5.95 m, `.68` center corridor); canyon band/group counts `3/6/10/4`, three portrait openings, `maxNearWallOccupancy <= .19`, no continuous generic wall; exact editable A3 Tide Scar record; and `trianglesMax=45000`;
- `clayMaterials`: the complete A4-only adapter above;
- `baselineFailures`: all five A4 failures plus the A5 missing-metadata terminal failure, preserved verbatim;
- `profiles`: portrait `540x960`, desktop `960x540`, landscape `844x390`, and supplementary closeup `640x480`, each with frozen camera transform/FOV, screen bands, HUD-safe rectangles, and road taper samples;
- `construction`: deterministic seed-derived road events, canyon clusters, route-frame actor placements, arch dimensions, and Tide Scar control points; and
- `prohibitions`: `render=false`, `blender=false`, `imageRead=false`, `network=false`, `export=false`, and no runtime/product paths.

### `temple-tr3-a6-preflight-result-v1`

Required top-level fields:

- `verdict`: exactly `READY_FOR_A6_IMPLEMENTATION` or `BLOCKED`; `READY` is impossible while any failure exists;
- `normalizedInputSha256`, `sourceHashes`, `resolvedMaterialAuthority="a4"`, `baselineFailures`, and invariant comparisons;
- `profilePredictions`: only pure-math projected bands, route widths, actor/hazard ordering, HUD exclusions, and depth-layer/occlusion intervals—never rendered pixels;
- `geometryAudit`: road event sequence, cross-section dimensions, canyon signatures, route-frame contact proof, arch/support/aperture values, and Tide Scar local polygons/intersections;
- `checks`, `failures`, and `nextAllowedAction`.

The result is green only when every check in this document and `A6_COMPOSITION_RECONSTRUCTION.md` is true. `nextAllowedAction` for a green result is only `coordinator-review`; it never starts Blender automatically. The result must be written atomically by a future implementation before any mutable output or process launch.

## Compatibility checks — all fail closed

1. A3/A4 schemas match the accepted versions and source hashes above; A5 verifier is `BLOCKED` and A5 metadata is absent.
2. A3/A4 seed, root order, stage, route, canyon invariant fields, Tide Scar recipe, and non-goals match exactly; the triangle ceiling remains `<=45000`.
3. `A4.materialValues` alone passes the exact ten-key adapter. `A3.materialValues` is neither read nor compared.
4. A4's baseline minimums remain: portrait actor separation `>=12 px`, positive road-band overlap, portrait/desktop arch height `>=.12H`, desktop aperture `>=.07W`; A5's stricter profile/hazard/Tide Scar requirements remain minima where defined.
5. Every finite numeric input is range-checked before use; unknown keys are rejected except listed optional diagnostics. No value may be derived from a beauty image, object-ID image, depth image, or post-render scene query.
6. All cameras, profile bands, construction dimensions, and exposure-independent geometry inputs are locked in the normalized input. Changing them after a failed result requires a fresh coordinator scope and preflight, never a hidden camera/exposure tweak.

## Future one-batch rule

If a later coordinator authorizes implementation, it must first execute the pure preflight once. Any `BLOCKED` preflight stops there: no Blender batch, no evaluator, no metadata reconstruction, no image deletion, and no retry. Only an all-green result may be reviewed by the coordinator for a separate, explicit one-batch Blender authorization. No inherited A3/A4/A5 threshold can be lowered, replaced by a proxy, or waived.
