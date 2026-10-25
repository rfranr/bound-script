# Architecture

## Goal

BoundScript aims to keep machine-produced software governable and locally repairable by humans. A human defines understandable boundaries and control flow; implementations remain isolated behind explicit contracts.

## Modules

### `@boundscript/language`

Owns source-level concerns: documents, the typed AST, parsing, validation, and language diagnostics. Langium generates the parser, typed AST, grammar model, and language metadata from `boundscript.langium`. The grammar intentionally supports one system, same-system flat record declarations, optional boxes with exactly one typed-input operation each, one director, and one `on start` handler. Value types are `string`, `number`, `boolean`, or named records with required primitive fields; only operation results may be `void`. Invocation arguments are string literals or compatible previously assigned variables. Value-returning invocations are assigned with `let`; void invocations are standalone statements. `print()` remains string-only. Shared semantic validation rejects unknown references, duplicate boxes/types/fields/variables, non-primitive record fields, void inputs, incompatible arguments, and incompatible result bindings. Named records use nominal identity; declarations are not silently discarded.

Core Langium services are composed without an LSP host. The generated language metadata and service structure establish the foundation for later editor support without introducing a VS Code extension now. Generated TypeScript sources are reproducible build artifacts and are not committed.

### `@boundscript/artifact`

Owns the stable hand-off between compiler and runtime. `ExecutableArtifact` is an immutable envelope containing:

- an explicit format and schema version;
- the system identity;
- named runtime entrypoints;
- byte assets addressed by unique relative paths.

The contract deliberately excludes compiler AST nodes, arbitrary metadata, build logs, prompts, model identities, and build-agent state. The runtime profile uses a versioned JSON director program with `print`, `invoke`, and `print-variable` instructions; the artifact envelope itself remains independent of the source language. Director program version 3 carries explicitly tagged literal/variable arguments, box/operation identity, and resolved input/result type metadata at each invocation. Record metadata contains only a name and primitive field descriptors, not AST nodes. Only non-void calls contain a result-variable name. Invocation instructions contain resolved host implementation IDs, never JavaScript functions or module paths. The runtime rejects older instruction versions; previously supported source programs recompile to version 3 without changes. The artifact envelope remains version 1.

### `@boundscript/compiler`

Consumes a fully resolved compilation input and deterministically emits one `ExecutableArtifact`. The typed language AST plus explicit box-to-implementation-ID bindings form the compilation input. Box implementation identities must be resolved before compilation; obtaining implementations is not the compiler's responsibility.

Compilation returns a discriminated success or failure result, preventing a failed compilation from accidentally exposing a partial artifact. The compiler validates the model and lowers statements to the versioned director instruction asset. An optional explicit `BoxBindings` argument maps each declared box name to a host implementation ID; missing bindings fail compilation. Resolution does not load or generate code. Existing box-free programs need no bindings.

### `@boundscript/runtime`

Executes `ExecutableArtifact` values using a named entrypoint and optional input. It is independent of parser, AST, compiler, and build-agent implementation details. The runtime validates and executes the director instruction format through an injected output sink and an explicit host implementation registry. IDs map to developer-provided functions with primitive/record input and primitive/record or void output, synchronously or asynchronously. The heterogeneous host registry erases TypeScript signatures; runtime metadata, not host type assertions, governs boundary validation. Required registrations are checked before any instructions execute. Calls are awaited sequentially; inputs and outputs are checked against the resolved contract on every invocation, and void results must be `undefined`. Records require own primitive fields, reject extra fields, and numbers must be finite. Record references pass directly between implementations without copying or coercion; trusted host code may mutate them, so subsequent inputs are revalidated. Argument tags are resolved explicitly, never inferred from variable-map contents. Variables are local to one execution. Host failures produce contextual runtime errors. The runtime neither imports modules dynamically nor depends on source box declarations.

`print` is a temporary built-in operation, not a sandboxed capability. Host box implementations are trusted code running in the same process, without sandbox enforcement. General control flow, events, tracing, correlation identifiers, and lifecycle hooks are deferred until concrete requirements exist.

### `@boundscript/sandbox`

Defines declarative capability and resource-limit policies. Concrete process, container, or WebAssembly execution interfaces are deferred until the executable workload contract is known. A policy type documents restrictions but does not enforce them.

### `@boundscript/cli`

Connects file loading, parsing, deterministic compilation, and artifact execution. It reports source diagnostics and returns a non-zero status on failure. It does not interpret source directly or bypass the compiler/runtime artifact boundary.

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

Build-time agents are development tooling. They may generate or repair box implementations from human-authored contracts. They execute before compilation and are outside both the language runtime and deterministic compiler.

Their prompts, conversations, provider APIs, model identifiers, and workspaces are not included in `ExecutableArtifact`. If reproducibility or provenance is later required, it will be represented by a separate build record rather than runtime metadata.

### Runtime agents

A runtime agent, if the language supports one, is application behavior that executes after deployment and may invoke a model as an explicit capability. It is declared by the program, compiled into normal runtime assets and entrypoints, and governed by the same contracts and sandbox policies as other components.

Supporting build-time agents does not imply that BoundScript programs contain runtime agents. The runtime remains provider-neutral.

## Dependency direction

```text
human source
    |
    v
language frontend
    |
    v
validated model
    |
    +----> optional build orchestration / build-time AI agents
    |                         |
    |                         v
    +----------------> resolved compilation input
                              |
                              v
                         compiler
                              |
                              v
                    ExecutableArtifact
                              |
                              v
                           runtime
                              |
                              v
                    sandbox enforcement
```

Package dependencies reflect the shared boundary:

```text
compiler --> artifact <-- runtime
```

The runtime must not depend on `language` or `compiler`. The artifact package contains data contracts only and depends on no other project package.

## Testing

BoundScript has no language-level `test`, `mock`, or `expect` constructs. Use Vitest to test BoundScript systems and their orchestration externally. Contracts and capabilities remain language concepts; `ensure` and `allow` are reserved for those concerns rather than testing DSL behavior.

## Future, not scaffolded

- grammar and semantic-model expansion beyond the executable subset;
- contract semantics and verification;
- richer resolved box compilation inputs beyond explicit host IDs;
- director control flow beyond sequential invocations and printing;
- box implementation packaging;
- build-agent orchestration;
- optional runtime-agent language semantics;
- expanded CLI and editor tooling;
- artifact serialization and integrity verification;
- concrete sandbox adapters.

These are intentionally deferred to avoid turning explored ideas into accidental commitments.
