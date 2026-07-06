# Architecture

Status: approved implementation contract. Do not implement gameplay code beyond
the currently approved stage.

## Objective

Build a high-fidelity browser study of Patrick's Parabox using React,
TypeScript, Vite, and PixiJS/WebGL. The result must not be a simple Sokoban
clone or a React DOM grid. React owns the host shell; PixiJS owns the game
canvas, world rendering, animation, camera, input focus, and frame loop.

Priority order:

1. Visual fidelity.
2. Recursive world architecture.
3. Smooth game feel.
4. Extensible level system.
5. Content amount.

## Current Baseline

The current worktree is records-only after a failed implementation reset. The
old `feature/recursive-box-lab` history is useful as evidence but not as a
continuation base. Its core mistake was treating the project as a lightweight
React/CSS puzzle UI instead of a canvas-first recursive game.

Carry forward these lessons only:

- A world/entity separation is necessary.
- Undo must be part of the deterministic core.
- Level metadata and scripted solution validation are useful.
- Dashboard chrome, lettered entities, DOM cells, and card-style level lists
  must not return.

## Runtime Layers

The app should be built as five explicit layers.

| Layer | Responsibility | Technology |
| --- | --- | --- |
| Host shell | Mount/unmount canvas, route menus, expose settings, keep React state minimal | React |
| Game runtime | Own lifecycle, dependency wiring, fixed command pipeline, ticker | TypeScript |
| Simulation core | Deterministic recursive puzzle state, commands, history, validation | TypeScript |
| Renderer | Project world graph into bounded visual frames and draw them | PixiJS |
| QA tooling | Screenshot comparison, canvas pixel checks, replay validation | Playwright/browser tools |

React components must not represent cells, entities, worlds, or animations.
The primary game surface is one PixiJS canvas.

## Module Dependency Contract

Future code should keep dependencies flowing in one direction. Lower layers must
not import higher layers.

| Module area | May import | Must not import |
| --- | --- | --- |
| `src/core/*` | pure TypeScript helpers, schema types | React, PixiJS, browser globals, CSS, renderer, runtime |
| `src/projection/*` | `src/core/*`, pure math helpers | React, DOM, PixiJS display objects, input handlers |
| `src/render/*` | PixiJS, `src/projection/*`, readonly core snapshots, render assets | React components, mutable core reducers, level loaders with side effects |
| `src/input/*` | command types, runtime command queue | renderer internals, direct entity mutation, React state |
| `src/animation/*` | transition events, easing/math helpers | canonical state mutation, React state |
| `src/runtime/*` | core, projection, render, input, animation, asset loading | React component trees beyond host lifecycle callbacks |
| `src/app/*` | React, runtime public API, shell CSS | core reducers, Pixi display tree internals, gameplay cell/entity rendering |
| `src/levels/*` | schema, validators, static JSON data | renderer objects, React components, animation state |

Public handoff types should be narrow:

- Core emits command results and transition events.
- Projection emits renderable view models.
- Renderer consumes projection view models and animation timelines.
- Runtime coordinates lifecycle and command flow.
- React starts/stops runtime and displays non-game shell state.

## Architecture Invariants

These invariants are non-negotiable. A future implementation that violates one
of them should be treated as a wrong direction even if it appears playable.

- Gameplay cells, entities, worlds, recursive previews, camera transforms, and
  movement animations are never modeled as React DOM nodes.
- React owns only app shell concerns: mounting, cleanup, menus, settings,
  non-game dialogs, and optional accessibility mirrors.
- The simulation core never imports React, PixiJS, browser APIs, or CSS.
- The renderer never mutates canonical simulation state.
- The camera owns every world-to-screen transform; core state never stores
  pixels, viewport sizes, CSS units, or render-layer coordinates.
- Recursive rendering is projection-based. Tiny nested worlds are views of
  canonical state, not cloned game-state subtrees.
- All state-changing player actions enter through command objects so keyboard,
  pointer, replay, tests, and future accessibility controls share one path.
- Undo/redo records deterministic core state or reversible patches, never
  renderer objects or animation timers.
- Level data is serializable JSON-compatible data; no level may require custom
  TypeScript logic to load.
