"""Blender 4.5.5 material socket introspection for TEMPLE-TR4 probe 001."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import bpy


EXPECTED_BLENDER_VERSION = "4.5.5 LTS"
EXPECTED_PROBE_ID = "001"
EXPECTED_INPUT_SCHEMA = "tide-relay.temple-tr4.material-socket-probe-input"
EXPECTED_EXECUTABLE_SHA256 = "597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c"
HASH_ARGUMENTS = (
    "contract_sha256",
    "input_sha256",
    "evidence_schema_sha256",
    "status_schema_sha256",
    "runner_sha256",
    "generator_sha256",
    "blender_executable_sha256",
)


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


def strict_json_object(data: bytes, label: str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError(f"duplicate JSON key in {label}: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid UTF-8 JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root must be an object: {label}")
    if data != canonical_bytes(value):
        raise RuntimeError(f"JSON is not canonical: {label}")
    return value


def require_hash(value: str, label: str) -> str:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise RuntimeError(f"invalid SHA-256: {label}")
    return value


def normalize_number(value: int | float) -> int | float:
    if isinstance(value, bool):
        raise RuntimeError("boolean entered numeric normalization")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RuntimeError("non-finite comparable number")
        if value == 0.0:
            return 0.0
    return value


def comparable_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return normalize_number(value)
    if isinstance(value, (list, tuple)):
        source = list(value)
    else:
        try:
            source = list(value)
        except TypeError as exc:
            raise RuntimeError(f"unsupported comparable value type: {type(value).__name__}") from exc
    result = [comparable_value(item) for item in source]
    if any(isinstance(item, list) or item is None for item in result):
        raise RuntimeError("comparable arrays must be flat non-null scalars")
    return result


def values_match(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1.0e-6
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(values_match(a, b) for a, b in zip(left, right))
    return type(left) is type(right) and left == right


def default_value_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "NUMBER"
    if isinstance(value, str):
        return "STRING"
    if isinstance(value, list):
        if not value:
            raise RuntimeError("empty comparable array has no closed type")
        if all(isinstance(item, bool) for item in value):
            return "BOOLEAN_ARRAY"
        if all(isinstance(item, int) and not isinstance(item, bool) for item in value):
            return "INTEGER_ARRAY"
        if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            return "NUMBER_ARRAY"
        if all(isinstance(item, str) for item in value):
            return "STRING_ARRAY"
    raise RuntimeError(f"unsupported closed default value type: {type(value).__name__}")


def resolve_property(node: Any, dotted_name: str) -> tuple[Any, str]:
    parts = dotted_name.split(".")
    owner = node
    for part in parts[:-1]:
        owner = getattr(owner, part)
    return owner, parts[-1]


def apply_properties(
    records: list[dict[str, Any]],
    nodes_by_name: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if set(record.keys()) != {"node", "property", "value"}:
            raise RuntimeError(f"property assignment schema mismatch: {index}")
        node = nodes_by_name[record["node"]]
        owner, attribute = resolve_property(node, record["property"])
        before = comparable_value(getattr(owner, attribute))
        requested = comparable_value(record["value"])
        setattr(owner, attribute, record["value"])
        after = comparable_value(getattr(owner, attribute))
        matches = values_match(after, requested)
        if not matches:
            raise RuntimeError(f"property readback mismatch: {record['node']}.{record['property']}")
        evidence.append(
            {
                "index": index,
                "node": record["node"],
                "property": record["property"],
                "before": before,
                "requested": requested,
                "after": after,
                "matchesRequested": True,
            }
        )
    return evidence


def socket_record(socket: Any, index: int, occurrence_count: int) -> dict[str, Any]:
    supports_default = hasattr(socket, "default_value")
    if supports_default:
        default_value = comparable_value(socket.default_value)
        type_name = default_value_type(default_value)
    else:
        default_value = None
        type_name = "NONE"
    return {
        "index": index,
        "name": str(socket.name),
        "identifier": str(socket.identifier),
        "nameOccurrenceCount": occurrence_count,
        "socketRnaIdentifier": str(socket.bl_rna.identifier),
        "enabled": bool(socket.enabled),
        "hidden": bool(socket.hide),
        "linked": bool(socket.is_linked),
        "supportsDefaultValue": supports_default,
        "defaultValueType": type_name,
        "defaultValue": default_value,
    }


def enumerate_nodes(node_order: list[str], nodes_by_name: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for node_index, name in enumerate(node_order):
        node = nodes_by_name[name]
        sockets = list(node.inputs)
        name_counts = {
            socket_name: sum(1 for candidate in sockets if str(candidate.name) == socket_name)
            for socket_name in {str(candidate.name) for candidate in sockets}
        }
        evidence.append(
            {
                "index": node_index,
                "name": name,
                "nodeType": str(node.bl_idname),
                "inputs": [
                    socket_record(socket, socket_index, name_counts[str(socket.name)])
                    for socket_index, socket in enumerate(sockets)
                ],
            }
        )
    return evidence


def absent_or_ambiguous_target(
    index: int,
    record: dict[str, Any],
    node_type: str,
    requested: Any,
    occurrence_count: int,
) -> dict[str, Any]:
    return {
        "index": index,
        "key": record["key"],
        "node": record["node"],
        "nodeType": node_type,
        "socket": record["socket"],
        "requested": requested,
        "occurrenceCount": occurrence_count,
        "present": occurrence_count > 0,
        "enabled": None,
        "hidden": None,
        "linked": None,
        "supportsDefaultValue": None,
        "before": None,
        "assignmentAttempted": False,
        "assignmentSucceeded": False,
        "assignmentError": "ABSENT" if occurrence_count == 0 else "AMBIGUOUS_OCCURRENCE_COUNT",
        "after": None,
        "matchesRequested": None,
    }


def inspect_targets(
    records: list[dict[str, Any]],
    nodes_by_name: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if set(record.keys()) != {"key", "node", "socket", "value"}:
            raise RuntimeError(f"target schema mismatch: {index}")
        node = nodes_by_name[record["node"]]
        requested = comparable_value(record["value"])
        matches = [socket for socket in node.inputs if str(socket.name) == record["socket"]]
        occurrence_count = len(matches)
        if occurrence_count != 1:
            evidence.append(
                absent_or_ambiguous_target(
                    index, record, str(node.bl_idname), requested, occurrence_count
                )
            )
            continue
        socket = matches[0]
        common = {
            "index": index,
            "key": record["key"],
            "node": record["node"],
            "nodeType": str(node.bl_idname),
            "socket": record["socket"],
            "requested": requested,
            "occurrenceCount": 1,
            "present": True,
            "enabled": bool(socket.enabled),
            "hidden": bool(socket.hide),
            "linked": bool(socket.is_linked),
        }
        if not hasattr(socket, "default_value"):
            evidence.append(
                {
                    **common,
                    "supportsDefaultValue": False,
                    "before": None,
                    "assignmentAttempted": False,
                    "assignmentSucceeded": False,
                    "assignmentError": "NO_DEFAULT_VALUE",
                    "after": None,
                    "matchesRequested": None,
                }
            )
            continue
        before = comparable_value(socket.default_value)
        try:
            socket.default_value = record["value"]
        except Exception as exc:
            raise RuntimeError(f"target assignment failed: {record['key']}: {exc}") from exc
        after = comparable_value(socket.default_value)
        if not values_match(after, requested):
            raise RuntimeError(f"target readback mismatch: {record['key']}")
        evidence.append(
            {
                **common,
                "supportsDefaultValue": True,
                "before": before,
                "assignmentAttempted": True,
                "assignmentSucceeded": True,
                "assignmentError": None,
                "after": after,
                "matchesRequested": True,
            }
        )
    return evidence


def atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if path.exists() or temporary.exists():
        raise RuntimeError(f"evidence output collision: {path}")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def build_evidence(arguments: argparse.Namespace) -> dict[str, Any]:
    input_path = arguments.input.resolve(strict=True)
    output_path = arguments.output_schema.resolve(strict=False)
    if output_path.exists() or not output_path.parent.is_dir():
        raise RuntimeError("schema output path is not a new file in an existing directory")
    input_bytes = input_path.read_bytes()
    probe_input = strict_json_object(input_bytes, "probe input")
    if sha256_bytes(input_bytes) != arguments.input_sha256:
        raise RuntimeError("probe input SHA-256 mismatch")
    if (
        probe_input.get("schemaId") != EXPECTED_INPUT_SCHEMA
        or probe_input.get("schemaVersion") != 1
        or probe_input.get("probeId") != EXPECTED_PROBE_ID
        or probe_input.get("blenderVersion") != EXPECTED_BLENDER_VERSION
        or probe_input.get("blenderExecutableSha256") != EXPECTED_EXECUTABLE_SHA256
    ):
        raise RuntimeError("probe input identity mismatch")
    if bpy.app.version_string != EXPECTED_BLENDER_VERSION:
        raise RuntimeError(f"Blender version mismatch: {bpy.app.version_string}")
    blender_executable_hash = getattr(arguments, "blender_executable_sha256")
    if blender_executable_hash != EXPECTED_EXECUTABLE_SHA256:
        raise RuntimeError("Blender executable provenance mismatch")
    if sha256_bytes(Path(__file__).resolve(strict=True).read_bytes()) != arguments.generator_sha256:
        raise RuntimeError("generator SHA-256 mismatch")

    material = bpy.data.materials.new("TR4.MaterialSocketProbe001")
    try:
        material.use_nodes = True
        node_collection = material.node_tree.nodes
        node_collection.clear()
        node_order = probe_input["nodeOrder"]
        node_types = probe_input["nodeTypeByName"]
        if len(node_order) != 11 or set(node_types.keys()) != set(node_order):
            raise RuntimeError("closed node input mismatch")
        nodes_by_name: dict[str, Any] = {}
        for name in node_order:
            node = node_collection.new(node_types[name])
            node.name = name
            node.label = name
            nodes_by_name[name] = node
        if [node.name for node in nodes_by_name.values()] != node_order:
            raise RuntimeError("node creation order mismatch")
        property_records = probe_input["propertyAssignments"]
        target_records = probe_input["targets"]
        if len(property_records) != 19 or len(target_records) != 25:
            raise RuntimeError("closed property/target count mismatch")
        property_evidence = apply_properties(property_records, nodes_by_name)
        node_evidence = enumerate_nodes(node_order, nodes_by_name)
        target_evidence = inspect_targets(target_records, nodes_by_name)
    finally:
        bpy.data.materials.remove(material, do_unlink=True)

    return {
        "schemaId": "tide-relay.temple-tr4.material-socket-schema",
        "schemaVersion": 1,
        "probeId": EXPECTED_PROBE_ID,
        "blenderVersion": bpy.app.version_string,
        "contractSha256": arguments.contract_sha256,
        "inputSha256": arguments.input_sha256,
        "evidenceSchemaSha256": arguments.evidence_schema_sha256,
        "statusSchemaSha256": arguments.status_schema_sha256,
        "runnerSha256": arguments.runner_sha256,
        "generatorSha256": arguments.generator_sha256,
        "blenderExecutableSha256": blender_executable_hash,
        "renderInvocationCount": 0,
        "propertyAssignments": property_evidence,
        "nodes": node_evidence,
        "targets": target_evidence,
        "artifacts": {
            "renderCalls": 0,
            "evaluatorCalls": 0,
            "exportCalls": 0,
            "pngFiles": 0,
            "glbFiles": 0,
            "gltfFiles": 0,
            "blendFiles": 0,
        },
        "verdict": "SOCKET_SCHEMA_OBSERVED",
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-schema", type=Path, required=True)
    for name in HASH_ARGUMENTS:
        parser.add_argument("--" + name.replace("_", "-"), required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    arguments = parser.parse_args(argv)
    for name in HASH_ARGUMENTS:
        require_hash(getattr(arguments, name), name)
    return arguments


def main() -> int:
    try:
        arguments = parse_arguments()
        evidence = build_evidence(arguments)
        atomic_write(arguments.output_schema.resolve(strict=False), canonical_bytes(evidence))
        print(json.dumps({"verdict": evidence["verdict"]}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"verdict": "PROBE_BLOCKED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
