# Temple project archive state

Updated: 2026-08-13 Asia/Shanghai

Project root: `E:\Proj\reproduction-temple-run`

Branch: `main`

Status: **ARCHIVE_IN_PROGRESS — preservation and remote synchronization only.** This is not a product-completion claim.

## Boundary

- User direction closes development and requires every existing file and historical artifact to be preserved.
- No file may be deleted, reverted, cleaned, overwritten, or silently omitted.
- No modeling, rendering, browser capture, Blender/process execution, product edit, retry, test, or build is part of archive closeout.
- Historical contracts below this checkpoint remain evidence, not active authority. Reopening requires a new explicit user instruction and a fresh resource/state preflight.

## Verified completion point

- TR2 remains the accepted deterministic simulation/runtime baseline: candidate `c5b3db041175c19c71bd0086baf1e034fc97caf0`, independent QA log commit `b974810fc4b0ba93fb5ed7d6012e22c67b0606a5`.
- R1E-V7 `2fb2d91acbbd17dc21a9655839584e9ffd4fdf95` is accepted only for bounded canyon readability.
- R1F `6680489cf2e3ec035da44fc1dde9aa7606bdd9c7` is accepted only for bounded causeway presentation.
- R1G/R1G-E1 `8de73c169d03ce32e15bce2145d64afff8973330` is the last accepted visual checkpoint, only for bounded courier geometry and hidden-pursuer snapshot conformance. Its 14-frame manifest SHA-256 is `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`.
- None of these accepts the full high-fidelity game.

## R1H disposition at closeout

- Geometry candidate `de636bc0d036f6d8916d5a19517387987bd40bc5` is independently source-`READY`; its final source gates were targeted `8/8`, complete `17 files / 75 tests`, and a successful no-delete production build.
- C1 evidence is `BLOCKED` at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c1-candidate-de636bc-20260809T232247032\`: one immutable PNG, no manifest, screenshot-time camera drift.
- C2 evidence is `BLOCKED` at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c2-candidate-de636bc-20260809T235226399\`: zero PNG, no manifest, presentation-clock lattice missed the camera window.
- C3 evidence is `BLOCKED` at `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c3-candidate-de636bc-20260810T002256684\`: zero PNG, no manifest, native RAF wrapper never reached the transient camera window.
- R1H-C4 candidate `b64f09e4fd6ca687a40655cd4e5662a807139d5b` adds the DEV-only presentation hold and is independently source-`READY`. Its final gates passed: typecheck, `17 files / 77 tests`, and a no-delete build of 31 files / 1,696,155 bytes. The capture harness passed static QA with SHA-256 `7C5C7742110A3BC7CFD6DF071D7C55FF151AB6FF9CF03BE198F59B2B852A2FCB`.
- The C4 browser pass never started because the recorded preflight reached CPU `98.4%`. `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1h-c4-candidate-b64f09e-20260810T010941303\` contains only the capture script: zero PNG, zero manifest, and no visual QA.
- Therefore R1H and the complete high-fidelity presentation remain `MANUAL_BLOCKED / NOT_ACCEPTED`.

## Preservation-only local inventory

The pre-archive worktree contained five real tracked path migrations (six additions and six deletions total) and two untracked material-socket probe scripts. Twenty-seven other tracked `M` reports were proven hash-identical to the index and cleared by index refresh without changing file bytes.

Authorized preservation checkpoint A contains only the five Blender executable path migrations listed in `docs/CURRENT_TASK.md`. Authorized checkpoint B contains only the two probe scripts with the hashes recorded there. Checkpoint B is explicitly `WIP_UNEXECUTED / NOT_ACCEPTED`; it is stored so local work is not lost, not because it passed any gate.

## Synchronization baseline and target

- Fetched remote baseline before archive: `origin/main` at `056b68701d71bb2c618e131d24039f53d646caff`.
- Pre-archive local source head: `b64f09e4fd6ca687a40655cd4e5662a807139d5b`, seven commits ahead and zero behind after fetch.
- The final archive record must append the preservation and coordinator commit SHAs, require clean index/worktree, push `main`, create and push annotated tag `archive-temple-incomplete-20260813`, and verify remote branch/tag identity.

## Sole next action

Complete only the two exact preservation commits, seal this state and the coordinator status documents, obtain read-only archive QA, push and verify. Then archive the Codex task. Do not resume product development.
