# BoundScript

**Human-designed. Agent-implemented. Bound by contracts.**

BoundScript is an early-stage language and runtime concept for defining software and AI-agent workflows with explicit architecture, contracts, control flow, and capability boundaries.

This repository contains the first executable vertical slice: a minimal parser, deterministic compiler, artifact-driven runtime, and CLI for a deliberately tiny language subset. It does not yet implement boxes, contracts, general control flow, sandbox enforcement, or agent execution.

## Direction

The design context suggests a hybrid language:

- declarative definitions for systems, isolated implementation units ("boxes"), contracts, permissions, and tests;
- explicit imperative control flow for human-governed coordinators ("directors");
- implementations hidden behind contracts and potentially produced by humans or build-time AI agents;
- capability restrictions enforced by a sandbox, not trusted to prompts or static types;
- no assumption that every workflow is a DAG;
- no dependency on a particular LLM provider or agent framework.

Run the executable example:

```bash
npm run bound -- examples/hello-minimal.bound
```

Expected output:

```text
Hello, World!
```

See [`examples/hello-world.bound`](examples/hello-world.bound) for broader, non-executable syntax exploration.

## Repository layout

```text
packages/
  language/   Source documents, diagnostics, and the future parser/validator boundary
  artifact/   Shared executable-artifact contract between compiler and runtime
  compiler/   Deterministic resolved-input to artifact compilation boundary
  runtime/    Provider-neutral artifact execution boundary; does not know the source DSL
  sandbox/    Capability and resource policy definitions
  cli/        Source-to-parser-to-compiler-to-runtime command-line pipeline
docs/
  architecture.md
  decisions.md
  open-questions.md
examples/
  hello-world.bound
tests/
  scaffolding.test.ts
```

Build-time AI-agent orchestration remains deferred. Build-time agents are development tooling, not runtime components. Runtime agents, if supported later, will be explicit language-level application behavior and will remain provider-neutral.

## Development

Requirements: Node.js 22.12+ and npm.

```bash
npm install
npm run check
npm run build
```

npm 12 blocks unreviewed dependency install scripts by default. The current dependency graph requires no install-script approvals; new scripts will remain blocked until explicitly reviewed.

Useful commands:

- `npm run typecheck` — compile all TypeScript project references
- `npm test` — run the Vitest suite
- `npm run check` — run type checking and tests
- `npm run clean` — remove TypeScript build outputs

## Status

Only this subset is executable: one `system`, one `director`, one `on start` block, and `print()` statements containing string literals. The broader example language remains design material rather than a finalized specification.
