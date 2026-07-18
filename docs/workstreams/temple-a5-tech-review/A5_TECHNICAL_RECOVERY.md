# TEMPLE-TR3-A5 — technical recovery plan

Status: **planning only; not authorized to implement or run.**  This is the smallest A5 that can repair the measured A4 failures without relaxing any A3/A4 gate.  It is deliberately an offline clay proof, not a runtime or asset-delivery slice.

## Finding

A4 cannot be repaired with its old permission set.  Its source locks both `build_causeway()` and `build_canyon()` to A3, while the failed review calls out the same roots those functions create: an unbroken route/medium structure and a coarse, low-poly strip-wall canyon.  Camera framing alone can move the five numerical results, but cannot add the missing physical road side mass, negative space, or authored near/mid/far structure.  A5 must therefore replace the offline *visual* builders for the causeway and canyon while preserving the A3 route contract.

A5 must not try to fix the following by reducing thresholds or changing a bounding-box definition:

- A4 portrait pursuer separation was `11.98 px`, below `12 px`; its road-band overlap was `-0.02130`.
- A4 portrait/desktop arch heights were `.06472H` and `.11601H`, below `.12H`; desktop aperture width was `.06503W`, below `.07W`.
- The manual visual failure is structural: repeated low-poly canyon walls and a featureless road/medium scale.  It remains a failure even if luminance or a GLB validator passes.

## Exact future A5 write scope

The coordinator must explicitly open this scope before any A5 implementation.  The sole implementation writer may add or change only these new A5 paths:

| Kind | Exact path |
| --- | --- |
| Generator | `E:\Proj\Game-1-temple\tools\temple-asset-pipeline\generate_tide_scar_hero_a5.py` |
| Evaluator | `E:\Proj\Game-1-temple\tools\temple-asset-pipeline\evaluate_asset_proof_a5.py` |
| Portrait proof | `E:\Proj\Game-1-temple\docs\workstreams\temple-tr3\asset-proof\a5\a5-clay-portrait.png` |
| Desktop proof | `E:\Proj\Game-1-temple\docs\workstreams\temple-tr3\asset-proof\a5\a5-clay-desktop.png` |
| Closeup proof | `E:\Proj\Game-1-temple\docs\workstreams\temple-tr3\asset-proof\a5\a5-clay-closeup.png` |
| Generated scene evidence | `E:\Proj\Game-1-temple\docs\workstreams\temple-tr3\asset-proof\a5\a5-clay-metadata.json` |
| Generated gate verdict | `E:\Proj\Game-1-temple\docs\workstreams\temple-tr3\asset-proof\a5\a5-clay-verifier.json` |

Before that writer starts, the coordinator must separately record the A5 contract change in the existing task/design/acceptance documents under its own authority.  Those existing documents are not part of the A5 implementation writer's scope.

No runner script, copied A3/A4 output, `.blend`, GLB, KTX2, texture, snapshot, cache, or `__pycache__` output is needed.  The A5 generator must set `sys.dont_write_bytecode = True` before importing A3 helper functions, so it cannot repeat A4's out-of-scope generated `.pyc` artifact.  The existing A3/A4 files remain read-only.

## Geometry recovery, not a camera-only correction

Use A3 only for low-level Blender helpers, lighting, courier construction, projections, and the immutable route values.  A5 locally owns `build_causeway_a5`, `build_canyon_a5`, `build_ring_a5`, and `build_pursuer_a5`; it must not call A3's causeway/canyon/ring/pursuer builders.

### Causeway

Keep all 16 A3 deck-cap modules on the identical 17-point `SPINE`, identical `WIDTHS`, original joints, yaw, elevation range, and `.68` safe center corridor.  The center `.68W` stays a continuous modelling-only lane-safe cap; none of these additions has collision or runtime meaning.

