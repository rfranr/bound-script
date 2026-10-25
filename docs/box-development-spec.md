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

The codec does no I/O and does not parse BoundScript, compile an artifact, or load implementations. A consumer needs only the JSON document and this format, not the original system/source. The codec implementation has only type-level dependencies on the existing compiler/artifact contracts.

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

Spec version 1 is independent of director instruction version 4 and executable-artifact envelope version 1. Unsupported spec versions and variants fail explicitly; evolving this format or its normative semantics requires an explicit version decision, not silently accepting new keys. There is no agent/verifier runner, general schema framework, code generator, or implementation discovery in this feature.
