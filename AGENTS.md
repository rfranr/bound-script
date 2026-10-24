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
