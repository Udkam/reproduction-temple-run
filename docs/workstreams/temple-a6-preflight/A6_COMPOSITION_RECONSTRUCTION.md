# TEMPLE-TR3-A6 — composition reconstruction specification

This is a no-render construction specification for a later pure-math preflight. It addresses A5's disconnected slab route, unreadable pursuit line, undersized arch, and counted-but-flat canyon before any Blender scene can exist. It uses only an original tide-scarred mineral causeway and broad readability principles; it does not reproduce commercial art, characters, maps, screen layouts, or trade dress.

## Freeze order

Freeze in this order: (1) profile camera and screen/HUD rails, (2) central route and actor/hazard bands, (3) physical road cross-sections, (4) depth-layer canyon plan, (5) editable Tide Scar polygons, then (6) later lighting/material work. Exposure, samples, fog density, surface noise, and color adjustments cannot repair a failed geometric preflight and are not preflight variables.

All screen values are normalized with origin at top-left. A pure projection routine must calculate these values from frozen camera matrices and analytic construction bounds; no image, renderer, `bpy`, or post-render bounding box is allowed.

## Central forward chase line and safe rails

The horizon, road centerline, courier, pursuer, and arch all stay in one forward visual corridor. A generic top HUD-safe rectangle is reserved for future shell information only; no A6 scene subject, scar, or far silhouette may intersect it. This is a safety rail, not a copied interface layout.

| Profile | Horizon center / road center | Road widths | Courier | Pursuer | Arch/hazard | HUD-safe rectangle |
| --- | --- | --- | --- | --- | --- | --- |
| Portrait `540x960` | horizon `x=.47-.53,y=.17-.24`; entry center `x=.47-.53,y=.94` | `.72-.90W` at `.94H`; `.22-.38W` at `.42H` | center `x=.45-.55,y=.60-.68`; height `.085-.14H` | center `x=.43-.57,y=.74-.83`; height `.12-.20H`; overlap `>=.045W`; gap `.020-.075H` | center `x=.43-.60,y=.34-.49`; height `>.15H`; opening `>.10W` | `x=.04-.96,y=.03-.14` |
| Desktop `960x540` | horizon `x=.47-.53,y=.25-.34`; entry center `x=.47-.53,y=.94` | `.66-.86W` at `.94H`; `.20-.36W` at `.48H` | center `x=.48-.56,y=.61-.70`; height `.13-.20H` | center `x=.46-.58,y=.75-.86`; height `.17-.27H`; overlap `>=.045W`; gap `.020-.075H` | center `x=.44-.59,y=.32-.49`; height `>.20H`; opening `>.09W` | `x=.04-.96,y=.03-.15` |
| Landscape `844x390` | horizon `x=.47-.53,y=.15-.25`; entry center `x=.47-.53,y=.93` | `.72-.91W` at `.93H`; `.22-.39W` at `.42H` | center `x=.48-.57,y=.63-.73`; height `.15-.23H` | center `x=.45-.59,y=.77-.90`; height `.19-.30H`; overlap `>=.045W`; gap `.020-.070H` | center `x=.43-.60,y=.29-.49`; height `>.22H`; opening `>.11W` | `x=.04-.96,y=.03-.18` |

Every actor/hazard box must be contained with a `.02` margin. The courier and pursuer must each overlap the analytic road corridor, while the pursuer stays vertically behind the courier. The arch may sit beyond the courier but cannot overlap the courier/pursuer boxes or the HUD-safe rectangle. A failed band is a geometry/layout failure, not permission to pan, crop, or change exposure after the fact.

## Physical causeway reconstruction

The exact A3 route data stays fixed: 16 modules, 17 spine samples, 125.949 m length, 120.494 degrees cumulative yaw, 5.95 m vertical range, four edge losses, 26 shelves, 32 original strata breaks, and a `.68W` safe center corridor. The center corridor stays clear of all visual side mass; no canonical lane, collision, or state data changes.

Each of the 16 modules needs a deterministic signature from `(270803,moduleIndex)` and at least one event from every class below across the first 70% of the visible route. All 16 modules are decorated, at least 32 attached side fragments exist, and no signature repeats for more than two adjacent modules.

| Cross-section event | Required physical construction | Quantified preflight check |
| --- | --- | --- |
| Broken lip/drop | A cap has a distinct top and outer vertical lip with an irregular notch or fractured loss. | cap thickness `>=.80 m`; lip drop `.14-.28 m`; at least 6 modules; no lip enters the central `.68W`. |
| Stepped side mass/buttress | The cap attaches to one or more downward offset stone masses, not a long vertical strip. | visible side-mass descent `>=.80 m`; 2+ fragments on 12+ modules; each fragment length `<=.35` of its module; outer footprint stays in one `.16W` side reserve. |
| Ledge/recess/rise | A locally offset shelf, recessed joint, or vertical change alters silhouette/occlusion. | at least 6 modules; local height change `.18-.45 m` or setback `.25-.70 m`; at least three distinct event types appear in the first 70%; no identical event-form run over two. |

