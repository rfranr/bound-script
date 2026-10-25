# Assignment 0009 — Box Composition

## Goal

Demonstrate actual orchestration between two independently implemented boxes: a director passes the result of one box operation as the input to another box operation.

Extend the executable subset delivered in Assignments 0006–0007 without introducing a general-purpose expression or type system.

## Target behavior

The following is **illustrative target syntax**; keep syntax consistent with the existing Langium grammar wherever possible:

```boundscript
system HelloWorld {
    box Greeter {
        operation greet(name: string): string
    }

    box Display {
        operation show(message: string): void
    }

    director Main {
        on start {
            let message = Greeter.greet("World")
            Display.show(message)
        }
    }
}
```

With two distinct host-provided TypeScript implementations, `Greeter.greet` returns `"Hello, World!"` and `Display.show` receives exactly that value and records/displays it. The director itself does not call `print()`.

## Requirements

1. Extend box operation declarations to support a `void` result in addition to the existing `string` result. Keep one operation and one string input per box for this slice.
2. Allow box invocation arguments to be either string literals or previously assigned local variables.
3. Allow a box operation returning `void` to be invoked as a standalone director statement, without `let` or a result binding.
4. Keep `let name = Box.operation(...)` for value-returning operations. Validate incompatible uses: a `void` invocation must not be assigned; a value-returning invocation must not be used as an unassigned statement in this slice.
5. Validate unknown boxes, unknown operations, variables referenced before assignment, and duplicate variable declarations. Reject invalid programs with diagnostics; never silently omit invalid instructions.
6. Preserve the distinction between literal values and variable references through compilation and artifact serialization. Do not infer it from variable-map contents.
7. Represent the new invocation and argument forms in the shared artifact contract and execute them sequentially in the runtime. Await async implementations before invoking the next box.
8. Extend the host implementation registry so that void operations may return `void | Promise<void>` while string operations must return `string | Promise<string>`. Enforce the declared result category at runtime, including rejecting a non-`undefined` result from a `void` operation and a non-string result from a `string` operation.
9. Add a runnable end-to-end demonstration that binds both `Greeter` and `Display` implementations using the existing explicit binding approach. Provide one documented npm command to run the demonstration from the repository root.
10. Add Vitest coverage for successful two-box composition, invocation order, argument propagation (literal and variable), asynchronous implementations, and invalid source/runtime cases.
11. Preserve the existing executable Hello World and Assignment 0007 demo behavior.

## Constraints

- No structured types or objects yet: only `string` inputs, `string` outputs, and `void` outputs.
- No general expression evaluation, loops, conditionals, imports, or additional box operations.
- No `ensure`, `allow`, sandbox enforcement, AI generation, or dynamic implementation discovery.
- No testing constructs inside BoundScript; use Vitest.
- Retain the compiler → versioned artifact → runtime architecture and the explicit box-name-to-implementation-ID binding mechanism.
- The compiler must not receive or execute TypeScript implementation functions, and executable code must not be embedded in the artifact.
- Avoid unrelated refactors, additional dependencies, and breaking changes to previously supported `.bound` programs.
- Do not modify this assignment file except when explicitly authorized.

## Acceptance criteria

1. A source program with `Greeter.greet("World")` followed by `Display.show(message)` compiles and executes via the real Langium → compiler → artifact → runtime pipeline.
2. The independently supplied `Display` implementation is called exactly once, after `Greeter`, with `"Hello, World!"`.
3. A single documented command executes the full composition demo successfully.
4. Using an undefined variable, assigning a `void` call, or invoking a string-returning operation as an unassigned statement fails before execution with an identifiable diagnostic.
5. A string literal whose contents equal a variable name remains a literal.
6. Runtime missing implementations, thrown/rejected implementation errors, and invalid return categories produce identifiable failures.
7. Existing 0006/0007 behavior and tests continue to work. `npm run check` and `npm run build` pass.

## Delivery

- Create a focused Conventional Commit referencing `Assignment: 0009`, following `AGENTS.md`, including actual AI metadata.
- Include this assignment file in the commit if not already committed.
- Report the execution command, observed output, verification results, and commit hash.
- Do not push without explicit authorization.
