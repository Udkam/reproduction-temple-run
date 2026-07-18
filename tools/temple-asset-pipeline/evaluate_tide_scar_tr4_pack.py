"""Pure-Python evaluator for the sole TEMPLE-TR4 diagnostic batch.

The evaluator has no Pillow or Blender dependency.  It decodes Blender PNGs with the
standard library, proves the exact ordered set, validates binary/semantic passes, runs
readability gates, and writes a hash-bound manifest.  Numeric success can issue only
READY_FOR_MANUAL_REVIEW.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import struct
import sys
import zlib
from pathlib import Path
from typing import Any, Iterable


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PALETTE = {
    "background": (0x00, 0x00, 0x00),
    "road": (0xD9, 0xB9, 0x8C),
    "canyon": (0x1B, 0x29, 0x35),
    "runner": (0xF2, 0xEA, 0xD7),
    "pursuer": (0x10, 0x18, 0x20),
    "beam": (0xB4, 0x4A, 0x38),
    "ring": (0xE6, 0x96, 0x48),
    "column": (0x6D, 0x48, 0x34),
    "gap-lips": (0x7A, 0x22, 0x21),
    "tide-scar": (0xFF, 0xFF, 0xFF),
}
DIAGNOSTIC_ID = "007"
PYTHON_VERSION = "3.12.0"
C7_CONSTRUCTION_SHA256 = "6a9735277c29ec32b3e22432b240385bc33993325aaf3422c60ac4f82e0dbd45"
PROFILE_ORDER = ["portrait", "desktop", "landscape", "closeup"]
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
    "foregroundDepthP10", "foregroundDepthP50", "foregroundDepthP90",
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
    "roadNormalUp", "depthBackgroundSeparation", "foregroundDepthQuantiles",
    "representativeDepthOrder",
]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def deep_compare(expected: Any, actual: Any, path: str = "$") -> None:
    if type(expected) is not type(actual):
        raise ValueError(f"type mismatch at {path}")
    if isinstance(expected, dict):
        if sorted(expected.keys()) != sorted(actual.keys()):
            raise ValueError(f"unknown or missing keys at {path}")
        for key in expected:
            deep_compare(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError(f"array length mismatch at {path}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            deep_compare(left, right, f"{path}[{index}]")
    elif expected != actual:
        raise ValueError(f"frozen value mismatch at {path}")


def strict_json_object_bytes(data: bytes, label: str) -> dict[str, Any]:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key in {label}: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {label}")
    if canonical_bytes(value) != data:
        raise ValueError(f"JSON is not exact canonical bytes: {label}")
    return value


def validate_planned_manifest(
    path: Path,
    preflight: dict[str, Any],
    preflight_bytes: bytes,
) -> str:
    if not path.is_file():
        raise ValueError("missing planned-manifest.json")
    preflight_sha256 = hashlib.sha256(preflight_bytes).hexdigest()
    plan = strict_json_object_bytes(path.read_bytes(), "planned-manifest.json")
    keys = [
        "schemaId", "schemaVersion", "diagnosticId", "preflightSha256",
        "constructionHash", "outputs", "verdict",
    ]
    if sorted(plan.keys()) != sorted(keys):
        raise ValueError("planned-manifest.json closed key set mismatch")
    if (
        plan["schemaId"] != "tide-relay.temple-tr4.diagnostic-plan"
        or isinstance(plan["schemaVersion"], bool)
        or not isinstance(plan["schemaVersion"], int)
        or plan["schemaVersion"] != 1
        or plan["diagnosticId"] != DIAGNOSTIC_ID
        or plan["preflightSha256"] != preflight_sha256
        or plan["constructionHash"] != preflight["constructionHash"]
        or plan["verdict"] != "READY_FOR_BLENDER"
    ):
        raise ValueError("planned-manifest.json identity/provenance mismatch")
    deep_compare(preflight["outputs"], plan["outputs"], "$.plannedManifest.outputs")
    return preflight_sha256


def atomic_write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".tmp")
    data = canonical_bytes(value)
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def paeth(a: int, b: int, c: int) -> int:
    estimate = a + b - c
    distance_a = abs(estimate - a)
    distance_b = abs(estimate - b)
    distance_c = abs(estimate - c)
    if distance_a <= distance_b and distance_a <= distance_c:
        return a
    if distance_b <= distance_c:
        return b
    return c


def read_png(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"not PNG: {path}")
    offset = len(PNG_SIGNATURE)
    ihdr: tuple[int, int, int, int, int] | None = None
    compressed = bytearray()
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f"truncated PNG chunk: {path}")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        if payload_end + 4 > len(data):
            raise ValueError(f"truncated PNG payload: {path}")
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:payload_end + 4])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(payload, actual_crc) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise ValueError(f"PNG CRC mismatch: {path}")
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if compression != 0 or filtering != 0 or interlace != 0:
                raise ValueError(f"unsupported PNG encoding: {path}")
            ihdr = (width, height, bit_depth, color_type, interlace)
        elif chunk_type == b"IDAT":
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            break
        offset = payload_end + 4
    if ihdr is None:
        raise ValueError(f"missing IHDR: {path}")
    width, height, bit_depth, color_type, _ = ihdr
    channels_by_type = {0: 1, 2: 3, 4: 2, 6: 4}
    if color_type not in channels_by_type or bit_depth not in (8, 16):
        raise ValueError(f"unsupported PNG color type/depth: {path}")
    channels = channels_by_type[color_type]
    bytes_per_sample = bit_depth // 8
    bytes_per_pixel = channels * bytes_per_sample
    row_bytes = width * bytes_per_pixel
    raw = zlib.decompress(bytes(compressed))
    if len(raw) != height * (row_bytes + 1):
        raise ValueError(f"PNG scanline length mismatch: {path}")
    rows: list[bytes] = []
    previous = bytearray(row_bytes)
    cursor = 0
    for _row in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor:cursor + row_bytes]
        cursor += row_bytes
        decoded = bytearray(row_bytes)
        for index, value in enumerate(encoded):
            left = decoded[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                result = value
            elif filter_type == 1:
                result = value + left
            elif filter_type == 2:
                result = value + up
            elif filter_type == 3:
                result = value + ((left + up) // 2)
            elif filter_type == 4:
                result = value + paeth(left, up, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter {filter_type}: {path}")
            decoded[index] = result & 0xFF
        rows.append(bytes(decoded))
        previous = decoded
    return {
        "width": width,
        "height": height,
        "bitDepth": bit_depth,
        "colorType": color_type,
        "channels": channels,
        "rows": rows,
    }


def rgb_pixels(image: dict[str, Any]) -> list[tuple[int, int, int]]:
    if image["bitDepth"] != 8:
        raise ValueError("rgb_pixels requires PNG8")
    color_type = image["colorType"]
    pixels: list[tuple[int, int, int]] = []
    for row in image["rows"]:
        if color_type == 0:
            pixels.extend((value, value, value) for value in row)
        elif color_type == 2:
            pixels.extend(tuple(row[index:index + 3]) for index in range(0, len(row), 3))
        elif color_type == 4:
            pixels.extend((row[index], row[index], row[index]) for index in range(0, len(row), 2))
        elif color_type == 6:
            pixels.extend(tuple(row[index:index + 3]) for index in range(0, len(row), 4))
        else:
            raise ValueError("unsupported RGB conversion")
    return pixels


def grayscale_values(image: dict[str, Any]) -> list[int]:
    if image["colorType"] != 0:
        raise ValueError("grayscale_values requires grayscale PNG")
    values: list[int] = []
    if image["bitDepth"] == 8:
        for row in image["rows"]:
            values.extend(row)
    elif image["bitDepth"] == 16:
        for row in image["rows"]:
            values.extend(struct.unpack(f">{len(row) // 2}H", row))
    else:
        raise ValueError("unsupported grayscale depth")
    return values


def quantile(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = fraction * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] * (1.0 - weight) + ordered[upper] * weight)


def srgb_channel(value: int) -> float:
    normalized = value / 255.0
    return normalized / 12.92 if normalized <= 0.04045 else ((normalized + 0.055) / 1.055) ** 2.4


def luminance(pixel: tuple[int, int, int]) -> float:
    return 0.2126 * srgb_channel(pixel[0]) + 0.7152 * srgb_channel(pixel[1]) + 0.0722 * srgb_channel(pixel[2])


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"non-numeric value: {label}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {label}")
    return number


def finite_matrix(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 16:
        raise ValueError(f"matrix shape mismatch: {label}")
    return [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]


def finite_vector(value: Any, length: int, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"vector shape mismatch: {label}")
    return [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]


def vector_sub(left: list[float], right: list[float]) -> list[float]:
    return [left[index] - right[index] for index in range(3)]


def dot(left: list[float], right: list[float]) -> float:
    return sum(left[index] * right[index] for index in range(3))


def cross(left: list[float], right: list[float]) -> list[float]:
    return [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]


def normalize(value: list[float]) -> list[float]:
    magnitude = math.sqrt(dot(value, value))
    if not math.isfinite(magnitude) or magnitude <= 1.0e-12:
        raise ValueError("degenerate vector")
    return [component / magnitude for component in value]


def camera_basis(camera: dict[str, Any]) -> dict[str, Any]:
    forward = normalize(vector_sub(camera["target"], camera["position"]))
    world_up = normalize(camera["up"])
    right = normalize(cross(forward, world_up))
    true_up = normalize(cross(right, forward))
    determinant = dot(right, cross(true_up, [-component for component in forward]))
    return {
        "forward": forward,
        "right": right,
        "trueUp": true_up,
        "vectorLengths": [math.sqrt(dot(vector, vector)) for vector in (right, true_up, forward)],
        "pairwiseDots": [dot(right, true_up), dot(right, forward), dot(true_up, forward)],
        "determinant": determinant,
    }


def canonical_view_row_major(camera: dict[str, Any]) -> list[float]:
    basis = camera_basis(camera)
    right = basis["right"]
    true_up = basis["trueUp"]
    backward = [-component for component in basis["forward"]]
    position = camera["position"]
    return [
        right[0], right[1], right[2], -dot(right, position),
        true_up[0], true_up[1], true_up[2], -dot(true_up, position),
        backward[0], backward[1], backward[2], -dot(backward, position),
        0.0, 0.0, 0.0, 1.0,
    ]


def multiply_column_major(matrix: list[float], vector: list[float]) -> list[float]:
    result = [sum(matrix[column * 4 + row] * vector[column] for column in range(4)) for row in range(4)]
    if any(not math.isfinite(value) for value in result):
        raise ValueError("projection produced a non-finite vector")
    return result


def project_world(camera: dict[str, Any], point: list[float], *, direction: bool = False) -> tuple[float, float]:
    camera_space = multiply_column_major(camera["viewMatrix"], [*point, 0.0 if direction else 1.0])
    clip = multiply_column_major(camera["projectionMatrix"], camera_space)
    if abs(clip[3]) <= 1.0e-12:
        raise ValueError("projection homogeneous divisor is degenerate")
    return ((clip[0] / clip[3] + 1.0) * 0.5, (1.0 - clip[1] / clip[3]) * 0.5)


def expected_screen_projection(camera: dict[str, Any]) -> dict[str, Any]:
    points = {name: project_world(camera, point) for name, point in camera["projectionAnchors"].items()}
    return {
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
        "horizonY": project_world(camera, [0.0, 0.0, -1.0], direction=True)[1],
        "farRouteY": points["farRoute"][1],
        "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
    }


def angle_between(left: list[float], right: list[float]) -> float:
    return math.acos(max(-1.0, min(1.0, dot(normalize(left), normalize(right)))))


def stable_axis_angle_match(recorded: float, recomputed: float) -> bool:
    """Pure C7 near-zero angle predicate; performs no I/O or process work."""
    if (
        isinstance(recorded, bool)
        or isinstance(recomputed, bool)
        or not isinstance(recorded, (int, float))
        or not isinstance(recomputed, (int, float))
    ):
        return False
    recorded_value = float(recorded)
    recomputed_value = float(recomputed)
    return (
        math.isfinite(recorded_value)
        and math.isfinite(recomputed_value)
        and 0.0 <= recorded_value <= 1.0e-5
        and 0.0 <= recomputed_value <= 1.0e-5
        and abs(math.cos(recorded_value) - math.cos(recomputed_value)) <= 1.0e-12
    )


def dry_axis_angle_predicate() -> bool:
    frozen_forward = (2.1073424255447017e-08, 2.580956827951785e-08)
    frozen_up = (2.580956827951785e-08, 2.1073424255447017e-08)
    injected_failure = (1.00001e-5, 0.0)
    return (
        stable_axis_angle_match(*frozen_forward)
        and stable_axis_angle_match(*frozen_up)
        and not stable_axis_angle_match(*injected_failure)
    )


def linear_rgb(value: str) -> list[float]:
    channels = [int(value[index:index + 2], 16) / 255.0 for index in (1, 3, 5)]
    return [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]


def validate_orientation(record: Any, camera: dict[str, Any], label: str) -> None:
    if not isinstance(record, dict) or sorted(record.keys()) != sorted(ORIENTATION_KEYS):
        raise ValueError(f"orientation schema mismatch: {label}")
    for name in ("position", "target", "up"):
        if finite_vector(record[name], 3, f"{label}.{name}") != [float(value) for value in camera[name]]:
            raise ValueError(f"orientation frozen record mismatch: {label}.{name}")
    basis = camera_basis(camera)
    for name in ("forward", "right", "trueUp", "vectorLengths", "pairwiseDots"):
        actual = finite_vector(record[name], 3, f"{label}.{name}")
        if max(abs(left - right) for left, right in zip(actual, basis[name])) > 5.0e-7:
            raise ValueError(f"orientation basis mismatch: {label}.{name}")
    determinant = finite_number(record["determinant"], f"{label}.determinant")
    if abs(determinant - basis["determinant"]) > 5.0e-7 or abs(determinant - 1.0) > 5.0e-7:
        raise ValueError(f"orientation determinant mismatch: {label}")
    canonical = finite_matrix(record["canonicalViewMatrix"], f"{label}.canonicalViewMatrix")
    expected = canonical_view_row_major(camera)
    if max(abs(left - right) for left, right in zip(canonical, expected)) > 1.0e-12:
        raise ValueError(f"canonical view mismatch: {label}")
    actual = finite_matrix(record["actualViewMatrix"], f"{label}.actualViewMatrix")
    max_error = max(abs(left - right) for left, right in zip(actual, expected))
    if abs(finite_number(record["maxViewMatrixError"], f"{label}.maxViewMatrixError") - max_error) > 1.0e-12 or max_error > 5.0e-6:
        raise ValueError(f"actual view mismatch: {label}")
    actual_forward = [-actual[8], -actual[9], -actual[10]]
    actual_up = [actual[4], actual[5], actual[6]]
    recomputed_forward_angle = angle_between(actual_forward, basis["forward"])
    recomputed_up_angle = angle_between(actual_up, basis["trueUp"])
    forward_angle = finite_number(record["localForwardAngleRadians"], f"{label}.localForwardAngleRadians")
    up_angle = finite_number(record["localUpAngleRadians"], f"{label}.localUpAngleRadians")
    if not stable_axis_angle_match(forward_angle, recomputed_forward_angle):
        raise ValueError(f"camera local forward alignment failed: {label}")
    if not stable_axis_angle_match(up_angle, recomputed_up_angle):
        raise ValueError(f"camera local up alignment failed: {label}")


def validate_screen_projection(record: Any, camera: dict[str, Any], label: str) -> None:
    if not isinstance(record, dict) or sorted(record.keys()) != sorted(SCREEN_PROJECTION_KEYS):
        raise ValueError(f"screen projection schema mismatch: {label}")
    expected = expected_screen_projection(camera)
    if max(abs(left - right) for left, right in zip(finite_vector(record["runnerAnchor"], 2, f"{label}.runnerAnchor"), expected["runnerAnchor"])) > 1.0e-12:
        raise ValueError(f"runner anchor projection mismatch: {label}")
    for name in SCREEN_PROJECTION_KEYS[1:-1]:
        if abs(finite_number(record[name], f"{label}.{name}") - expected[name]) > 1.0e-12:
            raise ValueError(f"screen projection mismatch: {label}.{name}")
    if record["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER":
        raise ValueError(f"screen projection verdict mismatch: {label}")
    if not record["runnerHeadY"] < min(record["runnerFootLY"], record["runnerFootRY"]):
        raise ValueError(f"runner screen orientation mismatch: {label}")
    if not record["scarX"] > record["routeCenterX"]:
        raise ValueError(f"Tide Scar side mismatch: {label}")
    if camera["profile"] != "closeup":
        low, high = (0.61, 0.72) if camera["profile"] == "portrait" else (0.62, 0.76)
        if not low <= record["runnerAnchor"][1] <= high:
            raise ValueError(f"runner analytic band mismatch: {label}")
        if not record["runnerAnchor"][1] > record["beamY"] > record["ringY"] > record["columnY"] > record["gapY"]:
            raise ValueError(f"semantic analytic order mismatch: {label}")
        if not 0.17 <= record["horizonY"] <= 0.31:
            raise ValueError(f"analytic horizon mismatch: {label}")


def validate_light_atmosphere_bindings(
    binding: dict[str, Any], lighting: dict[str, Any], atmosphere_contract: dict[str, Any]
) -> None:
    light_binding = binding["lightingBinding"]
    if not isinstance(light_binding, dict) or sorted(light_binding.keys()) != ["contact", "fill", "key", "verdict"]:
        raise ValueError("lighting binding schema mismatch")
    if light_binding["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER":
        raise ValueError("lighting binding verdict mismatch")
    directional_keys = ["colorHex", "colorLinear", "energy", "shadow", "surfaceToLight", "normalizedSurfaceToLight", "actualLocalMinusZ", "alignmentRadians"]
    for name in ("key", "fill"):
        record = light_binding[name]
        frozen = lighting[name]
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(directional_keys):
            raise ValueError(f"directional light binding schema mismatch: {name}")
        if record["colorHex"] != frozen["color"] or record["shadow"] is not frozen["shadow"]:
            raise ValueError(f"directional light exact record mismatch: {name}")
        if abs(finite_number(record["energy"], f"lightingBinding.{name}.energy") - frozen["energy"]) > 1.0e-6:
            raise ValueError(f"directional light energy mismatch: {name}")
        if max(abs(left - right) for left, right in zip(finite_vector(record["colorLinear"], 3, f"lightingBinding.{name}.colorLinear"), linear_rgb(frozen["color"]))) > 1.0e-6:
            raise ValueError(f"directional light color mismatch: {name}")
        source = finite_vector(record["surfaceToLight"], 3, f"lightingBinding.{name}.surfaceToLight")
        if source != [float(value) for value in frozen["surfaceToLight"]]:
            raise ValueError(f"directional light source mismatch: {name}")
        normalized = normalize(source)
        if max(abs(left - right) for left, right in zip(finite_vector(record["normalizedSurfaceToLight"], 3, f"lightingBinding.{name}.normalizedSurfaceToLight"), normalized)) > 5.0e-7:
            raise ValueError(f"directional light normalization mismatch: {name}")
        actual = finite_vector(record["actualLocalMinusZ"], 3, f"lightingBinding.{name}.actualLocalMinusZ")
        alignment = angle_between(actual, [-component for component in normalized])
        if abs(finite_number(record["alignmentRadians"], f"lightingBinding.{name}.alignmentRadians") - alignment) > 1.0e-12 or alignment > 1.0e-5:
            raise ValueError(f"directional light alignment mismatch: {name}")
    contact = light_binding["contact"]
    frozen_contact = lighting["contact"]
    contact_keys = ["colorHex", "colorLinear", "energy", "size", "shadow", "location", "target", "actualLocalMinusZ", "alignmentRadians"]
    if not isinstance(contact, dict) or sorted(contact.keys()) != sorted(contact_keys):
        raise ValueError("contact light binding schema mismatch")
    if contact["colorHex"] != frozen_contact["color"] or contact["shadow"] is not frozen_contact["shadow"]:
        raise ValueError("contact light exact record mismatch")
    location = finite_vector(contact["location"], 3, "lightingBinding.contact.location")
    target = finite_vector(contact["target"], 3, "lightingBinding.contact.target")
    if location != frozen_contact["location"] or target != frozen_contact["target"]:
        raise ValueError("contact light placement mismatch")
    if max(abs(left - right) for left, right in zip(finite_vector(contact["colorLinear"], 3, "lightingBinding.contact.colorLinear"), linear_rgb(frozen_contact["color"]))) > 1.0e-6:
        raise ValueError("contact light color mismatch")
    for name in ("energy", "size"):
        if abs(finite_number(contact[name], f"lightingBinding.contact.{name}") - frozen_contact[name]) > 1.0e-6:
            raise ValueError(f"contact light {name} mismatch")
    alignment = angle_between(finite_vector(contact["actualLocalMinusZ"], 3, "lightingBinding.contact.actualLocalMinusZ"), normalize(vector_sub(target, location)))
    if abs(finite_number(contact["alignmentRadians"], "lightingBinding.contact.alignmentRadians") - alignment) > 1.0e-12 or alignment > 1.0e-5:
        raise ValueError("contact light alignment mismatch")
    atmosphere = binding["atmosphereBinding"]
    expected_atmosphere = json.loads(json.dumps(atmosphere_contract, ensure_ascii=False, allow_nan=False))
    expected_atmosphere.update(
        {
            "transmittance20": math.exp(-atmosphere_contract["density"] * 20.0),
            "transmittance120": math.exp(-atmosphere_contract["density"] * 120.0),
            "transmittance520": math.exp(-atmosphere_contract["density"] * 520.0),
            "verdict": "READY_FOR_DIAGNOSTIC_RENDER",
        }
    )
    deep_compare(expected_atmosphere, atmosphere, "$.cameraBinding.atmosphereBinding")


def validate_c7_preflight_cameras(preflight: dict[str, Any]) -> None:
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
        raise ValueError("preflight camera profile order mismatch")
    for record in cameras:
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(camera_keys):
            raise ValueError(f"preflight camera schema mismatch: {record.get('profile')}")
        if not isinstance(record["projectionAnchors"], dict):
            raise ValueError(f"preflight projection anchor object mismatch: {record.get('profile')}")
        if sorted(record["projectionAnchors"].keys()) != sorted(anchor_keys):
            raise ValueError(f"preflight projection anchor key-set mismatch: {record.get('profile')}")


def validate_camera_binding(path: Path, preflight: dict[str, Any]) -> str:
    if not path.is_file():
        raise ValueError("missing camera-binding.json")
    binding = json.loads(path.read_text(encoding="utf-8"))
    top_keys = [
        "schemaId", "schemaVersion", "diagnosticId", "blenderVersion", "profiles",
        "lightingBinding", "atmosphereBinding", "renderCallCountAtWrite", "verdict",
    ]
    if not isinstance(binding, dict) or sorted(binding.keys()) != sorted(top_keys):
        raise ValueError("camera binding top-level schema mismatch")
    if (
        binding["schemaId"] != "tide-relay.temple-tr4.camera-binding"
        or isinstance(binding["schemaVersion"], bool)
        or not isinstance(binding["schemaVersion"], int)
        or binding["schemaVersion"] != 3
        or binding["diagnosticId"] != DIAGNOSTIC_ID
        or binding["blenderVersion"] != "4.5.5 LTS"
        or isinstance(binding["renderCallCountAtWrite"], bool)
        or not isinstance(binding["renderCallCountAtWrite"], int)
        or binding["renderCallCountAtWrite"] != 0
        or binding["verdict"] != "READY_FOR_DIAGNOSTIC_RENDER"
    ):
        raise ValueError("camera binding identity/verdict mismatch")
    profiles = binding["profiles"]
    cameras = preflight["cameras"]
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise ValueError("camera binding profile count mismatch")
    for profile_index, (record, camera) in enumerate(zip(profiles, cameras)):
        label = f"cameraBinding.profiles[{profile_index}]"
        if not isinstance(record, dict) or sorted(record.keys()) != sorted(CAMERA_BINDING_PROFILE_KEYS):
            raise ValueError(f"camera binding profile schema mismatch: {profile_index}")
        if record["profile"] != PROFILE_ORDER[profile_index] or record["profile"] != camera["profile"]:
            raise ValueError(f"camera binding profile order mismatch: {profile_index}")
        lens_shift = finite_number(record["lensShiftY"], f"{label}.lensShiftY")
        if lens_shift != camera["lensShiftY"]:
            raise ValueError(f"camera binding lens target mismatch: {profile_index}")
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
            raise ValueError(f"camera shift propagation mismatch: {profile_index}")
        expected_difference = [second - first for first, second in zip(matrices["matrix0"], matrices["matrix1"])]
        if max(abs(left - right) for left, right in zip(matrices["difference"], expected_difference)) > 1.0e-12:
            raise ValueError(f"camera calibration arithmetic mismatch: {profile_index}")
        if abs(scalars["b0"] - matrices["matrix0"][6]) > 1.0e-12 or abs(scalars["b1"] - matrices["matrix1"][6]) > 1.0e-12:
            raise ValueError(f"camera target alias mismatch: {profile_index}")
        response = matrices["difference"][6]
        max_off_target = max(abs(value) for index, value in enumerate(matrices["difference"]) if index != 6)
        dominance = abs(response) / max(max_off_target, 1.0e-12)
        if (
            abs(scalars["b0"]) > 1.0e-7
            or abs(scalars["response"] - response) > 1.0e-12
            or response <= 0.0
            or abs(response - 2.0) > 5.0e-7
            or abs(scalars["maxOffTargetCalibrationDelta"] - max_off_target) > 1.0e-12
            or max_off_target > 5.0e-7
            or abs(scalars["dominanceRatio"] - dominance) > 1.0e-12
            or dominance < 1.0e6
        ):
            raise ValueError(f"camera calibration gate failed: {profile_index}")
        expected_solved = (lens_shift - matrices["matrix0"][6]) / response
        if abs(scalars["solvedShift"] - expected_solved) > 1.0e-12 or abs(scalars["evaluatedSolvedShift"] - scalars["solvedShift"]) > 1.0e-8:
            raise ValueError(f"camera solved shift mismatch: {profile_index}")
        expected_solved_difference = [value - baseline for value, baseline in zip(matrices["matrixSolved"], matrices["matrix0"])]
        if max(abs(left - right) for left, right in zip(matrices["solvedDifference"], expected_solved_difference)) > 1.0e-12:
            raise ValueError(f"camera solved arithmetic mismatch: {profile_index}")
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
            raise ValueError(f"camera solved target/off-target gate failed: {profile_index}")
        expected_webgl = [matrices["matrixSolved"][(index % 4) * 4 + index // 4] for index in range(16)]
        if max(abs(left - right) for left, right in zip(matrices["webglMatrix"], expected_webgl)) > 1.0e-12:
            raise ValueError(f"camera WebGL transpose mismatch: {profile_index}")
        projection_errors = [abs(actual_value - expected_value) for actual_value, expected_value in zip(matrices["webglMatrix"], camera["projectionMatrix"])]
        max_projection_error = max(projection_errors)
        if abs(scalars["maxProjectionError"] - max_projection_error) > 1.0e-12 or projection_errors[9] > 5.0e-7 or max_projection_error > 5.0e-7:
            raise ValueError(f"camera frozen projection mismatch: {profile_index}")
        validate_orientation(record["orientation"], camera, f"{label}.orientation")
        validate_screen_projection(record["screenProjection"], camera, f"{label}.screenProjection")
    validate_light_atmosphere_bindings(
        binding,
        preflight["construction"]["lighting"],
        preflight["construction"]["atmosphere"],
    )
    return sha256_file(path)


def validate_render_order(path: Path, expected_names: list[str]) -> str:
    if not path.is_file() or json.loads(path.read_text(encoding="utf-8")) != expected_names:
        raise ValueError("render-order.json mismatch")
    return sha256_file(path)


def validate_scene_metrics(path: Path, preflight: dict[str, Any]) -> str:
    if not path.is_file():
        raise ValueError("missing scene-metrics.json")
    metrics = json.loads(path.read_text(encoding="utf-8"))
    keys = [
        "meshObjects", "sourceTrianglesBeforeModifiers", "beautyMaterialCount",
        "semanticRoots", "pursuerBookendRoot", "runnerRoot", "roadTopY",
        "geometryBinding", "materialGraphBinding", "depthEncodingBinding", "verdict",
    ]
    if not isinstance(metrics, dict) or sorted(metrics.keys()) != sorted(keys):
        raise ValueError("scene metrics schema mismatch")
    for name in ("meshObjects", "sourceTrianglesBeforeModifiers", "beautyMaterialCount"):
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"scene metric count mismatch: {name}")
        if value == 0:
            raise ValueError(f"empty scene metric count: {name}")
    if metrics["sourceTrianglesBeforeModifiers"] > preflight["budgets"]["sourceTriangles"]:
        raise ValueError("scene metric budget exceeded")
    if metrics["beautyMaterialCount"] != len(preflight["materials"]):
        raise ValueError("beauty material count mismatch")
    roots = metrics["semanticRoots"]
    expected_names = [record["name"] for record in preflight["semanticRoots"]]
    if not isinstance(roots, list) or len(roots) != 9:
        raise ValueError("scene semantic root count mismatch")
    for index, (record, expected_name) in enumerate(zip(roots, expected_names)):
        if not isinstance(record, dict) or sorted(record.keys()) != ["children", "name", "translation"]:
            raise ValueError(f"scene semantic root schema mismatch: {index}")
        if (
            record["name"] != expected_name
            or isinstance(record["children"], bool)
            or not isinstance(record["children"], int)
            or record["children"] <= 0
        ):
            raise ValueError(f"scene semantic root identity mismatch: {index}")
        translation = record["translation"]
        if not isinstance(translation, list) or len(translation) != 3:
            raise ValueError(f"scene semantic root translation schema mismatch: {index}")
        values = [finite_number(value, f"sceneMetrics.semanticRoots[{index}].translation") for value in translation]
        expected_translation = preflight["construction"]["pursuer"]["bookendRoot"] if expected_name == "TR4_Pursuer_Cinematic" else [0, 0, 0]
        if any(not math.isclose(actual, float(expected), rel_tol=0.0, abs_tol=1.0e-6) for actual, expected in zip(values, expected_translation)):
            raise ValueError(f"scene semantic root translation mismatch: {expected_name}")
    for name, expected in (
        ("pursuerBookendRoot", preflight["construction"]["pursuer"]["bookendRoot"]),
        ("runnerRoot", preflight["construction"]["runner"]["root"]),
    ):
        vector = metrics[name]
        if not isinstance(vector, list) or len(vector) != 3:
            raise ValueError(f"scene metric vector mismatch: {name}")
        values = [finite_number(value, f"sceneMetrics.{name}") for value in vector]
        if any(not math.isclose(actual, float(frozen), rel_tol=0.0, abs_tol=1.0e-6) for actual, frozen in zip(values, expected)):
            raise ValueError(f"scene metric vector mismatch: {name}")
    if not math.isclose(finite_number(metrics["roadTopY"], "sceneMetrics.roadTopY"), float(preflight["construction"]["road"]["surfaceY"]), rel_tol=0.0, abs_tol=1.0e-6):
        raise ValueError("scene road top mismatch")
    if metrics["verdict"] != "RENDERED_FOR_EVALUATION":
        raise ValueError("scene metrics verdict mismatch")
    construction = preflight["construction"]
    expected_geometry = {
        name: construction[name]
        for name in ("road", "canyon", "runner", "pursuer", "hazards", "tideScar")
    }
    expected_geometry["verdict"] = "READY_FOR_DIAGNOSTIC_RENDER"
    expected_material_graph = dict(construction["materialGraphs"])
    expected_material_graph["verdict"] = "READY_FOR_DIAGNOSTIC_RENDER"
    expected_depth_encoding = dict(construction["depthEncoding"])
    expected_depth_encoding["verdict"] = "READY_FOR_DIAGNOSTIC_RENDER"
    deep_compare(expected_geometry, metrics["geometryBinding"], "$.sceneMetrics.geometryBinding")
    deep_compare(expected_material_graph, metrics["materialGraphBinding"], "$.sceneMetrics.materialGraphBinding")
    deep_compare(expected_depth_encoding, metrics["depthEncodingBinding"], "$.sceneMetrics.depthEncodingBinding")
    return sha256_file(path)


def pixel_indices_for_color(pixels: list[tuple[int, int, int]], color: tuple[int, int, int]) -> list[int]:
    return [index for index, pixel in enumerate(pixels) if pixel == color]


def bounds_and_centroid(indices: list[int], width: int, height: int) -> tuple[list[float], float, float, int]:
    if not indices:
        raise ValueError("semantic pixel set is empty")
    xs = [index % width for index in indices]
    ys = [index // width for index in indices]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    bounds = [xmin / width, ymin / height, (xmax + 1) / width, (ymax + 1) / height]
    centroid_y = sum((value + 0.5) / height for value in ys) / len(ys)
    margin = min(bounds[0], bounds[1], 1.0 - bounds[2], 1.0 - bounds[3])
    return bounds, centroid_y, margin, xmax - xmin + 1


def longest_white_run(values: list[int], width: int, row: int) -> int:
    row = max(0, min(row, len(values) // width - 1))
    longest = 0
    current = 0
    for value in values[row * width:(row + 1) * width]:
        if value == 255:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def semantic_depth_median(depth_values: list[int], indices: list[int]) -> float:
    values = [depth_values[index] for index in indices if depth_values[index] != 65535]
    if not values:
        raise ValueError("semantic depth set is empty/background")
    return quantile(values, 0.50)


def evaluate(preflight_path: Path, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    preflight_bytes = preflight_path.read_bytes()
    preflight = strict_json_object_bytes(preflight_bytes, "preflight.json")
    preflight_sha256 = hashlib.sha256(preflight_bytes).hexdigest()
    failures: list[str] = []
    gates: dict[str, Any] = {}
    if (
        preflight.get("schemaId") != "tide-relay.temple-tr4.asset-preflight"
        or isinstance(preflight.get("schemaVersion"), bool)
        or not isinstance(preflight.get("schemaVersion"), int)
        or preflight.get("schemaVersion") != 7
        or preflight.get("contractVersion") != "TEMPLE-TR4-C7"
        or preflight.get("tools", {}).get("pythonVersion") != PYTHON_VERSION
        or platform.python_version() != PYTHON_VERSION
    ):
        raise ValueError("preflight schema/contract mismatch")
    if preflight.get("verdict") != "READY_FOR_BLENDER":
        raise ValueError("preflight verdict mismatch")
    construction = preflight.get("construction")
    if not isinstance(construction, dict):
        raise ValueError("preflight construction is not an object")
    calculated_construction_hash = hashlib.sha256(canonical_bytes(construction)).hexdigest()
    if preflight.get("constructionHash") != calculated_construction_hash or calculated_construction_hash != C7_CONSTRUCTION_SHA256:
        raise ValueError("preflight C7 construction hash mismatch")
    if validate_planned_manifest(root / "planned-manifest.json", preflight, preflight_bytes) != preflight_sha256:
        raise ValueError("planned manifest does not replay the evaluator-bound preflight hash")
    validate_c7_preflight_cameras(preflight)
    expected_outputs = preflight.get("outputs")
    if not isinstance(expected_outputs, list) or len(expected_outputs) != 20:
        raise ValueError("preflight output array is not the closed 20-record array")
    expected_names = [item["relativePath"] for item in expected_outputs]
    expected_order = [(profile, pass_name) for profile in PROFILE_ORDER for pass_name in ("beauty", "object-id", "road-mask", "normal", "linear-depth")]
    profile_metadata = {
        "portrait": ("tr4-diagnostic-running-007", 270, 480),
        "desktop": ("tr4-diagnostic-running-007", 480, 270),
        "landscape": ("tr4-diagnostic-running-007", 422, 195),
        "closeup": ("tr4-diagnostic-game-over-007", 320, 240),
    }
    output_keys = ["index", "profile", "pass", "sceneId", "relativePath", "width", "height"]
    if (
        [(item.get("profile"), item.get("pass")) for item in expected_outputs] != expected_order
        or [item.get("index") for item in expected_outputs] != list(range(20))
        or expected_names != [f"tr4-diagnostic-007-{profile}-{pass_name}.png" for profile, pass_name in expected_order]
        or any(not isinstance(item, dict) or sorted(item.keys()) != sorted(output_keys) for item in expected_outputs)
        or any(
            (item["sceneId"], item["width"], item["height"]) != profile_metadata[item["profile"]]
            for item in expected_outputs
        )
    ):
        raise ValueError("preflight diagnostic-007 output order/prefix mismatch")

    # C7 preserves the closed camera, light, atmosphere, geometry, material, depth, and render-order evidence before PNG reads.
    camera_binding_sha256 = validate_camera_binding(root / "camera-binding.json", preflight)
    render_order_sha256 = validate_render_order(root / "render-order.json", expected_names)
    scene_metrics_sha256 = validate_scene_metrics(root / "scene-metrics.json", preflight)
    allowed_before_evaluation = {
        "preflight.json", "planned-manifest.json", "camera-binding.json",
        "render-order.json", "scene-metrics.json", "blender.log", *expected_names,
    }
    directories = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_dir()]
    actual_before_evaluation = {path.name for path in root.iterdir() if path.is_file()}
    if directories or actual_before_evaluation != allowed_before_evaluation:
        raise ValueError(f"pre-evaluator ancillary allowlist mismatch: directories={directories}, files={sorted(actual_before_evaluation)}")

    actual_names = sorted(path.name for path in root.glob("*.png"))
    gates["exactPngSet"] = sorted(expected_names) == actual_names and len(actual_names) == 20
    if not gates["exactPngSet"]:
        failures.append("exact-png-set")

    manifest_records: list[dict[str, Any]] = []
    decoded: dict[tuple[str, str], dict[str, Any]] = {}
    for item in expected_outputs:
        path = root / item["relativePath"]
        if not path.is_file() or path.stat().st_size <= 0:
            failures.append(f"missing:{item['relativePath']}")
            continue
        image = read_png(path)
        decoded[(item["profile"], item["pass"])] = image
        size_ok = (image["width"], image["height"]) == (item["width"], item["height"])
        depth_ok = image["bitDepth"] == (16 if item["pass"] == "linear-depth" else 8)
        if not size_ok:
            failures.append(f"dimensions:{item['relativePath']}")
        if not depth_ok:
            failures.append(f"bit-depth:{item['relativePath']}")
        manifest_records.append(
            {
                "index": item["index"],
                "profile": item["profile"],
                "pass": item["pass"],
                "relativePath": item["relativePath"],
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "width": image["width"],
                "height": image["height"],
                "bitDepth": image["bitDepth"],
                "colorType": image["colorType"],
            }
        )

    camera_binding = json.loads((root / "camera-binding.json").read_text(encoding="utf-8"))
    binding_profiles = {record["profile"]: record for record in camera_binding["profiles"]}
    profile_metrics: dict[str, Any] = {}
    semantic_counts: dict[str, dict[str, int]] = {}
    hazard_totals = {name: 0 for name in ("beam", "ring", "column", "gap-lips")}
    profile_gate_state: dict[str, dict[str, bool]] = {}
    for profile in ("portrait", "desktop", "landscape", "closeup"):
        required = [(profile, name) for name in ("beauty", "object-id", "road-mask", "normal", "linear-depth")]
        if any(key not in decoded for key in required):
            failures.append(f"profile-incomplete:{profile}")
            continue
        beauty = rgb_pixels(decoded[(profile, "beauty")])
        object_pixels = rgb_pixels(decoded[(profile, "object-id")])
        road_values = grayscale_values(decoded[(profile, "road-mask")])
        normal_pixels = rgb_pixels(decoded[(profile, "normal")])
        depth_values = grayscale_values(decoded[(profile, "linear-depth")])
        width = decoded[(profile, "beauty")]["width"]
        height = decoded[(profile, "beauty")]["height"]
        luminances = [luminance(pixel) for pixel in beauty]
        route_luminances = [value for value, mask in zip(luminances, road_values) if mask == 255]
        semantic_indices = {name: pixel_indices_for_color(object_pixels, color) for name, color in PALETTE.items()}
        counts = {name: len(indices) for name, indices in semantic_indices.items()}
        semantic_counts[profile] = counts
        for hazard in hazard_totals:
            if profile != "closeup":
                hazard_totals[hazard] += counts[hazard]
        road_binary = set(road_values).issubset({0, 255})
        p50 = quantile(luminances, 0.50)
        p95 = quantile(luminances, 0.95)
        dark_fraction = sum(1 for pixel in beauty if max(pixel) <= 10) / max(1, len(beauty))
        route_p50 = quantile(route_luminances, 0.50)
        road_fraction = sum(1 for value in road_values if value == 255) / max(1, len(road_values))
        normal_unique = len(set(normal_pixels))
        known_nonbackground = set(PALETTE.values()) - {PALETTE["background"]}
        foreground_depth = [
            depth for depth, semantic in zip(depth_values, object_pixels)
            if semantic in known_nonbackground
        ]
        background_depth = [
            depth for depth, semantic in zip(depth_values, object_pixels)
            if semantic == PALETTE["background"]
        ]
        depth_background_ok = (
            bool(foreground_depth)
            and bool(background_depth)
            and all(value != 65535 for value in foreground_depth)
            and all(value == 65535 for value in background_depth)
        )
        depth_unique = len(set(foreground_depth))
        foreground_depth_p10 = quantile(foreground_depth, 0.10)
        foreground_depth_p50 = quantile(foreground_depth, 0.50)
        foreground_depth_p90 = quantile(foreground_depth, 0.90)
        runner_bounds, runner_centroid_y, runner_margin, _runner_width = bounds_and_centroid(
            semantic_indices["runner"], width, height
        )
        runner_beauty = [luminances[index] for index in semantic_indices["runner"]]
        runner_beauty_p50 = quantile(runner_beauty, 0.50)
        semantic_centroid_y: dict[str, float] = {}
        representative_depth: dict[str, float] = {}
        for semantic in ("runner", "beam", "ring", "column", "gap-lips"):
            _bounds, centroid_y, _margin, _width = bounds_and_centroid(semantic_indices[semantic], width, height)
            semantic_centroid_y[semantic] = centroid_y
            representative_depth[semantic] = semantic_depth_median(depth_values, semantic_indices[semantic])
        road_normal_pixels = [pixel for pixel, mask in zip(normal_pixels, road_values) if mask == 255]
        if not road_normal_pixels:
            raise ValueError(f"road normal mask is empty: {profile}")
        road_normal_median = [quantile((pixel[channel] for pixel in road_normal_pixels), 0.50) for channel in range(3)]
        bottom_run = longest_white_run(road_values, width, math.floor(0.98 * (height - 1)))
        far_route_y = binding_profiles[profile]["screenProjection"]["farRouteY"]
        far_run = longest_white_run(road_values, width, round(far_route_y * (height - 1)))
        road_bottom_width = bottom_run / width
        road_far_width = far_run / width
        road_width_ratio = road_bottom_width / road_far_width if far_run > 0 else 0.0
        pursuer_bounds: list[float] | None = None
        pursuer_margin: float | None = None
        pursuer_width = 0
        pursuer_beauty_p50: float | None = None
        pursuer_beauty_p95: float | None = None
        if profile == "closeup":
            pursuer_bounds, _pursuer_centroid, pursuer_margin, pursuer_width = bounds_and_centroid(
                semantic_indices["pursuer"], width, height
            )
            pursuer_beauty = [luminances[index] for index in semantic_indices["pursuer"]]
            pursuer_beauty_p50 = quantile(pursuer_beauty, 0.50)
            pursuer_beauty_p95 = quantile(pursuer_beauty, 0.95)
        profile_metrics[profile] = {
            "luminanceP50": p50,
            "luminanceP95": p95,
            "nearBlackFraction": dark_fraction,
            "routeLuminanceP50": route_p50,
            "roadMaskFraction": road_fraction,
            "normalUniqueColors": normal_unique,
            "depthUniqueValues": depth_unique,
            "depthMin": min(depth_values),
            "depthMax": max(depth_values),
            "foregroundDepthP10": foreground_depth_p10,
            "foregroundDepthP50": foreground_depth_p50,
            "foregroundDepthP90": foreground_depth_p90,
            "runnerBounds": runner_bounds,
            "runnerCentroidY": runner_centroid_y,
            "runnerMargin": runner_margin,
            "runnerBeautyLuminanceP50": runner_beauty_p50,
            "pursuerBounds": pursuer_bounds,
            "pursuerMargin": pursuer_margin,
            "pursuerWidthPixels": pursuer_width,
            "pursuerBeautyLuminanceP50": pursuer_beauty_p50,
            "pursuerBeautyLuminanceP95": pursuer_beauty_p95,
            "roadBottomWidthFraction": road_bottom_width,
            "roadFarRouteWidthFraction": road_far_width,
            "roadWidthRatio": road_width_ratio,
            "semanticCentroidY": semantic_centroid_y,
            "roadNormalMedian": road_normal_median,
            "representativeDepth": representative_depth,
        }
        global_ok = p50 >= 0.12 and p95 >= 0.55
        route_ok = route_p50 >= 0.25
        near_black_ok = dark_fraction < 0.10
        road_mask_ok = road_binary and 0.02 <= road_fraction <= 0.82
        subjects_ok = all(counts[name] > 0 for name in ("road", "canyon", "runner", "tide-scar"))
        normal_variation_ok = normal_unique >= 24
        depth_variation_ok = depth_unique >= 64 and min(depth_values) < max(depth_values)
        foreground_depth_quantiles_ok = (
            foreground_depth_p10 < foreground_depth_p50 < foreground_depth_p90 < 62000
        )
        runner_band_ok = runner_margin >= 0.02
        road_perspective_ok = True
        semantic_order_ok = True
        representative_depth_ok = True
        pursuer_closeup_ok = True
        if profile != "closeup":
            low, high = (0.61, 0.72) if profile == "portrait" else (0.62, 0.76)
            bottom_min = 0.74 if profile == "portrait" else 0.44
            far_low, far_high = (0.06, 0.19) if profile == "portrait" else (0.015, 0.08)
            runner_band_ok = runner_band_ok and low <= runner_centroid_y <= high
            road_perspective_ok = (
                road_bottom_width >= bottom_min
                and far_low <= road_far_width <= far_high
                and road_width_ratio >= 2.5
            )
            semantic_order_ok = (
                semantic_centroid_y["runner"] > semantic_centroid_y["beam"]
                > semantic_centroid_y["ring"] > semantic_centroid_y["column"]
                > semantic_centroid_y["gap-lips"]
            )
            representative_depth_ok = (
                representative_depth["runner"] < representative_depth["beam"]
                < representative_depth["ring"] < representative_depth["column"]
                < representative_depth["gap-lips"]
            )
        else:
            pursuer_closeup_ok = (
                pursuer_margin is not None and pursuer_margin >= 0.02
                and pursuer_width >= 48
                and pursuer_beauty_p50 is not None and pursuer_beauty_p50 >= 0.08
                and pursuer_beauty_p95 is not None and pursuer_beauty_p95 >= 0.20
            )
        runner_roi_ok = runner_beauty_p50 >= 0.12
        road_normal_up_ok = (
            road_normal_median[1] >= 240
            and 112 <= road_normal_median[0] <= 144
            and 112 <= road_normal_median[2] <= 144
        )
        profile_gate_state[profile] = {
            "globalLuminance": global_ok,
            "routeLuminance": route_ok,
            "nearBlack": near_black_ok,
            "roadMaskBinaryArea": road_mask_ok,
            "semanticSubjects": subjects_ok,
            "normalVariation": normal_variation_ok,
            "depthVariation": depth_variation_ok,
            "runnerBandContainment": runner_band_ok,
            "roadPerspective": road_perspective_ok,
            "semanticScreenOrder": semantic_order_ok,
            "runnerRoiLuminance": runner_roi_ok,
            "pursuerCloseup": pursuer_closeup_ok,
            "roadNormalUp": road_normal_up_ok,
            "depthBackgroundSeparation": depth_background_ok,
            "foregroundDepthQuantiles": foreground_depth_quantiles_ok,
            "representativeDepthOrder": representative_depth_ok,
        }
        for gate_name, passed in profile_gate_state[profile].items():
            if not passed:
                failures.append(f"{gate_name}:{profile}")
        known = set(PALETTE.values())
        unknown_nonblack = sum(1 for pixel in object_pixels if pixel != (0, 0, 0) and pixel not in known)
        if unknown_nonblack != 0:
            failures.append(f"object-id-blending:{profile}:{unknown_nonblack}")

    if list(profile_metrics.keys()) != PROFILE_ORDER:
        failures.append("profile-metrics-order")
    for profile, metrics in profile_metrics.items():
        if not isinstance(metrics, dict) or sorted(metrics.keys()) != sorted(PROFILE_METRIC_KEYS):
            raise ValueError(f"profile metric closed schema mismatch: {profile}")

    ordinary = ("portrait", "desktop", "landscape")
    pursuer_ordinary = sum(semantic_counts.get(profile, {}).get("pursuer", 0) for profile in ordinary)
    pursuer_closeup = semantic_counts.get("closeup", {}).get("pursuer", 0)
    gates["pursuerAbsentOrdinary"] = pursuer_ordinary == 0
    gates["pursuerPresentCloseup"] = pursuer_closeup > 0
    gates["hazardsPresentOrdinary"] = all(value > 0 for value in hazard_totals.values())
    if not gates["pursuerAbsentOrdinary"]:
        failures.append(f"pursuer-visible-ordinary:{pursuer_ordinary}")
    if not gates["pursuerPresentCloseup"]:
        failures.append("pursuer-missing-closeup")
    if not gates["hazardsPresentOrdinary"]:
        failures.append(f"hazard-semantic-missing:{hazard_totals}")

    gates["orderedManifest"] = [record["index"] for record in manifest_records] == list(range(20))
    if not gates["orderedManifest"]:
        failures.append("manifest-order")
    gates["cameraBinding"] = True
    for gate_name in (
        "globalLuminance", "routeLuminance", "nearBlack", "roadMaskBinaryArea",
        "semanticSubjects", "normalVariation", "depthVariation", "runnerBandContainment",
        "roadPerspective", "semanticScreenOrder", "runnerRoiLuminance", "pursuerCloseup",
        "roadNormalUp", "depthBackgroundSeparation", "foregroundDepthQuantiles",
        "representativeDepthOrder",
    ):
        gates[gate_name] = all(profile_gate_state.get(profile, {}).get(gate_name, False) for profile in PROFILE_ORDER)
    gates["scarRightOfRoute"] = all(
        record["screenProjection"]["scarX"] > record["screenProjection"]["routeCenterX"]
        for record in camera_binding["profiles"]
    )
    if not gates["scarRightOfRoute"]:
        failures.append("scar-right-of-route")
    if sorted(gates.keys()) != sorted(EVALUATION_GATE_KEYS):
        raise ValueError(f"evaluation gate key closure mismatch: {sorted(gates.keys())}")
    for gate_name, passed in gates.items():
        if not isinstance(passed, bool):
            raise ValueError(f"evaluation gate is not boolean: {gate_name}")
        if not passed and gate_name not in ("exactPngSet", "orderedManifest", "pursuerAbsentOrdinary", "pursuerPresentCloseup", "hazardsPresentOrdinary", "scarRightOfRoute"):
            marker = f"gate:{gate_name}"
            if marker not in failures:
                failures.append(marker)
    verdict = "READY_FOR_MANUAL_REVIEW" if not failures else "DIAGNOSTIC_BLOCKED"
    if preflight_path.read_bytes() != preflight_bytes:
        raise ValueError("preflight bytes changed during evaluation")
    if validate_planned_manifest(root / "planned-manifest.json", preflight, preflight_bytes) != preflight_sha256:
        raise ValueError("planned manifest changed during evaluation")
    manifest_core = {
        "schemaId": "tide-relay.temple-tr4.diagnostic-manifest",
        "schemaVersion": 1,
        "diagnosticId": DIAGNOSTIC_ID,
        "preflightSha256": preflight_sha256,
        "constructionHash": preflight.get("constructionHash"),
        "cameraBindingSha256": camera_binding_sha256,
        "renderOrderSha256": render_order_sha256,
        "sceneMetricsSha256": scene_metrics_sha256,
        "outputs": manifest_records,
    }
    manifest = dict(manifest_core)
    manifest["manifestHash"] = hashlib.sha256(canonical_bytes(manifest_core)).hexdigest()
    manifest["verdict"] = verdict
    evaluation = {
        "schemaId": "tide-relay.temple-tr4.diagnostic-evaluation",
        "schemaVersion": 1,
        "diagnosticId": DIAGNOSTIC_ID,
        "preflightSha256": manifest["preflightSha256"],
        "manifestHash": manifest["manifestHash"],
        "cameraBindingSha256": camera_binding_sha256,
        "renderOrderSha256": render_order_sha256,
        "sceneMetricsSha256": scene_metrics_sha256,
        "profileMetrics": profile_metrics,
        "semanticPixelCounts": semantic_counts,
        "hazardPixelTotalsOrdinary": hazard_totals,
        "gates": gates,
        "failures": failures,
        "manualReviewRequired": True,
        "verdict": verdict,
    }
    return evaluation, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--diagnostic-root", type=Path)
    parser.add_argument("--dry-axis-predicate", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.dry_axis_predicate:
            if arguments.preflight is not None or arguments.diagnostic_root is not None:
                raise ValueError("dry axis predicate does not accept evidence paths")
            if not dry_axis_angle_predicate():
                raise ValueError("C7 stable axis-angle predicate failed")
            print("C7_AXIS_PREDICATE_READY")
            return 0
        if arguments.preflight is None or arguments.diagnostic_root is None:
            raise ValueError("--preflight and --diagnostic-root are required for evaluation")
        preflight = arguments.preflight.resolve(strict=True)
        root = arguments.diagnostic_root.resolve(strict=True)
        if preflight.parent != root or preflight.name != "preflight.json":
            raise ValueError("preflight path is outside the exact diagnostic root")
        evaluation_path = root / "evaluation.json"
        manifest_path = root / "manifest.json"
        if evaluation_path.exists() or manifest_path.exists():
            raise ValueError("evaluator outputs must not pre-exist")
        evaluation, manifest = evaluate(preflight, root)
        atomic_write_json(manifest_path, manifest)
        atomic_write_json(evaluation_path, evaluation)
        print(json.dumps({"verdict": evaluation["verdict"], "manifestHash": manifest["manifestHash"]}, ensure_ascii=False))
        return 0 if evaluation["verdict"] == "READY_FOR_MANUAL_REVIEW" else 1
    except Exception as exc:
        print(json.dumps({"verdict": "DIAGNOSTIC_BLOCKED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
