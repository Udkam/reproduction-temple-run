# TEMPLE-TR3-A1 / A2 / A2R — Offline 3D asset proof

Status: **TEMPLE-TR3-A2R blocked — clay structural gate failed.** A2 is a new, isolated proof under `asset-proof/a2/`; it preserves the A0/A1 artifacts and the TR3-005C production dirt byte-for-byte. Neither the proof nor its companion scripts alters `src/**`, canonical state, browser evidence, or runtime configuration.

## A2 structural proof contract

A2 replaces the A1 blockout structurally rather than tuning its lighting. A deterministic Blender background-Python generator creates one original, curved and variable-width fractured causeway with at least two visible turns, a thick cap, discontinuous broken lips, layered side strata, recesses, rubble, and a safe central corridor. It is suspended over a non-planar deep-blue canyon made from separate near, middle, and far varied cliff clusters, negative space, an open non-shadowing panorama/procedural sky, and bounded volumetric depth — never a flat water horizon or camera-facing fog card.

The proof includes an original articulated courier, a low four-limbed basalt pursuer with a narrow coral dorsal ridge, and a thick supported broken-stone ring with a real opening. `TideScar_Ribbon_Editable` remains an independently editable, non-emissive curve/path along the right road edge. Locally generated image-backed base-color, normal, and ORM maps are bound to shared GLB materials; KTX2 files are derived from those same images rather than being unrelated proof payloads.

Both the source and semantic-preserving meshopt GLBs retain exactly these stable roots: `Causeway_Root`, `Canyon_Root`, `Runner_Root`, `Pursuer_Root`, `Obstacle_Ring_Root`, and `TideScar_Ribbon_Editable`. The manifest records metre units, `+Y` forward/`+Z` up, root pivots, collision-proxy and socket metadata, texture mappings, material reuse, hashes, and validation results. Optimization is explicitly configured not to flatten or join named semantic roots.

A2 is limited to one low-resolution clay/silhouette batch (portrait and desktop, plus a close crop in the same batch) and, only if its structural gate passes, one final portrait/desktop/closeup batch. The proof budgets are: unoptimized `<=180k` triangles, optimized `<=120k`, `<=8` shared materials, `<=8` bound images before mobile variants, optimized GLB `<=8 MiB`, and zero glTF validator errors. A technically valid result that still reads as a primitive blockout is reported blocked and is never integrated into runtime.

## A2R recovery result (2026-07-14)

The one authorized real clay/silhouette batch completed in Blender `4.5.5 LTS` after two bounded generator repairs. `create_deck()` now performs conditional sand/basalt fallback lookup without eagerly evaluating a missing `clay` value, and `create_tide_scar()` derives `last = len(SPINE) - 1`, skips wholly out-of-range requests, and clamps the final requested interval from `45..50` to `45..46`. `SPINE`, `section()`, deck geometry, canonical/gameplay data, and all runtime paths remain unchanged.

Pillow evidence passed: portrait `480x854` p50/p95/near-black = `.412/.690/0%`; desktop `854x480` = `.553/.725/0%`; closeup `640x480` = `.541/.694/0%`. The clay scene records `4,787` pre-export triangles and declares the six required semantic roots, but no GLB, KTX2, optimizer, or validator output exists because the structural/manual gate failed before final delivery.

Manual structural verdict: **blocked.** The curved road and separately modelled courier/pursuer exist, but the hero frames still read as a broad, nearly planar light road bounded by oversized regular low-poly slab walls. The causeway does not show sufficient thick broken lip/side-mass readability at the hero cameras; canyon depth is dominated by primitive wall silhouettes rather than a near/mid/far authored hierarchy; and the supported ring is not immediately identifiable in the portrait or desktop composition. This is a primitive/blockout failure regardless of the passing luminance evidence. No final render, GLB export, meshopt/KTX2 conversion, runtime integration, browser capture, commit, or QA action is permitted.

The exact A2R clay artifacts are `a2-clay-portrait.png` (SHA-256 `e41c3363c18b93c25691acf6b8f1f6b8c28d04fbc72dde8edb983f93cfcac677`), `a2-clay-desktop.png` (`8cded12db56a3fa39c4ccda002d006f96acaf13204f98272caa604760d03142a`), `a2-clay-silhouette-closeup.png` (`9748e6ff45f2db4117b23a74c43355579919c8773cefbc544f3e615b3174a273`), `a2-clay-readability.json`, and `a2-clay-scene-metadata.json`, all under `docs/workstreams/temple-tr3/asset-proof/a2/`. The next gate requires new coordinator authorization for a structural environment-art correction and a fresh bounded diagnostic; this A2R slice is closed.

## A1 diagnosed render fault and bounded repair

A0's portrait/desktop/closeup had global luma median `0.026/0.011/0.015`, p95 `0.120/0.102/0.070`, and `<=10/255` pixels `54.7%/65.4%/65.6%`. The proof failed because the capped inward panorama cast shadows, opaque contact discs and very dark materials crushed subjects, High Contrast AgX reduced the lower range, and three camera-facing mist cards became screen-wide bands. The original `samples` parameter was also never assigned to Blender 4.5 Eevee RNA, and the closeup was absent from the manifest file glob.

