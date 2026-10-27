# Proposal — Integrate autonomous Box implementation with BoundScript

**Status:** Proposed — pending architectural review and approval.  
**Origin:** Assignment `0018c-Architectural-Integration-Review.md`.  
**Scope:** Integration direction and proposed follow-up work, not implementation or execution authorization.

## Decision requested

Continue development from `feature/agent-driven-architecture`, preserving its DSL, compiler, executable artifact and runtime. Adapt selected Docker/Podman experiment mechanisms around its existing deterministic handoff and independent verification workflow.

Do not merge the experimental branch wholesale, restore removed files indiscriminately, or replace the existing architecture with the experiment's native TypeScript-only workflow. The experimental DSL removal was intentional and remains valid for that track.

The intended workflow is:

```text
Human-approved BoundScript specification + external natural-language task
    → deterministic per-Box handoff
    → independent autonomous implementation
    → isolated compilation and independent verification
    → unchanged integration checks
    → human review and acceptance
```

The DSL describes supported formal architectural contracts. Natural language describes functional intent and mandatory business requirements. The DSL must not become a prompt language.

## Review basis

The architectural review inspected these locally available revisions:

- `origin/feature/agent-driven-architecture` at `31dc3bf`.
- `experiment/boundscript-next` at `1364c49`.
- Architecture Proposals 0012/0013, the roadmap and architecture-branch assignments 0018–0023.
- Existing extraction, canonical codec, handoff derivation, standalone verifier, ContactOnboarding assets, autonomous pilot runner and experimental container adapters.

This is a source/document/history review. Historical test and generation results are recorded evidence, not newly reproduced checks. Remote freshness was not established.

The architecture branch's assignments under `docs/assignments/` are distinct from the experimental branch's similarly numbered assignments under `assignments/`.

## Existing capabilities to preserve

The architecture branch already implements most of the formal integration:

- Parsing, semantic validation and deterministic compilation.
- Portable Box contract extraction and strict canonical JSON encoding/decoding.
- Standalone `verifyBoxImplementation`, sharing runtime contract semantics.
- Explicit architecture/task/scope/policy associations through `tooling/handoff.ts`.
- Eight-file bounded handoffs, generated TypeScript declarations and a fixed implementation entrypoint through `tooling/handoff-render.ts`.
- ContactOnboarding tasks, literal acceptance cases, strict compilation configuration and prewritten integration wiring.
- A fixed autonomous pilot runner at `tooling/run-contact-pilot.mjs` with mocked protocol tests.

These components do not need a replacement specification model, task engine or generic agent controller.

M1/M2 are recorded as completed on the reviewed architecture branch. Its M3 pilot remains planned, with execution and spending approval outstanding. Experimental success does not retroactively complete that separately defined pilot.

## Proposed ownership boundaries

| Responsibility | Authority or component |
| --- | --- |
| Supported public types and predicates | Human-approved `.bound` source and existing extracted canonical contract. |
| Functional intent, requirements and examples | Human-owned task Markdown and independent acceptance expectations. |
| Bounded implementation context | Existing deterministic handoff derivation. |
| Autonomous session protocol | Existing external pilot runner. |
| Container mechanism and effective restrictions | Small external Docker/Podman adapter adapted from the experiment. |
| Compilation and contract checking | Existing strict compiler configuration, codec and M1 verifier inside evaluation containers. |
| Integration | Prewritten wiring and frozen expected-value assertions. |
| Final acceptance | Explicit human decision tied to the exact evaluated candidate pair and inputs. |

Agent/provider settings, credentials, prompts and execution state remain outside the DSL, portable Box contract and executable artifact. Do not introduce new workspace packages or a generic orchestration framework.

## Contract and task linkage

Retain the existing path-only handoff binding format:

- Select the architecture and exact system/Box explicitly.
- Associate human-owned task, scope and policy files.
- Derive the public contract afresh from the architecture.
- Generate declarations as projections, never manually maintained interface authorities.
- Preserve task text and behavioral examples without interpreting them as formal language semantics.

Successful derivation validates structure and reproducibility, not human approval or semantic consistency. Missing intent or conflicts return to the human owner; tooling must not invent requirements or repair the architecture.

Dependencies and capabilities not currently expressible in the DSL remain identified external policy/wiring decisions. Do not describe them as formally enforced declarations.

## Experimental mechanisms to adapt

Reuse the experiment's concrete execution mechanisms where appropriate:

- Explicit Docker/Podman selection without silent fallback.
- Podman-only `--userns=keep-id`.
- Exact bind source/destination and access-mode checks.
- Nonroot execution, read-only root and nonprivileged configuration.
- Effective capability and no-new-privileges checks.
- Effective memory, swap, CPU and PID limit checks.
- Runtime-specific tmpfs handling, sanitized failures and credential-free regression controls.

Adapt these to the fixed ContactOnboarding evaluator's resources, scratch paths and environment. Preserve its whole-container deadlines and cleanup; the experimental Python adapter is not a drop-in replacement for its lifecycle handling.

Keep existing verification semantics and independent behavioral expectations. Do not replace live-value M1 checks with serialized observations or duplicate the contract evaluator.

## Generation and acceptance policy

For the first integration, retain the architecture pilot's approved tool-free autonomous generation profile. This is autonomous execution, not pair programming. Organizational workspaces are not OS sandboxes.

