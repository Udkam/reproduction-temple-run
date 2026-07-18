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
EXPECTED_CONTRACT = "TEMPLE-TR4-C7"
EXPECTED_SEED = 1414090053
EXPECTED_BLENDER_VERSION = "4.5.5 LTS"
DIAGNOSTIC_ID = "007"
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
C6_CONSTRUCTION_SHA256 = "2ab30e4580a7bdf6b8eeddf8dcd2acc5d17fa3c101aecc9d530cbea535c79c10"

MATERIAL_PARAMETERS = {
    "sandstone": {"mappingScale": [1, 1, 1], "macroScale": .65, "macroDetail": 5, "macroRoughness": .68, "microScale": 8.5, "microDetail": 3, "voronoiScale": 2.4, "voronoiRandomness": .65, "rampLow": "#8F7659", "rampHigh": "#D8B98C", "roughnessRange": [.72, .94], "bumpDistance": .18, "bumpStrength": .42},
    "fresh-break": {"mappingScale": [1, 1, 1], "macroScale": 1.2, "macroDetail": 4, "macroRoughness": .62, "microScale": 12, "microDetail": 3, "voronoiScale": 3.2, "voronoiRandomness": .70, "rampLow": "#5E4A37", "rampHigh": "#8F7659", "roughnessRange": [.82, .96], "bumpDistance": .22, "bumpStrength": .58},
    "basalt": {"mappingScale": [1, 1, 1], "macroScale": .55, "macroDetail": 5, "macroRoughness": .72, "microScale": 7, "microDetail": 4, "voronoiScale": 1.8, "voronoiRandomness": .58, "rampLow": "#111A20", "rampHigh": "#263846", "roughnessRange": [.64, .90], "bumpDistance": .20, "bumpStrength": .48},
    "basalt-strata": {"mappingScale": [.55, 2.8, .55], "macroScale": .80, "macroDetail": 4, "macroRoughness": .66, "microScale": 10, "microDetail": 3, "voronoiScale": 2.2, "voronoiRandomness": .55, "rampLow": "#24343E", "rampHigh": "#405764", "roughnessRange": [.70, .92], "bumpDistance": .24, "bumpStrength": .62},
    "cloth": {"mappingScale": [1, 1, 1], "macroScale": 3.5, "macroDetail": 3, "macroRoughness": .55, "microScale": 32, "microDetail": 2, "voronoiScale": 10, "voronoiRandomness": .50, "rampLow": "#172B36", "rampHigh": "#294756", "roughnessRange": [.78, .94], "bumpDistance": .035, "bumpStrength": .24},
    "leather": {"mappingScale": [1, 1, 1], "macroScale": 2.2, "macroDetail": 4, "macroRoughness": .60, "microScale": 18, "microDetail": 3, "voronoiScale": 7, "voronoiRandomness": .62, "rampLow": "#20282C", "rampHigh": "#394247", "roughnessRange": [.66, .84], "bumpDistance": .055, "bumpStrength": .32},
    "rock-armour": {"mappingScale": [1, 1, 1], "macroScale": .75, "macroDetail": 5, "macroRoughness": .70, "microScale": 9, "microDetail": 4, "voronoiScale": 2.7, "voronoiRandomness": .68, "rampLow": "#0A1014", "rampHigh": "#1B2830", "roughnessRange": [.62, .86], "bumpDistance": .20, "bumpStrength": .54},
}


def material_graph_contract() -> dict[str, Any]:
    return {
        "coordinateSource": "Generated",
        "graphOrder": ["sandstone", "fresh-break", "basalt", "basalt-strata", "cloth", "leather", "rock-armour"],
        "template": {
            "nodeOrder": ["TextureCoordinate", "Mapping", "MacroNoise", "MicroNoise", "Voronoi", "MacroRamp", "RoughnessMap", "HeightMix", "Bump", "Principled", "MaterialOutput"],
            "nodeTypeByName": {"TextureCoordinate": "ShaderNodeTexCoord", "Mapping": "ShaderNodeMapping", "MacroNoise": "ShaderNodeTexNoise", "MicroNoise": "ShaderNodeTexNoise", "Voronoi": "ShaderNodeTexVoronoi", "MacroRamp": "ShaderNodeValToRGB", "RoughnessMap": "ShaderNodeMapRange", "HeightMix": "ShaderNodeMixRGB", "Bump": "ShaderNodeBump", "Principled": "ShaderNodeBsdfPrincipled", "MaterialOutput": "ShaderNodeOutputMaterial"},
            "linkOrder": ["TextureCoordinate.Generated->Mapping.Vector", "Mapping.Vector->MacroNoise.Vector", "Mapping.Vector->MicroNoise.Vector", "Mapping.Vector->Voronoi.Vector", "MacroNoise.Fac->MacroRamp.Fac", "MacroNoise.Fac->RoughnessMap.Value", "MicroNoise.Fac->HeightMix.Color1", "Voronoi.Distance->HeightMix.Color2", "HeightMix.Color->Bump.Height", "Bump.Normal->Principled.Normal", "MacroRamp.Color->Principled.Base Color", "RoughnessMap.Result->Principled.Roughness", "Principled.BSDF->MaterialOutput.Surface"],
            "rampPositions": [.28, .72], "heightMixBlend": "MULTIPLY", "roughnessMapClamp": True,
            "parameterBindings": {"mappingScale": "Mapping.inputs[Scale].default_value", "macroScale": "MacroNoise.inputs[Scale].default_value", "macroDetail": "MacroNoise.inputs[Detail].default_value", "macroRoughness": "MacroNoise.inputs[Roughness].default_value", "microScale": "MicroNoise.inputs[Scale].default_value", "microDetail": "MicroNoise.inputs[Detail].default_value", "voronoiScale": "Voronoi.inputs[Scale].default_value", "voronoiRandomness": "Voronoi.inputs[Randomness].default_value", "rampLow": "MacroRamp.color_ramp.elements[0].color:sRGB-to-linear-RGBA", "rampHigh": "MacroRamp.color_ramp.elements[1].color:sRGB-to-linear-RGBA", "rampPositions[0]": "MacroRamp.color_ramp.elements[0].position", "rampPositions[1]": "MacroRamp.color_ramp.elements[1].position", "roughnessRange[0]": "RoughnessMap.inputs[To Min].default_value", "roughnessRange[1]": "RoughnessMap.inputs[To Max].default_value", "bumpDistance": "Bump.inputs[Distance].default_value", "bumpStrength": "Bump.inputs[Strength].default_value", "materials[name].metallic": "Principled.inputs[Metallic].default_value", "materials[name].normalStrength": "equals:parameters[name].bumpStrength"},
            "fixedNodeProperties": {"TextureCoordinate.from_instancer": False, "Mapping.vector_type": "POINT", "MacroNoise.noise_dimensions": "3D", "MacroNoise.noise_type": "FBM", "MacroNoise.normalize": True, "MicroNoise.noise_dimensions": "3D", "MicroNoise.noise_type": "FBM", "MicroNoise.normalize": True, "Voronoi.voronoi_dimensions": "3D", "Voronoi.feature": "F1", "Voronoi.distance": "EUCLIDEAN", "MacroRamp.color_ramp.interpolation": "LINEAR", "MacroRamp.color_ramp.color_mode": "RGB", "MacroRamp.color_ramp.hue_interpolation": "NEAR", "RoughnessMap.data_type": "FLOAT", "RoughnessMap.interpolation_type": "LINEAR", "RoughnessMap.clamp": True, "HeightMix.blend_type": "MULTIPLY", "HeightMix.use_clamp": False, "Bump.invert": False},
            "fixedSocketValues": {"Mapping.Location": [0, 0, 0], "Mapping.Rotation": [0, 0, 0], "MacroNoise.Lacunarity": 2, "MacroNoise.Distortion": 0, "MicroNoise.Roughness": .55, "MicroNoise.Lacunarity": 2, "MicroNoise.Distortion": 0, "Voronoi.Detail": 0, "Voronoi.Roughness": .5, "Voronoi.Lacunarity": 2, "Voronoi.Smoothness": 0, "Voronoi.Exponent": .5, "RoughnessMap.From Min": 0, "RoughnessMap.From Max": 1, "HeightMix.Fac": 1, "Principled.Weight": 1, "Principled.IOR": 1.5, "Principled.Alpha": 1, "Principled.Subsurface Weight": 0, "Principled.Specular IOR Level": .5, "Principled.Transmission Weight": 0, "Principled.Coat Weight": 0, "Principled.Sheen Weight": 0, "Principled.Emission Color": [0, 0, 0, 1], "Principled.Emission Strength": 0},
        },
        "parameters": MATERIAL_PARAMETERS,
    }


def atmosphere_contract() -> dict[str, Any]:
    return {
        "mode": "beer-lambert-depth-composite", "worldVolumeEnabled": False,
        "depthSource": "RenderLayers.Depth", "density": .0035, "fogColor": "#9AA7A8",
        "backgroundPolicy": "fog-color", "viewTransform": "AgX", "look": "AgX - Medium High Contrast",
        "exposure": 0, "gamma": 1,
        "nodeOrder": ["RenderLayers", "NegDensity", "ExpTransmittance", "OneMinusTransmittance", "FogColor", "MixFog", "Composite"],
        "nodeTypeByName": {"RenderLayers": "CompositorNodeRLayers", "NegDensity": "CompositorNodeMath", "ExpTransmittance": "CompositorNodeMath", "OneMinusTransmittance": "CompositorNodeMath", "FogColor": "CompositorNodeRGB", "MixFog": "CompositorNodeMixRGB", "Composite": "CompositorNodeComposite"},
        "operationByName": {"NegDensity": "MULTIPLY", "ExpTransmittance": "EXPONENT", "OneMinusTransmittance": "SUBTRACT", "MixFog": "MIX"},
        "linkOrder": ["RenderLayers.Depth->NegDensity.Value", "NegDensity.Value->ExpTransmittance.Value", "ExpTransmittance.Value->OneMinusTransmittance.Value", "OneMinusTransmittance.Value->MixFog.Fac", "RenderLayers.Image->MixFog.Color1", "FogColor.Image->MixFog.Color2", "MixFog.Image->Composite.Image"],
    }


def depth_encoding_contract() -> dict[str, Any]:
    return {"distanceMetric": "euclidean-camera-distance-meters", "nearSource": "cameras[].near", "ceilingByProfile": {"portrait": 160, "desktop": 160, "landscape": 160, "closeup": 80}, "foregroundScale": .94, "backgroundValue": 65535, "bitDepth": 16, "colorType": 0, "rounding": "floor(x+0.5)", "foregroundQuantileSample": "known-object-id-nonbackground-and-depth-not-65535", "semanticSampleSource": "exact-object-id-palette"}


