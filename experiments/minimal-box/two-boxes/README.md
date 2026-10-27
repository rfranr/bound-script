# 0018 / 0018b: two independent Boxes

This extends the existing minimal-box reference, not a reusable runner. Tasks,
contracts, acceptance checks and `application.ts` are human-owned authority.

- **NormalizeContact:** `Contact -> NormalizeContactResult`; trim/collapse name
  whitespace, trim/lowercase email, accumulate ordered validation errors, return
  a discriminated success/failure union without mutation. The exact ECMAScript
  whitespace and deliberately simple Unicode-friendly email rules are defined in
  [the task](tasks/normalize-contact.md). Authorized Box dependencies: none.
- **RenderWelcome:** `(Contact, NormalizeContact) -> string`; call the supplied
  dependency exactly once on the original object and format success or errors.
  Its only authorized Box dependency is NormalizeContact's **public contract**.

These permissions are explicit in `tasks/*.md`; `contracts/render-welcome.ts`
imports the native dependency type. There is no new manifest format.

## Run from the repository root

Same installed Pi, Docker image, credentials and risks as the
[parent reference](../README.md). Install the existing TypeScript dependency with
`npm ci` if needed. No new packages are required.

```bash
npm run generate:pair # two fresh Pi processes/containers, then separate integration
npm run test:pair     # reverify both accepted sources and their composition; no model calls
npm test              # Greeting regression plus both Boxes and integration
```

`generate.py --pair` runs only the two named tasks, sequentially in independent
sessions. Each workspace starts empty. NormalizeContact gets `/inputs/task.md`
and `/inputs/contract.ts`; RenderWelcome gets those aliases for its own inputs
plus `/inputs/normalize-contact.ts`. Neither gets peer source, peer task, application
wiring, test files, verification code or the repository. The existing read-only Pi
runtime/auth mount, writable runtime tmpfs, unrestricted bridge networking and
resource limits are unchanged.

Each candidate is checked in a fresh credential-free, offline verifier container,
including a human-owned TypeScript consumer of the actual exported signature.
Behavioral expectations/assertions stay on the host. The RenderWelcome test injects
a deliberately different dependency result, so implementing its own normalizer
cannot pass by merely producing plausible welcome messages.

Only a passing submission is copied unchanged into `accepted/`. After both
individual promotions, a separate offline integration step loads ordinary
`application.ts`, which passes the accepted normalizer to the accepted renderer.
Twenty end-to-end cases check trimming, collapsing internal whitespace, lowercasing,
empty values, simultaneous errors, Unicode preservation and email rule boundaries.
The normalizer is also called repeatedly on frozen inputs. Eighty injected-result
renderer cases cover authoritative successes and ordered/duplicate/empty errors;
a further check requires dependency exception identity and exactly one call. Read-only mounts and before/after hashes check
that the integration did not repair either artifact. Promotions are per Box, not
an atomic pair transaction: failure stops the command but can leave an individually
accepted first artifact. No automatic retries, feedback or implementation repair.

## Boundary control and limits

Both actual generation environments and independent verification deliberately try
to read `/peer/implementation.ts` (`ENOENT`) and dynamically import it
(`ERR_MODULE_NOT_FOUND`). The missing mount/filesystem view rejects this access.
**This is not source-import allowlist enforcement.** It does not prevent imports
of exposed tooling, computed imports, transitive dependencies, or network retrieval
of public peer code. General boundary enforcement and a reusable runner are not
implemented here (0019/0020 are out of scope).

Existing prototype limitations apply: credentials readable by agent tools,
unrestricted generation networking, shared host kernel, writable runtime state,
finite behavioral observations and candidate-returned data that malicious code
could fabricate. Raw agent events/diagnostics remain in memory only; safe summaries
include session UUIDs, tool counts, failure counts and accepted-source hashes.
The literal credential scan is not a general secret/exfiltration detector.

Historical 0018 first-run results: [REPORT.md](REPORT.md).
Richer-domain two-generation comparison: [REPORT-0018b.md](REPORT-0018b.md).
