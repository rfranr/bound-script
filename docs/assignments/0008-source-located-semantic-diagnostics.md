# Assignment 0008 — Source-Located Semantic Diagnostics

## Goal

Make semantic errors actionable by including the source location of the offending construct in BoundScript diagnostics, consistent with the project's existing line/column reporting for parser errors.

## Requirements

- Extend semantic validation so diagnostics for unknown boxes, unknown operations, unknown variables, duplicate variables and duplicate box declarations carry accurate source ranges when produced from parsed source.
- Point each range to the relevant identifier or smallest useful source construct, rather than an unrelated enclosing block.
- Preserve diagnostic codes and meaningful existing messages unless a specific correction is necessary.
- Ensure the CLI displays file, line and column using its existing diagnostic formatting.
- Keep the compiler's validation behavior consistent: invalid input must fail compilation without emitting an artifact, and semantic diagnostics should retain available ranges.
- Add Vitest tests using multi-line fixtures to assert the correct location for each error category, including at least one case where multiple similar identifiers appear on different lines.
- Preserve the existing parser/lexer diagnostic behavior and successful programs.

## Constraints

- Use Langium's existing source/CST location facilities instead of introducing a second parser or scanning source text with regular expressions.
- Do not add new DSL constructs, alter runtime behavior, or redesign the diagnostics model unnecessarily.
- Do not broaden this assignment into import/module resolution or language-server features.
- Keep the patch focused on the language frontend, propagation of diagnostics and tests.

## Acceptance criteria

1. Each covered semantic error reports the correct offending source line and column.
2. CLI error output includes the source path and position for semantic errors.
3. Compiler validation fails on the same semantic errors and does not silently drop invalid instructions.
4. Existing diagnostics, tests and valid programs remain compatible.
5. `npm run check` and `npm run build` pass.

## Delivery

- Create a focused Conventional Commit referencing `Assignment: 0008` and recording actual AI metadata according to `AGENTS.md`.
- Include this assignment file in the commit if it is not already tracked.
- Report the tested diagnostics, verification results and commit hash.
- Do not push without explicit authorization.
