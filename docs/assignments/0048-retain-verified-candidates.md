# 0048 — Retain Verified Candidates for Human Review

Status: In Review
Type: Implementation

## Request and authorization

The supplied assignment was labeled Proposed for Product Owner review and explicitly requested implementation, tests and this deliverable. Work is limited to that requested implementation; neither requirements nor acceptance are self-approved.

## Requirements

- Add explicit `--retain-candidate`, valid only with `--agent-owned`; preserve defaults and legacy behavior.
- Retain complete source trees with exact bytes, filenames and directories only after whole-tree credential scanning, generation-container destruction and scan/snapshot binding. Never retain on scanner, integrity or cleanup failure.
- Use a private, Git-ignored `candidates/<unique-id>/` under the corresponding Box, separate from accepted/quarantine; never overwrite candidates.
- Persist only minimal review metadata: Box name, source inventory digest, PASS/FAIL verification result, file count, model/reasoning configuration and candidate identifier. No credentials, secret prompts, provider events or unrestricted logs.
- Allow safely scanned/integrity-validated verification failures to be retained as FAIL, without acceptance or promotion.
- Preserve independent verifier, consumer contracts/tasks/fixtures/tests, existing sandbox restrictions and source-read-only verification. Retention must not add an execution path.
- No registries, versioning/publication workflows, approval APIs, new Box types or generated-code architecture requirements. Reuse staging/digest/verification; prefer a small generator extension.

## Evidence and disposition required

Focused simulated-generation/synthetic-credential tests: successful one/many source retention, byte/directory fidelity, accurate failure status, no retention on scan/integrity/cleanup failure, traversal/overwrite resistance, unchanged legacy/default mode and no acceptance/promotion. Run relevant tests and `npm run check`. No real LLM calls, commits, pushes or self-acceptance. Report design, evidence and limitations for review.

## Design and implementation

- Extend only shared generation orchestration and CLI flags; `--retain-candidate` requires `--agent-owned` at both CLI and direct function boundaries. Existing defaults and legacy promotion/quarantine remain intact.
- Retain only after the generation workspace has yielded its scanned, post-container-cleanup bound snapshot, the independent verifier has completed, and full source plus original task/contract integrity have been checked again. A completed nonzero verifier exit permits FAIL retention only after those same checks; the original exception still propagates. Launch errors/timeouts retain nothing because verification did not complete.
- Store `candidates/<server-generated-32-hex-id>/source/` and `review.json`. Source paths/bytes remain unchanged; the protected consumer contract is not a generated source and is not copied. Reuse source staging/inventory for pre-copy validation and post-copy equality. Persist exactly the required metadata fields, without logs, prompts or provider data.
- Git-ignore the candidates directories of both existing native Boxes. Require host ownership and mode 0700 on the candidates parent, pin ancestors without symlink traversal, create the ID directory exclusively, and anchor copy/metadata writes to the opened parent descriptor. Reject unsafe IDs, symlink parents, public parents and collisions. Write files privately; remove incomplete candidate directories on ordinary copy/inventory/metadata exceptions.
- Retention occurs after verification and is not passed or mounted into its container. Existing verifier source views remain read-only; retained candidates confer no execution, approval or publication authority. Contracts, tasks, fixtures, acceptance suites, BoxDefinition, verifier and runtime policy were not changed.

## Verification evidence

- `BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 PYTHONPATH=.:tests/internal python3 -m unittest test_agent_owned_generation test_source_scanning test_native_workflow test_tree_verification test_portable_imports`: 35 tests passed. Log: `/tmp/boundscript-0048-targeted.log`.
- Tests cover exact single-file and nested-file retention (including unused source, BOM and CRLF), required metadata and inventory equality, private modes, successful independent Docker verification both with and without retention, simulated completed verifier FAIL retention, preserved failure propagation, scan/binding/container-cleanup/source/task failures retaining nothing, verifier timeout, copy corruption/failure and metadata failure cleanup, traversal/collision/symlink/public-parent refusal, Git-ignore rules, unchanged accepted bytes and absence of promotion/quarantine. Existing real-scanner and workspace lifecycle tests provide synthetic credential and fail-closed cleanup coverage.
- `BOUNDSCRIPT_RUNTIME=docker npm run check`: passed, including 81 internal tests (seven opt-in skips) and remaining suites/baseline checks. Log: `/tmp/boundscript-0048-check.log`. `git diff --check`: passed.
- The initial focused test caught a descriptor-path staging mismatch: ordinary staging correctly rejects `/proc/self/fd` symlink ancestors. The retention copy now uses the existing inventory routine on its securely opened source descriptor; all final targeted/full checks passed with no staging-policy relaxation.
- Test-created containers and temporary candidates were cleaned up. The unrelated exited generation container already noted in 0047 remains untouched.

## Limitations and review disposition

No real LLM, provider or real credential use. Generation completion and verifier failure status are simulated; successful independent verification and synthetic credential scanning have separate real Docker evidence. Existing literal-scanning and trusted-host limitations remain. Retention uses Linux descriptor paths (`/proc/self/fd`), consistent with the current sandbox environment. It preserves the existing bounded source snapshot, not workspace inputs or non-source/empty-directory artifacts. Ordinary errors clean partial copies; SIGKILL, host failure or filesystem cleanup failure can leave an incomplete private directory without completed review metadata. No crash-atomic persistence, retention lifecycle, replay command or publication mechanism is claimed.

The Product Owner subsequently authorized a local commit. Delivery remains In Review; commit authorization does not accept any generated candidate or mark the assignment accepted.
