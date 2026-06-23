# Test Plan

## Required commands

- `npm run typecheck`
- `npm run verify`
- `npm run smoke:api`
- `npm run smoke:ui`
- `npm run smoke:visual`
- `npm run audit:levels`
- `npm run audit:ui`
- `npm run audit:content`
- `npm run build`

## New audits

### audit:levels

Stage 10 slice mode checks exact count 20, 4/3/3/3/3/2/2 chapter counts, metadata, core ideas, solver status, replay validity, duplicate maps, required redesign mechanics, active spatial swap, recursive entry cores, worldline twin state, and water-level placeholders.

Future 70-level expansion must update this gate back to the requested 70-level structure only after the redesign slice passes visual/product/puzzle QA.

### audit:ui

Checks home, chapter star map, HUD, next button, mechanism archive, settings, transitions, mobile overflow, and absence of visible v6 3D entry points.

### audit:content

Checks README, claude.md, v7 docs, current level count, v6 failure archival language, no current 3D-complete promotion, and license records.

### smoke:visual

Playwright screenshots must cover home console, worldline star graph, representative slice levels, character state sheet, victory collapse, mobile home, and mobile chamber. Screenshots are saved under `screenshots/`.

## Acceptance rule

Passing typecheck/build alone is never enough. Visual QA and level quality audits are hard gates.
