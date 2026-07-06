# Design Reference

Status: approved implementation contract. This document records browser/image
research and visual targets for staged implementation.

## Sources Reviewed

Primary official sources:

- Official website: https://www.patricksparabox.com/
- Official press kit: https://www.patricksparabox.com/press/
- Official press screenshots:
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot1.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot2.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot3.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot4.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot5.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot6.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot7.png
  - https://www.patricksparabox.com/press/images/patricksparabox_screenshot8.png
- Steam page: https://store.steampowered.com/app/1260520/Patricks_Parabox/
- GameDeveloper interview: https://www.gamedeveloper.com/design/patrick-s-parabox-
- SteamDB screenshot metadata: https://steamdb.info/app/1260520/screenshots/

GitHub and related engine references:

- `kevinychen/patricks-hyperbox`: https://github.com/kevinychen/patricks-hyperbox
- PuzzleScript archive demake:
  https://github.com/darabos/puzzlescript-archive/blob/main/itch.io/competor.itch.io/patricks-parabox-puzzlescript-demake.txt
- `4454aa/patrick-demake`: https://github.com/4454aa/patrick-demake
- JS port of TIC-80/Lua demake:
  https://github.com/4454aa/Patrick-s-Parabox-Demake---JS-Port
- PuzzleScript gists:
  https://gist.github.com/Epicmasonic/c874facc897a46493e7d444b35f30c67
  and https://gist.github.com/jaxongamer3/bbc793ccb7c2f2a47fe5358ba9362e40

## Visual Analysis From Screenshots

The reference does not look like a conventional UI around a puzzle board. It
looks like a zoomed orthographic view of physical recursive slabs.

Key observations:

- The camera is usually 16:9 and centered on a large active world, with parent
  worlds partially visible around the edges.
- Worlds are thick, flat-color slabs. Their boundaries have strong bevels,
  darker inner walls, and bright rim highlights.
- The interior play space is usually darker than the outer shell, creating a
  readable tray-like depth.
- Recursive boxes are not generic crates. They are small world windows with
  visible nested geometry inside.
- Some screenshots show black void around a world with sparse square particles;
  this makes recursion feel spatial rather than menu-like.
- Entity colors are simple but high contrast: pink/red player-like squares,
  yellow/orange containers, blue/green boxes, pale goal outlines.
- Face dots on entities communicate identity without text labels.
- Goals are thin framed sockets on the floor, not dashed form controls.
- The scene has almost no external UI chrome during gameplay.
- Recursive previews become progressively tiny but still preserve color and
  silhouette hierarchy.
- Area palettes shift by chapter: blue, gray, orange, green, purple, brown.
  The style is not one monochrome skin.

## Browser And Image Inspection Notes

Chrome inspection of the official press page found eight screenshot images with
natural dimensions of `1920x1080`. The same session confirmed the page exposes
thumbnail URLs plus corresponding full-size PNG paths. The full-size PNGs were
downloaded to a system temporary directory for analysis only; they were not
added to this repository.

A temporary contact sheet was visually inspected. It confirmed three strong
composition modes that the local recreation should support:

- Cropped parent worlds at the screen edges, with the active world occupying a
  large central or off-center region.
- Isolated worlds floating in black void, with sparse square particles behind
  the board.
- Deep nested box previews where the tiny interior still preserves palette,
  walls, goals, and entity silhouettes.

Quantitative pass on downsampled official screenshots:

| Image | Dominant family | Dark pixels | Saturated pixels | Key read |
| --- | --- | ---: | ---: | --- |
| screenshot1 | blue/magenta | 44% | 56% | full-frame nested blue slab with magenta parent crop |
| screenshot2 | black/gray/ice | 63% | 3% | isolated light slab in black void with sparse particles |
| screenshot3 | navy/rust/green | 50% | 50% | cropped parent boxes and strong side-scale contrast |
| screenshot4 | green/gold/brown | 8% | 89% | bright chapter palette with many nested rooms visible |
| screenshot5 | gray/green | 1% | 37% | muted shell around green room, goals dominate interior |
| screenshot6 | purple/cyan | 29% | 70% | large parent crop, cyan inner frame, minimal entities |
| screenshot7 | orange/blue | 4% | 94% | warm outer frame and narrow vertical recursive stack |
| screenshot8 | dark teal/cyan/red | 61% | 39% | close camera, object-scale recursion and large red box |

Measured implications:

- A single palette is insufficient. The renderer needs authored palette sets,
  not hard-coded blue UI colors.
- Black/void scenes and full-frame colored-parent scenes are both first-class
  reference modes.
- Saturated flat regions are normal. Avoid low-contrast pastel dashboards.
- The active world can fill most of the frame, but cropped parent context is
  still important.
- Tiny recursive previews must remain color-legible at screenshot scale.

## Motion And Feel Targets

The screenshots imply several motion requirements even where still images are
used:

- Entering a box should zoom into the inner world, not hard-switch views.
- Exiting should expand back out while preserving parent context.
- Pushes should have a short, confident slide with impact settle.
- Push-in should feel like crossing a threshold into a visible aperture.
- Push-out should feel like an object leaving a contained frame into the parent
  scale.
- Undo should reverse the previous motion clearly enough for puzzle reasoning.
- Failed moves should produce a subtle blocked nudge without changing state.

Routine movement should remain crisp. The target is smooth but not floaty.

## Recreated Visual System

This project should use original procedural assets that recreate the visual
language without extracting or shipping proprietary art.

