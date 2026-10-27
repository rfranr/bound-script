# Experiment — Native TypeScript Contracts

State: InReview

We want to evaluate whether BoundScript can achieve its original goals without maintaining a custom DSL.

Start from `experiment/boundscript-next`, preferably in a dedicated experiment branch.

The existing autonomous two-box experiment and Docker/Podman isolation are our baseline. Preserve them.

## Objective

Replace the manually maintained contract definitions in the minimal-box experiment with native TypeScript contracts, using:

- TypeScript for Box interfaces and types.
- Typia for runtime input/output validation.
- Vitest + fast-check for independent behavioral and property-based tests.
- Pi for autonomous implementation generation.
- Docker/Podman for isolation.

Functional intent remains in external Markdown files (`task.md`).

## First phase — Feasibility spike

Use `NormalizeContact` as the first candidate.

1. Define its contract using native TypeScript interfaces and types.
2. Configure Typia and demonstrate runtime validation without duplicating schemas.
3. Preserve the natural-language task as a separate Markdown file.
4. Add independent Vitest tests and fast-check properties.
5. Reuse the existing generation, isolation and verification mechanisms.
6. Ensure the agent cannot modify the authoritative contracts or acceptance tests.
7. Run the existing acceptance cases and compare results with the baseline.

Do not migrate `RenderWelcome` or change the overall architecture yet.

## Constraints

- No custom DSL or compiler.
- No Zod or duplicate schema definitions.
- No weakening of sandbox restrictions.
- No manual repair of generated implementations.
- Do not change frozen baseline assets.
- Do not commit automatically.
- Document configuration changes and limitations.

## Acceptance criteria

Demonstrate that an independently generated TypeScript implementation can be validated through Typia and Vitest/fast-check while respecting the original isolation and promotion guarantees.

Report what worked, what failed, and whether this approach can replace the custom DSL without losing important capabilities.