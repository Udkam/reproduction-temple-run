"""Generate the clean-room TIDE//RELAY A0 hero proof in Blender 4.5.

Run only through Blender background mode. The script deliberately creates all
geometry and PBR detail procedurally; it imports no scene, texture, or model.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SEED = 731943
RNG = random.Random(SEED)
FINAL_TUNE = {
    "sandstone_variation": 0.18,
    "mist_strength": 0.075,
    "scar_width": 0.105,
    "coral_density": 1.0,
    "mesa_count": 28,
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("draft", "diagnostic", "final"), required=True)
    parser.add_argument("--output", required=True)
    if "--" not in sys.argv:
        raise SystemExit("Expected Blender arguments after --")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (bpy.data.materials, bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for datablock in list(collection):
            if datablock.users == 0:
                collection.remove(datablock)


def set_parent(obj: bpy.types.Object, parent: bpy.types.Object | None) -> bpy.types.Object:
    obj.parent = parent
    return obj


def root(name: str, position: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    return obj


def new_material(name: str, base: tuple[float, float, float, float], roughness: float, metallic: float = 0.0, noise_strength: float = 0.0) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    if noise_strength > 0.0:
        texcoord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 4.3
        noise.inputs["Detail"].default_value = 5.0
        noise.inputs["Roughness"].default_value = 0.72
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = tuple(max(0.0, c - noise_strength) for c in base[:3]) + (1.0,)
        ramp.color_ramp.elements[1].color = tuple(min(1.0, c + noise_strength) for c in base[:3]) + (1.0,)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = min(0.42, noise_strength * 2.0)
        bump.inputs["Distance"].default_value = 0.12
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return material


def mist_material(name: str, color: tuple[float, float, float, float], alpha: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (color[0], color[1], color[2], alpha)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    output = nodes.new("ShaderNodeOutputMaterial")
    mix = nodes.new("ShaderNodeMixShader")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 0.22
    # MixShader factor 0 is transparent and 1 is the tinted mist emission.
    # Keep fog translucent instead of allowing a full rectangular card to occlude the sky.
    mix.inputs[0].default_value = max(0.0, min(1.0, alpha))
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(emission.outputs["Emission"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    try:
        material.surface_render_method = "DITHERED"
    except AttributeError:
        pass
    return material


def contact_shadow_material(name: str, alpha: float = 0.35) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    output = nodes.new("ShaderNodeOutputMaterial")
    mix = nodes.new("ShaderNodeMixShader")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    shadow = nodes.new("ShaderNodeBsdfPrincipled")
    shadow.inputs["Base Color"].default_value = (0.004, 0.007, 0.01, 1.0)
    shadow.inputs["Roughness"].default_value = 1.0
    mix.inputs[0].default_value = alpha
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(shadow.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    try:
        material.surface_render_method = "DITHERED"
    except AttributeError:
        pass
    material["alpha"] = alpha
    return material


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)


def mesh_object(name: str, vertices: list[tuple[float, float, float]], faces: list[tuple[int, ...]], material: bpy.types.Material, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(clean_customdata=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    assign_material(obj, material)
    set_parent(obj, parent)
    return obj


def bevel(obj: bpy.types.Object, width: float, segments: int = 2) -> None:
    modifier = obj.modifiers.new("Edge_Soften", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    weighted = obj.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True


def add_uv_sphere(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material: bpy.types.Material, parent: bpy.types.Object | None, segments: int = 24, rings: int = 12) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    set_parent(obj, parent)
    bpy.ops.object.shade_smooth()
    return obj


def add_ico(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material: bpy.types.Material, parent: bpy.types.Object | None, subdivisions: int = 2) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    set_parent(obj, parent)
    bevel(obj, 0.08, 2)
    return obj


def add_cone(name: str, location: tuple[float, float, float], radius1: float, radius2: float, depth: float, material: bpy.types.Material, parent: bpy.types.Object | None, vertices: int = 10) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    assign_material(obj, material)
    set_parent(obj, parent)
    bevel(obj, min(radius1, radius2) * 0.18, 2)
    return obj


def add_box(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material: bpy.types.Material, parent: bpy.types.Object | None, bevel_width: float = 0.12) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    set_parent(obj, parent)
    bevel(obj, bevel_width, 2)
    return obj


def limb_between(name: str, start: Vector, end: Vector, radius: float, material: bpy.types.Material, parent: bpy.types.Object, sides: int = 10) -> bpy.types.Object:
    direction = end - start
    middle = (start + end) * 0.5
    bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius * 0.95, radius2=radius, depth=direction.length, location=middle)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    assign_material(obj, material)
    set_parent(obj, parent)
    bevel(obj, radius * 0.18, 2)
    return obj


def create_deck_cap(index: int, center_y: float, length: float, center_x: float, sand: bpy.types.Material, dark_sand: bpy.types.Material, parent: bpy.types.Object) -> tuple[float, float]:
    samples = 7
    half = 4.0
    vertices: list[tuple[float, float, float]] = []
    lefts: list[float] = []
    rights: list[float] = []
    for sample in range(samples):
        t = sample / (samples - 1)
        y = center_y - length * 0.5 + length * t
        wav = math.sin(index * 0.83 + t * 5.2) * 0.18
        left = center_x - half + wav - RNG.uniform(0.02, 0.22)
        right = center_x + half + wav + RNG.uniform(0.02, 0.22)
        z = RNG.uniform(-0.028, 0.025)
        vertices.extend([(left, y, z), (right, y, z + RNG.uniform(-0.01, 0.018))])
        lefts.append(left)
        rights.append(right)
    top_count = len(vertices)
    for sample in range(samples):
        left = lefts[sample] - RNG.uniform(0.18, 0.48)
        right = rights[sample] + RNG.uniform(0.18, 0.48)
        y = center_y - length * 0.5 + length * sample / (samples - 1)
        vertices.extend([(left, y, -1.22 - RNG.uniform(0.0, 0.28)), (right, y, -1.22 - RNG.uniform(0.0, 0.28))])
    faces: list[tuple[int, ...]] = []
    for sample in range(samples - 1):
        a, b = sample * 2, sample * 2 + 1
        c, d = (sample + 1) * 2, (sample + 1) * 2 + 1
        ba, bb = top_count + sample * 2, top_count + sample * 2 + 1
        bc, bd = top_count + (sample + 1) * 2, top_count + (sample + 1) * 2 + 1
        faces.extend([(a, b, d, c), (a, c, bc, ba), (b, bb, bd, d), (ba, bc, bd, bb)])
    faces.extend([(0, top_count, top_count + 1, 1), (top_count - 2, top_count - 1, top_count * 2 - 1, top_count * 2 - 2)])
    cap = mesh_object("Causeway_Deck_{:03d}".format(index), vertices, faces, sand, parent)
    bevel(cap, 0.11, 2)
    # A separate darker stratum makes the cap genuinely layered rather than a flat slab.
    band = add_box("Causeway_Stratum_{:03d}".format(index), (center_x, center_y, -0.72), (4.06, length * 0.46, 0.17), dark_sand, parent, 0.08)
    return lefts[0], rights[0]


def create_apron(index: int, x_sign: float, center_x: float, center_y: float, length: float, material: bpy.types.Material, parent: bpy.types.Object) -> bpy.types.Object:
    top_x = center_x + x_sign * 4.02
    outer_top = center_x + x_sign * (4.75 + RNG.uniform(0.15, 0.8))
    low_outer = center_x + x_sign * (8.0 + RNG.uniform(1.0, 3.5))
    bottom = -10.0 - RNG.uniform(2.0, 6.0)
    y0, y1 = center_y - length * 0.5, center_y + length * 0.5
    mid_y = center_y + RNG.uniform(-0.7, 0.7)
    vertices = [
        (top_x, y0, -0.12), (top_x, y1, -0.12),
        (outer_top, y0, -0.8), (outer_top, y1, -0.82),
        (low_outer, y0 - RNG.uniform(0.2, 0.9), bottom),
        (low_outer, mid_y, bottom - RNG.uniform(0.0, 2.0)),
        (low_outer, y1 + RNG.uniform(0.2, 0.9), bottom),
    ]
    faces = [(0, 1, 3, 2), (2, 3, 6, 5, 4), (0, 2, 4), (1, 6, 3), (0, 4, 5, 6, 1)]
    apron = mesh_object("Cliff_Apron_{:03d}_{}".format(index, "L" if x_sign < 0 else "R"), vertices, faces, material, parent)
    bevel(apron, 0.16, 2)
    return apron


def create_causeway(materials: dict[str, bpy.types.Material], stage: str) -> bpy.types.Object:
    group = root("Causeway_Root")
    start = -28.0
    segment_length = 8.5
    for index in range(21):
        y = start + index * segment_length
        x = math.sin(index * 0.37) * 1.25 + math.sin(index * 0.12) * 0.55
        create_deck_cap(index, y, segment_length + 0.18, x, materials["sand"], materials["sand_dark"], group)
        create_apron(index, -1.0, x, y, segment_length, materials["sand_cliff"] if index % 3 else materials["basalt"], group)
        create_apron(index, 1.0, x, y, segment_length, materials["basalt"] if index % 3 else materials["sand_cliff"], group)
        # Short isolated teeth keep the silhouette broken without becoming continuous rails.
        for side in (-1.0, 1.0):
            if (index * 3 + (0 if side < 0 else 1)) % 4 != 0:
                x_tooth = x + side * RNG.uniform(4.45, 5.45)
                tooth = add_ico("Basalt_Tooth_{:03d}_{}".format(index, "L" if side < 0 else "R"), (x_tooth, y + RNG.uniform(-3.0, 3.0), -0.18), (RNG.uniform(0.5, 1.0), RNG.uniform(0.7, 1.5), RNG.uniform(1.0, 2.0)), materials["basalt"], group, 1)
                tooth.rotation_euler.z = RNG.uniform(-0.45, 0.45)
            if stage == "final" and (index + (0 if side < 0 else 2)) % 5 == 0:
                coral = add_ico("Coral_Lip_{:03d}_{}".format(index, "L" if side < 0 else "R"), (x + side * 4.18, y + RNG.uniform(-2.3, 2.3), 0.10), (0.34, 0.55, 0.16), materials["coral"], group, 1)
                coral.rotation_euler.z = RNG.uniform(-0.7, 0.7)
    return group


def create_rock_stack(name: str, location: tuple[float, float, float], radius: float, height: float, material: bpy.types.Material, parent: bpy.types.Object) -> bpy.types.Object:
    rings, sides = 4, 8
    vertices: list[tuple[float, float, float]] = []
    randomizer = random.Random(abs(hash(name)) % (2**32))
    for ring in range(rings):
        z = location[2] + height * ring / (rings - 1)
        factor = 1.0 - ring * 0.10 + randomizer.uniform(-0.07, 0.07)
        for side in range(sides):
            theta = math.tau * side / sides + randomizer.uniform(-0.08, 0.08)
            r = radius * factor * randomizer.uniform(0.76, 1.18)
            vertices.append((location[0] + math.cos(theta) * r, location[1] + math.sin(theta) * r, z + randomizer.uniform(-0.16, 0.16)))
    faces: list[tuple[int, ...]] = []
    for ring in range(rings - 1):
        for side in range(sides):
            nxt = (side + 1) % sides
            faces.append((ring * sides + side, ring * sides + nxt, (ring + 1) * sides + nxt, (ring + 1) * sides + side))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple((rings - 1) * sides + side for side in range(sides)))
    rock = mesh_object(name, vertices, faces, material, parent)
    bevel(rock, 0.12, 2)
    return rock


def create_panorama_and_canyon(materials: dict[str, bpy.types.Material], stage: str) -> bpy.types.Object:
    group = root("Canyon_Root")
    # Inward-facing backdrop encloses cameras; it is a panorama volume, not a distant wall.
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=210.0, depth=160.0, end_fill_type="NOTHING", location=(0.0, 58.0, 35.0))
    enclosure = bpy.context.object
    enclosure.name = "Panorama_Inward_Enclosure"
    enclosure.scale.z = 1.0
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(enclosure, materials["panorama"])
    set_parent(enclosure, group)
    enclosure.visible_shadow = False
    enclosure["castsShadow"] = False
    # Flip normals so both cameras sit inside the panorama.
    bpy.context.view_layer.objects.active = enclosure
    enclosure.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode="OBJECT")
    enclosure.select_set(False)
    for layer, (distance, count, scale) in enumerate(((112.0, 10, 9.0), (74.0, 12, 6.0), (36.0, 8, 4.0))):
        for item in range(count):
            angle = math.tau * item / count + layer * 0.47
            x = math.sin(angle) * distance
            y = 48.0 + math.cos(angle) * distance
            if -18.0 < x < 18.0 and y < 150.0:
                # Preserve the main road corridor but still place far terrain behind it.
                y += 34.0
            height = scale * (1.0 + (item % 3) * 0.42)
            create_rock_stack("Canyon_{}_Mesa_{:02d}".format(("Far", "Mid", "Near")[layer], item), (x, y, -14.0), scale * (0.72 + (item % 4) * 0.12), height, materials["basalt"] if layer < 2 else materials["sand_cliff"], group)
    # Deep water is intentionally low and wide, visible through true causeway gaps at the edges.
    water = add_box("Deep_Blue_Canyon_Water", (0.0, 58.0, -16.5), (185.0, 185.0, 0.15), materials["water"], group, 0.0)
    # A1 has no Mist_Band geometry. The uncapped panorama, distant mesas and water
    # provide depth without screen-wide transparent rectangles.
    return group


def add_disc(name: str, position: tuple[float, float, float], scale: tuple[float, float, float], material: bpy.types.Material, parent: bpy.types.Object) -> bpy.types.Object:
    bpy.ops.mesh.primitive_circle_add(vertices=32, radius=1.0, fill_type="TRIFAN", location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    set_parent(obj, parent)
    return obj


def create_runner(materials: dict[str, bpy.types.Material]) -> bpy.types.Object:
    group = root("Runner_Root", (0.2, 14.0, 0.0))
    add_disc("Runner_Contact_Shadow", (0.0, 0.0, 0.025), (1.0, 0.7, 1.0), materials["shadow"], group)
    torso = add_cone("Runner_Torso", (0.0, 0.0, 1.78), 0.48, 0.63, 1.72, materials["courier"], group, 12)
    torso.rotation_euler.x = math.radians(-7.0)
    add_uv_sphere("Runner_Head", (0.0, 0.08, 2.96), (0.34, 0.34, 0.38), materials["skin"], group, 20, 12)
    add_cone("Runner_Hood", (0.0, 0.02, 2.92), 0.40, 0.34, 0.36, materials["courier_dark"], group, 12)
    # Alternating run pose keeps limbs distinct and grounded.
    for side, hip, knee, foot in ((-1.0, Vector((-0.25, 0.02, 1.28)), Vector((-0.35, 0.54, 0.62)), Vector((-0.42, 0.86, 0.08))), (1.0, Vector((0.25, 0.02, 1.28)), Vector((0.35, -0.48, 0.65)), Vector((0.48, -0.72, 0.08)))):
        limb_between("Runner_Thigh_{}".format("L" if side < 0 else "R"), hip, knee, 0.19, materials["courier_dark"], group)
        limb_between("Runner_Shin_{}".format("L" if side < 0 else "R"), knee, foot, 0.15, materials["courier_dark"], group)
        add_box("Runner_Foot_{}".format("L" if side < 0 else "R"), tuple(foot + Vector((0.0, 0.14 if side < 0 else -0.12, 0.05))), (0.19, 0.37, 0.10), materials["courier_dark"], group, 0.05)
    for side in (-1.0, 1.0):
        shoulder = Vector((side * 0.52, 0.02, 2.32))
        elbow = Vector((side * 0.72, 0.14 if side < 0 else -0.44, 1.78))
        hand = Vector((side * 0.78, 0.52 if side < 0 else -0.72, 1.45))
        limb_between("Runner_UpperArm_{}".format("L" if side < 0 else "R"), shoulder, elbow, 0.13, materials["courier"], group)
        limb_between("Runner_Forearm_{}".format("L" if side < 0 else "R"), elbow, hand, 0.11, materials["skin"], group)
    tails = [(-0.42, -0.12), (0.42, -0.12)]
    for index, (x, y) in enumerate(tails):
        vertices = [(x - 0.18, y, 1.42), (x + 0.18, y, 1.42), (x * 1.55, y - 0.55, 0.44), (x * 1.2, y - 0.12, 0.90)]
        mesh_object("Runner_Coat_Tail_{:02d}".format(index), vertices, [(0, 1, 3), (0, 3, 2), (1, 2, 3)], materials["courier"], group)
    scarf = add_box("Runner_Coral_Scarf", (0.0, -0.47, 2.42), (0.13, 0.08, 0.52), materials["coral"], group, 0.04)
    scarf.rotation_euler.x = math.radians(22.0)
    return group


def create_pursuer(materials: dict[str, bpy.types.Material]) -> bpy.types.Object:
    # Behind the courier in world forward order, but no longer clipped by the near camera edge.
    group = root("Pursuer_Root", (-0.35, 5.0, 0.0))
    group.rotation_euler.z = math.radians(-5.0)
    add_disc("Pursuer_Contact_Shadow", (0.0, 0.0, 0.026), (2.9, 2.3, 1.0), materials["shadow"], group)
    # Broad layered torso and shoulders read as a rock animal, never as a single sphere.
    add_ico("Pursuer_Basalt_Body", (0.0, 0.0, 1.82), (1.72, 2.20, 0.92), materials["basalt"], group, 2)
    add_ico("Pursuer_Shoulder_Mass", (0.0, 0.88, 1.96), (1.82, 1.12, 1.04), materials["basalt_light"], group, 2)
    add_ico("Pursuer_Head", (0.0, 2.38, 1.66), (1.02, 0.96, 0.72), materials["basalt_light"], group, 2)
    add_cone("Pursuer_Muzzle", (0.0, 3.05, 1.42), 0.66, 0.42, 0.95, materials["basalt"], group, 8).rotation_euler.x = math.radians(90.0)
    for side in (-1.0, 1.0):
        for row, y in enumerate((1.14, -1.20)):
            shoulder = Vector((side * 1.27, y, 1.62))
            knee = Vector((side * 1.70, y + (0.52 if row == 0 else -0.42), 0.78))
            foot = Vector((side * 1.78, y + (0.86 if row == 0 else -0.80), 0.10))
            label = ("F" if row == 0 else "H") + ("L" if side < 0 else "R")
            limb_between("Pursuer_Upper_Limb_" + label, shoulder, knee, 0.36, materials["basalt_light"], group, 9)
            limb_between("Pursuer_Lower_Limb_" + label, knee, foot, 0.29, materials["basalt"], group, 9)
            add_box("Pursuer_Grounded_Paw_" + label, tuple(foot + Vector((0.0, 0.18 if row == 0 else -0.15, 0.07))), (0.42, 0.50, 0.12), materials["basalt"], group, 0.07)
    for index, y in enumerate((-0.82, -0.20, 0.45, 1.08)):
        spike = add_cone("Pursuer_Coral_Dorsal_{:02d}".format(index), (0.0, y, 2.78 + index * 0.045), 0.22, 0.03, 0.82 - index * 0.06, materials["coral"], group, 6)
        spike.rotation_euler.x = math.radians(-13.0)
    for side in (-1.0, 1.0):
        add_ico("Pursuer_Brow_{}".format("L" if side < 0 else "R"), (side * 0.52, 2.72, 1.98), (0.30, 0.24, 0.22), materials["coral_dark"], group, 1)
    return group


def create_obstacle(materials: dict[str, bpy.types.Material]) -> bpy.types.Object:
    group = root("Obstacle_Ring_Root", (0.6, 43.0, 0.0))
    add_disc("Ring_Contact_Shadow", (0.0, 0.0, 0.026), (2.8, 1.2, 1.0), materials["shadow"], group)
    for side in (-1.0, 1.0):
        support = add_cone("Ring_Support_{}".format("L" if side < 0 else "R"), (side * 1.86, 0.0, 1.18), 0.56, 0.44, 2.35, materials["sand_cliff"], group, 10)
        support.rotation_euler.y = side * math.radians(4.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.86, minor_radius=0.34, major_segments=24, minor_segments=10, location=(0.0, 0.0, 2.42), rotation=(math.pi * 0.5, 0.0, 0.0))
    ring = bpy.context.object
    ring.name = "Open_Arch_Ring_Thick"
    assign_material(ring, materials["sand"])
    set_parent(ring, group)
    bevel(ring, 0.06, 2)
    for index in range(7):
        debris = add_ico("Ring_Debris_{:02d}".format(index), (RNG.uniform(-3.2, 3.2), RNG.uniform(-1.8, 1.8), 0.18), (RNG.uniform(0.12, 0.35), RNG.uniform(0.12, 0.35), RNG.uniform(0.10, 0.24)), materials["sand_cliff"], group, 1)
        debris.rotation_euler = (RNG.random(), RNG.random(), RNG.random())
    return group


def create_tide_scar(material: bpy.types.Material, stage: str) -> bpy.types.Object:
    curve = bpy.data.curves.new("TideScar_Ribbon_Editable_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = FINAL_TUNE["scar_width"] if stage == "final" else 0.082
    curve.bevel_resolution = 3
    curve.resolution_u = 24
    obj = bpy.data.objects.new("TideScar_Ribbon_Editable", curve)
    bpy.context.collection.objects.link(obj)
    assign_material(obj, material)
    segments = [(-22.0, -5.0), (-1.5, 17.0), (23.0, 39.0), (46.0, 70.0), (78.0, 111.0), (117.0, 143.0)]
    for index, (start, end) in enumerate(segments):
        spline = curve.splines.new("BEZIER")
        count = 5
        spline.bezier_points.add(count - 1)
        for point_index, point in enumerate(spline.bezier_points):
            t = point_index / (count - 1)
            y = start + (end - start) * t
            center = math.sin(((y + 28.0) / 8.5) * 0.37) * 1.25 + math.sin(((y + 28.0) / 8.5) * 0.12) * 0.55
            x = center + 3.46 + math.sin(y * 0.37 + index) * 0.13
            point.co = (x, y, 0.095)
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"
    obj["semantic"] = "analytic_right_edge_tide_scar"
    obj["emissive"] = False
    obj["baked_into_road"] = False
    return obj


def create_lighting(materials: dict[str, bpy.types.Material]) -> None:
    world = bpy.context.scene.world or bpy.data.worlds.new("TideScar_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.10, 0.16, 0.19, 1.0)
    background.inputs["Strength"].default_value = 0.45
    bpy.ops.object.light_add(type="AREA", location=(-12.0, -14.0, 34.0))
    key = bpy.context.object
    key.name = "Warm_Sun_Key"
    key.data.energy = 3500.0
    key.data.shape = "DISK"
    key.data.size = 10.0
    key.data.color = (1.0, 0.74, 0.45)
    key.rotation_euler = (Vector((0.0, 34.0, 0.0)) - key.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(14.0, -2.0, 16.0))
    rim = bpy.context.object
    rim.name = "Cool_Canyon_Rim"
    rim.data.energy = 500.0
    rim.data.shape = "RECTANGLE"
    rim.data.size = 14.0
    rim.data.color = (0.20, 0.48, 0.72)
    rim.rotation_euler = (Vector((0.0, 24.0, 0.0)) - rim.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 35.0))
    sun = bpy.context.object
    sun.name = "Soft_Far_Sun"
    sun.data.energy = 3.0
    sun.data.angle = math.radians(4.0)
    sun.rotation_euler = (Vector((0.0, 36.0, 0.0)) - sun.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.object.light_add(type="AREA", location=(0.0, -22.0, 18.0))
    fill = bpy.context.object
    fill.name = "Camera_Side_Fill"
    fill.data.energy = 1800.0
    fill.data.shape = "DISK"
    fill.data.size = 16.0
    fill.data.color = (0.44, 0.62, 0.72)
    fill.rotation_euler = (Vector((0.0, 16.0, 0.0)) - fill.location).to_track_quat("-Z", "Y").to_euler()


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(name: str, position: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name + "_Camera")
    data.lens = lens
    data.sensor_width = 32.0
    data.clip_start = 0.1
    data.clip_end = 500.0
    camera = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(camera)
    camera.location = position
    point_camera(camera, Vector(target))
    return camera


def render(camera: bpy.types.Object, path: Path, size: tuple[int, int], samples: int) -> None:
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.resolution_x = size[0]
    scene.render.resolution_y = size[1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = samples
    scene.eevee.taa_samples = samples
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.compression = 18
    scene.render.resolution_percentage = 100
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 18
    scene.render.filepath = str(path)
    scene.render.resolution_x, scene.render.resolution_y = size
    try:
        scene.view_settings.look = "AgX - Medium Low Contrast"
    except TypeError:
        pass
    scene.view_settings.exposure = 1.0
    scene.view_settings.gamma = 1.0
    scene["eeveeRenderSamples"] = samples
    bpy.ops.render.render(write_still=True)


def make_proof_images(texture_dir: Path) -> list[Path]:
    texture_dir.mkdir(parents=True, exist_ok=True)
    definitions = {
        "proof-sandstone-base.png": "sandstone",
        "proof-basalt-base.png": "basalt",
        "proof-sandstone-normal.png": "normal",
        "proof-sandstone-roughness.png": "roughness",
        "proof-sandstone-ao.png": "ao",
    }
    created: list[Path] = []
    size = 256
    for filename, kind in definitions.items():
        image = bpy.data.images.new("A0_" + filename, width=size, height=size, alpha=False, float_buffer=False)
        pixels: list[float] = []
        for y in range(size):
            for x in range(size):
                u, v = x / (size - 1), y / (size - 1)
                grain = 0.5 + 0.5 * math.sin(u * 63.0 + math.sin(v * 18.0) * 3.0) * math.sin(v * 57.0)
                broad = 0.5 + 0.5 * math.sin(u * 8.0 + v * 13.0)
                if kind == "sandstone":
                    r, g, b = 0.54 + grain * 0.20, 0.34 + grain * 0.22, 0.17 + broad * 0.12
                elif kind == "basalt":
                    r, g, b = 0.06 + grain * 0.07, 0.10 + grain * 0.10, 0.13 + broad * 0.12
                elif kind == "normal":
                    r, g, b = 0.5 + (grain - 0.5) * 0.22, 0.5 + (broad - 0.5) * 0.22, 1.0
                elif kind == "roughness":
                    r = g = b = 0.70 + grain * 0.22
                else:
                    r = g = b = 0.52 + broad * 0.40
                pixels.extend((r, g, b, 1.0))
        image.pixels.foreach_set(pixels)
        image.file_format = "PNG"
        image.filepath_raw = str(texture_dir / filename)
        image.save()
        created.append(texture_dir / filename)
        bpy.data.images.remove(image)
    return created


def scene_metadata(output: Path, stage: str, filename: str = "scene-metadata.json") -> None:
    triangles = sum(len(poly.vertices) - 2 for mesh in bpy.data.meshes for poly in mesh.polygons)
    metadata = {
        "schema": "temple-tr3-a0-blender-scene-v1",
        "stage": stage,
        "generator": "generate_tide_scar_hero.py",
        "seed": SEED,
        "units": "metres",
        "axes": {"forward": "+Y", "up": "+Z"},
        "stableRoots": ["Causeway_Root", "Canyon_Root", "Runner_Root", "Pursuer_Root", "Obstacle_Ring_Root", "TideScar_Ribbon_Editable"],
        "cameraNames": ["HeroCamera_Portrait", "HeroCamera_Desktop"],
        "materialNames": sorted(material.name for material in bpy.data.materials),
        "trianglesBeforeExport": triangles,
        "tideScar": {"object": "TideScar_Ribbon_Editable", "curve": True, "emissive": False, "bakedIntoRoad": False},
        "renderRepair": {"panoramaEndCaps": False, "panoramaCastsShadow": False, "mistBandCount": 0, "exposure": 1.0, "look": "AgX - Medium Low Contrast", "eeveeRenderSamples": bpy.context.scene.get("eeveeRenderSamples")},
        "cleanRoom": "No external model, image, commercial asset, or reference pixel is imported by this generator.",
    }
    (output / filename).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def export_glb(output: Path) -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(output / "tide-scar-hero.unoptimized.glb"), export_format="GLB", use_selection=False, export_apply=True, export_yup=True, export_materials="EXPORT", export_cameras=True, export_lights=True, export_extras=True)


def main() -> None:
    args = arguments()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    reset_scene()
    materials = {
        "sand": new_material("M_Sandstone_Sun", (0.56, 0.31, 0.13, 1.0), 0.80, 0.0, FINAL_TUNE["sandstone_variation"]),
        "sand_dark": new_material("M_Sandstone_Stratum", (0.27, 0.13, 0.055, 1.0), 0.88, 0.0, 0.08),
        "sand_cliff": new_material("M_Sandstone_Cliff", (0.34, 0.18, 0.075, 1.0), 0.86, 0.0, 0.12),
        "basalt": new_material("M_Basalt_Deep", (0.07, 0.12, 0.16, 1.0), 0.91, 0.01, 0.10),
        "basalt_light": new_material("M_Basalt_Lit", (0.12, 0.20, 0.24, 1.0), 0.89, 0.01, 0.11),
        "coral": new_material("M_Coral_Mineral", (0.52, 0.055, 0.024, 1.0), 0.78, 0.0, 0.04),
        "coral_dark": new_material("M_Coral_Dark", (0.25, 0.018, 0.01, 1.0), 0.85, 0.0, 0.03),
        "courier": new_material("M_Courier_Slate", (0.12, 0.19, 0.22, 1.0), 0.74, 0.0, 0.04),
        "courier_dark": new_material("M_Courier_Ink", (0.045, 0.065, 0.075, 1.0), 0.82, 0.0, 0.02),
        "skin": new_material("M_Courier_Skin", (0.27, 0.095, 0.047, 1.0), 0.62, 0.0, 0.02),
        "water": new_material("M_Deep_Canyon_Water", (0.015, 0.07, 0.14, 1.0), 0.40, 0.12, 0.04),
        "panorama": new_material("M_Panorama_Procedural", (0.13, 0.22, 0.29, 1.0), 1.0, 0.0, 0.08),
        "shadow": contact_shadow_material("M_Contact_Shadow", 0.35),
        "scar": new_material("M_Tide_Scar_Lime", (0.94, 0.80, 0.60, 1.0), 0.94, 0.0, 0.025),
    }
    create_causeway(materials, args.stage)
    create_panorama_and_canyon(materials, args.stage)
    create_runner(materials)
    create_pursuer(materials)
    create_obstacle(materials)
    create_tide_scar(materials["scar"], args.stage)
    create_lighting(materials)
    portrait = create_camera("HeroCamera_Portrait", (0.0, -33.0, 25.0), (0.0, 43.0, 0.0), 48.0)
    desktop = create_camera("HeroCamera_Desktop", (0.0, -34.0, 23.0), (0.0, 46.0, 0.0), 45.0)
    samples = 16 if args.stage == "diagnostic" else 24 if args.stage == "draft" else 96
    if args.stage == "draft":
        render(portrait, output / "portrait-hero-draft.png", (720, 1280), samples)
    elif args.stage == "diagnostic":
        render(portrait, output / "diagnostic-portrait.png", (360, 640), samples)
        render(desktop, output / "diagnostic-desktop.png", (640, 360), samples)
        close = create_camera("HeroCamera_Closeup", (6.8, -12.0, 8.0), (0.0, 3.0, 1.3), 55.0)
        render(close, output / "diagnostic-closeup.png", (480, 360), samples)
    else:
        render(portrait, output / "portrait-hero.png", (900, 1600), samples)
        render(desktop, output / "desktop-hero.png", (1600, 900), samples)
        close = create_camera("HeroCamera_Closeup", (6.8, -12.0, 8.0), (0.0, 3.0, 1.3), 55.0)
        render(close, output / "runner-pursuer-obstacle-closeup.png", (1200, 900), samples)
    if args.stage == "diagnostic":
        scene_metadata(output, args.stage, "diagnostic-scene-metadata.json")
    else:
        make_proof_images(output / "textures")
        scene_metadata(output, args.stage)
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "tide-scar-hero.blend"))
        export_glb(output)


if __name__ == "__main__":
    main()
