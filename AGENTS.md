# Agent Guidelines

## Project Context

- BoundScript uses native TypeScript contracts, natural-language tasks and independently verified AI-generated implementations.
- The current architecture, workflows and limitations are documented in `README.md` and the relevant technical guides.
- Development assignments are stored in `docs/assignments/`.
- Historical AI conversations provide context, not authoritative requirements. Consult only relevant sections when necessary.
- Do not assume a particular Git branch is required unless the current task specifies one.

## Development Workflow

Follow `docs/development/developer-workflow.md` for assignment registration, implementation, review, authorization and acceptance.

Before implementing a development request:

1. Use an existing referenced assignment, or register the human instructions under `docs/assignments/` before changing implementation code.
2. Preserve the intended requirements; do not invent, change or approve them.
3. Implement only within the authorized scope.
4. Never mark your own delivery as accepted.

Respect stricter task instructions, including `Do not modify files` and `Do not commit`.

## Git Workflow

- Follow Conventional Commits: `<type>(<scope>): <description>` (maximum 72 characters).
- Write a meaningful commit body explaining what changed and why; keep commits focused and run relevant checks.
- Create local commits only when authorized. Never push without explicit authorization.
- Never amend, reset, rebase or rewrite history without explicit authorization.
- Do not commit secrets, transcripts, temporary files or generated artifacts excluded from version control.

Include applicable, factual traceability metadata in commits:

```text
Assignment: <id>
AI-Tool: <tool-name>
AI-Model: <model-id>
AI-Reasoning: <effort-level>
```

- Report actual model usage. If multiple models contributed materially, identify them in the body; use `unknown` when details cannot be established.
- After an authorized commit, report its hash and summary. Otherwise leave changes uncommitted and report results.

## Information Disclosure

- Preserve the meaning of human requirements and the technical decisions needed for traceability.
- Do not unnecessarily reproduce private conversations, informal remarks or verbatim human instructions in reports or commits.
- Summarize authorizations factually and minimally; do not quote informal approval messages.
- Record verification evidence without disclosing secrets, credentials or unrelated personal information.
