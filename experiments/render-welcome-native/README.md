# RenderWelcome — independent native Box

Assignment [0036](../../docs/assignments/0036-design-render-welcome-specification.md),
[approved specification](../../docs/proposals/0036-render-welcome-specification.md).
The Product Owner reviewed and accepted the implementation delivery.

`renderWelcome` takes its own consumer-owned `WelcomeContact` (readonly nonempty
name/email/phone) and returns exactly `Welcome, NAME! <EMAIL>`. Name/email are
verbatim; phone is ignored. It is a pure synchronous formatter, not a normalizer.
The application owns normalization, failure handling, composition and safe text
rendering. Invalid direct calls have no prescribed business behavior.

## Ownership and independence

- `task.md` and `src/contract.ts` are the only agent-visible Box inputs.
- `src/validators.ts` derives Typia validators; `.generated/` is disposable.
- `fixtures/welcome-cases.json` owns six exact examples.
- `acceptance.test.ts` owns those examples and one combined fast-check property
  (seed 36, 100 runs): formatting, phone independence, call independence and
  immutability. `validators.test.ts` owns three small table-driven shape tests.
- `native_box.py` explicitly declares both suites and all support files.
- `verify.py` selects this root/definition and calls the existing extracted
  `boundscript_internal/native_verifier.py`; it never promotes.
- `generate.py` is fixed to this Box, reuses the existing disposable workspace
  mechanics, ends generation before running the separate offline verifier, and
  promotes only unchanged scanned/verifiable source. Failed verification saves
  scanned source only to a private local quarantine; failed scans are not saved.

No definition, runner, build or standalone test imports or reads the
NormalizeContact experiment. Its implementation, task and fixtures are not
inputs to this Box. Shared verifier assets live under `boundscript_internal/`,
not in a peer Box. There is no discovery, registry or joint runner.

## Run from the repository root

Requirements and isolation limitations are the same as the
[root guide](../../README.md): Node 24.16+, installed pinned npm dependencies,
Python assertions enabled, cgroup-v2 delegation and the cached pinned engine image.
No image pull, dependency installation or runtime selection is implicit.

```sh
npm run test:welcome:tooling       # builds Typia; 3 shape tests, no engine/model/auth
npm run build:welcome
python3 -B -m unittest discover -s experiments/render-welcome-native -v

# Billable, fresh isolated Pi; requires existing configured Pi/auth locations:
BOUNDSCRIPT_RUNTIME=podman npm run generate:welcome
# Verify the local generated artifact again without model/auth:
BOUNDSCRIPT_RUNTIME=podman npm run test:welcome
# Verify an explicit candidate without promotion:
BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/render-welcome-native/verify.py /absolute/path/candidate.ts

# Positive generated candidate required; then reject signature/shape/behavior/mutation negatives:
BOUNDSCRIPT_WELCOME_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman \
  python3 -B -m unittest discover -s experiments/render-welcome-native -v

# Application-owned compile-only compatibility check of both public contracts:
npm run test:contact:contracts
```

Use `BOUNDSCRIPT_RUNTIME=docker` for genuine Docker. Allow 900 seconds for a live
generation invocation and 300 seconds for the welcome engine suite. Current fixed
model: `openai-codex/gpt-5.6-luna`, low reasoning, same as the existing native
NormalizeContact runner. There are no automatic repairs, retries or peer calls.

`.generated/`, `accepted/` and `quarantine/` are ignored local artifacts. A clean
checkout has no candidate: generate one independently or supply a candidate path.
`npm run check` builds both Boxes' validators and runs credential-free unit/tooling,
public-contract compatibility and baseline regressions; it does not require local
native accepted artifacts. Full native candidate verification is separate.

## Limits and evidence

See [0036 implementation report](../../docs/development/render-welcome-report.md).
Passing verification and automatic promotion to `accepted/render-welcome.ts` do
not constitute Product Owner acceptance or immutable publication. The generator's
existing promotion semantics are unchanged. Runtime validators run at the test
boundary, not as production wrappers. Tests/review are not hostile-code proof;
import enforcement is incomplete, credential access and unrestricted generation
networking remain prototype exceptions. No versioning or runtime framework is added.
