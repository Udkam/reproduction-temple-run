# TEMPLE-A5 Visual Root-Cause Review

**Reviewer:** TEMPLE-A5-VISUAL-001
**Verdict:** **BLOCKED — no further render is justified until a new coordinator-owned A5 slice adopts this contract.**

This is a clean-room composition review, not a request to copy any asset, character, composition, layout, or trade dress. The desired result is only an original vertical causeway: a warm physical route through a cool, layered canyon/fog depth, with a readable courier, pursuer, hazard, and editable route marker.

## Evidence reviewed

- A3 portrait/desktop/closeup images, metadata, and verifier.
- A4 portrait/desktop/closeup images, metadata, verifier, generator, and evaluator.
- The A3/A4 terminal reports and the repository design/rules/acceptance contracts.

A4 did repair A3's zero-width pursuer projection and makes the two arch supports physically present. It did **not** establish a high-fidelity hero composition. Its valid source checks and manual arch note are necessary structural facts, not visual acceptance.

## Ordered root causes

1. **The camera does not stage one readable chase.**  In A4 portrait, the courier is at `x=.217–.268, y=.586–.653`; the pursuer is at `x=.041–.196, y=.665–.768`. Their horizontal road-band overlap is `-.02130`, so they are adjacent image objects rather than a pursuer visibly following the courier on the same route. The recorded 11.98 px separation just misses the old 12 px gate, but lowering that gate would leave the composition broken. In desktop, the 29 px-wide courier and 96 px-wide pursuer both remain in the far-left quarter while the hazard occupies a separate central region. In closeup, the pursuer is clipped to `x=0`, the courier is at `.257–.313`, and the ring is at `.612–.800`: three disconnected points rather than one forward threat line.

2. **The promised canyon is implemented as counted rocks around a blue void, not screen-space depth.**  The three canyon groups exist in metadata (`6` near, `10` mid, `4` far), but the actual frames read as isolated, similarly faceted boulders around a flat, uniform void. There is no foreground frame, playable middle distance, or far silhouette that successively occludes and recedes. A3/A4's group counts, maximum near-wall occupancy, and zero "repeated generic walls" can all pass while the camera sees neither a canyon wall hierarchy nor fog-separated depth.

3. **The causeway is structurally thick but visually remains a set of long, lightly chamfered slabs.**  Sixteen independent modules, side shelves, and a 5.95 m elevation range are real source facts, yet the beauty frames still lead with long uninterrupted deck caps and long side strips. The route therefore reads as an aerial blockout, not an ancient physical route with a top, broken lip, side mass, and changing scale. This is a medium-structure failure; adding texture noise or changing clay colors would not fix it.

4. **The hero hazard and route marker are structurally described, not visually proved.**  A4's ring contains two supports, a nominal 2.48 m aperture, and a manual `PASS`, but its arch-only projected height is `.06472H` in portrait and `.11601H` in desktop; the desktop projected aperture is `.06503W`. The rendered result is still perceived chiefly as small pillars and loose blocks rather than an immediate pass-under hazard. More importantly, the Tide Scar is an editable `CURVE`, while `projected_bbox()` deliberately samples only `MESH` objects. It therefore reports a zero bbox in every A3/A4 frame. `tideScarExact: true` proves source equality, not visible placement or editability in the hero image.

5. **The verifier validates proxy facts rather than the composition it is meant to decide.**  A4 has no landscape hero frame. Its gates use world-projected boxes, a spring-point aperture estimate, object counts, and one free-text manual note; they do not examine beauty-render semantic masks, road-relative actor alignment, canyon-band occlusion, marker pixels, silhouette readability, or repetition. A threshold-only repair can therefore turn this same aerial blockout green without making it a hero composition.

## Required hierarchy for the next clay proof

The next scene must be built and reviewed in this order. Detail never substitutes for an earlier layer.

