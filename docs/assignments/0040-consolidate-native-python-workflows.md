# 0040 — Consolidate Native Box Python Workflows

Status: In Review
Type: Structural refactoring

## Authorization and scope

The Product Owner authorized implementation of the proposed consolidation assignment. No model-backed generation, commits or pushes are authorized. Delivery remains subject to Product Owner review and acceptance.

## Requirements

Consolidate duplicated NormalizeContact and RenderWelcome Python generation orchestration, verification entry points and infrastructure tests into `boundscript_internal/` and shared tests. This is behavior-preserving, not an architectural redesign or migration to TypeScript.

Shared generation must preserve preflight, existing agent workspace and sandbox lifecycle, authorized-input boundaries, credential scanning, integrity checks, independent verification in a separate process, failure quarantine and promotion of only verified implementation bytes. Reuse `agent_workspace.py` and `container_runtime.py`; do not duplicate their responsibilities.

Provide a single explicit deterministic verification entry point accepting a selected existing `BoxDefinition`, Box root and candidate. Preserve fingerprints, exact declared suites, failure classifications/diagnostics and existing baseline support. Do not introduce discovery, arbitrary module loading, plugins, registries, manifests, a DSL or unnecessary abstraction.

Keep each `native_box.py`, contract, requirements, fixtures and acceptance tests independently owned. Do not modify candidate source, contracts, fixtures, acceptance criteria or generated implementations. Preserve portability without import rewriting, read-only consumer contracts, offline independent verification, Docker/Podman policies, resources, Vitest policy, dependencies and security diagnostics. Failed candidates must never be promoted.

Consolidate infrastructure tests without weakening assertions, parameterizing both Boxes where appropriate. Demonstrate third-Box configuration with a synthetic fixture rather than a business Box; no additional generation/verification script or duplicated infrastructure tests should be needed.

Preserve npm workflows including build:welcome, test:welcome, test:native and check. Builds and credential-free workflows must never invoke models, generation or retries automatically.

Excluded: Python migration, runtime replacement, contract redesign, Box composition, deployment/packaging changes, promotion/human-acceptance lifecycle changes, unrelated hardening or functionality. Report out-of-scope issues separately.

## Delivery

Inspect existing flows before implementation; deliver the smallest coherent refactor. Report consolidated responsibilities, removed/created/modified files, shared invocation, behavioral evidence, credential-free test results, retained duplication and compatibility limitations. Leave changes uncommitted and never self-accept.

## Implementation constraints confirmed during work

The Product Owner approved plain shared functions rather than runner classes or factories, and required Box selection to remain separate from core generation/verification. A third Box must not require core workflow changes. Final engine verification uses `BOUNDSCRIPT_RUNTIME=docker` explicitly. The reported host-level Podman/AppArmor issue is outside this assignment; no runtime, policy or resource-check workaround was made.

## Initial inspection

Both generation scripts duplicate preflight, workspace invocation, fingerprinted subprocess verification, bounded scanned-source quarantine and digest-checked promotion. Welcome additionally emits progress and classified generation diagnostics; NormalizeContact withholds arbitrary errors. Verification wrappers duplicate candidate selection, fingerprint validation, retained-candidate reporting and failure handling; only NormalizeContact supports baseline selection. Workflow tests mix shared lifecycle assertions with local fixture/behavior checks.

## Delivery

### Consolidated responsibilities and invocation

- `boundscript_internal/native_generator.py`: plain `generation_prompt`, `quarantine`, `generate` and `cli` functions. Reuses the unchanged workspace/runtime helpers; receives Box definition/root and independent verifier command explicitly. Retains both Boxes' existing diagnostic behavior.
- `boundscript_internal/native_cli.py`: plain `verify` and `cli` functions for candidate/baseline selection, fingerprint validation and classified failure reporting, delegating to the unchanged offline native verifier.
- `experiments/native_cli.py`: explicit lazy Box selection, separate from core workflows; dispatches one requested operation for one Box. No discovery, arbitrary module loading, registry, factories or runner classes.
- Shared tests parameterize both Boxes' orchestration/security wiring. Box-owned fixture and business-negative checks remain local. Existing synthetic definitions exercise the shared generation path (mock agent/subprocess) and shared verification entry point with real offline Typia/Vitest, without adding scripts or a business Box.

```sh
python3 -B experiments/native_cli.py verify normalize-contact [candidate.ts]
python3 -B experiments/native_cli.py verify normalize-contact --baseline
python3 -B experiments/native_cli.py verify render-welcome [candidate.ts]
# Billable; documented only, NOT executed during this assignment:
python3 -B experiments/native_cli.py generate normalize-contact
python3 -B experiments/native_cli.py generate render-welcome
```

