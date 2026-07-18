"""Combined deterministic and manual gate for the single TEMPLE-TR3-A4 clay batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOTS = ["Causeway_Root", "Canyon_Root", "Runner_Root", "Pursuer_Root", "Obstacle_Ring_Root", "TideScar_Ribbon_Editable"]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--manual-verdict", required=True, choices=("PASS", "BLOCKED"))
    parser.add_argument("--manual-note", required=True)
    return parser.parse_args()


def contained(box: dict[str, float], margin: float = 0.0) -> bool:
    return box["width"] > 0.0 and box["height"] > 0.0 and box["x"] >= margin and box["y"] >= margin and box["x"] + box["width"] <= 1.0 - margin and box["y"] + box["height"] <= 1.0 - margin


def overlap(first: dict[str, float], second: dict[str, float]) -> float:
    return min(first["x"] + first["width"], second["x"] + second["width"]) - max(first["x"], second["x"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    args = arguments()
    output = Path(args.output).resolve()
    metadata = json.loads((output / "a4-clay-metadata.json").read_text(encoding="utf-8"))
    a3_path = Path(metadata["derivedFrom"]["metadata"])
    a3 = json.loads(a3_path.read_text(encoding="utf-8"))
    files = {"portrait": output / "a4-clay-portrait.png", "desktop": output / "a4-clay-desktop.png", "closeup": output / "a4-clay-closeup.png"}
    failures = list(metadata["gateFailures"])
    frames: dict[str, dict] = {}
    for name, path in files.items():
        with Image.open(path) as image:
            frames[name] = {"width": image.width, "height": image.height, "sha256": sha256(path), "projections": metadata["projections"][name], "aperture": metadata["apertureProjections"][name]}

    source_checks = {
        "a3GeneratorHash": metadata["derivedFrom"]["generatorSha256"] == sha256(Path(__file__).with_name("generate_tide_scar_hero_a3.py")),
        "routeExact": metadata["route"] == a3["route"] and metadata["a3StructuralComparison"]["routeExact"] is True and metadata["route"]["moduleCount"] == 16,
        "canyonExact": metadata["canyon"] == a3["canyon"] and metadata["a3StructuralComparison"]["canyonExact"] is True and metadata["canyon"]["bandCount"] == 3,
        "tideScarExact": metadata["tideScar"] == a3["tideScar"] and metadata["a3StructuralComparison"]["tideScarExact"] is True,
        "semanticRoots": metadata["semanticRoots"] == ROOTS,
        "triangles": metadata["triangles"] <= 45000,
        "blender455": metadata["blender"].startswith("4.5.5"),
    }
    for name, passed in source_checks.items():
        if not passed:
            failures.append("source " + name)

    portrait = frames["portrait"]
    closeup = frames["closeup"]
    courier, pursuer = portrait["projections"]["courier"], portrait["projections"]["pursuer"]
    if not contained(pursuer, .02) or pursuer["pixelWidth"] < 32.0:
        failures.append("portrait pursuer containment or width")
    closeup_pursuer = closeup["projections"]["pursuer"]
    if not contained(closeup_pursuer) or closeup_pursuer["pixelWidth"] < 48.0:
        failures.append("closeup pursuer containment or width")
    if not .60 <= courier["centerY"] <= .68:
        failures.append("portrait courier centerY")
    if not .70 <= pursuer["centerY"] <= .79:
        failures.append("portrait pursuer centerY")
    separation_px = (pursuer["y"] - (courier["y"] + courier["height"])) * portrait["height"]
    horizontal_overlap = overlap(courier, pursuer)
    if separation_px < 12.0:
        failures.append("portrait actor separation")
    if horizontal_overlap <= 0.0:
        failures.append("portrait actor road-band overlap")

    for frame_name in ("portrait", "desktop"):
        frame = frames[frame_name]
        projection = frame["projections"]
        if not all(contained(projection[key]) for key in ("ring", "arch", "supportLeft", "supportRight")):
            failures.append(frame_name + " arch/support containment")
        if projection["ring"]["height"] < .12 or projection["arch"]["height"] < .12:
            failures.append(frame_name + " arch height")
        if frame["aperture"]["width"] < .07:
            failures.append(frame_name + " aperture width")
    if metadata["ring"]["openingToOuterArea"] < .38:
        failures.append("arch aperture area")
    if args.manual_verdict != "PASS":
        failures.append("manual first-glance review")

    result = {
        "schema": "temple-tr3-a4-clay-verifier-v1",
        "passed": not failures,
        "sourceChecks": source_checks,
        "portraitActorSeparationPx": round(separation_px, 2),
        "portraitHorizontalRoadBandOverlap": round(horizontal_overlap, 5),
        "frames": frames,
        "ring": metadata["ring"],
        "manualReview": {"verdict": args.manual_verdict, "note": args.manual_note, "requiredRead": "supported broken-stone opening"},
        "failures": failures,
        "notes": ["Projection bounds come from the actual one-shot Blender scene; image dimensions and hashes bind the evidence to the rendered frames.", "No final materials, export, runtime, browser, commit, push, or QA activity follows this clay gate."],
    }
    destination = output / "a4-clay-verifier.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "evidence": str(destination), "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
