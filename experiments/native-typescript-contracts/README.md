# Native TypeScript contracts — working foundation

This root owns NormalizeContact only. Native RenderWelcome has its own
[independent sibling root](../render-welcome-native/README.md); neither Box's
standalone workflow depends on the other. Historical baseline behaviors,
application wiring and container policy are retained. All workflows run independently of Git branch names.
See [current architecture](../../docs/development/architecture.md) and
[consolidation inventory/results](../../docs/development/consolidation-report.md).
The [0030 findings](REPORT.md), [fixture report](ACCEPTANCE-REPORT.md) and
[diagnostics report](DIAGNOSTICS-REPORT.md) retain historical evidence, not current
branch restrictions or guarantees that old candidates meet today's contract.

## Authority and configuration

- `native_box.py`: one explicit, immutable `BoxDefinition`, imported by both native
  entry points. It selects task/contract paths, the mounted contract module,
  function type/export, accepted destination and independent verification bundle.
  `boundscript_internal/box_definition.py` holds this data, validates explicit
  suite ownership, renders the signature consumer and fingerprints the entire
  definition (including suites/inputs); there is no registry or source inference. Generation passes that fingerprint to the separate verifier,
  which rejects a mismatch before checking the candidate. Standalone verification
  uses the same fixed definition without requiring a fingerprint argument.
  Implementation mounts and trusted Vitest/compiler adapters remain runner
  conventions. Box-owned test files, fixtures, source and built validators are
  staged only from the definition's explicit suites and `verification_inputs`.
  Each future Box still needs its own human-owned tests, Typia validators and
  explicit build configuration. Synthetic tests exercise two independent suite
  layouts with actual Typia/Vitest/fast-check offline, not a second business Box.

- `task.md`: independent, human-owned natural-language functional intent.
- `src/contract.ts`: authoritative native `Contact`, discriminated result union,
  error literals and function signature. Initially copied from the baseline,
  this is the experiment's evolving authority, not the frozen original contract.
  The baseline already used native types; this spike adds derived runtime
  validation and independent property tests, not another contract language.
- `src/validators.ts`: Typia `createEquals` / `createAssertEquals` calls for input
  and output. No separately maintained runtime schema or Zod.
- `tsconfig.json`: strict TypeScript 5.9.3. Typia **9.7.2** is pinned for its
  `>=4.8 <5.10` TypeScript support and standard `typia generate` CLI. No compiler
  patch, custom compiler, transformer integration into Vite, or new runtime.
  Typia 15 uses a different tooling path; this spike does not adopt it.
- `.generated/`: disposable Typia-expanded TypeScript, built from `src/` before
  every npm entry point. Vitest/Vite can transpile it normally; directly loading
  unexpanded Typia calls would not perform runtime validation.
- `check-contract.ts`: strict signature consumer generated deterministically by
  `boundscript_internal/typescript_contract.py` in the verifier's temporary checks
  directory. There is no source artifact to maintain or commit, and the agent
  neither generates nor receives it. It is hashed and mounted read-only with the
  other checks, then removed with the temporary directory.
- `cases.json`: human-owned acceptance data local to this experiment. The 20
  historical name/email inputs and expected outcomes are retained, with
  `phone: "+34600111222"` added to every input. Expected successes specify only
  name/email: no normalized phone value is prescribed. Fixtures are copied
  byte-for-byte into the read-only verifier checks, never generated from Python
  or mounted into the agent container.
- `acceptance.test.ts`: Vitest 5.0.5 consumes the local fixtures. Five fast-check 4.10.2
  properties use seed 30 and 300 runs each: deterministic/non-mutating results
  with normalized successes/idempotence, Unicode/whitespace preservation,
  email casing/punctuation, ordered required errors, and malformed-email error
  accumulation.
- `validators.test.ts`: independent shape-validation positives/negatives and
  200 randomized Contact checks, plus explicit examples of what shapes cannot
  establish about behavior.

`verify.py` is a thin fixed entry point selecting this root and its unchanged
definition. The extracted `boundscript_internal/native_verifier.py` and shared
trusted Vitest/compiler adapters contain the existing verification mechanics,
with explicit Box-root/definition arguments and no experiment imports. They mount
trusted checks, native contract, generated validators and
installed npm tooling read-only in a fresh **offline** verifier. The submission
is also read-only; only a disposable cache directory is writable. It reuses the
unmodified Docker/Podman adapter, pinned image, nonroot identity, dropped
capabilities, read-only root, and effective CPU/memory/PID checks. Runtime input
and output validation happens at the test boundary, not inside agent code.
Strict TypeScript checking uses the definition's `contract_module` mounted from
its `contract_path` (`/implementation/contract.ts` and `src/contract.ts` today).
The independent Vitest suite executes the 20 locally owned
acceptance cases, Typia validation and fast-check properties. It validates the
complete result before projecting name/email for exact behavioral comparisons.
The success key check includes the contract's required `phone` field; phone
formatting/normalization is not specified by these tests. Existing determinism,
immutability, fresh-object, error-order and idempotence checks remain.