A third Box uses the same functions with its existing `BoxDefinition` and root. Exposing it through the CLI requires only an explicit branch in the selection adapter, not changes to core orchestration, copied scripts or another infrastructure test suite.

### File inventory

Removed from both native Box roots: `generate.py`, `verify.py`.

Infrastructure tests relocated/consolidated:
- Removed NormalizeContact `test_spike.py`, `test_diagnostics.py`, `test_box_definition.py` and Welcome `test_workflow.py`.
- Added `tests/internal/test_native_workflow.py`, `test_native_diagnostics.py`, `test_native_box_definition.py`.
- Added each Box's local `test_box_behavior.py` to retain independently owned fixture/definition/business checks.

Other created files:
- `boundscript_internal/native_generator.py`
- `boundscript_internal/native_cli.py`
- `experiments/native_cli.py`
- This assignment record.

Modified files:
- `package.json`: native generation/verification commands use the shared selection CLI; build commands unchanged.
- `tests/internal/test_native_verifier.py`, `test_portable_imports.py`: shared entry wiring, core/selection separation, unchanged portability/promotion assertions and contract-change rejection.
- `experiments/minimal-box/test_workflows.py`: existing cross-entry-point import/assertion checks target the consolidated entry point; baseline implementation unchanged.
- `README.md`, `boundscript_internal/README.md`, `docs/development/architecture.md`, and both native Box README files: ownership, invocation and shared test locations.

No Box definitions, tasks, contracts, candidate source, fixtures, TypeScript acceptance tests, dependencies, runtime code, sandbox limits, verification policy or trusted diagnostic adapters were changed.

### Credential-free verification evidence

Final engine checks explicitly use Docker:

- `BOUNDSCRIPT_RUNTIME=docker npm run check`: PASS. 43 shared Python tests (4 opt-in skips), 6 baseline workflow tests, 2 local tests per native Box (one opt-in skip each); both validator suites (3 tests each), public-contract compilation and all baseline isolated regressions pass.
- `BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 python3 -B -m unittest discover -s tests/internal -v`: PASS, all 43 tests, no skips. Includes both sandbox profiles without credentials/models, independent synthetic verification, negative diagnostics, suite completeness/focus/skip rejection and parameterized lifecycle tests.
- After routing real synthetic positives/negatives through the shared entry point, its targeted Docker engine suite: PASS, all 6 tests.
- `BOUNDSCRIPT_RUNTIME=docker npm run test:welcome`: PASS against the existing local candidate: 3 validators, 6 fixtures, 1 property; integrity and cleanup pass; no promotion.
- Welcome local opt-in Docker suite: PASS, 2 tests, including signature/shape/behavior/mutation rejection and unchanged accepted bytes.
- `BOUNDSCRIPT_RUNTIME=docker npm run test:native -- experiments/native-typescript-contracts/quarantine/failed-8ifizg1w/implementation.ts`: PASS, 3 validators, 20 fixtures and 5 properties; integrity/cleanup pass; no promotion or source changes.
- Absolute CLI verification of Welcome from outside the checkout: PASS.
- `git diff --check`: PASS.

An earlier Podman check preceded the Docker-specific instruction; delivery evidence above was rerun using Docker. No model-backed generation, credential use, commits or pushes occurred.

### Remaining duplication and compatibility limits

- Box definitions, requirements, contracts, validators, fixtures and business checks remain separate by design. Small local unittest setup and explicit CLI selection branches are configuration/ownership, not copied orchestration. Baseline non-native workflows remain outside this refactor.
- Old per-Box Python script paths are removed; use the shared CLI or preserved npm scripts. No compatibility shims or packaging changes were added.
- This checkout has no local accepted NormalizeContact source. Its default `npm run test:native` therefore retains the existing missing-candidate infrastructure failure. The same npm command passes with an explicit existing quarantined candidate; it was not promoted. The local Contact business-negative opt-in test still requires the missing accepted path, while shared native diagnostic negatives and synthetic engine tests pass.
- Historical `test:native:baseline` remains an expected compilation failure; in this checkout the retained baseline uses a legacy sandbox import. No baseline source was repaired.
- Model-backed generation was not run; generation behavior is covered by parameterized mocked agent/verification lifecycle tests and credential-free real sandbox-profile tests, not a fresh provider call.

Awaiting Product Owner review and acceptance. The Product Owner subsequently authorized a local commit of this delivery; pushing remains unauthorized. This does not constitute acceptance.
