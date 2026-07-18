# TIDE//RELAY Runner Rules

## Canonical coordinate model

- The course is an ordered list of orthogonal sections with deterministic IDs, start coordinates, heading, length, authored events, and a required left/right turn at every section end.
- Canonical progress is `(sectionIndex, sectionDistance)` plus total distance. Rendering derives world position and heading from the course; it does not write them back.
- Lanes are `-1`, `0`, and `1`. A lane command clamps the target to that set and presentation interpolates toward it.

## Commands

Public commands are `Start`, `StepLeft`, `StepRight`, `Jump`, `Slide`, `Pause`, `Resume`, `Restart`, and fixed `Tick`.

- In an active turn window, `StepLeft`/`StepRight` submit the matching turn and do not also change lane.
- Outside a turn window, they shift exactly one lane when possible.
- Jump is accepted only while grounded and not sliding.
- Slide is accepted while grounded or airborne; it sets the low collision posture for a fixed duration.
- Invalid or redundant commands leave canonical state unchanged.

## Motion

- Simulation advances at 60 ticks per second.
- Forward speed begins at 9 m/s and increases monotonically toward 19 m/s with distance.
- Jump uses deterministic vertical velocity and gravity; landing clamps height and velocity exactly to zero.
- Slide lasts 31 ticks. A second slide input does not extend it.
- Lane target changes are discrete; lane position approaches the target deterministically for collision checks.

## Pursuit pressure

- `chaseGap` is canonical meters between the courier and the black-tide pack. It begins at `4.5 m`, cannot exceed `8 m`, and capture occurs at or below `0.65 m`.
- Safe forward travel opens the gap gradually. This recovery is distance based and therefore independent of frame rate.
- A non-gap obstacle miss is a deterministic stumble: the event resolves once, applies a 45-tick recovery at 72% of the normal speed, closes the gap by 2.25 m immediately, then closes it by 0.34 m for every recovery meter travelled. The run continues while the gap remains above capture threshold.
- A shielded obstacle impact removes exactly one shield and emits `shield-broken`; it does not duplicate the collision event, but it applies the same 45-tick recovery and chase pressure as an unshielded stumble. A shield never absorbs a gap, wrong turn, or missed turn.
- Repeated stumbles, or one stumble while already sufficiently close, can cross the capture threshold and end the run through the pursuer.
- Reaching the capture threshold emits one deterministic `run-failed` event with `pursuer-caught` and ends the run.
- Rendering maps this value to pursuer position and scale but cannot write pressure back into the simulation.
- TR4 presentation treats `chaseGap` as latent pressure during ordinary running. The pursuer mesh is restricted to the opening and game-over beats; visibility never changes capture timing, collision, replay, score, or state hash.

## Turn rules

- Each section exposes a visible warning and an input window before its end.
- The required direction is authored by the deterministic generator.
- The first matching turn command inside the window queues the turn.
- The wrong direction immediately fails with `wrong-turn`.
- Crossing the section end without the matching queued turn fails with `missed-turn`.
- A successful turn advances exactly once to the next section, resets the queued turn, and emits one turn event.

## Course events

- `beam`: same-lane collision unless runner height is above the jump threshold.
- `ring`: same-lane collision unless slide posture is active.
- `column`: same-lane collision regardless of jump/slide; change lane.
- `gap`: collision across its length unless runner is airborne above the gap threshold.
- `shard`: collected once when lane and longitudinal windows overlap.
- `shield`: collected once and grants one collision absorption.

When a shield absorbs a non-gap hazard, the event is consumed, speed is reduced briefly, one shield-break event is emitted, chase pressure is applied, and the run continues unless the pursuer reaches the capture threshold. Without a shield, a beam/ring/column miss emits one `collision` and one typed `stumbled` event, applies the same recovery pressure, and continues unless capture occurs. A gap collision always ends immediately with `gap-fall`; wrong and missed turns also remain immediate failures. Collected/consumed/resolved event IDs remain canonical so replay and rendering cannot process them twice.

## Fair generation

- Generation is deterministic from the seed and stored RNG state.
- The opening section is an authored onboarding sequence: lane shift, jump, slide, then turn.
- Generated patterns have a pre-read zone, decision zone, action zone, and recovery zone.
- No pattern may block all three lanes at the same distance.
- A jump/slide hazard cannot overlap a required turn reaction window.
- Minimum spacing is derived from current speed and the slowest required action duration.
- The generator validates at least one legal response path before accepting a section.

## Scoring and difficulty

- Distance is measured in meters from canonical progress.
- Flow multiplier starts at 1 and increases every 250 m to a maximum of 5.
- Crossing each 250 m boundary emits exactly one `distance-milestone` event and stores the last emitted boundary in canonical state.
- Score is derived from distance, collected shards, and flow multiplier; it never depends on frame time.
- Speed and pattern density increase with distance but never shorten reaction time below the contract minimum.
- Best score and best distance are presentation persistence, not canonical simulation inputs.

## Pause and lifecycle

- Paused ticks cannot change any canonical field.
- Window blur or hidden document pauses only an active run and clears held/pointer input.
- Restart reconstructs the initial state from the same seed unless an explicit new seed is supplied.
- Destroy removes keyboard, pointer, visibility, resize, renderer-loop, and audio resources.

## Determinism

The same initial seed and command/tick sequence must produce byte-equivalent canonical state, course sections, consumed event IDs, score, and state hash. Renderer state, local storage, audio, and wall-clock timing are excluded.

## QA trace contract

- Milestone, close-chase, beam, ring, column, and gap evidence states start from `createInitialState(seed)` and are produced only by accepted public commands and fixed ticks.
- Every stored QA trace must replay to the same canonical state hash; direct mutation of distance, section progress, score, chase gap, resolved IDs, or body state is forbidden.
- A preview trace stops before its named unresolved hazard, so the renderer can prove the canonical kind and clipped bounds without changing gameplay truth.
