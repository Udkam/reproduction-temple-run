# TEMPLE-TR4 material socket probe 001 contract

Status: **CONTRACT REVIEW REQUESTED; SOURCE AND BLENDER PROCESS NOT AUTHORIZED.**

Probe source authorization token: `TEMPLE-TR4-MATERIAL-SOCKET-PROBE-001-SOURCE-AUTHORIZED`.

This is a new zero-render evidence identity after immutable diagnostic `007` stopped with
zero PNGs at Blender material readback. It is not a retry of diagnostic `007`, does not
authorize diagnostic `008`, and cannot claim material, model, render, or visual quality.

## Frozen cause and inputs

- Diagnostic `007` evidence commit is `3937ef6`. Its exact four-file directory and hashes
  remain immutable; evaluator was not invoked and no PNG exists.
- First error is the unconditional read of `Voronoi.Smoothness` in
  `actual_material_graph_record`; the live Blender 4.5.5 F1/Euclidean node did not expose
  that dynamic input. The guarded material writer and unconditional readback therefore
  disagree.
- The probe input is exactly `MATERIAL_SOCKET_PROBE_001_INPUT.json`. Its canonical UTF-8
  bytes, node order/types, property-assignment order, 25 target records, intended values,
  Blender version/hash, output root, and output filenames are closed.
- Evidence and terminal JSON are governed by the exact Draft 2020-12 schemas
  `MATERIAL_SOCKET_SCHEMA_V1.json` and `MATERIAL_SOCKET_PROBE_STATUS_V1.json`. Both reject
  unknown fields. Their final committed SHA-256 values become launch inputs and are
  recorded in both evidence and status.
- The Blender executable remains
  `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`, version `4.5.5 LTS`,
  SHA-256 `597f600e625f24e4f542906702b5a7dd33f6c6ff166e106b03ef4b1c3fb3921c`.

## Proposed writer scope

No writer authority exists until independent review returns
`READY_FOR_MATERIAL_SOCKET_PROBE_001_CONTRACT` and the coordinator records a separate
reauthorization. The later source scope, if authorized, is exactly two new files:

- `tools/temple-asset-pipeline/generate_tide_scar_material_socket_probe.py`;
- `tools/temple-asset-pipeline/run_tide_scar_material_socket_probe.py`.

The generator may import `bpy` only inside the one Blender background process. The outer
runner may start exactly one Blender process and no other subprocess. Neither file may
import or invoke the C7 generator, evaluator, renderer, runtime, browser, npm, export, or
test tools. Source must pass UTF-8 AST, exact input replay, a static absence check for
`bpy.ops.render`, `write_still`, evaluator calls, retry loops, `.png`, `.glb`, `.gltf`,
`.blend`, and export operators, followed by independent source review and a separate
source commit.

## One-process execution boundary

Only a later coordinator launch checkpoint may authorize execution. The sole standard
probe invocation then:

1. verifies repository root, branch, committed input bytes, exactly one complete labelled
   token line above, the source-authorization coordination log record, both source files,
   both JSON schemas, Blender executable hash, output-root absence, and no source worktree
   diff;
2. creates exactly `docs/workstreams/temple-tr4-material-probe/probe-001`;
3. writes a canonical copy of the committed input as `probe-input.json` before launch;
4. launches exactly one Blender 4.5.5 background process with the generator and input;
5. captures complete stdout/stderr in `blender.log`;
6. validates `material-socket-schema.json` when Blender returns zero; and
7. atomically writes `probe-status.json` as the terminal file.

There is no dry/diagnostic pair and no retry. Any failure freezes the same probe ID as
`PROBE_BLOCKED`. A successful maximum verdict is `SOCKET_SCHEMA_OBSERVED`, not
`READY_FOR_DIAGNOSTIC_008`.

## Required material-socket evidence

The Blender generator creates a temporary node tree in the exact input node order and
applies the exact property assignments before inspecting inputs. It must not construct
course geometry, cameras, lights, world volume, characters, hazards, Tide Scar, or
compositor nodes.

`material-socket-schema.json` is canonical JSON and validates against the exact committed
`MATERIAL_SOCKET_SCHEMA_V1.json`. Array order and identity are additionally replayed
against the canonical input: property-assignment index/node/property/requested equals the
19 input records, node index/name/type equals the 11 input records, and target
index/key/node/socket/requested equals the 25 input records. It contains exactly:

- schema ID/version, probe ID, Blender version, input SHA-256, generator SHA-256,
  `renderInvocationCount: 0`, and verdict;
- exact ordered property assignment records with before, requested, after, and equality;
- one ordered node record per input node, with node name/type and the complete ordered
  input socket list;
