# BoundScript

**Human-designed. Agent-implemented. Bound by contracts.**

BoundScript is an early-stage language and runtime concept for defining software and AI-agent workflows with explicit architecture, contracts, control flow, and capability boundaries.

This repository contains a minimal parser, deterministic compiler, artifact-driven runtime, and CLI for a deliberately tiny language subset, including director-to-box calls. It does not yet implement contract verification, general control flow, sandbox enforcement, or agent execution.

## Direction

The design context suggests a hybrid language:

- declarative definitions for systems, isolated implementation units ("boxes"), contracts, and permissions;
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

## Director → Box invocation

[`examples/director-box.bound`](examples/director-box.bound) declares one string-in/string-out operation and invokes it from a director:

```boundscript
box Greeter {
    operation greet(name: string): string
}
```

Inside `on start`, `let greeting = Greeter.greet("World")` stores the result and `print(greeting)` consumes it. Boxes are declared before the director. Each box has exactly one operation, one named string input, and one string output. Calls accept only a string literal; variables can only hold call results and be passed to `print`. Variables are immutable and local to one execution.

Bind developer-provided TypeScript functions through the programmatic API:

```typescript
import { readFile } from 'node:fs/promises';
import { parseBoundScript } from '@boundscript/language';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptRuntime } from '@boundscript/runtime';
import { greet } from './my-greeter.js'; // Developer-provided (string) => string | Promise<string>

const parsed = parseBoundScript({
  uri: 'examples/director-box.bound',
  text: await readFile('examples/director-box.bound', 'utf8')
});
if (!parsed.program) throw new Error(JSON.stringify(parsed.diagnostics));

const compiled = await new BoundScriptCompiler().compile(parsed.program, {
  Greeter: 'my-greeter' // Source box name → resolved host implementation ID
});
if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));

const runtime = new BoundScriptRuntime(
  { writeLine: (value) => console.log(value) },
  { 'my-greeter': greet } // Implementation ID → trusted TypeScript function
);
await runtime.execute(compiled.artifact, { entrypoint: 'start' });
```

Every declared box requires an explicit binding. Unknown boxes, operations, and variables fail semantic validation/compilation. Missing host functions fail before instruction execution. Thrown/rejected implementation errors and non-string results fail execution with contextual errors. Functions are not generated, loaded dynamically, or embedded in the artifact; the host supplies them. They run **without sandbox enforcement**. The CLI has no implementation-loading option, so use the API for box programs; the existing Hello World CLI remains unchanged.

## Repository layout

```text
packages/
  language/   Langium grammar, generated typed AST, parsing, and diagnostics
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

Langium-generated TypeScript sources are reproducible and ignored by Git. Build and test commands regenerate them from `packages/language/src/boundscript.langium`.

Useful commands:

- `npm run langium:generate` — regenerate the parser, typed AST, and language metadata
- `npm run typecheck` — generate language sources and compile all TypeScript project references
- `npm test` — run the Vitest suite
- `npm run check` — run type checking and tests
- `npm run clean` — remove TypeScript build outputs

## Status

The executable subset supports one `system`, optional boxes with one string-in/string-out operation each, one `director`, and one sequential `on start` block. Statements are string-literal box calls assigned with `let`, and `print()` with a string literal or previously assigned variable. No imports, general expressions, loops, conditionals, or testing syntax are supported. Use Vitest for external tests. The broader example language remains design material rather than a finalized specification.
