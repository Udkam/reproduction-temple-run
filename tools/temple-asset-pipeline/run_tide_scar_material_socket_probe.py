"""Fail-closed one-process runner for TEMPLE-TR4 material socket probe 001."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import stat
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(r"E:\Proj\reproduction-temple-run")
EXPECTED_BRANCH = "main"
CONTRACT_RELATIVE = Path(
    "docs/workstreams/temple-tr4-material-probe/MATERIAL_SOCKET_PROBE_001_CONTRACT.md"
)
INPUT_RELATIVE = Path(
    "docs/workstreams/temple-tr4-material-probe/MATERIAL_SOCKET_PROBE_001_INPUT.json"
)
EVIDENCE_SCHEMA_RELATIVE = Path(
    "docs/workstreams/temple-tr4-material-probe/MATERIAL_SOCKET_SCHEMA_V1.json"
)
STATUS_SCHEMA_RELATIVE = Path(
    "docs/workstreams/temple-tr4-material-probe/MATERIAL_SOCKET_PROBE_STATUS_V1.json"
)
COORDINATION_RELATIVE = Path("docs/workstreams/temple-tr4-coordination/THREAD_LOG.md")
RUNNER_RELATIVE = Path("tools/temple-asset-pipeline/run_tide_scar_material_socket_probe.py")
GENERATOR_RELATIVE = Path(
    "tools/temple-asset-pipeline/generate_tide_scar_material_socket_probe.py"
)
OUTPUT_RELATIVE = Path("docs/workstreams/temple-tr4-material-probe/probe-001")
OUTPUT_NAMES = (
    "probe-input.json",
    "material-socket-schema.json",
    "blender.log",
    "probe-status.json",
)
BLENDER_EXECUTABLE = Path(r"E:\Blender 4.5\blender.exe")
BLENDER_VERSION = "4.5.5 LTS"
BLENDER_SHA256 = "597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c"
PROBE_ID = "001"

SOURCE_AUTHORIZATION_LINE = (
    "Probe source authorization token: "
    "`TEMPLE-TR4-MATERIAL-SOCKET-PROBE-001-SOURCE-AUTHORIZED`."
)
PROCESS_AUTHORIZATION_LINE = (
    "Probe process authorization token: "
    "`TEMPLE-TR4-MATERIAL-SOCKET-PROBE-001-PROCESS-AUTHORIZED`."
)
SOURCE_COORDINATION_LINE = (
    "REPORT TEMPLE-TR4 MATERIAL-SOCKET-PROBE-001 "
    "SOURCE-REAUTHORIZED-AFTER-PROCESS-TOKEN-REVIEW"
)
PROCESS_COORDINATION_LINE = "REPORT TEMPLE-TR4 MATERIAL-SOCKET-PROBE-001 PROCESS-AUTHORIZED"

INPUT_KEYS = {
    "schemaId",
    "schemaVersion",
    "probeId",
    "blenderVersion",
    "blenderExecutable",
    "blenderExecutableSha256",
    "outputRoot",
    "outputs",
    "nodeOrder",
    "nodeTypeByName",
    "propertyAssignments",
    "targets",
    "verdictCeiling",
}
EVIDENCE_KEYS = {
    "schemaId",
    "schemaVersion",
    "probeId",
    "blenderVersion",
    "contractSha256",
    "inputSha256",
    "evidenceSchemaSha256",
    "statusSchemaSha256",
    "runnerSha256",
    "generatorSha256",
    "blenderExecutableSha256",
    "renderInvocationCount",
    "propertyAssignments",
    "nodes",
    "targets",
    "artifacts",
    "verdict",
}
STATUS_KEYS = {
    "schemaId",
    "schemaVersion",
    "probeId",
    "stage",
    "verdict",
    "reason",
    "contractSha256",
    "inputSha256",
    "evidenceSchemaSha256",
    "statusSchemaSha256",
    "runnerSha256",
    "generatorSha256",
    "blenderExecutableSha256",
    "blenderReturnCode",
    "renderInvocationCount",
    "terminalFile",
    "siblingFiles",
}
PROVENANCE_FIELDS = (
    "contractSha256",
    "inputSha256",
    "evidenceSchemaSha256",
    "statusSchemaSha256",
    "runnerSha256",
    "generatorSha256",
    "blenderExecutableSha256",
)
HASH_PATHS = {
    "contractSha256": CONTRACT_RELATIVE,
    "inputSha256": INPUT_RELATIVE,
    "evidenceSchemaSha256": EVIDENCE_SCHEMA_RELATIVE,
    "statusSchemaSha256": STATUS_SCHEMA_RELATIVE,
    "runnerSha256": RUNNER_RELATIVE,
    "generatorSha256": GENERATOR_RELATIVE,
}


class ProbeBlocked(RuntimeError):
    """A closed precondition or evidence check failed."""


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


def parse_json_object(data: bytes, label: str, canonical: bool) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ProbeBlocked(f"duplicate JSON key in {label}: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeBlocked(f"invalid UTF-8 JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProbeBlocked(f"JSON root must be an object: {label}")
    if canonical and data != canonical_bytes(value):
        raise ProbeBlocked(f"JSON is not canonical: {label}")
    return value


def require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        raise ProbeBlocked(f"closed key mismatch at {label}: missing={missing}, extra={extra}")


def exact_line_count(text: str, expected: str) -> int:
    return sum(1 for line in text.splitlines() if line == expected)


def authorization_counts(contract_text: str, coordination_text: str) -> dict[str, int]:
    return {
        "sourceToken": exact_line_count(contract_text, SOURCE_AUTHORIZATION_LINE),
        "processToken": exact_line_count(contract_text, PROCESS_AUTHORIZATION_LINE),
        "sourceRecord": exact_line_count(coordination_text, SOURCE_COORDINATION_LINE),
        "processRecord": exact_line_count(coordination_text, PROCESS_COORDINATION_LINE),
    }


def authorization_lines_ready(contract_text: str, coordination_text: str) -> bool:
    return all(count == 1 for count in authorization_counts(contract_text, coordination_text).values())


def validate_authorization(contract_text: str, coordination_text: str) -> None:
    counts = authorization_counts(contract_text, coordination_text)
    for label, count in counts.items():
        if count != 1:
            raise ProbeBlocked(f"authorization exact-line count is {count}, expected 1: {label}")


def path_identity(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def has_reparse_attribute(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def reject_reparse_chain(root: Path, path: Path, allow_missing_leaf: bool = False) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ProbeBlocked(f"path escapes repository root: {path}") from exc
    current = root
    if has_reparse_attribute(current):
        raise ProbeBlocked(f"repository root is a reparse point: {current}")
    parts = relative.parts
    for index, part in enumerate(parts):
        current = current / part
        if not os.path.lexists(current):
            if allow_missing_leaf and index == len(parts) - 1:
                return
            raise ProbeBlocked(f"required path is absent: {current}")
        if current.is_symlink() or has_reparse_attribute(current):
            raise ProbeBlocked(f"reparse point is forbidden: {current}")


def ensure_regular_file(root: Path, relative: Path) -> Path:
    path = root / relative
    reject_reparse_chain(root, path)
    if not path.is_file():
        raise ProbeBlocked(f"required regular file is absent: {relative.as_posix()}")
    return path


def read_loose_object(git_directory: Path, object_id: str) -> tuple[str, bytes]:
    if len(object_id) != 40 or any(character not in "0123456789abcdef" for character in object_id):
        raise ProbeBlocked(f"invalid Git object id: {object_id}")
    object_path = git_directory / "objects" / object_id[:2] / object_id[2:]
    if not object_path.is_file():
        raise ProbeBlocked(f"loose Git object unavailable; packed objects are unsupported: {object_id}")
    try:
        inflated = zlib.decompress(object_path.read_bytes())
    except zlib.error as exc:
        raise ProbeBlocked(f"invalid loose Git object compression: {object_id}") from exc
    if hashlib.sha1(inflated).hexdigest() != object_id:
        raise ProbeBlocked(f"loose Git object hash mismatch: {object_id}")
    header, separator, payload = inflated.partition(b"\0")
    if separator != b"\0" or b" " not in header:
        raise ProbeBlocked(f"invalid loose Git object header: {object_id}")
    object_type_bytes, size_bytes = header.split(b" ", 1)
    try:
        object_type = object_type_bytes.decode("ascii")
        expected_size = int(size_bytes.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ProbeBlocked(f"invalid loose Git object header encoding: {object_id}") from exc
    if expected_size != len(payload):
        raise ProbeBlocked(f"loose Git object size mismatch: {object_id}")
    return object_type, payload


def parse_tree(payload: bytes) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    offset = 0
    while offset < len(payload):
        space = payload.find(b" ", offset)
        nul = payload.find(b"\0", space + 1)
        if space < 0 or nul < 0 or nul + 21 > len(payload):
            raise ProbeBlocked("malformed Git tree object")
        mode_bytes = payload[offset:space]
        name_bytes = payload[space + 1 : nul]
        try:
            mode = mode_bytes.decode("ascii")
            name = name_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ProbeBlocked("non-UTF-8 Git tree entry") from exc
        if not name or "/" in name or name in entries:
            raise ProbeBlocked(f"invalid Git tree entry name: {name!r}")
        object_id = payload[nul + 1 : nul + 21].hex()
        entries[name] = (mode, object_id)
        offset = nul + 21
    return entries


def head_commit_and_tree(git_directory: Path) -> tuple[str, str]:
    head_bytes = (git_directory / "HEAD").read_bytes()
    expected_head = f"ref: refs/heads/{EXPECTED_BRANCH}\n".encode("ascii")
    if head_bytes != expected_head:
        raise ProbeBlocked("HEAD does not name the expected branch with canonical bytes")
    branch_path = git_directory / "refs" / "heads" / Path(*EXPECTED_BRANCH.split("/"))
    if not branch_path.is_file():
        raise ProbeBlocked("expected branch ref is not a loose ref")
    branch_bytes = branch_path.read_bytes()
    try:
        commit_id = branch_bytes.decode("ascii").removesuffix("\n")
    except UnicodeDecodeError as exc:
        raise ProbeBlocked("branch ref is not ASCII") from exc
    if branch_bytes != (commit_id + "\n").encode("ascii"):
        raise ProbeBlocked("branch ref bytes are not canonical")
    object_type, commit = read_loose_object(git_directory, commit_id)
    if object_type != "commit":
        raise ProbeBlocked("HEAD object is not a commit")
    first_line = commit.split(b"\n", 1)[0]
    if not first_line.startswith(b"tree ") or len(first_line) != 45:
        raise ProbeBlocked("HEAD commit has no canonical tree header")
    tree_id = first_line[5:].decode("ascii")
    return commit_id, tree_id


def read_blob_at_tree(git_directory: Path, tree_id: str, relative: Path) -> bytes:
    current_id = tree_id
    parts = relative.as_posix().split("/")
    for index, part in enumerate(parts):
        object_type, payload = read_loose_object(git_directory, current_id)
        if object_type != "tree":
            raise ProbeBlocked(f"Git path parent is not a tree: {relative.as_posix()}")
        entry = parse_tree(payload).get(part)
        if entry is None:
            raise ProbeBlocked(f"Git HEAD does not contain: {relative.as_posix()}")
        mode, current_id = entry
        final = index == len(parts) - 1
        if not final and mode != "40000":
            raise ProbeBlocked(f"Git path has a non-tree parent: {relative.as_posix()}")
        if final and mode not in {"100644", "100755"}:
            raise ProbeBlocked(f"Git path is not a regular blob: {relative.as_posix()}")
    object_type, payload = read_loose_object(git_directory, current_id)
    if object_type != "blob":
        raise ProbeBlocked(f"Git path does not resolve to a blob: {relative.as_posix()}")
    return payload


def validate_git_state(root: Path, launch_bytes: dict[Path, bytes]) -> str:
    git_directory = root / ".git"
    if not git_directory.is_dir() or git_directory.is_symlink():
        raise ProbeBlocked("repository must have an independent .git directory")
    reject_reparse_chain(root, git_directory)
    if os.path.lexists(git_directory / "commondir"):
        raise ProbeBlocked("linked Git common-dir indirection is forbidden")
    commit_id, tree_id = head_commit_and_tree(git_directory)
    for relative, working_bytes in launch_bytes.items():
        committed_bytes = read_blob_at_tree(git_directory, tree_id, relative)
        if working_bytes != committed_bytes:
            raise ProbeBlocked(f"launch input differs from current HEAD: {relative.as_posix()}")
    return commit_id


def call_name(call: ast.Call) -> str:
    parts: list[str] = []
    value: ast.AST = call.func
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def static_source_audit(runner_bytes: bytes, generator_bytes: bytes) -> None:
    sources = {"runner": runner_bytes, "generator": generator_bytes}
    trees: dict[str, ast.AST] = {}
    for label, data in sources.items():
        try:
            text = data.decode("utf-8")
            trees[label] = ast.parse(text, filename=label)
        except (UnicodeDecodeError, SyntaxError) as exc:
            raise ProbeBlocked(f"UTF-8 AST failure in {label}: {exc}") from exc
        lowered = text.lower()
        forbidden_text = (
            "." + "png",
            "." + "glb",
            "." + "gltf",
            "." + "blend",
            "bpy.ops." + "render",
            "write" + "_still",
            "export" + "_scene",
            "export" + "_mesh",
        )
        for token in forbidden_text:
            if token in lowered:
                raise ProbeBlocked(f"forbidden source token in {label}: {token}")
        if "re" + "try" in lowered:
            raise ProbeBlocked(f"forbidden repeated-attempt token in {label}")

    generator_calls = [call_name(node) for node in ast.walk(trees["generator"]) if isinstance(node, ast.Call)]
    runner_calls = [call_name(node) for node in ast.walk(trees["runner"]) if isinstance(node, ast.Call)]
    if any(name.startswith("subprocess.") for name in generator_calls):
        raise ProbeBlocked("generator may not start a subprocess")
    subprocess_run_name = "subprocess" + ".run"
    if runner_calls.count(subprocess_run_name) != 1:
        raise ProbeBlocked("runner must contain exactly one process-start call site")
    if any(
        ("evaluator" in name.lower())
        or name.startswith("bpy.ops.")
        or ("export" in name.lower())
        for name in generator_calls + runner_calls
    ):
        raise ProbeBlocked("forbidden evaluator, Blender operator, or export call")

    for label, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                for module in modules:
                    if module == "bpy" and label != "generator":
                        raise ProbeBlocked("bpy import is generator-only")
                    if any(
                        token in module.lower()
                        for token in ("playwright", "selenium", "three", "vite", "vitest")
                    ):
                        raise ProbeBlocked(f"forbidden tool import in {label}: {module}")

    parent_by_child: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(trees["runner"]):
        for child in ast.iter_child_nodes(parent):
            parent_by_child[child] = parent
    run_call = next(
        node
        for node in ast.walk(trees["runner"])
        if isinstance(node, ast.Call) and call_name(node) == subprocess_run_name
    )
    ancestor = parent_by_child.get(run_call)
    while ancestor is not None:
        if isinstance(ancestor, (ast.For, ast.AsyncFor, ast.While)):
            raise ProbeBlocked("the process-start call may not be nested in a loop")
        ancestor = parent_by_child.get(ancestor)


def validate_schema_documents(evidence_schema: dict[str, Any], status_schema: dict[str, Any]) -> None:
    if (
        evidence_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or evidence_schema.get("$id") != "tide-relay.temple-tr4.material-socket-schema.v1"
        or evidence_schema.get("type") != "object"
        or evidence_schema.get("additionalProperties") is not False
        or set(evidence_schema.get("required", [])) != EVIDENCE_KEYS
    ):
        raise ProbeBlocked("evidence schema identity or closed top-level fields mismatch")
    if (
        status_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or status_schema.get("$id") != "tide-relay.temple-tr4.material-socket-probe-status.v1"
        or status_schema.get("type") != "object"
        or status_schema.get("additionalProperties") is not False
        or set(status_schema.get("required", [])) != STATUS_KEYS
    ):
        raise ProbeBlocked("status schema identity or closed top-level fields mismatch")


def validate_input(probe_input: dict[str, Any]) -> None:
    require_exact_keys(probe_input, INPUT_KEYS, "probe input")
    if (
        probe_input["schemaId"] != "tide-relay.temple-tr4.material-socket-probe-input"
        or probe_input["schemaVersion"] != 1
        or probe_input["probeId"] != PROBE_ID
        or probe_input["blenderVersion"] != BLENDER_VERSION
        or probe_input["blenderExecutable"] != str(BLENDER_EXECUTABLE)
        or probe_input["blenderExecutableSha256"] != BLENDER_SHA256
        or probe_input["outputRoot"] != OUTPUT_RELATIVE.as_posix()
        or probe_input["outputs"] != list(OUTPUT_NAMES)
        or probe_input["verdictCeiling"] != "SOCKET_SCHEMA_OBSERVED"
    ):
        raise ProbeBlocked("probe input closed identity mismatch")
    node_order = probe_input["nodeOrder"]
    node_types = probe_input["nodeTypeByName"]
    assignments = probe_input["propertyAssignments"]
    targets = probe_input["targets"]
    if (
        not isinstance(node_order, list)
        or len(node_order) != 11
        or len(set(node_order)) != 11
        or not isinstance(node_types, dict)
        or set(node_types) != set(node_order)
        or not isinstance(assignments, list)
        or len(assignments) != 19
        or not isinstance(targets, list)
        or len(targets) != 25
    ):
        raise ProbeBlocked("probe input 11/19/25 closure mismatch")
    for index, record in enumerate(assignments):
        if not isinstance(record, dict) or set(record) != {"node", "property", "value"}:
            raise ProbeBlocked(f"property input record mismatch: {index}")
        if record["node"] not in node_types or not isinstance(record["property"], str):
            raise ProbeBlocked(f"property input identity mismatch: {index}")
        validate_json_value(record["value"], f"property input value {index}")
    target_keys: set[str] = set()
    for index, record in enumerate(targets):
        if not isinstance(record, dict) or set(record) != {"key", "node", "socket", "value"}:
            raise ProbeBlocked(f"target input record mismatch: {index}")
        if (
            record["node"] not in node_types
            or not isinstance(record["key"], str)
            or not record["key"]
            or record["key"] in target_keys
            or not isinstance(record["socket"], str)
            or not record["socket"]
        ):
            raise ProbeBlocked(f"target input identity mismatch: {index}")
        target_keys.add(record["key"])
        validate_json_value(record["value"], f"target input value {index}")


def validate_json_value(value: Any, label: str, allow_null: bool = True) -> None:
    if value is None:
        if allow_null:
            return
        raise ProbeBlocked(f"null is forbidden at {label}")
    if isinstance(value, (bool, str)):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            raise ProbeBlocked(f"non-finite number at {label}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            if isinstance(item, list) or item is None:
                raise ProbeBlocked(f"array must be flat and non-null at {label}[{index}]")
            validate_json_value(item, f"{label}[{index}]", allow_null=False)
        return
    raise ProbeBlocked(f"unsupported JSON comparable value at {label}: {type(value).__name__}")


def values_match(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1.0e-6
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(values_match(a, b) for a, b in zip(left, right))
    return type(left) is type(right) and left == right


def derived_default_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "NUMBER"
    if isinstance(value, str):
        return "STRING"
    if isinstance(value, list) and value:
        if all(isinstance(item, bool) for item in value):
            return "BOOLEAN_ARRAY"
        if all(isinstance(item, int) and not isinstance(item, bool) for item in value):
            return "INTEGER_ARRAY"
        if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value):
            return "NUMBER_ARRAY"
        if all(isinstance(item, str) for item in value):
            return "STRING_ARRAY"
    raise ProbeBlocked("default value has no closed schema type")


def validate_provenance(value: dict[str, Any], hashes: dict[str, str], label: str) -> None:
    for field in PROVENANCE_FIELDS:
        if value.get(field) != hashes[field]:
            raise ProbeBlocked(f"provenance mismatch at {label}.{field}")


def validate_property_evidence(records: Any, probe_input: dict[str, Any]) -> None:
    if not isinstance(records, list) or len(records) != 19:
        raise ProbeBlocked("property evidence count mismatch")
    expected_records = probe_input["propertyAssignments"]
    keys = {"index", "node", "property", "before", "requested", "after", "matchesRequested"}
    for index, (record, expected) in enumerate(zip(records, expected_records)):
        if not isinstance(record, dict):
            raise ProbeBlocked(f"property evidence is not an object: {index}")
        require_exact_keys(record, keys, f"property evidence {index}")
        for field in ("before", "requested", "after"):
            validate_json_value(record[field], f"property evidence {index}.{field}")
        if (
            record["index"] != index
            or record["node"] != expected["node"]
            or record["property"] != expected["property"]
            or not values_match(record["requested"], expected["value"])
            or record["matchesRequested"] is not True
            or not values_match(record["after"], record["requested"])
        ):
            raise ProbeBlocked(f"property evidence replay mismatch: {index}")


def validate_socket_record(record: Any, index: int, label: str) -> None:
    keys = {
        "index",
        "name",
        "identifier",
        "nameOccurrenceCount",
        "socketRnaIdentifier",
        "enabled",
        "hidden",
        "linked",
        "supportsDefaultValue",
        "defaultValueType",
        "defaultValue",
    }
    if not isinstance(record, dict):
        raise ProbeBlocked(f"socket evidence is not an object: {label}")
    require_exact_keys(record, keys, label)
    if (
        record["index"] != index
        or not isinstance(record["name"], str)
        or not isinstance(record["identifier"], str)
        or not isinstance(record["nameOccurrenceCount"], int)
        or isinstance(record["nameOccurrenceCount"], bool)
        or record["nameOccurrenceCount"] < 1
        or not isinstance(record["socketRnaIdentifier"], str)
        or not record["socketRnaIdentifier"]
        or any(not isinstance(record[field], bool) for field in ("enabled", "hidden", "linked"))
        or not isinstance(record["supportsDefaultValue"], bool)
    ):
        raise ProbeBlocked(f"socket evidence scalar mismatch: {label}")
    supports = record["supportsDefaultValue"]
    if not supports:
        if record["defaultValueType"] != "NONE" or record["defaultValue"] is not None:
            raise ProbeBlocked(f"socket no-default disposition mismatch: {label}")
        return
    validate_json_value(record["defaultValue"], f"{label}.defaultValue", allow_null=False)
    if record["defaultValueType"] != derived_default_type(record["defaultValue"]):
        raise ProbeBlocked(f"socket default type mismatch: {label}")


def validate_node_evidence(records: Any, probe_input: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list) or len(records) != 11:
        raise ProbeBlocked("node evidence count mismatch")
    node_order = probe_input["nodeOrder"]
    node_types = probe_input["nodeTypeByName"]
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ProbeBlocked(f"node evidence is not an object: {index}")
        require_exact_keys(record, {"index", "name", "nodeType", "inputs"}, f"node evidence {index}")
        name = node_order[index]
        if (
            record["index"] != index
            or record["name"] != name
            or record["nodeType"] != node_types[name]
            or not isinstance(record["inputs"], list)
        ):
            raise ProbeBlocked(f"node evidence replay mismatch: {index}")
        inputs = record["inputs"]
        for socket_index, socket in enumerate(inputs):
            validate_socket_record(socket, socket_index, f"node {name} socket {socket_index}")
        for socket in inputs:
            occurrence = sum(1 for candidate in inputs if candidate["name"] == socket["name"])
            if socket["nameOccurrenceCount"] != occurrence:
                raise ProbeBlocked(f"socket name occurrence mismatch: {name}.{socket['name']}")
        result[name] = record
    return result


def validate_target_evidence(
    records: Any,
    probe_input: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(records, list) or len(records) != 25:
        raise ProbeBlocked("target evidence count mismatch")
    keys = {
        "index",
        "key",
        "node",
        "nodeType",
        "socket",
        "requested",
        "occurrenceCount",
        "present",
        "enabled",
        "hidden",
        "linked",
        "supportsDefaultValue",
        "before",
        "assignmentAttempted",
        "assignmentSucceeded",
        "assignmentError",
        "after",
        "matchesRequested",
    }
    for index, (record, expected) in enumerate(zip(records, probe_input["targets"])):
        if not isinstance(record, dict):
            raise ProbeBlocked(f"target evidence is not an object: {index}")
        require_exact_keys(record, keys, f"target evidence {index}")
        validate_json_value(record["requested"], f"target evidence {index}.requested")
        node = nodes[expected["node"]]
        matches = [socket for socket in node["inputs"] if socket["name"] == expected["socket"]]
        occurrence = len(matches)
        if (
            record["index"] != index
            or record["key"] != expected["key"]
            or record["node"] != expected["node"]
            or record["nodeType"] != node["nodeType"]
            or record["socket"] != expected["socket"]
            or not values_match(record["requested"], expected["value"])
            or record["occurrenceCount"] != occurrence
        ):
            raise ProbeBlocked(f"target evidence replay mismatch: {index}")
        if occurrence == 0:
            expected_disposition = {
                "present": False,
                "enabled": None,
                "hidden": None,
                "linked": None,
                "supportsDefaultValue": None,
                "before": None,
                "assignmentAttempted": False,
                "assignmentSucceeded": False,
                "assignmentError": "ABSENT",
                "after": None,
                "matchesRequested": None,
            }
        elif occurrence > 1:
            expected_disposition = {
                "present": True,
                "enabled": None,
                "hidden": None,
                "linked": None,
                "supportsDefaultValue": None,
                "before": None,
                "assignmentAttempted": False,
                "assignmentSucceeded": False,
                "assignmentError": "AMBIGUOUS_OCCURRENCE_COUNT",
                "after": None,
                "matchesRequested": None,
            }
        else:
            socket = matches[0]
            common = {
                "present": True,
                "enabled": socket["enabled"],
                "hidden": socket["hidden"],
                "linked": socket["linked"],
                "supportsDefaultValue": socket["supportsDefaultValue"],
            }
            if not socket["supportsDefaultValue"]:
                expected_disposition = {
                    **common,
                    "before": None,
                    "assignmentAttempted": False,
                    "assignmentSucceeded": False,
                    "assignmentError": "NO_DEFAULT_VALUE",
                    "after": None,
                    "matchesRequested": None,
                }
            else:
                for field in ("before", "after"):
                    validate_json_value(record[field], f"target evidence {index}.{field}", allow_null=False)
                expected_disposition = {
                    **common,
                    "assignmentAttempted": True,
                    "assignmentSucceeded": True,
                    "assignmentError": None,
                    "matchesRequested": True,
                }
                if not values_match(record["after"], record["requested"]):
                    raise ProbeBlocked(f"target requested readback mismatch: {index}")
        for field, expected_value in expected_disposition.items():
            if record[field] != expected_value:
                raise ProbeBlocked(f"target disposition mismatch: {index}.{field}")


def validate_evidence(
    evidence_bytes: bytes,
    probe_input: dict[str, Any],
    hashes: dict[str, str],
) -> dict[str, Any]:
    evidence = parse_json_object(evidence_bytes, "material socket evidence", canonical=True)
    require_exact_keys(evidence, EVIDENCE_KEYS, "material socket evidence")
    if (
        evidence["schemaId"] != "tide-relay.temple-tr4.material-socket-schema"
        or evidence["schemaVersion"] != 1
        or evidence["probeId"] != PROBE_ID
        or evidence["blenderVersion"] != BLENDER_VERSION
        or evidence["renderInvocationCount"] != 0
        or evidence["verdict"] != "SOCKET_SCHEMA_OBSERVED"
    ):
        raise ProbeBlocked("material socket evidence identity mismatch")
    validate_provenance(evidence, hashes, "evidence")
    validate_property_evidence(evidence["propertyAssignments"], probe_input)
    nodes = validate_node_evidence(evidence["nodes"], probe_input)
    validate_target_evidence(evidence["targets"], probe_input, nodes)
    expected_artifacts = {
        "renderCalls": 0,
        "evaluatorCalls": 0,
        "exportCalls": 0,
        "pngFiles": 0,
        "glbFiles": 0,
        "gltfFiles": 0,
        "blendFiles": 0,
    }
    if evidence["artifacts"] != expected_artifacts:
        raise ProbeBlocked("material socket evidence artifact closure mismatch")
    return evidence


def file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"name": path.name, "bytes": len(data), "sha256": sha256_bytes(data)}


def expected_sibling_names(stage: str) -> list[str]:
    if stage in {"launch", "blender"}:
        return [OUTPUT_NAMES[0], OUTPUT_NAMES[2]]
    return [OUTPUT_NAMES[0], OUTPUT_NAMES[1], OUTPUT_NAMES[2]]


def validate_directory_closure(output_root: Path, names: list[str], include_status: bool) -> None:
    expected = set(names)
    if include_status:
        expected.add(OUTPUT_NAMES[3])
    actual: set[str] = set()
    for child in output_root.iterdir():
        if child.is_symlink() or has_reparse_attribute(child) or not child.is_file():
            raise ProbeBlocked(f"output closure contains a directory or reparse point: {child.name}")
        actual.add(child.name)
    if actual != expected:
        raise ProbeBlocked(f"output closure mismatch: expected={sorted(expected)}, actual={sorted(actual)}")


def build_status(
    output_root: Path,
    hashes: dict[str, str],
    stage: str,
    verdict: str,
    reason: str,
    blender_return_code: int | None,
    render_count: int | None,
) -> dict[str, Any]:
    names = expected_sibling_names(stage)
    return {
        "schemaId": "tide-relay.temple-tr4.material-socket-probe-status",
        "schemaVersion": 1,
        "probeId": PROBE_ID,
        "stage": stage,
        "verdict": verdict,
        "reason": reason,
        **hashes,
        "blenderReturnCode": blender_return_code,
        "renderInvocationCount": render_count,
        "terminalFile": OUTPUT_NAMES[3],
        "siblingFiles": [file_record(output_root / name) for name in names],
    }


def validate_status(status_value: dict[str, Any], output_root: Path, hashes: dict[str, str]) -> None:
    require_exact_keys(status_value, STATUS_KEYS, "probe status")
    validate_provenance(status_value, hashes, "status")
    stage = status_value["stage"]
    if (
        status_value["schemaId"] != "tide-relay.temple-tr4.material-socket-probe-status"
        or status_value["schemaVersion"] != 1
        or status_value["probeId"] != PROBE_ID
        or stage not in {"launch", "blender", "schema-validation", "complete"}
        or not isinstance(status_value["reason"], str)
        or not status_value["reason"]
        or status_value["terminalFile"] != OUTPUT_NAMES[3]
    ):
        raise ProbeBlocked("probe status identity mismatch")
    if stage == "launch":
        expected_tuple = ("PROBE_BLOCKED", None, None)
    elif stage == "blender":
        return_code = status_value["blenderReturnCode"]
        if not isinstance(return_code, int) or isinstance(return_code, bool) or return_code == 0:
            raise ProbeBlocked("blender-stage return code mismatch")
        expected_tuple = ("PROBE_BLOCKED", return_code, None)
    elif stage == "schema-validation":
        expected_tuple = ("PROBE_BLOCKED", 0, 0)
    else:
        expected_tuple = ("SOCKET_SCHEMA_OBSERVED", 0, 0)
        if status_value["reason"] != "SOCKET_SCHEMA_OBSERVED":
            raise ProbeBlocked("complete-stage reason mismatch")
    actual_tuple = (
        status_value["verdict"],
        status_value["blenderReturnCode"],
        status_value["renderInvocationCount"],
    )
    if actual_tuple != expected_tuple:
        raise ProbeBlocked(f"probe status stage tuple mismatch: {stage}")
    names = expected_sibling_names(stage)
    siblings = status_value["siblingFiles"]
    if not isinstance(siblings, list) or [record.get("name") for record in siblings] != names:
        raise ProbeBlocked("probe status ordered sibling names mismatch")
    for name, record in zip(names, siblings):
        if not isinstance(record, dict) or set(record) != {"name", "bytes", "sha256"}:
            raise ProbeBlocked(f"probe status sibling record mismatch: {name}")
        if record != file_record(output_root / name):
            raise ProbeBlocked(f"probe status sibling provenance mismatch: {name}")


def atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    if os.path.lexists(path) or os.path.lexists(temporary):
        raise ProbeBlocked(f"atomic output collision: {path.name}")
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


def finish_stage(
    output_root: Path,
    hashes: dict[str, str],
    stage: str,
    verdict: str,
    reason: str,
    blender_return_code: int | None,
    render_count: int | None,
) -> dict[str, Any]:
    names = expected_sibling_names(stage)
    validate_directory_closure(output_root, names, include_status=False)
    status_value = build_status(
        output_root,
        hashes,
        stage,
        verdict,
        reason,
        blender_return_code,
        render_count,
    )
    validate_status(status_value, output_root, hashes)
    atomic_write(output_root / OUTPUT_NAMES[3], canonical_bytes(status_value))
    validate_directory_closure(output_root, names, include_status=True)
    return status_value


def prelaunch() -> dict[str, Any]:
    root = REPOSITORY_ROOT.resolve(strict=True)
    if path_identity(root) != path_identity(REPOSITORY_ROOT):
        raise ProbeBlocked(f"repository root mismatch: {root}")
    if path_identity(Path.cwd().resolve(strict=True)) != path_identity(root):
        raise ProbeBlocked("runner must start at the exact repository root")
    if root.is_symlink() or has_reparse_attribute(root):
        raise ProbeBlocked("repository root may not be a reparse point")

    relatives = (
        CONTRACT_RELATIVE,
        INPUT_RELATIVE,
        EVIDENCE_SCHEMA_RELATIVE,
        STATUS_SCHEMA_RELATIVE,
        COORDINATION_RELATIVE,
        RUNNER_RELATIVE,
        GENERATOR_RELATIVE,
    )
    paths = {relative: ensure_regular_file(root, relative) for relative in relatives}
    launch_bytes = {relative: path.read_bytes() for relative, path in paths.items()}

    try:
        contract_text = launch_bytes[CONTRACT_RELATIVE].decode("utf-8")
        coordination_text = launch_bytes[COORDINATION_RELATIVE].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProbeBlocked("authorization document is not UTF-8") from exc
    validate_authorization(contract_text, coordination_text)

    output_root = root / OUTPUT_RELATIVE
    reject_reparse_chain(root, output_root.parent)
    if os.path.lexists(output_root):
        raise ProbeBlocked("probe output root must be absent")

    probe_input = parse_json_object(launch_bytes[INPUT_RELATIVE], "probe input", canonical=True)
    evidence_schema = parse_json_object(
        launch_bytes[EVIDENCE_SCHEMA_RELATIVE], "evidence schema", canonical=False
    )
    status_schema = parse_json_object(
        launch_bytes[STATUS_SCHEMA_RELATIVE], "status schema", canonical=False
    )
    validate_input(probe_input)
    validate_schema_documents(evidence_schema, status_schema)
    static_source_audit(launch_bytes[RUNNER_RELATIVE], launch_bytes[GENERATOR_RELATIVE])

    head_commit = validate_git_state(root, launch_bytes)
    if not BLENDER_EXECUTABLE.is_file() or BLENDER_EXECUTABLE.is_symlink():
        raise ProbeBlocked("Blender executable is absent or redirected")
    if has_reparse_attribute(BLENDER_EXECUTABLE):
        raise ProbeBlocked("Blender executable may not be a reparse point")
    if sha256_file(BLENDER_EXECUTABLE) != BLENDER_SHA256:
        raise ProbeBlocked("Blender executable SHA-256 mismatch")

    hashes = {
        field: sha256_bytes(launch_bytes[relative])
        for field, relative in HASH_PATHS.items()
    }
    hashes["blenderExecutableSha256"] = BLENDER_SHA256
    return {
        "root": root,
        "outputRoot": output_root,
        "probeInput": probe_input,
        "inputBytes": launch_bytes[INPUT_RELATIVE],
        "hashes": hashes,
        "generator": paths[GENERATOR_RELATIVE],
        "head": head_commit,
    }


def invoke_blender(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def execute(context: dict[str, Any]) -> dict[str, Any]:
    output_root: Path = context["outputRoot"]
    output_root.mkdir(parents=False, exist_ok=False)
    input_copy = output_root / OUTPUT_NAMES[0]
    schema_output = output_root / OUTPUT_NAMES[1]
    log_output = output_root / OUTPUT_NAMES[2]
    atomic_write(input_copy, context["inputBytes"])
    hashes: dict[str, str] = context["hashes"]
    command = [
        str(BLENDER_EXECUTABLE),
        "--background",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        str(context["generator"]),
        "--",
        "--input",
        str(input_copy),
        "--output-schema",
        str(schema_output),
    ]
    for field in PROVENANCE_FIELDS:
        option = "--" + "".join(
            ("-" + character.lower()) if character.isupper() else character
            for character in field
        )
        command.extend([option, hashes[field]])
    try:
        completed = invoke_blender(command)
    except OSError as exc:
        atomic_write(log_output, (f"process start exception: {type(exc).__name__}: {exc}\n").encode("utf-8"))
        return finish_stage(
            output_root,
            hashes,
            "launch",
            "PROBE_BLOCKED",
            f"process start exception: {type(exc).__name__}: {exc}",
            None,
            None,
        )

    atomic_write(log_output, completed.stdout or b"")
    if completed.returncode != 0:
        if os.path.lexists(schema_output):
            raise ProbeBlocked("generator emitted schema on nonzero Blender exit")
        return finish_stage(
            output_root,
            hashes,
            "blender",
            "PROBE_BLOCKED",
            f"Blender returned nonzero exit code {completed.returncode}",
            completed.returncode,
            None,
        )
    if not schema_output.is_file() or schema_output.is_symlink() or has_reparse_attribute(schema_output):
        raise ProbeBlocked("zero-exit Blender did not emit a regular evidence schema")
    try:
        validate_evidence(schema_output.read_bytes(), context["probeInput"], hashes)
    except ProbeBlocked as exc:
        return finish_stage(
            output_root,
            hashes,
            "schema-validation",
            "PROBE_BLOCKED",
            str(exc),
            0,
            0,
        )
    return finish_stage(
        output_root,
        hashes,
        "complete",
        "SOCKET_SCHEMA_OBSERVED",
        "SOCKET_SCHEMA_OBSERVED",
        0,
        0,
    )


def terminal_line(verdict: str, reason: str, stage: str | None = None) -> str:
    value: dict[str, Any] = {"verdict": verdict, "reason": reason}
    if stage is not None:
        value["stage"] = stage
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    if len(sys.argv) != 1:
        print(terminal_line("PROBE_BLOCKED", "runner accepts no arguments"))
        return 1
    try:
        context = prelaunch()
    except Exception as exc:
        print(terminal_line("PROBE_BLOCKED", str(exc)))
        return 1
    try:
        status_value = execute(context)
    except Exception as exc:
        print(terminal_line("PROBE_BLOCKED", str(exc)))
        return 1
    print(terminal_line(status_value["verdict"], status_value["reason"], status_value["stage"]))
    return 0 if status_value["verdict"] == "SOCKET_SCHEMA_OBSERVED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
