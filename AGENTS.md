## Git workflow

- Follow Conventional Commits.
- Create one focused commit per completed assignment.
- Run relevant tests and build checks before committing.
- Every commit must include:
  - A concise subject following `<type>(<scope>): <description>`.
  - A blank line.
  - A descriptive body explaining the actual changes made.
  - Bullet points for significant changes when appropriate.
  - A brief explanation of important architectural decisions or trade-offs, when relevant.
- Describe **what changed and why**, not merely the task requested.
- Keep the subject under 72 characters.
- Avoid generic descriptions, redundant information and unnecessarily verbose commit bodies.
- Do not include trivial implementation details, obvious statements (e.g., "updated files" or "ran npm install"), or a chronological list of commands executed. Focus on meaningful changes, their purpose and their impact.
- Never commit generated artifacts, secrets or temporary files.
- Never amend, rebase, reset or rewrite existing commits without explicit authorization.
- Never push to remote repositories unless explicitly instructed.
- Report the commit hash, summary of changes and verification results after each assignment.

## Assignment workflow

- Development assignments are authored and owned by the human product owner.
- Assignments are stored in `docs/assignments/` with sequential identifiers and descriptive filenames.
- Treat assignment files as immutable requirements during implementation.
- Never create, rewrite or modify assignment files unless explicitly instructed by the human.
- Read the specified assignment and implement its requirements.
- Ask for clarification only when a decision materially affects the requirements or cannot be resolved safely.
- Include the assignment file and its implementation in the same commit when the assignment file is not already committed.
- Reference the assignment identifier in the commit body (e.g., `Assignment: 0003`).
- Report deviations, unresolved questions and verification results without modifying the original assignment.
- Do not include unrelated changes in the assignment commit.

## Project context

- Architecture and decisions are documented in `docs/`.
- Development requirements are defined in `docs/assignments/`.
- Historical ChatGPT conversations are available locally
  as reference material and are excluded from Git.
- Do not read historical conversations by default.
- Consult them only when the current documentation is
  insufficient to resolve a specific design question.
- When consulting historical conversations, retrieve only
  the relevant sections rather than loading entire files.
- Treat historical discussions as exploratory context, not as authoritative requirements.
