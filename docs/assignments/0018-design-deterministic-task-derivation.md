# Assignment 0018 — Design Deterministic Task Derivation (M2)

**Status:** Proposed
**Milestone:** [M2 — Deterministic task derivation](../roadmap.md#m2--deterministic-task-derivation)
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md), especially Sections 3, 5, 6, 8–11.
**Scope:** Design only; pending Product Owner review and approval. This document does not authorize production implementation or start or complete M2.

## Objective and authority

Design the smallest reproducible mechanism that combines approved BoundScript architecture, existing portable Box contracts, and human-owned functional requirements into bounded, independently consumable implementation packages.

M2's exit gate is: **identical approved inputs repeatedly produce equivalent per-Box tasks without manually duplicated public interfaces.** This design proposes the stronger byte-for-byte file-content guarantee under pinned derivation rules. It does not make agent implementations deterministic or establish their correctness.

The Product Owner owns requirements, examples, acceptance criteria, scope, policy, architectural approval, and final acceptance. Derivation assembles approved material; it neither invents missing intent nor grants approval. Approval of this design must be followed by a separately authorized implementation assignment. M3 pilot selection and execution, M4 evidence/promotion, and M6 comparative evaluation remain separate work. The evaluation protocol and conventional baseline must still be defined before M3 implementation.

## Repository findings and reuse

