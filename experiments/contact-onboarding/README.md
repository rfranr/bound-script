# ContactOnboarding pilot — Assignment 0022

From the repository root, run one command:

```bash
node tooling/run-contact-pilot.mjs --run-dir /tmp/contact-onboarding-01
```

Use a **fresh directory outside the repository**. The runner asks for execution
confirmation and the approved spending policy before making any model calls.
Do not confirm until launch and spending are authorized. Installing this runner
or passing its mocked tests does not launch the pilot.

Prerequisites: the existing repository dependencies, native authenticated Pi
1.4.0, Node 24.16.0, TypeScript 5.9.3, Docker 29.1.3, Git, Bash and Python 3.
Native Pi's global `cacheWarming` must already be `"off"` (the default can make
extra model requests); the runner checks but never changes global settings.
Version/profile mismatches stop for review. No authentication probes or provider changes.

The runner prepares/checks a separate checkout of frozen revision
`aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`, collects independent tools-off Pi
JSON responses from A then B, saves source automatically, and invokes the frozen
Docker evaluator. It never compiles or executes generated source on the host.
Both initial submissions precede feedback. Any permitted revision uses only the
same Box's history and operator-approved requirement IDs/failure class—never raw
test logs. Ambiguous/incomplete output, automatic recovery or compaction stops;
integration permits no repair.

Results: `<run-dir>/results.json`. Private session histories, raw responses,
numbered command logs, immutable candidate snapshots and `selected-pair.json`
remain alongside it. Inspect failed-stage logs locally; never give hidden case
data or peer material to either agent. Review/redact results before sharing;
record human effort and actual charges separately when not observable. A stopped
trial is retained, not automatically retried. Do not reuse the run directory.
A pass does not automatically close M3 or run the conventional baseline.

Directories/tools-off are not OS isolation; Docker shares its kernel, and tests
and candidates share a JavaScript realm. Results are observations, not security
attestation. Frozen contracts, tests, evaluators and historical validation evidence
are unchanged; this README and the runner are operator conveniences only.

Validate without model calls or Docker:

```bash
node --test tests/run-contact-pilot.test.mjs
```

Authority: [Assignment 0022](../../docs/assignments/0022-run-bounded-independent-implementation-pilot.md).
Historical preparation evidence: [VALIDATION.md](VALIDATION.md).
