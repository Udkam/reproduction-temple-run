# Implementation Plan

## Stage sequence

1. Project reset and route cleanup.
2. New sci-fi art system.
3. New home, navigation, transitions, and screen shell.
4. Engine mechanism layer and versioned replay.
5. Level data format upgrade.
6. First 15-level vertical slice.
7. Full 70-level buildout.
8. Solver, replay, and validation adaptation.
9. Visual QA and polish.
10. Final docs, reports, commits, and push.

## Commit and push rule

After each stage:

1. Run that stage's verification.
2. Update `09-iteration-log.md`, relevant agent logs, and `codex.md`.
3. Commit with `v7-loop v7-loop-20260623-195154-f683: <stage> - <summary>`.
4. Push to `origin main`.

If failed but checkpointed, use `v7-loop v7-loop-20260623-195154-f683: WIP failing <reason>` and push.

## Implementation notes

- Keep server replay authoritative.
- Use `driftbox.progress.v7` rather than mutating old progress shape in place.
- Build v7 replay as versioned data while retaining legacy validation during transition.
- Implement complex levels as replay-verified first where full solver support would be risky.
