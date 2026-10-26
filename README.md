# BoundScript

**Human-designed. Agent-implemented. Bound by contracts.**

BoundScript is an experimental language for making software construction independently delegable to coding agents without requiring humans to coordinate every implementation detail. Its hypothesis is that deterministic, human-readable architectural boundaries can keep probabilistic implementations compatible, governable, and understandable.

The approved direction in [Proposal 0013](docs/proposals/0013-deterministic-architecture-for-probabilistic-construction.md) separates architectural authority from implementation freedom:

- **Humans** own requirements, acceptance criteria, trust policies, architectural approval, and final acceptance.
- **Architects** (humans or LLMs) propose decomposition, Box responsibilities, interfaces, and changes. Proposals do not authorize changes to approved contracts.
- **BoundScript** represents approved boundaries and deterministically parses, validates, and extracts supported contracts. Compilation and extraction never call an LLM.
- **Implementers** choose algorithms and private organization within approved boundaries, using both contracts and externally supplied functional tasks. They must propose, not silently make, public architectural changes.
- **Independent verifiers and integrators** are intended to check candidates against trusted contracts and tests, report evidence, and integrate through approved wiring without silently repairing implementations. Promotion requires explicit acceptance.

A **Box** is a unit of delegated responsibility with an explicit architectural boundary—not necessarily a function, service, container, agent, or deployment unit. The build-time **Architect** is distinct from the existing runtime **`director`**, which orchestrates application execution.

## Current capabilities and planned direction

See the [roadmap](docs/roadmap.md) for the current milestone, completion criteria, related assignments, and execution status.

Today the repository implements a Langium parser and diagnostics, deterministic compiler, versioned executable artifacts, artifact-driven runtime, and CLI. It supports sequential director-to-box invocation, primitive and flat-record data contracts, minimal string postconditions, portable canonical Box contract extraction through `bound spec`, and standalone single-invocation verification of trusted functions.

