# Tide Scar visual-design log

Owner: `temple_visual_design`
Design coordinator: `019f4deb-7e83-7583-8cd5-8e6f075bc331`
Scope: design research, motion/layout specification, isolated static Canvas prototype only.
Branch / baseline: `codex/temple-run` / `c5b3db041175c19c71bd0086baf1e034fc97caf0` (read-only visual baseline)
Stable production milestone: `78dbdeb` (TR2 independently accepted and coordinator accepted; received 2026-07-14)
Status: design-only candidate verified; no production authorization.

## Boundaries honored

- Created only `docs/workstreams/temple-visual-design/`; did not modify `src`, config, package files, root design/task/changelog files, production AGENTS, or existing QA evidence.
- No merge, rebase, reset, clean, delete, push, production test/build, or production runtime edit.
- `npm.cmd run dev -- --host 127.0.0.1` was attempted once only to view the candidate page and stopped because local dependencies lack `vite`; production screenshots remained read-only visual evidence.

## Research (2026-07-14)

- Full UTF-8 Python `Path.read_text` review: `AGENTS.md`, `DESIGN.md`, `CURRENT_TASK.md`, `docs/rules/RUNNER_RULES.md`, `docs/qa/TEMPLE_ACCEPTANCE.md`, `docs/qa/temple-browser-evidence.json`, and `docs/workstreams/temple-tr2/THREAD_LOG.md`.
- Inspected current formal screenshots: `running-desktop.png`, `chase-close.png`, `mobile-portrait.png`. Observed leg/contact ambiguity, weak obstacle pre-read differentiation, bottom-heavy pursuer read, and portrait HUD competition.
- Public research: `https://imangistudios.com/` and `https://imangistudios.com/thegames/temple-run/`; used only high-level continuous-chase tension and mobile readability principles.
- Supplied Bilibili page `https://www.bilibili.com/video/BV1ce41137n2/` returned error 412. One safe fallback to its embed player rendered only a shell; stopped without scraping, downloading, or bypassing.
- Preview-only mood board generated with built-in image generation, stored as `tide-scar-moodboard-preview.png`; it is not a production asset and not counted as a formal mockup.

## Artifacts

- `ORIGINAL_VISUAL_DIRECTION.md`
- `RUNNER_MOTION_SPEC.md`
- `OBSTACLE_LANGUAGE_SPEC.md`
- `STATE_LAYOUT_SPEC.md`
- `tide-scar-prototype.html`, `tide-scar.css`, `tide-scar.js`
- `verify_tide_scar.py`, `prototype-acceptance.json`, and formal `mockups/*.png` after the targeted run
- `mockups/v2-runner-contact-pass.png` — V2 contact/passing comparison accepted during visual preview
- `DESIGN_REVIEW.md`

## Verification (2026-07-14)

Commands run, without invoking project install/test/build:

```text
node --check docs/workstreams/temple-visual-design/tide-scar.js
python -m http.server 4173 --bind 127.0.0.1  (isolated static server)
python -u docs/workstreams/temple-visual-design/verify_tide_scar.py --base-url http://127.0.0.1:4173
```

Result: **11 captures verified, zero console and page errors.** The verifier exercised the interactive state buttons separately, then captured the clean visual surface. Every capture had one canvas, zero gameplay DOM entities, zero horizontal overflow, in-viewport HUD/pause DOMRects, exact mock-state HUD text, positive clipped runner/pursuer/obstacle bounds, HUD contrast 11.54:1, scar contrast 12.82:1, coral/sand contrast 3.75:1, and a reduced-motion state that preserved canonical mock values.

V2 received explicit coordinator visual-preview acceptance before this final run. It narrows the tide scar to a road-edge aid plus short HUD terminal, adds the three mineral depth layers, fixes non-crossing contact/passing poses, retains identifiable normal/close pursuers with positive separation, and gives beam/ring physical mass, supports, and shadows. This remains a design-only result.

Formal mockups (the first nine are the requested presentation set):

