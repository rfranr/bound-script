# Current architecture — native contracts foundation

Current implementation, consolidated under assignment [0031](../assignments/0031-consolidate-native-contracts-foundation.md).
This records the existing approach, not approval of a new framework architecture.
Assignment [0036](../assignments/0036-design-render-welcome-specification.md)
adds independent native RenderWelcome and extracts existing verification mechanics
into the private shared package; the Product Owner reviewed and accepted its delivery.
Historical experiment reports describe earlier states; proposed integration in
`docs/proposals/0018c-architectural-integration.md` is not implemented.

## Purpose and Box lifecycle

BoundScript is a **developer tool, not an AI runtime platform**. A Box represents
a bounded software unit with a public contract, independent verification and an
integration interface. It is a generated software asset intended to become part
of a consuming project through its public interfaces. Architecturally, its
implementation may consist of functions, classes, modules or components; a Box
is not restricted to a single function or source file. Current experiments use
fixed TypeScript function exports and single-file candidates, not the full range
of these intended implementation forms.

Developers own contracts, requirements and acceptance criteria; AI agents
implement within those boundaries. Independent verification and explicit human
acceptance are required before an implementation becomes a trusted project asset.
Once accepted, a Box should be reproducible and usable without BoundScript, Pi or
an LLM at application runtime. Consuming applications should not require an AI
agent at runtime; the development sandbox is not their deployment model.

Boxes may eventually be integrated as libraries, modules, UI components, services
or runtime-loaded components. Future integration may support hierarchical
composition and imports between Boxes; current baseline ordinary TypeScript
composition does not establish those broader capabilities. Boxes may also
eventually produce standalone executable artifacts, such as CLI tools; this is
not a current capability. Different integration models may need different
execution and security guarantees. These are architectural intentions, not
implemented integration mechanisms or guarantees supplied by current verification.

### Planned versioning (not implemented)

The intended lifecycle is:

1. Generate a candidate Box.
2. Verify it independently.
3. Obtain human acceptance.
4. Publish an immutable, identifiable Box version.
5. Integrate that specific version into the consuming project.

Regeneration must produce a new candidate, never silently overwrite an accepted
version. Publishing a new version must not automatically update existing consumers.
Version numbering, compatibility rules, storage and distribution mechanisms remain
undecided. This document introduces no registry, manifest or runtime loader.

Current experiments verify and promote source to local `accepted/` paths, which
can be replaced by subsequent successful generation. That directory name does not
establish explicit human acceptance or immutable publication. The runners do not
yet implement the planned versioned lifecycle or a human-acceptance gate.

## Authority and trust (current implementation)

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
   containers. The native verifier stages a temporary signature consumer using
   `boundscript_internal/typescript_contract.py`, deterministically from module
   paths and export names, without agent involvement. Both native entry points
   import the same explicit `native_box.py` definition: public task/contract,
   function type/export, destination and independent verification bundle. A
   generation-side definition fingerprint is required to match in its verifier
   subprocess before candidate verification. No registry or export inference is
   involved; implementation mounts and trusted tool adapters remain runner
   conventions. Each Box declares exact test-file suites/categories and support
   inputs relative to its own verification root. Every conventional test/spec
   JS/TS file must be assigned once; missing, undeclared, duplicate or empty
   selections fail closed. Runtime validation and acceptance tests are mandatory;
   properties can only be absent through an explicit not-applicable declaration.
   All declared tests must run, with no skipped/pending/focused tests. The
   generated signature check and per-suite Vitest configs are hashed and mounted
   read-only alongside independently owned tests/fixtures, not retained as source
   artifacts. No business-specific test filename or description selects tests.
   Native verification mechanics and the unchanged trusted Vitest/compiler adapters
   now live in `boundscript_internal/`, not in a business Box directory. Thin fixed
   entry points pass their own root and definition; no discovery or registry is
   involved. Native verification performs strict TypeScript compilation, Typia
   validator tests, guarded examples/properties, protected-file hashes and cleanup.
   NormalizeContact retains its 20 examples and five seeded properties. Independent
   RenderWelcome owns six examples and one combined property (seed 36, 100 runs).
   Baseline oracles retain Greeting, dependency-injected RenderWelcome and
   ordinary TypeScript integration checks. They intentionally remain separate:
   sharing task oracles would compromise independent contract evolution.
4. **Promote:** each fixed generator invokes its external verifier and copies
   only a successful unchanged source. Hash checks bind scanning and verification
   to promotion. Native verification failure retains only scanned bytes in
   private ignored quarantine; scan failure never enters quarantine. Standalone
   verification never promotes and leaves its input in place. This automatic
   local promotion is not the human acceptance or version publication described
   in the planned lifecycle.

