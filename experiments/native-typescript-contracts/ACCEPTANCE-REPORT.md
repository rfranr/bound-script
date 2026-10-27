# Acceptance fixture decoupling

## Changes

- `cases.json` is now human-owned acceptance data within this experiment.
  All 20 historical name/email inputs and expected outcomes are preserved;
  each input adds the illustrative `phone: "+34600111222"`.
- `verify.py` copies this file byte-for-byte into the read-only checks mount.
  It no longer imports `verify_pair` or generates JSON from legacy `CASES`.
  The explicit `--baseline` option retains only a historical source-file path.
- Vitest validates complete inputs/results with Typia, then compares the exact
  approved name/email projection on successes and exact ordered errors on
  failures. The success contact key check now matches the existing contract's
  `name`, `email`, `phone` shape. No expected phone output is invented.
- All five fast-check properties remain. Inputs and structural-validator examples
  now include the illustrative phone. Name/email idempotence uses that fixed
  phone input rather than asserting a phone normalization round-trip rule.
  Determinism, immutability and fresh-result checks remain.
- Regression tests verify local fixture contents, byte-identical staging into
  checks, the current contract mount, strict compiler invocation and successful
  verifier import/execution while `verify_pair` imports are blocked.

## Verification

- One-time migration comparison: all 20 name/email input/expected pairs exactly
  match the historical cases after removing the added input `phone`. This is an
  execution-time comparison during development, not a dependency in the tests.
- Python native regression suite: 9 passed, 2 opt-in engine tests skipped.
- `npm run test:native:tooling`: all 3 validator tests passed.
- Podman verification of existing local
  `quarantine/failed-eicpfnez/implementation.ts`: passed strict TypeScript,
  Typia, 20 acceptance cases, 5 fast-check properties and security/offline probes.
- An older local candidate (`failed-9fxg1xln`) failed the Vitest suite; it was
  not repaired, promoted or used to redefine the expected results.
- `npm run test:native` cannot select a saved artifact because the default
  `accepted/normalize-contact.ts` is absent locally; explicit candidate-path
  verification above does not require that file or another model call.
- Original container adapter tests: 8 passed, optional engine test skipped.
  Root `npm test` still stops at the frozen baseline branch guard on the
  dedicated experiment branch. No frozen files or branch guards were changed.

## Unresolved assumptions and scope

The previous whole-object success assertions required exactly `name`/`email` and
were incompatible with a required phone field. The tests now preserve their
name/email assertions without prescribing a normalized phone value. Full Typia
validation still enforces the **existing** native contract, including its phone
string/minimum-length annotation; this assignment adds no phone formatting,
length, country-code or normalization rule.

The illustrative number is supplied as input to preserve existing successful
name/email scenarios and exact error lists. Passing these examples does not
establish phone correctness. What constitutes a valid or normalized phone,
and whether other inputs should produce phone errors, remains a human decision.
No assertions covering such new behavior were added.

Contracts, task, generated implementations, generation/promotion/quarantine logic,
shared Podman policy and frozen minimal-box files were not modified. No model
calls or automatic promotion occurred. The change was reviewed and explicitly
authorized for commit by the human. Fixture ownership is independent; runtime
tooling still intentionally reuses the existing sandbox.
