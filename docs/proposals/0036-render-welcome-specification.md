# Proposal — RenderWelcome native Box

**Status: Approved by the Product Owner; implementation delivery subsequently reviewed and accepted under assignment 0036.**

**Assignment:** [0036](../assignments/0036-design-render-welcome-specification.md)

The Product Owner approved this revised specification, including the independent consumer-owned contract, pure formatter boundary, application-owned composition, reduced verification suite and minimal shared-verifier extraction. The design below retains its proposal-time wording for traceability. Implementation was subsequently authorized and is documented in the [implementation report](../development/render-welcome-report.md). The Product Owner later reviewed and accepted the delivery and authorized a local commit, not a push.

## 1. Scope and references

RenderWelcome is a small, synchronous, pure formatter of an already-normalized contact. It does not normalize contacts, invoke NormalizeContact or handle normalization errors. Keeping those responsibilities outside the Box allows independent development and ordinary TypeScript composition later.

References:

- [Native public contract](../../experiments/native-typescript-contracts/src/contract.ts): `NormalizedContact` has required, readonly, nonempty `name`, `email` and `phone` strings; `NormalizeContactResult` is a discriminated union.
- [Native experiment guide](../../experiments/native-typescript-contracts/README.md) and [Box definition](../../experiments/native-typescript-contracts/native_box.py): independently owned tasks, contracts, validators, fixtures and explicitly selected suites.
- Historical [RenderWelcome contract](../../experiments/minimal-box/two-boxes/contracts/render-welcome.ts) and [task](../../experiments/minimal-box/two-boxes/tasks/render-welcome.md): useful precedent for the success message, but these take raw input and an injected normalizer. This proposal deliberately changes that boundary; it neither replaces nor changes the historical baseline.

Non-goals: localization, templates, HTML rendering, delivery of email/SMS, configurable greetings, raw-contact validation, error-message rendering, framework composition APIs, artifact versioning or a new runner architecture. Section 6 identifies only the minimal extraction of existing verifier mechanics needed for independent Box roots.

## 2. Proposed public TypeScript contract

The following is the proposed content of a future Box-owned `src/contract.ts`, not a file to create as part of this delivery:

```ts
import type { tags } from "typia";

export interface WelcomeContact {
  readonly name: string & tags.MinLength<1>;
  readonly email: string & tags.MinLength<1>;
  readonly phone: string & tags.MinLength<1>;
}

export type WelcomeMessage = string;

export type RenderWelcome =
  (contact: WelcomeContact) => WelcomeMessage;
```

The candidate's named function export would be `renderWelcome`, assignable to `RenderWelcome`. It takes one argument and returns a string, not a Promise or result envelope. There is no failure union for valid input.

`WelcomeContact` intentionally mirrors the current public `NormalizedContact` shape, using TypeScript structural compatibility rather than importing peer code. It is a consumer-owned input contract, not a new authority for NormalizeContact. Keeping it self-contained fits the existing single public-contract mount and Typia generation setup without introducing cross-Box runtime imports or changing the verifier. A future integration-only compile check should detect incompatibility with the upstream public type; it must not silently rewrite either contract.

All three fields are retained to accept the public normalized record directly. Phone is required structurally but not displayed. No email-format, whitespace-normalization or phone-format semantics are added by the types: `MinLength<1>` is only a shape constraint, not evidence that normalization occurred.

## 3. Proposed functional requirements

For every structurally valid input:

1. Return exactly `Welcome, NAME! <EMAIL>`, substituting `contact.name` and `contact.email` verbatim. The fixed punctuation and spaces are literal; append no newline.
2. Preserve case, whitespace, international characters, punctuation and Unicode code-unit sequences. Do not trim, collapse whitespace, lowercase, normalize Unicode, escape markup or encode values.
3. Do not include or format the phone value. Changing only a valid phone value must not change the message.
4. Do not mutate the input; accept a frozen input record. Do not retain input references or depend on earlier calls.
5. Be deterministic and synchronous, with no I/O, environment/time/randomness dependence, peer calls or external runtime dependencies.
6. Return plain text only. The caller must use a text-safe rendering sink; this contract does not make the result safe to interpolate as HTML.

