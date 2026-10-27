# Assignment 0018b — Richer Contact Domain

Before starting assignment 0019, extend the existing two-Box experiment with more substantial business logic.

The current implementations are too trivial to provide meaningful evidence about independent agent development.

## Goal

Demonstrate that independently generated Boxes can implement nontrivial behavior, respect native TypeScript contracts, and integrate without manual source repair.

We are not trying to force different code across runs. Identical correct implementations are acceptable.

## Scope

Keep the existing two-Box architecture:

- `NormalizeContact`
- `RenderWelcome`

### NormalizeContact

Extend its contract to support:

1. Name normalization: trim leading/trailing whitespace and collapse consecutive internal whitespace into a single space. Preserve case and Unicode characters.
2. Email normalization: trim surrounding whitespace and lowercase.
3. Validation: name and email are required; validate a deliberately simple, explicitly documented email format.
4. Accumulate multiple validation errors in deterministic order.
5. Return a discriminated union representing success or validation failure.
6. Never mutate the input object.

Define precise behavior for empty values, whitespace, Unicode, and invalid emails. Avoid ambiguous requirements.

### RenderWelcome

Adapt the public contract to consume the new NormalizeContact result.

- On success, produce the welcome message using normalized data.
- On failure, produce a deterministic error response.
- Call the injected NormalizeContact dependency exactly once.
- Do not duplicate its normalization or validation logic.

## Experiment requirements

1. Define and commit the human-owned contracts, tasks, integration code, and independent acceptance tests **before running Pi**.
2. Generate both Boxes using fresh, isolated Pi sessions.
3. Preserve the existing dependency visibility rules.
4. Verify each candidate independently.
5. Integrate the accepted implementations without modifying their generated source.
6. Test valid inputs, multiple simultaneous validation errors, Unicode, whitespace, and dependency behavior.
7. Run at least two fresh generations and compare their source hashes and behavior.

If implementations differ, report whether both satisfy the same contract.

If implementations are identical, report that fact without treating it as a failure.

## Constraints

Do not implement assignment 0019 or 0020.

Do not introduce a DSL, framework, generic runner, new dependencies, or additional Boxes.

Reuse the existing Docker/Pi experiment.

Keep the implementation proportional to the problem.

## Deliverables

- Updated contracts and acceptance tests.
- Two fresh, independently generated and verified Boxes.
- Passing end-to-end integration.
- A concise report comparing at least two generations, including source hashes, test results, and any manual intervention.
- Focused commits with the assignment reference.

**The objective is to test agent implementation freedom within fixed architectural boundaries, not to maximize code complexity.**