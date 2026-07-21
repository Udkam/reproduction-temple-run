# TIDE//RELAY Design Contract

## Intent

`TIDE//RELAY` is an original browser endless runner about carrying a star-map core across a flooded astronomical ruin. Fidelity means the continuous chase rhythm, readable third-person danger, swipe grammar, acceleration, score-and-distance hierarchy, and immediate feedback of a classic mobile runner. It does not mean duplicating Temple Run trade dress or content.

## Aesthetic direction — Tide Scar TR4 (in progress)

TR4 is the current visual authority. It targets a portrait-first, high-vantage third-person composition: a narrow but physically thick warm sandstone causeway fills the lower frame, bends through broken lips and strata, and recedes into a cold blue-black basalt canyon with distinct near/mid/far silhouettes and atmospheric falloff. The white Tide Scar is a procedural editable path gesture; sparse coral mineral deposits mark fresh breaks without becoming UI.

The approved reference supplies only high-level composition, depth, material, lighting, tension, and readability. No commercial or reference image, frame, mesh, texture, character, monster, UI, logo, or map may ship. The exact clean-room camera, construction, material, trap, anti-clipping, semantic-root, and evidence contract is `docs/workstreams/temple-tr4-coordination/TR4_VISUAL_CONTRACT.md`.

The courier remains an original articulated star-map runner. The rock-armored pursuer is a cinematic bookend: visible on the ready/opening beat and game-over ending beat only, absent during ordinary running, close-pressure, milestones, hazard previews, and pause. Canonical `chaseGap` remains deterministic pressure data and may drive presentation cues without exposing a continuous monster mesh.

### R1 runtime environment implementation

R1 replaces the legacy inward panorama/card canyon with deterministic geometry: irregular near cliff lips, interrupted mid-depth buttresses, and a desaturated far silhouette. The camera must read a thick broken causeway in the lower frame, playable middle depth, and open negative space to the horizon; fog is depth-based atmosphere only, never a card or full-width band.

The R1D silhouette layer uses closed terraced rock bodies rather than repeated prisms: separate shelf elevations, broken returns, non-mirrored notches, and limited overhangs preserve genuine negative space without adding a continuous wall. R1E keeps that massing fixed and makes it readable through one continuous clean-room basalt surface language. World-scaled UVs and face-aware values distinguish upward caps and shelves from risers, notch returns, and undersides; texture/value contrast is strongest near the camera, restrained in the middle distance, and quietest at the horizon. Extreme cavity readability may use only a bounded face-scoped additive shift of the scene's existing hemisphere sky/ground mixing weight before native AO and PBR output: top/shelf/wall stay unchanged, return receives at most `.10`, underside at most `.15`, and no correction exists without a HemisphereLight. It cannot alter normals, direct/specular light, shadows, emissive, exposure, or post-light output. Surface treatment must not become a checker, noisy displacement illusion, stretched seam, black wall, glowing recess, flat gray panel, or substitute for geometry.

Deferred R1F design, not current source authority: when separately reauthorized after R1E acceptance, R1F keeps canonical travel and collision flat and deterministic while rebuilding the visible causeway skin from six continuous instanced sandstone signatures. Each module uses connected, non-coplanar medium-scale top panels, shallow worn joints that never read as gameplay gaps, and asymmetric broken lips/returns grounded into real side mass. A world-anchored two-scale sandstone response separates sunlit tops, worn edges, and recessed faces without emissive lift, repeated tile stamps, or texture swim. Module terminals remain continuous, the playable corridor cannot acquire a false hole or safe lane, and presentation geometry cannot obscure a beam, ring, column, gap, turn, or runner pose.

Existing `beam`, `ring`, `column`, `gap`, and turn semantics remain unchanged. TR4 remaps them visually to an original fractured jump threshold, supported low-clearance arch, asymmetrical lane blocker, broken span, and route-end cliff. Any primitive/blockout appearance, flat water band, repeated wall corridor, featureless strip road, clipping, detached limb, floating support, or pixel-gate-only completion claim is a visual failure.

## Historical aesthetic direction — Tide Scar D4 (TR3-005C, superseded by TR4)

The signature gesture is a weathered chalk-white **Tide Scar** following the right road edge through a warm mineral causeway. It is a route annotation in the world, not an interface line: it tightens only under canonical close pursuit, may briefly show coral abrasion there, and never crosses the sky or HUD.

