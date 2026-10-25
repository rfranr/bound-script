# Portable Box Development Specification — Version 1

This is a **declared contract**, not a complete implementation brief. A nonempty greeting message does not specify what greeting to produce. A human-authored task and independent examples/tests are still required. Do not infer business intent from box names or director invocations. Exporting this document does not generate, execute, verify, or approve implementations, and grants no sandbox capabilities.

## Export and public APIs

After installing dependencies, from the repository root:

```bash
npm run --silent bound -- spec examples/structured-types.bound --box Greeter
```

The command builds the existing CLI, sends build output to stderr, and writes only UTF-8 JSON to stdout. `--silent` suppresses npm's command banner. A reference document is maintained at [`examples/specs/greeter.box-spec.json`](../examples/specs/greeter.box-spec.json); tests require the export to match it exactly. Redirect stdout if a local export file is needed.

`bound spec <source.bound> --box <name>` parses and validates the entire system, including unused declarations. It exports unused boxes too and never requires implementation bindings or host functions. Invalid arguments/source or unknown selections return a non-zero status, diagnostics on stderr, and no JSON on stdout. Source diagnostics retain file/line/column where available. Existing `bound <source.bound>` execution is unchanged.

The compiler package exports pure synchronous functions:

```typescript
extractBoxDevelopmentSpec(system: SystemNode, boxName: string): BoxSpecResult;
serializeBoxDevelopmentSpec(spec: BoxDevelopmentSpec): string;
parseBoxDevelopmentSpec(json: string): BoxSpecResult;
```

`@boundscript/compiler/box-spec` exposes `parseBoxDevelopmentSpec`, `serializeBoxDevelopmentSpec`, and `BoxSpecValidationError` without loading the compiler root, language frontend, or Langium at execution time. Existing compiler-root exports remain compatible. The codec does no I/O and does not parse BoundScript, compile an artifact, or load implementations. A consumer needs only the JSON document and this format, not the original system/source. The codec implementation has only type-level dependencies on the existing compiler/artifact contracts.

**Error contract:** Parsing returns `{ ok: true, spec, diagnostics: [] }` or `{ ok: false, diagnostics }`, never a partial spec. Malformed JSON uses `compiler.box-spec.invalid-json`; invalid/unsupported specification data uses `compiler.box-spec.invalid-spec` with a JSON-style property path in the message. These are document diagnostics, not source ranges. Serialization also validates first and throws exported `BoxSpecValidationError`, whose readonly `diagnostics` carry the latter code; it never silently removes unsupported data or mutates the input. Both boundaries report the first validation error.

## Exact document shape

Only these properties are allowed; every unmarked property is required:

- Root: `format: "boundscript/box-development-spec"`, `version: 1`, `system`, `box`, `operation`.
- `operation`: `name`, `input`, `resultType`, optional `postcondition`.
- `input`: `name`, `type`.
- A value type is the string `"string"`, `"number"`, or `"boolean"`, or `{ "kind": "record", "name": <identifier>, "fields": [...] }`.
- Each record field is exactly `{ "name": <identifier>, "type": <primitive-type-string> }`. Names are unique within a record; an empty record schema is allowed. Records are inline and fully resolved, never bare named references. Repeated definitions of one record name must have identical fields/types regardless of field order. Different record names retain distinct nominal identity.
- `resultType` additionally permits `"void"`; input/field types never do. Record names cannot equal built-in type names.
- `postcondition` is exactly `{ "kind": "string-not-equal", "target": <target>, "value": <string> }`. A target is `{ "kind": "result" }` for a string result, or `{ "kind": "field", "name": <identifier> }` for a declared string field of the result record. Void results forbid postconditions. No other predicate or target is supported.

System, box, operation, parameter, record, and field names follow `[A-Za-z_][A-Za-z0-9_]*`. No implicit conversions, missing required properties, unknown properties/versions/variants, nested schemas, optional fields, or arrays as value types are accepted. Arrays are used only to list field declarations. An optional property must be absent, not present with `undefined` or `null`.

Serialization accepts ordinary data objects (including null-prototype objects), dense ordinary field arrays, and supported primitive values. It rejects functions, class instances, symbol/extra/non-enumerable properties, accessors, sparse/customized arrays, and JSON hooks rather than invoking or dropping them. This is data validation, not protection against executing hostile JavaScript objects such as proxies; no sandbox claim is made.

## Contract semantics

- `number` means a finite JavaScript number, not a numeric string, `NaN`, or infinity. Strings and booleans likewise require their actual primitive categories.
- Runtime record values require their declared fields as **own properties**, with the declared primitive types and no extra fields. Null and arrays are not records. Record identity is nominal, scoped by the originating system, with no coercion.
- Void means an implementation returns `undefined`, possibly through an awaited promise. The spec describes a category; it does not encode an `undefined` JSON value.
- Implementations may be synchronous or asynchronous. Inputs are checked before invocation; the **entire output type is validated before the postcondition**, then the result is made available to subsequent statements. String inequality is an exact, non-coercing comparison against the decoded literal, not executable expression text.
- Host exceptions, data-contract failures, and postcondition violations remain distinct. A contract cannot establish unstated functionality, guarantee universal correctness from finite tests, prevent side effects, or roll them back.

## Canonical text and versioning

Serialization reconstructs the shape above with fixed key order: root `format/version/system/box/operation`; operation `name/input/resultType/postcondition`; input `name/type`; record `kind/name/fields`; field `name/type`; predicate `kind/target/value`; target `kind/name` where applicable. Fields are sorted by identifier in code-point order (`Z` before `_` before `a`), not locale order. Other array orders do not exist in this format.

