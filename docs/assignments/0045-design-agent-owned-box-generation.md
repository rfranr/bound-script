# 0045 — Design Agent-Owned Box Generation

**Status:** Completed — design explicitly accepted by the Product Owner

**Type:** Design only

## 1. Goal and smallest increment

Allow an agent to choose any **supported** internal TypeScript organization while retaining the existing public contract, `implementation.ts` entry and named export. One file is as valid as several; success must not depend on producing helpers, a particular directory structure or a demonstrated use of classes.

**Recommend one opt-in, verification-only generation mode.** Generate an empty implementation workspace, scan its complete output, destroy the credential-bearing container, and pass the resulting bounded source snapshot to the existing independent tree verifier. Treat one-file and multi-file results identically.

Keep existing generation commands and their single-file promotion/quarantine behavior unchanged. Do not introduce tree publication, retention, quarantine, artifact specifications, configuration fields, registries or another verification engine. This is a proposal; no implementation, candidates, model-backed generation, commits or pushes are authorized or performed here.

## 2. Current foundations and gaps

Inspected after `99dc3ce`; the 0043 verifier remains unchanged by 0044.

| Existing source | Relevant behavior |
| --- | --- |
| [`native_generator.py:23–33`](../../boundscript_internal/native_generator.py#L23) | Prompt explicitly asks for one file and prohibits other submission files. That restriction must remain for legacy mode, but not the new mode. |
| [`agent_workspace.py:19–57`](../../boundscript_internal/agent_workspace.py#L19) | Shared lifecycle already provides an empty writable implementation root, read-only task/contract, fixed Pi/auth mounts and effective isolation checks. Reuse it, not a second workspace runner. |
| [`agent_workspace.py:96–141`](../../boundscript_internal/agent_workspace.py#L96) | Read-event allowlist, direct-child validation and literal credential scan assume one filename. The helper hashes protected inputs/auth, removes the generation container, then yields one path and scanned digest. Extend these checks to the full source set. |
| [`source_tree.py:10–142`](../../boundscript_internal/source_tree.py#L10) | Existing bounded no-follow staging yields a private snapshot and sorted `(relative_path, size, sha256)` inventory. It rejects candidate-owned `contract.ts`, whereas generation's workspace contains that trusted input. A narrowly controlled generation-only exclusion is needed. |
| [`native_verifier.py:295–437`](../../boundscript_internal/native_verifier.py#L295) | The existing tree path already stages sources, checks disjoint oracle/source roots and runs all-source strict compilation/import closure, source/input integrity and unchanged suites in one independent engine. Reuse this path without changing the verifier. |
| [`native_generator.py:56–89`](../../boundscript_internal/native_generator.py#L56) | Fingerprinted subprocess verification, quarantine and promotion consume one file. New-mode tree results must not fall through into those file operations. |

[0044](0044-render-welcome-ab-verification-experiment.md) supplies evidence that different manual organizations can satisfy the same unchanged oracle. It does not establish multi-file generation or credential scanning.

## 3. Explicit mode, neutral instructions, unchanged compatibility

Illustrative future invocation, **not implemented or authorized to run**:

```sh
python3 -B experiments/native_cli.py generate render-welcome --agent-owned
```

The flag selects an authorized workflow, **not an architecture**. Do not call it `--multi-file`, select it according to observed file count, or switch default npm generation commands implicitly. In this first increment it always means **generate, independently verify, then discard temporary sources; no promotion or quarantine**, including when the agent chooses one file. Report that disposition clearly.

For the new mode, the prompt supplies only:

- The declared task and consumer contract paths, public entry, function type and export.
- The writable source boundary and existing supported TypeScript/import/output limits.
- Existing input, credential, package-installation and filesystem restrictions.

Remove the single-file prohibition in this mode. Do not suggest splitting, helpers, layers, classes, filenames, file counts below the safety cap, example implementations or reference architectures. Do not expose 0044 candidates, accepted implementations, fixtures, tests, repository context or peer code. Do not seed a source template. Retain the current fresh-session/tool restrictions and model/reasoning selection.

Use the existing profile: at most 16 source files and 16 KiB total, depth 8, 240-byte ASCII relative paths and the current traversal budget; regular UTF-8 `.ts` sources, no `.d.ts`, dependency/config/emitted files, unsafe objects or path collisions. These are safety boundaries, not organizational advice. `implementation.ts` and the protected root `contract.ts` relationship are public-boundary conventions, not a prescribed internal architecture.

Legacy mode remains file-only, with its current prompt/API defaults, accepted filenames, quarantine, model settings and npm workflows. Baseline callers using other filenames remain supported. No BoxDefinition, consumer task, contract, fixture or acceptance-test changes are proposed.

## 4. Complete-source scan → cleanup → snapshot → verification

### A. Reuse the workspace, extend its own-source authorization

Add an opt-in tree-output parameter to `agent_submission`, defaulting to its existing file behavior. Authorize read events for exact task/contract inputs and the implementation's own namespace, including nested files/directories. Resolve relative event paths against the known sandbox working directory; use component-aware containment, not string-prefix matching. An own-source path is not permission to read a parent, peer, tests, repository or credential path.

Event checking remains an audit, not complete mediation of bash/edit or historical symlink targets. Keep actual mounts and probes as the security boundary. No extra inputs/mount authority, dependencies, packages or runtime permissions are added.

### B. Scan every output before host-side candidate inspection/copying

Extend the existing trusted **in-container** scanner to enumerate all implementation-owned files, not only the entry or reachable import graph. Apply the same bounded path/object/encoding rules as staging using no-follow descriptor-based reads. Scan **every relative filename and every file's exact bytes**, including unused helpers, against the existing original and refreshed literal credential values. Preserve the current literal-value threshold/policy; never send credential values to host arguments, reports or new host files.

The scanner excludes only the exact workflow-created root contract input after validating its protected identity/content. It must not ignore an arbitrary same-named candidate entry, a replacement/link, case-collision or other output. Check the task, contract, sentinel and original auth as today. Return no inventory, names, source, provider events or secret-bearing errors before the entire scan succeeds; a bounded digest/status is sufficient.

Reuse the trusted Python staging policy constants as scanner inputs rather than separately configured limits. Node and Python necessarily perform reads in different processes, but their acceptance rules and digest encoding need shared test vectors, not a new policy DSL or agent-supplied manifest.

### C. Bind the scanned bytes and complete membership

Reuse the existing sorted inventory records. For this scan handoff only, define a small deterministic digest:

```text
records = sorted arrays [relative_path, byte_length, lowercase_sha256]
D = SHA256(ASCII compact JSON of records, with no whitespace or trailing newline)
```

Allowed paths/hashes are ASCII and sizes are bounded integers. Require matching Node/Python serialization and byte-preservation test vectors, including empty files, BOM and CRLF. Paths and every permitted file participate; the consumer contract is protected separately. No inventory file, artifact type, persisted receipt or publication identity is introduced.

After successful scanning, remove the generation container and all its writers. A settled agent event alone is not proof that background writers stopped. On cleanup failure, do not yield or verify anything.

Then use `staged_source_tree` to collect a pure source snapshot, with a generation-only option to validate and omit the known protected contract. Ordinary standalone staging must still reject candidate-owned contract files by default. Recompute `D` from the host snapshot; any missing/extra/renamed/changed file, unsafe object, contract change or scan mismatch stops the run. This catches changes during scanning/cleanup without claiming atomic capture of a live producer.

The workspace can retain its existing `(path, scanned_digest)` return shape: file path/file digest in legacy mode, pure snapshot root/tree digest in the explicitly selected new mode. The caller already knows the mode; no new result classes or artifact abstraction are necessary.

### D. Reuse the unchanged independent verifier

Invoke the existing verification subprocess with the unchanged Box-definition fingerprint and `--source-tree` pointing to the **new private snapshot**, never the generation workspace. Recompute `D` immediately before invocation. All credential-bearing generation processes are already destroyed, the snapshot is outside the oracle root, and the verifier exposes only its own read-only source view to candidate execution—not a writable bind of the parent's snapshot. No untrusted writer may retain access to the snapshot.

That ownership/lifetime invariant, together with the matched scan digest and existing verifier staging/view-integrity checks, supplies the handoff under the current trusted-host model. Before/after hashes alone would not protect a live mutable producer that changed and changed back; do not substitute such a producer or claim malicious-host protection. If private ownership cannot be maintained, stop for review rather than weakening it. No new verifier flag, receipt or verification engine is needed for this increment.

After the shared verifier succeeds and cleans up, re-inventory the parent's full snapshot and compare `D` again; retain the original contract/task integrity protections across the handoff. A changed tree cannot be described as the verified result. Sources always enter the existing verifier as a tree, even when there is just one implementation file; do not extract/verify only the entry or flatten helper imports.

### E. End this increment without extending publication

Success reports a verified, non-promoted temporary tree and observed file count—not a requirement that the count exceed one. Dispose of temporary sources on context exit. Failure also cleans up, emits bounded safe diagnostics and never enters the legacy file quarantine/promotion branch. Never save unscanned source, logs or a partial tree for diagnosis.

## 5. Minimal implementation surface proposed

| Existing file | Narrow future change |
| --- | --- |
| `agent_workspace.py` | Opt-in tree output; own-source read audit; recursive in-container scan and post-cleanup scan/snapshot binding. Reuse lifecycle/auth/probes/cleanup. |
| `source_tree.py` | Reuse inventory/limits; small shared inventory-digest function and controlled validation/exclusion of the known generation contract. Keep standalone defaults. |
| `native_generator.py` | Neutral new-mode prompt and a verification-only branch in the shared orchestration. Never run its legacy file quarantine/copy path for new-mode output. |
| `experiments/native_cli.py` | Forward the one explicit mode flag; keep Box selection fixed and separate. |

No verifier/verification-CLI, compiler, acceptance suite, runtime-policy, dependency, BoxDefinition or artifact-format changes. Prefer plain functions and existing modules; no new runner classes, factories, registries or per-Box scripts.

## 6. Small implementation sequence and evidence gates

1. **Scan and stage binding, credential-free first.** Extend shared staging/workspace helpers behind the opt-in default. Test the actual trusted scanner with synthetic original/refreshed credentials and inert one-file/nested-tree fixtures, without Pi/provider calls. Exercise credentials in entry, helper, unused file and filename; contract substitution; symlink/hard-link/special objects; bounds; source-set changes during scan/cleanup; deterministic digest parity; safe diagnostics and cleanup failure. Extend current shared tests, not a new per-Box workflow suite.
2. **Neutral orchestration and independent verification.** Add explicit mode/prompt dispatch. Simulate agent completion for both organizations; run the same independent Docker verifier on synthetic fixtures. Assert destruction of all generation writers before the private snapshot is yielded, matched scan/snapshot inventory, no writable snapshot exposure to candidate execution, full post-verification re-inventory, unchanged consumer assets, no architecture-specific prompt hints, and no new-mode promotion/quarantine—even for one file. Run existing single-file generation regressions (mocked), verification/portability tests, credential-free checks and 0044 compatibility evidence.

A live agent experiment requires **separate explicit authorization** after those checks. Start empty with only declared task/contract and the neutral prompt; observe the architecture rather than requiring several files or retrying until they appear. One file is a valid outcome. No model calls or candidate preparation occur under this design assignment.

## 7. Review decisions and limits

- **Approve the opt-in, verification-only disposition.** Existing `accepted_path` values are files; preserving them cannot safely publish an arbitrary tree. Retaining/publishing generated trees is a separate increment, not an implicit fallback that drops helpers or changes behavior according to file count. Successful new-mode sources are intentionally temporary in this proposal.
- **Approve the private snapshot boundary and controlled contract exclusion.** Destroy generation writers before creating/yielding the pure snapshot, require its full digest to match the scan, and keep it inaccessible for candidate writes. The trusted contract exception must not weaken ordinary standalone staging. No generalized artifact machinery is needed.
- Keep generation's existing bridge/auth prototype exception, pinned tools, nonroot/resource/mount policies, timeouts, disabled retries and independent offline credential-free verifier. Use Docker explicitly for later engine evidence in this environment. No isolation workaround or model call is introduced into build/check commands.
- Literal scanning still does not prevent encoded/split leaks or network exfiltration; read-event audits and static import checks are not universal hostile-code enforcement. Preserve safe normal diagnostics without presenting existing raw DEBUG behavior as safe. Host/kernel compromise and atomic snapshots of a hostile live producer are not promised.
- Do not rewrite task text or resolve business ambiguities to enable the mode. In particular, the already reported Welcome contract-path wording drift remains a separate review item; actual contract location is supplied by the existing definition/prompt.

**Proposed completion gate:** an agent-owned output containing either one file or nested supported sources can pass complete credential scanning, post-cleanup identity binding and the same independent verifier, without architecture coaching or changes to consumer criteria. Legacy file workflows remain unchanged. No tree publication capability is claimed.

**Review outcome:** the Product Owner approved the design and verification-only scope, authorizing step 1 separately as 0046. Orchestration/step 2 and live generation remain unauthorized. Design acceptance does not accept the implementation delivery.