def expected_construction() -> dict[str, Any]:
    band_data = {
        "near": ([8.0, 16.0], .86, 8, .72, [-8.0, 10.0], [-100.0, -10.0], "layered-ridge-near-v1", 9, 3, 2, 2),
        "mid": ([18.0, 34.0], .58, 10, .48, [-12.0, 18.0], [-140.0, -20.0], "layered-ridge-mid-v1", 8, 3, 2, 2),
        "far": ([38.0, 70.0], .30, 12, .24, [-16.0, 30.0], [-180.0, -35.0], "layered-ridge-far-v1", 7, 2, 1, 1),
    }
    canyon: dict[str, Any] = {"bandOrder": ["near", "mid", "far"]}
    for name, values in band_data.items():
        abs_x, contrast, count, saturation, y_range, z_range, recipe, ridge, terraces, overhangs, recesses = values
        canyon[name] = {"absXRange": abs_x, "contrast": contrast, "count": count, "saturation": saturation, "yRange": y_range, "zRange": z_range, "recipe": recipe, "ridgeSegmentsPerSignature": ridge, "terracesPerSignature": terraces, "overhangsPerSignature": overhangs, "recessesPerSignature": recesses}
    canyon.update({"negativeSpaceCount": 3, "occlusionBoundaryCount": 2, "fullWidthWaterVisible": False})
    hazards = {
        "order": ["beam", "ring", "column", "gap"],
        "beam": {"semanticRoot": "TR4_Hazard_Beam", "action": "jump", "collisionProxy": {"height": .82, "widthAll": 5.84, "widthLane": .84}, "visualBounds": {"topYRange": [.68, .76], "widthLaneMax": 1.55}, "socketOrder": ["entry", "apex.clearance", "exit", "ground.L", "ground.R"], "visualName": "Fault Lip", "baseEmbedRange": [.08, .15], "maxProxyDiscrepancy": .06, "coPlanarFacesAllowed": False},
        "ring": {"semanticRoot": "TR4_Hazard_Ring", "action": "slide", "collisionProxy": {"laneWidth": .84, "requiresSlide": True}, "visualBounds": {"lowestSolidY": 1.05, "openingHeight": .90, "widthLaneMax": 1.55}, "socketOrder": ["entry", "slide.clearance", "exit", "ground.L", "ground.R"], "visualName": "Coral Throat", "baseEmbedRange": [.08, .15], "maxProxyDiscrepancy": .06, "coPlanarFacesAllowed": False},
        "column": {"semanticRoot": "TR4_Hazard_Column", "action": "lane-change", "collisionProxy": {"laneWidth": .84}, "visualBounds": {"widthLaneMax": 1.55}, "socketOrder": ["entry", "safe.left", "safe.right", "exit", "ground"], "visualName": "Basalt Splitter", "baseEmbedRange": [.08, .15], "maxProxyDiscrepancy": .06, "coPlanarFacesAllowed": False},
        "gap": {"semanticRoot": "TR4_Gap_Lips", "action": "jump", "collisionProxy": {"clearanceHeight": .52, "lengthFromCanonicalEvent": True}, "visualBounds": {"hiddenFloor": False, "lipDepthMin": .55}, "socketOrder": ["takeoff", "apex.clearance", "landing"], "visualName": "Tidebreak Gap", "baseEmbedRange": [.08, .15], "maxProxyDiscrepancy": .06, "coPlanarFacesAllowed": False},
    }
    lighting = {
        "worldColor": "#6E8294", "worldStrength": .55,
        "key": {"color": "#FFD7A3", "energy": 4.2, "surfaceToLight": [-.51966, .77949, .34977], "shadow": True},
        "fill": {"color": "#7EA6C4", "energy": 1.1, "surfaceToLight": [.48019, .62025, -.62025], "shadow": False},
        "contact": {"color": "#E7C79C", "energy": 430.0, "shape": "DISK", "size": 9.0, "shadow": False, "location": [0.0, 7.5, 4.0], "target": [0.0, 0.0, -4.0]},
    }
    runner = {
        "partOrder": ["pelvis", "chest", "head", "upperArm.L", "forearm.L", "hand.L", "upperArm.R", "forearm.R", "hand.R", "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R", "coatTail.L", "coatTail.R"],
        "contactSocketOrder": ["ground.foot.L", "ground.foot.R", "camera.target"],
        "poseOrder": ["run.0", "run.1", "run.2", "run.3", "run.4", "run.5", "run.6", "run.7", "jump", "slide", "stumble", "failure"],
        "root": [0.0, 0.0, 0.0], "height": 2.32, "maxGroundError": .03, "triangleCeiling": 18000,
        "modelingMode": "profiled-articulated-mesh-v1", "minimumRadialSegments": 10, "primitiveJoinForbidden": True, "nonAdjacentIntersectionTolerance": 0,
    }
    pursuer = {
        "partOrder": ["pelvisPlate", "ribPlate", "shoulderPlate", "neck", "head", "jaw", "foreleg.L.upper", "foreleg.L.lower", "paw.L.front", "foreleg.R.upper", "foreleg.R.lower", "paw.R.front", "hindleg.L.upper", "hindleg.L.lower", "paw.L.rear", "hindleg.R.upper", "hindleg.R.lower", "paw.R.rear", "dorsalSeam"],
        "contactSocketOrder": ["ground.front.L", "ground.front.R", "ground.rear.L", "ground.rear.R", "capture.target"],
        "bookendRoot": [0.0, 0.0, 2.4], "height": 1.78, "maxGroundError": .03, "triangleCeiling": 24000,
        "modelingMode": "separated-rock-plate-quadruped-v1", "minimumRadialSegments": 10, "primitiveJoinForbidden": True, "bodyCoreSeparationMin": .18,
    }
    road = {"surfaceY": 0.0, "width": 6.4, "bounds": [-3.2, 3.2], "visualSafetyBounds": [-2.92, 2.92], "moduleCount": 16, "moduleLengthRange": [6.0, 11.0], "thicknessRange": [.55, 1.2], "sideDepthRange": [2.5, 8.0], "signatureOrder": ["terrace-fracture", "buttress-recess", "collapsed-lip", "strata-undercut", "rubble-shoulder", "split-ledge"], "maxConsecutiveSignatureRepeats": 2, "strataEventsPerModule": 2, "rubbleEventsPerModule": 1, "nearLoopShoulder": {"rightOuterX": 4.45, "zRange": [-5.2, -2.8]}, "capCrosswiseSegments": 9, "capLongitudinalSegmentsPerModule": 8, "fractureEventsPerModule": 3, "undercutEventsPerModule": 2, "sideApronsPerModule": 2, "vistaBendStartZ": -82, "vistaBendMaxOffsetX": 12}
    tide_scar = {
        "mainWidthRange": [.075, .11], "mainCenterXRange": [3.0, 3.06], "surfaceOffsetY": .035,
        "mainControlPoints": [[3.03, .035, 8.0], [3.05, .035, 0.0], [3.01, .035, -10.0], [3.06, .035, -22.0], [3.02, .035, -36.0], [3.04, .035, -52.0], [3.00, .035, -70.0], [3.05, .035, -92.0], [3.02, .035, -120.0]],
        "loopControlPoints": [[3.000, .035, -3.20], [3.054, .035, -2.87], [3.198, .035, -2.64], [3.390, .035, -2.55], [3.588, .035, -2.64], [3.732, .035, -2.87], [3.780, .035, -3.20], [3.732, .035, -3.52], [3.588, .035, -3.76], [3.390, .035, -3.85], [3.198, .035, -3.76], [3.054, .035, -3.52], [3.000, .035, -3.20]],
        "gapClipPadding": .35, "hazardClipPadding": .25, "nearLoopVisibilityProfile": "portrait", "bakedTextureAllowed": False,
    }
    return {"atmosphere": atmosphere_contract(), "axis": {"forward": "-Z", "right": "+X", "up": "+Y"}, "canyon": canyon, "depthEncoding": depth_encoding_contract(), "hazards": hazards, "lighting": lighting, "materialGraphs": material_graph_contract(), "pursuer": pursuer, "road": road, "runner": runner, "tideScar": tide_scar, "unitMeters": 1.0}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def frozen_camera_records() -> list[dict[str, Any]]:
    def normalize3(value: list[float]) -> list[float]:
        magnitude=math.sqrt(sum(component*component for component in value)); return [component/magnitude for component in value]
    def cross3(a: list[float],b: list[float]) -> list[float]: return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    def dot3(a: list[float],b: list[float]) -> float: return sum(x*y for x,y in zip(a,b))
    source=[("portrait",[540,960],[270,480],[0.0,6.20,15.20],[0.0,.55,-16.80],40.0,.08,520.0,-.055),("desktop",[960,540],[480,270],[0.0,6.06,13.60],[0.0,.60,-13.30],43.0,.08,520.0,-.025),("landscape",[844,390],[422,195],[0.0,6.15,12.80],[0.0,.55,-12.56],46.0,.08,520.0,-.020),("closeup",[640,480],[320,240],[0.0,5.40,9.80],[0.0,1.15,-3.40],48.0,.05,180.0,0.0)]
    result=[]
    for profile,resolution,diagnostic,position,target,fov,near,far,shift in source:
        up=[0.0,1.0,0.0]; forward=normalize3([target[i]-position[i] for i in range(3)]); right=normalize3(cross3(forward,up)); true_up=normalize3(cross3(right,forward)); backward=[-v for v in forward]
        row=[right[0],right[1],right[2],-dot3(right,position),true_up[0],true_up[1],true_up[2],-dot3(true_up,position),backward[0],backward[1],backward[2],-dot3(backward,position),0.0,0.0,0.0,1.0]
        view=[row[(i%4)*4+i//4] for i in range(16)]; aspect=resolution[0]/resolution[1]; reciprocal=1.0/math.tan(math.radians(fov)/2); projection=[0.0]*16; projection[0]=reciprocal/aspect; projection[5]=reciprocal; projection[9]=shift; projection[10]=-(far+near)/(far-near); projection[11]=-1.0; projection[14]=-(2*far*near)/(far-near)
        ordinary={"runnerAnchor":[0.0,1.20,0.0],"runnerHead":[0.0,2.05,-.25],"runnerFootL":[-.25,.085,-.56],"runnerFootR":[.25,.08,.22]}; failure={"runnerAnchor":[.46,1.08,-.34],"runnerHead":[.57,1.46,-.62],"runnerFootL":[-.48,.075,-.72],"runnerFootR":[1.02,.075,.48]}
        anchors={**(failure if profile=="closeup" else ordinary),"beam":[0.0,.72,-18.0],"ring":[0.0,1.05,-36.0],"column":[0.0,1.12,-54.0],"gap":[0.0,0.0,-74.0],"scar":[3.03,.035,0.0],"routeCenter":[0.0,.035,0.0],"farRoute":[0.0,0.0,-120.0]}
        result.append({"profile":profile,"resolution":resolution,"diagnosticResolution":diagnostic,"position":position,"target":target,"up":up,"verticalFovDegrees":fov,"aspect":aspect,"near":near,"far":far,"lensShiftY":shift,"viewMatrix":view,"projectionMatrix":projection,"projectionAnchors":anchors})
    return result


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
    expected_output=(Path(__file__).resolve(strict=True).parents[2]/"docs/workstreams/temple-tr4-asset/diagnostic-007").resolve(strict=False)
    if output_root != expected_output or output_root.name != "diagnostic-007" or preflight_path.name != "preflight.json" or preflight_path.parent != output_root:
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
        or schema_version != 7
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
    expected_reference={"path":r"C:\Users\ALEXCH~1\AppData\Local\Temp\codex-clipboard-ca70825b-99a6-4290-8307-4d90b2077d48.png","width":941,"height":1672,"sha256":"8fc0c6a7f7fc8d7e5b65fd3d256dee33ccfeede0e4aba4a04657c66a93e33074"}
    if canonical_bytes(preflight.get("reference")) != canonical_bytes(expected_reference):
        raise RuntimeError("reference record mismatch")
    reference_path=Path(expected_reference["path"]).resolve(strict=True)
    if not reference_path.is_file() or sha256_file(reference_path)!=expected_reference["sha256"]:
        raise RuntimeError("reference file/hash mismatch")
    expected_tools={"blenderExecutable":r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe","blenderVersion":"4.5.5 LTS","pythonVersion":"3.12.0","gltfTransformVersion":"not-invoked-diagnostic","ktxVersion":"not-invoked-diagnostic"}
    if canonical_bytes(preflight.get("tools")) != canonical_bytes(expected_tools):
        raise RuntimeError("tool record mismatch")
    scripts=preflight.get("scripts")
    if not isinstance(scripts,dict) or sorted(scripts)!=["evaluator","generator","runner"]:
        raise RuntimeError("script record key mismatch")
    script_dir=Path(__file__).resolve(strict=True).parent
    for name,filename in (("generator","generate_tide_scar_tr4_pack.py"),("evaluator","evaluate_tide_scar_tr4_pack.py"),("runner","run_tide_scar_tr4_pack.py")):
        record=scripts[name]
        if not isinstance(record,dict) or sorted(record)!=["path","sha256"]:
            raise RuntimeError(f"script child schema mismatch: {name}")
        actual_path=Path(record["path"]).resolve(strict=True)
        if actual_path != (script_dir/filename).resolve(strict=True) or record["sha256"] != sha256_file(actual_path):
            raise RuntimeError(f"script provenance mismatch: {name}")
    generator_record = scripts["generator"]
    if Path(generator_record.get("path", "")).resolve(strict=True) != Path(__file__).resolve(strict=True):
        raise RuntimeError("generator path mismatch")
    if generator_record.get("sha256") != sha256_file(Path(__file__).resolve(strict=True)):
        raise RuntimeError("generator hash mismatch")
    if [record.get("name") for record in preflight.get("semanticRoots", [])] != ROOT_NAMES:
        raise RuntimeError("semantic root contract mismatch")
    expected = expected_construction()
    if canonical_bytes(preflight["construction"]) != canonical_bytes(expected):
        raise RuntimeError("C7 closed construction mismatch")
    construction_bytes = canonical_bytes(preflight["construction"])
    if hashlib.sha256(construction_bytes).hexdigest() != preflight["constructionHash"]:
        raise RuntimeError("construction hash mismatch")
    if preflight["constructionHash"] == C6_CONSTRUCTION_SHA256:
        raise RuntimeError("C6 construction reuse is forbidden")
    expected_material_values = [
        ("sandstone", "#D8B98C", .82, .01, .42), ("fresh-break", "#8F7659", .90, .00, .58),
        ("basalt", "#1B2935", .78, .02, .48), ("basalt-strata", "#334653", .86, .01, .62),
        ("tide-scar", "#F2EAD7", .90, .00, .12), ("coral-mineral", "#B44A38", .74, .03, .36),
        ("skin", "#8A5B45", .70, .00, .18), ("cloth", "#203746", .88, .00, .24),
        ("leather", "#2A3338", .76, .02, .32), ("rock-armour", "#111A20", .72, .04, .54),
    ]
    expected_materials = [{"name": n, "baseColor": c, "roughness": r, "metallic": m, "normalStrength": s} for n, c, r, m, s in expected_material_values]
    if canonical_bytes(preflight.get("materials")) != canonical_bytes(expected_materials):
        raise RuntimeError("C7 top-level material contract mismatch")
    expected_scene = {
        "gameplay": {"id": "tr4-diagnostic-running-007", "status": "running", "tick": 240, "elapsedTicks": 240, "distance": 32.0, "lane": 0, "posture": "run", "gaitPhase": .25, "runnerRoot": [0, 0, 0], "pursuerPresent": False, "hazards": [{"kind": "beam", "courseDistance": 18.0}, {"kind": "ring", "courseDistance": 36.0}, {"kind": "column", "courseDistance": 54.0}, {"kind": "gap", "courseDistance": 72.0}]},
        "bookend": {"id": "tr4-diagnostic-game-over-007", "status": "game-over", "tick": 420, "elapsedTicks": 420, "distance": 63.0, "failureReason": "pursuer-caught", "posture": "failure", "runnerRoot": [0, 0, 0], "pursuerPresent": True, "pursuerRoot": [0, 0, 2.4]},
    }
    if canonical_bytes(preflight.get("scene")) != canonical_bytes(expected_scene):
        raise RuntimeError("C7 scene identity/state mismatch")
    expected_collision = {"laneWidth": 2.35, "laneCenters": [-2.35, 0, 2.35], "laneTolerance": .42, "roadBounds": [-3.2, 3.2], "visualSafetyBounds": [-2.92, 2.92], "beamClearanceHeight": .82, "gapClearanceHeight": .52, "slideTicks": 31, "ringLowestSolidY": 1.05, "slidePoseMaxY": .90, "visualPadding": .15}
    if canonical_bytes(preflight.get("collision")) != canonical_bytes(expected_collision):
        raise RuntimeError("C7 collision contract mismatch")
    expected_budgets = {"desktopDecodedTextureBytes": 39845888, "desktopDrawCalls": 60, "desktopVisibleTriangles": 150000, "materialCount": 10, "mobileDecodedTextureBytes": 18874368, "mobileDrawCalls": 45, "mobileVisibleTriangles": 100000, "optimizedGlbBytes": 8388608, "optimizedTriangles": 110000, "sourceTriangles": 150000}
    if canonical_bytes(preflight.get("budgets")) != canonical_bytes(expected_budgets):
        raise RuntimeError("C7 budget contract mismatch")
    expected_roots = [{"name": name, "parent": None, "translation": [0, 0, 0], "rotation": [0, 0, 0, 1], "scale": [1, 1, 1]} for name in ROOT_NAMES]
    if canonical_bytes(preflight.get("semanticRoots")) != canonical_bytes(expected_roots):
        raise RuntimeError("C7 semantic-root record mismatch")
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
    if canonical_bytes(cameras) != canonical_bytes(frozen_camera_records()):
        raise RuntimeError("frozen camera records/matrices mismatch")
    lighting = preflight["construction"].get("lighting")
    if not isinstance(lighting, dict) or sorted(lighting.keys()) != sorted(["worldColor", "worldStrength", "key", "fill", "contact"]):
        raise RuntimeError("lighting construction schema mismatch")
    outputs = preflight.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != 20:
        raise RuntimeError("closed output list mismatch")
    expected_order = [(profile, pass_name) for profile in PROFILE_ORDER for pass_name in PASS_ORDER]
    actual_order = [(record.get("profile"), record.get("pass")) for record in outputs]
    if actual_order != expected_order or [record.get("index") for record in outputs] != list(range(20)):
        raise RuntimeError("output order mismatch")
    output_keys = ["index", "profile", "pass", "sceneId", "relativePath", "width", "height"]
    expected_names = [f"tr4-diagnostic-007-{profile}-{pass_name}.png" for profile, pass_name in expected_order]
    if [record.get("relativePath") for record in outputs] != expected_names:
        raise RuntimeError("diagnostic-007 output filename mismatch")
    dimensions = {"portrait": (270, 480), "desktop": (480, 270), "landscape": (422, 195), "closeup": (320, 240)}
    for record in outputs:
        expected_scene = "tr4-diagnostic-game-over-007" if record["profile"] == "closeup" else "tr4-diagnostic-running-007"
        if sorted(record.keys()) != sorted(output_keys) or record["sceneId"] != expected_scene or (record["width"], record["height"]) != dimensions[record["profile"]]:
            raise RuntimeError(f"diagnostic-007 output record mismatch: {record.get('index')}")
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


def comparable_value(value: Any) -> Any:
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    try:
        return [float(component) for component in value]
    except (TypeError, ValueError):
        return str(value)


def values_close(left: Any, right: Any, tolerance: float = 1.0e-6) -> bool:
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right))
    if isinstance(left, (int, float)) and isinstance(right, (int, float)) and not isinstance(left, bool) and not isinstance(right, bool):
        return abs(float(left) - float(right)) <= tolerance
    return left == right


def normalize_readback(actual: Any, expected: Any) -> Any:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or sorted(actual) != sorted(expected): raise RuntimeError("readback object schema mismatch")
        return {key: normalize_readback(actual[key],expected[key]) for key in expected}
    if isinstance(expected, list):
        if not isinstance(actual,list) or len(actual)!=len(expected): raise RuntimeError("readback array schema mismatch")
        return [normalize_readback(a,e) for a,e in zip(actual,expected)]
    if isinstance(expected,bool):
        if actual is not expected: raise RuntimeError("readback boolean mismatch")
        return actual
    if isinstance(expected,(int,float)):
        if isinstance(actual,bool) or not isinstance(actual,(int,float)) or abs(float(actual)-float(expected))>1e-6: raise RuntimeError(f"readback numeric mismatch: {actual}!={expected}")
        return int(round(actual)) if isinstance(expected,int) else float(actual)
    if actual != expected: raise RuntimeError(f"readback scalar mismatch: {actual}!={expected}")
    return actual


def factory_default_audit(nodes: Any, created: dict[str, bpy.types.Node]) -> dict[str, Any]:
    allowed_inputs = {
        "Mapping": {"Location", "Rotation", "Scale", "Vector"},
        "MacroNoise": {"Vector", "Scale", "Detail", "Roughness", "Lacunarity", "Distortion"},
        "MicroNoise": {"Vector", "Scale", "Detail", "Roughness", "Lacunarity", "Distortion"},
        "Voronoi": {"Vector", "Scale", "Randomness", "Detail", "Roughness", "Lacunarity", "Smoothness", "Exponent"},
        "MacroRamp": {"Fac"},
        "RoughnessMap": {"Value", "From Min", "From Max", "To Min", "To Max"},
        "HeightMix": {"Fac", "Color1", "Color2"},
        "Bump": {"Strength", "Distance", "Height", "Normal"},
        "Principled": {"Base Color", "Roughness", "Metallic", "Normal", "Weight", "IOR", "Alpha", "Subsurface Weight", "Specular IOR Level", "Transmission Weight", "Coat Weight", "Sheen Weight", "Emission Color", "Emission Strength"},
        "MaterialOutput": {"Surface"},
    }
    explicit_properties={"TextureCoordinate":{"from_instancer"},"Mapping":{"vector_type"},"MacroNoise":{"noise_dimensions","noise_type","normalize"},"MicroNoise":{"noise_dimensions","noise_type","normalize"},"Voronoi":{"voronoi_dimensions","feature","distance"},"MacroRamp":set(),"RoughnessMap":{"data_type","interpolation_type","clamp"},"HeightMix":{"blend_type","use_clamp"},"Bump":{"invert"},"Principled":set(),"MaterialOutput":set()}
    ignored_properties={"rna_type","name","label","location","width","width_hidden","height","dimensions","select","show_options","show_preview","hide","mute","parent","use_custom_color","color","warning_propagation"}
    input_count=0; property_count=0
    for name, actual in created.items():
        factory_material=bpy.data.materials.new(f"TR4.FactoryAudit.{name}"); factory_material.use_nodes=True; factory_nodes=factory_material.node_tree.nodes; factory_nodes.clear(); factory=factory_nodes.new(actual.bl_idname)
        try:
            for socket in actual.inputs:
                if socket.name in allowed_inputs.get(name, set()) or socket.is_linked:
                    continue
                factory_socket = factory.inputs.get(socket.name)
                if factory_socket is None or not hasattr(socket, "default_value") or not hasattr(factory_socket, "default_value"):
                    continue
                if not values_close(comparable_value(socket.default_value), comparable_value(factory_socket.default_value)):
                    raise RuntimeError(f"material graph factory-default drift: {name}.{socket.name}")
                input_count += 1
            for prop in actual.bl_rna.properties:
                identifier=prop.identifier
                if identifier in ignored_properties or identifier in explicit_properties.get(name,set()) or getattr(prop,"is_readonly",False) or prop.type not in {"BOOLEAN","INT","FLOAT","STRING","ENUM"}:
                    continue
                left=comparable_value(getattr(actual,identifier)); right=comparable_value(getattr(factory,identifier))
                if not values_close(left,right): raise RuntimeError(f"material graph factory property drift: {name}.{identifier}")
                property_count += 1
        finally:
            bpy.data.materials.remove(factory_material)
    return {"freshFactoryPerNodeType": True, "unlistedInputsCompared": input_count, "unlistedPropertiesCompared": property_count, "verdict": "FACTORY_DEFAULTS_MATCH"}


def linear_hex(color: Any) -> str:
    def encode(value: float) -> int:
        srgb=12.92*value if value<=.0031308 else 1.055*(value**(1/2.4))-.055
        return max(0,min(255,int(math.floor(srgb*255+.5))))
    return "#"+"".join(f"{encode(float(value)):02X}" for value in color[:3])


def actual_material_graph_record(material: bpy.types.Material, material_record: dict[str, Any], expected_graph: dict[str, Any], factory_audit: dict[str, Any]) -> dict[str, Any]:
    nodes=material.node_tree.nodes; links=material.node_tree.links; by_name={node.name:node for node in nodes}; expected_template=expected_graph["template"]
    for node_name,sockets in {"Mapping":["Scale"],"MacroNoise":["Scale","Detail","Roughness"],"MicroNoise":["Scale","Detail"],"Voronoi":["Scale","Randomness"],"RoughnessMap":["To Min","To Max"],"Bump":["Distance","Strength"],"Principled":["Metallic"]}.items():
        if node_name not in by_name or any(by_name[node_name].inputs.get(socket) is None for socket in sockets): raise RuntimeError(f"material parameter target missing: {material_record['name']}:{node_name}")
    parameter_bindings={"mappingScale":f"{by_name['Mapping'].name}.inputs[Scale].default_value","macroScale":f"{by_name['MacroNoise'].name}.inputs[Scale].default_value","macroDetail":f"{by_name['MacroNoise'].name}.inputs[Detail].default_value","macroRoughness":f"{by_name['MacroNoise'].name}.inputs[Roughness].default_value","microScale":f"{by_name['MicroNoise'].name}.inputs[Scale].default_value","microDetail":f"{by_name['MicroNoise'].name}.inputs[Detail].default_value","voronoiScale":f"{by_name['Voronoi'].name}.inputs[Scale].default_value","voronoiRandomness":f"{by_name['Voronoi'].name}.inputs[Randomness].default_value","rampLow":f"{by_name['MacroRamp'].name}.color_ramp.elements[0].color:sRGB-to-linear-RGBA","rampHigh":f"{by_name['MacroRamp'].name}.color_ramp.elements[1].color:sRGB-to-linear-RGBA","rampPositions[0]":f"{by_name['MacroRamp'].name}.color_ramp.elements[0].position","rampPositions[1]":f"{by_name['MacroRamp'].name}.color_ramp.elements[1].position","roughnessRange[0]":f"{by_name['RoughnessMap'].name}.inputs[To Min].default_value","roughnessRange[1]":f"{by_name['RoughnessMap'].name}.inputs[To Max].default_value","bumpDistance":f"{by_name['Bump'].name}.inputs[Distance].default_value","bumpStrength":f"{by_name['Bump'].name}.inputs[Strength].default_value","materials[name].metallic":f"{by_name['Principled'].name}.inputs[Metallic].default_value","materials[name].normalStrength":"equals:parameters[name].bumpStrength"}
    template={
        "nodeOrder":[node.name for node in nodes],
        "nodeTypeByName":{name:by_name[name].bl_idname for name in [node.name for node in nodes]},
        "linkOrder":[f"{link.from_node.name}.{link.from_socket.name}->{link.to_node.name}.{link.to_socket.name}" for link in links],
        "rampPositions":[float(element.position) for element in by_name["MacroRamp"].color_ramp.elements],
        "heightMixBlend":by_name["HeightMix"].blend_type,"roughnessMapClamp":bool(by_name["RoughnessMap"].clamp),
        "parameterBindings":parameter_bindings,
        "fixedNodeProperties":{
            "TextureCoordinate.from_instancer":bool(by_name["TextureCoordinate"].from_instancer),"Mapping.vector_type":by_name["Mapping"].vector_type,"MacroNoise.noise_dimensions":by_name["MacroNoise"].noise_dimensions,"MacroNoise.noise_type":by_name["MacroNoise"].noise_type,"MacroNoise.normalize":bool(by_name["MacroNoise"].normalize),"MicroNoise.noise_dimensions":by_name["MicroNoise"].noise_dimensions,"MicroNoise.noise_type":by_name["MicroNoise"].noise_type,"MicroNoise.normalize":bool(by_name["MicroNoise"].normalize),"Voronoi.voronoi_dimensions":by_name["Voronoi"].voronoi_dimensions,"Voronoi.feature":by_name["Voronoi"].feature,"Voronoi.distance":by_name["Voronoi"].distance,"MacroRamp.color_ramp.interpolation":by_name["MacroRamp"].color_ramp.interpolation,"MacroRamp.color_ramp.color_mode":by_name["MacroRamp"].color_ramp.color_mode,"MacroRamp.color_ramp.hue_interpolation":by_name["MacroRamp"].color_ramp.hue_interpolation,"RoughnessMap.data_type":by_name["RoughnessMap"].data_type,"RoughnessMap.interpolation_type":by_name["RoughnessMap"].interpolation_type,"RoughnessMap.clamp":bool(by_name["RoughnessMap"].clamp),"HeightMix.blend_type":by_name["HeightMix"].blend_type,"HeightMix.use_clamp":bool(by_name["HeightMix"].use_clamp),"Bump.invert":bool(by_name["Bump"].invert)},
        "fixedSocketValues":{},
    }
    socket_targets={"Mapping.Location":("Mapping","Location"),"Mapping.Rotation":("Mapping","Rotation"),"MacroNoise.Lacunarity":("MacroNoise","Lacunarity"),"MacroNoise.Distortion":("MacroNoise","Distortion"),"MicroNoise.Roughness":("MicroNoise","Roughness"),"MicroNoise.Lacunarity":("MicroNoise","Lacunarity"),"MicroNoise.Distortion":("MicroNoise","Distortion"),"Voronoi.Detail":("Voronoi","Detail"),"Voronoi.Roughness":("Voronoi","Roughness"),"Voronoi.Lacunarity":("Voronoi","Lacunarity"),"Voronoi.Smoothness":("Voronoi","Smoothness"),"Voronoi.Exponent":("Voronoi","Exponent"),"RoughnessMap.From Min":("RoughnessMap","From Min"),"RoughnessMap.From Max":("RoughnessMap","From Max"),"HeightMix.Fac":("HeightMix","Fac"),"Principled.Weight":("Principled","Weight"),"Principled.IOR":("Principled","IOR"),"Principled.Alpha":("Principled","Alpha"),"Principled.Subsurface Weight":("Principled","Subsurface Weight"),"Principled.Specular IOR Level":("Principled","Specular IOR Level"),"Principled.Transmission Weight":("Principled","Transmission Weight"),"Principled.Coat Weight":("Principled","Coat Weight"),"Principled.Sheen Weight":("Principled","Sheen Weight"),"Principled.Emission Color":("Principled","Emission Color"),"Principled.Emission Strength":("Principled","Emission Strength")}
    for key,(node_name,socket_name) in socket_targets.items(): template["fixedSocketValues"][key]=comparable_value(by_name[node_name].inputs[socket_name].default_value)
    p=by_name
    parameters={"mappingScale":comparable_value(p["Mapping"].inputs["Scale"].default_value),"macroScale":float(p["MacroNoise"].inputs["Scale"].default_value),"macroDetail":float(p["MacroNoise"].inputs["Detail"].default_value),"macroRoughness":float(p["MacroNoise"].inputs["Roughness"].default_value),"microScale":float(p["MicroNoise"].inputs["Scale"].default_value),"microDetail":float(p["MicroNoise"].inputs["Detail"].default_value),"voronoiScale":float(p["Voronoi"].inputs["Scale"].default_value),"voronoiRandomness":float(p["Voronoi"].inputs["Randomness"].default_value),"rampLow":linear_hex(p["MacroRamp"].color_ramp.elements[0].color),"rampHigh":linear_hex(p["MacroRamp"].color_ramp.elements[1].color),"roughnessRange":[float(p["RoughnessMap"].inputs["To Min"].default_value),float(p["RoughnessMap"].inputs["To Max"].default_value)],"bumpDistance":float(p["Bump"].inputs["Distance"].default_value),"bumpStrength":float(p["Bump"].inputs["Strength"].default_value)}
    actual={"coordinateSource":"Generated","graphOrder":[material_record["name"]],"template":template,"parameters":{material_record["name"]:parameters}}
    expected_one={"coordinateSource":expected_graph["coordinateSource"],"graphOrder":[material_record["name"]],"template":expected_template,"parameters":{material_record["name"]:expected_graph["parameters"][material_record["name"]]}}
    normalized=normalize_readback(actual,expected_one)
    material["tr4_material_graph_readback"]=json.dumps(normalized,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":"))
    material["tr4_factory_default_audit"]=json.dumps(factory_audit,sort_keys=True,separators=(",",":"))
    return normalized


