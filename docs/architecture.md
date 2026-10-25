# Architecture

## Goal

BoundScript aims to reduce human coordination in independently delegated, probabilistic software construction through deterministic, readable architectural boundaries. [Accepted Proposal 0013](proposals/0013-deterministic-architecture-for-probabilistic-construction.md) defines the product direction; it does not authorize new language semantics. BoundScript separates architectural authority, implementation freedom, and verification authority rather than making code generation deterministic.

## Target conceptual architecture — not implemented modules

The roles and workflow below are the target design, not additional packages or claims of current automation.

### 1. Build-time architecture planning and approval

Humans own requirements, representative examples, acceptance criteria, trust policy, architectural approval, and final acceptance. An **Architect**, human or LLM, proposes Box decomposition, responsibilities, interfaces, dependencies, task allocation, and integration plans. An LLM Architect is probabilistic; its output becomes authoritative only after approval. Initially, public architectural changes require human approval.

A Box is a unit of delegated responsibility, not necessarily a function, class, agent, service, container, or deployment unit. Multiple Boxes may live in one monolith. Responsibility, dependencies, inputs, outputs, constraints, and execution conditions are conceptual dimensions, not a claim that all have DSL declarations today.

The build-time Architect does not replace or rename the runtime `director`. The latter remains application orchestration in the existing execution backend.

### 2. Deterministic parsing, validation, and contract extraction

Approved BoundScript source is intended to be the authoritative machine-readable architectural boundary. Deterministic tooling parses declarations, resolves supported types and contracts, and emits portable specifications. It must not call an LLM during compilation, extraction, or deterministic verification. Identical approved inputs should yield identical specifications and validation decisions under explicitly versioned tools and rules.

Today parsing, semantic diagnostics, shared declaration lowering, `extractBoxDevelopmentSpec`, the strict version-1 JSON codec, and `bound spec` provide this foundation. They describe only the supported one-operation interfaces, primitive/flat-record types, and minimal `ensure` predicates. Dependencies and capabilities are not formal declarations yet. Source extraction still validates a whole system that requires a runtime director, even though the exported JSON contains no director. Specification semantics must evolve through explicit, compatible version decisions.

The external [deterministic task derivation adapter](task-derivation.md) combines the canonical Box contract (with resolved shared types) with human-owned task/scope/policy snapshots, generated declarations, and a fixed entrypoint seed. Structural checks do not verify human approval. An external controller must provide protected handoff context and the prepared candidate environment; workspace isolation is not implemented. Task metadata, instructions, workspace configuration, and evidence stay separate from the formal contract. The current spec is not a complete implementation brief.

### 3. Independent implementation

Implementers receive bounded contexts and choose algorithms, private code organization, helpers, and permitted tools. They may not silently change public interfaces, shared types, approved dependencies, responsibilities, acceptance criteria, or protected policies. Discovering a better decomposition leads to a change proposal, impact assessment, human approval, regenerated handoffs, and reverification—not an unauthorized contract edit.

Implementation generation remains outside deterministic compilation. Independent work may be sequential and use existing tools; neither an agent runner nor distributed scheduling is required for the first pilot. Candidate workspaces must protect authoritative specifications, tests, and credentials. Separate directories or Git worktrees are organizational boundaries, not security isolation; a Node subprocess alone is not a security boundary. Untrusted generated code must not execute inside the trusted development process. Production isolation is a separate, deferred concern.

### 4. Verification, integration, and promotion

Planned independent verification consumes the approved spec, selected candidate, fixed inputs, and trusted tests rather than trusting implementer claims. It should distinguish invalid inputs, execution failures, invalid output types, postcondition failures, behavioral acceptance failures, integration failures, and unverified properties. Evidence must identify the candidate and contract/task/test versions; affected evidence becomes stale when any of those inputs change.

Integration uses pre-established wiring and approved interfaces. Failed candidates return for revision, or an architectural change is proposed; the integrator must not silently repair them. Human-readable evidence should explain the architecture and the scope of observed behavior before explicit promotion. Runtime checks and standalone single-invocation verification of trusted functions exist today. A candidate evidence workflow, behavioral acceptance runner, and promotion mechanism do not.

