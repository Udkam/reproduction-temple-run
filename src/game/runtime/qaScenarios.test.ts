import { describe, expect, it } from "vitest";
import { hashState } from "../core";
import {
  QA_SCENARIO_NAMES,
  createQaScenario,
  replayQaScenario,
} from "./qaScenarios";

describe("command-derived QA scenarios", () => {
  it("replays every stored scenario trace from createInitialState to its recorded hash", () => {
    for (const name of QA_SCENARIO_NAMES) {
      const scenario = createQaScenario(name, 0x54494445);
      expect(scenario.trace.length).toBeGreaterThanOrEqual(name === "ready" ? 0 : 1);
      expect(replayQaScenario(scenario)).toBe(scenario.replayHash);
      expect(hashState(scenario.state)).toBe(scenario.replayHash);
    }
  });

  it("keeps previews unresolved and reaches pursuer capture through ticks", () => {
    for (const name of ["beam-preview", "ring-preview", "column-preview", "gap-preview"] as const) {
      const scenario = createQaScenario(name, 0x54494445);
      const hazardId = scenario.state.course.sections
        .flatMap((section) => section.events)
        .find((event) => event.kind === name.replace("-preview", ""))?.id;
      expect(hazardId).toBeDefined();
      expect(scenario.state.resolvedEventIds).not.toContain(hazardId);
    }
    expect(createQaScenario("collision", 0x54494445).state.failureReason?.kind).toBe("pursuer-caught");
  });
});
