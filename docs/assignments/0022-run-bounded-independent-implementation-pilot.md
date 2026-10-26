# Assignment 0022 — Run Bounded Independent Implementation Pilot

**Status:** Proposed
**Milestone:** [M3 — Independent implementation pilot](../roadmap.md#m3--independent-implementation-pilot), **Planned**.
**Design:** [Assignment 0020 — bounded feasibility amendment](0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment), directed by the Product Owner.
**Authority:** **Deferred execution proposal, not the next implementation step.** The Product Owner requested [Proposed 0023 — asset preparation/freeze only](0023-prepare-and-freeze-independent-pilot-assets.md) first. No work/agents are authorized here. After actual assets are reviewed/frozen, revised pilot execution must be explicitly approved; asset preparation or acceptance cannot activate this proposal. M3 stays Planned until that execution approval.

## Objective

Run one bounded ContactOnboarding trial: independent Pi sessions implement `NormalizeContact` and `RenderWelcome` from their respective M2 handoffs; a human controller compiles/verifies them using M1 and integrates the frozen pair without negotiating interfaces, changing architecture, or repairing implementations.

Keep 0020's exact source/contracts, N-01–N-05/R-01–R-05 requirements, examples, corpus coverage, frozen integration/failure protocol, attempt budgets, metrics, and preregistered conventional TypeScript baseline. Reuse the actual accepted frozen revision from 0023 without changing tests, wiring or authority. The baseline is prepared/frozen before the pilot, not executed here. This deferred proposal covers eventual trial/reporting only after revised execution approval; no M6 comparison or automatic M3 closure.

## 1. Asset prerequisites — preparation is now assigned to Proposed 0023

The following prerequisites are retained for execution review; they do not authorize duplicate asset preparation or a combined preparation/launch phase under this deferred proposal. Use 0023's assets-only scope first. Agent choice/CLI details below are an external operator profile, never language/compiler/runtime/handoff-format integration.

- Prepare the human-owned architecture, per-Box task/scope/policy/bindings, fixed prompts, complete expected-output corpus, and predefined wiring from 0020. Obtain approval of their actual versions and consistency before operational derivation/model calls. Tasks describe behavior without restating public interfaces. Freeze tests and baseline assets/evaluation rules before either agent; do not invent hidden requirements or change expectations after observing results.
- Use existing M2 extraction/derivation with an explicit root and fresh output, twice; compare exact relative files/bytes. Copy only each selected real eight-file package into its own separate temporary workspace as `handoff/`. Keep the output symlink/backing data together until copying is complete; do not distribute the whole derivation parent.
- Keep architecture originals, trusted tests, wiring, tool configuration, baseline, reference solutions, logs, and the other Box's code outside both agent workspaces. Ordinary directories/worktrees organize work; they are **not security sandboxes**. The controller retains approved copies and compares handoff snapshots after use.
- Prepare ordinary strict ESM/NodeNext compile and test commands in an existing disposable container environment. Reuse repository TypeScript, M1/codec built exports, Node assertions or Vitest, and M2 consumer patterns. A small fixed test module, image/config if needed, and manual runbook suffice; no service, custom agent framework, SDK orchestration, tool extension, credential proxy, or security platform.
- Before any agent run, exercise the commands with trusted positive/negative fixtures and check the actual container settings: network disabled, no credentials/host home/socket, intended read-only inputs, private scratch, and whole-container deadline cleanup. This is ordinary test-environment readiness, not Assignment 0021 or a separate sandbox/provider qualification project. If containers cannot run with these settings, stop; never substitute host execution of candidate code.

## 2. Tool-free independent generation

Use existing Pi with the current `openai-codex/gpt-6.1-sol`, medium reasoning, and native host authentication. Record actual nonsecret provider/model/tool versions; no provider/model switch without explicit approval. Do not inspect/export credentials or copy them into a workspace/container. No Docker Sandboxes, Gondolin, OAuth-proxy compatibility test, or Assignment 0021 result is required.

For each Box, sequentially, start a **fresh independent Pi session** from its temporary workspace. Use separate controller-owned session/log locations outside the two delivered workspaces, no continuation/fork of the design session or peer session. Resume only the same Box's history for its one allowed revision.

- Disable **all model-callable tools** with `--no-tools`, and disable extensions, MCP, skills, prompt templates, themes, context-file discovery, and project resource approval using existing Pi flags. Use a fixed explicit system prompt rather than inherited task/system instructions. Do not load explicit extensions or enable tools, shell, `!` commands, web access, or file-reading/writing tools mid-run. No custom permission extension is needed.
- The controller explicitly attaches/embeds **only that Box's eight handoff files**, with a common frozen instruction to emit complete named `.ts` source files as text, or request clarification/propose a change. Pi's documented `@file` input can load these controller-selected files; this is not permission for model-selected host reads. Initial context must contain no full architecture, peer package/code/history, hidden tests, or additional repository material. Later feedback is restricted by 0020's existing protocol.
- Before submitting a generation prompt, verify/record the effective declared tool set is empty. If configuration unexpectedly enables a tool, stop and report the configuration violation; do not rely on a prompt telling the agent not to use it. The ordinary Pi client and its native credential handling remain trusted host software, **not a sandboxed process**.
- Agents cannot execute private checks while generating. They may emit permitted private helper/test `.ts` modules under `candidate/**`; all checks are performed by the controller in containers. This reduced authoring affordance must be reported and applied equally in a future baseline comparison.
- Mechanically save the emitted source under `candidate/implementation.ts` and any permitted private `.ts` paths. Preserve the named `implement` export/type-only import convention. Copy code as inert text with no host editor hooks, formatters, previews, test runners, or execution; do not fix syntax, rename fields, supply missing logic, or run suggested commands. Ambiguous/incomplete output follows clarification/failure rules, not manual repair. Record this transcription time as planned controller overhead, distinct from algorithm/interface interventions.

The two temporary workspaces provide organizational context separation only. Tool disabling limits the model's actions through Pi but is not an OS security guarantee, authenticated policy engine, or defense against a compromised harness/operator mistake.

## 3. Candidate compilation and tests — containers only

Never import, transpile, compile, run, or test agent-generated source on the host, including private tests or code appearing to be harmless. Do not add live candidate imports to root repository tests. Host work is limited to trusted preparation, inert text copying/review, standard container commands, and report inspection.

For each submitted snapshot, use disposable **non-privileged, credential-free, network-disabled containers** for compilation and all candidate tests:

- Explicit `--network=none`; no inherited credential variables, environment files, Pi auth/session directories, SSH agent, host home/repository, container socket, host namespaces, or device mounts. No privileged mode, host networking, or extra capabilities. Use a nonroot user, dropped capabilities/no-new-privileges, read-only runtime/input mounts, and private temporary build/output scratch through existing runtime options.
- Mount only that snapshot, its handoff, trusted compile/test configuration, relevant frozen tests, and the prepared compiler/M1/codec dependency closure. Independent checks do not mount peer code. Only the final frozen integration container may mount both implementations. Trusted test originals/wiring stay outside the agent workspaces and are mounted read-only for evaluation; this prevents file modification, **not reading by executing candidate code**.
- Use the approved TypeScript/ESM/NodeNext settings from 0020/M2, with a trusted named-export consumer assigning `implement` to the generated `Implementation` type. Confirm type-only declaration imports disappear; do not create runtime `contract.js`. No candidate-chosen flags, dependency installation, lifecycle scripts, or general loader framework. Dependencies/images are prepared from trusted inputs before candidate execution; compilation/tests themselves run offline.
- Strictly decode the packaged JSON through `@boundscript/compiler/box-spec`, then invoke existing `verifyBoxImplementation` inside the container on fixed live inputs/outputs. Keep compiler-root/frontend/Langium/director execution out of the consumption path. Reuse semantics; do not write another evaluator.
- Run frozen expected-value assertions, private checks, and both independent suites inside these containers. Preserve input-mutation/repeated-call cases and distinct setup/compile/load/M1/behavior/process/resource failures. Use a fresh environment per suite/rerun with fixed case order; log incomplete cases when stopped.
- Retain the 60 s build/suite deadline and evaluator limits of 1 CPU, 512 MiB, 64 PIDs using existing runtime controls. Timeout cleanup must stop/remove the entire container and descendants, not merely detach the CLI. Source snapshots remain immutable; reject links, special files, unexpected paths/manifests/config and submissions over the existing 10 MiB cap. That cap is not a hard host disk quota.

Tests and candidate share an evaluation environment/JavaScript realm. A deliberately malicious implementation may read tests, tamper with globals, or spoof results. Read-only mounts and outside originals protect test files/host authority, not secret or authenticated evaluation. Report observations and residual risks honestly; adversarial attestation is not an M3 deliverable. Do not feed raw logs, hidden test source/expected values, or peer output back to agents.

## 4. Frozen protocol and integration

Follow 0020 Section 7 unchanged in experimental substance:

1. Freeze all approved inputs/tests/wiring/prompts/baseline rules and record versions. Check the tool-free generation/container-only execution setup with trusted fixtures. No extra model smoke call or tooling qualification is required before the two approved sessions.
2. Collect **both initial submissions before feedback**. Per Box allow one initial episode plus at most one independent revision, each at most 30 elapsed minutes/40 model-response turns. Preserve failures, clarification/proposal episodes, provider retries, usage and missing metadata. No silent model changes, budget reset, extra agents, or cherry-picked reruns.
3. Send only approved existing-text clarification, own-source compiler diagnostics, or requirement ID plus failure class. No algorithms, peer context, or manual code/interface repair. Missing/conflicting intent or architectural changes stop the original trial and return to the Product Owner. Infrastructure failures are separate results; do not bypass container/tool restrictions to recover.
4. After independent checks and allowed revisions, freeze the exact pair. Prewritten wiring invokes normalizer through M1, passes its **unchanged live output** to renderer through M1, and asserts the full intermediate/final values against the frozen corpus. All compilation, invocation, and assertions run inside the restricted integration container.
5. If frozen-pair integration fails, record it: no candidate, contract, test, or wiring repair in this trial. Report first-pass success separately from success after permitted independent revision. A negative/inconclusive experiment is a valid delivery but does not satisfy M3's successful exit gate.

## 5. Evidence and delivery

Record 0020's human interventions/minutes, clarification requests, proposed/attempted/actual interface changes, context/tool violations, independent/integration failures, retries/revisions, supplied context, tokens/cost where observable, and workflow overhead. Tool calls are expected to be zero; container/private checks and mechanical source transcription are separate controller work. Do not count them as agent tool use or conceal their cost.

Use the accepted 0023 assets/runbook unchanged and deliver a redacted execution report with actual frozen input/test/tool versions, per-attempt local snapshot references, full independent/frozen integration results, negative outcomes, deviations, and unverified properties. Keep raw sessions, secrets, handoff/build directories and temporary candidate outputs out of Git; no promotion, hash/evidence database, M4 enforcement, or M6 comparison execution. Before agents, run `npm run check`, `npm run build`, the director-box/composition/structured-types demos, Hello World CLI, and canonical `bound spec` reference comparison. These repository regressions use trusted fixtures only; never import pilot candidates on the host.

## Acceptance criteria after explicit implementation/execution approval

| ID | Required evidence |
| --- | --- |
| AC-01 | Actual approved 0020 source/tasks/policy/tests/wiring/baseline are frozen before agents; fresh M2 derivations match file sets/bytes and only the respective handoff enters each temporary workspace/context. |
| AC-02 | Two fresh independent Pi histories preserve the approved provider/model, have zero effective model-callable tools and no inherited peer/repository context; no unrestricted tool or shell execution during generation. Any violation is reported and stops the affected run. |
| AC-03 | Candidate saving is mechanical, recorded, and contains no controller code/interface repair. No generated code is compiled/executed/tested on the host. |
| AC-04 | All candidate compile/private/independent/integration checks run in disposable credential-free, network-disabled containers with restricted read-only mounts/private scratch, bounded resources and full-container cleanup; trusted readiness controls pass or execution stops. No 0021/provider-proxy prerequisite or custom infrastructure. |
| AC-05 | Strict NodeNext/named-export/ESM checks and M1 strict decode/verification reuse current semantics. Complete behavioral expectations and malformed-output controls are asserted by frozen tests in containers. |
| AC-06 | The independent-check/revision/freeze protocol and unchanged wiring are followed; all trial outcomes are retained. Successful M3 exit evidence requires both independent suites and every frozen integration row to pass with zero interface negotiation, architecture changes or integration-time repair. Failure delivery is not falsely labelled success. |
| AC-07 | All existing outcome metrics, feedback/attempt limits, controller transcription overhead and residual risks are reported; baseline is preserved/prepared but not executed. Directories are explicitly not security sandboxes; test secrecy/anti-cheating and production isolation are not claimed. |
| AC-08 | Delivery remains pending Product Owner acceptance. M3 cannot be marked Completed automatically; current document preparation leaves it Planned and launches no agents/containers. |

## Current documentation-only boundary

This remains a Proposed, deferred execution document. The current next assignment is 0023 for actual asset creation/freeze after its own approval. Do not implement assets, build/pull images, start containers/Pi sessions, inspect credentials or call a provider under this proposal. After asset review, obtain explicit approval of revised execution before either agent; no automatic launch or M3 status change follows from asset acceptance.