def create_simple_pbr_material(record: dict[str, Any]) -> bpy.types.Material:
    material = bpy.data.materials.new(record["name"])
    material.use_nodes = True
    material.diffuse_color = (*linear_rgb(record["baseColor"]), 1.0)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial"); output.name = "MaterialOutput"
    principled = nodes.new("ShaderNodeBsdfPrincipled"); principled.name = "Principled"
    principled.inputs["Base Color"].default_value = (*linear_rgb(record["baseColor"]), 1.0)
    principled.inputs["Roughness"].default_value = record["roughness"]
    principled.inputs["Metallic"].default_value = record["metallic"]
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def create_pbr_material(record: dict[str, Any], parameters: dict[str, Any], template: dict[str, Any]) -> bpy.types.Material:
    material = bpy.data.materials.new(record["name"])
    material.use_nodes = True
    material.diffuse_color = (*linear_rgb(record["baseColor"]), 1.0)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    created: dict[str, bpy.types.Node] = {}
    for name in template["nodeOrder"]:
        node = nodes.new(template["nodeTypeByName"][name])
        node.name = name
        node.label = name
        created[name] = node
    texture = created["TextureCoordinate"]
    mapping = created["Mapping"]
    macro = created["MacroNoise"]
    micro = created["MicroNoise"]
    voronoi = created["Voronoi"]
    ramp = created["MacroRamp"]
    roughness_map = created["RoughnessMap"]
    height_mix = created["HeightMix"]
    bump = created["Bump"]
    principled = created["Principled"]
    output = created["MaterialOutput"]
    texture.from_instancer = False
    mapping.vector_type = "POINT"
    mapping.inputs["Location"].default_value = (0.0, 0.0, 0.0)
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, 0.0)
    mapping.inputs["Scale"].default_value = parameters["mappingScale"]
    for node, prefix in ((macro, "macro"), (micro, "micro")):
        node.noise_dimensions = "3D"
        node.noise_type = "FBM"
        node.normalize = True
        node.inputs["Scale"].default_value = parameters[prefix + "Scale"]
        node.inputs["Detail"].default_value = parameters[prefix + "Detail"]
        node.inputs["Lacunarity"].default_value = 2.0
        node.inputs["Distortion"].default_value = 0.0
    macro.inputs["Roughness"].default_value = parameters["macroRoughness"]
    micro.inputs["Roughness"].default_value = .55
    voronoi.voronoi_dimensions = "3D"
    voronoi.feature = "F1"
    voronoi.distance = "EUCLIDEAN"
    voronoi.inputs["Scale"].default_value = parameters["voronoiScale"]
    voronoi.inputs["Randomness"].default_value = parameters["voronoiRandomness"]
    for socket_name, value in (("Detail", 0.0), ("Roughness", .5), ("Lacunarity", 2.0), ("Smoothness", 0.0), ("Exponent", .5)):
        if voronoi.inputs.get(socket_name) is not None:
            voronoi.inputs[socket_name].default_value = value
    ramp.color_ramp.interpolation = "LINEAR"
    ramp.color_ramp.color_mode = "RGB"
    ramp.color_ramp.hue_interpolation = "NEAR"
    ramp.color_ramp.elements[0].position = template["rampPositions"][0]
    ramp.color_ramp.elements[0].color = (*linear_rgb(parameters["rampLow"]), 1.0)
    ramp.color_ramp.elements[1].position = template["rampPositions"][1]
    ramp.color_ramp.elements[1].color = (*linear_rgb(parameters["rampHigh"]), 1.0)
    roughness_map.data_type = "FLOAT"
    roughness_map.interpolation_type = "LINEAR"
    roughness_map.clamp = True
    roughness_map.inputs["From Min"].default_value = 0.0
    roughness_map.inputs["From Max"].default_value = 1.0
    roughness_map.inputs["To Min"].default_value = parameters["roughnessRange"][0]
    roughness_map.inputs["To Max"].default_value = parameters["roughnessRange"][1]
    height_mix.blend_type = "MULTIPLY"
    height_mix.use_clamp = False
    height_mix.inputs["Fac"].default_value = 1.0
    bump.invert = False
    bump.inputs["Distance"].default_value = parameters["bumpDistance"]
    bump.inputs["Strength"].default_value = parameters["bumpStrength"]
    principled.inputs["Metallic"].default_value = record["metallic"]
    fixed_principled = {"Weight": 1.0, "IOR": 1.5, "Alpha": 1.0, "Subsurface Weight": 0.0, "Specular IOR Level": .5, "Transmission Weight": 0.0, "Coat Weight": 0.0, "Sheen Weight": 0.0, "Emission Color": (0.0, 0.0, 0.0, 1.0), "Emission Strength": 0.0}
    for socket_name, value in fixed_principled.items():
        if principled.inputs.get(socket_name) is not None:
            principled.inputs[socket_name].default_value = value
    link_specs = [
        (texture, "Generated", mapping, "Vector"), (mapping, "Vector", macro, "Vector"),
        (mapping, "Vector", micro, "Vector"), (mapping, "Vector", voronoi, "Vector"),
        (macro, "Fac", ramp, "Fac"), (macro, "Fac", roughness_map, "Value"),
        (micro, "Fac", height_mix, "Color1"), (voronoi, "Distance", height_mix, "Color2"),
        (height_mix, "Color", bump, "Height"), (bump, "Normal", principled, "Normal"),
        (ramp, "Color", principled, "Base Color"), (roughness_map, "Result", principled, "Roughness"),
        (principled, "BSDF", output, "Surface"),
    ]
    for source, source_socket, target, target_socket in link_specs:
        links.new(source.outputs[source_socket], target.inputs[target_socket])
    actual_links = [f"{link.from_node.name}.{link.from_socket.name}->{link.to_node.name}.{link.to_socket.name}" for link in links]
    if actual_links != template["linkOrder"]:
        raise RuntimeError(f"material graph link order mismatch: {record['name']}")
    if record["normalStrength"] != parameters["bumpStrength"]:
        raise RuntimeError(f"material normal/bump binding mismatch: {record['name']}")
    factory_audit=factory_default_audit(nodes, created)
    actual_material_graph_record(material,record,{"coordinateSource":"Generated","graphOrder":[record["name"]],"template":template,"parameters":{record["name"]:parameters}},factory_audit)
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
    if segments < 10 or rings < 6:
        raise RuntimeError(f"profiled mesh resolution below C7 contract: {name}")
    vertices: list[tuple[float, float, float]] = []
    for ring in range(rings + 1):
        v = ring / rings
        latitude = -math.pi * .5 + math.pi * v
        radial = math.cos(latitude)
        for segment in range(segments):
            angle = math.tau * segment / segments
            profile = 1.0 + .045 * math.sin(angle * 3.0 + len(name) * .37) * math.sin(math.pi * v)
            x = center[0] + math.cos(angle) * radial * scale[0] * profile
            y = center[1] + math.sin(latitude) * scale[1] * (1.0 + .025 * math.cos(angle*2.0))
            z = center[2] + math.sin(angle) * radial * scale[2] * (1.0 - .035*math.cos(angle*2.0))
            vertices.append((x,y,z))
    faces=[]
    for ring in range(rings):
        for segment in range(segments):
            nxt=(segment+1)%segments; a=ring*segments+segment; b=ring*segments+nxt; c=(ring+1)*segments+nxt; d=(ring+1)*segments+segment
            faces.append((a,b,c,d))
    obj = mesh_object(name, vertices, faces, material, parent, semantic, smooth=True, bevel=min(scale)*.035)
    obj["modelingMode"] = "profiled-articulated-mesh-v1" if semantic == "runner" else "separated-rock-plate-quadruped-v1" if semantic == "pursuer" else "authored-profile-v1"
    obj["radialSegments"] = segments
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
    axis = direction.normalized()
    tangent = axis.orthogonal().normalized()
    bitangent = axis.cross(tangent).normalized()
    radial_segments = 12
    length_segments = 5
    vertices=[]
    for along in range(length_segments+1):
        t=along/length_segments
        centerline=start_vector+direction*t
        radius=start_radius+(end_radius-start_radius)*t
        radius*=1.0+.10*math.sin(math.pi*t)
        for segment in range(radial_segments):
            angle=math.tau*segment/radial_segments
            elliptical=tangent*(math.cos(angle)*radius)+bitangent*(math.sin(angle)*radius*.82)
            point=centerline+elliptical
            vertices.append(tuple(point))
    faces=[]
    for along in range(length_segments):
        for segment in range(radial_segments):
            nxt=(segment+1)%radial_segments; a=along*radial_segments+segment; b=along*radial_segments+nxt; c=(along+1)*radial_segments+nxt; d=(along+1)*radial_segments+segment
            faces.append((a,b,c,d))
    faces.extend([tuple(reversed(range(radial_segments))),tuple(length_segments*radial_segments+i for i in range(radial_segments))])
    obj=mesh_object(name,vertices,faces,material,parent,semantic,smooth=True,bevel=min(start_radius,end_radius)*.12)
    obj["radialSegments"] = radial_segments
    obj["modelingMode"] = "profiled-articulated-mesh-v1" if semantic == "runner" else "separated-rock-plate-quadruped-v1" if semantic == "pursuer" else "authored-profile-v1"
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
    cross_segments = 9
    longitudinal_segments = 8
    thickness = 0.66 + 0.08 * (index % 6)
    vertex_columns = cross_segments + 1
    top_vertices: list[tuple[float, float, float]] = []
    left_edges: list[tuple[float, float, float]] = []
    right_edges: list[tuple[float, float, float]] = []
    for row in range(longitudinal_segments + 1):
        t = row / longitudinal_segments
        z = start_z + (end_z - start_z) * t
        bend_t = max(0.0, min(1.0, (-z - 82.0) / 52.0))
        center_x = 12.0 * bend_t * bend_t * (3.0 - 2.0 * bend_t)
        left = center_x - 3.2 + rng.uniform(-.14, .02)
        right = center_x + 3.2 + rng.uniform(-.02, .14)
        left_edges.append((left, 0.0, z)); right_edges.append((right, 0.0, z))
        for column in range(vertex_columns):
            u = column / cross_segments
            x = left + (right - left) * u
            edge_weight = abs(u - .5) * 2.0
            y = (math.sin((index * 9 + row * 3 + column) * 1.37) * .018 + rng.uniform(-.008, .008)) * edge_weight
            if .42 <= u <= .58:
                y = 0.0
            top_vertices.append((x, y, z))
    top_faces = []
    for row in range(longitudinal_segments):
        for column in range(cross_segments):
            a = row * vertex_columns + column
            top_faces.append((a, a + 1, a + vertex_columns + 1, a + vertex_columns))
    module = mesh_object(f"Road.Cap.{index:02d}.{signature}", top_vertices, top_faces, materials["sandstone"], root, "road", bevel=.025)
    module["signature"] = signature
    module["tr4_module_index"] = index
    module["tr4_start_z"] = start_z
    module["tr4_end_z"] = end_z
    module["tr4_thickness"] = thickness
    module["capCrosswiseSegments"] = cross_segments
    module["capLongitudinalSegments"] = longitudinal_segments
    result = [module]
    # A separate eroded break-face shell gives physical thickness without a flat box extrusion.
    side_vertices: list[tuple[float, float, float]] = []
    for row, (left, right) in enumerate(zip(left_edges, right_edges)):
        depth_jitter = thickness + .08 * math.sin(index * 1.7 + row * .9)
        side_vertices.extend([left, right, (left[0] + .16, -depth_jitter, left[2] + .04), (right[0] - .16, -depth_jitter, right[2] - .04)])
    side_faces: list[tuple[int, ...]] = []
    for row in range(longitudinal_segments):
        a = row * 4; b = (row + 1) * 4
        side_faces.extend([(a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1), (a + 2, b + 2, b + 3, a + 3)])
    side_faces.extend([(0, 2, 3, 1), (longitudinal_segments * 4, longitudinal_segments * 4 + 1, longitudinal_segments * 4 + 3, longitudinal_segments * 4 + 2)])
    result.append(mesh_object(f"Road.BreakFace.{index:02d}", side_vertices, side_faces, materials["fresh-break"], root, "road", bevel=.035))
    span = abs(end_z - start_z)
    for side in (-1.0, 1.0):
        for fragment in range(1):
            local_t = .36 + rng.uniform(-.04, .04)
            center_z = start_z + (end_z - start_z) * local_t
            bend_t = max(0.0, min(1.0, (-center_z - 82.0) / 52.0)); center_x = 12.0 * bend_t * bend_t * (3.0 - 2.0 * bend_t)
            inner_x = center_x + side * (3.18 + .08 * fragment)
            outer_x = center_x + side * (4.05 + .20 * fragment + rng.uniform(0, .22))
            ledge_y = -.68 - fragment * .72 - .07 * (index % 3)
            deep_side_y = ledge_y - 2.75
            ledge_vertices = [(inner_x, ledge_y + .12, center_z - span * .16), (outer_x, ledge_y + .04, center_z - span * .11), (outer_x + side * .14, ledge_y - .28, center_z + span * .12), (inner_x, ledge_y - .20, center_z + span * .17), (inner_x + side * .10, ledge_y - 2.35, center_z - span * .12), (outer_x - side * .08, deep_side_y, center_z), (inner_x + side * .08, ledge_y - 2.48, center_z + span * .13)]
            result.append(mesh_object(f"Road.Apron.{index:02d}.{('L' if side < 0 else 'R')}.{fragment}", ledge_vertices, [(0,1,2,3),(0,4,5,1),(3,2,5,6),(0,3,6,4),(1,5,2)], materials["fresh-break" if fragment == 0 else "sandstone"], root, "road", bevel=.035))
            undercut = [(inner_x, ledge_y-.18, center_z-span*.10),(outer_x,ledge_y-.26,center_z-span*.07),(outer_x-side*.18,ledge_y-2.10,center_z+span*.08),(inner_x+side*.10,ledge_y-1.95,center_z+span*.11)]
            result.append(mesh_object(f"Road.Undercut.{index:02d}.{('L' if side < 0 else 'R')}.{fragment}", undercut, [(0,1,2,3)], materials["basalt-strata"], root, "road", bevel=.018))
    for strata in range(2):
        row = 2 + strata * 4
        left, right = left_edges[row], right_edges[row]
        z = (left[2] + right[2]) * .5
        y = -.22 - strata * .18
        strip = [(left[0]+.12,y,z-.08),(right[0]-.12,y,z-.08),(right[0]-.18,y-.09,z+.08),(left[0]+.18,y-.09,z+.08)]
        strata_obj=mesh_object(f"Road.Strata.{index:02d}.{strata}",strip,[(0,1,2,3)],materials["basalt-strata"],root,"road",bevel=.012)
        strata_obj["tr4_event_id"] = f"road-strata-{index:02d}-{strata}"
    for fracture in range(3):
        z = start_z + (end_z - start_z) * (.20 + fracture * .29)
        side = -1.0 if (index + fracture) % 2 else 1.0
        bend_t = max(0.0, min(1.0, (-z - 82.0) / 52.0)); center_x = 12.0 * bend_t * bend_t * (3.0 - 2.0 * bend_t)
        x0 = center_x + side * (2.98 + .06 * fracture)
        seam = [(x0, .012, z-.42),(x0+side*.19,-.018,z-.12),(x0+side*.31,-.06,z+.24),(x0+side*.18,-.025,z+.48)]
        result.append(mesh_object(f"Road.Fracture.{index:02d}.{fracture}", seam, [(0,1,2,3)], materials["fresh-break"], root, "road", bevel=.012))
    rubble_z = start_z + (end_z - start_z) * .63
    rubble_cluster = make_empty(f"Road.RubbleCluster.{index:02d}.0", root)
    rubble_cluster["tr4_event_id"] = f"road-rubble-cluster-{index:02d}-0"
    rubble_cluster["tr4_piece_count"] = 3
    for rubble in range(3):
        side = -1.0 if (index + rubble) % 2 else 1.0
        bend_t = max(0.0, min(1.0, (-rubble_z - 82.0) / 52.0)); center_x = 12.0 * bend_t * bend_t * (3.0 - 2.0 * bend_t)
        result.append(create_rock_spire(f"Road.RubblePiece.{index:02d}.0.{rubble}", (center_x + side * (3.40 + rubble*.14), -.38, rubble_z + rubble*.27), .16 + rubble*.035, .40 + .08*rubble, 7 + rubble, materials["sandstone"], rubble_cluster, "road", rng, top_taper=.18))
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


