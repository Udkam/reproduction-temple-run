# Temple R1G candidate evidence

Updated: 2026-08-09 Asia/Shanghai

Status: **candidate captured; independent evidence and visual QA pending**

## Candidate chain

- Branch: `main`
- R1G opening contract: `e468a0deff3befa2d64994b1a397f0880f9388e7`
- Courier source checkpoints: `43ba6a3d4044d936199f4166f2d4efc60ae9a189`, `f08a17044bd1c677857f732bffb7f5b38342dad4`
- Evidence/schema correction contract: `0e7e8b2fd984ac3d48727087ac432d7fa3880a5a`
- Final source candidate: `8de73c169d03ce32e15bce2145d64afff8973330`
- R1G-E1 changes only `WorldRenderer.ts` and its direct test; the courier source remains frozen at `f08a170`.

## Verification after the last source edit

- Development target: `src/game/render/WorldRenderer.test.ts`, `6/6` passed.
- Final typecheck: `npm.cmd run typecheck`, passed.
- Final complete suite: `17` files / `75` tests, passed once.
- Final no-delete build: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-build-8de73c1-20260809T201903272`, passed; only the existing non-blocking Vite chunk-size advisory remains.
- Candidate source paths were clean before capture.

## Preserved browser evidence

- Directory: `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-e1-candidate-8de73c1-20260809T201927156`
- Manifest: `candidate-8de73c1-browser-evidence.json`
- Manifest SHA-256: `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`
- Capture script SHA-256: `DB49CEED0C4A79EC2E4373847F05C03A141BB1777EBB92AA249933FDA135A05B`
- Schema/matrix: `2` / `TEMPLE-TR4-R1G-E1-14`
- Contract/candidate binding: `0e7e8b2fd984ac3d48727087ac432d7fa3880a5a` / `8de73c169d03ce32e15bce2145d64afff8973330`
- Capture result: `captured`, zero failures, 14 records and 14 PNGs.
- All PNG SHA-256 values were recomputed after capture and match the manifest.
- Every state hash equals its independent replay hash; every frame has one canvas, zero gameplay DOM/overflow/problems/context loss, and at most `28,000` triangles.
- The 11 ordinary-composition records have null pursuer x/y/bounds/gap and exactly `31` calls. Jump, slide, and game-over retain required scene entities at exactly `36`, `37`, and `34` calls.
- Vite PID `6948` and capture PID `35196` were project-owned; capture exited, Vite was stopped by exact PID, and port `4208` is closed.

| Record | PNG SHA-256 | State hash | Calls | Triangles |
| --- | --- | ---: | ---: | ---: |
| `gait-phase-0-desktop-tick60` | `8D5DBDFF4F80D75DEB422F4D13DAA33C561EFB5698E6D961E6844F04F5D055B0` | `fa4e69d7` | 31 | 23,574 |
| `gait-phase-1-desktop-tick64` | `7E372BF71599F4FD4BFBD5BF12663BF7F7B7BF61AF579A23A8302A9F901ABFBE` | `d93e1a93` | 31 | 23,574 |
| `gait-phase-2-desktop-tick68` | `DCE9F97D375E574F5B39F51966B30AA05BFD65C0D9EEF419BEDF902D2935C5D8` | `a8635405` | 31 | 23,574 |
| `gait-phase-3-desktop-tick72` | `14FE173C4F166659AC9045AB9B23E5617E84D4A6A3513439BEA54A9B24354390` | `9217dafc` | 31 | 23,574 |
| `gait-phase-4-desktop-tick76` | `5FF7F8EAAB2A983FB8D8EDCFA8064C2B49973E27C39C9F4A20A9D389DE8B39DD` | `237cedab` | 31 | 23,574 |
| `gait-phase-5-desktop-tick80` | `B88B82B8DA48533B4BE4C570B47DADE0296BE9E8D540A03A49DAB49DF613D0C0` | `3687c795` | 31 | 23,574 |
| `gait-phase-6-desktop-tick84` | `D27321404191BC290AA8AE0AAB829B166BC0EC346A52C1DD837DE72ADCE7C56C` | `9aeda728` | 31 | 23,574 |
| `gait-phase-7-desktop-tick88` | `0395C64DBC2FC8F3C4F2CBA592F452FFA04EBC870DFB5D8158E9A57EE6176FFA` | `dce46007` | 31 | 23,574 |
| `running-portrait-tick60` | `D6DF1DF2205239AC62E34DD26F57FE7179D247DAB78BA948219EA95B47D43C03` | `fa4e69d7` | 31 | 23,574 |
| `running-landscape-tick60` | `9BA63E0B4690F811FB941FF0103387A527524A76A7A422C3593233EA1409BF30` | `fa4e69d7` | 31 | 23,574 |
| `jump-apex-portrait` | `CEFB0D28F37807BA17E0C05E8D468D9D2082D2DBD8DF72AE1527BA020406AEBF` | `d6238479` | 36 | 24,810 |
| `slide-mid-landscape` | `115CA5614E98BDA67A0ED2FD0FC0B47F01961034FC02861102E38BAC342963E0` | `28fadccd` | 37 | 24,890 |
| `collision-game-over-desktop` | `B14A4BAF27A920D362742D3BD698443E7855702AE859DEFB10D85E633F46465F` | `3df53258` | 34 | 24,236 |
| `reduced-motion-portrait-tick60` | `7BD922D3189F1992A0B8406110C8B060BB8BBD9F0B7032BB4FA527C4E924B100` | `fa4e69d7` | 31 | 23,574 |

## Immutable failed predecessor

The prior directory `C:\Users\Alex Chen\AppData\Local\Temp\tide-relay-r1g-v2-candidate-f08a170-20260809T193900` remains unchanged. Its failed manifest SHA-256 is still `0CA07D549173FE12A367AE2C9EA55A5E393759561D845CAEC99B4DBBB92D06D1`; it remains failure history and is not acceptance evidence.
