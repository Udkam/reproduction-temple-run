"""Blender 4.5.5 generator for the sole TEMPLE-TR4 diagnostic batch.

The scene is clean-room procedural geometry.  It emits no blend/GLB and performs
exactly twenty ordered ``write_still`` calls from the contract-bound cameras.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Any, Iterable

import bpy
from mathutils import Matrix, Vector


EXPECTED_SCHEMA = "tide-relay.temple-tr4.asset-preflight"
EXPECTED_CONTRACT = "TEMPLE-TR4-C6"
EXPECTED_SEED = 1414090053
EXPECTED_BLENDER_VERSION = "4.5.5 LTS"
DIAGNOSTIC_ID = "006"
ROOT_NAMES = [
    "TR4_Road_Modules", "TR4_Canyon_Modules", "TR4_Runner_Rig",
    "TR4_Pursuer_Cinematic", "TR4_Hazard_Beam", "TR4_Hazard_Ring",
    "TR4_Hazard_Column", "TR4_Gap_Lips", "TR4_TideScar_Path",
]
PASS_ORDER = ["beauty", "object-id", "road-mask", "normal", "linear-depth"]
PROFILE_ORDER = ["portrait", "desktop", "landscape", "closeup"]
ID_COLORS = {
    "background": "#000000", "road": "#D9B98C", "canyon": "#1B2935",
    "runner": "#F2EAD7", "pursuer": "#101820", "beam": "#B44A38",
    "ring": "#E69648", "column": "#6D4834", "gap-lips": "#7A2221",
    "tide-scar": "#FFFFFF",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hex_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4))


def srgb_to_linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def linear_rgb(value: str) -> tuple[float, float, float]:
    return tuple(srgb_to_linear(component) for component in hex_rgb(value))


def validate_input(preflight_path: Path, output_root: Path) -> dict[str, Any]:
    if preflight_path.name != "preflight.json" or preflight_path.parent != output_root:
        raise RuntimeError("preflight must be the exact diagnostic-root preflight.json")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    top_keys = [
        "schemaId", "schemaVersion", "contractVersion", "seed", "reference", "tools",
        "scripts", "scene", "cameras", "construction", "collision", "materials",
        "semanticRoots", "budgets", "outputs", "constructionHash", "verdict",
    ]
    if not isinstance(preflight, dict) or sorted(preflight.keys()) != sorted(top_keys):
        raise RuntimeError("preflight top-level schema mismatch")
    schema_version = preflight.get("schemaVersion")
    if (
        preflight.get("schemaId") != EXPECTED_SCHEMA
        or isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != 6
    ):
        raise RuntimeError("unsupported preflight schema")
    if preflight.get("contractVersion") != EXPECTED_CONTRACT or preflight.get("seed") != EXPECTED_SEED:
        raise RuntimeError("contract/seed mismatch")
    if preflight.get("tools", {}).get("pythonVersion") != "3.12.0":
        raise RuntimeError("frozen runner Python version mismatch")
    if preflight.get("verdict") != "READY_FOR_BLENDER":
        raise RuntimeError("preflight verdict is not READY_FOR_BLENDER")
    if bpy.app.version_string != EXPECTED_BLENDER_VERSION:
        raise RuntimeError(f"Blender version mismatch: {bpy.app.version_string}")
    generator_record = preflight.get("scripts", {}).get("generator", {})
    if Path(generator_record.get("path", "")).resolve(strict=True) != Path(__file__).resolve(strict=True):
        raise RuntimeError("generator path mismatch")
    if generator_record.get("sha256") != sha256_file(Path(__file__).resolve(strict=True)):
        raise RuntimeError("generator hash mismatch")
    if [record.get("name") for record in preflight.get("semanticRoots", [])] != ROOT_NAMES:
        raise RuntimeError("semantic root contract mismatch")
    construction_bytes = (
        json.dumps(preflight["construction"], ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if hashlib.sha256(construction_bytes).hexdigest() != preflight["constructionHash"]:
        raise RuntimeError("construction hash mismatch")
    camera_keys = [
        "profile", "resolution", "diagnosticResolution", "position", "target", "up",
        "verticalFovDegrees", "aspect", "near", "far", "lensShiftY", "viewMatrix",
        "projectionMatrix", "projectionAnchors",
    ]
    anchor_keys = [
        "runnerAnchor", "runnerHead", "runnerFootL", "runnerFootR", "beam", "ring",
        "column", "gap", "scar", "routeCenter", "farRoute",
    ]
    cameras = preflight.get("cameras")
    if not isinstance(cameras, list) or [record.get("profile") for record in cameras] != PROFILE_ORDER:
        raise RuntimeError("camera profile order mismatch")
    for record in cameras:
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(camera_keys):
            raise RuntimeError(f"camera schema mismatch: {record.get('profile')}")
        if not isinstance(record["projectionAnchors"], dict):
            raise RuntimeError(f"projection anchor object mismatch: {record.get('profile')}")
        if sorted(record["projectionAnchors"].keys()) != sorted(anchor_keys):
            raise RuntimeError(f"projection anchor key-set mismatch: {record.get('profile')}")
    lighting = preflight["construction"].get("lighting")
    if not isinstance(lighting, dict) or sorted(lighting.keys()) != sorted([
        "worldColor", "worldStrength", "fogColor", "fogDensity", "fogAnisotropy",
        "key", "fill", "contact",
    ]):
        raise RuntimeError("lighting construction schema mismatch")
    outputs = preflight.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != 20:
        raise RuntimeError("closed output list mismatch")
    expected_order = [(profile, pass_name) for profile in PROFILE_ORDER for pass_name in PASS_ORDER]
    actual_order = [(record.get("profile"), record.get("pass")) for record in outputs]
    if actual_order != expected_order or [record.get("index") for record in outputs] != list(range(20)):
        raise RuntimeError("output order mismatch")
    expected_names = [f"tr4-diagnostic-006-{profile}-{pass_name}.png" for profile, pass_name in expected_order]
    if [record.get("relativePath") for record in outputs] != expected_names:
        raise RuntimeError("diagnostic-006 output filename mismatch")
    if any((output_root / record["relativePath"]).exists() for record in outputs):
        raise RuntimeError("a PNG output already exists")
    return preflight


def validate_camera_probe_input(plan_path: Path, output_root: Path) -> dict[str, Any]:
    if plan_path.name != "probe-plan.json" or plan_path.parent != output_root:
        raise RuntimeError("camera probe plan must be the exact probe-root probe-plan.json")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected_keys = [
        "schemaId", "schemaVersion", "probeId", "blenderExecutable", "blenderVersion",
        "scripts", "cameras", "matrixElement", "verdict",
    ]
    if sorted(plan.keys()) != sorted(expected_keys):
        raise RuntimeError("camera probe plan key mismatch")
    if plan["schemaId"] != "tide-relay.temple-tr4.camera-probe-plan" or plan["schemaVersion"] != 1 or plan["probeId"] != "001":
        raise RuntimeError("camera probe plan schema mismatch")
    if plan["blenderVersion"] != "4.5.5 LTS" or bpy.app.version_string != plan["blenderVersion"]:
        raise RuntimeError(f"camera probe Blender version mismatch: {bpy.app.version_string}")
    if plan["matrixElement"] != [2, 1] or plan["verdict"] != "READY_FOR_CAMERA_PROBE":
        raise RuntimeError("camera probe matrix/verdict mismatch")
    scripts = plan.get("scripts")
    if not isinstance(scripts, dict) or sorted(scripts.keys()) != ["generator", "runner"]:
        raise RuntimeError("camera probe scripts mismatch")
    generator_path = Path(scripts["generator"]["path"]).resolve(strict=True)
    runner_path = Path(scripts["runner"]["path"]).resolve(strict=True)
    if generator_path != Path(__file__).resolve(strict=True) or scripts["generator"]["sha256"] != sha256_file(generator_path):
        raise RuntimeError("camera probe generator provenance mismatch")
    if runner_path.name != "run_tide_scar_tr4_pack.py" or scripts["runner"]["sha256"] != sha256_file(runner_path):
        raise RuntimeError("camera probe runner provenance mismatch")
    cameras = plan.get("cameras")
    if not isinstance(cameras, list) or [record.get("profile") for record in cameras] != PROFILE_ORDER:
        raise RuntimeError("camera probe profile order mismatch")
    if (output_root / "camera-response.json").exists():
        raise RuntimeError("camera response must not pre-exist")
    return plan


def validate_matrix_probe_input(plan_path: Path, output_root: Path) -> dict[str, Any]:
    if plan_path.name != "matrix-probe-plan.json" or plan_path.parent != output_root:
        raise RuntimeError("matrix probe plan must be the exact probe-root matrix-probe-plan.json")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected_keys = [
        "schemaId", "schemaVersion", "probeId", "repoRoot", "blenderExecutable",
        "blenderExecutableSha256", "expectedBlenderVersion", "scripts",
        "frozenEvidence", "cameras", "verdict",
    ]
    if sorted(plan.keys()) != sorted(expected_keys):
        raise RuntimeError("matrix probe plan key mismatch")
    if plan["schemaId"] != "tide-relay.temple-tr4.matrix-probe-plan" or plan["schemaVersion"] != 1 or plan["probeId"] != "001":
        raise RuntimeError("matrix probe plan identity mismatch")
    repo_root = Path(plan["repoRoot"]).resolve(strict=True)
    if repo_root != Path(r"E:\Proj\Game-1-temple").resolve(strict=True):
        raise RuntimeError("matrix probe repository root mismatch")
    blender_path = Path(plan["blenderExecutable"]).resolve(strict=True)
    if blender_path != Path(r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe").resolve(strict=True):
        raise RuntimeError("matrix probe Blender path mismatch")
    if plan["blenderExecutableSha256"] != sha256_file(blender_path):
        raise RuntimeError("matrix probe Blender executable hash mismatch")
    if plan["expectedBlenderVersion"] != "4.5.5 LTS" or bpy.app.version_string != plan["expectedBlenderVersion"]:
        raise RuntimeError(f"matrix probe Blender version mismatch: {bpy.app.version_string}")
    scripts = plan.get("scripts")
    if not isinstance(scripts, dict) or sorted(scripts.keys()) != ["generator", "runner"]:
        raise RuntimeError("matrix probe script schema mismatch")
    for script_name, expected_filename in (("generator", "generate_tide_scar_tr4_pack.py"), ("runner", "run_tide_scar_tr4_pack.py")):
        record = scripts[script_name]
        if not isinstance(record, dict) or sorted(record.keys()) != ["path", "sha256"]:
            raise RuntimeError(f"matrix probe script record mismatch: {script_name}")
        path = Path(record["path"]).resolve(strict=True)
        if path.name != expected_filename or record["sha256"] != sha256_file(path):
            raise RuntimeError(f"matrix probe script provenance mismatch: {script_name}")
    if Path(scripts["generator"]["path"]).resolve(strict=True) != Path(__file__).resolve(strict=True):
        raise RuntimeError("matrix probe generator path mismatch")
    evidence_paths = {
        "diagnostic001Preflight": "docs/workstreams/temple-tr4-asset/diagnostic-001/preflight.json",
        "diagnostic001Plan": "docs/workstreams/temple-tr4-asset/diagnostic-001/planned-manifest.json",
        "diagnostic001BlenderLog": "docs/workstreams/temple-tr4-asset/diagnostic-001/blender.log",
        "diagnostic001Status": "docs/workstreams/temple-tr4-asset/diagnostic-001/diagnostic-status.json",
        "diagnostic002Preflight": "docs/workstreams/temple-tr4-asset/diagnostic-002/preflight.json",
        "diagnostic002Plan": "docs/workstreams/temple-tr4-asset/diagnostic-002/planned-manifest.json",
        "diagnostic002BlenderLog": "docs/workstreams/temple-tr4-asset/diagnostic-002/blender.log",
        "diagnostic002Status": "docs/workstreams/temple-tr4-asset/diagnostic-002/diagnostic-status.json",
        "cameraProbe001Plan": "docs/workstreams/temple-tr4-asset/camera-probe-001/probe-plan.json",
        "cameraProbe001BlenderLog": "docs/workstreams/temple-tr4-asset/camera-probe-001/blender.log",
        "cameraProbe001Status": "docs/workstreams/temple-tr4-asset/camera-probe-001/probe-status.json",
        "evaluator": "tools/temple-asset-pipeline/evaluate_tide_scar_tr4_pack.py",
    }
    evidence = plan.get("frozenEvidence")
    if not isinstance(evidence, dict) or sorted(evidence.keys()) != sorted(evidence_paths.keys()):
        raise RuntimeError("matrix probe frozen-evidence schema mismatch")
    for name, relative_path in evidence_paths.items():
        if evidence[name] != sha256_file(repo_root / relative_path):
            raise RuntimeError(f"matrix probe frozen evidence mismatch: {name}")
    cameras = plan.get("cameras")
    expected_camera_keys = ["profile", "diagnosticResolution", "position", "target", "verticalFovDegrees", "near", "far"]
    if not isinstance(cameras, list) or [record.get("profile") for record in cameras] != PROFILE_ORDER:
        raise RuntimeError("matrix probe camera order mismatch")
    for camera in cameras:
        if not isinstance(camera, dict) or sorted(camera.keys()) != sorted(expected_camera_keys):
            raise RuntimeError(f"matrix probe camera schema mismatch: {camera.get('profile') if isinstance(camera, dict) else '?'}")
    if plan["verdict"] != "READY_FOR_MATRIX_PROBE":
        raise RuntimeError("matrix probe plan verdict mismatch")
    if (repo_root / "docs/workstreams/temple-tr4-asset/diagnostic-003").exists():
        raise RuntimeError("matrix probe cannot coexist with unauthorized diagnostic-003")
    if {path.name for path in output_root.iterdir() if path.is_file()} != {"matrix-probe-plan.json"}:
        raise RuntimeError("matrix probe root contains unexpected pre-process files")
    return plan


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    return obj


def create_pbr_material(record: dict[str, Any], seed_offset: float) -> bpy.types.Material:
    material = bpy.data.materials.new(record["name"])
    material.use_nodes = True
    material.diffuse_color = (*linear_rgb(record["baseColor"]), 1.0)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")
    noise.inputs["Scale"].default_value = 4.5 + seed_offset * 0.43
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.68
    noise.inputs["Distortion"].default_value = 0.12 + (seed_offset % 3.0) * 0.04
    base = linear_rgb(record["baseColor"])
    darker = tuple(max(0.0, channel * (0.64 + 0.02 * (seed_offset % 4.0))) for channel in base)
    lighter = tuple(min(1.0, channel * 1.12 + 0.018) for channel in base)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (*darker, 1.0)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (*lighter, 1.0)
    bump.inputs["Strength"].default_value = record["normalStrength"]
    bump.inputs["Distance"].default_value = 0.075 if record["name"] not in ("cloth", "skin") else 0.025
    principled.inputs["Roughness"].default_value = record["roughness"]
    principled.inputs["Metallic"].default_value = record["metallic"]
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
    *,
    smooth: bool = False,
    bevel: float = 0.0,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + ".Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    obj["tr4_semantic"] = semantic
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    if bevel > 0.0:
        modifier = obj.modifiers.new("Eroded edge bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        modifier.limit_method = "ANGLE"
    return obj


def add_uv_ellipsoid(
    name: str,
    center: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
    *,
    segments: int = 20,
    rings: int = 12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.parent = parent
    obj["tr4_semantic"] = semantic
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def add_tapered_limb(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    start_radius: float,
    end_radius: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
) -> bpy.types.Object:
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    length = direction.length
    if length <= 1.0e-5:
        raise RuntimeError(f"degenerate limb: {name}")
    bpy.ops.mesh.primitive_cone_add(
        vertices=16,
        radius1=end_radius,
        radius2=start_radius,
        depth=length,
        end_fill_type="NGON",
        location=(start_vector + end_vector) * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.parent = parent
    obj["tr4_semantic"] = semantic
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Anatomical edge", "BEVEL")
    bevel.width = min(start_radius, end_radius) * 0.22
    bevel.segments = 2
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def create_road_module(
    index: int,
    start_z: float,
    end_z: float,
    root: bpy.types.Object,
    materials: dict[str, bpy.types.Material],
    rng: random.Random,
) -> list[bpy.types.Object]:
    signature = ["terrace-fracture", "buttress-recess", "collapsed-lip", "strata-undercut", "rubble-shoulder", "split-ledge"][index % 6]
    sample_count = 5
    thickness = 0.62 + 0.08 * (index % 6)
    vertices: list[tuple[float, float, float]] = []
    for sample in range(sample_count):
        t = sample / (sample_count - 1)
        z = start_z + (end_z - start_z) * t
        left = -3.2 + rng.uniform(-0.13, 0.07)
        right = 3.2 + rng.uniform(-0.07, 0.13)
        vertices.extend(
            [
                (left, 0.0, z), (right, 0.0, z),
                (left + rng.uniform(0.08, 0.22), -thickness - rng.uniform(0.0, 0.16), z + rng.uniform(-0.06, 0.06)),
                (right - rng.uniform(0.08, 0.22), -thickness - rng.uniform(0.0, 0.16), z + rng.uniform(-0.06, 0.06)),
            ]
        )
    faces: list[tuple[int, ...]] = []
    for sample in range(sample_count - 1):
        a = sample * 4
        b = (sample + 1) * 4
        faces.extend(
            [
                (a, a + 1, b + 1, b),
                (a, b, b + 2, a + 2),
                (a + 1, a + 3, b + 3, b + 1),
                (a + 2, b + 2, b + 3, a + 3),
            ]
        )
    faces.extend([(0, 2, 3, 1), ((sample_count - 1) * 4, (sample_count - 1) * 4 + 1, (sample_count - 1) * 4 + 3, (sample_count - 1) * 4 + 2)])
    module = mesh_object(
        f"Road.Module.{index:02d}.{signature}", vertices, faces, materials["sandstone"], root, "road",
        bevel=0.055,
    )
    module["signature"] = signature
    result = [module]

    # Two separated structural masses per side create real downward depth without a wall strip.
    span = abs(end_z - start_z)
    for side in (-1.0, 1.0):
        for fragment in range(2):
            local_t = 0.25 + 0.48 * fragment + rng.uniform(-0.07, 0.07)
            center_z = start_z + (end_z - start_z) * local_t
            depth = 2.7 + ((index * 7 + fragment * 3) % 11) * 0.37
            radius = 0.72 + rng.uniform(0.0, 0.58)
            fragment_obj = create_rock_spire(
                f"Road.SideMass.{index:02d}.{('L' if side < 0 else 'R')}.{fragment}",
                (side * (3.42 + rng.uniform(0.0, 0.36)), -depth, center_z),
                radius,
                depth + 0.15,
                9 + ((index + fragment) % 3),
                materials["fresh-break" if fragment == 0 else "sandstone"],
                root,
                "road",
                rng,
                top_taper=0.38,
            )
            result.append(fragment_obj)
            # Authored ledge/strata event, always outside the protected corridor.
            ledge_y = -0.72 - fragment * 0.64 - 0.08 * (index % 3)
            ledge_vertices = [
                (side * 3.18, ledge_y + 0.11, center_z - span * 0.16),
                (side * (3.78 + radius * 0.25), ledge_y + 0.04, center_z - span * 0.12),
                (side * (3.72 + radius * 0.32), ledge_y - 0.16, center_z + span * 0.12),
                (side * 3.22, ledge_y - 0.12, center_z + span * 0.16),
            ]
            result.append(mesh_object(
                f"Road.Strata.{index:02d}.{('L' if side < 0 else 'R')}.{fragment}",
                ledge_vertices,
                [(0, 1, 2, 3)],
                materials["fresh-break"], root, "road", bevel=0.025,
            ))
        # One rubble cluster per module side, beyond X=3.2.
        rubble_z = start_z + (end_z - start_z) * (0.36 if side < 0 else 0.67)
        for rubble in range(2):
            result.append(create_rock_spire(
                f"Road.Rubble.{index:02d}.{('L' if side < 0 else 'R')}.{rubble}",
                (side * (3.46 + rubble * 0.24 + rng.uniform(0.0, 0.12)), -0.42, rubble_z + rubble * 0.34),
                0.18 + rubble * 0.07,
                0.52 + rubble * 0.21,
                7,
                materials["sandstone"], root, "road", rng, top_taper=0.24,
            ))
    return result


def create_rock_spire(
    name: str,
    base_center: tuple[float, float, float],
    radius: float,
    height: float,
    segments: int,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
    rng: random.Random,
    *,
    top_taper: float = 0.12,
) -> bpy.types.Object:
    ring_fractions = [0.0, 0.16, 0.34, 0.52, 0.69, 0.83, 0.94, 1.0]
    radial_profile = [0.88, 1.08, 0.78, 1.02, 0.70, 0.82, 0.44, top_taper]
    vertices: list[tuple[float, float, float]] = []
    phase = rng.uniform(0.0, math.tau)
    for ring_index, fraction in enumerate(ring_fractions):
        center_x = base_center[0] + math.sin(phase + fraction * 4.1) * radius * 0.12
        center_z = base_center[2] + math.cos(phase * 0.7 + fraction * 3.7) * radius * 0.11
        y = base_center[1] + height * fraction
        for segment in range(segments):
            angle = math.tau * segment / segments + phase
            jag = 0.82 + 0.25 * math.sin(segment * 2.37 + ring_index * 1.73 + phase)
            ring_radius = radius * radial_profile[ring_index] * jag
            x = center_x + math.cos(angle) * ring_radius
            z = center_z + math.sin(angle) * ring_radius * (0.74 + 0.08 * math.sin(phase))
            vertices.append((x, y, z))
    faces: list[tuple[int, ...]] = []
    for ring in range(len(ring_fractions) - 1):
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            a = ring * segments + segment
            b = ring * segments + next_segment
            c = (ring + 1) * segments + next_segment
            d = (ring + 1) * segments + segment
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(tuple(range(segments)))))
    faces.append(tuple((len(ring_fractions) - 1) * segments + segment for segment in range(segments)))
    return mesh_object(name, vertices, faces, material, parent, semantic, smooth=True, bevel=0.035)


def create_canyon(
    root: bpy.types.Object,
    materials: dict[str, bpy.types.Material],
    rng: random.Random,
) -> None:
    bands = [
        ("near", 8, (8.0, 16.0), (-100.0, -10.0), -9.5, (11.0, 19.0), (2.6, 5.0)),
        ("mid", 10, (18.0, 34.0), (-140.0, -20.0), -13.5, (16.0, 28.0), (4.0, 7.0)),
        ("far", 12, (38.0, 70.0), (-180.0, -35.0), -18.0, (22.0, 42.0), (6.0, 11.0)),
    ]
    for band_index, (band, count, x_range, z_range, base_y, height_range, radius_range) in enumerate(bands):
        for index in range(count):
            side = -1.0 if index % 2 == 0 else 1.0
            progression = (index // 2 + 0.36) / max(1.0, count / 2.0)
            abs_x = x_range[0] + (x_range[1] - x_range[0]) * (0.18 + 0.70 * ((index * 0.37 + band_index * 0.13) % 1.0))
            z = z_range[1] + (z_range[0] - z_range[1]) * min(0.94, progression + rng.uniform(-0.10, 0.10))
            height = rng.uniform(*height_range)
            radius = rng.uniform(*radius_range)
            material = materials["basalt" if (index + band_index) % 3 else "basalt-strata"]
            spire = create_rock_spire(
                f"Canyon.{band}.{index:02d}", (side * abs_x, base_y + rng.uniform(-1.0, 1.0), z),
                radius, height, 10 + ((index + band_index) % 3), material, root, "canyon", rng,
                top_taper=0.05 + 0.06 * ((index + 2) % 3),
            )
            spire["depthBand"] = band
            spire["signature"] = f"{band}-{index:02d}"
            # Two non-continuous strata ledges strengthen scale and material response.
            for ledge_index, fraction in enumerate((0.34, 0.62)):
                ledge_radius = radius * (0.94 - ledge_index * 0.18)
                ledge_y = base_y + height * fraction
                create_rock_spire(
                    f"Canyon.{band}.{index:02d}.Ledge.{ledge_index}",
                    (side * abs_x + rng.uniform(-0.25, 0.25), ledge_y - 0.18, z + rng.uniform(-0.25, 0.25)),
                    ledge_radius, 0.34 + ledge_index * 0.12, 9,
                    materials["basalt-strata"], root, "canyon", rng, top_taper=0.72,
                )


def create_shoulder(root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    vertices = [
        (3.18, -0.04, 2.65), (4.12, -0.07, 2.78), (4.46, -0.12, 3.34),
        (4.52, -0.10, 4.58), (4.18, -0.06, 5.25), (3.18, -0.03, 5.36),
        (3.25, -0.74, 2.76), (4.02, -0.92, 2.92), (4.24, -1.08, 3.45),
        (4.28, -1.02, 4.48), (4.02, -0.86, 5.08), (3.26, -0.72, 5.22),
    ]
    faces = [(0, 1, 2, 3, 4, 5), (6, 11, 10, 9, 8, 7)]
    for index in range(6):
        faces.append((index, (index + 1) % 6, ((index + 1) % 6) + 6, index + 6))
    mesh_object("Road.NearLoopShoulder", vertices, faces, materials["sandstone"], root, "road", bevel=0.06)


def add_curve(
    name: str,
    splines: list[list[tuple[float, float, float]]],
    width: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
    *,
    cyclic: bool = False,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name + ".Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = width * 0.5
    curve.bevel_resolution = 3
    curve.resolution_u = 12
    for points in splines:
        spline = curve.splines.new("NURBS")
        spline.points.add(len(points) - 1)
        for point, coordinate in zip(spline.points, points):
            point.co = (*coordinate, 1.0)
        spline.order_u = min(3, len(points))
        spline.use_endpoint_u = not cyclic
        spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    obj["tr4_semantic"] = semantic
    obj.data.materials.append(material)
    return obj


def create_tide_scar(preflight: dict[str, Any], root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    points = [tuple(point) for point in preflight["construction"]["tideScar"]["mainControlPoints"]]
    near_gap = (3.015, 0.061, -71.65)
    far_gap = (3.025, 0.061, -76.35)
    first = [(x, 0.061, z) for x, _y, z in points[:7]] + [near_gap]
    second = [far_gap] + [(x, 0.061, z) for x, _y, z in points[7:]]
    add_curve("TideScar.Main.Editable", [first, second], 0.092, materials["tide-scar"], root, "tide-scar")
    loop = [(x, 0.064, z) for x, _y, z in preflight["construction"]["tideScar"]["loopControlPoints"][:-1]]
    add_curve("TideScar.NearLoop.Editable", [loop], 0.086, materials["tide-scar"], root, "tide-scar", cyclic=True)


def create_runner_pose(
    name: str,
    parent: bpy.types.Object,
    materials: dict[str, bpy.types.Material],
    *,
    failure: bool,
) -> bpy.types.Object:
    pose = make_empty(name, parent)
    semantic = "runner"
    if not failure:
        pelvis = (0.0, 1.03, 0.04)
        chest = (0.0, 1.58, -0.12)
        head = (0.0, 2.05, -0.25)
        hips = {"L": (-0.23, 0.96, 0.02), "R": (0.23, 0.96, 0.02)}
        knees = {"L": (-0.27, 0.57, -0.26), "R": (0.27, 0.55, 0.27)}
        ankles = {"L": (-0.25, 0.17, -0.43), "R": (0.25, 0.16, 0.36)}
        feet = {"L": (-0.25, 0.085, -0.56), "R": (0.25, 0.08, 0.22)}
        shoulders = {"L": (-0.32, 1.78, -0.16), "R": (0.32, 1.78, -0.16)}
        elbows = {"L": (-0.43, 1.43, 0.12), "R": (0.43, 1.39, -0.44)}
        hands = {"L": (-0.39, 1.13, 0.24), "R": (0.39, 1.12, -0.56)}
    else:
        pelvis = (0.28, 0.66, 0.06)
        chest = (0.46, 1.08, -0.34)
        head = (0.57, 1.46, -0.62)
        hips = {"L": (0.06, 0.61, 0.02), "R": (0.45, 0.59, 0.09)}
        knees = {"L": (-0.17, 0.29, -0.31), "R": (0.73, 0.30, 0.27)}
        ankles = {"L": (-0.38, 0.14, -0.62), "R": (0.91, 0.13, 0.43)}
        feet = {"L": (-0.48, 0.075, -0.72), "R": (1.02, 0.075, 0.48)}
        shoulders = {"L": (0.18, 1.19, -0.36), "R": (0.70, 1.15, -0.40)}
        elbows = {"L": (-0.03, 0.77, -0.62), "R": (0.94, 0.76, -0.22)}
        hands = {"L": (-0.18, 0.47, -0.79), "R": (1.10, 0.47, -0.06)}
    suffix = ".failure" if failure else ""
    add_uv_ellipsoid("pelvis" + suffix, pelvis, (0.31, 0.28, 0.24), materials["leather"], pose, semantic)
    add_uv_ellipsoid("chest" + suffix, chest, (0.40, 0.48, 0.25), materials["cloth"], pose, semantic)
    add_uv_ellipsoid("head" + suffix, head, (0.22, 0.25, 0.22), materials["skin"], pose, semantic)
    # Leather shoulder mantle and mineral relay core make the torso readable at gameplay scale.
    add_uv_ellipsoid("Runner.Mantle" + suffix, (chest[0], chest[1] + 0.12, chest[2] + 0.01), (0.44, 0.15, 0.28), materials["leather"], pose, semantic)
    add_uv_ellipsoid("Runner.Core" + suffix, (chest[0], chest[1] + 0.03, chest[2] - 0.235), (0.105, 0.14, 0.055), materials["tide-scar"], pose, semantic, segments=16, rings=10)
    for side in ("L", "R"):
        add_tapered_limb("upperArm." + side + suffix, shoulders[side], elbows[side], 0.115, 0.095, materials["cloth"], pose, semantic)
        add_tapered_limb("forearm." + side + suffix, elbows[side], hands[side], 0.095, 0.072, materials["leather"], pose, semantic)
        add_uv_ellipsoid("hand." + side + suffix, hands[side], (0.09, 0.115, 0.085), materials["skin"], pose, semantic, segments=16, rings=8)
        add_tapered_limb("thigh." + side + suffix, hips[side], knees[side], 0.145, 0.118, materials["cloth"], pose, semantic)
        add_tapered_limb("shin." + side + suffix, knees[side], ankles[side], 0.115, 0.085, materials["leather"], pose, semantic)
        add_uv_ellipsoid("foot." + side + suffix, feet[side], (0.135, 0.085, 0.235), materials["leather"], pose, semantic, segments=18, rings=8)
    tail_x = (-0.52, 0.52) if not failure else (-0.12, 0.86)
    for side, x in zip(("L", "R"), tail_x):
        z = 0.62 if not failure else 0.65
        vertices = [(x - 0.13, 1.25 if not failure else 0.91, z), (x + 0.13, 1.25 if not failure else 0.91, z),
                    (x + 0.18, 0.48 if not failure else 0.32, z + 0.27), (x - 0.10, 0.46 if not failure else 0.31, z + 0.31)]
        mesh_object("coatTail." + side + suffix, vertices, [(0, 1, 2, 3)], materials["cloth"], pose, semantic, bevel=0.018)
    for socket_name, location in (("ground.foot.L", (feet["L"][0], 0.0, feet["L"][2])), ("ground.foot.R", (feet["R"][0], 0.0, feet["R"][2])), ("camera.target", chest)):
        socket = make_empty(socket_name + suffix, pose)
        socket.location = location
    return pose


def create_pursuer(root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    root.location = (0.0, 0.0, 2.4)
    semantic = "pursuer"
    plates = [
        ("pelvisPlate", (0.0, 1.03, 0.62), (0.90, 0.48, 0.64)),
        ("ribPlate", (0.0, 1.20, 0.04), (1.12, 0.56, 0.72)),
        ("shoulderPlate", (0.0, 1.20, -0.52), (1.27, 0.48, 0.55)),
        ("neck", (0.0, 1.25, -0.90), (0.48, 0.38, 0.49)),
        ("head", (0.0, 1.22, -1.26), (0.58, 0.38, 0.49)),
        ("jaw", (0.0, 1.03, -1.48), (0.46, 0.20, 0.38)),
    ]
    for index, (name, center, scale) in enumerate(plates):
        plate = add_uv_ellipsoid(name, center, scale, materials["rock-armour"], root, semantic, segments=20, rings=12)
        plate.rotation_euler[1] = math.radians((index % 3 - 1) * 5.0)
        # Separate basalt-strata plate catches the rim light without becoming a blob.
        if index < 3:
            cap_scale = (scale[0] * 0.76, scale[1] * 0.30, scale[2] * 0.76)
            add_uv_ellipsoid(name + ".ridge", (center[0], center[1] + scale[1] * 0.58, center[2]), cap_scale, materials["basalt-strata"], root, semantic, segments=18, rings=10)
    leg_specs = {
        "foreleg.L": ((-0.82, 1.14, -0.52), (-1.03, 0.54, -0.72), (-1.02, 0.13, -1.02)),
        "foreleg.R": ((0.82, 1.14, -0.52), (1.03, 0.54, -0.72), (1.02, 0.13, -1.02)),
        "hindleg.L": ((-0.72, 1.02, 0.58), (-0.99, 0.49, 0.86), (-0.98, 0.13, 1.08)),
        "hindleg.R": ((0.72, 1.02, 0.58), (0.99, 0.49, 0.86), (0.98, 0.13, 1.08)),
    }
    for base_name, (hip, knee, paw) in leg_specs.items():
        add_tapered_limb(base_name + ".upper", hip, knee, 0.22, 0.16, materials["rock-armour"], root, semantic)
        add_tapered_limb(base_name + ".lower", knee, paw, 0.17, 0.12, materials["rock-armour"], root, semantic)
        paw_name = "paw." + ("L" if ".L" in base_name else "R") + (".front" if "fore" in base_name else ".rear")
        add_uv_ellipsoid(paw_name, paw, (0.24, 0.13, 0.32), materials["rock-armour"], root, semantic, segments=18, rings=9)
    seam_points = [(0.0, 1.55, 0.78), (0.0, 1.68, 0.35), (0.0, 1.72, -0.10), (0.0, 1.65, -0.55), (0.0, 1.50, -0.94)]
    add_curve("dorsalSeam", [seam_points], 0.075, materials["coral-mineral"], root, semantic)
    for socket_name, location in (("ground.front.L", (-1.02, 0.0, -1.02)), ("ground.front.R", (1.02, 0.0, -1.02)), ("ground.rear.L", (-0.98, 0.0, 1.08)), ("ground.rear.R", (0.98, 0.0, 1.08)), ("capture.target", (0.0, 1.1, -1.6))):
        socket = make_empty(socket_name, root)
        socket.location = location


def irregular_box(
    name: str,
    center: tuple[float, float, float],
    size: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    semantic: str,
    rng: random.Random,
    *,
    jitter: float = 0.06,
) -> bpy.types.Object:
    cx, cy, cz = center
    sx, sy, sz = (component * 0.5 for component in size)
    vertices = []
    for x_sign, y_sign, z_sign in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        vertices.append((cx + x_sign * sx + rng.uniform(-jitter, jitter), cy + y_sign * sy + rng.uniform(-jitter, jitter), cz + z_sign * sz + rng.uniform(-jitter, jitter)))
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    return mesh_object(name, vertices, faces, material, parent, semantic, bevel=min(size) * 0.12)


def create_hazards(
    roots: dict[str, bpy.types.Object],
    materials: dict[str, bpy.types.Material],
    rng: random.Random,
) -> None:
    # Jump threshold: five interlocked fractured mineral-rib segments, top <= .76 m.
    for index in range(5):
        x = -2.32 + index * 1.16
        obj = irregular_box(
            f"Beam.FracturedRib.{index}", (x, 0.36 + 0.015 * (index % 2), -18.0 + rng.uniform(-0.10, 0.10)),
            (1.13, 0.62, 0.56), materials["fresh-break"], roots["TR4_Hazard_Beam"], "beam", rng, jitter=0.025,
        )
        obj.rotation_euler[1] = math.radians((index - 2) * 1.8)
        if index in (0, 4):
            irregular_box(f"Beam.CoralCut.{index}", (x, 0.48, -17.71), (0.72, 0.16, 0.08), materials["coral-mineral"], roots["TR4_Hazard_Beam"], "beam", rng, jitter=0.02)
    for socket_name, location in (("entry", (0,0,-17.1)),("apex.clearance",(0,0.82,-18)),("exit",(0,0,-18.9)),("ground.L",(-2.8,0,-18)),("ground.R",(2.8,0,-18))):
        socket = make_empty(socket_name, roots["TR4_Hazard_Beam"]); socket.location = location

    # Slide lintel: two grounded supports, real negative-space aperture, no copied statue language.
    ring_root = roots["TR4_Hazard_Ring"]
    for side in (-1.0, 1.0):
        create_rock_spire(f"Ring.Support.{('L' if side < 0 else 'R')}", (side * 0.57, 0.0, -36.0), 0.15, 1.16, 9, materials["sandstone"], ring_root, "ring", rng, top_taper=0.70)
    irregular_box("Ring.LowClearanceLintel", (0.0, 1.32, -36.0), (1.44, 0.44, 0.50), materials["fresh-break"], ring_root, "ring", rng, jitter=0.040)
    for side in (-1.0, 1.0):
        irregular_box(f"Ring.MineralVent.{('L' if side < 0 else 'R')}", (side * 0.69, 0.82, -35.73), (0.13, 0.31, 0.10), materials["coral-mineral"], ring_root, "ring", rng, jitter=0.018)
    for socket_name, location in (("entry",(0,0,-35.2)),("slide.clearance",(0,0.90,-36)),("exit",(0,0,-36.8)),("ground.L",(-0.63,0,-36)),("ground.R",(0.63,0,-36))):
        socket = make_empty(socket_name, ring_root); socket.location = location

    column_root = roots["TR4_Hazard_Column"]
    create_rock_spire("Column.CollapsedButtress", (0.0, 0.0, -54.0), 0.54, 2.45, 11, materials["sandstone"], column_root, "column", rng, top_taper=0.18)
    irregular_box("Column.FractureFace", (0.18, 1.12, -53.55), (0.72, 1.10, 0.18), materials["fresh-break"], column_root, "column", rng, jitter=0.05)
    for index, x in enumerate((-0.55, -0.32, 0.43, 0.61)):
        create_rock_spire(f"Column.GroundedRubble.{index}", (x, 0.0, -53.68 + (index % 2) * 0.22), 0.12 + 0.03 * index, 0.28 + 0.08 * (index % 3), 7, materials["sandstone"], column_root, "column", rng, top_taper=0.15)
    for socket_name, location in (("entry",(0,0,-53.1)),("safe.left",(-2.35,0,-54)),("safe.right",(2.35,0,-54)),("exit",(0,0,-54.9)),("ground",(0,0,-54))):
        socket = make_empty(socket_name, column_root); socket.location = location

    gap_root = roots["TR4_Gap_Lips"]
    for lip_index, z in enumerate((-72.0, -76.0)):
        direction = -1.0 if lip_index == 0 else 1.0
        for index in range(9):
            x = -2.95 + index * 0.74
            irregular_box(
                f"Gap.Lip.{lip_index}.{index}", (x, -0.19 - 0.035 * (index % 3), z + direction * (0.12 + 0.06 * (index % 2))),
                (0.72, 0.48 + 0.08 * (index % 3), 0.46),
                materials["coral-mineral" if index in (1, 6) else "fresh-break"], gap_root, "gap-lips", rng, jitter=0.055,
            )
    for socket_name, location in (("takeoff",(0,0,-71.5)),("apex.clearance",(0,0.52,-74)),("landing",(0,0,-76.5))):
        socket = make_empty(socket_name, gap_root); socket.location = location


def set_hidden_recursive(root: bpy.types.Object, hidden: bool) -> None:
    root.hide_render = hidden
    for child in root.children_recursive:
        child.hide_render = hidden


def apply_camera_profile(camera: bpy.types.Object, record: dict[str, Any]) -> None:
    scene = bpy.context.scene
    width, height = record["diagnosticResolution"]
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    position = Vector(record["position"])
    target = Vector(record["target"])
    forward = (target - position).normalized()
    world_up = Vector(record["up"]).normalized()
    right = forward.cross(world_up).normalized()
    true_up = right.cross(forward).normalized()
    rotation = Matrix((right, true_up, -forward)).transposed().to_quaternion()
    camera.location = position
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = rotation
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 32.0
    camera.data.lens = camera.data.sensor_height / (2.0 * math.tan(math.radians(record["verticalFovDegrees"]) * 0.5))
    camera.data.clip_start = record["near"]
    camera.data.clip_end = record["far"]


def component_dot(left: list[float], right: list[float]) -> float:
    return sum(left[index] * right[index] for index in range(3))


def component_cross(left: list[float], right: list[float]) -> list[float]:
    return [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]


def component_normalize(value: list[float]) -> list[float]:
    magnitude = math.sqrt(component_dot(value, value))
    if not math.isfinite(magnitude) or magnitude <= 1.0e-12:
        raise RuntimeError("camera basis vector is degenerate")
    return [component / magnitude for component in value]


def camera_basis(record: dict[str, Any]) -> dict[str, Any]:
    position = [float(value) for value in record["position"]]
    target = [float(value) for value in record["target"]]
    world_up = component_normalize([float(value) for value in record["up"]])
    forward = component_normalize([target[index] - position[index] for index in range(3)])
    right = component_normalize(component_cross(forward, world_up))
    true_up = component_normalize(component_cross(right, forward))
    negative_forward = [-component for component in forward]
    vector_lengths = [math.sqrt(component_dot(vector, vector)) for vector in (right, true_up, forward)]
    pairwise_dots = [component_dot(right, true_up), component_dot(right, forward), component_dot(true_up, forward)]
    determinant = component_dot(right, component_cross(true_up, negative_forward))
    if (
        any(abs(length - 1.0) > 5.0e-7 for length in vector_lengths)
        or any(abs(value) > 5.0e-7 for value in pairwise_dots)
        or abs(determinant - 1.0) > 5.0e-7
    ):
        raise RuntimeError(f"camera basis gate failed for {record['profile']}")
    return {
        "forward": forward,
        "right": right,
        "trueUp": true_up,
        "vectorLengths": vector_lengths,
        "pairwiseDots": pairwise_dots,
        "determinant": determinant,
    }


def angle_between_components(left: list[float], right: list[float]) -> float:
    left_length = math.sqrt(sum(component * component for component in left))
    right_length = math.sqrt(sum(component * component for component in right))
    if left_length <= 1.0e-12 or right_length <= 1.0e-12:
        raise RuntimeError("axis alignment vector is degenerate")
    cosine = sum(a * b for a, b in zip(left, right)) / (left_length * right_length)
    return math.acos(max(-1.0, min(1.0, cosine)))


def camera_orientation_record(camera: bpy.types.Object, record: dict[str, Any]) -> dict[str, Any]:
    basis = camera_basis(record)
    canonical_view = [record["viewMatrix"][(index % 4) * 4 + index // 4] for index in range(16)]
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = camera.evaluated_get(depsgraph)
    actual_view = matrix_row_major(evaluated.matrix_world.inverted())
    max_view_error = max(abs(left - right) for left, right in zip(actual_view, canonical_view))
    actual_forward = [-actual_view[8], -actual_view[9], -actual_view[10]]
    actual_up = [actual_view[4], actual_view[5], actual_view[6]]
    forward_angle = angle_between_components(actual_forward, basis["forward"])
    up_angle = angle_between_components(actual_up, basis["trueUp"])
    if max_view_error > 5.0e-6 or forward_angle > 1.0e-5 or up_angle > 1.0e-5:
        raise RuntimeError(f"camera orientation readback failed for {record['profile']}")
    return {
        "position": [float(value) for value in record["position"]],
        "target": [float(value) for value in record["target"]],
        "up": [float(value) for value in record["up"]],
        "forward": basis["forward"],
        "right": basis["right"],
        "trueUp": basis["trueUp"],
        "vectorLengths": basis["vectorLengths"],
        "pairwiseDots": basis["pairwiseDots"],
        "determinant": basis["determinant"],
        "canonicalViewMatrix": canonical_view,
        "actualViewMatrix": actual_view,
        "maxViewMatrixError": max_view_error,
        "localForwardAngleRadians": forward_angle,
        "localUpAngleRadians": up_angle,
    }


def multiply_column_major(matrix: list[float], vector: list[float]) -> list[float]:
    result = [sum(matrix[column * 4 + row] * vector[column] for column in range(4)) for row in range(4)]
    if any(not math.isfinite(value) for value in result):
        raise RuntimeError("screen projection produced a non-finite vector")
    return result


def project_anchor(record: dict[str, Any], point: list[float], *, direction: bool = False) -> tuple[float, float]:
    camera_space = multiply_column_major(record["viewMatrix"], [*point, 0.0 if direction else 1.0])
    clip = multiply_column_major(record["projectionMatrix"], camera_space)
    if abs(clip[3]) <= 1.0e-12:
        raise RuntimeError("screen projection divisor is degenerate")
    result = ((clip[0] / clip[3] + 1.0) * 0.5, (1.0 - clip[1] / clip[3]) * 0.5)
    if any(not math.isfinite(value) for value in result):
        raise RuntimeError("screen projection produced a non-finite coordinate")
    return result


def screen_projection_record(record: dict[str, Any]) -> dict[str, Any]:
    anchors = record["projectionAnchors"]
    points = {name: project_anchor(record, point) for name, point in anchors.items()}
    result = {
        "runnerAnchor": list(points["runnerAnchor"]),
        "runnerHeadY": points["runnerHead"][1],
        "runnerFootLY": points["runnerFootL"][1],
        "runnerFootRY": points["runnerFootR"][1],
        "beamY": points["beam"][1],
        "ringY": points["ring"][1],
        "columnY": points["column"][1],
        "gapY": points["gap"][1],
        "scarX": points["scar"][0],
        "routeCenterX": points["routeCenter"][0],
        "horizonY": project_anchor(record, [0.0, 0.0, -1.0], direction=True)[1],
        "farRouteY": points["farRoute"][1],
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }
    scalar_values = [*result["runnerAnchor"], *[result[name] for name in (
        "runnerHeadY", "runnerFootLY", "runnerFootRY", "beamY", "ringY", "columnY",
        "gapY", "scarX", "routeCenterX", "horizonY", "farRouteY",
    )]]
    if any(not 0.0 <= value <= 1.0 for value in scalar_values):
        raise RuntimeError(f"screen projection outside frame for {record['profile']}")
    if not result["runnerHeadY"] < min(result["runnerFootLY"], result["runnerFootRY"]):
        raise RuntimeError(f"runner head/feet screen order failed for {record['profile']}")
    if not result["scarX"] > result["routeCenterX"]:
        raise RuntimeError(f"Tide Scar side projection failed for {record['profile']}")
    if record["profile"] != "closeup":
        low, high = (0.61, 0.72) if record["profile"] == "portrait" else (0.62, 0.76)
        if not low <= result["runnerAnchor"][1] <= high:
            raise RuntimeError(f"runner screen band failed for {record['profile']}")
        if not result["runnerAnchor"][1] > result["beamY"] > result["ringY"] > result["columnY"] > result["gapY"]:
            raise RuntimeError(f"semantic screen order failed for {record['profile']}")
        if not 0.17 <= result["horizonY"] <= 0.31:
            raise RuntimeError(f"horizon screen band failed for {record['profile']}")
        far_x, far_y = points["farRoute"]
        if not 0.0 <= far_x <= 1.0 or not 0.0 <= far_y <= 1.0:
            raise RuntimeError(f"far-route screen projection failed for {record['profile']}")
    return result


def webgl_from_row_major(matrix: list[float]) -> list[float]:
    if len(matrix) != 16 or any(not math.isfinite(value) for value in matrix):
        raise RuntimeError("camera matrix is not a finite 4x4 matrix")
    return [matrix[(index % 4) * 4 + index // 4] for index in range(16)]


def calibration_profile(camera: bpy.types.Object, record: dict[str, Any]) -> dict[str, Any]:
    apply_camera_profile(camera, record)
    width, height = record["diagnosticResolution"]
    original_shift0, evaluated_shift0, matrix0 = observe_matrix_shift(camera, 0.0, width, height)
    if not invariants_match(expected_camera_invariants(record), camera_invariants(camera, bpy.context.scene)):
        raise RuntimeError(f"camera calibration parameters do not match the frozen profile for {record['profile']}")
    original_shift1, evaluated_shift1, matrix1 = observe_matrix_shift(camera, 1.0, width, height)
    if any(abs(value - expected) > 1.0e-8 for value, expected in (
        (original_shift0, 0.0), (evaluated_shift0, 0.0),
        (original_shift1, 1.0), (evaluated_shift1, 1.0),
    )):
        raise RuntimeError(f"evaluated camera shift propagation failed for {record['profile']}")
    difference = [second - first for first, second in zip(matrix0, matrix1)]
    if any(not math.isfinite(value) for value in difference):
        raise RuntimeError(f"camera calibration difference is non-finite for {record['profile']}")
    b0 = matrix0[6]
    b1 = matrix1[6]
    response = difference[6]
    max_off_target_calibration = max(abs(value) for index, value in enumerate(difference) if index != 6)
    dominance = abs(response) / max(max_off_target_calibration, 1.0e-12)
    if abs(b0) > 1.0e-7:
        raise RuntimeError(f"camera zero baseline failed for {record['profile']}: {b0}")
    if response <= 0.0 or abs(response - 2.0) > 5.0e-7:
        raise RuntimeError(f"camera target response failed for {record['profile']}: {response}")
    if max_off_target_calibration > 5.0e-7 or dominance < 1.0e6:
        raise RuntimeError(f"camera off-target calibration failed for {record['profile']}: {max_off_target_calibration}")
    solved_shift = (record["lensShiftY"] - b0) / response
    if not math.isfinite(solved_shift):
        raise RuntimeError(f"camera solved shift is non-finite for {record['profile']}")
    original_solved_shift, evaluated_solved_shift, matrix_solved = observe_matrix_shift(camera, solved_shift, width, height)
    if abs(original_solved_shift - solved_shift) > 1.0e-8 or abs(evaluated_solved_shift - solved_shift) > 1.0e-8:
        raise RuntimeError(f"evaluated solved camera shift failed for {record['profile']}")
    solved_difference = [value - baseline for value, baseline in zip(matrix_solved, matrix0)]
    actual = matrix_solved[6]
    target_error = abs(actual - record["lensShiftY"])
    max_off_target_solved = max(abs(value) for index, value in enumerate(solved_difference) if index != 6)
    webgl_matrix = webgl_from_row_major(matrix_solved)
    projection_errors = [abs(actual_value - frozen_value) for actual_value, frozen_value in zip(webgl_matrix, record["projectionMatrix"])]
    max_projection_error = max(projection_errors)
    if target_error > 5.0e-7 or max_off_target_solved > 5.0e-7:
        raise RuntimeError(f"camera solved target/off-target gate failed for {record['profile']}")
    if projection_errors[9] > 5.0e-7 or max_projection_error > 5.0e-7:
        raise RuntimeError(f"camera WebGL projection gate failed for {record['profile']}: {max_projection_error}")
    return {
        "profile": record["profile"],
        "lensShiftY": record["lensShiftY"],
        "originalShift0": original_shift0,
        "evaluatedShift0": evaluated_shift0,
        "originalShift1": original_shift1,
        "evaluatedShift1": evaluated_shift1,
        "matrix0": matrix0,
        "matrix1": matrix1,
        "difference": difference,
        "b0": b0,
        "b1": b1,
        "response": response,
        "maxOffTargetCalibrationDelta": max_off_target_calibration,
        "dominanceRatio": dominance,
        "solvedShift": solved_shift,
        "evaluatedSolvedShift": evaluated_solved_shift,
        "matrixSolved": matrix_solved,
        "solvedDifference": solved_difference,
        "actual": actual,
        "targetError": target_error,
        "maxOffTargetSolvedDelta": max_off_target_solved,
        "webglMatrix": webgl_matrix,
        "maxProjectionError": max_projection_error,
        "orientation": camera_orientation_record(camera, record),
        "screenProjection": screen_projection_record(record),
    }


def invariants_match(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    if expected.keys() != actual.keys():
        return False
    for key in expected:
        left = expected[key]
        right = actual[key]
        if isinstance(left, tuple):
            if len(left) != len(right) or any(abs(float(a) - float(b)) > 5.0e-6 for a, b in zip(left, right)):
                return False
        elif isinstance(left, float):
            if abs(left - float(right)) > 5.0e-6:
                return False
        elif left != right:
            return False
    return True


def replay_and_validate_camera(
    camera: bpy.types.Object,
    record: dict[str, Any],
    binding: dict[str, Any],
) -> None:
    scene = bpy.context.scene
    apply_camera_profile(camera, record)
    width, height = record["diagnosticResolution"]
    original_shift, evaluated_shift, matrix = observe_matrix_shift(camera, binding["solvedShift"], width, height)
    if not invariants_match(expected_camera_invariants(record), camera_invariants(camera, scene)):
        raise RuntimeError(f"camera replay does not match the frozen parameters for {record['profile']}")
    if abs(original_shift - binding["solvedShift"]) > 1.0e-8 or abs(evaluated_shift - binding["solvedShift"]) > 1.0e-8:
        raise RuntimeError(f"camera replay evaluated shift failed for {record['profile']}")
    actual = matrix[6]
    if abs(actual - record["lensShiftY"]) > 5.0e-7:
        raise RuntimeError(f"camera replay target failed for {record['profile']}: {actual}")
    replay_difference = [value - baseline for value, baseline in zip(matrix, binding["matrix0"])]
    if max(abs(value) for index, value in enumerate(replay_difference) if index != 6) > 5.0e-7:
        raise RuntimeError(f"camera replay off-target gate failed for {record['profile']}")
    webgl_matrix = webgl_from_row_major(matrix)
    if max(abs(value - frozen) for value, frozen in zip(webgl_matrix, record["projectionMatrix"])) > 5.0e-7:
        raise RuntimeError(f"camera replay frozen projection gate failed for {record['profile']}")
    if max(abs(value - calibrated) for value, calibrated in zip(webgl_matrix, binding["webglMatrix"])) > 5.0e-7:
        raise RuntimeError(f"camera replay calibration drift failed for {record['profile']}")
    replay_orientation = camera_orientation_record(camera, record)
    if replay_orientation.keys() != binding["orientation"].keys():
        raise RuntimeError(f"camera replay orientation schema drift failed for {record['profile']}")
    for name in ("maxViewMatrixError", "localForwardAngleRadians", "localUpAngleRadians"):
        if float(replay_orientation[name]) > (5.0e-6 if name == "maxViewMatrixError" else 1.0e-5):
            raise RuntimeError(f"camera replay orientation gate failed for {record['profile']}: {name}")
    replay_screen = screen_projection_record(record)
    if replay_screen != binding["screenProjection"]:
        raise RuntimeError(f"camera replay screen projection drift failed for {record['profile']}")
    scene.camera = camera


def matrix_row_major(matrix: Any) -> list[float]:
    values = [float(matrix[row][column]) for row in range(4) for column in range(4)]
    if len(values) != 16 or any(not math.isfinite(value) for value in values):
        raise RuntimeError("camera probe matrix contains non-finite values")
    return values


def tagged_camera_matrix(
    camera: bpy.types.Object,
    shift_y: float,
    width: int,
    height: int,
) -> Any:
    camera.data.shift_y = shift_y
    camera.data.update_tag()
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return camera.calc_matrix_camera(depsgraph, x=width, y=height, scale_x=1.0, scale_y=1.0)


def camera_invariants(camera: bpy.types.Object, scene: bpy.types.Scene) -> dict[str, Any]:
    return {
        "location": tuple(float(value) for value in camera.location),
        "rotationQuaternion": tuple(float(value) for value in camera.rotation_quaternion),
        "type": camera.data.type,
        "sensorFit": camera.data.sensor_fit,
        "sensorHeight": float(camera.data.sensor_height),
        "lens": float(camera.data.lens),
        "clipStart": float(camera.data.clip_start),
        "clipEnd": float(camera.data.clip_end),
        "resolution": (scene.render.resolution_x, scene.render.resolution_y),
        "resolutionPercentage": scene.render.resolution_percentage,
        "pixelAspect": (float(scene.render.pixel_aspect_x), float(scene.render.pixel_aspect_y)),
    }


def expected_camera_invariants(record: dict[str, Any]) -> dict[str, Any]:
    position = Vector(record["position"])
    forward = (Vector(record["target"]) - position).normalized()
    world_up = Vector(record["up"]).normalized()
    right = forward.cross(world_up).normalized()
    true_up = right.cross(forward).normalized()
    quaternion = Matrix((right, true_up, -forward)).transposed().to_quaternion()
    lens = 32.0 / (2.0 * math.tan(math.radians(record["verticalFovDegrees"]) * 0.5))
    return {
        "location": tuple(float(value) for value in record["position"]),
        "rotationQuaternion": tuple(float(value) for value in quaternion),
        "type": "PERSP",
        "sensorFit": "VERTICAL",
        "sensorHeight": 32.0,
        "lens": lens,
        "clipStart": float(record["near"]),
        "clipEnd": float(record["far"]),
        "resolution": tuple(record["diagnosticResolution"]),
        "resolutionPercentage": 100,
        "pixelAspect": (1.0, 1.0),
    }


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    encoded = (
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    with temporary.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run_camera_probe(plan: dict[str, Any], output_root: Path) -> None:
    clean_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    camera_data = bpy.data.cameras.new("TR4.CameraProbe.001")
    camera = bpy.data.objects.new("TR4.CameraProbe.001", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    profile_results: list[dict[str, Any]] = []
    for record in plan["cameras"]:
        width, height = record["diagnosticResolution"]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.pixel_aspect_x = 1.0
        scene.render.pixel_aspect_y = 1.0
        camera.location = record["position"]
        target = Vector(record["target"])
        direction = target - camera.location
        camera.rotation_mode = "QUATERNION"
        camera.rotation_quaternion = direction.to_track_quat("-Z", "Y")
        camera.data.type = "PERSP"
        camera.data.sensor_fit = "VERTICAL"
        camera.data.sensor_height = 32.0
        camera.data.lens = camera.data.sensor_height / (2.0 * math.tan(math.radians(record["verticalFovDegrees"]) * 0.5))
        camera.data.clip_start = record["near"]
        camera.data.clip_end = record["far"]
        frozen_parameters = camera_invariants(camera, scene)

        matrix0 = tagged_camera_matrix(camera, 0.0, width, height)
        b0 = float(matrix0[2][1])
        matrix1 = tagged_camera_matrix(camera, 1.0, width, height)
        b1 = float(matrix1[2][1])
        response = b1 - b0
        if not all(math.isfinite(value) for value in (b0, b1, response)) or abs(response) < 1.0e-9:
            raise RuntimeError(f"camera probe response is degenerate for {record['profile']}: b0={b0}, b1={b1}")
        solved_shift = (record["lensShiftY"] - b0) / response
        if not math.isfinite(solved_shift):
            raise RuntimeError(f"camera probe solved shift is non-finite for {record['profile']}")
        matrix_solved = tagged_camera_matrix(camera, solved_shift, width, height)
        actual = float(matrix_solved[2][1])
        error = actual - record["lensShiftY"]
        if not math.isfinite(actual) or not math.isfinite(error) or abs(error) > 1.0e-6:
            raise RuntimeError(f"camera probe solved error failed for {record['profile']}: {error}")
        if camera_invariants(camera, scene) != frozen_parameters:
            raise RuntimeError(f"camera probe mutated a frozen parameter for {record['profile']}")
        profile_results.append(
            {
                "profile": record["profile"],
                "resolution": [width, height],
                "lensShiftY": record["lensShiftY"],
                "b0": b0,
                "b1": b1,
                "response": response,
                "solvedShift": solved_shift,
                "actual": actual,
                "error": error,
                "matrix0": matrix_row_major(matrix0),
                "matrix1": matrix_row_major(matrix1),
                "matrixSolved": matrix_row_major(matrix_solved),
            }
        )
    response = {
        "schemaId": "tide-relay.temple-tr4.camera-probe",
        "schemaVersion": 1,
        "blenderVersion": bpy.app.version_string,
        "generatorSha256": plan["scripts"]["generator"]["sha256"],
        "runnerSha256": plan["scripts"]["runner"]["sha256"],
        "profiles": profile_results,
        "renderCallCount": 0,
        "verdict": "READY_FOR_DIAGNOSTIC_003_CONTRACT",
    }
    atomic_json(output_root / "camera-response.json", response)


def observe_matrix_shift(
    camera: bpy.types.Object,
    shift_y: float,
    width: int,
    height: int,
) -> tuple[float, float, list[float]]:
    camera.data.shift_y = shift_y
    camera.data.update_tag()
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_camera = camera.evaluated_get(depsgraph)
    original_shift = float(camera.data.shift_y)
    evaluated_shift = float(evaluated_camera.data.shift_y)
    matrix = camera.calc_matrix_camera(depsgraph, x=width, y=height, scale_x=1.0, scale_y=1.0)
    values = matrix_row_major(matrix)
    if not math.isfinite(original_shift) or not math.isfinite(evaluated_shift):
        raise RuntimeError("matrix probe observed a non-finite camera shift")
    return original_shift, evaluated_shift, values


def significant_matrix_elements(difference: list[float]) -> list[dict[str, Any]]:
    return [
        {
            "row": index // 4,
            "column": index % 4,
            "rowMajorIndex": index,
            "webglColumnMajorIndex": (index % 4) * 4 + index // 4,
            "delta": value,
        }
        for index, value in enumerate(difference)
        if abs(value) > 1.0e-8
    ]


def derive_observed_binding(profiles: list[dict[str, Any]]) -> dict[str, Any] | None:
    responses: list[dict[str, Any]] = []
    for record in profiles:
        shifts = (
            (record["originalShift0"], 0.0), (record["evaluatedShift0"], 0.0),
            (record["originalShift1"], 1.0), (record["evaluatedShift1"], 1.0),
        )
        if any(abs(float(value) - expected) > 1.0e-8 for value, expected in shifts):
            return None
        significant = record["significantElements"]
        if len(significant) != 1:
            return None
        element = significant[0]
        if (element["row"], element["column"], element["rowMajorIndex"], element["webglColumnMajorIndex"]) != (1, 2, 6, 9):
            return None
        response = float(record["difference"][6])
        if abs(float(element["delta"]) - response) > 1.0e-12 or not math.isfinite(response) or abs(response - 2.0) > 1.0e-6:
            return None
        responses.append({"profile": record["profile"], "response": response})
    return {"row": 1, "column": 2, "rowMajorIndex": 6, "webglColumnMajorIndex": 9, "responses": responses}


def run_full_matrix_probe(plan: dict[str, Any], output_root: Path) -> None:
    clean_scene()
    if any(obj.type in ("MESH", "LIGHT") for obj in bpy.context.scene.objects):
        raise RuntimeError("matrix probe scene cleanup left geometry or lights")
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new("TR4.MatrixProbe.001")
    camera = bpy.data.objects.new("TR4.MatrixProbe.001", camera_data)
    scene.collection.objects.link(camera)
    if len([obj for obj in scene.objects if obj.type == "CAMERA"]) != 1:
        raise RuntimeError("matrix probe must contain exactly one temporary camera")
    profiles: list[dict[str, Any]] = []
    for record in plan["cameras"]:
        width, height = record["diagnosticResolution"]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.pixel_aspect_x = 1.0
        scene.render.pixel_aspect_y = 1.0
        camera.location = record["position"]
        direction = Vector(record["target"]) - camera.location
        camera.rotation_mode = "QUATERNION"
        camera.rotation_quaternion = direction.to_track_quat("-Z", "Y")
        camera.data.type = "PERSP"
        camera.data.sensor_fit = "VERTICAL"
        camera.data.sensor_height = 32.0
        camera.data.lens = camera.data.sensor_height / (2.0 * math.tan(math.radians(record["verticalFovDegrees"]) * 0.5))
        camera.data.clip_start = record["near"]
        camera.data.clip_end = record["far"]
        original_shift0, evaluated_shift0, matrix0 = observe_matrix_shift(camera, 0.0, width, height)
        original_shift1, evaluated_shift1, matrix1 = observe_matrix_shift(camera, 1.0, width, height)
        difference = [second - first for first, second in zip(matrix0, matrix1)]
        if any(not math.isfinite(value) for value in difference):
            raise RuntimeError(f"matrix probe difference is non-finite for {record['profile']}")
        significant = significant_matrix_elements(difference)
        for element in significant:
            if abs(float(element["delta"]) - difference[element["rowMajorIndex"]]) > 1.0e-12:
                raise RuntimeError(f"matrix probe significant delta mismatch for {record['profile']}")
        profiles.append(
            {
                "profile": record["profile"],
                "resolution": [width, height],
                "originalShift0": original_shift0,
                "evaluatedShift0": evaluated_shift0,
                "originalShift1": original_shift1,
                "evaluatedShift1": evaluated_shift1,
                "matrix0": matrix0,
                "matrix1": matrix1,
                "difference": difference,
                "significantElements": significant,
            }
        )
    consistent_binding = derive_observed_binding(profiles)
    response = {
        "schemaId": "tide-relay.temple-tr4.matrix-probe",
        "schemaVersion": 1,
        "probeId": "001",
        "blenderVersion": bpy.app.version_string,
        "generatorSha256": plan["scripts"]["generator"]["sha256"],
        "runnerSha256": plan["scripts"]["runner"]["sha256"],
        "profiles": profiles,
        "consistentBinding": consistent_binding,
        "renderCallCount": 0,
        "verdict": "READY_FOR_CAMERA_BINDING_CONTRACT" if consistent_binding is not None else "MATRIX_PROBE_BLOCKED",
    }
    atomic_json(output_root / "matrix-response.json", response)


def emission_material(name: str, color: tuple[float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material.diffuse_color = (*color, 1.0)
    return material


def normal_material() -> bpy.types.Material:
    material = bpy.data.materials.get("TR4.Pass.Normal") or bpy.data.materials.new("TR4.Pass.Normal")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = (0.5, 0.5, 0.5)
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Normal"], multiply.inputs[0])
    links.new(multiply.outputs["Vector"], add.inputs[0])
    links.new(add.outputs["Vector"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def depth_material(camera_position: tuple[float, float, float], far: float) -> bpy.types.Material:
    material = bpy.data.materials.get("TR4.Pass.LinearDepth") or bpy.data.materials.new("TR4.Pass.LinearDepth")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = "DISTANCE"
    distance.inputs[1].default_value = camera_position
    divide = nodes.new("ShaderNodeMath")
    divide.operation = "DIVIDE"
    divide.inputs[1].default_value = far
    divide.use_clamp = True
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Position"], distance.inputs[0])
    links.new(distance.outputs["Value"], divide.inputs[0])
    links.new(divide.outputs["Value"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def configure_world(preflight: dict[str, Any]) -> tuple[bpy.types.Node, bpy.types.Node, bpy.types.Node, dict[str, Any]]:
    world = bpy.data.worlds.new("TR4.CanyonAtmosphere")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    volume = nodes.new("ShaderNodeVolumePrincipled")
    lighting = preflight["construction"]["lighting"]
    background.inputs["Color"].default_value = (*linear_rgb(lighting["worldColor"]), 1.0)
    background.inputs["Strength"].default_value = lighting["worldStrength"]
    volume.inputs["Color"].default_value = (*linear_rgb(lighting["fogColor"]), 1.0)
    volume.inputs["Density"].default_value = lighting["fogDensity"]
    volume.inputs["Anisotropy"].default_value = lighting["fogAnisotropy"]
    links.new(background.outputs["Background"], output.inputs["Surface"])
    links.new(volume.outputs["Volume"], output.inputs["Volume"])
    set_view_transform("beauty")
    world_color = [float(value) for value in background.inputs["Color"].default_value[:3]]
    fog_color = [float(value) for value in volume.inputs["Color"].default_value[:3]]
    world_strength = float(background.inputs["Strength"].default_value)
    fog_density = float(volume.inputs["Density"].default_value)
    fog_anisotropy = float(volume.inputs["Anisotropy"].default_value)
    if (
        max(abs(left - right) for left, right in zip(world_color, linear_rgb(lighting["worldColor"]))) > 1.0e-6
        or max(abs(left - right) for left, right in zip(fog_color, linear_rgb(lighting["fogColor"]))) > 1.0e-6
        or abs(world_strength - lighting["worldStrength"]) > 1.0e-6
        or abs(fog_density - lighting["fogDensity"]) > 1.0e-6
        or abs(fog_anisotropy - lighting["fogAnisotropy"]) > 1.0e-6
    ):
        raise RuntimeError("atmosphere node readback mismatch")
    transmittance20 = math.exp(-lighting["fogDensity"] * 20.0)
    transmittance120 = math.exp(-lighting["fogDensity"] * 120.0)
    transmittance520 = math.exp(-lighting["fogDensity"] * 520.0)
    if not (transmittance20 >= 0.90 and 0.55 <= transmittance120 <= 0.72 and transmittance520 >= 0.12):
        raise RuntimeError("atmosphere transmittance gate failed")
    binding = {
        "worldColorHex": lighting["worldColor"],
        "worldColorLinear": world_color,
        "worldStrength": world_strength,
        "fogColorHex": lighting["fogColor"],
        "fogColorLinear": fog_color,
        "fogDensity": fog_density,
        "fogAnisotropy": fog_anisotropy,
        "transmittance20": transmittance20,
        "transmittance120": transmittance120,
        "transmittance520": transmittance520,
        "beautyViewTransform": bpy.context.scene.view_settings.view_transform,
        "beautyLook": bpy.context.scene.view_settings.look,
        "exposure": float(bpy.context.scene.view_settings.exposure),
        "gamma": float(bpy.context.scene.view_settings.gamma),
        "dither": float(bpy.context.scene.render.dither_intensity),
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }
    return background, volume, output, binding


def set_world_mode(
    mode: str,
    background: bpy.types.Node,
    volume: bpy.types.Node,
    output: bpy.types.Node,
    lighting: dict[str, Any],
) -> None:
    links = bpy.context.scene.world.node_tree.links
    for link in list(output.inputs["Volume"].links):
        links.remove(link)
    if mode == "beauty":
        background.inputs["Color"].default_value = (*linear_rgb(lighting["worldColor"]), 1.0)
        background.inputs["Strength"].default_value = lighting["worldStrength"]
        volume.inputs["Color"].default_value = (*linear_rgb(lighting["fogColor"]), 1.0)
        volume.inputs["Density"].default_value = lighting["fogDensity"]
        volume.inputs["Anisotropy"].default_value = lighting["fogAnisotropy"]
        links.new(volume.outputs["Volume"], output.inputs["Volume"])
    elif mode in ("object-id", "road-mask"):
        background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        background.inputs["Strength"].default_value = 1.0
    elif mode == "normal":
        background.inputs["Color"].default_value = (128 / 255.0, 128 / 255.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 1.0
    elif mode == "linear-depth":
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 1.0
    else:
        raise RuntimeError(f"unknown pass mode: {mode}")


def set_view_transform(mode: str) -> None:
    scene = bpy.context.scene
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.render.dither_intensity = 0.0
    if mode == "beauty":
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
        if scene.view_settings.view_transform != "AgX" or scene.view_settings.look != "AgX - Medium High Contrast":
            raise RuntimeError("beauty color-management readback mismatch")
    elif mode in ("object-id", "road-mask", "normal", "linear-depth"):
        scene.view_settings.view_transform = "Raw"
        scene.view_settings.look = "None"
        if scene.view_settings.view_transform != "Raw" or scene.view_settings.look != "None":
            raise RuntimeError(f"{mode} color-management readback mismatch")
    else:
        raise RuntimeError(f"unknown view-transform mode: {mode}")


def set_render_samples(mode: str) -> None:
    """Beauty receives stable temporal sampling; data passes are single-sample IDs."""
    scene = bpy.context.scene
    if not hasattr(scene, "eevee"):
        return
    target = 24 if mode == "beauty" else 1
    for attribute in ("taa_render_samples", "taa_samples"):
        if hasattr(scene.eevee, attribute):
            setattr(scene.eevee, attribute, target)


def set_pass_materials(
    mode: str,
    render_objects: list[bpy.types.Object],
    beauty_materials: dict[str, bpy.types.Material],
    pass_materials: dict[str, bpy.types.Material],
    camera_record: dict[str, Any],
) -> None:
    if mode == "beauty":
        for obj in render_objects:
            original_name = obj.get("tr4_beauty_material")
            if not original_name or original_name not in beauty_materials:
                raise RuntimeError(f"missing beauty material binding: {obj.name}")
            obj.data.materials.clear()
            obj.data.materials.append(beauty_materials[original_name])
        return
    if mode == "normal":
        material = pass_materials["normal"]
        for obj in render_objects:
            obj.data.materials.clear(); obj.data.materials.append(material)
        return
    if mode == "linear-depth":
        material = depth_material(tuple(camera_record["position"]), camera_record["far"])
        for obj in render_objects:
            obj.data.materials.clear(); obj.data.materials.append(material)
        return
    for obj in render_objects:
        semantic = obj.get("tr4_semantic", "canyon")
        if mode == "object-id":
            material = pass_materials[semantic]
        elif mode == "road-mask":
            material = pass_materials["mask-white" if semantic in ("road", "gap-lips") else "mask-black"]
        else:
            raise RuntimeError(f"unknown material mode: {mode}")
        obj.data.materials.clear(); obj.data.materials.append(material)


def create_lights(preflight: dict[str, Any]) -> dict[str, Any]:
    lighting = preflight["construction"]["lighting"]
    binding: dict[str, Any] = {}
    for name in ("key", "fill"):
        record = lighting[name]
        source_values = [float(value) for value in record["surfaceToLight"]]
        normalized_values = component_normalize(source_values)
        if normalized_values[1] < (0.75 if name == "key" else 0.55):
            raise RuntimeError(f"{name} surface-to-light Y gate failed")
        if (name == "key" and normalized_values[0] >= 0.0) or (name == "fill" and normalized_values[0] <= 0.0):
            raise RuntimeError(f"{name} surface-to-light X sign gate failed")
        data = bpy.data.lights.new(f"TR4.{name.title()}", "SUN")
        data.color = linear_rgb(record["color"])
        data.energy = record["energy"]
        data.use_shadow = record["shadow"]
        obj = bpy.data.objects.new(f"TR4.{name.title()}", data)
        bpy.context.scene.collection.objects.link(obj)
        desired_values = [-component for component in normalized_values]
        desired_minus_z = Vector(desired_values)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = desired_minus_z.to_track_quat("-Z", "Y")
        bpy.context.view_layer.update()
        actual_minus_z = obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        actual_values = [float(value) for value in actual_minus_z]
        alignment = angle_between_components(actual_values, desired_values)
        if (
            alignment > 1.0e-5
            or abs(float(data.energy) - record["energy"]) > 1.0e-6
            or bool(data.use_shadow) is not record["shadow"]
            or max(abs(left - right) for left, right in zip(data.color, linear_rgb(record["color"]))) > 1.0e-6
        ):
            raise RuntimeError(f"{name} light readback gate failed")
        binding[name] = {
            "colorHex": record["color"],
            "colorLinear": [float(value) for value in data.color],
            "energy": float(data.energy),
            "shadow": bool(data.use_shadow),
            "surfaceToLight": source_values,
            "normalizedSurfaceToLight": normalized_values,
            "actualLocalMinusZ": actual_values,
            "alignmentRadians": alignment,
        }
    # A broad warm bounce supports contact readability but remains subordinate to frozen key/fill.
    record = lighting["contact"]
    data = bpy.data.lights.new("TR4.ContactBounce", "AREA")
    data.color = linear_rgb(record["color"])
    data.energy = record["energy"]
    data.shape = record["shape"]
    data.size = record["size"]
    data.use_shadow = record["shadow"]
    obj = bpy.data.objects.new("TR4.ContactBounce", data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = record["location"]
    location_values = [float(value) for value in record["location"]]
    target_values = [float(value) for value in record["target"]]
    desired_values = component_normalize([target_values[index] - location_values[index] for index in range(3)])
    desired_minus_z = Vector(desired_values)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = desired_minus_z.to_track_quat("-Z", "Y")
    bpy.context.view_layer.update()
    actual_minus_z = obj.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    actual_values = [float(value) for value in actual_minus_z]
    alignment = angle_between_components(actual_values, desired_values)
    if (
        alignment > 1.0e-5
        or data.shape != record["shape"]
        or abs(float(data.energy) - record["energy"]) > 1.0e-6
        or abs(float(data.size) - record["size"]) > 1.0e-6
        or bool(data.use_shadow) is not record["shadow"]
        or max(abs(left - right) for left, right in zip(data.color, linear_rgb(record["color"]))) > 1.0e-6
    ):
        raise RuntimeError("contact light readback gate failed")
    binding["contact"] = {
        "colorHex": record["color"],
        "colorLinear": [float(value) for value in data.color],
        "energy": float(data.energy),
        "size": float(data.size),
        "shadow": bool(data.use_shadow),
        "location": [float(value) for value in obj.location],
        "target": target_values,
        "actualLocalMinusZ": actual_values,
        "alignmentRadians": alignment,
    }
    binding["verdict"] = "READY_FOR_DIAGNOSTIC_RENDER"
    return binding


def scene_metrics(materials: dict[str, bpy.types.Material], roots: dict[str, bpy.types.Object]) -> dict[str, Any]:
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    triangles = sum(max(0, len(poly.vertices) - 2) for obj in meshes for poly in obj.data.polygons)
    root_records = []
    for name in ROOT_NAMES:
        root = roots[name]
        root_records.append({"name": name, "translation": list(root.location), "children": len(root.children_recursive)})
    return {
        "meshObjects": len(meshes),
        "sourceTrianglesBeforeModifiers": triangles,
        "beautyMaterialCount": len(materials),
        "semanticRoots": root_records,
        "pursuerBookendRoot": list(roots["TR4_Pursuer_Cinematic"].location),
        "runnerRoot": list(roots["TR4_Runner_Rig"].location),
        "roadTopY": 0.0,
        "verdict": "RENDERED_FOR_EVALUATION",
    }


def write_json(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        handle.write("\n")


def generate(preflight: dict[str, Any], output_root: Path) -> None:
    if bpy.app.version_string != EXPECTED_BLENDER_VERSION:
        raise RuntimeError(f"Blender version mismatch before scene construction: {bpy.app.version_string}")
    clean_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 15
    scene.render.use_file_extension = True
    scene.render.use_overwrite = False
    scene.render.use_placeholder = False
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.dither_intensity = 0.0
    if hasattr(scene, "eevee"):
        for attribute in ("taa_render_samples", "taa_samples"):
            if hasattr(scene.eevee, attribute):
                setattr(scene.eevee, attribute, 24)

    materials = {record["name"]: create_pbr_material(record, index + 1.0) for index, record in enumerate(preflight["materials"])}
    roots = {name: make_empty(name) for name in ROOT_NAMES}
    rng = random.Random(preflight["seed"])

    # Sixteen physically thick modules.  A single 4 m interval is omitted at the canonical gap.
    lengths = [8.0, 7.0, 9.0, 8.0, 10.0, 7.0, 9.0, 8.0, 8.0, 6.0, 8.0, 9.0, 7.0, 10.0, 8.0, 9.0]
    cursor = 8.0
    for index, length in enumerate(lengths):
        if index == 10:
            cursor -= 4.0
        end = cursor - length
        create_road_module(index, cursor, end, roots["TR4_Road_Modules"], materials, rng)
        cursor = end
    create_shoulder(roots["TR4_Road_Modules"], materials)
    # Sparse outer-lip mineral growth, always outside X=3.2 and below four percent coverage.
    for index, (side, z) in enumerate(((1, 3.0), (-1, -12.0), (1, -27.0), (-1, -45.0), (1, -62.0), (-1, -91.0))):
        create_rock_spire(f"Road.CoralDeposit.{index}", (side * 3.34, -0.10, z), 0.12, 0.28, 7, materials["coral-mineral"], roots["TR4_Road_Modules"], "road", rng, top_taper=0.14)

    create_canyon(roots["TR4_Canyon_Modules"], materials, rng)
    create_tide_scar(preflight, roots["TR4_TideScar_Path"], materials)
    run_pose = create_runner_pose("Runner.Pose.Run", roots["TR4_Runner_Rig"], materials, failure=False)
    failure_pose = create_runner_pose("Runner.Pose.Failure", roots["TR4_Runner_Rig"], materials, failure=True)
    create_pursuer(roots["TR4_Pursuer_Cinematic"], materials)
    create_hazards(roots, materials, rng)
    lighting_binding = create_lights(preflight)
    background, volume, world_output, atmosphere_binding = configure_world(preflight)

    camera_data = bpy.data.cameras.new("TR4.FrozenCamera")
    camera = bpy.data.objects.new("TR4.FrozenCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)

    render_objects = [obj for obj in scene.objects if obj.type in ("MESH", "CURVE")]
    beauty_materials = dict(materials)
    for obj in render_objects:
        if len(obj.data.materials) != 1:
            raise RuntimeError(f"mesh must have one beauty material: {obj.name}")
        obj["tr4_beauty_material"] = obj.data.materials[0].name
    pass_materials: dict[str, bpy.types.Material] = {}
    for semantic, color in ID_COLORS.items():
        if semantic == "background":
            continue
        pass_materials[semantic] = emission_material("TR4.ID." + semantic, hex_rgb(color))
    pass_materials["mask-white"] = emission_material("TR4.Mask.White", (1.0, 1.0, 1.0))
    pass_materials["mask-black"] = emission_material("TR4.Mask.Black", (0.0, 0.0, 0.0))
    pass_materials["normal"] = normal_material()

    cameras = {record["profile"]: record for record in preflight["cameras"]}
    outputs = {(record["profile"], record["pass"]): record for record in preflight["outputs"]}
    binding_profiles = [calibration_profile(camera, cameras[profile]) for profile in PROFILE_ORDER]
    camera_binding = {
        "schemaId": "tide-relay.temple-tr4.camera-binding",
        "schemaVersion": 2,
        "diagnosticId": DIAGNOSTIC_ID,
        "blenderVersion": bpy.app.version_string,
        "profiles": binding_profiles,
        "lightingBinding": lighting_binding,
        "atmosphereBinding": atmosphere_binding,
        "renderCallCountAtWrite": 0,
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }
    binding_path = output_root / "camera-binding.json"
    if binding_path.exists():
        raise RuntimeError("camera-binding.json must not pre-exist")
    atomic_json(binding_path, camera_binding)

    bindings = {record["profile"]: record for record in binding_profiles}
    rendered_order: list[str] = []
    write_still_count = 0
    for profile in PROFILE_ORDER:
        camera_record = cameras[profile]
        replay_and_validate_camera(camera, camera_record, bindings[profile])
        is_bookend = profile == "closeup"
        set_hidden_recursive(run_pose, is_bookend)
        set_hidden_recursive(failure_pose, not is_bookend)
        set_hidden_recursive(roots["TR4_Pursuer_Cinematic"], not is_bookend)
        for pass_name in PASS_ORDER:
            record = outputs[(profile, pass_name)]
            set_pass_materials(pass_name, render_objects, beauty_materials, pass_materials, camera_record)
            set_world_mode(pass_name, background, volume, world_output, preflight["construction"]["lighting"])
            set_view_transform(pass_name)
            set_render_samples(pass_name)
            scene.render.image_settings.color_mode = "BW" if pass_name in ("road-mask", "linear-depth") else "RGB"
            scene.render.image_settings.color_depth = "16" if pass_name == "linear-depth" else "8"
            output_path = output_root / record["relativePath"]
            if output_path.exists():
                raise RuntimeError(f"output collision: {output_path}")
            scene.render.filepath = str(output_path)
            bpy.ops.render.render(write_still=True)
            write_still_count += 1
            rendered_order.append(record["relativePath"])
            if not output_path.is_file() or output_path.stat().st_size <= 0:
                raise RuntimeError(f"write_still omitted output: {output_path}")
    if write_still_count != 20 or rendered_order != [record["relativePath"] for record in preflight["outputs"]]:
        raise RuntimeError("exact write_still/order contract failed")
    write_json(output_root / "render-order.json", rendered_order)
    metrics = scene_metrics(materials, roots)
    if metrics["sourceTrianglesBeforeModifiers"] > preflight["budgets"]["sourceTriangles"]:
        raise RuntimeError(f"source triangle budget exceeded: {metrics['sourceTrianglesBeforeModifiers']}")
    write_json(output_root / "scene-metrics.json", metrics)


def main() -> int:
    parser = argparse.ArgumentParser()
    probe_group = parser.add_mutually_exclusive_group()
    probe_group.add_argument("--camera-probe", action="store_true")
    probe_group.add_argument("--matrix-probe", action="store_true")
    parser.add_argument("--probe-plan", type=Path)
    parser.add_argument("--matrix-probe-plan", type=Path)
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
    output_root = arguments.output.resolve(strict=True)
    if arguments.matrix_probe:
        if arguments.matrix_probe_plan is None or arguments.probe_plan is not None or arguments.preflight is not None:
            parser.error("--matrix-probe requires --matrix-probe-plan and forbids other plan inputs")
        matrix_plan_path = arguments.matrix_probe_plan.resolve(strict=True)
        matrix_plan = validate_matrix_probe_input(matrix_plan_path, output_root)
        run_full_matrix_probe(matrix_plan, output_root)
    elif arguments.camera_probe:
        if arguments.probe_plan is None or arguments.preflight is not None or arguments.matrix_probe_plan is not None:
            parser.error("--camera-probe requires --probe-plan and forbids other plan inputs")
        plan_path = arguments.probe_plan.resolve(strict=True)
        plan = validate_camera_probe_input(plan_path, output_root)
        run_camera_probe(plan, output_root)
    else:
        if arguments.preflight is None or arguments.probe_plan is not None or arguments.matrix_probe_plan is not None:
            parser.error("diagnostic mode requires --preflight and forbids probe plans")
        preflight_path = arguments.preflight.resolve(strict=True)
        preflight = validate_input(preflight_path, output_root)
        generate(preflight, output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
