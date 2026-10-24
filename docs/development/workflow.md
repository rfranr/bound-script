# Development Workflow — BoundScript

This document defines the development workflow, roles, responsibilities and traceability practices for BoundScript.

Agent-specific operational instructions are defined in `AGENTS.md`.

## 1. Roles

### Product Owner

- Defines assignments, scope, constraints and acceptance criteria.
- Owns requirements and architectural decisions.
- Reviews and accepts or rejects deliveries.
- Authorizes publishing changes to remote repositories.

### Developer

- Implements assigned work.
- Makes technical implementation decisions within the approved scope.
- Runs relevant checks and tests.
- Produces focused commits following the repository conventions.
- Reports implementation results, deviations and limitations.

### Reviewer

- Inspects implementation, architecture and tests.
- Evaluates deliveries against the original assignment.
- Records actionable feedback.
- Verifies whether acceptance criteria have been satisfied.
- Recommends acceptance or requests corrections.

Roles may be performed by different contributors, including automated development tools.

## 2. Assignment Workflow

The Product Owner creates an assignment:

`docs/assignments/NNNN-description.md`

An assignment should define:

- Goals
- Requirements
- Constraints
- Acceptance criteria

The assignment is owned by the Product Owner and must not be modified by the Developer without explicit authorization.

### Implementation

The Developer receives the assignment using a reference to its file.

Example:

```text
Implement docs/assignments/0005-expand-boundscript-execution-tests.md
```

The Developer:

1. Reads the assignment and relevant project documentation.
2. Implements the requested functionality within scope.
3. Runs the relevant tests and checks.
4. Creates a focused commit containing the implementation and the assignment file, if not already committed.
5. Reports the outcome, verification results and any unresolved issues.

Every implementation commit must reference the assignment identifier.

## 3. Code Review Workflow

The Reviewer evaluates the delivery against the assignment and repository conventions.

When corrections need to be documented, the Reviewer creates:

`docs/reviews/NNNN-review-XX.md`

A review document should contain:

- Assignment identifier.
- Commit or implementation being reviewed.
- Required corrections.
- Constraints on the corrections.
- Review status.

### Addressing Review Feedback

The Developer receives the review through a reference to its file.

Example:

```text
Resolve docs/reviews/0005-review-01.md
```

The Developer:

1. Reads the review feedback.
2. Applies the required corrections without expanding the original scope.
3. Runs the relevant tests and checks.
4. Creates a separate fix commit referencing the original assignment.
5. Includes the review document in the commit if not already committed.
6. Reports the corrections and verification results.

Review corrections must not rewrite previous commits without explicit authorization.

Not every minor review comment requires a separate document. Reviews should be preserved when they contain significant corrections or decisions.

## 4. Git Workflow

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

- **Assignment:** Describes what was requested.
- **Commit:** Describes what was implemented and why.
- **Review:** Describes what must be corrected or verified.

### Commit Conventions

Commits follow Conventional Commits and include a descriptive body explaining meaningful changes and their rationale.

Commits associated with an assignment must include traceability metadata.

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

AI-specific metadata applies when AI tooling contributes to an implementation. Metadata must reflect actual usage and must not be fabricated.

The detailed commit rules and repository safety restrictions are defined in `AGENTS.md` for AI coding agents.

## 5. Acceptance

An assignment is not automatically accepted when a commit is created.

The Product Owner evaluates the delivery, considering the Reviewer's findings and the original acceptance criteria.

Possible outcomes:

- **Accepted:** The implementation satisfies the assignment.
- **Changes requested:** Corrections are needed within the existing scope.
- **Rejected:** The implementation is not accepted.
- **New assignment:** Additional requirements or scope are identified.

Review corrections remain associated with the original assignment when they do not introduce new requirements.

Rejected implementations must not be considered accepted. The Product Owner decides whether to request corrections, revert the changes or abandon the assignment.

## 6. Governance

- The Product Owner retains authority over requirements, scope and acceptance decisions.
- Developers must not expand assignment scope without approval.
- Assignments and reviews must not be modified without authorization from their owners.
- Changes must not be pushed to remote repositories without explicit authorization.
- Historical conversations are reference material, not authoritative requirements.
- Technical decisions within the approved scope may be delegated to the Developer.

The purpose of this workflow is to preserve traceability between requirements, implementation, review feedback and the resulting software history.