- Visual reference comparison is a required gate before calling any playable
  slice acceptable.

## Rejected Approaches

The following approaches are explicitly rejected for this project:

- React component grids for the board.
- CSS-only entities or recursive box previews.
- Plain HTML Canvas without a retained renderer layer and camera abstraction.
- PuzzleScript or TIC-80 style engines as the primary runtime.
- Copying official Patrick's Parabox levels, art, sound, UI copy, or branding.
- Importing official-format levels as a substitute for an original extensible
  level system.
- A flat single-world Sokoban engine with recursion simulated by UI tricks.
- A dashboard, card grid, or form-panel presentation around a small puzzle.
- A large content pack before visual fidelity, recursion, and game feel are
  proven.

## PixiJS Runtime

Use PixiJS v8 conventions:

- Create `new Application()` and call async `app.init(...)`.
- Prefer `preference: ["webgpu", "webgl"]` with WebGL-compatible fallback.
- Use `resizeTo` or explicit resize handling for the canvas host.
- Use `Assets` for managed asset loading and future texture atlases.
- Use `app.ticker` as the visual frame loop, not React renders.
- Destroy the application and remove listeners on React unmount.

React integration is an imperative external-system boundary: a `GameCanvasHost`
component owns a DOM ref, creates the runtime in an effect, and cleans it up.
React may display surrounding menus, but not the game board itself.

## Core World Model

The simulation state is graph-based, not screen-based.

```ts
type WorldId = string;
type EntityId = string;

type Direction = "up" | "down" | "left" | "right";

interface WorldNode {
  id: WorldId;
  size: { width: number; height: number };
  paletteId: string;
  boundary: BoundarySpec;
  cells: CellSpec[];
}

interface ContainerComponent {
  innerWorldId: WorldId;
  entrances: Partial<Record<Direction, EntranceSpec>>;
  allowsRecursiveCycle: boolean;
}

interface PositionComponent {
  worldId: WorldId;
  x: number;
  y: number;
}
```

`WorldNode` is a logical space. `ContainerComponent` connects an entity to the
world it contains. These edges form a directed world graph and may eventually
be cyclic. Cyclic containment must be represented as graph references, not by
materializing infinite copies.

## Recursive Addressing

Rendering and movement need a bounded view of a potentially cyclic graph.
Introduce explicit view addresses:

```ts
interface WorldAddress {
  rootWorldId: WorldId;
  path: EntityId[];
}

interface WorldProjection {
  address: WorldAddress;
  worldId: WorldId;
  depth: number;
  transform: ProjectionTransform;
  clip: ClipSpec;
}
```

The simulation stores canonical entities and graph edges. The renderer builds a
finite projection tree from the active focus, repeating canonical worlds when a
cycle is visible and stopping at a configured depth. A rendered tiny copy is a
projection of canonical state, not a duplicate entity.

This keeps the architecture ready for:

- Box contains world.
- Box enters another box.
- Box exits its parent world.
- World-bearing box moves and changes graph parent.
- Recursive/cyclic containment with bounded visual expansion.
- Future infinity-style mechanics without unserializable state.

## Entity Component Separation

Entities are records with independent components. Avoid inheritance-heavy game
objects.

Core components:

- `PositionComponent`: canonical world/cell location.
- `SolidComponent`: blocks movement.
- `PushableComponent`: can be pushed and may define mass/friction later.
- `PlayerComponent`: command-controlled actor.
- `ContainerComponent`: links an entity to an inner world.
- `GoalComponent`: win target matcher.
- `VisualComponent`: palette key, sprite archetype, scale hints.
- `MotionComponent`: transient interpolation and impact state.

Systems:

- `MovementResolver`: computes one command against canonical graph state.
- `RecursiveTransitionSystem`: enter, exit, push-in, push-out, parent updates.
- `CycleGuard`: validates or rejects unsupported containment cycles.
- `WinSystem`: checks goals across all logical worlds.
- `HistorySystem`: records deterministic snapshots or reversible patches.
- `ProjectionSystem`: builds renderable world projections.
- `AnimationSystem`: converts command results into visual timelines.

