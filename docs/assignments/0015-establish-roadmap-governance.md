# Assignment 0015 — Establish Roadmap Governance

**Status:** Proposed  
**Parent:** Proposal 0013  
**Scope:** Documentation only

## Objective

Establish a single, maintainable roadmap for BoundScript following the acceptance of Proposal 0013.

The roadmap must become the authoritative reference for project execution: what we intend to achieve, what is currently in progress, what has been completed, and which assignments contribute to each milestone.

Proposal 0013 remains the authoritative record of the product-direction decision, not the operational tracker.

## Tasks

### 1. Create `docs/roadmap.md`

Extract and organize milestones M0–M6 from Section 11 of Proposal 0013:

- M0 — Approve the product thesis
- M1 — Standalone contract verification
- M2 — Deterministic task derivation
- M3 — Independent implementation pilot
- M4 — Integration and evidence
- M5 — Architectural evolution experiment
- M6 — Comparative evaluation

For each milestone, document:

- Objective
- Scope and expected deliverables
- Completion criteria
- Status
- Related assignments
- Dependencies, where relevant

Preserve the intent and ordering of Proposal 0013. Do not introduce new architectural commitments.

### 2. Establish milestone and assignment tracking

Use the following milestone statuses:

- `Planned`
- `In Progress`
- `Blocked`
- `Completed`
- `Cancelled`

Assignments retain their own independent status.

An assignment being completed does not automatically complete its parent milestone.

A milestone may contain multiple assignments, and assignments must retain their existing sequential numbering independently of milestone identifiers.

Do not mark milestones as completed without supporting evidence.

### 3. Establish documentation responsibilities

Document the following ownership rules:

| Document | Responsibility |
|---|---|
| `README.md` | Product introduction and current capabilities |
| `docs/architecture.md` | Current and target architecture |
| `docs/decisions.md` | Approved decisions and rationale |
| `docs/proposals/` | Historical proposals and product-direction decisions |
| `docs/roadmap.md` | Current execution plan and milestone status |
| `docs/assignments/` | Individual work definitions and acceptance criteria |
| `docs/reviews/` | Review outcomes and supporting evidence |

A roadmap update must not silently change an approved architectural decision.

Changes that affect approved architectural boundaries or product direction require a new proposal or explicit decision.

### 4. Link existing work

Identify existing assignments related to Proposal 0013 and reference them from the appropriate milestones.

In particular:

- Assignment 0014 concerns documentation alignment and belongs to M0.
- Assignment 0015 concerns roadmap governance and belongs to M0.

Check the repository before assigning statuses. Do not assume that a committed document proves that its assignment has been formally accepted.

Do not create future implementation assignments as part of this task.

### 5. Update navigation

Add a concise link to `docs/roadmap.md` from `README.md`.

Update references elsewhere only when necessary to avoid contradictory navigation or status information.

Keep Proposal 0013 intact as the historical decision document. Do not duplicate its full contents in the roadmap.

## Constraints

- Documentation changes only.
- No source code, grammar, compiler, runtime, API, or test modifications.
- No speculative packages or infrastructure.
- No new agent framework or project-management tooling.
- No automatic approval of architectural decisions.
- No invented completion evidence.
- Keep the roadmap concise, readable, and easy to maintain manually.

## Deliverables

1. `docs/roadmap.md`
2. Updated `README.md` navigation
3. `docs/assignments/0015-establish-roadmap-governance.md`
4. Summary of changes and any unresolved tracking inconsistencies

## Acceptance criteria

A contributor should be able to answer, by reading `docs/roadmap.md`:

1. What is the current milestone?
2. What must be achieved to complete it?
3. Which assignments contribute to it?
4. What has been completed, and what evidence supports that status?
5. What comes next?
6. Where are architectural decisions recorded?

The roadmap must be consistent with Proposal 0013 and the actual repository state.

## Execution instructions

Inspect the existing documentation before editing.

Implement only the documentation changes described above.

Run relevant documentation checks if available, and review the final diff for unrelated changes.

Do not commit or push automatically.

Return the changed-file list, a concise summary, and any decisions requiring human approval.