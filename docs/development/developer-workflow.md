# Development Workflow — BoundScript

This document defines how BoundScript development work is assigned, implemented, reviewed and accepted. Agent-specific operational instructions belong in `AGENTS.md`.

## 1. Roles

**Product Owner**
- Defines and owns requirements, scope, acceptance criteria and architectural decisions.
- Authorizes development, local commits and remote publication.
- Accepts or rejects deliveries.

**Developer**
- Registers assignments when needed and implements authorized work.
- Makes technical decisions within scope, runs checks and reports results.
- Commits only when authorized.

**Reviewer**
- Reviews changes against the assignment and reports findings or corrections.
- Recommends acceptance; does not grant it.

Roles may be performed by humans or agents. Developer or Reviewer responsibilities do not confer Product Owner authority.

## 2. Assignments

Every authorized development task must be recorded before implementation in `docs/assignments/NNNN-description.md`.

An assignment captures the human-defined goals, requirements, constraints and acceptance criteria.

### Automatic registration

When receiving a development request, the Developer:

1. Uses the referenced assignment if one exists; otherwise creates one with the next available identifier.
2. Records the human instructions faithfully, distinguishing requirements from assumptions. Do not invent or silently alter requirements.
3. Saves the assignment **before changing implementation code**.
4. References its identifier in reports and associated commits.

An explicit request to implement authorizes assignment registration and work within the stated scope; it does **not** authorize changing requirements, committing, pushing or accepting the result.

If a material requirement or architectural decision remains unresolved, record `Proposed` and seek a decision before implementing the affected work. If the human explicitly prohibits file changes, do not create an assignment file.

| Status | Meaning |
|---|---|
| `Proposed` | Awaiting essential clarification or authorization |
| `In Progress` | Implementation authorized and underway |
| `In Review` | Delivered for review |
| `Completed` | Explicitly accepted by the Product Owner |

The Developer may register progress and evidence but must not independently change authoritative requirements or mark an assignment `Completed`.

## 3. Implementation

The Developer:

1. Reads or registers the assignment and relevant technical documentation.
2. Implements within the authorized scope, retaining independent verification and security boundaries.
3. Runs relevant tests and reports results, limitations and deviations.
4. Delivers changes for review and records `In Review`.

Technical implementation choices belong to the Developer within scope. Material changes to requirements, architecture or acceptance criteria require Product Owner authorization. Do not weaken tests to make an implementation pass.

Technical commands, experiment-specific checks and infrastructure requirements belong in `README.md`, `docs/development/architecture.md` and the relevant experiment guides—not in this workflow.

## 4. Review and corrections

The Reviewer assesses the delivery against the assignment. Significant findings may be saved to `docs/reviews/NNNN-review-XX.md`.

The Developer applies authorized corrections within the original scope and reruns relevant checks. New requirements require a new or explicitly updated assignment. Do not rewrite existing commits without authorization.

## 5. Git and traceability

Assignments record **what was requested**, commits **what changed and why**, and reviews **what needs correction**.

Commits use Conventional Commits, include a meaningful rationale and reference the assignment. When AI contributed, record actual tool, model and reasoning metadata as described in `AGENTS.md`; never fabricate it.

- Local commits require explicit authorization. `Do not commit` means leave changes uncommitted.
- Remote pushes always require explicit Product Owner authorization.
- Do not amend, reset, rebase or rewrite history without authorization.
- Keep reports and commit messages technically relevant; do not reproduce private conversations or informal human remarks.

## 6. Acceptance and governance

Passing tests, a positive review or a commit **does not** imply acceptance. Only the Product Owner may accept a delivery and authorize marking its assignment `Completed` or closing a roadmap milestone.

The Developer may record an explicit decision and its verification evidence, but may not make that decision on the Product Owner's behalf. Corrections stay with the original assignment unless they introduce new scope.

Direct human instructions can authorize current work; historical conversations are context, not independent authorization. Preserve traceability without exposing unnecessary personal or conversational detail.
