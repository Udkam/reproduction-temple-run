# Temple R1H-C1 blocked-candidate correction contract

Date: 2026-08-09 Asia/Shanghai

Status: **R1H candidate `8112156` is BLOCKED; one bounded C1 geometry correction is authorized; R1H and the complete game remain in progress**

## Immutable inputs and disposition

- Branch: `main`.
- Pushed contract baseline: `056b68701d71bb2c618e131d24039f53d646caff`.
- Unpushed blocked source candidate: `8112156c8dd90bdd1821fbce5314b125cf912ebf`.
- Preserved failed evidence directory: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-candidate-8112156-20260809T220359291`.
- Failed manifest: `candidate-8112156-browser-evidence.json`.
- Manifest SHA-256: `29360C33992B48CCE62ED1C42AE2335363C2F563AE8ADE6F8A883B63C8D981BF`.
- Capture-script SHA-256: `13B58CD85F8D3F0F30577BBBCF7DCAA6C038BD46DBB1CC75ECC1D6065E21C4DF`.

The source review of `8112156` is `READY` with no P0/P1/P2 for the bounded topology and projection claim. That does not accept R1H. Independent evidence QA is `BLOCKED` because the manifest is `failed`, and independent visual QA is `BLOCKED` because all 14 candidate PNGs still show the defects R1H was required to remove. The failed manifest, all 14 PNGs, both logs, and the source commit remain immutable failure history; they are not rewritten, removed, replaced in place, or described as accepted evidence.

## Confirmed root causes

The fixed `140 ms` sleep in the failed capture did not establish a deterministic presentation pose. Canonical state, viewport, FOV, runner world position, calls, and triangles match the accepted R1G baseline, but `running-landscape-tick60` recorded camera `z=11.186076609486689` instead of baseline `z=4.150890634103529`. The runner therefore shrank from `90.25220231053049 px` to `59.96653025884419 px`. Several other records also have multi-metre camera drift. No runner, camera, profile, or viewport source changed in `8de73c1..8112156`; the only product paths are the Tide Scar geometry and its direct test. The existing `84-91 px` landscape courier gate remains authoritative and cannot be relaxed.

The geometry failure is independent of that capture fault. Same or near-same camera records still show repeated extruded blocks, a long left foreground wall, a shallow/equal roof band, weak near/mid/far separation, a broad structureless right-side void, and thin black seams. Actual-triangle raycasts identify the principal owners:

- near shelf run seed `11`: interior stations 1/2/3 are almost co-linear at inner `11.72/11.68/11.14 m` and top `3.04/3.42/3.08 m`, producing the long left wall;
- mid shelf run seed `47`: station 0 front cap and segment 0-1 own the landscape void's inner edge and the desktop right-side horizontal seam;
- near seed `17` contributes only the nearer inner edge and is not permission to widen one giant wall across the void;
- horizon seed `421` owns only the outer/upper closure, while the existing crown relief is applied only to tier 0 and therefore does not reliably reshape the visible outer skyline.

## Exact C1 source authority and budget

One sole writer may modify exactly:

- `src/game/render/tideScarWorld.ts`
- `src/game/render/tideScarWorld.test.ts`

The C1 base is `8112156c8dd90bdd1821fbce5314b125cf912ebf`. The complete R1H source range from accepted R1G base `8de73c169d03ce32e15bce2145d64afff8973330` remains within the original `500` hand-authored added-or-modified-line budget. The blocked candidate already consumes `171` lines of churn; C1 may add or modify at most `320` more lines, with at most `90` production lines and `230` direct-test lines. Line compression cannot evade the budget.

Production authority is limited to deterministic position rules for the existing shelf stations and the existing 12 horizon islands' six rings/crowns. It may:

- apply seed/station-specific x/y/z offsets to existing stations, including the diagnosed seed `11`, `47`, and secondary seed `17` positions;
- move existing crown, shoulder, wall, and return profile-step vertices independently so the result is not another rigid extrusion of one cross-section;
- propagate bounded deterministic crown relief through the existing visible outer rings and apply deterministic whole-island vertical staggering;
- change only existing numeric position tables and pure calculations that produce those vertices.

It may not add a run, station, profile step, island, ring, tier, face, index, mesh, material, object, group, instance, texture, shader path, light, fog element, camera behavior, road element, actor, hazard, UI element, package, or owned resource.

## Frozen proof

C1 retains the abyss plus three named canyon meshes, their four existing material owners, object names, vertex/index counts, and every index byte. It retains 12 islands with eight stations, six tiers, and 96 triangles each; all run/seed/side/station counts; zero groups and zero instancing; the far index SHA `15c61b15613bc21f5aba67e4b5ba4b6c22ebe80f80c40e640b5c480ebb12c402`; cut/shoulder factors; the near/mid `.04` final radial bridge; all 128 near/mid upper-riser triangles within `.045 <= normalY < .55`; shelf ratios; far overhang; surface attributes and treatment rules; zero emissive; map ownership/strength/floor; hemisphere correction; quantized world cell/yaw; genuine gaps; route clearance; disposal; and the exact calls/triangles matrix.

Position-derived bounds, positions, normals, UVs, colours, and fingerprints remain reopened only where authorized vertex movement recomputes them. Camera, FOV, lens shift, runner scale, runner geometry, route/collision, simulation, lifecycle, materials, lighting, fog, and exposure are frozen. None may be used to make C1 appear improved.

## Required direct geometry gates

All new proof is reconstructed from actual `position` and `index` buffers. `userData`, AABBs, metadata, vertex-only projection, or a self-reported hash cannot satisfy it.

1. Every existing manifold, winding, non-degenerate, topology, material, bridge, riser, shelf, overhang, gap, route-clearance, determinism, and disposal gate remains unchanged.
2. For the five-station seed `11` run, the three interior crown/inner stations have lateral range at least `1.25 m` and elevation range at least `1.50 m`; each of the two interior adjacent pairs changes laterally by at least `.75 m` and vertically by at least `.75 m`.
3. For every four-station run, the two interior crown/inner stations differ laterally by at least `.75 m` and vertically by at least `.50 m`. At least one actual crown-versus-shoulder displacement per run differs by `.35 m` laterally or `.30 m` vertically, proving non-rigid profile shaping rather than whole-section translation.
4. The actual visible upper-outer horizon ring, not only the hidden top-inner ring, retains vertical relief of at least `.55/.40/.26 m` for near/mid/far and below `1.35 m`; each band retains at least three distinct visible outer-ring profiles. Whole-island visible roof means span at least `.50 m` in each band.
5. The corrected homogeneous clipping, left/right separation, aspect-normalized gap, `.02H` needle rejection, 2,048 midpoint scanlines, and near/mid/far union-height gates from `056b687` remain exact. No bank may hide the other bank's failure and no uncovered row may be fabricated into coverage.

The known landscape ROI `x≈595..844, y≈198..390` and desktop seam `x≈1160..1200, y≈451..454` remain binding manual gates. A read-only diagnostic could not establish a trustworthy depth-resolved occupancy threshold without contradicting its own raycasts, so this contract does not invent one. If the new full-resolution frames retain either one-piece black void, the thin right seam, a long left seed-11 wall, or a box/extruded-corridor reading, visual QA returns `BLOCKED` regardless of numeric tests.

## Deterministic same-view evidence correction

After the last C1 source edit, development runs only:

`npm.cmd run test -- src/game/render/tideScarWorld.test.ts`

Then the coordinator creates the source checkpoint and runs exactly one new typecheck, one complete Vitest suite, one no-delete production build to a new unique directory, and one browser pass to a new unique evidence directory. The old failed directory is read-only.

The browser script must bind and verify the accepted R1G baseline manifest SHA-256 `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`. Before each screenshot it must fail closed until the candidate camera naturally reaches the same record's baseline position within `.05 m` on each x/y/z axis; FOV and yaw must match exactly. A fixed sleep alone is invalid. The script may observe the unchanged presentation camera but may not set or patch the runtime camera, change scale, loosen the `84-91 px` landscape runner gate, or alter canonical state.

The new manifest keeps the complete 14-record seed/tick matrix and exact calls/triangles constants. Every record binds the new candidate SHA, baseline camera record, actual candidate camera record, canonical/replay hash equality, screenshot SHA-256, one canvas, and zero gameplay DOM, overflow, browser problems, or context loss.

Manual QA compares all 14 original-resolution candidate frames against the same-view R1G baseline, prioritizing `gait-phase-7-desktop-tick88`, `running-portrait-tick60`, `slide-mid-landscape`, and the technically corrected `running-landscape-tick60`. Any building/box/extruded-corridor reading, entire-side wall, repeated/equal roof band, swallowed middle/far layer, flat skyline strip, mirrored banks, structureless void, repeated needle seam, filled genuine gap, floating/intersecting/flipped rock, z-fighting, gameplay/HUD occlusion, or camera/material/light/fog-only change is `BLOCKED`.

## Checkpoint and push boundary

This contract checkpoint is stacked above unaccepted source commit `8112156`; pushing it alone would also publish a visually and evidentially blocked candidate. It therefore remains local until the complete C1 source, evidence, independent QA, and coordinator acceptance chain is ready. No history rewrite, force push, duplicate acceptance branch, deletion, or evidence replacement is permitted.
