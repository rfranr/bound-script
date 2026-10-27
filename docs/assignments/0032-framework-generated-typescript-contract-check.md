# 0032 — Framework-Generated TypeScript Contract Check

## Status

Completed

## Objective

Move generation of `check-contract.ts` from the NormalizeContact experiment into shared BoundScript infrastructure. The framework must generate it deterministically; the AI agent must never generate or modify the verification check.

## Requirements

1. Inspect the current check and its use in `experiments/native-typescript-contracts/verify.py`.
2. Implement a minimal reusable generator under `boundscript_internal/` accepting the contract module path, exported function type, implementation module path and exported function name.
3. Generate TypeScript verifying implementation assignability to the declared function type.
4. Integrate it into the native verifier and remove the hardcoded check source artifact. Generated checks are temporary verification infrastructure, not committed source artifacts.
5. Test at least two different contracts and export names, including incompatible signatures and missing exports.
6. Preserve sandbox restrictions, TypeScript compilation and independent verification boundaries; never execute candidate code on the host.
7. Do not modify business contracts or acceptance tests, generate functional acceptance criteria, involve Pi or an LLM in check generation, or introduce a generic verification framework, plugin system or DSL.

## Acceptance criteria

- NormalizeContact continues to verify successfully.
- A second independent contract uses the same generator without modifying it.
- Signature mismatches and missing exports fail TypeScript compilation.
- Existing regression tests pass.
- Identical generator inputs yield reproducible output.

## Delivery and verification evidence

- Added `boundscript_internal/typescript_contract.py`: deterministic, standard-library-only rendering from four explicit inputs, with aliased imports and a typed assignment. No model or candidate-source access.
- Native verification writes the generated check only into its disposable checks directory, before protected-file hashing and read-only mounting. Removed the hardcoded source artifact. Compiler options, sandbox policy and independent acceptance suites remain unchanged.
- Added synthetic compile-only regressions for `FormatLabel`/`formatLabel` and `SumValues`/`sumValues`: positive assignments, incompatible parameters and returns (TS2322), missing implementation exports and contract types (TS2305), reproducibility, escaping and malformed-input rejection. Host compilation is restricted to these trusted synthetic fixtures with no emit; candidate execution remains sandbox-only.
- Added staging regression coverage and updated current infrastructure documentation. Business contracts and acceptance tests were not modified.
- `BOUNDSCRIPT_RUNTIME=podman npm run check`: passed (35 Python tests, 3 opt-in skips; 3 trusted validator tests; Greeting, both contact Boxes and integration container regressions).
- `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/native-typescript-contracts -v`: all 16 passed, including actual NormalizeContact verification and negative/diagnostic engine cases; no Pi/model calls.
- `git diff --check`: passed.
- Product Owner reviewed and explicitly accepted the delivery, then authorized a local commit. No push authorized.

## Authorization

Implementation and assignment registration were initially authorized without committing or pushing. Following review and explicit acceptance, the Product Owner authorized a local commit. Remote publication remains unauthorized.
