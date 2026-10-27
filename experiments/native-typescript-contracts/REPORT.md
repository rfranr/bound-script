# 0030 — Feasibility results

Observed on 2026-10-27, on `experiment/typescript-contracts`.
State: **InReview**; ready for independent review, not final acceptance.
All files under `experiments/minimal-box` remain unchanged, as do the original
npm test/generation commands. No RenderWelcome migration or architecture change.

## Current verification update

The native pipeline no longer invokes the legacy `verify_pair.check` after Vitest.
That redundant verifier recompiled submissions against the frozen baseline contract,
blocking evolution of the experiment's authoritative `src/contract.ts`. Strict
TypeScript checking now uses only the experiment contract. Vitest still consumes
all 20 unchanged original `CASES`, with Typia validation and fast-check properties.
Sandbox probes, independent offline verification, failure quarantine and
verify-before-promotion are unchanged; no frozen minimal-box files were modified.
The results below describe the initial feasibility run, which included the legacy
second stage, not a requirement to retain that stage.

## Outcome

**Feasible for this TypeScript Box.** A fresh Pi implementation was generated
without tests or peer implementation access through mounts, verified with Typia
and Vitest/fast-check in the original isolation policy, then promoted unchanged.
The same pipeline also passes the frozen baseline implementation. Both pass all
20 original external NormalizeContact cases, not just newly written tests.

The baseline already had native TypeScript interfaces/types; there was no
remaining NormalizeContact DSL to remove. The demonstrated improvement is
runtime input/output shape validation derived from those types plus independent
behavior/property checks, without a parallel handwritten schema.

### Live generation evidence

- Pi **1.4.0**, `openai-codex/gpt-6.1-sol`, medium reasoning; fresh empty workspace.
- Successful session: `01a17e20-a1c3-7772-b38b-1cd6113705e0`.
- Tools: **2 reads, 1 write, 0 edits, 0 Bash**, no tool failures. Reads were
  restricted by the observed read-path check to the authorized task/contract.
- Generation filesystem probes passed before Pi executed. Effective security
  checks passed before the auth copy. No tests or peer implementation were
  mounted; contract/task were read-only.
- Host auth hash and protected input hashes remained unchanged. The source
  passed the original/refreshed literal credential scan. No credential values,
  raw provider events or transcripts were saved in the repository.
- The generation container was removed before either offline verification stage.
- Promoted local source: `accepted/normalize-contact.ts`, SHA-256
  `ffbe49708ca9c0e741ceed0269e8e3c77c4bf2e4d7933e5cd571bd448c9bb591`.
- This is **byte-identical to the frozen baseline NormalizeContact source**.
  It was independently generated, not seeded/copied from the baseline. No manual
  repair occurred. The original accepted baseline sources were never replaced.
- The generated source and generated validators are Git-ignored local artifacts.

### Checks and comparison

| Check | Frozen baseline candidate | Fresh generated candidate |
| --- | --- | --- |
| Effective Podman security/resource policy | Pass | Pass |
| Protected mounts, absent repo/auth/peer, symlink write denial, offline network | Pass | Pass |
| Strict native TypeScript signature consumer | Pass | Pass |
| Typia runtime input/output validation | Pass | Pass |
| Vitest: 20 original examples | Pass | Pass |
| fast-check: 5 properties, 300 runs each, seed 30 | Pass | Pass |
| Original external verifier: 20 cases, repeatability, frozen inputs, fresh success contact | Pass | Pass |

The final saved-candidate and baseline comparison runs include the five-property
suite. Three additional validator tests pass, including 200 randomized Contact
shape checks and malformed union/error-value/input rejection examples. Strict
`tsc --project experiments/native-typescript-contracts/tsconfig.json` also passes.

Credential-free Python wiring tests pass: unchanged task/native consumer/contract,
cleanup on create/start/exec failure, read-only verification mounts, no tests in
generation mounts, and failed independent verification preserving prior accepted
bytes. The opt-in Podman test first establishes a positive baseline, then rejects
three synthetic submissions: wrong function result type; `any` hiding a wrong
runtime output shape; and a shape-correct but behaviorally wrong empty error
list. Accepted bytes remain unchanged. These synthetic negatives are separate
submissions, not repairs of the generated implementation.