The preflight records a cross-section polyline at every module midpoint and proves: positive top thickness; distinct lip/side mass; zero side-feature intrusion into the `.68W` corridor; route taper in the profile table; and no uninterrupted rectangular cap or side wall across a joint. Material noise, clay-value changes, or separate off-road rocks do not count as structural events.

## Canyon depth reconstruction

Keep the immutable three bands and group counts: 6 near buttress clusters, 10 middle mesa/shelf clusters, 4 far silhouette clusters, three portrait abyss openings, `maxNearWallOccupancy <=.19`, and zero generic continuous walls. A group count alone never passes.

- Each near cluster contains one buttress, one offset ledge, and one recess/negative gap; each mid cluster contains a mesa, short fractured terrace, and offset shelf; each far cluster contains two asymmetric silhouette masses separated by a gap.
- The 20 cluster signatures are all unique. Hash-derived rotation, scale, side, and fracture location cannot repeat as a neighbouring form; the maximum identical cluster-form run is one.
- A canyon mesh cannot be a continuous rectangular/extruded wall: reject any single side mesh longer than `6 m` adjacent to the route, any continuous side profile across a module joint, or any planar group whose length-to-height ratio exceeds `3:1` without a recess/gap.
- The pure projection plan must place non-contiguous near/mid/far content respectively in the profile intervals: portrait `y=.38-.92/.24-.68/.13-.44`; desktop `.44-.96/.28-.70/.18-.48`; landscape `.38-.94/.20-.64/.10-.38`. It must predict at least two occlusion boundaries, each with `>=.02W` horizontal overlap, and a far silhouette that does not occupy the full width.

The later visual gate still decides whether depth reads; this preflight only proves that the proposed geometry cannot collapse into A5's counted rocks around a void or a repeated slab canyon by construction.

## Route-frame pursuit proof

Preflight defines the courier and pursuer in route coordinates, not independent world or screen positions:

- courier: route progress `s`, lateral offset `0`, feet projected to the analytic deck top;
- pursuer: the same route segment at `s - 4.0 m`, lateral offset whose magnitude is `<=.20W` and remains inside the `.68W` center corridor;
- `dot(routeForward, courierPosition - pursuerPosition) > 0`, longitudinal separation is exactly `4.0 m` before presentation scaling, and all four pursuer foot contacts are within `.05 m` of the analytic deck surface;
- projected courier/pursuer bands, overlap, clear gap, containment, and HUD exclusion must meet the profile table simultaneously.

The preflight emits `routeFrameProof` with route samples, forward vectors, lateral coordinates, four contact distances, projected corridor intervals, and a boolean for every condition. A camera cannot be adjusted to pass this proof after the values are locked.

## Supported arch and editable Tide Scar

The hero obstacle is one original broken-stone arch assembly. It has exactly two distinct supports, both contacting the deck; outer span-to-deck width stays `.42-.56`; support bodies are at least `2.15 m` tall; its true clear aperture is at least `2.72 m`, `openingToOuterArea >=.38`, and no decorative piece closes the aperture. Its assembly is the measured hazard, not a detached arc-only bounding box. It must satisfy the profile height/opening bands above before any render is allowed.

`TideScar_Ribbon_Editable` remains an actual local curve/spline annotation, never a painted road texture or generic bounding box. Preflight extracts its control points into road-relative polygons with the existing inset `.32-.46 m`, width `.07-.11 m`, right-third condition, and semantic clips for courier, pursuer, and arch/hazard. It must have at least two visible candidate runs, each projected length `>=.12H`, total projected span `.32-.55H`, and zero polygon intersection with courier, pursuer, hazard, or HUD-safe rectangles.

The preflight performs an editability proof without rendering: move one declared control point by a fixed local offset, recompute the curve hash/polygons, require exactly its local segment to change, and require road, actor, hazard, and canyon construction hashes to be identical. Restore the point and require the original curve hash. This is stronger than `editable: true` metadata and does not touch A5 evidence.

## Green condition before a future batch

All compatibility, profile, road, canyon, route-frame, arch, and Tide Scar checks must be green in one pure-data result before a later coordinator may consider authorizing a Blender batch. The result must explicitly retain the historical A4 and A5 failures. Any missing material key, untyped metadata access, screen-band violation, corridor intrusion, slab/wall pattern, actor disconnection, aperture failure, Scar intersection, or threshold reduction is `BLOCKED`; it stops before Blender rather than producing another consumed image batch.
