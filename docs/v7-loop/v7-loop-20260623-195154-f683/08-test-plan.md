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

Checks exact count 70, chapter counts, metadata, core ideas, solver status, replay validity, duplicate maps, canonical mirror/rotation duplicates, water levels, unreachable cells, and declared intentional variants.

### audit:ui

Checks home, chapter star map, HUD, next button, mechanism archive, settings, transitions, mobile overflow, and absence of visible v6 3D entry points.

### audit:content

Checks README, claude.md, v7 docs, current level count, v6 failure archival language, no current 3D-complete promotion, and license records.

### smoke:visual

Playwright screenshots must cover home, chapter map, archive, representative chapter levels, chain UI, boss level, win overlay, mobile home, and mobile game screen. Screenshots are saved under `screenshots/`.

## Acceptance rule

Passing typecheck/build alone is never enough. Visual QA and level quality audits are hard gates.
