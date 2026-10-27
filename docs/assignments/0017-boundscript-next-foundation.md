We have made an architectural decision for BoundScript Next.

**BoundScript is not a programming language or an application orchestrator. It is a tool for enforcing human-defined architectural boundaries during agent-driven software development.**

## Core principles

- Humans define Boxes, their public contracts, authorized dependencies, and capabilities.
- Agents implement Boxes using ordinary programming languages and existing tooling.
- A Box may represent a function, library, service, React component, or even an entire application.
- An application can itself be a Box that consumes other Boxes.
- Agents may read their own task and contract, plus the public contracts of authorized dependencies.
- Agents cannot modify contracts, dependency declarations, acceptance tests, or other Boxes.
- BoundScript independently verifies submissions and integrates accepted artifacts.
- Application logic, dependency wiring, and orchestration belong in ordinary application code, not in a BoundScript DSL.

**BoundScript controls boundaries, not business logic.**

## Your task: simplify the codebase

Work exclusively on `experiment/boundscript-next`.

The original implementation remains preserved on `feature/agent-driven-architecture`.

Clean up the experimental branch and establish a minimal codebase skeleton for this architecture.

Remove obsolete DSL-specific machinery from the new branch where appropriate:
- Langium grammar and generated language infrastructure.
- Custom compiler and interpreter.
- Director DSL and execution machinery.
- DSL-specific artifact and contract transformations.
- Obsolete examples, tests, and documentation.

Preserve or adapt genuinely reusable capabilities:
- Isolated agent execution.
- Native-language contracts.
- Explicit dependency boundaries.
- Independent verification.
- Controlled artifact promotion.
- Existing Docker/Pi experiment as a working reference.

## Keep the architecture minimal

Aim for a small, understandable separation of responsibilities:

1. **Box definition:** task, public contract, authorized dependencies and capabilities.
2. **Agent execution:** isolated workspace with restricted filesystem authority.
3. **Verification:** independent checks of the candidate against its contract and acceptance criteria.
4. **Artifact integration:** make verified Box artifacts available to authorized consumers.

These are responsibilities, not necessarily four packages. Do not create packages or abstractions unless they are justified by working code.

Avoid introducing a new DSL, generic plugin system, custom runtime, elaborate manifests, or speculative support for multiple languages.

Use TypeScript as the initial supported language. Design for other languages conceptually, but don't implement them yet.

## Deliverables

- A clean, minimal repository structure.
- The existing one-Box experiment still working.
- A short README explaining the new architecture and how to run the experiment.
- A clear description of what was removed, retained, and deliberately deferred.

Do not implement the two-Box experiment yet. That will be our next step, once the skeleton is understandable.

You may remove obsolete code **on the experimental branch only**. Do not merge into or modify the original branch.

Make small, reviewable commits. Run the relevant checks and report the results.

**Most importantly: simplify aggressively. We are reducing the architecture, not replacing one complex system with another.**
