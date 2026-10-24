# Initial design decisions

## Agreed direction

1. **Separate language, compilation, runtime, and sandbox concerns.** They evolve at different rates and have different trust boundaries.
2. **Use a hybrid model.** Structure, contracts, and capabilities are declarative; directors may express explicit imperative control flow.
3. **Do not force workflows into DAGs.** Branching, retries, loops, errors, and stateful coordination may be legitimate language concepts.
4. **Keep boxes implementation-agnostic.** Contracts should not require a specific implementation language, LLM provider, or agent framework.
5. **Treat sandboxing as enforcement.** Prompts, manifests, and TypeScript types can describe limits but cannot enforce them.
6. **Keep compilation deterministic.** AI-assisted implementation generation is a separate pipeline, not part of parsing or compilation.
7. **Start as a TypeScript monorepo.** npm workspaces and TypeScript project references provide enough isolation without extra build tooling.
8. **Review dependency install scripts explicitly.** npm's install-script protection remains enabled. Any future approval must be package- and version-specific rather than globally disabling the policy.

## Trade-offs

- **Four packages now:** clearer boundaries, with small workspace overhead. An agent/CLI package is deferred.
- **Interfaces before implementations:** enables parallel design, but some types will change once semantics are validated.
- **Custom DSL remains likely, not decided:** it best matches the desired readability, but parser technology such as Langium is not yet adopted.
- **No embedded implementation code:** keeps blueprints readable and preserves isolation, at the cost of managing separate box artifacts.
- **No concrete sandbox:** avoids a premature Docker/WebAssembly/process choice, but means security claims are not yet implemented.
