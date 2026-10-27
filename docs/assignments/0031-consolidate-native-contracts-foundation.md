# 0031 — Consolidate Native Contracts Foundation

Status: In Review

## Human assignment

Create a clean, maintainable foundation from the existing `experiment/typescript-contracts` branch. This is consolidation/refactoring, not architectural redesign.

### Objectives

1. Remove obsolete experimental code, duplicated implementations, unused files and outdated documentation.
2. Consolidate the working autonomous generation and independent verification workflow.
3. Preserve the validated TypeScript + Typia + Vitest + fast-check + Pi + Podman approach.
4. Update documentation to describe the architecture that actually exists.
5. Establish a clear starting point for a reusable framework.

### Required work

- Review repository structure and propose minimal cleanup. Inventory affected files and justify large deletions before performing them; retain required behavior and evidence.
- Consolidate duplicated generation and verification code where maintenance improves without weakening security.
- Clearly separate native contracts, natural-language tasks, candidates and independent verification.
- Remove obsolete branch restrictions; enforce actual safety boundaries instead.
- Preserve Podman/Docker isolation, resource checks, permissions, cleanup, contract validation, Typia, Vitest, fast-check, phase diagnostics, failure classification, failed-candidate quarantine and verify-before-promotion.
- Keep baseline regression checks runnable.
- Update README, developer workflow and current architectural decisions; distinguish implemented from proposed/deferred features; document reproducible generation, verification and testing commands.
- Remove or archive obsolete documentation without losing important experimental findings.

### Constraints

- No custom BoundScript DSL, generic orchestration framework, plugin system or premature abstractions.
- Do not change business requirements or acceptance criteria to make tests pass.
- Do not modify accepted implementations unless strictly necessary and justified.
- Do not relax sandbox or credential handling restrictions.
- No automatic commits.
- Stop and report if an architectural decision or loss of baseline evidence requires human approval.

### Acceptance criteria

- Clean structure with documented responsibilities for major components.
- Existing baseline and native TypeScript verification scenarios pass.
- Tests independent of branch names; no loss of validated security guarantees.
- Generation and verification remain separate trust boundaries.
- README, architecture and developer workflow accurately reflect implementation.
- Concise report identifies removed files, retained evidence, decisions and remaining debt.
- Present final diff and test results for review; do not commit automatically.

## Authorized continuation — structural consolidation

The human requested completion of the structural consolidation after reviewing
that shared infrastructure was still owned by `experiments/minimal-box/`:

1. Move shared container infrastructure and agent workspace lifecycle outside
   `experiments/` into a clearly named internal package or directory.
2. Update both experiments to consume this shared infrastructure.
3. Keep each experiment's contracts, tasks, acceptance tests, verification rules
   and promotion policies independent.
4. Preserve Docker/Podman checks, credential handling, quarantine and
   verify-before-promotion.
5. Do not introduce generic orchestration, plugins or new framework APIs.
6. Update imports, tests and documentation; run relevant regression/integration checks.
7. Update this assignment and report with completed/deferred work and report
   final structure, results and unresolved dependencies.

Do not delete historical evidence, modify acceptance criteria, commit or push.
This continuation authorizes relocation of mechanics, not changes to task authority.

## Initial observations (not changed requirements)

- Current branch is `refactor/native-contracts-foundation`; no branch switch is needed.
- Three runners already have uncommitted edits. Consolidation will replace commented branch checks with explicit assertion preflights and remove the newly added arbitrary generation-error print, preserving diagnostic confidentiality.
- The native phone contract deliberately diverges from the original baseline. Historical `test:native:baseline` is documented as a potentially failing comparison, not a positive regression requirement. This incompatibility must be reported rather than changing contracts, fixtures or accepted implementations.
- Ignored local accepted/quarantined candidates are user evidence, not authorized deletion targets.

Implementation inventory, final diff summary and test evidence:
`docs/development/consolidation-report.md`.

## Delivery status after structural continuation

Completed for review, not accepted:

- Shared container policy and Pi workspace lifecycle now reside in the private
  `boundscript_internal/` package, outside both experiments. No new public API,
  orchestration framework or plugin system was introduced.
- Both experiments import that package through the checkout root. Shared tests
  are in `tests/internal/`; baseline policy tests remain in
  `experiments/minimal-box/test_workflows.py`, native policy/diagnostic tests in
  their own experiment. Old infrastructure locations have no copies or shims.
- Contracts, tasks, TypeScript acceptance tests, verification rules, promotion
  policies, credential handling, quarantine and historical evidence are retained.
- README, architecture, developer workflow, aggregate test commands and the
  consolidation report describe the actual structure and remaining limits.
- Post-relocation `npm run check`, full native verification, opt-in real Podman
  sandbox profiles and all native negative/diagnostic engine checks pass.

Deferred/unresolved: public/installable framework packaging, generic verification
orchestration, production hardening and previously documented operational/security
limitations. Genuine Docker and live provider generation were not newly tested.
Full native checks still need a local candidate; the historical old-source/new-
phone-contract comparison remains incompatible. No requirement, acceptance test
or accepted source was changed to conceal it.

The delivery was initially left uncommitted. The human subsequently reviewed it
and requested: “reviewed commit please”, authorizing a local commit of the reviewed
changes. No push was authorized. No provider calls or real promotions were
performed during consolidation. Status remains In Review; commit authorization
is not recorded as Product Owner acceptance.
