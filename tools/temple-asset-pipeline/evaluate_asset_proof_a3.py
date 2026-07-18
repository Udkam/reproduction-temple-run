"""Deterministic Pillow and metadata gate for the one A3 clay batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def percentile(values: list[int], ratio: float) -> float:
    values.sort()
    return values[min(len(values) - 1, int((len(values) - 1) * ratio))] / 255.0


def luminance_roi(image: Image.Image, bbox: dict[str, float]) -> dict[str, float | list[int]]:
    gray = image.convert("RGB").convert("L")
    width, height = gray.size
    x0 = max(0, min(width - 1, round(bbox["x"] * width)))
    y0 = max(0, min(height - 1, round(bbox["y"] * height)))
    x1 = max(x0 + 1, min(width, round((bbox["x"] + bbox["width"]) * width)))
    y1 = max(y0 + 1, min(height, round((bbox["y"] + bbox["height"]) * height)))
    values = list(gray.crop((x0, y0, x1, y1)).getdata())
    return {"box": [x0, y0, x1, y1], "p50": percentile(values, .5), "p95": percentile(values, .95), "contrast": (max(values) - min(values)) / 255.0}


def gap_pixels(upper: dict[str, float], lower: dict[str, float], height: int) -> float:
    return (lower["y"] - (upper["y"] + upper["height"])) * height


def main() -> None:
    output = Path(arguments().output).resolve()
    metadata = json.loads((output / "a3-clay-metadata.json").read_text(encoding="utf-8"))
    files = {"portrait": output / "a3-clay-portrait.png", "desktop": output / "a3-clay-desktop.png", "closeup": output / "a3-clay-closeup.png"}
    frames: dict[str, dict] = {}
    failures = list(metadata["gateFailures"])
    route, canyon, ring = metadata["route"], metadata["canyon"], metadata["ring"]
    source_checks = {
        "deckModules": route["moduleCount"] >= 14,
        "canyonBands": canyon["bandCount"] >= 3,
        "elevationSteps": route["broadRises"] >= 3,
        "fractureJoints": route["jointCount"] >= 8,
        "wallOccupancy": canyon["maxNearWallOccupancy"] <= .22,
        "ringAperture": ring["openingToOuterArea"] >= .38,
        "triangles": metadata["triangles"] <= 45000,
        "semanticRoots": metadata["semanticRoots"] == ["Causeway_Root", "Canyon_Root", "Runner_Root", "Pursuer_Root", "Obstacle_Ring_Root", "TideScar_Ribbon_Editable"],
    }
    for name, path in files.items():
        with Image.open(path) as source:
            image = source.convert("RGB")
            values = list(image.convert("L").getdata())
            projections = metadata["projections"][name]
            frame = {
                "width": image.width, "height": image.height,
                "p50": percentile(values, .5), "p95": percentile(values, .95),
                "nearBlackPercent": sum(value <= 10 for value in values) / len(values) * 100.0,
                "semanticRois": {key: luminance_roi(image, projections[key]) for key in ("courier", "pursuer", "ring")},
                "projections": projections,
            }
            frames[name] = frame
            if frame["p50"] < .12 or frame["p95"] < .30:
                failures.append(name + " clay luminance")
            for key in ("courier", "pursuer", "ring"):
                box = projections[key]
                if box["width"] <= 0 or box["height"] <= 0:
                    failures.append(name + " " + key + " non-positive bbox")
    portrait = frames["portrait"]
    desktop = frames["desktop"]
    portrait_projections = portrait["projections"]
    desktop_projections = desktop["projections"]
    courier, pursuer, portrait_ring = portrait_projections["courier"], portrait_projections["pursuer"], portrait_projections["ring"]
    actor_gap = gap_pixels(courier, pursuer, portrait["height"])
    if not .60 <= courier["centerY"] <= .68: failures.append("portrait courier raster band")
    if not .70 <= pursuer["centerY"] <= .79: failures.append("portrait pursuer raster band")
    if not .34 <= portrait_ring["centerY"] <= .48: failures.append("portrait ring raster band")
    if portrait_ring["height"] < .12 or desktop_projections["ring"]["height"] < .12: failures.append("ring raster height")
    if actor_gap < 12.0: failures.append("portrait actor separation")
    if courier["x"] + courier["width"] <= pursuer["x"] or pursuer["x"] + pursuer["width"] <= courier["x"]:
        failures.append("actors not in same road band")
    for check, passed in source_checks.items():
        if not passed:
            failures.append("source gate " + check)
    result = {
        "schema": "temple-tr3-a3-clay-verifier-v1",
        "passed": not failures,
        "sourceChecks": source_checks,
        "portraitActorSeparationPx": round(actor_gap, 2),
        "frames": frames,
        "failures": failures,
        "notes": ["Pillow records rendered luminance/semantic ROI evidence; Blender source projection records the real camera-space semantic bounds.", "Manual structural review remains mandatory and can block a numerically passing batch."],
    }
    destination = output / "a3-clay-verifier.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "evidence": str(destination), "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
