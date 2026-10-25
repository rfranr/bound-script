# Assignment 0017 — Implement Standalone Box Verifier

**Status:** Completed
**Milestone:** [M1 — Standalone contract verification](../roadmap.md#m1--standalone-contract-verification)
**Design:** [Assignment 0016](0016-design-standalone-box-verifier.md), including its Product Owner approval and clarifications.
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md).

## Objective

Implement the approved minimal standalone verifier for one invocation of a trusted, already-loaded TypeScript function with a fixed input against an existing portable Box contract. Verification must require neither a BoundScript source AST nor compiler/artifact/director execution.

M1's acceptance criteria are: **valid cases pass; invalid inputs, candidate execution failures, invalid outputs, and postcondition failures are distinguishable; existing examples remain compatible.** Completing this assignment does not automatically complete M1 or approve any candidate for application use.

## Prerequisites and authority

- Assignment 0016's architecture is approved with its six recorded clarifications. This assignment translates that design into implementation requirements; it does not add a new architecture.
- Reuse the existing specification and strict codec established by Assignments [0012](0012-box-specification-extraction.md) and [0013](0013-box-specification-portability.md).
- Implementation must wait for explicit Product Owner authorization. Do not implement production code, commit, or push during review of this proposal.

## Requirements

### 1. Portable-spec boundary and package exports

1. Expose the existing codec through `@boundscript/compiler/box-spec`, with JavaScript and declaration exports for `parseBoxDevelopmentSpec`, `serializeBoxDevelopmentSpec`, and `BoxSpecValidationError`. Preserve existing compiler root exports.
2. The codec subpath must not load the compiler root, language frontend, or Langium at execution time. Reuse the existing codec rather than copying validation rules or moving the authoritative spec/codec into another package.
3. The trusted caller decodes portable JSON first. Malformed JSON or invalid specifications retain existing `BoxSpecResult` diagnostics and prevent candidate execution. Do not add another combined JSON-verification API or replace decoder diagnostics.
4. Runtime remains independent of compiler/language. No new package, dependency, serialized format, or spec-version change.

### 2. Standalone runtime API

Export `verifyBoxImplementation`, `BoxVerificationContract`, `BoxVerificationFailure`, and `BoxVerificationResult` from `@boundscript/runtime`, using the signatures in Assignment 0016.

```typescript
verifyBoxImplementation(
  contract: BoxVerificationContract,
  implementation: BoxImplementation<any>,
  input: unknown
): Promise<BoxVerificationResult>;
```

- `BoxVerificationContract` must remain a structural consumer view: `box` plus `operation.name`, `operation.input.type`, `operation.resultType`, and optional `operation.postcondition`, using existing artifact descriptor types. A decoded `BoxDevelopmentSpec` must be directly assignable. This is not an authoritative contract model, serialized format, or versioned schema.
- Reuse existing `BoxImplementation` signature erasure so both string-input and record-input functions are accepted; never skip runtime input validation because of TypeScript annotations.
- Return `{ ok: true, output: unknown }` on success, always including `output` even when it is `undefined`. Return `{ ok: false, failure }` without partial output on failure. Preserve the exact failure union and associated fields specified in Assignment 0016:

| `failure.kind` | Structured fields |
| --- | --- |
| `invalid-contract` | `message` |
| `invalid-implementation` | `message` |
| `invalid-input` | `expected: ValueType`, `problem` |
| `execution-failure` | `message` |
| `invalid-output` | `expected: ValueType \| 'void'`, `problem` |
| `postcondition-failure` | `predicate: Postcondition`, `observed: string` |
| `inspection-failure` | `phase: 'input' \| 'output' \| 'postcondition'`, `message` |

Classify by the discriminant, not by message parsing. Do not include arbitrary thrown objects, full input values, invalid outputs, or stack traces in failure results. Success is an invocation-level observation, not application acceptance or provenance evidence.

### 3. Shared semantics and ordered execution

1. Defensively check the runtime consumer view's required identity fields and descriptor compatibility, reusing existing runtime descriptor guards. Return `invalid-contract` for malformed views before calling the candidate. This does not validate the portable envelope/version: document that the host must first use the strict decoder and must not mutate the contract during verification.
2. Check candidate callability; return `invalid-implementation` for a non-function supplied by JavaScript or an unchecked cast.
3. Validate input with the shared value checker; on mismatch return `invalid-input` without calling the function.
4. Invoke the function exactly once and await it. Synchronous throws, rejected promises, and rejected thenable assimilation are `execution-failure`. Restrict this catch to candidate execution/awaiting: even a candidate-thrown `PostconditionViolationError` is an execution failure.
5. Validate the entire resolved output before evaluating any predicate. Wrong primitive/record values or a non-`undefined` void result return `invalid-output`.
6. Evaluate the supported postcondition with the shared evaluator only after successful output validation. Exact equality with the forbidden string produces `postcondition-failure`; otherwise return the original output/reference.
7. Errors encountered while checking values must produce `inspection-failure` with the correct stage. These are **not proven contract violations**. Arbitrary getters and mutable objects do not provide deterministic verification guarantees. Do not use one broad catch that reclassifies all errors as candidate failures.

