"""TEMPLE-TR3-A2 clean-room structural environment-art proof.

This is intentionally an offline Blender scene generator.  It neither imports
external art nor reads project runtime files.  Run with Blender 4.5 in
background mode and pass --stage clay or --stage final after ``--``.
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


SEED = 270731
ROOT_NAMES = [
    "Causeway_Root",
    "Canyon_Root",
    "Runner_Root",
    "Pursuer_Root",
    "Obstacle_Ring_Root",
    "TideScar_Ribbon_Editable",
]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("clay", "final"))
    parser.add_argument("--output", required=True)
    # Blender retains its own command-line flags. Only parse the explicit payload
    # following its conventional `--` separator.
    payload = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(payload)


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium Low Contrast"
    scene.view_settings.exposure = 0.7
    scene.view_settings.gamma = 1.0
    scene.world = bpy.data.worlds.new("A2_Procedural_Deep_Blue_World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.025, 0.075, 0.13, 1.0)
    background.inputs["Strength"].default_value = 0.34
    try:
        scene.eevee.taa_render_samples = 48
        scene["eeveeRenderSamples"] = 48
    except AttributeError:
        scene.eevee.taa_samples = 48
        scene["eeveeRenderSamples"] = 48
    scene.camera = None
    bpy.context.preferences.filepaths.save_version = 0


def parent_empty(name: str, location: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material | None,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    if material:
        mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def add_cube(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj.parent = parent
    return obj


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    segments: int = 12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(6, segments // 2), location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj.parent = parent
    return obj


def add_cone_between(
    name: str,
    start: Vector,
    end: Vector,
    radius0: float,
    radius1: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    vertices: int = 8,
) -> bpy.types.Object:
    delta = end - start
    midpoint = (start + end) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius0,
        radius2=radius1,
        depth=delta.length,
        location=midpoint,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(delta.normalized())
    obj.data.materials.append(material)
    obj.parent = parent
    return obj


def add_rock(
    name: str,
    location: tuple[float, float, float],
    radius_x: float,
    radius_y: float,
    height: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    seed: int,
    sides: int = 7,
) -> bpy.types.Object:
    """An irregular three-ring rock, intentionally not a repeated primitive."""
    rng = random.Random(seed)
    rings: list[list[tuple[float, float, float]]] = []
    ring_specs = ((0.0, 1.0), (height * (0.42 + rng.random() * 0.12), 1.12), (height, 0.48 + rng.random() * 0.19))
    for z, scale in ring_specs:
        ring: list[tuple[float, float, float]] = []
        for index in range(sides):
            angle = math.tau * index / sides + 0.11 * math.sin(index * 3.7 + seed)
            irregular = 0.75 + rng.random() * 0.45
            ring.append((
                location[0] + math.cos(angle) * radius_x * scale * irregular,
                location[1] + math.sin(angle) * radius_y * scale * irregular,
                location[2] + z + math.sin(index * 2.3 + seed) * height * 0.035,
            ))
        rings.append(ring)
    vertices = [point for ring in rings for point in ring]
    faces: list[tuple[int, ...]] = []
    for ring_index in range(2):
        offset = ring_index * sides
        for index in range(sides):
            nxt = (index + 1) % sides
            faces.append((offset + index, offset + nxt, offset + sides + nxt, offset + sides + index))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple(range(2 * sides, 3 * sides)))
    return mesh_object(name, vertices, faces, material, parent)


def new_simple_material(name: str, color: tuple[float, float, float, float], roughness: float, metallic: float = 0.0) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def create_texture(path: Path, name: str, mode: str, size: int = 256) -> Path:
    image = bpy.data.images.new(name, width=size, height=size, alpha=False, float_buffer=False)
    pixels: list[float] = []
    for y in range(size):
        for x in range(size):
            u, v = x / (size - 1), y / (size - 1)
            grain = 0.5 + 0.5 * math.sin(u * 41.0 + math.sin(v * 13.0) * 2.0) * math.sin(v * 53.0)
            strata = 0.5 + 0.5 * math.sin(v * 18.0 + u * 4.0)
            fracture = 0.5 + 0.5 * math.sin((u * 10.0 + v * 7.0) * math.pi)
            if mode == "sand_base":
                color = (0.42 + grain * 0.27, 0.19 + strata * 0.22, 0.065 + fracture * 0.12)
            elif mode == "basalt_base":
                color = (0.045 + grain * 0.09, 0.105 + strata * 0.13, 0.14 + fracture * 0.13)
            elif mode == "coral_mask":
                c = 0.2 + 0.8 * max(0.0, math.sin(u * 17.0) * math.sin(v * 23.0))
                color = (c, c, c)
            elif mode == "normal":
                color = (0.5 + (grain - 0.5) * 0.18, 0.5 + (strata - 0.5) * 0.18, 1.0)
            else:  # ORM: occlusion / roughness / metallic
                color = (0.62 + grain * 0.30, 0.58 + strata * 0.32, 0.01 + fracture * 0.04)
            pixels.extend((*color, 1.0))
    image.pixels.foreach_set(pixels)
    image.file_format = "PNG"
    image.filepath_raw = str(path)
    image.save()
    bpy.data.images.remove(image)
    return path


def create_bound_images(texture_dir: Path) -> dict[str, bpy.types.Image]:
    texture_dir.mkdir(parents=True, exist_ok=True)
    definitions = {
        "sand_base": ("a2-sandstone-base.png", "sand_base", "sRGB"),
        "sand_normal": ("a2-sandstone-normal.png", "normal", "Non-Color"),
        "sand_orm": ("a2-sandstone-orm.png", "orm", "Non-Color"),
        "basalt_base": ("a2-basalt-base.png", "basalt_base", "sRGB"),
        "basalt_normal": ("a2-basalt-normal.png", "normal", "Non-Color"),
        "basalt_orm": ("a2-basalt-orm.png", "orm", "Non-Color"),
        "coral_mask": ("a2-coral-mask.png", "coral_mask", "Non-Color"),
    }
    images: dict[str, bpy.types.Image] = {}
    for key, (filename, mode, color_space) in definitions.items():
        path = create_texture(texture_dir / filename, "A2_" + key, mode)
        image = bpy.data.images.load(str(path), check_existing=False)
        image.name = "A2_" + key
        try:
            image.colorspace_settings.name = color_space
        except TypeError:
            pass
        images[key] = image
    return images


def new_pbr_material(
    name: str,
    base_image: bpy.types.Image | None,
    normal_image: bpy.types.Image | None,
    orm_image: bpy.types.Image | None,
    factor: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = new_simple_material(name, factor, roughness, metallic)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    if base_image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = base_image
        texture.projection = "FLAT"
        links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    if normal_image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = normal_image
        normal = nodes.new("ShaderNodeNormalMap")
        normal.inputs["Strength"].default_value = 0.38
        links.new(texture.outputs["Color"], normal.inputs["Color"])
        links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    if orm_image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = orm_image
        separate = nodes.new("ShaderNodeSeparateRGB")
        links.new(texture.outputs["Color"], separate.inputs["Image"])
        links.new(separate.outputs["G"], bsdf.inputs["Roughness"])
        links.new(separate.outputs["B"], bsdf.inputs["Metallic"])
    return material


def coral_material(mask: bpy.types.Image) -> bpy.types.Material:
    material = new_simple_material("M_Coral_Mineral", (0.56, 0.075, 0.035, 1.0), 0.72)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = mask
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.18, 0.008, 0.002, 1.0)
    ramp.color_ramp.elements[1].color = (0.78, 0.12, 0.045, 1.0)
    links.new(texture.outputs["Color"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return material


def transparent_shadow_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_ContactShadow")
    material.use_nodes = True
    material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    mix = nodes.new("ShaderNodeMixShader")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = (0.006, 0.012, 0.016, 1.0)
    principled.inputs["Roughness"].default_value = 1.0
    mix.inputs[0].default_value = 0.35
    material.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
    material.node_tree.links.new(principled.outputs[0], mix.inputs[2])
    material.node_tree.links.new(mix.outputs[0], out.inputs[0])
    return material


def volume_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_Bounded_Mist_Volume")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    volume = nodes.new("ShaderNodeVolumePrincipled")
    volume.inputs["Color"].default_value = (0.16, 0.33, 0.43, 1.0)
    volume.inputs["Density"].default_value = 0.00125
    volume.inputs["Anisotropy"].default_value = 0.18
    material.node_tree.links.new(volume.outputs["Volume"], out.inputs["Volume"])
    return material


def materials(output: Path, stage: str) -> dict[str, bpy.types.Material]:
    if stage == "clay":
        return {
            "clay": new_simple_material("M_A2_Clay", (0.42, 0.45, 0.47, 1.0), 0.86),
            "abyss": new_simple_material("M_A2_Clay_Abyss", (0.06, 0.13, 0.19, 1.0), 1.0),
            "fog": volume_material(),
        }
    images = create_bound_images(output / "textures")
    return {
        "sand": new_pbr_material("M_Sandstone", images["sand_base"], images["sand_normal"], images["sand_orm"], (0.83, 0.52, 0.27, 1.0), 0.78),
        "basalt": new_pbr_material("M_Basalt", images["basalt_base"], images["basalt_normal"], images["basalt_orm"], (0.22, 0.38, 0.45, 1.0), 0.89),
        "coral": coral_material(images["coral_mask"]),
        "courier": new_simple_material("M_Courier", (0.13, 0.25, 0.29, 1.0), 0.61, 0.05),
        "scar": new_simple_material("M_TideScar", (0.92, 0.79, 0.59, 1.0), 0.94),
        "abyss": new_simple_material("M_Abyss_Panorama", (0.035, 0.13, 0.23, 1.0), 0.98),
        "shadow": transparent_shadow_material(),
        "fog": volume_material(),
    }


def catmull(a: Vector, b: Vector, c: Vector, d: Vector, t: float) -> Vector:
    return 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t)


def make_spine() -> list[tuple[Vector, float]]:
    knots = [
        (Vector((-3.1, -48.0, -0.3)), 8.0), (Vector((-2.2, -30.0, 0.0)), 8.8),
        (Vector((-0.8, -12.0, 0.45)), 9.35), (Vector((1.2, 7.0, 0.85)), 8.2),
        (Vector((3.0, 27.0, 1.15)), 7.25), (Vector((2.0, 49.0, 1.55)), 8.7),
        (Vector((-1.0, 73.0, 1.4)), 7.85), (Vector((-3.5, 99.0, 1.9)), 9.45),
        (Vector((-2.0, 126.0, 2.45)), 8.05), (Vector((1.8, 154.0, 2.1)), 7.55),
    ]
    samples: list[tuple[Vector, float]] = []
    for index in range(len(knots) - 1):
        a = knots[max(0, index - 1)][0]
        b, width_b = knots[index]
        c, width_c = knots[index + 1]
        d = knots[min(len(knots) - 1, index + 2)][0]
        for step in range(6):
            if index and step == 0:
                continue
            t = step / 6.0
            samples.append((catmull(a, b, c, d, t), width_b + (width_c - width_b) * t))
    samples.append(knots[-1])
    return samples


SPINE = make_spine()


def section(index: int) -> tuple[Vector, Vector, Vector, float]:
    point, width = SPINE[index]
    previous = SPINE[max(0, index - 1)][0]
    following = SPINE[min(len(SPINE) - 1, index + 1)][0]
    tangent = (following - previous).normalized()
    side = Vector((tangent.y, -tangent.x, 0.0)).normalized()
    return point, tangent, side, width


def sample_road(y: float) -> tuple[Vector, Vector, float]:
    candidates = sorted(range(len(SPINE)), key=lambda index: abs(SPINE[index][0].y - y))
    index = candidates[0]
    point, _, side, width = section(index)
    return point, side, width


def create_deck(materials: dict[str, bpy.types.Material], root: bpy.types.Object) -> None:
    sand = materials["sand"] if "sand" in materials else materials["clay"]
    basalt = materials["basalt"] if "basalt" in materials else materials["clay"]
    for chunk, start in enumerate(range(0, len(SPINE) - 1, 5)):
        end = min(len(SPINE) - 1, start + 6)
        top_vertices: list[tuple[float, float, float]] = []
        for index in range(start, end + 1):
            point, _, side, width = section(index)
            edge_variation = 0.16 * math.sin(index * 5.1 + chunk)
            left = point - side * (width * 0.5 + edge_variation)
            right = point + side * (width * 0.5 - edge_variation * 0.6)
            top_vertices.extend((tuple(left), tuple(right)))
        faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(end - start)]
        cap = mesh_object(f"DeckCap_{chunk:02d}", top_vertices, faces, sand, root)
        cap["a2Role"] = "fractured cap; safe corridor remains modelling-only"
        for side_sign, label in ((-1.0, "Left"), (1.0, "Right")):
            vertices: list[tuple[float, float, float]] = []
            for index in range(start, end + 1):
                point, _, side, width = section(index)
                edge = point + side * side_sign * (width * 0.5 + 0.08)
                inset = point + side * side_sign * (width * 0.32)
                depth = 1.4 + 0.55 * math.sin(index * 1.7 + chunk)
                vertices.extend((tuple(edge), tuple(edge - Vector((0.0, 0.0, depth))), tuple(inset - Vector((0.0, 0.0, depth * 0.66)))))
            faces = []
            for local in range(end - start):
                a, b = local * 3, (local + 1) * 3
                faces.extend(((a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2)))
            strata = mesh_object(f"BrokenLip_{label}_{chunk:02d}", vertices, faces, basalt, root)
            strata["a2Role"] = "discontinuous outer lip / undercut"
            if chunk % 2 == (0 if side_sign < 0 else 1):
                for tooth in range(2):
                    idx = min(len(SPINE) - 2, start + 1 + tooth * max(1, (end - start - 1) // 2))
                    point, _, side, width = section(idx)
                    location = point + side * side_sign * (width * 0.58 + 0.4)
                    add_rock(f"BasaltTooth_{label}_{chunk}_{tooth}", tuple(location - Vector((0.0, 0.0, 1.1))), 0.55, 1.1, 1.8, basalt, root, 1000 + chunk * 13 + tooth, 6)
    for crack, index in enumerate((5, 12, 19, 28, 37, 45)):
        point, _, side, width = section(min(index, len(SPINE) - 2))
        for sign in (-1.0, 1.0):
            start = point + side * sign * (width * 0.18)
            end = point + side * sign * (width * 0.43)
            add_cone_between(f"EdgeCrack_{crack}_{sign}", start + Vector((0, 0, 0.025)), end + Vector((0, 0, 0.025)), 0.045, 0.018, basalt, root, 6)
    for rubble, index in enumerate((3, 9, 16, 24, 33, 41, 49)):
        point, _, side, width = section(min(index, len(SPINE) - 2))
        sign = -1.0 if rubble % 2 else 1.0
        loc = point + side * sign * (width * 0.63 + 0.55) - Vector((0, 0, 0.9))
        add_rock(f"EdgeRubble_{rubble}", tuple(loc), 0.4 + 0.12 * (rubble % 3), 0.65, 0.7 + 0.15 * (rubble % 2), basalt, root, 3000 + rubble, 6)


def create_panorama(root: bpy.types.Object, material: bpy.types.Material) -> None:
    vertices: list[tuple[float, float, float]] = []
    radius, center_y = 175.0, 46.0
    sides = 36
    for level, z in enumerate((-66.0, 72.0)):
        for index in range(sides):
            angle = math.tau * index / sides
            vertices.append((math.cos(angle) * radius, center_y + math.sin(angle) * radius, z + 8 * math.sin(angle * 2.0)))
    faces = []
    for index in range(sides):
        nxt = (index + 1) % sides
        faces.append((index, nxt, sides + nxt, sides + index))
    panorama = mesh_object("Panorama_Open_No_Caps", vertices, faces, material, root)
    panorama.visible_shadow = False
    panorama["a2Role"] = "open-ended inward panorama without cap/horizon"


def create_canyon(materials: dict[str, bpy.types.Material], root: bpy.types.Object, stage: str) -> None:
    basalt = materials.get("basalt", materials["clay"])
    abyss = materials["abyss"]
    create_panorama(root, abyss)
    rng = random.Random(SEED + 44)
    bands = [
        ("FarMesa", 14, 46.0, 72.0, (96.0, 190.0), (-36.0, -14.0), 6200),
        ("MidStack", 20, 16.0, 34.0, (38.0, 125.0), (-22.0, -6.0), 7200),
        ("NearCliff", 15, 5.0, 15.0, (-26.0, 58.0), (-10.0, 5.0), 8200),
    ]
    for label, count, lo_radius, hi_radius, y_range, z_range, seed_start in bands:
        for index in range(count):
            side = -1.0 if (index + (0 if label == "FarMesa" else 1)) % 2 else 1.0
            if label == "FarMesa":
                x = side * rng.uniform(lo_radius, hi_radius) + rng.uniform(-8.0, 8.0)
            elif label == "MidStack":
                x = side * rng.uniform(lo_radius, hi_radius)
            else:
                # Keep a corridor around the deck and break outer lips into clusters.
                y = rng.uniform(*y_range)
                point, side_vector, width = sample_road(y)
                x = point.x + side_vector.x * side * (width * 0.66 + rng.uniform(4.0, 11.0))
                y = point.y + side_vector.y * side * (width * 0.66 + rng.uniform(4.0, 11.0))
                z = point.z + rng.uniform(*z_range)
                add_rock(f"{label}_{index:02d}", (x, y, z), rng.uniform(2.5, 6.5), rng.uniform(3.0, 8.0), rng.uniform(7.0, 21.0), basalt, root, seed_start + index, rng.choice((6, 7, 8)))
                continue
            y = rng.uniform(*y_range)
            z = rng.uniform(*z_range)
            add_rock(f"{label}_{index:02d}", (x, y, z), rng.uniform(3.0, 12.0), rng.uniform(4.0, 14.0), rng.uniform(8.0, 33.0), basalt, root, seed_start + index, rng.choice((6, 7, 8)))
    if stage != "clay":
        add_cube("Bounded_Canyon_Mist", (0.0, 72.0, -11.0), (68.0, 92.0, 22.0), materials["fog"], root)
        bpy.context.object.visible_shadow = False


def ground_shadow(name: str, loc: Vector, scale: tuple[float, float, float], material: bpy.types.Material, parent: bpy.types.Object) -> None:
    bpy.ops.mesh.primitive_circle_add(vertices=20, radius=1.0, fill_type="TRIFAN", location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj.parent = parent


def add_socket(parent: bpy.types.Object, name: str, location: Vector) -> None:
    empty = parent_empty(name, tuple(location))
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.12
    empty.parent = parent


def create_runner(materials: dict[str, bpy.types.Material], root: bpy.types.Object) -> None:
    courier = materials.get("courier", materials["clay"])
    shadow = materials.get("shadow", materials["clay"])
    point, _, _ = sample_road(2.0)
    root.location = point + Vector((0.0, 0.0, 0.05))
    root["a2Role"] = "original articulated courier, forward run pose"
    ground_shadow("Runner_ContactShadow", Vector((0.0, 0.0, 0.015)), (0.78, 1.05, 1.0), shadow, root)
    add_cone_between("Runner_Torso_Coat", Vector((0.0, 0.0, 0.83)), Vector((0.12, 0.18, 1.8)), 0.42, 0.29, courier, root, 9)
    add_uv_sphere("Runner_HoodedHead", (0.18, 0.28, 2.06), (0.28, 0.26, 0.32), courier, root, 10)
    # Offset limbs make the running read directional rather than a standing toy.
    limb_data = [
        ("Runner_LeftArm", Vector((-0.22, 0.08, 1.62)), Vector((-0.54, 0.37, 1.22)), Vector((-0.30, 0.64, 0.94))),
        ("Runner_RightArm", Vector((0.30, 0.17, 1.58)), Vector((0.56, -0.22, 1.16)), Vector((0.72, -0.52, 0.94))),
        ("Runner_LeftLeg", Vector((-0.18, 0.02, 0.85)), Vector((-0.44, 0.34, 0.43)), Vector((-0.30, 0.65, 0.08))),
        ("Runner_RightLeg", Vector((0.22, 0.03, 0.86)), Vector((0.48, -0.34, 0.46)), Vector((0.68, -0.52, 0.08))),
    ]
    for name, hip, knee, foot in limb_data:
        add_cone_between(name + "_Upper", hip, knee, 0.14, 0.10, courier, root, 7)
        add_cone_between(name + "_Lower", knee, foot, 0.11, 0.075, courier, root, 7)
        add_rock(name + "_Boot", tuple(foot + Vector((0.03, 0.06, -0.05))), 0.16, 0.28, 0.12, courier, root, 9100 + len(name), 6)
        add_socket(root, "Socket_" + name + "_Contact", foot)
    tail = mesh_object("Runner_CoatTail", [(-0.28, -0.1, 1.3), (0.28, -0.1, 1.3), (0.10, -0.82, 0.62), (-0.12, -0.88, 0.72)], [(0, 1, 2, 3)], courier, root)
    tail["a2Role"] = "coat-tail/signal accent"


def create_pursuer(materials: dict[str, bpy.types.Material], root: bpy.types.Object) -> None:
    basalt = materials.get("basalt", materials["clay"])
    coral = materials.get("coral", materials["clay"])
    shadow = materials.get("shadow", materials["clay"])
    point, _, _ = sample_road(-11.0)
    root.location = point + Vector((0.0, 0.0, 0.04))
    root["a2Role"] = "low original four-limb basalt pursuer; grounded joints and narrow coral spine"
    ground_shadow("Pursuer_ContactShadow", Vector((0.0, 0.0, 0.015)), (1.55, 1.95, 1.0), shadow, root)
    add_rock("Pursuer_Carapace", (0.0, 0.10, 0.65), 1.05, 1.45, 1.05, basalt, root, 10101, 8)
    add_rock("Pursuer_Shoulder", (0.0, 0.86, 0.78), 0.92, 0.74, 0.88, basalt, root, 10102, 7)
    head = mesh_object("Pursuer_HeadWedge", [(-0.58, 1.4, 0.95), (0.58, 1.4, 0.95), (-0.36, 2.06, 0.75), (0.36, 2.06, 0.75), (-0.42, 1.52, 0.42), (0.42, 1.52, 0.42)], [(0, 1, 3, 2), (0, 2, 4), (1, 5, 3), (4, 2, 3, 5), (0, 4, 5, 1)], basalt, root)
    head["a2Role"] = "forward-facing low basalt head, not sphere"
    leg_data = [
        ("FrontLeft", Vector((-0.67, 0.88, 0.66)), Vector((-0.86, 1.2, 0.36)), Vector((-0.93, 1.47, 0.07))),
        ("FrontRight", Vector((0.67, 0.88, 0.66)), Vector((0.88, 1.15, 0.34)), Vector((0.94, 1.42, 0.07))),
        ("RearLeft", Vector((-0.76, -0.72, 0.63)), Vector((-0.96, -1.05, 0.34)), Vector((-0.84, -1.42, 0.07))),
        ("RearRight", Vector((0.76, -0.72, 0.63)), Vector((0.96, -1.00, 0.34)), Vector((0.86, -1.38, 0.07))),
    ]
    for name, shoulder, joint, foot in leg_data:
        add_cone_between("Pursuer_" + name + "_Upper", shoulder, joint, 0.18, 0.13, basalt, root, 7)
        add_cone_between("Pursuer_" + name + "_Lower", joint, foot, 0.14, 0.09, basalt, root, 7)
        add_rock("Pursuer_" + name + "_Paw", tuple(foot + Vector((0.0, 0.08, -0.05))), 0.20, 0.32, 0.13, basalt, root, 10300 + len(name), 6)
        add_socket(root, "Socket_Pursuer_" + name + "_Foot", foot)
    for index in range(5):
        y = -0.62 + index * 0.36
        plate = mesh_object(f"Pursuer_CoralSpine_{index}", [(-0.12, y - 0.12, 1.43), (0.12, y - 0.12, 1.43), (0.0, y + 0.08, 1.84), (0.0, y + 0.20, 1.40)], [(0, 1, 2), (0, 2, 3), (1, 3, 2)], coral, root)
        plate["a2Role"] = "narrow coral dorsal plate"
    add_socket(root, "Collision_Pursuer_Body", Vector((0.0, 0.1, 0.7)))


def create_ring(materials: dict[str, bpy.types.Material], root: bpy.types.Object) -> None:
    sand = materials.get("sand", materials["clay"])
    shadow = materials.get("shadow", materials["clay"])
    point, _, _ = sample_road(48.0)
    root.location = point + Vector((0.0, 0.0, 0.05))
    root["a2Role"] = "supported broken stone arch with physical opening"
    ground_shadow("Ring_ContactShadow", Vector((0.0, 0.0, 0.01)), (2.75, 1.25, 1.0), shadow, root)
    for side in (-1.0, 1.0):
        for level in range(3):
            add_rock(f"Ring_Support_{'L' if side < 0 else 'R'}_{level}", (side * 2.55 + 0.12 * level * side, 0.0, 0.35 + level * 0.72), 0.48, 0.62, 0.78, sand, root, 11100 + level + (10 if side > 0 else 0), 6)
    radius = 2.55
    for index in range(9):
        if index == 4:  # a clearly authored broken crown, never a fake solid torus.
            continue
        theta = math.pi * index / 8.0
        x, z = math.cos(theta) * radius, 1.85 + math.sin(theta) * radius
        add_cube(f"Ring_Voussoir_{index}", (x, 0.0, z), (0.43, 0.56, 0.72), sand, root, (0.0, theta - math.pi * 0.5, 0.0))
    add_rock("Ring_CrownDebris", (0.55, 0.25, 3.35), 0.34, 0.47, 0.42, sand, root, 11201, 6)
    add_socket(root, "Collision_Ring_Opening", Vector((0.0, 0.0, 2.0)))


def create_tide_scar(material: bpy.types.Material, output_root: bpy.types.Object | None = None) -> bpy.types.Object:
    curve = bpy.data.curves.new("TideScar_Ribbon_Editable_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.085
    curve.bevel_resolution = 2
    curve.resolution_u = 8
    curve.materials.append(material)
    intervals = ((2, 7), (9, 14), (17, 23), (27, 33), (36, 42), (45, 50))
    last = len(SPINE) - 1
    for interval_index, (start, requested_end) in enumerate(intervals):
        if start > last:
            continue
        end = min(requested_end, last)
        spline = curve.splines.new("NURBS")
        spline.points.add(end - start)
        for offset, index in enumerate(range(start, end + 1)):
            point, _, side, width = section(index)
            inset = width * (0.32 + 0.035 * math.sin(index * 1.9))
            p = point + side * inset + Vector((0.0, 0.0, 0.055))
            spline.points[offset].co = (p.x, p.y, p.z, 1.0)
        spline.order_u = min(3, end - start + 1)
        spline.use_endpoint_u = True
    obj = bpy.data.objects.new("TideScar_Ribbon_Editable", curve)
    bpy.context.collection.objects.link(obj)
    obj["a2Role"] = "editable right-edge warm-white road scar; non-emissive; not baked"
    if output_root:
        obj.parent = output_root
    return obj


def create_lighting() -> None:
    bpy.ops.object.light_add(type="SUN", location=(18.0, -30.0, 44.0))
    sun = bpy.context.object
    sun.name = "Warm_Daylight_Sun"
    sun.data.energy = 2.8
    sun.data.angle = math.radians(16.0)
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(28))
    bpy.ops.object.light_add(type="AREA", location=(-16.0, -17.0, 27.0))
    key = bpy.context.object
    key.name = "Warm_Causeway_Key"
    key.data.energy = 2800.0
    key.data.shape = "DISK"
    key.data.size = 13.0
    key.data.color = (1.0, 0.55, 0.31)
    key.rotation_euler = (math.radians(23), 0.0, math.radians(-21))
    bpy.ops.object.light_add(type="AREA", location=(12.0, -21.0, 17.0))
    fill = bpy.context.object
    fill.name = "Cool_Canyon_Fill"
    fill.data.energy = 1800.0
    fill.data.shape = "DISK"
    fill.data.size = 18.0
    fill.data.color = (0.22, 0.52, 1.0)
    fill.rotation_euler = (math.radians(58), 0.0, math.radians(151))


def camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], fov: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name + "_Data")
    data.lens = 42.0
    data.clip_start = 0.1
    data.clip_end = 500.0
    data.angle = math.radians(fov)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def render(camera_obj: bpy.types.Object, path: Path, resolution: tuple[int, int], samples: int) -> None:
    scene = bpy.context.scene
    scene.camera = camera_obj
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        scene.eevee.taa_samples = samples
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def metadata(output: Path, stage: str) -> None:
    triangles = sum(len(poly.vertices) - 2 for mesh in bpy.data.meshes for poly in mesh.polygons)
    data = {
        "schema": "temple-tr3-a2-structural-proof-v1",
        "stage": stage,
        "generator": "generate_tide_scar_hero_a2.py",
        "seed": SEED,
        "units": "metres",
        "axes": {"forward": "+Y", "up": "+Z", "right": "+X"},
        "stableRoots": ROOT_NAMES,
        "trianglesBeforeExport": triangles,
        "materials": sorted(material.name for material in bpy.data.materials),
        "textureMapping": {
            "M_Sandstone": ["a2-sandstone-base.png", "a2-sandstone-normal.png", "a2-sandstone-orm.png"],
            "M_Basalt": ["a2-basalt-base.png", "a2-basalt-normal.png", "a2-basalt-orm.png"],
            "M_Coral_Mineral": ["a2-coral-mask.png"],
        } if stage == "final" else {},
        "semanticHandoff": {
            "Causeway_Root": {"pivot": "road origin", "proxy": "Collision_Causeway_Corridor"},
            "Canyon_Root": {"pivot": "world origin", "proxy": "presentation only"},
            "Runner_Root": {"pivot": "ground at courier", "sockets": ["Socket_Runner_LeftLeg_Contact", "Socket_Runner_RightLeg_Contact"]},
            "Pursuer_Root": {"pivot": "ground at pursuer", "proxy": "Collision_Pursuer_Body"},
            "Obstacle_Ring_Root": {"pivot": "ring ground center", "proxy": "Collision_Ring_Opening"},
            "TideScar_Ribbon_Editable": {"pivot": "curve world coordinates", "curve": True, "emissive": False, "bakedIntoRoad": False},
        },
        "structure": {"directionChanges": 4, "noWaterPlane": True, "panoramaEndCaps": False, "mistCards": 0, "causewayPrism": True, "sideStrataChunked": True},
        "cleanRoom": "Generated locally from deterministic Blender Python; no source image, external model, commercial asset, or reference pixel is read.",
    }
    (output / ("a2-clay-scene-metadata.json" if stage == "clay" else "a2-scene-metadata.json")).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_scene(output: Path, stage: str) -> None:
    reset_scene()
    mats = materials(output, stage)
    causeway = parent_empty("Causeway_Root")
    canyon = parent_empty("Canyon_Root")
    runner = parent_empty("Runner_Root")
    pursuer = parent_empty("Pursuer_Root")
    ring = parent_empty("Obstacle_Ring_Root")
    create_deck(mats, causeway)
    create_canyon(mats, canyon, stage)
    create_runner(mats, runner)
    create_pursuer(mats, pursuer)
    create_ring(mats, ring)
    create_tide_scar(mats.get("scar", mats["clay"]), causeway)
    add_socket(causeway, "Collision_Causeway_Corridor", Vector((0.0, 50.0, 0.8)))
    create_lighting()
    if stage == "clay":
        bpy.context.scene.view_layers[0].material_override = mats["clay"]


def main() -> None:
    args = arguments()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    build_scene(output, args.stage)
    portrait = camera("A2_HeroCamera_Portrait", (0.0, -39.0, 20.5), (0.3, 35.0, 1.3), 45.0)
    desktop = camera("A2_HeroCamera_Desktop", (-1.5, -42.0, 18.0), (0.5, 40.0, 1.5), 43.0)
    if args.stage == "clay":
        render(portrait, output / "a2-clay-portrait.png", (480, 854), 20)
        render(desktop, output / "a2-clay-desktop.png", (854, 480), 20)
        close = camera("A2_ClayCloseup", (5.5, -18.0, 7.5), (0.0, -2.0, 1.0), 52.0)
        render(close, output / "a2-clay-silhouette-closeup.png", (640, 480), 20)
        metadata(output, "clay")
        return
    render(portrait, output / "portrait-hero.png", (900, 1600), 48)
    render(desktop, output / "desktop-hero.png", (1600, 900), 48)
    close = camera("A2_FinalCloseup", (6.5, -20.0, 8.0), (0.0, -2.0, 1.1), 52.0)
    render(close, output / "runner-pursuer-obstacle-closeup.png", (1200, 900), 48)
    metadata(output, "final")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "tide-scar-hero-a2.blend"))
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(output / "tide-scar-hero-a2.unoptimized.glb"), export_format="GLB", use_selection=False,
        export_apply=True, export_yup=True, export_materials="EXPORT", export_cameras=True, export_lights=True, export_extras=True,
    )


if __name__ == "__main__":
    main()
