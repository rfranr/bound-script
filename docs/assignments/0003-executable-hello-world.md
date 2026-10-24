## Assignment: First executable BoundScript program

The architectural scaffolding is accepted. Your next task is to implement the smallest end-to-end executable vertical slice of BoundScript.

**Goal**

Make this command work:

`npm run bound -- examples/hello-minimal.bound`

Expected output:

`Hello, World!`

**Minimum language subset**

Support a system declaration, one director, an `on start` block, and a built-in `print()` statement accepting a string literal.

Do not attempt to implement the complete language.

**Implementation requirements**

- Implement a minimal parser that produces a typed AST.
- Provide meaningful syntax errors with source locations.
- Compile the validated AST deterministically into the existing `ExecutableArtifact` contract.
- Implement a minimal runtime capable of executing that artifact.
- Add a CLI entry point that connects these stages.
- Keep the runtime independent of the parser and source language.
- Do not bypass the compiler by directly interpreting the source in the CLI.
- Make the CLI return a non-zero exit code on failure.
- Add automated tests for successful execution and invalid syntax.

**Constraints**

- No AI agents, LLM integrations or build-time code generation.
- No boxes, contracts, mocks or postconditions yet.
- No loops, branching or DAG execution machinery yet.
- No external sandbox technology.
- Treat `print()` as a temporary, explicitly defined built-in operation. Do not present it as a sandboxed or security-enforced capability.
- Avoid speculative abstractions and unnecessary dependencies.
- Keep the implementation small and coherent.

**Acceptance criteria**

1. The example runs successfully from the terminal.
2. Invalid source produces useful diagnostics.
3. Compiler output is consumed by the runtime through the shared artifact contract.
4. Type checking, tests and build pass.
5. The existing architecture boundaries remain intact.

You own the technical decisions.

Create one focused Conventional Commit with a descriptive body explaining what changed and why.

Report the commit hash, verification results and any deliberately deferred features.
