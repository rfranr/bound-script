# Deterministic Box handoffs

Assignment [0019](assignments/0019-implement-deterministic-task-derivation.md) implements the accepted [0018 design](assignments/0018-design-deterministic-task-derivation.md). The Product Owner [accepted reviewed implementation `b692da02f54a36beabce47f1bc41e4d7a68ac926`](assignments/0019-implement-deterministic-task-derivation.md#product-owner-acceptance-and-completion-evidence), including its exclusive publication correction, and authorized **M2 — Completed**. M3 remains Planned under [0020's bounded amendment](assignments/0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment): own-package temporary workspaces and tool-free Pi generation, with candidate compilation/tests exclusively in disposable credential-free network-disabled containers. Directories are not security sandboxes. Whole-agent/OAuth-proxy qualification and 0021 are no longer prerequisites. [0022 implementation](assignments/0022-run-bounded-independent-implementation-pilot.md) is Proposed; no agents/assets have started and explicit approval is required. Preserve the existing OpenAI/Pi provider/model. This is an external repository adapter, not a compiler/runtime feature, planner, candidate loader, or agent integration.

## Human gate and invocation

Before operational derivation, an authorized human must:

- Approve the exact architecture and selected task/scope/policy versions and confirm their consistency.
- Check task responsibility, requirement IDs, representative examples, and acceptance criteria; do not duplicate or redefine public interfaces in prose.
- Check private scope and permitted dependencies/tools (or explicitly none), keeping authoritative inputs, trusted tests, and wiring outside candidate control.
- Resolve missing intent, conflicts, or missing context with the Product Owner/Architect. Do not infer or repair requirements.

**Successful derivation verifies structure, never approval.** Nonempty unapproved Markdown can render. There is no approval flag/parser, dirty-tree gate, hash, authenticated policy, or semantic Markdown checker.

From the repository, with its locked dependencies installed:

```sh
npm ci
delivery=$(mktemp -d /tmp/bound-handoff-delivery.XXXXXX)
npm run handoff -- "$PWD" tests/fixtures/handoff/input.json "$delivery/all" --all
# Or select exactly one explicitly listed pair, not a director invocation:
npm run handoff -- "$PWD" tests/fixtures/handoff/input.json "$delivery/greeter" GreetingSystem Greeter
# After use, removing the dedicated delivery parent removes links AND backing data:
# rm -r -- "$delivery"
```

Use fresh destinations for every invocation. The trusted fixture associates `examples/structured-types.bound` with two human-readable tasks and shared scope/policy. It is a small test demonstration, not operational approval or the M3 pilot. Output may live outside the repository and must not be committed. The script is `tooling/derive-handoff.ts`; the pure renderer is `tooling/handoff-render.ts`. `npm run build` builds tooling into disposable `.tool-dist/`.

The positional interface requires an explicit root, repository-relative binding path, output directory, and `--all` or exact `system box`. Root and output are resolved by the caller's cwd; input paths are always relative to the explicit root. Errors exit nonzero with stage and applicable path/Box. They do not assert anything about approval. Existing output entries (including candidate directories, files, and symlinks) are rejected. All selected packages are validated/rendered before publication. The complete tree is written into a unique sibling `.handoff-data-*` directory, then exposed by **one atomic, exclusive relative symlink creation** at the requested output path. Unlike ordinary directory rename, this cannot replace even an empty destination created concurrently. An `EEXIST` failure leaves the winning destination untouched and removes only this invocation's unpublished backing tree. Other publication failures also clean that tree and fail closed; there is no non-atomic fallback if directory symlink creation is unavailable.

On success the sibling directory is the actual output data, not job state. The output symlink and backing directory must stay together; moving or removing only the symlink does not move or remove its data. Prefer a dedicated disposable delivery parent as above, and remove that parent after use. Alternatively inspect the relative symlink target and remove both generated entries. The eight-file per-Box layout and all rendered bytes remain unchanged; publication metadata is outside the byte guarantee and derivation rules remain version 1. This adds no lock, manager, orchestration, or persistent execution record.

This is still a trusted local-filesystem operation: source inputs and ancestor directories must not be adversarially replaced during invocation. Atomic publication protects the final destination from concurrent creation, not from subsequent deletion/modification or hostile ancestor-directory changes, and is not a security boundary.

## Exact input

```json
{
  "format": "boundscript/handoff-input",
  "version": 1,
  "architecture": "examples/structured-types.bound",
  "policy": "tests/fixtures/handoff/policy.md",
  "boxes": [
    {
      "system": "GreetingSystem",
      "box": "Greeter",
      "task": "tests/fixtures/handoff/greet-task.md",
      "scope": "tests/fixtures/handoff/scope.md"
    }
  ]
}
```

All keys are required; unknown keys/versions, duplicate pairs, invalid identities, malformed shapes, unsafe/noncanonical POSIX paths, traversal, absolute paths, symlink path components, missing/nonregular files, invalid UTF-8, and empty Markdown are rejected. Bindings are explicit: there is no name/filename/director-based selection inference. Whole-system validation includes unused declarations; unused valid Boxes can be selected. A source director is still required but is never executed or bundled. There is no standalone contract-only input.

## Package and authoring environment

Each `<output>/<system>/<box>/` contains exactly:

```text
handoff.json
README.md
contract.box-spec.json
task.md
scope.md
policy.md
generated/contract.d.ts
seed/implementation.ts
```

The existing canonical version-1 contract is the **sole packaged public interface**, with shared records resolved inline. The declarations are generated, not another authority. Task instructions remain distinct from formal contract semantics. Markdown snapshots preserve exact bytes, including BOM, CRLF, Unicode, and missing final LF; generated text uses UTF-8, LF, and one final LF. Metadata has fixed key order and only format/version/rules version, system/Box/operation, selected input paths, and fixed entrypoint. It contains no hashes, approval references, toolchain/test references, inventory, or package ID. Full source, unrelated implementation/context, hidden tests, credentials, and dependencies are not bundled.

An external controller prepares read-only `handoff/` beside writable `candidate/`, then copies the seed to `candidate/implementation.ts`:

```typescript
import type { Implementation } from '../handoff/generated/contract.js';

export const implement: Implementation = (input) => {
  throw new Error('Not implemented');
};
```

The controller supplies `package.json` with `"type": "module"`, TypeScript and config, not editable package assets. A minimal strict test configuration is:

```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "NodeNext", "moduleResolution": "NodeNext",
    "strict": true, "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true, "isolatedModules": true,
    "verbatimModuleSyntax": true, "types": [], "skipLibCheck": false,
    "outDir": "built"
  },
  "include": ["candidate/*.ts", "consumer.ts"]
}
```

A trusted `consumer.ts` imports named `implement` from `./candidate/implementation.js`; this checks the export convention, which an annotation alone cannot establish. Type-only imports disappear: no runtime `contract.js` is generated or needed. The projection exports `Input`, `Result`, and `(input: Input) => Result | Promise<Result>`, with sorted `Record_<name>` aliases and quoted sorted fields. Empty records use `Record<string, never>`. For void results, **explicitly return `undefined`**, including async functions. Implicit return is rejected by the tested TypeScript authoring convention even though runtime implicit undefined remains valid.

Static typing does not establish own-key exactness, nominal origin, finite numbers, or predicates. Symbol-key extras can type-check even on empty records. Existing strict decoding and runtime [verification](box-development-spec.md#standalone-verification) remain authoritative. Agents may add permitted private helpers/tests only inside `candidate/**`, further narrowed by scope; never edit protected inputs/contracts/shared types, requirements, trusted tests, wiring, dependency manifests/lockfiles, or policy. New dependencies, public interfaces, or responsibilities need human approval.

This adapter never compiles, loads, or executes candidates. The independent compilation/import checks are **trusted test harnesses only**, not a production compilation service. Directories/worktrees and Node subprocesses are not security boundaries. Untrusted execution requires M3 isolation. No M3/M4 enforcement is implemented.

## Fresh regeneration policy

Affected workflow scope is distinct from observable output differences:

| Change | Human-controlled action |
| --- | --- |
| Any source edit | Regenerate all still-selected Boxes from that source and revalidate the whole source. Irrelevant valid director/declaration/whitespace edits can yield identical bytes. |
| Task or scope | Regenerate every referencing Box. |
| Shared policy | Regenerate every referencing package. |
| Rules/templates or supported tool environment | Full derivation, direct byte comparison, and regressions; intentional rendering behavior changes need a rules-version decision. Current rules version is 1. |
| Package edited/added/deleted | Discard and rederive into a fresh output. |
| Box removed/renamed | Retire its old selection; do not silently migrate candidates. |
| Candidate/private-test/trusted-test-only edit | No handoff regeneration; rerun affected verification. Evidence tracking/enforcement is M4. |
| Approval-only change | Authorization can change with identical bytes; the adapter cannot detect it. |

The existing language grammar does **not** support comments. A comment edit therefore triggers the same all-source policy but fails source parsing and publishes nothing; this assignment does not extend the grammar. Whole-source validation intentionally overinvalidates and cannot infer unrecorded requirement or integration impacts. Humans decide candidate reuse/revision and affected reverification. There is no watcher, impact graph, incremental state, currentness database, automatic repair, or promotion gate.

Compare fresh directory file sets and bytes directly, not hashes. Same explicit inputs under the same supported environment produce identical bytes regardless of input key/Box order, cwd, output root, or directory enumeration. Input path changes may change metadata even if content is equal. Permissions/mtimes, candidates, approval decisions, and verification outcomes are outside this guarantee. Environment/rules changes require comparison rather than an untested universal cross-platform/version reproducibility claim.

## Verification and delivery evidence

Tested with **Node v24.16.0**, **TypeScript 5.9.3**, locked repository dependencies on Linux. The repository engine floor remains Node >=22.12.0; no broader handoff cross-version reproducibility claim is made.

- `tests/handoff.test.ts`: exact eight-file golden; canonical Greeter byte equality; repeated roots/order/cwd; snapshots; structural failures; all-or-nothing publication; concurrent empty/populated directory, file, and symlink destinations created by a separate process immediately before the real publication syscall (identity and contents preserved, unpublished backing tree cleaned); fail-closed unsupported publication; conservative two-Box regeneration matrix. Comment edits demonstrate validation failure, not comment support.
- `tests/handoff-consumer.test.ts`: 16 design-spike cases plus all primitives, sorted/deduplicated aliases and prefix collisions (20 independent strict compilation cases); successful built ESM imports without runtime declarations. Separate LoadUser/Greeter packages consume fixed trusted implementations and prewritten wiring, strictly decode packaged JSON, and verify human-owned expected outputs. A guarded Node consumption process forbids compiler-root/frontend/Langium loading and director execution; malformed output is rejected rather than repaired.
- Existing verifier tests retain coverage for finite numbers, exact own fields/symbol extras, and output-before-postcondition ordering. No duplicate evaluator or changed formal/runtime semantics.

See [roadmap delivery evidence](roadmap.md#m2--deterministic-task-derivation) for full regression results and the verified, accepted M2 exit gate. These tests do not demonstrate agent determinism, universal correctness, dependency/security enforcement, the M3 pilot, or comparative evaluation.
