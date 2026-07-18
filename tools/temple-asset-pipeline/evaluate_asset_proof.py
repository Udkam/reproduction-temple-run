"""Fail-closed Pillow luma and declared-ROI evidence for A1 asset renders."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


THRESHOLDS = {
    "globalP50": 0.12,
    "globalP95": 0.55,
    "nearBlackFraction": 0.10,
    "roadP50": 0.25,
    "semanticP95": 0.18,
}

# Fractions are declared camera-space audit windows, not fabricated object bounds.
ROIS = {
    "portrait": {
        "road": (0.32, 0.30, 0.69, 0.98),
        "runner": (0.40, 0.48, 0.60, 0.76),
        "pursuer": (0.27, 0.65, 0.73, 0.99),
        "ring": (0.35, 0.28, 0.65, 0.56),
    },
    "desktop": {
        "road": (0.33, 0.27, 0.67, 0.99),
        "runner": (0.40, 0.48, 0.60, 0.76),
        "pursuer": (0.28, 0.63, 0.72, 0.99),
        "ring": (0.36, 0.25, 0.64, 0.56),
    },
    "closeup": {
        "road": (0.12, 0.57, 0.98, 0.99),
        "runner": (0.66, 0.05, 0.98, 0.50),
        "pursuer": (0.16, 0.14, 0.78, 0.88),
    },
}


def luma_values(image: Image.Image) -> list[float]:
    rgb = image.convert("RGB")
    return [(0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255.0 for red, green, blue in rgb.getdata()]


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * fraction))]


def bounds(width: int, height: int, roi: tuple[float, float, float, float]) -> list[int]:
    left, top, right, bottom = roi
    return [round(left * width), round(top * height), round(right * width), round(bottom * height)]


def analyze(path: Path, kind: str) -> dict[str, object]:
    image = Image.open(path)
    values = luma_values(image)
    record: dict[str, object] = {
        "file": path.name,
        "width": image.width,
        "height": image.height,
        "global": {
            "p50": percentile(values, 0.50),
            "p95": percentile(values, 0.95),
            "nearBlackFraction": sum(value <= 10 / 255.0 for value in values) / len(values),
        },
        "rois": {},
    }
    for name, roi in ROIS[kind].items():
        crop = image.crop(bounds(image.width, image.height, roi))
        luma = luma_values(crop)
        record["rois"][name] = {"fraction": roi, "bounds": bounds(image.width, image.height, roi), "p50": percentile(luma, 0.50), "p95": percentile(luma, 0.95)}
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("diagnostic", "final"), required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if args.mode == "diagnostic":
        files = {"portrait": output / "diagnostic-portrait.png", "desktop": output / "diagnostic-desktop.png", "closeup": output / "diagnostic-closeup.png"}
        scene_metadata_path = output / "diagnostic-scene-metadata.json"
    else:
        files = {"portrait": output / "portrait-hero.png", "desktop": output / "desktop-hero.png", "closeup": output / "runner-pursuer-obstacle-closeup.png"}
        scene_metadata_path = output / "scene-metadata.json"
    for file in files.values():
        if not file.exists():
            raise SystemExit("Missing image: " + str(file))
    records = {kind: analyze(file, kind) for kind, file in files.items()}
    combined = [value for record in records.values() for value in (Image.open(output / record["file"]).convert("L").getdata())]
    global_values = [value / 255.0 for value in combined]
    scene_metadata = json.loads(scene_metadata_path.read_text(encoding="utf-8"))
    gates = {
        "globalP50": percentile(global_values, 0.50) >= THRESHOLDS["globalP50"],
        "globalP95": percentile(global_values, 0.95) >= THRESHOLDS["globalP95"],
        "nearBlackFraction": sum(value <= 10 / 255.0 for value in global_values) / len(global_values) < THRESHOLDS["nearBlackFraction"],
        "roadP50": all(record["rois"]["road"]["p50"] >= THRESHOLDS["roadP50"] for record in records.values()),
        "semanticReadability": all(record["rois"][name]["p95"] >= THRESHOLDS["semanticP95"] for record in records.values() for name in record["rois"] if name != "road"),
        "mistBands": scene_metadata.get("renderRepair", {}).get("mistBandCount") == 0,
    }
    payload = {"schema": "temple-tr3-a1-pixel-evidence-v1", "mode": args.mode, "thresholds": THRESHOLDS, "images": records, "combined": {"p50": percentile(global_values, 0.50), "p95": percentile(global_values, 0.95), "nearBlackFraction": sum(value <= 10 / 255.0 for value in global_values) / len(global_values)}, "gates": gates, "passed": all(gates.values())}
    destination = output / ("diagnostic-pixel-evidence.json" if args.mode == "diagnostic" else "final-pixel-evidence.json")
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not payload["passed"]:
        raise SystemExit("A1 pixel gates failed; see " + str(destination))


if __name__ == "__main__":
    main()
