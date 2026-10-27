# 0033 — Box-Independent Verification Configuration

## Status

Completed — the Product Owner reviewed and explicitly accepted the correction and authorized a local commit. The original delivery was accepted and committed as `e2c51e7`. No push authorized.

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

## Review correction — independent verification suites

### Objective and requirements

Remove test-file, description and business-fixture assumptions from reusable verification logic. Each Box must explicitly supply its independently owned suite through configuration or a directory convention. Run declared tests without relying on descriptions or test-name patterns, and preserve separate TypeScript compilation, runtime validation, acceptance and property reporting where applicable. Distinguish optional categories from required verification; required tests must never be silently omitted. Keep contracts, acceptance criteria and tests human-owned. Demonstrate two synthetic Boxes with different filenames, descriptions and suite structures using unchanged shared verification code.

### Constraints and acceptance

- No business tests in `boundscript_internal/`, test DSL, plugins or orchestration framework.
- Do not relocate the existing test-name regex into configuration or modify existing acceptance tests to satisfy selection.
- Preserve TypeScript, Typia, Vitest, fast-check, sandbox security, quarantine, integrity checks and verify-before-promotion.
- No business-specific filenames/descriptions in reusable verification logic; a second Box can supply independently named tests and fixtures.
- Required tests cannot silently disappear through configuration; existing NormalizeContact and invalid-candidate rejection must still work.
- Diagnostics must identify failed tests and phases readably.
- Update documentation and record verification evidence; leave the correction uncommitted for review.

### Correction implementation

- Added immutable `VerificationSuite(categories, files)`, explicit support inputs and an explicit not-applicable property category to the shared Box data. Both native entry points validate the suite and fingerprint these settings.
- Preflight inventories conventional test/spec JS/TS files under the independently owned verification root, requires complete one-suite-per-file coverage, and rejects missing inputs, duplicates, undeclared files, traversal/globs and symlinks. Runtime validation and acceptance are mandatory; properties are required unless explicitly not applicable. A category cannot be both declared and not applicable.
- Removed all business-specific test/fixture filenames and description-based selection from reusable verifier mechanics. Stage only the Box's declared tests/support inputs, plus trusted runner adapters and generated exact-include Vitest configs; preserve read-only mounts, protected hashes, quarantine and verify-before-promotion.
- Run whole declared files without test-name patterns. Preserve separate compilation/category phases; mixed-category files run once in an explicitly combined phase. NormalizeContact's unchanged `acceptance.test.ts` therefore runs all 20 examples and 5 properties together, separate from 3 runtime-validator tests. No business tests, contracts, fixtures or implementations were changed.
- Reports retain nested relative file paths, enforce exact declared-module coverage and executed tests in every file, and reject skipped/pending tests, focused `.only` tests, empty collections and truncated reports. Existing sanitized failures and cleanup remain intact.
- Two synthetic Boxes use different test/fixture names, descriptions and directory structures: separate runtime/acceptance/property files versus runtime plus a nested mixed suite. Both pass actual TypeScript, generated Typia, Vitest and fast-check verification without modifying shared mechanics; both reject signature, runtime-shape and behavioral negatives.

### Correction verification evidence

- `npm run test:unit`: 43 tests discovered; 38 passed, 5 opt-in engine tests skipped.
- `npm run test:native:tooling`: 3 trusted validator tests passed.
- `BOUNDSCRIPT_RUNTIME=podman npm test`: Greeting, NormalizeContact, RenderWelcome and integration baseline regressions passed.
- `BOUNDSCRIPT_RUNTIME=podman npm run test:native`: existing local accepted candidate passed compilation, 3 runtime-validator tests and all 25 combined acceptance/property tests with zero skips, plus security, integrity and cleanup.
- `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/native-typescript-contracts -v`: all 24 tests passed in 487 seconds, including both synthetic Box positives/negatives, empty/skipped/pending/focused-suite rejection, existing invalid NormalizeContact submissions and sanitized diagnostic checks.
- Static search confirms no `acceptance.test.ts`, `validators.test.ts`, `cases.json`, `testNamePattern` or acceptance-description prefix in reusable verifier/selection code. `git diff --check` passes.

### Correction limitations

- Actual native selection remains NormalizeContact only; synthetic Boxes are disposable test fixtures, not a second business delivery. No billable generation was performed.
- Test ownership uses explicit literal paths and the documented conventional test/spec JS/TS filename inventory; it does not infer semantics from source. Category meaning and acceptance criteria remain human-owned. Runtime validation and acceptance cannot be disabled; only properties can be explicitly not applicable.
- Mixed-category files have combined phase reporting. Obtaining separate per-category reporting from such a file would require human-owned test restructuring, not description-based inference.
- Existing report bounds remain (100 tests per run, 10 detailed failures); overflow now fails rather than silently truncating successful evidence. Existing conservative Typia path filtering, prototype security limitations and non-provenance configuration fingerprints remain.

## Original delivery limitations (before review correction)

- Only NormalizeContact is configured for actual native execution. Synthetic definitions are wiring/static-compilation tests, not a new business implementation or acceptance suite.
- Verification bundle filenames/layout, phase naming/filter conventions and conservative diagnostic path filtering remain runner conventions. Each future Box needs human-owned task/contracts/tests/Typia validators and explicit build setup; no automatic discovery or orchestration was added.
- Fingerprints bind configuration values between processes, not complete repository provenance. Existing protected-file integrity and submission digests remain unchanged.
- No billable live generation was performed; generation selection/promotion/quarantine were exercised with mocks, and actual candidate verification ran offline. Existing sandbox/prototype limitations remain as documented.
