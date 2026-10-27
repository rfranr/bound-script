# 0036 — Design the RenderWelcome Box Specification

## Status

Completed — the Product Owner reviewed and explicitly accepted the implementation delivery and authorized a local commit. No push was authorized.

## Human-defined objective

Propose RenderWelcome as a second independent native Box alongside NormalizeContact. It consumes normalized contact information and produces a welcome message. Use the existing NormalizeContact public contract and native Box experiment as references. Keep the Box small enough for independent development and future composition.

## Required delivery

A proposed specification for Product Owner review covering:

- Public TypeScript input, output, signature and relevant types.
- Functional requirements, expected behavior and edge cases.
- Independently verifiable acceptance examples and properties.
- Integration with NormalizeContact's public output without implementation coupling.
- RenderWelcome-owned tests and fixtures compatible with the existing verifier.

## Constraints and authority

- Initial scope was design only. The subsequent implementation authorization below supersedes that restriction.
- Preserve NormalizeContact behavior, public contract and business verification assets. Only the approved mechanical verifier extraction and entry-point/test rewiring may change its infrastructure.
- Do not introduce framework abstractions or treat approval in principle as implementation authorization.
- Initial delivery prohibited commits and pushes; subsequent acceptance authorized a local commit only.
- The revised proposal was subsequently approved; do not expand its contract, business rules or infrastructure scope without further authorization.
- Acceptance remains exclusively with the Product Owner.

## Product Owner follow-up — design revision

The Product Owner approved the proposal in principle, retaining the independent consumer-owned contract, pure formatter boundary and application-owned composition. Before implementation, the requested revision must:

- Reduce acceptance/property coverage to what is necessary for the specified behavior.
- Give RenderWelcome its own Box root with no structural dependency on the NormalizeContact experiment directory.
- Reuse existing verification mechanics without a registry, orchestration layer or generic framework.
- Preserve independent generation and verification for both Boxes.
- Report minimal infrastructure changes required, without implementing them.

That revision was documentation-only. The subsequent authorization below permits implementation; it does not authorize commits, pushes or acceptance.

## Product Owner implementation authorization

The Product Owner approved the revised proposal and authorized implementing RenderWelcome with the approved consumer-owned contract and reduced acceptance suite, including the minimal extraction of existing verifier mechanics into `boundscript_internal/` and thin fixed Box-specific entry points.

- Preserve NormalizeContact behavior and existing regressions.
- Keep both Boxes independently generated, verified and structurally isolated.
- Do not introduce a registry, generic runner, versioning or additional abstractions.
- Run relevant verification suites and report evidence, limitations and deviations.
- Do not commit or push; leave the delivery ready for review. A passing candidate or local `accepted/` path is not Product Owner acceptance.

## Design-stage delivery evidence (historical)

- Proposal: [0036-render-welcome-specification.md](../proposals/0036-render-welcome-specification.md).
- Reviewed the native public contract, task, Box definition, verifier selection/staging and independent suite ownership rules, plus the historical RenderWelcome contract/task.
- Changes are limited to this assignment and the proposal. No executable contract, tests, fixtures, runner, candidate or accepted artifact was created.
- Revised the proposal to use six exact examples and one combined property, an independent Box-root layout, and an explicit minimal extraction plan for existing verifier mechanics and trusted adapters.
- Documentation whitespace checked with `git diff --check` and explicit checks of the untracked documentation files; no runtime tests or generation were needed for the design-only stage.

## Implementation delivery and verification

- Full [implementation report](../development/render-welcome-report.md) records changes, independent generation evidence, commands/results, limitations and the one outer-test-timeout rerun/cleanup.
- RenderWelcome now owns its contract, task, Typia validators, six fixtures, one 100-run combined property, fixed definition and entry points under `experiments/render-welcome-native/`.
- Extracted existing verification mechanics and byte-identical trusted adapters into `boundscript_internal/`. NormalizeContact retains its business assets and CLI behavior; only infrastructure/wiring tests changed.
- Independently generated RenderWelcome once using the fixed Pi runner; no manual candidate repair. Its ignored local artifact passed offline verification and standalone replay. Existing NormalizeContact source passed unchanged; no peer regeneration occurred.
- `npm run check` passed (52 Python tests with 6 opt-in skips, both tooling suites, public-contract compilation and baseline regressions). All opt-in internal (15), NormalizeContact (24) and RenderWelcome (7) engine tests subsequently passed with no skips.
- No semantic deviations or additional abstractions. Generated source/build artifacts remain ignored; local promotion alone does not imply acceptance.
- The Product Owner subsequently reviewed and accepted the delivery and authorized a local commit. No push was authorized.
- Before the authorized commit, `BOUNDSCRIPT_RUNTIME=podman npm run check` passed again with the same unit/tooling/compatibility/baseline coverage; whitespace checks passed. Ignored generated artifacts remain excluded.
