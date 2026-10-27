# 0036 — RenderWelcome implementation delivery

**Status: Accepted.** The Product Owner reviewed and explicitly accepted the
implementation delivery and authorized a local commit. No push was authorized.

References: [assignment](../assignments/0036-design-render-welcome-specification.md),
[approved specification](../proposals/0036-render-welcome-specification.md),
[RenderWelcome guide](../../experiments/render-welcome-native/README.md).

## Delivered

- Independent `experiments/render-welcome-native/` root: approved consumer-owned
  contract, task, derived Typia validators, six independent exact fixtures and
  one combined property (seed 36, 100 runs). Shape coverage is three small tests.
- Fixed local Box definition and generation/verification entry points, build and
  tooling commands, ignored generated/source/quarantine paths, and workflow tests.
- Existing verification mechanics extracted to
  `boundscript_internal/native_verifier.py`, with explicit Box-root/definition
  arguments and no experiment imports. No registry, discovery, generic job runner,
  versioning or composition runtime was introduced.
- Existing Vitest config, compiler adapter and diagnostic reporter moved to that
  shared directory **byte-for-byte** (hash-compared with the original Git files).
- NormalizeContact's verifier is a thin fixed wrapper retaining its CLI,
  fingerprint validation, default local artifact and historical `--baseline` flag.
  Its task, public contract, business fixtures, validators and acceptance/property
  tests are unchanged. Infrastructure tests were mechanically retargeted.
- Application-owned compile-only compatibility check in
  `tests/integration/check-contact-composition.ts`: public success output assigns
  to the welcome input; a narrowed successful result can be rendered, while a
  normalization failure is not a valid formatter input. It is not a standalone
  Box oracle or agent input and uses no peer implementation.

## Independent generation

Executed `BOUNDSCRIPT_RUNTIME=podman npm run generate:welcome` once. The fixed
runner used Pi with `openai-codex/gpt-5.6-luna`, low reasoning, in a fresh empty
workspace. It read only the two authorized public files (own task/contract), wrote
one candidate and made no edit/repair calls. Generation ended before the separate
credential-free, offline verification process. Filesystem/peer probes, scanning,
strict compilation, all suites, input integrity and cleanup passed.

The candidate was promoted unchanged to the existing experimental local
`experiments/render-welcome-native/accepted/render-welcome.ts` path, ignored by
version control. SHA-256:

```text
935c24c06ede74df3bff5e71f4a8d5bcccf5a4a78073dd0fa5e244bf57eba51d
```

Inspection found only a type-only contract import and the exact synchronous
string formatter; no normalization, phone use, mutation, retained state, I/O or
runtime dependency. No manual candidate changes were made. Infrastructure/tests
were developed through Pi using `gpt-6.1-sol`, medium reasoning; candidate generation
was a separate model invocation as above. No NormalizeContact candidate was
regenerated, repaired or replaced; the existing local native source was verified.

## Verification evidence

All commands ran from the checkout with cached tooling/image; engine commands
used `BOUNDSCRIPT_RUNTIME=podman`.

| Check | Result |
| --- | --- |
| `npm run check` | PASS: builds both validator bundles; 52 Python tests with 6 opt-in skips; 3 NormalizeContact and 3 RenderWelcome tooling tests; public-contract compilation; full historical baseline regression. |
| `npm run test:native` | PASS on existing local NormalizeContact source: strict compilation, 3 runtime tests, 20 examples, 5 properties, security/integrity/cleanup. |
| `npm run generate:welcome` | PASS: independently generated candidate, strict compilation, 3 runtime tests, 6 examples and 1 property (100 runs), security/integrity/cleanup. |
| `npm run test:welcome` | PASS: standalone offline replay of that candidate, same complete suite; no model/auth or promotion. |
| `BOUNDSCRIPT_WELCOME_ENGINE_TEST=1 python3 -B -m unittest discover -s experiments/render-welcome-native -v` | PASS: 7 tests, no skips; generated positive plus signature, output-shape, exact-behavior and mutation negatives rejected; previous artifact unchanged. |
| `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 python3 -B -m unittest discover -s experiments/native-typescript-contracts -v` | PASS: all 24 tests, no skips; retained diagnostics, quarantine/promotion, two independent synthetic roots, negative compilation/shape/behavior, empty/skipped/pending/focused-suite rejection. |
| `BOUNDSCRIPT_ENGINE_TEST=1 python3 -B -m unittest discover -s tests/internal -v` | PASS: all 15 tests, no skips, including real credential-free generation/verification security profiles. |
| `npm run test:contact:contracts` | PASS: strict compile-only public-interface composition. Also included in `check`. |
| Diff and isolation checks | PASS: whitespace checks; NormalizeContact business assets unchanged; moved adapters hash-identical; fresh-process audit rejects peer-directory reads during RenderWelcome import/preflight. |

The first combined engine-test invocation exceeded its 600-second **outer**
command budget after the welcome suite passed and while NormalizeContact was
cleaning up its final negative test. The full NormalizeContact suite was rerun
separately with a 900-second command budget and passed (about 479 seconds). The
one leftover stopped/stopping test container was explicitly removed. No containers
remained afterward. This was a harness scheduling issue, not a relaxed verifier
limit or changed acceptance test.

## Limitations and deviations

- No behavioral or contract deviations from the approved specification.
  `test:unit` now explicitly builds both validator bundles first so clean checkouts
  can run the staging/ownership checks without pre-existing ignored build outputs.
- A clean checkout has no native candidate source. Generate independently or pass
  an explicit source to the Box's verifier; the candidate itself must remain
  ignored under the repository's generated-artifact policy. Tracked files contain
  the reproducible specification, independent verifier assets and fixed wiring.
- Existing automatic promotion to an `accepted/` directory is not human acceptance
  or immutable publication. This delivery adds neither an acceptance gate nor
  versioning. Only the Product Owner can accept the implementation delivery.
- Finite tests and source review are not proof of purity or hostile-code safety.
  Existing generation credential/network exceptions, incomplete import enforcement,
  shared host kernel, candidate-readable verifier tests and best-effort diagnostic
  sanitization remain unchanged. Runtime guards are test boundaries, not production
  validation wrappers.
- Composition evidence is public-type compilation only. No native application
  orchestrator, joint generation/verification or runtime integration promotion is
  added. Historical baseline runtime composition remains covered unchanged.
- Phone normalization semantics remain unresolved upstream and untouched here;
  RenderWelcome only requires a nonempty phone structurally and ignores its value.
