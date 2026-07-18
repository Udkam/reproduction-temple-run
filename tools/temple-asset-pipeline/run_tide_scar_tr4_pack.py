"""Fail-closed TEMPLE-TR4 diagnostic runner.

This module intentionally has no bpy dependency.  It constructs the complete closed
schema in memory, verifies all provenance and containment facts, writes the normalized
preflight exactly once, launches one Blender process, verifies the exact render set,
and invokes the evaluator exactly once.  It never retries or exports a GLB.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import platform
import stat
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_ID = "tide-relay.temple-tr4.asset-preflight"
SCHEMA_VERSION = 6
CONTRACT_VERSION = "TEMPLE-TR4-C6"
SEED = 1414090053
REFERENCE_PATH = Path(
    r"C:\Users\ALEXCH~1\AppData\Local\Temp\codex-clipboard-ca70825b-99a6-4290-8307-4d90b2077d48.png"
)
REFERENCE_SHA256 = "8fc0c6a7f7fc8d7e5b65fd3d256dee33ccfeede0e4aba4a04657c66a93e33074"
REFERENCE_SIZE = (941, 1672)
BLENDER_EXECUTABLE = Path(
    r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
)
BLENDER_VERSION = "4.5.5 LTS"
BLENDER_EXECUTABLE_SHA256 = "597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c"
PYTHON_VERSION = "3.12.0"
CONSTRUCTION_SHA256 = "2ab30e4580a7bdf6b8eeddf8dcd2acc5d17fa3c101aecc9d530cbea535c79c10"
DIAGNOSTIC_RELATIVE = Path("docs/workstreams/temple-tr4-asset/diagnostic-006")
CAMERA_PROBE_RELATIVE = Path("docs/workstreams/temple-tr4-asset/camera-probe-001")
MATRIX_PROBE_RELATIVE = Path("docs/workstreams/temple-tr4-asset/matrix-probe-001")
AUTHORIZATION_RELATIVE = Path("docs/workstreams/temple-tr4-coordination/DIAGNOSTIC_006_AUTHORIZATION.md")
CURRENT_TASK_RELATIVE = Path("CURRENT_TASK.md")
COORDINATION_LOG_RELATIVE = Path("docs/workstreams/temple-tr4-coordination/THREAD_LOG.md")
DIAGNOSTIC_ID = "006"
CAMERA_BINDING_PROFILE_KEYS = [
    "profile", "lensShiftY", "originalShift0", "evaluatedShift0",
    "originalShift1", "evaluatedShift1", "matrix0", "matrix1", "difference",
    "b0", "b1", "response", "maxOffTargetCalibrationDelta", "dominanceRatio",
    "solvedShift", "evaluatedSolvedShift", "matrixSolved", "solvedDifference",
    "actual", "targetError", "maxOffTargetSolvedDelta", "webglMatrix",
    "maxProjectionError", "orientation", "screenProjection",
]
ORIENTATION_KEYS = [
    "position", "target", "up", "forward", "right", "trueUp", "vectorLengths",
    "pairwiseDots", "determinant", "canonicalViewMatrix", "actualViewMatrix",
    "maxViewMatrixError", "localForwardAngleRadians", "localUpAngleRadians",
]
SCREEN_PROJECTION_KEYS = [
    "runnerAnchor", "runnerHeadY", "runnerFootLY", "runnerFootRY", "beamY", "ringY",
    "columnY", "gapY", "scarX", "routeCenterX", "horizonY", "farRouteY", "verdict",
]
PROFILE_METRIC_KEYS = [
    "luminanceP50", "luminanceP95", "nearBlackFraction", "routeLuminanceP50",
    "roadMaskFraction", "normalUniqueColors", "depthUniqueValues", "depthMin", "depthMax",
    "runnerBounds", "runnerCentroidY", "runnerMargin", "runnerBeautyLuminanceP50",
    "pursuerBounds", "pursuerMargin", "pursuerWidthPixels", "pursuerBeautyLuminanceP50",
    "pursuerBeautyLuminanceP95", "roadBottomWidthFraction", "roadFarRouteWidthFraction",
    "roadWidthRatio", "semanticCentroidY", "roadNormalMedian", "representativeDepth",
]
EVALUATION_GATE_KEYS = [
    "exactPngSet", "pursuerAbsentOrdinary", "pursuerPresentCloseup",
    "hazardsPresentOrdinary", "orderedManifest", "cameraBinding", "globalLuminance",
    "routeLuminance", "nearBlack", "roadMaskBinaryArea", "semanticSubjects",
    "normalVariation", "depthVariation", "runnerBandContainment", "roadPerspective",
    "semanticScreenOrder", "scarRightOfRoute", "runnerRoiLuminance", "pursuerCloseup",
    "roadNormalUp", "representativeDepthOrder",
]
EXPECTED_SCENE_COUNTS = {
    "meshObjects": 400,
    "sourceTrianglesBeforeModifiers": 45224,
    "beautyMaterialCount": 10,
}
EXPECTED_ROOT_CHILDREN = [215, 90, 46, 27, 12, 10, 11, 21, 2]
FROZEN_C6_EVIDENCE = {
    "diagnostic001Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-001/preflight.json", "50d9c5bd2b59f6475e8ddd87ab6b404260fe3bb19f7132ff866d3e3d679fea12"),
    "diagnostic001Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-001/planned-manifest.json", "dc57b641ad824a84dcfb27299e7ebdb5fbe9a6e35a2d96bd099cde1877a830bf"),
    "diagnostic001BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-001/blender.log", "aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343"),
    "diagnostic001Status": ("docs/workstreams/temple-tr4-asset/diagnostic-001/diagnostic-status.json", "551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9"),
    "diagnostic002Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-002/preflight.json", "a43a26447924f4c6a6e07ebf7ad9de4273bb28eeb142393d9a14007eda63b294"),
    "diagnostic002Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-002/planned-manifest.json", "5325ca93cef20d3201c9e20a8bcfb45beebeec79a382b965fc208754373a8df1"),
    "diagnostic002BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-002/blender.log", "aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343"),
    "diagnostic002Status": ("docs/workstreams/temple-tr4-asset/diagnostic-002/diagnostic-status.json", "551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9"),
    "cameraProbe001Plan": ("docs/workstreams/temple-tr4-asset/camera-probe-001/probe-plan.json", "4cf25d218366661f01cab8ff6d3cd66809b9883b25a57b74548b9d99d65a5802"),
    "cameraProbe001BlenderLog": ("docs/workstreams/temple-tr4-asset/camera-probe-001/blender.log", "e32fb009d0c551faaaaa8d76f314aeadfb03fee696e226a6ca01b115435519cf"),
    "cameraProbe001Status": ("docs/workstreams/temple-tr4-asset/camera-probe-001/probe-status.json", "feaec46ada7ab64e579751d884d68b22a7a96f4467d59037feb373d59b8979dc"),
    "matrixProbe001Plan": ("docs/workstreams/temple-tr4-asset/matrix-probe-001/matrix-probe-plan.json", "85f11d7a986e8bc5f9ebfed6b240ec13285fa45bf54a12f9af166c0cd2c24ae8"),
    "matrixProbe001Response": ("docs/workstreams/temple-tr4-asset/matrix-probe-001/matrix-response.json", "40ee6316d267444a8f1874200e8782885fc47d2ad437d8eb2df5ef2eb7ed8f34"),
    "matrixProbe001BlenderLog": ("docs/workstreams/temple-tr4-asset/matrix-probe-001/blender.log", "505e414d7fa2eb6336d47ed6eeeff397a1e482042ee4ffc322550611e40f3dd5"),
    "matrixProbe001Status": ("docs/workstreams/temple-tr4-asset/matrix-probe-001/matrix-probe-status.json", "f6fa513d161f16d9be5cc1347696c15d0900de3cdc2a58f8be0383af92662d0e"),
    "diagnostic003Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-003/preflight.json", "4963f1aac82cea6a57d1c0872db980530c30cec38d1686ab4a49016484216008"),
    "diagnostic003Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-003/planned-manifest.json", "b89b2e91d4ab90d3ece2157c00a9c346593ac0a03486d8885a587d36ec6da676"),
    "diagnostic003CameraBinding": ("docs/workstreams/temple-tr4-asset/diagnostic-003/camera-binding.json", "c75c33086a343b1e473613c4fa7a69bc005d8610fa8163d1f1b9c94ec672c0e8"),
    "diagnostic003BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-003/blender.log", "9ec64ef0b9988ae156fcfa4ae94eec472891141891c9c9bdebe370f27ce1b31c"),
    "diagnostic003Status": ("docs/workstreams/temple-tr4-asset/diagnostic-003/diagnostic-status.json", "a9aea45e9842e437c1b459be56d27da6ae5bf7d514ed10939dc425843aab71ba"),
    "diagnostic004Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-004/preflight.json", "b497e349ca936cd83bc84fcfc5b2cd7d03bbf5ff92665b29902cd66d9bd4c6ae"),
    "diagnostic004Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-004/planned-manifest.json", "d94c51550da7157d64f6f2979d3d8f7c9fa5dbdc260c67b147cdbbc51dd5e524"),
    "diagnostic004CameraBinding": ("docs/workstreams/temple-tr4-asset/diagnostic-004/camera-binding.json", "c25715dfa1766be1299a9f8aa51ff236badb16bed7107b752a296e28fa1d5196"),
    "diagnostic004RenderOrder": ("docs/workstreams/temple-tr4-asset/diagnostic-004/render-order.json", "b0fe59a3a2576c9dd671cb2f32821854c75a466a55875b763c528a2898444810"),
    "diagnostic004SceneMetrics": ("docs/workstreams/temple-tr4-asset/diagnostic-004/scene-metrics.json", "7f89c5ea9d4457d285a75fbb4cb8aad4cd94dce3598e4773d6a0152e0707ebe6"),
    "diagnostic004BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-004/blender.log", "014611394e378b600c646b066641a250ec597a1ecc1fc25d20be8da471c89783"),
    "diagnostic004Status": ("docs/workstreams/temple-tr4-asset/diagnostic-004/diagnostic-status.json", "f10fea75788c3a1c434b6461c99be1cf01b5ba0e86bfa4bd1f9843a2b16883a6"),
    "diagnostic004PortraitBeauty": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-portrait-beauty.png", "1bfb7de64fc27042f03b952313a2b7b5af89fb306b394521f109c8f710001be3"),
    "diagnostic004PortraitObjectId": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-portrait-object-id.png", "835b7828fa6de0c8332d173e74301e55e98727ec707e21d6d8861ba81a3d5341"),
    "diagnostic004PortraitRoadMask": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-portrait-road-mask.png", "0b1c192346f9219dc717f1a28201c7a66a7ced6a95096ad7b2587506873a9e73"),
    "diagnostic004PortraitNormal": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-portrait-normal.png", "37eb27c447a7f3cd2c8d61bd88ad003dc94a3eb0edf51a0a914877b58da6fc03"),
    "diagnostic004PortraitDepth": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-portrait-linear-depth.png", "834ee04024806454850a55bac5d46193311f3a9ae1a3679d2354ff2929581876"),
    "diagnostic004DesktopBeauty": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-desktop-beauty.png", "0c863ea2e4ed258f0c5536fb6241a78ff729a3af7a201b9d2bedbc1daa89ffdd"),
    "diagnostic004DesktopObjectId": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-desktop-object-id.png", "2823a2bf1082934af1e54bf2e205277ee8a4d88fb7495b784e3c5ddbe99d4e27"),
    "diagnostic004DesktopRoadMask": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-desktop-road-mask.png", "5b234cdef30661af186514ae6279f23f1a90ea7b97ebbf043eca439a04bc3be9"),
    "diagnostic004DesktopNormal": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-desktop-normal.png", "9f270e33c893a9620bfbf0dd2e05867e1dbed414698f8289b5e1ee4259d10cb6"),
    "diagnostic004DesktopDepth": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-desktop-linear-depth.png", "29842153c9a0dd2492f554413d7dcf784e890ddcba5e636a712de7b8d9f3a504"),
    "diagnostic004LandscapeBeauty": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-landscape-beauty.png", "c2e85329435a559d5f00ba78216cf2203e3c76e813c4aa64478902b99f6a4aa3"),
    "diagnostic004LandscapeObjectId": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-landscape-object-id.png", "8fefcbe7f9f5180400487280fa188c25228ca9e06472844cccfc350070f06843"),
    "diagnostic004LandscapeRoadMask": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-landscape-road-mask.png", "820ee913f1e8b86237a28f5c27960c0ee3f8bd865718c06a784a1792dec93425"),
    "diagnostic004LandscapeNormal": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-landscape-normal.png", "3001e4f5bab4179e62f6b225a29e19c302ddabec7568515ff91de59612a72b03"),
    "diagnostic004LandscapeDepth": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-landscape-linear-depth.png", "26fde0d06dc75e91825aaff13aa4b324be4fbb1e17dc4c1a25f9b4ce61773b58"),
    "diagnostic004CloseupBeauty": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-closeup-beauty.png", "baf0402bdc4c1e383a9160650d9658c14823613170b264005d9ef2104843a6fe"),
    "diagnostic004CloseupObjectId": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-closeup-object-id.png", "7c6fe7a705a785b1f254048f6e3fec5d692587a9c9b04ba4d0934b09f6449504"),
    "diagnostic004CloseupRoadMask": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-closeup-road-mask.png", "b158134b6d635a42401aa0dd516e6d41c43e6c21180ed8b091401af3bac134fd"),
    "diagnostic004CloseupNormal": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-closeup-normal.png", "2bf07d60cf796331231aaaaf2dbae6dd1a15a3448ff95b0f0e9035527a95fc7b"),
    "diagnostic004CloseupDepth": ("docs/workstreams/temple-tr4-asset/diagnostic-004/tr4-diagnostic-004-closeup-linear-depth.png", "9c05e52d6efcd4be832b2fa6f8551c00bebfa77e4ca61c660e23f939d63c40a8"),
    "diagnostic005Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-005/preflight.json", "3f7997793ea9629cc17bdb4cfe186eed4d505273363105f90e9bec3778662659"),
    "diagnostic005Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-005/planned-manifest.json", "933890d49f728410b11c723be7c7ffbfe6f724d27018dabda85fc2ba45035437"),
    "diagnostic005BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-005/blender.log", "68f20d179729ff363aa142e76f55a530690ce156a6378552b981c0afa1abdd94"),
    "diagnostic005Status": ("docs/workstreams/temple-tr4-asset/diagnostic-005/diagnostic-status.json", "e31e89d92fc5a5ed0f3e93acda637ee15ab384141ba49f29bbe487f178431752"),
}
FROZEN_MATRIX_PROBE_EVIDENCE = {
    "diagnostic001Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-001/preflight.json", "50d9c5bd2b59f6475e8ddd87ab6b404260fe3bb19f7132ff866d3e3d679fea12"),
    "diagnostic001Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-001/planned-manifest.json", "dc57b641ad824a84dcfb27299e7ebdb5fbe9a6e35a2d96bd099cde1877a830bf"),
    "diagnostic001BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-001/blender.log", "aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343"),
    "diagnostic001Status": ("docs/workstreams/temple-tr4-asset/diagnostic-001/diagnostic-status.json", "551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9"),
    "diagnostic002Preflight": ("docs/workstreams/temple-tr4-asset/diagnostic-002/preflight.json", "a43a26447924f4c6a6e07ebf7ad9de4273bb28eeb142393d9a14007eda63b294"),
    "diagnostic002Plan": ("docs/workstreams/temple-tr4-asset/diagnostic-002/planned-manifest.json", "5325ca93cef20d3201c9e20a8bcfb45beebeec79a382b965fc208754373a8df1"),
    "diagnostic002BlenderLog": ("docs/workstreams/temple-tr4-asset/diagnostic-002/blender.log", "aefcd7fa6b80112f030583769f8865fdb2da2e254a77192bdde3c48d95561343"),
    "diagnostic002Status": ("docs/workstreams/temple-tr4-asset/diagnostic-002/diagnostic-status.json", "551768eaf9a764d906cf7be54b05203bdc7fa78c79f43e1a0528c392f7e097a9"),
    "cameraProbe001Plan": ("docs/workstreams/temple-tr4-asset/camera-probe-001/probe-plan.json", "4cf25d218366661f01cab8ff6d3cd66809b9883b25a57b74548b9d99d65a5802"),
    "cameraProbe001BlenderLog": ("docs/workstreams/temple-tr4-asset/camera-probe-001/blender.log", "e32fb009d0c551faaaaa8d76f314aeadfb03fee696e226a6ca01b115435519cf"),
    "cameraProbe001Status": ("docs/workstreams/temple-tr4-asset/camera-probe-001/probe-status.json", "feaec46ada7ab64e579751d884d68b22a7a96f4467d59037feb373d59b8979dc"),
    "evaluator": ("tools/temple-asset-pipeline/evaluate_tide_scar_tr4_pack.py", "656ace4f6b1c73e33352523fe36a55ad37f67df99aa4e52db608ee4b391af9a1"),
}


class PrecheckBlocked(RuntimeError):
    """Raised before the diagnostic directory exists."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_header(path: Path) -> tuple[int, int, int, int]:
    with path.open("rb") as handle:
        header = handle.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise PrecheckBlocked(f"not a PNG: {path}")
    length = struct.unpack(">I", header[8:12])[0]
    if length != 13 or header[12:16] != b"IHDR":
        raise PrecheckBlocked(f"invalid PNG IHDR: {path}")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
    return width, height, bit_depth, color_type


