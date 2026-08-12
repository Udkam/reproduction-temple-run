# Changelog

## 2026-07-13 — TIDE//RELAY branch initialized

- Began the second game only after the Tetris branch was completed and pushed.
- Selected React, TypeScript, Vite, and Three.js for a real third-person WebGL runner rather than a DOM or flat-card imitation.
- Froze the clean-room product boundary, deterministic runner rules, original tidal-observatory visual system, responsive input contract, and browser acceptance matrix.
- Kept the branch independent from `codex/tetris` and the archived recursive-puzzle study.

## 2026-07-13 — TIDE//RELAY vertical slice completed

- Implemented a deterministic 60 Hz runner simulation with replay hashing, bounded catch-up, three-lane motion, jump, slide, 90-degree turns, gaps, beams, rings, columns, pickups, shields, scoring, multiplier, pause, restart, and game-over rules.
- Added seeded course generation with authored onboarding, reaction-distance fairness checks, deterministic fallback templates, and repeatable QA scenarios.
- Built the original storm-observatory presentation in Three.js: instanced causeways, turn platforms, meridian seams, readable lane guides, procedural obstacles, a rigged runner, chase pressure, particles, fog, responsive cameras, and reduced-motion/high-contrast variants.
- Added smooth lane interpolation, ballistic jump motion, dedicated slide/collision poses, a distance-derived Bezier turn path shared by the runner and camera, impact feedback, and procedural audio with autoplay-safe activation.
- Made post-corner lane changes continuous by applying interpolated lane displacement along the active turn yaw and returning to the canonical path without a stale endpoint frame.
- Made frozen QA frames render the canonical endpoint at alpha 1, and made reduced-motion mode freeze runner core, shield, pickup, mist, impact, camera-FOV, and decorative rotations.
- Added a React shell and accessible HUD for ready, running, paused, and failed states, including persisted best distance/score, audio/contrast settings, keyboard controls, pointer swipes, and responsive portrait/landscape layouts.
- Added strict-mode-safe lifecycle cleanup for animation frames, events, WebGL resources, audio voices, blur/visibility pause, and a development-only structured QA surface.
- Fixed late audit findings: all-lane obstacle geometry now matches collision rules; QA captures render canonical state endpoints; keyboard controls no longer swallow button activation; audio only primes from a user gesture; grounded footsteps exclude jumps/slides; horizon and turn geometry follow the route; mobile composition preserves forward visibility.
- Added a reproducible browser evidence script with a locked `playwright-core` driver and fail-closed assertions for canvas/DOM boundaries, console health, DPR caps, runner visibility, render budgets, deterministic hashes, real keyboard/touch input, turn continuity, and scene-preparation performance.
- Final verification passed: clean install of 65 locked packages; typecheck; 9 Vitest files / 37 tests; production build; 13 screenshots; 17 browser evidence records; zero console problems; zero WebGL context losses; 0.10 ms desktop and 0.20 ms mobile-context scene-preparation p95.

## 2026-07-14 — TR2 runner refinement accepted

- Reworked non-gap collisions into deterministic recoverable stumbles that close the canonical chase gap, while keeping gaps and invalid turns immediately fatal and making repeated misses reach a reproducible pursuer capture.
- Added command-derived milestone, close-chase, beam, ring, column, and gap QA scenarios with canonical replay hashes; no scenario mutates the simulation state directly.
- Refined the articulated runner, visible pursuer pressure, score-first HUD, 250 m milestone, organic ruin palette, and distinct obstacle silhouettes across desktop, portrait, landscape, high-contrast, and reduced-motion evidence.
- Extended browser evidence to 23 structured records and 19 hashed screenshots with exact HUD/state comparison, positive pursuer and per-obstacle clipped bounds, one canvas, zero gameplay DOM entities, zero console/page errors, and zero WebGL context losses.
- Final implementation verification passed: typecheck, 11 Vitest files / 47 tests, and production build; the only build advisory remains Vite's non-blocking chunk-size warning.
- Independent QA accepted candidate `c5b3db041175c19c71bd0086baf1e034fc97caf0` in log-only commit `b974810fc4b0ba93fb5ed7d6012e22c67b0606a5`. QA independently reproduced the clean install and code gates and matched every committed screenshot hash. A fresh isolated browser capture did not produce artifacts after one safe retry, so that limitation remains explicitly documented rather than hidden.
- Opened a separate design-only visual-restart study for a more distinctive mobile-first presentation. TR2 acceptance freezes the current rules and engine; it does not pre-approve those future visual changes.

## 2026-07-17 — Bounded commit policy adopted

- Added an authoritative small-checkpoint policy so source, assets, generated evidence,
  QA verdicts, and coordinator records are no longer accumulated into one large commit.
- Set a default source checkpoint budget of 10 product/test paths, 500 hand-authored
  changed lines, and one subsystem or user-visible claim, with explicit pre-authorization
  required for any atomic exception.
- Froze the inherited dirty set at `52ae9ae` as preservation-only backlog. Temple may not
  add new product scope until the current paths are inventoried and split into an ordered,
  independently reviewable commit chain.

