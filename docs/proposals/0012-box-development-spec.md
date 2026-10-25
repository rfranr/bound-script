# Proposal 0012 — Box Development Specification

**Status:** Proposal only. No implementation or orchestration is introduced.

## Recommendation and current architecture

Add a **pure box-specification extractor in `@boundscript/compiler`**, separate from `BoundScriptCompiler.compile`. Export one versioned JSON document describing one declared box, using the existing `ValueType` and `Postcondition` data contracts from `@boundscript/artifact`. No new package, language syntax, or intermediate language is needed.

Today, the language frontend validates primitive/flat-record interfaces and single string-inequality postconditions. The compiler resolves these into director instructions; the runtime checks inputs, awaits implementations, checks output types, then checks postconditions. Explicit host bindings remain outside the source contract. These are suitable foundations, but **do not extract the specification from an executable artifact**: compilation requires bindings, unused boxes have no instructions, and invocation instructions do not retain the declared parameter name.

This follows [the architecture](../architecture.md) and [existing decisions](../decisions.md): deterministic preparation and compilation are separate from obtaining implementations.

## Responsibilities

- **Language frontend:** Own syntax, reference/type checks, and source-located diagnostics. No prompts, implementation discovery, or provider calls.
- **Compiler module:** Validate the supplied system, select a box, resolve its interface and postcondition, and construct/serialize the specification. Require neither bindings nor implementation functions. Reuse a small internal declaration-resolution helper with normal compilation rather than maintaining two lowering rules.
- **Build-time host script:** Give the exported specification, a human-authored task, and a small TypeScript workspace to an agent or developer. Run tools, manage candidate files, request review, and choose implementation IDs. The first experiment can be manually orchestrated; no agent SDK abstraction is required.
- **Independent verifier:** Consume the same specification and separately supplied candidate/tests, not an agent's claims, transcript, or private context. Check the specification before trusting it. A concrete verifier awaits the candidate and applies input validation → host call → output validation → postcondition validation. It reports host, data-contract, and postcondition failures separately. Passing finite tests is evidence, not proof of all behavior.
- **Runtime:** Remain independent of the compiler, agent, and development-spec envelope. Continue executing explicitly bound artifacts; no development metadata enters `ExecutableArtifact`.

## Data structure

Proposed compiler export; `ValueType` and `Postcondition` below are the **existing aliases**, not parallel schemas:

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
    readonly postcondition?: Postcondition; // Forbidden for void; validated on decode
  };
}
```

For example, extracting `Greeter` from the structured-types demo includes its parameter name `user`, the complete inline `User` and `Greeting` field schemas, and:

```json
{"kind":"string-not-equal","target":{"kind":"field","name":"message"},"value":""}
```

**Self-contained means all declared contract dependencies are resolved.** Include only input/output record definitions, inline as existing `ValueType` descriptors; no external type registry or source lookup is needed. Preserve system/type names and nominal identity. Exclude director code and invocation arguments, unrelated declarations, implementation IDs/paths, AST/CST nodes, source paths, timestamps, prompts, model metadata, and sandbox policy.

Version 1 fixes the current semantics: finite numbers; required own primitive record fields with no extras, rejecting null/arrays as records; no coercion; `undefined` for void; synchronous or asynchronous host results; output type validation before the supported postcondition. A specification contains no runtime values, so void does not require a JSON encoding of `undefined`. Unknown versions, types, descriptor variants, incompatible targets, duplicate fields, and conflicting schemas for the same named type are errors, not ignored extensions. Changes to these semantics require an appropriate spec-version change; do not equate its version with director instruction version 4.

Serialize with fixed object-key order, fields sorted by identifier using code-point order, and a fixed newline convention. Omit absent postconditions. Whitespace and unrelated valid declarations must not change the selected spec's bytes. No hash, signature, cache key, or universal canonical-JSON framework is needed initially.

### Important limit: declared contracts are not complete intent

A nonempty `Greeting.message` does **not** specify how to greet a user. The extractor must not invent that behavior from box names, director calls, or an AI interpretation. The first real development task also needs a human-owned brief and input/expected-output fixtures, supplied to both developer and verifier outside this contract document. Keep these as ordinary task files/Vitest tests, not a new testing DSL or opaque metadata bag. A spec-only verifier can check declared conformance, not unstated application correctness.

## Public APIs and independence

Proposed exports from `@boundscript/compiler`:

```typescript
type BoxSpecResult =
  | { readonly ok: true; readonly spec: BoxDevelopmentSpec;
      readonly diagnostics: readonly CompilationDiagnostic[] }
  | { readonly ok: false; readonly diagnostics: readonly CompilationDiagnostic[] };

