# BoundScript

**Human-designed. Agent-implemented. Bound by contracts.**

BoundScript is an early-stage language and runtime concept for defining software and AI-agent workflows with explicit architecture, contracts, control flow, and capability boundaries.

This repository currently contains **project scaffolding and public module boundaries only**. It does not yet contain a parser, compiler, runtime implementation, sandbox, or agent execution logic.

## Direction

The design context suggests a hybrid language:

- declarative definitions for systems, isolated implementation units ("boxes"), contracts, permissions, and tests;
- explicit imperative control flow for human-governed coordinators ("directors");
- implementations hidden behind contracts and potentially produced by humans or agents;
- capability restrictions enforced by a sandbox, not trusted to prompts or static types;
- no assumption that every workflow is a DAG;
- no dependency on a particular LLM provider or agent framework.

See [`examples/hello-world.bound`](examples/hello-world.bound) for non-executable syntax exploration.

## Repository layout

```text
packages/
  language/   Source documents, diagnostics, and the future parser/validator boundary
  compiler/   Deterministic validated-model to artifact compilation boundary
  runtime/    Provider-neutral execution boundary; does not know the source DSL
  sandbox/    Capability policies and isolated command execution boundary
docs/
  architecture.md
  decisions.md
  open-questions.md
examples/
  hello-world.bound
tests/
  scaffolding.test.ts
```

The agent-driven implementation pipeline and CLI are intentionally deferred until their requirements are concrete.

## Development

Requirements: Node.js 22+ and npm.

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

The example language syntax is design material, not a finalized specification. The next technical milestone should validate a minimal grammar and semantic model before choosing parser tooling or implementing code generation.
