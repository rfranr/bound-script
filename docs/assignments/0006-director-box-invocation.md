Implement the next minimal executable BoundScript slice: **Director → Box invocation**.

Goal: demonstrate that a director can invoke a box through its declared interface and consume the result.

Requirements:
- Extend the Langium grammar to declare a box with one operation, one string input, and one string output.
- Allow a director to invoke that operation, assign its result to a variable, and pass the variable to `print()`.
- Bind the box to a developer-provided TypeScript implementation through an explicit mechanism.
- Validate unknown boxes, operations, and missing implementations with clear diagnostics.
- Add Vitest tests for successful invocation and failure cases.
- Keep the existing `Hello, World!` executable example working.

Constraints:
- No AI implementation generation.
- No sandbox enforcement yet.
- No imports, general-purpose expressions, loops, or conditionals.
- No testing syntax inside BoundScript.
- Do not redesign the compiler/runtime architecture.
- Keep the change as small as possible.

