# 0041 — Design Evolvable Box Artifacts

## Revised proposal: verify a multi-file TypeScript Box

**Status:** Completed — revised design explicitly accepted by the Product Owner

**Type:** Design only

**Depends on:** Assignment 0040, implemented in `2dbd144`

The previous proposal was rejected as too broad. This revision replaces it with one verifier-only experiment. It does not authorize implementation.

## 1. One hypothesis

**The existing independent verifier can verify a TypeScript Box without knowing its internal file organization, provided that its public entry and consumer-owned contract remain stable.**

Prove this using two manually prepared test candidates for RenderWelcome:

- **A:** one implementation file.
- **B:** the same public entry/export, implemented through multiple freely organized TypeScript files and relative imports.

Both must pass the same unchanged contract, validators, fixtures and acceptance/property tests. No model call is needed. Candidate B represents an organization an agent could choose; this experiment does **not** establish multi-file generation support.

## 2. Smallest proposed scope

Extend **verification only** to accept an explicitly selected source directory in addition to the existing file input. Keep one compiler/test execution path.

Proposed invocation:

```sh
python3 -B experiments/native_cli.py verify render-welcome candidate.ts
python3 -B experiments/native_cli.py verify render-welcome --source-tree candidate-directory
```

The syntax is illustrative. Selection must remain explicit; no discovery, arbitrary module loading or plugins.

**No BoxDefinition changes are needed for this proof.** The source directory is a runtime verification input. Retain existing definitions, named exports, contract paths, suites and accepted paths. Keep `implementation.ts` as the public entry relative to the submitted directory because existing acceptance tests already import that name. Do not prescribe helper filenames, directories, functions or classes.

Single-file generation, verification, quarantine and promotion must retain their current behavior. Directory verification does not promote anything and does not make directories valid generation or accepted-path inputs.

### Explicitly deferred

- Multi-file agent generation and credential scanning.
- Tree promotion, transactional publication and crash recovery.
- Multi-file quarantine.
- Persistent inventories, verification receipts and artifact identity protocols.
- Packaged/compiled deliverables, OCI images and generic artifact specifications.
- Consumer installation/integration, dependency support and unrelated hardening.

## 3. Relevant current behavior

