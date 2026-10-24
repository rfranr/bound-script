# Architecture

## Goal

BoundScript aims to keep machine-produced software governable and locally repairable by humans. A human defines understandable boundaries and control flow; implementations remain isolated behind explicit contracts.

## Modules

### `@boundscript/language`

Owns source-level concerns: documents, parsing, AST/model construction, name resolution, type checking, and language diagnostics. No grammar or parser is selected yet.

### `@boundscript/artifact`

Owns the stable hand-off between compiler and runtime. `ExecutableArtifact` is an immutable envelope containing:

- an explicit format and schema version;
- the system identity;
- named runtime entrypoints;
- byte assets addressed by unique relative paths.

The contract deliberately excludes compiler AST nodes, arbitrary metadata, build logs, prompts, model identities, and build-agent state. Entry-point targets and asset media types remain runtime-defined until execution semantics are designed.

### `@boundscript/compiler`

Consumes a fully resolved compilation input and deterministically emits one `ExecutableArtifact`. A resolved input includes every implementation asset or reference required for packaging; obtaining those implementations is not the compiler's responsibility.

Compilation returns a discriminated success or failure result, preventing a failed compilation from accidentally exposing a partial artifact.

### `@boundscript/runtime`

Executes `ExecutableArtifact` values using a named entrypoint and optional input. It is independent of parser, AST, compiler, and build-agent implementation details. It must support explicit control flow rather than reducing every program to a DAG.

The runtime result currently contains only output. Events, tracing, correlation identifiers, and lifecycle hooks are deferred until concrete observability requirements exist.

### `@boundscript/sandbox`

Defines declarative capability and resource-limit policies. Concrete process, container, or WebAssembly execution interfaces are deferred until the executable workload contract is known. A policy type documents restrictions but does not enforce them.

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

## Future, not scaffolded

- textual grammar and typed AST;
- contract semantics and verification;
- a resolved compilation-input model;
- director control-flow compilation;
- box implementation packaging;
- build-agent orchestration;
- optional runtime-agent language semantics;
- CLI and editor tooling;
- artifact serialization and integrity verification;
- concrete sandbox adapters.

These are intentionally deferred to avoid turning explored ideas into accidental commitments.