## 2026-07-18 — Standalone repository migration

- Published the current Temple Run clean-room study as the sole `main` branch of
  `https://github.com/Udkam/reproduction-temple-run` from exact source
  `be8bcd439646656e98319c647f62ac7e11f5aa3f`.
- Repointed `origin` and the active repository contracts to the standalone
  repository and its `main` branch.
- The historical `Udkam/Game-1` remote was not rewritten or deleted. Four
  pre-existing untracked local paths remain preserved locally and were not pushed.
- Updated the active TR4 preflight path contract and tracked asset-pipeline root
  guards for `E:\Proj\reproduction-temple-run`; historical evidence paths remain
  unchanged. The untracked material-socket probe remains uncommitted, with only
  its local repository-root and branch guards migrated.

## 2026-08-08 — R1F causeway presentation accepted

- Rebuilt the runtime causeway skin as six deterministic instanced sandstone signatures with five connected non-coplanar panels, staggered short joints, asymmetric broken lips, real downward returns, and grounded side mass while preserving canonical travel, collisions, gaps, camera, actors, hazards, and lifecycle.
- Added a zero-emissive, world-anchored two-scale triplanar sandstone response with face-aware top, worn-edge, return, and underside treatment; the tracked texture remains non-owning and no render object or asset was added.
- Preserved first candidate `ccee77c` as visual-`BLOCKED` history, then accepted correction candidate `6680489cf2e3ec035da44fc1dde9aa7606bdd9c7` after targeted `8/8`, final typecheck, final `17 files / 72 tests`, production build, seven hashed browser frames, and independent source, test/evidence, and visual QA.
- Every accepted frame records one canvas, zero gameplay DOM/overflow/problems/context loss, `31` draw calls, and `24,484` triangles. R1F accepts only the causeway; courier, pursuer, hazards, character detail, animation, and the final high-fidelity game remain in progress.

## 2026-08-09 — R1G courier reconstruction accepted

- Replaced the centered ball/capsule/box courier blockout with a closed volumetric Tide courier containing a layered hood and cowl, tapered torso, mantle and harness, articulated sleeved limbs, directional boots, compact relay housing, and asymmetric split coat tails while retaining the six existing material batches, one shadow caster, canonical scale, route placement, and simulation inputs.
- Added geometry- and matrix-backed rig tests for closed non-degenerate volumes, bounds and proportions, joint/ground clearance, deterministic independent rigs, left/right gait half-cycle, speed response, reduced-motion freezing, and pose-order-independent run/jump/slide/dead transforms; courier geometry remains below the `3,200`-triangle limit.
- Corrected the hidden-pursuer presentation snapshot so both initial and live hidden records use null x/y coordinates through the same pure constructor, without changing lifecycle timing, visible placement, canonical chase state, geometry, calls, or triangles.
- Accepted candidate `8de73c169d03ce32e15bce2145d64afff8973330` after targeted courier `8/8` and renderer `6/6`, the single final post-source typecheck, `17 files / 75 tests`, production build, and 14 fixed-seed hashed browser frames. Manifest SHA-256 is `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`; all records replay deterministically with one canvas and zero gameplay DOM, overflow, browser problems, or context loss.
- Independent source, evidence, and visual QA returned `READY` with no P0/P1/P2. The original `f08a170` failed manifest remains preserved historical evidence; R1G accepts only the courier and snapshot-schema claim, while pursuer reconstruction, hazards, broader animation, lighting/material completion, and the final high-fidelity game remain in progress.

## 2026-08-13 — Project archived incomplete and prepared for remote synchronization

- Closed Temple development by user direction without claiming product completion. R1G `8de73c169d03ce32e15bce2145d64afff8973330` remains the last accepted visual checkpoint for its bounded courier/snapshot claim; the complete high-fidelity game remains `MANUAL_BLOCKED / NOT_ACCEPTED`.
- Preserved the R1H linear source history through R1H-C4 candidate `b64f09e4fd6ca687a40655cd4e5662a807139d5b`. C1/C2/C3 remain immutable evidence-`BLOCKED`; C4 source/static QA is `READY`, but its browser pass never started and produced zero PNG and no manifest.
- Authorized and committed the five existing Blender executable path migrations at `021a717b63ebc492052477d72f576e2f47e8d091` without running Blender or changing product scope.
- Preserved the two material-socket probe scripts verbatim at `cf12e4cbb6d35890813c9a76f5b043cb4d11836f` as `WIP_UNEXECUTED / NOT_ACCEPTED`; archival storage is not technical or visual acceptance.
- Kept 4,022 ignored local files / 346,391,295 bytes in place without uploading them: 3,949 `node_modules`/`dist` generated files and 73 local references, screenshots, Blender backups, or Python caches. Remote synchronization covers Git-tracked history only; the external `.codex/reference-29000m.mp4` remains local and outside the clean-room repository.
- Recorded the exact closeout boundary in `docs/agent-runs/temple-project-archive-20260813/STATE.md`. The annotated tag `archive-temple-incomplete-20260813` identifies the final coordinator closeout commit after remote verification.