| Layer | Required read | Prohibited substitute |
| --- | --- | --- |
| Primary | One vertically legible, warm causeway that narrows into a route horizon; courier followed on that route by a distinct quadruped; one clearly passable hero hazard; asymmetrical near/far canyon silhouette. | A top-down road filling the frame, actors placed in unrelated screen columns, or a void with decorative rocks. |
| Medium | Causeway changes in profile and broken lips; staggered ledges, buttresses, recesses, shelves, and negative spaces; near/mid/far canyon masses that overlap and lose contrast with depth; supported hazard aperture. | Repeated slab sides, regular low-poly boulders, evenly spaced props, full-width fog bands, or a count of off-screen objects. |
| Surface | Restrained clay value separation now; later physical material response through roughness, edge wear, deposits, and contact shadows. The scar remains a narrow world-space route annotation. | Noise, color swaps, decals, or materials used to disguise an unreadable primary/medium composition. |

## A5 screen-band contract

All coordinates below are normalized beauty-render coordinates (`x` left-to-right, `y` top-to-bottom). Measurements must be taken from clipped object-ID/road/depth masks generated by the same scene and camera as the unannotated beauty render; a projected world bbox alone is insufficient. The portrait, desktop, and landscape renders show the same chase state. A closeup may be supplementary only.

| Profile / fixed proof size | Horizon / far route | Route and depth bands | Chase band | Hero hazard band |
| --- | --- | --- | --- | --- |
| Portrait `540×960` | Vanishing/horizon `y=.17–.24`; far silhouette occupies part of `y=.13–.36`, never a full-width strip. | At `y=.94`, road-mask width `.72–.90W`; at `y=.42`, `.22–.38W`. Near/mid/far canyon masks each have visible, non-contiguous content in `y=.38–.92`, `.24–.68`, `.13–.44` respectively. | Courier center `x=.45–.55, y=.60–.68`, height `.085–.14H`. Pursuer center `x=.43–.57, y=.74–.83`, height `.12–.20H`; road-relative horizontal overlap with courier `>=.045W` and vertical clear gap `.020–.075H`. | Ring/hazard center `x=.43–.60, y=.34–.49`; overall height `.15–.25H`; readable opening width `>=.10W`. |
| Desktop `960×540` | Vanishing/horizon `y=.25–.34`; far silhouette in `y=.18–.46`. | At `y=.94`, road-mask width `.66–.86W`; at `y=.48`, `.20–.36W`. Near/mid/far masks occupy distinct, overlapping depth intervals `y=.44–.96`, `.28–.70`, `.18–.48`. | Courier center `x=.48–.56, y=.61–.70`, height `.13–.20H`. Pursuer center `x=.46–.58, y=.75–.86`, height `.17–.27H`; overlap and gap use the portrait requirements. | Ring/hazard center `x=.44–.59, y=.32–.49`; overall height `.20–.34H`; opening `>=.09W`. |
| Landscape `844×390` | Vanishing/horizon `y=.15–.25`; far silhouette in `y=.11–.36`. | At `y=.93`, road-mask width `.72–.91W`; at `y=.42`, `.22–.39W`. Near/mid/far masks occupy distinct, overlapping depth intervals `y=.38–.94`, `.20–.64`, `.10–.38`. | Courier center `x=.48–.57, y=.63–.73`, height `.15–.23H`. Pursuer center `x=.45–.59, y=.77–.90`, height `.19–.30H`; overlap `>=.045W`, clear gap `.020–.070H`. | Ring/hazard center `x=.43–.60, y=.29–.49`; overall height `.22–.36H`; opening `>=.11W`. |

For every profile, the Tide Scar must be within the road mask's right third at each sampled cross-section, not merely somewhere on the screen. It must render as at least two disconnected visible runs, each `>=.12H`, with total visible route-span `.32–.55H`; its beauty-render mask must have positive area. At the listed resolutions its local width is 2–6 px (portrait), 2–5 px (desktop), and 2–5 px (landscape). The scar may not cross the courier, pursuer, or hero-hazard mask.

## Pass/fail checklist — all gates are required

Freeze this schema and its camera values before rendering. Do not change a threshold after seeing the frame; a blocked result requires a new scope, not a lowered bar.