- Sand `#e7d6b4`: warm mineral road surface and restrained HUD highlight.
- Sandstone edge `#8f7659`: broken causeway faces and distant cliff silhouettes.
- Tide blue `#10283c`: deep canyon, contact shadows, and pursuer mass.
- Tide blue light `#31536b`: misted middle ground and water-plane depth.
- Tide Scar `#f4ecd8`: single readable right-edge guide only.
- Hazard coral `#b84432`: sparse cut faces, broken lips, and pursuer dorsal scars only.
- Ink `#14202b`: high-contrast HUD labels and controls.

TR3-005A reconstructs that language as a high-fidelity but still stylized Three.js scene: irregular warm deck caps and downward cliff aprons over a cold blue canyon, a curved distant-canyon panorama, three fog bands, sparse outer-lip coral, and one analytic right-edge Tide Scar. Only the seven D4A manifest-approved WebP/PNG derivatives may load at runtime; the D4 composition and north-star images are never runtime assets. Procedural terrain decoration is section/event-seeded presentation data only; it must not alter lanes, collision semantics, canonical state, or replay hashes. CRT scanlines, glass panels, neon grids, card arrays, copied commercial imagery, and generic telemetry decoration are forbidden.

## Technology and boundaries

- React 19 + TypeScript + Vite for the application shell.
- Three.js/WebGL for the world, character, camera, particles, and effects.
- Deterministic, serializable simulation under `src/game/core`.
- Fixed 60 Hz runtime with bounded catch-up and interpolated presentation.
- Procedural WebAudio with a bounded voice pool; no copied audio.
- Local storage only for settings and best score, outside canonical state.
- Vitest for rules/runtime tests and Python Playwright for browser evidence.

## Camera and composition

- D4 freezes camera FOV by profile: desktop `43°`, portrait `40°`, landscape `46°`. Classification is landscape first (`height <= 520 && aspect > 1.5`), then portrait (`aspect < .72`), otherwise desktop. Speed never changes FOV.
- TR4 C5 replaces the failed C4 offline framing with an explicit right-handed `+Y`-up basis. Desktop uses camera `(0,6.06,13.60)` toward `(0,.60,-13.30)`; portrait uses `(0,6.20,15.20)` toward `(0,.55,-16.80)`; landscape uses `(0,6.15,12.80)` toward `(0,.55,-12.56)`. Their analytic target is a horizon near `.23H` and courier anchor near `.67H`; closeup uses `(0,5.40,9.80)` toward `(0,1.15,-3.40)`. Frozen FOV, near/far, and lens shifts remain the WebGL projection values in the TR4 contract; turns change path yaw/position only.
- C6 proved that this construction and its matrix transpose chain are upright, but is frozen `DIAGNOSTIC_BLOCKED`: runner/evaluator compared two valid near-zero landscape axis angles by direct radians at `1e-12` even though both were far below the real `1e-5` alignment ceiling. Its 20 PNGs are also `MANUAL_BLOCKED` for black beauty frames, a flat strip road, repeated low-poly canyon columns, primitive semantic models, a cropped Scar loop, and unusable white depth passes. A future C7 must repair the evidence predicate and the visible art together before one new diagnostic; unchanged C6 geometry may not be rerendered for acceptance.
- Horizon/road/runner bands, fixed look targets, and HUD clear rails are renderer evidence gates. Pursuer bounds are required only in `ready`, the deterministic opening window, and `game-over`; all ordinary running and pause records require null pursuer evidence.
- Lane shifts complete in about 180 ms with a small camera lag.
- A jump lasts about 650 ms; camera follows at most 18% of vertical travel.
- A slide lasts about 520 ms; camera lowers by no more than 6% of runner height.
- A 90-degree turn uses a 320 ms monotonic yaw transition that keeps old and new path visible at midpoint.
- Collision impact is one 70 ms directional impulse plus a short recovery, not continuous shake.
- Reduced motion disables shake, FOV breathing, speed streaks, and decorative particles.

## World presentation