Extract internal shared descriptor/value/void-result/predicate helpers from the current runtime as described in Assignment 0016. Both director execution and verification must use the same implementations. Keep legacy runtime error adapters/context and preserve its messages, classes, codes, failure order, and exception behavior. Do not create a second evaluator, a new runtime interpreter, or a synthetic director program for verification.

Preserve existing own-field/no-extra-field checks, finite numbers, no coercion, exact string predicate comparison, and `undefined` for void. Retain live-object behavior, including existing treatment of prototypes, accessors, and record references. Do not clone, freeze, brand records, or tighten plain-object rules. Internal helpers need not become public exports.

### 4. Documentation

Update `README.md` and `docs/box-development-spec.md` after implementation to show strict decoding followed by standalone verification through public entrypoints. Explain every failure kind, especially inspection errors versus proven mismatches, and retain the distinction between declared conformance and external functional acceptance tests.

Document trusted-only execution, live references/mutation, getter-related nondeterminism, possible side effects before failure, no rollback, no enforced timeout/cancellation/resource limits, and no sandbox/isolation. The verifier cannot prove arbitrary business behavior, algorithm correctness, dependency/capability compliance, nominal origins of JavaScript records, integration correctness, or correctness for all inputs. A hanging candidate can hang the host.

Update M1's assignment/evidence links when delivery is recorded, without automatically marking the milestone Completed or changing assignment acceptance records.

## Expected affected files

Use the minimal footprint from Assignment 0016:

- New `packages/runtime/src/contract-checks.ts` and `packages/runtime/src/box-verifier.ts`.
- `packages/runtime/src/index.ts` for shared-check use and public exports, retaining legacy behavior.
- `packages/compiler/package.json` for the existing codec subpath export.
- `vitest.config.ts` for an exact codec-subpath alias preceding the compiler-root alias.
- New `tests/box-verifier.test.ts`, `tests/box-verifier-consumer.test.ts`, and `tests/box-verifier.types.ts`.
- Existing codec/runtime tests only as needed for public-import coverage and parity regressions; retain existing assertions.
- `README.md`, `docs/box-development-spec.md`, and `docs/roadmap.md` for implemented usage and delivery evidence.

No changes are expected to grammar, artifact contracts/versions, spec type/codec semantics, compiler lowering, CLI functionality, sandbox, dependency graph, or example behavior. Return for approval if implementation requires a semantic or scope change.

## Acceptance criteria and required tests