def create_canyon_signature(
    band: str,
    index: int,
    record: dict[str, Any],
    root: bpy.types.Object,
    materials: dict[str, bpy.types.Material],
    rng: random.Random,
) -> str:
    side = -1.0 if index % 2 == 0 else 1.0
    count = record["count"]
    x_min, x_max = record["absXRange"]
    z_min, z_max = record["zRange"]
    y_min, y_max = record["yRange"]
    sequence = ((index * 7 + len(band) * 3) % count + .35) / count
    abs_x = x_min + (x_max - x_min) * (.12 + .78 * ((index * .61803398875 + len(band) * .11) % 1.0))
    center_z = z_max + (z_min - z_max) * sequence
    base_y = y_min + 1.2 + rng.uniform(-.3, .3)
    height = max(7.0, (y_max - base_y) * (.56 + .30 * ((index * .37) % 1.0)))
    length = 6.0 + (index % 5) * 1.55 + (2.0 if band == "far" else 0.0)
    depth = 3.6 + (index % 4) * .72 + (1.6 if band == "far" else .7 if band == "mid" else 0.0)
    segments = record["ridgeSegmentsPerSignature"]
    vertices: list[tuple[float, float, float]] = []
    for segment in range(segments + 1):
        t = segment / segments
        z = center_z + (t - .5) * length
        lateral = side * abs_x + math.sin(t * math.pi * (1.35 + .13 * index) + index) * depth * .18
        skyline = base_y + height * (.58 + .34 * math.sin(math.pi * t) + .08 * math.sin((segment + index) * 2.1))
        inner = lateral - side * depth * (.45 + .08 * math.sin(segment * 1.7))
        outer = lateral + side * depth * (.52 + .10 * math.cos(segment * 1.3))
        vertices.extend([(inner, base_y, z), (outer, base_y-.8, z), (outer-side*.22, skyline-.55, z), (inner+side*.12, skyline, z)])
    faces: list[tuple[int, ...]] = []
    for segment in range(segments):
        a = segment * 4; b = (segment + 1) * 4
        faces.extend([(a,b,b+3,a+3),(a+3,b+3,b+2,a+2),(a+2,b+2,b+1,a+1),(a+1,b+1,b,a)])
    faces.extend([(0,3,2,1),(segments*4,segments*4+1,segments*4+2,segments*4+3)])
    signature_data = {"band": band, "index": index, "recipe": record["recipe"], "segments": segments, "absX": round(abs_x, 6), "z": round(center_z, 6), "height": round(height, 6), "length": round(length, 6), "depth": round(depth, 6)}
    signature_hash = hashlib.sha256(canonical_bytes(signature_data)).hexdigest()
    ridge = mesh_object(f"Canyon.{band}.{index:02d}.LayeredRidge", vertices, faces, materials["basalt" if index % 3 else "basalt-strata"], root, "canyon", bevel=.08)
    ridge["depthBand"] = band; ridge["signatureHash"] = signature_hash; ridge["recipe"] = record["recipe"]
    ridge["tr4_abs_x"] = abs_x; ridge["tr4_center_z"] = center_z; ridge["tr4_contrast"] = record["contrast"]; ridge["tr4_saturation"] = record["saturation"]
    ridge["tr4_ridge_segments"] = segments; ridge["tr4_signature_index"] = index
    for terrace in range(record["terracesPerSignature"]):
        fraction = .24 + terrace * (.48 / max(1, record["terracesPerSignature"]-1))
        y = base_y + height * fraction
        z_shift = center_z + (terrace - 1) * length * .12
        inner = side * (abs_x - depth*.54); outer = side * (abs_x + depth*(.60-.08*terrace))
        verts = [(inner,y+.10,z_shift-length*.28),(outer,y,z_shift-length*.23),(outer+side*.18,y-.32,z_shift+length*.20),(inner,y-.20,z_shift+length*.29),(inner+side*.18,y-.72,z_shift-length*.18),(outer-side*.16,y-.78,z_shift+length*.13)]
        terrace_obj=mesh_object(f"Canyon.{band}.{index:02d}.Terrace.{terrace}", verts, [(0,1,2,3),(0,4,5,1),(3,2,5,4),(0,3,4),(1,5,2)], materials["basalt-strata"], root, "canyon", bevel=.045)
        terrace_obj["depthBand"] = band; terrace_obj["tr4_signature_index"] = index; terrace_obj["tr4_event_index"] = terrace
    for overhang in range(record["overhangsPerSignature"]):
        y = base_y + height * (.52 + .16*overhang)
        z_shift = center_z + (overhang-.5)*length*.18
        inner = side*(abs_x-depth*.38); outer = side*(abs_x+depth*(.72+.08*overhang))
        verts=[(inner,y,z_shift-length*.18),(outer,y-.08,z_shift-length*.12),(outer+side*.28,y-.35,z_shift+length*.16),(inner,y-.24,z_shift+length*.20),(inner+side*.12,y-.62,z_shift-length*.09),(outer-side*.12,y-.70,z_shift+length*.08)]
        overhang_obj=mesh_object(f"Canyon.{band}.{index:02d}.Overhang.{overhang}", verts, [(0,1,2,3),(0,4,5,1),(3,2,5,4),(0,3,4),(1,5,2)], materials["basalt"], root, "canyon", bevel=.055)
        overhang_obj["depthBand"] = band; overhang_obj["tr4_signature_index"] = index; overhang_obj["tr4_event_index"] = overhang
    for recess in range(record["recessesPerSignature"]):
        y = base_y + height*(.30+.22*recess)
        x = side*(abs_x-depth*.48)
        z = center_z+(recess-.5)*length*.24
        recess_vertices=[(x,y,z-length*.12),(x+side*.22,y+.08,z-length*.10),(x+side*.24,y+.70,z+length*.08),(x,y+.62,z+length*.11)]
        recess_obj=mesh_object(f"Canyon.{band}.{index:02d}.Recess.{recess}",recess_vertices,[(0,1,2,3)],materials["rock-armour"],root,"canyon",bevel=.02)
        recess_obj["depthBand"] = band; recess_obj["tr4_signature_index"] = index; recess_obj["tr4_event_index"] = recess
    return signature_hash


def create_canyon(root: bpy.types.Object, materials: dict[str, bpy.types.Material], rng: random.Random, construction: dict[str, Any]) -> dict[str, list[str]]:
    hashes: dict[str, list[str]] = {}
    for band in construction["bandOrder"]:
        record = construction[band]
        hashes[band] = [create_canyon_signature(band, index, record, root, materials, rng) for index in range(record["count"])]
        if len(set(hashes[band])) != record["count"]:
            raise RuntimeError(f"canyon signature uniqueness failed: {band}")
    return hashes


