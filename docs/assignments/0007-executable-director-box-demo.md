# Assignment 0007 — Executable Director → Box Demo

## Goal

Provide a reproducible, one-command demonstration of the Director → Box functionality delivered in Assignment 0006, using a developer-provided TypeScript implementation. The demo must exercise the actual language, compiler, artifact and runtime path.

## Requirements

- Add a small host application/script that loads `examples/director-box.bound`, parses and validates it, compiles it with an explicit box-to-implementation-ID binding, and executes the artifact with a registered `Greeter` implementation.
- Keep the box implementation separate from the `.bound` source, returning `Hello, World!` when passed `World`.
- Expose one documented npm command to build what is necessary and run the demo from a clean checkout after dependency installation.
- Successful execution must print exactly `Hello, World!` to stdout (build-tool output on stderr is acceptable).
- Preserve the existing `npm run bound -- examples/hello-minimal.bound` behavior.
- Document the demo command and explain explicitly why running `npm run bound -- examples/director-box.bound` without host bindings is not supported by the current CLI.
- Add Vitest coverage of the demo's integration path, including a missing-runtime-implementation failure, without reproducing an entirely separate execution implementation in the test.

## Constraints

- Do not implement CLI dynamic loading, automatic implementation discovery, or a general plugin system.
- Do not embed TypeScript implementations or executable code in the compiled artifact.
- Do not add AI-agent generation, sandbox enforcement, imports, or new language syntax.
- Avoid new dependencies unless essential; prefer the existing build and Node.js setup.
- Do not change the binding contract introduced in Assignment 0006 unless an actual defect prevents the demo; report such a defect instead of expanding scope silently.
- Keep the solution small and focused.

## Acceptance criteria

1. A documented npm command executes the example and prints `Hello, World!`.
2. The example executes the real BoundScript source via the public compiler and runtime APIs, not a hardcoded output.
3. The host implementation is a separate module/function and is provided through the existing binding mechanism.
4. The demo is covered by a repeatable Vitest test, and a missing runtime binding produces an identifiable error.
5. Existing language conformance and Hello World tests remain passing.
6. `npm run check` and `npm run build` pass.

## Delivery

- Create a focused Conventional Commit referencing `Assignment: 0007` and recording actual AI metadata according to `AGENTS.md`.
- Include this assignment file in the commit if it is not already tracked.
- Report the execution command, observed output, verification results and commit hash.
- Do not push without explicit authorization.
