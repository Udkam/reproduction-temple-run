# TIDE//RELAY Design Contract

## Intent

`TIDE//RELAY` is an original browser endless runner about carrying a star-map core across a flooded astronomical ruin. Fidelity means the continuous chase rhythm, readable third-person danger, swipe grammar, acceleration, score-and-distance hierarchy, and immediate feedback of a classic mobile runner. It does not mean duplicating Temple Run trade dress or content.

## Aesthetic direction

The signature gesture is a jade survey line running through every weathered causeway. It behaves like a human route annotation against an organic ruin instead of a science-fiction HUD effect.

- Mist sky `#c7d8d1`: humid horizon and atmospheric depth.
- Weathered stone `#4b5148`: road and structural masses.
- Porcelain `#e7dfca`: runner highlights and broken observatory shells.
- Foliage `#315b4a`: moss, damp rock, cloth, and oxidized instruments.
- Route jade `#12ae9d`: meridian seam, pickups, and positive feedback.
- Hazard coral `#c9513a`: cut faces and danger edge accents only.
- Sun brass `#e7c68a`: lane calibration and restrained antique detail.
- HUD ivory `#f7f4ea`: high-contrast interface copy.

Geometry is low-poly but authored: uneven masonry, wet soil, mossy rubble, porcelain cuts, warm metal, water fog, and celestial instruments. Bloom is restrained; fog and particles support depth but never hide path edges or obstacle silhouettes. CRT scanlines, glass panels, and generic neon-console decoration are forbidden.

## Technology and boundaries

- React 19 + TypeScript + Vite for the application shell.
- Three.js/WebGL for the world, character, camera, particles, and effects.
- Deterministic, serializable simulation under `src/game/core`.
- Fixed 60 Hz runtime with bounded catch-up and interpolated presentation.
- Procedural WebAudio with a bounded voice pool; no copied audio.
- Local storage only for settings and best score, outside canonical state.
- Vitest for rules/runtime tests and Python Playwright for browser evidence.

## Camera and composition

- Perspective camera FOV starts at 47 degrees and may ease toward 53 degrees at maximum speed.
- Portrait is the primary composition. The runner occupies roughly 18–24% of viewport height with at least 2.3 seconds of readable path ahead.
- Lane shifts complete in about 180 ms with a small camera lag.
- A jump lasts about 650 ms; camera follows at most 18% of vertical travel.
- A slide lasts about 520 ms; camera lowers by no more than 6% of runner height.
- A 90-degree turn uses a 320 ms monotonic yaw transition that keeps old and new path visible at midpoint.
- Collision impact is one 70 ms directional impulse plus a short recovery, not continuous shake.
- Reduced motion disables shake, FOV breathing, speed streaks, and decorative particles.

## Gameplay presentation

- Runner: narrow courier silhouette, split coat tail, articulated pelvis/chest/arms/forearms/legs/shins/feet, speed-scaled gait, grounded contact shadow, and distinct jump/slide recovery poses.
- Pursuer: an abstract two-figure black-tide pack, never a monkey or animal imitation. Its canonical gap starts close, opens during safe running, closes after every non-gap obstacle stumble, and becomes visually prominent near capture. Repeated misses must end through a reachable pursuer capture instead of a fabricated QA state.
- Collectible: translucent triangular signal shard, never a round gold coin.
- Jump obstacle: fallen surveying timber with coral cut faces.
- Slide obstacle: a low astronomical ring supported as a readable gate.
- Lane obstacle: an asymmetrical broken statue and rubble pile, not a plain cylinder.
- Gap: a missing stone span with two coral lips and a clearly visible far edge.
- Shield: orbiting meridian lattice around the runner.

Non-gap impacts are recoverable stumbles: the obstacle resolves once, the courier loses speed briefly, and the pursuer closes a deterministic distance. A shield absorbs the direct impact feedback but is consumed and still preserves deterministic chase pressure. Gap falls and wrong or missed turns remain immediate failures because they break the route rather than the chase rhythm.

## Interface

- Ready screen: title, short premise, primary start action, best distance, controls, accessibility settings.
- Running HUD: score is the largest number, distance is second, shards/flow are supporting data, and pause stays isolated. No large opaque panels cover the route.
- The browser QA surface exposes the exact canonical score, floored distance, shards, and flow values rendered by the HUD. Evidence must compare those values rather than accepting non-empty text.
- Every 250 m emits one deterministic milestone and shows a short 600–900 ms route callout.
- Pause: simulation frozen, route remains visible and desaturated.
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

- Desktop scene-preparation CPU p95 below 8 ms; mobile below 12 ms.
- Normal desktop draw calls at or below 60 and visible triangles below 150k.
- Mobile DPR is capped at 1.75; expensive shadows and decorative particles scale down.
- Retain a bounded course window and reuse or dispose Three.js resources.
- WebAudio voices are capped at 16.
- Headless rAF timing is diagnostic only; a fixed-workload CPU benchmark is the automated performance gate.

## Evidence geometry

- QA scenarios are replayable traces from `createInitialState(seed)` using only public commands, including milestone, close chase, and beam/ring/column/gap previews.
- The render snapshot exposes clipped CSS-pixel bounds for the pursuer and every visible hazard occurrence. A center point alone is not sufficient evidence.
- Pursuer evidence requires a meaningful positive clipped area, and obstacle evidence requires the expected canonical kind plus a positive clipped area in the fixed viewport.
- Desktop, portrait/mobile, and high-contrast captures must collectively prove all four hazard silhouettes while preserving one canvas and zero DOM gameplay entities.

## Non-goals

- Accounts, ads, purchases, online leaderboards, multiple characters, a shop, licensed music, or copied assets.
- A complete reproduction of every commercial level theme, power-up, achievement, or meta system.
- Tilt-only steering; keyboard and one-finger gestures are the primary controls.
