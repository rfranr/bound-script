# Assignment 0019 — Implement Deterministic Task Derivation

**Status:** Pending Product Owner acceptance
**Milestone:** [M2 — Deterministic task derivation](../roadmap.md#m2--deterministic-task-derivation)
**Design:** [Assignment 0018](0018-design-deterministic-task-derivation.md), including its five approved architectural decisions and Product Owner acceptance record.
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md).

## Implementation authorization

The Product Owner separately approved Assignment 0019 and explicitly authorized implementation of the accepted Assignment 0018 scope, complete mandatory checks, and commit/push to the current feature branch. Implementation delivery remains pending Product Owner acceptance; it does not complete M2. Earlier references below to waiting for separate authorization describe the original proposal gate, now satisfied by that explicit instruction.

## Objective

Implement the approved minimal external derivation adapter that combines BoundScript architecture, existing canonical portable Box contracts, and human-owned functional requirements into reproducible, bounded per-Box implementation packages.

M2's exit gate is: **identical approved inputs repeatedly produce equivalent tasks without manually duplicated public interfaces.** This assignment must demonstrate byte-identical relative file sets/content for identical explicit inputs under the same supported derivation rules/environment. Deterministic handoffs do not make agents deterministic or establish implementation correctness. Assignment delivery does not automatically close M2.

## Prerequisites and authorization

- Assignment 0018's revised design (`049ffc626e82e2f07fbc566979d9dbe6b6c4c098`) and all five decisions are explicitly approved and accepted by the Product Owner. Its later acceptance record is authoritative for that approval.
- Reuse portable specification version 1, its extraction/strict canonical codec, and the accepted standalone verifier from Assignments 0016–0017. Preserve compiler/runtime ownership and dependency direction.
- **This assignment is Proposed. Wait for separate Product Owner review and explicit implementation authorization before adding production code.** Approval of Assignment 0018 or preparation/commit/push of this document is not implementation authorization.
- Humans must approve the actual architecture, selected task/scope/policy versions, and their consistency before operational derivation. This prerequisite is not mechanically enforced by the adapter.

## Requirements

### 1. External adapter and explicit selection

Provide a repository-level TypeScript script with a pure rendering helper outside compiler/runtime. Use existing parsing, whole-system validation, `extractBoxDevelopmentSpec`, and strict canonical serialization. Do not add a package or change compiler/runtime APIs to host task generation.

Accept an explicit repository root, binding document, fresh output directory, and selection of one exact system/Box pair or all listed Boxes. The developer may choose a small script/npm command interface and file placement consistent with existing tooling; document the invocation and errors. Do not introduce a general CLI framework or alter existing `bound` execution/spec behavior.

Use the exact `boundscript/handoff-input` version-1 shape in Assignment 0018 Section 2: `format`, `version`, `architecture`, `policy`, and nonempty `boxes` entries containing exactly `system`, `box`, `task`, `scope`. Paths are repository-relative POSIX paths resolved against the explicit root. Sort selected identities by code point. Reject missing/unknown keys, unsupported versions, duplicate selections, invalid identities, unknown source selections, absolute/traversal paths, symlinks, missing/nonregular files, invalid UTF-8, and empty Markdown. Do not infer selections from names, filenames, or director invocations. Validate the whole source, including unused declarations; unused valid Boxes can be selected.

Read task/scope/policy text without interpreting business intent. Human-owned task content supplies responsibility, requirement IDs, representative examples, and acceptance criteria; scope supplies private implementation boundaries; policy supplies allowed dependencies/tools or explicitly none. Do not generate missing requirements or duplicate interface declarations in prose. Missing intent/conflicts require human clarification, not automatic repair. Standalone contract-only input is out of scope.

### 2. Exact package and canonical metadata

Produce exactly the eight files in Assignment 0018 Section 3 under `<output>/<system>/<box>/`:

- `handoff.json`, `README.md`, `contract.box-spec.json`.
- Verbatim `task.md`, `scope.md`, `policy.md` snapshots.
- `generated/contract.d.ts`, `seed/implementation.ts`.

The canonical contract is the sole packaged public interface, with resolved inline shared types. Keep its existing canonical bytes and version unchanged. Generate the exact informational metadata shape/key order from Assignment 0018: `format`, `version`, `derivationVersion`, system/Box/operation identity, selected input paths, and fixed entrypoint. It contains no approval references, hashes, package ID, tool revision, toolchain/test references, or output inventory.

