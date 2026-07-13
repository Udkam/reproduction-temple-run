import {
  createInitialState,
  dispatch,
  getCurrentSection,
  hashState,
  isTurnWindow,
  replay,
  type CourseEvent,
  type HazardKind,
  type Lane,
  type RunnerCommand,
  type RunnerEvent,
  type RunnerState,
} from "../core";

export const QA_SCENARIO_NAMES = [
  "ready",
  "running",
  "lane-mid",
  "jump-apex",
  "slide-mid",
  "turn-mid",
  "milestone",
  "chase-close",
  "collision",
  "beam-preview",
  "ring-preview",
  "column-preview",
  "gap-preview",
] as const;

export type QaScenarioName = (typeof QA_SCENARIO_NAMES)[number];

export interface QaScenario {
  readonly name: QaScenarioName;
  readonly previousState: RunnerState;
  readonly state: RunnerState;
  /** Events from the final accepted command, used by the renderer. */
  readonly events: readonly RunnerEvent[];
  /** Full public-command trace from createInitialState(seed). */
  readonly trace: readonly RunnerCommand[];
  /** hashState(state), independently reproducible from trace. */
  readonly replayHash: string;
}

interface HazardTarget {
  readonly sectionIndex: number;
  readonly event: CourseEvent & { readonly kind: HazardKind };
}

class TraceRunner {
  state: RunnerState;
  previousState: RunnerState;
  events: readonly RunnerEvent[] = [];
  readonly trace: RunnerCommand[] = [];

  constructor(seed: number) {
    this.state = createInitialState(seed);
    this.previousState = this.state;
  }

  command(command: RunnerCommand): void {
    const result = dispatch(this.state, command);
    if (!result.accepted) {
      throw new Error(`QA scenario command ${command.type} was rejected: ${result.rejection}`);
    }
    this.previousState = this.state;
    this.state = result.state;
    this.events = result.events;
    this.trace.push(command);
  }

  tick(): void {
    this.command({ type: "Tick" });
  }
}

function complete(name: QaScenarioName, runner: TraceRunner): QaScenario {
  const replayed = replay(runner.state.seed, runner.trace);
  const replayHash = hashState(runner.state);
  if (replayed.hash !== replayHash) {
    throw new Error(`${name} QA trace replay hash mismatch`);
  }
  return {
    name,
    previousState: runner.previousState,
    state: runner.state,
    events: runner.events,
    trace: runner.trace,
    replayHash,
  };
}

function start(seed: number): TraceRunner {
  const runner = new TraceRunner(seed);
  runner.command({ type: "Start" });
  return runner;
}

function isHazard(event: CourseEvent): event is CourseEvent & { readonly kind: HazardKind } {
  return event.kind === "beam" || event.kind === "ring" || event.kind === "column" || event.kind === "gap";
}

function unresolved(state: RunnerState, event: CourseEvent): boolean {
  return !state.resolvedEventIds.includes(event.id) && !state.consumedEventIds.includes(event.id);
}

function nextHazardGroup(state: RunnerState): readonly (CourseEvent & { readonly kind: HazardKind })[] {
  const section = getCurrentSection(state);
  const candidates = section.events
    .filter((event) => unresolved(state, event) && event.at >= state.sectionDistance)
    .filter(isHazard)
    .sort((left, right) => left.at - right.at || left.id.localeCompare(right.id, "en"));
  const first = candidates[0];
  return first ? candidates.filter((event) => Math.abs(event.at - first.at) < 0.001) : [];
}

function laneCommand(from: Lane, to: Lane): RunnerCommand | null {
  if (from === to) return null;
  return { type: to < from ? "StepLeft" : "StepRight" };
}

function safeLane(group: readonly (CourseEvent & { readonly kind: HazardKind })[]): Lane | null {
  if (group.some((event) => event.lane === "all")) return null;
  const blocked = new Set(group.map((event) => event.lane));
  return ([-1, 0, 1] as const).find((lane) => !blocked.has(lane)) ?? null;
}

function steerToward(runner: TraceRunner, desired: Lane): boolean {
  const { runner: body } = runner.state;
  if (body.laneTransition || body.targetLane === desired) return false;
  const command = laneCommand(body.targetLane, desired);
  if (!command) return false;
  runner.command(command);
  return true;
}

/**
 * Deterministic command-only autopilot used solely to create reproducible QA traces.
 * It reacts early enough for the authored minimum reaction distances and never edits
 * canonical fields directly.
 */
function pilot(runner: TraceRunner): void {
  const state = runner.state;
  if (state.status !== "running") return;
  const section = getCurrentSection(state);
  if (isTurnWindow(state) && state.queuedTurn === null) {
    runner.command({ type: section.requiredTurn === "left" ? "StepLeft" : "StepRight" });
    return;
  }

  const group = nextHazardGroup(state);
  if (group.length === 0) return;
  const at = group[0].at;
  const allLaneHazard = group.find((event) => event.lane === "all");
  if (!allLaneHazard) {
    const lane = safeLane(group);
    if (lane !== null && state.sectionDistance >= at - 8 && steerToward(runner, lane)) return;
  }

  if (!allLaneHazard || state.runner.grounded === false && allLaneHazard.kind !== "ring") return;
  if ((allLaneHazard.kind === "beam" || allLaneHazard.kind === "gap") && state.sectionDistance >= at - 0.95) {
    if (state.runner.grounded && state.runner.slideTicksRemaining === 0) runner.command({ type: "Jump" });
    return;
  }
  if (allLaneHazard.kind === "ring" && state.sectionDistance >= at - 0.35) {
    if (state.runner.slideTicksRemaining === 0) runner.command({ type: "Slide" });
  }
}

