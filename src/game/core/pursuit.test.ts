import { describe, expect, it } from "vitest";
import {
  CHASE_CAPTURE_GAP,
  CHASE_STUMBLE_LOSS,
  DISTANCE_MILESTONE_METERS,
  INITIAL_CHASE_GAP,
  MAX_CHASE_GAP,
  MAX_SPEED,
  advanceOneTick,
  createInitialState,
  dispatch,
  replay,
  speedForDistance,
} from "./index";
import type { CourseEvent, RunnerCommand, RunnerState } from "./types";

function started(seed = 0x715e): RunnerState {
  return dispatch(createInitialState(seed), { type: "Start" }).state;
}

function withCurrentEvents(
  state: RunnerState,
  events: readonly CourseEvent[],
): RunnerState {
  return {
    ...state,
    course: {
      ...state.course,
      sections: state.course.sections.map((section) =>
        section.index === state.sectionIndex ? { ...section, events } : section,
      ),
    },
    resolvedEventIds: [],
    consumedEventIds: [],
  };
}

describe("deterministic pursuit pressure and distance progression", () => {
  it("starts the pursuer close, then opens a bounded gap during safe running", () => {
    let state = started();
    expect(state.chaseGap).toBe(INITIAL_CHASE_GAP);

    for (let tick = 0; tick < 120; tick += 1) {
      state = advanceOneTick(state).state;
    }

    expect(state.status).toBe("running");
    expect(state.chaseGap).toBeGreaterThan(INITIAL_CHASE_GAP);
    expect(state.chaseGap).toBeLessThanOrEqual(MAX_CHASE_GAP);

    const capped = advanceOneTick({ ...state, chaseGap: MAX_CHASE_GAP }).state;
    expect(capped.chaseGap).toBe(MAX_CHASE_GAP);
  });

  it("turns a shielded stumble into chase pressure and catches at the threshold", () => {
    const events: readonly CourseEvent[] = [
      { id: "shield", kind: "shield", lane: 0, at: 0.05, length: 1 },
      { id: "column", kind: "column", lane: 0, at: 0.1, length: 1 },
    ];
    const ordinary = advanceOneTick(withCurrentEvents(started(), events));
    expect(ordinary.state.status).toBe("running");
    expect(ordinary.state.chaseGap).toBeLessThan(
      INITIAL_CHASE_GAP - CHASE_STUMBLE_LOSS + 0.01,
    );
    expect(ordinary.events.filter((event) => event.type === "shield-broken")).toHaveLength(1);
    expect(ordinary.events).toContainEqual(
      expect.objectContaining({ type: "stumbled", hazard: "column", shielded: true }),
    );

    const threatened = withCurrentEvents(
      { ...started(), chaseGap: CHASE_CAPTURE_GAP + CHASE_STUMBLE_LOSS / 2 },
      events,
    );
    const caught = advanceOneTick(threatened);
    expect(caught.state.status).toBe("game-over");
    expect(caught.state.failureReason).toEqual({
      kind: "pursuer-caught",
      hazard: "black-tide",
    });
    expect(caught.events.at(-1)).toEqual({
      type: "run-failed",
      tick: caught.state.tick,
      reason: caught.state.failureReason,
    });
  });

  it("keeps an unshielded obstacle miss recoverable until chase pressure reaches capture", () => {
    const column: CourseEvent = {
      id: "column",
      kind: "column",
      lane: 0,
      at: 0.1,
      length: 1,
    };
    const first = advanceOneTick(withCurrentEvents(started(), [column]));
    expect(first.state.status).toBe("running");
    expect(first.state.failureReason).toBeNull();
    expect(first.events).toContainEqual(
      expect.objectContaining({ type: "stumbled", shielded: false }),
    );

    const caught = advanceOneTick(
      withCurrentEvents({ ...started(), chaseGap: CHASE_CAPTURE_GAP + 0.2 }, [column]),
    );
    expect(caught.state.status).toBe("game-over");
    expect(caught.state.failureReason?.kind).toBe("pursuer-caught");
  });

  it("emits each 250 m milestone once and never repeats it on later ticks", () => {
    let state: RunnerState = {
      ...started(),
      distance: DISTANCE_MILESTONE_METERS - 0.05,
      lastDistanceMilestone: 0,
    };
    const crossing = advanceOneTick(state);
    state = crossing.state;

    expect(crossing.events.filter((event) => event.type === "distance-milestone")).toEqual([
      {
        type: "distance-milestone",
        tick: state.tick,
        meters: DISTANCE_MILESTONE_METERS,
      },
    ]);
    expect(state.lastDistanceMilestone).toBe(DISTANCE_MILESTONE_METERS);

    const after = advanceOneTick(state);
    expect(after.events.some((event) => event.type === "distance-milestone")).toBe(false);
    expect(after.state.lastDistanceMilestone).toBe(DISTANCE_MILESTONE_METERS);
  });

  it("uses one continuous capped speed curve for play and conservative course authoring", () => {
    let previous = speedForDistance(0);
    for (let distance = 0.25; distance <= 5_000; distance += 0.25) {
      const current = speedForDistance(distance);
      expect(current).toBeGreaterThanOrEqual(previous);
      expect(current - previous).toBeLessThanOrEqual(0.001000000001);
      expect(current).toBeLessThanOrEqual(MAX_SPEED);
      previous = current;
    }
    expect(previous).toBe(MAX_SPEED);

    const sections = createInitialState(81).course.sections;
    let cumulativeStart = 0;
    for (const section of sections) {
      expect(section.authoredSpeed).toBeGreaterThanOrEqual(speedForDistance(cumulativeStart));
      cumulativeStart += section.length;
    }
  });

  it("includes deterministic onboarding pursuit pressure in replay hashes", () => {
    const commands: RunnerCommand[] = [
      { type: "Start" },
      ...Array.from({ length: 180 }, () => ({ type: "Tick" }) as const),
    ];
    const first = replay(0x8badf00d, commands);
    const second = replay(0x8badf00d, commands);

    expect(second.hash).toBe(first.hash);
    expect(second.state.chaseGap).toBe(first.state.chaseGap);
    // This command trace intentionally stays in the opening lane and therefore
    // misses the authored center column; the reduced gap proves pressure is hashed.
    expect(first.state.chaseGap).toBeLessThan(INITIAL_CHASE_GAP);
  });
});