A1 repairs only those scene settings: an open, non-shadow-casting panorama enclosure; no mist cards; AgX Medium Low Contrast at exposure `+1.0`; sun/key/fill lighting; raised dark-material values; transparent contact shadows; camera clips `0.1..500`; and explicit `scene.eevee.taa_render_samples`. Geometry, camera composition, scene topology, clean-room boundary, and runtime isolation remain unchanged.

## Clean-room direction

The proof translates only high-level visual qualities into an original scene: a high rear-follow view along a broken warm-sandstone causeway over a deep blue fog canyon, a restrained right-edge lime Tide Scar, sparse coral mineral, a slim courier, a grounded basalt quadruped, and a supported stone ring. It is not a copy of the supplied reference, D4 composite, commercial game art, character, road layout, logo, or level.

The Tide Scar is a separate editable curve object named `TideScar_Ribbon_Editable`. It is neither baked into the road material nor emitted from a texture. The scene builds all road, cliffs, characters, obstacle, panorama enclosure, and materials procedurally in Blender Python.

## Reproducible inputs and outputs

Authoritative generator:

`tools/temple-asset-pipeline/generate_tide_scar_hero.py`

The generator accepts `--stage draft` or `--stage final`; it resets Blender to a new scene, creates every mesh/material/camera, writes a `.blend`, exports an unoptimized GLB, emits procedural PBR proof PNGs, and renders the requested compositions. It must be invoked headlessly:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python-exit-code 1 --python tools/temple-asset-pipeline/generate_tide_scar_hero.py -- --stage final --output docs/workstreams/temple-tr3/asset-proof
```

The required delivery commands after the final Blender run are recorded in `tools/temple-asset-pipeline/run_asset_proof.py`. It runs glTF Transform validation/inspection, meshopt optimization, KTX2 conversion/validation, computes SHA-256 values, and writes the proof manifest. The script rejects a missing source output and never reads or writes production paths.

```powershell
python tools/temple-asset-pipeline/run_asset_proof.py --output docs/workstreams/temple-tr3/asset-proof --stage final
```

## Scene contract

- Units are metres; Blender forward is `+Y`, up is `+Z`. Root pivots sit at ground level.
- Stable roots: `Causeway_Root`, `Canyon_Root`, `Runner_Root`, `Pursuer_Root`, `Obstacle_Ring_Root`, and `TideScar_Ribbon_Editable`.
- Road caps have real thickness, broken edge lips, lower sandstone bands, and downward basalt cliff aprons. The canonical road plane is represented only as a modelling convention; there is no gameplay or collision export in this proof.
- `Panorama_Inward_Enclosure` is an inward-facing, open-ended, non-shadow-casting curved enclosure surrounding both hero cameras. Far mesas, middle stacks, near lips, and water add separate depth layers instead of repeated wall props; A1 deliberately adds no camera-facing fog cards.
- `Pursuer_Root` contains a broad faceted shoulder/body, head, four two-segment grounded limbs, contact shadow, and a narrow coral dorsal ridge. It is intentionally not a sphere with thin legs.
- `Obstacle_Ring_Root` contains a thick open stone ring, two supports, debris, and a contact shadow.
- Sandstone, basalt, coral, Tide Scar, water, mist, and courier use reused PBR materials. Blender node noise/bump defines visual surface detail; the emitted proof textures provide reproducible base/normal/roughness/AO test inputs for KTX2 packaging.

## Offline validation gates

1. `gltf-transform inspect` and `gltf-transform validate` pass for both unoptimized and meshopt GLBs.
2. `ktx validate` passes for every generated proof KTX2 texture.
3. Manifest records generator/tool versions, GLB byte sizes, SHA-256 values, node roots, units, material reuse, triangle/material/texture counts, and KTX2 metadata.
4. Before final rendering, one low-resolution diagnostic batch must pass Pillow evidence: global p50 `>= .12`, p95 `>= .55`, `<=10/255 <10%`, road ROI p50 `>= .25`, no `Mist_Band` object, and non-black fixed ROIs for courier, quadruped, and ring.
5. One portrait (9:16), one desktop (16:9), and one closeup final render are manually reviewed. The final pixel-evidence JSON includes all three frames, their luma distributions, road ROI, and declared semantic ROIs.
6. If a final render reads as flat road, black trapezoid, repeated low-poly wall, or primitive characters, it is reported as blocked regardless of validation or size metrics.

## Explicit non-goals

- No runtime load, scene integration, browser capture, game rule change, package/config edit, or candidate commit.
- No external downloads, commercial assets, image generation, Blender MCP, baked reference imagery, or copied source texture.
- No direct modification, staging, cleanup, or commit of the preserved TR3-005C dirty paths.
