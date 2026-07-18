# TEMPLE-TR4 diagnostic 007 contract review request

Status: **DRAFT / CONTRACT REVIEW REQUESTED — NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

Independent review of draft commit `2f5fa9c4b1e2f6b51be92020765fa01632e28491` returned `CONTRACT_BLOCKED`: construction-hash scope and the fail-closed material/compositor/depth schema were P0; manual review triggering and the generator checkpoint exception were P1. This revision resolves those findings and requires a fresh review of its exact commit before authorization.

This document is a proposed C7 overlay on the immutable C1 schema and the consumed C2-C6 authorizations. It does not authorize a source edit, diagnostic directory, Blender process, evaluator, render, export, runtime integration, browser capture, test, build, commit beyond coordinator documentation, or push. An independent read-only review must return `READY_FOR_DIAGNOSTIC_007_CONTRACT`, after which the coordinator must record a separate explicit authorization before the asset writer starts.

## Frozen evidence and baseline

- baseline: `ecd5de640362a6e30c5d0157ecd1590be7673318`;
- frozen inherited-backlog anchor: `52ae9ae631fa3761f8f8737978af1840ba2df8a4`;
- C1-C6 plus both probes are immutable; C6 contributes 27 files and the older diagnostic/probe set contributes 51 files, for 78 frozen files total;
- C6 remains `DIAGNOSTIC_BLOCKED; MANUAL_BLOCKED`. Its 20 PNGs cannot be rerun, reused as C7 output, deleted, re-evaluated, or described as acceptance evidence;
- the five backup/cache paths listed in `BACKLOG_SPLIT_PLAN.md` remain untracked, untouched, and never-stage.

## C7 identity and closed output set

- schema ID remains `tide-relay.temple-tr4.asset-preflight`;
- schema version is integer `7`; contract version is `TEMPLE-TR4-C7`;
- diagnostic root is exactly `docs\workstreams\temple-tr4-asset\diagnostic-007`;
- output prefix is exactly `tr4-diagnostic-007-`;
- gameplay scene ID is `tr4-diagnostic-running-007`; bookend scene ID is `tr4-diagnostic-game-over-007`;
- `constructionHash` is new and remains SHA-256 of canonical `construction` only. It covers C7 geometry, material-graph, light, compositor, and depth records inside that object; it does not cover sibling fields. `planned-manifest.json.preflightSha256` binds the complete normalized preflight, including camera, collision, top-level material, semantic-root, budget, and output records;
- output order, profiles, passes, and dimensions remain exactly the C1 order: four profiles `portrait,desktop,landscape,closeup`, each with `beauty,object-id,road-mask,normal,linear-depth`, for exactly 20 PNGs named `tr4-diagnostic-007-{profile}-{pass}.png`;
- all four frozen camera positions, targets, up vectors, FOV, near/far, lens shifts, projection matrices, view matrices, and analytic screen gates remain unchanged.

No C7 output path may exist before the authorized runner completes its in-memory checks. A pre-existing root, extra output, changed camera, changed output order, unchanged C6 construction hash, or technical-only predicate rerender is `PRECHECK_BLOCKED`.

## Stable camera evidence predicate

The camera construction and generator's recorded-axis calculation remain valid. Runner and evaluator replace only the unstable direct-radian equality comparison:

1. require recorded axis angle `<=1e-5`;
2. require independently recomputed axis angle `<=1e-5`;
3. require `abs(cos(recorded)-cos(recomputed))<=1e-12`;
4. retain every determinant, basis, view-matrix, projection, lens-shift, finite-value, and screen-order gate.

A non-writing dry predicate test must accept the frozen C6 landscape pair `2.1073424255447017e-08` / `2.580956827951785e-08` and reject an injected sample with an axis angle greater than `1e-5`. The dry test may not import `bpy`, create `diagnostic-007`, launch Blender, invoke the evaluator, or mutate evidence.

