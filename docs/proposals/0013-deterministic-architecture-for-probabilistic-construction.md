# Proposal 0013 — Deterministic Architecture for Probabilistic Software Construction

**Status:** Accepted.  
**Scope:** Product direction, architectural boundaries, development workflow, and validation strategy.  
**Nature:** Roadmap proposal, not an implementation assignment or authorization to change existing language semantics.

## 1. Vision

BoundScript aims to make software construction delegable to autonomous coding agents without requiring humans to continuously coordinate their implementations.

The central hypothesis is:

> A deterministic, human-readable architectural specification can serve as the authoritative boundary within which probabilistic agents independently design and implement software.

Humans define intent and approve architectural decisions. Agents propose decompositions, implementations, and architectural improvements. BoundScript represents approved boundaries, derives portable contracts and implementation tasks, and supports deterministic validation and integration.

BoundScript is not intended to replace general-purpose programming languages or embed LLM reasoning inside a compiler.

Its purpose is to separate:

- **Architectural authority:** what the system is allowed to become.
- **Implementation freedom:** how agents construct the approved components.
- **Verification authority:** what evidence is required before an implementation can be accepted.

The product objective is not merely to verify independently written code. It is to reduce the human coordination required to construct, understand, integrate, and evolve a multi-component software system.

## 2. Product hypothesis and success criteria

The hypothesis must be tested rather than assumed.

BoundScript should provide measurable advantages over delegating work using ordinary TypeScript interfaces, Markdown specifications, tests, and existing coding agents.

Potential advantages include:

1. A single, readable representation of approved architectural boundaries.
2. Deterministic generation of consistent, bounded implementation contexts.
3. Reduced interface negotiation and coordination between independent agents.
4. Detection of unauthorized architectural changes.
5. Reproducible integration checks based on approved contracts.
6. Traceability between requirements, contracts, implementations, tests, and architectural revisions.
7. Controlled architectural evolution through explicit proposals.

The initial experiments must measure:

| Metric | Question |
|---|---|
| Human interventions | How often must a human resolve coordination problems? |
| Interface renegotiations | How often do agents need to change or clarify contracts? |
| Integration modifications | Can implementations integrate without editing generated code? |
| Boundary violations | Are unauthorized changes detected before acceptance? |
| Context requirements | How much system context does each agent need? |
| Architectural comprehension | Can a human understand the system without reading all implementation code? |
| Implementation comprehension | Can a human understand each Box's declared behavior and verified properties without reading its entire implementation? |
| Workflow overhead | Does BoundScript reduce total coordination effort compared with conventional tooling? |

A successful integration alone does not prove BoundScript's value.

The same experiment must be performed with conventional TypeScript interfaces and tests.

If BoundScript does not provide meaningful benefits, its scope should be simplified rather than expanded to justify its existence.

## 3. Fundamental architecture

BoundScript separates four concerns.

### 3.1 Human authority

The human owns:

- Product requirements and intended behavior.
- Acceptance criteria and representative examples.
- Architectural decisions requiring approval.
- Security and trust policies.
- Final acceptance and promotion authority.

The human should not need to manually coordinate every implementation detail.

### 3.2 Architect (build-time Director)

The Architect may be a human or an LLM.

It interprets requirements and proposes:

- System decomposition.
- Box responsibilities.
- Public interfaces and dependencies.
- Implementation boundaries.
- Changes to existing architecture.
- Task allocation and integration plans.

The Architect is probabilistic when implemented by an LLM.

Its proposals have no authority until accepted under the project's approval policy.

The Architect must not silently change approved contracts.

The term **Architect** is used for the build-time role to distinguish it from BoundScript's existing runtime `director`.

### 3.3 BoundScript deterministic layer

BoundScript is the authoritative, machine-readable representation of approved architectural boundaries.

Its responsibilities include:

- Parsing and validating architectural declarations.
- Resolving types and contracts.
- Representing Box interfaces and allowed relationships.
- Producing canonical, portable specifications.
- Deriving consistent implementation handoffs.
- Supporting verification against approved boundaries.
- Detecting changes that require architectural approval.

The language should describe architectural constraints without prescribing internal algorithms.

BoundScript must not call an LLM during compilation, contract extraction, or deterministic verification.