The original container adapter suite passes (8 tests; optional engine smoke test
skipped). The **full original `BOUNDSCRIPT_RUNTIME=podman npm test` passes** in a
temporary worktree of `experiment/boundscript-next`: Greeting, 20 NormalizeContact
cases, 81 RenderWelcome dependency cases, and 20 integration cases. TypeScript
was copied locally into that worktree's tooling directory; no baseline sources
were edited. The worktree was removed afterwards. No experiment containers remain.

## What failed / operational findings

- Plain `npm test` on the dedicated branch stops at the frozen branch guard.
  That guard was intentionally not changed. Full baseline acceptance was run
  on its actual branch in a temporary worktree instead.
- `docker` on this host is a Podman wrapper. The Docker adapter rejects its
  unexpected `container=podman` environment entry. This was not bypassed;
  successful runs explicitly selected the existing Podman adapter. A genuine
  Docker engine was not validated here.
- An initial live generation attempt was interrupted by a **120-second outer
  command timeout**, after Pi wrote the submission but before verification or
  promotion. The leftover container was explicitly removed, and a completely
  fresh session completed with a 600-second outer budget. The interrupted source
  was not repaired or promoted. Generation makes real provider calls; there were
  two live Pi sessions, one completed end to end.
- A first baseline-worktree run using symlinked npm tooling failed the exact bind
  source check. Copying the installed TypeScript directory instead satisfied the
  unchanged mount policy. No security checks were relaxed.
- The old minimal-box README records resource-policy failures on an earlier host
  setup. In these runs Podman passed the **unmodified effective cgroup checks**,
  including the original 256 MiB verification and 512 MiB generation limits.

## Configuration and limitations

See [README.md](README.md) for files and exact reproduction commands. This spike
pins TypeScript 5.9.3, Typia 9.7.2, Vitest 5.0.5 and fast-check 4.10.2. Typia's
standard CLI generates validator source before Vite runs: no custom compiler,
patched TypeScript, custom DSL, Zod schema or generic runner is introduced.
The additional node_modules tree is read-only verifier tooling, never an agent
mount. Validators are rebuilt by the npm entry points, not committed artifacts;
when using Python entry points directly, run `npm run build:native` first.

Important boundaries of the result:

- Typia establishes **shape**, not normalization intent. For example a success
  containing empty strings, or a failure with an empty error list, satisfies the
  native union but can violate the task. Properties and examples remain essential.
  TypeScript readonly fields are not a runtime immutability guarantee.
- Typia `equals` checks reject ordinary additional fields but can allow additional
  `undefined` values. The behavioral invocation separately checks exact result and
  contact keys. No claim of universally exact serialization is made.
- Validation is at the independent test invocation boundary. This spike does not
  install a production boundary wrapper or make every future consumer validate.
- Tests/validators are authoritative relative to the **generation agent**, which
  cannot modify or access them through mounts. Candidate code in the verifier can
  see mounted tests, just as a verifier must load candidates. Candidate-controlled
  output and a successful Vitest exit are not hostile-program attestation.
- The original prototype exceptions remain: agent-readable auth and unrestricted
  generation bridge networking, shared host kernel, no complete import allowlist,
  no credential brokerage/egress firewall or proof of semantic correctness.
  Mount isolation does not prevent fetching public peer code over the network.
- One small TypeScript function and deterministic property samples do not establish
  general correctness, multi-language portability, richer dependency enforcement,
  production readiness, or feasibility of all historic DSL capabilities.
- The fixed generation path is adapted locally to avoid modifying frozen baseline
  assets. Keeping this small duplication synchronized is a maintenance limitation,
  not a reason to introduce a generic runner during this spike.

## Recommendation

For this scope, **native types + generated validators + independent tests can
replace a separately maintained contract/schema language without losing the
observed isolation or verify-before-promotion guarantees**. Keep Markdown for
intent, native types for structure, tests for semantics, and the existing sandbox
for authority. Those are complementary responsibilities; Typia is not a sandbox
or a behavioral specification. Retain this as a successful feasibility spike,
not authorization to migrate RenderWelcome or redesign the architecture.