## Mandatory substantive reconstruction

C7 is not a validator retry. Before its sole render, the new construction hash must prove all of these authored changes:

- **Causeway:** rebuild the road cap as a subdivided irregular warm-sandstone surface with real thickness, fractured lips, darker break faces, undercuts, side aprons, strata, cracks, dust, contact shadow, and rubble. At least six deterministic macro signatures remain, with no signature repeated more than twice. A vista bend may begin only beyond the frozen gap proof distance.
- **Canyon:** replace the repeated column corridor with layered ridge, terrace, ledge, recess, and overhang meshes. Near/mid/far bands retain at least `8/10/12` unique signatures, three negative spaces, two occlusion boundaries, asymmetric skylines, and monotonic atmospheric loss. No visible flat water band, wall slab, panorama cap, or corridor repetition is allowed.
- **Courier:** retain named articulated parts while replacing joined primitive readability with modeled torso, head, clothing, hands, legs, feet, and split coat tails. Eight gait phases plus jump/slide/stumble/failure must keep non-adjacent parts disjoint, feet grounded within `.03m`, silhouettes readable, and contact shadows present.
- **Bookend pursuer:** model separated pelvis/rib/shoulder plates, neck, head, jaw, four upper/lower limbs, four paws, and a restrained coral dorsal seam. It appears in the opening state and game-over closeup only, remains absent from ordinary-running profiles, and cannot read as a black blob. In capture framing the runner and creature body cores remain separated while forelimbs may bracket the runner without intersecting it.
- **Canonical hazards:** keep simulation and collision rules unchanged. `beam` becomes the grounded Fault Lip jump threshold; `ring` the two-supported Coral Throat slide arch with true clearance; `column` the single-lane Basalt Splitter; `gap` the genuinely missing Tidebreak span; turn the route-ending Sundered Elbow. Bases embed `0.08-.15m`, visible/proxy discrepancy remains `<=.06m`, no co-planar faces exist, and no visual part invents a false safe or blocked lane.
- **Tide Scar:** remain editable curve geometry. The longitudinal line stays outside `X=2.92m`; the near loop is moved ahead of the runner into the supported right shoulder, wholly visible in portrait, outside the safety corridor, clipped against hazards/gaps/actors, and never baked into a texture or UI strip.

Public gameplay sources inform only generic turn/jump/slide/gap/lane-readability grammar. No commercial frame, name, logo, character, creature, road mesh, texture, UI, sound, exact obstacle arrangement, or trade dress may enter C7.

### Exact reconstruction-schema additions

C7 retains every C6 construction field except where this section supplies a replacement. The resulting objects reject unknown or missing keys:

- `road` retains its thirteen C6 fields and adds exactly `capCrosswiseSegments=9`, `capLongitudinalSegmentsPerModule=8`, `fractureEventsPerModule=3`, `undercutEventsPerModule=2`, `sideApronsPerModule=2`, `vistaBendStartZ=-82`, `vistaBendMaxOffsetX=12`. `nearLoopShoulder` becomes `{"rightOuterX":4.45,"zRange":[-5.2,-2.8]}`.
- each `canyon.near/mid/far` band retains its C6 fields and adds exactly `recipe`, `ridgeSegmentsPerSignature`, `terracesPerSignature`, `overhangsPerSignature`, `recessesPerSignature`. Values are near `{"recipe":"layered-ridge-near-v1","ridgeSegmentsPerSignature":9,"terracesPerSignature":3,"overhangsPerSignature":2,"recessesPerSignature":2}`, mid `{"recipe":"layered-ridge-mid-v1","ridgeSegmentsPerSignature":8,"terracesPerSignature":3,"overhangsPerSignature":2,"recessesPerSignature":2}`, and far `{"recipe":"layered-ridge-far-v1","ridgeSegmentsPerSignature":7,"terracesPerSignature":2,"overhangsPerSignature":1,"recessesPerSignature":1}`. Counts remain `8/10/12` and every generated signature record must hash uniquely inside its band.
- `runner` retains its C6 fields and adds exactly `modelingMode="profiled-articulated-mesh-v1"`, `minimumRadialSegments=10`, `primitiveJoinForbidden=true`, `nonAdjacentIntersectionTolerance=0`.
- `pursuer` retains its C6 fields and adds exactly `modelingMode="separated-rock-plate-quadruped-v1"`, `minimumRadialSegments=10`, `primitiveJoinForbidden=true`, `bodyCoreSeparationMin=.18`.
- every hazard record retains its C6 fields and adds exactly `visualName`, `baseEmbedRange=[.08,.15]`, `maxProxyDiscrepancy=.06`, `coPlanarFacesAllowed=false`. Names are `Fault Lip`, `Coral Throat`, `Basalt Splitter`, and `Tidebreak Gap` in canonical order.
- `tideScar` retains its C6 fields and adds exactly `nearLoopVisibilityProfile="portrait"`, `bakedTextureAllowed=false`. `loopControlPoints` is replaced by the ahead-of-runner spline `[[3.00,.035,-3.20],[3.09,.035,-2.87],[3.33,.035,-2.64],[3.65,.035,-2.55],[3.98,.035,-2.64],[4.22,.035,-2.87],[4.30,.035,-3.20],[4.22,.035,-3.52],[3.98,.035,-3.76],[3.65,.035,-3.85],[3.33,.035,-3.76],[3.09,.035,-3.52],[3.00,.035,-3.20]]`.

`scene-metrics.json` retains the C6 keys and adds exact `geometryBinding`, `materialGraphBinding`, and `depthEncodingBinding`. `geometryBinding` has exactly `road`, `canyon`, `runner`, `pursuer`, `hazards`, `tideScar`, `verdict`; its normalized values are generated from the actual Blender objects and must deep-equal the corresponding construction records, with `verdict="READY_FOR_DIAGNOSTIC_RENDER"`. The generator also verifies unique canyon signature hashes, road cap/apron/undercut event counts, named part/root coverage, ground sockets, hazard supports, and the loop spline before writing this record. Runner and evaluator reject any mismatch before pixel gates.

## Procedural PBR and atmosphere repair

- No external texture file is allowed. Each sandstone, fresh-break, basalt, strata, cloth, leather, and rock-armour node graph explicitly connects Object or Generated coordinates through Mapping into bounded macro and micro Noise/Voronoi fields, colour ramps, roughness modulation, and bump. Every node link and scale is serialized in construction metadata.
- Procedural surface response supplements authored macro/medium geometry; it cannot replace fractures, strata, ledges, plates, limbs, or supports.
- The raw beauty scene uses Principled BSDF materials, the frozen warm key/cool fill/contact bounce, AgX `AgX - Medium High Contrast`, exposure `0`, and world surface `#6E8294` at strength `.55`. World volume is disabled.
- The beauty compositor uses rendered visible depth to compute `T(d)=exp(-.0035*d)` and mixes fog `#9AA7A8` by `1-T`; background is the same fog colour. Fog cards, panorama caps, emission lift, exposure lift, and pixel-threshold shortcuts are forbidden.

### Exact material-graph record

`construction.materialGraphs` has exactly `coordinateSource="Generated"`, ordered `graphOrder=["sandstone","fresh-break","basalt","basalt-strata","cloth","leather","rock-armour"]`, `template`, and `parameters`.

`template` has exactly:

