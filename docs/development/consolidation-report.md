# 0031 — Consolidation inventory and delivery report

## Initial inventory before cleanup

The repository has 57 tracked files; the DSL and its obsolete tooling have already been removed. No large deletion is warranted.

| Files | Disposition and justification |
| --- | --- |
| `experiments/minimal-box/contract.ts`, `task.md`, `slugger.ts`, `implementation/greet.ts` | Retain Greeting authority and original generated baseline evidence. |
| `experiments/minimal-box/two-boxes/{contracts,tasks,accepted}/*`, consumers and `application.ts` | Retain both baseline behaviors, dependency-injection checks and ordinary application composition. Do not modify accepted sources. |
| Both `generate.py` runners | Consolidate their duplicated credential-bearing container lifecycle into one small internal helper; retain fixed task selection and independent verification/promotion at each entry point. No job format or orchestrator. |
| `container_runtime.py`, `test_container_runtime.py` | Retain shared fail-closed Docker/Podman policy and effective-resource evidence. Under the authorized continuation, relocate mechanics to `boundscript_internal/` and their tests to `tests/internal/`; retain experiment-specific cleanup tests with baseline policies. |
| Three verification runners | Retain distinct human-owned behavioral oracles. Remove Git branch checks and the unused raw-output subprocess helper, not security assertions. Native diagnostics and tests stay independent of baseline fixtures. |
| Native `src/*`, `task.md`, `cases.json`, TS tests/configs/consumers and diagnostic adapters | All used by the native pipeline; retain. Generated validators remain disposable, not source authority. |
| Native Python tests | Retain and extend for branch-independent preflights and shared generation lifecycle. |
| Baseline `REPORT*.md`, native `REPORT.md`, `ACCEPTANCE-REPORT.md`, `DIAGNOSTICS-REPORT.md` | Retain dated experimental evidence in place; historical statements are not current operating instructions. |
| README files | Update current operating instructions; remove obsolete branch restrictions and duplication of historical host results. |
| `docs/assignments/*`, `docs/proposals/*` | Retain requirement/review history. Clearly label proposals and unimplemented work in current architecture docs. |
| Ignored native `accepted/`, `quarantine/`, `.generated/`, installed dependencies | Do not delete or alter user evidence. Local accepted copies are not tracked duplicates eligible for cleanup. |

The first delivery retained all paths; human review identified that this left
shared infrastructure owned by an experiment. The authorized continuation corrects
that structural gap. Experiment authority and historical evidence paths remain
unchanged, but shared mechanics and their tests are relocated as inventoried below.
No unique evidence or capability is deleted; obsolete duplicate blocks, unused
helpers and stale instructions are removed.

### Structural continuation inventory (before relocation)

| Original location | Final disposition and justification |
| --- | --- |
| `experiments/minimal-box/container_runtime.py` | Move to `boundscript_internal/container_runtime.py`; shared policy must not be owned by a baseline experiment. Update repository-root calculation, not policy. |
| `experiments/minimal-box/agent_workspace.py` | Move to `boundscript_internal/agent_workspace.py`; retain lifecycle/signature, use a package-relative runtime import. |
| `experiments/minimal-box/test_container_runtime.py` | Move shared adapter/resource/real-engine tests to `tests/internal/test_container_runtime.py`; preserve the pair cleanup test in baseline policy tests. |
| `experiments/minimal-box/test_agent_workspace.py` | Split shared lifecycle tests into `tests/internal/test_agent_workspace.py` and baseline workflow/promotion tests into `experiments/minimal-box/test_workflows.py`. |
| Five experiment entry points | Import qualified internal modules through the checkout root. Native runners no longer add the baseline experiment directory to their import path. |

No compatibility shims or copied infrastructure remain at the original locations.
This is a private package relocation, not a new framework API or orchestration layer.

## Known compatibility boundary

The native contract requires `phone`; the original baseline contract does not. `test:native:baseline` is a historical comparison that can fail against this evolved contract. Do not make it pass by changing either authority, baseline source or acceptance expectations. Original `npm test` remains the positive baseline regression. Current native accepted-candidate verification is a separate scenario.

## Delivery — ready for review, not accepted

### Final diff summary

- Added `boundscript_internal/agent_workspace.py`: one shared Pi lifecycle with
  the original exact mounts, probes, settings, event summaries, credential scan
  and cleanup. Both fixed generators retain their own verifier/promotion choices.
- Removed duplicate lifecycle blocks from both generators, all Git branch guards
  and the unused raw-output `run` helper. Replaced the pre-existing commented-out
  guards with assertion preflights. Removed the pre-existing unsafe arbitrary-error
  print; both generator CLIs expose only a safe error class.
