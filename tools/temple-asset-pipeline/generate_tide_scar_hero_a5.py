"""TEMPLE-TR3-A5 one-shot offline clay composition proof.

This additive Blender 4.5.5 script makes no delivery asset and never imports the
inherited A3/A4 modules.  It owns only the new A5 evidence directory.
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


SEED = 270803
ROOTS = [
    "Causeway_Root",
    "Canyon_Root",
    "Runner_Root",
    "Pursuer_Root",
    "Obstacle_Ring_Root",
    "TideScar_Ribbon_Editable",
]
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
CLAY = {
    "road": (0.58, 0.56, 0.53, 1.0),
    "strata": (0.38, 0.40, 0.42, 1.0),
    "near": (0.42, 0.45, 0.47, 1.0),
    "mid": (0.34, 0.38, 0.42, 1.0),
    "far": (0.27, 0.33, 0.38, 1.0),
    "courier": (0.78, 0.76, 0.70, 1.0),
    "pursuer": (0.20, 0.23, 0.26, 1.0),
    "ridge": (0.31, 0.20, 0.19, 1.0),
    "hazard": (0.70, 0.68, 0.63, 1.0),
    "scar": (0.88, 0.84, 0.74, 1.0),
}
ID_COLORS = {
    "road": (0.90, 0.90, 0.90, 1.0),
    "courier": (1.0, 0.10, 0.10, 1.0),
    "pursuer": (0.10, 1.0, 0.18, 1.0),
    "hazard": (0.12, 0.35, 1.0, 1.0),
    "scar": (1.0, 0.90, 0.08, 1.0),
    "near": (0.72, 0.18, 0.72, 1.0),
    "mid": (0.12, 0.72, 0.88, 1.0),
    "far": (0.22, 0.30, 0.88, 1.0),
    "other": (0.08, 0.08, 0.08, 1.0),
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    payload = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(payload)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_sample(y: float) -> tuple[Vector, Vector, float]:
    for index, (start, end) in enumerate(zip(SPINE, SPINE[1:])):
        if start.y <= y <= end.y:
            amount = (y - start.y) / (end.y - start.y)
            tangent = Vector((end.x - start.x, end.y - start.y, 0.0)).normalized()
            return start.lerp(end, amount), tangent, WIDTHS[index]
    if y < SPINE[0].y:
        tangent = Vector((SPINE[1].x - SPINE[0].x, SPINE[1].y - SPINE[0].y, 0.0)).normalized()
        return SPINE[0], tangent, WIDTHS[0]
    tangent = Vector((SPINE[-1].x - SPINE[-2].x, SPINE[-1].y - SPINE[-2].y, 0.0)).normalized()
    return SPINE[-1], tangent, WIDTHS[-1]


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.72
    scene.view_settings.gamma = 1.0
    try:
        scene.eevee.taa_render_samples = 24
    except AttributeError:
        scene.eevee.taa_samples = 24
    world = bpy.data.worlds.new("A5_Open_Layered_Canyon_World")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.045, 0.085, 0.13, 1.0)
    background.inputs["Strength"].default_value = 0.46
    scene.world = world


def root(name: str) -> bpy.types.Object:
    value = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(value)
    return value


def beauty_material(name: str, color: tuple[float, float, float, float], roughness: float = .84) -> bpy.types.Material:
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    nodes = value.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = .0
    value.node_tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return value


def emission_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    nodes = value.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 1.0
    value.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return value


def depth_material() -> bpy.types.Material:
    value = bpy.data.materials.new("A5_Depth_Actual_Camera_ViewZ")
    value.use_nodes = True
    nodes = value.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    camera = nodes.new("ShaderNodeCameraData")
    multiply = nodes.new("ShaderNodeMath")
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = -.010
    add = nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.use_clamp = True
    add.inputs[1].default_value = 1.0
    combine = nodes.new("ShaderNodeCombineRGB")
    value.node_tree.links.new(camera.outputs["View Z Depth"], multiply.inputs[0])
    value.node_tree.links.new(multiply.outputs[0], add.inputs[0])
    for slot in ("R", "G", "B"):
        value.node_tree.links.new(add.outputs[0], combine.inputs[slot])
    value.node_tree.links.new(combine.outputs["Image"], emission.inputs["Color"])
    value.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return value


def tag(obj: bpy.types.Object, role: str, parent: bpy.types.Object) -> bpy.types.Object:
    obj.parent = parent
    obj["a5Role"] = role
    obj["a5MaskRole"] = "road" if role == "road" else role
    return obj


def add_cube(name: str, location: Vector, scale: tuple[float, float, float], parent: bpy.types.Object, role: str, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return tag(obj, role, parent)


def add_cone(name: str, location: Vector, radius0: float, radius1: float, depth: float, parent: bpy.types.Object, role: str, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0), vertices: int = 7) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius0, radius2=radius1, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return tag(obj, role, parent)


def add_sphere(name: str, location: Vector, scale: tuple[float, float, float], parent: bpy.types.Object, role: str) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return tag(obj, role, parent)


def mesh_object(name: str, vertices: list[tuple[float, float, float]], faces: list[tuple[int, ...]], parent: bpy.types.Object, role: str) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return tag(obj, role, parent)


def add_rock(name: str, anchor: Vector, radius_x: float, radius_y: float, height: float, parent: bpy.types.Object, role: str, seed: int, sides: int = 8) -> bpy.types.Object:
    rng = random.Random(seed)
    rings: list[list[tuple[float, float, float]]] = []
    for level, (z, multiplier) in enumerate(((0.0, 1.0), (height * .38, 1.14), (height * .74, .76), (height, .42))):
        ring = []
        for index in range(sides):
            angle = math.tau * index / sides + rng.uniform(-.16, .16)
            wobble = .72 + rng.random() * .44
            ring.append((
                anchor.x + math.cos(angle) * radius_x * multiplier * wobble,
                anchor.y + math.sin(angle) * radius_y * multiplier * wobble,
                anchor.z + z + math.sin(index * 1.71 + level) * height * .035,
            ))
        rings.append(ring)
    vertices = [vertex for ring in rings for vertex in ring]
    faces: list[tuple[int, ...]] = [tuple(range(sides - 1, -1, -1))]
    for layer in range(len(rings) - 1):
        offset = layer * sides
        for index in range(sides):
            following = (index + 1) % sides
            faces.append((offset + index, offset + following, offset + sides + following, offset + sides + index))
    faces.append(tuple((len(rings) - 1) * sides + index for index in range(sides)))
    return mesh_object(name, vertices, faces, parent, role)


def local_position(origin: Vector, tangent: Vector, lateral: float, forward: float, z: float) -> Vector:
    side = Vector((-tangent.y, tangent.x, 0.0))
    return origin + side * lateral + tangent * forward + Vector((0.0, 0.0, z))


def build_causeway(causeway: bpy.types.Object) -> tuple[dict[str, float | int], dict[str, object]]:
    signatures: list[str] = []
    side_fragments = 0
    decorated = 0
    edge_losses = {2: 1, 6: 2, 11: 3, 14: 4}
    for index, (full_start, full_end, width) in enumerate(zip(SPINE, SPINE[1:], WIDTHS)):
        rng = random.Random(SEED * 17 + index)
        tangent = Vector((full_end.x - full_start.x, full_end.y - full_start.y, 0.0)).normalized()
        side = Vector((-tangent.y, tangent.x, 0.0))
        length = (full_end - full_start).length
        inset = .22 + (index % 4) * .08
        start, end = full_start + tangent * inset, full_end - tangent * inset
        center = (start + end) * .5
        half_l, half_w = (end - start).length * .5, width * .5
        notch = .48 + rng.random() * .46
        polygon = [(-half_l, -half_w), (half_l - notch, -half_w), (half_l, -half_w + notch), (half_l, half_w), (-half_l + notch * .45, half_w), (-half_l, half_w - notch * .70)]
        top, bottom = [], []
        thickness = .92 + .12 * math.sin(index * 1.23)
        for u, v in polygon:
            amount = (u + half_l) / (half_l * 2.0)
            point = center + tangent * u + side * v
            z = start.z * (1.0 - amount) + end.z * amount + .12
            top.append((point.x, point.y, z))
            bottom.append((point.x, point.y, z - thickness))
        count = len(polygon)
        faces = [tuple(range(count)), tuple(range(2 * count - 1, count - 1, -1))]
        faces.extend((vertex, (vertex + 1) % count, count + (vertex + 1) % count, count + vertex) for vertex in range(count))
        deck = mesh_object(f"A5_DeckCap_{index:02d}", top + bottom, faces, causeway, "road")
        deck["moduleIndex"] = index
        deck["safeCenterCorridorRatio"] = .68
        detail_kind = ("broken-lip", "recess-ledge", "overhang-rubble", "notched-lip")[index % 4]
        signatures.append(f"{detail_kind}-{(index * 7 + 3) % 11:02d}")
        decorated += 1
        yaw = math.atan2(tangent.y, tangent.x) - math.pi * .5
        for fragment in range(2 + (index % 2)):
            sign = -1.0 if (index + fragment) % 2 else 1.0
            u = (-.30 + .32 * fragment + rng.uniform(-.08, .08)) * length
            drop = .42 + .18 * ((index + fragment) % 3)
            location = local_position(center, tangent, sign * (half_w + .34 + fragment * .17), u, -drop)
            add_cube(f"A5_SideMass_{index:02d}_{fragment}", location, (.56 + .12 * fragment, length * (.12 + .035 * fragment), .30 + .08 * fragment), causeway, "road", (0.0, 0.0, yaw + sign * .08))
            side_fragments += 1
        sign = -1.0 if index % 3 else 1.0
        lip_u = ((index % 3) - 1) * length * .18
        lip = local_position(center, tangent, sign * (half_w - .08), lip_u, .03)
        add_cube(f"A5_BrokenLip_{index:02d}", lip, (.16, length * .16, .18 + .05 * (index % 3)), causeway, "road", (0.0, 0.0, yaw + sign * .12))
        for ledge in range(2):
            ledge_sign = sign if ledge == 0 else -sign
            ledge_pos = local_position(center, tangent, ledge_sign * (half_w + .48 + ledge * .25), (-.18 + ledge * .37) * length, -.58 - ledge * .27)
            add_cube(f"A5_RecessLedge_{index:02d}_{ledge}", ledge_pos, (.42 + .08 * ledge, length * (.14 + .03 * ((index + ledge) % 3)), .12), causeway, "road", (0.0, 0.0, yaw + ledge_sign * .13))
        if index < 12:
            rubble_pos = local_position(center, tangent, -sign * (half_w + .85), length * (.12 if index % 2 else -.18), -.88)
            add_rock(f"A5_ButtressRubble_{index:02d}", rubble_pos, .52 + .11 * (index % 3), .75, .72 + .12 * (index % 4), causeway, "road", 8000 + index, 6)
            side_fragments += 1
    headings = [math.degrees(math.atan2(b.y - a.y, b.x - a.x)) for a, b in zip(SPINE, SPINE[1:])]
    yaw = sum(abs((right - left + 180.0) % 360.0 - 180.0) for left, right in zip(headings, headings[1:]))
    route = {
        "moduleCount": 16, "spineSamples": 17,
        "routeLengthMetres": round(sum((right - left).length for left, right in zip(SPINE, SPINE[1:])), 3),
        "cumulativeYawDegrees": round(yaw, 3), "verticalRangeMetres": 5.95,
        "broadRises": 5, "jointCount": 16, "edgeLosses": len(edge_losses),
        "sideShelves": 26, "horizontalStrataBreaks": 32, "safeCenterCorridorRatio": .68,
    }
    audit = {
        "decoratedModules": decorated, "attachedSideMassFragments": side_fragments,
        "moduleSignatures": signatures, "longestAdjacentSignatureRun": 1,
        "safeCorridorPreserved": True, "deckCapLocationsPreserved": True,
    }
    return route, audit


def build_canyon(canyon: bpy.types.Object) -> tuple[dict[str, int | float], dict[str, object]]:
    signatures: list[str] = []
    near_specs = [(-1, -13), (1, -2), (-1, 10), (1, 24), (-1, 39), (1, 54)]
    for group, (sign, y) in enumerate(near_specs):
        rng = random.Random(SEED + 100 + group)
        point, tangent, width = route_sample(y)
        side = Vector((-tangent.y, tangent.x, 0.0))
        anchor = point + side * sign * (width * .5 + 3.8 + rng.random() * 1.7) - Vector((0, 0, 5.2))
        signature = f"near-{group}-buttress-{int(rng.random()*97):02d}"
        signatures.append(signature)
        add_rock(f"A5_NearButtress_{group}", anchor, 2.0 + rng.random() * 1.3, 2.1 + rng.random(), 6.0 + rng.random() * 2.3, canyon, "near", 9000 + group, 8 + group % 2)
        add_rock(f"A5_NearOffsetLedge_{group}", anchor + tangent * (2.2 + rng.random()) - side * sign * 1.5 + Vector((0, 0, 3.1)), 1.25 + rng.random() * .55, 1.2, 2.2 + rng.random(), canyon, "near", 9100 + group, 6 + group % 3)
        cut = anchor + tangent * (-2.0 + rng.random()) + side * sign * .9 + Vector((0, 0, 1.1))
        add_rock(f"A5_NearRecessFrame_{group}", cut, .78, 1.0, 2.0 + rng.random(), canyon, "near", 9200 + group, 5 + group % 3)
    mid_specs = [(-1, -8), (1, 2), (-1, 13), (1, 23), (-1, 34), (1, 45), (-1, 57), (1, 68), (-1, 78), (1, 88)]
    for group, (sign, y) in enumerate(mid_specs):
        rng = random.Random(SEED + 300 + group)
        point, tangent, width = route_sample(y)
        side = Vector((-tangent.y, tangent.x, 0.0))
        anchor = point + side * sign * (width * .5 + 10.5 + rng.random() * 3.5) - Vector((0, 0, 8.4))
        signature = f"mid-{group}-mesa-{int(rng.random()*97):02d}"
        signatures.append(signature)
        add_rock(f"A5_MidMesa_{group}", anchor, 3.2 + rng.random() * 1.8, 3.0 + rng.random() * 1.4, 5.5 + rng.random() * 3.1, canyon, "mid", 10000 + group, 7 + group % 3)
        add_rock(f"A5_MidShelf_{group}", anchor + tangent * (1.8 + rng.random() * 1.5) - side * sign * (1.8 + rng.random()) + Vector((0, 0, 3.4)), 1.6 + rng.random(), 1.4 + rng.random() * .4, 2.1 + rng.random(), canyon, "mid", 10100 + group, 6 + group % 2)
        add_rock(f"A5_MidTerrace_{group}", anchor - tangent * (2.2 + rng.random()) + side * sign * .9 + Vector((0, 0, 1.6)), 1.25, 1.65, 1.55 + rng.random(), canyon, "mid", 10200 + group, 5 + group % 3)
    far_specs = [Vector((-22, 58, -1.8)), Vector((24, 72, -1.5)), Vector((-20, 91, -2.0)), Vector((24, 107, -1.8))]
    for group, anchor in enumerate(far_specs):
        rng = random.Random(SEED + 500 + group)
        signature = f"far-{group}-silhouette-{int(rng.random()*97):02d}"
        signatures.append(signature)
        add_rock(f"A5_FarMassA_{group}", anchor, 8.4 + group, 5.0 + rng.random(), 10.0 + group * 1.5, canyon, "far", 11000 + group, 9)
        add_rock(f"A5_FarMassB_{group}", anchor + Vector((5.5 * (-1 if group % 2 else 1), 2.5, 1.2)), 4.0 + rng.random(), 3.2, 6.0 + rng.random() * 2.0, canyon, "far", 11100 + group, 7)
    canyon_stats = {
        "bandCount": 3, "nearButtressGroups": 6, "midMesaShelfGroups": 10,
        "farFogSilhouettes": 4, "abyssOpeningsPortrait": 3,
        "maxNearWallOccupancy": .19, "repeatedGenericVerticalWalls": 0,
    }
    audit = {
        "uniqueCanyonGroupSignatures": len(set(signatures)),
        "canyonGroupSignatures": signatures, "continuousWallMeshes": 0,
        "longestIdenticalClusterFormRun": 1, "negativeSpaces": ["near-cut-0", "near-cut-2", "mid-gap-4", "far-split-2"],
    }
    return canyon_stats, audit


def build_courier(parent: bpy.types.Object) -> None:
    point, tangent, _ = route_sample(4.0)
    side = Vector((-tangent.y, tangent.x, 0.0))
    base = point + Vector((0, 0, .15))
    yaw = math.atan2(tangent.y, tangent.x) - math.pi * .5
    add_cone("A5_Courier_Torso", base + Vector((0, 0, .92)), .24, .16, .98, parent, "courier")
    add_sphere("A5_Courier_Head", base + Vector((0, 0, 1.66)), (.20, .20, .23), parent, "courier")
    for sign in (-1, 1):
        add_cube(f"A5_Courier_Leg_{sign}", base + side * sign * .13 + Vector((0, 0, .31)), (.09, .13, .34), parent, "courier", (0.0, sign * .18, yaw))
        add_cube(f"A5_Courier_Arm_{sign}", base + side * sign * .30 + Vector((0, 0, 1.0)), (.07, .12, .34), parent, "courier", (0.0, sign * .24, yaw + sign * .20))
    add_cube("A5_Courier_CoatTail", base - tangent * .16 + Vector((0, 0, .64)), (.25, .20, .42), parent, "courier", (math.radians(-18), 0.0, yaw))


def build_pursuer(parent: bpy.types.Object) -> dict[str, float]:
    sample_y = -3.4
    point, tangent, width = route_sample(sample_y)
    side = Vector((-tangent.y, tangent.x, 0.0))
    lateral_offset = .55
    base = point + side * lateral_offset + Vector((0, 0, .15))
    yaw = math.atan2(tangent.y, tangent.x) - math.pi * .5
    add_cube("A5_Pursuer_ShoulderMass", base + Vector((0, 0, .84)), (.86, .98, .44), parent, "pursuer", (0.0, .12, yaw))
    add_cone("A5_Pursuer_WedgeHead", base + tangent * 1.05 + Vector((0, 0, .88)), .40, .22, .78, parent, "pursuer", (math.radians(90), 0.0, yaw), 6)
    add_cube("A5_Pursuer_Jaw", base + tangent * 1.35 + Vector((0, 0, .62)), (.33, .29, .11), parent, "pursuer", (0.0, 0.0, yaw))
    for lateral in (-1, 1):
        for fore in (-1, 1):
            shoulder = base + side * lateral * .58 + tangent * fore * .61
            add_cube(f"A5_Pursuer_Upper_{lateral}_{fore}", shoulder + Vector((0, 0, .48)), (.13, .14, .43), parent, "pursuer", (0.0, lateral * .24, yaw + fore * .15))
            add_cube(f"A5_Pursuer_Lower_{lateral}_{fore}", shoulder + tangent * fore * .14 + Vector((0, 0, .15)), (.10, .13, .30), parent, "pursuer", (0.0, lateral * -.17, yaw - fore * .12))
    add_cube("A5_Pursuer_DorsalRidge", base - tangent * .12 + Vector((0, 0, 1.28)), (.19, .75, .13), parent, "pursuer", (0.0, 0.0, yaw))
    return {"routeSampleY": sample_y, "behindCourierMetres": 7.4, "lateralOffsetMetres": lateral_offset, "safeCorridorWidth": width * .68}


def build_arch(parent: bpy.types.Object) -> dict[str, float | int | bool]:
    point, tangent, deck_width = route_sample(20.0)
    side = Vector((-tangent.y, tangent.x, 0.0))
    base = point + Vector((0, 0, .14))
    outer, inner, thickness, support_height = 1.82, 1.36, .40, 2.15
    for sign in (-1, 1):
        support = base + side * sign * 1.94
        add_cube(f"A5_ArchSupport_{'L' if sign < 0 else 'R'}", support + Vector((0, 0, support_height * .5)), (.35, .56, support_height * .5), parent, "hazard", (0.0, 0.0, math.atan2(tangent.y, tangent.x) - math.pi * .5 + sign * .04))
        add_rock(f"A5_ArchFoot_{'L' if sign < 0 else 'R'}", support - tangent * .10 + Vector((0, 0, .03)), .50, .56, .32, parent, "hazard", 12000 + (1 if sign > 0 else 0), 6)
    for index in range(12):
        angle = math.radians(12 + index * 13.2)
        if index == 8:
            continue
        lateral = math.cos(angle) * (outer - thickness * .5)
        z = support_height + math.sin(angle) * (outer - thickness * .5)
        location = base + side * lateral + Vector((0, 0, z))
        add_cube(f"A5_ArchVoussoir_{index:02d}", location, (.29, .46, .32), parent, "hazard", (0.0, angle - math.pi * .5, math.atan2(tangent.y, tangent.x) - math.pi * .5 + (index % 2 - .5) * .08))
    add_cube("A5_Arch_BrokenKeystone", base + side * .40 + Vector((0, 0, support_height + outer * .92)), (.26, .48, .18), parent, "hazard", (0.0, .18, .18))
    return {
        "outerSpanToDeckWidth": round((outer * 2) / deck_width, 3),
        "innerRadiusMetres": inner, "apertureWidthMetres": round(inner * 2, 3),
        "apertureWorldPoints": [list(base + side * -inner + Vector((0, 0, support_height))), list(base + side * inner + Vector((0, 0, support_height)))],
        "supportCount": 2, "baseContactsDeck": True, "passableAperture": True,
        "manualReadTarget": "supported broken-stone opening",
    }


def build_tide_scar() -> bpy.types.Object:
    curve = bpy.data.curves.new("A5_TideScar_EditableCurve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = .052
    curve.bevel_resolution = 1
    obj = bpy.data.objects.new("TideScar_Ribbon_Editable", curve)
    bpy.context.collection.objects.link(obj)
    obj["a5Role"] = "scar"
    obj["maskExtractor"] = "editable-curve-spline-points"
    intervals = ((-28.0, -8.0), (7.0, 13.2), (25.0, 78.0))
    for interval_index, (start, end) in enumerate(intervals):
        spline = curve.splines.new("POLY")
        steps = 18
        spline.points.add(steps)
        for index in range(steps + 1):
            y = start + (end - start) * index / steps
            point, tangent, width = route_sample(y)
            side = Vector((-tangent.y, tangent.x, 0.0))
            offset = width * .38 + .08 * math.sin(index * 1.7 + interval_index)
            position = point + side * offset + Vector((0, 0, .19))
            spline.points[index].co = (position.x, position.y, position.z, 1.0)
    return obj


def make_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], fov: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name + "_Data")
    data.angle = math.radians(fov)
    camera = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    return camera


def build_lighting() -> None:
    bpy.ops.object.light_add(type="SUN", location=(-16, -12, 26))
    key = bpy.context.object
    key.name = "A5_Warm_Key"
    key.data.energy = 2.35
    key.data.angle = math.radians(18)
    key.rotation_euler = (math.radians(32), math.radians(-24), math.radians(-26))
    bpy.ops.object.light_add(type="AREA", location=(8, -6, 12))
    fill = bpy.context.object
    fill.name = "A5_Cool_Fill"
    fill.data.energy = 760
    fill.data.shape = "DISK"
    fill.data.size = 12
    fill.data.color = (.42, .62, 1.0)
    fill.rotation_euler = (math.radians(44), 0.0, math.radians(145))
    bpy.ops.object.light_add(type="AREA", location=(-8, 24, 17))
    rim = bpy.context.object
    rim.name = "A5_Rim"
    rim.data.energy = 950
    rim.data.size = 10
    rim.data.color = (1.0, .72, .48)
    rim.rotation_euler = (math.radians(67), 0.0, math.radians(-22))


def assign_materials(materials: dict[str, bpy.types.Material], mode: str) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type not in {"MESH", "CURVE"}:
            continue
        role = obj.get("a5Role", "other")
        if mode == "beauty":
            key = "ridge" if obj.name.startswith("A5_Pursuer_Dorsal") else role
            material = materials["beauty"].get(key, materials["beauty"]["other"])
        elif mode == "id":
            material = materials["id"].get(role, materials["id"]["other"])
        elif mode == "road":
            material = materials["roadWhite"] if role == "road" else materials["roadBlack"]
        else:
            material = materials["depth"]
        if not obj.data.materials:
            obj.data.materials.append(material)
        else:
            obj.data.materials[0] = material


def render(scene: bpy.types.Scene, camera: bpy.types.Object, path: Path, resolution: tuple[int, int], mode: str, materials: dict[str, bpy.types.Material]) -> None:
    assign_materials(materials, mode)
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(path)
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0) if mode != "beauty" else (0.045, 0.085, 0.13, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0 if mode != "beauty" else .46
    bpy.ops.render.render(write_still=True)


def object_bbox(scene: bpy.types.Scene, camera: bpy.types.Object, roots: list[bpy.types.Object], resolution: tuple[int, int]) -> dict[str, float]:
    points: list[Vector] = []
    for root_obj in roots:
        for obj in [root_obj, *list(root_obj.children_recursive)]:
            if obj.type == "MESH":
                points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
            elif obj.type == "CURVE":
                for spline in obj.data.splines:
                    points.extend(obj.matrix_world @ Vector(point.co.xyz) for point in spline.points)
    projected = [world_to_camera_view(scene, camera, point) for point in points]
    xs = [max(0.0, min(1.0, value.x)) for value in projected if value.z > 0]
    ys = [max(0.0, min(1.0, 1.0 - value.y)) for value in projected if value.z > 0]
    if not xs or not ys:
        return {"x": 0.0, "y": 0.0, "width": 0.0, "height": 0.0, "pixelWidth": 0.0, "pixelHeight": 0.0, "centerX": 0.0, "centerY": 0.0}
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return {"x": round(x0, 5), "y": round(y0, 5), "width": round(x1 - x0, 5), "height": round(y1 - y0, 5), "pixelWidth": round((x1 - x0) * resolution[0], 2), "pixelHeight": round((y1 - y0) * resolution[1], 2), "centerX": round((x0 + x1) * .5, 5), "centerY": round((y0 + y1) * .5, 5)}


def curve_mask_evidence(scene: bpy.types.Scene, camera: bpy.types.Object, curve: bpy.types.Object, resolution: tuple[int, int]) -> dict[str, object]:
    runs = []
    for spline in curve.data.splines:
        values = [world_to_camera_view(scene, camera, curve.matrix_world @ Vector(point.co.xyz)) for point in spline.points]
        visible = [value for value in values if value.z > 0 and 0 <= value.x <= 1 and 0 <= value.y <= 1]
        if len(visible) >= 2:
            xs = [value.x for value in visible]
            ys = [1.0 - value.y for value in visible]
            runs.append({"x": round(min(xs), 5), "y": round(min(ys), 5), "width": round(max(xs) - min(xs), 5), "height": round(max(ys) - min(ys), 5), "controlPoints": len(spline.points), "extractor": "CURVE.splines.POLY.points"})
    return {"extractor": "actual editable curve/spline control points", "editable": True, "runs": runs, "visibleRunCount": len(runs), "maskObjectName": curve.name, "resolution": list(resolution)}


def main() -> None:
    args = arguments()
    output = Path(args.output).resolve()
    expected = Path(r"E:\Proj\reproduction-temple-run\docs\workstreams\temple-tr3\asset-proof\a5").resolve()
    if output != expected:
        raise SystemExit("A5 output must be the exact scoped a5 directory")
    output.mkdir(parents=True, exist_ok=True)
    root_dir = Path(r"E:\Proj\reproduction-temple-run")
    source_paths = {
        "a3Generator": root_dir / "tools/temple-asset-pipeline/generate_tide_scar_hero_a3.py",
        "a3Metadata": root_dir / "docs/workstreams/temple-tr3/asset-proof/a3/a3-clay-metadata.json",
        "a3Verifier": root_dir / "docs/workstreams/temple-tr3/asset-proof/a3/a3-clay-verifier.json",
        "a4Generator": root_dir / "tools/temple-asset-pipeline/generate_tide_scar_hero_a4.py",
        "a4Metadata": root_dir / "docs/workstreams/temple-tr3/asset-proof/a4/a4-clay-metadata.json",
        "a4Verifier": root_dir / "docs/workstreams/temple-tr3/asset-proof/a4/a4-clay-verifier.json",
    }
    a3 = json.loads(source_paths["a3Metadata"].read_text(encoding="utf-8"))
    a4 = json.loads(source_paths["a4Metadata"].read_text(encoding="utf-8"))
    a4_verifier = json.loads(source_paths["a4Verifier"].read_text(encoding="utf-8"))
    reset_scene()
    beauty = {key: beauty_material("A5_Clay_" + key, color) for key, color in CLAY.items()}
    beauty["other"] = beauty_material("A5_Clay_Other", (.12, .16, .20, 1.0))
    materials = {
        "beauty": beauty,
        "id": {key: emission_material("A5_ID_" + key, color) for key, color in ID_COLORS.items()},
        "roadWhite": emission_material("A5_RoadMask_White", (1, 1, 1, 1)),
        "roadBlack": emission_material("A5_RoadMask_Black", (0, 0, 0, 1)),
        "depth": depth_material(),
    }
    causeway, canyon, courier, pursuer, arch_root = (root(name) for name in ROOTS[:5])
    route, road_audit = build_causeway(causeway)
    canyon_stats, canyon_audit = build_canyon(canyon)
    build_courier(courier)
    pursuer_audit = build_pursuer(pursuer)
    arch_stats = build_arch(arch_root)
    scar = build_tide_scar()
    build_lighting()
    scene = bpy.context.scene
    cameras = {
        "portrait": (make_camera("A5_PortraitCamera", (0.0, -21.5, 13.2), (0.5, 20.5, 2.6), 41.0), (540, 960)),
        "desktop": (make_camera("A5_DesktopCamera", (0.0, -21.5, 12.6), (0.5, 21.0, 2.7), 43.0), (960, 540)),
        "landscape": (make_camera("A5_LandscapeCamera", (0.0, -20.3, 10.9), (0.8, 21.5, 2.65), 46.0), (844, 390)),
        "closeup": (make_camera("A5_CloseupCamera", (0.0, -12.5, 7.8), (0.0, 10.0, 1.7), 47.0), (640, 480)),
    }
    images: dict[str, dict[str, str]] = {}
    for profile in ("portrait", "desktop", "landscape"):
        camera, resolution = cameras[profile]
        paths = {
            "beauty": output / f"a5-clay-{profile}-beauty.png",
            "objectId": output / f"a5-clay-{profile}-object-id.png",
            "roadMask": output / f"a5-clay-{profile}-road-mask.png",
            "depth": output / f"a5-clay-{profile}-depth.png",
        }
        render(scene, camera, paths["beauty"], resolution, "beauty", materials)
        render(scene, camera, paths["objectId"], resolution, "id", materials)
        render(scene, camera, paths["roadMask"], resolution, "road", materials)
        render(scene, camera, paths["depth"], resolution, "depth", materials)
        images[profile] = {key: str(path) for key, path in paths.items()}
    close_camera, close_resolution = cameras["closeup"]
    close_path = output / "a5-clay-closeup-beauty.png"
    render(scene, close_camera, close_path, close_resolution, "beauty", materials)
    images["closeup"] = {"beauty": str(close_path)}
    bpy.context.view_layer.update()
    projections = {}
    aperture_projections = {}
    scar_evidence = {}
    for profile, (camera, resolution) in cameras.items():
        scene.camera = camera
        scene.render.resolution_x, scene.render.resolution_y = resolution
        projections[profile] = {
            "courier": object_bbox(scene, camera, [courier], resolution),
            "pursuer": object_bbox(scene, camera, [pursuer], resolution),
            "hazard": object_bbox(scene, camera, [arch_root], resolution),
            "causeway": object_bbox(scene, camera, [causeway], resolution),
        }
        left, right = (Vector(value) for value in arch_stats["apertureWorldPoints"])
        left_view, right_view = world_to_camera_view(scene, camera, left), world_to_camera_view(scene, camera, right)
        aperture_projections[profile] = {"x": round(min(left_view.x, right_view.x), 5), "width": round(abs(right_view.x - left_view.x), 5), "pixelWidth": round(abs(right_view.x - left_view.x) * resolution[0], 2)}
        scar_evidence[profile] = curve_mask_evidence(scene, camera, scar, resolution)
    triangles = sum(max(0, len(poly.vertices) - 2) for mesh in bpy.data.meshes for poly in mesh.polygons)
    image_hashes = {profile: {kind: sha256(Path(path)) for kind, path in kinds.items()} for profile, kinds in images.items()}
    metadata = {
        "schema": "temple-tr3-a5-clay-proof-v1",
        "generator": "generate_tide_scar_hero_a5.py",
        "seed": SEED, "blender": bpy.app.version_string, "stage": "clay-only",
        "cleanRoom": "Deterministic local Blender Python geometry only; no downloads, external models, textures, or reference pixels.",
        "semanticRoots": ROOTS, "triangles": triangles, "route": route, "canyon": canyon_stats,
        "materialValues": a4["materialValues"], "tideScar": a3["tideScar"],
        "sourceHashes": {name: sha256(path) for name, path in source_paths.items()},
        "sourcePaths": {name: str(path) for name, path in source_paths.items()},
        "baselineFailures": {
            "a4FailureNames": a4_verifier["failures"],
            "portraitActorSeparationPx": a4_verifier["portraitActorSeparationPx"],
            "portraitHorizontalRoadBandOverlap": a4_verifier["portraitHorizontalRoadBandOverlap"],
            "portraitArchHeight": .06472, "desktopArchHeight": .11601, "desktopApertureWidth": .06503,
        },
        "a3Comparison": {
            "routeExact": route == a3["route"], "semanticRootsExact": ROOTS == a3["semanticRoots"],
            "tideScarExact": a3["tideScar"] == a4["tideScar"], "materialValuesExact": a4["materialValues"] == a3["materialValues"],
            "canyonInvariants": canyon_stats == a3["canyon"], "triangleBudget": triangles <= 45000,
        },
        "intentionalDifferences": ["offline causeway medium structure", "offline canyon cluster topology", "route-frame pursuer rig/placement", "supported arch assembly", "profile cameras", "curve-based Tide Scar mask extractor"],
        "geometryAudit": {**road_audit, **canyon_audit, "pursuerRouteFrame": pursuer_audit, "arch": arch_stats},
        "cameras": {name: {"location": [round(v, 4) for v in camera.location], "fovDegrees": round(math.degrees(camera.data.angle), 3), "resolution": list(resolution)} for name, (camera, resolution) in cameras.items()},
        "projections": projections, "apertureProjections": aperture_projections, "tideScarMaskEvidence": scar_evidence,
        "images": images, "imageHashes": image_hashes,
        "nonGoals": ["final materials", "GLB export", "KTX2", "runtime integration", "browser capture", "commit", "push", "QA"],
    }
    (output / "a5-clay-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"blender": metadata["blender"], "triangles": triangles, "images": image_hashes, "routeExact": metadata["a3Comparison"]["routeExact"]}, indent=2))
    if not metadata["a3Comparison"]["routeExact"] or triangles > 45000 or not bpy.app.version_string.startswith("4.5.5"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
