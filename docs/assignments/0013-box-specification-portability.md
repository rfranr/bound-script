# Assignment 0013 — Portable Box Specification Validation & Export

## Prerequisite
Assignment 0012 is implemented, reviewed and accepted. Base this work on its `BoxDevelopmentSpec` API and `docs/proposals/0012-box-development-spec.md`.

## Goal
Turn the compiler-owned, in-memory box specification into a stable, strictly validated, portable JSON document usable by a future build-time agent and an independent verifier. Provide a small, reproducible export command. Do **not** implement either consumer yet.

## Requirements
1. Export pure functions `serializeBoxDevelopmentSpec(spec: BoxDevelopmentSpec): string` and `parseBoxDevelopmentSpec(json: string): BoxSpecResult` from `@boundscript/compiler` (or a narrowly equivalent API consistent with Assignment 0012). Parsing and serialization must not perform filesystem I/O.
2. On parse, strictly validate the format marker, version, top-level structure, required operation/input members, permitted primitive/record type descriptors, record-name consistency and unique primitive field names, result/void constraints, and any `Postcondition` target's compatibility with the resolved result type. Reject unsupported variants and unexpected properties rather than silently ignoring them.
3. Serialization must validate its input too; do not silently drop unsupported values or allow JavaScript functions/ASTs to be serialized. Define and document the error contract for invalid input.
4. Produce deterministic UTF-8 JSON text with stable key ordering, records' fields sorted in code-point order, no metadata dependent on source location or time, and a single documented final-newline convention. Semantically equivalent specs must yield identical bytes, including after parse/serialize round trips.
5. Add a minimal CLI export command (prefer the current CLI architecture) conceptually equivalent to `bound spec examples/structured-types.bound --box Greeter`. It should emit the spec JSON to stdout and diagnostics to stderr, return non-zero for invalid input or unknown boxes, and not require compile-time bindings or registered implementations. Avoid redesigning the whole CLI.
6. Add a small, deterministic JSON-only consumer test to prove the produced document can be read without Langium, source files, or a compiler at consumption time. The test may use the strict decoder, but must not need AST/source inspection.
7. Document the format semantics (finite numbers, required own record fields, no extras, nominal record identity, no coercion, void as `undefined`, type validation before postcondition), versioning, and limitations.
8. Explicitly document that the JSON specification is a *declared contract*, not a complete implementation brief: a human-authored task and independent examples/tests are still required. Do not infer business intent from box names or director invocations.
9. Preserve existing runtime artifacts, binding APIs, demos and tests.

## Acceptance criteria
- A documented single command emits a Greeter spec containing resolved `User` and `Greeting` schemas and its postcondition; standard output contains only JSON.
- The output matches the published format, has stable ordering, and is byte-identical across repeated exports and source whitespace changes.
- Valid specs round-trip without semantic or byte changes.
- Malformed JSON, wrong format/version, missing/unknown keys, duplicate record fields, unknown primitive types, conflicting record schemas, and incompatible/unknown postconditions fail explicitly.
- Spec export succeeds for unused declared boxes and never requires implementations.
- `npm run check`, `npm run build`, and existing demo commands pass.

## Out of scope
- Executing, verifying, generating, selecting, or approving box implementations; agent SDKs; isolated workers; sandbox enforcement; resource/capability policies; automatic test generation; new DSL syntax; general purpose schema/IR frameworks; cryptographic signatures, hashes, caching, and production packaging.

## Delivery
- Focused Conventional Commit with `Assignment: 0013` and actual AI metadata per `AGENTS.md`.
- Include positive/negative Vitest tests, CLI documentation and an example export. Do not alter this assignment without authorization.
- Report the exact export command, sample output, verification results and commit hash. Do not push without explicit authorization.