Code reuse is not context reuse: Pi never receives tests, repository, peer
implementation, host sessions/settings/extensions, container sockets or verifier
code. Sharing a host helper does not add any agent mount. In the verifier the
candidate can read tests/tooling, but cannot modify them through mounts.

## Portable native Box layout

Assignment [0038](../assignments/0038-portable-box-imports.md) keeps the public
contract and implementation as siblings:

```text
<box>/
  contract.ts
  <implementation>.ts          # imports types from './contract'
```

Both native sandboxes reproduce this layout under `/implementation/`, with the
candidate named `implementation.ts` and a read-only `contract.ts`. Generation
mounts only this public contract and `/inputs/task.md` as task inputs: no tests,
validators, repository, peer implementations or peer contracts are added. Current
Boxes declare no implementation dependencies. The public contracts retain their
existing type-only Typia tags dependency; consumers need the existing `typia`
package for type checking, not a BoundScript runtime.

As corrected by assignment [0039](../assignments/0039-remove-contract-promotion-ownership.md),
each fixed native generator promotes only the unchanged verified implementation to
its own `accepted/` directory, retaining the existing `normalize-contact.ts` or
`render-welcome.ts` filename. The public contract remains a consumer-owned read-only
input, not a generated or promoted artifact. Consumers integrate the implementation
beside their existing `contract.ts` in their Box directory, including nested ones;
sibling imports need no rewriting, aliases or custom resolution. Promotion neither
creates nor updates contracts. The compiler adapter rejects non-relative module
specifiers and nonliteral dynamic imports in candidate source; ordinary TypeScript
resolution checks the relative imports. This is not universal hostile-code import
or transitive-dependency enforcement. Future permitted dependencies must preserve
relative placement and be explicitly staged; no peer implementation access or
hierarchical composition mechanism is introduced here.

Contract hashes bind generation through promotion, and source hashes bind
credential scanning through verification and byte-identical copying. No import
rewriting occurs after verification. Older local candidates using `/inputs/contract`
or `../inputs/contract` must be generated anew (or submitted as new candidates
before verification); they are not silently repaired or aliased. Historical
baseline runners and their accepted source bytes remain unchanged.

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
there is no compiler patch or custom Vite transformer. Vitest runs exact declared
files, without test-name patterns. NormalizeContact's unchanged mixed
acceptance/property file is run once in an explicitly combined phase, separate
from its runtime-validator suite and TypeScript compilation. Boxes with separate
category files receive separate phases. Reports retain relative file paths and
must account for every declared file with executed tests; bounded-report
truncation is a failure. Details are emitted at phase completion, not streamed
per assertion.

## Consolidation choices

- Separate shared mechanics into the private `boundscript_internal/` package,
  outside `experiments/`. It contains container policy, the Pi workspace
  lifecycle and deterministic signature-check generation, with no experiment
  imports or public framework API. Preserve paths
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
  typescript_contract.py      # deterministic temporary TypeScript signature consumer
  box_definition.py           # explicit inputs/suites, ownership checks, fingerprint
tests/internal/               # shared lifecycle/security/resource regressions
experiments/minimal-box/      # baseline authority, workflows and policy tests
experiments/native-typescript-contracts/
                              # NormalizeContact authority, workflows and policy tests
experiments/render-welcome-native/
                              # independent consumer contract, formatter tests and workflow
tests/integration/            # application-owned public-contract compile check
docs/                         # assignments, current docs and historical proposals
```

The dependency direction is experiments → internal mechanics, never the reverse.
RenderWelcome's root/definition, local Typia build, fixed generator and verifier
have no dependency on NormalizeContact's directory. Neither Box receives peer
source, tasks or tests during generation; neither standalone verifier invokes its
peer. Application-owned composition can narrow the normalization result and pass
its public success contact structurally to the consumer-owned welcome contract.
The compile-only check in `tests/integration/` imports only public contracts and
is not either Box's standalone oracle or generation input.

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
repair loops remain deferred. No accepted sources are manually repaired. Native RenderWelcome is a separate
formatter Box, not a migration of the historical dependency-injected baseline.
No broader architectural proposal is promoted to implemented capability by this
document; versioning, registry and application orchestration remain absent.

Reproduction commands: [root README](../../README.md),
[native workflow](../../experiments/native-typescript-contracts/README.md),
[baseline](../../experiments/minimal-box/README.md).