The full [Assignment 0016 test matrix](0016-design-standalone-box-verifier.md#concrete-test-matrix-for-implementation) applies. The following are mandatory acceptance checks, not optional examples:

| ID | Criterion / concrete tests |
| --- | --- |
| AC-01 | A public codec-subpath consumer decodes the published `examples/specs/greeter.box-spec.json` and verifies the shipped trusted structured Greeter with a fixed valid User. No `.bound` source, AST, binding, artifact, compiler call, or director execution is needed. Also cover trusted simple string Greeter, async LoadUser, and a void Display-style fixture. |
| AC-02 | Existing invalid JSON/spec cases (format/version, unknown/missing keys/types, duplicate fields, conflicting schemas, incompatible/unknown/void predicates) retain decoder diagnostics; a decode-then-verify host never calls the candidate on failure. Reuse codec tests rather than duplicating schema logic. |
| AC-03 | Malformed runtime views (missing required identity, bad input/result descriptors, incompatible/unknown predicate, predicate on void) return `invalid-contract`; non-function candidate returns `invalid-implementation`. Neither invokes a candidate. The runtime guard is not represented as strict envelope validation. |
| AC-04 | Parameterized input/output tests cover strings including empty, finite numbers including zero, booleans including false, wrong primitive categories, null/undefined, boxed primitives, numeric strings, NaN, and both infinities. Invalid input prevents execution; invalid output is separately classified. |
| AC-05 | Records cover complete/empty schemas, missing/inherited required fields, wrong/non-finite field values, null/arrays, and extra own string/symbol/non-enumerable keys. Verify parity for null-prototype records, exact-own-field class instances, inherited extras, and accessors without introducing plain-object restrictions. |
| AC-06 | Sync/async success, sync throw, rejection, non-Error thrown value, candidate-thrown runtime/postcondition errors, and rejecting thenables are distinguished correctly. A valid invocation calls the candidate once and awaits completion. |
| AC-07 | Sync implicit return, explicit undefined, and async undefined pass for void and include `output: undefined`; null/string/object returns fail as `invalid-output`. |
| AC-08 | Result/field predicates cover equal and unequal empty/nonempty strings, escaped literals, and absent predicates. Malformed full output or an invalid unrelated output field wins over a failing predicate; the predicate does not run before full output validation. |
| AC-09 | Controlled throwing getters yield `inspection-failure` separately for input, output, and postcondition inspection. For the last case, a getter succeeds during output checking and throws during predicate access. Assert the stage, not a type/behavioral violation. Do not promise deterministic outcomes for arbitrary getters or mutable objects. |
| AC-10 | Candidate input and successful record output preserve reference identity. A later invocation rechecks a host-mutated input. No clone/freeze/branding is introduced; a side effect before output/predicate failure is not rolled back. |
| AC-11 | Type tests prove decoded-spec assignability, string/User function compatibility, discriminated result/failure narrowing, unknown success output, and absence of output on failed results. Runtime tests cover every failure discriminant and first-failure ordering without message parsing. |
| AC-12 | A source-level consumer test blocks frontend/compiler-root execution. A built Node import smoke test exercises the actual package export maps beyond Vitest aliases and establishes that codec + verifier imports do not load the frontend/Langium. |
| AC-13 | Parity/regression tests feed equivalent descriptors/values through legacy runtime and verifier. Assert unchanged runtime messages/classes/codes, checking order, and live-object behavior. Artifact/AST setup may appear only in parity tests, not in the standalone consumer path. |
| AC-14 | `npm run check`, `npm run build`, `demo:director-box`, `demo:box-composition`, and `demo:structured-types` pass. `bound spec examples/structured-types.bound --box Greeter` still emits the published canonical JSON byte-for-byte, and existing CLI tests remain unchanged in behavior. |

Do not execute infinite loops or leave unresolved operations running to test missing timeout support. Document the limitation rather than hanging tests. No new test framework is required.

## Explicit exclusions

- No DSL syntax, new contract language/version, second authoritative contract model, or second evaluator/runtime.
- No candidate/module loader, TypeScript transpilation service, CLI verify command, agent integration, scheduler, batch runner, or behavioral acceptance runner/callback.
- No sandbox/isolation, timeout/cancellation enforcement, resource limits, cloning/freezing, nominal branding, stricter plain-object policy, or security guarantee.
- No task derivation, candidate promotion, hashes/provenance/report framework, stale-evidence handling, or integration workflow. Trusted external tests remain responsible for functional assertions.

## Delivery after authorization

Report the changed files, API usage example, test/build/demo/export results, deviations, and unresolved issues. Preserve source-independent consumption and all compatibility constraints. Follow repository commit conventions only when committing is authorized; never push without explicit authorization. Do not change this assignment's requirements or acceptance status without Product Owner approval.

## Product Owner acceptance and completion evidence

The Product Owner explicitly approved and accepted Assignment 0017, conditional on all mandatory checks passing. Those checks were rerun successfully on the corrected implementation before recording this acceptance. **Assignment 0017 is Completed.**

- **Implementation:** `ea2a8dcc50c90b929be8a6077b828094df3261d5` — standalone verifier, shared runtime checks, public codec subpath, tests, and documentation.
- **Accepted correction/revision:** `5d15c9b0269146282bc07a1da3edcf522b036609` — exceptions from contract getters/proxy traps during initial validation become `invalid-contract`; regressions confirm the candidate is never invoked. The public failure union and legacy runtime semantics remain unchanged.

### Mandatory-check evidence

| Acceptance criteria | Passing evidence on the accepted revision |
| --- | --- |
| AC-01, AC-12 | [`box-verifier-consumer.test.ts`](../../tests/box-verifier-consumer.test.ts) verifies the published portable Greeter spec and existing trusted functions without source/compiler/director execution; source-level guards and a built Node import smoke test exclude the frontend/compiler root/Langium. |
| AC-02 | [`box-spec-json.test.ts`](../../tests/box-spec-json.test.ts) retains strict decoder diagnostic coverage and confirms invalid portable inputs never invoke the candidate. |
| AC-03 | [`box-verifier.test.ts`](../../tests/box-verifier.test.ts) covers malformed consumer views, non-functions, and the four throwing contract getter/proxy regressions, with structured failures and no invocation. |
| AC-04–AC-10 | The same verifier suite covers primitive/record input/output boundaries, execution failures and awaiting, void, exact result/field predicates and ordering, all three inspection phases, reference identity, mutation/revalidation, and no rollback. |
| AC-11 | [`box-verifier.types.ts`](../../tests/box-verifier.types.ts) passes type checking for decoded-spec assignability, heterogeneous functions, unknown success output, and discriminated result/failure narrowing. Verifier tests exercise every failure kind and first-failure ordering. |
| AC-13 | Verifier legacy-parity tests and the unchanged-behavior runtime suites ([structured types](../../tests/structured-types.test.ts), [behavioral contracts](../../tests/behavioral-contracts.test.ts), [director invocation](../../tests/director-box-invocation.test.ts)) pass, including errors, ordering, live references, and raw legacy inspection exceptions. |
| AC-14 | `npm run check` passes type checking and **374 tests in 15 files**; `npm run build` passes. `demo:director-box`, `demo:box-composition`, and `demo:structured-types` each print `Hello, World!`. The Hello World CLI also passes. `npm run --silent bound -- spec examples/structured-types.bound --box Greeter` matches `examples/specs/greeter.box-spec.json` byte-for-byte (`cmp` succeeds). Existing CLI tests pass within the full suite. |

All mandatory criteria have supporting evidence; none remains unverified. This acceptance closes the trusted, single-invocation implementation scope only. It does not approve arbitrary Box candidates or claim behavioral correctness, determinism for arbitrary JavaScript objects, security isolation, or later-roadmap capabilities.