def vector_sub(a: list[float], b: list[float]) -> list[float]:
    return [a[index] - b[index] for index in range(3)]


def dot(a: list[float], b: list[float]) -> float:
    return sum(a[index] * b[index] for index in range(3))


def cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def normalize(value: list[float]) -> list[float]:
    magnitude = math.sqrt(dot(value, value))
    if not math.isfinite(magnitude) or magnitude <= 1.0e-12:
        raise PrecheckBlocked("camera basis is degenerate")
    return [component / magnitude for component in value]


def camera_basis(position: list[float], target: list[float], up: list[float]) -> dict[str, Any]:
    forward = normalize(vector_sub(target, position))
    world_up = normalize(up)
    right = normalize(cross(forward, world_up))
    true_up = normalize(cross(right, forward))
    negative_forward = [-component for component in forward]
    determinant = dot(right, cross(true_up, negative_forward))
    vector_lengths = [math.sqrt(dot(vector, vector)) for vector in (right, true_up, forward)]
    pairwise_dots = [dot(right, true_up), dot(right, forward), dot(true_up, forward)]
    if (
        any(abs(length - 1.0) > 5.0e-7 for length in vector_lengths)
        or any(abs(value) > 5.0e-7 for value in pairwise_dots)
        or abs(determinant - 1.0) > 5.0e-7
    ):
        raise PrecheckBlocked("camera basis gate failed")
    return {
        "forward": forward,
        "right": right,
        "trueUp": true_up,
        "vectorLengths": vector_lengths,
        "pairwiseDots": pairwise_dots,
        "determinant": determinant,
    }


def canonical_view_row_major(position: list[float], target: list[float], up: list[float]) -> list[float]:
    basis = camera_basis(position, target, up)
    right = basis["right"]
    true_up = basis["trueUp"]
    backward = [-component for component in basis["forward"]]
    return [
        right[0], right[1], right[2], -dot(right, position),
        true_up[0], true_up[1], true_up[2], -dot(true_up, position),
        backward[0], backward[1], backward[2], -dot(backward, position),
        0.0, 0.0, 0.0, 1.0,
    ]


def view_matrix(position: list[float], target: list[float], up: list[float]) -> list[float]:
    row_major = canonical_view_row_major(position, target, up)
    # WebGL column-major world-to-camera matrix.
    return [row_major[(index % 4) * 4 + index // 4] for index in range(16)]


def column_major_multiply_vector(matrix: list[float], vector: list[float]) -> list[float]:
    if len(matrix) != 16 or len(vector) != 4:
        raise PrecheckBlocked("projection operand shape mismatch")
    result = [sum(matrix[column * 4 + row] * vector[column] for column in range(4)) for row in range(4)]
    if any(not math.isfinite(value) for value in result):
        raise PrecheckBlocked("projection produced a non-finite vector")
    return result


def project_world(camera: dict[str, Any], point: list[float], *, direction: bool = False) -> tuple[float, float]:
    world = [*point, 0.0 if direction else 1.0]
    camera_space = column_major_multiply_vector(camera["viewMatrix"], world)
    clip = column_major_multiply_vector(camera["projectionMatrix"], camera_space)
    if abs(clip[3]) <= 1.0e-12:
        raise PrecheckBlocked("projection homogeneous divisor is degenerate")
    x = (clip[0] / clip[3] + 1.0) * 0.5
    y = (1.0 - clip[1] / clip[3]) * 0.5
    if not math.isfinite(x) or not math.isfinite(y):
        raise PrecheckBlocked("projection produced a non-finite coordinate")
    return x, y


def build_projection_anchors(profile: str) -> dict[str, list[float]]:
    ordinary = {
        "runnerAnchor": [0.0, 1.20, 0.0],
        "runnerHead": [0.0, 2.05, -0.25],
        "runnerFootL": [-0.25, 0.085, -0.56],
        "runnerFootR": [0.25, 0.08, 0.22],
    }
    failure = {
        "runnerAnchor": [0.46, 1.08, -0.34],
        "runnerHead": [0.57, 1.46, -0.62],
        "runnerFootL": [-0.48, 0.075, -0.72],
        "runnerFootR": [1.02, 0.075, 0.48],
    }
    return {
        **(failure if profile == "closeup" else ordinary),
        "beam": [0.0, 0.72, -18.0],
        "ring": [0.0, 1.05, -36.0],
        "column": [0.0, 1.12, -54.0],
        "gap": [0.0, 0.0, -74.0],
        "scar": [3.03, 0.035, 0.0],
        "routeCenter": [0.0, 0.035, 0.0],
        "farRoute": [0.0, 0.0, -120.0],
    }


def expected_screen_projection(camera: dict[str, Any]) -> dict[str, Any]:
    anchors = camera["projectionAnchors"]
    points = {name: project_world(camera, point) for name, point in anchors.items()}
    horizon_y = project_world(camera, [0.0, 0.0, -1.0], direction=True)[1]
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
        "horizonY": horizon_y,
        "farRouteY": points["farRoute"][1],
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }
    coordinates = [*result["runnerAnchor"], *[result[key] for key in SCREEN_PROJECTION_KEYS[1:-1]]]
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in coordinates):
        raise PrecheckBlocked(f"screen projection is outside the normalized frame: {camera['profile']}")
    if not result["runnerHeadY"] < min(result["runnerFootLY"], result["runnerFootRY"]):
        raise PrecheckBlocked(f"runner head/feet projection order failed: {camera['profile']}")
    if not result["scarX"] > result["routeCenterX"]:
        raise PrecheckBlocked(f"Tide Scar projection side failed: {camera['profile']}")
    if camera["profile"] != "closeup":
        low, high = (0.61, 0.72) if camera["profile"] == "portrait" else (0.62, 0.76)
        if not low <= result["runnerAnchor"][1] <= high:
            raise PrecheckBlocked(f"runner analytic band failed: {camera['profile']}")
        if not result["runnerAnchor"][1] > result["beamY"] > result["ringY"] > result["columnY"] > result["gapY"]:
            raise PrecheckBlocked(f"semantic analytic screen order failed: {camera['profile']}")
        if not 0.17 <= result["horizonY"] <= 0.31:
            raise PrecheckBlocked(f"analytic horizon band failed: {camera['profile']}")
        far_x, far_y = points["farRoute"]
        if not 0.0 <= far_x <= 1.0 or not 0.0 <= far_y <= 1.0:
            raise PrecheckBlocked(f"far-route projection failed: {camera['profile']}")
    return result


def projection_matrix(
    fov_degrees: float,
    aspect: float,
    near: float,
    far: float,
    lens_shift_y: float,
) -> list[float]:
    reciprocal_tan = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)
    result = [0.0] * 16
    result[0] = reciprocal_tan / aspect
    result[5] = reciprocal_tan
    result[9] = lens_shift_y
    result[10] = -(far + near) / (far - near)
    result[11] = -1.0
    result[14] = -(2.0 * far * near) / (far - near)
    return result


def build_cameras() -> list[dict[str, Any]]:
    source = [
        ("portrait", [540, 960], [270, 480], [0.0, 6.20, 15.20], [0.0, 0.55, -16.80], 40.0, 0.08, 520.0, -0.055),
        ("desktop", [960, 540], [480, 270], [0.0, 6.06, 13.60], [0.0, 0.60, -13.30], 43.0, 0.08, 520.0, -0.025),
        ("landscape", [844, 390], [422, 195], [0.0, 6.15, 12.80], [0.0, 0.55, -12.56], 46.0, 0.08, 520.0, -0.020),
        ("closeup", [640, 480], [320, 240], [0.0, 5.40, 9.80], [0.0, 1.15, -3.40], 48.0, 0.05, 180.0, 0.0),
    ]
    cameras: list[dict[str, Any]] = []
    for profile, resolution, diagnostic, position, target, fov, near, far, shift in source:
        aspect = resolution[0] / resolution[1]
        up = [0.0, 1.0, 0.0]
        cameras.append(
            {
                "profile": profile,
                "resolution": resolution,
                "diagnosticResolution": diagnostic,
                "position": position,
                "target": target,
                "up": up,
                "verticalFovDegrees": fov,
                "aspect": aspect,
                "near": near,
                "far": far,
                "lensShiftY": shift,
                "viewMatrix": view_matrix(position, target, up),
                "projectionMatrix": projection_matrix(fov, aspect, near, far, shift),
                "projectionAnchors": build_projection_anchors(profile),
            }
        )
        expected_screen_projection(cameras[-1])
    return cameras


def build_construction() -> dict[str, Any]:
    return {
        "axis": {"forward": "-Z", "right": "+X", "up": "+Y"},
        "canyon": {
            "bandOrder": ["near", "mid", "far"],
            "near": {"absXRange": [8.0, 16.0], "contrast": 0.86, "count": 8, "saturation": 0.72, "yRange": [-8.0, 10.0], "zRange": [-100.0, -10.0]},
            "mid": {"absXRange": [18.0, 34.0], "contrast": 0.58, "count": 10, "saturation": 0.48, "yRange": [-12.0, 18.0], "zRange": [-140.0, -20.0]},
            "far": {"absXRange": [38.0, 70.0], "contrast": 0.30, "count": 12, "saturation": 0.24, "yRange": [-16.0, 30.0], "zRange": [-180.0, -35.0]},
            "negativeSpaceCount": 3,
            "occlusionBoundaryCount": 2,
            "fullWidthWaterVisible": False,
        },
        "hazards": {
            "order": ["beam", "ring", "column", "gap"],
            "beam": {
                "semanticRoot": "TR4_Hazard_Beam",
                "action": "jump",
                "collisionProxy": {"height": 0.82, "widthAll": 5.84, "widthLane": 0.84},
                "visualBounds": {"topYRange": [0.68, 0.76], "widthLaneMax": 1.55},
                "socketOrder": ["entry", "apex.clearance", "exit", "ground.L", "ground.R"],
            },
            "ring": {
                "semanticRoot": "TR4_Hazard_Ring",
                "action": "slide",
                "collisionProxy": {"laneWidth": 0.84, "requiresSlide": True},
                "visualBounds": {"lowestSolidY": 1.05, "openingHeight": 0.90, "widthLaneMax": 1.55},
                "socketOrder": ["entry", "slide.clearance", "exit", "ground.L", "ground.R"],
            },
            "column": {
                "semanticRoot": "TR4_Hazard_Column",
                "action": "lane-change",
                "collisionProxy": {"laneWidth": 0.84},
                "visualBounds": {"widthLaneMax": 1.55},
                "socketOrder": ["entry", "safe.left", "safe.right", "exit", "ground"],
            },
            "gap": {
                "semanticRoot": "TR4_Gap_Lips",
                "action": "jump",
                "collisionProxy": {"clearanceHeight": 0.52, "lengthFromCanonicalEvent": True},
                "visualBounds": {"hiddenFloor": False, "lipDepthMin": 0.55},
                "socketOrder": ["takeoff", "apex.clearance", "landing"],
            },
        },
        "lighting": {
            "worldColor": "#6E8294",
            "worldStrength": 0.55,
            "fogColor": "#9AA7A8",
            "fogDensity": 0.0035,
            "fogAnisotropy": 0.18,
            "key": {"color": "#FFD7A3", "energy": 4.2, "surfaceToLight": [-0.51966, 0.77949, 0.34977], "shadow": True},
            "fill": {"color": "#7EA6C4", "energy": 1.1, "surfaceToLight": [0.48019, 0.62025, -0.62025], "shadow": False},
            "contact": {
                "color": "#E7C79C", "energy": 430.0, "shape": "DISK", "size": 9.0,
                "shadow": False, "location": [0.0, 7.5, 4.0], "target": [0.0, 0.0, -4.0],
            },
        },
        "pursuer": {
            "partOrder": ["pelvisPlate", "ribPlate", "shoulderPlate", "neck", "head", "jaw", "foreleg.L.upper", "foreleg.L.lower", "paw.L.front", "foreleg.R.upper", "foreleg.R.lower", "paw.R.front", "hindleg.L.upper", "hindleg.L.lower", "paw.L.rear", "hindleg.R.upper", "hindleg.R.lower", "paw.R.rear", "dorsalSeam"],
            "contactSocketOrder": ["ground.front.L", "ground.front.R", "ground.rear.L", "ground.rear.R", "capture.target"],
            "bookendRoot": [0.0, 0.0, 2.4],
            "height": 1.78,
            "maxGroundError": 0.03,
            "triangleCeiling": 24000,
        },
        "road": {
            "surfaceY": 0.0,
            "width": 6.4,
            "bounds": [-3.2, 3.2],
            "visualSafetyBounds": [-2.92, 2.92],
            "moduleCount": 16,
            "moduleLengthRange": [6.0, 11.0],
            "thicknessRange": [0.55, 1.2],
            "sideDepthRange": [2.5, 8.0],
            "signatureOrder": ["terrace-fracture", "buttress-recess", "collapsed-lip", "strata-undercut", "rubble-shoulder", "split-ledge"],
            "maxConsecutiveSignatureRepeats": 2,
            "strataEventsPerModule": 2,
            "rubbleEventsPerModule": 1,
            "nearLoopShoulder": {"rightOuterX": 4.45, "zRange": [2.8, 5.2]},
        },
        "runner": {
            "partOrder": ["pelvis", "chest", "head", "upperArm.L", "forearm.L", "hand.L", "upperArm.R", "forearm.R", "hand.R", "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R", "coatTail.L", "coatTail.R"],
            "contactSocketOrder": ["ground.foot.L", "ground.foot.R", "camera.target"],
            "poseOrder": ["run.0", "run.1", "run.2", "run.3", "run.4", "run.5", "run.6", "run.7", "jump", "slide", "stumble", "failure"],
            "root": [0.0, 0.0, 0.0],
            "height": 2.32,
            "maxGroundError": 0.03,
            "triangleCeiling": 18000,
        },
        "tideScar": {
            "mainWidthRange": [0.075, 0.11],
            "mainCenterXRange": [3.0, 3.06],
            "surfaceOffsetY": 0.035,
            "mainControlPoints": [[3.03, 0.035, 8.0], [3.05, 0.035, 0.0], [3.01, 0.035, -10.0], [3.06, 0.035, -22.0], [3.02, 0.035, -36.0], [3.04, 0.035, -52.0], [3.00, 0.035, -70.0], [3.05, 0.035, -92.0], [3.02, 0.035, -120.0]],
            "loopControlPoints": [[3.00, 0.035, 4.00], [3.09, 0.035, 4.33], [3.33, 0.035, 4.56], [3.65, 0.035, 4.65], [3.98, 0.035, 4.56], [4.22, 0.035, 4.33], [4.30, 0.035, 4.00], [4.22, 0.035, 3.68], [3.98, 0.035, 3.44], [3.65, 0.035, 3.35], [3.33, 0.035, 3.44], [3.09, 0.035, 3.68], [3.00, 0.035, 4.00]],
            "gapClipPadding": 0.35,
            "hazardClipPadding": 0.25,
        },
        "unitMeters": 1.0,
    }


def build_materials() -> list[dict[str, Any]]:
    values = [
        ("sandstone", "#D8B98C", 0.82, 0.01, 0.42),
        ("fresh-break", "#8F7659", 0.90, 0.00, 0.58),
        ("basalt", "#1B2935", 0.78, 0.02, 0.48),
        ("basalt-strata", "#334653", 0.86, 0.01, 0.62),
        ("tide-scar", "#F2EAD7", 0.90, 0.00, 0.12),
        ("coral-mineral", "#B44A38", 0.74, 0.03, 0.36),
        ("skin", "#8A5B45", 0.70, 0.00, 0.18),
        ("cloth", "#203746", 0.88, 0.00, 0.24),
        ("leather", "#2A3338", 0.76, 0.02, 0.32),
        ("rock-armour", "#111A20", 0.72, 0.04, 0.54),
    ]
    return [
        {"name": name, "baseColor": color, "roughness": roughness, "metallic": metallic, "normalStrength": normal}
        for name, color, roughness, metallic, normal in values
    ]