Neither `verify_pair.CASES` nor `verify_pair.check` is imported or invoked.
The frozen baseline source path remains available only for the explicit
`--baseline` comparison; an old baseline implementation may fail the evolved
phone contract. No candidate executes on the host. See the
[fixture decoupling report](ACCEPTANCE-REPORT.md) for results and open assumptions.

`generate.py` remains a fixed NormalizeContact runner, not a generic orchestrator.
All fixed generators use `../../boundscript_internal/agent_workspace.py` for the shared
Pi workspace, credential/probe/event-summary/scan lifecycle and
`../../boundscript_internal/container_runtime.py` for engine policy. This private
package imports no experiment code; shared regressions live in `../../tests/internal/`.
The native runners no longer add the baseline experiment directory to `sys.path`. The helper removes the generation container before yielding a source and
scanned digest; each generator independently selects verification and promotion.
Native verification imports only shared infrastructure, not a baseline verifier.

The agent receives only `/inputs/task.md`, `/implementation/contract.ts`, read-only Pi
and the explicitly authorized auth file, plus a writable `/implementation` with
no seeded implementation. The sibling contract is mounted read-only. It receives neither Typia/Vitest tooling nor tests nor peer
code. Generation ends before verification starts. Only a regular, size-limited,
credential-scanned source that passes the independent native verification pipeline
is copied unchanged to `accepted/normalize-contact.ts`. Promotion publishes only
the implementation, never the public contract. The consumer integrates that source
beside its own existing `contract.ts`; generated type imports use `./contract` in
both sandboxes and the consumer. The contract remains a consumer-owned read-only
input, not a generation output.
Existing type-only Typia tags require `typia` for type checking. Legacy sandbox-path
candidates are not rewritten after verification; generate a new candidate instead.
See the [portable layout](../../docs/development/architecture.md#portable-native-box-layout).
Failed verification
leaves the previous accepted source untouched. No integration promotion or peer generation is performed by this root.
The new native RenderWelcome workflow is separate, not a migration of the
historical dependency-injected baseline Box.

## Run

From the repository root, with Node 24.16+, Python 3, and dependencies installed:

```sh
npm ci
npm run test:native:tooling             # trusted validator tests only; no container/model/auth
npm run build:native
python3 -B -m unittest discover -s experiments/native-typescript-contracts -v

# Same cached pinned image and effective engine requirements as the baseline:
BOUNDSCRIPT_RUNTIME=podman npm run test:native:baseline
BOUNDSCRIPT_RUNTIME=podman npm run generate:native  # billable Pi; explicitly authorized auth mount
BOUNDSCRIPT_RUNTIME=podman npm run test:native     # saved local generated artifact; no model/auth
BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman \
  python3 -B -m unittest discover -s experiments/native-typescript-contracts -v
```

Use `BOUNDSCRIPT_RUNTIME=docker` for a genuine Docker engine. No automatic image
pulls or package installation occur inside either container. Set a command
budget of 900 seconds for live generation and 600 seconds for the complete
opt-in native suite (including two synthetic layouts and container cleanup). Independent verification
has a bounded 360-second generation-side deadline for its separated phases;
container resource limits are unchanged. The existing Pi 1.4.0
installation path and auth-file exception are retained in `generate.py`. Its current
model is `openai-codex/gpt-5.6-luna`, low reasoning; historical runs may differ.

To check another standalone candidate, without promotion:

```sh
npm run build:native
BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/native-typescript-contracts/verify.py /absolute/path/candidate.ts
```

## Independent suite configuration

`VerificationSuite(categories, files)` names literal paths relative to the Box's
`verification_path`, with one or more of `runtime`, `acceptance`, `properties`.
Every `*.test.*` / `*.spec.*` JavaScript/TypeScript test file under that
root must be assigned exactly once, including nested files (`.ts`, `.tsx`, `.js`,
`.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs`). Different fixture names and directory
structures are explicit `verification_inputs` (files or directories), not known
by the verifier. No test source or description is parsed to infer requirements.

Runtime validation and acceptance are always required. Properties are required
unless the human-owned definition explicitly declares
`optional_categories=('properties',)` and declares no property suite. This is
reported as `NOT APPLICABLE`, not a pass. Existing property files cannot be
silently omitted: the test-directory inventory must still be fully covered.
All declared suites run; optional does not mean skip failures or missing files.
A mixed file can declare multiple categories and is executed once in a combined
phase, without duplicating tests or inventing a description-to-category mapping.

A missing input/test, duplicate or undeclared test file, empty suite, empty file
collection, unexpected collected file, skipped/todo/pending test, focused `.only`
selection or truncated report fails verification. The bounded reporter retains
relative paths (not just basenames) and the host requires each declared file to
execute at least one test. All staged files, generated suite configs and trusted
adapters are hashed and read-only. Existing business test implementations,
fixtures, contracts and runtime input/output guards are unchanged.

## Live verification diagnostics and quarantine

Every phase prints flushed `START` and `PASS`/`FAIL` updates: preflight,
sandbox/security, strict TypeScript compilation, Typia validator tests, Vitest
acceptance tests (including full runtime guards), fast-check properties, input
integrity and cleanup. Vitest executes the **unchanged** test suites with exact
file selection, never test-description filters. NormalizeContact declares two
runs: 3 runtime-validator tests, then the combined 20 acceptance cases and 5
properties already present in one human-owned file. That phase is explicitly
reported as `Vitest acceptance tests + fast-check properties`; the verifier does
not infer which descriptions are properties. Boxes that independently own
separate files get separate category phases. Each run reports relative paths,
full test names, counts, exit status and bounded assertion differences.

**Streaming limitation:** phase updates are live, but test details are emitted at
the end of each phase, not per test. The existing narrow reporter uses Vitest's
structured TestCase API; no custom test runner is introduced. Its adapter is
needed because the standard JSON reporter omits structured Typia fields and
assertion causes. Raw text reporters are not forwarded because they can include
candidate console output, stacks and values. Separate runs add startup overhead
and fail fast: later phases are not attempted after a failing phase.

Compiler diagnostics come from TypeScript's standard compiler API with the same
strict/no-emit options, not raw CLI stdout/stderr. Output includes bounded TS
codes, approved source locations and sanitized messages. Typia failures include
known contract property paths, expected types and **actual value types only**;
values and arbitrary dynamic property keys are withheld. Error causes from
fast-check are traversed without exposing its counterexample messages.

Compilation, assertion, Typia, runtime, timeout, security/integrity and verifier
infrastructure failures have distinct labels. Expected failures exit nonzero
without Python tracebacks. Collection/unhandled errors, tool startup/process
failures and missing/invalid reports fail closed without arbitrary error text.
A fixed parent process discards child stdout/stderr; reports are size-bounded,
regular-file/no-symlink checked and cannot reuse stale preceding-phase results.
Host filtering redacts sensitive environment values/common credential forms and
escapes terminal controls; diff lines have a fixed output prefix. This remains
best-effort sanitization, not hostile-program attestation. Pi/provider events,
credentials and generation-container diagnostics are never forwarded. The shared
container policy and all sandbox restrictions are unchanged.
See [diagnostics verification results](DIAGNOSTICS-REPORT.md).

When generation succeeds and the credential scan passes but independent verification
fails (including timeout/launch failure), only the unchanged scanned source is saved
under `quarantine/failed-*/implementation.ts`. Each local entry is unique, with a
0700 directory and 0600 file. No logs, auth or runtime state are retained. Failed
credential scans are never quarantined. Verification failure never promotes or
replaces the accepted source. Quarantine retention is local and manual; remove an
entry when no longer needed. Existing failures whose temporary workspace has already
been deleted cannot be recovered retroactively. Standalone verification leaves its
input source in place, reports that location on failure and never promotes it;
it does not copy an unscanned standalone source into generation quarantine.

Rerun a quarantined source without credentials or another model call:

```sh
npm run build:native
BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/native-typescript-contracts/verify.py \
  experiments/native-typescript-contracts/quarantine/failed-<id>/implementation.ts
python3 -B -m unittest discover -s experiments/native-typescript-contracts -p test_diagnostics.py -v
BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman \
  python3 -B -m unittest discover -s experiments/native-typescript-contracts -p test_diagnostics.py -v
```

`.generated/`, `accepted/` and `quarantine/` are ignored and must not be committed. A clean
checkout has no accepted native implementation or quarantined candidates: supply
an existing candidate by path without model calls, or generate independently before
`test:native`. `test:native:baseline` is a credential-free historical comparison
expected to fail strict compilation because the original implementation lacks the
native required phone field. The positive baseline regression is `npm test`.
No generated implementation was manually repaired. No automatic commit occurs.

`npm test` runs the unchanged baseline behaviors on any branch. `npm run check`
builds both native validator bundles and combines credential-free Python unit
tests, both trusted tooling suites, application-owned public-contract compatibility
and baseline container regressions. It does not require an ignored native accepted
artifact. `npm run test:native` is the separate full native candidate check.
Assertion preflights, effective sandbox/resource checks and cleanup remain mandatory.
