# Agent Log: frontend-engineer

Agent: frontend-engineer
Task clarity: clear
Capability fit: good
Questions needed: none
Assumptions: keep the plain TypeScript DOM stack unless the existing app becomes harder to maintain than replacing it.
Proceed decision: proceed

## Responsibility

Own UI shell, routes, board rendering, transitions, responsive layout, and visual smoke hooks.

## Decisions made

- Retire user-facing `IsoRenderer` path.
- Keep server and engine APIs as the source of truth for level/replay data.
- Add DOM landmarks/classes for `audit:ui`.
- Stage 2 removed the visible dev demo entry and runtime 3D catalog exposure.
- Stage 3 rebuilt the home screen as a command deck and added DOM-visible routes for chapter map, codex, records, and settings.
- Stage 3 replaced the old CSS surface with a new 2D sci-fi shell while keeping the existing `App` wiring stable.
- Stage 4 added a visible `time-shadow` board piece and preserved the existing board renderer for old levels.
- Stage 4 exposes `lastBlockedReason` through game wrappers for later HUD/feedback rendering.

## Files touched

- `src/web/ui.ts`
- `src/engine/levels.ts`
- `README.md`
- `claude.md`
- `package.json`
- `src/web/styles.css`
- `src/web/game.ts`
- `src/web/render.ts`
- Stage docs and `codex.md`

## Risks

- Current `src/web/ui.ts` is too large and mixes routing, input, rendering, modals, and camera behavior.
- Stage 3 has DOM verification but not full Playwright screenshots yet.
- The new settings and records overlays are product shells; they need deeper persistence/settings behavior in later stages.
- Blocked-reason data is not yet surfaced in HUD copy or animation.

## Review notes

- Split by screen/component enough to keep v7 maintainable.
- Stage 2 leaves old 2.5D code unused as history. Later stages should remove or archive it when the v7 shell replaces the legacy UI.
- Stage 3 verification passed: `typecheck`, `verify`, `smoke:api`, `smoke:ui`, `build`, and a temporary DOM audit for new home/navigation landmarks.
- Stage 4 verification passed after renderer support for the time-shadow piece.

## Next handoff

- Engine and level agents deliver v7 metadata and mechanism contracts; frontend wires richer state feedback and final `audit:ui` / `smoke:visual` hooks.
