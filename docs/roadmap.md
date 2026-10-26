# BoundScript roadmap

This is the authoritative **current execution plan and milestone tracker**. [Accepted Proposal 0013](proposals/0013-deterministic-architecture-for-probabilistic-construction.md), especially Section 11, remains the historical authority for product direction; this roadmap does not replace or amend that decision.

## Current position

**M0 — Completed:** Proposal 0013 establishes the approved product direction; the supporting documentation and governance deliverables are present (see M0 evidence below).

**M1 — Completed:** The Product Owner accepted Assignment 0017 after all mandatory checks passed on the corrected implementation (`5d15c9b`). The criterion-by-criterion evidence below confirms M1's exit gate, not merely assignment delivery.

**M2 — Completed:** The Product Owner explicitly accepted [Assignment 0019](assignments/0019-implement-deterministic-task-derivation.md#product-owner-acceptance-and-completion-evidence) against reviewed implementation `b692da02f54a36beabce47f1bc41e4d7a68ac926`, including exclusive publication and regression coverage, and authorized M2 closure. The exit-gate evidence below establishes repeatable byte-identical tasks without manually duplicated public interfaces; delivery alone did not close the milestone.

**Next milestone: M3 — Planned until revised execution is explicitly approved.** The Product Owner accepted [0021's phase-1 report](assignments/0021-qualify-existing-pilot-tooling.md#product-owner-acceptance-and-conclusion) as an **Inconclusive infrastructure investigation** and concluded 0021 **Completed**. No sandbox/OAuth-proxy qualification is an M3 prerequisite. [0020's bounded design](assignments/0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment) keeps ContactOnboarding, deterministic handoffs, independent contexts, immutable approved architectural/test authority, frozen integration/failure accounting, metrics and baseline. Production-grade agent isolation and credential proxying are not pilot objectives; temporary directories/worktrees are organizational boundaries, not security sandboxes. All candidate compilation/execution/tests remain in disposable containers without credentials/network access and with restricted mounts—never directly on the host. BoundScript core and handoff format remain independent of coding-agent/sandbox providers; Pi/container choices are external operator details, with no adapters/frameworks/proxies to build. The Product Owner accepted [0023 technical preparation](assignments/0023-prepare-and-freeze-independent-pilot-assets.md) after independently passing validation. Final requirement-to-value review found no discrepancies: [the entire unchanged asset tree is frozen](development/0023-contact-onboarding-freeze.md) at `aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`, and 0023 is Completed. [0022 execution](assignments/0022-run-bounded-independent-implementation-pilot.md) is Proposed pending explicit launch and spending-policy approval. Only trusted preparation controls/regressions have executed, exclusively in offline containers; no implementation agents, pilot or provider probes. M6 comparison remains separate.

| Milestone | Status | Execution assignments | Existing foundations |
| --- | --- | --- | --- |
| M0 — Approve the product thesis | Completed | 0014, 0015 | Proposal 0013 |
| M1 — Standalone contract verification | Completed | [0016 — Verifier design](assignments/0016-design-standalone-box-verifier.md), [0017 — Implementation (accepted)](assignments/0017-implement-standalone-box-verifier.md) | 0012, 0013 |
| M2 — Deterministic task derivation | Completed | [0018 — Design (accepted)](assignments/0018-design-deterministic-task-derivation.md), [0019 — Implementation (accepted)](assignments/0019-implement-deterministic-task-derivation.md) | 0013 |
| M3 — Independent implementation pilot | Planned | [0020 — Design (Completed; bounded amendment)](assignments/0020-design-independent-implementation-pilot.md), [0023 — Completed; assets frozen](development/0023-contact-onboarding-freeze.md); [0022 — Execution (Proposed)](assignments/0022-run-bounded-independent-implementation-pilot.md) needs separate approval | M1 verification, M2 handoffs; 0021 concluded Inconclusive/non-gating |
| M4 — Integration and evidence | Planned | Not yet defined | M1–M3 outputs |
| M5 — Architectural evolution experiment | Planned | Not yet defined | M2–M4 workflow |
| M6 — Comparative evaluation | Planned | Not yet defined | M3–M5 evidence |

M0, M1, and M2 are Completed. Product-direction approval and trusted single-invocation verification are distinct from M3 pilot design/execution and M6 comparative baseline/evaluation. Assignment acceptance remains independently tracked; no future implementation assignments are created by this roadmap.

## Milestones

### M0 — Approve the product thesis

- **Status:** Completed.
- **Objective:** Establish agreement on the product direction and the hypothesis to be tested.
- **Scope/deliverables:** Approved architectural direction, role definitions, guarantees, non-guarantees, and high-level pilot/comparison intent; aligned product/architecture documentation and roadmap governance. Detailed pilot scope is tracked under M3 and comparative baseline design under M6, to be defined before their respective experiments rather than as M0 closure conditions.
- **Completion criteria:** Recorded agreement that success means reduced coordination and understandable, verifiable boundaries—not extra DSL features or agent count—with the supporting documentation and governance in place. These criteria are satisfied; no M0 deliverable remains outstanding.
- **Execution assignments:** [0014 — Documentation alignment](assignments/0014-align-project-documentation-with-proposal-0013.md); [0015 — Roadmap governance](assignments/0015-establish-roadmap-governance.md). Their independent acceptance records are not changed by this milestone status.
- **Existing foundations/evidence:** Proposal 0013 is Accepted (commit `289cb26`) and establishes the direction, roles, guarantees/non-guarantees, and experiment intent. [README](../README.md) introduces the product and current capabilities; [architecture](architecture.md) separates the target workflow from implemented components; [decisions](decisions.md#accepted-direction--proposal-0013) records the approved direction and rationale (documentation delivered in `9a6789f`). [This roadmap](roadmap.md#tracking-and-maintenance-rules) establishes milestone/assignment tracking and documentation responsibilities, with README navigation in place. Together these satisfy M0's documentation and governance deliverables.

### M1 — Standalone contract verification

- **Status:** Completed.
- **Objective:** Check Box implementations independently of executable director programs.
- **Scope/deliverables:** Minimal verifier consuming existing portable Box specifications and trusted fixture implementations, without an executable director or source AST; reuse existing runtime validation semantics.
- **Completion criteria:** Valid cases pass; invalid inputs, candidate execution failures, invalid outputs, and postcondition failures are distinguishable. Existing examples remain compatible.
- **Execution assignments:** [0016 — Design Standalone Box Verifier](assignments/0016-design-standalone-box-verifier.md) records the approved design and Product Owner clarifications. [0017 — Implement Standalone Box Verifier](assignments/0017-implement-standalone-box-verifier.md) delivers the codec subpath, shared runtime checks, single-invocation verifier, consumer/type/parity tests, and [usage documentation](box-development-spec.md#standalone-verification). The Product Owner explicitly accepted Assignment 0017 after all mandatory checks passed. Its [acceptance record](assignments/0017-implement-standalone-box-verifier.md#product-owner-acceptance-and-completion-evidence) identifies implementation `ea2a8dc` and accepted correction `5d15c9b`. M1 closure follows the exit-criterion verification below, not automatic completion from assignment delivery.
- **Existing foundations:** [0012 — Specification extraction](assignments/0012-box-specification-extraction.md) and [0013 — Specification portability](assignments/0013-box-specification-portability.md) provide existing foundations, not verifier execution.
- **Dependencies/evidence:** Builds on M0's direction and existing contracts. Extraction was delivered in `4a63eff`; portability/CLI export in `9beec9b`, documented in the [Box spec reference](box-development-spec.md). Assignment 0013 explicitly records Assignment 0012 as implemented, reviewed, and accepted. No equivalent formal acceptance record was found for Assignment 0013. Neither delivery completes M1.
- **0017 delivery checks:** Type checking and all 374 tests (15 files) pass, including public-import, structured-result, inspection, type-narrowing, and legacy-parity coverage. Review corrections add throwing contract getter/proxy regressions, classified as `invalid-contract` before candidate execution. Build, the three existing Box demos, Hello World CLI, and byte-identical canonical spec export pass. These checks were rerun successfully on accepted revision `5d15c9b` before recording Product Owner acceptance and M1 closure.

**M1 exit-criterion verification:**

| Criterion | Supporting evidence | Result |
| --- | --- | --- |
| Portable specs and trusted functions without a source AST/executable director | `tests/box-verifier-consumer.test.ts`: published JSON consumption, existing trusted functions, guarded source imports, and built Node public-export smoke test. | Satisfied |
| Reuse existing runtime validation semantics | Shared `packages/runtime/src/contract-checks.ts`, exercised by verifier and legacy runtime parity/regression tests; artifact/spec versions and legacy behavior remain unchanged. | Satisfied |
| Valid cases pass | `tests/box-verifier.test.ts` and consumer tests cover primitive/record, synchronous/asynchronous, void, and successful postcondition cases. | Satisfied |
| Invalid inputs, execution failures, invalid outputs, and postcondition failures are distinguishable | Verifier tests assert the structured failure discriminants, first-failure ordering, no call on invalid input, and output checks before predicates. Inspection and malformed-contract failures remain separate. | Satisfied |
| Existing examples remain compatible | Full 374-test suite, build, three Box demos, Hello World CLI, and byte-identical canonical export all pass on `5d15c9b`. | Satisfied |

All M1 completion criteria are verified, with no missing evidence. Completion is limited to the approved trusted single-invocation scope; it does not claim candidate isolation, behavioral acceptance infrastructure, or later milestones.

### M2 — Deterministic task derivation

- **Status:** Completed.
- **Objective:** Derive consistent, bounded per-Box implementation contexts from approved inputs.
- **Scope/deliverables:** Handoff packages combining approved BoundScript specs and external functional tasks; reuse the existing spec format and a fixed TypeScript entrypoint. No general task language.
- **Completion criteria:** Identical approved inputs repeatedly yield equivalent tasks without manually duplicated public interfaces.
- **Execution assignments:** [0018 — Design Deterministic Task Derivation](assignments/0018-design-deterministic-task-derivation.md) is Completed after explicit Product Owner acceptance of revision `049ffc626e82e2f07fbc566979d9dbe6b6c4c098` and all five architectural decisions. [0019 — Implement Deterministic Task Derivation](assignments/0019-implement-deterministic-task-derivation.md) is Completed after explicit Product Owner acceptance of reviewed implementation `b692da02f54a36beabce47f1bc41e4d7a68ac926`, including the publication correction, and separate authorization to close M2. The [assignment acceptance record](assignments/0019-implement-deterministic-task-derivation.md#product-owner-acceptance-and-completion-evidence) records AC-01 through AC-08 and the supported environment.
- **Design progress/evidence:** The [0018 acceptance record](assignments/0018-design-deterministic-task-derivation.md#product-owner-acceptance-and-completion-evidence) documents structural validation versus human approval, minimal path-only metadata, fixed TypeScript entrypoint/projection, and conservative regeneration separately from output determinism. Its disposable spike passed 16 independent compilation cases with no unexpected outcomes and built ESM import checks for successful cases; static empty-record limitations remain documented. These are design/feasibility results, not evidence that derivation is implemented.
- **0019 delivery/evidence:** External [adapter and pure renderer](../tooling/handoff.ts), [usage and limitations](task-derivation.md), [golden/determinism/structural/regeneration tests](../tests/handoff.test.ts), and [independent consumer/wiring tests](../tests/handoff-consumer.test.ts). `npm run check` passes all 416 tests in 17 files and tooling type checking; build, director-box/composition/structured-types demos, Hello World CLI, and byte-identical canonical `bound spec` export pass. Repeated roots/input ordering/cwd compare exact file sets/bytes. Twenty independent strict ESM/NodeNext compilation cases reproduce all 16 design-spike outcomes and extend primitive/alias coverage; successful built imports need no runtime declarations. Two separately compiled trusted packages integrate via prewritten wiring with exact expected outputs and malformed-output rejection. Consumption guards prohibit frontend/compiler-root/Langium loading and director execution. Existing verifier finite-number/own-key/symbol/output-before-predicate checks remain passing. Actual environment: Node v24.16.0, TypeScript 5.9.3, Linux, locked dependencies.
- **0019 review correction:** Replaced the destination-check/directory-rename race with atomic exclusive symlink publication of the complete sibling backing tree. A concurrent empty/populated directory, file, or symlink is never replaced; failed publication cleans only this invocation's unpublished tree. Six additional tests cover complete publication, four separate-process destination-creation races (preserving destination inode and contents), and fail-closed unsupported publication. Rendering/golden bytes and rules version 1 are unchanged. Usage documents the output symlink/backing-data lifecycle; no lock service or orchestration was added. Full check/build/demos/Hello World/canonical export and independent consumers were rerun successfully. The Product Owner explicitly accepted this correction as part of completing Assignment 0019 and closing M2.
- **Constraint/deviation:** The existing grammar has no comment tokens. Comment edits conservatively affect all source selections but fail parsing with no publication; valid irrelevant director/declaration edits regenerate identical bytes. No grammar expansion was made. Rules/environment-change checks demonstrate the full-set rederivation/comparison workflow under the supported environment, not cross-version equivalence. Approval and regeneration scope remain human-controlled, not enforced by a new state/evidence mechanism.
- **Acceptance/closure:** The Product Owner accepted Assignment 0019 and explicitly authorized M2 completion against the reviewed implementation and exit-gate evidence below. No M2 acceptance correction remains unresolved. This closes only the approved deterministic derivation scope; M3 requires its own design assignment and separate Product Owner approval, and no M3/M4 implementation or pilot/evaluation work is authorized.
- **Existing foundations:** Assignment 0013's portable contracts are a shared foundation, not task derivation.
- **Dependencies:** Approved architecture and human-owned functional inputs, portable specs, and the accepted M1 verifier. The adapter performs structural checks, not human approval verification; isolation remains M3 work and durable evidence/promotion remains M4 work.

**M2 exit-gate verification:**

| Criterion | Supporting evidence | Result |
| --- | --- | --- |
| Identical explicit inputs repeatedly yield equivalent bounded tasks | `tests/handoff.test.ts` compares exact relative file sets/bytes across fresh roots, repeated runs, input key/Box ordering, changed cwd, and reverse filesystem creation order; Markdown snapshots preserve exact bytes. | Satisfied |
| No manually duplicated public interfaces | Existing whole-system extraction and canonical codec supply the sole packaged public contract and generated declarations; Greeter export remains byte-identical. Eight-file golden and unused-Box/source-validation tests pass. | Satisfied |
| Complete, exclusive publication without overwriting concurrent destinations | Accepted correction `b692da02f54a36beabce47f1bc41e4d7a68ac926`; separate-process races preserve empty/populated directories, files, and symlinks, including inode/contents, with unpublished-data cleanup and fail-closed unsupported publication. | Satisfied |
| Independently consumable handoffs and trusted integration without repair | Twenty strict ESM/NodeNext compilation cases, guarded standalone packaged-JSON verification, and separately compiled trusted LoadUser/Greeter packages with fixed wiring/expected outputs and malformed-output rejection. | Satisfied |
| Existing behavior and authority boundaries retained | All 416 tests in 17 files, type checking, build, three demos, Hello World CLI, canonical export comparison, and handoff CLI pass. Structural success does not verify human approval; isolation, evidence enforcement, and agent execution remain unimplemented. | Satisfied |

The Product Owner explicitly accepted the implementation and authorized closure on this evidence. M2's exit gate is satisfied under the supported environment, not a claim of cross-version reproducibility, agent determinism, arbitrary correctness, or later milestone completion.

### M3 — Independent implementation pilot

- **Status:** Planned until revised pilot execution is explicitly approved. Asset preparation is a separate readiness stage and does not start/complete the pilot or satisfy its untested exit gate.
- **Objective:** Test whether bounded tasks allow independent implementations to integrate without interface negotiation.
- **Scope/deliverables:** Preserve ContactOnboarding's independent `NormalizeContact` and `RenderWelcome` Boxes, exact contracts/requirements, deterministic M2 handoffs, protected acceptance tests, frozen no-repair wiring/failure rules and outcome metrics. Independent agent contexts and immutable human-approved architectural/test/wiring authority are essential. Use the bounded external agent profile (currently tool-free native Pi in separate temporary workspaces) without shared implementation context; generation directories do not provide OS isolation. All candidate compilation/execution/tests use disposable credential-free offline containers with restricted mounts. Actual 0023 assets are frozen unchanged at the recorded revision after technical acceptance and final consistency review; launch no agents until execution/budget approval. Keep the baseline preregistered, not executed.
- **Completion criteria:** Both candidates pass independent checks and integrate through prewritten wiring without implementation edits or agent-to-agent negotiation.
- **Assignments:** [0020 design](assignments/0020-design-independent-implementation-pilot.md) remains Completed, retaining original acceptance of `7b75de628a91b81ee0160ba34360297ff2b4e15c` and the Product Owner-directed bounded policy. [0021](assignments/0021-qualify-existing-pilot-tooling.md#product-owner-acceptance-and-conclusion) is **Completed, outcome Inconclusive**, by explicit acceptance of phase-1 report revision `847e52805f467bf2007dd30f07fad387a90806bf`; no runtime is qualified and no further investigation is required as an initial pilot gate. [0023 — Prepare and Freeze Independent Pilot Assets](assignments/0023-prepare-and-freeze-independent-pilot-assets.md) is Completed by accepted technical preparation and the conditional [final-review/freeze instruction](development/0023-contact-onboarding-freeze.md), not automatic test-based acceptance. [0022's execution proposal](assignments/0022-run-bounded-independent-implementation-pilot.md) is now ready for explicit launch/budget approval, not activated by the freeze.
- **Design evidence:** The original [0020 acceptance record](assignments/0020-design-independent-implementation-pilot.md#product-owner-acceptance-and-completion-evidence) is retained; its operational gates are superseded by the [bounded amendment](assignments/0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment). Source/contracts/functional rules/corpus, no-repair integration/failure protocol, metrics and baseline are preserved. Documentation checks include source parsing/whole-system extraction, canonical/shared-descriptor equality, preservation comparisons, links/anchors/status and whitespace. These are design checks, not candidate execution, container readiness or pilot results.
- **Remaining readiness/approval:** Approve 0022's one-trial plan, existing model/episode limits (at most four episodes, 160 logical model-response turns and 120 active generation minutes; normally 2–4 complete responses), and a monetary ceiling/enforcement policy or explicit usage/time-only policy if native billing is unobservable. No model/provider/auth probe or agents before that approval. Recheck ordinary tool-free/container readiness from the frozen checkout before calls; no new research/framework/proxy or reopened 0021 gate. Source/tests/wiring/baseline remain unchanged. Earlier 39/24 independent rows, 18 integration rows and 416 repository tests are accepted preparation evidence, not pilot results.
- **Existing foundations:** M1 verification and M2 handoffs; accepted 0020 design, not pilot execution.
- **Agent/provider independence and risk policy:** No Pi-specific integration, sandbox dependency, SDK/callback, credential logic or vendor fields in the language/compiler/runtime, portable specs or handoff format/templates. The current tool/model and container CLI are replaceable external operator choices, not BoundScript authorities. Independent contexts/frozen authority remain required; production-grade isolation/credential proxying do not. The native agent client/operator are trusted host software; restricted workspaces and tool disabling do not OS-isolate them from bugs, prompt/attachment errors or mistakes. Candidate containers share a kernel, and read-only tests may be read or JavaScript state tampered with; do not claim test secrecy, authenticated results or production security. Preserve the existing provider/model without a switch unless explicitly approved. 0023 authorizes asset preparation only, not agents/pilot execution; M3 stays Planned after delivery until execution is explicitly approved. M6 comparison remains separately authorized and unexecuted.

### M4 — Integration and evidence

- **Status:** Planned.
- **Objective:** Make verification, integration, and acceptance evidence reproducible and understandable.
- **Scope/deliverables:** Repeatable workflow and human-readable reports connecting requirements, approved contracts, candidate revisions, tests, and observed outcomes.
- **Completion criteria:** A fresh run reproduces relevant checks; unauthorized modifications and stale evidence prevent promotion. A human can understand the architecture and the scope of verified implementation behavior.
- **Execution assignments:** Not yet defined.
- **Existing foundations:** M1–M3 verification, handoffs, and pilot candidates.
- **Dependencies:** M1–M3 verification, handoffs, and pilot candidates. Integration uses approved wiring, not silent implementation repairs; evidence must distinguish checked behavior from unverified properties.

### M5 — Architectural evolution experiment

- **Status:** Planned.
- **Objective:** Demonstrate controlled evolution of approved Box boundaries.
- **Scope/deliverables:** An Architect proposes a meaningful decomposition change with rationale, source diff, impact assessment, and affected task/test updates. Use a manual process or existing tools; no generalized planner is required.
- **Completion criteria:** After human approval, apply the change, regenerate affected handoffs, and reverify implementations/integration without silent changes to active architecture.
- **Execution assignments:** Not yet defined.
- **Existing foundations:** M2–M4 handoff, verification, and evidence workflow.
- **Dependencies:** Existing pilot architecture and M2–M4 workflow. Public architectural changes require human approval.

### M6 — Comparative evaluation

- **Status:** Planned.
- **Objective:** Determine whether BoundScript's benefits justify its complexity.
- **Scope/deliverables:** Define the comparative baseline and measurement protocol **before M3 pilot implementation begins**, using the same functional requirements and comparable tooling. Repeat the pilot with plain TypeScript interfaces, Markdown tasks, tests, and existing coding agents. Compare coordination, boundary drift, context needs, comprehension, and workflow overhead using Proposal 0013's metrics.
- **Completion criteria:** A documented decision assesses meaningful advantages and chooses whether to continue, narrow the DSL, reuse existing IDL technologies, or stop. A positive result is not assumed.
- **Execution assignments:** Not yet defined.
- **Existing foundations:** M3–M5 pilot and workflow evidence for the final comparison.
- **Dependencies:** Pilot and workflow evidence from M3–M5 for final evaluation. The baseline and measurement protocol are M6 design responsibilities that must be completed ahead of M3 implementation, potentially alongside M1 preparation. This early design work does not block M0 completion or starting M1.

## Tracking and maintenance rules

- Milestone statuses are **Planned** (not started), **In Progress** (active work), **Blocked** (cannot advance; record the blocker), **Completed** (completion criteria met with supporting evidence), and **Cancelled** (no longer pursued; record the approved reason).
- Assignments retain their own independent status and existing sequential `NNNN` numbering. Milestone IDs do not renumber assignments. A milestone may have multiple assignments; completing or accepting one does not automatically complete its milestone.
- Keep assignment status separate from delivery evidence. A commit proves a delivery exists, not that the Product Owner accepted it. Do not alter assignment or review records without their owner's authorization; follow the [development workflow](development/developer-workflow.md).
- When work, acceptance, or blockers change, update this tracker manually: status, linked assignments, evidence, remaining criteria, and dependencies as relevant. Record milestone completion only when its criteria are supported by acceptance/review and implementation or experiment evidence as applicable. The Product Owner retains acceptance authority; updating a status is not architectural approval.
- A roadmap update must not silently change approved boundaries or product direction. Such changes require a new proposal or explicit decision, recorded in the appropriate decision documents before the execution plan is aligned.
- Distinguish **execution assignments** (work intended to satisfy this milestone) from **existing foundations** (prior work or outputs the milestone depends on). Foundations are not evidence that the milestone itself is complete.

## Documentation responsibilities

| Document | Responsibility |
| --- | --- |
| [README.md](../README.md) | Product introduction and current capabilities |
| [docs/architecture.md](architecture.md) | Current and target architecture |
| [docs/decisions.md](decisions.md) | Approved decisions and rationale |
| [docs/proposals/](proposals/) | Historical proposals and product-direction decisions |
| [docs/roadmap.md](roadmap.md) | Current execution plan and milestone status |
| [docs/assignments/](assignments/) | Individual work definitions and acceptance criteria; owned by the Product Owner |
| [docs/reviews/](reviews/) | Review outcomes and supporting evidence; owned by the Reviewer |

Architectural decisions belong in proposals/decisions, not status edits here. Other documents may summarize the direction, but operational milestone status is maintained only in this roadmap.

## Outstanding tracking confirmations

- Assignment 0014 remains `Proposed` despite its implementation commit. No formal acceptance evidence was found; accepting Proposal 0013 does not by itself accept Assignment 0014.
- Assignment 0015 remains `Proposed` in the supplied definition. This roadmap delivery does not change its status or imply acceptance.
- Assignment 0012's acceptance is recorded in Assignment 0013's prerequisite; Assignment 0013 has implementation evidence but no explicit acceptance record found. Preserve that distinction rather than retroactively assigning statuses.
- M0's direction approval and supporting documentation/governance are complete; the independent assignment acceptance confirmations above do not reopen that milestone. Detailed pilot scope remains M3 work, and comparative baseline/evaluation remains M6 work, with the baseline protocol defined before M3 implementation. Neither blocks M1.