def create_shoulder(root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    vertices = [
        (3.18, -0.04, -5.20), (4.10, -0.07, -5.10), (4.42, -0.12, -4.60),
        (4.45, -0.10, -3.40), (4.16, -0.06, -2.86), (3.18, -0.03, -2.80),
        (3.25, -0.74, -5.16), (4.00, -0.92, -5.00), (4.22, -1.08, -4.48),
        (4.27, -1.02, -3.48), (4.00, -0.86, -2.90), (3.26, -0.72, -2.82),
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
    obj["radialSegments"] = 4 + 2 * int(curve.bevel_resolution)
    if semantic in ("runner", "pursuer"):
        obj["modelingMode"] = "profiled-articulated-mesh-v1" if semantic == "runner" else "separated-rock-plate-quadruped-v1"
    obj.data.materials.append(material)
    return obj


def create_tide_scar(construction: dict[str, Any], root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    surface_y = construction["tideScar"]["surfaceOffsetY"]
    points: list[tuple[float, float, float]] = []
    for index,(x, y, z) in enumerate(construction["tideScar"]["mainControlPoints"]):
        bend_t = max(0.0, min(1.0, (-z - 82.0) / 52.0))
        point=(x + 12.0 * bend_t * bend_t * (3.0 - 2.0 * bend_t), surface_y, z); points.append(point)
        source=make_empty(f"TideScar.MainSourcePoint.{index:02d}",root); source["tr4_source_role"]="main"; source["tr4_source_index"]=index; source.location=point
    clips = [(-17.75, -18.25), (-35.75, -36.25), (-53.75, -54.25), (-71.65, -76.35)]
    def sample(z: float) -> tuple[float, float, float]:
        exact=next((point for point in points if abs(point[2]-z)<1e-9),None)
        if exact is not None: return exact
        left,right=next((pair for pair in zip(points,points[1:]) if pair[0][2]>z>pair[1][2]))
        amount=(z-left[2])/(right[2]-left[2]); return (left[0]+(right[0]-left[0])*amount,surface_y,z)
    visible_ranges=[(points[0][2],clips[0][0])]+[(clips[index][1],clips[index+1][0]) for index in range(len(clips)-1)]+[(clips[-1][1],points[-1][2])]
    splines=[]
    for upper,lower in visible_ranges:
        segment=[sample(upper)]+[point for point in points if upper>point[2]>lower]+[sample(lower)]
        splines.append(segment)
    main_curve=add_curve("TideScar.Main.Editable", splines, 0.092, materials["tide-scar"], root, "tide-scar")
    main_curve["tr4_curve_role"] = "main"
    loop=[]
    for index,(x,_y,z) in enumerate(construction["tideScar"]["loopControlPoints"][:-1]):
        source=make_empty(f"TideScar.LoopSourcePoint.{index:02d}",root); source["tr4_source_role"]="near-loop"; source["tr4_source_index"]=index; source.location=(x,surface_y,z)
        loop.append((x,surface_y,z))
    loop_curve=add_curve("TideScar.NearLoop.Editable", [loop], 0.086, materials["tide-scar"], root, "tide-scar", cyclic=True)
    loop_curve["tr4_curve_role"] = "near-loop"


def mesh_bounds(obj: bpy.types.Object) -> tuple[list[float], list[float]]:
    if obj.type != "MESH" or not obj.data.vertices:
        raise RuntimeError(f"cannot derive mesh AABB: {obj.name}")
    points = [obj.matrix_local @ vertex.co for vertex in obj.data.vertices]
    return ([min(point[axis] for point in points) for axis in range(3)], [max(point[axis] for point in points) for axis in range(3)])


def mesh_world_bounds(obj: bpy.types.Object) -> tuple[list[float], list[float]]:
    if obj.type != "MESH" or not obj.data.vertices:
        raise RuntimeError(f"cannot derive world mesh AABB: {obj.name}")
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return ([min(point[axis] for point in points) for axis in range(3)], [max(point[axis] for point in points) for axis in range(3)])


def validate_runner_pose_geometry(pose: bpy.types.Object, part_order: list[str], socket_order: list[str], max_ground_error: float) -> dict[str, Any]:
    parts = {obj.get("tr4_part_name"): obj for obj in pose.children if obj.get("tr4_part_name")}
    sockets = {obj.get("tr4_socket_name"): obj for obj in pose.children if obj.get("tr4_socket_name")}
    if list(parts) != part_order or list(sockets) != socket_order:
        raise RuntimeError(f"runner pose part/socket order mismatch: {pose.get('poseKind')}")
    bounds = {name: mesh_bounds(obj) for name, obj in parts.items()}
    adjacent = {frozenset(pair) for pair in [
        ("pelvis","chest"),("pelvis","thigh.L"),("pelvis","thigh.R"),("pelvis","coatTail.L"),("pelvis","coatTail.R"),
        ("chest","head"),("chest","upperArm.L"),("chest","upperArm.R"),
        ("upperArm.L","forearm.L"),("forearm.L","hand.L"),("upperArm.R","forearm.R"),("forearm.R","hand.R"),
        ("thigh.L","shin.L"),("shin.L","foot.L"),("thigh.R","shin.R"),("shin.R","foot.R"),
    ]}
    for left_index, left_name in enumerate(part_order):
        for right_name in part_order[left_index+1:]:
            if frozenset((left_name,right_name)) in adjacent:
                continue
            low_a, high_a = bounds[left_name]; low_b, high_b = bounds[right_name]
            overlaps = [min(high_a[axis],high_b[axis])-max(low_a[axis],low_b[axis]) for axis in range(3)]
            if min(overlaps) > 1.0e-8:
                raise RuntimeError(f"runner non-adjacent AABB intersection: {pose.get('poseKind')}:{left_name}:{right_name}:{overlaps}")
    foot_errors = {side: abs(bounds[f"foot.{side}"][0][1]) for side in ("L","R")}
    if any(error > max_ground_error for error in foot_errors.values()):
        raise RuntimeError(f"runner foot grounding failed: {pose.get('poseKind')}:{foot_errors}")
    if any(abs(float(sockets[f"ground.foot.{side}"].location.y)) > max_ground_error for side in ("L","R")):
        raise RuntimeError(f"runner ground socket failed: {pose.get('poseKind')}")
    return {"poseKind": pose.get("poseKind"), "partOrder": list(parts), "socketOrder": list(sockets), "footGroundError": foot_errors, "nonAdjacentIntersectionCount": 0}


def create_runner_pose(name: str, pose_kind: str, parent: bpy.types.Object, materials: dict[str, bpy.types.Material], contract: dict[str, Any]) -> tuple[bpy.types.Object, dict[str, Any]]:
    pose = make_empty(name, parent)
    pose["poseKind"] = pose_kind
    semantic = "runner"
    if pose_kind.startswith("run."):
        phase = int(pose_kind.split(".")[1]) / 8.0
        stride = math.sin(math.tau * phase); counter = math.cos(math.tau * phase)
        pelvis = (0.0, 1.03 + .025*counter, 0.04)
        chest = (0.0, 1.58 + .018*counter, -0.12)
        head = (0.0, 2.05 + .012*counter, -0.25)
        hips = {"L": (-0.23, 0.96, 0.02), "R": (0.23, 0.96, 0.02)}
        knees = {"L": (-0.27, 0.55+.08*max(0,stride), -0.30*stride), "R": (0.27, 0.55+.08*max(0,-stride), 0.30*stride)}
        ankles = {"L": (-0.25, 0.17, -0.48*stride), "R": (0.25, 0.17, 0.48*stride)}
        feet = {"L": (-0.25, 0.087, -0.58*stride-.08), "R": (0.25, 0.087, 0.58*stride+.08)}
        shoulders = {"L": (-0.32, 1.78, -0.16), "R": (0.32, 1.78, -0.16)}
        elbows = {"L": (-0.47, 1.43, .36*stride+.30), "R": (0.47, 1.43, -.36*stride-.52)}
        hands = {"L": (-0.50, 1.12, .52*stride+.42), "R": (0.50, 1.12, -.52*stride-.64)}
    elif pose_kind == "jump":
        pelvis=(0,1.00,.02); chest=(0,1.53,-.20); head=(0,1.99,-.32); hips={"L":(-.23,.93,.02),"R":(.23,.93,.02)}; knees={"L":(-.30,.50,-.22),"R":(.30,.50,-.22)}; ankles={"L":(-.27,.17,-.50),"R":(.27,.17,-.50)}; feet={"L":(-.27,.087,-.64),"R":(.27,.087,-.64)}; shoulders={"L":(-.32,1.72,-.22),"R":(.32,1.72,-.22)}; elbows={"L":(-.50,1.83,-.52),"R":(.50,1.83,-.52)}; hands={"L":(-.53,2.04,-.70),"R":(.53,2.04,-.70)}
    elif pose_kind == "slide":
        pelvis=(0,.54,.02); chest=(0,.92,-.38); head=(0,1.22,-.62); hips={"L":(-.23,.50,.04),"R":(.23,.50,.04)}; knees={"L":(-.29,.28,-.42),"R":(.29,.28,.34)}; ankles={"L":(-.27,.15,-.82),"R":(.27,.15,.70)}; feet={"L":(-.27,.087,-.96),"R":(.27,.087,.84)}; shoulders={"L":(-.32,1.05,-.42),"R":(.32,1.05,-.42)}; elbows={"L":(-.50,.72,-.70),"R":(.50,.72,-.70)}; hands={"L":(-.52,.43,-.86),"R":(.52,.43,-.86)}
    elif pose_kind == "stumble":
        pelvis=(.10,.89,.08); chest=(.22,1.38,-.34); head=(.31,1.81,-.56); hips={"L":(-.14,.84,.06),"R":(.34,.82,.10)}; knees={"L":(-.34,.45,-.26),"R":(.48,.43,.31)}; ankles={"L":(-.40,.15,-.58),"R":(.56,.15,.58)}; feet={"L":(-.42,.087,-.72),"R":(.58,.087,.72)}; shoulders={"L":(-.10,1.56,-.36),"R":(.52,1.52,-.38)}; elbows={"L":(-.43,1.22,-.66),"R":(.80,1.18,-.10)}; hands={"L":(-.57,.91,-.82),"R":(.94,.88,.04)}
    elif pose_kind == "failure":
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
    else:
        raise RuntimeError(f"unknown runner pose: {pose_kind}")
    parts: dict[str, bpy.types.Object] = {}
    def part(part_name: str, obj: bpy.types.Object) -> None:
        obj["tr4_part_name"] = part_name; obj["modelingMode"] = "profiled-articulated-mesh-v1"; parts[part_name] = obj
    part("pelvis", add_uv_ellipsoid(f"pelvis.{pose_kind}", pelvis, (.31,.28,.24), materials["leather"], pose, semantic))
    part("chest", add_uv_ellipsoid(f"chest.{pose_kind}", chest, (.40,.48,.25), materials["cloth"], pose, semantic))
    part("head", add_uv_ellipsoid(f"head.{pose_kind}", head, (.22,.25,.22), materials["skin"], pose, semantic))
    # Leather shoulder mantle and mineral relay core make the torso readable at gameplay scale.
    add_uv_ellipsoid(f"Runner.Mantle.{pose_kind}", (chest[0],chest[1]+.12,chest[2]+.01), (.44,.15,.28), materials["leather"], pose, semantic)
    add_uv_ellipsoid(f"Runner.Core.{pose_kind}", (chest[0],chest[1]+.03,chest[2]-.235), (.105,.14,.055), materials["tide-scar"], pose, semantic, segments=16, rings=10)
    for side in ("L", "R"):
        part(f"upperArm.{side}",add_tapered_limb(f"upperArm.{side}.{pose_kind}",shoulders[side],elbows[side],.115,.095,materials["cloth"],pose,semantic)); part(f"forearm.{side}",add_tapered_limb(f"forearm.{side}.{pose_kind}",elbows[side],hands[side],.095,.072,materials["leather"],pose,semantic)); part(f"hand.{side}",add_uv_ellipsoid(f"hand.{side}.{pose_kind}",hands[side],(.09,.115,.085),materials["skin"],pose,semantic,segments=16,rings=8))
    for side in ("L", "R"):
        part(f"thigh.{side}",add_tapered_limb(f"thigh.{side}.{pose_kind}",hips[side],knees[side],.145,.118,materials["cloth"],pose,semantic)); part(f"shin.{side}",add_tapered_limb(f"shin.{side}.{pose_kind}",knees[side],ankles[side],.115,.085,materials["leather"],pose,semantic)); part(f"foot.{side}",add_uv_ellipsoid(f"foot.{side}.{pose_kind}",feet[side],(.135,.085,.235),materials["leather"],pose,semantic,segments=18,rings=8))
    tail_x = (-.52,.52) if pose_kind != "failure" else (-.12,.86)
    for side, x in zip(("L", "R"), tail_x):
        z=.62 if pose_kind!="failure" else .65; top_y=pelvis[1]+.22; bottom_y=max(.26,pelvis[1]-.55)
        vertices=[(x-.13,top_y,z),(x+.13,top_y,z),(x+.18,bottom_y,z+.27),(x-.10,bottom_y-.02,z+.31)]
        part(f"coatTail.{side}",mesh_object(f"coatTail.{side}.{pose_kind}",vertices,[(0,1,2,3)],materials["cloth"],pose,semantic,bevel=.018))
    for socket_name, location in (("ground.foot.L", (feet["L"][0], 0.0, feet["L"][2])), ("ground.foot.R", (feet["R"][0], 0.0, feet["R"][2])), ("camera.target", chest)):
        socket=make_empty(f"{socket_name}.{pose_kind}",pose); socket["tr4_socket_name"]=socket_name; socket.location=location
    if list(parts) != contract["partOrder"]:
        raise RuntimeError(f"runner part construction order mismatch: {pose_kind}")
    return pose, validate_runner_pose_geometry(pose,contract["partOrder"],contract["contactSocketOrder"],contract["maxGroundError"])


def create_pursuer(root: bpy.types.Object, materials: dict[str, bpy.types.Material]) -> None:
    root.location = (0.0, 0.0, 2.4)
    semantic = "pursuer"
    plates = [
        ("pelvisPlate", (0.0, .98, .88), (.82, .40, .32)),
        ("ribPlate", (0.0, 1.18, .00), (1.02, .46, .30)),
        ("shoulderPlate", (0.0, 1.24, -.84), (1.18, .42, .28)),
        ("neck", (0.0, 1.27, -1.12), (.42, .32, .24)),
        ("head", (0.0, 1.25, -1.40), (.55, .34, .30)),
        ("jaw", (0.0, 1.01, -1.62), (.43, .16, .25)),
    ]
    for index, (name, center, scale) in enumerate(plates):
        plate = add_uv_ellipsoid(name, center, scale, materials["rock-armour"], root, semantic, segments=20, rings=12)
        # The three body-core plates retain measurable open seams; smaller
        # cranial plates may rotate for silhouette variation.
        if index >= 3:
            plate.rotation_euler[1] = math.radians((index % 3 - 1) * 5.0)
        # Separate basalt-strata plate catches the rim light without becoming a blob.
        if index < 3:
            cap_scale = (scale[0] * .72, scale[1] * .18, scale[2] * .70)
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
    seam_points = [(0.0, 1.54, 0.90), (0.0, 1.62, 0.50), (0.0, 1.66, 0.00), (0.0, 1.61, -0.58), (0.0, 1.49, -1.12)]
    add_curve("dorsalSeam", [seam_points], 0.075, materials["coral-mineral"], root, semantic)
    for socket_name, location in (("ground.front.L", (-1.02, 0.0, -1.02)), ("ground.front.R", (1.02, 0.0, -1.02)), ("ground.rear.L", (-0.98, 0.0, 1.08)), ("ground.rear.R", (0.98, 0.0, 1.08)), ("capture.target", (0.0, 1.1, -1.6))):
        socket = make_empty(socket_name, root)
        socket["tr4_socket_name"] = socket_name
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
    jitter_y: float | None = None,
) -> bpy.types.Object:
    cx, cy, cz = center
    sx, sy, sz = (component * 0.5 for component in size)
    vertices = []
    y_jitter = jitter if jitter_y is None else jitter_y
    for x_sign, y_sign, z_sign in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)):
        vertices.append((cx + x_sign * sx + rng.uniform(-jitter, jitter), cy + y_sign * sy + rng.uniform(-y_jitter, y_jitter), cz + z_sign * sz + rng.uniform(-jitter, jitter)))
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    return mesh_object(name, vertices, faces, material, parent, semantic, bevel=min(size) * 0.12)


def create_hazards(
    roots: dict[str, bpy.types.Object],
    materials: dict[str, bpy.types.Material],
    rng: random.Random,
    construction: dict[str, Any],
) -> None:
    for kind in construction["order"]:
        record = construction[kind]
        root = roots[record["semanticRoot"]]
        root["tr4_hazard_kind"] = kind
        root["tr4_action"] = record["action"]
        root["tr4_visual_name"] = record["visualName"]
        root["tr4_collision_proxy"] = json.dumps(record["collisionProxy"], sort_keys=True, separators=(",", ":"))
        root["tr4_visual_bounds"] = json.dumps(record["visualBounds"], sort_keys=True, separators=(",", ":"))
        root["tr4_coplanar_faces_allowed"] = record["coPlanarFacesAllowed"]
    # Fault Lip: grounded fractured threshold, embedded .09 m and top exactly .76 m.
    for index in range(5):
        x = -2.32 + index * 1.16
        obj = irregular_box(
            f"Beam.FaultLip.{index}", (x, .335, -18.0 + rng.uniform(-.08, .08)),
            (1.144, .85, .56), materials["fresh-break"], roots["TR4_Hazard_Beam"], "beam", rng, jitter=0.0,
        )
        obj.rotation_euler[1] = math.radians((index - 2) * 1.8)
        if index in (0, 4):
            irregular_box(f"Beam.CoralCut.{index}", (x, 0.48, -17.71), (0.72, 0.16, 0.08), materials["coral-mineral"], roots["TR4_Hazard_Beam"], "beam", rng, jitter=0.02)
    for socket_name, location in (("entry", (0,0,-17.1)),("apex.clearance",(0,0.82,-18)),("exit",(0,0,-18.9)),("ground.L",(-2.8,0,-18)),("ground.R",(2.8,0,-18))):
        socket = make_empty(socket_name, roots["TR4_Hazard_Beam"]); socket["tr4_socket_name"] = socket_name; socket.location = location

    # Coral Throat: two .12 m embedded supports and a true .90 m negative-space opening.
    ring_root = roots["TR4_Hazard_Ring"]
    for side in (-1.0, 1.0):
        create_rock_spire(f"Ring.Support.{('L' if side < 0 else 'R')}", (side * .57, -.12, -36.0), .12, 1.17, 11, materials["sandstone"], ring_root, "ring", rng, top_taper=.70)
    irregular_box("Ring.CoralThroat.Lintel", (0.0, 1.29, -36.0), (1.44, .48, .50), materials["fresh-break"], ring_root, "ring", rng, jitter=0.0)
    for side in (-1.0, 1.0):
        irregular_box(f"Ring.MineralVent.{('L' if side < 0 else 'R')}", (side * 0.69, 0.82, -35.73), (0.13, 0.31, 0.10), materials["coral-mineral"], ring_root, "ring", rng, jitter=0.018)
    for socket_name, location in (("entry",(0,0,-35.2)),("slide.clearance",(0,0.90,-36)),("exit",(0,0,-36.8)),("ground.L",(-0.63,0,-36)),("ground.R",(0.63,0,-36))):
        socket = make_empty(socket_name, ring_root); socket["tr4_socket_name"] = socket_name; socket.location = location

    column_root = roots["TR4_Hazard_Column"]
    create_rock_spire("Column.BasaltSplitter", (0.0, -.12, -54.0), .54, 2.57, 13, materials["basalt"], column_root, "column", rng, top_taper=.18)
    irregular_box("Column.FractureFace", (0.18, 1.12, -53.55), (0.72, 1.10, 0.18), materials["fresh-break"], column_root, "column", rng, jitter=0.05)
    for index, x in enumerate((-0.55, -0.32, 0.43, 0.61)):
        create_rock_spire(f"Column.GroundedRubble.{index}", (x, 0.0, -53.68 + (index % 2) * 0.22), 0.12 + 0.03 * index, 0.28 + 0.08 * (index % 3), 7, materials["sandstone"], column_root, "column", rng, top_taper=0.15)
    for socket_name, location in (("entry",(0,0,-53.1)),("safe.left",(-2.35,0,-54)),("safe.right",(2.35,0,-54)),("exit",(0,0,-54.9)),("ground",(0,0,-54))):
        socket = make_empty(socket_name, column_root); socket["tr4_socket_name"] = socket_name; socket.location = location

    gap_root = roots["TR4_Gap_Lips"]
    for lip_index, z in enumerate((-72.0, -76.0)):
        direction = -1.0 if lip_index == 0 else 1.0
        for index in range(9):
            x = -2.95 + index * 0.74
            lip_height = 0.48 + 0.08 * (index % 3)
            irregular_box(
                f"Gap.Lip.{lip_index}.{index}", (x, lip_height * .5 - .12, z + direction * (0.12 + 0.06 * (index % 2))),
                (0.72, lip_height, 0.68),
                materials["coral-mineral" if index in (1, 6) else "fresh-break"], gap_root, "gap-lips", rng, jitter=0.055, jitter_y=0.0,
            )
    for socket_name, location in (("takeoff",(0,0,-71.5)),("apex.clearance",(0,0.52,-74)),("landing",(0,0,-76.5))):
        socket = make_empty(socket_name, gap_root); socket["tr4_socket_name"] = socket_name; socket.location = location


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