Text uses `JSON.stringify` string escaping, two-space indentation, LF line endings, and **exactly one final LF**. The CLI writes that text as UTF-8. No timestamps, source paths, ASTs, bindings, implementation code, or provider metadata are included. Key/field order and input whitespace do not affect canonical bytes. Parsing normalizes key/field order; canonical documents round-trip byte-for-byte, while noncanonical valid JSON is normalized on serialization.

Spec version 1 is independent of director instruction version 4 and executable-artifact envelope version 1. Unsupported spec versions and variants fail explicitly; evolving this format or its normative semantics requires an explicit version decision, not silently accepting new keys. There is no agent runner, general schema framework, code generator, or implementation discovery in this feature. Standalone verification is a separate runtime API described below.

## Standalone verification

Use the existing strict decoder first, then `verifyBoxImplementation` from `@boundscript/runtime` with a trusted, already-loaded function and one fixed input. The [README example](../README.md#standalone-box-verification) demonstrates the published Greeter contract and implementation. No source AST, compiler call, binding, artifact, or director execution is required. Invalid JSON/spec setup returns the codec's existing structured diagnostics; the host must not invoke a candidate after decoding failure.

```typescript
import { parseBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';
import { verifyBoxImplementation } from '@boundscript/runtime';
import { greet } from './trusted-greeter.js'; // Already built and loaded by the host.

const decoded = parseBoxDevelopmentSpec(json); // Host-supplied portable JSON text.
if (!decoded.ok) {
  // Report decoded.diagnostics; do not execute the function.
} else {
  const result = await verifyBoxImplementation(decoded.spec, greet, {
    id: '123', name: 'World', active: true, score: 7
  });
  if (result.ok) {
    // result.output is unknown, or undefined for a successful void operation.
    // Apply human-owned functional assertions separately.
  } else {
    // Classify with result.failure.kind, not by parsing its descriptive message.
  }
}
```

The public signature is:

```typescript
verifyBoxImplementation(
  contract: BoxVerificationContract,
  implementation: BoxImplementation<any>,
  input: unknown
): Promise<BoxVerificationResult>;
```

`BoxVerificationContract` is a readonly structural consumer view containing `box` and `operation` (`name`, `input.type`, `resultType`, optional `postcondition`), with the existing artifact `ValueType` and `Postcondition` descriptors. A decoded `BoxDevelopmentSpec` is directly assignable. The view is **not another authoritative contract model, serialized format, or versioned schema**. Its defensive descriptor/identity guard does not validate the portable envelope, format/version, system/parameter names, or conflicting schemas. Do not pass raw `JSON.parse` output instead of strict decoding. The trusted host must keep the decoded contract stable during verification.

The verifier checks the consumer view, callability, then input; invokes/awaits the function once; checks the entire resolved output (including void); then checks the optional predicate. Director execution and standalone verification share the same internal descriptor, value, void-result, and postcondition semantics. Existing director errors and behavior remain unchanged.

### Structured results

Success is `{ ok: true, output: unknown }`, always including `output` even when it is `undefined`. Failure is `{ ok: false, failure }`, with no partial output. The first failed stage wins:

| `failure.kind` | Fields and meaning |
| --- | --- |
| `invalid-contract` | `message`: malformed runtime consumer view/descriptors; not full portable-spec validation. |
| `invalid-implementation` | `message`: candidate is not callable. |
| `invalid-input` | `expected: ValueType`, `problem: string`: input value mismatch; candidate did not run. |
| `execution-failure` | `message`: candidate threw/rejected or failed during awaiting. Even a candidate-thrown `PostconditionViolationError` stays an execution failure. |
| `invalid-output` | `expected: ValueType` or `'void'`, `problem: string`: resolved output mismatch; predicate was not evaluated. |
| `postcondition-failure` | `predicate: Postcondition`, `observed: string`: a structurally valid output's result/field equaled the forbidden string. |
| `inspection-failure` | `phase: 'input'`, `'output'`, or `'postcondition'`, and `message`: error encountered while checking a value, such as a throwing getter. **Not a proven contract violation or type mismatch.** |

Failure results do not embed arbitrary thrown objects, stack traces, full inputs, or invalid outputs. Successful output retains its original reference and is not a durable evidence record. Descriptive messages/problem strings are not the machine-classification protocol. Hostile descriptor proxies, fatal process failures, and verifier defects are not promised structured outcomes.

### Guarantees and limits

- One successful invocation establishes only the supported checks on the supplied values. External tests remain responsible for intended behavior. The verifier cannot prove arbitrary business behavior, algorithms, dependency/capability compliance, integration correctness, or correctness for all inputs.
- No copying/freezing, nominal branding, or new plain-object restrictions: existing own-field/no-extra checks still apply to class instances, prototypes, accessors, and null-prototype objects. Arbitrary getters and mutable objects do not provide deterministic verification guarantees; property reads can execute code or observe changing values. Runtime objects cannot prove their originating nominal record type merely from their shape.
- Trusted code executes in-process with host privileges. Side effects can precede output/postcondition failure, with no rollback. No timeout, cancellation, resource-limit enforcement, sandbox, or isolation is provided. A hanging function can hang the host. Do not execute untrusted generated code in the trusted development process.
- The host supplies already-loaded code and handles file I/O/functional assertions. No candidate loader, TypeScript transpilation service, CLI verify command, agent integration, behavioral acceptance runner, task derivation, promotion, or provenance/evidence framework is included.