- Causeway deck caps are selected by stable section hash and use repeated world-space UVs; cliff aprons, basalt teeth, and coral sit outside the canonical corridor and never redefine collision or lane meaning.
- D4 environment loading selects the exact desktop (`tide-sandstone-base-1024.webp`, `tide-basalt-base-1024.webp`, `tide-distant-canyon-2048x1024.webp`, `tide-coral-mask-512.png`) or mobile (`tide-sandstone-base-mobile-512.webp`, `tide-basalt-base-mobile-512.webp`, `tide-distant-canyon-mobile-1024x512.webp`, `tide-coral-mask-512.png`) set before `TextureLoader` construction. Desktop is `22.667 MiB` within a `38 MiB` ceiling; mobile/low-GPU (`<=430px`, `deviceMemory <=4`, or coarse-pointer short landscape) is `6.667 MiB` within an `18 MiB` ceiling. Failed loading falls back to flat PBR without blocking gameplay; destroy disposes textures, materials, and geometry.
- The Tide Scar is an analytic, camera-independent right-edge ribbon with 2–5 hash-derived pre-clip intervals and 42–64% requested coverage. It uses `.32–.46m` inset, `.07–.11m` width, `±.018m` lateral and `±12%` width jitter, and 0–2 dry gaps; renderer-only deck occupancy and unresolved hazard/gap silhouettes are subtracted before vertices are built. A canonical gap removes only its local span, and evidence records per-segment clipped polygons rather than a global AABB.
- TR4 diagnostic beauty uses AgX / sRGB with exposure `0`, a road-facing warm key, opposite cool fill, aimed contact bounce, world `#6E8294` at strength `.55`, and volumetric fog `#9AA7A8` at density `.0035` / anisotropy `.18`. The historical D4 runtime values below remain unaccepted until a later runtime-adoption contract.

## Gameplay presentation

- Runner: narrow courier silhouette, split coat tail, articulated pelvis/chest/arms/forearms/legs/shins/feet, grounded contact shadow, and continuously interpolated eight-phase gait. Low, medium, and high speed alter cadence, arm swing, and contact compression only; reduced motion retains readable alternating poses while removing secondary swing.
- Pursuer: an original black-rock quadruped with head, shoulder mass, four readable limbs, contact shadow, and sparse coral dorsal scars. It is required in `ready`, required only while `elapsedTicks < 54 AND distance < 6m` during `running`, hidden for all other running and every paused frame, and required for all `game-over` frames. Canonical `chaseGap` remains active while hidden; only visible non-capture bookend frames require separated geometry.
- Collectible: translucent triangular signal shard, never a round gold coin.
- Jump obstacle: a thick fallen sandstone beam with coral-cut end caps, support feet, and a contact shadow.
- Slide obstacle: a low, double-supported mineral ring with an unmistakable negative-space opening.
- Lane obstacle: an asymmetrical broken tide-worn column and grounded rubble, not a plain cylinder.
- Gap: a missing stone span with broken near edge, coral lips, deep tide below, and a clearly visible far edge.
- Shield: orbiting meridian lattice around the runner.

Non-gap impacts are recoverable stumbles: the obstacle resolves once, the courier loses speed briefly, and the pursuer closes a deterministic distance. A shield absorbs the direct impact feedback but is consumed and still preserves deterministic chase pressure. Gap falls and wrong or missed turns remain immediate failures because they break the route rather than the chase rhythm.

## Interface

- Ready screen: title, short premise, primary start action, best distance, controls, accessibility settings.
- Running HUD: score is the largest number, distance is second, shards/flow are supporting data, and pause stays isolated. No large opaque panels cover the route.
- The browser QA surface exposes the exact canonical score, floored distance, shards, and flow values rendered by the HUD. Evidence must compare those values rather than accepting non-empty text.
- Every 250 m emits one deterministic milestone and shows a short 600–900 ms marker anchored to the right road edge/Tide Scar, with zero intersection with HUD, runner, pursuer, or obstacle bounds.
- Pause: simulation frozen, and only the real viewport is locally darkened/desaturated without a large modal.
- Failure: `SIGNAL LOST`, final distance, score, shards, best, and restart.
- Desktop: keyboard controls plus optional visible action buttons.
- Mobile: full-screen gesture surface, safe-area pause button, compact HUD, and a one-time gesture legend.

## Input

- Left/right or A/D: lane shift; within a turn window, submit that turn instead.
- Up/W/Space: jump.
- Down/S: slide.
- Escape/P: pause.
- R: restart only from ready, paused, or game over.
- Mobile swipes use dominant-axis CSS-pixel displacement and velocity. A gesture can dispatch only one action.
- Buttons and gesture starts are isolated so UI presses cannot leak into runner swipes.

