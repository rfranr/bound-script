# Assignment 0005 — Expand BoundScript execution tests

Expand the automated test coverage of the currently supported BoundScript language by establishing an initial language conformance test suite.

## Goals

- Establish a structured conformance test suite using `.bound` source files.
- Test single and multiple `print()` statements.
- Verify that changing string literals changes the execution output.
- Test escaped strings, whitespace and multiline formatting.
- Test invalid syntax and malformed declarations.
- Verify compiler determinism and runtime output ordering.
- Ensure the test suite can grow incrementally as the language evolves.

## Test organization

Organize test fixtures by expected validity:

```text
tests/
  fixtures/
    valid/
      hello.bound
      multiple-prints.bound
      escaped-strings.bound
      whitespace.bound
    invalid/
      missing-brace.bound
      unknown-statement.bound
      malformed-string.bound
```

Add corresponding Vitest tests that execute these fixtures through the existing language frontend, compiler and runtime.

Keep test fixtures separate from test implementation logic.

The suite should verify observable behavior rather than internal implementation details wherever possible.

## Constraints

- Do not extend the language grammar.
- Do not introduce new language features.
- Do not modify compiler or runtime behavior unless fixing a demonstrated bug.
- Do not add new dependencies.
- Use the existing Langium parser, compiler and runtime.
- Keep test cases small, readable and independent.
- Avoid unnecessary abstractions or introducing a generic testing framework.
- Do not duplicate existing tests unnecessarily.
- If a test reveals a bug, document the failing case and apply only the minimal necessary correction.
- Do not weaken test assertions to accommodate incorrect behavior.

## Acceptance criteria

1. All valid `.bound` fixtures execute with their expected output.
2. All invalid `.bound` fixtures produce diagnostics and non-zero exit codes.
3. Tests cover the complete parser → compiler → runtime integration.
4. Multiple `print()` statements execute in the correct order.
5. Escaped string literals produce the expected runtime values.
6. Compilation of identical inputs produces identical artifacts.
7. Existing tests continue passing.
8. `npm run check` and `npm run build` pass.
9. The conformance suite can be extended with additional fixtures without modifying production code.

Follow the repository assignment and commit conventions.
