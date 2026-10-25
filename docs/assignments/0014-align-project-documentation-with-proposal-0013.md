# Assignment 0014 — Align Project Documentation with Proposal 0013

**Status:** Proposed  
**Parent:** Proposal 0013  
**Scope:** Documentation only

## Objective

Align the project's primary documentation with the new product direction established in Proposal 0013: deterministic architectural boundaries for independently delegated, probabilistic software construction.

The purpose is to establish a coherent product vision before implementing the new roadmap.

## Required changes

### README.md

Update the project introduction to explain:

- The problem BoundScript aims to solve.
- The separation between deterministic architectural specifications and probabilistic agent implementations.
- The roles of humans, Architects, implementers, and verifiers.
- The distinction between current capabilities and planned capabilities.

Preserve accurate installation, CLI, examples, and usage instructions.

### architecture.md

Describe the target conceptual architecture and its relationship to the existing implementation.

Clearly distinguish:

- Build-time architecture planning.
- BoundScript parsing and contract extraction.
- Independent implementation.
- Verification and integration.
- Existing compiler, artifact, runtime, and runtime `director`.

Do not present planned components as implemented modules.

### decisions.md

Record the approved architectural direction and its rationale.

Document:

- Why the product focus is changing.
- Which existing decisions remain valid.
- Which responsibilities belong to BoundScript versus agents.
- Why implementation generation is kept outside deterministic compilation.
- Why production isolation and agent orchestration are not immediate requirements.

Preserve the historical decision record. Do not silently rewrite past decisions.

## Constraints

- Documentation changes only.
- No changes to grammar, compiler, runtime, public APIs, or tests.
- Do not invent capabilities.
- Do not rename the existing runtime `director`.
- Do not introduce speculative package structures.
- Use Proposal 0013 as the product-direction reference.
- Resolve inconsistencies explicitly rather than deleting historical context.

## Deliverables

1. Updated `README.md`, `architecture.md`, and `decisions.md`.
2. A concise summary of the changes.
3. A list of remaining inconsistencies or unresolved architectural questions.

## Acceptance criteria

A developer unfamiliar with BoundScript should be able to understand:

- What BoundScript currently implements.
- What the project ultimately aims to achieve.
- Why the deterministic layer exists.
- What responsibilities are delegated to agents.
- What is planned but not yet implemented.

All existing technical documentation must remain accurate.