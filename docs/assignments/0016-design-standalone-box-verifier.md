# Assignment 0016 — Design Standalone Box Verifier

**Status:** Design approved by the Product Owner, subject to the recorded clarifications below. Implementation and its acceptance are tracked separately in Assignment 0017.
**Milestone:** [M1 — Standalone contract verification](../roadmap.md#m1--standalone-contract-verification)
**Direction:** [Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md), Sections 6, 9, 11, and 13.
**Scope:** Repository investigation and design only. This document does not authorize implementation.

## Objective and acceptance reference

Design the smallest verifier for a **trusted, explicitly supplied TypeScript function** and fixed input, using an existing portable Box specification without a source AST, compiler invocation, executable artifact, or director execution.

M1's completion criteria are: **valid cases pass; invalid inputs, candidate execution failures, invalid outputs, and postcondition failures are distinguishable; existing examples remain compatible.** This design contributes to M1 but does not complete it. Task derivation, pilot execution, behavioral acceptance infrastructure, integration reports, and promotion remain later work.

## Repository findings

### Specification and prior decisions

- [`BoxDevelopmentSpec`](../../packages/compiler/src/box-development-spec.ts) is compiler-owned, format `boundscript/box-development-spec`, version 1. It includes system/Box identity, operation and parameter names, resolved `ValueType` input, `ValueType | 'void'` output, and an optional `Postcondition`. The latter two descriptor types already belong to [`@boundscript/artifact`](../../packages/artifact/src/index.ts); no new contract language is needed.
- Extraction validates the whole source system and shares `resolveBoxOperation` with normal compilation. It does not need bindings, but source syntax still requires a director. The portable document has **no** director, AST, binding ID, implementation, or invocation input.
- [`box-spec-json.ts`](../../packages/compiler/src/box-spec-json.ts) already validates the entire portable envelope, identifiers, supported versions/types, duplicate fields, repeated-record schema consistency, and predicate compatibility. Unknown properties are rejected. Parsing returns `BoxSpecResult`; malformed JSON and invalid specs have separate diagnostic codes. Serialization throws `BoxSpecValidationError` on invalid data.
- Canonicalization fixes key order, sorts fields by code point, uses two-space indentation and one final LF. These rules do not need changing for verification. See the [format reference](../box-development-spec.md) and [published Greeter spec](../../examples/specs/greeter.box-spec.json).
- [Assignment 0012](0012-box-specification-extraction.md) established extraction/shared lowering; [Assignment 0013](0013-box-specification-portability.md) established the strict codec and export. Both deliberately excluded verifier execution. [Proposal 0012](../proposals/0012-box-development-spec.md) explicitly recommends a verifier using narrow runtime checks over existing artifact types, **not** making runtime depend on the compiler or synthesizing a director.
- [Approved decisions](../decisions.md#accepted-direction--proposal-0013) retain deterministic compilation, the existing backend, versioned spec semantics, and separate functional tasks/evidence. No LLM or implementation execution belongs in compilation or extraction.

### Runtime semantics and reuse points

All execution-time checks currently live privately in [`packages/runtime/src/index.ts`](../../packages/runtime/src/index.ts):

| Existing mechanism | Observed behavior / implication |
| --- | --- |
| `isValueType`, `isPostcondition` | Validate instruction descriptors and compatible string predicate targets before execution. These are less strict about document shape than the portable codec; they are not a replacement for it. |
| `valueTypeProblem`, `valueCategory` | No coercion; numbers must be finite. Records require own declared primitive fields, reject missing/wrong fields, null/arrays, and extra own keys (including symbols/non-enumerable extras). First problem is reported in descriptor order. |
| `assertBoundaryValue` | Adds implementation ID, Box/operation, direction, and expected type to the value-check problem, then throws `RuntimeExecutionError`. |
| Invocation branch | Checks input, calls/awaits the supplied function, checks the **entire** output, then evaluates the postcondition. A void operation must resolve to `undefined`. Records pass by reference. |
| `assertPostcondition` | Exact string equality against the forbidden literal; supports result or one declared string field only. Throws `PostconditionViolationError` on equality, with predicate and observed string. No `eval`. |
| Failure surface | Input/output failures and host failures are mostly message-only `RuntimeExecutionError`; only postcondition failures have a dedicated code and structured fields. Do not classify verification failures by parsing these messages. |

`BoundScriptRuntime.execute` additionally resolves artifacts, entrypoints, all implementation IDs, variables, and sequential director instructions. None is needed for one-function verification. Its `signal` checks run between instructions, not during a host call: they cannot terminate a hanging implementation.

Runtime currently depends only on `@boundscript/artifact`. Compiler's root entrypoint imports the language frontend, although the codec module itself has **only type-level imports**. Compiler's package exports currently expose only `.`. The JSON-only consumer test imports the codec's source file directly and forbids loading the language frontend. A public source-independent consumption path therefore needs an explicit export decision, not a runtime → compiler dependency.

### CLI and test coverage

- [`runBoundCli`](../../packages/cli/src/index.ts) supports `bound <source.bound>` and `bound spec <source.bound> --box <name>`. Export writes canonical JSON without bindings; execution supplies no Box implementations. There is no verify command, candidate loader, or TypeScript execution/transpilation facility. Retain both commands unchanged for this slice.
- [`box-development-spec.test.ts`](../../tests/box-development-spec.test.ts) covers extraction, unused declarations, whole-system errors, deterministic detached specs, and parity with compiled metadata.
- [`box-spec-json.test.ts`](../../tests/box-spec-json.test.ts), [`box-spec-json-consumer.test.ts`](../../tests/box-spec-json-consumer.test.ts), and [`box-spec-export.test.ts`](../../tests/box-spec-export.test.ts) cover strict decoding, canonical bytes, JSON-only consumption, and CLI success/failure.
- [`structured-types.test.ts`](../../tests/structured-types.test.ts) covers primitive/record boundaries, finite numbers, required own fields, no extras, nominal source-level compatibility, mutation/revalidation, and void results.
- [`behavioral-contracts.test.ts`](../../tests/behavioral-contracts.test.ts) covers synchronous/asynchronous results, output-before-predicate ordering, host versus predicate failures, escaped literals, descriptor rejection, and side effects without rollback. [`director-box-invocation.test.ts`](../../tests/director-box-invocation.test.ts) covers host binding/execution regressions.
- `vitest.config.ts` aliases package roots to source entrypoints. A new codec subpath must have an exact alias ahead of the compiler-root alias so tests do not accidentally load the frontend or map to a nonexistent nested `index.ts` path.

**Baseline verification performed during design:** `npm run check` passed (13 test files, 272 tests); `npm run build` passed; the director-box, box-composition, and structured-types demos each printed `Hello, World!`; `bound spec` output matched the published Greeter JSON byte-for-byte. These establish the current baseline, not evidence that a standalone verifier exists.

## Approved design — not yet implemented

### 1. Two-stage boundary, no new package

1. A trusted host reads JSON and calls the **existing strict decoder**. Failed decoding yields its existing structured diagnostics and never invokes the candidate.
2. A new `@boundscript/runtime` function receives the validated operation view, a trusted function, and a fixed input. It returns one invocation's conformance result.

Recommend a compiler subpath `@boundscript/compiler/box-spec` pointing to the existing codec module, exposing its existing functions/error class without importing the compiler root at execution time. Keep root exports compatible. Do not relocate the formal spec, codec, or artifact types. No runtime dependency on compiler, language, CLI, or filesystem is added.

The runtime parameter below is only a **structural consumer view**, not a second portable schema or independently versioned specification. A decoded `BoxDevelopmentSpec` is assignable to it directly; no interface regeneration or translation of type/predicate descriptors is required. The decoder remains responsible for format/version, system/parameter names, conflicting schemas, and exact envelope validation. The runtime view is not an alternative way to validate raw JSON.

### 2. Approved public API design

Planned exports from `@boundscript/runtime` (not implemented by this assignment):

```typescript
import type { Postcondition, ValueType } from '@boundscript/artifact';
// Reuse the existing runtime BoxImplementation type.

export interface BoxVerificationContract {
  readonly box: string;
  readonly operation: {
    readonly name: string;
    readonly input: { readonly type: ValueType };
    readonly resultType: ValueType | 'void';
    readonly postcondition?: Postcondition;
  };
}

export type BoxVerificationFailure =
  | { readonly kind: 'invalid-contract'; readonly message: string }
  | { readonly kind: 'invalid-implementation'; readonly message: string }
  | { readonly kind: 'invalid-input'; readonly expected: ValueType;
      readonly problem: string }
  | { readonly kind: 'execution-failure'; readonly message: string }
  | { readonly kind: 'invalid-output'; readonly expected: ValueType | 'void';
      readonly problem: string }
  | { readonly kind: 'postcondition-failure'; readonly predicate: Postcondition;
      readonly observed: string }
  | { readonly kind: 'inspection-failure';
      readonly phase: 'input' | 'output' | 'postcondition';
      readonly message: string };

export type BoxVerificationResult =
  | { readonly ok: true; readonly output: unknown }
  | { readonly ok: false; readonly failure: BoxVerificationFailure };

export function verifyBoxImplementation(
  contract: BoxVerificationContract,
  implementation: BoxImplementation<any>,
  input: unknown
): Promise<BoxVerificationResult>;
```

`BoxImplementation<any>` reuses the existing heterogeneous host-signature erasure and admits functions such as `(user: User) => Greeting`; it does **not** mean the input skips runtime validation. The result deliberately does not assert a TypeScript output type from a dynamic descriptor. Success always includes `output`, including `undefined` for void. It means only that this invocation passed the supported checks.

Use a discriminated `failure.kind` for machine classification; descriptive messages/problem strings are not a classification protocol. Return the first failure and no partial output on failure. Do not serialize arbitrary thrown values, full inputs, stack traces, or invalid outputs into the result. Successful output is the original value/reference, not a clone or durable evidence record. The host retains the associated spec and invocation context; the result introduces no candidate identity or promotion claim.

Intended host usage (proposed API, not available today):

```typescript
import { parseBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';
import { verifyBoxImplementation } from '@boundscript/runtime';
import { greet } from './trusted-greeter.js'; // Already compiled/imported by host.

const decoded = parseBoxDevelopmentSpec(json); // Host supplies JSON text.
if (!decoded.ok) {
  // Report decoded.diagnostics; do not execute a candidate.
} else {
  const result = await verifyBoxImplementation(decoded.spec, greet, {
    id: '123', name: 'World', active: true, score: 7
  });
  // A separate trusted test may assert expected functional output on success.
}
```

Raw JSON decoding intentionally retains `BoxSpecResult` rather than adding another JSON-verification wrapper/error vocabulary. Invalid JSON/spec is a **setup failure**, distinct from invalid invocation input. A host wanting a combined report can distinguish decoder diagnostics from the verifier union without interpreting strings.

### 3. Execution and failure ordering

1. Require a previously decoded/validated contract that the trusted caller does not mutate during verification. Defensively validate the runtime view's required identity fields and descriptor compatibility using the existing runtime descriptor guards; malformed views return `invalid-contract`. This is not full envelope validation: the runtime view does not inspect the portable format/version fields. The trusted host must enforce the decoder boundary; handing raw `JSON.parse` output directly to this function is not supported portable-spec verification.
2. Check `typeof implementation === 'function'`; otherwise return `invalid-implementation`. There is no registry, implementation ID, discovery, or module loading.
3. Check input with the shared value checker. On mismatch return `invalid-input`; the function must not run.
4. Call the candidate **once**, await it, and catch only that execution/await scope as `execution-failure`. Synchronous throws, rejected promises, and failed thenable assimilation all belong here. An implementation deliberately throwing `PostconditionViolationError` is still an execution failure, not a verifier-observed postcondition failure.
5. Check the entire resolved output using the same shared value rules. For void, require `undefined`. On mismatch return `invalid-output` and do not evaluate the predicate.
6. Evaluate the optional supported predicate with the shared evaluator. On equality return `postcondition-failure`; otherwise return success/output.

`inspection-failure` covers errors encountered while checking values during input/output checks or predicate access (for example, a throwing getter). It is not a proven contract violation, a proven type mismatch, or a candidate execution failure. Arbitrary JavaScript getters and mutable objects do not provide deterministic verification guarantees. Keep it stage-specific; do not use one broad catch that mislabels every exception. Descriptor objects originate in the strict decoder and must be ordinary trusted data. Hostile descriptor proxies, fatal process errors, and verifier programming defects are not promised structured outcomes.

### 4. Shared checks, not a second evaluator/runtime

Recommend factoring internal helpers into `packages/runtime/src/contract-checks.ts`:

- Move the existing primitive/record descriptor guards, predicate compatibility guard, `valueCategory`, and `valueTypeProblem` without semantic tightening. The director decoder and verifier import these same helpers.
- Add a small shared result-value helper for `ValueType | 'void'`, using `valueTypeProblem` plus the existing `undefined` rule. Both invocation paths use it rather than defining separate void behavior.
- Separate predicate **evaluation** from contextual throwing: a pure internal helper returns an observed violation (or none) using the existing target lookup and exact comparison. Runtime's assertion/error adapter still throws the existing `PostconditionViolationError`; the verifier maps the same observation to its structured failure. Evaluate only after full output validation and descriptor checks.
- Keep artifact/entrypoint/variable handling, implementation-registry resolution, runtime errors, and public error formatting in the existing runtime path. Preserve existing error messages/classes/codes and failure ordering. Do not route director execution through a fake portable spec or classify errors using `instanceof` across candidate execution.

The verifier adds only one-function invocation/stage-result glue over those shared semantics, not another interpreter or independent contract engine. Keep helpers internal unless another concrete public use appears. Shared helpers should not import `index.ts`, preventing cycles with runtime public exports/errors.

## Compatibility and limitations

- No changes to spec version 1, canonical bytes, director instruction version 4, artifact envelope version 1, source grammar, compiler bindings, or `BoundScriptRuntime.execute` API. Existing root exports remain available.
- Published structured Greeter JSON can be decoded and checked against the shipped `greet` directly. LoadUser's async implementation and Display's void contract use the same path with fixed trusted inputs; simple string Greeter functions remain valid. Tests may prepare additional portable fixtures, but standalone verification itself must not read `.bound` source or compile anything.
- Runtime values do not carry nominal record tags. Named identity is retained in descriptors and checked between declarations/portable schemas, **not proved from an arbitrary JavaScript object**. Identically shaped objects cannot reveal their originating named type. Do not add branding or stronger guarantees here.
- Existing runtime value checks are not the codec's plain-data restrictions: class instances/prototypes/accessors are not categorically rejected if existing own-field rules pass. Property reads can execute getters; extras are detected via own keys. Preserve behavior rather than silently tightening spec semantics. Stateful getters/proxies and mutation during checking cannot yield a stable proof of a value's behavior.
- The host supplies an already compiled/imported trusted function, JSON, and ordinary fixed values. No TypeScript compiler, import resolver, candidate file loader, source signature analysis, fixture generator, or CLI verify command is proposed.
- Passing conformance does not verify intended business behavior, algorithms, purity, dependencies, capabilities, security, integration, or all possible inputs. A wrong greeting can satisfy a nonempty-message postcondition. Trusted external tests must establish functional expectations separately; no behavioral-test callback or general acceptance runner is added in this slice.
- In-process execution has application privileges. Side effects may occur before output/predicate failure; no rollback, immutability, copying, resource limits, timeout, cancellation, or isolation is provided. An unresolved promise or infinite loop can hang the host. Never use this entrypoint for untrusted generated code inside the trusted development process.
- Explicit predicates/checks are deterministic for stable values and fixed rules; arbitrary candidate code, external state, and getters need not be deterministic. Results are per-invocation observations, not reproducible build/provenance or promotion evidence. No candidate hashes, task/test identity, stale-evidence detection, or M4 reporting is included.

## Required source changes for a later implementation

**None of these changes are performed by Assignment 0016.** After approval, the expected minimal implementation footprint is:

| File | Proposed change |
| --- | --- |
| `packages/runtime/src/contract-checks.ts` (new) | Internal shared descriptor/value/result/predicate checks extracted from the current runtime. |
| `packages/runtime/src/box-verifier.ts` (new) | Public consumer view/result types and one-invocation verification function; imports shared helpers and existing types only. |
| `packages/runtime/src/index.ts` | Reuse helpers in current director execution, retain legacy error adapters, export verifier API. Use a type-only import for `BoxImplementation` if needed to avoid a runtime cycle. |
| `packages/compiler/package.json` | Add `./box-spec` exports for existing `dist/box-spec-json.js` and its declarations; retain `.`. No new dependency. |
| `vitest.config.ts` | Exact codec-subpath source alias before the compiler root alias. |
| `tests/box-verifier.test.ts` (new) | Functional stage/failure tests and supported-type coverage. |
| `tests/box-verifier-consumer.test.ts` (new) | Published-JSON + trusted fixture consumption with language/frontend/compiler execution/director execution prohibited. |
| `tests/box-verifier.types.ts` (new) | Consumer-view assignability, heterogeneous functions, result narrowing, no success output on failure. Existing type-test include pattern already covers it. |
| Existing runtime/codec tests | Add parity/edge regressions where current cases do not cover shared-check extraction; retain existing assertions. Update JSON-only consumer to exercise the new public subpath. |
| `docs/box-development-spec.md`, `README.md` | Explain decode-then-verify usage, result categories, and trusted-only limits once implemented; remove only statements then superseded by actual implementation. |
| `docs/roadmap.md` | Track implementation assignment/evidence when authorized; do not complete M1 on design delivery. |

No artifact-package API, spec type/codec implementation, compiler lowering, language, CLI, sandbox, package dependency graph, or example behavior change is expected. If the implementation reveals a need for those changes, return for approval rather than expanding scope.

## Concrete test matrix for implementation

| Area | Cases | Expected assertion |
| --- | --- | --- |
| Strict decode/setup | Malformed JSON, wrong format/version, unknown/missing keys, unknown types, conflicting schemas, duplicate fields, void/incompatible/unknown predicates | Existing decoder diagnostics; no candidate execution, no spec on failure. Reuse existing codec tables, not a second schema implementation. |
| Runtime-view misuse | Invalid input/result descriptor, missing operation identity, incompatible/unknown predicate, predicate on void | `invalid-contract`; no candidate call. Portable document validation still precedes this guard. |
| Candidate registration | Non-function supplied from JS/type-cast test | `invalid-implementation`; no execution. |
| Primitive inputs/outputs | String (including empty), finite number (including 0), boolean (including false); wrong primitive, null, undefined, boxed primitive, numeric string, NaN, ±Infinity | Correct values pass without coercion; mismatches identify input vs output; invalid input call count is zero. |
| Record inputs/outputs | Complete flat record; empty record schema; null/array; absent/inherited required field; wrong field category; non-finite numeric field; extra string/symbol/non-enumerable own key | Shared own-field/no-extra semantics; first problem retained; invalid input prevents call, invalid output prevents predicate. |
| Value representation parity | Null-prototype record, class instance with exact own fields, inherited extras, own accessor; throwing input/output getter | Preserve legacy acceptance/rejection; throwing getter gives phase-specific `inspection-failure` in verifier. No new plain-object restriction. |
| Candidate execution | Sync return, async return, sync throw, rejected promise, non-Error thrown value, thrown runtime/postcondition error, rejecting thenable | Exactly one call and awaited completion; candidate-origin errors always `execution-failure`. |
| Void | Sync implicit return, explicit/async undefined; null/string/object result | Success always has `output: undefined`; non-undefined is `invalid-output`. |
| Predicates | Result and string field, equal/not equal to empty and nonempty escaped literals, predicate absent | Exact forbidden-literal comparison; descriptor/observed string on failure; no expression evaluation. |
| Ordering | Bad input plus throwing candidate; bad full record output plus failing predicate; valid string field but invalid unrelated output field | Input failure wins without execution; full output failure wins over predicate; no later stage runs. |
| Predicate access failure | Controlled trusted getter passes type read then throws on predicate read | `inspection-failure` with `phase: 'postcondition'`, not execution/type/postcondition mismatch. Document unstable getters as a limitation. |
| References/mutation | Candidate receives the same record reference and returns a reference; mutate input then verify again | No implicit cloning/freezing; next invocation rechecks input. No immutability/rollback claim. |
| Published JSON consumer | Decode `examples/specs/greeter.box-spec.json`, invoke shipped `greet` with fixed User, then variants producing empty message/malformed Greeting | Success, predicate failure, output failure respectively, with no `.bound` source, AST, bindings, artifact, compiler call, or director execution. |
| Existing implementations | Trusted simple Greeter, async LoadUser, void Display-style fixture | Existing valid operation shapes remain usable; external assertions check expected functional output. |
| Independent import boundary | Public codec subpath plus runtime with frontend/compiler-root execution blocked; built Node import smoke check | No Langium/frontend loading; package exports work beyond Vitest aliases. |
| Legacy parity | Feed equivalent descriptors/values to artifact runtime tests and verifier (AST/artifacts only in parity-test setup) | Same pass/fail semantics and ordering; existing runtime error messages/classes/codes unchanged. |
| Result contract/types | Each failure kind, successful output including undefined, decoded spec assignability, string/User host functions, discriminated result narrowing | No message parsing, no output field on failed results, no false static output guarantee. |
| Regression | `npm run check`, `npm run build`, all existing demos and canonical CLI export | All prior checks pass; published JSON and CLI behavior unchanged. |

Do not run an actual infinite loop or hang the test suite to demonstrate missing limits. Document timeout/isolation as unsupported instead. No new tests are added in this design-only delivery.

## Product Owner approval and clarifications

The Product Owner reviewed and approved this M1 design with the following binding clarifications. These resolve the design decisions previously awaiting approval; they authorize preparation of [Assignment 0017 — Implement Standalone Box Verifier](0017-implement-standalone-box-verifier.md), not production implementation yet.

1. **Two-stage API/import boundary:** Use the existing strict portable-spec decoder followed by the standalone runtime verifier. Expose the codec through `@boundscript/compiler/box-spec` without loading the language frontend. Keep runtime independent of compiler/language.
2. **One set of semantics:** Reuse existing runtime descriptor, value, void-result, and postcondition semantics. Do not create a second contract evaluator or change legacy runtime behavior.
3. **Structured results and inspection errors:** Use the discriminated verification result, including `inspection-failure`. Inspection failures are errors encountered while checking values, not proven contract violations. Arbitrary JavaScript getters and mutable objects do not provide deterministic verification guarantees.
4. **Consumer view only:** `BoxVerificationContract` is a structural consumer view of the existing `BoxDevelopmentSpec`, not a second authoritative contract model, serialized format, or versioned schema.
5. **Single trusted invocation:** M1 covers one invocation with a fixed input and a trusted, already-loaded TypeScript function. No candidate loader, CLI verify command, agent integration, behavioral acceptance runner, sandbox, or isolation implementation.
6. **Preserve live-object behavior:** Retain existing runtime object/reference semantics. Do not add cloning, freezing, nominal record branding, or stricter plain-object rules.

### Remaining implementation risks and authorization boundary

Shared-check extraction must retain legacy error messages, classes, codes, ordering, and object behavior; parity/regression tests are required. The source-independent codec export needs both source-alias and built-package import checks. Per-invocation results remain observations, not deterministic guarantees for arbitrary JavaScript or acceptance/provenance evidence.

No architectural decision remains pending among the choices above. Any newly discovered need to change semantics or expand scope must return to the Product Owner. Assignment 0017 was prepared separately for review; this design approval alone did not authorize implementation, commits, or pushes. Subsequent implementation authorization and delivery are tracked under Assignment 0017. Proposals 0012/0013 remain unchanged.