The external [deterministic task derivation adapter](docs/task-derivation.md) assembles canonical contracts and human-owned task/scope/policy snapshots into bounded packages; structural success does not verify human approval. The Product Owner accepted Assignment 0019, including its exclusive publication correction, and closed M2 as Completed; see the [acceptance evidence](docs/assignments/0019-implement-deterministic-task-derivation.md#product-owner-acceptance-and-completion-evidence).

It does **not** implement agent-driven construction, candidate loading, behavioral acceptance runners, evidence reports, candidate promotion, dependency/capability declarations, or sandbox enforcement. Imports and general control flow are also unsupported. Current host implementations are trusted functions running in the host process.

The planned workflow is: human requirements → Architect proposal → approval → deterministic contract extraction and task derivation → independent implementation → independent and integration verification → evidence-backed acceptance and promotion. A contract is not a complete implementation brief: intended behavior still needs human-owned tasks, examples, and trusted tests. A passing type check or finite test cannot prove arbitrary semantic correctness.

The standalone verifier reuses existing contract semantics; task derivation is accepted and M2 is Completed. The two-Box pilot remains Planned under [0020's bounded amendment](docs/assignments/0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment): separate temporary handoff workspaces, tool-free native Pi generation, and all candidate compilation/tests in disposable credential-free network-disabled containers. Directories/worktrees are organizational boundaries, not security sandboxes. [0021 is concluded Completed with Inconclusive outcome](docs/assignments/0021-qualify-existing-pilot-tooling.md#product-owner-acceptance-and-conclusion), not a qualified-runtime result or pilot prerequisite. [0023 — prepare/freeze assets](docs/assignments/0023-prepare-and-freeze-independent-pilot-assets.md) was authorized; [actual assets and validation](experiments/contact-onboarding/README.md) are delivered pending Product Owner acceptance; [0022 execution](docs/assignments/0022-run-bounded-independent-implementation-pilot.md) is deferred until assets are reviewed and revised execution is explicitly approved. M3 stays Planned through preparation. Agent/sandbox choices belong to the external operator runbook, never language/compiler/runtime/handoff-format integrations. No implementation agents or pilot have run, and no custom orchestration/security infrastructure is introduced; preserve the existing provider/model unless explicitly approved otherwise.

The product hypothesis will be compared against ordinary TypeScript interfaces, Markdown tasks, tests, and existing agents, measuring coordination effort, boundary drift, and comprehension—not merely successful integration. BoundScript does not make code generation deterministic; it makes its boundaries and supported acceptance checks explicit and reproducible.

BoundScript is not a replacement for general-purpose programming languages and is provider- and agent-framework-neutral. The existing compiler/runtime remains a valid execution backend, not a mandatory path for every future implementation workflow. Alternative execution targets remain possible, not implemented. See [architecture](docs/architecture.md) and [decisions](docs/decisions.md) for the target/current distinction and historical context.

Run the executable example:

```bash
npm run bound -- examples/hello-minimal.bound
```

Expected output:

```text
Hello, World!
```

See [`examples/hello-world.bound`](examples/hello-world.bound) for broader, non-executable syntax exploration.

## Director → Box invocation

After `npm install`, run this command from the repository root:

```bash
npm run --silent demo:director-box
```

It builds the TypeScript packages and demo host, then prints exactly:

```text
Hello, World!
```

`--silent` suppresses npm's command banner; build-tool output is sent to stderr. The [demo host](examples/director-box/host.ts) loads the real `.bound` source, parses and validates it, compiles with the explicit `Greeter` → `demo.greeter` binding, and executes the artifact with the separate [TypeScript Greeter](examples/director-box/greeter.ts) registered under that ID.

Running `npm run bound -- examples/director-box.bound` is **not supported**: the current CLI supplies neither compile-time box bindings nor runtime implementation registrations, so compilation reports `compiler.missing-implementation`. It does not load or discover TypeScript implementations. Use the demo host for this example; `npm run bound -- examples/hello-minimal.bound` continues to work without bindings.

[`examples/director-box.bound`](examples/director-box.bound) declares one string-in/string-out operation and invokes it from a director:

```boundscript
box Greeter {
    operation greet(name: string): string
}
```

Inside `on start`, `let greeting = Greeter.greet("World")` stores the result and `print(greeting)` consumes it. Boxes are declared before the director. Each box has exactly one operation and one named input. Inputs and value results may be `string`, `number`, `boolean`, or a named flat record; results may also be `void`. Calls accept a string literal or a previously assigned variable of the declared input type. Variables hold call results, cannot be reassigned, and are local to one execution. Value-returning calls must be assigned with `let`; void-returning calls must be standalone statements.

Bind developer-provided TypeScript functions through the programmatic API:

```typescript
import { readFile } from 'node:fs/promises';
import { parseBoundScript } from '@boundscript/language';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptRuntime } from '@boundscript/runtime';
import { greet } from './my-greeter.js'; // Developer-provided (string) => string | Promise<string>

const parsed = parseBoundScript({
  uri: 'examples/director-box.bound',
  text: await readFile('examples/director-box.bound', 'utf8')
});
if (!parsed.program) throw new Error(JSON.stringify(parsed.diagnostics));

const compiled = await new BoundScriptCompiler().compile(parsed.program, {
  Greeter: 'my-greeter' // Source box name → resolved host implementation ID
});
if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));

const runtime = new BoundScriptRuntime(
  { writeLine: (value) => console.log(value) },
  { 'my-greeter': greet } // Implementation ID → trusted TypeScript function
);
await runtime.execute(compiled.artifact, { entrypoint: 'start' });
```

Every declared box requires an explicit binding. Unknown boxes, operations, and variables fail semantic validation/compilation. Missing host functions fail before instruction execution. Thrown/rejected implementation errors and invalid return categories fail execution with contextual errors: value operations must satisfy their declared primitive or record type, and void operations must return `undefined` (including implicit returns). All may be asynchronous. Functions are not generated, loaded dynamically, or embedded in the artifact; the host supplies them. They run **without sandbox enforcement**. The CLI has no implementation-loading option, so use the API for box programs; the existing Hello World CLI remains unchanged.


## Two-box composition

From the repository root after `npm install`:

```bash
npm run --silent demo:box-composition
```

Expected stdout is exactly `Hello, World!` followed by a newline; build output goes to stderr. This runs [`examples/box-composition.bound`](examples/box-composition.bound) through parsing, validation, compilation, and artifact execution:

```boundscript
system HelloWorld {
    box Greeter { operation greet(name: string): string }
    box Display { operation show(message: string): void }
    director Main {
        on start {
            let message = Greeter.greet("World")
            Display.show(message)
        }
    }
}
```

The [host](examples/box-composition/host.ts) binds `Greeter` to `demo.greeter` and `Display` to `demo.display`, registering separate [Greeter](examples/box-composition/greeter.ts) and [Display](examples/box-composition/display.ts) implementations. The director never calls `print()`: Display receives and writes the Greeter result. Calls execute sequentially, awaiting each implementation before continuing. Literal `"message"` and variable `message` remain distinct in the serialized instruction program. As with the single-box demo, the plain CLI cannot supply these bindings.

## Structured data contracts

Run the three-box structured demo from the repository root after `npm install`:

```bash
npm run --silent demo:structured-types
```

Expected stdout is `Hello, World!` followed by a newline (build output goes to stderr). The real [`examples/structured-types.bound`](examples/structured-types.bound) program declares `User` and `Greeting` records, then runs:

```boundscript
let user = LoadUser.load("123")
let greeting = Greeter.greet(user)
Display.show(greeting)
```

The [host](examples/structured-types/host.ts) explicitly binds three separate TypeScript implementations: [LoadUser](examples/structured-types/load-user.ts), [Greeter](examples/structured-types/greeter.ts), and [Display](examples/structured-types/display.ts). The director passes records directly; it neither constructs nor inspects them and does not call `print()`.

Declare records before boxes, for example:

```boundscript
type User {
    id: string
    name: string
    active: boolean
    score: number
}
```

Fields are required and must be `string`, finite `number`, or `boolean`. This slice uses **named type identity**: different record names are not interchangeable, even if their fields match. Runtime records must have their declared fields as own properties; missing, wrong-typed, and extra fields are rejected. Inputs are checked immediately before each host call and outputs immediately after it resolves, with box/operation, expected type, and field/category details in errors. Records are passed by reference, without string conversion or copying; trusted host code can mutate them, so inputs are rechecked at every call. Host TypeScript interfaces are handwritten conveniences, not substitutes for runtime validation.

There are no nested/optional fields, arrays, object literals, numeric/boolean literals, property access, or implicit conversions in director code. Numeric/boolean values may be produced by boxes and passed through compatible variables. `print()` remains string-only. These structural checks are data contracts, not behavioral `ensure` predicates or sandbox enforcement. The plain CLI still cannot supply box bindings; use the explicit demo host.

The compiler emits director instruction **version 4**, containing tagged operands, resolved primitive/record metadata, and optional structured postconditions, never host functions or AST nodes. The executable-artifact envelope remains version 1. Recompile older source programs to the current instruction version; older instruction versions are rejected.

## Minimal behavioral postconditions

A box may declare one postcondition after its operation:

```boundscript
box Greeter {
    operation greet(name: string): Greeting
    ensure result.message != ""
}
```

The structured demo now includes this check; `npm run --silent demo:structured-types` still prints `Hello, World!`. A structurally valid `Greeting` with an empty `message` instead throws `PostconditionViolationError` (`runtime.postcondition-violation`) before Display runs. The error identifies the box/operation, predicate, and observed string.

Only `ensure result != "literal"` on a string result, or `ensure result.field != "literal"` on a declared string record field, is supported. The literal may be empty or nonempty and uses normal string escaping. `void`, non-string targets, and unknown fields are rejected with source-located diagnostics. There is no `==`, chained access, expression evaluation, reference to inputs, boolean combination, or director-level assertion syntax.

The runtime awaits the host, validates the **entire output data type first**, checks the postcondition, and only then binds the result and continues. Host exceptions remain execution errors and malformed outputs remain data-contract errors, not postcondition violations. Predicates are serialized as explicit descriptors and interpreted without `eval` or generated code. These checks are **not security boundaries**: trusted host code may already have caused side effects, and failure provides no rollback or side-effect isolation.

## Deterministic task packages

```sh
delivery=$(mktemp -d)
npm run handoff -- "$PWD" tests/fixtures/handoff/input.json "$delivery/handoffs" --all
```

Use a fresh output and human-approved inputs for operational use. Publication atomically creates an output symlink to complete sibling data; keep both together and discard the dedicated delivery parent after use. See [usage, protected-context boundaries, regeneration policy, and independent consumer checks](docs/task-derivation.md). No candidate execution, sandbox, orchestration, or evidence enforcement is included.

## Box development specification

Export the structured demo's Greeter contract after dependency installation:

```bash
npm run --silent bound -- spec examples/structured-types.bound --box Greeter
```

Stdout contains only canonical JSON, including the resolved `User`/`Greeting` schemas and postcondition; build output and diagnostics go to stderr. No bindings or implementations are required. See the [reference export](examples/specs/greeter.box-spec.json) and [format/API documentation](docs/box-development-spec.md).

`@boundscript/compiler` exports the synchronous, pure `extractBoxDevelopmentSpec(system, boxName)` API, plus `BoxDevelopmentSpec` and the discriminated `BoxSpecResult` types. Given a successfully parsed `SystemNode`:

```typescript
import { extractBoxDevelopmentSpec } from '@boundscript/compiler';

const extracted = extractBoxDevelopmentSpec(program, 'Greeter');
if (!extracted.ok) throw new Error(JSON.stringify(extracted.diagnostics));
const spec = extracted.spec;
// spec.operation.input: { name: 'user', type: complete User descriptor }
// spec.operation.resultType: complete Greeting descriptor
// spec.operation.postcondition: string-not-equal on result.message
```

For `examples/structured-types.bound`, the result has format `boundscript/box-development-spec`, version `1`, system/box identity, operation/parameter names, fully resolved primitive or named flat-record input/output types (or a `void` result), and the optional existing postcondition descriptor. Only the selected box's contract is included—no AST/CST, source paths, director statements, implementation IDs, or functions. Record fields retain declaration order, exactly as in ordinary compilation.

Extraction validates the **whole system**, including unused declarations and director statements. Invalid source returns diagnostics with available source ranges and no partial spec. Selecting a nonexistent box returns `compiler.unknown-box`; there is no source range for a selection supplied outside the source. Declared but unused boxes can be extracted, without bindings, host implementations, file I/O, or artifact compilation.

`serializeBoxDevelopmentSpec(spec)` validates and returns canonical JSON: fixed key order, code-point-sorted record fields, two-space indentation, and one final LF. `parseBoxDevelopmentSpec(json)` strictly validates and returns the same discriminated result shape. Unknown properties/versions/types, conflicting record schemas, and incompatible postconditions fail explicitly. Parsing returns diagnostics; invalid serialization throws `BoxSpecValidationError` with diagnostics. Neither codec performs I/O or loads host implementations.

The document describes **declared contracts**, not unstated functional intent or a complete implementation brief. A human-authored task and independent examples/tests are still required; business behavior is not inferred from box names or director calls. Agent orchestration remains outside this slice.

## Standalone Box verification

After `npm run build`, a host can decode portable JSON and check one fixed-input invocation of a **trusted, already-loaded** function without source, AST, bindings, artifacts, or director execution. From a module in the repository root:

```typescript
import { readFile } from 'node:fs/promises';
import { parseBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';
import { verifyBoxImplementation } from '@boundscript/runtime';
import { greet } from './examples/structured-types/dist/greeter.js';

const decoded = parseBoxDevelopmentSpec(await readFile('examples/specs/greeter.box-spec.json', 'utf8'));
if (!decoded.ok) throw new Error(JSON.stringify(decoded.diagnostics));
const checked = await verifyBoxImplementation(decoded.spec, greet, {
  id: '123', name: 'World', active: true, score: 7
});
if (!checked.ok) throw new Error(JSON.stringify(checked.failure));
console.log(checked.output); // { message: 'Hello, World!', recipientId: '123' }
```

The codec subpath does not load the language frontend. The verifier shares the director runtime's descriptor, input/output, void, and predicate checks. It calls the function once, awaits it, validates the entire output, then evaluates any postcondition. `BoxVerificationContract` is only a structural consumer view of a decoded spec, not another serialized schema; always decode first and keep the contract stable during verification.

Results are discriminated by `ok` and, on failure, `failure.kind`: `invalid-contract`, `invalid-implementation`, `invalid-input`, `execution-failure`, `invalid-output`, `postcondition-failure`, or `inspection-failure`. Inspection failures are errors encountered while checking values, **not proven contract violations**. Success includes `output: unknown` (including `undefined` for void); failure exposes no partial output. See the [API and failure reference](docs/box-development-spec.md#standalone-verification) for fields and examples.

Records retain their original references: no cloning, freezing, branding, or stricter plain-object rules are added. Getters and mutable objects do not provide deterministic verification guarantees. Functions execute with host privileges and may cause side effects before failure, without rollback, timeouts, cancellation/resource enforcement, or isolation; a hanging function can hang the host. Do not run untrusted generated code in the trusted development process. A conformance pass does not prove business behavior, algorithms, dependencies/capabilities, nominal record origins, integration, or correctness for all inputs. Use separate trusted functional tests. There is no CLI verify command or candidate loader.

## Target use cases

The following are historical runtime **behavioral targets**, not a current feature checklist, finalized syntax, or the implementation order for Proposal 0013. Existing examples cover parts of UC-01 and UC-02; the broader targets remain design material:

| Target | Capability to demonstrate |
| --- | --- |
| [UC-01](docs/use-cases/01-system-box-execution.md) | A director invokes a bound box implementation and consumes its output |
| [UC-02](docs/use-cases/02-contract-enforcement.md) | Input and output contract violations produce identifiable failures |
| [UC-03](docs/use-cases/03-director-control-flow.md) | Branches and repetition control box execution |
| [UC-04](docs/use-cases/04-modules-and-imports.md) | Reusable declarations can be imported by multiple systems |
| [UC-05](docs/use-cases/05-capability-isolation.md) | The execution environment denies undeclared capabilities |

Each target includes success and failure criteria. See [the target use case index](docs/use-cases/README.md) for scope and acceptance guidance. These targets are independent of whether the eventual execution backend interprets artifacts or generates JavaScript. Modules, richer control flow, and production capability isolation are not prerequisites for the new construction pilot.

## Repository layout

```text
packages/
  language/   Langium grammar, generated typed AST, parsing, and diagnostics
  artifact/   Shared executable-artifact contract between compiler and runtime
  compiler/   Deterministic resolved-input to artifact compilation boundary
  runtime/    Provider-neutral artifact execution boundary; does not know the source DSL
  sandbox/    Capability and resource policy definitions
  cli/        Source-to-parser-to-compiler-to-runtime command-line pipeline
docs/
  architecture.md
  decisions.md
  open-questions.md
  assignments/
  reviews/
  development/
    developer-workflow.md
  use-cases/
examples/
  hello-minimal.bound
  hello-world.bound
  director-box.bound
  box-composition.bound
  structured-types.bound
tests/
  scaffolding.test.ts
  conformance.test.ts
  fixtures/
```

Standalone verification is an API in the existing runtime package, not a new package. No Architect, agent runner, or promotion module is implemented in this layout. Build-time agents are development tooling, not runtime components; generalized orchestration remains deferred. Runtime agents, if supported later, will be explicit language-level application behavior and will remain provider-neutral.

## Development

Requirements: Node.js 22.12+ and npm.

```bash
npm install
npm run check
npm run build
```

npm 12 blocks unreviewed dependency install scripts by default. The current dependency graph requires no install-script approvals; new scripts will remain blocked until explicitly reviewed.

Langium-generated TypeScript sources are reproducible and ignored by Git. Build and test commands regenerate them from `packages/language/src/boundscript.langium`.

Useful commands:

- `npm run --silent demo:director-box` — build and run the bound TypeScript Greeter demo
- `npm run --silent demo:box-composition` — build and run Greeter → Display composition
- `npm run --silent demo:structured-types` — build and run LoadUser → Greeter → Display with records
- `npm run langium:generate` — regenerate the parser, typed AST, and language metadata
- `npm run typecheck` — generate language sources and compile all TypeScript project references
- `npm test` — run the Vitest suite
- `npm run check` — run type checking and tests
- `npm run clean` — remove TypeScript build outputs

## Status

The executable subset supports one `system`, same-system flat record declarations, optional boxes with one typed-input operation and a typed or `void` result each, one `director`, and one sequential `on start` block. Box calls accept string literals or compatible previously assigned variables; value results are assigned with `let` and void calls are standalone. `print()` accepts a string literal or string variable. No imports, general expressions, loops, conditionals, or testing syntax are supported. Use Vitest for external tests. The broader example language remains design material rather than a finalized specification.