## Movement Pipeline

One player action should pass through this pipeline:

1. Input manager emits a command: `Move(Direction)`, `Undo`, `Redo`, `Reset`.
2. Runtime queues the command; simulation consumes commands one at a time.
3. Movement resolver checks the actor, target cell, blockers, and graph edge.
4. Recursive transition system resolves enter, exit, push-in, or push-out.
5. Core state changes atomically or not at all.
6. History records the successful command.
7. Animation system receives a structured transition event.
8. Renderer animates toward the new projection state.
9. Input unlocks when the animation reaches a commit-safe point.

Failed moves should still produce small feedback, but they must not alter
history.

## Camera System

The camera is part of game feel, not a CSS layout detail.

Required camera behaviors:

- Fit the active projection to the canvas with stable margins.
- Smoothly zoom when entering or exiting a box.
- Keep parent context visible during transitions when possible.
- Support both reference composition modes: isolated world in black void and
  cropped parent world filling the screen edges.
- Support screen shake or compression only for impact feedback, not decoration.
- Provide deterministic camera states for screenshot comparison.
- Respect reduced motion by snapping or shortening transitions.

The camera owns world-to-screen transforms. Simulation never stores pixels.

## Renderer Architecture

PixiJS display tree:

```text
stage
  backgroundLayer
  cameraRoot
    recursiveWorldLayer
      worldFrameContainer*
        floorLayer
        wallLayer
        goalLayer
        entityLayer
        innerPreviewLayer
        maskLayer
    effectLayer
  overlayLayer
```

Render rules:

- Draw worlds as thick beveled slabs with clipped interiors.
- Draw open boxes as windowed containers showing bounded inner projections.
- Use masks for world interiors and nested previews.
- Prefer procedural `Graphics` first; introduce texture atlases only when they
  improve fidelity or performance.
- Cache static world geometry into render textures where beneficial.
- Keep UI labels outside the game canvas or as minimal Pixi overlay text.

## Input Manager

Input is command-based and independent of React.

- Keyboard: arrow keys and WASD for movement; Z/Backspace undo; Y/Shift+Z redo;
  R reset.
- Pointer/touch: directional controls or swipe layer can be added later, but
  must emit the same commands.
- Input lock: commands are queued or rejected while critical animations play.
- Replay: tests and QA use the same command API as the player.

## History And Determinism

Undo/redo must be reliable because the puzzle rules are experimental.

History options:

- Early stage: immutable full core snapshots for clarity.
- Later stage: reversible patches with structural sharing if memory requires.

Every history entry stores:

- command
- pre-state hash
- post-state hash
- transition event list
- move counter

No renderer, React state, or transient animation state belongs in core history.

## Level Serialization

Levels should be data, not TypeScript code.

Initial schema:

```json
{
  "schemaVersion": 1,
  "id": "study-001",
  "title": "First Fold",
  "worlds": [],
  "entities": [],
  "rootWorldId": "root",
  "playerId": "player",
  "goals": [],
  "palette": "blue-lab",
  "scriptedSolution": ["right", "down"]
}
```

Validation requirements:

- Unique IDs.
- Every entity position references an existing world and valid cell.
- Every container references an existing inner world.
- No unsupported graph cycle unless explicitly marked.
- At least one required goal.
- Scripted solution, if present, must solve the level.

Keep the schema compatible with future imported level packs, but do not block
the first architecture-approved implementation on full editor support.

## Testing And Verification

Required gates after implementation begins:

- Unit tests for movement, push chains, enter/exit, push-in/push-out, win
  checks, undo/redo, and serialization validation.
- Graph invariant tests for parent updates and cycle handling.
- Replay tests for all included levels.
- Browser smoke test that mounts PixiJS and verifies nonblank canvas pixels.
- Screenshot comparison against the design reference at desktop and mobile
  viewports.
- No DOM cell/entity rendering in `src`.

## Approval Gate

Implementation may start only after approval of:

- This architecture.
- `DESIGN_REFERENCE.md`.
- `IMPLEMENTATION_PLAN.md`.

Until then, allowed work is limited to documentation, evidence gathering, and
architecture review.