def depth_material(camera_position: tuple[float, float, float], near: float, ceiling: float, foreground_scale: float) -> bpy.types.Material:
    material = bpy.data.materials.get("TR4.Pass.LinearDepth") or bpy.data.materials.new("TR4.Pass.LinearDepth")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    distance = nodes.new("ShaderNodeVectorMath")
    distance.name = "DepthDistance"
    distance.operation = "DISTANCE"
    distance.inputs[1].default_value = camera_position
    subtract = nodes.new("ShaderNodeMath")
    subtract.name = "DepthSubtractNear"
    subtract.operation = "SUBTRACT"
    subtract.inputs[1].default_value = near
    divide = nodes.new("ShaderNodeMath")
    divide.name = "DepthDivideCeiling"
    divide.operation = "DIVIDE"
    divide.inputs[1].default_value = ceiling - near
    divide.use_clamp = True
    scale = nodes.new("ShaderNodeMath")
    scale.name = "DepthForegroundScale"
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = foreground_scale
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Position"], distance.inputs[0])
    links.new(distance.outputs["Value"], subtract.inputs[0])
    links.new(subtract.outputs["Value"], divide.inputs[0])
    links.new(divide.outputs["Value"], scale.inputs[0])
    links.new(scale.outputs["Value"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def configure_world(construction: dict[str, Any]) -> tuple[bpy.types.Node, bpy.types.Node, dict[str, Any]]:
    world = bpy.data.worlds.new("TR4.CanyonAtmosphere")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld"); output.name = "WorldOutput"
    background = nodes.new("ShaderNodeBackground"); background.name = "WorldSurface"
    lighting = construction["lighting"]
    background.inputs["Color"].default_value = (*linear_rgb(lighting["worldColor"]), 1.0)
    background.inputs["Strength"].default_value = lighting["worldStrength"]
    links.new(background.outputs["Background"], output.inputs["Surface"])
    if output.inputs["Volume"].is_linked:
        raise RuntimeError("C7 world volume must be disabled")
    set_view_transform("beauty")
    world_color = [float(value) for value in background.inputs["Color"].default_value[:3]]
    world_strength = float(background.inputs["Strength"].default_value)
    if max(abs(left - right) for left, right in zip(world_color, linear_rgb(lighting["worldColor"]))) > 1.0e-6 or abs(world_strength - lighting["worldStrength"]) > 1.0e-6:
        raise RuntimeError("atmosphere node readback mismatch")
    atmosphere = construction["atmosphere"]
    transmittance20 = math.exp(-atmosphere["density"] * 20.0)
    transmittance120 = math.exp(-atmosphere["density"] * 120.0)
    transmittance520 = math.exp(-atmosphere["density"] * 520.0)
    if not (transmittance20 >= 0.90 and 0.55 <= transmittance120 <= 0.72 and transmittance520 >= 0.12):
        raise RuntimeError("atmosphere transmittance gate failed")
    binding = json.loads(json.dumps(atmosphere))
    binding.update({"transmittance20": transmittance20, "transmittance120": transmittance120, "transmittance520": transmittance520, "verdict": "READY_FOR_DIAGNOSTIC_RENDER"})
    return background, output, binding


def configure_beauty_compositor(scene: bpy.types.Scene, atmosphere: dict[str, Any]) -> None:
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes; links = tree.links
    nodes.clear()
    created: dict[str, bpy.types.Node] = {}
    for name in atmosphere["nodeOrder"]:
        node = nodes.new(atmosphere["nodeTypeByName"][name]); node.name = name; node.label = name; created[name] = node
    created["NegDensity"].operation = "MULTIPLY"
    created["NegDensity"].inputs[1].default_value = -atmosphere["density"]
    created["ExpTransmittance"].operation = "EXPONENT"
    created["OneMinusTransmittance"].operation = "SUBTRACT"
    created["OneMinusTransmittance"].inputs[0].default_value = 1.0
    created["MixFog"].blend_type = "MIX"
    created["MixFog"].use_clamp = True
    created["FogColor"].outputs[0].default_value = (*linear_rgb(atmosphere["fogColor"]), 1.0)
    specs = [
        ("RenderLayers", "Depth", "NegDensity", 0), ("NegDensity", 0, "ExpTransmittance", 0),
        ("ExpTransmittance", 0, "OneMinusTransmittance", 1), ("OneMinusTransmittance", 0, "MixFog", 0),
        ("RenderLayers", "Image", "MixFog", 1), ("FogColor", "Image", "MixFog", 2),
        ("MixFog", "Image", "Composite", "Image"),
    ]
    for from_name, from_socket, to_name, to_socket in specs:
        links.new(created[from_name].outputs[from_socket], created[to_name].inputs[to_socket])
    actual_nodes = [node.name for node in nodes]
    if actual_nodes != atmosphere["nodeOrder"]:
        raise RuntimeError("beauty compositor node order mismatch")


def set_compositor_mode(scene: bpy.types.Scene, mode: str) -> None:
    scene.use_nodes = mode == "beauty"


def set_world_mode(
    mode: str,
    background: bpy.types.Node,
    output: bpy.types.Node,
    lighting: dict[str, Any],
    atmosphere: dict[str, Any],
) -> None:
    if output.inputs["Volume"].is_linked:
        raise RuntimeError("C7 world volume link appeared")
    if mode == "beauty":
        background.inputs["Color"].default_value = (*linear_rgb(lighting["worldColor"]), 1.0)
        background.inputs["Strength"].default_value = lighting["worldStrength"]
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
    scene.view_layers[0].use_pass_z = True
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
    depth_encoding: dict[str, Any],
) -> dict[str, Any] | None:
    if mode == "beauty":
        for obj in render_objects:
            original_name = obj.get("tr4_beauty_material")
            if not original_name or original_name not in beauty_materials:
                raise RuntimeError(f"missing beauty material binding: {obj.name}")
            obj.data.materials.clear()
            obj.data.materials.append(beauty_materials[original_name])
        return None
    if mode == "normal":
        material = pass_materials["normal"]
        for obj in render_objects:
            obj.data.materials.clear(); obj.data.materials.append(material)
        return None
    if mode == "linear-depth":
        material = depth_material(tuple(camera_record["position"]), camera_record["near"], depth_encoding["ceilingByProfile"][camera_record["profile"]], depth_encoding["foregroundScale"])
        for obj in render_objects:
            obj.data.materials.clear(); obj.data.materials.append(material)
        nodes=material.node_tree.nodes
        distance_node=nodes["DepthDistance"]; subtract_node=nodes["DepthSubtractNear"]; divide_node=nodes["DepthDivideCeiling"]; scale_node=nodes["DepthForegroundScale"]
        return {"profile":camera_record["profile"],"distanceOperation":distance_node.operation,"subtractOperation":subtract_node.operation,"divideOperation":divide_node.operation,"scaleOperation":scale_node.operation,"near":float(subtract_node.inputs[1].default_value),"ceiling":float(subtract_node.inputs[1].default_value+divide_node.inputs[1].default_value),"foregroundScale":float(scale_node.inputs[1].default_value)}
    for obj in render_objects:
        semantic = obj.get("tr4_semantic", "canyon")
        if mode == "object-id":
            material = pass_materials[semantic]
        elif mode == "road-mask":
            material = pass_materials["mask-white" if semantic in ("road", "gap-lips") else "mask-black"]
        else:
            raise RuntimeError(f"unknown material mode: {mode}")
        obj.data.materials.clear(); obj.data.materials.append(material)
    return None


def create_lights(construction: dict[str, Any]) -> dict[str, Any]:
    lighting = construction["lighting"]
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


def aabb_corners(bounds: tuple[list[float], list[float]]) -> list[list[float]]:
    low, high = bounds
    return [
        [low[0] if x == 0 else high[0], low[1] if y == 0 else high[1], low[2] if z == 0 else high[2]]
        for x in range(2) for y in range(2) for z in range(2)
    ]


def screen_aabb(record: dict[str, Any], bounds: tuple[list[float], list[float]]) -> tuple[list[float], list[float]]:
    projected = [project_anchor(record, point) for point in aabb_corners(bounds)]
    return (
        [min(point[axis] for point in projected) for axis in range(2)],
        [max(point[axis] for point in projected) for axis in range(2)],
    )


def canyon_relation_audit(root: bpy.types.Object, construction: dict[str, Any]) -> dict[str, int]:
    camera = frozen_camera_records()[0]
    band_bounds: dict[str, list[tuple[list[float], list[float]]]] = {}
    band_objects: dict[str, list[bpy.types.Object]] = {}
    open_intervals = 0
    for band in construction["bandOrder"]:
        authored = [
            obj for obj in root.children_recursive
            if obj.type == "MESH" and obj.name.startswith(f"Canyon.{band}.")
            and (".LayeredRidge" in obj.name or ".Terrace." in obj.name)
        ]
        if not authored:
            raise RuntimeError(f"canyon authored AABB set missing: {band}")
        bounds = [mesh_bounds(obj) for obj in authored]
        band_objects[band] = authored
        band_bounds[band] = bounds
        left = [item for item in bounds if item[1][0] < 0.0]
        right = [item for item in bounds if item[0][0] > 0.0]
        if not left or not right:
            raise RuntimeError(f"canyon bilateral AABB coverage missing: {band}")
        left_inner = max(item[1][0] for item in left)
        right_inner = min(item[0][0] for item in right)
        longitudinal_span = max(item[1][2] for item in bounds) - min(item[0][2] for item in bounds)
        if right_inner - left_inner <= 6.4 or longitudinal_span <= 1.0:
            raise RuntimeError(f"canyon central negative-space interval collapsed: {band}")
        open_intervals += 1
    occlusion_boundaries = 0
    pair_evidence: list[dict[str, Any]] = []
    for near_band, far_band in zip(construction["bandOrder"], construction["bandOrder"][1:]):
        witness: dict[str, Any] | None = None
        for near_obj in band_objects[near_band]:
            near_bounds = mesh_bounds(near_obj); near_screen = screen_aabb(camera, near_bounds)
            near_center_x = (near_bounds[0][0] + near_bounds[1][0]) * .5
            for far_obj in band_objects[far_band]:
                far_bounds = mesh_bounds(far_obj); far_screen = screen_aabb(camera, far_bounds)
                far_center_x = (far_bounds[0][0] + far_bounds[1][0]) * .5
                if near_center_x * far_center_x <= 0.0 or abs(far_center_x) <= abs(near_center_x) + 1.0:
                    continue
                near_center=[(near_bounds[0][axis]+near_bounds[1][axis])*.5 for axis in range(3)]; far_center=[(far_bounds[0][axis]+far_bounds[1][axis])*.5 for axis in range(3)]
                near_depth=math.sqrt(sum((near_center[axis]-camera["position"][axis])**2 for axis in range(3))); far_depth=math.sqrt(sum((far_center[axis]-camera["position"][axis])**2 for axis in range(3)))
                if far_depth <= near_depth + 1.0:
                    continue
                longitudinal_overlap = min(near_bounds[1][2], far_bounds[1][2]) - max(near_bounds[0][2], far_bounds[0][2])
                screen_overlap = [min(near_screen[1][axis], far_screen[1][axis]) - max(near_screen[0][axis], far_screen[0][axis]) for axis in range(2)]
                if longitudinal_overlap > 0.0 and min(screen_overlap) > 0.0:
                    witness = {"near": near_obj.name, "far": far_obj.name, "nearDepth":near_depth,"farDepth":far_depth,"longitudinalOverlap": longitudinal_overlap, "screenOverlap": screen_overlap}
                    break
            if witness is not None:
                break
        if witness is None:
            raise RuntimeError(f"canyon cross-band occlusion boundary missing: {near_band}/{far_band}")
        pair_evidence.append(witness)
        occlusion_boundaries += 1
    root["tr4_occlusion_pair_evidence"] = json.dumps(pair_evidence, sort_keys=True, separators=(",", ":"))
    return {"negativeSpaceCount": open_intervals, "occlusionBoundaryCount": occlusion_boundaries}


def exact_socket_order(root: bpy.types.Object, expected: list[str]) -> list[str]:
    sockets: dict[str, list[bpy.types.Object]] = {}
    for obj in root.children_recursive:
        canonical = obj.get("tr4_socket_name")
        if canonical is not None:
            sockets.setdefault(str(canonical), []).append(obj)
    if sorted(sockets) != sorted(expected):
        raise RuntimeError(f"semantic socket key-set mismatch: {root.name}:{sorted(sockets)}")
    actual: list[str] = []
    for socket in expected:
        matches = sockets.get(socket, [])
        if len(matches) != 1:
            raise RuntimeError(f"semantic socket cardinality mismatch: {root.name}:{socket}")
        actual.append(str(matches[0]["tr4_socket_name"]))
    return actual


def socket_by_canonical(root: bpy.types.Object, canonical: str) -> bpy.types.Object:
    matches = [obj for obj in root.children_recursive if obj.get("tr4_socket_name") == canonical]
    if len(matches) != 1:
        raise RuntimeError(f"semantic socket lookup mismatch: {root.name}:{canonical}")
    return matches[0]


def base_embed_gate(objects: list[bpy.types.Object], expected_range: list[float], label: str) -> None:
    if not objects:
        raise RuntimeError(f"hazard base mesh missing: {label}")
    embeds = [-mesh_bounds(obj)[0][1] for obj in objects]
    if any(value < expected_range[0] - 1.0e-6 or value > expected_range[1] + 1.0e-6 for value in embeds):
        raise RuntimeError(f"hazard actual base embed mismatch: {label}:{embeds}")


def exact_duplicate_face_count(objects: list[bpy.types.Object]) -> int:
    seen: set[tuple[tuple[float, float, float], ...]] = set()
    duplicates = 0
    for obj in objects:
        for polygon in obj.data.polygons:
            key = tuple(sorted(tuple(round(float(value), 6) for value in (obj.matrix_local @ obj.data.vertices[index].co)) for index in polygon.vertices))
            if key in seen:
                duplicates += 1
            seen.add(key)
    return duplicates


def hazard_geometry_audit(roots: dict[str, bpy.types.Object], construction: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actual: dict[str, dict[str, Any]] = {}
    actual_order = [str(root["tr4_hazard_kind"]) for root in roots.values() if root.get("tr4_hazard_kind") is not None]
    if actual_order != construction["order"]:
        raise RuntimeError(f"hazard four-root order readback mismatch: {actual_order}")
    for kind in construction["order"]:
        root = roots[construction[kind]["semanticRoot"]]
        actual[kind] = {
            "semanticRoot": root.name,
            "action": str(root["tr4_action"]),
            "collisionProxy": json.loads(root["tr4_collision_proxy"]),
            "visualBounds": json.loads(root["tr4_visual_bounds"]),
            "socketOrder": exact_socket_order(root, construction[kind]["socketOrder"]),
            "visualName": str(root["tr4_visual_name"]),
            "coPlanarFacesAllowed": bool(root["tr4_coplanar_faces_allowed"]),
        }

    beam_root = roots["TR4_Hazard_Beam"]
    beam_meshes = [obj for obj in beam_root.children_recursive if obj.type == "MESH" and obj.name.startswith("Beam.FaultLip.")]
    base_embed_gate(beam_meshes, construction["beam"]["baseEmbedRange"], "beam")
    beam_bounds = [mesh_bounds(obj) for obj in beam_meshes]
    beam_top = max(item[1][1] for item in beam_bounds)
    beam_width = max(item[1][0] for item in beam_bounds) - min(item[0][0] for item in beam_bounds)
    beam_socket = socket_by_canonical(beam_root, "apex.clearance")
    if not construction["beam"]["visualBounds"]["topYRange"][0] <= beam_top <= construction["beam"]["visualBounds"]["topYRange"][1]:
        raise RuntimeError("beam actual top bound mismatch")
    if max(item[1][0]-item[0][0] for item in beam_bounds)>construction["beam"]["visualBounds"]["widthLaneMax"]+1e-6 or abs(beam_socket.location.y - construction["beam"]["collisionProxy"]["height"]) > 1.0e-6 or max(abs(beam_socket.location.y - beam_top), abs(beam_width - construction["beam"]["collisionProxy"]["widthAll"])) > construction["beam"]["maxProxyDiscrepancy"] + 1.0e-6:
        raise RuntimeError("beam actual clearance/proxy discrepancy mismatch")

    ring_root = roots["TR4_Hazard_Ring"]
    ring_supports = [obj for obj in ring_root.children_recursive if obj.type == "MESH" and obj.name.startswith("Ring.Support.")]
    base_embed_gate(ring_supports, construction["ring"]["baseEmbedRange"], "ring")
    left_support = next(obj for obj in ring_supports if obj.name.endswith(".L"))
    right_support = next(obj for obj in ring_supports if obj.name.endswith(".R"))
    ring_opening_width = mesh_bounds(right_support)[0][0] - mesh_bounds(left_support)[1][0]
    lintel = next(obj for obj in ring_root.children_recursive if obj.name == "Ring.CoralThroat.Lintel")
    lintel_low = mesh_bounds(lintel)[0][1]
    slide_socket = socket_by_canonical(ring_root, "slide.clearance")
    ring_meshes=[obj for obj in ring_root.children_recursive if obj.type=="MESH"]
    ring_width=max(mesh_bounds(obj)[1][0] for obj in ring_meshes)-min(mesh_bounds(obj)[0][0] for obj in ring_meshes)
    if ring_width>construction["ring"]["visualBounds"]["widthLaneMax"]+1e-6 or abs(lintel_low - construction["ring"]["visualBounds"]["lowestSolidY"]) > 1.0e-6 or abs(slide_socket.location.y - construction["ring"]["visualBounds"]["openingHeight"]) > 1.0e-6 or abs(ring_opening_width - construction["ring"]["collisionProxy"]["laneWidth"]) > construction["ring"]["maxProxyDiscrepancy"] + 1.0e-6:
        raise RuntimeError("ring actual opening/clearance mismatch")

    column_root = roots["TR4_Hazard_Column"]
    splitter = next(obj for obj in column_root.children_recursive if obj.name == "Column.BasaltSplitter")
    base_embed_gate([splitter], construction["column"]["baseEmbedRange"], "column")
    splitter_bounds = mesh_bounds(splitter)
    splitter_width = splitter_bounds[1][0] - splitter_bounds[0][0]
    safe_left = socket_by_canonical(column_root, "safe.left")
    safe_right = socket_by_canonical(column_root, "safe.right")
    if splitter_width > construction["column"]["visualBounds"]["widthLaneMax"] + 1.0e-6 or safe_left.location.x >= splitter_bounds[0][0] or safe_right.location.x <= splitter_bounds[1][0] or min(abs(safe_left.location.x - splitter_bounds[0][0]), abs(safe_right.location.x - splitter_bounds[1][0])) < construction["column"]["collisionProxy"]["laneWidth"] * .5:
        raise RuntimeError("column actual safe-lane clearance mismatch")

    gap_root = roots["TR4_Gap_Lips"]
    near_lips = [obj for obj in gap_root.children_recursive if obj.type == "MESH" and obj.name.startswith("Gap.Lip.0.")]
    far_lips = [obj for obj in gap_root.children_recursive if obj.type == "MESH" and obj.name.startswith("Gap.Lip.1.")]
    all_lips = near_lips + far_lips
    base_embed_gate(all_lips, construction["gap"]["baseEmbedRange"], "gap")
    if min(mesh_bounds(obj)[1][2] - mesh_bounds(obj)[0][2] for obj in all_lips) < construction["gap"]["visualBounds"]["lipDepthMin"] - 1.0e-6:
        raise RuntimeError("gap actual lip depth mismatch")
    open_near_z = min(mesh_bounds(obj)[0][2] for obj in near_lips)
    open_far_z = max(mesh_bounds(obj)[1][2] for obj in far_lips)
    apex = socket_by_canonical(gap_root, "apex.clearance")
    hidden_floor_present=any(obj.type=="MESH" and obj.get("tr4_semantic")=="gap-floor" for obj in gap_root.children_recursive)
    if hidden_floor_present is not construction["gap"]["visualBounds"]["hiddenFloor"] or not open_far_z < apex.location.z < open_near_z or abs(apex.location.y - construction["gap"]["collisionProxy"]["clearanceHeight"]) > 1.0e-6:
        raise RuntimeError("gap actual open-span clearance mismatch")
    for kind in construction["order"]:
        root = roots[construction[kind]["semanticRoot"]]
        hazard_meshes = [obj for obj in root.children_recursive if obj.type == "MESH"]
        if not construction[kind]["coPlanarFacesAllowed"] and exact_duplicate_face_count(hazard_meshes) != 0:
            raise RuntimeError(f"hazard exact coplanar-face duplicate mismatch: {kind}")
        actual[kind]["baseEmbedRange"] = list(construction[kind]["baseEmbedRange"])
        actual[kind]["maxProxyDiscrepancy"] = construction[kind]["maxProxyDiscrepancy"]
    return actual


def pursuer_geometry_audit(root: bpy.types.Object, construction: dict[str, Any]) -> dict[str, Any]:
    child_names = [obj.name for obj in root.children_recursive]
    part_order: list[str] = []
    for part in construction["partOrder"]:
        matches = [name for name in child_names if name == part]
        if len(matches) != 1:
            raise RuntimeError(f"pursuer actual part cardinality mismatch: {part}")
        part_order.append(matches[0])
    sockets = exact_socket_order(root, construction["contactSocketOrder"])
    if any(abs(socket_by_canonical(root, socket).location.y) > construction["maxGroundError"] for socket in sockets[:4]):
        raise RuntimeError("pursuer actual ground-socket mismatch")
    core = [next(obj for obj in root.children_recursive if obj.name == name) for name in ("pelvisPlate", "ribPlate", "shoulderPlate")]
    pelvis_bounds, rib_bounds, shoulder_bounds = [mesh_bounds(obj) for obj in core]
    core_gaps = [pelvis_bounds[0][2] - rib_bounds[1][2], rib_bounds[0][2] - shoulder_bounds[1][2]]
    minimum_gap = min(core_gaps)
    if minimum_gap < construction["bodyCoreSeparationMin"] - 1.0e-6:
        raise RuntimeError(f"pursuer actual body-core separation mismatch: {core_gaps}")
    root["tr4_body_core_separation_actual"] = minimum_gap
    return {"partOrder": part_order, "contactSocketOrder": sockets, "bookendRoot": [float(value) for value in root.location]}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    return sum(max(0, len(polygon.vertices) - 2) for obj in objects if obj.type == "MESH" for polygon in obj.data.polygons)


def evaluated_geometry_readback(obj: bpy.types.Object, depsgraph: Any) -> dict[str, Any]:
    evaluated=obj.evaluated_get(depsgraph)
    temporary=evaluated.to_mesh(preserve_all_data_layers=False,depsgraph=depsgraph)
    if temporary is None:
        raise RuntimeError(f"evaluated geometry conversion failed: {obj.name}")
    try:
        vertices=[[float(value) for value in (evaluated.matrix_world @ vertex.co)] for vertex in temporary.vertices]
        if not vertices:
            raise RuntimeError(f"evaluated geometry is empty: {obj.name}")
        triangles=sum(max(0,len(polygon.vertices)-2) for polygon in temporary.polygons)
        return {"object":obj.name,"verticesWorld":vertices,"triangles":triangles}
    finally:
        evaluated.to_mesh_clear()


def road_geometry_record(root: bpy.types.Object, contract: dict[str, Any]) -> dict[str, Any]:
    children = list(root.children_recursive)
    caps = sorted((obj for obj in children if obj.name.startswith("Road.Cap.")), key=lambda obj: int(obj["tr4_module_index"]))
    if [int(obj["tr4_module_index"]) for obj in caps] != list(range(contract["moduleCount"])):
        raise RuntimeError("road actual module index sequence mismatch")
    cap_lengths = [abs(float(obj["tr4_start_z"]) - float(obj["tr4_end_z"])) for obj in caps]
    thicknesses = [float(obj["tr4_thickness"]) for obj in caps]
    if any(not contract["moduleLengthRange"][0] <= value <= contract["moduleLengthRange"][1] for value in cap_lengths):
        raise RuntimeError("road actual module-length threshold mismatch")
    if any(not contract["thicknessRange"][0] <= value <= contract["thicknessRange"][1] for value in thicknesses):
        raise RuntimeError("road authored thickness threshold mismatch")
    for index in range(contract["moduleCount"]):
        break_face = next(obj for obj in children if obj.name == f"Road.BreakFace.{index:02d}")
        actual_depth = -mesh_bounds(break_face)[0][1]
        if not contract["thicknessRange"][0] <= actual_depth <= contract["thicknessRange"][1]:
            raise RuntimeError(f"road break-face actual thickness mismatch: {index}:{actual_depth}")
    row_spans: list[float] = []
    surface_samples: list[float] = []
    vista_errors: list[float] = []
    for cap in caps:
        columns = int(cap["capCrosswiseSegments"]) + 1
        rows = int(cap["capLongitudinalSegments"]) + 1
        for row in range(rows):
            points = [cap.data.vertices[row * columns + column].co for column in range(columns)]
            low_x=min(float(point.x) for point in points); high_x=max(float(point.x) for point in points)
            row_spans.append(high_x-low_x)
            surface_samples.extend(float(points[column].y) for column in (4,5))
            z=sum(float(point.z) for point in points)/len(points)
            center=(low_x+high_x)*.5
            bend_t=max(0.0,min(1.0,(-z-contract["vistaBendStartZ"])/52.0))
            expected_center=contract["vistaBendMaxOffsetX"]*bend_t*bend_t*(3.0-2.0*bend_t)
            vista_errors.append(abs(center-expected_center))
    if max(abs(value-contract["surfaceY"]) for value in surface_samples)>1.0e-9 or min(row_spans)<6.10 or max(vista_errors)>.16:
        raise RuntimeError("road actual surface/width/vista gate mismatch")
    bounds=json.loads(root["tr4_collision_bounds"]); safety=json.loads(root["tr4_visual_safety_bounds"])
    if abs(bounds[1]-bounds[0]-contract["width"])>1.0e-9 or safety[0] <= bounds[0] or safety[1] >= bounds[1] or min(row_spans)*.5 < max(abs(safety[0]),abs(safety[1])):
        raise RuntimeError("road collision/visual safety semantic gate mismatch")
    signatures=[str(obj["signature"]) for obj in caps]; signature_order=[]
    for signature in signatures:
        if signature not in signature_order: signature_order.append(signature)
    runs=[]; current=None; count=0
    for signature in signatures:
        if signature==current: count+=1
        else:
            if current is not None: runs.append(count)
            current=signature; count=1
    runs.append(count)
    if signature_order != contract["signatureOrder"] or max(runs)>contract["maxConsecutiveSignatureRepeats"]:
        raise RuntimeError("road actual signature sequence mismatch")
    strata_counts=[]; rubble_counts=[]; fracture_counts=[]; undercut_counts=[]; apron_counts=[]; side_depths=[]
    for index in range(contract["moduleCount"]):
        strata_counts.append(len([obj for obj in children if obj.name.startswith(f"Road.Strata.{index:02d}.")]))
        clusters=[obj for obj in children if obj.name.startswith(f"Road.RubbleCluster.{index:02d}.")]
        if any(int(cluster["tr4_piece_count"])!=len([obj for obj in cluster.children if obj.name.startswith(f"Road.RubblePiece.{index:02d}.")]) for cluster in clusters):
            raise RuntimeError(f"road rubble cluster membership mismatch: {index}")
        rubble_counts.append(len(clusters))
        fracture_counts.append(len([obj for obj in children if obj.name.startswith(f"Road.Fracture.{index:02d}.")]))
        undercut_counts.append(len([obj for obj in children if obj.name.startswith(f"Road.Undercut.{index:02d}.")]))
        aprons=[obj for obj in children if obj.name.startswith(f"Road.Apron.{index:02d}.")]
        apron_counts.append(len(aprons)); side_depths.append(max(-mesh_bounds(obj)[0][1] for obj in aprons))
    if len(set(strata_counts))!=1 or strata_counts[0]!=contract["strataEventsPerModule"] or len(set(rubble_counts))!=1 or rubble_counts[0]!=contract["rubbleEventsPerModule"] or any(not contract["sideDepthRange"][0]<=value<=contract["sideDepthRange"][1] for value in side_depths):
        raise RuntimeError("road actual strata/rubble/side-depth mismatch")
    if any(value!=contract["fractureEventsPerModule"] for value in fracture_counts) or any(value!=contract["undercutEventsPerModule"] for value in undercut_counts) or any(value!=contract["sideApronsPerModule"] for value in apron_counts) or any(int(obj["capCrosswiseSegments"])!=contract["capCrosswiseSegments"] or int(obj["capLongitudinalSegments"])!=contract["capLongitudinalSegmentsPerModule"] for obj in caps):
        raise RuntimeError("road actual cap/fracture/undercut/apron cardinality mismatch")
    shoulder=next(obj for obj in children if obj.name=="Road.NearLoopShoulder"); shoulder_low,shoulder_high=mesh_bounds(shoulder)
    actual_shoulder={"rightOuterX":float(shoulder_high[0]),"zRange":[float(shoulder_low[2]),float(shoulder_high[2])]}
    return {
        "surfaceY":float(surface_samples[0]),"width":float(bounds[1]-bounds[0]),"bounds":bounds,"visualSafetyBounds":safety,
        "moduleCount":len(caps),"moduleLengthRange":list(contract["moduleLengthRange"]),"thicknessRange":list(contract["thicknessRange"]),"sideDepthRange":list(contract["sideDepthRange"]),
        "signatureOrder":signature_order,"maxConsecutiveSignatureRepeats":contract["maxConsecutiveSignatureRepeats"],"strataEventsPerModule":strata_counts[0],"rubbleEventsPerModule":rubble_counts[0],
        "nearLoopShoulder":actual_shoulder,"capCrosswiseSegments":min(int(obj["capCrosswiseSegments"]) for obj in caps),"capLongitudinalSegmentsPerModule":min(int(obj["capLongitudinalSegments"]) for obj in caps),
        "fractureEventsPerModule":min(fracture_counts),"undercutEventsPerModule":min(undercut_counts),"sideApronsPerModule":min(apron_counts),"vistaBendStartZ":contract["vistaBendStartZ"],"vistaBendMaxOffsetX":contract["vistaBendMaxOffsetX"],
    }


def canyon_geometry_record(root: bpy.types.Object, contract: dict[str, Any]) -> dict[str, Any]:
    relations=canyon_relation_audit(root,contract)
    ridges=[obj for obj in root.children_recursive if obj.name.endswith(".LayeredRidge")]
    band_order=[]
    for ridge in ridges:
        band=str(ridge["depthBand"])
        if band not in band_order: band_order.append(band)
    if band_order!=contract["bandOrder"]: raise RuntimeError("canyon actual band order mismatch")
    result: dict[str,Any]={"bandOrder":band_order}
    for band in band_order:
        band_ridges=[obj for obj in ridges if obj["depthBand"]==band]; record=contract[band]
        signature_hashes=[str(obj.get("signatureHash","")) for obj in band_ridges]
        if len(signature_hashes)!=record["count"] or len(set(signature_hashes))!=record["count"] or any(not value for value in signature_hashes): raise RuntimeError(f"canyon actual signature uniqueness mismatch: {band}")
        abs_x=[float(obj["tr4_abs_x"]) for obj in band_ridges]; centers_z=[float(obj["tr4_center_z"]) for obj in band_ridges]
        center_y=[sum(mesh_bounds(obj)[axis][1] for axis in (0,1))*.5 for obj in band_ridges]
        if any(not record["absXRange"][0]<=value<=record["absXRange"][1] for value in abs_x) or any(not record["zRange"][0]<=value<=record["zRange"][1] for value in centers_z) or any(not record["yRange"][0]<=value<=record["yRange"][1] for value in center_y):
            raise RuntimeError(f"canyon actual placement range mismatch: {band}")
        contrasts={float(obj["tr4_contrast"]) for obj in band_ridges}; saturations={float(obj["tr4_saturation"]) for obj in band_ridges}; recipes={str(obj["recipe"]) for obj in band_ridges}; segments={int(obj["tr4_ridge_segments"]) for obj in band_ridges}
        if len(contrasts)!=1 or len(saturations)!=1 or len(recipes)!=1 or len(segments)!=1: raise RuntimeError(f"canyon authored signature drift: {band}")
        event_counts={kind:[] for kind in ("Terrace","Overhang","Recess")}
        for ridge in band_ridges:
            index=int(ridge["tr4_signature_index"])
            for kind in event_counts: event_counts[kind].append(len([obj for obj in root.children_recursive if obj.name.startswith(f"Canyon.{band}.{index:02d}.{kind}.")]))
        if any(len(set(values))!=1 for values in event_counts.values()): raise RuntimeError(f"canyon per-signature event drift: {band}")
        result[band]={"absXRange":list(record["absXRange"]),"contrast":contrasts.pop(),"count":len(band_ridges),"saturation":saturations.pop(),"yRange":list(record["yRange"]),"zRange":list(record["zRange"]),"recipe":recipes.pop(),"ridgeSegmentsPerSignature":segments.pop(),"terracesPerSignature":event_counts["Terrace"][0],"overhangsPerSignature":event_counts["Overhang"][0],"recessesPerSignature":event_counts["Recess"][0]}
    result.update(relations); result["fullWidthWaterVisible"]=any(obj.type=="MESH" and obj.get("tr4_semantic")=="water" for obj in root.children_recursive)
    return result


def runner_geometry_record(root: bpy.types.Object, contract: dict[str, Any], pose_audits: list[dict[str, Any]]) -> dict[str, Any]:
    poses=[obj for obj in root.children if obj.get("poseKind") is not None]
    if [str(obj["poseKind"]) for obj in poses]!=contract["poseOrder"]: raise RuntimeError("runner actual pose-root order mismatch")
    pose_heights=[]; pose_triangles=[]; radial=[]; mesh_data=[]
    for pose in poses:
        pose_meshes=[obj for obj in pose.children_recursive if obj.type=="MESH"]
        bounds=[mesh_bounds(obj) for obj in pose_meshes]; pose_heights.append(max(item[1][1] for item in bounds)-min(item[0][1] for item in bounds)); pose_triangles.append(triangle_count(pose_meshes)); mesh_data.extend(obj.data.name for obj in pose_meshes)
        if any(obj.get("modelingMode")!=contract["modelingMode"] for obj in pose_meshes): raise RuntimeError(f"runner actual modeling mode mismatch: {pose.name}")
        radial.extend(int(obj["radialSegments"]) for obj in pose_meshes if obj.get("radialSegments") is not None)
    if max(pose_heights)>contract["height"]+1e-6 or max(pose_triangles)>contract["triangleCeiling"] or min(radial)<contract["minimumRadialSegments"] or len(mesh_data)!=len(set(mesh_data)):
        raise RuntimeError("runner actual height/triangle/profile/separation mismatch")
    return {"partOrder":pose_audits[0]["partOrder"],"contactSocketOrder":pose_audits[0]["socketOrder"],"poseOrder":[audit["poseKind"] for audit in pose_audits],"root":[float(value) for value in root.location],"height":contract["height"],"maxGroundError":contract["maxGroundError"],"triangleCeiling":contract["triangleCeiling"],"modelingMode":contract["modelingMode"],"minimumRadialSegments":contract["minimumRadialSegments"],"primitiveJoinForbidden":len(mesh_data)==len(set(mesh_data)),"nonAdjacentIntersectionTolerance":max(audit["nonAdjacentIntersectionCount"] for audit in pose_audits)}


def capture_separation_gate(runner_root: bpy.types.Object, pursuer_root: bpy.types.Object) -> None:
    bpy.context.view_layer.update()
    failure=next(obj for obj in runner_root.children if obj.get("poseKind")=="failure")
    runner_core=[obj for obj in failure.children_recursive if obj.get("tr4_part_name") in ("pelvis","chest","head")]
    pursuer_core=[obj for obj in pursuer_root.children_recursive if obj.name in ("pelvisPlate","ribPlate","shoulderPlate","head")]
    def union(objects: list[bpy.types.Object]) -> tuple[list[float],list[float]]:
        bounds=[mesh_world_bounds(obj) for obj in objects]; return ([min(item[0][axis] for item in bounds) for axis in range(3)],[max(item[1][axis] for item in bounds) for axis in range(3)])
    runner_bounds=union(runner_core); pursuer_bounds=union(pursuer_core); overlaps=[min(runner_bounds[1][axis],pursuer_bounds[1][axis])-max(runner_bounds[0][axis],pursuer_bounds[0][axis]) for axis in range(3)]
    if min(overlaps)>0.0: raise RuntimeError(f"closeup runner/pursuer body-core world AABB intersection: {overlaps}")
    pursuer_root["tr4_capture_world_aabb_evidence"]=json.dumps({"runner":runner_bounds,"pursuer":pursuer_bounds,"overlaps":overlaps},sort_keys=True,separators=(",",":"))


def pursuer_geometry_record(root: bpy.types.Object, runner_root: bpy.types.Object, contract: dict[str, Any]) -> dict[str, Any]:
    audit=pursuer_geometry_audit(root,contract)
    if max(abs(float(value)-contract["bookendRoot"][index]) for index,value in enumerate(root.location))>1e-6: raise RuntimeError("pursuer actual bookend root transform mismatch")
    capture_separation_gate(runner_root,root)
    parts=[next(obj for obj in root.children_recursive if obj.name==name) for name in contract["partOrder"]]
    renderables=[obj for obj in root.children_recursive if obj.type in ("MESH","CURVE") and not obj.hide_render]
    renderable_meshes=[obj for obj in renderables if obj.type=="MESH"]; renderable_curves=[obj for obj in renderables if obj.type=="CURVE"]
    if len(renderable_meshes)<=len([obj for obj in parts if obj.type=="MESH"]) or {obj.name for obj in renderable_curves}!={"dorsalSeam"}: raise RuntimeError("pursuer total renderable descendant coverage mismatch")
    radial=[int(obj["radialSegments"]) for obj in renderables if obj.get("radialSegments") is not None]
    if len(radial)!=len(renderables): raise RuntimeError("pursuer renderable radial-segment evidence missing")
    unique_data=len({int(obj.data.as_pointer()) for obj in renderables})==len(renderables)
    depsgraph=bpy.context.evaluated_depsgraph_get(); evaluated=[evaluated_geometry_readback(obj,depsgraph) for obj in renderables]
    evaluated_triangles=sum(record["triangles"] for record in evaluated); evaluated_vertices=[vertex for record in evaluated for vertex in record["verticesWorld"]]
    if any(obj.get("modelingMode")!=contract["modelingMode"] for obj in parts) or any(obj.get("modelingMode")!=contract["modelingMode"] for obj in renderables) or min(radial)<contract["minimumRadialSegments"] or evaluated_triangles>contract["triangleCeiling"] or not unique_data: raise RuntimeError("pursuer total evaluated renderable modeling/profile/triangle/uniqueness mismatch")
    actual_height=max(vertex[1] for vertex in evaluated_vertices)-min(vertex[1] for vertex in evaluated_vertices)
    if actual_height>contract["height"]+1e-6: raise RuntimeError(f"pursuer actual height mismatch: {actual_height}")
    audit.update({"height":contract["height"],"maxGroundError":contract["maxGroundError"],"triangleCeiling":contract["triangleCeiling"],"modelingMode":contract["modelingMode"],"minimumRadialSegments":contract["minimumRadialSegments"],"primitiveJoinForbidden":unique_data,"bodyCoreSeparationMin":contract["bodyCoreSeparationMin"]})
    return audit


def tide_scar_geometry_record(root: bpy.types.Object, contract: dict[str, Any]) -> dict[str, Any]:
    role_objects=[obj for obj in root.children_recursive if obj.type=="CURVE" and obj.get("tr4_curve_role") is not None]
    roles=[str(obj["tr4_curve_role"]) for obj in role_objects]
    if sorted(roles)!=["main","near-loop"] or len(role_objects)!=2: raise RuntimeError("Tide Scar actual curve-role cardinality mismatch")
    curves={str(obj["tr4_curve_role"]):obj for obj in role_objects}
    main=curves["main"]; loop=curves["near-loop"]
    main_points=[[float(value) for value in point.co[:3]] for spline in main.data.splines for point in spline.points]
    main_sources=sorted((obj for obj in root.children_recursive if obj.get("tr4_source_role")=="main"),key=lambda obj:int(obj["tr4_source_index"]))
    if [int(obj["tr4_source_index"]) for obj in main_sources]!=list(range(len(contract["mainControlPoints"]))): raise RuntimeError("Tide Scar main source-control cardinality mismatch")
    canonical=[]
    for source in main_sources:
        z=float(source.location.z); bend_t=max(0.0,min(1.0,(-z-82.0)/52.0)); x=float(source.location.x)-12.0*bend_t*bend_t*(3.0-2.0*bend_t); canonical.append([x,float(source.location.y),z])
    loop_local=[[float(value) for value in point.co[:3]] for point in loop.data.splines[0].points]
    bpy.context.view_layer.update(); identity=Matrix.Identity(4)
    for obj in (root,loop):
        if max(abs(float(obj.matrix_world[row][column]-identity[row][column])) for row in range(4) for column in range(4))>1e-9: raise RuntimeError(f"Tide Scar identity transform mismatch: {obj.name}")
    loop_points=[[float(value) for value in (loop.matrix_world @ Vector(point))] for point in loop_local]; loop_points.append(list(loop_points[0]))
    loop_sources=sorted((obj for obj in root.children_recursive if obj.get("tr4_source_role")=="near-loop"),key=lambda obj:int(obj["tr4_source_index"]))
    source_loop=[[float(value) for value in obj.matrix_world.translation] for obj in loop_sources]; source_loop.append(list(source_loop[0]))
    if len(loop_sources)+1!=len(contract["loopControlPoints"]) or max(abs(a-b) for left,right in zip(loop_points,source_loop) for a,b in zip(left,right))>1e-6: raise RuntimeError("Tide Scar loop world/source control mismatch")
    widths=[float(main.data.bevel_depth*2.0),float(loop.data.bevel_depth*2.0)]
    if any(not contract["mainWidthRange"][0]<=value<=contract["mainWidthRange"][1] for value in widths) or any(not contract["mainCenterXRange"][0]<=point[0]<=contract["mainCenterXRange"][1] for point in canonical) or any(abs(point[1]-contract["surfaceOffsetY"])>1e-6 for point in main_points+loop_points): raise RuntimeError("Tide Scar actual width/center/surface mismatch")
    endpoints=[float(spline.points[0].co.z) for spline in main.data.splines]+[float(spline.points[-1].co.z) for spline in main.data.splines]
    for center in (-18.0,-36.0,-54.0):
        targets=(center+contract["hazardClipPadding"],center-contract["hazardClipPadding"])
        if not all(any(abs(value-target)<1e-6 for value in endpoints) for target in targets): raise RuntimeError(f"Tide Scar actual two-sided hazard clip mismatch: {center}")
    if not all(any(abs(value-target)<1e-6 for value in endpoints) for target in (-72.0+contract["gapClipPadding"],-76.0-contract["gapClipPadding"])): raise RuntimeError("Tide Scar actual gap clip mismatch")
    if int(loop.get("radialSegments",0))<10 or int(loop["radialSegments"])!=4+2*int(loop.data.bevel_resolution): raise RuntimeError("Tide Scar near-loop actual cross-section resolution mismatch")
    depsgraph=bpy.context.evaluated_depsgraph_get(); evaluated_loop=evaluated_geometry_readback(loop,depsgraph); world_samples=evaluated_loop["verticesWorld"]
    camera=frozen_camera_records()[0]; projected=[project_anchor(camera,point) for point in world_samples]
    if not all(0.0<=point[0]<=1.0 and 0.0<=point[1]<=1.0 for point in projected) or min(point[0] for point in world_samples)<=expected_construction()["road"]["visualSafetyBounds"][1]: raise RuntimeError("Tide Scar evaluated near-loop tube portrait/safety visibility mismatch")
    beauty_name=str(main.get("tr4_beauty_material","")); material=bpy.data.materials.get(beauty_name)
    if beauty_name!="tide-scar" or material is None or material.node_tree is None: raise RuntimeError("Tide Scar beauty-material readback missing")
    principled=[node for node in material.node_tree.nodes if node.bl_idname=="ShaderNodeBsdfPrincipled"]
    if any(node.bl_idname=="ShaderNodeTexImage" for node in material.node_tree.nodes) or len(principled)!=1 or principled[0].inputs.get("Emission Strength") is None or abs(float(principled[0].inputs["Emission Strength"].default_value))>1e-9: raise RuntimeError("Tide Scar beauty material texture/emission gate failed")
    return {"mainWidthRange":list(contract["mainWidthRange"]),"mainCenterXRange":list(contract["mainCenterXRange"]),"surfaceOffsetY":float(main_points[0][1]),"mainControlPoints":canonical,"loopControlPoints":loop_points,"gapClipPadding":contract["gapClipPadding"],"hazardClipPadding":contract["hazardClipPadding"],"nearLoopVisibilityProfile":camera["profile"],"bakedTextureAllowed":False}


def scene_metrics(
    materials: dict[str, bpy.types.Material],
    roots: dict[str, bpy.types.Object],
    pose_audits: list[dict[str, Any]],
    depth_audits: list[dict[str, Any]],
) -> dict[str, Any]:
    # Reconstruct every declared binding against the generator-owned frozen
    # constants.  The preflight document is validated at the process boundary,
    # but is deliberately not used as the source of any scene binding claim.
    construction = expected_construction()
    frozen_cameras = frozen_camera_records()
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    triangles = sum(max(0, len(poly.vertices) - 2) for obj in meshes for poly in obj.data.polygons)
    root_records = []
    for name in ROOT_NAMES:
        root = roots[name]
        root_records.append({"name": name, "translation": list(root.location), "children": len(root.children_recursive)})
    pose_order=construction["runner"]["poseOrder"]
    if [audit["poseKind"] for audit in pose_audits] != pose_order or any(audit["partOrder"] != construction["runner"]["partOrder"] or audit["socketOrder"] != construction["runner"]["contactSocketOrder"] or audit["nonAdjacentIntersectionCount"] != 0 or max(audit["footGroundError"].values()) > construction["runner"]["maxGroundError"] for audit in pose_audits):
        raise RuntimeError("runner actual-pose geometry audit mismatch")
    hazard_audit = hazard_geometry_audit(roots, construction["hazards"])
    expected_geometry={name:construction[name] for name in ("road","canyon","runner","pursuer","hazards","tideScar")}
    actual_geometry={
        "road":road_geometry_record(roots["TR4_Road_Modules"],construction["road"]),
        "canyon":canyon_geometry_record(roots["TR4_Canyon_Modules"],construction["canyon"]),
        "runner":runner_geometry_record(roots["TR4_Runner_Rig"],construction["runner"],pose_audits),
        "pursuer":pursuer_geometry_record(roots["TR4_Pursuer_Cinematic"],roots["TR4_Runner_Rig"],construction["pursuer"]),
        "hazards":{"order":[str(root["tr4_hazard_kind"]) for root in roots.values() if root.get("tr4_hazard_kind") is not None]},
        "tideScar":tide_scar_geometry_record(roots["TR4_TideScar_Path"],construction["tideScar"]),
    }
    for kind in actual_geometry["hazards"]["order"]:
        actual_geometry["hazards"][kind]=hazard_audit[kind]
    geometry_binding={name:normalize_readback(actual_geometry[name],expected_geometry[name]) for name in expected_geometry}
    geometry_binding["verdict"] = "READY_FOR_DIAGNOSTIC_RENDER"
    graph_order=[]; graph_template=None; graph_parameters={}
    for name in construction["materialGraphs"]["graphOrder"]:
        material=materials[name]; record=json.loads(material["tr4_material_graph_readback"]); factory=json.loads(material["tr4_factory_default_audit"])
        if factory.get("verdict")!="FACTORY_DEFAULTS_MATCH" or factory.get("freshFactoryPerNodeType") is not True or factory.get("unlistedInputsCompared",0)<=0 or factory.get("unlistedPropertiesCompared",0)<=0:
            raise RuntimeError(f"material factory audit missing: {name}")
        graph_order.extend(record["graphOrder"])
        if graph_template is None: graph_template=record["template"]
        elif canonical_bytes(graph_template)!=canonical_bytes(record["template"]): raise RuntimeError(f"material graph template drift: {name}")
        graph_parameters.update(record["parameters"])
    actual_material_graph={"coordinateSource":"Generated","graphOrder":graph_order,"template":graph_template,"parameters":graph_parameters}
    material_binding=normalize_readback(actual_material_graph,construction["materialGraphs"]); material_binding["verdict"]="READY_FOR_DIAGNOSTIC_RENDER"
    if [audit["profile"] for audit in depth_audits] != PROFILE_ORDER or any(audit["distanceOperation"]!="DISTANCE" or audit["subtractOperation"]!="SUBTRACT" or audit["divideOperation"]!="DIVIDE" or audit["scaleOperation"]!="MULTIPLY" or audit["colorMode"]!="BW" or audit["colorDepth"]!=16 or any(abs(value-1.0)>1e-6 for value in audit["backgroundLinear"]) for audit in depth_audits):
        raise RuntimeError("actual depth graph/PNG audit mismatch")
    actual_depth={"distanceMetric":"euclidean-camera-distance-meters","nearSource":"cameras[].near","ceilingByProfile":{audit["profile"]:audit["ceiling"] for audit in depth_audits},"foregroundScale":depth_audits[0]["foregroundScale"],"backgroundValue":65535,"bitDepth":depth_audits[0]["colorDepth"],"colorType":0,"rounding":"floor(x+0.5)","foregroundQuantileSample":"known-object-id-nonbackground-and-depth-not-65535","semanticSampleSource":"exact-object-id-palette"}
    for audit,camera in zip(depth_audits,frozen_cameras):
        if abs(audit["near"]-camera["near"])>1e-6 or abs(audit["foregroundScale"]-depth_audits[0]["foregroundScale"])>1e-6: raise RuntimeError("depth near/scale readback mismatch")
    depth_binding=normalize_readback(actual_depth,construction["depthEncoding"]); depth_binding["verdict"]="READY_FOR_DIAGNOSTIC_RENDER"
    return {
        "meshObjects": len(meshes),
        "sourceTrianglesBeforeModifiers": triangles,
        "beautyMaterialCount": len(materials),
        "semanticRoots": root_records,
        "pursuerBookendRoot": list(roots["TR4_Pursuer_Cinematic"].location),
        "runnerRoot": list(roots["TR4_Runner_Rig"].location),
        "roadTopY": 0.0,
        "geometryBinding": geometry_binding,
        "materialGraphBinding": material_binding,
        "depthEncodingBinding": depth_binding,
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

    graph_contract = expected_construction()["materialGraphs"]
    graph_names = set(graph_contract["graphOrder"])
    materials = {
        record["name"]: (
            create_pbr_material(record, graph_contract["parameters"][record["name"]], graph_contract["template"])
            if record["name"] in graph_names else create_simple_pbr_material(record)
        )
        for record in preflight["materials"]
    }
    roots = {name: make_empty(name) for name in ROOT_NAMES}
    construction=expected_construction()
    roots["TR4_Road_Modules"]["tr4_collision_bounds"] = json.dumps(construction["road"]["bounds"], separators=(",", ":"))
    roots["TR4_Road_Modules"]["tr4_visual_safety_bounds"] = json.dumps(construction["road"]["visualSafetyBounds"], separators=(",", ":"))
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

    create_canyon(roots["TR4_Canyon_Modules"], materials, rng, construction["canyon"])
    create_tide_scar(construction, roots["TR4_TideScar_Path"], materials)
    pose_roots: dict[str, bpy.types.Object] = {}
    pose_audits: list[dict[str, Any]] = []
    runner_contract = construction["runner"]
    for pose_name in construction["runner"]["poseOrder"]:
        pose_root, pose_audit = create_runner_pose(f"Runner.Pose.{pose_name}", pose_name, roots["TR4_Runner_Rig"], materials, runner_contract)
        pose_roots[pose_name] = pose_root
        pose_audits.append(pose_audit)
    run_pose = pose_roots["run.2"]
    failure_pose = pose_roots["failure"]
    for pose_name, pose_root in pose_roots.items():
        set_hidden_recursive(pose_root, pose_root not in (run_pose,))
    create_pursuer(roots["TR4_Pursuer_Cinematic"], materials)
    create_hazards(roots, materials, rng, construction["hazards"])
    lighting_binding = create_lights(construction)
    background, world_output, atmosphere_binding = configure_world(construction)
    configure_beauty_compositor(scene, construction["atmosphere"])

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
        "schemaVersion": 3,
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
    depth_audits: list[dict[str, Any]] = []
    for profile in PROFILE_ORDER:
        camera_record = cameras[profile]
        replay_and_validate_camera(camera, camera_record, bindings[profile])
        is_bookend = profile == "closeup"
        set_hidden_recursive(run_pose, is_bookend)
        set_hidden_recursive(failure_pose, not is_bookend)
        set_hidden_recursive(roots["TR4_Pursuer_Cinematic"], not is_bookend)
        for pass_name in PASS_ORDER:
            record = outputs[(profile, pass_name)]
            depth_audit=set_pass_materials(pass_name, render_objects, beauty_materials, pass_materials, camera_record, construction["depthEncoding"])
            set_world_mode(pass_name, background, world_output, construction["lighting"], construction["atmosphere"])
            set_compositor_mode(scene, pass_name)
            set_view_transform(pass_name)
            set_render_samples(pass_name)
            scene.render.image_settings.color_mode = "BW" if pass_name in ("road-mask", "linear-depth") else "RGB"
            scene.render.image_settings.color_depth = "16" if pass_name == "linear-depth" else "8"
            if depth_audit is not None:
                depth_audit.update({"colorMode":scene.render.image_settings.color_mode,"colorDepth":int(scene.render.image_settings.color_depth),"backgroundLinear":[float(value) for value in background.inputs["Color"].default_value[:3]]})
                depth_audits.append(depth_audit)
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
    metrics = scene_metrics(materials, roots, pose_audits, depth_audits)
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