def build_roots() -> list[dict[str, Any]]:
    names = [
        "TR4_Road_Modules", "TR4_Canyon_Modules", "TR4_Runner_Rig",
        "TR4_Pursuer_Cinematic", "TR4_Hazard_Beam", "TR4_Hazard_Ring",
        "TR4_Hazard_Column", "TR4_Gap_Lips", "TR4_TideScar_Path",
    ]
    return [
        {"name": name, "parent": None, "translation": [0, 0, 0], "rotation": [0, 0, 0, 1], "scale": [1, 1, 1]}
        for name in names
    ]


def build_outputs() -> list[dict[str, Any]]:
    profiles = [
        ("portrait", "tr4-diagnostic-running-001", 270, 480),
        ("desktop", "tr4-diagnostic-running-001", 480, 270),
        ("landscape", "tr4-diagnostic-running-001", 422, 195),
        ("closeup", "tr4-diagnostic-game-over-001", 320, 240),
    ]
    passes = ["beauty", "object-id", "road-mask", "normal", "linear-depth"]
    outputs: list[dict[str, Any]] = []
    for profile, scene_id, width, height in profiles:
        for pass_name in passes:
            index = len(outputs)
            outputs.append(
                {
                    "index": index,
                    "profile": profile,
                    "pass": pass_name,
                    "sceneId": scene_id,
                    "relativePath": f"tr4-diagnostic-006-{profile}-{pass_name}.png",
                    "width": width,
                    "height": height,
                }
            )
    return outputs


def build_preflight(repo_root: Path, script_hashes: dict[str, str]) -> dict[str, Any]:
    scripts_dir = repo_root / "tools" / "temple-asset-pipeline"
    construction = build_construction()
    return {
        "schemaId": SCHEMA_ID,
        "schemaVersion": SCHEMA_VERSION,
        "contractVersion": CONTRACT_VERSION,
        "seed": SEED,
        "reference": {
            "path": str(REFERENCE_PATH),
            "width": REFERENCE_SIZE[0],
            "height": REFERENCE_SIZE[1],
            "sha256": REFERENCE_SHA256,
        },
        "tools": {
            "blenderExecutable": str(BLENDER_EXECUTABLE),
            "blenderVersion": BLENDER_VERSION,
            "pythonVersion": PYTHON_VERSION,
            "gltfTransformVersion": "not-invoked-diagnostic",
            "ktxVersion": "not-invoked-diagnostic",
        },
        "scripts": {
            "generator": {"path": str((scripts_dir / "generate_tide_scar_tr4_pack.py").resolve()), "sha256": script_hashes["generator"]},
            "evaluator": {"path": str((scripts_dir / "evaluate_tide_scar_tr4_pack.py").resolve()), "sha256": script_hashes["evaluator"]},
            "runner": {"path": str((scripts_dir / "run_tide_scar_tr4_pack.py").resolve()), "sha256": script_hashes["runner"]},
        },
        "scene": {
            "gameplay": {
                "id": "tr4-diagnostic-running-001", "status": "running", "tick": 240,
                "elapsedTicks": 240, "distance": 32.0, "lane": 0, "posture": "run",
                "gaitPhase": 0.25, "runnerRoot": [0, 0, 0], "pursuerPresent": False,
                "hazards": [
                    {"kind": "beam", "courseDistance": 18.0},
                    {"kind": "ring", "courseDistance": 36.0},
                    {"kind": "column", "courseDistance": 54.0},
                    {"kind": "gap", "courseDistance": 72.0},
                ],
            },
            "bookend": {
                "id": "tr4-diagnostic-game-over-001", "status": "game-over", "tick": 420,
                "elapsedTicks": 420, "distance": 63.0, "failureReason": "pursuer-caught",
                "posture": "failure", "runnerRoot": [0, 0, 0], "pursuerPresent": True,
                "pursuerRoot": [0, 0, 2.4],
            },
        },
        "cameras": build_cameras(),
        "construction": construction,
        "collision": {
            "laneWidth": 2.35, "laneCenters": [-2.35, 0, 2.35], "laneTolerance": 0.42,
            "roadBounds": [-3.2, 3.2], "visualSafetyBounds": [-2.92, 2.92],
            "beamClearanceHeight": 0.82, "gapClearanceHeight": 0.52,
            "slideTicks": 31, "ringLowestSolidY": 1.05, "slidePoseMaxY": 0.90,
            "visualPadding": 0.15,
        },
        "materials": build_materials(),
        "semanticRoots": build_roots(),
        "budgets": {
            "desktopDecodedTextureBytes": 39845888, "desktopDrawCalls": 60,
            "desktopVisibleTriangles": 150000, "materialCount": 10,
            "mobileDecodedTextureBytes": 18874368, "mobileDrawCalls": 45,
            "mobileVisibleTriangles": 100000, "optimizedGlbBytes": 8388608,
            "optimizedTriangles": 110000, "sourceTriangles": 150000,
        },
        "outputs": build_outputs(),
        "constructionHash": sha256_bytes(canonical_bytes(construction)),
        "verdict": "READY_FOR_BLENDER",
    }


