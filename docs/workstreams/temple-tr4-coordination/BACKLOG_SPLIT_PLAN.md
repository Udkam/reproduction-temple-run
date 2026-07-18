# Temple inherited-backlog checkpoint plan

Status: **COMPLETE — RECOVERY RANGE FROZEN.** This plan is the path inventory required by
`docs/COMMIT_POLICY.md` before any new Temple product or visual expansion. It records
the frozen working tree observed on 2026-07-18 and does not accept any historical proof.

## Git boundary and inventory closure

- branch: `codex/temple-run`;
- policy checkpoint: `4353205e90559e782ae959e2449d42e8234c3670`;
- completed recovery `HEAD`: `ecd5de640362a6e30c5d0157ecd1590be7673318`;
- recovery range after the policy checkpoint: `3446996b9c597fe4401691a618ae46758b0e6bc1..ecd5de640362a6e30c5d0157ecd1590be7673318` (`31` commits);
- frozen backlog anchor: `52ae9ae631fa3761f8f8737978af1840ba2df8a4`;
- remote: `https://github.com/Udkam/Game-1.git`;
- Git dir and common dir: repository-local `.git`;
- staged paths at inventory time: zero;
- `git status --short -uall`: exactly 219 paths;
- ignored but evidence-bearing `*.log` adjuncts: exactly nine paths listed below.
- post-inventory C6 visual-review adjuncts: exactly two paths in checkpoint C04V.
- current porcelain after recovery: exactly the five never-stage paths in this file; staged paths zero.
- C29's five referenced local screenshots exist and match the hashes recorded by its two JSON files, but remain repository-excluded temporary evidence and were not committed.

The match rules in the table are disjoint. Exact-file rows take precedence over prefix
rows. Counts refer to the 219 porcelain paths; ignored evidence logs are additional and
must be force-staged only by exact path in their named evidence checkpoint.

## Ordered checkpoint inventory

