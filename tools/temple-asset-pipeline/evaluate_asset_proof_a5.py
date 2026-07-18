"""Fail-closed deterministic raster/depth evaluator for TEMPLE-TR3-A5."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


ROOTS = [
    "Causeway_Root",
    "Canyon_Root",
    "Runner_Root",
    "Pursuer_Root",
    "Obstacle_Ring_Root",
    "TideScar_Ribbon_Editable",
]
SPECS = {
    "portrait": {"size": (540, 960), "courier": ((.45, .55), (.60, .68)), "pursuer": ((.43, .57), (.74, .83)), "hazard": ((.43, .60), (.34, .49)), "height": .15, "opening": .10},
    "desktop": {"size": (960, 540), "courier": ((.48, .56), (.61, .70)), "pursuer": ((.46, .58), (.75, .86)), "hazard": ((.44, .59), (.32, .49)), "height": .20, "opening": .09},
    "landscape": {"size": (844, 390), "courier": ((.48, .57), (.63, .73)), "pursuer": ((.45, .59), (.77, .90)), "hazard": ((.43, .60), (.29, .49)), "height": .22, "opening": .11},
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[int], ratio: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * ratio))] / 255.0


def contained(box: dict[str, float], margin: float = .0) -> bool:
    return box["width"] > 0 and box["height"] > 0 and box["x"] >= margin and box["y"] >= margin and box["x"] + box["width"] <= 1 - margin and box["y"] + box["height"] <= 1 - margin


def overlap(left: dict[str, float], right: dict[str, float]) -> float:
    return min(left["x"] + left["width"], right["x"] + right["width"]) - max(left["x"], right["x"])


def luma(path: Path) -> dict[str, float]:
    with Image.open(path) as image:
        values = list(image.convert("L").getdata())
    return {
        "p50": round(percentile(values, .50), 5),
        "p95": round(percentile(values, .95), 5),
        "nearBlackPercent": round(sum(value <= 10 for value in values) * 100.0 / len(values), 5),
    }


def role_predicate(role: str, red: int, green: int, blue: int) -> bool:
    # ID materials are emitted, but the renderer's color transform may change their
    # exact byte values. These dominance tests keep the evidence image-bound.
    if role == "courier":
        return red > green * 1.25 and red > blue * 1.35 and red > 75
    if role == "pursuer":
        return green > red * 1.25 and green > blue * 1.12 and green > 65
    if role == "hazard":
        return blue > red * 1.35 and blue > green * 1.12 and blue > 60
    if role == "scar":
        return red > 75 and green > 65 and blue < min(red, green) * .55
    if role == "near":
        return red > 70 and blue > 55 and green < min(red, blue) * .82
    if role == "mid":
        return green > 55 and blue > 65 and red < min(green, blue) * .78
    if role == "far":
        return blue > 58 and blue > red * 1.20 and blue > green * 1.04
    return False


def role_mask(path: Path, role: str) -> dict[str, object]:
    with Image.open(path) as image:
        source = image.convert("RGB")
        width, height = source.size
        pixels = source.load()
        positions: list[tuple[int, int]] = []
        for y in range(height):
            for x in range(width):
                if role_predicate(role, *pixels[x, y]):
                    positions.append((x, y))
    if not positions:
        return {"pixels": 0, "box": None}
    xs, ys = zip(*positions)
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    return {
        "pixels": len(positions),
        "box": {"x": x0 / width, "y": y0 / height, "width": (x1 - x0) / width, "height": (y1 - y0) / height, "pixelWidth": x1 - x0, "pixelHeight": y1 - y0, "centerX": (x0 + x1) / (2 * width), "centerY": (y0 + y1) / (2 * height)},
    }


def road_evidence(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        source = image.convert("RGB")
        width, height = source.size
        pixels = source.load()
        counts = []
        for fraction in (.42, .48, .93, .94):
            y = min(height - 1, max(0, round(fraction * height)))
            runs, current, longest = 0, 0, 0
            for x in range(width):
                red, green, blue = pixels[x, y]
                white = min(red, green, blue) > 150 and max(red, green, blue) - min(red, green, blue) < 22
                if white:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 0
            counts.append({"y": fraction, "width": longest / width, "pixelWidth": longest})
        all_values = list(source.convert("L").getdata())
    return {"crossSections": counts, "p50": percentile(all_values, .50)}


def semantic_roi(image_path: Path, box: dict[str, float]) -> dict[str, float]:
    with Image.open(image_path) as image:
        gray = image.convert("L")
        width, height = gray.size
        x0 = max(0, min(width - 1, int(box["x"] * width)))
        y0 = max(0, min(height - 1, int(box["y"] * height)))
        x1 = max(x0 + 1, min(width, int((box["x"] + box["width"]) * width)))
        y1 = max(y0 + 1, min(height, int((box["y"] + box["height"]) * height)))
        values = list(gray.crop((x0, y0, x1, y1)).getdata())
    return {"p50": percentile(values, .50), "p95": percentile(values, .95), "positivePixels": sum(value > 10 for value in values)}


def depth_evidence(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        gray = image.convert("L")
        width, height = gray.size
        rows = []
        for fraction in (.22, .38, .56, .78):
            y = min(height - 1, round(fraction * height))
            values = [gray.getpixel((x, y)) for x in range(width)]
            changes = sum(abs(right - left) >= 18 for left, right in zip(values, values[1:]))
            rows.append(changes)
        histogram = Counter(gray.getdata())
    return {"rowEdgeCounts": rows, "occlusionBoundaryCount": sum(value > 0 for value in rows), "distinctDepthValues": len(histogram)}


def source_checks(metadata: dict, output: Path) -> tuple[dict[str, bool], dict]:
    paths = {name: Path(value) for name, value in metadata["sourcePaths"].items()}
    a3 = json.loads(paths["a3Metadata"].read_text(encoding="utf-8"))
    a4 = json.loads(paths["a4Metadata"].read_text(encoding="utf-8"))
    a4_verifier = json.loads(paths["a4Verifier"].read_text(encoding="utf-8"))
    checks = {
        "recordedSourceHashes": all(metadata["sourceHashes"][name] == sha256(path) for name, path in paths.items()),
        "seed": metadata["seed"] == 270803,
        "roots": metadata["semanticRoots"] == ROOTS == a3["semanticRoots"],
        "routeExact": metadata["route"] == a3["route"],
        "canyonInvariants": metadata["canyon"] == a3["canyon"],
        "tideScarExact": metadata["tideScar"] == a3["tideScar"] == a4["tideScar"],
        "materialValuesExact": metadata["materialValues"] == a4["materialValues"],
        "triangleBudget": metadata["triangles"] <= 45000,
        "blender455": metadata["blender"].startswith("4.5.5"),
        "a4BaselineFailuresPreserved": metadata["baselineFailures"]["a4FailureNames"] == a4_verifier["failures"] and metadata["baselineFailures"]["portraitActorSeparationPx"] == a4_verifier["portraitActorSeparationPx"],
        "a5OutputOnly": output.name == "a5",
    }
    return checks, {"a3": a3, "a4": a4, "a4Verifier": a4_verifier}


def geometry_checks(audit: dict) -> dict[str, bool]:
    return {
        "decoratedModules": audit["decoratedModules"] == 16,
        "attachedSideFragments": audit["attachedSideMassFragments"] >= 32,
        "signatureRun": audit["longestAdjacentSignatureRun"] <= 2,
        "uniqueCanyonGroups": audit["uniqueCanyonGroupSignatures"] == 20,
        "continuousWalls": audit["continuousWallMeshes"] == 0,
        "clusterRun": audit["longestIdenticalClusterFormRun"] <= 1,
        "pursuerRouteFrame": audit["pursuerRouteFrame"]["behindCourierMetres"] > 0,
        "supportedArch": audit["arch"]["supportCount"] == 2 and audit["arch"]["baseContactsDeck"] is True and audit["arch"]["passableAperture"] is True,
    }


def main() -> None:
    output = Path(arguments().output).resolve()
    metadata_path = output / "a5-clay-metadata.json"
    if not metadata_path.is_file():
        result = {
            "schema": "temple-tr3-a5-clay-verifier-v1",
            "verdict": "BLOCKED",
            "passed": False,
            "sourceChecks": {},
            "geometryChecks": {},
            "frames": {},
            "baselineFailures": {},
            "manualReview": {"required": True, "state": "PENDING_SINGLE_INSPECTION", "cannotOverrideFailure": True, "cannotClaimFinalAcceptance": True},
            "failures": ["generator did not write a5-clay-metadata.json; the sole Blender batch ended after image emission"],
            "notes": ["Fail-closed recovery verdict. No rerender or metadata reconstruction is authorized after the one Blender process."],
        }
        destination = output / "a5-clay-verifier.json"
        destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"verdict": "BLOCKED", "failures": result["failures"], "evidence": str(destination)}, indent=2))
        raise SystemExit(1)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    source, inherited = source_checks(metadata, output)
    for name, passed in source.items():
        if not passed:
            failures.append("source " + name)
    geometry = geometry_checks(metadata["geometryAudit"])
    for name, passed in geometry.items():
        if not passed:
            failures.append("geometry " + name)
    frames: dict[str, dict] = {}
    for name, spec in SPECS.items():
        expected_size = spec["size"]
        paths = {kind: Path(value) for kind, value in metadata["images"][name].items()}
        actual_hashes = {kind: sha256(path) for kind, path in paths.items()}
        if actual_hashes != metadata["imageHashes"][name]:
            failures.append(name + " image hashes")
        with Image.open(paths["beauty"]) as image:
            if image.size != expected_size:
                failures.append(name + " beauty dimensions")
        for kind in ("objectId", "roadMask", "depth"):
            with Image.open(paths[kind]) as image:
                if image.size != expected_size:
                    failures.append(name + " " + kind + " dimensions")
        metrics = luma(paths["beauty"])
        road = road_evidence(paths["roadMask"])
        depth = depth_evidence(paths["depth"])
        masks = {role: role_mask(paths["objectId"], role) for role in ("courier", "pursuer", "hazard", "scar", "near", "mid", "far")}
        projections = metadata["projections"][name]
        for role in ("courier", "pursuer", "hazard"):
            if masks[role]["pixels"] <= 0:
                failures.append(name + " missing " + role + " object-id mask")
        if masks["near"]["pixels"] <= 0 or masks["mid"]["pixels"] <= 0 or masks["far"]["pixels"] <= 0:
            failures.append(name + " missing canyon band ID content")
        if metrics["p50"] <= .12 or metrics["p95"] <= .55 or metrics["nearBlackPercent"] >= 10.0:
            failures.append(name + " luminance")
        if road["p50"] <= .25:
            failures.append(name + " road ROI")
        if depth["occlusionBoundaryCount"] < 2 or depth["distinctDepthValues"] < 12:
            failures.append(name + " depth occlusion evidence")
        courier, pursuer, hazard = projections["courier"], projections["pursuer"], projections["hazard"]
        for role, bands in (("courier", spec["courier"]), ("pursuer", spec["pursuer"]), ("hazard", spec["hazard"])):
            box = projections[role]
            if not bands[0][0] <= box["centerX"] <= bands[0][1] or not bands[1][0] <= box["centerY"] <= bands[1][1]:
                failures.append(name + " " + role + " screen band")
        if hazard["height"] <= spec["height"]:
            failures.append(name + " hazard height")
        aperture_width = metadata["apertureProjections"][name]["width"]
        if aperture_width <= spec["opening"]:
            failures.append(name + " aperture width")
        if name == "portrait":
            if not contained(pursuer, .02) or pursuer["pixelWidth"] < 32:
                failures.append("portrait pursuer containment/width")
            if overlap(courier, pursuer) < .045:
                failures.append("portrait actor overlap")
            gap = pursuer["y"] - (courier["y"] + courier["height"])
            if not .020 <= gap <= .075:
                failures.append("portrait actor gap")
        for role in ("courier", "pursuer", "hazard"):
            roi = semantic_roi(paths["beauty"], projections[role])
            if roi["positivePixels"] <= 0 or roi["p95"] <= 10 / 255:
                failures.append(name + " non-positive " + role + " beauty ROI")
            masks[role]["beautyRoi"] = roi
        scar_evidence = metadata["tideScarMaskEvidence"][name]
        if scar_evidence["extractor"] != "actual editable curve/spline control points" or scar_evidence["visibleRunCount"] < 2:
            failures.append(name + " Tide Scar curve extractor/runs")
        if masks["scar"]["pixels"] <= 0:
            failures.append(name + " Tide Scar object-id mask")
        frames[name] = {"hashes": actual_hashes, "luminance": metrics, "road": road, "depth": depth, "masks": masks, "projections": projections, "apertureWidthNormalized": aperture_width}
    close_path = Path(metadata["images"]["closeup"]["beauty"])
    close_hash = sha256(close_path)
    with Image.open(close_path) as image:
        if image.size != (640, 480):
            failures.append("closeup dimensions")
    closeup = metadata["projections"]["closeup"]["pursuer"]
    if not contained(closeup) or closeup["pixelWidth"] < 48:
        failures.append("closeup pursuer containment/width")
    verdict = "READY_FOR_VISUAL_REVIEW" if not failures else "BLOCKED"
    result = {
        "schema": "temple-tr3-a5-clay-verifier-v1",
        "verdict": verdict,
        "passed": not failures,
        "sourceChecks": source,
        "geometryChecks": geometry,
        "frames": frames,
        "closeup": {"sha256": close_hash, "projections": metadata["projections"]["closeup"], "beautyLuminance": luma(close_path)},
        "baselineFailures": metadata["baselineFailures"],
        "manualReview": {"required": True, "state": "PENDING_SINGLE_INSPECTION", "cannotOverrideFailure": True, "cannotClaimFinalAcceptance": True},
        "failures": failures,
        "notes": [
            "Object-ID, road-mask, and depth files are bound by image hashes and come from the same Blender scene/cameras as beauty.",
            "Tide Scar evidence is extracted from CURVE spline control points, never a mesh-only bounding-box proxy.",
            "READY_FOR_VISUAL_REVIEW is not final visual or runtime acceptance.",
        ],
    }
    destination = output / "a5-clay-verifier.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "failures": failures, "evidence": str(destination)}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
