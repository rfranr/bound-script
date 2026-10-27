# BoundScript — Architectural Integration Review

We have two parallel development tracks in the same repository:

**Architecture branch:** `feature/agent-driven-architecture`

Contains the existing DSL, compiler, runtime, Box specification export, architecture proposals, roadmap and assignments.

**Experimental branch:** `experiment/boundscript-next`

Contains the independent Box implementation experiment using Pi, Docker/Podman isolation, native TypeScript contracts and independent acceptance verification.

The experimental branch intentionally removed the DSL. This was an authorized decision, not an accidental deletion.

## Objective

Study both branches and propose how to integrate the successful autonomous-agent experiment into the existing BoundScript architecture.

The intended direction is:

`BoundScript formal specification + natural-language task → autonomous Box implementation → independent verification → human acceptance`

We want the DSL to express formal architectural boundaries and contracts, while natural language expresses functional intent and business requirements.

**We do not want to turn the DSL into a prompt language.**

## Instructions

1. Inspect both branches, their histories, documentation and implementations.
2. Start from `feature/agent-driven-architecture`, not `main`.
3. Review the existing architecture proposal, roadmap and assignments 0018–0023 before suggesting new components.
4. Identify what can be reused from the Docker/Podman experiment and what should remain experimental.
5. Determine whether the existing Box specification and task derivation mechanisms already solve part of this integration.
6. Propose how formal contracts and external natural-language tasks should be linked without duplicating authoritative definitions.
7. Preserve independent Box development, isolated workspaces, external verification and human-controlled acceptance.

## Architectural constraints

- Preserve the existing DSL, compiler and runtime.
- Autonomous execution is the only mode in scope; pair programming is deferred.
- Do not introduce unnecessary abstractions or a generic orchestration framework.
- Do not weaken sandbox security or independent acceptance checks.
- Allow agents freedom over algorithms, internal implementation and technical decisions.
- Human-defined contracts and mandatory business requirements remain authoritative.
- Do not merge entire branches or reintroduce intentionally removed files indiscriminately.

## Deliverables

Provide an architectural review containing:

1. Current architecture and capabilities already implemented.
2. Relevant experimental components worth integrating.
3. Gaps between the two development tracks.
4. Proposed minimal integration design and module boundaries.
5. A sequence of small assignments with explicit acceptance criteria.
6. Risks, unresolved decisions and features that should remain deferred.

Prefer adapting existing components over introducing new frameworks.

**This is analysis only. Do not modify files, create branches, stage changes or commit. Wait for human architectural approval.**