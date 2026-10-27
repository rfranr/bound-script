# Current architecture — native contracts foundation

Current implementation, consolidated under assignment [0031](../assignments/0031-consolidate-native-contracts-foundation.md).
This records the existing approach, not approval of a new framework architecture.
Historical experiment reports describe earlier states; proposed integration in
`docs/proposals/0018c-architectural-integration.md` is not implemented.

## Authority and trust

1. **Define:** human-owned Markdown describes intent; native TypeScript defines
   structural interfaces. Neither replaces the other. Independent fixtures,
   contract consumers and properties establish observed semantics. Typia derives
   validators from types; no parallel handwritten schema or DSL exists.
2. **Generate:** fixed Python entry points select a known task and public inputs.
   `boundscript_internal/agent_workspace.py` owns the shared Pi lifecycle, mounts, probes, event
   summaries and literal credential scan. Its context yields a temporary source
   and scanned digest only after removing the credential-bearing container.
   It neither imports tests nor chooses a verifier or promotion destination.
3. **Verify:** separate Python processes create fresh offline, credential-free
   containers. Native verification performs strict TypeScript compilation, Typia
   validator tests, 20 independent examples with runtime input/output guards,
   five seeded fast-check properties, protected-file hashes and cleanup.
   Baseline oracles retain Greeting, dependency-injected RenderWelcome and
   ordinary TypeScript integration checks. They intentionally remain separate:
   sharing task oracles would compromise independent contract evolution.
4. **Promote:** each fixed generator invokes its external verifier and copies
   only a successful unchanged source. Hash checks bind scanning and verification
   to promotion. Native verification failure retains only scanned bytes in
   private ignored quarantine; scan failure never enters quarantine. Standalone
   verification never promotes and leaves its input in place.

Code reuse is not context reuse: Pi never receives tests, repository, peer
implementation, host sessions/settings/extensions, container sockets or verifier
code. Sharing a host helper does not add any agent mount. In the verifier the
candidate can read tests/tooling, but cannot modify them through mounts.

## Mechanisms retained

- `boundscript_internal/container_runtime.py` supplies a single Docker/Podman policy. Engine choice
  is explicit (`BOUNDSCRIPT_RUNTIME`); Docker is the default. The image is pinned
  by digest; automatic pulls and in-container package installation are absent.
- Inspection checks exact bind sources/destinations/access and allowed
  environment. Live procfs/cgroup-v2 checks require nonroot UID/GID, read-only
  root and bind flags, no-new-privileges, zero capability sets, one CPU,
  no swap, memory/PID bounds and generation tmpfs ownership/mode/flags/size.
- Generation: bridge networking, 512 MiB, 64 PIDs; private auth copy in a
  64 MiB, mode-0700, nosuid/nodev/noexec tmpfs. Host auth is read-only and hashed.
  Verification: network disabled, 256 MiB, 32 PIDs; no auth mount. Read-only
  trusted checks/tooling and native source; only disposable cache space writable.
- Fixed negative filesystem/symlink/peer/network probes and input hashes remain.
  Assertion checks must be enabled on every branch. Git names are not security
  evidence, so no runner consults them.
- Native diagnostics retain flushed phase updates, compilation/assertion/Typia/
  runtime/timeout/security/infrastructure classification and bounded structured
  reports. Candidate stdout/stderr and raw Pi/provider events are not forwarded.
  Sanitization remains best-effort, not a hostile-code attestation protocol.
- Ordinary failure cleanup is in `finally`; process kill/host failure may require
  manual cleanup. Pair promotion remains per Box, not an atomic transaction.

Versions remain pinned: TypeScript 5.9.3, Typia 9.7.2, Vitest 5.0.5,
fast-check 4.10.2 and an existing Pi 1.4.0 installation. Typia's standard CLI
expands `src/validators.ts` into ignored `.generated/` source before Vitest;
there is no compiler patch or custom Vite transformer. Native tests run in three
phases; details are emitted at phase completion, not streamed per assertion.

## Consolidation choices

- Separate shared mechanics into the private `boundscript_internal/` package,
  outside `experiments/`. It contains only container policy and the Pi workspace
  lifecycle, with no experiment imports or public framework API. Preserve paths
  for tasks, contracts, accepted baseline bytes and all experimental reports.
  Infrastructure tests live in `tests/internal/`; policy tests stay per experiment.
- Extract only the duplicated credential-bearing workspace lifecycle. Fixed
  generation entry points retain prompts/models, verification commands and
  promotion policy. No manifests, callbacks, plugin registry or generic runner.
- Keep common image, repository-relative tooling path and hashing definitions in
  the internal container module. Both experiments import its qualified package
  name. Direct entry points explicitly locate the repository root; no Python
  package installation or cross-experiment import path is required. Native
  verification no longer imports the baseline verifier. The unused raw-output
  subprocess helper and old infrastructure locations are removed.
- Keep independent native acceptance fixtures separate from baseline cases.
  The evolved phone contract is **not** compatible with baseline name/email-only
  sources; the historical comparison is a negative result, not a test to fix by
  changing acceptance criteria. `npm test` remains the positive baseline suite.
- Keep generated validators/local native accepted sources/quarantine ignored.
  A clean checkout supports baseline regression and trusted tooling tests; full
  native verification needs an explicitly supplied candidate or real generation.

## Current ownership structure

```text
boundscript_internal/          # shared host-side mechanics; no experiment imports
  __init__.py                 # private package marker; no facade/API exports
  container_runtime.py        # engine policy, probes, image/tooling/hash utilities
  agent_workspace.py          # Pi lifecycle, credential scan, generation cleanup
tests/internal/               # shared lifecycle/security/resource regressions
experiments/minimal-box/      # baseline authority, workflows and policy tests
experiments/native-typescript-contracts/
                              # native authority, diagnostics, workflows and policy tests
docs/                         # assignments, current docs and historical proposals
```

The dependency direction is experiments → internal mechanics, never the reverse.
Experiment paths remain independent except native verification's explicit
`--baseline` historical candidate selection. Prompts/model/auth paths, acceptance
rules, quarantine and promotion remain experiment-owned. Both generators may
share mechanics without receiving each other's files inside their containers.
Moving host Python modules does not alter any sandbox mount or runtime limit.

## Unchanged limits and deferred decisions

Types describe shape, not intent. Finite seeded properties and examples do not
prove general correctness. Phone formatting/normalization and new phone-error
semantics still require human requirements; no such rules are added here.

Agent-readable credentials and unrestricted generation networking remain explicit
prototype exceptions; a literal scan cannot prevent encoded leaks or exfiltration.
Mount isolation does not prevent downloading public peer code. Containers share
the host kernel; malicious candidates may fabricate verifier observations. There
is no universal import/transitive dependency enforcement or production runtime
validation wrapper.

Credential brokerage, egress restrictions, robust hostile-program verification,
artifact distribution/provenance, reusable orchestration, other languages and
repair loops remain deferred. No accepted sources are manually repaired, no
RenderWelcome Typia migration occurs, and no architectural proposal is promoted
to implemented capability by this document.

Reproduction commands: [root README](../../README.md),
[native workflow](../../experiments/native-typescript-contracts/README.md),
[baseline](../../experiments/minimal-box/README.md).