def validate_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PrecheckBlocked(f"non-finite number at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_finite(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise PrecheckBlocked(f"non-string key at {path}")
            validate_finite(item, f"{path}.{key}")
        return
    raise PrecheckBlocked(f"unsupported value type at {path}: {type(value).__name__}")


def deep_compare(expected: Any, actual: Any, path: str = "$") -> None:
    if type(expected) is not type(actual):
        raise PrecheckBlocked(f"type mismatch at {path}")
    if isinstance(expected, dict):
        if list(expected.keys()) != list(actual.keys()):
            raise PrecheckBlocked(f"unknown/missing/reordered keys at {path}")
        for key in expected:
            deep_compare(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise PrecheckBlocked(f"array length mismatch at {path}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            deep_compare(left, right, f"{path}[{index}]")
    elif expected != actual:
        raise PrecheckBlocked(f"frozen value mismatch at {path}")


def reject_reparse(path: Path, stop: Path | None = None) -> None:
    current = path
    checked: list[Path] = []
    while True:
        checked.append(current)
        if stop is not None and current == stop:
            break
        if current.parent == current:
            break
        current = current.parent
    for item in reversed(checked):
        if not item.exists():
            continue
        attributes = getattr(item.lstat(), "st_file_attributes", 0)
        if item.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise PrecheckBlocked(f"reparse/symlink path rejected: {item}")


def assert_contained(path: Path, root: Path) -> None:
    resolved = path.resolve(strict=False)
    resolved_root = root.resolve(strict=True)
    try:
        common = Path(os.path.commonpath([resolved, resolved_root]))
    except ValueError as exc:
        raise PrecheckBlocked(f"path drive mismatch: {path}") from exc
    if common != resolved_root:
        raise PrecheckBlocked(f"path escapes repository: {path}")
    reject_reparse(path.parent if not path.exists() else path, resolved_root)


def verify_reference() -> None:
    if not REFERENCE_PATH.exists() or not REFERENCE_PATH.is_file():
        raise PrecheckBlocked(f"approved reference is missing: {REFERENCE_PATH}")
    reject_reparse(REFERENCE_PATH)
    if sha256_file(REFERENCE_PATH) != REFERENCE_SHA256:
        raise PrecheckBlocked("approved reference SHA-256 mismatch")
    width, height, bit_depth, color_type = png_header(REFERENCE_PATH)
    if (width, height) != REFERENCE_SIZE:
        raise PrecheckBlocked(f"approved reference dimension mismatch: {width}x{height}")
    if bit_depth not in (8, 16) or color_type not in (0, 2, 4, 6):
        raise PrecheckBlocked("approved reference PNG encoding is unsupported")


def srgb_to_linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def linear_rgb(value: str) -> list[float]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise PrecheckBlocked("invalid closed hexadecimal color")
    try:
        channels = [int(value[index:index + 2], 16) / 255.0 for index in (1, 3, 5)]
    except ValueError as exc:
        raise PrecheckBlocked("invalid closed hexadecimal color") from exc
    return [srgb_to_linear(channel) for channel in channels]


def validate_c6_preflight_contract(preflight: dict[str, Any]) -> None:
    if preflight["tools"].get("pythonVersion") != PYTHON_VERSION or platform.python_version() != PYTHON_VERSION:
        raise PrecheckBlocked("C6 frozen Python tool version mismatch")
    camera_keys = [
        "profile", "resolution", "diagnosticResolution", "position", "target", "up",
        "verticalFovDegrees", "aspect", "near", "far", "lensShiftY", "viewMatrix",
        "projectionMatrix", "projectionAnchors",
    ]
    anchor_keys = [
        "runnerAnchor", "runnerHead", "runnerFootL", "runnerFootR", "beam", "ring",
        "column", "gap", "scar", "routeCenter", "farRoute",
    ]
    if [camera.get("profile") for camera in preflight["cameras"]] != ["portrait", "desktop", "landscape", "closeup"]:
        raise PrecheckBlocked("C6 camera profile order mismatch")
    for camera in preflight["cameras"]:
        if not isinstance(camera, dict) or sorted(camera.keys()) != sorted(camera_keys):
            raise PrecheckBlocked(f"C6 camera schema mismatch: {camera.get('profile')}")
        if camera["up"] != [0.0, 1.0, 0.0]:
            raise PrecheckBlocked(f"C6 camera up-vector mismatch: {camera['profile']}")
        if not isinstance(camera["projectionAnchors"], dict):
            raise PrecheckBlocked(f"C6 projection anchor object mismatch: {camera['profile']}")
        if sorted(camera["projectionAnchors"].keys()) != sorted(anchor_keys):
            raise PrecheckBlocked(f"C6 projection anchor key-set mismatch: {camera['profile']}")
        for name, point in camera["projectionAnchors"].items():
            if not isinstance(point, list) or len(point) != 3:
                raise PrecheckBlocked(f"C6 projection anchor shape mismatch: {camera['profile']}.{name}")
            for index, value in enumerate(point):
                finite_number(value, f"cameras.{camera['profile']}.projectionAnchors.{name}[{index}]")
        canonical_view = canonical_view_row_major(camera["position"], camera["target"], camera["up"])
        expected_webgl_view = [canonical_view[(index % 4) * 4 + index // 4] for index in range(16)]
        if max(abs(left - right) for left, right in zip(camera["viewMatrix"], expected_webgl_view)) > 1.0e-12:
            raise PrecheckBlocked(f"C6 canonical view matrix mismatch: {camera['profile']}")
        if expected_screen_projection(camera)["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER":
            raise PrecheckBlocked(f"C6 analytic screen projection failed: {camera['profile']}")

    lighting = preflight["construction"]["lighting"]
    if not isinstance(lighting, dict) or sorted(lighting.keys()) != sorted([
        "worldColor", "worldStrength", "fogColor", "fogDensity", "fogAnisotropy",
        "key", "fill", "contact",
    ]):
        raise PrecheckBlocked("C6 lighting schema mismatch")
    if (
        lighting["worldColor"] != "#6E8294"
        or lighting["worldStrength"] != 0.55
        or lighting["fogColor"] != "#9AA7A8"
        or lighting["fogDensity"] != 0.0035
        or lighting["fogAnisotropy"] != 0.18
    ):
        raise PrecheckBlocked("C6 atmosphere record mismatch")
    linear_rgb(lighting["worldColor"])
    linear_rgb(lighting["fogColor"])
    for name, minimum_y, sign in (("key", 0.75, -1), ("fill", 0.55, 1)):
        record = lighting[name]
        if not isinstance(record, dict) or sorted(record.keys()) != ["color", "energy", "shadow", "surfaceToLight"]:
            raise PrecheckBlocked(f"C6 {name} light schema mismatch")
        linear_rgb(record["color"])
        vector = record["surfaceToLight"]
        if not isinstance(vector, list) or len(vector) != 3:
            raise PrecheckBlocked(f"C6 {name} surface-to-light shape mismatch")
        normalized = normalize([finite_number(value, f"lighting.{name}.surfaceToLight") for value in vector])
        if normalized[1] < minimum_y or (sign < 0 and normalized[0] >= 0.0) or (sign > 0 and normalized[0] <= 0.0):
            raise PrecheckBlocked(f"C6 {name} surface-to-light direction gate failed")
    contact = lighting["contact"]
    if not isinstance(contact, dict) or sorted(contact.keys()) != ["color", "energy", "location", "shadow", "shape", "size", "target"]:
        raise PrecheckBlocked("C6 contact light schema mismatch")
    if contact != {
        "color": "#E7C79C", "energy": 430.0, "shape": "DISK", "size": 9.0,
        "shadow": False, "location": [0.0, 7.5, 4.0], "target": [0.0, 0.0, -4.0],
    }:
        raise PrecheckBlocked("C6 contact light record mismatch")
    linear_rgb(contact["color"])
    transmittances = [math.exp(-lighting["fogDensity"] * distance) for distance in (20.0, 120.0, 520.0)]
    if not (transmittances[0] >= 0.90 and 0.55 <= transmittances[1] <= 0.72 and transmittances[2] >= 0.12):
        raise PrecheckBlocked("C6 fog transmittance gate failed")


def verify_c6_generator_contract(generator_path: Path) -> None:
    source = generator_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(generator_path))
    functions_by_name = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    view_functions = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "set_view_transform"
    ]
    if len(view_functions) != 1:
        raise PrecheckBlocked("C6 requires exactly one set_view_transform function")
    function = view_functions[0]
    segment = ast.get_source_segment(source, function)
    if segment is None:
        raise PrecheckBlocked("C6 could not isolate set_view_transform source")
    forbidden_text = ("enum_items", "preferred", '"NONE"', "'NONE'", "fallback", "bl_rna")
    if any(token in segment for token in forbidden_text):
        raise PrecheckBlocked("C6 diagnostic view-transform function contains a forbidden enum/fallback pattern")
    for node in ast.walk(function):
        if isinstance(node, ast.Constant) and node.value == "NONE":
            raise PrecheckBlocked("C6 diagnostic view-transform function assigns forbidden NONE")
        if isinstance(node, ast.Name) and node.id == "preferred":
            raise PrecheckBlocked("C6 diagnostic view-transform function uses forbidden preferred selection")
        if isinstance(node, ast.Attribute) and node.attr in ("enum_items", "bl_rna"):
            raise PrecheckBlocked("C6 diagnostic view-transform function inspects forbidden RNA enum metadata")
    required_source = (
        'scene.view_settings.exposure = 0.0',
        'scene.view_settings.gamma = 1.0',
        'scene.render.dither_intensity = 0.0',
        'scene.view_settings.view_transform = "AgX"',
        'scene.view_settings.look = "AgX - Medium High Contrast"',
        'scene.view_settings.view_transform != "AgX"',
        'scene.view_settings.look != "AgX - Medium High Contrast"',
        'scene.view_settings.view_transform = "Raw"',
        'scene.view_settings.look = "None"',
        'scene.view_settings.view_transform != "Raw"',
        'scene.view_settings.look != "None"',
    )
    if any(text not in segment for text in required_source):
        raise PrecheckBlocked("C6 diagnostic view-transform exact assignments/readbacks are incomplete")
    validate_input = functions_by_name.get("validate_input")
    if validate_input is None:
        raise PrecheckBlocked("C6 generator validate_input is missing")
    validate_input_segment = ast.get_source_segment(source, validate_input) or ""
    anchor_contract_tokens = (
        'sorted(record.keys()) != sorted(camera_keys)',
        'not isinstance(record["projectionAnchors"], dict)',
        'sorted(record["projectionAnchors"].keys()) != sorted(anchor_keys)',
    )
    if any(token not in validate_input_segment for token in anchor_contract_tokens):
        raise PrecheckBlocked("C6 generator exact camera/anchor key-set predicate is incomplete")
    if 'list(record["projectionAnchors"].keys())' in validate_input_segment:
        raise PrecheckBlocked("C6 generator retains insertion-order-dependent anchor validation")
    for name in ("apply_camera_profile", "expected_camera_invariants"):
        camera_function = functions_by_name.get(name)
        if camera_function is None:
            raise PrecheckBlocked(f"C6 generator is missing {name}")
        camera_segment = ast.get_source_segment(source, camera_function) or ""
        if "to_track_quat" in camera_segment:
            raise PrecheckBlocked(f"C6 {name} contains forbidden to_track_quat")
    required_tokens = (
        'EXPECTED_CONTRACT = "TEMPLE-TR4-C6"',
        'DIAGNOSTIC_ID = "006"',
        'schema_version != 6',
        'tr4-diagnostic-006-',
        "Matrix((right, true_up, -forward)).transposed().to_quaternion()",
        'record["surfaceToLight"]',
        'lighting["fogAnisotropy"]',
        '"lightingBinding": lighting_binding',
        '"atmosphereBinding": atmosphere_binding',
        '"schemaVersion": 2',
    )
    if any(token not in source for token in required_tokens):
        raise PrecheckBlocked("C6 generator identity/camera/light/atmosphere source is incomplete")
    if 'rotationEulerDegrees' in source:
        raise PrecheckBlocked("C6 generator retains forbidden diagnostic Euler lighting")


def verify_c6_evaluator_contract(evaluator_path: Path) -> None:
    source = evaluator_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(evaluator_path))
    required_tokens = (
        'DIAGNOSTIC_ID = "006"',
        'preflight.get("schemaVersion") != 6',
        'preflight.get("contractVersion") != "TEMPLE-TR4-C6"',
        'tr4-diagnostic-006-',
        'PROFILE_METRIC_KEYS',
        'EVALUATION_GATE_KEYS',
        'roadFarRouteWidthFraction',
        'representativeDepthOrder',
    )
    if any(token not in source for token in required_tokens):
        raise PrecheckBlocked("C6 evaluator closed identity/metrics/gates source is incomplete")
    if not any(isinstance(node, ast.FunctionDef) and node.name == "validate_camera_binding" for node in tree.body):
        raise PrecheckBlocked("C6 evaluator camera binding validator is missing")
    camera_validator = next(
        (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "validate_c6_preflight_cameras"),
        None,
    )
    if camera_validator is None:
        raise PrecheckBlocked("C6 evaluator preflight camera validator is missing")
    camera_segment = ast.get_source_segment(source, camera_validator) or ""
    anchor_contract_tokens = (
        'sorted(record.keys()) != sorted(camera_keys)',
        'not isinstance(record["projectionAnchors"], dict)',
        'sorted(record["projectionAnchors"].keys()) != sorted(anchor_keys)',
    )
    if any(token not in camera_segment for token in anchor_contract_tokens):
        raise PrecheckBlocked("C6 evaluator exact camera/anchor key-set predicate is incomplete")
    if 'list(record["projectionAnchors"].keys())' in camera_segment:
        raise PrecheckBlocked("C6 evaluator retains insertion-order-dependent anchor validation")


def verify_c6_runner_contract(runner_path: Path) -> None:
    source = runner_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(runner_path))
    functions_by_name = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    camera_validator = functions_by_name.get("validate_c6_preflight_contract")
    prepare = functions_by_name.get("prepare_diagnostic")
    if camera_validator is None or prepare is None:
        raise PrecheckBlocked("C6 runner validator/canonical preparation function is missing")
    camera_segment = ast.get_source_segment(source, camera_validator) or ""
    anchor_contract_tokens = (
        'sorted(camera.keys()) != sorted(camera_keys)',
        'not isinstance(camera["projectionAnchors"], dict)',
        'sorted(camera["projectionAnchors"].keys()) != sorted(anchor_keys)',
    )
    if any(token not in camera_segment for token in anchor_contract_tokens):
        raise PrecheckBlocked("C6 runner exact camera/anchor key-set predicate is incomplete")
    if 'list(camera["projectionAnchors"].keys())' in camera_segment:
        raise PrecheckBlocked("C6 runner retains insertion-order-dependent anchor validation")
    prepare_segment = ast.get_source_segment(source, prepare) or ""
    round_trip_tokens = (
        'authored_preflight = build_preflight(repo_root, script_hashes)',
        'canonical_preflight_bytes = canonical_bytes(authored_preflight)',
        'preflight = json.loads(canonical_preflight_bytes.decode("utf-8"))',
        'validate_c6_preflight_contract(preflight)',
        'canonical_bytes(preflight) != canonical_preflight_bytes',
    )
    if any(token not in prepare_segment for token in round_trip_tokens):
        raise PrecheckBlocked("C6 runner canonical round-trip source is incomplete")


def verify_scripts(repo_root: Path) -> tuple[dict[str, Path], dict[str, str]]:
    scripts_dir = repo_root / "tools" / "temple-asset-pipeline"
    scripts = {
        "generator": scripts_dir / "generate_tide_scar_tr4_pack.py",
        "evaluator": scripts_dir / "evaluate_tide_scar_tr4_pack.py",
        "runner": scripts_dir / "run_tide_scar_tr4_pack.py",
    }
    hashes: dict[str, str] = {}
    for name, path in scripts.items():
        assert_contained(path, repo_root)
        if not path.exists() or not path.is_file():
            raise PrecheckBlocked(f"missing authorized script: {path}")
        if path.name != f"{('generate_tide_scar_tr4_pack' if name == 'generator' else 'evaluate_tide_scar_tr4_pack' if name == 'evaluator' else 'run_tide_scar_tr4_pack')}.py":
            raise PrecheckBlocked(f"unexpected script name: {path}")
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            raise PrecheckBlocked(f"authorized script does not parse as UTF-8 Python: {path}: {exc}") from exc
        if name == "generator":
            verify_c6_generator_contract(path)
        elif name == "evaluator":
            verify_c6_evaluator_contract(path)
        else:
            verify_c6_runner_contract(path)
        hashes[name] = sha256_file(path)
        if len(hashes[name]) != 64:
            raise PrecheckBlocked(f"invalid script hash: {path}")
    return scripts, hashes


def verify_c6_authorization(repo_root: Path) -> None:
    authorization = (repo_root / AUTHORIZATION_RELATIVE).resolve(strict=True)
    current_task = (repo_root / CURRENT_TASK_RELATIVE).resolve(strict=True)
    coordination_log = (repo_root / COORDINATION_LOG_RELATIVE).resolve(strict=True)
    for path in (authorization, current_task, coordination_log):
        assert_contained(path, repo_root)
        if not path.is_file():
            raise PrecheckBlocked(f"required authorization input is missing: {path}")
    authorization_text = authorization.read_text(encoding="utf-8")
    if "Status: **AUTHORIZED.**" not in authorization_text:
        raise PrecheckBlocked("diagnostic-006 authorization status is not AUTHORIZED")
    if authorization_text.count("READY_FOR_DIAGNOSTIC_006_CONTRACT") < 2:
        raise PrecheckBlocked("diagnostic-006 two independent contract verdicts are missing")
    current_task_text = current_task.read_text(encoding="utf-8")
    if "Current sub-slice: **diagnostic `006` authorized" not in current_task_text:
        raise PrecheckBlocked("CURRENT_TASK.md does not name diagnostic 006 as the authorized current sub-slice")
    coordination_text = coordination_log.read_text(encoding="utf-8")
    if "REPORT TEMPLE-TR4-DIAGNOSTIC-006 AUTHORIZED" not in coordination_text:
        raise PrecheckBlocked("coordination THREAD_LOG lacks TEMPLE-TR4-DIAGNOSTIC-006 AUTHORIZED")


def verify_c6_frozen_evidence(repo_root: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, (relative_path, expected_hash) in FROZEN_C6_EVIDENCE.items():
        path = (repo_root / relative_path).resolve(strict=True)
        assert_contained(path, repo_root)
        if not path.is_file():
            raise PrecheckBlocked(f"frozen evidence is missing: {relative_path}")
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise PrecheckBlocked(f"frozen evidence SHA-256 mismatch: {relative_path}")
        observed[name] = actual_hash
    c4_root = (repo_root / "docs/workstreams/temple-tr4-asset/diagnostic-004").resolve(strict=True)
    assert_contained(c4_root, repo_root)
    expected_c4_names = {
        Path(relative_path).name
        for name, (relative_path, _expected_hash) in FROZEN_C6_EVIDENCE.items()
        if "diagnostic004" in name
    }
    actual_c4_names = {path.name for path in c4_root.iterdir() if path.is_file()}
    actual_c4_directories = [path.name for path in c4_root.iterdir() if path.is_dir()]
    if len(expected_c4_names) != 27 or actual_c4_names != expected_c4_names or actual_c4_directories:
        raise PrecheckBlocked(
            f"frozen diagnostic-004 exact-set mismatch: files={sorted(actual_c4_names)}, directories={actual_c4_directories}"
        )
    c5_root = (repo_root / "docs/workstreams/temple-tr4-asset/diagnostic-005").resolve(strict=True)
    assert_contained(c5_root, repo_root)
    expected_c5_names = {
        Path(relative_path).name
        for name, (relative_path, _expected_hash) in FROZEN_C6_EVIDENCE.items()
        if "diagnostic005" in name
    }
    actual_c5_names = {path.name for path in c5_root.iterdir() if path.is_file()}
    actual_c5_directories = [path.name for path in c5_root.iterdir() if path.is_dir()]
    if len(expected_c5_names) != 4 or actual_c5_names != expected_c5_names or actual_c5_directories:
        raise PrecheckBlocked(
            f"frozen diagnostic-005 exact-set mismatch: files={sorted(actual_c5_names)}, directories={actual_c5_directories}"
        )
    return observed


def verify_blender_executable() -> str:
    if not BLENDER_EXECUTABLE.is_file():
        raise PrecheckBlocked(f"Blender executable missing: {BLENDER_EXECUTABLE}")
    reject_reparse(BLENDER_EXECUTABLE)
    actual_hash = sha256_file(BLENDER_EXECUTABLE)
    if actual_hash != BLENDER_EXECUTABLE_SHA256:
        raise PrecheckBlocked("Blender executable SHA-256 mismatch")
    return actual_hash


def verify_probe_scripts(repo_root: Path) -> tuple[dict[str, Path], dict[str, str]]:
    scripts_dir = repo_root / "tools" / "temple-asset-pipeline"
    scripts = {
        "generator": scripts_dir / "generate_tide_scar_tr4_pack.py",
        "runner": scripts_dir / "run_tide_scar_tr4_pack.py",
    }
    hashes: dict[str, str] = {}
    for name, path in scripts.items():
        assert_contained(path, repo_root)
        if not path.is_file():
            raise PrecheckBlocked(f"missing camera-probe script: {path}")
        expected_name = "generate_tide_scar_tr4_pack.py" if name == "generator" else "run_tide_scar_tr4_pack.py"
        if path.name != expected_name:
            raise PrecheckBlocked(f"unexpected camera-probe script name: {path}")
        hashes[name] = sha256_file(path)
    return scripts, hashes


def atomic_write_json(path: Path, value: Any) -> None:
    data = canonical_bytes(value)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def verify_render_set(root: Path, outputs: list[dict[str, Any]]) -> None:
    expected_names = [item["relativePath"] for item in outputs]
    actual_names = sorted(path.name for path in root.glob("*.png"))
    if sorted(expected_names) != actual_names or len(actual_names) != 20:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED exact PNG set mismatch: {actual_names}")
    order_path = root / "render-order.json"
    if not order_path.is_file():
        raise RuntimeError("DIAGNOSTIC_BLOCKED missing render-order.json")
    order = json.loads(order_path.read_text(encoding="utf-8"))
    if order != expected_names:
        raise RuntimeError("DIAGNOSTIC_BLOCKED render order mismatch")
    for item in outputs:
        path = root / item["relativePath"]
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED empty output: {path}")
        width, height, bit_depth, color_type = png_header(path)
        if (width, height) != (item["width"], item["height"]):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED dimension mismatch: {path}")
        expected_depth = 16 if item["pass"] == "linear-depth" else 8
        if bit_depth != expected_depth:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED bit depth mismatch: {path}")
        if item["pass"] in ("road-mask", "linear-depth") and color_type != 0:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED grayscale encoding mismatch: {path}")
        if item["pass"] in ("beauty", "object-id", "normal") and color_type not in (2, 6):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED color encoding mismatch: {path}")


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED non-numeric value: {label}")
    number = float(value)
    if not math.isfinite(number):
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED non-finite value: {label}")
    return number


def finite_matrix(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 16:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED matrix shape mismatch: {label}")
    return [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]


def finite_vector(value: Any, length: int, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED vector shape mismatch: {label}")
    return [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]


def angle_between(left: list[float], right: list[float]) -> float:
    left_unit = normalize(left)
    right_unit = normalize(right)
    return math.acos(max(-1.0, min(1.0, dot(left_unit, right_unit))))


def validate_orientation_binding(record: Any, camera: dict[str, Any], label: str) -> None:
    if not isinstance(record, dict) or sorted(record.keys()) != sorted(ORIENTATION_KEYS):
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED orientation schema mismatch: {label}")
    for name in ("position", "target", "up"):
        values = finite_vector(record[name], 3, f"{label}.{name}")
        if values != [float(value) for value in camera[name]]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED orientation frozen record mismatch: {label}.{name}")
    expected_basis = camera_basis(camera["position"], camera["target"], camera["up"])
    for name in ("forward", "right", "trueUp", "vectorLengths", "pairwiseDots"):
        values = finite_vector(record[name], 3, f"{label}.{name}")
        if max(abs(left - right) for left, right in zip(values, expected_basis[name])) > 5.0e-7:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED orientation basis mismatch: {label}.{name}")
    determinant = finite_number(record["determinant"], f"{label}.determinant")
    if abs(determinant - expected_basis["determinant"]) > 5.0e-7 or abs(determinant - 1.0) > 5.0e-7:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED orientation determinant mismatch: {label}")
    canonical = finite_matrix(record["canonicalViewMatrix"], f"{label}.canonicalViewMatrix")
    expected_view = canonical_view_row_major(camera["position"], camera["target"], camera["up"])
    if max(abs(left - right) for left, right in zip(canonical, expected_view)) > 1.0e-12:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED canonical view matrix mismatch: {label}")
    actual = finite_matrix(record["actualViewMatrix"], f"{label}.actualViewMatrix")
    max_error = max(abs(left - right) for left, right in zip(actual, expected_view))
    recorded_error = finite_number(record["maxViewMatrixError"], f"{label}.maxViewMatrixError")
    if abs(recorded_error - max_error) > 1.0e-12 or max_error > 5.0e-6:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED actual view matrix mismatch: {label}")
    actual_forward = [-actual[8], -actual[9], -actual[10]]
    actual_up = [actual[4], actual[5], actual[6]]
    recomputed_forward_angle = angle_between(actual_forward, expected_basis["forward"])
    recomputed_up_angle = angle_between(actual_up, expected_basis["trueUp"])
    forward_angle = finite_number(record["localForwardAngleRadians"], f"{label}.localForwardAngleRadians")
    up_angle = finite_number(record["localUpAngleRadians"], f"{label}.localUpAngleRadians")
    if (
        abs(forward_angle - recomputed_forward_angle) > 1.0e-12
        or abs(up_angle - recomputed_up_angle) > 1.0e-12
        or recomputed_forward_angle > 1.0e-5
        or recomputed_up_angle > 1.0e-5
    ):
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED local camera axis alignment failed: {label}")


def validate_screen_projection_binding(record: Any, camera: dict[str, Any], label: str) -> None:
    if not isinstance(record, dict) or sorted(record.keys()) != sorted(SCREEN_PROJECTION_KEYS):
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED screen-projection schema mismatch: {label}")
    expected = expected_screen_projection(camera)
    runner_anchor = finite_vector(record["runnerAnchor"], 2, f"{label}.runnerAnchor")
    if max(abs(left - right) for left, right in zip(runner_anchor, expected["runnerAnchor"])) > 1.0e-12:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED runner anchor projection mismatch: {label}")
    for name in SCREEN_PROJECTION_KEYS[1:-1]:
        actual = finite_number(record[name], f"{label}.{name}")
        if abs(actual - expected[name]) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED screen projection mismatch: {label}.{name}")
    if record["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER":
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED screen projection verdict mismatch: {label}")


def validate_lighting_binding(binding: Any, lighting: dict[str, Any]) -> None:
    if not isinstance(binding, dict) or sorted(binding.keys()) != ["contact", "fill", "key", "verdict"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED lighting binding schema mismatch")
    if binding["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER":
        raise RuntimeError("DIAGNOSTIC_BLOCKED lighting binding verdict mismatch")
    directional_keys = [
        "colorHex", "colorLinear", "energy", "shadow", "surfaceToLight",
        "normalizedSurfaceToLight", "actualLocalMinusZ", "alignmentRadians",
    ]
    for name in ("key", "fill"):
        record = binding[name]
        frozen = lighting[name]
        label = f"lightingBinding.{name}"
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(directional_keys):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light binding schema mismatch: {name}")
        if record["colorHex"] != frozen["color"] or record["shadow"] is not frozen["shadow"]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light exact readback mismatch: {name}")
        if abs(finite_number(record["energy"], f"{label}.energy") - frozen["energy"]) > 1.0e-6:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light energy mismatch: {name}")
        color = finite_vector(record["colorLinear"], 3, f"{label}.colorLinear")
        if max(abs(left - right) for left, right in zip(color, linear_rgb(frozen["color"]))) > 1.0e-6:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light color mismatch: {name}")
        source = finite_vector(record["surfaceToLight"], 3, f"{label}.surfaceToLight")
        if source != [float(value) for value in frozen["surfaceToLight"]]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light source vector mismatch: {name}")
        normalized = normalize(source)
        recorded_normalized = finite_vector(record["normalizedSurfaceToLight"], 3, f"{label}.normalizedSurfaceToLight")
        if max(abs(left - right) for left, right in zip(normalized, recorded_normalized)) > 5.0e-7:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light normalization mismatch: {name}")
        actual_minus_z = finite_vector(record["actualLocalMinusZ"], 3, f"{label}.actualLocalMinusZ")
        expected_direction = [-component for component in normalized]
        alignment = angle_between(actual_minus_z, expected_direction)
        recorded_alignment = finite_number(record["alignmentRadians"], f"{label}.alignmentRadians")
        if abs(recorded_alignment - alignment) > 1.0e-12 or alignment > 1.0e-5:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED directional light alignment mismatch: {name}")
    contact_keys = [
        "colorHex", "colorLinear", "energy", "size", "shadow", "location", "target",
        "actualLocalMinusZ", "alignmentRadians",
    ]
    contact = binding["contact"]
    frozen_contact = lighting["contact"]
    if not isinstance(contact, dict) or sorted(contact.keys()) != sorted(contact_keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED contact light binding schema mismatch")
    if contact["colorHex"] != frozen_contact["color"] or contact["shadow"] is not frozen_contact["shadow"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED contact light exact readback mismatch")
    for name in ("energy", "size"):
        if abs(finite_number(contact[name], f"lightingBinding.contact.{name}") - frozen_contact[name]) > 1.0e-6:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED contact light {name} mismatch")
    color = finite_vector(contact["colorLinear"], 3, "lightingBinding.contact.colorLinear")
    if max(abs(left - right) for left, right in zip(color, linear_rgb(frozen_contact["color"]))) > 1.0e-6:
        raise RuntimeError("DIAGNOSTIC_BLOCKED contact light color mismatch")
    location = finite_vector(contact["location"], 3, "lightingBinding.contact.location")
    target = finite_vector(contact["target"], 3, "lightingBinding.contact.target")
    if location != frozen_contact["location"] or target != frozen_contact["target"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED contact light placement mismatch")
    actual_minus_z = finite_vector(contact["actualLocalMinusZ"], 3, "lightingBinding.contact.actualLocalMinusZ")
    expected_direction = normalize(vector_sub(target, location))
    alignment = angle_between(actual_minus_z, expected_direction)
    recorded_alignment = finite_number(contact["alignmentRadians"], "lightingBinding.contact.alignmentRadians")
    if abs(recorded_alignment - alignment) > 1.0e-12 or alignment > 1.0e-5:
        raise RuntimeError("DIAGNOSTIC_BLOCKED contact light alignment mismatch")


def validate_atmosphere_binding(binding: Any, lighting: dict[str, Any]) -> None:
    keys = [
        "worldColorHex", "worldColorLinear", "worldStrength", "fogColorHex",
        "fogColorLinear", "fogDensity", "fogAnisotropy", "transmittance20",
        "transmittance120", "transmittance520", "beautyViewTransform", "beautyLook",
        "exposure", "gamma", "dither", "verdict",
    ]
    if not isinstance(binding, dict) or sorted(binding.keys()) != sorted(keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED atmosphere binding schema mismatch")
    exact = {
        "worldColorHex": lighting["worldColor"], "fogColorHex": lighting["fogColor"],
        "beautyViewTransform": "AgX", "beautyLook": "AgX - Medium High Contrast",
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }
    if any(binding[name] != value for name, value in exact.items()):
        raise RuntimeError("DIAGNOSTIC_BLOCKED atmosphere exact record mismatch")
    for name, expected in (
        ("worldStrength", lighting["worldStrength"]), ("fogDensity", lighting["fogDensity"]),
        ("fogAnisotropy", lighting["fogAnisotropy"]), ("exposure", 0.0),
        ("gamma", 1.0), ("dither", 0.0),
    ):
        if abs(finite_number(binding[name], f"atmosphereBinding.{name}") - expected) > 1.0e-6:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED atmosphere numeric mismatch: {name}")
    for name, color_key in (("worldColorLinear", "worldColor"), ("fogColorLinear", "fogColor")):
        values = finite_vector(binding[name], 3, f"atmosphereBinding.{name}")
        if max(abs(left - right) for left, right in zip(values, linear_rgb(lighting[color_key]))) > 1.0e-6:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED atmosphere color mismatch: {name}")
    transmittances = {
        "transmittance20": math.exp(-lighting["fogDensity"] * 20.0),
        "transmittance120": math.exp(-lighting["fogDensity"] * 120.0),
        "transmittance520": math.exp(-lighting["fogDensity"] * 520.0),
    }
    for name, expected in transmittances.items():
        if abs(finite_number(binding[name], f"atmosphereBinding.{name}") - expected) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED atmosphere transmittance mismatch: {name}")


def validate_camera_binding(path: Path, preflight: dict[str, Any]) -> str:
    if not path.is_file():
        raise RuntimeError("DIAGNOSTIC_BLOCKED missing camera-binding.json")
    binding = json.loads(path.read_text(encoding="utf-8"))
    top_keys = [
        "schemaId", "schemaVersion", "diagnosticId", "blenderVersion", "profiles",
        "lightingBinding", "atmosphereBinding", "renderCallCountAtWrite", "verdict",
    ]
    if not isinstance(binding, dict) or sorted(binding.keys()) != sorted(top_keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED camera binding top-level schema mismatch")
    if (
        binding["schemaId"] != "tide-relay.temple-tr4.camera-binding"
        or isinstance(binding["schemaVersion"], bool)
        or not isinstance(binding["schemaVersion"], int)
        or binding["schemaVersion"] != 2
        or binding["diagnosticId"] != DIAGNOSTIC_ID
        or binding["blenderVersion"] != BLENDER_VERSION
        or isinstance(binding["renderCallCountAtWrite"], bool)
        or not isinstance(binding["renderCallCountAtWrite"], int)
        or binding["renderCallCountAtWrite"] != 0
        or binding["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER"
    ):
        raise RuntimeError("DIAGNOSTIC_BLOCKED camera binding identity/verdict mismatch")
    profiles = binding["profiles"]
    cameras = preflight["cameras"]
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise RuntimeError("DIAGNOSTIC_BLOCKED camera binding profile count mismatch")
    for profile_index, (record, camera) in enumerate(zip(profiles, cameras)):
        label = f"cameraBinding.profiles[{profile_index}]"
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(CAMERA_BINDING_PROFILE_KEYS):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera binding profile schema mismatch: {profile_index}")
        if record["profile"] != camera["profile"]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera binding profile order mismatch: {profile_index}")
        lens_shift = finite_number(record["lensShiftY"], f"{label}.lensShiftY")
        if lens_shift != camera["lensShiftY"]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera binding lens target mismatch: {profile_index}")
        scalar_names = [
            "originalShift0", "evaluatedShift0", "originalShift1", "evaluatedShift1",
            "b0", "b1", "response", "maxOffTargetCalibrationDelta", "dominanceRatio",
            "solvedShift", "evaluatedSolvedShift", "actual", "targetError",
            "maxOffTargetSolvedDelta", "maxProjectionError",
        ]
        scalars = {name: finite_number(record[name], f"{label}.{name}") for name in scalar_names}
        matrices = {
            name: finite_matrix(record[name], f"{label}.{name}")
            for name in ("matrix0", "matrix1", "difference", "matrixSolved", "solvedDifference", "webglMatrix")
        }
        if any(abs(scalars[name] - expected) > 1.0e-8 for name, expected in (
            ("originalShift0", 0.0), ("evaluatedShift0", 0.0),
            ("originalShift1", 1.0), ("evaluatedShift1", 1.0),
        )):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera calibration shift propagation mismatch: {profile_index}")
        expected_difference = [second - first for first, second in zip(matrices["matrix0"], matrices["matrix1"])]
        if max(abs(left - right) for left, right in zip(matrices["difference"], expected_difference)) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera calibration difference arithmetic mismatch: {profile_index}")
        if abs(scalars["b0"] - matrices["matrix0"][6]) > 1.0e-12 or abs(scalars["b1"] - matrices["matrix1"][6]) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera binding target aliases mismatch: {profile_index}")
        if abs(scalars["b0"]) > 1.0e-7:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera zero baseline mismatch: {profile_index}")
        response = matrices["difference"][6]
        if abs(scalars["response"] - response) > 1.0e-12 or response <= 0.0 or abs(response - 2.0) > 5.0e-7:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera response gate failed: {profile_index}")
        max_off_target = max(abs(value) for index, value in enumerate(matrices["difference"]) if index != 6)
        dominance = abs(response) / max(max_off_target, 1.0e-12)
        if (
            abs(scalars["maxOffTargetCalibrationDelta"] - max_off_target) > 1.0e-12
            or max_off_target > 5.0e-7
            or abs(scalars["dominanceRatio"] - dominance) > 1.0e-12
            or dominance < 1.0e6
        ):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera off-target calibration gate failed: {profile_index}")
        expected_solved = (lens_shift - matrices["matrix0"][6]) / response
        if abs(scalars["solvedShift"] - expected_solved) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera solved-shift arithmetic mismatch: {profile_index}")
        if abs(scalars["evaluatedSolvedShift"] - scalars["solvedShift"]) > 1.0e-8:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED evaluated solved shift mismatch: {profile_index}")
        expected_solved_difference = [value - baseline for value, baseline in zip(matrices["matrixSolved"], matrices["matrix0"])]
        if max(abs(left - right) for left, right in zip(matrices["solvedDifference"], expected_solved_difference)) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera solved-difference arithmetic mismatch: {profile_index}")
        actual = matrices["matrixSolved"][6]
        target_error = abs(actual - lens_shift)
        max_solved_off_target = max(abs(value) for index, value in enumerate(matrices["solvedDifference"]) if index != 6)
        if (
            abs(scalars["actual"] - actual) > 1.0e-12
            or abs(scalars["targetError"] - target_error) > 1.0e-12
            or target_error > 5.0e-7
            or abs(scalars["maxOffTargetSolvedDelta"] - max_solved_off_target) > 1.0e-12
            or max_solved_off_target > 5.0e-7
        ):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera solved matrix gate failed: {profile_index}")
        expected_webgl = [matrices["matrixSolved"][(index % 4) * 4 + index // 4] for index in range(16)]
        if max(abs(left - right) for left, right in zip(matrices["webglMatrix"], expected_webgl)) > 1.0e-12:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera WebGL transpose mismatch: {profile_index}")
        projection_errors = [abs(actual_value - expected_value) for actual_value, expected_value in zip(matrices["webglMatrix"], camera["projectionMatrix"])]
        max_projection_error = max(projection_errors)
        if abs(scalars["maxProjectionError"] - max_projection_error) > 1.0e-12 or max_projection_error > 5.0e-7 or projection_errors[9] > 5.0e-7:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED camera frozen projection mismatch: {profile_index}")
        validate_orientation_binding(record["orientation"], camera, f"{label}.orientation")
        validate_screen_projection_binding(record["screenProjection"], camera, f"{label}.screenProjection")
    lighting = preflight["construction"]["lighting"]
    validate_lighting_binding(binding["lightingBinding"], lighting)
    validate_atmosphere_binding(binding["atmosphereBinding"], lighting)
    return sha256_file(path)


def validate_render_order(path: Path, outputs: list[dict[str, Any]]) -> str:
    if not path.is_file():
        raise RuntimeError("DIAGNOSTIC_BLOCKED missing render-order.json")
    expected = [record["relativePath"] for record in outputs]
    actual = json.loads(path.read_text(encoding="utf-8"))
    if actual != expected:
        raise RuntimeError("DIAGNOSTIC_BLOCKED render-order.json mismatch")
    return sha256_file(path)


def validate_scene_metrics(path: Path, preflight: dict[str, Any]) -> str:
    if not path.is_file():
        raise RuntimeError("DIAGNOSTIC_BLOCKED missing scene-metrics.json")
    metrics = json.loads(path.read_text(encoding="utf-8"))
    keys = [
        "meshObjects", "sourceTrianglesBeforeModifiers", "beautyMaterialCount",
        "semanticRoots", "pursuerBookendRoot", "runnerRoot", "roadTopY", "verdict",
    ]
    if not isinstance(metrics, dict) or sorted(metrics.keys()) != sorted(keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED scene metrics schema mismatch")
    for name in ("meshObjects", "sourceTrianglesBeforeModifiers", "beautyMaterialCount"):
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene metric count mismatch: {name}")
        if value != EXPECTED_SCENE_COUNTS[name]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED frozen scene metric count drift: {name}")
    if metrics["sourceTrianglesBeforeModifiers"] > preflight["budgets"]["sourceTriangles"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED source triangle budget exceeded")
    if metrics["beautyMaterialCount"] > preflight["budgets"]["materialCount"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED material budget exceeded")
    roots = metrics["semanticRoots"]
    expected_names = [record["name"] for record in preflight["semanticRoots"]]
    if not isinstance(roots, list) or len(roots) != 9:
        raise RuntimeError("DIAGNOSTIC_BLOCKED scene semantic root count mismatch")
    for index, (record, expected_name) in enumerate(zip(roots, expected_names)):
        if not isinstance(record, dict) or sorted(record.keys()) != ["children", "name", "translation"]:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene semantic root schema mismatch: {index}")
        if (
            record["name"] != expected_name
            or isinstance(record["children"], bool)
            or not isinstance(record["children"], int)
            or record["children"] != EXPECTED_ROOT_CHILDREN[index]
        ):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene semantic root identity/count mismatch: {index}")
        translation = record["translation"]
        if not isinstance(translation, list) or len(translation) != 3:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene semantic root translation mismatch: {index}")
        values = [finite_number(value, f"sceneMetrics.semanticRoots[{index}].translation") for value in translation]
        expected_translation = preflight["construction"]["pursuer"]["bookendRoot"] if expected_name == "TR4_Pursuer_Cinematic" else [0, 0, 0]
        if any(not math.isclose(actual, float(expected), rel_tol=0.0, abs_tol=1.0e-6) for actual, expected in zip(values, expected_translation)):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene semantic root placement mismatch: {expected_name}")
    vector_expectations = (
        ("pursuerBookendRoot", preflight["construction"]["pursuer"]["bookendRoot"]),
        ("runnerRoot", preflight["construction"]["runner"]["root"]),
    )
    for name, expected in vector_expectations:
        vector = metrics[name]
        if not isinstance(vector, list) or len(vector) != 3:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene metric vector mismatch: {name}")
        values = [finite_number(value, f"sceneMetrics.{name}") for value in vector]
        if any(not math.isclose(actual, float(frozen), rel_tol=0.0, abs_tol=1.0e-6) for actual, frozen in zip(values, expected)):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED scene metric vector mismatch: {name}")
    if not math.isclose(
        finite_number(metrics["roadTopY"], "sceneMetrics.roadTopY"),
        float(preflight["construction"]["road"]["surfaceY"]),
        rel_tol=0.0,
        abs_tol=1.0e-6,
    ):
        raise RuntimeError("DIAGNOSTIC_BLOCKED scene road top mismatch")
    if metrics["verdict"] != "RENDERED_FOR_EVALUATION":
        raise RuntimeError("DIAGNOSTIC_BLOCKED scene metrics verdict mismatch")
    return sha256_file(path)


def assert_exact_files(root: Path, allowed: set[str], *, subset: bool = False) -> None:
    directories = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_dir()]
    if directories:
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED unexpected directories: {directories}")
    actual = {path.name for path in root.iterdir() if path.is_file()}
    if (not subset and actual != allowed) or (subset and not actual.issubset(allowed)):
        unexpected = sorted(actual - allowed)
        missing = [] if subset else sorted(allowed - actual)
        raise RuntimeError(f"DIAGNOSTIC_BLOCKED ancillary allowlist mismatch: unexpected={unexpected}, missing={missing}")


def validate_evaluation_metrics(evaluation: dict[str, Any]) -> None:
    semantic_names = [
        "background", "road", "canyon", "runner", "pursuer", "beam", "ring",
        "column", "gap-lips", "tide-scar",
    ]
    profiles = evaluation["profileMetrics"]
    counts = evaluation["semanticPixelCounts"]
    hazards = evaluation["hazardPixelTotalsOrdinary"]
    gates = evaluation["gates"]
    if not isinstance(profiles, dict) or list(profiles.keys()) != ["portrait", "desktop", "landscape", "closeup"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED profileMetrics profile order/schema mismatch")
    if not isinstance(counts, dict) or list(counts.keys()) != ["portrait", "desktop", "landscape", "closeup"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED semanticPixelCounts profile order/schema mismatch")
    if not isinstance(hazards, dict) or list(hazards.keys()) != ["beam", "ring", "column", "gap-lips"]:
        raise RuntimeError("DIAGNOSTIC_BLOCKED hazardPixelTotalsOrdinary schema mismatch")
    if not isinstance(gates, dict) or sorted(gates.keys()) != sorted(EVALUATION_GATE_KEYS):
        raise RuntimeError("DIAGNOSTIC_BLOCKED evaluation gate schema mismatch")
    if any(value is not True for value in gates.values()):
        raise RuntimeError("DIAGNOSTIC_BLOCKED evaluator reported a non-green closed gate")
    ordinary = ("portrait", "desktop", "landscape")
    for profile in profiles:
        metric = profiles[profile]
        if not isinstance(metric, dict) or sorted(metric.keys()) != sorted(PROFILE_METRIC_KEYS):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED profile metric schema mismatch: {profile}")
        count_record = counts[profile]
        if not isinstance(count_record, dict) or list(count_record.keys()) != semantic_names:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED semantic pixel-count schema mismatch: {profile}")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in count_record.values()):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED semantic pixel-count type mismatch: {profile}")
        scalar_names = [
            "luminanceP50", "luminanceP95", "nearBlackFraction", "routeLuminanceP50",
            "roadMaskFraction", "runnerCentroidY", "runnerMargin", "runnerBeautyLuminanceP50",
            "roadBottomWidthFraction", "roadFarRouteWidthFraction", "roadWidthRatio",
        ]
        scalars = {name: finite_number(metric[name], f"profileMetrics.{profile}.{name}") for name in scalar_names}
        for name in ("normalUniqueColors", "depthUniqueValues", "depthMin", "depthMax", "pursuerWidthPixels"):
            value = metric[name]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise RuntimeError(f"DIAGNOSTIC_BLOCKED profile integer metric mismatch: {profile}.{name}")
        runner_bounds = finite_vector(metric["runnerBounds"], 4, f"profileMetrics.{profile}.runnerBounds")
        if not (0.0 <= runner_bounds[0] < runner_bounds[2] <= 1.0 and 0.0 <= runner_bounds[1] < runner_bounds[3] <= 1.0):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED runner bounds invalid: {profile}")
        for nested_name in ("semanticCentroidY", "representativeDepth"):
            nested = metric[nested_name]
            if not isinstance(nested, dict) or list(nested.keys()) != ["runner", "beam", "ring", "column", "gap-lips"]:
                raise RuntimeError(f"DIAGNOSTIC_BLOCKED nested semantic metric schema mismatch: {profile}.{nested_name}")
            for key, value in nested.items():
                finite_number(value, f"profileMetrics.{profile}.{nested_name}.{key}")
        normal_median = finite_vector(metric["roadNormalMedian"], 3, f"profileMetrics.{profile}.roadNormalMedian")
        if any(value < 0.0 or value > 255.0 for value in normal_median):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED road normal channel range mismatch: {profile}")
        if not (
            scalars["luminanceP50"] >= 0.12
            and scalars["luminanceP95"] >= 0.55
            and scalars["nearBlackFraction"] < 0.10
            and scalars["routeLuminanceP50"] >= 0.25
            and 0.02 <= scalars["roadMaskFraction"] <= 0.82
            and metric["normalUniqueColors"] >= 24
            and metric["depthUniqueValues"] >= 64
            and metric["depthMin"] < metric["depthMax"]
            and scalars["runnerMargin"] >= 0.02
            and scalars["runnerBeautyLuminanceP50"] >= 0.12
            and normal_median[1] >= 240.0
            and 112.0 <= normal_median[0] <= 144.0
            and 112.0 <= normal_median[2] <= 144.0
        ):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED reported threshold metric failed: {profile}")
        if any(count_record[name] <= 0 for name in ("road", "canyon", "runner", "tide-scar")):
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED required semantic pixels missing: {profile}")
        if profile in ordinary:
            low, high = (0.61, 0.72) if profile == "portrait" else (0.62, 0.76)
            bottom_min = 0.74 if profile == "portrait" else 0.44
            far_low, far_high = (0.06, 0.19) if profile == "portrait" else (0.015, 0.08)
            centroid = metric["semanticCentroidY"]
            depth = metric["representativeDepth"]
            if not (
                low <= scalars["runnerCentroidY"] <= high
                and scalars["roadBottomWidthFraction"] >= bottom_min
                and far_low <= scalars["roadFarRouteWidthFraction"] <= far_high
                and scalars["roadWidthRatio"] >= 2.5
                and centroid["runner"] > centroid["beam"] > centroid["ring"] > centroid["column"] > centroid["gap-lips"]
                and depth["runner"] < depth["beam"] < depth["ring"] < depth["column"] < depth["gap-lips"]
            ):
                raise RuntimeError(f"DIAGNOSTIC_BLOCKED ordinary perspective/order metric failed: {profile}")
            if any(metric[name] is not None for name in ("pursuerBounds", "pursuerMargin", "pursuerBeautyLuminanceP50", "pursuerBeautyLuminanceP95")) or metric["pursuerWidthPixels"] != 0:
                raise RuntimeError(f"DIAGNOSTIC_BLOCKED ordinary pursuer metrics are not null/zero: {profile}")
        else:
            pursuer_bounds = finite_vector(metric["pursuerBounds"], 4, "profileMetrics.closeup.pursuerBounds")
            if not (0.0 <= pursuer_bounds[0] < pursuer_bounds[2] <= 1.0 and 0.0 <= pursuer_bounds[1] < pursuer_bounds[3] <= 1.0):
                raise RuntimeError("DIAGNOSTIC_BLOCKED closeup pursuer bounds invalid")
            if not (
                finite_number(metric["pursuerMargin"], "profileMetrics.closeup.pursuerMargin") >= 0.02
                and metric["pursuerWidthPixels"] >= 48
                and finite_number(metric["pursuerBeautyLuminanceP50"], "profileMetrics.closeup.pursuerBeautyLuminanceP50") >= 0.08
                and finite_number(metric["pursuerBeautyLuminanceP95"], "profileMetrics.closeup.pursuerBeautyLuminanceP95") >= 0.20
            ):
                raise RuntimeError("DIAGNOSTIC_BLOCKED closeup pursuer metric failed")
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in hazards.values()):
        raise RuntimeError("DIAGNOSTIC_BLOCKED ordinary hazard totals invalid")
    if any(counts[profile]["pursuer"] != 0 for profile in ordinary) or counts["closeup"]["pursuer"] <= 0:
        raise RuntimeError("DIAGNOSTIC_BLOCKED pursuer lifecycle pixel counts invalid")


def validate_evaluator_artifacts(
    evaluation: Any,
    manifest: Any,
    preflight_path: Path,
    preflight: dict[str, Any],
    root: Path,
    hashes: dict[str, str | None],
) -> None:
    manifest_keys = [
        "schemaId", "schemaVersion", "diagnosticId", "preflightSha256", "constructionHash",
        "cameraBindingSha256", "renderOrderSha256", "sceneMetricsSha256", "outputs",
        "manifestHash", "verdict",
    ]
    evaluation_keys = [
        "schemaId", "schemaVersion", "diagnosticId", "preflightSha256", "manifestHash",
        "cameraBindingSha256", "renderOrderSha256", "sceneMetricsSha256", "profileMetrics",
        "semanticPixelCounts", "hazardPixelTotalsOrdinary", "gates", "failures",
        "manualReviewRequired", "verdict",
    ]
    if not isinstance(manifest, dict) or sorted(manifest.keys()) != sorted(manifest_keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED manifest closed schema mismatch")
    if not isinstance(evaluation, dict) or sorted(evaluation.keys()) != sorted(evaluation_keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED evaluation closed schema mismatch")
    preflight_hash = sha256_file(preflight_path)
    if (
        manifest["schemaId"] != "tide-relay.temple-tr4.diagnostic-manifest"
        or isinstance(manifest["schemaVersion"], bool)
        or not isinstance(manifest["schemaVersion"], int)
        or manifest["schemaVersion"] != 1
        or manifest["diagnosticId"] != DIAGNOSTIC_ID
        or manifest["preflightSha256"] != preflight_hash
        or manifest["constructionHash"] != preflight["constructionHash"]
        or manifest["verdict"] != "READY_FOR_MANUAL_REVIEW"
    ):
        raise RuntimeError("DIAGNOSTIC_BLOCKED manifest identity/provenance mismatch")
    ancillary_keys = ("cameraBindingSha256", "renderOrderSha256", "sceneMetricsSha256")
    if any(manifest[key] != hashes[key] for key in ancillary_keys):
        raise RuntimeError("DIAGNOSTIC_BLOCKED manifest ancillary hash mismatch")
    manifest_core = {key: manifest[key] for key in manifest_keys if key not in ("manifestHash", "verdict")}
    if manifest["manifestHash"] != sha256_bytes(canonical_bytes(manifest_core)):
        raise RuntimeError("DIAGNOSTIC_BLOCKED manifestHash mismatch")
    output_keys = ["index", "profile", "pass", "relativePath", "sha256", "bytes", "width", "height", "bitDepth", "colorType"]
    records = manifest["outputs"]
    if not isinstance(records, list) or len(records) != 20:
        raise RuntimeError("DIAGNOSTIC_BLOCKED manifest output count mismatch")
    for expected, record in zip(preflight["outputs"], records):
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(output_keys):
            raise RuntimeError("DIAGNOSTIC_BLOCKED manifest output schema mismatch")
        path = root / expected["relativePath"]
        if (
            record["index"] != expected["index"]
            or record["profile"] != expected["profile"]
            or record["pass"] != expected["pass"]
            or record["relativePath"] != expected["relativePath"]
            or record["sha256"] != sha256_file(path)
            or record["bytes"] != path.stat().st_size
            or record["width"] != expected["width"]
            or record["height"] != expected["height"]
            or record["bitDepth"] != (16 if expected["pass"] == "linear-depth" else 8)
            or (
                record["colorType"] != 0
                if expected["pass"] in ("road-mask", "linear-depth")
                else record["colorType"] not in (2, 6)
            )
        ):
            raise RuntimeError("DIAGNOSTIC_BLOCKED manifest output provenance mismatch")
    if (
        evaluation["schemaId"] != "tide-relay.temple-tr4.diagnostic-evaluation"
        or isinstance(evaluation["schemaVersion"], bool)
        or not isinstance(evaluation["schemaVersion"], int)
        or evaluation["schemaVersion"] != 1
        or evaluation["diagnosticId"] != DIAGNOSTIC_ID
        or evaluation["preflightSha256"] != preflight_hash
        or evaluation["manifestHash"] != manifest["manifestHash"]
        or evaluation["manualReviewRequired"] is not True
        or evaluation["failures"] != []
        or evaluation["verdict"] != "READY_FOR_MANUAL_REVIEW"
        or any(evaluation[key] != hashes[key] for key in ancillary_keys)
    ):
        raise RuntimeError("DIAGNOSTIC_BLOCKED evaluation identity/provenance/verdict mismatch")
    validate_evaluation_metrics(evaluation)


def write_text_atomic(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def build_camera_probe_plan(repo_root: Path, scripts: dict[str, Path], hashes: dict[str, str]) -> dict[str, Any]:
    return {
        "schemaId": "tide-relay.temple-tr4.camera-probe-plan",
        "schemaVersion": 1,
        "probeId": "001",
        "blenderExecutable": str(BLENDER_EXECUTABLE),
        "blenderVersion": BLENDER_VERSION,
        "scripts": {
            "generator": {"path": str(scripts["generator"].resolve()), "sha256": hashes["generator"]},
            "runner": {"path": str(scripts["runner"].resolve()), "sha256": hashes["runner"]},
        },
        "cameras": build_cameras(),
        "matrixElement": [2, 1],
        "verdict": "READY_FOR_CAMERA_PROBE",
    }


def validate_camera_response(response: Any, plan: dict[str, Any]) -> list[float]:
    expected_top_keys = [
        "schemaId", "schemaVersion", "blenderVersion", "generatorSha256",
        "runnerSha256", "profiles", "renderCallCount", "verdict",
    ]
    if not isinstance(response, dict) or sorted(response.keys()) != sorted(expected_top_keys):
        raise RuntimeError("CAMERA_PROBE_BLOCKED response top-level key mismatch")
    if response["schemaId"] != "tide-relay.temple-tr4.camera-probe" or response["schemaVersion"] != 1:
        raise RuntimeError("CAMERA_PROBE_BLOCKED response schema mismatch")
    if response["blenderVersion"] != BLENDER_VERSION:
        raise RuntimeError("CAMERA_PROBE_BLOCKED Blender version mismatch")
    if response["generatorSha256"] != plan["scripts"]["generator"]["sha256"] or response["runnerSha256"] != plan["scripts"]["runner"]["sha256"]:
        raise RuntimeError("CAMERA_PROBE_BLOCKED response script hash mismatch")
    if response["renderCallCount"] != 0 or response["verdict"] != "READY_FOR_DIAGNOSTIC_003_CONTRACT":
        raise RuntimeError("CAMERA_PROBE_BLOCKED response verdict/render count mismatch")
    expected_profile_keys = [
        "profile", "resolution", "lensShiftY", "b0", "b1", "response",
        "solvedShift", "actual", "error", "matrix0", "matrix1", "matrixSolved",
    ]
    profiles = response["profiles"]
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise RuntimeError("CAMERA_PROBE_BLOCKED response profile count mismatch")
    expected_names = ["portrait", "desktop", "landscape", "closeup"]
    errors: list[float] = []
    for index, record in enumerate(profiles):
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(expected_profile_keys):
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED profile key mismatch: {index}")
        camera = plan["cameras"][index]
        if record["profile"] != expected_names[index] or record["resolution"] != camera["diagnosticResolution"] or record["lensShiftY"] != camera["lensShiftY"]:
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED frozen camera mismatch: {index}")
        scalar_names = ("lensShiftY", "b0", "b1", "response", "solvedShift", "actual", "error")
        if any(isinstance(record[name], bool) or not isinstance(record[name], (int, float)) or not math.isfinite(float(record[name])) for name in scalar_names):
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED non-finite scalar: {index}")
        for matrix_name in ("matrix0", "matrix1", "matrixSolved"):
            matrix = record[matrix_name]
            if not isinstance(matrix, list) or len(matrix) != 16 or any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in matrix):
                raise RuntimeError(f"CAMERA_PROBE_BLOCKED matrix mismatch: {index}.{matrix_name}")
        if abs(float(record["response"])) < 1.0e-9 or abs(float(record["error"])) > 1.0e-6:
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED response/error gate: {index}")
        errors.append(float(record["error"]))
    return errors


def probe_output_records(root: Path, names: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name in names:
        path = root / name
        if path.is_file():
            records.append({"relativePath": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return records


def assert_no_probe_render_outputs(root: Path) -> None:
    forbidden = {".png", ".exr", ".jpg", ".jpeg", ".glb", ".gltf"}
    escaped = [path.name for path in root.rglob("*") if path.is_file() and path.suffix.lower() in forbidden]
    if escaped:
        raise RuntimeError(f"CAMERA_PROBE_BLOCKED forbidden render/export outputs: {escaped}")


def run_camera_probe() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    expected_repo = Path(r"E:\Proj\Game-1-temple").resolve(strict=True)
    if repo_root != expected_repo:
        raise PrecheckBlocked(f"repository root mismatch: {repo_root}")
    root = (repo_root / CAMERA_PROBE_RELATIVE).resolve(strict=False)
    assert_contained(root, repo_root)
    if root.exists():
        raise PrecheckBlocked(f"camera probe root must not pre-exist: {root}")
    if not root.parent.is_dir() or not os.access(root.parent, os.W_OK):
        raise PrecheckBlocked(f"camera probe parent is unavailable: {root.parent}")
    if not BLENDER_EXECUTABLE.is_file():
        raise PrecheckBlocked(f"Blender executable missing: {BLENDER_EXECUTABLE}")
    reject_reparse(BLENDER_EXECUTABLE)
    scripts, hashes = verify_probe_scripts(repo_root)
    plan = build_camera_probe_plan(repo_root, scripts, hashes)
    validate_finite(plan)
    normalized = json.loads(canonical_bytes(plan).decode("utf-8"))
    expected = json.loads(canonical_bytes(build_camera_probe_plan(repo_root, scripts, hashes)).decode("utf-8"))
    deep_compare(expected, normalized)
    if [camera["profile"] for camera in plan["cameras"]] != ["portrait", "desktop", "landscape", "closeup"]:
        raise PrecheckBlocked("camera probe profile order mismatch")
    scripts_second, hashes_second = verify_probe_scripts(repo_root)
    if scripts_second != scripts or hashes_second != hashes:
        raise PrecheckBlocked("camera probe scripts changed during preflight")

    root.mkdir(mode=0o755)
    plan_path = root / "probe-plan.json"
    atomic_write_json(plan_path, plan)
    command = [
        str(BLENDER_EXECUTABLE), "--background", "--factory-startup",
        "--python-exit-code", "1", "--python", str(scripts["generator"]), "--",
        "--camera-probe", "--probe-plan", str(plan_path), "--output", str(root),
    ]
    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    log_path = root / "blender.log"
    write_text_atomic(log_path, completed.stdout + "\n--- STDERR ---\n" + completed.stderr)
    response_path = root / "camera-response.json"
    errors: list[float] = []
    verdict = "CAMERA_PROBE_BLOCKED"
    reason: str | None = None
    try:
        assert_no_probe_render_outputs(root)
        allowed_before_status = {"probe-plan.json", "blender.log", "camera-response.json"}
        actual_files = {path.name for path in root.iterdir() if path.is_file()}
        if not actual_files.issubset(allowed_before_status):
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED unexpected files: {sorted(actual_files - allowed_before_status)}")
        if completed.returncode != 0:
            raise RuntimeError(f"CAMERA_PROBE_BLOCKED Blender exited {completed.returncode}")
        if not response_path.is_file():
            raise RuntimeError("CAMERA_PROBE_BLOCKED missing camera-response.json")
        response = json.loads(response_path.read_text(encoding="utf-8"))
        errors = validate_camera_response(response, plan)
        verdict = response["verdict"]
    except Exception as exc:
        reason = str(exc)
    outputs = probe_output_records(root, ["probe-plan.json", "blender.log", "camera-response.json"])
    status = {
        "schemaId": "tide-relay.temple-tr4.camera-probe-status",
        "schemaVersion": 1,
        "probeId": "001",
        "processReturnCode": completed.returncode,
        "responseErrors": errors,
        "outputs": outputs,
        "renderCallCount": 0,
        "reason": reason,
        "verdict": verdict,
    }
    atomic_write_json(root / "probe-status.json", status)
    if verdict != "READY_FOR_DIAGNOSTIC_003_CONTRACT":
        raise RuntimeError(reason or "CAMERA_PROBE_BLOCKED")
    print(json.dumps({"verdict": verdict, "cameraProbeRoot": str(root), "errors": errors}, ensure_ascii=False))
    return 0


def build_matrix_probe_cameras() -> list[dict[str, Any]]:
    return [
        {
            "profile": camera["profile"],
            "diagnosticResolution": camera["diagnosticResolution"],
            "position": camera["position"],
            "target": camera["target"],
            "verticalFovDegrees": camera["verticalFovDegrees"],
            "near": camera["near"],
            "far": camera["far"],
        }
        for camera in build_cameras()
    ]


def verify_matrix_probe_authorization(repo_root: Path) -> None:
    authorization = (repo_root / "docs/workstreams/temple-tr4-coordination/MATRIX_PROBE_001_AUTHORIZATION.md").read_text(encoding="utf-8")
    coordination_log = (repo_root / "docs/workstreams/temple-tr4-coordination/THREAD_LOG.md").read_text(encoding="utf-8")
    if "Status: **AUTHORIZED.**" not in authorization or "READY_FOR_MATRIX_PROBE_001_CONTRACT" not in authorization:
        raise PrecheckBlocked("matrix probe authorization is not independently ready and authorized")
    if "REPORT TEMPLE-TR4-MATRIX-PROBE-001 AUTHORIZED" not in coordination_log:
        raise PrecheckBlocked("coordinator matrix probe status is not AUTHORIZED")


def verify_matrix_probe_scripts(repo_root: Path) -> tuple[dict[str, Path], dict[str, str]]:
    scripts_dir = repo_root / "tools" / "temple-asset-pipeline"
    scripts = {
        "generator": scripts_dir / "generate_tide_scar_tr4_pack.py",
        "runner": scripts_dir / "run_tide_scar_tr4_pack.py",
    }
    hashes: dict[str, str] = {}
    for name, path in scripts.items():
        assert_contained(path, repo_root)
        if not path.is_file():
            raise PrecheckBlocked(f"missing matrix-probe script: {path}")
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            raise PrecheckBlocked(f"matrix-probe AST failure: {path}: {exc}") from exc
        hashes[name] = sha256_file(path)
    return scripts, hashes


def verify_matrix_probe_evidence(repo_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, (relative_path, expected_hash) in FROZEN_MATRIX_PROBE_EVIDENCE.items():
        path = repo_root / relative_path
        assert_contained(path, repo_root)
        if not path.is_file():
            raise PrecheckBlocked(f"frozen matrix-probe evidence missing: {relative_path}")
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise PrecheckBlocked(f"frozen matrix-probe evidence changed: {relative_path}")
        result[name] = actual_hash
    return result


def build_matrix_probe_plan(
    repo_root: Path,
    blender_hash: str,
    scripts: dict[str, Path],
    script_hashes: dict[str, str],
    evidence_hashes: dict[str, str],
) -> dict[str, Any]:
    return {
        "schemaId": "tide-relay.temple-tr4.matrix-probe-plan",
        "schemaVersion": 1,
        "probeId": "001",
        "repoRoot": str(repo_root),
        "blenderExecutable": str(BLENDER_EXECUTABLE),
        "blenderExecutableSha256": blender_hash,
        "expectedBlenderVersion": BLENDER_VERSION,
        "scripts": {
            "generator": {"path": str(scripts["generator"].resolve()), "sha256": script_hashes["generator"]},
            "runner": {"path": str(scripts["runner"].resolve()), "sha256": script_hashes["runner"]},
        },
        "frozenEvidence": evidence_hashes,
        "cameras": build_matrix_probe_cameras(),
        "verdict": "READY_FOR_MATRIX_PROBE",
    }


def prepare_matrix_probe() -> tuple[Path, Path, dict[str, Path], dict[str, str], str, dict[str, str], dict[str, Any]]:
    repo_root = Path(__file__).resolve().parents[2]
    expected_repo = Path(r"E:\Proj\Game-1-temple").resolve(strict=True)
    if repo_root != expected_repo:
        raise PrecheckBlocked(f"repository root mismatch: {repo_root}")
    root = (repo_root / MATRIX_PROBE_RELATIVE).resolve(strict=False)
    assert_contained(root, repo_root)
    if root.exists():
        raise PrecheckBlocked(f"matrix probe root must not pre-exist: {root}")
    if (repo_root / "docs/workstreams/temple-tr4-asset/diagnostic-003").exists():
        raise PrecheckBlocked("diagnostic-003 is unauthorized and must not exist")
    if not root.parent.is_dir() or not os.access(root.parent, os.W_OK):
        raise PrecheckBlocked(f"matrix probe parent is unavailable: {root.parent}")
    verify_matrix_probe_authorization(repo_root)
    if not BLENDER_EXECUTABLE.is_file():
        raise PrecheckBlocked(f"Blender executable missing: {BLENDER_EXECUTABLE}")
    reject_reparse(BLENDER_EXECUTABLE)
    blender_hash = sha256_file(BLENDER_EXECUTABLE)
    scripts, script_hashes = verify_matrix_probe_scripts(repo_root)
    evidence_hashes = verify_matrix_probe_evidence(repo_root)
    plan = build_matrix_probe_plan(repo_root, blender_hash, scripts, script_hashes, evidence_hashes)
    validate_finite(plan)
    normalized = json.loads(canonical_bytes(plan).decode("utf-8"))
    expected = json.loads(canonical_bytes(build_matrix_probe_plan(repo_root, blender_hash, scripts, script_hashes, evidence_hashes)).decode("utf-8"))
    deep_compare(expected, normalized)
    if [camera["profile"] for camera in plan["cameras"]] != ["portrait", "desktop", "landscape", "closeup"]:
        raise PrecheckBlocked("matrix probe camera order mismatch")
    for camera in plan["cameras"]:
        if sorted(camera.keys()) != sorted(["profile", "diagnosticResolution", "position", "target", "verticalFovDegrees", "near", "far"]):
            raise PrecheckBlocked(f"matrix probe camera schema mismatch: {camera.get('profile')}")
        resolution = camera["diagnosticResolution"]
        if not isinstance(resolution, list) or len(resolution) != 2 or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in resolution):
            raise PrecheckBlocked(f"matrix probe resolution mismatch: {camera['profile']}")
    return repo_root, root, scripts, script_hashes, blender_hash, evidence_hashes, plan


def matrix_significant_elements(difference: list[float]) -> list[dict[str, Any]]:
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


def derive_matrix_binding(profiles: list[dict[str, Any]]) -> dict[str, Any] | None:
    responses: list[dict[str, Any]] = []
    for record in profiles:
        if any(abs(float(record[name]) - target) > 1.0e-8 for name, target in (("originalShift0", 0.0), ("evaluatedShift0", 0.0), ("originalShift1", 1.0), ("evaluatedShift1", 1.0))):
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


def validate_matrix_response(response: Any, plan: dict[str, Any]) -> dict[str, Any] | None:
    top_keys = ["schemaId", "schemaVersion", "probeId", "blenderVersion", "generatorSha256", "runnerSha256", "profiles", "consistentBinding", "renderCallCount", "verdict"]
    if not isinstance(response, dict) or sorted(response.keys()) != sorted(top_keys):
        raise RuntimeError("MATRIX_PROBE_BLOCKED response top-level schema mismatch")
    if response["schemaId"] != "tide-relay.temple-tr4.matrix-probe" or response["schemaVersion"] != 1 or response["probeId"] != "001":
        raise RuntimeError("MATRIX_PROBE_BLOCKED response identity mismatch")
    if response["blenderVersion"] != BLENDER_VERSION or response["generatorSha256"] != plan["scripts"]["generator"]["sha256"] or response["runnerSha256"] != plan["scripts"]["runner"]["sha256"]:
        raise RuntimeError("MATRIX_PROBE_BLOCKED response provenance mismatch")
    if response["renderCallCount"] != 0:
        raise RuntimeError("MATRIX_PROBE_BLOCKED nonzero render count")
    profile_keys = ["profile", "resolution", "originalShift0", "evaluatedShift0", "originalShift1", "evaluatedShift1", "matrix0", "matrix1", "difference", "significantElements"]
    profiles = response["profiles"]
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise RuntimeError("MATRIX_PROBE_BLOCKED profile count mismatch")
    for index, record in enumerate(profiles):
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(profile_keys):
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED profile schema mismatch: {index}")
        camera = plan["cameras"][index]
        if record["profile"] != camera["profile"] or record["resolution"] != camera["diagnosticResolution"]:
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED profile identity mismatch: {index}")
        for shift_name in ("originalShift0", "evaluatedShift0", "originalShift1", "evaluatedShift1"):
            value = record[shift_name]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise RuntimeError(f"MATRIX_PROBE_BLOCKED shift mismatch: {index}.{shift_name}")
        matrices = []
        for matrix_name in ("matrix0", "matrix1", "difference"):
            matrix = record[matrix_name]
            if not isinstance(matrix, list) or len(matrix) != 16 or any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in matrix):
                raise RuntimeError(f"MATRIX_PROBE_BLOCKED matrix mismatch: {index}.{matrix_name}")
            matrices.append([float(value) for value in matrix])
        matrix0, matrix1, difference = matrices
        for matrix_index in range(16):
            if abs(difference[matrix_index] - (matrix1[matrix_index] - matrix0[matrix_index])) > 1.0e-12:
                raise RuntimeError(f"MATRIX_PROBE_BLOCKED difference mismatch: {index}.{matrix_index}")
        expected_significant = matrix_significant_elements(difference)
        actual_significant = record["significantElements"]
        if not isinstance(actual_significant, list) or len(actual_significant) != len(expected_significant):
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED significant count mismatch: {index}")
        significant_keys = ["row", "column", "rowMajorIndex", "webglColumnMajorIndex", "delta"]
        for expected_element, actual_element in zip(expected_significant, actual_significant):
            if not isinstance(actual_element, dict) or sorted(actual_element.keys()) != sorted(significant_keys):
                raise RuntimeError(f"MATRIX_PROBE_BLOCKED significant schema mismatch: {index}")
            for key in ("row", "column", "rowMajorIndex", "webglColumnMajorIndex"):
                if actual_element[key] != expected_element[key]:
                    raise RuntimeError(f"MATRIX_PROBE_BLOCKED significant index mismatch: {index}.{key}")
            if not isinstance(actual_element["delta"], (int, float)) or isinstance(actual_element["delta"], bool) or not math.isfinite(float(actual_element["delta"])) or abs(float(actual_element["delta"]) - float(expected_element["delta"])) > 1.0e-12:
                raise RuntimeError(f"MATRIX_PROBE_BLOCKED significant delta mismatch: {index}")
    derived = derive_matrix_binding(profiles)
    if response["consistentBinding"] != derived:
        raise RuntimeError("MATRIX_PROBE_BLOCKED consistent binding mismatch")
    expected_verdict = "READY_FOR_CAMERA_BINDING_CONTRACT" if derived is not None else "MATRIX_PROBE_BLOCKED"
    if response["verdict"] != expected_verdict:
        raise RuntimeError("MATRIX_PROBE_BLOCKED response verdict mismatch")
    return derived


def matrix_probe_output_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name in ("matrix-probe-plan.json", "matrix-response.json", "blender.log"):
        path = root / name
        if path.is_file():
            records.append({"relativePath": name, "byteCount": path.stat().st_size, "sha256": sha256_file(path)})
    return records


def run_matrix_probe() -> int:
    repo_root, root, scripts, script_hashes, blender_hash, evidence_hashes, plan = prepare_matrix_probe()
    # Re-read every drift-prone byte immediately before creating the root and sole process.
    scripts_second, hashes_second = verify_matrix_probe_scripts(repo_root)
    evidence_second = verify_matrix_probe_evidence(repo_root)
    blender_hash_second = sha256_file(BLENDER_EXECUTABLE)
    if scripts_second != scripts or hashes_second != script_hashes or evidence_second != evidence_hashes or blender_hash_second != blender_hash:
        raise PrecheckBlocked("matrix probe inputs changed during preflight")
    root.mkdir(mode=0o755)
    plan_path = root / "matrix-probe-plan.json"
    atomic_write_json(plan_path, plan)
    command = [
        str(BLENDER_EXECUTABLE), "--background", "--factory-startup",
        "--python-exit-code", "1", "--python", str(scripts["generator"]), "--",
        "--matrix-probe", "--matrix-probe-plan", str(plan_path), "--output", str(root),
    ]
    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    write_text_atomic(root / "blender.log", completed.stdout + "\n--- STDERR ---\n" + completed.stderr)
    allowed_before_status = {"matrix-probe-plan.json", "matrix-response.json", "blender.log"}
    actual_files = {path.name for path in root.iterdir() if path.is_file()}
    forbidden_suffixes = {".png", ".exr", ".jpg", ".jpeg", ".blend", ".glb", ".gltf", ".ktx", ".ktx2", ".dds", ".tga", ".tiff"}
    forbidden_files = [path.name for path in root.rglob("*") if path.is_file() and path.suffix.lower() in forbidden_suffixes]
    consistent_binding: dict[str, Any] | None = None
    reason: str | None = None
    verdict = "MATRIX_PROBE_BLOCKED"
    try:
        if not actual_files.issubset(allowed_before_status):
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED unexpected files: {sorted(actual_files - allowed_before_status)}")
        if forbidden_files:
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED forbidden outputs: {forbidden_files}")
        if completed.returncode != 0:
            raise RuntimeError(f"MATRIX_PROBE_BLOCKED Blender exited {completed.returncode}")
        response_path = root / "matrix-response.json"
        if not response_path.is_file():
            raise RuntimeError("MATRIX_PROBE_BLOCKED missing matrix-response.json")
        response = json.loads(response_path.read_text(encoding="utf-8"))
        consistent_binding = validate_matrix_response(response, plan)
        verdict = response["verdict"]
        if verdict != "READY_FOR_CAMERA_BINDING_CONTRACT":
            reason = "observed matrix mapping did not satisfy the frozen consistent-binding gate"
    except Exception as exc:
        reason = str(exc)
        verdict = "MATRIX_PROBE_BLOCKED"
        consistent_binding = None
    status = {
        "schemaId": "tide-relay.temple-tr4.matrix-probe-status",
        "schemaVersion": 1,
        "probeId": "001",
        "processReturnCode": completed.returncode,
        "outputs": matrix_probe_output_records(root),
        "consistentBinding": consistent_binding,
        "renderCallCount": 0,
        "reason": reason,
        "verdict": verdict,
    }
    atomic_write_json(root / "matrix-probe-status.json", status)
    if verdict != "READY_FOR_CAMERA_BINDING_CONTRACT":
        raise RuntimeError(reason or "MATRIX_PROBE_BLOCKED")
    print(json.dumps({"verdict": verdict, "matrixProbeRoot": str(root), "consistentBinding": consistent_binding}, ensure_ascii=False))
    return 0


def prepare_diagnostic() -> tuple[Path, Path, dict[str, Path], dict[str, str], dict[str, str], str, dict[str, Any]]:
    repo_root = Path(__file__).resolve().parents[2]
    expected_repo = Path(r"E:\Proj\Game-1-temple").resolve(strict=True)
    if repo_root != expected_repo:
        raise PrecheckBlocked(f"repository root mismatch: {repo_root}")
    if platform.python_version() != PYTHON_VERSION:
        raise PrecheckBlocked(
            f"Python version mismatch: expected {PYTHON_VERSION}, observed {platform.python_version()}"
        )
    diagnostic_root = (repo_root / DIAGNOSTIC_RELATIVE).resolve(strict=False)
    assert_contained(diagnostic_root, repo_root)
    if diagnostic_root.exists():
        raise PrecheckBlocked(f"diagnostic root must not pre-exist: {diagnostic_root}")
    if not diagnostic_root.parent.exists() or not diagnostic_root.parent.is_dir():
        raise PrecheckBlocked(f"diagnostic parent missing: {diagnostic_root.parent}")
    if not os.access(diagnostic_root.parent, os.W_OK):
        raise PrecheckBlocked(f"diagnostic parent not writable: {diagnostic_root.parent}")
    verify_c6_authorization(repo_root)
    blender_hash = verify_blender_executable()
    frozen_evidence = verify_c6_frozen_evidence(repo_root)
    scripts, script_hashes = verify_scripts(repo_root)
    verify_reference()
    authored_preflight = build_preflight(repo_root, script_hashes)
    validate_finite(authored_preflight)
    canonical_preflight_bytes = canonical_bytes(authored_preflight)
    preflight = json.loads(canonical_preflight_bytes.decode("utf-8"))
    validate_finite(preflight)
    validate_c6_preflight_contract(preflight)
    if canonical_bytes(preflight) != canonical_preflight_bytes:
        raise PrecheckBlocked("C6 canonical preflight round-trip mismatch")
    normalized = preflight
    expected_normalized = json.loads(canonical_bytes(build_preflight(repo_root, script_hashes)).decode("utf-8"))
    deep_compare(expected_normalized, normalized)
    preflight_keys = [
        "schemaId", "schemaVersion", "contractVersion", "seed", "reference", "tools",
        "scripts", "scene", "cameras", "construction", "collision", "materials",
        "semanticRoots", "budgets", "outputs", "constructionHash", "verdict",
    ]
    if sorted(preflight.keys()) != sorted(preflight_keys):
        raise PrecheckBlocked("C6 preflight top-level schema mismatch")
    if preflight["schemaId"] != SCHEMA_ID or preflight["schemaVersion"] != 6 or preflight["contractVersion"] != "TEMPLE-TR4-C6":
        raise PrecheckBlocked("C6 preflight identity mismatch")
    if preflight["constructionHash"] != sha256_bytes(canonical_bytes(preflight["construction"])):
        raise PrecheckBlocked("construction hash mismatch")
    if preflight["constructionHash"] != CONSTRUCTION_SHA256:
        raise PrecheckBlocked("frozen construction hash mismatch")
    if preflight["verdict"] != "READY_FOR_BLENDER":
        raise PrecheckBlocked("preflight verdict is not READY_FOR_BLENDER")
    if len(preflight["outputs"]) != 20 or [item["index"] for item in preflight["outputs"]] != list(range(20)):
        raise PrecheckBlocked("closed output array mismatch")
    expected_output_tuples = []
    for profile, scene_id, width, height in (
        ("portrait", "tr4-diagnostic-running-001", 270, 480),
        ("desktop", "tr4-diagnostic-running-001", 480, 270),
        ("landscape", "tr4-diagnostic-running-001", 422, 195),
        ("closeup", "tr4-diagnostic-game-over-001", 320, 240),
    ):
        for pass_name in ("beauty", "object-id", "road-mask", "normal", "linear-depth"):
            expected_output_tuples.append(
                (profile, pass_name, scene_id, f"tr4-diagnostic-006-{profile}-{pass_name}.png", width, height)
            )
    actual_output_tuples = [
        (item["profile"], item["pass"], item["sceneId"], item["relativePath"], item["width"], item["height"])
        for item in preflight["outputs"]
    ]
    output_keys = ["index", "profile", "pass", "sceneId", "relativePath", "width", "height"]
    if any(not isinstance(item, dict) or sorted(item.keys()) != sorted(output_keys) for item in preflight["outputs"]):
        raise PrecheckBlocked("C6 output record schema mismatch")
    if actual_output_tuples != expected_output_tuples:
        raise PrecheckBlocked("C6 output profile/pass/scene/name/dimension ordering mismatch")
    if len({item["relativePath"] for item in preflight["outputs"]}) != 20:
        raise PrecheckBlocked("duplicate output path")
    if (
        len(frozen_evidence) != 51
        or sum("diagnostic004" in name for name in frozen_evidence) != 27
        or sum("diagnostic005" in name for name in frozen_evidence) != 4
    ):
        raise PrecheckBlocked("C6 frozen evidence closure is not 20 historical plus 27 C4 plus 4 C5 files")
    for item in preflight["outputs"]:
        output_path = diagnostic_root / item["relativePath"]
        assert_contained(output_path, repo_root)
        if output_path.parent != diagnostic_root:
            raise PrecheckBlocked(f"nested/traversal output rejected: {item['relativePath']}")

    # Recheck every drift-prone byte without starting Blender or a version subprocess.
    scripts_second, hashes_second = verify_scripts(repo_root)
    verify_reference()
    verify_c6_authorization(repo_root)
    if (
        scripts_second != scripts
        or hashes_second != script_hashes
        or verify_c6_frozen_evidence(repo_root) != frozen_evidence
        or verify_blender_executable() != blender_hash
    ):
        raise PrecheckBlocked("diagnostic inputs changed during preflight")
    return repo_root, diagnostic_root, scripts, script_hashes, frozen_evidence, blender_hash, preflight


def diagnostic_status(
    stage: str,
    blender_return_code: int | None,
    evaluator_return_code: int | None,
    hashes: dict[str, str | None],
    reason: str | None,
    verdict: str,
) -> dict[str, Any]:
    if stage not in ("blender", "render-set", "evaluator", "complete"):
        raise RuntimeError(f"invalid diagnostic status stage: {stage}")
    return {
        "schemaId": "tide-relay.temple-tr4.diagnostic-status",
        "schemaVersion": 1,
        "diagnosticId": DIAGNOSTIC_ID,
        "stage": stage,
        "blenderReturnCode": blender_return_code,
        "evaluatorReturnCode": evaluator_return_code,
        "cameraBindingSha256": hashes.get("cameraBindingSha256"),
        "renderOrderSha256": hashes.get("renderOrderSha256"),
        "sceneMetricsSha256": hashes.get("sceneMetricsSha256"),
        "evaluationSha256": hashes.get("evaluationSha256"),
        "manifestSha256": hashes.get("manifestSha256"),
        "reason": reason,
        "verdict": verdict,
    }


def run(*, dry_preflight: bool = False) -> int:
    repo_root, diagnostic_root, scripts, script_hashes, frozen_evidence, blender_hash, preflight = prepare_diagnostic()
    if dry_preflight:
        if diagnostic_root.exists():
            raise PrecheckBlocked("dry preflight created the diagnostic root")
        print("READY_FOR_BLENDER")
        return 0

    diagnostic_root.mkdir(mode=0o755)
    preflight_path = diagnostic_root / "preflight.json"
    planned_path = diagnostic_root / "planned-manifest.json"
    hashes: dict[str, str | None] = {
        "cameraBindingSha256": None,
        "renderOrderSha256": None,
        "sceneMetricsSha256": None,
        "evaluationSha256": None,
        "manifestSha256": None,
    }
    blender_return_code: int | None = None
    evaluator_return_code: int | None = None
    stage = "blender"
    try:
        atomic_write_json(preflight_path, preflight)
        planned = {
            "schemaId": "tide-relay.temple-tr4.diagnostic-plan",
            "schemaVersion": 1,
            "diagnosticId": DIAGNOSTIC_ID,
            "preflightSha256": sha256_file(preflight_path),
            "constructionHash": preflight["constructionHash"],
            "outputs": preflight["outputs"],
            "verdict": "READY_FOR_BLENDER",
        }
        atomic_write_json(planned_path, planned)
        command = [
            str(BLENDER_EXECUTABLE), "--background", "--factory-startup",
            "--python-exit-code", "1", "--python", str(scripts["generator"]), "--",
            "--preflight", str(preflight_path), "--output", str(diagnostic_root),
        ]
        try:
            completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            blender_return_code = completed.returncode
            blender_log = completed.stdout + "\n--- STDERR ---\n" + completed.stderr
        except Exception as exc:
            blender_log = f"Blender process launch failed: {exc}\n"
            write_text_atomic(diagnostic_root / "blender.log", blender_log)
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED Blender process launch failed: {exc}") from exc
        write_text_atomic(diagnostic_root / "blender.log", blender_log)
        if blender_return_code != 0:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED Blender exited {blender_return_code}")

        stage = "render-set"
        hashes["cameraBindingSha256"] = validate_camera_binding(diagnostic_root / "camera-binding.json", preflight)
        hashes["renderOrderSha256"] = validate_render_order(diagnostic_root / "render-order.json", preflight["outputs"])
        hashes["sceneMetricsSha256"] = validate_scene_metrics(diagnostic_root / "scene-metrics.json", preflight)
        verify_render_set(diagnostic_root, preflight["outputs"])
        before_evaluator = {
            "preflight.json", "planned-manifest.json", "camera-binding.json",
            "render-order.json", "scene-metrics.json", "blender.log",
            *[record["relativePath"] for record in preflight["outputs"]],
        }
        assert_exact_files(diagnostic_root, before_evaluator)

        stage = "evaluator"
        evaluator_command = [
            sys.executable, str(scripts["evaluator"]),
            "--preflight", str(preflight_path), "--diagnostic-root", str(diagnostic_root),
        ]
        evaluated = subprocess.run(evaluator_command, cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        evaluator_return_code = evaluated.returncode
        write_text_atomic(diagnostic_root / "evaluator.log", evaluated.stdout + "\n--- STDERR ---\n" + evaluated.stderr)
        evaluation_path = diagnostic_root / "evaluation.json"
        manifest_path = diagnostic_root / "manifest.json"
        if evaluation_path.is_file():
            hashes["evaluationSha256"] = sha256_file(evaluation_path)
        if manifest_path.is_file():
            hashes["manifestSha256"] = sha256_file(manifest_path)
        if evaluator_return_code != 0:
            raise RuntimeError(f"DIAGNOSTIC_BLOCKED evaluator exited {evaluator_return_code}")
        if not evaluation_path.is_file() or not manifest_path.is_file():
            raise RuntimeError("DIAGNOSTIC_BLOCKED evaluator omitted required JSON")
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_evaluator_artifacts(evaluation, manifest, preflight_path, preflight, diagnostic_root, hashes)
        final_before_status = before_evaluator | {"evaluator.log", "evaluation.json", "manifest.json"}
        assert_exact_files(diagnostic_root, final_before_status)
        scripts_after, hashes_after = verify_scripts(repo_root)
        verify_reference()
        verify_c6_authorization(repo_root)
        if (
            scripts_after != scripts
            or hashes_after != script_hashes
            or verify_c6_frozen_evidence(repo_root) != frozen_evidence
            or verify_blender_executable() != blender_hash
        ):
            raise RuntimeError("DIAGNOSTIC_BLOCKED launch provenance changed during the process")

        stage = "complete"
        status = diagnostic_status(stage, blender_return_code, evaluator_return_code, hashes, None, "READY_FOR_MANUAL_REVIEW")
        atomic_write_json(diagnostic_root / "diagnostic-status.json", status)
        assert_exact_files(diagnostic_root, final_before_status | {"diagnostic-status.json"})
        print(json.dumps({"verdict": "READY_FOR_MANUAL_REVIEW", "diagnosticRoot": str(diagnostic_root)}, ensure_ascii=False))
        return 0
    except Exception as exc:
        reason = str(exc)
        available_hash_paths = {
            "cameraBindingSha256": diagnostic_root / "camera-binding.json",
            "renderOrderSha256": diagnostic_root / "render-order.json",
            "sceneMetricsSha256": diagnostic_root / "scene-metrics.json",
            "evaluationSha256": diagnostic_root / "evaluation.json",
            "manifestSha256": diagnostic_root / "manifest.json",
        }
        for hash_name, path in available_hash_paths.items():
            if hashes[hash_name] is None and path.is_file():
                hashes[hash_name] = sha256_file(path)
        try:
            scripts_after, hashes_after = verify_scripts(repo_root)
            verify_reference()
            verify_c6_authorization(repo_root)
            if (
                scripts_after != scripts
                or hashes_after != script_hashes
                or verify_c6_frozen_evidence(repo_root) != frozen_evidence
                or verify_blender_executable() != blender_hash
            ):
                raise RuntimeError("post-process provenance or frozen evidence changed")
        except Exception as provenance_exc:
            reason = f"{reason}; DIAGNOSTIC_BLOCKED post-process provenance check failed: {provenance_exc}"
        allowed_failure = {
            "preflight.json", "planned-manifest.json", "camera-binding.json", "render-order.json",
            "scene-metrics.json", "blender.log", "evaluator.log", "evaluation.json", "manifest.json",
            *[record["relativePath"] for record in preflight["outputs"]],
        }
        try:
            assert_exact_files(diagnostic_root, allowed_failure, subset=True)
        except Exception as allowlist_exc:
            reason = f"{reason}; {allowlist_exc}"
        atomic_write_json(
            diagnostic_root / "diagnostic-status.json",
            diagnostic_status(stage, blender_return_code, evaluator_return_code, hashes, reason, "DIAGNOSTIC_BLOCKED"),
        )
        raise RuntimeError(reason) from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    probe_group = parser.add_mutually_exclusive_group()
    probe_group.add_argument("--camera-probe", action="store_true")
    probe_group.add_argument("--matrix-probe", action="store_true")
    probe_group.add_argument("--dry-preflight", action="store_true")
    arguments = parser.parse_args()
    blocked_verdict = "MATRIX_PROBE_BLOCKED" if arguments.matrix_probe else "CAMERA_PROBE_BLOCKED" if arguments.camera_probe else "PRECHECK_BLOCKED"
    try:
        if arguments.matrix_probe:
            return run_matrix_probe()
        if arguments.camera_probe:
            return run_camera_probe()
        return run(dry_preflight=arguments.dry_preflight)
    except PrecheckBlocked as exc:
        print(json.dumps({"verdict": blocked_verdict, "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as exc:  # fail closed after the diagnostic root exists
        verdict = "MATRIX_PROBE_BLOCKED" if arguments.matrix_probe else "CAMERA_PROBE_BLOCKED" if arguments.camera_probe else "DIAGNOSTIC_BLOCKED"
        print(json.dumps({"verdict": verdict, "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