## Accessibility and responsive behavior

- One semantic `h1`, logical landmarks, visible keyboard focus, and restrained `aria-live` status.
- HUD text meets WCAG AA and hazards have shape/pattern cues.
- Every mobile target is at least 44 CSS px and respects safe-area insets.
- Desktop, portrait 390 x 844, and landscape 844 x 390 must show the full actionable route without horizontal overflow.
- Canvas has an accessible label; gameplay world objects are never represented as DOM lists.

## Performance budget

- TR4 scene-preparation CPU p95 remains below 8 ms desktop and 12 ms mobile on all fixed profiles.
- TR4 draw calls include shadow passes and are at or below 60 desktop / 45 mobile; visible triangles are at or below 150,000 desktop / 100,000 mobile. The older D4 46/38-call and 190k/115k-triangle limits below are historical development evidence, not current TR4 authority.
- Mobile internal DPR is capped at 1.5; expensive shadows and decorative particles scale down before runner, pursuer, obstacle, or Tide Scar silhouettes are removed.
- Retain a bounded course window and reuse or dispose Three.js resources.
- WebAudio voices are capped at 16.
- Headless rAF timing is diagnostic only; a fixed-workload CPU benchmark is the automated performance gate.

## Evidence geometry

- QA scenarios are replayable traces from `createInitialState(seed)` using only public commands, including milestone, close chase, and beam/ring/column/gap previews.
- The render snapshot exposes clipped CSS-pixel bounds for every visible hazard occurrence, plus profile camera pitch, horizon, vanishing point, bottom-road width, and runner-center bands. Pursuer bounds exist only in TR4 bookend states and are null while hidden; a center point alone is not sufficient evidence.
- Tide Scar proof is a per-section/per-interval/per-segment clipped polygon with DPR-outward pixel bounds and visible area; HUD/hazard collision tests use those polygons and actual HUD content rectangles.
- Visible bookend pursuer evidence requires meaningful positive clipped area; ordinary running and pause evidence requires `visible=false` and null position/bounds/area/gap. Obstacle evidence requires the expected canonical kind plus positive clipped area in the fixed viewport.
- Desktop, portrait/mobile, and high-contrast captures must collectively prove all four hazard silhouettes while preserving one canvas and zero DOM gameplay entities.
- Historical TR3 proof recorded continuous non-capture pursuer gaps. TR4 supersedes that visibility gate and instead records exact lifecycle boundaries, the exact four canonical HUD values, eight-phase continuity samples, its current 60/45-call and 150k/100k-triangle budgets, and scene-preparation p95 below 8 ms desktop / 12 ms mobile.

## Non-goals

- Accounts, ads, purchases, online leaderboards, multiple characters, a shop, licensed music, or copied assets.
- A complete reproduction of every commercial level theme, power-up, achievement, or meta system.
- Tilt-only steering; keyboard and one-finger gestures are the primary controls.

## TEMPLE-TR3-A3 IN PROGRESS — not integrated

This bounded A3 activity is an offline, clay-only structural environment-art proof. It studies one original S-like fractured mineral causeway, three-layer fog canyon, readable courier/pursuer chase band, supported broken-stone arch, and an editable right-edge Tide Scar using deterministic local Blender Python geometry only. It preserves every runtime, renderer, UI, canonical-state, rule, replay, and browser-evidence path byte-for-byte. A3 stops after exactly one portrait/desktop/closeup clay batch and its deterministic/manual structural gate; it does not authorize final materials, export, optimization, runtime integration, browser capture, commit, push, or QA.

## TEMPLE-TR3-A4 IN PROGRESS — not integrated

A4 is exactly one offline, low-resolution clay batch derived from the closed A3 proof. It may correct only camera framing, the original pursuer transform/rig silhouette, and broken-stone ring/support geometry while preserving A3's causeway modules, canyon bands, clay values, Tide Scar recipe, route counts, and triangle budget. It stops after one portrait/desktop/closeup Blender 4.5.5 batch plus one deterministic verifier and manual structural review; no final materials, GLB/KTX2 export, optimization, runtime/browser work, commit, push, or QA is authorized.