Tool-enabled containerized generation is a possible later external profile requiring separate approval. Do not silently adopt the experiment's agent-readable authentication mounts or unrestricted bridge networking as defaults. Those were explicit prototype exceptions, not general security guarantees.

Keep candidates separate from accepted application artifacts:

1. Collect independent candidate snapshots without peer context.
2. Verify each candidate in a credential-free offline container.
3. Freeze the exact selected pair and run unchanged integration wiring.
4. Present results and limitations for human review.
5. Accept or promote only after explicit human authorization.

A verification pass must not automatically replace accepted files. Integration failure must not trigger manual implementation, contract, test or wiring repair.

## Compatibility constraints

The experimental richer-contact implementation is not directly compatible with the architecture pilot:

- It uses nested discriminated unions and error arrays beyond the current flat-record specification.
- Its renderer receives an injected function dependency, unlike the pilot's unary operations.

Reuse the independent-development method, not those implementations or interfaces. Do not silently flatten their semantics or expand the language merely to transplant them. Retain the existing ContactOnboarding scenario initially; richer types require a separate demonstrated requirement and design decision.

The frozen architecture pilot assets at `aee34e3` must not be edited and still described as unchanged. Evaluator/profile changes require a visible successor revision, review and renewed readiness evidence.

Current uncommitted experimental model settings, contract extensions and accepted-file replacements are not approved integration inputs by virtue of being present locally.

## Proposed follow-up assignments

These are suggested scopes only. Assignment IDs, authoring and authorization remain with the Product Owner.

### 1. Approve the integration profile and input revisions

Acceptance criteria:

- Select exact architecture and successor pilot revisions.
- Confirm the initial generation profile and security policy.
- Identify individual experimental files/commits to adapt.
- Review any impact on the preregistered comparison conditions.
- Separate asset approval, execution/budget approval and final acceptance.

### 2. Adapt runtime enforcement for the fixed evaluator

Acceptance criteria:

- Docker remains default; invalid selections fail; `keep-id` is Podman-only.
- Existing exact mounts, readonly/nonroot execution, privilege/capability restrictions and effective resource checks remain mandatory.
- Preserve evaluator scratch requirements, resource settings and whole-container timeout/cleanup.
- Positive and negative unit controls pass.
- Credential-free engine checks pass for every claimed supported engine; unavailable engines remain unverified.
- No agents, authentication mounts or provider calls.

### 3. Connect the existing runner to the reviewed evaluator

Acceptance criteria:

- M2 handoffs, contract semantics and fixed entrypoint remain unchanged.
- Each agent receives only its own handoff; both initial snapshots precede feedback.
- Revisions remain bounded and use only the same Box's history.
- All generated-code compilation and execution remain inside evaluation containers.
- Mocked checks cover setup failure, timeout, revision and integration failure.
- No automatic promotion.

### 4. Execute one separately approved autonomous trial

Acceptance criteria:

- Approve model/settings, episode limits and spending policy before calls.
- Pass readiness checks before generation.
- Retain all attempts, interventions, failures and infrastructure interruptions.
- Report independent checks and unchanged-pair integration without manual repair.
- Distinguish first-pass success, revised success, failure and inconclusive outcomes.
- Do not infer milestone closure or human acceptance from a pass flag.

### 5. Record reviewed acceptance

Acceptance criteria:

- Identify exact architecture/task/test/wiring and candidate snapshots.
- Record checks, important unverified properties and explicit human acceptance.
- Require affected reverification and renewed acceptance after relevant changes.
- Prevent partial pair replacement or acceptance based on stale observations.
- Use a small reviewed record, not a registry, evidence database or generalized promotion service.

## Risks and unresolved decisions

Review must resolve:

- Whether tool-free generation remains the initial profile, as recommended.
- Which host/runtime versions are supported by actual evidence.
- Where accepted candidate pairs and their human acceptance records will live.
- Whether historical experimental results are merely exploratory or comparable to a future matched baseline.

Preserve the following limitations in all reports:

- Finite tests do not prove arbitrary correctness, purity or universal dependency compliance.
- Candidates and tests share an evaluation environment; readonly test mounts do not make tests secret or results authenticated.
- Containers share the host kernel.
- TypeScript projections do not establish every runtime contract property.
- Python assertions require non-optimized execution.
- Hard kills and infrastructure interruptions require explicit cleanup accounting.
- Deployed ordinary Node applications do not inherit development-container restrictions.

## Deferred work

Pair programming, generic orchestration, distributed scheduling, provider abstraction, credential proxies, production per-Box isolation, automated architectural approval, registries and authenticated evidence infrastructure remain deferred.

Richer types, dependency/capability syntax and other language extensions require separate concrete requirements and review. They are not prerequisites for this integration.

## Proposed conclusion

The architecture branch already defines the appropriate formal-contract and natural-language-task pipeline. The experiment supplies useful autonomous implementation evidence, effective container checks and Podman compatibility—not a reason to replace that pipeline or import its prototype trust exceptions.

Approve a small external evaluator adaptation first, then a separately authorized autonomous trial and explicit human acceptance of its exact outputs.

**This proposal authorizes no implementation, asset changes, agent launches, provider calls, commits or milestone status changes. Await human architectural review.**
