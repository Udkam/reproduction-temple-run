# Driftbox v7 Loop Brief

RUN_ID: `v7-loop-20260623-195154-f683`

## Hard input facts

- Current v6 2.5D direction is rejected for product acceptance.
- 2.5D effect, rotate/top-down/highlight views, avatar UI, home page, level UI, page transition, and high-difficulty level design are all treated as failed.
- This run must rebuild Driftbox as a 2D sci-fi puzzle game, not patch the v6 2.5D path.
- Current 3D/2.5D chapters and public entry points must be retired from the final user-facing app.

## Target

Build a complete 70-level 2D sci-fi Sokoban-variant game with redesigned home, chapter map, game HUD, win flow, mechanism archive, challenge record, settings/help, chapter progress, visual system, character, engine mechanisms, level metadata, replay validation, audits, screenshots, docs, and push-per-stage workflow.

## Execution rules

- Follow the v7 plan strictly.
- Each stage must end with verification, QA notes, commit, and `git push origin main`.
- Failed stages must not be described as complete. If a checkpoint must be pushed while failing, use `v7-loop v7-loop-20260623-195154-f683: WIP failing <reason>`.
- Keep this run's durable records in this directory and maintain repo-local `codex.md`.