Declarations, static checks, test observations, runtime enforcement, and unverified properties must be distinguished. A declared permission restriction is not enforcement, and a type check or deterministic test result is not proof of arbitrary behavior. Postconditions cannot undo side effects.

### Relationship to the current backend

```text
Target construction workflow (not yet automated end to end):
human requirements -> Architect proposal -> human approval
    -> approved BoundScript -> deterministic validation/extraction
    -> bounded tasks -> independent implementations
    -> independent verification -> integration checks -> evidence -> promotion

Existing paths:
BoundScript source -> language frontend -> validated model
    +-> spec extraction -> strict canonical JSON codec -> portable Box spec
        -> strict decoding + trusted function + fixed input -> standalone runtime verifier
    +-> compiler + explicit host bindings -> ExecutableArtifact
        -> runtime + trusted host registry -> runtime director execution
```

The compiler, artifact contract, runtime, runtime `director`, and host bindings remain supported. They are a valid execution backend, not a mandatory dependency of every future Box implementation workflow. The immediate roadmap starts with standalone verification of existing portable specs using trusted fixtures and existing validation semantics, then task derivation and an independent two-Box pilot. Evidence, controlled evolution, and comparison against conventional TypeScript tooling follow. Richer DSL features, production sandboxes, and general agent orchestration require demonstrated need rather than being prerequisites.

## Existing implementation modules

### `@boundscript/language`

Owns source-level concerns: documents, the typed AST, parsing, validation, and language diagnostics. Langium generates the parser, typed AST, grammar model, and language metadata from `boundscript.langium`. The grammar intentionally supports one system, same-system flat record declarations, optional boxes with exactly one typed-input operation each, one director, and one `on start` handler. Value types are `string`, `number`, `boolean`, or named records with required primitive fields; only operation results may be `void`. Invocation arguments are string literals or compatible previously assigned variables. Value-returning invocations are assigned with `let`; void invocations are standalone statements. `print()` remains string-only. Shared semantic validation rejects unknown references, duplicate boxes/types/fields/variables, non-primitive record fields, void inputs, incompatible arguments, and incompatible result bindings. Named records use nominal identity; declarations are not silently discarded. A box may additionally declare one structured `ensure result != STRING` or `ensure result.field != STRING` postcondition targeting a string result/field. Source-located validation rejects void and non-string targets and unknown fields; this is not a general expression grammar.

Core Langium services are composed without an LSP host. The generated language metadata and service structure establish the foundation for later editor support without introducing a VS Code extension now. Generated TypeScript sources are reproducible build artifacts and are not committed.

### `@boundscript/artifact`

Owns the stable hand-off between compiler and runtime. `ExecutableArtifact` is an immutable envelope containing:

- an explicit format and schema version;
- the system identity;
- named runtime entrypoints;
- byte assets addressed by unique relative paths.

The contract deliberately excludes compiler AST nodes, arbitrary metadata, build logs, prompts, model identities, and build-agent state. The runtime profile uses a versioned JSON director program with `print`, `invoke`, and `print-variable` instructions; the artifact envelope itself remains independent of the source language. Director program version 4 carries explicitly tagged literal/variable arguments, box/operation identity, resolved input/result type metadata, and optional postconditions at each invocation. The only predicate descriptor is `string-not-equal`, containing an explicit result/field target and comparison string; no AST or executable expression is serialized. Record metadata contains only a name and primitive field descriptors, not AST nodes. Only non-void calls contain a result-variable name. Invocation instructions contain resolved host implementation IDs, never JavaScript functions or module paths. The runtime rejects older instruction versions; previously supported source programs recompile to version 4 without changes. The artifact envelope remains version 1.

### `@boundscript/compiler`

