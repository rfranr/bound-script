# Architecture

## Goal

BoundScript aims to keep machine-produced software governable and locally repairable by humans. A human defines understandable boundaries and control flow; implementations remain isolated behind explicit contracts.

## Modules

### `@boundscript/language`

Owns source-level concerns: documents, parsing, AST/model construction, name resolution, type checking, and language diagnostics. No grammar or parser is selected yet.

### `@boundscript/compiler`

Consumes a validated language model and deterministically emits artifacts. It must not call an LLM or silently redesign the architecture. Agent task generation may later consume compiler output, but remains a separate concern.

### `@boundscript/runtime`

Executes compiled artifacts and coordinates calls. It is independent of parser and AST implementation details and must support explicit control flow rather than reducing every program to a DAG.

### `@boundscript/sandbox`

Defines capability policies and the enforcement boundary for isolated development or execution. Policy declarations are not security by themselves; concrete adapters must enforce filesystem, network, process, and resource limits.

## Dependency direction

```text
source -> language -> compiler -> artifact -> runtime
                                      |
                                      v
                              sandbox enforcement
```

The runtime must not depend on the language package. Sandbox technology is replaceable and should not leak into language semantics beyond abstract capabilities.

## Future, not scaffolded

- a textual grammar and typed AST;
- contract semantics and verification;
- director control-flow compilation;
- box manifests and implementation packaging;
- agent director/executor workflows;
- CLI and editor tooling;
- concrete process, container, or WebAssembly sandbox adapters.

These are intentionally deferred to avoid turning explored ideas into accidental commitments.
