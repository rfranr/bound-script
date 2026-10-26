# Direction review — analysis only

Baseline: `feature/agent-driven-architecture`, commit `31dc3bf1eabc48f77d2024b9c421714dc205da6c`. The current `experiment/boundscript-next` checkout already points to that commit; no branch was created or switched. No attached conversation was available, so this review assesses the direction in the request against repository documentation and source. No pilot, tests, or model calls were run for this review.

## Assessment

This is a better fit for the stated goal. The valuable abstraction is controlled delegation, not a new execution language. But removing the DSL removes relatively mature plumbing while leaving the hardest, largely unimplemented parts: enforceable isolation, dependency authority, independent verification, and safe integration. A Box manifest can become another language if it grows algorithms, predicates, or orchestration semantics.

## 1. What is genuinely reusable?

- Human-owned tasks, protected interfaces/tests, independent contexts, fixed integration without repair, and bounded feedback are the strongest existing design assets.
- The contact-onboarding pilot contains reusable testing methods: negative controls, failure classification, independent functional assertions, fixed wiring, and restricted offline evaluation containers. Its conventional TypeScript arm already supplies native interfaces and concrete runtime assertions. These are reference assets, not evidence that agent delegation has succeeded.
- Handoff packaging, stable snapshots, candidate identification, and fail-closed validation provide useful patterns. Current handoff tooling itself depends on DSL extraction; it is not a drop-in native-contract implementation.
- Existing contract checks and standalone verifier remain useful for the old primitive/flat-record subset, but should not dictate the new contract model. Reuse their semantics/tests where appropriate, not necessarily their package boundaries.

## 2. What becomes unnecessary for the new path?

The Langium grammar/frontend, DSL lowering, mandatory director, executable artifact, custom runtime interpreter, and DSL-to-TypeScript declaration generation. Native compilers, ordinary modules, and explicit wiring can cover those jobs. Keep the existing backend intact; none of this requires migration or deletion.

The version-1 portable spec is optional, not an obligation to preserve a second type system alongside native interfaces.

## 3. What guarantees could be lost?

- A single restricted, canonical, versioned contract with source-located diagnostics and common extraction/runtime semantics. Separate native declarations, manifests, and tests can drift.
- DSL nominal record compatibility and explicit invocation validation. TypeScript is largely structural; its compile-time types disappear at runtime and can be bypassed.
- Exact runtime record checks, finite-number checks, postconditions, and ordered director execution—unless explicitly retained through native validators/tests and wiring. Type checking alone does not replace them.

Do **not** count dependency enforcement or sandbox isolation as existing guarantees: the grammar declares neither dependencies nor capabilities, and `packages/sandbox` contains policy types only. The standalone verifier executes trusted functions in-process. The pilot evaluator isolates execution from the host, but candidates share a JavaScript realm with tests and can read mounted acceptance data. Keeping tests outside the *generation* sandbox is not sufficient to make verification tamper-resistant.

Also distinguish build-time restrictions from deployed behavior: restricted agent access does not prevent an accepted module from using ambient filesystem/network privileges later. Import allowlists alone do not cover dynamic loading or transitive dependencies.

## 4. Smallest useful experiment

On the already-existing `experiment/boundscript-next` branch, later and only with authorization: a fresh two-Box TypeScript exercise, separate from the frozen pilot. Use one authorized dependency edge: B consumes A's interface, never its implementation. Give each agent only its task, read-only native contract, authorized dependency declarations/stubs, and writable implementation directory. Use existing sandbox technology, no new orchestration framework, DSL, or compiler changes.

An external verifier checks exports/types and dependency access, then runs hidden behavioral and real A-to-B integration tests with fixed wiring and no human repair. Protect the test oracle from candidate code; do not simply import untrusted code into the trusted verifier's realm.

Include deliberate controls: wrong export, type-correct wrong behavior, forbidden import/file/network access, and attempted test modification. The narrow success criterion is that controls are rejected and independently produced implementations integrate unchanged. Record first-pass/revision outcomes, human intervention time, and setup effort. One pair validates feasibility—not superiority or general architectural safety. If ordinary TypeScript plus sandbox/CI tooling accomplishes this, BoundScript's remaining value must be the boundary workflow and evidence, not proprietary syntax.

### Principal source references

- `docs/architecture.md`
- `docs/box-development-spec.md`
- `packages/language/src/boundscript.langium`
- `packages/runtime/src/box-verifier.ts`
- `packages/sandbox/src/index.ts`
- `tooling/handoff.ts`
- `experiments/contact-onboarding/{README.md,evaluate.sh}`
- `experiments/contact-onboarding/tests/{evaluate.mjs,wiring.mjs}`
- `experiments/contact-onboarding/baseline/README.md`
