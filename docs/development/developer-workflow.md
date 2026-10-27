# Development Workflow — BoundScript

This document defines the development workflow, roles, responsibilities, authorization rules and traceability practices for BoundScript.

Agent-specific operational instructions are defined in `AGENTS.md`.

## 1. Roles

### Product Owner

- Defines requirements, scope, constraints and acceptance criteria.
- Owns product requirements and architectural decisions.
- Authorizes development work.
- Reviews and accepts or rejects deliveries.
- Authorizes publishing changes to remote repositories.

### Developer

- Registers development assignments when necessary.
- Implements authorized work.
- Makes technical implementation decisions within the authorized scope.
- Runs relevant checks and tests.
- Prepares or creates focused commits when authorized.
- Reports implementation results, deviations and limitations.

### Reviewer

- Inspects implementations, architecture and tests.
- Evaluates deliveries against the original assignment.
- Records actionable feedback.
- Verifies whether acceptance criteria have been satisfied.
- Recommends acceptance or requests corrections.

Roles may be performed by different contributors, including automated development tools.

A contributor may perform multiple roles, but performing the Developer role does not implicitly grant Product Owner approval authority.

## 2. Assignment Workflow

The Product Owner defines and owns the assignment's requirements, scope, constraints and acceptance criteria.

An assignment may be created directly by the Product Owner or registered administratively by the Developer on their behalf.

Assignment documents are stored at:

`docs/assignments/NNNN-description.md`

Each assignment should contain:

- Identifier and title.
- Status.
- Goals.
- Requirements.
- Constraints.
- Acceptance criteria.
- Relevant implementation and verification references, when available.

The Product Owner owns the requirements. Developers must not silently introduce, remove or modify requirements or acceptance criteria.

### Automatic Assignment Registration

Every authorized development task must have a persistent assignment before implementation begins.

When a Developer receives a development request through chat or another direct instruction:

1. Check whether the request references an existing assignment.
2. If an existing assignment applies, use it rather than creating a duplicate.
3. Otherwise, create a new document under `docs/assignments/`, using the next available identifier.
4. Preserve the human-provided objectives, requirements, constraints and acceptance criteria.
5. Clearly distinguish explicit requirements from assumptions or unresolved questions.
6. Record the appropriate assignment status.
7. Persist the assignment before modifying implementation code.
8. Reference its identifier in subsequent implementation reports and associated commits.

Creating an assignment document is an administrative action and does not require separate approval when development has already been explicitly authorized.

An agent must not invent requirements or treat its own interpretation as an approved Product Owner decision.

If an instruction contains unresolved decisions that materially affect scope, architecture or acceptance criteria, register the assignment as `Proposed` and request clarification before implementing the affected work.

If the Product Owner explicitly requests analysis without file modifications, no automatic assignment file should be created unless separately authorized.

Direct chat instructions are valid development instructions. Once registered, the assignment becomes the persistent record of their authorized scope.

Historical conversations may provide context but do not independently authorize new work.

### Assignment States

Assignments use the following states:

| Status | Meaning |
|---|---|
| `Proposed` | Requirements or authorization are incomplete; implementation has not been authorized. |
| `In Progress` | The Product Owner has explicitly authorized implementation within the recorded scope. |
| `In Review` | An implementation has been delivered for review or acceptance. |
| `Completed` | The Product Owner has explicitly accepted the implementation. |

An explicit instruction to implement constitutes authorization to begin work within the stated scope.

It does not constitute acceptance of the resulting implementation.

A Developer may update an assignment's administrative status to reflect an authorized action or an observable workflow transition.

Only the Product Owner may approve requirements, authorize scope changes or accept a delivery.

### Assignment Ownership and Updates

The assignment's requirements and acceptance criteria belong to the Product Owner.

Developers may update administrative information without separate approval when required by this workflow, including:

- Initial registration of an explicitly authorized request.
- Implementation status.
- References to commits, tests and verification evidence.
- Delivery reports and unresolved issues.

Developers must not change the authoritative requirements, constraints or acceptance criteria without Product Owner authorization.

Corrections that materially change an assignment's meaning require approval.

Historical requirements should remain traceable when an authorized change is made.

## 3. Implementation Workflow

The Developer may receive either:

- A reference to an existing assignment.
- An explicit development request that must first be registered.

For example:

```text
Implement docs/assignments/0005-expand-boundscript-execution-tests.md
```

Or:

```text
Improve the independent verifier's diagnostic reporting.
Preserve sandbox security and do not commit.
```