For every module, derive a deterministic event signature from `(SEED, moduleIndex)`.  The signature chooses a non-repeating sequence of one broken outer lip, one recessed strata ledge, and one asymmetric overhang or rubble cluster, never the same signature for more than two adjacent modules.  Place all additions outside the center corridor:

- make the cap an actual top plus downward side mass, retaining the A3 thickness range;
- add `1–3` short lip fragments at local longitudinal fractions chosen from `.19`, `.52`, and `.83`, each with a `0.10–0.22 m` step/drop and a different edge notch;
- attach `2` staggered horizontal strata/recess fragments below alternating outer edges, with no continuous side strip spanning a module joint;
- add one outer-side buttress/rubble event to at least 12 modules, alternating sides from the hash rather than forming a regular row.

This creates a readable broken top, lip, and side mass at the hero cameras while preserving the authored path data.  The generator records actual object-role counts and the 16 signature sequence in `geometryAudit`; the evaluator rejects fewer than 16 decorated modules, fewer than 32 attached side-mass fragments, or a repeated signature run longer than two.

### Canyon

Keep exactly three depth bands and the A3 cardinal group counts: 6 near buttress groups, 10 mid mesa/shelf groups, and 4 far silhouette groups.  A5 may change the geometry inside those groups because A4's `canyonExact` condition is the identified quality blocker.

Each group is an indexed, seed-derived cluster rather than a repeated upright rock or wall: a near cluster combines a lower buttress, offset ledge, and recessed negative-space cut; a mid group combines a mesa, offset shelf, and short fractured terrace; a far group combines two offset silhouette masses with an intervening gap.  Rotate, scale, and choose the fracture side from `random.Random(SEED + bandOffset + groupIndex)`; never reuse a transform tuple.  Preserve `maxNearWallOccupancy <= .19`, `repeatedGenericVerticalWalls == 0`, and `abyssOpeningsPortrait == 3`.

`geometryAudit` must report all 20 unique group signatures, zero continuous wall meshes, and a longest identical cluster-form run of at most one.  These are evidence for medium-scale hierarchy, not a substitute for the mandatory manual review.

### Pursuer and arch

Move the pursuer by a deterministic local route-frame transform, not a portrait camera shift: sample it `0.40 m` farther behind A4's route sample and apply a fixed `+0.55 m` lateral offset toward the courier's projected road band.  Retain the original quadruped's shoulder, wedge head, four grounded two-segment limbs, and dorsal ridge.  The A5 camera may receive only a framing adjustment after these geometry transforms pass source-space checks.

Retain A4's outer arch span (`outerSpanToDeckWidth` stays within `.42–.56`) but build a single `A5_ArchAssembly` containing both visible supports and the broken voussoir arc.  Use a `1.82 m` outer radius, increase the clear inner radius from `1.24 m` to `1.36 m`, reduce stone thickness to `.40 m`, and raise/taper the two support bodies to `2.15 m` with distinct grounded foot rocks.  Project the assembly—not an isolated arc fragment—as `arch`; also project both support descendants separately.  This measures the real supported obstacle silhouette, preserves the `.12H` gate, increases its physical vertical read, and gives a conservative desktop clear opening.

## Required A3/A4 comparison data

`a5-clay-metadata.json` must retain source hashes and compare before rendering.  A mismatch is fail-closed.

| Immutable comparison | Required A5 result |
| --- | --- |
| A3 generator, metadata, verifier hashes | Exact recorded inputs; A3 generator hash must still match the local A3 source. |
| A4 generator, metadata, verifier hashes | Exact recorded provenance inputs; `baselineFailures` records A4's five measured failures unchanged. |
| Seed, six semantic roots, stage, non-goals | Exact A3/A4 values: seed `270803`, exact root order, clay-only, no delivery/runtime actions. |
| Route | `metadata.route == A3.route`, including 16 modules, 17 samples, 125.949 m, 120.494 degrees, 5.95 m vertical range, 4 edge losses, 26 shelves, 32 strata breaks, and `.68` corridor. |
| Tide Scar | Exact A3 recipe: editable, non-baked, right third, `.016` width-to-deck, `.67` coverage, and the three semantic clips. |
| Clay values | Exact A4 `materialValues`; A5 changes shape/depth only, not the clay value study. |
| Canyon invariants | Preserve the A3 band and group cardinalities, three portrait abyss openings, wall-occupancy ceiling, and zero repeated generic vertical walls; do **not** require `canyonExact`. |
| Triangle ceiling | `<= 45,000`, unchanged. |