Consumes a fully resolved compilation input and deterministically emits one `ExecutableArtifact`. The typed language AST plus explicit box-to-implementation-ID bindings form the compilation input. Box implementation identities must be resolved before compilation; obtaining implementations is not the compiler's responsibility.

Compilation returns a discriminated success or failure result, preventing a failed compilation from accidentally exposing a partial artifact. The compiler validates the model and lowers statements to the versioned director instruction asset. An optional explicit `BoxBindings` argument maps each declared box name to a host implementation ID; missing bindings fail compilation. Resolution does not load or generate code. Existing box-free programs need no bindings.

The separate pure, synchronous `extractBoxDevelopmentSpec(system, boxName)` API validates the whole system and extracts one declared box's complete in-memory contract without implementation bindings or director invocations. `BoxDevelopmentSpec` version 1 uses the existing resolved `ValueType` and `Postcondition` descriptors; a small internal declaration-lowering helper is shared with normal compilation. The spec contains no ASTs, source paths, implementation IDs, or executable instructions, and is not part of `ExecutableArtifact`. The separate pure `serializeBoxDevelopmentSpec` / `parseBoxDevelopmentSpec` codec strictly validates the portable version-1 shape and postcondition/type compatibility, reconstructing canonical key order and code-point-sorted fields. The codec has only type-level dependencies on compiler/artifact data contracts; the public `@boundscript/compiler/box-spec` subpath exposes it without loading the compiler root or language frontend. Invalid decoding returns diagnostics; invalid serialization throws `BoxSpecValidationError`. The development spec is a declared contract, not a complete implementation brief; human-owned tasks and independent examples/tests are still required. Agent orchestration and verifier execution remain outside the compiler.

### `@boundscript/runtime`

Executes `ExecutableArtifact` values using a named entrypoint and optional input. It is independent of parser, AST, compiler, and build-agent implementation details. The runtime validates and executes the director instruction format through an injected output sink and an explicit host implementation registry. IDs map to developer-provided functions with primitive/record input and primitive/record or void output, synchronously or asynchronously. The heterogeneous host registry erases TypeScript signatures; runtime metadata, not host type assertions, governs boundary validation. Required registrations are checked before any instructions execute. Calls are awaited sequentially; inputs and outputs are checked against the resolved contract on every invocation, and void results must be `undefined`. Records require own primitive fields, reject extra fields, and numbers must be finite. Record references pass directly between implementations without copying or coercion; trusted host code may mutate them, so subsequent inputs are revalidated. Argument tags are resolved explicitly, never inferred from variable-map contents. Variables are local to one execution. Host failures produce contextual runtime errors. After validating the complete output data type, the runtime evaluates any postcondition before storing the result or continuing. A failed check throws `PostconditionViolationError` with code `runtime.postcondition-violation`, box/operation, predicate, and observed string; host exceptions and data-contract failures retain their existing error categories. Descriptor validation rejects unsupported variants and targets incompatible with the resolved result type. The runtime neither imports modules dynamically nor depends on source box declarations.