Empty fields, missing fields, `null`, non-string fields and normalization failure objects are outside the input contract. Independently derived validators must reject those shapes before candidate invocation in tests. No fallback, exception type or business error behavior is specified for invalid direct calls. This is not a promise of a production runtime validation wrapper.

Whitespace-only strings and unusual email/phone strings can satisfy the structural contract. RenderWelcome must still format them verbatim; it must not infer missing upstream business rules. In particular, NormalizeContact's unresolved phone semantics are irrelevant to rendering.

## 4. Proposed acceptance examples

Each row denotes exact input and exact output. Inputs contain only the three declared fields. The JSON string notation preserves significant whitespace and escapes.

| Case | Input | Expected output (JSON string) |
| --- | --- | --- |
| Basic | `{"name":"Ada Lovelace","email":"ada@example.com","phone":"+34600111222"}` | `"Welcome, Ada Lovelace! <ada@example.com>"` |
| Unicode and tab preservation | `{"name":"李 e\u0301🙂\t雷","email":"li@example.cn","phone":"+8613800000000"}` | `"Welcome, 李 e\u0301🙂\t雷! <li@example.cn>"` |
| No re-normalization | `{"name":"  Ana  María ","email":"ANA+News@Example.COM","phone":"x"}` | `"Welcome,   Ana  María ! <ANA+News@Example.COM>"` |
| Literal punctuation | `{"name":"<Sam & Co>","email":"sam+news@example.com","phone":"1"}` | `"Welcome, <Sam & Co>! <sam+news@example.com>"` |
| Minimal structural input | `{"name":" ","email":"x","phone":"?"}` | `"Welcome,  ! <x>"` |
| Control characters preserved | `{"name":"A\nB","email":"a@example.com","phone":"1"}` | `"Welcome, A\nB! <a@example.com>"` |

These six fixtures are the complete proposed example set; no additional long-string matrix or separate character-specific property suites are needed. The third, fifth and sixth examples test the formatter's boundary, not whether NormalizeContact should produce those contacts. The Unicode example includes a decomposed accent, emoji and a tab.

### One combined property

Use one RenderWelcome-owned fast-check property (proposed seed 36, 100 runs) over nonempty name/email strings, two nonempty phone strings, and an unrelated valid contact. Keep generated sizes modest for the existing verifier budget; generator bounds are not new contract limits.

For each run:

1. Snapshot and freeze the input records.
2. Call RenderWelcome on the first contact, the unrelated contact, the first contact again, and the same name/email with the other phone.
3. Guard every result and compare it to the exact literal template using that call's original name/email. The repeated call and phone variant must equal the first result.
4. Assert the inputs still equal their pre-call snapshots.

This single property checks exact formatting, deterministic/call-independent results, phone independence and immutability without duplicating preservation tests already covered by the fixtures. Guard fixture inputs/outputs too, and invoke fixture cases with frozen inputs. All valid calls must return normally with a string. No separate idempotence, output-length or substring property is necessary. Tests provide behavioral evidence, not proof of absence of hidden I/O or retained references; review the candidate for the purity requirements.

## 5. Integration through public outputs

Composition belongs to the consuming application, not either Box. Illustrative application wiring only (not an implementation of RenderWelcome):

```ts
const result = normalizeContact(rawContact);
if (result.ok) {
  const message: WelcomeMessage = renderWelcome(result.contact);
  // Application decides how to display or deliver message.
} else {
  // Application owns error handling; do not call renderWelcome.
}
```

A future integration check should import only the two public contracts and establish that the success branch of `NormalizeContactResult` is assignable to `WelcomeContact`. It should also compile the call above using public function signatures. No casts, copied normalization logic or NormalizeContact source are needed. Both contracts' current three-field shapes match, including Typia minimum-length tags.

