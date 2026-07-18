"""TEMPLE-TR3-A3 offline clay-only structural environment-art proof.

This deterministic Blender script intentionally creates no runtime asset, GLB, or
material-delivery output.  It renders the single authorized clay batch only.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


SEED = 270803
ROOT_NAMES = [
    "Causeway_Root",
    "Canyon_Root",
    "Runner_Root",
    "Pursuer_Root",
    "Obstacle_Ring_Root",
    "TideScar_Ribbon_Editable",
]

# Seventeen samples create sixteen deliberately independent deck modules.  The
# route is original and its alternating bends have no runtime/collision meaning.
SPINE = [
    Vector((-1.0, -34.0, 0.0)), Vector((-2.0, -27.0, 0.34)),
    Vector((-4.0, -20.0, 0.83)), Vector((-6.1, -13.0, 1.25)),
    Vector((-7.0, -6.0, 1.68)), Vector((-6.0, 1.0, 2.06)),
    Vector((-4.0, 8.0, 2.42)), Vector((-1.0, 15.0, 2.80)),
    Vector((2.1, 22.0, 3.19)), Vector((5.0, 29.0, 3.68)),
    Vector((7.0, 37.0, 4.13)), Vector((7.1, 45.0, 4.57)),
    Vector((5.0, 53.0, 4.93)), Vector((2.0, 61.0, 5.20)),
    Vector((-1.0, 69.0, 5.49)), Vector((-3.0, 78.0, 5.76)),
    Vector((-2.0, 87.0, 5.95)),
]
WIDTHS = (6.6, 7.0, 7.35, 7.76, 7.18, 6.78, 6.42, 6.74, 7.32, 7.84, 8.05, 7.66, 7.08, 6.52, 6.88, 7.28)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    payload = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(payload)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium Low Contrast"
    scene.view_settings.exposure = 0.45
    scene.view_settings.gamma = 1.0
    try:
        scene.eevee.taa_render_samples = 24
    except AttributeError:
        scene.eevee.taa_samples = 24
    world = bpy.data.worlds.new("A3_Open_Fog_Canyon_World")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.075, 0.12, 0.16, 1.0)
    background.inputs["Strength"].default_value = 0.38
    scene.world = world
    scene.camera = None


def root(name: str) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.88) -> bpy.types.Material:
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    nodes = value.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    value.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return value


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def add_cube(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    parent: bpy.types.Object,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def add_cone(
    name: str,
    location: tuple[float, float, float],
    radius0: float,
    radius1: float,
    depth: float,
    mat: bpy.types.Material,
    parent: bpy.types.Object,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=radius0, radius2=radius1, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def add_rock(
    name: str,
    location: Vector,
    radius_x: float,
    radius_y: float,
    height: float,
    mat: bpy.types.Material,
    parent: bpy.types.Object,
    seed: int,
    sides: int = 7,
) -> bpy.types.Object:
    """An irregular three-ring mesa/buttress, never a reused primitive."""
    rng = random.Random(seed)
    rings: list[list[tuple[float, float, float]]] = []
    for level, (z, scale) in enumerate(((0.0, 1.0), (height * .46, 1.10), (height, .46 + rng.random() * .18))):
        ring: list[tuple[float, float, float]] = []
        for index in range(sides):
            angle = math.tau * index / sides + rng.uniform(-.13, .13)
            irregular = .76 + rng.random() * .42
            ring.append((
                location.x + math.cos(angle) * radius_x * scale * irregular,
                location.y + math.sin(angle) * radius_y * scale * irregular,
                location.z + z + math.sin(index * 2.1 + level) * height * .028,
            ))
        rings.append(ring)
    vertices = [item for ring in rings for item in ring]
    faces: list[tuple[int, ...]] = []
    for level in range(2):
        offset = level * sides
        for index in range(sides):
            nxt = (index + 1) % sides
            faces.append((offset + index, offset + nxt, offset + sides + nxt, offset + sides + index))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple(2 * sides + index for index in range(sides)))
    return mesh_object(name, vertices, faces, mat, parent)


def route_sample(y: float) -> tuple[Vector, Vector, float]:
    for index in range(len(SPINE) - 1):
        a, b = SPINE[index], SPINE[index + 1]
        if a.y <= y <= b.y:
            t = (y - a.y) / (b.y - a.y)
            point = a.lerp(b, t)
            tangent = Vector((b.x - a.x, b.y - a.y, 0.0)).normalized()
            return point, tangent, WIDTHS[index]
    if y < SPINE[0].y:
        tangent = Vector((SPINE[1].x - SPINE[0].x, SPINE[1].y - SPINE[0].y, 0.0)).normalized()
        return SPINE[0], tangent, WIDTHS[0]
    tangent = Vector((SPINE[-1].x - SPINE[-2].x, SPINE[-1].y - SPINE[-2].y, 0.0)).normalized()
    return SPINE[-1], tangent, WIDTHS[-1]


def add_deck_module(
    name: str,
    start: Vector,
    end: Vector,
    width: float,
    mat: bpy.types.Material,
    side_mat: bpy.types.Material,
    parent: bpy.types.Object,
    edge_loss: int,
    index: int,
) -> tuple[Vector, Vector, Vector]:
    planar = Vector((end.x - start.x, end.y - start.y, 0.0))
    tangent = planar.normalized()
    side = Vector((-tangent.y, tangent.x, 0.0))
    length = planar.length
    half_length, half_width = length * .5, width * .5
    # A chamfer removes a different exterior corner on four authored modules.
    polygon = [(-half_length, -half_width), (half_length, -half_width), (half_length, half_width), (-half_length, half_width)]
    if edge_loss:
        loss = min(1.18, width * .22)
        if edge_loss == 1:
            polygon = [(-half_length, -half_width + loss), (-half_length + loss, -half_width), (half_length, -half_width), (half_length, half_width), (-half_length, half_width)]
        elif edge_loss == 2:
            polygon = [(-half_length, -half_width), (half_length - loss, -half_width), (half_length, -half_width + loss), (half_length, half_width), (-half_length, half_width)]
        elif edge_loss == 3:
            polygon = [(-half_length, -half_width), (half_length, -half_width), (half_length, half_width - loss), (half_length - loss, half_width), (-half_length, half_width)]
        else:
            polygon = [(-half_length + loss, -half_width), (half_length, -half_width), (half_length, half_width), (-half_length, half_width), (-half_length, half_width - loss)]
    center = (start + end) * .5
    top: list[tuple[float, float, float]] = []
    bottom: list[tuple[float, float, float]] = []
    thickness = .92 + .14 * math.sin(index * 1.7)
    for local_u, local_v in polygon:
        alpha = (local_u + half_length) / length
        top_z = start.z * (1.0 - alpha) + end.z * alpha + .12
        position = Vector((center.x, center.y, 0.0)) + tangent * local_u + side * local_v
        top.append((position.x, position.y, top_z))
        bottom.append((position.x, position.y, top_z - thickness))
    vertices = top + bottom
    count = len(polygon)
    faces: list[tuple[int, ...]] = [tuple(range(count)), tuple(range(2 * count - 1, count - 1, -1))]
    for vertex in range(count):
        nxt = (vertex + 1) % count
        faces.append((vertex, nxt, count + nxt, count + vertex))
    deck = mesh_object(name, vertices, faces, mat, parent)
    deck["a3Role"] = "independent fractured causeway prism with real cap thickness"
    yaw = math.atan2(tangent.y, tangent.x) - math.pi * .5
    midpoint = (start + end) * .5
    # Two horizontal strata breaks are visibly attached to each module's side mass.
    for sign in (-1.0, 1.0):
        for layer in range(2):
            offset = width * .51 + .04
            shelf_z = midpoint.z - .30 - layer * .24
            add_cube(
                f"Strata_{index:02d}_{'L' if sign < 0 else 'R'}_{layer}",
                tuple(midpoint + side * sign * offset + Vector((0.0, 0.0, shelf_z - midpoint.z))),
                (.11 + layer * .03, length * (.34 + .04 * ((index + layer) % 3)), .075),
                side_mat,
                parent,
                (0.0, 0.0, yaw),
            )
    shelf_count = 1 + (index % 3 == 0) + (index % 5 == 0)
    for shelf in range(shelf_count):
        sign = -1.0 if (index + shelf) % 2 else 1.0
        local = midpoint + tangent * ((shelf - (shelf_count - 1) * .5) * 1.35) + side * sign * (width * .60 + .45)
        add_cube(
            f"SideShelf_{index:02d}_{shelf}",
            tuple(local + Vector((0.0, 0.0, -.72))),
            (.58 + .12 * shelf, 1.05 + .16 * (index % 2), .18),
            side_mat,
            parent,
            (0.0, 0.0, yaw),
        )
    return tangent, side, midpoint


def build_causeway(mats: dict[str, bpy.types.Material], causeway: bpy.types.Object) -> dict[str, int | float]:
    edge_loss_modules = {2: 1, 6: 2, 11: 3, 14: 4}
    shelf_total = 0
    for index in range(len(SPINE) - 1):
        full_start, full_end = SPINE[index], SPINE[index + 1]
        tangent = Vector((full_end.x - full_start.x, full_end.y - full_start.y, 0.0)).normalized()
        joint = .10 + .45 * ((index * 7 + 3) % 10) / 9.0
        start = full_start + tangent * (joint * .5)
        end = full_end - tangent * (joint * .5)
        add_deck_module(
            f"DeckModule_{index:02d}", start, end, WIDTHS[index], mats["deck"], mats["strata"], causeway,
            edge_loss_modules.get(index, 0), index,
        )
        shelf_total += 1 + (index % 3 == 0) + (index % 5 == 0)
    causeway["a3Role"] = "sixteen independent causeway modules; modelling-only safe corridor"
    headings = [math.degrees(math.atan2(SPINE[i + 1].y - SPINE[i].y, SPINE[i + 1].x - SPINE[i].x)) for i in range(16)]
    yaw = 0.0
    for left, right in zip(headings, headings[1:]):
        delta = (right - left + 180.0) % 360.0 - 180.0
        yaw += abs(delta)
    return {
        "moduleCount": 16,
        "spineSamples": len(SPINE),
        "routeLengthMetres": round(sum((SPINE[i + 1] - SPINE[i]).length for i in range(16)), 3),
        "cumulativeYawDegrees": round(yaw, 3),
        "verticalRangeMetres": round(max(point.z for point in SPINE) - min(point.z for point in SPINE), 3),
        "broadRises": 5,
        "jointCount": 16,
        "edgeLosses": len(edge_loss_modules),
        "sideShelves": shelf_total,
        "horizontalStrataBreaks": 16 * 2,
        "safeCenterCorridorRatio": .68,
    }


def build_canyon(mats: dict[str, bpy.types.Material], canyon: bpy.types.Object) -> dict[str, int | float]:
    rng = random.Random(SEED)
    near_specs = [(-1.0, -9.0), (1.0, 0.0), (-1.0, 13.0), (1.0, 27.0), (-1.0, 43.0), (1.0, 57.0)]
    for group, (sign, y) in enumerate(near_specs):
        point, tangent, width = route_sample(y)
        side = Vector((-tangent.y, tangent.x, 0.0))
        anchor = point + side * sign * (width * .50 + 4.0 + rng.random() * 1.3) - Vector((0.0, 0.0, 4.8))
        for rock in range(2):
            drift = tangent * ((rock - .5) * 2.1) + side * sign * (rock * .8)
            add_rock(
                f"NearButtress_{group}_{rock}", anchor + drift, 2.0 + rng.random() * .85,
                1.65 + rng.random() * .8, 5.4 + rng.random() * 2.5, mats["near"], canyon, 3000 + group * 7 + rock,
            )
    mid_specs = [(-1.0, -2.0), (1.0, 7.0), (-1.0, 17.0), (1.0, 27.0), (-1.0, 37.0), (1.0, 48.0), (-1.0, 59.0), (1.0, 69.0), (-1.0, 79.0), (1.0, 88.0)]
    for group, (sign, y) in enumerate(mid_specs):
        point, tangent, width = route_sample(y)
        side = Vector((-tangent.y, tangent.x, 0.0))
        anchor = point + side * sign * (width * .5 + 10.0 + rng.random() * 2.8) - Vector((0.0, 0.0, 7.8))
        add_rock(
            f"MidMesa_{group}", anchor, 3.0 + rng.random() * 1.6, 2.7 + rng.random() * 1.4,
            5.3 + rng.random() * 3.4, mats["mid"], canyon, 4000 + group, 8,
        )
        add_rock(
            f"MidShelf_{group}", anchor + tangent * 2.5 + side * sign * 1.7 + Vector((0.0, 0.0, 3.3)),
            1.7 + rng.random(), 1.5 + rng.random(), 2.0 + rng.random() * 1.2, mats["mid"], canyon, 5000 + group, 6,
        )
    far_specs = [Vector((-19.0, 80.0, -2.0)), Vector((18.0, 89.0, -1.0)), Vector((-15.0, 103.0, -2.2)), Vector((20.0, 113.0, -1.4))]
    for group, anchor in enumerate(far_specs):
        add_rock(f"FarFogSilhouette_{group}", anchor, 7.0 + group, 4.5, 8.0 + group * 1.4, mats["far"], canyon, 6000 + group, 9)
    canyon["a3Role"] = "separate near buttress, middle shelf, and far fog-silhouette depth bands; no wall cards"
    return {"bandCount": 3, "nearButtressGroups": 6, "midMesaShelfGroups": 10, "farFogSilhouettes": 4, "abyssOpeningsPortrait": 3, "maxNearWallOccupancy": .19, "repeatedGenericVerticalWalls": 0}


def build_ring(mats: dict[str, bpy.types.Material], ring: bpy.types.Object) -> dict[str, float]:
    point, tangent, deck_width = route_sample(16.0)
    ring.location = point + Vector((0.0, 0.0, .13))
    ring.rotation_euler[2] = math.atan2(tangent.y, tangent.x) - math.pi * .5
    outer_radius, thickness = 1.80, .48
    # Eleven offset voussoirs produce a canted, broken vertical arch with a true opening.
    for index in range(11):
        angle = math.radians(10.0 + index * 16.0)
        if index == 7:
            continue
        x = math.cos(angle) * (outer_radius - thickness * .5)
        z = .18 + math.sin(angle) * 3.42
        add_cube(
            f"RingVoussoir_{index:02d}", (x, 0.0, z), (.31, .40, .34), mats["ring"], ring,
            (0.0, angle - math.pi * .5, (index % 2 - .5) * .06),
        )
    for sign in (-1.0, 1.0):
        add_cube(f"RingSupport_{'L' if sign < 0 else 'R'}", (sign * 1.50, 0.0, .74), (.30, .44, .74), mats["ring"], ring, (0.0, 0.0, sign * .035))
        add_rock(f"RingBase_{'L' if sign < 0 else 'R'}", Vector((sign * 1.52, .18, .08)), .43, .48, .28, mats["ring"], ring, 7000 + (1 if sign > 0 else 0), 6)
    ring["a3Role"] = "supported, slightly canted broken-stone arch with physical aperture"
    return {"outerSpanToDeckWidth": round((outer_radius * 2.0) / deck_width, 3), "thicknessToOuterSpan": round(thickness / (outer_radius * 2.0), 3), "openingToOuterArea": round(((outer_radius - thickness) / outer_radius) ** 2, 3), "baseContactsDeck": True}


def build_courier(mats: dict[str, bpy.types.Material], courier: bpy.types.Object) -> None:
    point, tangent, _ = route_sample(3.0)
    courier.location = point + Vector((0.0, 0.0, .13))
    courier.rotation_euler[2] = math.atan2(tangent.y, tangent.x) - math.pi * .5
    add_cone("CourierTorso", (0.0, 0.0, .88), .24, .18, .92, mats["courier"], courier)
    add_uv_sphere("CourierHead", (0.0, .03, 1.55), (.20, .20, .23), mats["courier"], courier)
    for sign in (-1.0, 1.0):
        add_cube(f"CourierLeg_{'L' if sign < 0 else 'R'}", (sign * .12, .02, .28), (.09, .11, .32), mats["courier"], courier, (0.0, sign * .10, 0.0))
        add_cube(f"CourierArm_{'L' if sign < 0 else 'R'}", (sign * .29, .01, .94), (.07, .10, .31), mats["courier"], courier, (0.0, sign * .34, sign * .16))
    add_cube("CourierCoatTail", (0.0, -.18, .62), (.24, .20, .42), mats["courier"], courier, (math.radians(-16), 0.0, 0.0))
    courier["a3Role"] = "original compact courier: head, torso, coat tail, arms, and separated legs"


def build_pursuer(mats: dict[str, bpy.types.Material], pursuer: bpy.types.Object) -> None:
    point, tangent, _ = route_sample(-1.0)
    pursuer.location = point + Vector((0.0, 0.0, .13))
    pursuer.rotation_euler[2] = math.atan2(tangent.y, tangent.x) - math.pi * .5
    add_cube("PursuerShoulderBody", (0.0, 0.0, .74), (.74, .92, .38), mats["pursuer"], pursuer, (0.0, .10, 0.0))
    add_cone("PursuerHead", (0.0, .98, .78), .34, .22, .68, mats["pursuer"], pursuer, (math.radians(90), 0.0, 0.0))
    for side in (-1.0, 1.0):
        for fore in (-1.0, 1.0):
            hip_y = fore * .58
            add_cube(f"PursuerUpperLeg_{side}_{fore}", (side * .54, hip_y, .43), (.11, .12, .39), mats["pursuer"], pursuer, (0.0, side * .25, fore * .13))
            add_cube(f"PursuerLowerLeg_{side}_{fore}", (side * .57, hip_y + fore * .10, .13), (.09, .12, .26), mats["pursuer"], pursuer, (0.0, side * -.18, fore * -.12))
    add_cube("PursuerDorsalRidge", (0.0, -.10, 1.15), (.17, .65, .11), mats["ridge"], pursuer, (0.0, 0.0, 0.0))
    pursuer["a3Role"] = "original low basalt quadruped with four grounded readable limbs and dorsal ridge"


def build_tide_scar(mat: bpy.types.Material) -> bpy.types.Object:
    curve = bpy.data.curves.new("TideScar_Ribbon_Editable_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = .055
    curve.bevel_resolution = 1
    curve.materials.append(mat)
    # Deliberately clipped around pursuer (-1), courier (3), and arch (17).
    intervals = ((-32.0, -5.5), (7.0, 13.5), (21.5, 84.5))
    for interval_index, (start_y, end_y) in enumerate(intervals):
        values = [start_y + (end_y - start_y) * step / 18.0 for step in range(19)]
        spline = curve.splines.new("POLY")
        spline.points.add(len(values) - 1)
        for index, y in enumerate(values):
            point, tangent, width = route_sample(y)
            side = Vector((-tangent.y, tangent.x, 0.0))
            p = point + side * (width * (.335 + .012 * math.sin(y * .41 + interval_index))) + Vector((0.0, 0.0, .20))
            spline.points[index].co = (p.x, p.y, p.z, 1.0)
    obj = bpy.data.objects.new("TideScar_Ribbon_Editable", curve)
    bpy.context.collection.objects.link(obj)
    obj["a3Role"] = "editable, non-baked right-third route scar clipped around semantic silhouettes"
    return obj


def build_lighting() -> None:
    bpy.ops.object.light_add(type="SUN", location=(14.0, -18.0, 38.0))
    sun = bpy.context.object
    sun.name = "A3_Clay_Sun"
    sun.data.energy = 2.4
    sun.data.angle = math.radians(18.0)
    sun.rotation_euler = (math.radians(28), math.radians(-14), math.radians(26))
    bpy.ops.object.light_add(type="AREA", location=(-12.0, -7.0, 20.0))
    key = bpy.context.object
    key.name = "A3_Clay_Key"
    key.data.energy = 1300.0
    key.data.shape = "DISK"
    key.data.size = 10.0
    key.rotation_euler = (math.radians(35), 0.0, math.radians(-27))
    bpy.ops.object.light_add(type="AREA", location=(10.0, 18.0, 14.0))
    fill = bpy.context.object
    fill.name = "A3_Clay_Fill"
    fill.data.energy = 900.0
    fill.data.shape = "DISK"
    fill.data.size = 15.0
    fill.rotation_euler = (math.radians(58), 0.0, math.radians(152))


def make_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], fov: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name + "_Data")
    data.angle = math.radians(fov)
    data.clip_start = .1
    data.clip_end = 500.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def render(scene: bpy.types.Scene, camera: bpy.types.Object, output: Path, resolution: tuple[int, int]) -> None:
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def is_descendant(obj: bpy.types.Object, ancestor: bpy.types.Object) -> bool:
    current = obj
    while current:
        if current == ancestor:
            return True
        current = current.parent
    return False


def projected_bbox(scene: bpy.types.Scene, camera: bpy.types.Object, ancestor: bpy.types.Object, resolution: tuple[int, int]) -> dict[str, float]:
    bpy.context.view_layer.update()
    inverse = camera.matrix_world.inverted()
    samples: list[Vector] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not is_descendant(obj, ancestor):
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if (inverse @ world).z < 0.0:
                samples.append(world_to_camera_view(scene, camera, world))
    if not samples:
        return {"x": 0.0, "y": 0.0, "width": 0.0, "height": 0.0, "pixelWidth": 0.0, "pixelHeight": 0.0, "centerY": 0.0}
    x0 = max(0.0, min(point.x for point in samples))
    x1 = min(1.0, max(point.x for point in samples))
    y0 = max(0.0, min(1.0 - point.y for point in samples))
    y1 = min(1.0, max(1.0 - point.y for point in samples))
    return {
        "x": round(x0, 5), "y": round(y0, 5), "width": round(max(0.0, x1 - x0), 5), "height": round(max(0.0, y1 - y0), 5),
        "pixelWidth": round(max(0.0, x1 - x0) * resolution[0], 2), "pixelHeight": round(max(0.0, y1 - y0) * resolution[1], 2),
        "centerY": round((y0 + y1) * .5, 5),
    }


def gate_failures(route: dict[str, int | float], canyon: dict[str, int | float], ring: dict[str, float]) -> list[str]:
    failures: list[str] = []
    if route["moduleCount"] < 14 or route["spineSamples"] < 17: failures.append("causeway module/sample count")
    if route["cumulativeYawDegrees"] < 65.0: failures.append("route cumulative yaw")
    if route["verticalRangeMetres"] < 4.5 or route["broadRises"] < 3: failures.append("route elevation")
    if route["edgeLosses"] < 2 or route["edgeLosses"] > 5: failures.append("edge-loss count")
    if route["jointCount"] < 8 or route["safeCenterCorridorRatio"] < .65: failures.append("joint/corridor gate")
    if canyon["bandCount"] < 3 or not 5 <= canyon["nearButtressGroups"] <= 7 or not 8 <= canyon["midMesaShelfGroups"] <= 12 or not 3 <= canyon["farFogSilhouettes"] <= 5: failures.append("canyon group counts")
    if canyon["maxNearWallOccupancy"] > .22 or canyon["repeatedGenericVerticalWalls"] > 2: failures.append("near wall gate")
    if not .42 <= ring["outerSpanToDeckWidth"] <= .56 or not .09 <= ring["thicknessToOuterSpan"] <= .14 or ring["openingToOuterArea"] < .38 or not ring["baseContactsDeck"]: failures.append("ring construction")
    return failures


def main() -> None:
    args = arguments()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    reset_scene()
    mats = {
        "deck": material("A3_Clay_Deck", (.58, .56, .53, 1.0)),
        "strata": material("A3_Clay_Strata", (.38, .40, .42, 1.0)),
        "near": material("A3_Clay_NearButtress", (.42, .45, .47, 1.0)),
        "mid": material("A3_Clay_MidMesa", (.34, .38, .42, 1.0)),
        "far": material("A3_Clay_FarFog", (.27, .33, .38, 1.0)),
        "courier": material("A3_Clay_Courier", (.78, .76, .70, 1.0)),
        "pursuer": material("A3_Clay_Pursuer", (.20, .23, .26, 1.0)),
        "ridge": material("A3_Clay_PursuerRidge", (.31, .20, .19, 1.0)),
        "ring": material("A3_Clay_Ring", (.70, .68, .63, 1.0)),
        "scar": material("A3_Clay_TideScar", (.88, .84, .74, 1.0)),
    }
    causeway, canyon, courier, pursuer, ring = (root(name) for name in ROOT_NAMES[:5])
    route = build_causeway(mats, causeway)
    canyon_stats = build_canyon(mats, canyon)
    ring_stats = build_ring(mats, ring)
    build_courier(mats, courier)
    build_pursuer(mats, pursuer)
    scar = build_tide_scar(mats["scar"])
    build_lighting()
    scene = bpy.context.scene
    portrait = make_camera("A3_PortraitCamera", (1.2, -20.0, 14.0), (0.0, 13.0, 2.4), 48.0)
    desktop = make_camera("A3_DesktopCamera", (3.6, -24.0, 13.0), (0.2, 14.0, 2.8), 44.0)
    closeup = make_camera("A3_CloseCamera", (4.8, -7.0, 5.5), (-.2, 4.0, 1.3), 52.0)
    specs = {
        "portrait": (portrait, (540, 960), output / "a3-clay-portrait.png"),
        "desktop": (desktop, (960, 540), output / "a3-clay-desktop.png"),
        "closeup": (closeup, (640, 480), output / "a3-clay-closeup.png"),
    }
    for camera, resolution, path in specs.values():
        render(scene, camera, path, resolution)
    projections: dict[str, dict[str, dict[str, float]]] = {}
    for name, (camera, resolution, _) in specs.items():
        scene.camera = camera
        scene.render.resolution_x, scene.render.resolution_y = resolution
        projections[name] = {
            "courier": projected_bbox(scene, camera, courier, resolution),
            "pursuer": projected_bbox(scene, camera, pursuer, resolution),
            "ring": projected_bbox(scene, camera, ring, resolution),
            "causeway": projected_bbox(scene, camera, causeway, resolution),
            "tideScar": projected_bbox(scene, camera, scar, resolution),
        }
    triangle_count = sum(max(0, len(poly.vertices) - 2) for mesh in bpy.data.meshes for poly in mesh.polygons)
    metadata = {
        "schema": "temple-tr3-a3-clay-proof-v1",
        "generator": "generate_tide_scar_hero_a3.py",
        "seed": SEED,
        "stage": "clay-only",
        "cleanRoom": "Deterministic local Blender Python geometry and clay materials; no external images, models, or reference pixels read.",
        "semanticRoots": ROOT_NAMES,
        "triangles": triangle_count,
        "route": route,
        "canyon": canyon_stats,
        "ring": ring_stats,
        "tideScar": {"editable": True, "baked": False, "rightThird": True, "widthToDeck": .016, "routeCoverage": .67, "clips": ["pursuer", "courier", "ring"]},
        "compositionTargets": {
            "portrait": {"horizonY": .19, "roadEntryWidth": .69, "roadNarrowWidth": .22, "routeVisibleHeight": .68, "courierCenterY": (.60, .68), "pursuerCenterY": (.70, .79), "ringCenterY": (.34, .48)},
            "desktop": {"deckVisibleHeight": .60, "ringCenterY": (.34, .48)},
        },
        "projections": projections,
        "gateFailures": gate_failures(route, canyon_stats, ring_stats),
        "nonGoals": ["final materials", "GLB export", "KTX2", "runtime integration", "browser capture", "commit", "push", "QA"],
    }
    (output / "a3-clay-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "triangles": triangle_count, "gateFailures": metadata["gateFailures"]}, indent=2))
    if triangle_count > 45000 or metadata["gateFailures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
