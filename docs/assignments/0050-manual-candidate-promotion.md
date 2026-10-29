# Assignment 0050 — Manual Promotion of Verified Box Candidates

Status: In Review — Product Owner acceptance pending
Type: Implementation

## Requirements

Implement an explicit human-invoked promotion command selecting a Box and retained candidate ID. Existing PASS evidence is necessary but is not authorization or sufficient verification evidence. Validate Box identity, metadata and the complete bounded no-follow source inventory; reject unsafe, missing, changed or unexpected files.

Independently reverify the complete source against current consumer-owned contract, task, fixtures, acceptance suites and BoxDefinition. Bind and check source and verification-input integrity throughout. Do not modify verification criteria to pass a candidate.

Publish a complete, immutable, sequential local version under `versions/0001/source/` with `manifest.json`, preserving every source path and byte. Never overwrite or partially publish. Record candidate ID, Box identity, version, inventory digest, BoxDefinition fingerprint and SHA-256 hashes of consumer-owned verification inputs.

No Pi/LLM calls, generation, repair, accepted/quarantine changes, consumer integration, candidate deletion, generation behavior changes, artifact framework, SemVer, registry or language migration. Keep changes uncommitted; no push or self-acceptance.

## Verification and delivery

Use synthetic/fixture candidates only. Cover single/multi-file success, exact preservation, FAIL, source mutation, invalid metadata, reverification failure, input changes, no overwrite/partial publication, unsafe symlinks/traversal and candidate preservation. Check legacy and agent-owned regressions. Run focused tests, `npm run check` and explicit Docker-backed independent verification. Deliver minimal implementation, CLI, usage and evidence. Escalate scope-changing architectural decisions to the Product Owner.

## Delivery and evidence

- Added `boundscript_internal/native_promotion.py` and explicit CLI routing; generation and verifier criteria are unchanged.
- Current consumer-owned inputs are copied to a private verification root and hashed in the manifest. Source and original/frozen inputs are checked again before publication.
- Publication uses a private host-owned versions directory, directory advisory lock and Linux atomic no-replace rename. Version source paths/bytes are copied without flattening; existing versions and retained candidates are not modified.
- Usage: `python3 -B experiments/native_cli.py promote plan-fulfillment --candidate <candidate-id>` (also documented in `README.md`).
- Focused Docker run: `BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 python3 -B -m unittest discover -s tests/internal -p test_native_promotion.py -v`: **9 tests passed**, including actual independent compiler/runtime/acceptance/property verification. No model calls.
- Final `npm run check`: **passed**; internal 90 tests (8 opt-in skips), minimal-box 6 passed, native 2 (1 skip), welcome 3 (2 skips), tooling suites and contract composition passed, baseline/container composition checks passed. This includes existing legacy and agent-owned generation regressions.
- During validation, a fixture outside the repository could not resolve Typia tooling; placing it under an existing verification root also interfered with concurrent suite inventory tests. The fixture now lives under repository `tests/`, outside all Box verification roots. Final Docker and full checks passed sequentially.
- Changes remain uncommitted. No push, consumer integration, real generation or acceptance performed.

## Decisions and limitations for review

Linux-specific publication reuses the existing Linux/procfs environment; no registry or artifact layer was added. Published versions are immutable under normal application operations, not against filesystem owners/privileged writers. Atomic publication does not guarantee power-loss durability. A killed writer can leave hidden `.pending-*` data; future promotion fails closed for human inspection/removal. Integrity checks cannot detect transient mutations restored between observations, but verification uses frozen inputs rather than mutable originals. Stronger durability, hostile-host monitoring, automatic crash recovery or portability would require a separately authorized scope extension.
