# Assignment 0018 — Design Deterministic Task Derivation (M2)

**Status:** Completed
**Milestone:** [M2 — Deterministic task derivation](../roadmap.md#m2--deterministic-task-derivation)
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md), especially Sections 3, 5, 6, 8–11.
**Scope:** Design only, including a disposable technical spike; approved and accepted by the Product Owner. Production implementation requires separate authorization under Assignment 0019. Design acceptance does not complete M2.

## Objective and authority

Design the smallest reproducible mechanism combining approved BoundScript architecture, existing portable Box contracts, and human-owned functional requirements into bounded, independently consumable implementation packages.

M2's exit gate is: **identical approved inputs repeatedly produce equivalent per-Box tasks without manually duplicated public interfaces.** The proposed mechanism guarantees identical relative file sets and bytes for identical explicit inputs under the same supported derivation rules. It does not make agent implementations deterministic or establish correctness.

The Product Owner owns intent, examples, acceptance criteria, scope, policy, architectural approval, and final acceptance. Derivation assembles supplied material; it neither invents missing intent nor establishes that the inputs were approved. Approval of this design must be followed by a separately authorized implementation assignment. M3 pilot selection/execution and isolation, M4 evidence/promotion, and M6 comparative evaluation remain separate work. The evaluation protocol and conventional baseline must still be defined before M3 implementation.

## Repository findings and reuse

