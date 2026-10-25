# Architecture

## Goal

BoundScript aims to keep machine-produced software governable and locally repairable by humans. A human defines understandable boundaries and control flow; implementations remain isolated behind explicit contracts.

## Modules

### `@boundscript/language`

Owns source-level concerns: documents, the typed AST, parsing, validation, and language diagnostics. Langium generates the parser, typed AST, grammar model, and language metadata from `boundscript.langium`. The grammar intentionally supports only one system, one director, one `on start` handler, and string-literal `print()` statements.

Core Langium services are composed without an LSP host. The generated language metadata and service structure establish the foundation for later editor support without introducing a VS Code extension now. Generated TypeScript sources are reproducible build artifacts and are not committed.

### `@boundscript/artifact`

Owns the stable hand-off between compiler and runtime. `ExecutableArtifact` is an immutable envelope containing:

- an explicit format and schema version;
- the system identity;
- named runtime entrypoints;
- byte assets addressed by unique relative paths.

The contract deliberately excludes compiler AST nodes, arbitrary metadata, build logs, prompts, model identities, and build-agent state. The first runtime profile adds a versioned JSON director program containing only `print` instructions; the artifact envelope itself remains independent of the source language.

### `@boundscript/compiler`

Consumes a fully resolved compilation input and deterministically emits one `ExecutableArtifact`. For the first slice, the typed language AST is already the complete compilation input. Future box implementations must be resolved before compilation; obtaining them will not be the compiler's responsibility.

Compilation returns a discriminated success or failure result, preventing a failed compilation from accidentally exposing a partial artifact. The current compiler lowers `print()` statements to the versioned director instruction asset.

### `@boundscript/runtime`

Executes `ExecutableArtifact` values using a named entrypoint and optional input. It is independent of parser, AST, compiler, and build-agent implementation details. The current runtime validates and executes the first director instruction format through an injected output sink.

`print` is a temporary built-in operation, not a sandboxed capability. General control flow, events, tracing, correlation identifiers, and lifecycle hooks are deferred until concrete requirements exist.

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
- a resolved compilation-input model for boxes;
- director control flow beyond sequential `print` instructions;
- box implementation packaging;
- build-agent orchestration;
- optional runtime-agent language semantics;
- expanded CLI and editor tooling;
- artifact serialization and integrity verification;
- concrete sandbox adapters.

These are intentionally deferred to avoid turning explored ideas into accidental commitments.