Identical approved inputs should produce identical specifications and validation decisions, subject to explicitly versioned tools and rules.

### 3.4 Implementer agents

Implementers receive bounded tasks derived from approved architecture and externally supplied functional requirements.

They may independently choose:

- Algorithms.
- Internal code organization.
- Private helper functions and classes.
- Implementation techniques.
- Permitted libraries and tools.

They may not silently redefine:

- Public interfaces.
- Shared types.
- Approved dependencies.
- Architectural responsibilities.
- Acceptance criteria.
- Protected files or policies.

An implementer may propose a change to any of these boundaries, but a proposal is not an approved modification.

## 4. The Box abstraction

A Box is a **unit of delegated responsibility with an explicit architectural boundary**.

A Box is not necessarily:

- A function.
- A class.
- A microservice.
- A container.
- An agent.
- A deployment unit.

Multiple Boxes may be implemented within one application and deployed as a monolith.

A single Box may contain multiple internal modules or private abstractions.

A Box should conceptually answer six questions:

| Dimension | Question |
|---|---|
| Responsibility | What may this Box do? |
| Dependencies | What may it use? |
| Input | What does it accept? |
| Output | What may it return? |
| Constraints | How may it implement its responsibility? |
| Execution conditions | When may it act? |

These dimensions do not imply that the existing DSL already supports every corresponding declaration.

Each constraint must identify its verification mechanism.

Distinguish:

- **Declared:** present in the specification.
- **Statically checked:** verified by type or structural analysis.
- **Test-observed:** exercised by a defined test.
- **Runtime-enforced:** restricted by an actual execution boundary.
- **Unverified:** not established by available evidence.

A declaration such as `network: denied` is not a security guarantee without an enforcement mechanism.

The Box boundary defines implementation freedom, not implementation correctness.

## 5. Behavioral requirements and determinism

BoundScript must not attempt to encode every functional requirement as language syntax.

The Architect and human-owned task specification define intended behavior.

For example:

> A token may only be issued after successful credential validation.

This is a behavioral and security requirement.

A dependency declaration or a successful type check does not prove that it holds.

Depending on the application, evidence may require tests, reviewed control flow, explicit state transitions, or stronger verification mechanisms.

The deterministic layer can verify supported properties, but it cannot establish arbitrary semantic correctness.

A deterministic test result is not a universal proof.

The existing runtime `director` remains responsible for application orchestration where used. The build-time Architect does not replace it.

## 6. Target development workflow

```text
Human requirements
        |
        v
Architect proposes architecture
        |
        v
Human approval / approval policy
        |
        v
Approved BoundScript specification
        |
        v
Deterministic validation and extraction
        |
        v
Independent implementation tasks
        |
   +----+----+
   |         |
   v         v
Agent A   Agent B
   |         |
   v         v
Box A     Box B
   |         |
   +----+----+
        |
        v
Independent verification
        |
        v
Integration verification
        |
        v
Human-readable evidence
        |
        v
Explicit promotion
        |
        v
Application
```

The workflow must support sequential execution before parallel execution.

Independent implementation does not require a distributed scheduler or agent communication infrastructure.

The first implementation may use repository scripts and existing coding tools.

### 6.1 Implementation handoff

Each agent receives:

- An approved canonical Box specification.
- Its relevant shared interfaces and types.
- A human-owned functional task.
- Representative examples and permitted implementation scope.
- A fixed implementation entrypoint or template.
- Allowed dependencies and tool policies.
- An isolated candidate workspace.

Acceptance tests and authoritative specifications must remain outside the candidate's control.

Task metadata, agent instructions, execution evidence, and workspace configuration remain separate from the formal Box specification.

A Box contract is not a complete implementation brief.

### 6.2 Independent verification

Verification must not depend on the implementer's own claims.

A verifier should consume the approved specification, selected candidate, fixed inputs, and trusted tests.

It should distinguish:

1. Invalid inputs.
2. Candidate execution failures.
3. Invalid output types.
4. Postcondition failures.
5. Behavioral acceptance failures.
6. Integration failures.
7. Unverified properties.

The verification process must produce evidence that identifies the exact candidate and approved inputs evaluated.

A changed candidate, contract, task, or test invalidates affected previous acceptance evidence.