| Source | Existing behavior and necessary change for the proof |
| --- | --- |
| [`native_cli.py:7–23`](../../boundscript_internal/native_cli.py#L7) and [`experiments/native_cli.py:28–44`](../../experiments/native_cli.py#L28) | Explicit Box/candidate selection already exists. Add only explicit tree-input forwarding; preserve file/default/baseline invocations. |
| [`native_verifier.py:270–315`](../../boundscript_internal/native_verifier.py#L270) | Accepts one regular file of at most 16 KiB, mounts it read-only as `/implementation/implementation.ts`, and generates the signature consumer. Tree input needs bounded staging and read-only visibility of all submitted source files. |
| [`compiler-diagnostics.mjs:6–32`](../../boundscript_internal/compiler-diagnostics.mjs#L6) | Compilation follows entry imports, but the import-policy pass inspects only `implementation.ts`. Check every submitted source, including unused helpers, and reject relative resolution outside the authorized source/contract boundary. |
| [`native_verifier.py:147–168`](../../boundscript_internal/native_verifier.py#L147) | Compiler diagnostic paths recognize only the entry and contract. Permit bounded, validated helper-relative locations through the existing sanitizer. |
| [`native_verifier.py:252–268`](../../boundscript_internal/native_verifier.py#L252), [`compiler-diagnostics.mjs:34`](../../boundscript_internal/compiler-diagnostics.mjs#L34), [`diagnostic-reporter.mjs:66–69`](../../boundscript_internal/diagnostic-reporter.mjs#L66), [`vitest.config.mts:4–15`](../../boundscript_internal/vitest.config.mts#L4) | Reports/caches currently use writable `/implementation`. A read-only source directory needs a separate writable work directory; change trusted paths, not execution/resource policy. |
| [`box_definition.py:44–95`](../../boundscript_internal/box_definition.py#L44) | Exact independently owned suites, explicit support inputs, signature rendering and fingerprints are reusable. Keep candidates outside the verification root: its recursive test discovery must not mistake a helper named `helper.test.ts` for an oracle. |
| [Welcome definition](../../experiments/render-welcome-native/native_box.py#L7) and [acceptance suite](../../experiments/render-welcome-native/acceptance.test.ts#L3) | Already specify the public contract/export and import only the stable entry. Neither needs helper-specific knowledge or content changes. |

The current generator prompt and workspace explicitly require one submission file ([generator:23–33](../../boundscript_internal/native_generator.py#L23), [workspace:105–141](../../boundscript_internal/agent_workspace.py#L105)). Leave those restrictions intact; relaxing them is not necessary to test this hypothesis.

## 4. Minimal verification design

### Source boundary

For tree mode, the selected directory contains implementation-owned source only. Require root `implementation.ts`; allow arbitrary internal organization within safety bounds. Stage the existing consumer-owned contract as read-only sibling `contract.ts`, as today. Reject a candidate-owned collision with that reserved path. Never copy the staged contract back into the submitted directory.

Proposed proof-of-concept bounds: at most **16 source files**, **16 KiB aggregate source bytes** (retaining today's total submission bound), depth at most **8**, and relative paths at most **240 ASCII bytes**. These are reviewable experiment limits, not new container resource settings. Admit regular `.ts` source files, excluding `.d.ts`; reject dependency/config files, emitted JS/maps and other outputs. No packages or assets are required for this proof.

Reject symlinks at any traversed component, hard links and special files. Traverse using directory-relative no-follow opens, validate opened objects, enforce limits while reading, and reject unsafe or ambiguous relative names rather than repairing them. Paths use `/`, with no absolute, `.`/`..`, backslash or control-character components; reject case-fold collisions. These path rules govern stored filenames, not legitimate internal `../` imports.

### One independent execution path

1. For tree input, create a private bounded snapshot; do not execute the caller's live directory. Record its complete relative-path/content-hash set **in memory**. Recheck membership/content when staging finishes; reject detected concurrent changes. This identifies the tested snapshot, not an atomic capture of a changing external producer.
2. Compose a read-only execution view at `/implementation` containing that snapshot and the trusted contract. Keep trusted checks/tooling read-only. Use a separate writable work directory for reports/caches. Reuse the existing container adapter and effective mount checks; do not change its privileges, networking, environment allowlist or resource limits.
3. Reuse the signature consumer and existing strict no-emit compiler. Include every submitted source in compilation and import-policy checking, not only the reachable entry graph. Resolve supported literal import/export/type/dynamic-import/reference forms to inventoried files or the exact authorized type-only contract. Reject unresolved, nonliteral, package, builtin, absolute and escaping dependencies. Relative imports between internal directories are allowed; no rewriting occurs.
4. Run the same exact declared Vitest suites, runtime validators and behavioral/property tests. Do not collect implementation files as tests or add a layout-specific test runner. Preserve current timeouts, worker policy, classifications and safe default diagnostics.
5. Recheck the snapshot's complete membership and content hashes plus protected consumer inputs; any mismatch fails verification. Clean up the container and temporary snapshot. Report verification success only—no promotion, receipt, quarantine or persisted inventory.

Reuse this execution machinery for file mode where staging changes require it; file input remains a one-file view with unchanged bytes and existing accepted basename semantics. Do not create a second verification engine. Do not change existing file input validation merely to impose new tree filename rules on caller-supplied file paths.

This extends source-set integrity and import checks; it is not a claim of universal JavaScript capability enforcement or hostile-code attestation. Preserve the current sandbox and documented limitations. Standalone verification remains credential-free; it does not claim that manually supplied candidates passed a generation credential scan.

## 5. Evidence to collect after implementation authorization

Prepare fresh fixtures in temporary directories **outside** the existing Box verification roots. Do not edit or replace existing implementation sources or accepted artifacts.

### Positive proof

- Candidate A implements RenderWelcome entirely in its public entry.
- Candidate B delegates through at least two helpers, including a nested directory and an internal relative import across directories.
- Both use the unchanged [contract](../../experiments/render-welcome-native/src/contract.ts), [fixtures and suites](../../experiments/render-welcome-native/native_box.py#L16), with no helper-specific verifier configuration.
- Verify A through the existing file invocation and both A's one-file directory and B through the tree invocation. All must pass the existing three validator tests, six examples and one seeded property.
- Rename/reorganize B's helpers, including a helper with a test-like filename, without changing the public entry, definition or consumer tests. Verification must still pass, and oracle collection must remain unchanged.
- Assert exact source bytes and consumer inputs are unchanged; temporary verifier outputs never become submitted source.

Use independent offline Docker verification explicitly (`BOUNDSCRIPT_RUNTIME=docker`), with no generation auth/model. Manually preparing the fixtures and running these checks requires later implementation authorization; neither is done by this design assignment.

### Necessary negative proof

| Scenario | Required evidence |
| --- | --- |
| Missing entry/export or wrong public type | Preflight/compilation failure; no acceptance-test edits. |
| Correct type but incorrect formatting, mutation or call-history dependence | Existing behavioral/property tests reject it. |
| Helper imports outside the source boundary, an unauthorized package/builtin, or a nonliteral loader | Rejected before candidate execution, including when the offending helper is unused. |
| Missing helper or inconsistent supported compiler/runtime resolution | Deterministic compilation/policy failure, not import rewriting. |
| Symlink/unsafe entry, reserved contract collision, unexpected output or exceeded count/size/depth/path bound | Bounded rejection without following or copying unsafe content. |
| Snapshot file added, removed or altered after staging or during verification | Integrity failure; a previously successful phase cannot hide changed bytes. |
| Attempted source/contract write in the verifier | Read-only enforcement; protected bytes unchanged. Reports/caches remain confined to the work area. |

Use one parameterized infrastructure suite over file, one-file-directory and multi-file-directory inputs. Retain existing file portability, integrity, diagnostics and engine-policy assertions rather than deleting them to accommodate the new staging layout.

## 6. Small implementation sequence proposed for review

1. **Tree input and bounded staging:** add explicit verification-only selection and safe source-set handling, with unit boundary/object/tampering tests. No generator or BoxDefinition changes.
2. **Shared execution and import closure:** adapt trusted source/work mounts and diagnostic paths; check/compile all source files; keep one independent compiler/test path. Existing file regressions and Docker isolation checks must pass.
3. **Hypothesis experiment:** prepare A/B fixtures, run the unchanged external oracle and required negatives, and record results. Run existing credential-free checks to establish single-file compatibility.

**Completion criterion:** differently organized single-file and multi-file implementations satisfy the same unchanged external contract and tests through one independent verifier, without the verifier prescribing internal structure and without weakening security or file compatibility.

**Not a completion criterion:** multi-file generation, publication, quarantine, packaging or future artifact support. Those require separate evidence and assignments.

**Review outcome:** the Product Owner accepted this revised design and authorized step 1 under separate Assignment 0042. Step 2 was subsequently authorized as 0043. Step 3 was subsequently authorized as experiment 0044; design approval does not accept an implementation or experiment delivery.