RenderWelcome's standalone tests use locally constructed fixtures, never NormalizeContact's implementation, fixtures, task or verifier oracle. Its development context needs only its own approved contract and task. An integration test can exercise successful composition and ensure rendering is not invoked on normalization failure, but that is application-level evidence, not a prerequisite for independently verifying RenderWelcome. No new import authorization, runtime loader or framework abstraction is proposed.

## 6. RenderWelcome-owned verification plan

Suggested future location: `experiments/render-welcome-native/`, a sibling outside NormalizeContact's recursive verification root. These paths are recommendations only; none are created by this delivery.

| Future file | Ownership and purpose |
| --- | --- |
| `task.md` | Approved RenderWelcome intent and export instructions; agent-visible. |
| `src/contract.ts` | Approved public contract above; agent-visible. |
| `src/validators.ts` | Typia `createEquals` / `createAssertEquals` for input and output, derived from that contract, not a handwritten schema. |
| `.generated/contract.ts`, `.generated/validators.ts` | Disposable Typia build outputs, never committed. |
| `fixtures/welcome-cases.json` | Independent exact input/expected-output data based on the examples above. |
| `validators.test.ts` | Runtime category: valid and invalid input/output shapes, independent of a candidate. |
| `acceptance.test.ts` | Combined acceptance/properties categories: six exact fixture cases and the single seeded property above, with input/output guards. |
| `native_box.py`, `verify.py`, `generate.py` | Fixed RenderWelcome definition and thin Box-specific entry points, rooted here; no peer-experiment imports. |
| `tsconfig.json`, build command | Explicit local Typia build using the repository's pinned tooling. |

Keep runtime-validator tests small and table-driven: a valid record; empty, missing and non-string field cases covering all three fields; `null`; a failure object; and an extra key for exact-object validation. For output, check a string and representative non-string values (an object and `null`). A string with wrong greeting text passes the output shape but must fail acceptance; runtime shapes do not substitute for semantics. Do not add randomized shape tests duplicating Typia.

A future explicit `BoxDefinition` uses the existing fields, with all Box paths relative to **RenderWelcome's own root**, `experiments/render-welcome-native/`:

- `name`: `render-welcome-native`.
- `task_path`: `task.md`; `contract_path`: `src/contract.ts`.
- `contract_module`: `/inputs/contract.ts`.
- `function_type`: `RenderWelcome`; `implementation_export`: `renderWelcome`.
- `verification_path`: `.`.
- `suites`: runtime → `validators.test.ts`; combined acceptance/properties → `acceptance.test.ts`, executed once.
- `verification_inputs`: `src`, `.generated/contract.ts`, `.generated/validators.ts`, `fixtures/welcome-cases.json`.
- No optional categories. A future local `accepted_path`, if runner configuration requires one, would be `accepted/render-welcome.ts`; configuring a path would not grant human acceptance.

Any generated validators, accepted source and quarantine stay local to this Box and ignored by version control. The root is a sibling of, not a child of, the NormalizeContact experiment. No `../native-typescript-contracts` paths, imports, tool-adapter references or build dependencies are permitted in RenderWelcome's standalone definition or entry points. Public-contract references in this design and future application-level compatibility checks do not create a standalone Box dependency.

All test files must be declared exactly once; no skipped, pending, focused or empty tests. Expected outputs are independently authored, not obtained from a candidate or upstream implementation. The generator must not receive tests, fixtures or validators. Existing offline sandboxing, generated signature checking, full test collection, read-only inputs and integrity checks remain unchanged.

### Minimal infrastructure changes — approved extraction plan

Inspection shows that reusable verification mechanics exist, but their current host is still `experiments/native-typescript-contracts/verify.py`. Its `check(submission, box=...)` resolves paths against module-global `SPIKE`, stages adapters from `RUNNER` in that same directory, and imports NormalizeContact configuration at module load. Calling it directly from a sibling Box would retain structural dependence on the NormalizeContact experiment. Merely adding another definition or using `../` paths is insufficient.

The minimal proposed correction is an extraction, not a new verifier:

