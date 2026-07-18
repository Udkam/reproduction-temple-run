# TEMPLE-TR4 material socket probe thread log

## 2026-07-18 contract review request

- Diagnostic `007` is immutable `DIAGNOSTIC_BLOCKED` at evidence commit `3937ef6`:
  exactly four files, zero PNG, Blender return code `1`, evaluator not invoked, and no
  retry. The first material readback failed on absent dynamic `Voronoi.Smoothness`.
- Independent read-only root-cause review returned
  `MATERIAL_SOCKET_CONTRACT_BLOCKED` and
  `NEW_ZERO_RENDER_MATERIAL_SOCKET_SCHEMA_PROBE_REQUIRED`. It found that
  `Voronoi.Exponent` and the guarded Principled fixed inputs remain unobserved after the
  first error, so no diagnostic-008 correction can be inferred safely.
- This workstream proposes only the closed zero-render probe contract and canonical input.
  Source, Blender, diagnostic-008, render, evaluator, PNG, export, runtime, browser,
  tests/build, staging, push, and visual acceptance remain blocked pending independent
  `READY_FOR_MATERIAL_SOCKET_PROBE_001_CONTRACT` and separate coordinator authority.

## 2026-07-18 contract review 001 blocked and closure correction

- Independent review of exact commit `733f4d1` found no P0/P2 and three P1 gaps: no
  implementable unique contract token, descriptive rather than closed evidence/status
  schemas, and incomplete stage/provenance closure. Verdict: `CONTRACT_BLOCKED`.
- The corrected review request adds one complete labelled token line; exact evidence and
  status JSON Schemas with unknown-field rejection; input-bound array identities; exact
  Blender properties for RNA/enabled/hidden/linked evidence; numeric normalization; exact
  stage-to-file closures; and contract/input/schema/runner/generator/Blender hashes.
- Source, Blender, diagnostic-008, render/evaluator/export, runtime, browser, tests/build,
  staging, push, and visual acceptance remain blocked pending a fresh independent review.

## 2026-07-18 contract review 002 blocked and closure correction

- Independent review of exact commit `bf4cda5` found no P0/P2 and three remaining P1
  gaps: tuple branches did not fully close sibling file objects, value-type labels and
  successful target non-null fields were underconstrained, and an OS launch failure had
  no schema-valid terminal stage. Verdict: `CONTRACT_BLOCKED`.
- The corrected status schema uses full file-schema references plus `items:false` in every
  tuple branch and adds exact `launch` failure semantics. The evidence schema binds every
  value-type label to its JSON type and requires real booleans/non-null before/after for
  unique writable targets.
- Source, Blender, diagnostic-008, render/evaluator/export, runtime, browser, tests/build,
  staging, push, and visual acceptance remain blocked pending another fresh review.