- every socket record includes index, name, identifier, occurrence count for its name,
  socket RNA type, enabled, hidden, linked, default-value support, default-value type,
  and comparable default value;
- one record for every one of the 25 target keys, including node/type, requested socket
  name, exact occurrence count, present, enabled, hidden, pre-assignment value,
  assignment attempted/succeeded/error, post-assignment value, and requested value;
- a closed no-artifact record proving zero renders/evaluator/export and zero PNG/GLB/
  glTF/BLEND outputs.

All five Voronoi targets and all ten Principled targets must be present as target records
whether their runtime socket is present or absent. `socketRnaIdentifier` is exactly
`socket.bl_rna.identifier`; `enabled`, `hidden`, and `linked` are exactly
`bool(socket.enabled)`, `bool(socket.hide)`, and `bool(socket.is_linked)`. For each target,
`occurrenceCount` counts exact `socket.name` matches. Assignment is attempted only when
that count is exactly one and the socket has `default_value`; count zero or greater than
one records no assignment, and ambiguity is never resolved by first-match selection. The
probe observes the schema; absence is valid evidence, not a reason to fabricate a socket
or change F1/Euclidean properties.

Target dispositions are exact: count zero uses `ABSENT`; count greater than one uses
`AMBIGUOUS_OCCURRENCE_COUNT`; a unique socket without `default_value` uses
`NO_DEFAULT_VALUE`; only a unique socket with `default_value` may set
`assignmentAttempted/assignmentSucceeded/matchesRequested` true. The two JSON Schemas
close every corresponding null, boolean, and error field. Socket records use
`defaultValueType: NONE` plus null only when `supportsDefaultValue` is false; every other
type label is bound to the matching scalar or homogeneous array JSON type. A unique target
always records non-null enabled/hidden/linked booleans and, when `default_value` exists,
non-null before/after values. `occurrenceCount: 1` also forces
`supportsDefaultValue` to a boolean, so null cannot bypass both unique-socket branches.

Comparable values are null, booleans, strings, finite JSON numbers, or flat arrays of
those scalar types. Negative zero normalizes to zero; tuples and Blender arrays normalize
to JSON arrays; non-finite values block. `defaultValueType` is derived from the normalized
Python value and must use the schema enum. Property readback uses exact equality for
boolean/string values and absolute tolerance `1e-6` for each numeric scalar/array element.
Targets record that same numeric comparison in `matchesRequested`; absence, ambiguity, or
missing `default_value` uses null values exactly as permitted by the schema.

## Closure and review

The terminal directory has zero subdirectories. After every prelaunch validation passes,
the runner creates it once. The only permitted stage closures are:

- `launch` + `PROBE_BLOCKED`: exactly `probe-input.json`, `blender.log`, and
  `probe-status.json`; an OS/process-start exception is recorded in the log, Blender
  return code and render count are null, and no child process was established;
- `blender` + `PROBE_BLOCKED`: exactly `probe-input.json`, `blender.log`, and
  `probe-status.json`; the generator writes no schema on a nonzero exit;
- `schema-validation` + `PROBE_BLOCKED`: exactly all four files below after Blender exits
  zero but runner validation rejects the emitted schema;
- `complete` + `SOCKET_SCHEMA_OBSERVED`: exactly all four files below after every gate.

Any prelaunch failure occurs before output-root creation and prints one terminal JSON line
to stdout; no process starts and the root remains absent. The successful/all-four names
are:

1. `probe-input.json`;
2. `material-socket-schema.json` when Blender reaches schema emission;
3. `blender.log`;
4. `probe-status.json`.

`probe-status.json` validates against the exact committed
`MATERIAL_SOCKET_PROBE_STATUS_V1.json`. It records the final contract, input, evidence
schema, status schema, runner, generator, and Blender executable SHA-256 values; Blender
return code; render count; stage/verdict/reason; and exact ordered sibling hashes/sizes.
The sibling list excludes the terminal status itself to avoid a circular self-hash and is
exactly `[probe-input.json, blender.log]` at `launch` or `blender`, or
`[probe-input.json, material-socket-schema.json, blender.log]` at the other two stages.
The evidence schema repeats all seven provenance hashes except its own terminal status
file. The runner rejects any extra file, directory, reparse point, output
escape, non-canonical JSON, missing/duplicate target, reordered node/target, wrong Blender
hash/version, render/export token, or schema mismatch.

Independent evidence review must verify the exact closure and determine which dynamic
sockets are observed under frozen `3D + F1 + EUCLIDEAN`. Only a later coordinator
contract may use that evidence to change `fixedSocketValues` or authorize diagnostic
`008`.
