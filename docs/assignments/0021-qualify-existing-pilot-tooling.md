# Assignment 0021 — Qualify Existing Pilot Tooling

**Status:** Proposed
**Milestone:** Pre-execution prerequisite for [M3 — Independent implementation pilot](../roadmap.md#m3--independent-implementation-pilot); M3 remains **Planned**.
**Design:** [Completed Assignment 0020](0020-design-independent-implementation-pilot.md#product-owner-acceptance-and-completion-evidence), accepted revision `7b75de628a91b81ee0160ba34360297ff2b4e15c`.
**Scope:** Minimal existing-tool qualification proposal, not pilot implementation or execution. The Product Owner authorized preparing/publishing this proposal only. Wait for separate review and explicit qualification-execution authorization before installing/configuring tools, starting environments, or making model calls. No experiment assets or pilot agents are authorized.

## Objective and priority

Determine whether existing documented tools can meet 0020's essential isolation, credential-handling, protected-workspace, and reproducibility requirements **while preserving the existing OpenAI/Pi provider and model configuration**, without custom infrastructure.

The existing session metadata identifies provider `openai-codex`, model `gpt-6.1-sol`, reasoning `medium`. The design references Pi 1.4.0, Node v24.16.0, and TypeScript 5.9.3; confirm actual installed versions in the authorized qualification rather than assuming them. Metadata does not prove which credential storage/refresh mechanism is configured. Do not inspect, copy, print, or publish credential values to establish it.

**No provider or model switch is authorized.** In particular, the stock Pi kit's documented Anthropic path is not permission to select Anthropic, change the model, or perform a cross-provider smoke test. If the existing OpenAI/Pi path cannot be qualified, report the blocker and request an explicit Product Owner decision. A negative/inconclusive result is a valid qualification delivery; it does not justify new infrastructure or a weaker boundary.

## Starting gaps, not qualification results

| 0020 blocker | Known from design review | Question this assignment must answer |
| --- | --- | --- |
| B-01 | No `sbx` executable was found in the inspected PATH. Docker/Podman executables were present; their operation/configuration was not qualified. | Which supported host and existing runtime/version, if any, can provide the required boundary without custom code? What approved installation/configuration would be necessary? |
| B-02 | The reviewed stock Docker Sandboxes Pi kit documents Anthropic credential substitution; compatibility with the selected OpenAI Codex/Pi authentication/model path is unverified. | Can an existing documented mechanism preserve the exact OpenAI provider/model and keep real credentials outside model-directed code, including refresh if applicable? |
| B-03 | Read-only shares, restricted egress, resource/cleanup controls, and repeatable kit/image/tool versions were not exercised locally. Kit-tag pinning alone may still select a moving Pi image. | Do existing supported settings satisfy all essential controls on the chosen host, without a new proxy, extension, or controller platform? |

The [accepted isolation design](0020-design-independent-implementation-pilot.md#51-select-an-existing-whole-session-sandbox) prefers whole-session Docker Sandboxes/Pi-kit authoring and ordinary credential-free Docker evaluation. Qualify compatibility with the existing OpenAI configuration **before** spending effort installing a kit whose documented provider path differs. Do not make tool convenience determine the provider/model.

## Bounded qualification plan after separate authorization

### 1. Documentation and feasibility first

- Record redacted host/OS/virtualization availability, executable availability, tool versions, and the selected Pi provider/model/reasoning. Inspect only necessary nonsecret configuration metadata; do not read auth stores into a model transcript or use credential-printing commands.
- Review release-matched upstream Pi/runtime documentation for the **actual OpenAI authentication path**, required endpoints, credential substitution or host-side credential separation, and essential workspace controls. Distinguish documented support, upstream tests, local observations, and unverified assumptions.
- Assess the preferred existing mechanism first. If it lacks the required OpenAI path, document that precise gap. At most one already available, documented alternative may be proposed for Product Owner review, including an existing Pi isolation capability only if all enabled tools and executable actions are covered without code changes. Do not patch example extensions, write an adapter, or survey/build a new platform.
- Deliver a short go/no-go setup plan naming the existing mechanism, exact versions/configuration, expected file/network exposure, any install/update, and any nonzero provider cost. Installation/configuration and runtime/auth probes require explicit approval of that plan; if not already included in the execution authorization, stop here and request it. Any departure from 0020's preferred isolation mechanism needs Product Owner approval, not an implicit design waiver.

### 2. Small local qualification, only within the approved setup plan

Use disposable **generic trusted probes**, not ContactOnboarding source/tasks, a solution candidate, a pilot driver, acceptance corpus, or baseline assets. Use existing CLIs and ordinary manual checks; no persistent controller code or automated agent runner.

| Essential check | Minimal evidence / pass condition |
| --- | --- |
| Real authoring boundary (B-01/B-03) | Pi/tools execute within the selected existing VM/container mechanism. Host sentinel, repository, other workspace, host Pi home, credential paths, host sockets/namespaces, and hidden-test stand-in are not exposed. A directory/worktree, prompt, or ordinary Node subprocess alone never passes. No local-tool fallback or unisolated extension/MCP path. |
| Same OpenAI/Pi configuration (B-02) | Record the exact original provider/model/reasoning and actual nonsecret auth mechanism. Existing supported facilities keep real credentials outside model-directed code; no raw token/key is passed to the guest, its environment, files, or logs, and no guest login is used. A proxy placeholder alone is not proof of successful authentication. |
| Bounded auth check (B-02) | Only if explicitly authorized with a cost cap: use the existing CLI for one minimal tool-disabled, non-coding request to the **same** provider/model. No coding task, implementation agent, alternate model, or provider change. Record redacted success/failure and applicable expiry/refresh support from existing documentation or a bounded authorized probe; unknown lifecycle behavior remains unverified. Never print real credentials or export an auth store. |
| Protected workspace (B-03) | Generic `handoff/` and prepared config are genuinely read-only to model-directed actions, while only the intended candidate subtree is accepted as source. Probe write denial and compare originals after shutdown; confirm another workspace/test stand-in is absent. Guest-local home/tmp writes are not mistaken for authorized deliverables or host write access. |
| Network/access control (B-03) | Effective authoring egress allows only approved provider/auth endpoints; unnecessary registry/web/peer paths are denied. Credential-free evaluation uses existing non-privileged containers with no network, socket, host home/repository, host namespaces, or device passthrough, and read-only input/config mounts. |
| Lifetime/resources (B-03) | Record the accepted design's CPU/memory/PID settings and standard external deadline/stop commands. Use a bounded trusted wait fixture to show timeout cleanup stops all environment processes rather than merely detaching the client. No malicious payloads or host execution of candidate code. The source submission cap is not a hard disk quota. |
| Reproducibility (B-03) | Record exact resolved image/kit/tool versions and effective settings, not only `latest`. Recreate the generic workspace once with the same supported settings and repeat the essential access/protection checks. No shared session/skills/MCP state. |

If a test is unavailable, unsafe, unsupported, or fails, record **Unverified/Blocked/Failed**, not Pass. Stop affected probes; never fall back to host execution, copy a real credential into a sandbox, switch models/providers, or weaken a protected mount. Stronger hardening excluded by 0020 remains out of scope.

### 3. Qualification report and decision

Produce one short Markdown report with:

- Selected existing mechanism/configuration and release-matched documentation references, or why none qualifies for the current OpenAI/Pi setup.
- A B-01/B-02/B-03 table: requirement, documented support, local check/result, remaining gap, and proposed Product Owner decision. Separate a documentation-based recommendation from a locally qualified pass; do not label a partially tested setup ready.
- A minimal manual runbook using existing commands, actual versions/image references, resource/stop settings, permitted mounts/endpoints, and redacted evidence. Keep raw logs, secrets, generated files, and probe outputs outside Git; do not build evidence machinery.
- Explicit outcome: **Qualified for the existing configuration**, **Blocked**, or **Inconclusive**. Any install/update, provider/model change, alternative mechanism, unsupported essential control, or further prerequisite must be called out for approval. No automatic fallback.

Qualification is necessary but not sufficient for M3 readiness. Even a successful report does not authorize creating experiment assets, launching pilot agents, executing the comparison, or marking M3 In Progress/Completed. Product Owner acceptance of qualification and a separate pilot implementation/execution assignment are still required.

## Scope and exclusions

Allowed after separate authorization: release-matched document review, redacted configuration inventory, narrowly approved existing-tool setup, generic trusted access/resource/auth probes, and the short report/runbook. Do not add repository packages, runtime/compiler/grammar changes, custom Pi tools/extensions/transports, a credential proxy, provider integration, sandbox implementation, controller service, orchestration, or M4 evidence/promotion infrastructure. Do not modify ContactOnboarding, its approved requirements/frozen integration protocol, or the preregistered TypeScript baseline to fit a tool.

Current preparation delivers **only this Proposed document and acceptance/status documentation**. It does not authorize installing tools, mutating credentials/configuration, starting environments, or running qualification/model/pilot probes now.

## Acceptance criteria for later authorized qualification

| ID | Required evidence |
| --- | --- |
| Q-01 | B-01 is resolved or precisely blocked with a supported-host/runtime/version finding; documentation review precedes unnecessary installation. Only separately approved setup is performed. |
| Q-02 | B-02 addresses the exact existing OpenAI/Pi provider/model/auth path, real-credential separation and applicable lifecycle support. No model/provider change occurs without explicit Product Owner approval; absent compatibility yields a blocker, not a substitution. |
| Q-03 | B-03 has explicit pass/fail/unverified results for the essential real boundary, protected shares/tests/contexts, egress, resources/cleanup, and reproducible versions/settings. Real isolation is never replaced by directories, instructions, or ordinary Node processes. |
| Q-04 | Findings use existing supported facilities without custom infrastructure. Any unsupported essential requirement leads to a bounded gap report and approval request; optional hardening is not quietly made a platform project. |
| Q-05 | One concise report/runbook records redacted evidence and limitations without secrets, transcripts, generated artifacts, or test/credential leakage. Successful generic qualification is distinguished from pilot execution and stronger security guarantees. |
| Q-06 | No ContactOnboarding assets, implementation candidates, pilot agents, baseline comparison, or M3 implementation/execution occurs; M3 remains Planned pending separate Product Owner authorization. Negative or inconclusive findings are reported honestly. |

## Proposal delivery checks and review boundary

For this documentation-only preparation, validate local Markdown links/anchors, fences, numbering/status, B-01–B-03 coverage, provider/model preservation and authorization language, and `git diff --check`. Do not claim runtime qualification or new pilot regression results. Commit/push the authorized documentation for review, then wait for the Product Owner; this proposal has not been approved for execution.
