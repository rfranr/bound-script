# Verification diagnostics and live progress — review report

## Implementation

- Flushed phase start/pass/fail updates identify preflight, sandbox/security,
  TypeScript compilation, Typia validator tests, acceptance tests, fast-check
  properties, protected input integrity and cleanup.
- The unchanged Vitest tests run in three groups: 3 validator tests, 20 acceptance
  cases and 5 properties. Each phase prints executed test names/statuses, counts,
  exit status and bounded assertion differences. Filtered tests count as skipped.
- The existing narrow reporter consumes Vitest's structured TestCase results.
  It includes fast-check causes and structured Typia property path, expected type
  and actual value type, but never the Typia value. Arbitrary dynamic path keys
  are withheld. No custom test runner or new dependency was introduced.
- The temporary raw TypeScript stdout/stderr dump was removed. A fixed helper uses
  the standard TypeScript compiler API with equivalent strict/no-emit options and
  returns bounded diagnostic codes, locations and messages for host sanitization.
- Compilation, assertion, Typia, runtime exception, timeout, security/integrity
  and infrastructure failures receive distinct labels. Collection/startup,
  transport and invalid/missing reports fail closed. CLI failure handling prints
  no Python traceback or arbitrary exception message.
- Child stdout/stderr is discarded, not forwarded. Structured files are bounded,
  regular-file/no-symlink checked; stale prior-phase reports are removed. Sensitive
  environment values/common credential forms are redacted and terminal controls
  escaped. Diff lines have a fixed prefix. Pi/provider and generation-container
  diagnostics remain withheld.
- Generation retains the existing scanned-source quarantine path and never
  promotes a failure. Its verification deadline is now 360 seconds to accommodate
  the separated runs; sandbox limits and model/tool capabilities are unchanged.
  Standalone verification reports the retained input path, without moving it or
  copying an unscanned source into credential-scanned generation quarantine.

## Verification

- Existing `quarantine/failed-eicpfnez/implementation.ts` passed offline Podman
  verification: strict compilation, 3 validator tests, 20 acceptance cases,
  5 properties, unchanged effective security/resource probes and integrity checks.
  The implementation was not repaired or promoted.
- Native Python regression suite: 13 passed; 2 optional engine checks skipped.
- Engine-enabled diagnostic suite: all 10 tests passed, including real offline
  compiler-error, assertion-failure, Typia-failure and runtime-exception candidates.
  CLI output identifies the respective failure categories, retains each input and
  contains neither candidate console output/private error values nor tracebacks.
  The Typia case reports `$input.contact.name`, the contract's expected string
  type/constraint and actual type `number`.
- Unit regressions additionally cover success counts and phase ordering, immediate
  flushes, timeouts, tool startup/transport failures, test/hook timeout classification,
  compiler diagnostics sanitization, missing/invalid/oversized/symlink/stale reports,
  assertion redaction, dynamic Typia path suppression, and quarantine integrity,
  uniqueness, permissions and no-promotion behavior.
- Trusted validator tooling: all 3 tests passed. Original container adapter suite:
  8 passed, optional engine smoke test skipped. Root `npm test` remains blocked by
  its frozen baseline-branch guard on this experiment branch; it was not changed.

## Limitations / review notes

Phase updates are truly live; **individual test results arrive at phase end**.
Safe streaming would require another transport/protocol and is deliberately not
introduced. Separate Vitest starts add overhead and fail fast, so a failed phase
prevents later phases from running. At most 100 test summaries, 10 failed-test
records and 2 assertion/Typia details per record are retained; compiler details
are limited to 20 diagnostics. Reports themselves have a 256 KiB host read limit.
These bounds are ample for the current fixed 28-test suite, not a generic runner.

The stock JSON reporter does not expose structured Typia fields or original
assertion causes. The existing adapter is retained for that reason; unfiltered
text reporters would violate the output policy. Vitest exposes test/hook timeouts
through a fixed message prefix rather than a dedicated error code; only that
classification boolean is exported, never the message. Actual-type diagnostics
come from Vitest's serialized error metadata; unusual custom `toJSON` values or
serialized functions/symbols can obscure the original JavaScript type. The current
string/number/null/array/plain-object cases do not need an extra worker hook.

Sanitization is bounded best effort, not hostile-program attestation. A malicious
candidate can attempt to forge verifier-visible data; no new security guarantee
or relaxation is claimed. Functional acceptance tests, fixtures, task, contracts,
generated implementations and frozen minimal-box files were not modified.
No credentials, model calls or automatic promotion were used. The change was
reviewed and explicitly authorized for commit by the human.
