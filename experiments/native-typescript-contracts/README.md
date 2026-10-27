# 0030 — Native TypeScript contracts feasibility spike

NormalizeContact only. The frozen `../minimal-box` experiment, RenderWelcome,
application wiring and container policy are unchanged. Work is on the dedicated
`experiment/typescript-contracts` branch, based on `experiment/boundscript-next`.
See [observed results and limitations](REPORT.md).

## Authority and configuration

- `task.md`: independent, natural-language functional intent, copied unchanged
  from the baseline NormalizeContact task.
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
- `check-contract.ts`: unchanged strict native consumer from the baseline.
- `acceptance.test.ts`: Vitest 5.0.5; baseline examples are materialized from the
  original verifier's `CASES`, not redefined here. Five fast-check 4.10.2
  properties use seed 30 and 300 runs each: deterministic/non-mutating results
  with normalized successes/idempotence, Unicode/whitespace preservation,
  email casing/punctuation, ordered required errors, and malformed-email error
  accumulation.
- `validators.test.ts`: independent shape-validation positives/negatives and
  200 randomized Contact checks, plus explicit examples of what shapes cannot
  establish about behavior.

`verify.py` mounts trusted checks, native contract, generated validators and
installed npm tooling read-only in a fresh **offline** verifier. The submission
is also read-only; only a disposable cache directory is writable. It reuses the
unmodified Docker/Podman adapter, pinned image, nonroot identity, dropped
capabilities, read-only root, and effective CPU/memory/PID checks. Runtime input
and output validation happens at the test boundary, not inside agent code.
Strict TypeScript checking uses `/inputs/contract.ts` mounted from the experiment's
`src/contract.ts`. The independent Vitest suite executes all 20 unchanged original
acceptance cases, Typia validation and fast-check properties. The legacy
`verify_pair.check` is not invoked: it recompiles against the frozen original
contract and would prevent this experiment's contract from evolving. Only its
case fixtures and baseline artifact path are reused. No candidate executes on
the host.

`generate.py` is a fixed NormalizeContact adaptation of the existing generator,
not a generic runner. Its generation/credential/probe/event-sanitization path is
retained locally rather than refactoring frozen baseline files. Both generators
share the original container adapter. Future baseline policy changes must be
reviewed against this small duplicated path.

The agent receives only `/inputs/task.md`, `/inputs/contract.ts`, read-only Pi
and the explicitly authorized auth file, plus an initially empty writable
`/implementation`. It receives neither Typia/Vitest tooling nor tests nor peer
code. Generation ends before verification starts. Only a regular, size-limited,
credential-scanned source that passes the independent native verification pipeline
is copied unchanged to `accepted/normalize-contact.ts`. Failed verification
leaves the previous accepted source untouched. No integration promotion or
RenderWelcome migration is performed.

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
budget of at least 450 seconds for live generation and 300 seconds for the
opt-in negative suite (including container cleanup). The original Pi 1.4.0
installation path, model and auth-file exception are retained in `generate.py`.

To check another standalone candidate, without promotion:

```sh
npm run build:native
BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/native-typescript-contracts/verify.py /absolute/path/candidate.ts
```

## Offline failure diagnostics and quarantine

Offline Vitest failures report exit status, failed test names and bounded assertion
expected/actual/diff fields, including fast-check assertion causes. Collection,
unhandled/process errors, missing reports and transport failures are identified
as verifier infrastructure failures without raw error text. The dedicated reporter
never exports console output, error messages/stacks, counterexamples or environment
dumps. A fixed parent process discards candidate stdout/stderr; host-side filtering
redacts sensitive environment values and common credential forms and JSON-escapes
control characters. This is bounded, best-effort diagnostic sanitization, not
attestation against hostile code forging reporter artifacts. Pi/provider logs and
generation-container diagnostics remain withheld; the shared container adapter and
all sandbox restrictions are unchanged.

When generation succeeds and the credential scan passes but independent verification
fails (including timeout/launch failure), only the unchanged scanned source is saved
under `quarantine/failed-*/implementation.ts`. Each local entry is unique, with a
0700 directory and 0600 file. No logs, auth or runtime state are retained. Failed
credential scans are never quarantined. Verification failure never promotes or
replaces the accepted source. Quarantine retention is local and manual; remove an
entry when no longer needed. Existing failures whose temporary workspace has already
been deleted cannot be recovered retroactively.

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
checkout has no accepted spike implementation: use `test:native:baseline` for a
credential-free comparison, or generate independently before `test:native`.
No generated implementation was manually repaired. No automatic commit occurs.

The baseline `npm test` deliberately retains its original branch guard and
must run on `experiment/boundscript-next` (or in a temporary worktree for that
branch). Do not weaken it just to run on this dedicated experiment branch.
