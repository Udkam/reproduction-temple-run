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