- `nodeOrder=["TextureCoordinate","Mapping","MacroNoise","MicroNoise","Voronoi","MacroRamp","RoughnessMap","HeightMix","Bump","Principled","MaterialOutput"]`;
- `nodeTypeByName={"TextureCoordinate":"ShaderNodeTexCoord","Mapping":"ShaderNodeMapping","MacroNoise":"ShaderNodeTexNoise","MicroNoise":"ShaderNodeTexNoise","Voronoi":"ShaderNodeTexVoronoi","MacroRamp":"ShaderNodeValToRGB","RoughnessMap":"ShaderNodeMapRange","HeightMix":"ShaderNodeMixRGB","Bump":"ShaderNodeBump","Principled":"ShaderNodeBsdfPrincipled","MaterialOutput":"ShaderNodeOutputMaterial"}`;
- `linkOrder=["TextureCoordinate.Generated->Mapping.Vector","Mapping.Vector->MacroNoise.Vector","Mapping.Vector->MicroNoise.Vector","Mapping.Vector->Voronoi.Vector","MacroNoise.Fac->MacroRamp.Fac","MacroNoise.Fac->RoughnessMap.Value","MicroNoise.Fac->HeightMix.Color1","Voronoi.Distance->HeightMix.Color2","HeightMix.Color->Bump.Height","Bump.Normal->Principled.Normal","MacroRamp.Color->Principled.Base Color","RoughnessMap.Result->Principled.Roughness","Principled.BSDF->MaterialOutput.Surface"]`;
- `rampPositions=[.28,.72]`, `heightMixBlend="MULTIPLY"`, and `roughnessMapClamp=true`.

Every `parameters` child rejects unknown keys and has exactly `mappingScale`, `macroScale`, `macroDetail`, `macroRoughness`, `microScale`, `microDetail`, `voronoiScale`, `voronoiRandomness`, `rampLow`, `rampHigh`, `roughnessRange`, `bumpDistance`, `bumpStrength`:

| Material | Exact parameter record |
| --- | --- |
| sandstone | `{"mappingScale":[1,1,1],"macroScale":.65,"macroDetail":5,"macroRoughness":.68,"microScale":8.5,"microDetail":3,"voronoiScale":2.4,"voronoiRandomness":.65,"rampLow":"#8F7659","rampHigh":"#D8B98C","roughnessRange":[.72,.94],"bumpDistance":.18,"bumpStrength":.42}` |
| fresh-break | `{"mappingScale":[1,1,1],"macroScale":1.2,"macroDetail":4,"macroRoughness":.62,"microScale":12,"microDetail":3,"voronoiScale":3.2,"voronoiRandomness":.70,"rampLow":"#5E4A37","rampHigh":"#8F7659","roughnessRange":[.82,.96],"bumpDistance":.22,"bumpStrength":.58}` |
| basalt | `{"mappingScale":[1,1,1],"macroScale":.55,"macroDetail":5,"macroRoughness":.72,"microScale":7,"microDetail":4,"voronoiScale":1.8,"voronoiRandomness":.58,"rampLow":"#111A20","rampHigh":"#263846","roughnessRange":[.64,.90],"bumpDistance":.20,"bumpStrength":.48}` |
| basalt-strata | `{"mappingScale":[.55,2.8,.55],"macroScale":.80,"macroDetail":4,"macroRoughness":.66,"microScale":10,"microDetail":3,"voronoiScale":2.2,"voronoiRandomness":.55,"rampLow":"#24343E","rampHigh":"#405764","roughnessRange":[.70,.92],"bumpDistance":.24,"bumpStrength":.62}` |
| cloth | `{"mappingScale":[1,1,1],"macroScale":3.5,"macroDetail":3,"macroRoughness":.55,"microScale":32,"microDetail":2,"voronoiScale":10,"voronoiRandomness":.50,"rampLow":"#172B36","rampHigh":"#294756","roughnessRange":[.78,.94],"bumpDistance":.035,"bumpStrength":.24}` |
| leather | `{"mappingScale":[1,1,1],"macroScale":2.2,"macroDetail":4,"macroRoughness":.60,"microScale":18,"microDetail":3,"voronoiScale":7,"voronoiRandomness":.62,"rampLow":"#20282C","rampHigh":"#394247","roughnessRange":[.66,.84],"bumpDistance":.055,"bumpStrength":.32}` |
| rock-armour | `{"mappingScale":[1,1,1],"macroScale":.75,"macroDetail":5,"macroRoughness":.70,"microScale":9,"microDetail":4,"voronoiScale":2.7,"voronoiRandomness":.68,"rampLow":"#0A1014","rampHigh":"#1B2830","roughnessRange":[.62,.86],"bumpDistance":.20,"bumpStrength":.54}` |

