# BoundScript Next

**BoundScript controls boundaries, not business logic.** It is not a programming
language or an application orchestrator. Humans define Boxes; agents implement
them with ordinary languages and tooling. A Box can be a function, library,
service, component, or application. Application logic and wiring remain ordinary
application code.

Work happens on `experiment/boundscript-next`. The original DSL implementation,
including its historical pilot, remains on `feature/agent-driven-architecture`.

## The working skeleton

The TypeScript Greeting reference and its fixed two-Box contact experiment
demonstrate four responsibilities without four packages:

- **Define:** human-owned task, native public contract, authorized dependency
  interface, and capabilities expressed by the task and concrete sandbox policy.
- **Implement:** Pi and its tools run in a disposable Docker workspace. Only
  authorized Box inputs, runtime tooling, credentials explicitly accepted for this
  prototype, and the writable implementation are exposed—not the repository.
- **Verify:** a separate credential-free, offline environment runs type, behavior,
  dependency-call and negative-access checks. The agent cannot modify the tests.
- **Promote:** only a passing source file is copied back as the accepted artifact.
  The two-Box example composes accepted artifacts in ordinary TypeScript
  `application.ts`, not a BoundScript orchestrator.

## Run

Requires Linux, Docker, Python 3, Node 24.16+, and the digest-pinned Node image
listed in `experiments/minimal-box/verify.py` already cached locally.

```bash
npm ci
npm test              # Saved Greeting + both contact Boxes + integration; no model calls
npm run generate      # Original Greeting: real Pi generation, verification, promotion
npm run generate:pair # Two fresh Pi agents, independent checks, then integration
```

Generation additionally requires the existing Pi 1.4.0 installation and
`~/.pi/agent/auth.json` at the paths in `generate.py`; it makes billable provider
calls. See the [experiment](experiments/minimal-box/README.md) for the
exact environment, commands and observed results.

**Prototype limitations:** generation has unrestricted bridge networking and
agent-readable credentials, explicitly authorized for this experiment. Docker
shares the host kernel. Tests establish observations, not general correctness or
security attestation. Dependency imports are not comprehensively enforced. The
verifier is outside the agent's environment; hostile candidate output is not
inherently trustworthy.

## Removed, retained, deferred

- **Removed:** Langium, the DSL/compiler/interpreter/director, executable artifact
  transforms, old demos/tests, ContactOnboarding tooling, monorepo build setup, and
  superseded DSL documentation/assignments/roadmaps (available in Git history).
- **Retained/extended:** the Docker/Pi reference, native TypeScript contracts,
  explicit dependency injection, independent checks, per-Box promotion and a fixed
  two-Box application. See the [0018 run report](experiments/minimal-box/two-boxes/REPORT.md).
- **Deferred:** artifact registry, transitive dependency
  enforcement, credential brokerage, egress hardening, other languages, generic
  runners/plugins, and production security. No new runtime or DSL replaces the old
  one.

Scope: [foundation](assignments/0017-boundscript-next-foundation.md) and
[two independent Boxes](assignments/0018-two-independent-boxes.md).
Assignments 0019 and 0020 are not implemented.
