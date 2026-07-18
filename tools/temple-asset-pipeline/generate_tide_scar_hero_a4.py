"""TEMPLE-TR3-A4: one offline clay-only correction derived from closed A3.

The A3 generator remains the source of the route, canyon, clay materials, and
Tide Scar.  This A4 file changes only the permitted camera framing, pursuer
silhouette/transform, and supported broken-stone arch geometry.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_tide_scar_hero_a3 as a3


ROOT_NAMES = a3.ROOT_NAMES
A3_GENERATOR = SCRIPT_DIR / "generate_tide_scar_hero_a3.py"
A3_METADATA = REPO_ROOT / "docs/workstreams/temple-tr3/asset-proof/a3/a3-clay-metadata.json"
MATERIAL_VALUES = {
    "deck": [.58, .56, .53, 1.0],
    "strata": [.38, .40, .42, 1.0],
    "near": [.42, .45, .47, 1.0],
    "mid": [.34, .38, .42, 1.0],
    "far": [.27, .33, .38, 1.0],
    "courier": [.78, .76, .70, 1.0],
    "pursuer": [.20, .23, .26, 1.0],
    "ridge": [.31, .20, .19, 1.0],
    "ring": [.70, .68, .63, 1.0],
    "scar": [.88, .84, .74, 1.0],
}


def child_root(name: str, parent):
    obj = a3.bpy.data.objects.new(name, None)
    a3.bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def build_ring_a4(mats: dict, ring):
    """A tall, open arch: two obvious grounded supports plus broken voussoirs."""
    point, tangent, deck_width = a3.route_sample(16.0)
    ring.location = point + a3.Vector((0.0, 0.0, .13))
    ring.rotation_euler[2] = math.atan2(tangent.y, tangent.x) - math.pi * .5
    arch = child_root("A4_BrokenStoneArch", ring)
    support_left = child_root("A4_ArchSupport_Left", ring)
    support_right = child_root("A4_ArchSupport_Right", ring)

    outer_radius, inner_radius, thickness = 1.82, 1.24, .46
    support_x, support_height = 1.48, 1.78
    for sign, support, label in ((-1.0, support_left, "L"), (1.0, support_right, "R")):
        a3.add_cube(
            f"A4_Support_{label}", (sign * support_x, 0.0, support_height * .5),
            (.35, .48, support_height * .5), mats["ring"], support, (0.0, 0.0, sign * .035),
        )
        a3.add_cube(
            f"A4_SupportCap_{label}", (sign * support_x, 0.0, support_height + .08),
            (.44, .53, .16), mats["ring"], support, (0.0, 0.0, sign * .025),
        )
        a3.add_rock(
            f"A4_SupportFoot_{label}", a3.Vector((sign * support_x, .13, .04)), .48, .52, .26,
            mats["ring"], support, 7400 + (1 if sign > 0 else 0), 6,
        )

    # A short, intentionally uneven voussoir arc keeps a large, unoccluded opening.
    for index in range(9):
        angle = math.pi * index / 8.0
        radial = outer_radius - thickness * .5
        x = math.cos(angle) * radial
        z = support_height + .10 + math.sin(angle) * radial
        scale = (.31 + .025 * (index % 2), .46, .30 + .018 * ((index + 1) % 3))
        a3.add_cube(
            f"A4_ArchVoussoir_{index:02d}", (x, 0.0, z), scale, mats["ring"], arch,
            (0.0, angle - math.pi * .5, (index % 2 - .5) * .075),
        )
    # A missing upper-right corner makes the stone span broken without closing the aperture.
    a3.add_cube("A4_BrokenKeystone", (.42, -.02, support_height + outer_radius * .92), (.22, .44, .16), mats["ring"], arch, (0.0, .22, -.19))
    ring["a4Role"] = "fully supported broken-stone opening: two grounded supports and a clear aperture"
    return {
        "outerSpanToDeckWidth": round((outer_radius * 2.0) / deck_width, 3),
        "thicknessToOuterSpan": round(thickness / (outer_radius * 2.0), 3),
        "openingToOuterArea": round((inner_radius / outer_radius) ** 2, 3),
        "apertureWidthMetres": round(inner_radius * 2.0, 3),
        "supportCount": 2,
        "baseContactsDeck": True,
        "manualReadTarget": "supported broken-stone opening",
    }, arch, support_left, support_right, inner_radius


def build_pursuer_a4(mats: dict, pursuer) -> None:
    """An original, wider quadruped silhouette that remains behind the courier."""
    point, tangent, _ = a3.route_sample(-1.0)
    pursuer.location = point + a3.Vector((0.0, 0.0, .13))
    pursuer.rotation_euler[2] = math.atan2(tangent.y, tangent.x) - math.pi * .5
    a3.add_cube("A4_PursuerShoulderMass", (0.0, -.04, .78), (.82, .98, .42), mats["pursuer"], pursuer, (0.0, .09, 0.0))
    a3.add_cone("A4_PursuerWedgeHead", (0.0, 1.03, .82), .39, .22, .74, mats["pursuer"], pursuer, (math.radians(90), 0.0, 0.0))
    a3.add_cube("A4_PursuerJaw", (0.0, 1.28, .59), (.32, .29, .11), mats["pursuer"], pursuer, (0.0, 0.0, 0.0))
    for side in (-1.0, 1.0):
        for fore in (-1.0, 1.0):
            hip_y = fore * .62
            a3.add_cube(
                f"A4_PursuerUpperLeg_{side}_{fore}", (side * .58, hip_y, .46),
                (.13, .14, .42), mats["pursuer"], pursuer, (0.0, side * .24, fore * .16),
            )
            a3.add_cube(
                f"A4_PursuerLowerLeg_{side}_{fore}", (side * .62, hip_y + fore * .13, .14),
                (.10, .13, .29), mats["pursuer"], pursuer, (0.0, side * -.17, fore * -.13),
            )
    a3.add_cube("A4_PursuerDorsalRidge", (0.0, -.12, 1.22), (.18, .72, .12), mats["ridge"], pursuer)
    pursuer["a4Role"] = "original broad black-rock quadruped: wedge head, shoulder mass, four grounded limbs, dorsal ridge"


def aperture_projection(scene, camera, ring, inner_radius: float, resolution: tuple[int, int]) -> dict[str, float]:
    # The aperture is intentionally empty; project its left/right springing points rather than adding a guide mesh.
    left = ring.matrix_world @ a3.Vector((-inner_radius, 0.0, 1.78))
    right = ring.matrix_world @ a3.Vector((inner_radius, 0.0, 1.78))
    left_view = a3.world_to_camera_view(scene, camera, left)
    right_view = a3.world_to_camera_view(scene, camera, right)
    width = abs(right_view.x - left_view.x)
    return {
        "x": round(min(left_view.x, right_view.x), 5),
        "width": round(width, 5),
        "pixelWidth": round(width * resolution[0], 2),
    }


def main() -> None:
    args = a3.arguments()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    a3_metadata = json.loads(A3_METADATA.read_text(encoding="utf-8"))
    a3_source_hash = hashlib.sha256(A3_GENERATOR.read_bytes()).hexdigest()

    a3.reset_scene()
    mats = {key: a3.material("A3_Clay_" + {"deck": "Deck", "strata": "Strata", "near": "NearButtress", "mid": "MidMesa", "far": "FarFog", "courier": "Courier", "pursuer": "Pursuer", "ridge": "PursuerRidge", "ring": "Ring", "scar": "TideScar"}[key], tuple(value)) for key, value in MATERIAL_VALUES.items()}
    causeway, canyon, courier, pursuer, ring = (a3.root(name) for name in ROOT_NAMES[:5])
    route = a3.build_causeway(mats, causeway)
    canyon_stats = a3.build_canyon(mats, canyon)
    ring_stats, arch, support_left, support_right, inner_radius = build_ring_a4(mats, ring)
    a3.build_courier(mats, courier)
    build_pursuer_a4(mats, pursuer)
    scar = a3.build_tide_scar(mats["scar"])
    a3.build_lighting()

    scene = a3.bpy.context.scene
    # Portrait moves the projection left just enough to contain the pursuer while retaining A3's chase bands.
    portrait = a3.make_camera("A4_PortraitCamera", (0.0, -24.0, 16.0), (-2.5, 13.0, 3.0), 45.0)
    desktop = a3.make_camera("A4_DesktopCamera", (3.6, -24.0, 13.0), (0.2, 14.0, 2.8), 44.0)
    closeup = a3.make_camera("A4_CloseCamera", (0.0, -10.0, 7.5), (-3.0, 5.0, 2.0), 48.0)
    specs = {
        "portrait": (portrait, (540, 960), output / "a4-clay-portrait.png"),
        "desktop": (desktop, (960, 540), output / "a4-clay-desktop.png"),
        "closeup": (closeup, (640, 480), output / "a4-clay-closeup.png"),
    }
    for camera, resolution, path in specs.values():
        a3.render(scene, camera, path, resolution)

    a3.bpy.context.view_layer.update()
    projections: dict[str, dict[str, dict[str, float]]] = {}
    aperture_projections: dict[str, dict[str, float]] = {}
    for name, (camera, resolution, _) in specs.items():
        scene.camera = camera
        scene.render.resolution_x, scene.render.resolution_y = resolution
        projections[name] = {
            "courier": a3.projected_bbox(scene, camera, courier, resolution),
            "pursuer": a3.projected_bbox(scene, camera, pursuer, resolution),
            "ring": a3.projected_bbox(scene, camera, ring, resolution),
            "arch": a3.projected_bbox(scene, camera, arch, resolution),
            "supportLeft": a3.projected_bbox(scene, camera, support_left, resolution),
            "supportRight": a3.projected_bbox(scene, camera, support_right, resolution),
            "causeway": a3.projected_bbox(scene, camera, causeway, resolution),
            "tideScar": a3.projected_bbox(scene, camera, scar, resolution),
        }
        aperture_projections[name] = aperture_projection(scene, camera, ring, inner_radius, resolution)

    triangle_count = sum(max(0, len(poly.vertices) - 2) for mesh in a3.bpy.data.meshes for poly in mesh.polygons)
    tide_scar = {"editable": True, "baked": False, "rightThird": True, "widthToDeck": .016, "routeCoverage": .67, "clips": ["pursuer", "courier", "ring"]}
    metadata = {
        "schema": "temple-tr3-a4-clay-proof-v1",
        "generator": "generate_tide_scar_hero_a4.py",
        "derivedFrom": {"generator": "generate_tide_scar_hero_a3.py", "generatorSha256": a3_source_hash, "metadata": str(A3_METADATA), "metadataSha256": hashlib.sha256(A3_METADATA.read_bytes()).hexdigest()},
        "seed": a3.SEED,
        "blender": a3.bpy.app.version_string,
        "stage": "clay-only",
        "cleanRoom": "Deterministic local Blender Python geometry and inherited A3 clay values; no external images, models, or reference pixels read.",
        "semanticRoots": ROOT_NAMES,
        "triangles": triangle_count,
        "route": route,
        "canyon": canyon_stats,
        "materialValues": MATERIAL_VALUES,
        "tideScar": tide_scar,
        "ring": ring_stats,
        "permittedDifferences": ["camera framing", "pursuer transform/rig silhouette", "ring/support geometry"],
        "a3StructuralComparison": {
            "routeExact": route == a3_metadata["route"],
            "canyonExact": canyon_stats == a3_metadata["canyon"],
            "tideScarExact": tide_scar == a3_metadata["tideScar"],
            "moduleCount": route["moduleCount"],
            "canyonBands": canyon_stats["bandCount"],
        },
        "cameras": {name: {"location": list(camera.location), "fovDegrees": round(math.degrees(camera.data.angle), 3)} for name, (camera, _, _) in specs.items()},
        "projections": projections,
        "apertureProjections": aperture_projections,
        "gateFailures": a3.gate_failures(route, canyon_stats, ring_stats),
        "nonGoals": ["final materials", "GLB export", "KTX2", "runtime integration", "browser capture", "commit", "push", "QA"],
    }
    (output / "a4-clay-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "blender": metadata["blender"], "triangles": triangle_count, "gateFailures": metadata["gateFailures"], "a3StructuralComparison": metadata["a3StructuralComparison"]}, indent=2))
    if triangle_count > 45000 or metadata["gateFailures"] or not all(metadata["a3StructuralComparison"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
