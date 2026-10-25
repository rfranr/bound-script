# Assignment 0011 — Minimal Behavioral Contracts (`ensure`)

## Goal

Add a first, deliberately narrow **postcondition** mechanism to BoundScript boxes. A box declares a verifiable property of its returned value, and the runtime checks it immediately after the host implementation returns. Build on Assignment 0010's runtime type-boundary validation.

This assignment is **not** a general expression language, an assertion framework for directors, or a sandbox.

## Target behavior (illustrative syntax)

```boundscript
system GreetingSystem {
    type Greeting {
        message: string
        recipientId: string
    }

    box Greeter {
        operation greet(name: string): Greeting
        ensure result.message != ""
    }

    box Display {
        operation show(greeting: Greeting): void
    }

    director Main {
        on start {
            let greeting = Greeter.greet("World")
            Display.show(greeting)
        }
    }
}
```

The host's `Greeter.greet` implementation must first return a valid `Greeting` record (Assignment 0010). Then the declared `ensure` must hold. If it returns `{ message: "", recipientId: "123" }`, the call fails with a recognizable **postcondition violation**, and `Display.show` is never invoked.

## Scope and syntax

Implement only the following forms, with at most one `ensure` per box operation:

- `ensure result != ""` when the operation result type is `string`.
- `ensure result.field != ""` when the operation returns a named flat record and `field` is declared as `string`.
- Optionally `==` in addition to `!=` **only if** it is equally small and straightforward; `!=` alone satisfies this assignment.

Treat these as structured contract predicates, **not** free-form expressions. The right-hand side is a **string literal only**. There are no arithmetic operators, concatenation, boolean combinators, function calls, variable references, chained property access, or arbitrary statements in contracts. Do not support `ensure` on a `void` operation in this slice.

## Requirements

1. Extend the Langium grammar/AST to represent an optional `ensure` declaration associated with a box operation. Preserve existing source programs unchanged.
2. Validate postconditions statically: reject `ensure` on `void`, an unknown record field, a field whose type is not `string`, and an incompatible result type; return a source-located diagnostic with a stable code. Do not silently drop bad contracts.
3. Compile the postcondition to a **small, explicit, serializable descriptor** in the versioned director instruction artifact; never serialize executable functions, source-language AST objects, or JavaScript expression text for evaluation.
4. Validate the implementation's result against its declared **data type first**, then evaluate its `ensure` postcondition, before storing the returned value or executing the next director statement.
5. A violated postcondition must throw a distinct, identifiable runtime error with box name, operation, predicate and observed failure context. The downstream box must not be invoked.
6. A thrown or rejected host implementation remains a host execution error, **not** a postcondition failure. Data-type mismatches remain data-contract failures, **not** postcondition failures.
7. Preserve sequential async execution, explicit host bindings, and existing input/output validation.
8. Add an executable example or extend the structured-types demo to demonstrate a successful postcondition. Include a negative test in which the host returns a structurally valid record violating the condition.
9. Add Vitest tests for successful and failed postconditions, grammar/semantic errors, deterministic serialized descriptors, and preservation of previous programs.
10. `npm run check`, `npm run build`, and the existing `demo:director-box`, `demo:box-composition`, `demo:structured-types`, and CLI Hello World commands must continue to work.

## Constraints / architectural boundaries

- **Postconditions only.** No `require`, `invariant`, director-level assertions, or contract inheritance.
- No general expression parser/evaluator, `eval`, `new Function`, or generated JavaScript predicate code.
- Do not implement the earlier aspirational expression `ensure result == "Hello, " + name + "!"` yet. That requires language-design decisions outside this assignment.
- No new types, records with nested fields, arrays, optional properties, type-system refactors, imports, control-flow statements, agent implementation, or sandbox permissions.
- Contracts are **data/behavior checks, not security boundaries**. Host code is still trusted and can cause side effects before the postcondition is checked. Do not claim transaction rollback or side-effect isolation.
- The syntax above is a suggested minimal form; keep consistency with the existing language. If it would require a broader redesign, report the conflict before widening scope.
- Do not modify this assignment file unless explicitly authorized.

## Acceptance criteria

1. A box returning a valid `Greeting` with a nonempty `message` passes its `ensure` and subsequent director statements execute.
2. The **same record shape** with `message: ""` fails specifically as a postcondition violation, before the following box is invoked.
3. Incorrect record shapes fail as type-boundary violations **before** postcondition evaluation.
4. Using `ensure result.unknown != ""`, targeting a non-string field, or attaching `ensure` to `void` is rejected before artifact emission, with source location and identifiable diagnostic codes.
5. The artifact encodes the check deterministically as data, and the runtime interprets only the supported descriptor variant(s).
6. Existing `.bound` programs and demos work without modification; `npm run check` and `npm run build` pass.

## Delivery

- Make a focused Conventional Commit with `Assignment: 0011` and actual `AI-Tool`, `AI-Model`, and `AI-Reasoning` trailers following `AGENTS.md`.
- Include this assignment file in the commit if it was not previously tracked.
- Report commands run, observed demo/test output, limitations and commit SHA.
- Do not push without explicit authorization.