## TEMPLE-TR3-A5 AUTHORIZED - one offline clay composition proof only

**A3 and A4 are closed BLOCKED.** Their generators, evidence, hashes, and reports remain immutable. This addendum authorizes exactly one clean-room A5 Blender 4.5.5 process in a separate A5 proof directory, not a runtime or product slice. A5 replaces only offline causeway/canyon visual builders, pursuer route-frame placement/rig, supported arch assembly, profile cameras, and Tide Scar mask extraction. It never changes gameplay data.

The one deterministic chase state renders portrait 540x960, desktop 960x540, landscape 844x390, and closeup 640x480. Portrait, desktop, and landscape emit beauty, object-ID, road-mask, and depth PNGs from the same scene/camera state; closeup emits beauty only. One evaluator runs once after that one Blender process, then the four beauty frames are inspected manually once. No diagnostic/final split, retry, export, GLB/KTX2, texture, browser, build, runtime, commit, push, or QA action is authorized.

Immutable A3 facts are seed 270803; roots in the fixed order Causeway_Root, Canyon_Root, Runner_Root, Pursuer_Root, Obstacle_Ring_Root, TideScar_Ribbon_Editable; clay-only values; 16 modules / 17 SPINE samples / 125.949 m / 120.494 degrees yaw / 5.95 m range / .68 corridor; three canyon bands with 6/10/4 groups, three portrait abyss openings, near-wall ceiling, no generic continuous walls; editable clipped right-edge Tide Scar; and <=45,000 triangles. A5 metadata compares exact A3/A4 sources and preserves the A4 values in baselineFailures.

All gates fail closed: 16 decorated deck caps, >=32 attached side fragments, signature run <=2, 20 unique canyon groups and zero continuous walls; a grounded deterministic route-frame quadruped; one two-support deck-contacting arch with a physical aperture; and an actual curve/spline Tide Scar extractor proving two road-right-third runs without actor/hazard intersections. Portrait courier center is x=.45-.55,y=.60-.68; pursuer x=.43-.57,y=.74-.83 with overlap >=.045W, clear gap .020-.075H, .02 containment margin, and width >=32 px; closeup pursuer is contained and >=48 px. Desktop/landscape retain their A5 visual-review bands. Hazard/ring height/opening gates are >.15H/.10W portrait, >.20H/.09W desktop, >.22H/.11W landscape. Hero frames require p50>.12, p95>.55, <=10/255 pixels <10 percent, route ROI p50>.25, positive non-black semantic ROIs, no fog card/panorama cap/full-width fog step, non-contiguous near/mid/far content, and two real occlusion boundaries.

The evaluator may report READY_FOR_VISUAL_REVIEW only when every deterministic, raster, and depth gate passes; otherwise it reports BLOCKED and never final visual acceptance. Manual detection of a blockout, featureless road, or low-poly strip wall is BLOCKED.

## TEMPLE-TR3-A6 preflight contract — no-render, not integrated

A5 is closed **BLOCKED** and remains immutable. A6 is a documentation-only recovery preflight: it authorizes neither a Blender process nor any product, asset, browser, test, build, export, Git, or QA action. Before a future coordinator-owned scene slice can start, a pure pre-render calculation must lock A3/A4 provenance and the A6 composition construction plan. A3 supplies route, canyon, root, and Tide Scar invariants; A4 is the sole clay-material authority because A3 intentionally has no `materialValues`; A5 is failed historical evidence only.

The locked plan must establish one original forward chase line in portrait, desktop, and landscape: a warm, physically thick causeway narrows toward a centered horizon through cool, separate near/mid/far canyon masses; an original courier is followed on the same corridor by an original grounded quadruped; a supported mineral arch has a readable open passage; and the Tide Scar stays an editable local right-edge world annotation. No commercial character, asset, composition, or trade dress is an input.

The preflight must calculate, before any renderer exists: typed source compatibility; frozen camera/profile bands; road cross-sections and center corridor; three or more deterministic medium-structure event types; canyon depth/occlusion plan with no slab-wall repetition; route-frame courier/pursuer relation; arch supports/aperture; and Tide Scar control-point polygons with actor/hazard exclusions. A non-green result blocks any later Blender invocation. Existing A3/A4/A5 thresholds are minima and cannot be lowered or redefined after the calculation.