function advanceWithPilot(
  runner: TraceRunner,
  stop: (state: RunnerState) => boolean,
  limit = 12_000,
): void {
  for (let tick = 0; tick < limit; tick += 1) {
    if (stop(runner.state)) return;
    pilot(runner);
    runner.tick();
    if (runner.state.status !== "running") {
      throw new Error(`QA autopilot ended at ${runner.state.failureReason?.kind ?? runner.state.status}`);
    }
  }
  throw new Error("QA autopilot exceeded its deterministic tick budget");
}

function findHazard(state: RunnerState, kind: HazardKind): HazardTarget {
  for (const section of state.course.sections) {
    const event = section.events.find((candidate) => candidate.kind === kind);
    if (event && isHazard(event)) return { sectionIndex: section.index, event };
  }
  throw new Error(`Generated QA course contains no ${kind} event`);
}

function previewScenario(name: QaScenarioName, seed: number, kind: HazardKind): QaScenario {
  const runner = start(seed);
  const target = findHazard(runner.state, kind);
  advanceWithPilot(runner, (state) =>
    state.sectionIndex === target.sectionIndex && state.sectionDistance >= Math.max(0, target.event.at - 9),
  );
  if (!unresolved(runner.state, target.event)) {
    throw new Error(`${name} QA trace resolved its preview hazard`);
  }
  return complete(name, runner);
}

function turnScenario(seed: number): QaScenario {
  const runner = start(seed);
  advanceWithPilot(runner, (state) => state.sectionIndex === 1);
  if (!runner.events.some((event) => event.type === "turned")) {
    throw new Error("Turn QA trace did not finish through a public turn command");
  }
  return complete("turn-mid", runner);
}

function chaseCloseScenario(seed: number): QaScenario {
  const runner = start(seed);
  let stumbled = false;
  for (let tick = 0; tick < 500; tick += 1) {
    runner.tick();
    stumbled ||= runner.events.some((event) => event.type === "stumbled" && event.shielded === false);
    if (stumbled && runner.state.status === "running" && runner.state.chaseGap <= 1.2) {
      return complete("chase-close", runner);
    }
    if (runner.state.status !== "running") break;
  }
  throw new Error("Close-chase QA trace did not reach a visible recoverable threat state");
}

function captureScenario(seed: number): QaScenario {
  const runner = start(seed);
  for (let tick = 0; tick < 600; tick += 1) {
    runner.tick();
    if (runner.state.status === "game-over") {
      if (runner.state.failureReason?.kind !== "pursuer-caught") {
        throw new Error(`Collision QA trace ended with ${runner.state.failureReason?.kind}`);
      }
      return complete("collision", runner);
    }
  }
  throw new Error("Collision QA trace did not reach pursuer capture");
}

export function createQaScenario(name: QaScenarioName, seed: number): QaScenario {
  switch (name) {
    case "ready": {
      const runner = new TraceRunner(seed);
      return complete(name, runner);
    }
    case "running":
      return complete(name, start(seed));
    case "lane-mid": {
      const runner = start(seed);
      runner.command({ type: "StepRight" });
      for (let index = 0; index < 5; index += 1) runner.tick();
      return complete(name, runner);
    }
    case "jump-apex": {
      const runner = start(seed);
      runner.command({ type: "Jump" });
      while (runner.state.runner.verticalVelocity > 0) runner.tick();
      if (runner.state.runner.height <= 0 || runner.state.runner.grounded) {
        throw new Error("Jump QA trace did not reach an airborne apex");
      }
      return complete(name, runner);
    }
    case "slide-mid": {
      const runner = start(seed);
      runner.command({ type: "Slide" });
      for (let index = 0; index < 15; index += 1) runner.tick();
      return complete(name, runner);
    }
    case "turn-mid":
      return turnScenario(seed);
    case "milestone": {
      const runner = start(seed);
      advanceWithPilot(runner, (state) => state.lastDistanceMilestone === 250 && state.distance < 252);
      if (!runner.events.some((event) => event.type === "distance-milestone" && event.meters === 250)) {
        throw new Error("Milestone QA trace did not finish on the 250 m event");
      }
      return complete(name, runner);
    }
    case "chase-close":
      return chaseCloseScenario(seed);
    case "collision":
      return captureScenario(seed);
    case "beam-preview":
      return previewScenario(name, seed, "beam");
    case "ring-preview":
      return previewScenario(name, seed, "ring");
    case "column-preview":
      return previewScenario(name, seed, "column");
    case "gap-preview":
      return previewScenario(name, seed, "gap");
  }
}

export function replayQaScenario(scenario: QaScenario): string {
  return replay(scenario.state.seed, scenario.trace).hash;
}
