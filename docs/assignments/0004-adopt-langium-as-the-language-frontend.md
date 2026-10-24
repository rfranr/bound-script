## Assignment 0004 — Adopt Langium as the language frontend

Replace the current handwritten lexer/parser with Langium while preserving the existing executable BoundScript vertical slice.

### Goals
- Define the current supported syntax in a `.langium` grammar.
- Generate the typed AST using Langium.
- Integrate parsing and diagnostics with the existing compiler pipeline.
- Preserve the existing `ExecutableArtifact` and runtime behavior.
- Keep `hello-minimal.bound` executable without changes.
- Preserve or improve existing tests, including invalid syntax diagnostics.
- Establish the foundation for future VS Code/LSP support.

### Constraints
- Do not expand the language grammar beyond the currently executable subset.
- Do not implement boxes, control flow, contracts or runtime agents.
- Do not implement the VS Code extension yet.
- Do not alter the runtime instruction format unless strictly necessary.
- Avoid unnecessary scaffolding or dependencies beyond Langium tooling.
- Keep the migration focused on replacing the language frontend.
- Preserve existing architectural boundaries.
- Do not introduce unrelated refactoring.
- If Langium introduces unexpected architectural complications, stop and report the issue, its impact, and possible solutions. Do not redesign the project without approval.

### Acceptance criteria
1. `npm run bound -- examples/hello-minimal.bound` prints `Hello, World!`.
2. Existing tests pass.
3. Parser and AST definitions are generated or managed through Langium.
4. No handwritten parser or lexer remains in the language module.
5. Compiler/runtime architectural boundaries remain intact.

Follow the repository assignment and commit conventions.