| ID | Reviewable claim and exact assignment | Porcelain paths | Verification before commit |
| --- | --- | ---: | --- |
| C01 | `docs(tr4): freeze the C6 terminal contract and backlog split`: `docs/CURRENT_TASK.md`, `docs/DESIGN.md`, `docs/rules/RUNNER_RULES.md`, `docs/qa/TEMPLE_ACCEPTANCE.md`, and every file directly under `docs/workstreams/temple-tr4-coordination/`, including this plan | 17 after this plan is added | UTF-8/LF audit, `git diff --check`, closed C1-C6 status consistency |
| C02 | `tool(tr4): preserve the fail-closed C1-C6 diagnostic pipeline`: exact three files `tools/temple-asset-pipeline/generate_tide_scar_tr4_pack.py`, `evaluate_tide_scar_tr4_pack.py`, and `run_tide_scar_tr4_pack.py` | 3 | AST parse, exact launch hashes, C6 status/hash cross-check; no rerun |
| C03 | `evidence(tr4): preserve C1-C5 and probe failures`: every porcelain path under `docs/workstreams/temple-tr4-asset/` except `THREAD_LOG.md` and `diagnostic-006/**` | 44 | exact-set/hash audit, PNG headers, terminal verdicts; force-stage the seven exact logs below |
| C04 | `evidence(tr4): preserve the blocked C6 render set`: every porcelain path under `docs/workstreams/temple-tr4-asset/diagnostic-006/` | 26 | exact 27-file set including the ignored log, hashes, 20 PNG headers, `DIAGNOSTIC_BLOCKED`, Blender `0`, evaluator null |
| C04V | `qa(tr4): record the independent C6 visual block`: exact `docs/workstreams/temple-tr4-visual-review/TR4_DIAGNOSTIC_REVIEW.md` and `THREAD_LOG.md` | 2 post-inventory adjuncts | UTF-8/LF audit, all 20 filenames present, `MANUAL_BLOCKED`, no production repair |
| C05 | `docs(tr4): record asset-workstream provenance`: exact `docs/workstreams/temple-tr4-asset/THREAD_LOG.md` | 1 | UTF-8/LF audit and consistency with C1-C6 terminal evidence |
| C06 | `docs(tr3): preserve historical asset-pipeline contracts`: exact `docs/workstreams/temple-tr3/ASSET_PIPELINE.md` and `docs/workstreams/temple-tr3/THREAD_LOG.md` | 2 | UTF-8/LF audit and historical-only status |
| C07 | `tool(tr3): preserve A0 asset proof pipeline`: exact `generate_tide_scar_hero.py`, `evaluate_asset_proof.py`, and `run_asset_proof.py` under `tools/temple-asset-pipeline/` | 3 | AST parse and recorded-manifest provenance |
| C08 | `tool(tr3): preserve A2 asset proof pipeline`: exact `generate_tide_scar_hero_a2.py`, `evaluate_asset_proof_a2.py`, and `run_asset_proof_a2.py` | 3 | AST parse and A2 metadata/provenance |
| C09 | `evidence(tr3): preserve A0-A2 asset proof`: every path directly under `docs/workstreams/temple-tr3/asset-proof/` plus `textures/**` and `a2/**`, excluding `a3/**`, `a4/**`, `a5/**`, and `tide-scar-hero.blend1` | 46 | manifest/SHA256SUMS, GLB/KTX validation records, image headers; force-stage `blender-final.log` |
| C10 | `tool(tr3): preserve A3 pipeline`: exact `generate_tide_scar_hero_a3.py` and `evaluate_asset_proof_a3.py` | 2 | AST parse and A3 metadata schema |
| C11 | `evidence(tr3): preserve blocked A3 proof`: every path under `docs/workstreams/temple-tr3/asset-proof/a3/` | 5 | exact-set/hash/image-header audit and blocked status |
| C12 | `tool(tr3): preserve A4 pipeline`: exact `generate_tide_scar_hero_a4.py` and `evaluate_asset_proof_a4.py` | 2 | AST parse and A4 metadata schema |
| C13 | `evidence(tr3): preserve blocked A4 proof`: every path under `docs/workstreams/temple-tr3/asset-proof/a4/` | 6 | exact-set/hash/image-header audit and blocked status |
| C14 | `tool(tr3): preserve A5 pipeline`: exact `generate_tide_scar_hero_a5.py` and `evaluate_asset_proof_a5.py` | 2 | AST parse and A5 verifier schema |
| C15 | `evidence(tr3): preserve blocked A5 proof`: every path under `docs/workstreams/temple-tr3/asset-proof/a5/` | 15 | exact-set/hash/image-header audit and blocked status |
| C16 | `docs(tr3): preserve A5 technical and visual reviews`: every path under `docs/workstreams/temple-a5-tech-review/` and `docs/workstreams/temple-a5-visual-review/` | 4 | UTF-8/LF audit; no acceptance wording |
| C17 | `docs(tr3): preserve A6 no-render contract`: every path under `docs/workstreams/temple-a6-preflight/` | 3 | UTF-8/LF audit and no-render boundary |
| C18 | `qa(tr3): preserve A6 read-only review`: every path under `docs/workstreams/temple-a6-visual-review/` | 2 | UTF-8/LF audit; review-only disposition |
| C19 | `asset(d4): preserve the approved runtime texture tier`: every path under `src/assets/tide-scar-d4/` | 8 | manifest hashes, dimensions, color/data roles, byte budget |
| C20 | `feat(render): preserve D4 profile selection`: exact `src/game/render/d4Profile.ts`, `d4Profile.test.ts`, and `theme.ts` | 3 | typecheck plus targeted profile test |
| C21 | `feat(render): preserve D4 asset tier loading`: exact `src/game/render/d4Assets.ts` and `d4Assets.test.ts` | 2 | typecheck plus targeted asset test |
| C22 | `feat(render): preserve the articulated courier`: exact `src/game/render/runnerRig.ts` and `runnerRig.test.ts` | 2 | typecheck plus targeted rig test |
| C23 | `feat(render): preserve the bookend pursuer`: exact `src/game/render/pursuerRig.ts` and `pursuerRig.test.ts` | 2 | typecheck plus targeted pursuer test |
| C24 | `feat(render): preserve deterministic Tide Scar road geometry`: exact `src/game/render/tideScarRoad.ts` and `tideScarRoad.test.ts` | 2 | typecheck plus targeted road test |
| C25 | `feat(render): preserve the D4 world builder`: exact `src/game/render/tideScarWorld.ts` and `tideScarWorld.test.ts` | 2 | typecheck plus targeted world test |
| C26 | `feat(render): preserve the D4 renderer integration`: exact `src/game/render/WorldRenderer.ts` and `WorldRenderer.test.ts` | 2 | typecheck plus targeted renderer test |
| C27 | `feat(ui): preserve the D4 shell and HUD layout`: exact `src/App.tsx` and `src/styles.css` | 2 | typecheck and targeted shell inspection |
| C28 | `test(evidence): preserve the deterministic Temple capture harness`: exact `scripts/capture-temple-evidence.mjs` | 1 | Node syntax/import check only; no browser capture during recovery |
| C29 | `evidence(tr3): preserve the D4 browser diagnostic`: exact two `docs/qa/temple-tr3-browser-*.json` files | 2 | JSON parse, recorded screenshot/hash/status consistency |
| C30 | `docs(tr3): preserve the D4 visual-review log`: exact `docs/workstreams/temple-visual-review/THREAD_LOG.md` | 1 | UTF-8/LF and diagnostic-only wording |