| Screenshot | SHA-256 |
| --- | --- |
| `mockups/mobile-normal.png` | `ddc67871fe38018f47eac243d667bb795c08ec775ad0001969a6e8f2280fd47e` |
| `mockups/mobile-close-chase.png` | `bc342d32948c1175e3dd2d9420f18c21f710ab3ddc546392cc24c73b35ab8e6a` |
| `mockups/mobile-milestone.png` | `6750fdb198ec21e87052844d0bff75ec369bec26435ae440871e7a34d66e1367` |
| `mockups/desktop-run.png` | `4a10047aa4f49b8129e885c5bb91bd1b083ad8c9ce2b89088eee57247a425d4f` |
| `mockups/desktop-beam.png` | `6139ec003d5b260c624b4b8435bd5cab76249b8e51419b8577f6e28ed226b866` |
| `mockups/desktop-ring.png` | `d497f3e38701d4c46c847d3f1e2aa01b82678bcc539163966799b1ade45c9b41` |
| `mockups/desktop-column.png` | `db8db2b98a38b35c23cb16959a6917e7ad0e1181b42d28b791fce944ef88fb6e` |
| `mockups/desktop-gap.png` | `d234f3d548bd2621a797cc81951f14835fa52387468f7714d170303bcc5aea30` |
| `mockups/desktop-paused.png` | `b79becf4007b7497b574088ae3127539092b3cb0e04fedcd3ecff5a7802bc53f` |
| `mockups/mobile-landscape.png` | `9cf0670400319af9630e3e32332f4327d167d095bf06793ae98654f3fa2613b7` |
| `mockups/mobile-reduced-motion.png` | `6f530ee3a9cd93b3d2ba025dc7327e2db66942221129d4ce6592c2abb917dd97` |

The authoritative machine-readable records and current SHA-256 values are in `prototype-acceptance.json`; rerun the command above after any visual change.

## Open items

- Do not translate this candidate into production without a new bounded coordinator authorization.
- Video keyframes are unavailable in this environment due to documented 412 access block.
- Production adoption must preserve continuous interpolation across all eight gait phases and a non-capture positive `chaseGap` screen interval across FOV / viewport changes.

## Conditional-reject P1 repair (2026-07-14)

- Independent design QA conditionally rejected `913ff46` only for two P1 layout issues: low-height landscape hid `flow` / `shards`, and the 250m marker sat in a central position that could compete with a column.
- Scope stayed within this directory. Changed only `tide-scar.css`, `tide-scar.js`, `verify_tide_scar.py`, `STATE_LAYOUT_SPEC.md`, `DESIGN_REVIEW.md`, this log, `prototype-acceptance.json`, and the two affected formal PNGs. No production path, root document, package/config, existing QA evidence, or unrelated mockup was edited.
- P1-A: 844x390 now has a compact 44 px rail with complete score, distance, flow, and shards labels/values plus the 44 px pause target. The wordmark and gesture hint yield space; canonical metrics do not.
- P1-B: `250 m` now uses a right road-edge / tide-scar anchor instead of a centered message. The 390x844 marker bounds are `(255,320.7,82.7,23.4)` and its calculated right-road-edge distance is `56.38 CSS px` (acceptance interval `18–96`). Its intersection areas with score, distance, flow, shards, pause, runner, pursuer, and column are all `0`.
- Targeted commands (no project install/test/build): `node --check docs/workstreams/temple-visual-design/tide-scar.js`; `python -u docs/workstreams/temple-visual-design/verify_tide_scar.py --base-url http://127.0.0.1:4173 --labels mobile-landscape mobile-milestone`.
- Result: **2 directed captures verified; 9 untouched formal records preserved; 0 console/page errors.** Both targeted captures retain `canvasCount=1`, `gameplayDomEntities=0`, and `overflowX=0`.
- Updated evidence: `mockups/mobile-landscape.png` SHA-256 `d869fbc1f578ade8870ccf76b4dda2e478e29746ccf95d4847eab9c3d827a38f`; `mockups/mobile-milestone.png` SHA-256 `7df5ff170039bd3dab8e6b5c8a0a19e18be055059d30602c0410f9bfc8ef0a6d`.
- A temporary user-approved north-star image was inspected only for high-level Tide Scar language (high bridge, warm stone, deep-water canyon, haze, restrained white scar/coral, rear pursuer). It was not copied, embedded, or used as a runtime asset; no visual expansion beyond these two P1 repairs occurred.
