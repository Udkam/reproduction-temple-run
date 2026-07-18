"""Post-process a completed A2 final render without re-rendering Blender."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path


ROOTS = ["Causeway_Root", "Canyon_Root", "Runner_Root", "Pursuer_Root", "Obstacle_Ring_Root", "TideScar_Ribbon_Editable"]
TOKTX = Path(r"C:\Program Files\KTX-Software\bin\toktx.exe")
KTX = Path(r"C:\Program Files\KTX-Software\bin\ktx.exe")


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def execute(command: list[str], log: Path) -> str:
    process = subprocess.run(command, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    text = "$ " + " ".join(command) + "\n" + process.stdout + process.stderr
    log.write_text(text, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(command)}")
    return text


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def glb_json(path: Path) -> dict:
    with path.open("rb") as stream:
        magic, version, length = struct.unpack("<4sII", stream.read(12))
        if magic != b"glTF" or version != 2 or length != path.stat().st_size:
            raise RuntimeError(f"invalid GLB header: {path}")
        chunk_length, chunk_type = struct.unpack("<I4s", stream.read(8))
        if chunk_type != b"JSON":
            raise RuntimeError(f"GLB missing JSON chunk: {path}")
        return json.loads(stream.read(chunk_length).decode("utf-8"))


def metrics(path: Path) -> dict:
    data = glb_json(path)
    triangles = 0
    accessors = data.get("accessors", [])
    for mesh in data.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) == 4 and "indices" in primitive:
                triangles += accessors[primitive["indices"]]["count"] // 3
    names = [node.get("name") for node in data.get("nodes", [])]
    missing = [root for root in ROOTS if root not in names]
    if missing:
        raise RuntimeError(f"semantic roots missing from {path.name}: {missing}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path), "triangles": triangles, "materials": len(data.get("materials", [])), "textures": len(data.get("textures", [])), "images": len(data.get("images", [])), "semanticRoots": ROOTS, "nodeCount": len(data.get("nodes", []))}


def main() -> None:
    out = Path(args().output).resolve()
    source = out / "tide-scar-hero-a2.unoptimized.glb"
    optimized = out / "tide-scar-hero-a2.meshopt.glb"
    if not source.is_file():
        raise RuntimeError(f"missing A2 source GLB: {source}")
    logs = out / "validation"
    logs.mkdir(parents=True, exist_ok=True)
    execute(["gltf-transform.cmd", "validate", str(source)], logs / "source-validate.txt")
    execute(["gltf-transform.cmd", "inspect", str(source)], logs / "source-inspect.txt")
    execute([
        "gltf-transform.cmd", "optimize", str(source), str(optimized), "--compress", "meshopt", "--flatten", "false",
        "--instance", "false", "--join", "false", "--join-meshes", "false", "--join-named", "false", "--palette", "false",
        "--prune", "false", "--simplify", "false", "--texture-compress", "false",
    ], logs / "meshopt-optimize.txt")
    execute(["gltf-transform.cmd", "validate", str(optimized)], logs / "optimized-validate.txt")
    execute(["gltf-transform.cmd", "inspect", str(optimized)], logs / "optimized-inspect.txt")
    ktx_records = []
    for image in sorted((out / "textures").glob("*.png")):
        is_data = any(part in image.stem for part in ("normal", "orm", "mask"))
        target = image.with_suffix(".ktx2")
        command = [str(TOKTX), "--t2", "--genmipmap", "--assign_oetf", "linear" if is_data else "srgb", "--encode", "uastc" if is_data else "etc1s"]
        if is_data:
            command.extend(("--zcmp", "12"))
        command.extend((str(target), str(image)))
        execute(command, logs / (image.stem + "-toktx.txt"))
        execute([str(KTX), "validate", str(target)], logs / (image.stem + "-ktx-validate.txt"))
        ktx_records.append({"source": image.name, "ktx2": target.name, "bytes": target.stat().st_size, "sha256": sha(target), "colorSpace": "linear" if is_data else "sRGB"})
    source_metrics, optimized_metrics = metrics(source), metrics(optimized)
    readability = json.loads((out / "a2-final-readability.json").read_text(encoding="utf-8"))
    final_images = [out / "portrait-hero.png", out / "desktop-hero.png", out / "runner-pursuer-obstacle-closeup.png"]
    manifest = {
        "schema": "temple-tr3-a2-asset-manifest-v1",
        "generator": "generate_tide_scar_hero_a2.py",
        "cleanRoom": True,
        "units": "metres", "axes": {"forward": "+Y", "up": "+Z", "right": "+X"},
        "semanticRoots": ROOTS,
        "pivotsAndSockets": json.loads((out / "a2-scene-metadata.json").read_text(encoding="utf-8"))["semanticHandoff"],
        "textureMapping": json.loads((out / "a2-scene-metadata.json").read_text(encoding="utf-8"))["textureMapping"],
        "source": source_metrics, "optimized": optimized_metrics, "ktx2": ktx_records,
        "renders": [{"path": image.name, "sha256": sha(image), "bytes": image.stat().st_size} for image in final_images],
        "readability": readability,
        "budgets": {"unoptimizedTrianglesMax": 180000, "optimizedTrianglesMax": 120000, "materialsMax": 8, "boundImagesMax": 8, "optimizedBytesMax": 8 * 1024 * 1024},
    }
    failures = []
    if source_metrics["triangles"] > 180000: failures.append("source triangle budget")
    if optimized_metrics["triangles"] > 120000: failures.append("optimized triangle budget")
    if optimized_metrics["materials"] > 8: failures.append("material budget")
    if optimized_metrics["images"] > 8: failures.append("image budget")
    if optimized_metrics["bytes"] > 8 * 1024 * 1024: failures.append("optimized byte budget")
    if not readability.get("passed"): failures.append("final pixel/readability gate")
    manifest["passed"] = not failures
    manifest["failures"] = failures
    destination = out / "a2-asset-manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": manifest["passed"], "manifest": str(destination), "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
