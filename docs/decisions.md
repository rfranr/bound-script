# Design decisions

The initial record below is preserved as historical context. The appended [Proposal 0013 decision](#accepted-direction--proposal-0013) governs the current product direction and explicitly qualifies earlier assumptions; historical intentions are not claims of implemented capabilities.

## Initial agreed direction

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
12. **Use Langium as the language frontend.** The grammar is the source of truth for parser and AST generation. Core services are used without an LSP host so editor integration can be added later without coupling it to compilation.
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
- **Generated language sources:** Langium removes handwritten parsing code and prepares future LSP support, but adds a required generation step and framework dependency. Generated files remain ignored and reproducible from the committed grammar.
- **No embedded implementation code:** keeps blueprints readable and preserves isolation, at the cost of managing separate box artifacts.
- **No concrete sandbox:** avoids a premature Docker/WebAssembly/process choice, but means security claims are not yet implemented.

## Accepted direction — Proposal 0013

**Reference:** [Proposal 0013 — Deterministic Architecture for Probabilistic Software Construction](proposals/0013-deterministic-architecture-for-probabilistic-construction.md) (accepted). This records a product-direction decision, not authorization to change grammar, public APIs, or runtime semantics.

### Why the focus changes

The initial language/runtime exploration establishes useful contracts and execution machinery, but more orchestration syntax or sandbox abstractions alone would not establish the product's value. The primary objective is now to reduce the human coordination needed to construct and evolve software with independent coding agents. Deterministic, readable specifications should bound probabilistic implementation choices and make acceptance evidence understandable.

This is a hypothesis to test against ordinary TypeScript interfaces, Markdown tasks, tests, and existing coding tools. The pilot must measure human interventions, interface renegotiations, integration modifications, boundary violations, context needs, comprehension, and workflow overhead. Successful integration alone is insufficient; narrowing or stopping the project remains a valid outcome if it adds no meaningful value.

### Authority and responsibilities

- **Humans** own intended behavior, acceptance criteria, trust/security policy, approval of public architecture, and final acceptance/promotion authority.
- **Architects**, human or LLM, propose decomposition, responsibilities, interfaces, dependencies, tasks, and changes. Proposals have no authority until approved. The build-time role is named Architect to distinguish it from the existing runtime `director`.
- **BoundScript** represents approved architectural boundaries. Its deterministic responsibilities are parsing, validation, supported type/contract resolution, portable canonical specs, and eventually consistent handoffs and checks for changes requiring approval. Only existing language validation, contract extraction, and codecs are implemented today; generalized boundary-change detection and task derivation are planned.
- **Implementers** choose internal algorithms and organization within approved boundaries and permitted tools. They receive external functional tasks as well as contracts. They may propose but not silently change public interfaces, shared types, dependencies, responsibilities, acceptance criteria, or protected policy.
- **Verifiers and integrators** independently check candidates against trusted specifications, inputs, and tests, report failures and unverified properties, and integrate with approved wiring without silently repairing candidates. The target workflow requires version-linked evidence and explicit promotion; this tooling is not implemented yet.

A Box is a unit of delegated responsibility, not inherently an isolated process, function, service, or deployment unit. Its boundary defines implementation freedom, not correctness. Functional intent must not be inferred from names or dependency declarations. Every claimed property must identify whether it is merely declared, statically checked, test-observed, runtime-enforced, or unverified. Finite tests do not prove universal semantic correctness.

### Existing decisions retained and qualified

- **Separation and determinism (1, 6–8, 12, 15) remain valid.** Preserve Langium, diagnostics, shared declaration-lowering semantics, the compiler/artifact/runtime boundary, the strict portable Box spec codec, and the CLI. Formal spec semantics require explicit version decisions compatible with existing consumers. Implementation tasks and evidence remain outside executable artifacts.
- **Hybrid execution and non-DAG workflows (2–3, 13–14) remain valid backend choices, not the product's mandatory construction path.** The runtime `director`, host bindings, and sequential versioned instruction format remain supported and are not renamed or replaced by the Architect. The language still requires a director per system, even for source extraction; exported Box specs omit it. Standalone verification should not require an executable director or source AST.
- **Implementation independence (4, 9) remains valid.** Build-time agents remain outside the compiler and runtime; runtime model-invoking agents remain optional future application behavior. The first pilot uses a fixed TypeScript entrypoint without making a particular agent framework, provider, or implementation language a universal requirement.
- **Sandbox enforcement (5) remains a valid security principle, not an implemented guarantee.** Current sandbox types express policy only. Trusted host functions run in-process with application privileges; runtime postconditions provide neither isolation nor rollback. Development isolation and production isolation are distinct.
- **Repository/tooling choices (10–11) remain unchanged.** npm workspaces, TypeScript references, explicit dependency install-script review, and reproducible ignored Langium output remain appropriate.
- **Historical simplifications and trade-offs remain history.** In particular, “Five packages now” describes an earlier snapshot, not today's layout: the repository currently has six packages including the CLI. It is not a reason to remove a package. No new speculative package structure is approved here.

### Keep generation outside deterministic compilation

LLM planning and implementation are probabilistic and may depend on tools, prompts, and external services. Mixing them into compilation would conflate proposals with approved inputs and undermine reproducible outputs. The compiler therefore continues to accept resolved inputs and explicit implementation IDs; it neither calls an LLM nor discovers, loads, or generates host code. Contract extraction likewise requires no implementation. Deterministic verification must use explicit, versioned inputs and rules; it cannot establish arbitrary semantic correctness.

The target handoff combines the canonical contract with a human-owned functional task, examples, fixed entrypoint, allowed tools/dependencies, and a controlled candidate workspace. These are separate from the formal specification. Acceptance tests and authoritative inputs remain outside candidate control. A changed candidate, contract, task, or test invalidates affected acceptance evidence.

### Defer production isolation and generalized orchestration

The initial question is whether bounded tasks let independently produced implementations integrate with less human coordination. Sequential experiments with existing tools and repository scripts can test that; an agent framework, distributed scheduler, autonomous approval system, new runtime engine, or production container per Box would add complexity without first proving the hypothesis.

Development isolation still matters when executing untrusted generated code. Disposable containers or equivalent restricted environments must protect paths, context, credentials, network access, privileges, resources, and time as appropriate. Git worktrees and directories are not security boundaries, nor is a Node subprocess alone. Untrusted generated code must not run inside the trusted development process. A subsequently imported Box inherits its application's production privileges; development isolation does not imply production isolation.

### Roadmap and remaining questions

The next implementation recommendation is standalone verification using existing portable specs, trusted fixtures, and runtime validation semantics. Task derivation and a two-Box pilot follow, then repeatable integration/evidence, a manually approved architectural-evolution experiment, and comparative evaluation. No new syntax or infrastructure is justified merely by this direction decision.

[Open questions](open-questions.md) and the [runtime use cases](use-cases/README.md) predate this decision and are retained, not silently rewritten. Read them with these explicit resolutions:

- Delegation authority: initial public architectural changes require human approval; private refactoring inside boundaries does not.
- Isolation: controlled development comes first; production isolation is not a pilot prerequisite.
- Portability: the initial handoff uses TypeScript; broader multi-language support is not required for the pilot.
- Success criteria: reduced coordination and evidence-backed comprehension, measured against conventional tooling, replace an open-ended search for a success metric.
- Terminology: Architect is the build-time role; runtime `director` is unchanged. Boxes do not imply deployment isolation. Runtime control flow, modules, and capability isolation remain explored targets, not the immediate implementation order. The historical question about adding calls to the artifact profile is partly overtaken by existing sequential invocations; richer error/control-flow semantics remain open.

Still unresolved are the concrete verifier API and diagnostics, task/evidence formats and identity/invalidation mechanisms, pilot workspace enforcement and promotion controls, representation and checking of future dependency/responsibility constraints, and the practical comparative baseline. State ownership, richer runtime control flow, runtime-agent semantics, and artifact integrity mechanisms remain deferred design questions. Whether the product's benefits justify its complexity remains an experimental question, not an accepted guarantee.