- [Architecture](../architecture.md) and [decisions](../decisions.md#accepted-direction--proposal-0013) separate deterministic extraction from probabilistic construction and keep tasks, workspace configuration, and evidence outside formal contracts and executable artifacts.
- [`extractBoxDevelopmentSpec`](../../packages/compiler/src/box-development-spec.ts) validates the whole source system and exports one Box, including unused Boxes, without host bindings. Source extraction still requires a valid director; the handoff does not execute or distribute it.
- [Portable specification version 1](../box-development-spec.md) already identifies system, Box, operation, parameter, resolved primitive/flat-record types, and optional supported postcondition. Shared records are fully resolved inline; no additional shared-interface registry is needed.
- The strict `@boundscript/compiler/box-spec` decoder and canonical serializer already reject unsupported shapes/versions and produce stable JSON. Keep ownership, semantics, public exports, and canonical bytes unchanged. `bound spec` remains unchanged.
- [Assignment 0016](0016-design-standalone-box-verifier.md) records the approved verifier design; [0017](0017-implement-standalone-box-verifier.md) is accepted and Completed. `verifyBoxImplementation` checks a trusted, already-loaded function for one fixed input after strict decoding. It is not a loader, acceptance runner, sandbox, or implementation brief.
- Existing repository scripts, TypeScript, Vitest, npm lockfile, and Markdown suffice. No new package, runtime dependency direction, language syntax, or task engine is justified.

## Revision rationale: minimum M2 versus M4

The initial proposal coupled derivation to hash-pinned references, approval coverage, toolchain manifests, output hashes, and a self-excluding package digest. These can support later evidence, but are not necessary to derive reproducible tasks. This revision removes them from M2.

| M2 needs now | Deferred or external responsibility |
| --- | --- |
| Explicit source/Box/task associations and human-supplied scope/policy | Human approval before invocation; no automated authorization claim. |
| Existing canonical contract plus verbatim Markdown snapshots | M4 candidate/contract/task/test identities, integrity manifests, durable provenance, and acceptance-evidence linkage. |
| Fixed generated declarations, seed, instructions, and derivation rules version | M4 package digest/content-addressed storage if evidence requires it; no M2 package ID or file hashes. |
| Same supported implementation/environment for repeatability tests | Reuse repository lockfile/configuration; no per-package toolchain pinning or toolchain reference schema. Record actual tool versions in ordinary test reports. |
| Fresh derivation and byte comparison of directories | M4 stale-evidence enforcement, promotion controls, and any authenticated approval mechanism. |

A Git revision plus ordinary human review can select inputs operationally; it is not an additional package schema or proof of approval. M2 does not reject dirty trees as an authorization proxy. Cross-version/compiler/platform reproducibility beyond the supported, tested environment is not promised. Changed derivation behavior requires updating the explicit rules version and tests.

## Approved design — not implemented

### 1. External repository adapter

Use a repository-level TypeScript script with a pure rendering helper, outside compiler/runtime. The script reads explicit inputs, uses existing whole-system parsing/validation and extraction, and writes packages into a fresh output directory. It executes no candidate code, invokes no LLM, fetches no network content, and discovers no tasks automatically.

Select one Box or all explicitly listed Boxes. Select by exact system/Box identity, never filenames or director invocations. A package represents the Box's one supported operation. Unsupported future operation/type shapes fail rather than being guessed.

### 2. Input bindings and exact approval boundary

Use a small JSON association document, provisionally `handoff-input.json`, with exactly these required fields:

| Field | Shape and purpose |
| --- | --- |
| `format`, `version` | `"boundscript/handoff-input"`, `1`; metadata version independent of spec version 1. |
| `architecture` | Repository-relative POSIX path to the supplied `.bound` source. |
| `policy` | Repository-relative path to human-owned Markdown describing allowed dependencies/tools and trust restrictions. |
| `boxes` | Nonempty array of `{ "system": string, "box": string, "task": string, "scope": string }`; task/scope strings are repository-relative Markdown paths. |

Paths are resolved against an explicit repository root, not the output directory. Reject missing/unknown keys, unknown versions, duplicate system/Box selections, absolute paths, traversal, symlinks, nonregular/missing files, invalid UTF-8, and empty Markdown. Validate identifiers and source identity through existing extraction/codec semantics. Sort Box selections by system then Box in code-point order; input array/key order is irrelevant. No globs, URLs, environment interpolation, priorities, executable instructions, agents, or scheduler fields.

`task` contains responsibility, human-owned requirement IDs, representative input/output examples, and acceptance criteria. `scope` defines private implementation freedom and writable boundaries. `policy` lists permitted libraries/tools, or explicitly says none. Refer to the contract identity and requirement IDs rather than restating public signatures or record declarations. Examples are behavioral data, not authoritative type definitions. Keep trusted acceptance tests outside packages; M2 does not inventory or hash them. Public examples belong in the task.

**Mechanically verifiable in M2:** binding shape, path/file validity, nonempty text, successful whole-system validation, existence of selected Boxes, identity agreement, supported contract shape, deterministic rendering, and equality of fresh outputs. These are structural/input checks, not approval checks. If a committed portable export is supplied for comparison by a repository check, canonical equality with fresh extraction is mechanically checkable; it still establishes no approval.

**Human prerequisite, not mechanically verified:** the Product Owner or authorized human confirms the exact source and selected task/scope/policy versions are approved, complete, mutually consistent, and applicable to the selected Boxes. The human checks examples against intent, reviews permitted dependencies/tools, and keeps authoritative inputs/tests outside candidate control. Missing or ambiguous approval must stop the human-controlled workflow before invocation. The adapter has no approval field, approval-record parser, authenticated identity, or approval-policy engine; it can technically render unapproved inputs, whose output must not be described as approved. A successful exit status means derivation succeeded, never that approval was verified.

Human review also checks that requirements do not duplicate/redefine interfaces. Nonempty Markdown cannot mechanically establish semantic completeness or consistency. Missing intent or a task/contract conflict returns to the Product Owner/Architect; the adapter does not infer or repair it.

Derive contracts afresh from the supplied source via existing extraction and serialization. Do not accept a separately edited portable contract as a second authority. Standalone contract-only input is deferred until its architecture provenance/approval boundary is defined.

### 3. Exact per-Box package

Output: `<output>/<system>/<box>/`, using existing validated identifiers. Exactly these files:

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
| `handoff.json` | Small informational association/entrypoint metadata defined below, not an integrity or approval manifest. No type/predicate descriptors. |
| `contract.box-spec.json` | Existing canonical version-1 extracted Box spec; sole packaged public contract, including all relevant inline shared record definitions. |
| `task.md`, `scope.md`, `policy.md` | Exact input bytes, including line endings. Protected snapshots of human-owned material, not new agent-editable authorities. |
| `generated/contract.d.ts` | Deterministic read-only TypeScript projection of the spec; never a manually maintained interface. |
| `seed/implementation.ts` | Fixed unimplemented seed exporting `implement`; throws `new Error('Not implemented')`. No generated algorithm. |
| `README.md` | Fixed versioned instructions: identities, relative links, candidate path/export, writable boundaries, conflict escalation, submission/check instructions, and limits. No model-generated summary. |

`handoff.json` contains exactly these keys in this order:

1. `format: "boundscript/box-handoff"`, `version: 1`, `derivationVersion: 1`.
2. `system`, `box`, `operation`: identity strings from the extracted contract.
3. `inputs: { "architecture": string, "task": string, "scope": string, "policy": string }`: the selected repository-relative paths from the binding document.
4. `entrypoint: { "source": "candidate/implementation.ts", "export": "implement" }`.

There are **no approval references, hashes, tool revision, toolchain references, acceptance-test references, output file inventory, or package ID**. Input paths aid navigation but do not pin file versions; the snapshots give the agent its bounded context. A path's current contents must not be assumed equal to an old snapshot. M4 can later define evidence identity separately without changing the formal Box spec.

Do not bundle whole architecture, unrelated tasks, other Boxes' implementations, hidden tests, credentials, conversations, or dependency trees. Agents need only their package and an externally prepared permitted tool environment. Missing task context requires human clarification, not automatic context expansion.

### 4. Deterministic output guarantee

Define derivation as a function of the selected identity, architecture bytes, selected task/scope/policy bytes and repository-relative paths, and versioned derivation rules/templates. Hold the supported implementation/tool environment fixed. The same explicit inputs produce identical relative file sets and bytes across runs and output roots. Unrelated Box bindings and input JSON key/array ordering do not affect a selected package. Changing an input path may change metadata even if its contents are equal.

Use the existing contract serializer. Serialize handoff metadata using the fixed key order above, JSON string escaping, two-space indentation, LF, one final LF, and UTF-8 without BOM. Generated text uses LF and one final LF; Markdown snapshots preserve exact input bytes. Use code-point sorting, not locale sorting. Exclude clocks, random values, absolute root/output paths, environment interpolation, branch/model identity, and filesystem enumeration order.

Validate all selected inputs and render all selected packages before publishing results. Return nonzero diagnostics with stage and Box/path on structural failure; publish no partial output. Do not overwrite existing outputs or candidate workspaces. A temporary staging directory and final rename suffice; no persistent job state is needed.

Directory permissions, mtimes, archives, candidate code, approval decisions, and verification outcomes are outside the deterministic-output guarantee. Equal outputs do not prove equal approvals, input provenance, candidate behavior, or acceptance evidence. Compare fresh directories directly in M2 tests; hashes are not required to demonstrate equality.

### 5. Fixed TypeScript entrypoint and boundaries

An external controller supplies the package read-only as `handoff/` beside writable `candidate/`. Copy only the seed to `candidate/implementation.ts`:

```typescript
import type { Implementation } from '../handoff/generated/contract.js';

export const implement: Implementation = (input) => {
  throw new Error('Not implemented');
};
```

Use ESM (`package.json` with `"type": "module"`) and the repository's NodeNext TypeScript configuration. The type-only `.js` import resolves to `contract.d.ts` during compilation and disappears from emitted JavaScript; no runtime `contract.js` is needed. The externally prepared tool environment supplies package/config files, not agent-editable copies in the protected handoff. A trusted consumer importing named `implement` checks the export convention; type annotation alone cannot check the export name.

Generate `Input`, `Result`, and `Implementation = (input: Input) => Result | Promise<Result>`. Map primitives directly and result `void` to TypeScript `undefined`, not permissive `void`. Under the tested compiler, implementations of such operations must explicitly return `undefined` (or an awaited equivalent); the empty implicit-return body is rejected. This is a stricter authoring convention than the runtime's acceptance of implicit `undefined`, not a change to contract/runtime semantics.

Generate one alias `Record_<name>` per record identity, sorted by name, with quoted code-point-sorted primitive fields; reuse the alias on input/output. The prefix avoids collisions with fixed projection names. For empty records, use `Record<string, never>` rather than broad `{}`. The spike below validates common cases but also demonstrates a symbol-key limitation. This remains a best-effort structural projection, not proof of exact own keys, nominal origin, finite numbers, or postconditions. No brands, cloning, freezing, or new runtime restrictions. The original spec and runtime checks remain authoritative.

Agents may add permitted private helpers/tests only within `candidate/**`; scope may narrow that boundary. They may not edit handoffs, source contracts, shared types, requirements, trusted tests, wiring, dependency manifests/lockfiles, or protected policies. New dependencies, responsibilities, or public entrypoints require human approval, not agent negotiation. A better decomposition is a separate architectural proposal.

M2 adds no candidate loader or compilation service to M1. An external trusted controller later compiles candidates using the prepared environment and supplies an already-loaded function to the verifier. M3 must provide actual isolation before executing untrusted code; directories/worktrees and Node subprocesses are not security boundaries. Declared restrictions/read-only instructions are not enforcement.

### 6. Conservative invalidation policy — separate from determinism

Determinism says **same inputs yield same output**; it does not require different inputs to yield different outputs. Invalidation is a workflow decision to stop using an old handoff pending fresh derivation/review. M2 has no watcher, fingerprint database, automated currentness service, or promotion gate. A human-controlled script invocation regenerates into a fresh directory from the currently selected, human-approved inputs.

| Change | First-implementation policy |
| --- | --- |
| Any architecture/source bytes, including comments/director or unused declarations | Treat every existing handoff from that source as needing regeneration. Revalidate the whole system, then regenerate all still-selected Boxes. Invalid source blocks derivation. |
| One Box's task or scope | Regenerate that Box and any other Box sharing the changed file. |
| Shared policy | Regenerate all packages referencing it. |
| Derivation code/templates/rules or supported tool environment | Rerun full derivation and comparison/regression checks; update rules version for intentional behavior changes. Output need not differ for a tool-only change. |
| Packaged file edited/deleted/added | Discard/rederive into a fresh directory. Direct comparison with fresh output detects differences; no authenticated integrity claim. |
| Box removed/renamed | Retire old selection; do not alias or migrate candidates silently. |
| Candidate code/private tests or trusted acceptance tests only | No handoff regeneration unless packaged task/scope/policy also changes. Prior affected verification must be rerun; tracking/enforcing stale evidence belongs to M4. |
| Approval decision only, with unchanged supplied files | Human authorization to use the package may change while output remains byte-identical; the adapter cannot detect or enforce this. |

Source-wide invalidation is deliberately conservative because extraction validates the whole system, shared records can affect multiple Boxes, and current contracts do not describe every dependency/responsibility relationship. It avoids building a semantic impact graph prematurely. **Limitations:** comments/director/unrelated valid declaration edits can trigger unnecessary regeneration; unchanged Boxes may regenerate byte-identically. It is not proof of integration impact, cannot detect unrecorded human requirement changes, and does not determine which candidates/tests need reverification. Humans must identify affected source inputs under the repository workflow. A future M4/M5 impact/evidence mechanism may refine this policy with explicit approval.

Never patch candidates in place to fit regenerated interfaces or claim unchanged package bytes preserve acceptance evidence. Human review determines reuse/revision and required reverification; M2 does not automate that decision.

## Disposable TypeScript feasibility spike — performed for review

Executed outside the repository in a temporary directory, using Node **v24.16.0** and repository TypeScript **5.9.3**. Each case had its own ESM package, `handoff/generated/contract.d.ts`, `candidate/implementation.ts`, and trusted consumer importing `implement`. Invoked the repository compiler by absolute path with NodeNext/ES2022, strict, exact optional properties, unchecked-index checking, isolated modules, verbatim module syntax, `types: []`, and `skipLibCheck: false`. No repository source imports, config inheritance, node-module dependencies, agent execution, or production changes were involved.

| Cases | Observed result |
| --- | --- |
| Flat-record sync and async functions; throwing seed | Compile successfully. |
| Sync/async explicit `undefined` result | Compile successfully. |
| Implicit empty-body return for `undefined`; wrong result; wrong parameter | Rejected with TS2322. |
| Empty record `{}` with `Record<string, never>` | Compiles successfully. |
| Empty-record result containing string-keyed extra field, number, array, null, or callable | All rejected with TS2322. |
| Empty-record result containing symbol-keyed extra property | **Compiles:** demonstrates the projection's limit, not a supported runtime value. Existing own-key runtime checks remain required. |
| Candidate exports `other`, consumer imports `implement` | Rejected with TS2305; export convention needs a consumer check. |

**Result: 16 independent compilation cases, zero unexpected outcomes.** Every successful case also passed a built ESM import check confirming a callable named `implement` without a runtime declaration-module import. The checks imported trusted functions but did not invoke the seed. Temporary spike files/output were removed and are not committed. This validates feasibility of the convention, not a generator implementation, verifier regression run, or universal static representation of empty-record semantics.

## Architectural alternatives and trade-offs

| Alternative | Proposed decision / trade-off |
| --- | --- |
| Handwritten task interfaces | Reject: duplicated authority and drift. Keep human prose; derive declarations from portable contracts. |
| Reference-only package | Reject for task/spec contents: moving paths break independent/offline consumption. Verbatim snapshots are sufficient without hash manifests. |
| Hash-pinned approval/toolchain/input/output manifests and package digest | Defer to M4 if needed for evidence. More identity metadata does not make rendering more deterministic or establish human authorization. M2 loses automated integrity/currentness checks deliberately. |
| Extend formal Box spec or executable artifact with task metadata | Reject: conflates boundaries. Use a narrow association document and informational handoff metadata. |
| Task DSL or JSON behavioral schema | Reject: arbitrary intent still requires human judgment. Markdown and explicit associations suffice. |
| Compiler/runtime drives agents | Reject: keep external deterministic adapter; no execution state or orchestration. |
| Generic type-level descriptor library or `unknown` entrypoint | Prefer a small declaration projection for current supported types: readable bounded interface, with explicit static/runtime limitations and parity tests. |
| Semantic incremental invalidation | Defer: source-wide policy is smaller/safer but overinvalidates and can regenerate identical outputs. |
| Bundled repository/container | Reject: excessive context and false isolation implications. M3 supplies controlled environment independently. |

## Explicit exclusions

No production implementation, milestone status change, grammar/type/predicate expansion, general task language, new DSL, second authoritative interface model, LLM invocation, scheduler, agent framework/provider integration, automatic architectural approval, candidate loader/transpiler service, acceptance runner, integration repair, or promotion system. No integrity manifests, package digest, authenticated approval, evidence database, or stale-evidence enforcement in M2. No sandbox/time/resource enforcement, credentials management, or production isolation.

Functional correctness, dependency compliance, security, and universal semantic equivalence are not established by declared policy, TypeScript, or deterministic packages. Existing verifier results remain per-invocation observations; external human-owned tests establish only observed behavior. Never execute untrusted candidates inside the trusted development process.

## Acceptance criteria

### Assignment 0018 design delivery

- **D-01:** Proposed, design-only document specifies existing reuse, exact inputs/package/entrypoint, minimality, authority boundaries, alternatives, exclusions, and future tests without changing production code or roadmap status.
- **D-02:** Mechanical validation is explicitly separated from human approval. Output determinism is separated from conservative invalidation and M4 evidence/promotion.
- **D-03:** Disposable independent TypeScript/empty-record spike results and limitations are reported; no spike artifacts or production implementation are committed.

### Gate for a later M2 implementation assignment

| ID | Criterion |
| --- | --- |
| AC-01 | Derive each selected Box using existing whole-system validation/extraction and canonical codec; portable contract bytes remain unchanged. |
| AC-02 | Same explicit inputs/rules produce byte-identical file sets/content across roots and input ordering, without copied manual interfaces or hash infrastructure. |
| AC-03 | Bind exact system/Box/operation, human-owned task/scope/policy snapshots and input paths, projection, and fixed candidate path/export. |
| AC-04 | Invalid structural inputs fail without partial output, execution, or overwrites. Documentation never labels these checks automated approval verification. |
| AC-05 | Regeneration tests establish the conservative affected set and allow byte-identical regeneration. No automatic evidence acceptance/currentness claim. |
| AC-06 | Trusted fixture independently compiles using only package plus prepared TypeScript environment, then strictly decodes and uses the existing verifier without source/director execution or interface edits. |
| AC-07 | Independent trusted fixture Boxes integrate via prewritten wiring without repairs; this is not the M3 agent pilot or proof of reduced coordination. |
| AC-08 | Existing checks/build/demos/canonical export pass; dependency direction and formal spec semantics remain unchanged. |

## Concrete test strategy for later implementation

Use existing Vitest/TypeScript and trusted fixtures only; no agents or untrusted execution.

| Area | Cases and assertions |
| --- | --- |
| Golden package | Published structured Greeter: canonical contract matches existing JSON byte-for-byte. Compare exact package file list, metadata, declarations, seed, and instructions. |
| Reproducibility | Two output roots; permuted binding keys/Box order; changed cwd/enumeration order. Compare file bytes directly. Codec tests cover field-order canonicalization. No timestamps, absolute paths, model/branch identity, or network access. |
| Snapshot bytes | Preserve CRLF, Unicode, quotes, and final-newline variations. Task-only edit changes only packages referencing it. Source comment edit triggers all-source regeneration but may leave all bytes identical. |
| Structural failures | Unknown/duplicate Box/system, invalid unused declarations, missing director, unsupported versions/shapes, missing/empty text, unknown keys, traversal, absolute paths, symlinks, invalid UTF-8. Nonempty but unapproved Markdown can render: document this as an intentional limit, not success at authorization. |
| Type projection | Recreate the 16 spike cases, plus all primitive types, shared aliases, prefix/name collisions, sorted fields, and output-before-predicate runtime checks. Demonstrate finite-number/extra-key/symbol/postcondition limits with existing verifier checks. |
| Independent consumer | Temporary workspace contains only package, trusted fixture/consumer, and prepared tool config. Compile fixed export with NodeNext, check emitted ESM import, strictly decode contract, then verify fixed input. Guard frontend/compiler-root loading as in 0017. |
| Two-Box wiring | Separate trusted fixture contexts with compatible existing types and fixed exports. Prewritten wiring checks human-owned expected behavior; reject malformed output rather than adapting it. Does not select the M3 pilot. |
| Invalidation policy | Two Boxes: change source/shared record/predicate, one task/scope, shared policy, rules/tool environment. Assert regeneration scope separately from output differences. Candidate/test-only changes require no package changes; stale-evidence enforcement is not tested as an M2 feature. |
| Publication | One invalid Box in a multi-Box request publishes nothing; existing destinations/candidates remain untouched. Diagnostics do not expose hidden tests or credentials. |
| Regressions | `npm run check`, `npm run build`, director-box/composition/structured-types demos, Hello World CLI, canonical `bound spec` comparison. Reuse existing codec/verifier tests rather than duplicating semantics. |

For this design revision, run local Markdown link/section/status checks and `git diff --check`; report the disposable spike separately. Production regression tests are not claimed as run for unimplemented functionality.

## Architectural decisions approved by the Product Owner

1. External adapter with minimal path-only bindings/informational metadata; omit hashes, approval references, package ID, and per-package toolchain pinning from M2.
2. Human-controlled approval prerequisite without automated approval enforcement; verbatim protected task/scope/policy snapshots and existing repository tooling.
3. Fixed `candidate/implementation.ts` / named `implement`, NodeNext ESM type-only import, generated declaration projection, explicit `undefined` return convention, and documented empty-record static limitation.
4. Conservative all-source regeneration policy, allowing unchanged output bytes; fresh publication rather than candidate updates or a semantic impact graph.
5. M2 renders reproducible bounded context; M3 enforces development isolation and M4 defines evidence identity, stale-evidence/promotion controls, and any stronger authorization/integrity mechanism.

The Product Owner explicitly approved all five decisions above as part of accepting this revised design. Return any newly discovered need for new contract semantics, automated approval, or orchestration to the Product Owner rather than expanding scope.

## Delivery and authorization boundary

The design was delivered and revised under this assignment; the Product Owner subsequently authorized recording acceptance and preparing [Assignment 0019 — Implement Deterministic Task Derivation](0019-implement-deterministic-task-derivation.md). Assignment 0019 remains Proposed pending separate review and implementation authorization. This acceptance record authorizes neither production code nor M2 closure.

## Product Owner acceptance and completion evidence

The Product Owner explicitly approved and accepted the revised Assignment 0018 design and all five documented architectural decisions, and authorized marking this design assignment **Completed**.

- **Accepted design revision:** `049ffc626e82e2f07fbc566979d9dbe6b6c4c098` — simplified M2 metadata, explicit human approval boundary, deterministic-output versus invalidation distinction, and disposable TypeScript feasibility results.
- **D-01:** The accepted document specifies exact inputs/package files, existing component reuse, entrypoint, scope, alternatives, exclusions, and future implementation tests. It was delivered as Proposed without production changes or milestone status changes; this later acceptance updates its assignment status only.
- **D-02:** The revision separates mechanical structural validation from human approval, and deterministic rendering from conservative regeneration and M4 evidence/promotion responsibilities.
- **D-03:** Sixteen independent TypeScript compilation cases had zero unexpected outcomes; successful cases also passed built ESM import checks. Explicit `undefined` returns and empty-record symbol-key limitations are documented. Disposable artifacts were removed, not committed.
- **Documentation verification:** Local links, required sections/status, balanced code fences, and whitespace checks passed for the accepted revision. No production functionality or production regression results are claimed.

No architectural decision among the five remains pending. M2's implementation exit gate is still outstanding; accepting this design does not establish task derivation is implemented, authorize the M3 pilot, or complete M2.
