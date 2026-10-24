# Initial design decisions

## Agreed direction

1. **Separate language, artifact, compilation, runtime, and sandbox concerns.** They evolve at different rates and have different trust boundaries.
2. **Use a hybrid model.** Structure, contracts, and capabilities are declarative; directors may express explicit imperative control flow.
3. **Do not force workflows into DAGs.** Branching, retries, loops, errors, and stateful coordination may be legitimate language concepts.
4. **Keep boxes implementation-agnostic.** Contracts should not require a specific implementation language, LLM provider, or agent framework.
5. **Treat sandboxing as enforcement.** Prompts, manifests, and TypeScript types can describe limits but cannot enforce them.
6. **Keep compilation deterministic.** A compiler receives a fully resolved input and never invokes an AI model or build-time agent.
7. **Use one shared executable-artifact contract.** Compiler output and runtime input are the same `ExecutableArtifact` type from `@boundscript/artifact`; parallel `CompilationArtifact` and `RuntimeArtifact` types were removed.
8. **Keep the initial artifact envelope small.** It carries versioned entrypoints and byte assets, not arbitrary metadata or build-process details.
9. **Distinguish build-time and runtime agents.** Build-time agents generate implementations before compilation. Runtime agents, if later supported, are explicit application components governed by runtime contracts and capabilities.
10. **Start as a TypeScript monorepo.** npm workspaces and TypeScript project references provide enough isolation without extra build tooling.
11. **Review dependency install scripts explicitly.** npm's install-script protection remains enabled. Any future approval must be package- and version-specific rather than globally disabling the policy.
12. **Start with a hand-written parser.** The first grammar is small enough that adding parser infrastructure would cost more than it provides. Parser tooling can be reconsidered when the language expands.
13. **Compile to a versioned instruction asset.** The first runtime profile uses deterministic JSON with sequential `print` instructions, keeping the runtime independent from the source AST.
14. **Treat `print` as a temporary built-in.** It writes through an injected runtime sink and makes no sandbox or capability-security claim.
15. **Keep the CLI as composition only.** It loads source and connects language, compiler, artifact, and runtime packages without interpreting the program itself.

## Simplifications made

- Removed duplicate compiler/runtime artifact representations.
- Replaced optional compilation artifacts with a discriminated success/failure result.
- Removed arbitrary artifact metadata until a concrete use case exists.
- Removed runtime events, correlation context, and optional entrypoint selection until runtime semantics require them.
- Removed process-command sandbox execution interfaces; the sandbox package currently defines policy only.
- Removed speculative CPU-unit limits while retaining portable timeout and memory limits.

## Trade-offs

- **Five packages now:** the artifact package adds a workspace boundary, but prevents compiler/runtime coupling and schema drift.
- **Interfaces before implementations:** enables parallel design, but some types will change once semantics are validated.
- **Byte-oriented assets:** support text and binary implementations uniformly, at the cost of requiring explicit encoding outside the contract.
- **Opaque targets and media types:** avoid committing to JavaScript modules or another execution technology, but defer validation details to future runtime profiles.
- **Custom DSL remains likely, not decided:** it best matches the desired readability, but parser technology such as Langium is not yet adopted.
- **No embedded implementation code:** keeps blueprints readable and preserves isolation, at the cost of managing separate box artifacts.
- **No concrete sandbox:** avoids a premature Docker/WebAssembly/process choice, but means security claims are not yet implemented.