The generator serializes the actual constructed node names/types/links and numeric values into `scene-metrics.json.materialGraphBinding`; runner and evaluator require exact deep equality with this record before pixel gates.

### Exact atmosphere/compositor record

`construction.lighting` has exactly the C6 values for `worldColor="#6E8294"`, `worldStrength=.55`, `key`, `fill`, and `contact`, with no fog-volume keys. `construction.atmosphere` has exactly:

- `mode="beer-lambert-depth-composite"`, `worldVolumeEnabled=false`, `depthSource="RenderLayers.Depth"`, `density=.0035`, `fogColor="#9AA7A8"`, `backgroundPolicy="fog-color"`, `viewTransform="AgX"`, `look="AgX - Medium High Contrast"`, `exposure=0`, `gamma=1`;
- `nodeOrder=["RenderLayers","NegDensity","ExpTransmittance","OneMinusTransmittance","FogColor","MixFog","Composite"]`;
- `nodeTypeByName={"RenderLayers":"CompositorNodeRLayers","NegDensity":"CompositorNodeMath","ExpTransmittance":"CompositorNodeMath","OneMinusTransmittance":"CompositorNodeMath","FogColor":"CompositorNodeRGB","MixFog":"CompositorNodeMixRGB","Composite":"CompositorNodeComposite"}`;
- `operationByName={"NegDensity":"MULTIPLY","ExpTransmittance":"EXPONENT","OneMinusTransmittance":"SUBTRACT","MixFog":"MIX"}`;
- `linkOrder=["RenderLayers.Depth->NegDensity.Value","NegDensity.Value->ExpTransmittance.Value","ExpTransmittance.Value->OneMinusTransmittance.Value","OneMinusTransmittance.Value->MixFog.Fac","RenderLayers.Image->MixFog.Color1","FogColor.Image->MixFog.Color2","MixFog.Image->Composite.Image"]`.

Constants are `NegDensity` multiplier `-.0035` and `OneMinusTransmittance` first input `1`. Blender's `EXPONENT` operation is the exact `e^value` operation. `camera-binding.json` schema version `3` records an `atmosphereBinding` with exactly the normalized atmosphere fields, `transmittance20/120/520`, and `verdict="READY_FOR_DIAGNOSTIC_RENDER"`; runner/evaluator deep-compare it before accepting the output set.

## Visible-depth repair

The C1 far-plane-normalized depth mapping is superseded only for C7:

- portrait/desktop/landscape ceiling: `160m`; closeup ceiling: `80m`;
- foreground value: `round(65535 * .94 * clamp((distance-near)/(ceiling-near),0,1))`;
- true background: `65535`;
- at least 64 distinct foreground values per profile;
- foreground `p10 < p50 < p90 < 62000`;
- ordinary-running semantic median depth strictly increases `runner < beam < ring < column < gap`;
- every pass remains PNG16 with its exact camera matrix and dimensions.

`construction.depthEncoding` has exactly:

`{"distanceMetric":"euclidean-camera-distance-meters","nearSource":"cameras[].near","ceilingByProfile":{"portrait":160,"desktop":160,"landscape":160,"closeup":80},"foregroundScale":.94,"backgroundValue":65535,"bitDepth":16,"colorType":0,"rounding":"floor(x+0.5)","foregroundQuantileSample":"known-object-id-nonbackground-and-depth-not-65535","semanticSampleSource":"exact-object-id-palette"}`.