- Relocated container policy and image/tooling/hash definitions to
  `boundscript_internal/container_runtime.py`. Its engine policy/checks are
  unchanged; only the repository-relative tooling path calculation changes with
  location. Both experiments consume the private package. Native verification
  imports no baseline verifier; independent behavioral oracles remain separate.
- Added scanned-source integrity checks after generation cleanup and before
  promotion. Extended lifecycle, promotion, failure/confidentiality and optimized-
  Python rejection regressions. Existing quarantine permission/digest checks stay.
- Moved shared regressions to `tests/internal/`, preserved local experiment
  policy tests, and added checkout-root/qualified-import regressions. `test:unit`
  runs all three test locations; `check` adds trusted Typia tooling and baseline.
  No dependency, contract, task, acceptance fixture, TypeScript test or accepted
  implementation changes. No automatic model calls in these aggregate checks.
- Replaced the root README with current architecture/workflows, updated both
  operational guides and developer workflow, added current architecture and this
  inventory/report. Historical reports, assignments and proposals remain in place.

Review tracked edits with `git diff`; new files appear in `git status --short`.
A complete review patch (including new files) is exported locally to
`/tmp/boundscript-0031.patch`; this temporary review artifact is not committed.

### First-delivery verification (before structural relocation)

These results retain the first delivery's evidence and original command paths;
the current post-relocation commands/results are recorded below.

Run on `refactor/native-contracts-foundation` with Node 24.16.0, Python 3.14.4,
Podman and the unchanged cached digest-pinned image. No branch switches, auth
mounts, provider calls, implementation repairs or real promotions were performed.

| Command | Result |
| --- | --- |
| `BOUNDSCRIPT_RUNTIME=podman npm run check` | PASS: baseline Python suite 13 passed / 1 opt-in skip; native Python suite 14 passed / 2 opt-in skips; 3 trusted Typia tests; full baseline below. |
| `BOUNDSCRIPT_RUNTIME=podman npm test` | PASS: Greeting type/security/network/3 behavior cases; NormalizeContact 20; RenderWelcome 81 dependency cases; integration 20. |
| `BOUNDSCRIPT_RUNTIME=podman npm run test:native` | PASS: strict compilation; effective sandbox/offline checks; 3 Typia tests, 20 examples, 5 seeded properties; integrity and cleanup. Uses pre-existing ignored local accepted candidate. |
| `BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/minimal-box -v` | PASS: all 14 tests including real generation/verifier resource, permissions and tmpfs profiles without Pi/auth. |
| `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/native-typescript-contracts -v` | PASS: all 16 tests including positive native verification and negative compilation/shape/behavior/runtime/output-confidentiality checks. |
| `BOUNDSCRIPT_RUNTIME=podman npm run test:native:baseline` | EXPECTED INCOMPATIBILITY: exit 1, TS2322, missing required `phone` in original baseline success. Sandbox passed; cleanup completed; source retained, never promoted. |
| `git diff --check` | PASS. |
| `podman ps -a --filter name=boundscript --format '{{.Names}}'` | Empty after all checks; no leftover experiment containers. |

Native candidate verified without alteration: SHA-256
`66cb5d47ba67d98523856c58601a67792345286e915766ecdeee598ac19bf407`.
Tracked accepted baseline paths, native `src/`, `task.md`, `cases.json`, and all
TypeScript acceptance/property tests have no diff. Historical evidence was not
rewritten. Mocked tests exercise generation success/failure and scan-to-promotion
hash continuity; they do not substitute for a new live Pi/provider run.

### Decisions and remaining debt

- Kept the validated native-types/Typia/Vitest/fast-check/Pi/container approach.
  No new architecture, orchestration framework, plugins, DSL or runtime wrapper.
- Completed the authorized structural correction: shared infrastructure is
  outside experiments. Baseline authority/evidence paths remain unchanged.
- Kept separate trust boundaries and independent behavioral authorities while
  sharing only mechanics; no sandbox or credential restriction was relaxed.
- **Human compatibility decision remains open:** if acceptance requires the old
  source to pass the evolved native phone contract, requirements need clarification.
  This delivery does not resolve that incompatibility by altering business rules,
  tests or accepted source. Positive baseline and current native scenarios pass.
- Genuine Docker and live provider generation were not newly exercised. Fixed
  Pi installation/auth paths and model availability remain environment-specific.
- Native accepted/quarantined sources remain local/ignored; a clean checkout
  needs a supplied candidate or authorized generation for full native checks.
- Existing prototype debt remains: agent-readable auth, unrestricted generation
  egress, shared kernel, incomplete import enforcement, best-effort diagnostics,
  no hostile-candidate attestation, no production validation wrapper. Phone
  normalization semantics need human requirements. Quarantine retention is manual;
  SIGKILL can interrupt cleanup; pair promotion is not atomic.

## Structural continuation — completed for review

