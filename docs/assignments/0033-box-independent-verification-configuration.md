# 0033 — Box-Independent Verification Configuration

## Status

Completed. Reviewed and explicitly accepted by the Product Owner. Local commit authorized; no push authorized.

## Objective

Remove NormalizeContact-specific contract/export configuration from reusable native verification mechanics. Prepare the workflow for a second independent Box without implementing that Box.

## Requirements

1. Inspect selection in native `generate.py`, `verify.py` and `generate_contract_check()`.
2. Introduce a minimal explicit Box definition carrying generation and verification inputs.
3. Obtain contract module, exported function type and implementation export from that definition, not hardcoded NormalizeContact values.
4. Retain implementation paths and temporary mounts as runner conventions where appropriate.
5. Generation and verification must use the same definition and cannot silently select different definitions.
6. Preserve independently human-owned acceptance tests and Typia validation per Box.
7. Test two different definitions driving selection and generated checks through unchanged shared infrastructure.

## Constraints

- No second business Box, plugin system, registry, DSL or orchestration framework.
- Do not change business contracts, acceptance criteria or implementations.
- Do not weaken sandbox isolation, credential handling, quarantine or verify-before-promotion.
- Do not discover requirements or infer exports from source code.
- Keep changes minimal and deterministic.

## Acceptance criteria

- No NormalizeContact-specific identifiers in reusable contract-check generation or Box-selection logic.
- Existing NormalizeContact workflow still passes.
- A second synthetic definition drives the same contract-check mechanism.
- Generation and verification cannot silently select different definitions.
- Existing regression tests remain green.

## Delivery

Report changes, test evidence and remaining limitations for review. The original delivery was left uncommitted; following review and acceptance, the Product Owner authorized a local commit.

## Implementation and verification evidence

- Inspected the native runners and `generate_contract_check()`: the renderer was already generic; runner selection and generation prompts held Box-specific names.
- Added immutable `boundscript_internal/box_definition.py` and the single explicit native `native_box.py` configuration. Both runners select public inputs, exports, destination and the independently owned verification bundle from it.
- Generation sends a deterministic definition fingerprint to the separate verifier; differing settings fail before candidate checking. No requirements or exports are inferred.
- Preserved runner implementation/mount conventions, separate offline verification, protected hashes, credentials, quarantine and verify-before-promotion. Contract write/symlink probes target the selected contract module.
- Synthetic definition tests cover two public-input/verification bundles, generation prompts/destinations, staged checks/validators, phase selection and mismatch rejection. Trusted synthetic TypeScript fixtures compile valid exports and reject invalid signatures/missing exports for two definitions; no second business Box was implemented.
- `npm run test:unit`: 37 tests total, passing with 3 opt-in engine tests skipped.
- `npm run test:native:tooling`: 3 validator tests passed.
- `BOUNDSCRIPT_RUNTIME=podman npm test`: Greeting, both baseline Boxes and integration passed.
- `BOUNDSCRIPT_RUNTIME=podman npm run test:native`: existing local accepted candidate passed strict TypeScript, 3 Typia tests, 20 acceptance cases and 5 properties, plus isolation/integrity/cleanup.
- `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/native-typescript-contracts -v`: all 18 tests passed, including negative candidate and diagnostic engine checks. Unit and full positive native checks were rerun after making contract probes use the configured module.
- `git diff --check`: clean.

## Remaining limitations

- Only NormalizeContact is configured for actual native execution. Synthetic definitions are wiring/static-compilation tests, not a new business implementation or acceptance suite.
- Verification bundle filenames/layout, phase naming/filter conventions and conservative diagnostic path filtering remain runner conventions. Each future Box needs human-owned task/contracts/tests/Typia validators and explicit build setup; no automatic discovery or orchestration was added.
- Fingerprints bind configuration values between processes, not complete repository provenance. Existing protected-file integrity and submission digests remain unchanged.
- No billable live generation was performed; generation selection/promotion/quarantine were exercised with mocks, and actual candidate verification ran offline. Existing sandbox/prototype limitations remain as documented.
