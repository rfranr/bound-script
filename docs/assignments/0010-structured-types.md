# Assignment 0010 — Structured Types

## Goal

Extend BoundScript's box interfaces beyond string-only values so directors can pass **structured, typed data** between independently implemented boxes.

Build on Assignment 0009 (Box Composition). Keep this slice focused on **data contracts at box boundaries**, not on general-purpose programming or behavioral contracts (`ensure`).

## Target behavior

The following syntax is **illustrative**, not a finalized language specification. Prefer consistent extensions to the current Langium grammar.

```boundscript
system GreetingSystem {
    type User {
        id: string
        name: string
        active: boolean
    }

    type Greeting {
        message: string
        recipientId: string
    }

    box LoadUser {
        operation load(id: string): User
    }

    box Greeter {
        operation greet(user: User): Greeting
    }

    box Display {
        operation show(greeting: Greeting): void
    }

    director Main {
        on start {
            let user = LoadUser.load("123")
            let greeting = Greeter.greet(user)
            Display.show(greeting)
        }
    }
}
```

An explicit host binds each box to a separate TypeScript implementation. `LoadUser` returns a `User` object, `Greeter` receives it and returns a `Greeting`, and `Display` receives that structured value. The director does not need to inspect or construct the objects.

## Requirements

1. Add reusable named **record types** with required fields of primitive types: `string`, `number`, and `boolean`. Allow operation parameters and results to refer to these types, while retaining existing `string` and `void` behavior. Limit this slice to flat records; no nested records, arrays, unions, generics, optional fields, or user-defined methods.
2. Resolve type references and reject unknown types, duplicate type declarations, duplicate field names, and use of `void` for inputs or record fields. Do not silently ignore invalid declarations.
3. Validate the type compatibility of each director invocation, including passing the result of one box to another. Preserve the distinction between literal and variable operands. The current minimal director syntax does not need object literals or property access.
4. Preserve explicit box-to-host-implementation-ID bindings. Compiler output must contain only serializable values, resolved type metadata and instructions; never embed executable TypeScript functions.
5. Extend the versioned director instruction format as needed to transport structured values without string coercion or loss of object structure. Respect the existing artifact envelope version unless its own shape must change. Reject unsupported instruction versions cleanly.
6. Validate **inputs and outputs at runtime** against their declared primitive or record type at each box boundary. Reject missing required fields, wrong field types, arrays/null where records are expected, and incorrect `void` results with identifiable errors. Apply validation to values returned by host implementations as well as values passed to them.
7. Provide clear errors identifying the failing box/operation, expected type and invalid field or value category. Static source errors belong to the language/compiler diagnostics; host-value contract errors belong to the runtime.
8. Retain sequential asynchronous execution and variables local to a single execution. Passing a record from one box to another must not require reimplementing or serializing the record to a string.
9. Add an executable end-to-end demo using three independent TypeScript implementations (`LoadUser` → `Greeter` → `Display`), with one documented npm command. Make its observable output deterministic.
10. Add Vitest tests for valid structured composition, type/reference errors, static incompatibilities, incorrect runtime outputs and inputs, missing required fields, and compatibility with earlier string/void programs.
11. Preserve existing example commands, conformance tests, and behavior introduced in Assignments 0003–0009.

## Constraints

- **No `ensure` or arbitrary predicates** in this assignment; structural type checks are not behavioral contracts.
- No imports/module system yet. Named types may be declared in the same system for this slice; modular reuse is a later target.
- No object literals, property access, arithmetic, conditions, loops, function declarations, or general expression interpreter.
- No classes, inheritance, generics, unions, nested schemas, arrays, optional fields, or implicit type conversions.
- No agent-generated implementations, sandbox enforcement, capability permissions, dynamic implementation loading or automatic discovery.
- Do not convert the project to a JavaScript code generator or redesign compiler/runtime boundaries.
- Keep type metadata deterministic and serializable, without retaining Langium AST nodes in executable artifacts.
- Keep the change narrowly focused and avoid unrelated refactors or dependencies.
- Do not modify this assignment file without explicit authorization.

## Acceptance criteria

1. A `.bound` program declaring `User` and `Greeting` records and the three boxes compiles and executes through Langium → compiler → artifact → runtime with explicit host bindings.
2. `Greeter` receives a `User` record with correct primitive fields; `Display` receives the `Greeting` record produced by `Greeter`, exactly once and in the correct sequence.
3. Unknown/duplicate types or fields and incompatible director variable arguments fail before execution with identifiable diagnostics.
4. Invalid host values (wrong primitive field, missing field, null/array instead of record, and incompatible output type) fail at the box boundary rather than being silently accepted.
5. The compiled artifact contains no host functions, AST nodes, or implementation source code and is deterministic for equivalent input and bindings.
6. A documented npm command runs the new structured composition demo; existing `demo:director-box`, `demo:box-composition`, and minimal Hello World examples continue to work.
7. `npm run check` and `npm run build` pass, with positive and negative Vitest coverage.

## Delivery

- Create a focused Conventional Commit referencing `Assignment: 0010`, with actual AI metadata according to `AGENTS.md`.
- Include this assignment file in the implementation commit if not already tracked.
- Report the demo command, observed output, test/build results, commit hash, and any limitations or deviations.
- Do not push without explicit authorization.

## Design principle

BoundScript types describe data contracts at box boundaries, not a general-purpose programming type system.

Implement only the type features necessary to declare, validate and transfer data between boxes.

Do not introduce object methods, classes, inheritance, generics, type inference, operators, general expressions or data transformation features in directors.

Complex data processing belongs inside box implementations.