### Final directory structure and ownership

```text
boundscript_internal/
  __init__.py                 # private package marker, no facade exports
  README.md
  container_runtime.py        # shared engines/policy/probes/image/tooling/hashing
  agent_workspace.py          # shared credential-bearing generation lifecycle
tests/internal/
  test_container_runtime.py   # shared security/resource/adapter tests
  test_agent_workspace.py     # shared lifecycle/scan/cleanup tests
experiments/minimal-box/
  generate.py, verify.py, verify_pair.py
  test_workflows.py           # baseline verification/promotion policy tests
  contract.ts, task.md, slugger.ts, implementation/greet.ts
  two-boxes/                 # tasks/contracts/accepted sources/wiring retained
experiments/native-typescript-contracts/
  generate.py, verify.py      # native verification/quarantine/promotion policy
  test_spike.py, test_diagnostics.py
  src/, task.md, cases.json, TS tests/configs/diagnostic adapters unchanged
  ignored .generated/, accepted/, quarantine/ unchanged in ownership
  historical reports retained
docs/
  assignments/, development/, proposals/
```

The internal package imports only standard-library code and its own sibling;
it has no experiment dependency. Runners resolve the package from the checkout
root even when invoked from another working directory. Shared tests no longer
import a baseline verifier for the image constant. The only intentional native
reference to baseline source is `--baseline`, not an infrastructure dependency.
The package itself is not mounted into Pi or the offline verifier.

No verification rule, promotion destination, credential path, sandbox mount,
resource bound, quarantine policy, contract or acceptance criterion was changed
by relocation. No historical report or accepted implementation was removed.
Existing repeated runner configuration and task-specific verification checks are
not converted into a generic framework API.

### Post-relocation verification

Same host/toolchain and pre-existing native candidate as the first delivery. No
auth mounts, provider calls, real promotions, commits or pushes were performed.

| Command | Result |
| --- | --- |
| `BOUNDSCRIPT_RUNTIME=podman npm run check` | PASS: internal 9 passed / 1 opt-in skip; baseline policies 6 passed; native policies/diagnostics 14 passed / 2 opt-in skips; 3 trusted Typia tests; full baseline integration. |
| Baseline integration included in `check` | PASS: Greeting security/type/3 behavior cases; NormalizeContact 20; RenderWelcome 81 dependency cases; composition 20. |
| `BOUNDSCRIPT_RUNTIME=podman npm run test:native` | PASS: effective sandbox/offline checks, strict compilation, 3 Typia tests, 20 acceptance cases, 5 seeded properties, integrity and cleanup. |
| `BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s tests/internal -v` | PASS: all 10 shared tests, including both real Podman resource/permission/tmpfs profiles without credentials/Pi. |
| `BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s experiments/native-typescript-contracts -v` | PASS: all 16 tests, including real negative signature/shape/behavior/runtime and diagnostic-confidentiality cases. |
| `BOUNDSCRIPT_RUNTIME=podman npm run test:native:baseline` | EXPECTED INCOMPATIBILITY remains after relocation: exit 1 / TS2322, missing `phone`; security checks and cleanup pass, accepted source unchanged. |
| `git diff --check`; final container inspection | PASS; no remaining `boundscript` containers. |

New import regression loads all five entry points in an isolated Python process
from an unrelated working directory, verifies that each uses the same qualified
internal modules and that no baseline/native workflow module is imported as
infrastructure. Existing optimized-Python rejection checks also run outside the
checkout. Tooling-path regression checks the relocated repository root.

### Completed versus deferred / unresolved dependencies

**Completed:** infrastructure ownership outside experiments; one shared workspace
lifecycle and one container policy; both experiments consume them; infrastructure
tests live outside experiments; local verification/promotion authorities stay
independent; affected imports, aggregate commands, README, architecture and
developer workflow are updated. Positive baseline/native and negative/security
checks were rerun after relocation.

**Deferred/unresolved:** no public/installable framework API or generic verifier/
orchestrator is introduced. The fixed checkout layout, Node tooling in
`node_modules`, cached pinned image, effective cgroup-v2 delegation, environment-
specific Pi 1.4.0 installation/auth paths and model availability remain operational
dependencies. Genuine Docker and live Pi/provider generation were not newly tested.
Native accepted candidates remain ignored/local; full native verification on a
clean checkout needs a supplied candidate or authorized generation. The historical
name/email baseline versus required-phone native contract incompatibility and all
previously documented security/semantic debt remain unresolved, not hidden by
changing tests or accepted source.

The delivery was initially left uncommitted. Following human review, “reviewed
commit please” authorized a local commit of these changes; pushing remains
unauthorized. Assignment 0031 remains In Review, not marked accepted. No approval
to discard evidence or change task semantics is inferred.
