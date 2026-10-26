# Assignment 0022 — Run Bounded Independent Implementation Pilot

**Status:** Proposed
**Milestone:** [M3 — Independent implementation pilot](../roadmap.md#m3--independent-implementation-pilot), **Planned**.
**Design:** [Assignment 0020 — bounded feasibility amendment](0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment), directed by the Product Owner.
**Authority:** **Execution-ready proposal; NOT authorized to launch.** The Product Owner accepted 0023 technical preparation and conditionally authorized the asset freeze after the final consistency review. That review found no discrepancies: see the [freeze record](../development/0023-contact-onboarding-freeze.md). Assets are frozen at `aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`. The Product Owner must still approve this execution plan and spending policy below. Preparing this proposal launches no agents, containers or provider calls; M3 stays Planned.

## Objective

Run one bounded ContactOnboarding trial: independent Pi sessions implement `NormalizeContact` and `RenderWelcome` from their respective M2 handoffs; a human controller compiles/verifies them using M1 and integrates the frozen pair without negotiating interfaces, changing architecture, or repairing implementations.

Keep 0020's exact source/contracts, N-01–N-05/R-01–R-05 requirements, examples, corpus coverage, frozen integration/failure protocol, attempt budgets, metrics, and preregistered conventional TypeScript baseline. Reuse the actual accepted frozen revision from 0023 without changing tests, wiring or authority. The baseline is prepared/frozen before the pilot, not executed here. This proposal covers one trial/report only after explicit execution approval; no M6 comparison or automatic M3 closure.

## 1. Frozen inputs and pre-call readiness

**Proposed run ID:** `M3-ContactOnboarding-01`. A is NormalizeContact; B is RenderWelcome. Use a dedicated trusted checkout of **`aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`**, including its core/M1/M2 source and the entire `experiments/contact-onboarding/` tree. Do not execute mutable HEAD or rewrite any frozen asset, even historical delivery-status text. The later freeze/approval records are controller documentation outside the delivered contexts. Agent choice/CLI details are an external operator profile, never language/compiler/runtime/handoff-format integration.

- Reuse the exact source/task/scope/policy/bindings, `generation.md`, literal expected corpus and array order, tests/configuration/wiring, event template, controls and preregistered conventional baseline at that revision. Technical preparation is accepted and final requirement-to-value review found no discrepancy. No asset authoring, expectation changes, new image/configuration or baseline redesign is part of execution.
- Use existing M2 extraction/derivation with an explicit root and fresh output, twice; compare exact relative files/bytes. Copy only each selected real eight-file package into its own separate temporary workspace as `handoff/`. Keep the output symlink/backing data together until copying is complete; do not distribute the whole derivation parent.
- Keep architecture originals, trusted tests, wiring, tool configuration, baseline, reference solutions, logs, and the other Box's code outside both agent workspaces. Ordinary directories/worktrees organize work; they are **not security sandboxes**. The controller retains approved copies and compares handoff snapshots after use.
- Use the existing frozen `prepare.mjs`, `evaluate.sh`, `check-controls.sh` and `check-regressions.sh` commands in the asset README, unchanged. After execution approval, restage into a fresh external directory and rerun ordinary trusted readiness checks before model calls. Model calls in readiness: **zero**. Evaluator: pinned official Node image/container Node v24.22.1, TypeScript 5.9.3; host preparation Node v24.16.0, Docker 29.1.3 as validated. Record actual versions; if they differ, stop for profile review, not new qualification research or a silent switch. No service, SDK/extension, adapter, credential proxy, framework or new security infrastructure.
- Before any agent run, exercise the commands with trusted positive/negative fixtures and check the actual container settings: network disabled, no credentials/host home/socket, intended read-only inputs, private scratch, and whole-container deadline cleanup. This is ordinary test-environment readiness, not Assignment 0021 or a separate sandbox/provider qualification project. If containers cannot run with these settings, stop; never substitute host execution of candidate code.

### 1.1 Exact model/time budget and remaining approval

Retain the preregistered 0020/0023 limits; the ceiling is **not a target or permission for extra tries**:

| Budget | Per Box | Entire trial |
| --- | --- | --- |
| Initial generation episodes | 1 | 2, A then B |
| Own-context revision episodes | At most 1 | At most 2, A then B if needed; no new agent |
| Model-response turns/logical model calls | At most 40 per episode | At most **160** across at most 4 episodes (80 initial + 80 revision) |
| Elapsed generation time | At most 30 minutes per episode | At most **120 minutes** active generation; waiting/preparation/check overhead separately reported |
| Normal complete-response path | One initial response; at most one revision response if needed | Expected **2–4** completed responses, not 160 independent submissions |
| Readiness/smoke/model-probe calls, extra agents, replacement runs, M6 calls | 0 | **0** |

Stop each episode at submission, clarification/proposal, interruption, time limit or turn limit, whichever comes first. Count automatic model-recovery turns against the same allowance; retain failed/interrupted attempts. Streaming chunks are not separate turns. Native provider transport retries are separately recorded, with missing visibility `unknown`: **160 is a logical-turn ceiling, not a claimed hard cap on physical HTTP attempts, tokens or dollars**. No controller-initiated transport retry, budget reset or availability probe; reported infrastructure/model failure stops the trial. This budget covers the two implementation sessions only; no separate model-judge/reporter agent phase is authorized. Any controller assistance in the existing coding conversation is separately reported workflow overhead (usage/cost `unknown` if unobservable), not zero or part of the 160 implementation-turn allowance.

**Product Owner decisions required before launch:**

1. Explicitly authorize this one run, model/settings, order, existing 40-turn/30-minute episode limits and 160-turn/120-minute aggregate ceilings. No launch follows from the asset freeze alone.
2. Specify a monetary spending ceiling and how it is enforced/observed, **or explicitly approve the response/time budget without an observable monetary ceiling** if native billing does not expose charges. No numerical dollar limit or token allowance has been approved; none defaults to unlimited. An observed-spend stop cannot guarantee against an in-flight request overshoot. A hard financial/request cap requires an already available account/provider control, not a proxy or new framework; if that is required but unavailable, do not launch.

Empty effective tools, matching versions, original-copy comparisons, fresh handoffs and offline-container readiness are operational pre-call checks after approval, not additional infrastructure decisions/research. A mismatch stops execution and returns for review. Baseline comparison, new-trial reruns, model/provider/profile changes and milestone closure require separate later authorization.

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

Follow 0020 Section 7 unchanged in experimental substance. Exact normal order: **A initial → B initial → both snapshots retained → A checks → B checks → permitted A revision/checks → permitted B revision/checks → exact passing-pair freeze → one integration selection → report**. Skip a revision when not needed. Clarification of existing text consumes that Box's episode/revision allowance; do not answer/perform revisions before both initial snapshots are retained. A missing/conflicting requirement, architecture request, infrastructure failure or context violation follows the original immediate-stop rule; report later stages unrun. If a Box has no passing selected snapshot after its allowance, report Box failure/integration unrun, not an extra attempt.

Use `evaluate.sh` from the frozen checkout for each inert snapshot: `normalize` and `render` independently, an explicitly selected `private:<emitted-relative.js>` route when private checks exist (a separate fresh container, never a replacement for acceptance), and `integration` only for the stopped/frozen pair. Preserve the **39 normalizer / 24 renderer rows**, repeated-call/input-preservation checks, **18 integration rows** plus live-identity probe, and exact source/config/corpus versions. No tests or expectations change after results.

Protocol:

1. Freeze all approved inputs/tests/wiring/prompts/baseline rules and record versions. Check the tool-free generation/container-only execution setup with trusted fixtures. No extra model smoke call or tooling qualification is required before the two approved sessions.
2. Collect **both initial submissions before feedback**. Per Box allow one initial episode plus at most one independent revision, each at most 30 elapsed minutes/40 model-response turns. Preserve failures, clarification/proposal episodes, provider retries, usage and missing metadata. No silent model changes, budget reset, extra agents, or cherry-picked reruns.
3. Send only approved existing-text clarification, own-source compiler diagnostics, or requirement ID plus failure class. No algorithms, peer context, or manual code/interface repair. Missing/conflicting intent or architectural changes stop the original trial and return to the Product Owner. Infrastructure failures are separate results; do not bypass container/tool restrictions to recover.
4. After independent checks and allowed revisions, freeze the exact pair. Prewritten wiring invokes normalizer through M1, passes its **unchanged live output** to renderer through M1, and asserts the full intermediate/final values against the frozen corpus. All compilation, invocation, and assertions run inside the restricted integration container.
5. If frozen-pair integration fails, record it: no candidate, contract, test, or wiring repair in this trial. Report first-pass success separately from success after permitted independent revision. A negative/inconclusive experiment is a valid delivery but does not satisfy M3's successful exit gate.

## 5. Evidence and delivery

Record 0020's human interventions/minutes, clarification requests, proposed/attempted/actual interface changes, context/tool violations, independent/integration failures, retries/revisions, supplied context, tokens/cost where observable, and workflow overhead. Tool calls are expected to be zero; container/private checks and mechanical source transcription are separate controller work. Do not count them as agent tool use or conceal their cost.

Use the accepted 0023 executable assets unchanged through the [experiment-specific runner](../../experiments/contact-onboarding/README.md) and deliver a redacted execution report with actual frozen input/test/tool versions, per-attempt local snapshot references, full independent/frozen integration results, negative outcomes, deviations, and unverified properties. Keep raw sessions, secrets, handoff/build directories and temporary candidate outputs out of Git; no promotion, hash/evidence database, M4 enforcement, or M6 comparison execution. Before agents, use the frozen `check-regressions.sh`: it runs the existing check components (typecheck plus all 416 tests with one worker), build, three Box demos, Hello World CLI and canonical export comparison inside an offline container with only the curated trusted regression closure. All executable trusted fixture checks stay in containers; no pilot candidate enters that closure or runs on the host. Readiness results reported by the Product Owner are accepted technical evidence; the restaging recheck records the actual trial environment without changing assets.

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

The final expected-value review found no discrepancies and the current assets are frozen as recorded above. This **Proposed execution plan remains unapproved** until the Product Owner resolves Section 1.1 and explicitly authorizes launch. This request performs documentation/read-only consistency checks only: no asset edits, containers, Pi sessions, provider/auth probes, credentials inspection, implementation agents, pilot or baseline execution. M3 remains Planned.