The percentile population is every pixel whose object-ID RGB equals a non-background palette entry and whose depth is not `65535`; quantiles use the existing evaluator's deterministic sorted linear interpolation. Each semantic median uses only pixels matching that semantic's exact object-ID colour. `scene-metrics.json.depthEncodingBinding` must deep-equal the normalized record plus `verdict="READY_FOR_DIAGNOSTIC_RENDER"`; evaluator also verifies the actual PNG header and pixel distribution.

A nearly uniform white depth image, background/foreground ambiguity, inverted ordering, eight-bit truncation, or fewer than 64 foreground values is `DIAGNOSTIC_BLOCKED`.

## Manual visual review

Numeric or pixel success can emit at most `READY_FOR_MANUAL_REVIEW`. The independent reviewer must inspect all 20 outputs, in this order:

1. global camera, portrait hierarchy, horizon, vanishing depth, and road bands;
2. road primary mass and medium fractures/strata/undercuts/rubble;
3. canyon near/mid/far layers, negative spaces, occlusion, and atmospheric falloff;
4. courier and hazard silhouettes, supports, contact, and canonical clearance;
5. closeup pursuer anatomy, grounded limbs, runner separation, and no clipping;
6. PBR material variation, warm/cool light, contact shadows, and fog integration;
7. complete editable Tide Scar longitudinal path and near loop;
8. object-ID, road-mask, normal, and linear-depth correctness.

Any flat strip road, low-poly blockout, repeated primitive, wall corridor, black beauty frame, white depth frame, cropped Scar loop, unreadable anatomy, floating/detached support, hidden gap floor, z-fighting, interpenetration, near-plane clipping, or material-only detail returns `MANUAL_BLOCKED`. Pixel gates never override that result.

## Checkpoint and execution order

1. **C7-D1 coordinator contract:** this review-request commit only. No implementation or process launch.
2. **Independent contract review:** read-only against the exact C7-D1 SHA and these coordinator documents. It returns `READY_FOR_DIAGNOSTIC_007_CONTRACT` or exact P0/P1 findings; it cannot edit production or evidence. Draft `2f5fa9c` was blocked and is not authority; this corrected revision requires a fresh verdict.
3. **C7-D2 coordinator authorization:** only after a ready verdict, a separate docs-only commit records execution authority and exact accepted review provenance.
4. **C7-T1 generator reconstruction:** the single asset writer changes exactly `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`; AST/static checks only. Its size is an explicit atomic exception because this self-hashed scene generator cannot be partially staged without falsifying construction provenance.
5. **C7-T2 evidence predicate/depth evaluation:** the same writer changes exactly `tools/temple-asset-pipeline/run_tide_scar_tr4_pack.py` and `evaluate_tide_scar_tr4_pack.py`; AST/static checks plus the non-writing positive/negative dry predicate test only.
6. **Authorized dry preflight:** only after C7-T1 and C7-T2 are committed and hashes are stable. It must stop before Blender on any mismatch.
7. **C7-E1 diagnostic evidence:** one Blender 4.5.5 background process, exactly 20 PNG writes, then at most one evaluator. New `diagnostic-007/**` plus its exact ignored `blender.log` form a separate evidence commit. No retry.
8. **C7-V1 independent visual review:** whenever the runner stops with the exact complete 20-PNG set, regardless of evaluator invocation/result, perform docs-only `TR4_DIAGNOSTIC_REVIEW.md` and visual-review `THREAD_LOG.md`; no repair or rerender. An incomplete set is not manually reviewed.

Every asset step appends `docs/workstreams/temple-tr4-asset/THREAD_LOG.md`. Every commit stages exact paths and separates coordinator docs, source, generated evidence, and independent review. Export, runtime adoption, browser work, final typecheck/full Vitest/build, independent candidate QA, changelog acceptance, and push remain blocked regardless of C7 numeric success.