extractBoxDevelopmentSpec(system: SystemNode, boxName: string): BoxSpecResult;
serializeBoxDevelopmentSpec(spec: BoxDevelopmentSpec): string;
parseBoxDevelopmentSpec(json: string): BoxSpecResult;
```

Extraction runs existing whole-system semantic validation and reports an identifiable unknown-box error if selection fails. No partial spec is returned on error. This deliberately means an invalid unrelated declaration/director can block extraction; selected-box-only validation is unnecessary for the first valid-system experiment. An unused but valid box is extractable. Serialization validates the document rather than silently dropping unsupported data; parsing validates structure and contract compatibility. Neither performs I/O or calls a host implementation.

An external verifier needs only the JSON format, documented semantics, and conformance fixtures—not Langium or a compiler instance. An in-repository verifier can later reuse narrow exports of the runtime's existing value/postcondition checks, taking existing artifact types rather than this compiler-owned envelope. Do not add a second evaluator, make the runtime depend on the compiler, or synthesize a fake director merely to verify one result. Assignment 0012 need not introduce a candidate-execution API or verifier service.

## Alternatives and trade-offs

- **New `box-spec`, contract-engine, or agent package:** Premature ownership/dependency machinery for a small document and three functions. Start in the compiler; extract a package only when an actual independent consumer needs it.
- **Raw AST/source slice:** Smaller exporter, but not self-contained: it exposes parser machinery and requires consumers to resolve types and reinterpret semantics.
- **Executable artifact or general resolved-system IR:** Couples development to bindings/director execution or creates a second language. Export only one operation's existing contract descriptors.
- **JSON Schema plus predicate text:** Adds a translation/dependency and still cannot safely express the existing postcondition without another convention. Reusing current descriptors reduces semantic drift; the trade-off is a BoundScript-specific consumer format.
- **Inline records instead of a named-type table:** Minor duplication when input/output share a record, but no reference-resolution protocol. Decoder consistency checks retain named identity.

## Future isolation, without premature sandbox design

The spec is a portable data input to a future isolated worker. Keep execution policy in the **host's** workspace/runner configuration: allowed tools, filesystem/network access, credentials, timeouts, and resource limits. `SandboxPolicy` currently describes restrictions but enforces nothing. Neither a spec nor a prompt grants capabilities. Candidate code must not edit the authoritative spec or verifier fixtures; later enforcement should mount/copy these separately from its writable implementation workspace. Do not execute untrusted candidate code in-process or claim that a Node child process alone is a sandbox.

Defer worker protocols, container choice, capability manifests, provider adapters, retry planners, implementation registries, provenance systems, and automated approval. For the first run, use a trusted/reviewed candidate and the existing explicit host binding; keep generation logs and verification reports outside both the spec and runtime artifact.

## Minimal implementation plan

1. Add the compiler-owned spec type, extractor, serializer, and strict decoder; share only existing declaration-to-contract lowering with compilation. Do not change the DSL, runtime artifact envelope, or binding API.
2. Test primitive/void/record extraction, postconditions, unused-box selection, missing/duplicate/invalid declarations, deterministic bytes, unknown versions, and malformed descriptors. Assert parity with contracts emitted by ordinary compilation and absence of ASTs, functions, bindings, and unrelated source context.
3. Add a small export example for the existing structured `Greeter`; round-trip it through a JSON-only consumer test. Document the format's semantics and the separate human task/fixture requirement. No new dependency or general CLI plugin mechanism.
4. For the first real development experiment, manually hand that JSON and a fixed TypeScript task/test workspace to an agent. Independently review/test its candidate, then register it in the existing host and run the real pipeline. Automate orchestration or extract reusable verifier checks only when this concrete run demonstrates the need.

**Success:** one box's declared contract can be exported before any implementation exists, understood without the rest of the program, and used unchanged by developer and verifier—while compilation stays deterministic and implementation acquisition stays outside it.