1. **Same-scene evidence.** Render portrait, desktop, and landscape beauty, object-ID, road mask, and depth passes from the identical deterministic scene/camera state. Hash every image and the camera/scene metadata. Landscape is mandatory; closeup cannot replace it.
2. **Primary first glance.** At native size with labels, wireframes, object IDs, and metadata hidden, two independent reviewers must each identify within three seconds: forward route direction, courier, pursuer, the passable hazard opening, the right-edge route marker, and separate near/mid/far canyon layers. Any missed or guessed item blocks the proof. A reviewer must record the failure by profile; there is no averaged score.
3. **Silhouette and route relation.** From flat black semantic masks, the courier, pursuer, and hazard are three separate positive connected components in the screen bands above. The pursuer has an identifiable head/shoulder mass and four grounded limb terminations; the courier has head/torso/two legs; the hazard has two grounded supports and an empty aperture. Their components must intersect the road corridor in the prescribed order. No bbox-only substitute passes this gate.
4. **Depth is visible, not counted.** The depth and object-ID passes must show near, mid, and far canyon geometry at three non-overlapping depth ranges and at least two real occlusion boundaries between them. The beauty image must show progressively lower contrast/saturation from near to far while retaining a distinct far silhouette. A flat water/void region, an uninterrupted long wall, a full-width fog step, or regularly repeated rock silhouette is an automatic failure even if the group counts pass.
5. **Physical route and medium structure.** A route-mask cross-section confirms the stated taper, while the beauty/depth images show at least three visibly different module profiles in the first 70% of the route (for example: broken lip, rise/drop, ledge/recess). Each must change the route's silhouette or occlusion, not just material. The road cannot be accepted as one continuous rectangular cap.
6. **Editable marker proof.** Use the actual curve/spline or a separately rooted editable mesh representation in the mask extractor. Record a baseline beauty/mask hash, move one declared marker control point by a fixed local offset, and prove only a local marker-pixel change; road, actor, hazard, and canyon masks must remain byte-identical. Restore the point and reproduce the baseline hash. Metadata flags such as `editable: true` do not satisfy this test.
7. **No proxy-only acceptance.** Object counts, triangle count, source equality, world bboxes, aperture spring points, luminance, and a manual note are diagnostic evidence only. They cannot set `passed: true` unless gates 1–6 pass. A visual reviewer can block a numerically passing batch; an evaluator cannot override a recorded visual block.

## A4 preservation boundary

Remain untouched:

- All existing A3/A4 evidence, hashes, reports, and source files; A5 must be additive and never overwrite evidence to make a comparison disappear.
- Production/runtime/UI/core/rules/replay/browser/package/configuration paths, root changelog, commits, push, and QA boundary.
- Clean-room provenance: deterministic local geometry only; no commercial/reference assets, reference pixels, downloads, or copied trade dress.
- The existing semantic root names and the independent editable Tide Scar concept: `Causeway_Root`, `Canyon_Root`, `Runner_Root`, `Pursuer_Root`, `Obstacle_Ring_Root`, and `TideScar_Ribbon_Editable`.
- Unless a future coordinator scope explicitly changes them, preserve the A4/A3 route and canyon structural facts (16 modules / 17 spine samples / 125.949 m route / 120.494 degree cumulative yaw / 5.95 m range; three canyon bands with 6/10/4 group counts), the clay-only stage, and the no-export/no-runtime boundary.
- Do not regress A4's genuine structural corrections: a separately readable original quadruped and a hazard with two grounded supports and a physical aperture.

Not frozen for a future authorized correction: the A4 camera framing, the aerial object packing, the visible medium-scale composition, the mesh-only marker measurement, and the bbox-only evaluator. They are the roots to replace, not acceptance criteria to preserve.

## Required next action

Coordinator must decide whether to open one explicitly bounded A5 composition slice. That slice must adopt this contract before it launches any new render. This review authorizes no render, Blender launch, export, optimization, runtime work, browser work, commit, push, or QA contact.