In the second case, the Developer first registers the request as an assignment.

### Implementation Steps

The Developer:

1. Identifies or registers the assignment.
2. Reads the assignment and relevant project documentation.
3. Confirms that implementation is authorized.
4. Implements the requested functionality within scope.
5. Runs the relevant tests and checks.
6. Reviews the changes for unintended modifications or scope expansion.
7. Creates a focused local commit only when authorized.
8. Reports the outcome, verification results and unresolved issues.
9. Marks the assignment `In Review` when the implementation is ready for evaluation.

If commits are not authorized, the Developer leaves changes uncommitted and may propose a commit message.

Every implementation commit associated with an assignment must reference its identifier.

A successful implementation or passing test suite does not authorize the Developer to mark the assignment `Completed`.

### Scope and Technical Decisions

The Developer may independently choose implementation details within the approved scope.

Changes to architectural direction, product requirements or acceptance criteria require Product Owner approval.

If implementation reveals a missing requirement or material ambiguity, the Developer must report it rather than silently establishing a new requirement.

The Developer must not weaken tests or verification boundaries solely to obtain a successful result.

### Current native-contract development checks

The implemented architecture is described in [architecture.md](architecture.md);
proposals and historical assignments are not implemented requirements. Current
commands are in the [root README](../../README.md).

- Shared host-side mechanics belong in `boundscript_internal/`, with their tests
  in `tests/internal/`. Experiments import that private package, never each
  other's infrastructure. Keep verification rules, quarantine and promotion
  policy in the owning experiment; do not turn relocation into a generic API.
- Keep `task.md` (intent), native contract types (shape), independent tests
  (observed semantics) and candidate source separate. Requirement/acceptance
  changes need Product Owner authorization; never repair them to fit a candidate.
- Run `npm ci`, select `BOUNDSCRIPT_RUNTIME=podman` or `docker` explicitly, and
  cache the pinned image before container checks. `npm run check` runs Python
  units, Typia tooling and the complete saved baseline without model calls/auth.
  No Git branch name is a prerequisite; assertions and effective sandbox checks are.
- Build validators with `npm run build:native` before direct Python verification.
  Use `verify.py /absolute/path/candidate.ts` for a supplied native candidate;
  `npm run test:native` requires a local ignored accepted artifact. A clean
  checkout does not contain one. Never execute untrusted candidates on the host.
- `test:native:baseline` is an intentionally incompatible historical comparison
  after the required-phone contract evolution; report its failure separately
  from positive `npm test` regressions. Do not change baseline evidence to fit it.
- Generation is billable, mounts the explicitly authorized prototype auth file,
  and promotes on success. Use it intentionally, not as a prerequisite for unit
  tests. Mocked lifecycle tests do not establish real engine security. Run opt-in
  offline engine/negative tests as documented in the experiment guides.
- Preserve verify-before-promotion and native scanned-source quarantine. Standalone
  verification never promotes. Do not commit native generated validators, accepted
  sources, quarantine, auth, provider events or transcripts. Do not manually repair
  accepted generated sources; justify any strictly necessary baseline change.
- Before cleanup, inventory removals and retained behavioral/security evidence.
  Stop for human decisions if cleanup would lose baseline evidence or change
  architecture. Report exact test outcomes, skipped/unavailable checks, limitations
  and final diff; passing checks do not authorize acceptance or commits.

## 4. Code Review Workflow

The Reviewer evaluates the delivery against the assignment, its acceptance criteria and repository conventions.

When significant corrections or decisions need to be documented, the Reviewer creates:

`docs/reviews/NNNN-review-XX.md`

A review document should contain:

- Assignment identifier.
- Commit or implementation being reviewed.
- Findings and required corrections.
- Constraints on the corrections.
- Review status.

Not every minor review comment requires a separate document.

Reviews should be preserved when they contain significant corrections, architectural findings or decisions relevant to future work.

### Addressing Review Feedback

The Developer receives review feedback through a document reference or direct instruction.

Example:

```text
Resolve docs/reviews/0005-review-01.md
```

The Developer:

1. Reads the review feedback and original assignment.
2. Applies corrections within the existing authorized scope.
3. Registers a new assignment if the requested changes introduce new requirements or independent scope.
4. Runs relevant tests and checks.
5. Creates a separate correction commit when authorized.
6. Includes the review document in the commit when applicable.
7. Reports corrections and verification results.

Corrections remain associated with the original assignment when they do not introduce new requirements.

Review corrections must not rewrite previous commits without explicit authorization.

