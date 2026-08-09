# Temple R1G independent QA disposition

Date: 2026-08-09 Asia/Shanghai

Status: **READY for coordinator acceptance; R1G is not yet the complete game**

## Reviewed candidate

- R1G source base: `e468a0deff3befa2d64994b1a397f0880f9388e7`
- Evidence/schema contract: `0e7e8b2fd984ac3d48727087ac432d7fa3880a5a`
- Final source candidate: `8de73c169d03ce32e15bce2145d64afff8973330`
- Evidence manifest SHA-256: `9A5628675F7BF977225BBE354FB035EB9EDD10D47538B52D1F47555298D0C0EE`
- Candidate browser matrix: `TEMPLE-TR4-R1G-E1-14`, 14 records.

## Independent source dispositions

- Courier range `e468a0d..f08a170`: `READY`, no P0/P1/P2. Only `runnerRig.ts` and its direct test changed; the two source checkpoints total exactly 500 hand-authored added/modified lines. Actual geometry and instance matrices prove closed outward non-degenerate volumes, six batches, one caster, `<=3,200` courier triangles, joint/ground/half-cycle gates, deterministic pose resets, speed response, and reduced-motion behavior.
- R1G-E1 range `0e7e8b2..8de73c1`: `READY`, no P0/P1/P2. Only `WorldRenderer.ts` and its direct test changed, at 45 hand-authored added/modified lines within the 80-line cap. Initial and live hidden pursuer snapshots now use null x/y, the live path uses the tested pure constructor, and visible projection behavior is unchanged.

## Independent visual disposition

`VISUAL_READY`, no P0/P1. All 14 new PNGs were opened at original resolution and compared with the prior courier baseline. Eight gait phases remain continuous and grounded; portrait and approximately 85 px landscape silhouettes preserve the hood/shoulder/trunk/pelvis chain, elbows, knees, separate feet, forked coat, waist and bounded relay. Jump, slide, game-over, and reduced-motion poses remain distinct. No detached joint, foot float/slide, road or limb penetration, or robot/target-core regression was found.

The game-over overlay still reduces contrast, but the failed pose remains readable and unchanged from the independently accepted visual baseline. This does not accept later pursuer, hazard, lighting, animation-polish, or complete-game work.

## Independent evidence disposition

`READY`, no P0/P1/P2.

- Manifest schema `2`, matrix `TEMPLE-TR4-R1G-E1-14`, status `captured`, zero failures.
- All 14 IDs are unique and ordered, use seed `1414087749`, and bind the exact contract and candidate SHAs.
- Eleven ordinary/gait/reduced records are exactly `31` calls / `23,574` triangles with null pursuer x/y/bounds/gap and `visible=false`.
- Jump is tick `21`, `36` calls / `24,810` triangles, with command trace/hash `d6238479`, visible opening pursuer, and positive exact `section-0:jump-beam` bounds.
- Slide is tick `15`, `37` calls / `24,890` triangles, with command trace/hash `28fadccd`, visible opening pursuer, and positive exact `section-0:slide-ring` bounds.
- Game-over is tick `336`, `34` calls / `24,236` triangles, with `pursuer-caught`, command trace/hash `3df53258`, visible pursuer, and null capture gap.
- Every frame has one canvas, zero gameplay DOM/overflow/problems/context loss, canonical state equal to replay, and a screenshot SHA-256 independently matched to its PNG.
- Exactly 14 PNGs exist in the unique evidence directory. Capture and Vite stderr are empty; port `4208` is closed.

## Boundary

This disposition proves only the bounded R1G courier reconstruction and R1G-E1 snapshot-schema conformance. Overall TR4 and the complete high-fidelity TIDE//RELAY game remain in progress.