Use fixed JSON key order, two-space indentation, LF, one final LF, UTF-8 without BOM; use existing serializer for contract bytes. Generated text uses LF/one final LF; snapshots preserve exact bytes, including CRLF/final-newline differences. Exclude clock/random/absolute-path/network/environment/branch/model identity. Input key/Box order, output root, cwd, and enumeration order must not affect bytes for the same explicit inputs. Input path changes may change metadata even for equal file contents. Keep a derivation-rules version with tests; intentional rendering behavior changes require a rules-version decision.

Render and validate all selected packages before publishing any. Fail with nonzero diagnostics identifying stage and applicable Box/path, without partial published output or overwriting existing outputs/candidate directories. Use staging/final rename rather than persistent execution state. Generated packages/build artifacts are disposable and must not be committed.

### 3. TypeScript projection and fixed entrypoint

Generate the approved `Input`, `Result`, and `Implementation = (input: Input) => Result | Promise<Result>` exports. Map primitives directly and void results to `undefined`. Generate sorted `Record_<name>` aliases with quoted, sorted fields, deduplicating repeated record identity. Use `Record<string, never>` for empty records, not `{}`. Preserve contract identity in descriptors without adding nominal runtime brands.

The seed must import type `Implementation` from `../handoff/generated/contract.js`, export named `implement`, and throw `new Error('Not implemented')`, as specified in Assignment 0018. It is copied externally to `candidate/implementation.ts`, not executed by derivation. Document ESM/NodeNext setup supplied by the external environment. Type-only imports disappear from emitted JavaScript; no runtime declaration-module implementation is generated. A trusted consumer importing `implement` must check export naming.

Document the tested requirement to explicitly return `undefined` for void operations under this authoring convention, while preserving runtime acceptance of implicit undefined. Document structural/empty-record limitations: symbol-key extras can type-check, and static typing does not prove own-key exactness, nominal origin, finite numbers, or predicates. Existing verifier/runtime checks remain authoritative.

### 4. Human approval and protected context

Mechanically check only structural inputs, source/Box validity, supported contracts, and deterministic rendering. Successful derivation does **not** verify approval. Do not add an approval flag/record parser, hash check, dirty-tree gate, semantic Markdown validator, or authenticated policy engine.

Generated instructions and usage documentation must distinguish the human approval prerequisite from structural success. The adapter may technically render unapproved nonempty text; tests/docs must acknowledge this rather than claim authorization enforcement.

The external controller supplies read-only `handoff/` beside writable `candidate/`. Agents may work only in `candidate/**`, possibly narrowed by scope, and may not edit contracts/shared types, requirements, trusted tests, wiring, dependency manifests/lockfiles, or policy. New dependencies/interfaces/responsibilities require human approval. Do not bundle full architecture, unrelated context, hidden tests, credentials, or dependency trees. Missing context prompts human clarification.

No candidate loader, compilation service, sandbox, or enforcement system is part of this adapter. Test compilation/loading is limited to trusted fixtures. Actual untrusted candidate execution requires M3 isolation; directories/worktrees and Node subprocesses are not security boundaries.

### 5. Regeneration policy, not evidence machinery

Implement fresh derivation, not incremental state or automatic currentness tracking. Document and test Assignment 0018's conservative policy:

- Any architecture edit requires human-controlled regeneration of all still-selected Boxes from that source, with whole-system revalidation. Comments/director/unrelated declaration changes may regenerate identical bytes.
- Task/scope edits require regeneration of referencing Boxes; shared policy changes affect every referencing package.
- Rules/tool-environment changes require full derivation/comparison/regression checks; intentional behavior changes require a rules-version decision.
- Discard/rederive modified packages into fresh outputs. Retire removed/renamed Box selections without silently migrating candidates.
- Candidate/private-test/trusted-acceptance-test changes alone do not change handoffs. Affected verification must be rerun, but evidence tracking/enforcement is M4 work.
- Approval decisions may change authorization while package bytes remain identical; the adapter cannot detect that.

Separate affected regeneration scope from output differences in tests and reports. Do not add semantic impact analysis, watchers, hashes, fingerprint databases, candidate repair, stale-evidence enforcement, or promotion gates. Explain conservative overinvalidation and inability to infer unrecorded requirement/integration impact.

### 6. Usage documentation and delivery

Document a complete invocation using small trusted fixtures, human approval checklist, exact package layout, prepared ESM/TypeScript environment, fixed entrypoint, fresh regeneration workflow, supported tool versions, and limitations. Keep task instructions separate from formal contract semantics. Link from relevant existing documentation without describing planned isolation/evidence as implemented.

Update roadmap delivery/evidence links when implementation is authorized and delivered; do not change acceptance records or mark M2 Completed without separate Product Owner acceptance and exit-gate authorization.

## Expected affected files after authorization

Keep the footprint minimal:

- Repository script and pure rendering helper in an appropriate tooling directory; a root npm script only if needed for a usable invocation.
- Vitest derivation tests and trusted source/Markdown/binding fixtures; TypeScript consumer tests using temporary independent workspaces.
- Root test/type configuration only as needed to cover tooling and fixtures without weakening checks.
- Usage documentation, relevant navigation, and roadmap delivery evidence.

No grammar, artifact/spec schema/semantics, runtime verifier semantics, compiler lowering, sandbox implementation, new workspace package, or new general framework is expected. Return to the Product Owner if implementation reveals a need to change those boundaries. Do not commit generated handoff directories or spike/build artifacts.

## Mandatory acceptance criteria and tests

All eight implementation criteria and the full concrete test strategy in Assignment 0018 apply. The following make their mandatory evidence explicit:

| ID | Required passing evidence |
| --- | --- |
| AC-01 | Existing whole-system extraction/codec produces selected packages, including an unused valid Box. Published structured Greeter contract remains byte-identical to its reference. Unknown selections, missing director, invalid unused declarations, unsupported versions/shapes, duplicate/malformed bindings, and identity mismatch fail before publication. |
| AC-02 | Compare exact file sets/bytes directly across two output roots, repeated runs, permuted input keys/Box ordering, changed cwd/enumeration order. Preserve Markdown CRLF/Unicode/quotes/final-newline differences. No hashes or manual interface duplication. Unrelated Box bindings do not alter a selected package. |
| AC-03 | Golden tests assert all eight files, metadata shape/order/version/identities/paths, verbatim snapshots, sorted generated declarations, seed/import/export, and fixed instructions. No hidden acceptance assets, full source, unrelated implementations, or environment-dependent metadata. |
| AC-04 | Reject unsafe/missing/nonregular/symlink/traversal/absolute input paths, invalid UTF-8, empty Markdown, and unknown keys. Multi-Box failure publishes nothing; existing output/candidate destinations remain untouched. Diagnostics identify structural failure without approval claims. Nonempty unapproved text can render; approval remains a documented human gate. |
| AC-05 | Two-Box regeneration matrix covers source comments/shared records/predicates, one task/scope, shared policy, rules/environment changes, removed Boxes, and candidate/test-only changes. Assert affected invocation scope independently from byte differences; demonstrate identical regenerated output after an irrelevant source edit. No automated currentness/promotion claim. |
| AC-06 | Independent temporary ESM/NodeNext consumer has only its handoff, trusted fixture, and prepared tool config. Recreate the 16 spike cases from 0018 and extend coverage to all primitives, shared aliases, prefix collisions, sorted fields, and empty records. Check sync/async functions, explicit undefined, rejection of wrong parameter/result and implicit void, expected symbol-key static limitation, named-export consumer check, and built ESM import without runtime `contract.js`. Strictly decode packaged JSON and verify fixed trusted inputs without source/director/compiler-root/frontend loading in the consumption path. Reuse 0017 import-boundary techniques. |
| AC-07 | Two separate trusted fixture implementations consume independent packages and integrate via prewritten wiring, with human-owned expected-output assertions and no interface/candidate repair. Malformed output is rejected. This is not the M3 agent pilot, final pilot selection, or comparative evaluation. |
| AC-08 | `npm run check`, `npm run build`, director-box/composition/structured-types demos, Hello World CLI, and canonical `bound spec` export comparison pass. Reuse existing verifier checks for finite numbers, exact own fields/symbol extras, and output-before-postcondition ordering; do not duplicate evaluation semantics. Documentation accurately distinguishes structural checks, human approval, static limits, and unimplemented enforcement. |

Record actual Node/TypeScript versions and check results in delivery. Use trusted fixtures only; no real agents, untrusted candidate execution, infinite loops, or new framework. Temporary compile/import checks are test harnesses, not a production candidate loader/transpiler service.

## Explicit exclusions

No general task language/new DSL, task planner/orchestrator/scheduler, agent/provider integration, LLM call during derivation, dependency/capability language expansion, autonomous approval, hash/integrity manifests, package digest, per-package toolchain pinning, evidence database, stale-evidence enforcement, candidate promotion, integration repair, sandbox/time/resource enforcement, production isolation, or new contract authority. No M3 execution or M6 baseline/evaluation design under this assignment.

## Delivery after separate implementation authorization

Report changed files, invocation/package example, deterministic comparison results, independent compilation/verification/wiring results, regression results, supported tool versions, deviations, and unresolved questions. Follow repository commit conventions and push only with authorization. Do not mark this assignment Completed or close M2 on implementation delivery alone; explicit Product Owner acceptance remains required.

Preparation and publication of this **Proposed** assignment are authorized documentation work only. No production implementation is authorized by this document's creation or by the acceptance of Assignment 0018.