## Atomic source-checkpoint exceptions

`docs/CURRENT_TASK.md` names the same exceptions. They are preservation checkpoints, not
permission to add code:

- C02 is one self-hashed, closed three-script TR4 process; splitting it would make the
  frozen C6 preflight provenance false.
- C07, C08, C10, and C14 each preserve a stage-specific generator/evaluator/runner
  family whose generated metadata binds that family. Some generators exceed 500 lines.
- C26 contains an inherited `WorldRenderer.ts` delta larger than 500 lines and its direct
  test. Partial staging would create an untypecheckable intermediate renderer.

No other source checkpoint may exceed ten product/test paths or 500 hand-authored changed
lines. Each source checkpoint must typecheck and run only its named targeted test before
commit. The final full Vitest/build/browser gates remain deferred until the last future
source edit, as required by `AGENTS.md`.

## Ignored evidence adjuncts

The following pre-existing logs are ignored only by the repository-wide `*.log` rule.
They are immutable evidence, not temporary runtime logs, and are assigned to exact
evidence checkpoints:

- C03: `docs/workstreams/temple-tr4-asset/camera-probe-001/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/diagnostic-001/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/diagnostic-002/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/diagnostic-003/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/diagnostic-004/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/diagnostic-005/blender.log`;
- C03: `docs/workstreams/temple-tr4-asset/matrix-probe-001/blender.log`;
- C04: `docs/workstreams/temple-tr4-asset/diagnostic-006/blender.log`;
- C09: `docs/workstreams/temple-tr3/asset-proof/blender-final.log`.

## Explicitly unrelated and never staged

These five generated/cache paths remain untouched and untracked. They are not part of a
candidate and must never be force-added:

- `docs/workstreams/temple-tr3/asset-proof/tide-scar-hero.blend1`;
- `tools/temple-asset-pipeline/__pycache__/evaluate_asset_proof_a2.cpython-312.pyc`;
- `tools/temple-asset-pipeline/__pycache__/generate_tide_scar_hero_a2.cpython-312.pyc`;
- `tools/temple-asset-pipeline/__pycache__/generate_tide_scar_hero_a3.cpython-311.pyc`;
- `tools/temple-asset-pipeline/__pycache__/run_asset_proof_a2.cpython-312.pyc`.

## Staging and stop rules

Every checkpoint stages only the exact paths named above, prints
`git diff --cached --name-only`, runs `git diff --cached --check`, and compares the cached
set against this plan before committing. `git add .`, `git add -A`, wildcard staging,
cleanup, deletion, and history rewriting are forbidden. A failed verification leaves the
checkpoint `WIP_UNCOMMITTED`; work does not expand into the next checkpoint.

After C30 and C04V, the only dirty paths are the five explicitly unrelated files. The
coordinator refreshed the inventory at `ecd5de640362a6e30c5d0157ecd1590be7673318` and
opened a bounded C7 contract review. This completed plan supplies no C7 execution authority:
camera, modeling, material, export, runtime, browser, and product edits remain governed by
the new independently reviewed C7 authorization chain.