### 6.3 Integration

The integrator must use approved interfaces and pre-established wiring.

It must not silently repair candidate implementations to make them compatible.

If integration fails, the responsible implementation should return for revision, or an architectural change should be proposed.

Successful integration means the independently implemented Boxes work together under the approved contracts and tested behavior.

## 7. Readability as a product requirement

BoundScript must support two distinct forms of comprehension.

### 7.1 Architectural comprehension

A human should be able to inspect the approved system specification and understand:

- Which Boxes exist.
- Their responsibilities.
- Their public contracts.
- Their declared dependencies.
- Their relationships.
- Their relevant restrictions.

This should not require reading implementation source code.

### 7.2 Implementation comprehension

A human should be able to inspect the implementation evidence for a Box and understand:

- Which approved responsibility was implemented.
- Which candidate revision was evaluated.
- Which contract and task versions were used.
- Which checks passed or failed.
- Which behavior was exercised.
- Which important properties remain unverified.

An agent-generated implementation summary may assist comprehension, but it is not verification evidence.

BoundScript should not claim to fully describe arbitrary implementation behavior without inspecting or verifying that behavior.

The goal is **bounded, evidence-backed understanding**, not automatic proof of complete semantic equivalence between specification and implementation.

## 8. Controlled architectural evolution

The architecture must be able to evolve.

An Architect or implementer may discover that a Box is too complex, contains unrelated responsibilities, or requires a new dependency.

For example, an implementer may propose splitting one Box into two.

The change workflow is:

1. Produce an architectural change proposal.
2. Explain the reason and expected benefit.
3. Provide the proposed BoundScript source diff.
4. Identify affected Boxes, tasks, contracts, and tests.
5. Obtain approval.
6. Apply and validate the new architecture.
7. Regenerate affected implementation handoffs.
8. Reverify affected candidates and integration.

Private implementation refactoring does not require architectural approval if it remains within the approved boundary.

Initially, human approval is mandatory for changes to public architecture.

Automated approval policies may be investigated later, but must not be assumed.

The first architectural-evolution experiment should be performed manually or with existing LLM tools. It does not require a general-purpose autonomous planner.

## 9. Relationship to the existing implementation

The roadmap must build on the existing BoundScript codebase rather than replace it prematurely.

Preserve:

- Langium grammar, typed AST, and diagnostics.
- Existing primitive and flat-record types.
- Supported `ensure` predicates.
- `extractBoxDevelopmentSpec`.
- Strict JSON codec and `bound spec`.
- Shared declaration-lowering semantics.
- Existing compiler, executable artifact, and runtime.
- Runtime `director` and host bindings.
- Existing tests and regression examples.

Recognize current limitations:

- A system currently requires a runtime `director`.
- Boxes currently expose one operation.
- Types are limited.
- Dependencies and capabilities are not yet formal DSL declarations.
- Runtime checks are not yet exposed as a standalone verifier.
- There is no agent runner or candidate promotion mechanism.
- Existing sandbox policy types do not enforce isolation.

Do not describe planned capabilities as implemented features.

The compiler/runtime remains a valid execution backend, but should not be mandatory for every future Box implementation workflow.

Any change to formal specification semantics must be versioned and compatible with existing consumers.

## 10. Isolation and security

Development isolation and production isolation are separate concerns.

The first experiments may use disposable containers or equivalent restricted environments.

A development sandbox should restrict:

- Writable paths.
- Accessible task context.
- Network access.
- Available credentials.
- Process privileges.
- Resource consumption.
- Execution time.

The controller, protected specifications, acceptance tests, and credentials must remain outside the candidate's writable or accessible trust boundary as appropriate.

Git worktrees and separate directories provide organization, not security isolation.

A Node subprocess alone is not a security boundary.

Do not execute untrusted generated code inside the trusted development process.

Production isolation is not a prerequisite for the initial pilot.

A Box implemented in a restricted development environment and subsequently imported into an ordinary Node.js application inherits that application's execution privileges.

The initial objective is controlled development and verification, not a distributed production sandbox platform.

## 11. Revised roadmap

### M0 — Approve the product thesis

**Deliverable:** Approved architectural direction, role definitions, guarantees, non-guarantees, and pilot scope.

