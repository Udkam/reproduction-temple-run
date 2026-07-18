"""Fail-closed Pillow readability evidence for the isolated A2 proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageStat


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("clay", "final"), required=True)
    return parser.parse_args()


def luminance(image: Image.Image) -> Image.Image:
    return image.convert("RGB").convert("L")


def percentile(values: list[int], ratio: float) -> float:
    values = sorted(values)
    return values[min(len(values) - 1, int((len(values) - 1) * ratio))] / 255.0


def stats(path: Path, rois: dict[str, tuple[float, float, float, float]]) -> dict:
    with Image.open(path) as source:
        image = luminance(source)
        values = list(image.getdata())
        width, height = image.size
        roi_stats = {}
        for label, (x0, y0, x1, y1) in rois.items():
            box = (round(width * x0), round(height * y0), round(width * x1), round(height * y1))
            crop = image.crop(box)
            crop_values = list(crop.getdata())
            roi_stats[label] = {"box": box, "p50": percentile(crop_values, .5), "p95": percentile(crop_values, .95), "contrast": (max(crop_values) - min(crop_values)) / 255.0}
        return {"path": str(path), "width": width, "height": height, "p50": percentile(values, .5), "p95": percentile(values, .95), "nearBlackPercent": sum(v <= 10 for v in values) / len(values) * 100.0, "rois": roi_stats}


def main() -> None:
    parsed = args()
    out = Path(parsed.output).resolve()
    frames = {
        "portrait": out / ("a2-clay-portrait.png" if parsed.mode == "clay" else "portrait-hero.png"),
        "desktop": out / ("a2-clay-desktop.png" if parsed.mode == "clay" else "desktop-hero.png"),
        "closeup": out / ("a2-clay-silhouette-closeup.png" if parsed.mode == "clay" else "runner-pursuer-obstacle-closeup.png"),
    }
    rois = {
        "road": (0.19, .47, .81, .98), "runner": (.38, .47, .62, .74),
        "pursuer": (.23, .63, .77, .98), "ring": (.34, .23, .66, .57),
        "canyon": (.03, .12, .97, .58),
    }
    evidence = {name: stats(path, rois) for name, path in frames.items()}
    clay_rules = []
    for value in evidence.values():
        clay_rules.extend((
            value["p50"] >= .12, value["p95"] >= .34, value["nearBlackPercent"] < 18.0,
            value["rois"]["road"]["contrast"] >= .12,
            value["rois"]["runner"]["contrast"] >= .08,
            value["rois"]["pursuer"]["contrast"] >= .08,
            value["rois"]["ring"]["contrast"] >= .08,
            value["rois"]["canyon"]["contrast"] >= .10,
        ))
    final_rules = []
    for value in evidence.values():
        final_rules.extend((
            value["p50"] >= .16, value["p95"] >= .48, value["nearBlackPercent"] < 12.0,
            value["rois"]["road"]["p50"] >= .20,
            value["rois"]["runner"]["contrast"] >= .10,
            value["rois"]["pursuer"]["contrast"] >= .10,
            value["rois"]["ring"]["contrast"] >= .10,
        ))
    passed = all(clay_rules if parsed.mode == "clay" else final_rules)
    payload = {
        "schema": "temple-tr3-a2-pillow-readability-v1", "mode": parsed.mode,
        "passed": passed, "frames": evidence,
        "notes": [
            "ROIs are declared camera-space evidence regions, not fabricated runtime bounds.",
            "Numeric readability cannot replace the required manual structural/blockout review.",
        ],
    }
    destination = out / ("a2-clay-readability.json" if parsed.mode == "clay" else "a2-final-readability.json")
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "evidence": str(destination)}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