Canvas-level targets:

- Full-viewport canvas-first game surface.
- Minimal React UI outside the canvas.
- Orthographic top-down projection.
- High-DPI rendering with pixel-stable geometric edges.
- Deterministic camera for visual QA.

World frame targets:

- Thick outer shell.
- Darker recessed interior.
- Beveled inner rim.
- Thin bright outline on selected or active recursive frame.
- Masked inner content.
- Optional void particles behind detached worlds.

Entity targets:

- Player: square body with two circular eyes/dots; clear facing or interaction
  hint may be added if it does not break fidelity.
- Pushable box: solid square with side tabs/shadow and color-coded body.
- Recursive container: square aperture/window with visible inner world preview.
- Goal: floor socket frame with target-specific symbol.
- Wall/boundary: part of world geometry, not separate UI tiles.

Palette targets:

- Area palettes should be authored as token sets: shell, rim, interior, shadow,
  goal, player, box variants, void.
- Avoid old failed palette choices that made the board look like a dashboard or
  spreadsheet.
- Avoid decorative gradients, bokeh, or UI-card backgrounds.

## GitHub Reference Lessons

The available public demakes and ports are useful for rule research, but they
are not suitable architecture models for this project.

Related engine audit:

| Reference | Observed structure | Useful lesson | Boundary for this project |
| --- | --- | --- | --- |
| `kevinychen/patricks-hyperbox` | Static web project with `index.html`, `rendering.js`, `serialization.js`, `tree.js`, and level files; README frames it as Parabox in hyperbolic space. | Recursive spatial games benefit from explicit rendering, serialization, and tree/graph modules instead of an all-in-one move function. | It is JavaScript/HTML and a different hyperbolic experiment, not the React + TypeScript + PixiJS/WebGL architecture target. |
| `4454aa/patrick-demake` | Static HTML + Canvas + ESM demake with import/export for Parafox or official `version 4` text levels and replay records keyed by level hash. | Level import, content hash identity, and replay persistence are worth planning early. | Its no-build Canvas approach and compatibility with official formats are reference ideas only; do not copy levels or assets. |
| `4454aa/Patrick-s-Parabox-Demake---JS-Port` | Browser HTML + Canvas + JavaScript port from a TIC-80/Lua demake; includes level parsing, recursive rendering, movement, undo, victory transition, and atlas texture rendering. | It confirms the minimum feature set required before a recursive puzzle feels coherent: parsing, recursive rendering, enter/exit, undo, and transitions. | It uses exported TIC-80 assets and a low-fidelity port structure, so it is not acceptable for this high-fidelity PixiJS renderer. |
| PuzzleScript archive/gists | Declarative object sprites, rule layers, animation frames, parent-level/player/crate symbols, and compact level notation. | Rule notation and tiny sprites are useful for edge-case reasoning and future level authoring vocabulary. | PuzzleScript is too constrained for camera, WebGL rendering, high-DPI visuals, and smooth recursive transitions. |

Useful:

- PuzzleScript versions demonstrate compact rule notation and level text ideas.
- Canvas/ESM demakes demonstrate browser feasibility and custom level import
  directions.
- TIC-80/JS ports show how small recursive previews can be represented with a
  sprite/atlas style.

Not acceptable as project direction:

- Single-file HTML.
- PuzzleScript as the engine.
- DOM or plain Canvas without a retained renderer layer.
- Low-fidelity tile sprites as the final target.
- Copying levels, art, or text.

## Failed Local Direction To Avoid

Old local history and visual audit identify these rejected patterns:

- React DOM cells.
- CSS game board.
- Letter labels such as `P`, `B`, or `IN`.
- Dashboard side rails that compete with the playfield.
- Card-based level selection as the primary experience.
- Debug panels with equal visual weight to gameplay.
- Tiny inner-world previews that read as decoration.
- Generic graph-paper app backgrounds.

These patterns must be treated as explicit regression risks.

## Acceptance Criteria For Visual Fidelity

Before implementation is considered visually credible:

- The first screen must read as a game scene, not an app dashboard.
- The playfield must be a PixiJS/WebGL canvas.
- Parent and child worlds must be visible in the same frame for recursive
  states.
- The player, normal box, recursive box, wall, and goal must be recognizable
  without text labels.
- Enter/exit transitions must visibly change scale.
- Screenshots must be captured from a browser and compared against this
  reference on desktop and mobile viewports.
- Canvas pixel checks must confirm the scene is nonblank and uses multiple
  authored palette colors.
- Visual QA should report dominant color families, dark/void coverage,
  saturation coverage, and nested-preview visibility for each captured local
  screenshot.

## Visual Regression Red Flags

Stop and redesign the visual layer if any of these appear in screenshots:

- The board reads as a spreadsheet, wireframe, dashboard widget, or form panel.
- Entities need letters or labels to be understood.
- Recursive boxes look like ordinary crates with a small icon.
- Inner worlds are decorative thumbnails rather than readable spaces.
- The camera hard-switches between worlds with no scale continuity.
- The first viewport shows more UI chrome than game scene.
- The palette collapses into one low-saturation blue/gray app theme.
- The scene could plausibly have been built with DOM cards and CSS borders.

## Non-Commercial Study Boundary

This is a technical recreation study. Do not ship Patrick's Parabox assets,
logos, level layouts, sound, copy, or trademarked presentation as an official
product. Recreate mechanics and visual principles with original code and
procedural assets.
