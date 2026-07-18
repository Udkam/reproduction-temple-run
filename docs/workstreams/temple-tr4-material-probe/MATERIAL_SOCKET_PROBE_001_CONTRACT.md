# TEMPLE-TR4 material socket probe 001 contract

Status: **CONTRACT REVIEW REQUESTED; SOURCE AND BLENDER PROCESS NOT AUTHORIZED.**

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

1. verifies repository root, branch, committed input bytes, contract token, both source
   files, Blender executable hash, output-root absence, and no source worktree diff;
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

`material-socket-schema.json` is canonical JSON and contains exactly:

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
whether their runtime socket is present or absent. The probe observes the schema; absence
is valid evidence, not a reason to fabricate a socket or change F1/Euclidean properties.

## Closure and review

The terminal directory has exactly four files and zero subdirectories:

1. `probe-input.json`;
2. `material-socket-schema.json` when Blender reaches schema emission;
3. `blender.log`;
4. `probe-status.json`.

On a pre-emission failure, the directory may contain only the files already reached plus
the terminal status; that smaller set is frozen. The status records Blender return code,
stage, verdict, reason, and SHA-256/size for every sibling file; it never invents a hash
for an absent file. The runner rejects any extra file, directory, reparse point, output
escape, non-canonical JSON, missing/duplicate target, reordered node/target, wrong Blender
hash/version, render/export token, or schema mismatch.

Independent evidence review must verify the exact closure and determine which dynamic
sockets are observed under frozen `3D + F1 + EUCLIDEAN`. Only a later coordinator
contract may use that evidence to change `fixedSocketValues` or authorize diagnostic
`008`.