The separate `verifyBoxImplementation(contract, implementation, input)` API checks one fixed-input invocation of a trusted, already-loaded function without an artifact or director. Its `BoxVerificationContract` parameter is only a structural consumer view of a strictly decoded `BoxDevelopmentSpec`, not another schema. Runtime stays independent of the compiler: the host decodes through `@boundscript/compiler/box-spec` before calling the verifier. Shared internal helpers implement the same descriptor, value, void, and predicate checks for both paths; legacy director errors remain unchanged. Verification returns discriminated input, execution, output, predicate, setup, and inspection failures; inspection errors are not proven contract violations. No copying/freezing, branding, plain-object tightening, loading, isolation, or timeout enforcement is added. Arbitrary getters/mutable objects do not guarantee deterministic results. See the [API reference](box-development-spec.md#standalone-verification).

`print` is a temporary built-in operation, not a sandboxed capability. Host box implementations are trusted code running in the same process, without sandbox enforcement. Postconditions are behavior checks, not security boundaries: implementation side effects can occur before a check fails, with no rollback or side-effect isolation. General control flow, events, tracing, correlation identifiers, and lifecycle hooks are deferred until concrete requirements exist.

### `@boundscript/sandbox`

Defines declarative capability and resource-limit policies. Concrete process, container, or WebAssembly execution interfaces are deferred until the executable workload contract is known. A policy type documents restrictions but does not enforce them.

### `@boundscript/cli`

Connects file loading, parsing, deterministic compilation, and artifact execution. It reports source diagnostics and returns a non-zero status on failure. It does not interpret source directly or bypass the compiler/runtime artifact boundary. The small `bound spec <source.bound> --box <name>` branch instead connects parsing, validated extraction, and canonical serialization, writing only JSON to stdout. It does not compile executable artifacts or require host bindings.

## Compiler/runtime artifact boundary

```text
ExecutableArtifact
├── format: "boundscript/executable"
├── version: 1
├── system
├── entrypoints[]
│   ├── name
│   └── target
└── assets[]
    ├── path
    ├── mediaType
    └── bytes
```

The compiler guarantees that the artifact is structurally valid, complete, and deterministic for the same resolved input. The runtime validates support for the artifact format/version, resolves the requested entrypoint, and interprets its target and assets.

Serialization, integrity hashes, signatures, dependency manifests, and persistent storage are intentionally not part of the first contract.

## Build-time agents and runtime agents

The word **agent** describes two separate concepts.

### Build-time AI agents

Build-time agents are development tooling. They may generate or repair Box implementations from approved contracts and external functional tasks. Their work precedes acceptance and integration; for the current executable backend, implementation identities are resolved before compilation. Agent execution is outside both the language runtime and deterministic compiler. No agent integration is implemented today.

Their prompts, conversations, provider APIs, model identifiers, and workspaces are not included in `ExecutableArtifact`. Proposal 0013 now requires traceable candidate and verification evidence in the target workflow; that evidence remains separate from runtime metadata and is not implemented yet.

### Runtime agents

A runtime agent, if the language supports one, is application behavior that executes after deployment and may invoke a model as an explicit capability. It is declared by the program, compiled into normal runtime assets and entrypoints, and governed by the same contracts and sandbox policies as other components.

Supporting build-time agents does not imply that BoundScript programs contain runtime agents. The runtime remains provider-neutral.

## Dependency direction

The current execution path is source → language frontend → validated model plus explicit host bindings → compiler → `ExecutableArtifact` → runtime plus trusted host functions. Contract extraction branches from the validated model and does not require those bindings or an executable artifact. Build-time planning/generation and concrete sandbox enforcement are not implemented stages of this path.

Package dependencies reflect the shared boundary:

```text
compiler --> artifact <-- runtime
```

The runtime must not depend on `language` or `compiler`. The artifact package contains data contracts only and depends on no other project package.

## Testing

BoundScript has no language-level `test`, `mock`, or `expect` constructs. Use Vitest to test BoundScript systems and their orchestration externally. `ensure` has the limited implemented postcondition semantics described above; capability declarations and explored `allow` syntax remain design material, not implemented language features.

## Future, not scaffolded

Proposal 0013 prioritizes standalone verification, deterministic task derivation, the independent implementation pilot, evidence/integration, controlled architectural evolution, and comparative evaluation. Standalone single-invocation verification and the external deterministic task adapter are implemented; task delivery remains pending Product Owner acceptance. The broader agent construction, isolation, and evidence workflow capabilities remain planned. The older exploration list below is retained as possible future work, not the immediate roadmap:

- grammar and semantic-model expansion beyond the executable subset;
- richer behavioral contracts beyond single string-inequality postconditions;
- richer resolved box compilation inputs beyond explicit host IDs;
- director control flow beyond sequential invocations and printing;
- box implementation packaging;
- build-agent orchestration;
- optional runtime-agent language semantics;
- expanded CLI and editor tooling;
- artifact serialization and integrity verification;
- concrete sandbox adapters.

These are intentionally deferred to avoid turning explored ideas into accidental commitments.
