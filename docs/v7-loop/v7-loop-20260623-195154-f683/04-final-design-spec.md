# Final Design Spec

## Product identity

Driftbox v7 is a 2D sci-fi puzzle game about moving energy cores through quantum chambers. It is no longer a warm paper/wood Sokoban and no longer a 2.5D experiment.

## Visual style

- Dark neutral lab base with high-contrast neon accents.
- Clear color coding for actors, cargo, portals, time echoes, swap anchors, recursive room anchors, chain state, and goals.
- Animated route lines, pulses, and blocked feedback.
- No wood-box or paper feel.
- No visible 3D/2.5D mainline.

## Character

Final character: quantum drone.

Required states:

- idle: stable core pulse.
- moving: thrust trail in movement direction.
- pushing: front emitter compresses against block.
- pulling: tractor tether if pull remains active.
- sync: linked drones share a harmonic ring.
- teleport: core collapses into portal ring then reappears.
- split: echo shell separates from main drone.
- blocked: short red shield ripple and reason label.
- victory: orbiting particles and expanded core ring.

## Screens

- Home command deck with progress, recent level, continue experiment, chapter star map, mechanism archive, challenge record, settings.
- Chapter star map with unlock, complete, master, current recommendation, and illuminated cleared paths.
- Game screen with sci-fi HUD, actions, mechanism badges, clear feedback, and mobile-safe controls.
- Win screen with completion transition, next level, records, and chapter progress.
- Mechanism archive with icons, rules, diagrams, and no full solutions.
- Settings/help with accessibility, high contrast, reduced motion, reset progress, and input help.
