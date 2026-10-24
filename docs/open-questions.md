# Product-level open questions

These decisions materially affect what BoundScript is and should be resolved through examples and prototypes rather than folder-level debate.

1. **Primary user:** Is the language first for software architects, application developers, or end users modifying an existing product through an agent?
2. **Delegation authority:** Which architectural changes may an agent director make without explicit human approval (new boxes, contracts, directors, or dependencies)?
3. **Contract strength:** Which guarantees must be mechanically checkable, and where are examples, tests, natural-language requirements, or human approval acceptable?
4. **Director semantics:** Which control-flow features belong in the first language version: conditions, bounded iteration, retries, parallelism, timeouts, and compensation?
5. **State ownership:** How are private box state, director workflow state, migrations, and shared data represented and governed?
6. **Isolation target:** Is the first sandbox intended as a development boundary, a production security boundary, or both?
7. **Implementation portability:** Must boxes support multiple implementation languages initially, or is a TypeScript-only first prototype acceptable?
8. **End-user modification lifecycle:** Who reviews, approves, deploys, rolls back, and audits agent-generated changes?
9. **Success criteria:** What experiment demonstrates value—lower agent context use, fewer regressions, safer customization, or faster human repair?
10. **Project terminology:** `box`, `director`, and `contract` are useful working terms but are not yet a finalized product vocabulary.