1. **Move existing Box-neutral verification mechanics into `boundscript_internal/`.** Give the existing check operation explicit `box_root` and `box` arguments instead of an implicit experiment root/default definition. Keep suite ownership, signature generation, fingerprint enforcement at the entry-point boundary, diagnostic classification, sandbox/resource policy, integrity checks and no-promotion behavior unchanged. The shared module must not import experiment configuration or know business Box names.
2. **Move the existing trusted verifier assets alongside those mechanics:** `vitest.config.mts`, `compiler-diagnostics.mjs` and `diagnostic-reporter.mjs`. Resolve them from the shared module location, not either Box root. Preserve their contents and mounted paths; they contain tooling policy, not business fixtures or validators. Do not maintain a second copied verifier or adapter set.
3. **Leave fixed entry points in each Box.** NormalizeContact's existing verifier becomes a thin wrapper selecting its unchanged definition and own root, retaining its CLI and historical `--baseline` behavior. RenderWelcome gets its own thin wrapper selecting only its own definition/root. Both wrappers check their own definition fingerprint when invoked by generation. No registry, auto-discovery, Box-name selector, plugin API, orchestration or generic job runner is needed.
4. **Add only RenderWelcome-local build/generation wiring.** Build its validators with the existing pinned Typia/TypeScript toolchain. Its fixed generator reuses `agent_workspace.py` and `container_runtime.py`, mounts only its own task/contract and empty submission workspace, ends generation before invoking its own verifier process, and uses its own artifact/quarantine paths. Preserve scan/hash binding and existing failure handling; introduce no joint generation or promotion. Repository scripts and ignore rules may need explicit entries for this root; no dependency/version changes are expected.
5. **Adjust infrastructure tests for the extraction.** Retarget mechanics tests as needed, retain NormalizeContact regressions, and exercise the same check with two separate explicit roots/definitions. Verify that shared mechanics import no experiment and RenderWelcome's standalone path does not read NormalizeContact's root. Keep such infrastructure checks separate from RenderWelcome's small business suite.

Only the first three items change the location/parameterization of existing infrastructure. The fourth adds Box-local wiring; the fifth protects the refactor. These are future changes requiring explicit authorization, not changes made under this assignment. NormalizeContact's contract, task, fixtures, validators, properties and implementation must remain untouched; its verifier wrapper and infrastructure test imports would need mechanical changes only. This is the limited change to the original no-verifier-change constraint that must be authorized if implementation proceeds.

The resulting dependency direction is each independent Box → `boundscript_internal`, never Box → peer experiment. NormalizeContact can remain in its current directory. RenderWelcome has no reason to relocate or share its business inputs with it. The current CLI does not yet support this layout; no claim is made that today's NormalizeContact verifier verifies RenderWelcome.

### Independent lifecycle and limits

Each Box has its own definition fingerprint, task/contract, candidate workspace, trusted verification bundle, verifier invocation and local artifacts. Neither generator receives the other's source, tests, fixtures or task; neither verifier invokes the other Box. A future application can compose separately verified, human-accepted implementations through their public contracts, but composition is not a prerequisite or hidden phase of standalone verification.

Tests use locally generated Typia validators, not unexpanded Typia calls. Existing automatic promotion to an `accepted/` path is not explicit human acceptance or immutable publication. This proposal does not add an acceptance gate or change that lifecycle limitation. No generation, verification of a candidate or promotion occurs under this design assignment.

## 7. Approval and delivery review

The Product Owner approved the revised specification and explicitly authorized implementation, including the mechanical verifier extraction and thin fixed entry points. The approved scope remains the reduced suite, independent Box-root layout, consumer-owned contract, pure formatter boundary and application-owned composition.

The Product Owner subsequently reviewed and accepted the implementation delivery and authorized a local commit. No push, registry, orchestration layer, generic framework, versioning or business-rule changes to NormalizeContact were authorized. See assignment 0036 and the implementation report for actual work and verification evidence; proposal-time restrictions above describe the earlier design stage, not a revocation of subsequent authorizations.