Review findings and recommendations do not constitute Product Owner acceptance.

## 5. Git Workflow

An assignment may generate multiple commits, including implementation and subsequent review corrections.

Example:

```text
Assignment 0005
    |
    +-- Initial implementation
    |     test(language): add conformance fixtures
    |
    +-- Review 01
          |
          +-- Correction
                fix(test): await runtime execution
```

Each artifact has a distinct responsibility:

- **Assignment:** Records what was requested and authorized.
- **Commit:** Records what was implemented and why.
- **Review:** Records findings and required corrections.
- **Acceptance record:** Records the Product Owner's decision.

### Commit Authorization

Local commits and remote publication are separate actions.

- Developers may create local commits when explicitly authorized by the Product Owner or the active task instructions.
- When the task specifies `Do not commit`, all changes must remain uncommitted.
- Developers must not amend, squash, rebase or otherwise rewrite existing commits without authorization.
- Pushing changes to remote repositories always requires explicit Product Owner authorization.

Authorization to implement does not automatically authorize committing or pushing.

### Commit Conventions

Commits follow Conventional Commits and include a descriptive body explaining meaningful changes and their rationale.

Commits associated with assignments must contain traceability metadata.

Example:

```text
test(language): add BoundScript conformance fixtures

- Add valid and invalid language fixtures.
- Verify escaped strings and statement execution order.
- Cover syntax errors and deterministic compilation.

Establishes a reusable conformance baseline for future
language extensions.

Assignment: 0005
AI-Tool: pi
AI-Model: gpt-5.6-luna
AI-Reasoning: low
```

AI-specific metadata applies when AI tooling contributes to an implementation.

Metadata must reflect actual usage and must not be fabricated.

The detailed commit conventions and repository safety restrictions for AI agents are defined in `AGENTS.md`.

## 6. Acceptance Workflow

An assignment is not automatically accepted when implementation finishes, tests pass, a review is positive or a commit is created.

The Product Owner evaluates the delivery against the original requirements and acceptance criteria, considering available review findings and verification evidence.

Possible outcomes:

- **Accepted:** The delivery satisfies the assignment.
- **Changes requested:** Corrections are needed within the existing scope.
- **Rejected:** The delivery is not accepted.
- **New assignment:** Additional requirements or independent scope have been identified.

The Product Owner decides whether to request corrections, revert changes or abandon rejected work.

### Recording Acceptance

Acceptance is an explicit Product Owner decision.

Once the Product Owner communicates a decision:

1. The Developer may record that decision in the assignment document.
2. The acceptance record must identify the decision, approving role, reviewed implementation commit when available, and supporting verification evidence.
3. An assignment may be marked `Completed` only after explicit Product Owner acceptance.
4. A roadmap milestone may be marked `Completed` only when its own criteria have been verified and the Product Owner has authorized closure.
5. Documentation updates may be committed or pushed only when the applicable Git authorization has been granted.

Recording a communicated approval is an administrative action, not an approval decision.

Developers must not independently accept their own deliveries or close milestones on behalf of the Product Owner.

## 7. Governance

The following rules apply throughout the development process:

- The Product Owner retains authority over requirements, scope, architectural direction and acceptance decisions.
- Developers may register assignments administratively but do not thereby acquire ownership of requirements.
- Explicit implementation instructions authorize work within their stated scope, not acceptance of the result.
- Material requirement or scope changes require Product Owner authorization.
- Administrative status updates and evidence recording must accurately reflect actual decisions and results.
- Historical conversations are reference material, not independent authorization for new work.
- Technical implementation decisions may be delegated within the authorized scope.
- Reviewer recommendations do not substitute for Product Owner acceptance.
- Local commits require authorization; remote publication always requires explicit authorization.
- Existing security, isolation and verification guarantees must not be weakened without an explicit, informed architectural decision.
- Traceability records must distinguish original requirements, implementation results, review findings and acceptance decisions.

## 8. Traceability Principle

BoundScript development follows this lifecycle:

```text
Human development request
          |
          v
Assignment registration
          |
          v
Authorized implementation
          |
          v
Tests and verification
          |
          v
Delivery / In Review
          |
          v
Review and human decision
          |
          +-- Changes requested --> Corrections --> Review
          |
          +-- Rejected
          |
          +-- Accepted --> Completed
```

The assignment must exist before implementation, even when the original request was delivered through chat.

The objective is to preserve a verifiable relationship between human intent, delegated implementation, independent review and the resulting software history, without introducing unnecessary approval steps.