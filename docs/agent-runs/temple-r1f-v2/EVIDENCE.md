# Temple R1F-V2 evidence record

Candidate: `6680489cf2e3ec035da44fc1dde9aa7606bdd9c7`

Evidence directory: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1f-v2-candidate-6680489-20260808T110100\`

Evidence JSON: `candidate-6680489-browser-evidence.json`

Evidence JSON SHA-256: `0B6D8767C0A4A4E61BC5E7C3305045476E9F017863256F7C17F96D8AC051321B`

Production build: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1f-v2-build-20260808T105753336\`

## Verification

- Targeted renderer/world test: 1 file, 8 tests passed.
- Final typecheck after the last source edit: passed.
- Final complete Vitest suite: 17 files, 72 tests passed.
- Final production Vite build: passed; only the existing non-blocking chunk-size advisory remained.
- `git diff --check`: passed.
- Browser evidence: seven frames captured once against the exact candidate, with one canvas, zero gameplay DOM, zero overflow, zero console/page problems, zero context loss, 31 draw calls, and 24,484 triangles in every record.
- Candidate Vite PID 11244 was stopped by exact ownership after capture; port 4208 was verified closed.

## Frame hashes

| Profile | Tick | SHA-256 |
| --- | ---: | --- |
| desktop 1440x900 | 60 | `17EA61B68F4BD5F112213BE47A860C7F5A6E51111CA9A4A1E90C3B15B289C594` |
| desktop 1440x900 | 68 | `7198190DF98CBFEF6E1FA14ED8B029C6CCB2097C3CB31007E2343E2913E988AA` |
| desktop 1440x900 | 76 | `B15279EC0BA9094047DABA006954CF8D1F4A5C73DD1DE5E46CCB9851CA4547B1` |
| portrait 390x844 | 60 | `BD72ED14B2ABFCCE352B04AC0AD02F155961033FE72CB052D05FE6B53980BE3A` |
| landscape 844x390 | 60 | `2CF5E4C1F20962FF0CAFF260976E1BFC4911ACCD2C41F22EDDC954C30071FF0C` |
| landscape 844x390 | 68 | `8965606C8D154A91321EF1DEBA9A8D2FB0BC1C832532E5098FCE0A38B25C2CB1` |
| landscape 844x390 | 76 | `C98EE2D5D67E187E43FE0B9C6480017562CC1677D583AF61630A37045D0DF058` |

## Independent QA

- Source QA: READY; no P0/P1/P2. It verified exact source authority, six instanced signatures, five non-coplanar panels, closed thick lip/return geometry, real array reconstruction, face-aware world-anchored zero-emissive PBR, lifecycle, and absence of canonical-state changes.
- Test/evidence QA: READY; no P0/P1/P2. It matched the evidence JSON and every PNG hash, reconstructed the real staggered joint edges, and verified all seven profile/tick and render-health records without rerunning the complete suite.
- Visual QA: READY; no P0/P1. It viewed all seven PNGs at original resolution and found readable staggered panels, non-coplanar response, thick asymmetric lips/returns/side mass, stable motion, and no repeated stamp, false hole, floating lip, full-width dark seam, shimmer, or lost runner/hazard/turn readability.

This record does not accept the courier, pursuer, hazards, character materials/detail, animation, broader asset program, or final game.
