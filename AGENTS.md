# Agent Guidelines

## Project Context

- BoundScript uses native TypeScript contracts, natural-language tasks and independently verified AI-generated implementations.
- The current architecture, supported workflows and limitations are documented in `README.md`.
- Development assignments are stored in `docs/assignments/`.
- Historical AI conversations are reference material, not authoritative requirements. Read only relevant sections when necessary.
- Do not assume a particular Git branch is required unless explicitly specified by the current task.

## Development Workflow

Follow `docs/development/developer-workflow.md` for assignment registration, implementation, review, authorization and acceptance.

Before implementing a development request:

1. Use the referenced assignment if one exists.
2. Otherwise, register the human instructions under `docs/assignments/` before modifying implementation code.
3. Preserve the original requirements; do not invent or approve requirements.
4. Implement only within the authorized scope.
5. Never mark your own implementation as accepted.

Explicit task restrictions, such as `Do not modify files` or `Do not commit`, must be respected.

## Git Workflow

- Follow Conventional Commits: `<type>(<scope>): <description>` (maximum 72 characters).
- Write a meaningful commit body explaining what changed and why.
- Keep commits focused and run relevant checks before committing.
- Create local commits only when authorized.
- Never amend, reset, rebase or rewrite history without explicit authorization.
- Never push without explicit authorization.
- Never commit secrets, transcripts, temporary files or generated artifacts that should remain excluded from version control.

Include traceability metadata in commits:

```text
Assignment: <id>
AI-Tool: <tool-name>
AI-Model: <model-id>
AI-Reasoning: <effort-level>
```

- Report actual AI tool and model usage; never fabricate metadata.
- If multiple models contributed materially, identify them in the commit body.
- Use `unknown` when metadata cannot be determined.
- After an authorized commit, report its hash and a brief summary.
- When commits are not authorized, leave changes uncommitted and report the results.

## Information Disclosure

- Record technical decisions, requirements and verification evidence.
- Do not reproduce private conversations, informal remarks or verbatim human instructions in reports or commits.
- Summarize authorizations factually and minimally.
- Disclose only information necessary for technical traceability.