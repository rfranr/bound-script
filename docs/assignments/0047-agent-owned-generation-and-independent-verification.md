# 0047 — Agent-Owned Generation and Independent Verification

Status: In Review
Type: Implementation — step 2 of approved design 0045

## Authorized scope

Add explicit opt-in `--agent-owned` generation connecting the existing generator to 0046 complete-source scanning/snapshots and 0043 independent tree verification. Let the agent choose its internal TypeScript organization without architectural hints; accept one or several files equally while preserving the public contract, implementation.ts entry and named export. Reuse the workspace, scanner, snapshot and verifier; destroy the credential-bearing container before independent verification and verify the complete tree.

Preserve legacy single-file generation, promotion and quarantine unchanged. New-mode outputs must never be promoted or quarantined, even on success. Preserve sandbox policies, limits and security guarantees. Implement step 2 only; do not invoke a real LLM, prepare a business Box, or change contracts, acceptance tests, BoxDefinition or verifier. Leave changes uncommitted for Product Owner review.

## Required evidence

Credential-free simulated generation of single-file and multi-file outputs, independent Docker verification, integrity and cleanup checks, and legacy regression tests. Report results and limitations; acceptance remains with the Product Owner.

## Delivery and evidence

- Added an explicit opt-in flag in the shared generation CLI, neutral bounded-source prompt, and verification-only orchestration. Existing selection dispatch already forwards generation arguments; its usage text now identifies the flag.
- Reused complete-source scanning/snapshot lifecycle and unchanged independent `--source-tree` verification with Box fingerprint, pre/post complete inventory and original task/contract checks. New mode cannot enter legacy quarantine/promotion; snapshots are discarded on success and failure.
- Added credential-free orchestration tests using the real trusted scanner and private staging, simulated producer completion, and independent verification subprocesses for synthetic identity fixtures (one source and nested sources including an unused file). No business Box, consumer oracle or verifier changes.
- `BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 PYTHONPATH=.:tests/internal python3 -m unittest test_agent_owned_generation test_source_scanning test_native_workflow test_tree_verification test_portable_imports`: 33 tests passed. Includes real Docker scan/sandbox checks, separate-process Docker verification for both organizations, existing workspace completion/cleanup simulations and legacy/portability regressions. Log: `/tmp/boundscript-0047-targeted.log`.
- `BOUNDSCRIPT_RUNTIME=docker npm run check`: passed (79 internal tests, seven opt-in skips, plus remaining checks). Log: `/tmp/boundscript-0047-check.log`. `git diff --check`: passed.
- The first focused Docker run passed both independent verifications but exposed a test-harness integrity baseline captured before trusted Typia fixture generation. Moved the test baseline after fixture setup; the full targeted rerun passed. No consumer expectations were changed.
- Snapshot cleanup, changed unused source/membership, changed task, verifier failure, unchanged accepted bytes and no quarantine/copy are asserted. Existing 0046 workspace tests cover container removal before yielding and fail-closed cleanup/scan binding. No new test containers remain. An exited generation container created about seven hours before these checks was left untouched.

## Limits and disposition

No Pi/provider call, real credential use, live generation experiment, commit or push. Generation completion is simulated; Docker scanner/sandbox evidence and independent Docker verifier evidence are separate checks, not an end-to-end live-agent claim. Existing literal-scan, network, trusted-host and abrupt-termination limitations remain unchanged. Outputs in this mode are intentionally temporary, with no publication/retention capability. The Product Owner subsequently authorized a local commit. Delivery remains In Review; commit authorization is not implementation acceptance.