The intentional deltas are A5 causeway medium structure, canyon cluster topology, pursuer route-frame transform/rig, arch assembly, and framing.  A5 must not compare their A4 projections for equality, because that would make recovery impossible.

## One-batch sequence

1. Read A3/A4 JSON and hash the listed inputs with UTF-8 `Path.read_text(encoding="utf-8")`; preflight rejects any output path outside the seven paths above.
2. Run exactly one Blender 4.5.5 portrait (`540x960`), desktop (`960x540`), and closeup (`640x480`) clay batch from the new A5 generator.  It produces the three PNGs and metadata once.  No diagnostic/final pair and no repair rerun are permitted.
3. Run the A5 evaluator once.  It binds each image hash, reads the actual Blender projections/geometry audit, computes luminance and semantic ROIs, writes the verifier JSON, and exits non-zero on any failure.
4. A human reviewer inspects the three native-resolution images once against the four-item checklist below and supplies `PASS` only if every item is true.  The evaluator writes `BLOCKED` for any other verdict.  There is no retry, export, integration, or escalation into runtime after either outcome.

## Exact fail-closed gates

The old thresholds are retained and strengthened where A4 missed them by a rounding margin:

- Source/provenance and every immutable comparison in the table must pass; Blender version must start with `4.5.5`.
- Portrait pursuer: contained with `.02` margin, width `>=32 px`, courier center `.60–.68H`, pursuer center `.70–.79H`, vertical separation `>=14 px`, and horizontal road-band overlap `>=.02000`.
- Closeup pursuer: contained and width `>=48 px`.
- Portrait and desktop: ring, arch assembly, and each support are contained; ring height and arch-assembly height are each `>=.125H`; measured clear aperture is `>=.075W`; aperture-to-outer area is `>=.38`; two supports contact the deck.
- Every frame: global luminance `p50 >= .12`, `p95 >= .55`, `<=10/255 <10%`, route ROI median `>=.25`, and courier/pursuer/arch semantic ROIs are positive and non-black.  No camera-facing fog card, inward panorama cap shadow, or full-width fog step is allowed.
- Geometry audit: 16 deterministic decorated deck modules, `>=32` attached side-mass fragments, signature run `<=2`, all 20 canyon group signatures unique, zero continuous wall meshes, and no generic repeated cluster-form run above one.
- Manual checklist: (1) route immediately reads as a thick irregular object with broken lip and side mass; (2) canyon has asymmetric near/mid/far depth and visible negative spaces; (3) courier and pursuer read as separate grounded silhouettes; (4) the obstacle immediately reads as a supported broken-stone opening.  Any "blockout", "featureless route", "low-poly strip wall", or failed checklist finding is `BLOCKED` regardless of numbers.

## Runtime ownership boundary

This A5 plan is offline-only.  It must not read or change `src/**`, game core/runtime/rules/generator/canonical state/replay/hash/UI/browser evidence/package/config, root changelog, or existing A3/A4/TR3 artifacts.  It creates no shippable asset and authorizes no GLB, KTX2, optimization, texture, browser, test, build, commit, push, or QA action.

The coordinator owns any later authorization and all integration decisions.  A future A5 implementation owner owns only the seven listed A5 paths.  Independent QA has no task until a separate runtime candidate exists; a successful clay proof is not runtime acceptance.
