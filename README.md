# BoundScript Next

**BoundScript controls boundaries, not business logic.** It is not a programming
language or an application orchestrator. Humans define Boxes; agents implement
them with ordinary languages and tooling. A Box can be a function, library,
service, component, or application. Application logic and wiring remain ordinary
application code.

Work happens on `experiment/boundscript-next`. The original DSL implementation,
including its historical pilot, remains on `feature/agent-driven-architecture`.

## The working skeleton

One TypeScript Greeting Box demonstrates four responsibilities without four
packages:

- **Define:** human-owned task, native public contract, authorized dependency
  interface, and capabilities expressed by the task and concrete sandbox policy.
- **Implement:** Pi and its tools run in a disposable Docker workspace. Only
  authorized Box inputs, runtime tooling, credentials explicitly accepted for this
  prototype, and the writable implementation are exposed—not the repository.
- **Verify:** a separate credential-free, offline environment runs type, behavior,
  dependency-call and negative-access checks. The agent cannot modify the tests.
- **Promote:** only a passing source file is copied back as the accepted artifact.
  Multi-Box consumption and application integration are not implemented yet.

## Run

Requires Linux, Docker, Python 3, Node 24.16+, and the digest-pinned Node image
listed in `docs/boundscript-next/minimal-box/verify.py` already cached locally.

```bash
npm ci
npm test          # Verify the saved implementation; no model calls or credentials
npm run generate # Real Pi generation, independent verification, then promotion
```

Generation additionally requires the existing Pi 1.4.0 installation and
`~/.pi/agent/auth.json` at the paths in `generate.py`; it makes billable provider
calls. See the [experiment](docs/boundscript-next/minimal-box/README.md) for the
exact environment, commands and observed results.

**Prototype limitations:** generation has unrestricted bridge networking and
agent-readable credentials, explicitly authorized for this experiment. Docker
shares the host kernel. Tests establish observations, not general correctness or
security attestation. Dependency imports are not comprehensively enforced. The
verifier is outside the agent's environment; hostile candidate output is not
inherently trustworthy.

## Removed, retained, deferred

- **Removed:** Langium, the DSL/compiler/interpreter/director, executable artifact
  transforms, old demos/tests, ContactOnboarding tooling, and monorepo build setup.
- **Retained:** the working one-Box Docker/Pi reference, native TypeScript
  contracts, explicit dependency injection, independent checks and promotion.
- **Deferred:** two-Box integration, artifact registry, transitive dependency
  enforcement, credential brokerage, egress hardening, other languages, generic
  runners/plugins, and production security. No new runtime or DSL replaces the old
  one.

Scope: [foundation assignment](assignments/0017-boundscript-next-foundation.md).
