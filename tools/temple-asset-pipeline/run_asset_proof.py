"""Bounded offline post-process for the Blender-generated A0 hero asset proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe")
GENERATOR = ROOT / "tools" / "temple-asset-pipeline" / "generate_tide_scar_hero.py"
EVALUATOR = ROOT / "tools" / "temple-asset-pipeline" / "evaluate_asset_proof.py"


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(command, cwd=cwd, check=True, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return completed.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def glb_metrics(path: Path) -> dict[str, object]:
    """Read GLB JSON directly so the manifest records evaluated export metrics."""
    payload = path.read_bytes()
    if payload[:4] != b"glTF":
        raise RuntimeError("Not a GLB: " + str(path))
    offset = 12
    document = None
    while offset < len(payload):
        length = int.from_bytes(payload[offset : offset + 4], "little")
        kind = int.from_bytes(payload[offset + 4 : offset + 8], "little")
        chunk = payload[offset + 8 : offset + 8 + length]
        if kind == 0x4E4F534A:
            document = json.loads(chunk.decode("utf-8"))
            break
        offset += 8 + length
    if document is None:
        raise RuntimeError("GLB has no JSON chunk: " + str(path))
    accessors = document.get("accessors", [])
    triangles = 0
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            count = accessors[primitive["indices"]]["count"] if "indices" in primitive else accessors[primitive["attributes"]["POSITION"]]["count"]
            mode = primitive.get("mode", 4)
            triangles += count // 3 if mode == 4 else max(0, count - 2) if mode in (5, 6) else 0
    return {
        "triangles": triangles,
        "meshes": len(document.get("meshes", [])),
        "nodes": len(document.get("nodes", [])),
        "materials": len(document.get("materials", [])),
        "textures": len(document.get("textures", [])),
        "extensionsUsed": document.get("extensionsUsed", []),
        "namedRootsPresent": sorted(name for name in metadata_roots(document) if name),
    }


def metadata_roots(document: dict[str, object]) -> list[str]:
    expected = {"Causeway_Root", "Canyon_Root", "Runner_Root", "Pursuer_Root", "Obstacle_Ring_Root", "TideScar_Ribbon_Editable"}
    return [node.get("name", "") for node in document.get("nodes", []) if isinstance(node, dict) and node.get("name") in expected]


def command_path(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError("Required executable is unavailable: " + name)
    return resolved


def ktx_path() -> str:
    candidate = Path(r"C:\Program Files\KTX-Software\bin\toktx.exe")
    if not candidate.exists():
        raise RuntimeError("Required KTX encoder is unavailable: " + str(candidate))
    return str(candidate)


def ktx_validate_path() -> str:
    candidate = Path(r"C:\Program Files\KTX-Software\bin\ktx.exe")
    if not candidate.exists():
        raise RuntimeError("Required KTX validator is unavailable: " + str(candidate))
    return str(candidate)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--stage", choices=("draft", "final"), required=True)
    parser.add_argument("--reuse-generated", action="store_true", help="Skip Blender and post-process an already generated final source once.")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = output / "tide-scar-hero.unoptimized.glb"
    if args.reuse_generated:
        if not source.exists():
            raise RuntimeError("--reuse-generated requires an existing unoptimized GLB")
    else:
        blender_log = run([str(BLENDER), "--background", "--python-exit-code", "1", "--python", str(GENERATOR), "--", "--stage", args.stage, "--output", str(output)], ROOT)
        (output / "blender-{}.log".format(args.stage)).write_text(blender_log, encoding="utf-8")
    if not source.exists():
        raise RuntimeError("Blender did not emit the required unoptimized GLB")
    gltf = command_path("gltf-transform.cmd")
    meshopt = output / "tide-scar-hero.meshopt.glb"
    inspect_unoptimized = run([gltf, "inspect", str(source)], ROOT)
    validate_unoptimized = run([gltf, "validate", str(source)], ROOT)
    optimize = run([gltf, "optimize", str(source), str(meshopt), "--compress", "meshopt", "--texture-compress", "false"], ROOT)
    inspect_meshopt = run([gltf, "inspect", str(meshopt)], ROOT)
    validate_meshopt = run([gltf, "validate", str(meshopt)], ROOT)
    (output / "gltf-transform-inspect-unoptimized.txt").write_text(inspect_unoptimized, encoding="utf-8")
    (output / "gltf-transform-validate-unoptimized.txt").write_text(validate_unoptimized, encoding="utf-8")
    (output / "gltf-transform-optimize-meshopt.txt").write_text(optimize, encoding="utf-8")
    (output / "gltf-transform-inspect-meshopt.txt").write_text(inspect_meshopt, encoding="utf-8")
    (output / "gltf-transform-validate-meshopt.txt").write_text(validate_meshopt, encoding="utf-8")
    pixel_log = run([sys.executable, str(EVALUATOR), "--output", str(output), "--mode", "final"], ROOT)
    pixel_evidence = json.loads((output / "final-pixel-evidence.json").read_text(encoding="utf-8"))
    toktx = ktx_path()
    ktx = ktx_validate_path()
    texture_records = []
    for png in sorted((output / "textures").glob("*.png")):
        destination = png.with_suffix(".ktx2")
        encode = run([toktx, "--t2", "--uastc", "--genmipmap", str(destination), str(png)], ROOT)
        validate = run([ktx, "validate", str(destination)], ROOT)
        (destination.with_suffix(".toktx.txt")).write_text(encode, encoding="utf-8")
        (destination.with_suffix(".ktx.validate.txt")).write_text(validate, encoding="utf-8")
        texture_records.append({"png": png.name, "ktx2": destination.name, "bytes": destination.stat().st_size, "sha256": sha256(destination), "validation": "passed"})
    metadata = json.loads((output / "scene-metadata.json").read_text(encoding="utf-8"))
    file_records = []
    proof_images = [output / "portrait-hero.png", output / "desktop-hero.png", output / "runner-pursuer-obstacle-closeup.png"]
    for path in sorted(output.glob("*.glb")) + sorted(output.glob("*.blend")) + [path for path in proof_images if path.exists()]:
        file_records.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schema": "temple-tr3-a0-asset-proof-v1",
        "stage": args.stage,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "cleanRoom": "Generated locally from versioned Blender Python; no reference or commercial pixels/models are input.",
        "source": metadata,
        "tools": {
            "blender": str(BLENDER),
            "gltfTransform": gltf,
            "toktx": toktx,
            "ktx": ktx,
        },
        "glbValidation": {"unoptimized": "passed", "meshopt": "passed", "meshoptCompression": True},
        "glbMetrics": {"unoptimized": glb_metrics(source), "meshopt": glb_metrics(meshopt)},
        "pixelEvidence": pixel_evidence,
        "files": file_records,
        "proofTextures": texture_records,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checksums = "\n".join("{}  {}".format(record["sha256"], record["file"]) for record in file_records + [{"file": item["ktx2"], "sha256": item["sha256"]} for item in texture_records]) + "\n"
    (output / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")


if __name__ == "__main__":
    main()
