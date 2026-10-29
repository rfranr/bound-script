# 0039 — Remove Contract Promotion Ownership

Status: In Review

## Scope and requirements

Correct assignment 0038 without redesigning the native Box workflow. The request was supplied as Proposed and explicitly directs this correction.

The consumer owns the contract. The agent generates the implementation. The verifier validates the implementation against the contract. Promotion publishes only the independently verified implementation, preserving its exact bytes.

- Remove contract copying during promotion from both native generators; successful generation must not create, copy or modify consumer-owned contracts as outputs.
- Preserve the public contract as a read-only input during generation and verification and retain the same portable sibling layout for relative imports such as `./contract`.
- Update tests expecting `accepted/contract.ts` and correct documentation introduced by 0038 describing contract copying/distribution alongside promoted source.
- Preserve generation, verification, isolation and regression behavior, including NormalizeContact and RenderWelcome regressions.
- `accepted/` receives only the verified implementation from the generation pipeline; no contract is copied during promotion.

Make the smallest coherent correction. Do not introduce contract packaging, registries, abstractions, import rewriting or additional promotion mechanisms. Use credential-free tests only; model-backed generation requires separate explicit authorization. Do not commit or push. Report changed files, test evidence and remaining limitations for Product Owner review.

## Delivery and evidence

Removed only the contract-copy statement from each native generator's promotion block. Read-only sandbox inputs, sibling import paths, verification, source/contract integrity checks and byte-preserving implementation promotion are unchanged.

Changed files:

- `experiments/native-typescript-contracts/generate.py`, `experiments/render-welcome-native/generate.py`: implementation-only promotion.
- Native `test_box_definition.py`, `test_spike.py`, welcome `test_workflow.py`: assert no promoted contract, only implementation output and unchanged input contracts.
- `tests/internal/test_portable_imports.py`: distinguish consumer-owned contract fixture setup from implementation integration; cover both generators leaving existing contracts untouched and making exactly one promotion copy, with byte-identical implementation contents (including CRLF).
- Root README, both native README files and `docs/development/architecture.md`: document consumer ownership and integration beside an existing contract, never generator distribution of contracts.
- Assignment 0038: annotate original evidence as superseded for contract promotion, retaining historical traceability. This assignment records the correction.

## Credential-free verification

- `BOUNDSCRIPT_RUNTIME=podman npm run check`: passed. Python suites: 56 tests total, six opt-in skips; both validator suites passed (three tests each); public-contract compatibility compiled; baseline Greeting, NormalizeContact (20 cases), RenderWelcome (81 cases) and integration (20 cases) passed.
- `BOUNDSCRIPT_RUNTIME=podman npm run test:native`: passed against the existing local implementation; three validators, 20 acceptance examples and five properties, with offline isolation/integrity checks.
- `BOUNDSCRIPT_RUNTIME=podman npm run test:welcome`: passed against the existing local implementation; three validators, six acceptance examples and one property, with offline isolation/integrity checks.
- `git diff --check`: passed. No containers remained after verification.

## Limitations / review notes

No model-backed generation was executed. Promotion paths were exercised using mocked generation/verification in credential-free tests; actual offline verifiers independently exercised the existing local candidates. Native accepted candidates are ignored local artifacts and remain necessary for reproducing the separate full native verifier runs on a clean checkout. Existing contract artifacts from the former 0038 behavior are not deleted or managed by this correction; no contract cleanup/promotion mechanism was introduced. Consumers remain responsible for their contracts and implementation integration.

Following delivery, the Product Owner authorized a local commit. Pushing remains unauthorized. Acceptance remains with the Product Owner.
