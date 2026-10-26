# Assignment 0020 — Extract a Minimal Reusable Runner

**Conditional assignment. Do not start until 0018 and 0019 have been reviewed and approved.**

## Goal

Remove duplication proven by the working one- and two-Box experiments so a new TypeScript Box can be defined and evaluated without copying experiment-specific Python scripts.

## Scope

Extract only reusable responsibilities that are already exercised:

- Read a human-owned Box definition, public contract, authorized dependencies, and execution permissions.
- Prepare a bounded agent workspace and run generation.
- Verify a candidate independently.
- Promote only verified artifacts.
- Supply accepted dependency artifacts to an ordinary TypeScript integration step.

Choose the smallest practical interface and repository layout. A CLI or library is acceptable if justified by actual use; neither is mandatory. Preserve the existing experiments as regression tests.

## Non-goals

No new DSL, Director, application orchestrator, custom runtime, artifact registry/service, generic plugin architecture, broad multi-language abstractions, or production-grade credential broker.

## Acceptance

Both existing experiments continue to pass using the extracted functionality, and a small additional Box can be configured without duplicating the entire runner. Include negative regression checks, reproducible commands, and a short explanation of which abstractions were necessary and which were deliberately omitted.

If the experiments do not yet justify extraction, stop and report that conclusion rather than inventing a framework. Do not modify the original branch.