Define the baseline against conventional TypeScript interfaces and existing coding tools.

**Exit gate:** The team agrees that success means reduced coordination and understandable, verifiable boundaries—not additional DSL features or agent count.

### M1 — Standalone contract verification

**Deliverable:** A minimal verifier consuming existing portable Box specifications and trusted fixture implementations without requiring an executable director or source AST.

Reuse existing runtime validation semantics.

**Exit gate:** Valid cases pass; invalid inputs, execution failures, output failures, and postcondition failures are distinguishable. Existing examples remain compatible.

### M2 — Deterministic task derivation

**Deliverable:** Generate consistent per-Box handoff packages from approved BoundScript specifications and external functional tasks.

Use the existing spec format and a fixed TypeScript entrypoint. Introduce no general task language.

**Exit gate:** Repeated derivation from identical approved inputs produces equivalent tasks, with no manually duplicated public interfaces.

### M3 — Independent implementation pilot

**Deliverable:** Two independently implemented Boxes using separate agent contexts and a controlled development environment.

Suggested initial scenario: `NormalizeContact` and `RenderWelcome`, using existing supported types.

**Exit gate:** Both candidates pass independent checks and integrate using prewritten wiring without implementation edits or agent-to-agent negotiation.

Record interventions, revisions, failures, and coordination costs.

### M4 — Integration and evidence

**Deliverable:** A repeatable verification and integration workflow with human-readable reports.

Reports connect requirements, approved contracts, candidate revisions, tests, and observed outcomes.

**Exit gate:** A fresh run reproduces the relevant checks; unauthorized modifications and stale evidence prevent promotion. A human can inspect the architecture and understand the scope of verified implementation behavior.

### M5 — Architectural evolution experiment

**Deliverable:** An Architect proposes a meaningful change to an existing Box decomposition.

The change includes a rationale, source diff, impact assessment, and affected task/test updates.

**Exit gate:** The approved change can be applied, affected handoffs regenerated, and implementations reverified without silent changes to the active architecture.

No generalized planner is required.

### M6 — Comparative evaluation

**Deliverable:** Repeat the pilot using plain TypeScript interfaces, Markdown tasks, tests, and existing coding agents.

Compare both workflows using the same functional requirements and comparable tooling.

**Exit gate:** A documented decision identifies whether BoundScript reduces coordination, boundary drift, context requirements, or comprehension costs sufficiently to justify its complexity.

Possible outcomes include continuing, narrowing the DSL, reusing existing IDL technologies, or stopping the project.

The roadmap does not assume a positive result.

## 12. Explicit non-goals

The following are not prerequisites for this roadmap:

- A general-purpose programming language.
- A universal intermediate representation.
- A theorem prover.
- A new agent framework.
- A distributed task scheduler.
- A provider-specific agent integration.
- A production container per Box.
- A microservice architecture.
- A generalized capability-security language.
- A new runtime orchestration engine.
- An autonomous architecture approval system.
- A full architectural visualization platform.

Research into WIT, effect systems, formal contracts, and other existing approaches may inform later decisions, but does not authorize replacing current infrastructure.

Do not add language features without evidence that the development workflow requires them.

## 13. Immediate implementation recommendation

Begin with **M1: a standalone verifier for existing Box contracts**, using trusted fixtures and existing validation semantics.

In parallel, define the M3 pilot's functional tasks and conventional TypeScript baseline before building additional infrastructure.

The first meaningful end-to-end experiment should demonstrate:

1. A human-readable approved architecture.
2. Deterministically derived implementation contexts.
3. Two independent agent implementations.
4. Integration without manual interface negotiation.
5. Evidence-backed understanding of what was checked.
6. A comparison against conventional tooling.

Only then should the project prioritize additional DSL semantics, automated architectural planning, or advanced agent orchestration.

---

## Final principle

**BoundScript does not make probabilistic code generation deterministic. It makes the boundaries, contracts, and acceptance process governing that generation explicit and reproducible.**

The Architect proposes.  
The human approves.  
The agents implement.  
BoundScript defines and validates the boundaries.  
The verifier produces evidence.  
The integrator promotes accepted implementations.

The ultimate goal is to allow humans to govern the architecture of a software system without having to manually coordinate every step of its construction.