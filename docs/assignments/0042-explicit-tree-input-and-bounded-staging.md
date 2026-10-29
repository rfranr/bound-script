# 0042 — Explicit Tree Input and Bounded Staging

Status: In Review — Product Owner approved, subject to final code review
Type: Implementation — step 1 only
Depends on: approved revised design 0041

## Authorization and requirements

The Product Owner accepted the narrowed 0041 design and authorized a separate implementation assignment for step 1 only: explicit tree input and bounded staging. Keep the increment small, preserve single-file behavior and existing security guarantees, and provide focused tests/evidence.

Do not implement shared tree execution/import closure (step 2) or prepare the business A/B experiment (step 3). Do not modify the generator or BoxDefinition. Tree generation, promotion, quarantine, publication/recovery, artifact formats and unrelated infrastructure remain deferred. No model calls, commits or pushes are authorized. Use Docker explicitly for any real-engine checks.

## Implementation boundary

- Add explicit verification CLI tree selection; retain existing file/default/baseline/fingerprint behavior.
- Add a small context-managed staging function: safe directory-relative traversal, regular TypeScript files, complete in-memory inventory, bounded copying and cleanup, with change detection.
- Use the approved proposed bounds: 16 source files, 16 KiB aggregate, depth 8 and 240 ASCII-byte relative paths. Reject reserved contract collisions, dependency/config/emitted outputs, symlinks, hard links, special entries and ambiguous/unsafe paths.
- No tree is executed or promoted. A valid CLI tree input is staged and cleaned up, then returns an explicit infrastructure failure indicating tree verification execution is not implemented. This avoids representing staging as independent verification or silently verifying only the entry.
- Focused filesystem/CLI tests use inert source text, not business implementations. Test limits, unsafe objects, mutations, cleanup and unchanged file dispatch. No runtime policies or consumer assets change.

Delivery remains subject to Product Owner review; do not self-accept.

## Delivery

- Added `boundscript_internal/source_tree.py`: plain context-managed staging, descriptor-relative no-follow traversal, single-link regular UTF-8 `.ts` source validation, reserved-path/case-collision checks, bounded reads, private byte-identical snapshots and sorted in-memory `(path, size, sha256)` inventories. Rechecks source inventory, root identity and copied bytes before yielding; removes staging on success, rejection and caller exceptions.
- Added a derived 144-entry traversal budget (16 files × nine file/ancestor entries) to bound empty-directory enumeration as well as file bytes/count. Empty directories are not copied or included in source identity. Same-device traversal is required; hostile same-authority host writers/mount manipulation and atomic capture of a live producer are not claimed to be solved.
- Updated `boundscript_internal/native_cli.py` to accept `--source-tree DIRECTORY` after the existing optional fingerprint. Malformed/mismatched inputs fail before staging. Valid input stages and cleans up, then exits nonzero with `FAIL [infrastructure] Source tree staging completed; tree verification is not implemented`. No tree compiler, runtime or acceptance execution is enabled.
- Added `tests/internal/test_source_tree.py` with 11 focused tests covering exact bytes/inventory/private modes, bounds, unsafe inputs, root/ancestor symlinks, symlink substitution between stat/open, hard links/FIFO/socket/device mismatch, source/snapshot/root mutation, partial-stage cleanup and CLI dispatch/non-execution.
- Updated root/internal README documentation to describe the intentionally incomplete CLI mode. Recorded the explicit acceptance of revised design 0041 in its document; no implementation is marked accepted.

### Verification

- `BOUNDSCRIPT_RUNTIME=docker python3 -B -m unittest discover -s tests/internal -p test_source_tree.py -v`: PASS, 11 tests, approximately 0.04 seconds; no compiler/container/model invoked.
- `BOUNDSCRIPT_RUNTIME=docker npm run check`: PASS. Shared Python suite: 54 tests, four existing opt-in skips; baseline workflow: six tests; local native suites: two each with one existing opt-in skip each. Both three-test validator suites, contract compatibility compilation and isolated baseline verification pass.
- `BOUNDSCRIPT_RUNTIME=docker npm run test:welcome`: PASS against the existing single-file candidate; three validators, six examples and one property, protected-input integrity and cleanup pass; no promotion.
- Whitespace checks pass. Generator, BoxDefinition, workspace, independent verifier, compiler/reporter/Vitest tooling, runtime policy, Box definitions and consumer assets remain unchanged.

### Deliberate limitations

This increment cannot independently verify a source tree. The new CLI mode always returns failure after staging rather than implying verification success. It creates no receipts, persisted inventories, source artifacts, quarantine or promoted trees. It does not check public export/type correctness or import closure; those are step 2. No business A/B candidates were prepared and step 3 was not performed. Only inert staging fixtures and existing single-file regressions were exercised.

No model-backed generation, commits or pushes occurred. The Product Owner subsequently approved 0042 subject to final code review and authorized step 2 separately as 0043. The staging-only CLI limitation and its dispatch regression are superseded by 0043; bounded staging itself is retained.
