# Product-level open questions

These decisions materially affect what BoundScript is and should be resolved through examples and prototypes rather than folder-level debate.

1. **Primary user:** Is the language first for software architects, application developers, or end users modifying an existing product through a build-time agent?
2. **Delegation authority:** Which architectural changes may build-time agents propose or perform without explicit human approval?
3. **Contract strength:** Which guarantees must be mechanically checkable, and where are examples, tests, natural-language requirements, or human approval acceptable?
4. **Director semantics:** Which control-flow features belong in the first language version: conditions, bounded iteration, retries, parallelism, timeouts, and compensation?
5. **State ownership:** How are private box state, director workflow state, migrations, and shared data represented and governed?
6. **Isolation target:** Is the first sandbox intended as a build-time workspace boundary, a production execution boundary, or both?
7. **Implementation portability:** Must boxes support multiple implementation languages initially, or is a TypeScript-only first prototype acceptable?
8. **Build lifecycle:** Who reviews, approves, packages, deploys, rolls back, and audits build-agent-generated implementations?
9. **Runtime agents:** Does the language need first-class model-invoking agents, or should initial programs only call externally supplied capabilities?
10. **Artifact runtime profile evolution:** How should the initial sequential director instruction format grow to support calls, errors, and control flow without becoming a general-purpose bytecode prematurely?
11. **Artifact integrity and provenance:** When are hashes, signatures, dependency manifests, reproducible builds, or separate build records required?
12. **Success criteria:** What experiment demonstrates value—lower build-agent context use, fewer regressions, safer customization, or faster human repair?
13. **Project terminology:** `box`, `director`, `contract`, and `runtime agent` are useful working terms but are not finalized product vocabulary.
