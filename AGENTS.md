# Agent Guidelines

## Project context

- Work on BoundScript Next only on `experiment/boundscript-next`.
- The original implementation is preserved on `feature/agent-driven-architecture`.
- Architecture and current limitations are documented in `README.md` and
  `experiments/minimal-box/README.md`.
- Requirements are defined in `assignments/`.
- Historical AI conversations are local reference material, excluded from Git. Do not read them unless necessary, and retrieve only relevant sections.
- Treat historical conversations as exploratory context, not authoritative requirements.


## Assignment workflow

- Assignments are owned by the Product Owner; reviews are owned by the Reviewer. Do not modify them without explicit authorization.
- Read and implement the specified assignment in `assignments/`.
- Stay within scope. Ask only when a decision materially affects requirements.
- Address review corrections under the original assignment unless the scope changes.
- An assignment may require multiple commits.
- Include uncommitted assignment or review files in the corresponding implementation or correction commit.
- Report deviations, unresolved questions and verification results.
- Run `npm test` for the credential-free saved Box and integration checks.
  `npm run generate` and `npm run generate:pair` make real provider calls and expose
  the explicitly authorized auth file to Pi tools.
- Keep acceptance checks external; do not add a DSL, custom runtime, generic runner
  or new packages without a concrete requirement.


## Git workflow

- Follow Conventional Commits: `<type>(<scope>): <description>` (max. 72 characters).
- Write a meaningful commit body explaining what changed and why, including important technical decisions when relevant.
- Avoid trivial details, command logs and redundant descriptions.
- Keep commits focused and run relevant checks before committing.
- Append Git trailers separated from the body by a blank line:

  `Assignment: <id>`  
  `AI-Tool: <tool-name>`  
  `AI-Model: <model-id>`  
  `AI-Reasoning: <effort-level>`

- Report actual model usage. If multiple models contributed materially, identify them in the body. Use `unknown` when metadata cannot be determined.
- Never include secrets, transcripts, generated artifacts or temporary files in commits.
- Never amend, reset, rebase or rewrite history without explicit authorization.
- Never push without explicit authorization.
- Report the commit hash and summary after completing the work.