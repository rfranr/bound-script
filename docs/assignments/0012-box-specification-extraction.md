# Assignment 0012 — Box Specification Extraction

## Goal
Extract a deterministic, self-contained development specification for one declared BoundScript box, without requiring implementation bindings or involving build-time agents.

Follow `docs/proposals/0012-box-development-spec.md` as the architecture reference. This assignment implements only extraction and its typed in-memory contract; portable JSON decoding and CLI export belong to Assignment 0013.

## Scope
1. Introduce `BoxDevelopmentSpec` (format `boundscript/box-development-spec`, version `1`) in `@boundscript/compiler`, using the existing `ValueType` and `Postcondition` descriptors from `@boundscript/artifact`. Include `system`, `box`, `operation.name`, `operation.input.name`, resolved input type, resolved result type (or `void`), and optional postcondition.
2. Expose `extractBoxDevelopmentSpec(system: SystemNode, boxName: string): BoxSpecResult`, with a discriminated success/failure result and source-located diagnostics where available.
3. Validate the whole system using the existing semantic validator; reject unknown box selection, invalid declarations, and invalid `ensure`. Return no partial spec on failure.
4. Resolve primitive and same-system named flat-record types, including all required primitive fields, into existing serializable descriptors. Preserve nominal record name identity.
5. Support extraction from a declared but unused box. Extraction must not require any host implementation, implementation ID, director invocation, execution artifact, or file I/O.
6. Factor out the smallest appropriate shared declaration-to-contract lowering helper so the normal compiler and extractor cannot drift. Keep the normal `compile` API, artifact format, and runtime behavior unchanged.
7. Ensure extracted data contains no Langium AST/CST nodes, source paths, prompts, timestamps, implementation identifiers, model metadata, unrelated box definitions or director statements.

## Proposed public shape
```typescript
interface BoxDevelopmentSpec {
  readonly format: 'boundscript/box-development-spec';
  readonly version: 1;
  readonly system: string;
  readonly box: string;
  readonly operation: {
    readonly name: string;
    readonly input: { readonly name: string; readonly type: ValueType };
    readonly resultType: ValueType | 'void';
    readonly postcondition?: Postcondition;
  };
}

type BoxSpecResult =
  | { readonly ok: true; readonly spec: BoxDevelopmentSpec; readonly diagnostics: readonly CompilationDiagnostic[] }
  | { readonly ok: false; readonly diagnostics: readonly CompilationDiagnostic[] };
```

## Acceptance criteria
- Extracting `Greeter` from `examples/structured-types.bound` produces a complete `User` input and `Greeting` result, including its `ensure result.message != ""` descriptor.
- A separate `LoadUser` spec includes its string input and resolved `User` output, even if that box is unused by the director in another valid program.
- Unknown box, invalid system, unknown/duplicate type or field, and invalid ensure produce failure diagnostics and no spec.
- The same selected box contract produces deeply equal specifications regardless of source whitespace or unrelated valid declarations; no host bindings required.
- Descriptor/type metadata exactly matches the corresponding declaration-derived metadata emitted by ordinary compilation when invoked.
- No changes to existing executable program semantics; `npm run check`, `npm run build` and existing demos pass.

## Out of scope
- JSON serializer/parser/decoder, CLI commands and export files (0013).
- Agent orchestration, prompts, task briefs, fixture generation, verifier execution, AI APIs, sandbox policies, code generation, hashes, signatures, or caching.
- New DSL syntax or type features, generalized IR or packages, changing compiler/runtime layering.

## Delivery
- Use a focused Conventional Commit containing `Assignment: 0012` and actual AI metadata per `AGENTS.md`.
- Include tests and documentation of the in-memory API. Do not modify the proposal or this assignment unless authorized.
- Report tests/build outcomes and commit hash. Do not push without explicit authorization.
