# TEMPLE-TR3-A6-REVIEW-001 — independent no-render preflight review

**Verdict: BLOCKED as a planning contract.** A6 correctly fixes the source-authority mistake that caused A5 to emit images before its metadata crash, and it materially improves the structural response to the blockout. It is not yet a verifiable pure-data gate because the exact camera/projection and construction records it says it will freeze have not been defined.

This verdict authorizes neither Blender nor any product action. After the bounded corrections below, A6 may be accepted **only as a planning contract** and still requires separate coordinator approval before any implementation or batch.

## Read-only findings

| Review area | Result | Evidence |
| --- | --- | --- |
| Provenance and material authority | Pass | All five A6-pinned source hashes match. A3 has no `materialValues`; A4 has exactly `deck,strata,near,mid,far,courier,pursuer,ridge,ring,scar`; A3/A4 seed, roots, stage, route, canyon, Tide Scar, and non-goals match. A5 metadata is absent and its verifier records the terminal missing-metadata failure. |
| Metadata-crash prevention | Pass as a plan | A4-only `ClayMaterialAuthority`, complete-document parsing, exact source hashes, typed normalization before `bpy`/output/scene work, and no raw post-normalization lookup directly address `a3["materialValues"]`. This has not run yet, so it is not implementation evidence. |
| Fail-closed and boundaries | Pass | Unknown/malformed source, schema/hash/key/range failure, A5 reconstruction, dynamic metadata lookup, image-derived values, and threshold regression block. The contract preserves clean-room, clay-only, no-render, no-runtime, no-Git, and no-QA boundaries. |
| Root-failure coverage | Pass in intent | Road cross-sections/side masses address the slab route; clustered near/mid/far geometry plus occlusion rules address the void; route-frame contacts and actor bands address the detached pursuer; full two-support arch bounds address the undersized arc-only measure; curve polygons/edit proof address the zero-MESH-bbox Tide Scar. |
| Screen-band arithmetic | Pass, but only as interval arithmetic | Portrait, desktop, and landscape each admit a contained courier/pursuer/hazard witness with courier-pursuer overlap/gap of `.080/.020H`, `.060/.045H`, and `.070/.030H` respectively. This proves the listed intervals are nonempty; it does not prove a real camera/route can project the prescribed geometry there. |

## Blocking contract gaps and minimal corrections

1. **Freeze the actual camera definitions.** `profiles` requires fixed camera transform/FOV, and the composition document requires frozen camera matrices, but neither document gives one. Add a versioned per-profile record with coordinate basis, position, target or rotation, up convention, vertical FOV, aspect/resolution, near/far clip, and any lens shift. State whether it intentionally differs from D4 runtime cameras. The pure projection must name its handedness, normalization, clipping rule, and rounding policy. Without these values, `profilePredictions` cannot be reproduced or used to establish cross-viewport feasibility.

2. **Make the nested input/result schema normative, not descriptive.** Define required keys, types, units, finite ranges, and canonical serialization for `profiles`, `construction`, `geometryAudit`, `routeFrameProof`, `profilePredictions`, and `checks`. Include actor/hazard width and full assembly-bounds definitions, road corridor samples at every tested progress, the exact occlusion predicate, the canonical canyon-signature tuple, and the continuous-wall/slab test. Define RGBA as `[0,1]` and the exact curve-edit local delta/hash scope. Otherwise a later writer can satisfy a named boolean or unique ID without proving its geometry.

3. **Bind a green preflight to the later scene input.** Require the future generator to consume the immutable normalized input/result, verify `normalizedInputSha256` plus a canonical construction hash before scene reset or output creation, and copy both hashes into the first planned metadata skeleton. Reject any camera, geometry, or control-point deviation. At present A6 says values are locked, but it does not define this handoff check, so a green calculation could be followed by a different scene.

4. **Resolve Tide Scar authority precisely.** A3's exact record contains `widthToDeck=.016` and `routeCoverage=.67`; it does not contain the A6 phrase "existing inset `.32–.46 m`, width `.07–.11 m`". Name the authority for those values, choose exact frozen scalars or deterministic formulas in `construction`, and state how they coexist with the immutable A3 record. This prevents an untracked geometry override while preserving the editable local curve requirement.

## Consequence

Do not authorize a Blender batch from the current A6 documents. A coordinator may make only the four documentation-level corrections above, then request a fresh read-only review. The later mandatory beauty/mask/depth/manual gates remain necessary: a pure preflight can prevent known structural/provenance regressions, but cannot itself establish final visual quality.