- [Architecture](../architecture.md) and [decisions](../decisions.md#accepted-direction--proposal-0013) separate deterministic extraction from probabilistic construction and keep tasks, workspace configuration, and evidence outside formal contracts and executable artifacts.
- [`extractBoxDevelopmentSpec`](../../packages/compiler/src/box-development-spec.ts) validates the whole source system and exports one Box, including unused Boxes, without host bindings. Source extraction still requires a syntactically valid director; the handoff does not execute or distribute it.
- [Portable specification version 1](../box-development-spec.md) already identifies system, Box, operation, parameter, resolved primitive/flat-record types, and optional supported postcondition. Shared records are fully resolved inline. No second shared-interface registry is needed.
- The strict `@boundscript/compiler/box-spec` decoder and canonical serializer already reject unsupported shapes/versions and produce stable JSON. Keep their ownership, semantics, public exports, and canonical bytes unchanged. `bound spec` remains available unchanged.
- [Assignment 0016](0016-design-standalone-box-verifier.md) records the approved verifier design and clarifications; [0017](0017-implement-standalone-box-verifier.md) is accepted and Completed. `verifyBoxImplementation` checks a trusted, already-loaded function for one fixed input after strict decoding. It is not a loader, acceptance runner, sandbox, or complete implementation brief.
- Existing npm workspaces, TypeScript, Vitest, repository scripts, and Markdown are sufficient. No new package, language syntax, task engine, or runtime dependency on compiler/language is justified.

## Proposed design — not implemented or approved

### 1. Small derivation adapter outside the compiler

Use a repository-level TypeScript script plus a pure derivation helper, not a compiler feature or new service. The script performs I/O, validates approved input references, parses/validates source through existing APIs, extracts selected contracts, and writes results to a fresh output directory. The pure helper assembles deterministic file bytes from validated data and explicit versioned templates. Neither executes candidate code, invokes an LLM, fetches network content, discovers tasks, nor resolves architecture changes.

A single invocation may select one Box or derive all explicitly listed Boxes. Selection is by exact system/Box identity, never inferred from a task filename or director calls. One package represents the Box's one supported operation. Unsupported future multi-operation shapes fail rather than being guessed.

### 2. Approved inputs and minimal binding metadata

Keep functional requirements in ordinary human-owned Markdown, not new DSL syntax or a general task language. Use one strict JSON binding document, provisionally `handoff-input.json`, with only these required fields:

| Field | Exact purpose |
| --- | --- |
| `format`, `version` | `"boundscript/handoff-input"`, `1`; metadata version independent of spec version 1. |
| `approval` | `{ "path": string, "sha256": string }` reference to a human approval record identifying the approved input set/revision. |
| `architecture` | Same file reference, to the approved `.bound` source. |
| `policy` | Same file reference, to human-owned Markdown defining allowed dependencies/tools and trust restrictions. |
| `toolchain` | Nonempty array of file references pinning repository package manifest, lockfile, and applicable TypeScript configuration. |
| `boxes` | Nonempty array of `{ "system": string, "box": string, "task": FileRef, "scope": FileRef, "acceptance": FileRef[] }`; `acceptance` is nonempty. |

`FileRef` means exactly `{ "path": string, "sha256": string }`. Paths are repository-relative POSIX paths; hashes are lowercase SHA-256 hex of exact bytes. Reject missing/extra fields, unknown versions, duplicate identities, conflicting path/hash pairs, absolute paths, traversal, symlinks, missing/nonregular files, invalid UTF-8 text, and hash mismatches. Sort references by code-point path and Box selections by system then Box; input array ordering has no semantic meaning. Require the source-extracted system and Box identities to match each selection. No glob expansion, remote URLs, environment interpolation, executable instructions, priority, scheduling, or agent/provider fields.

This is a narrow association/integrity manifest, not a behavior schema. The `task` Markdown must contain responsibility, functional requirements with stable human-owned IDs, representative input/output examples, and acceptance criteria. `scope` Markdown must state permitted private implementation work and owned paths; `policy` must explicitly list allowed libraries/tools, or say none. Empty files are rejected, but a human reviewer—not an NLP validator—decides completeness and resolves contradictions. Do not repeat public signatures or record definitions in these documents; refer to the contract identity and requirement IDs. Examples are behavioral data, not authoritative type declarations.

`acceptance` references identify trusted test files or a human-owned acceptance-plan document when tests are not yet written. A plan is not evidence that tests exist or behavior passed. Acceptance assets stay on the controller side. Their exact bytes are hashed but are not copied into the agent package. Public representative examples belong in `task`, not in hidden tests.

The approval record must explicitly cover architecture, tasks, scope, policy, toolchain, and acceptance references, either by hashes or by a fixed repository revision and paths. It need not hash itself or the binding document (avoiding circular identities). The trusted controller checks that coverage before derivation. M2 does not implement signatures, credentials, an approval database, or automated interpretation of human approval prose. Hash consistency establishes identity, not human authorization. Missing or ambiguous approval stops the workflow; it is not repaired by generation.

For this first mechanism, derive contracts afresh from the pinned approved source using existing extraction and serialization. Do not accept a separately edited contract as an additional authority. Where a committed portable export is part of the approval, compare its canonical bytes with fresh extraction and fail on disagreement. Supporting standalone contract-only input is deferred: it would require a separately defined architecture provenance/approval boundary.

### 3. Exact per-Box package layout

Output directory: `<output>/<system>/<box>/`, using validated existing identifiers. The package contains exactly these files, with no archives, timestamps, logs, hidden acceptance assets, or machine-specific workspace paths:

```text
<System>/<Box>/
├── handoff.json
├── README.md
├── contract.box-spec.json
├── task.md
├── scope.md
├── policy.md
├── generated/
│   └── contract.d.ts
└── seed/
    └── implementation.ts
```

| File | Contents and authority |
| --- | --- |
| `handoff.json` | Canonical identity, input references, derivation version, output hashes, fixed entrypoint, and package ID as specified below. No copied type/predicate descriptors. |
| `contract.box-spec.json` | Existing canonical version-1 Box spec from extraction; sole packaged public contract. Its inline records provide all relevant shared types. |
| `task.md` | Exact bytes of approved functional requirements, examples, and criteria. Snapshot of the referenced authority, not agent-editable replacement authority. |
| `scope.md`, `policy.md` | Exact approved bytes defining responsibility/private implementation limits and allowed dependencies/tools. Restrictions remain declared unless separately enforced. |
| `generated/contract.d.ts` | Deterministically generated TypeScript projection of the spec, explicitly marked generated/read-only. No manually maintained interfaces. |
| `seed/implementation.ts` | Fixed unimplemented seed importing the generated function type and exporting `implement`; throws `new Error('Not implemented')`. Never a suggested algorithm or working candidate. |
| `README.md` | Versioned fixed instructions: identities, relative links to the above files, entrypoint and writable paths, precedence/conflict handling, submission/check instructions, and trusted-verification/isolation limits. No LLM-authored summary. |

Do not bundle the full architecture, unrelated tasks, other Boxes' implementations, test secrets, approval prose, lockfile contents, credentials, or conversations. Source/approval/toolchain references remain traceable in the manifest; an agent does not need repository-wide access to implement its contract. If the task requires absent context, stop for human clarification rather than broadening context automatically.

### 4. Manifest, identity, and reproducibility rules

`handoff.json` has exactly these required keys in this order:

1. `format: "boundscript/box-handoff"`, `version: 1`.
2. `derivation: { "version": 1, "toolRevision": string }`. `toolRevision` is the immutable repository commit containing the derivation code/templates; refuse dirty derivation inputs. An intentional template/projection-rule change requires a derivation-version decision.
3. `system`, `box`, `operation`: copied identity strings from the decoded extracted contract.
4. `inputs`: `{ "approval": FileRef, "architecture": FileRef, "task": FileRef, "scope": FileRef, "policy": FileRef, "toolchain": FileRef[], "acceptance": FileRef[] }`, with the sorted references defined above.
5. `entrypoint: { "source": "candidate/implementation.ts", "export": "implement" }`.
6. `files`: sorted array of `{ "path": string, "sha256": string }` for every other package file (never `handoff.json`).
7. `id`: package SHA-256 identity as defined below.

Serialize metadata with fixed key order, JSON string escaping, two-space indentation, LF, exactly one final LF, and UTF-8 without BOM. Hash all other files as exact bytes. Compute `id` as SHA-256 of canonical manifest bytes **with the `id` key omitted**, then serialize the full manifest. This avoids self-hashing. Contract bytes use the existing serializer. Markdown snapshots preserve bytes (including line endings); changing those bytes intentionally changes identity. Generated text uses LF and one final LF. No locale-dependent sorting, random IDs, clock, absolute paths, network state, Git branch name, agent identity, or filesystem enumeration order enters the output.

Approved referenced file bytes, selected identity, binding associations, derivation version/revision, and pinned toolchain jointly define the derivation input. The binding file's unrelated Box entries do not enter a selected Box's identity. Use the pinned Node/npm/TypeScript environment recorded by the repository toolchain; document the supported environment in the later implementation assignment. Repeated runs must produce identical relative file sets and bytes, even under different output roots and input array ordering. Directory permissions, mtimes, archives, candidate edits, and logs are outside this guarantee.

Validate every selected input and render every selected package before publishing any result. On failure return nonzero diagnostics with stage and Box/path where applicable; publish no partial handoff. Do not overwrite an existing output or candidate workspace. A temporary staging directory and final directory rename are sufficient; no persistent job state or scheduler is needed.

### 5. Fixed TypeScript entrypoint and implementation boundaries

The controller mounts the package read-only as `handoff/` and creates a separate writable `candidate/` directory. Copy only the seed to `candidate/implementation.ts`. Relative imports in the seed target `../handoff/generated/contract.js` using the repository's TypeScript declaration-resolution convention. The fixed export is:

```typescript
import type { Implementation } from '../handoff/generated/contract.js';

export const implement: Implementation = (input) => {
  throw new Error('Not implemented');
};
```

The projection exports `Input`, `Result`, and `Implementation = (input: Input) => Result | Promise<Result>`. Primitive mappings are direct; result `void` maps to TypeScript `undefined` (not permissive `void`). Flat records use object types with quoted, code-point-sorted property names. Generate record aliases with a fixed prefix such as `Record_<name>`; emit one per record identity in sorted order and reference the same alias on input/output. Fixed `Input`/`Result`/`Implementation` names cannot collide with prefixed aliases. Handle empty records with `Record<string, never>` to avoid TypeScript's broad `{}` type. Do not introduce runtime brands, clone/freeze behavior, or dependency declarations into the spec.

This projection is compile-time assistance only: TypeScript structural types do not prove nominal origin, finite numbers, exact own fields/no extras, or postconditions. The original spec and existing runtime checks remain authoritative. Generated declarations and the manifest must never evolve into a second editable contract model.

Within `candidate/`, agents may add private helpers and tests allowed by `scope` and `policy`. They may not edit the protected handoff, authoritative repository inputs, trusted tests, wiring, dependency manifests/lockfiles, generated declarations, public interfaces, responsibilities, or policy. Default writable scope is only `candidate/**`; no additional repository write paths are granted by this design. Human-approved scope may narrow it. New dependencies or additional public entrypoints require approval, not agent negotiation.

No automatic build/load convention is added to M1. A trusted external controller later compiles the candidate with pinned settings and supplies its already-loaded `implement` function to the existing verifier. M2 supplies source identity and type projection, not a module loader or runtime adapter. M3 must establish isolated execution and approved wiring before running untrusted candidates.

Conflicts between task examples and the contract, missing requirements, or a need for a new dependency halt implementation for Product Owner/Architect review. Neither side silently wins through regeneration. Agents can propose architecture changes separately; they cannot approve or apply them. Separate packages can be consumed sequentially or independently without shared agent context or interface negotiation.

### 6. Invalidation and regeneration

Use explicit hashes and recomputation, not a watcher or dependency graph. A trusted controller compares the current approved input set and tool revision to the manifest and rederives into a fresh directory before use. Comparing internal package hashes alone cannot establish that approvals are still current. Never promote a candidate on its own assertion that a handoff is current.

| Change | Required effect |
| --- | --- |
| Architecture bytes, system/Box identity, operation, type, shared record, or postcondition | Regenerate **all selected handoffs from that source**, even if some extracted contracts are unchanged. Whole-system extraction validates unrelated declarations; conservative invalidation avoids inventing incomplete dependency semantics. Invalid source blocks derivation. |
| One Box's task, examples, scope, or acceptance references | Regenerate that Box's handoff; other Box entries are unaffected unless they share the changed referenced file. |
| Shared policy, approval record, or toolchain file | Regenerate every handoff referencing it. A source-wide approval update may therefore invalidate all its packages. |
| Derivation code/template/version | Regenerate all packages made with the old revision/rules; compare outputs and review intentional changes. |
| Packaged file modified, deleted, or added | Integrity check fails; discard/rederive rather than accepting an edited handoff. |
| Candidate implementation/private tests | Handoff identity stays unchanged; previous verification of the changed candidate is stale. |
| Trusted acceptance tests | Changed acceptance hashes invalidate referencing handoffs and prior acceptance evidence, even though hidden tests are not bundled. |
| Box removed/renamed | Old identity is no longer authorized; no automatic alias/migration or reuse of its candidate evidence. |

Every input change requires approval under the project's policy before regeneration becomes an approved handoff. Hashes detect drift, not whether a change deserves approval. New packages do not update existing candidates in place. Return the new package for revision/reverification, even if a candidate might still work unchanged.

M2 defines the handoff fingerprint and currentness check only. A changed handoff invalidates acceptance evidence referring to its old ID; candidate and test revisions must also be checked independently. Durable evidence storage, integration impact analysis, and promotion enforcement are M4 work, not implemented by this document or by a handoff hash.

## Architectural alternatives and trade-offs

| Alternative | Decision / trade-off |
| --- | --- |
| Handwritten Markdown containing copied TypeScript interfaces | Reject: initially simpler, but duplicates authority and invites drift. Keep human prose; derive the interface projection. |
| Reference-only package | Reject for task/spec contents: smaller but fragile offline and dependent on moving external files. Hash-pinned snapshots are bounded and independently readable. Keep protected tests and whole-source provenance reference-only. |
| Extend `BoxDevelopmentSpec` or `ExecutableArtifact` with tasks and workspace metadata | Reject: conflates contract/runtime boundaries with development context and forces unnecessary format changes. Use a narrow separate JSON metadata envelope. |
| JSON schema for all functional behavior or new task DSL | Reject: arbitrary semantics still need human judgment; Markdown plus explicit associations is sufficient. |
| Compiler generates workspaces or runtime orchestrates agents | Reject: violates ownership boundaries and adds execution state. Use an external deterministic repository adapter. |
| Generic descriptor-to-TypeScript type-level library, or untyped `unknown` entrypoint | Prefer a small deterministic declaration projection for the currently supported types: readable bounded interfaces without new library machinery. Cost: explicit parity/type tests and versioned projection rules. |
| Incremental semantic impact graph | Defer: conservative source-level invalidation is less efficient but safer and much smaller. It can overinvalidate on comments/director changes. Task-local changes remain scoped. |
| Full repository snapshot or container in every package | Reject: unnecessary context/storage and false isolation implications. Package is a directory of text files; M3 supplies actual controlled workspaces. |
| Signed approvals and content-addressed artifact store | Defer: hashes plus human review/repository revisions suffice for identity, not authenticity. No new trust service is warranted for M2. |

## Explicit exclusions and guarantees

- No production implementation in Assignment 0018; no milestone status change or implication of acceptance.
- No grammar changes, new types/predicates, general task language, new DSL, generalized schema framework, or second authoritative interface representation.
- No LLM during derivation, agent runner, provider integration, scheduler, retries, allocation, inter-agent messaging, runtime director changes, or autonomous architectural approval.
- No candidate generation beyond an unimplemented seed, candidate loader/transpiler service, behavioral acceptance runner, integration repair, evidence database, or promotion system.
- No new dependency/capability declarations in BoundScript. Markdown scope/policy is declared and human-reviewed; it is not static compliance analysis or runtime enforcement.
- No sandbox, timeout/resource enforcement, credentials management, or production isolation. Read-only mounts require an external controller; ordinary directories/worktrees and Node subprocesses are not security boundaries. Never execute untrusted candidate code inside the trusted development process.
- Deterministic packages do not imply deterministic agents/candidates, complete behavior specification, universal correctness, or reproducible execution of arbitrary JavaScript. Verifier observations remain limited to supported checks on supplied values; human-owned tests establish only observed functional behavior.

## Acceptance criteria

### Assignment 0018 design delivery

| ID | Criterion |
| --- | --- |
| D-01 | This Proposed document identifies existing foundations, authority boundaries, exact package files/metadata, approved input associations, entrypoint, and implementation scope without changing production code or accepted formats. |
| D-02 | Determinism, fingerprint construction, failure behavior, input approval, invalidation, and independent consumption are specified sufficiently to write a separate implementation assignment. |
| D-03 | Alternatives, trade-offs, exclusions, concrete future tests, and Product Owner decisions are explicit. M2 remains Planned; no implementation, pilot, or acceptance is implied by delivery. |

### Required gate for a later M2 implementation assignment

| ID | Criterion |
| --- | --- |
| AC-01 | Derive one package per approved selected Box using existing whole-system validation/extraction and strict canonical codec; public contract bytes remain unchanged. |
| AC-02 | Repeated derivation under pinned rules produces byte-identical relative file sets/manifests/IDs across output roots and input ordering. No manual public interface duplication. |
| AC-03 | Every package binds exact system/Box/operation, approved requirement/example/scope/policy/test references, generated TypeScript projection, and fixed candidate path/export. |
| AC-04 | Missing, invalid, ambiguous, stale, mismatched, unsupported, or tampered inputs/packages fail closed without partial output, candidate execution, or overwrites. Human approval remains a separate trusted prerequisite. |
| AC-05 | Changes invalidate/regenerate the affected packages according to the table; candidate changes do not change handoffs but invalidate candidate evidence. No silent acceptance reuse. |
| AC-06 | A consumer can type-check a trusted fixture against only its package and the pinned TypeScript toolchain, then use strict decoding and the existing verifier without source/director execution or editing generated interfaces. |
| AC-07 | Independent fixture implementations integrate through prewritten test wiring with no interface edits; this is a trusted design test, not the M3 agent pilot or proof of reduced coordination. |
| AC-08 | Existing check/build/demo/export regressions pass; compiler/runtime dependency direction and formal spec semantics remain unchanged. Documentation states enforcement and semantic limits accurately. |

## Concrete test strategy for later implementation

Use existing Vitest and TypeScript; no new framework. Test only trusted fixtures in-process. Do not launch real agents or untrusted code to test derivation.

| Area | Fixtures and assertions |
| --- | --- |
| Golden package | Extract the published structured Greeter and compare `contract.box-spec.json` byte-for-byte to the existing reference. Snapshot the complete file list, canonical manifest, generated declarations, seed, fixed instructions, and independently recomputed hashes/ID. |
| Reproducibility | Derive twice into different roots; permute JSON keys, Box/reference array order, and portable record field order at the codec boundary; change cwd and enumeration order. Require identical per-Box output bytes. Assert no timestamp, absolute output path, locale order, branch/model identity, or network lookup. |
| Byte identity | Task Markdown containing CRLF, Unicode, quotes, and final-newline variations is preserved exactly. One-byte task change changes only referencing package IDs (subject to shared approval changes). Verify manifest self-hash exclusion and reject altered/additional/missing output files. |
| Source/selection validation | Unknown Box/system, duplicate mappings, invalid unused declarations, removed Box, missing director, incompatible schema, unsupported format/version, and a conflicting committed export fail before publication. Include an unused valid Box to prove derivation is not invocation-driven. |
| Input trust | Wrong hashes, missing/empty task/scope/policy, missing acceptance plan, unpinned approval, incomplete human approval checklist, path traversal, absolute paths, symlinks, conflicting references, invalid UTF-8, unknown keys, and dirty derivation code fail. Human approval coverage is tested as a documented controller review gate, not claimed as automated prose understanding. |
| Type projection | All primitive inputs/results, finite-number limitation, false/zero/empty string, empty/flat records, repeated record names, identifier collisions with alias names, async/sync returns, and `undefined` results. Positive fixture compiles; wrong parameter/output/export and non-undefined void result fail type checks. Reordered fields do not change declarations. Runtime rejection of NaN/extra fields/postcondition failures demonstrates limits of static typing. |
| Independent consumption | Copy only package plus pinned test toolchain into a temporary test workspace; no `.bound`/AST/other Box sources available. Type-check trusted fixture, strictly decode packaged spec, and verify fixed input. Guard against frontend/compiler-root execution in the consumption path, reusing 0017's import-boundary approach. |
| Two-Box wiring | Two small trusted fixture Boxes with compatible existing primitive/record types and separate package contexts. Prewritten test wiring imports their fixed exports and asserts human-owned expected behavior. No implementation/interface repair; malformed output is rejected rather than adapted. This does not select the M3 pilot. |
| Invalidation matrix | With two Boxes, alter task/scope/test reference for one, shared policy, approval, source comments, shared record, predicate, toolchain, and tool revision in turn. Assert exact conservative affected set and new IDs. Reordering bindings and changing only candidate code leave package bytes unchanged. |
| Publication failure | Fail one Box in a multi-Box request; assert no published output. Existing destination/candidate directory remains untouched. Errors identify stage and input/Box without leaking hidden test contents or credentials. |
| Regressions | Run `npm run check`, `npm run build`, existing director-box/composition/structured-types demos, Hello World CLI, and canonical `bound spec` comparison. Reuse existing codec/verifier coverage rather than building a second evaluator. |

For this design-only delivery, verify Markdown references, required sections/status, and `git diff --check`. Production tests are not added or claimed as run for future functionality.

## Decisions requiring Product Owner approval

All choices above are proposed, not recorded as accepted architecture. In particular:

1. Approve the external repository adapter and narrow versioned binding/handoff metadata envelopes, leaving portable specs and compiler/runtime semantics unchanged.
2. Approve hash-pinned Markdown snapshots, reference-only protected acceptance assets, and human-reviewed approval coverage (hashes are not authorization).
3. Approve `candidate/implementation.ts` / named `implement`, generated declaration projection, synchronous-or-asynchronous result, and `undefined` rather than TypeScript `void` for void results.
4. Approve conservative whole-source invalidation and fresh output-only publication rather than semantic incremental dependency analysis or in-place candidate updates.
5. Approve the boundary that M2 defines identity/currentness and declared workspace policy, while M3 supplies real isolation and M4 implements durable evidence/promotion controls.

If review reveals a need for new contract semantics, dependency modeling, automated approval, or broader orchestration, return for an explicit scope/architecture decision rather than expanding this mechanism.

## Delivery and authorization boundary

Deliver only this design document. Commit and push to the current feature branch are explicitly authorized for this document preparation. Report the commit SHA, documentation checks, deviations, and pending architectural decisions. Do not alter existing assignments/reviews, record Product Owner acceptance, or mark M2 In Progress or Completed. Assignment 0018 remains Proposed pending Product Owner review; a later implementation assignment requires separate authorization.
