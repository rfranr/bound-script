# Assignment 0020 — Design Independent Implementation Pilot (M3)

**Status:** Completed
**Milestone:** [M3 — Independent implementation pilot](../roadmap.md#m3--independent-implementation-pilot)
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md), especially Sections 2, 6, 7, 10, and 11.
**Scope:** Design only, explicitly accepted by the Product Owner; see the [acceptance record](#product-owner-acceptance-and-completion-evidence). No pilot implementation, agent launch, comparison execution, or milestone-status change is authorized by design acceptance. M3 remains **Planned**. [Assignment 0021](0021-qualify-existing-pilot-tooling.md) proposes the separate B-01–B-03 tooling qualification prerequisite; both qualification execution and later pilot work require separate authorization.

## Review revision and authority

The Product Owner accepted ContactOnboarding, the two-Box decomposition, functional requirements, frozen integration protocol, failure accounting, and conventional TypeScript baseline as a sound design direction, while requesting simpler execution infrastructure. This revision preserves those experimental choices and replaces the custom Pi Bash transport with existing whole-session sandbox tooling. Sections 5–6 distinguish essential controls, optional hardening, and explicit prerequisites/blockers. That revision was delivered as **Proposed**; the Product Owner subsequently accepted it at design level against `7b75de628a91b81ee0160ba34360297ff2b4e15c`. Acceptance does not authorize qualification or pilot execution. Earlier Proposed/review-gate wording below describes design delivery, not the current assignment status.

## 1. Question, experiment, and authority

Test the central hypothesis: **Can two independent coding agents implement separate Boxes from approved contracts and functional tasks, then integrate successfully without negotiating interfaces or modifying the architecture?**

Propose one small, preregistered trial: two fresh Pi sessions implement `NormalizeContact` and `RenderWelcome` independently, sequentially, in separate restricted workspaces. Both use the same approved model/settings and budgets. A human controller collects their candidates, applies independent checks, and integrates the frozen pair using wiring written before either session starts. Neither agent sees the other's implementation, transcript, private tests, or failures. There is no agent-to-agent channel.

This tests feasibility and coordination at a fixed boundary, not whether BoundScript is superior to conventional TypeScript. A successful pair is one observation; failures are first-class results, not a reason to repair interfaces or quietly rerun until success. Section 8 preregisters a minimal conventional baseline for later, separately authorized M6 execution.

The Product Owner owns scenario, business rules, contracts, examples, test expectations, budget, isolation policy, and final acceptance. An Architect proposes changes; implementers cannot approve them. The controller follows a runbook, not an autonomous scheduler. Follow the [development workflow](../development/developer-workflow.md); neither a passing run nor acceptance of this design completes M3.

## 2. Investigated foundations and constraints

| Existing foundation inspected | Reuse and boundary |
| --- | --- |
| [0016 design](0016-design-standalone-box-verifier.md), [Completed 0017](0017-implement-standalone-box-verifier.md), accepted correction `5d15c9b0269146282bc07a1da3edcf522b036609` | M1 checks a fixed invocation of an already-loaded function. It is not a loader, sandbox, or functional oracle. |
| [Strict codec](../../packages/compiler/src/box-spec-json.ts), [verifier](../../packages/runtime/src/box-verifier.ts), [shared checks](../../packages/runtime/src/contract-checks.ts), [consumer tests](../../tests/box-verifier-consumer.test.ts) | Strictly decode via `@boundscript/compiler/box-spec`, then use `verifyBoxImplementation`. Preserve finite-number, exact-own-field/symbol-extra, void, inspection-error, and output-before-predicate semantics. Runtime stays independent of compiler/frontend. |
| [Completed 0018](0018-design-deterministic-task-derivation.md), [Completed 0019](0019-implement-deterministic-task-derivation.md), accepted implementation `b692da02f54a36beabce47f1bc41e4d7a68ac926` | M2 derives eight-file, per-Box packages with protected human text and generated declarations. It does not verify approval or isolate candidates. |
| [Extraction](../../packages/compiler/src/box-development-spec.ts), [adapter](../../tooling/handoff.ts), [renderer](../../tooling/handoff-render.ts), [usage](../task-derivation.md) | Whole-system validation, explicit selections including unused Boxes, resolved inline records, spec version 1/rules version 1. Exclusive output symlink points to complete sibling data: retain both during delivery or copy the selected real package directory. |
| [Independent consumer/wiring tests](../../tests/handoff-consumer.test.ts) | Reuse strict ESM/NodeNext compilation, named-export/import checks, and frontend/compiler-root import guards. Those tests execute trusted fixtures only; do not import new agent candidates into the repository test process. |
| Current grammar/backend | One operation per Box, primitives and flat records, string-inequality `ensure`, mandatory director, no record literal construction or formal dependency/capability declarations. No new syntax is needed. |
| Installed Pi 1.4.0 documentation and examples | Reviewed `README.md`, `docs/cli.md`, `sessions.md`, `configuration.md`, `environment-variables.md`, `security.md`, `containerization.md`, `cli-integration.md`, `extensions.md`, and the `ssh.ts`/`sandbox` tool-operation examples. Separate sessions are supported; cwd, prompts, tool allowlists, and project trust are not OS security boundaries. |

M1/M2 acceptance records report Node v24.16.0, TypeScript 5.9.3, Linux, and 416 passing tests in 17 files after M2 correction. Those are existing foundation results, **not pilot evidence**. Pi's installed `docs/containerization.md` documents whole-session Docker Sandboxes and its Pi kit, including host-side credential substitution. Upstream kit documentation describes end-to-end testing; it is not local qualification of this pilot configuration. No sandbox configuration has been exercised under this assignment. The earlier SSH/sandbox extension examples are no longer proposed pilot infrastructure.

## 3. Proposed scenario and architecture

### 3.1 Contact onboarding with safe welcome rendering

An application receives a contact submission containing inconsistent whitespace/case, an email address, locale preference, consent, and trial duration. It must normalize and classify the submission, then produce either an exact localized welcome message or a deterministic suppression result. No message is actually sent.

This is more meaningful than a greeting echo: the producer handles canonicalization, multiple validation failures and precedence, and numeric limits; the consumer handles consent/invalid-state policy, localization, zero-day behavior, and HTML escaping. Integration must preserve identity and carry a complete shared record across independently implemented boundaries. Type-correct code can still disagree on error priority, canonicalization, suppression, escaping, or exact output. There are enough interacting requirements to expose coordination problems without introducing databases, services, nested types, clocks, or network dependencies.

This selects and elaborates Proposal 0013's suggested `NormalizeContact`/`RenderWelcome` scenario. The Product Owner approved this scenario and decomposition at design level; actual assets still require pre-execution freeze and approval.

### 3.2 Proposed source (document only)

The following would become one human-owned `.bound` input under a later authorized assignment. Names, fields, and operation identities below are the proposed single formal authority, not interfaces for agents to renegotiate.

```boundscript
system ContactOnboarding {
    type ContactSubmission {
        requestId: string
        name: string
        email: string
        locale: string
        consent: boolean
        trialDays: number
    }
    type NormalizedContact {
        requestId: string
        displayName: string
        email: string
        locale: string
        consent: boolean
        trialDays: number
        valid: boolean
        reason: string
    }
    type WelcomeMessage {
        requestId: string
        send: boolean
        recipient: string
        subject: string
        html: string
        reason: string
    }
    box NormalizeContact {
        operation normalize(submission: ContactSubmission): NormalizedContact
        ensure result.reason != ""
    }
    box RenderWelcome {
        operation render(contact: NormalizedContact): WelcomeMessage
        ensure result.subject != ""
    }
    director Main {
        on start {
            print("Pilot uses external fixed-input wiring")
        }
    }
}
```

The director satisfies the existing whole-source requirement; it is not executed in this experiment. Record-valued test inputs and the edge `NormalizeContact -> RenderWelcome` are supplied by **predefined external wiring**, not by inventing record literals or dependency syntax. The exact shared `NormalizedContact` identity/schema must agree between the two extracted contracts. No third Box, adapter operation, coercion, or handwritten public interface is needed in the BoundScript arm. A later director-backend experiment is not necessary to answer this trial's question.

### 3.3 Proposed human-owned functional requirements

The rules below must be reviewed and frozen before agents run. Later `task.md` files carry the relevant requirement IDs, behavioral rules, and examples, referring to the extracted interface rather than repeating declarations. All operations are deterministic, have no external side effects, and must not mutate their inputs. The functions may be synchronous or async; results must be equivalent.

**Normalizer — responsibility: canonicalize and classify, not render or decide whether to send.**

| ID | Required behavior |
| --- | --- |
| N-01 | For this experiment, trimming removes only ASCII space, tab, CR, and LF from string ends. Collapse runs of those characters inside the trimmed name to one ASCII space. Preserve other characters, including Unicode and HTML metacharacters; do not title-case, HTML-escape, or Unicode-normalize names. |
| N-02 | Trim the identifier and preserve its case. It is valid iff it matches `[A-Za-z0-9_-]{1,32}` in full. The normalized name must have 1–80 UTF-16 code units and no remaining C0 control characters or DEL. |
| N-03 | Trim email and lowercase ASCII A–Z only. The complete result must match `^[a-z0-9]+(?:[._+-][a-z0-9]+)*@[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$`. This is an intentionally limited experiment rule, not RFC email validation or a deliverability claim. |
| N-04 | Trim locale and lowercase ASCII A–Z; preserve exactly `en` or `fr`, otherwise use `en`. Consent is copied unchanged. Trial duration is copied unchanged and valid iff it is an integer in inclusive range 0–30; do not clamp or round it. M1 rejects non-finite values before candidate invocation. |
| N-05 | Apply the above canonicalization even on invalid submissions. Return `valid = false` and the first applicable reason in this fixed priority: `BAD_ID`, `BAD_NAME`, `BAD_EMAIL`, `BAD_DAYS`; otherwise `valid = true`, reason `OK`. Invalid results still contain every contract field. No throw for a type-valid business-invalid submission. |

**Renderer — responsibility: make a message/suppression decision from the supplied record, not repeat normalization.**

| ID | Required behavior |
| --- | --- |
| R-01 | Copy request identity exactly. If `valid` is false, suppress with `send = false`, empty recipient/HTML, subject `Not sent`, and the supplied reason. This wins over lack of consent. If valid but consent is false, suppress identically except reason `NO_CONSENT`. |
| R-02 | Otherwise set `send = true`, recipient to the supplied email, and reason `OK`. Use French only when locale is exactly `fr`; otherwise use English. Do not recanonicalize or revalidate names, addresses, identifiers, or days. Canonical producer values are the integration domain; standalone renderer tests also specify direct flag/locale behavior without assuming a peer implementation. |
| R-03 | English subject is exactly `Welcome`; French subject exactly `Bienvenue`. HTML begins with `<p>Hello, NAME!</p>` or `<p>Bonjour, NAME !</p>`. Replace NAME by escaped display name: original `&`, `<`, `>`, `"`, and `'` become `&amp;`, `&lt;`, `&gt;`, `&quot;`, and `&#39;`, respectively, once per original character. Do not trim or otherwise alter the name. |
| R-04 | Append, without extra whitespace/newline, `<p>Your trial lasts D days.</p>` or `<p>Votre essai dure D jours.</p>` when days is nonzero; D is JavaScript's string representation of the supplied finite number. For zero append `<p>No trial is included.</p>` or `<p>Aucun essai inclus.</p>`. Plural wording is intentionally fixed even for one day. |
| R-05 | Output only the specified fields. Never send email, fetch templates, consult time/randomness/environment, or read external data. The renderer's nonempty-subject predicate is only a narrow formal check; trusted assertions establish the richer behavior above. |

R-01 passes through a supplied reason even for a direct type-valid but semantically inconsistent record; the renderer does not invent missing producer intent.

**Representative public examples (to be duplicated as data in the relevant tasks, not as interface definitions):**

- E-01: `{ requestId: " r-7 ", name: "  Ada\t  <Lovelace>  ", email: " ADA@EXAMPLE.COM ", locale: " FR ", consent: true, trialDays: 7 }` normalizes to identity `r-7`, name `Ada <Lovelace>`, email `ada@example.com`, locale `fr`, consent true, days 7, valid true/reason `OK`. Final result sends to that email with subject `Bienvenue`, HTML exactly `<p>Bonjour, Ada &lt;Lovelace&gt; !</p><p>Votre essai dure 7 jours.</p>`, identity `r-7`, reason `OK`.
- E-02: Valid identifier/name/email, locale `es`, consent true, days 0: locale falls back to `en`; greeting uses the unchanged normalized name and the exact English no-trial paragraph.
- E-03: A valid contact without consent suppresses with reason `NO_CONSENT`. A bad email **and** no consent suppresses with reason `BAD_EMAIL`, not `NO_CONSENT`.
- E-04: Empty identifier, blank name, bad email, and fractional days yield `BAD_ID`; independently fix earlier faults to expose each subsequent priority. Name `A&B "C" 'D'` must appear as `A&amp;B &quot;C&quot; &#39;D&#39;` in sent HTML, not double-escaped.

### 3.4 Acceptance corpus and fixed wiring to prepare before execution

An independent human reviews expected values, not generated candidate behavior. Freeze concrete inputs and expected **complete outputs** before either session. Cover at least:

- Normalizer: whitespace/case rules; preserved Unicode; valid/invalid identifier boundaries; name lengths 0/1/80/81 and controls; accepted/rejected email subset; locales en/fr/fallback; days -1/0/1/30/31/fractional; consent both values; each failure and multiple-failure precedence.
- Renderer: both languages, fallback, zero/nonzero days, all five escaped characters including literal entity-looking text, Unicode preservation, invalid/consent precedence, exact suppressed fields, identity preservation, no input mutation, repeated-call equality.
- Integration: at least 12 distinct frozen rows spanning valid en/fr, fallback, zero and maximum days, Unicode/escaping, non-consent, each normalizer error, and competing errors. Every row asserts both the intermediate normalized record and final message; include rows not present verbatim in public examples. Each requirement has at least one independent and one applicable integration assertion; list intentional exceptions explicitly.
- Trusted harness controls: known-good human-written fixture pair, known-wrong behavioral output, malformed full output, predicate failure, missing export, invalid input/no invocation, and resource/process failure. These validate the harness, are never supplied as agent solutions, and are not the pilot agents. Existing M1 tests remain the semantics oracle; do not duplicate its evaluator.

Contracts formally check shape/finite numbers and the supported predicates. Corpus assertions check business rules; OS controls enforce resource/access restrictions; the controller records unverified properties separately. No dependency/capability syntax or automatic semantic approval is implied.

## 4. M2 delivery and independent Pi contexts

### 4.1 Explicit handoff inputs

After separate approval/implementation authorization, prepare ordinary human-owned source/tasks/scopes/policy under a proposed `experiments/contact-onboarding/` directory. Paths below are prospective, not files created by this assignment:

```json
{
  "format": "boundscript/handoff-input",
  "version": 1,
  "architecture": "experiments/contact-onboarding/system.bound",
  "policy": "experiments/contact-onboarding/policy.md",
  "boxes": [
    {
      "system": "ContactOnboarding",
      "box": "NormalizeContact",
      "task": "experiments/contact-onboarding/normalize-task.md",
      "scope": "experiments/contact-onboarding/normalize-scope.md"
    },
    {
      "system": "ContactOnboarding",
      "box": "RenderWelcome",
      "task": "experiments/contact-onboarding/render-task.md",
      "scope": "experiments/contact-onboarding/render-scope.md"
    }
  ]
}
```

The trusted controller invokes existing `npm run handoff -- <explicit-root> experiments/contact-onboarding/input.json <fresh-output> --all` twice and compares relative file sets/bytes directly. Approve actual input versions manually first; structural success is not approval. Respect M2's all-source regeneration policy and exclusive publication lifecycle. Mount/copy only the selected real per-Box directory as `handoff/`, never the whole output parent or a dangling publication symlink.

Each agent gets exactly its own eight-file handoff and prepared tool/config environment. Its `candidate/implementation.ts` starts from the seed, imports type `Implementation` via `../handoff/generated/contract.js`, and exports named `implement`. Private helpers/tests can be `.ts` modules inside `candidate/**`; no `.d.ts`, manifests, lockfiles, configs, `.pi` resources, symlinks, or new public entrypoints may be submitted. No additional dependencies: implementation uses ECMAScript only; prepared Bash/Node/TypeScript tools support authoring/private checks. Questions go to the human, not a peer.

### 4.2 Session separation

Use two ordinary Pi CLI processes, one per Box, each **entirely inside its own existing Docker Sandbox microVM**; run A then B for this minimal trial. They start from empty session history, not forks/clones/continuations of the design session or each other. Give them separate sandbox-local Pi homes/session directories and separate candidate workspaces. Session persistence is for same-Box revision only. The controller captures logs outside their reach. Do not mount the host Pi home or share skills stores, MCP integrations, peer sessions, repository, reference implementations, or auto-discovered instructions.

Use Pi's documented resource-disabling flags (`--no-extensions`, `--no-mcp`, `--no-skills`, `--no-prompt-templates`, `--no-context-files`, `--no-approve`) and the ordinary `--tools read,bash,edit,write` built-ins. **No custom extension or host-side tool forwarding is required:** Pi, its tools, private test execution, and user `!` commands all remain inside the existing sandbox boundary. Disable the sandbox runtime's shared skills and MCP integrations as well; Pi flags alone do not restrict an external gateway.

Pin provider/model/thinking and actual tool/image versions for both Boxes and the future baseline. The original `openai-codex/gpt-6.1-sol`, medium reasoning, Pi 1.4.0, Node v24.16.0, TypeScript 5.9.3 proposal remains conditional, not a proven stock-kit combination. The reviewed stock Pi kit documents an Anthropic credential path, not this OpenAI Codex OAuth path. The Product Owner's acceptance instruction prioritizes preserving the **existing OpenAI/Pi configuration**. P-04 and Assignment 0021 must qualify an existing mechanism for that configuration first; **no provider or model switch, including to the kit's documented Anthropic path, is authorized without explicit Product Owner approval**, and no new proxy implementation is permitted. Record actual selected IDs, versions, resolved kit/image references, and provider revision metadata if available. An alias or moving `latest` image is not an immutable version guarantee.

An initial prompt, identical except Box identity, says: read your protected handoff; implement only your Box inside candidate; run permitted private checks; do not change interfaces or seek another implementation; report `READY`, `CLARIFICATION` with requirement references, or `ARCHITECTURE_PROPOSAL`. These labels are human-readable conventions, not a new task DSL. The controller verifies completion rather than trusting `READY` or process exit status. Do not use RPC, SDK subagents, delegation, or a new session runner.

## 5. Proposed isolation and trusted controller

### 5.1 Select an existing whole-session sandbox

**Preferred authoring mechanism: local Docker Sandboxes with its existing Pi kit and host-side credential proxy.** Run all of Pi inside a separate microVM per Box, using its normal tools. Use the documented sandbox CLI to create, attach/exec, stop, and remove environments; no Pi extension, tool transport, SDK runner, remote-shell bridge, or new credential proxy is part of M3. Use only a dedicated per-Box workspace, never the repository checkout. Two folders/worktrees, prompt restrictions, or an ordinary Node subprocess are not acceptable substitutes for this real boundary.

Relevant existing documentation reviewed for this revision:

- Pi's installed `docs/containerization.md`: whole-process isolation and the existing Pi kit/credential setup.
- [Docker Sandboxes security model](https://docs.docker.com/ai/sandboxes/security/): microVM boundary, host-side credential substitution, explicitly shared workspaces, and shared-skills/MCP caveats.
- [Sandbox run reference](https://docs.docker.com/reference/cli/sbx/run/): additional `:ro` workspaces/files, CPU/memory sizing, and shared-skills opt-out. Use the command syntax of the selected release, not an invented wrapper.
- [Upstream Pi kit documentation](https://github.com/docker/sbx-kits-contrib/blob/main/pi/README.md): documented Anthropic authentication, upstream end-to-end tests under deny-all policy, and the warning that pinning a kit tag alone does not pin its rolling Pi image.

These are existing documented/upstream-tested capabilities, **not a claim that the pilot setup has been tested locally**. The installed host currently exposes Docker/Podman executables but no `sbx` executable was found during design inventory. Section 5.3 therefore makes qualification of the selected existing tooling an explicit prerequisite, not implementation work hidden in this design.

For frozen candidate compilation and evaluation, use ordinary disposable **non-privileged Docker containers** with no credentials, no network, read-only candidate/config/library mounts, and no host socket/home/repository, host namespaces, or device passthrough. This uses the existing runtime rather than adding an agent execution service. All candidate imports and executions, including build/private-test work, remain inside the corresponding VM/container; the controller never imports an agent module in its developer/Vitest process.

### 5.2 Essential M3 controls versus optional hardening

| Essential for this trial | Existing mechanism and small readiness check |
| --- | --- |
| Separate contexts and host boundary | One fresh whole-Pi sandbox per Box; only that Box's dedicated workspace is shared. Disable shared skills/MCP and use separate sandbox-local Pi homes/sessions. Confirm host sentinel, host credentials, repository, peer workspace, and hidden tests are not accessible. |
| Protected architectural authority | Retain approved source, contracts, tasks, config, and original tests on the controller. Share the selected handoff and prepared workspace config read-only via the runtime's documented `:ro` mounts, including read-only subpaths in an otherwise writable workspace. Probe a write denial and compare with originals after each attempt. Never rely on `chmod` or instructions against a privileged guest. If the selected release cannot enforce this, block under B-03. |
| Bounded submissions | `candidate/**` is the only accepted source subtree; permitted files remain as in Section 4.1. Guest home/tmp/system state is not an accepted deliverable. Read-only host mounts protect authority; the scope rule is not a claim that every guest filesystem write is prohibited. Stop the sandbox before snapshotting. |
| Credential protection | Use the existing host-side proxy's placeholder/credential substitution. No host Pi home, raw API/OAuth token, SSH agent, or credential-bearing environment is mounted/passed in; no in-sandbox `/login`. The guest still has metered access to the approved provider through the proxy, not access to the real key. Unsupported provider/auth is a blocker, not permission to expose a key. |
| Limited communication | Authoring permits only approved model-provider/required authentication endpoints through existing network policy, not general web/package access or peer communication. Stock kit allowlists may be broader: inspect/narrow them before use. Evaluation has network disabled entirely. Check effective policy and one bounded denied-network probe; do not claim authoring can be both network-free and call the model. |
| Protected acceptance tests | Keep hidden corpus source, expected answers, and assertion code on the controller, never in authoring or evaluation mounts. Only the fixed invocation driver and concrete inputs cross into evaluation; controller-side assertions determine functional outcomes. |
| Resource and lifetime bounds | Use existing runtime controls: proposed authoring size 1 CPU/2 GiB; evaluator 1 CPU/512 MiB with a 64-PID limit. Retain the Section 7 attempt budgets and a 60 s evaluation-suite/build deadline. A short runbook using standard timeout/stop/kill commands must stop the whole VM/container on expiry, not just detach its CLI client. Record actual settings and check a bounded stop/cleanup fixture. |

Use a dedicated disposable workspace and check the existing 10 MiB submission cap. This is not a hard disk quota. Ordinary finite resource/stop/read-only/access probes qualify configuration; they are not a custom sandbox test platform. Fail any essential check before pilot execution and return to the Product Owner.

**Optional hardening, not M3 work or a reason to expand its infrastructure:** hard storage quotas beyond the submission cap; per-tool or per-case containers; a read-only guest OS/nonroot guest restriction; dedicated hardened hosts; adversarial escape/anti-cheating suites; fine-grained per-process provider capabilities; authenticated worker attestations; automatic policy/evidence/promotion systems. Docker Sandboxes documents full guest privileges, so nonroot/read-only-guest-root claims from the earlier proposal are expressly removed. Host isolation and protected shares must still hold. Optional controls must not be reported as enforced unless actually enabled; stronger threat-model requirements need separate approval.

### 5.3 Explicit blockers and narrow prerequisite

| ID | Gap / blocking decision | Smallest permitted resolution before execution |
| --- | --- | --- |
| B-01 | No `sbx` executable is available in the inspected PATH and no local qualification has been performed. Available Docker/Podman executables do not establish equivalent credential-isolated whole-Pi support. | Separately authorize a short **existing-tool qualification prerequisite**: select a supported host/release, install/configure the existing Pi kit, and record the essential probes. No coding-agent trial, custom transport, new gateway, or platform development is included. |
| B-02 | No reviewed evidence establishes the original OpenAI Codex OAuth/model combination with the stock Pi kit's proxy. Its documented/tested path is Anthropic. | Prioritize qualification of an already available compatible mechanism for the existing OpenAI/Pi configuration under Assignment 0021. If it cannot qualify, report the exact blocker and request a Product Owner decision. No provider/model switch without explicit approval, raw-key fallback, or custom proxy; M3 execution stays unapproved. |
| B-03 | Required read-only shares, credential substitution, restricted egress, sizing/cleanup, or repeatable versions may be unsupported by the selected runtime/host/release. A pinned kit may still pull a moving Pi image. | Qualify these existing settings; record matching resolved kit/image references and actual Pi/Node/tsc versions. Use an existing documented template/image facility if needed, not new security code. If an essential control cannot be met with existing facilities, report the exact unsupported requirement and request a separate prerequisite or revised Product Owner decision; do not weaken it silently. |

No claim is made that existing tooling has met these local requirements yet. If qualification fails, stop with a bounded gap report; do not resurrect the custom Bash transport or replace OS isolation with a directory, prompt, or Node process. [Assignment 0021](0021-qualify-existing-pilot-tooling.md) is the separate **Proposed** qualification prerequisite. Its execution must be explicitly approved before any installation, configuration, environment start, or model call, and qualification must finish before the pilot's model/tool configuration and baseline assets are frozen. It changes neither the functional design nor the baseline protocol.

### 5.4 Minimal controller duties and candidate export

The controller is a human following documented runtime commands and a short runbook, not a new controller application. It approves versions/inputs, prepares the two workspaces, checks the small readiness list, starts/stops each Pi session manually, records the existing event table, handles authorized clarification, and invokes ordinary TypeScript/test commands inside disposable evaluation containers. Capture CLI/stdout/stderr and maintain a Markdown summary; no RPC control loop, scheduling, tool broker, job database, generic loader, or duplicated contract evaluator is required.

Stop all authoring/sandbox processes before copying source so agents cannot race the snapshot. Inspect and accept only bounded regular UTF-8 `.ts` files from candidate; reject links, special files, unexpected paths, manifests/config, and oversized submissions without following them on the host. Use ordinary filesystem inspection/copy after stopping; no live synchronization or custom export service. Retain per-attempt snapshots outside both sessions and compare protected inputs with originals. The controller never writes candidate code, supplies an algorithm, repairs an interface/test, or relays peer context. Raw Pi logs/transcripts, candidate/build outputs, and credentials remain local and excluded from Git; only reviewed redacted reports may be committed.

## 6. Compilation, M1 verification, and fixed integration

Use only a fixed experiment invocation/test module plus ordinary controller-side expected-value assertions and runtime commands. Reuse the M1/M2 consumer patterns; there is no custom agent execution service or general controller library.

1. **Compile each snapshot independently** inside a disposable Docker build/evaluation environment with the read-only source snapshot, handoff, and prepared ESM/strict NodeNext config: ES2022, strict, exact optional properties, unchecked-index checks, isolated modules, verbatim module syntax, `types: []`, `skipLibCheck: false`. Include the named-export consumer and permitted private modules. No repo config inheritance, candidate-selected flags, dependency installs, or lifecycle scripts. Build output goes to disposable scratch; use a 60 s external build deadline and retain diagnostics. Missing `implement`, wrong parameter/result, unapproved imports, or altered config are failures, not repair opportunities.
2. Type-only imports must disappear; no runtime `handoff/generated/contract.js` is created. Check allowed imports before execution: only permitted candidate helpers, no external runtime dependencies. Static review is not proof against computed behavior; the VM/container remains the real boundary.
3. For each frozen candidate run **one independent suite in a fresh disposable evaluation container**, and later one integration suite for the frozen pair. Ordinary Node is inside this boundary, never a substitute for it. A small fixed driver imports named `implement`, strictly decodes packaged JSON through the public codec subpath, and invokes existing M1 on the live values. Keep the M1 API/semantics unchanged; do not copy its checks. Reuse consumer import guards to forbid compiler-root/frontend/Langium loading and director execution; supply only the built codec/runtime dependency closure, not the repository. Import exceptions are load failures, not invented M1 discriminants.
4. Feed the fixed suite inputs using ordinary bounded stdin or a read-only input file; return bounded JSON observations and stderr diagnostics. Hidden test sources and expected answers remain outside. The driver records M1 results and actual intermediate/final outputs; the controller parses them as data and uses its frozen assertions to compare **complete expected values**. No second host-side M1/fixture verification pipeline, custom RPC/framing service, or per-case container machinery is required. Run in fixed case order; cap each suite at 60 s with external container cleanup. Record incomplete/unrun cases on failure. Serialization errors are transport failures, not a change to formal contract semantics.
5. Independent suites use **human-written** inputs, not peer candidates. Repeated-call/input-mutation assertions remain; within-suite state is observable behavior rather than hidden by a per-case sandbox. A fresh environment on each whole-suite rerun supplies the same initial state. No cloning/freezing is added to M1. Record actual ordering and environment for reproducibility.
6. After independent verification/revision, freeze the exact selected pair. Prewritten integration wiring aliases their existing exports, invokes normalizer through M1 on each fixed raw record, and, only on success, invokes renderer through M1 on the **unchanged live output**. No coercion, field rename, default insertion, added responsibility, schema adaptation, or implementation edit is permitted. The controller asserts both intermediate and final observations against the frozen corpus. Agents are stopped and receive no peer source even though integration necessarily loads both modules inside the evaluator.

Worker data/pass flags are not authenticated evidence. Candidate and driver share a JavaScript realm; a deliberately malicious candidate may tamper with globals or spoof observations. External assertions keep hidden expectations outside its reach, but do not prove honest execution inside a compromised worker. This bounded, non-adversarial implementation experiment retains code review and records the limitation; anti-cheating attestation is optional future work, not a new M3 security platform.

Classify results separately: setup/strict-decode failure; compile failure; export/load failure; each existing M1 `failure.kind` (inspection errors are not proven mismatches); functional assertion failure; integration failure; timeout/resource/transport failure; isolation violation; infrastructure interruption. Invalid input is a harness-negative control and must prevent invocation, not be misreported as a business-invalid contact. A shape-conforming but wrong message is a functional failure, not M1 success establishing correctness. Do not copy M1 evaluators or change compiler/runtime behavior.

The fixed driver/assertions are ordinary experiment tests prepared under a later assignment, not a production candidate loader/transpiler service, orchestration API, sandbox package, or M4 promotion/evidence system. The existing sandbox/runtime owns isolation; no custom Pi transport remains.

## 7. Reproducible protocol and failure handling

### 7.1 Readiness and ordering

Before **either** agent session:

1. Obtain explicit design acceptance and separate implementation/execution authorization. Freeze the actual source, per-Box tasks/examples/scope/policy, public/private corpus, expected outputs, wiring, baseline specification/evaluation rules, prompts, feedback policy, budgets, and model/tool/isolation configuration. Record ordinary Git revisions for human-owned inputs/tests; retain exact local snapshots of generated handoffs. No hashes/package manifests or evidence database are required.
2. Validate source/extraction and compare fresh M2 outputs. Review responsibility/interface consistency and every expected test row manually. Exercise the harness with trusted controls and complete isolation probes; run repository regressions before agents. Fix preparation defects **before** execution, not after seeing candidate outcomes.
3. Assign local run ID and Box session IDs; start fresh A then fresh B with the identical approved prompt template. Finish and snapshot **both initial submissions before sending any acceptance feedback or revisions**. The operator must not leak learning from A to B. Sequential ordering is recorded as a validity limitation, not independence proof.

### 7.2 Attempt limits and responses

Proposed per Box: **one initial attempt plus at most one independent revision**, each capped at 30 elapsed minutes and 40 model-response turns, whichever ends first. Count automatic model recovery turns in that turn budget; record provider transport retries separately. The controller tracks session usage/turns and stops at the budget; an external wall deadline stops the whole authoring sandbox. Human waiting outside an attempt is measured separately, not hidden as zero effort. Do not select the best of unreported extra runs.

An attempt is a generation episode ending in a submission, clarification/proposal, budget exhaustion, or interruption. Private test/edit loops within an episode are not extra submitted attempts; count their tool calls and elapsed time separately. An allowed revision resumes **only that Box's own** session/candidate, never forks peer context. Every episode and snapshot is retained, including failures.

| Event | Required controller response |
| --- | --- |
| Agent says READY | Snapshot and run trusted checks; claim alone is not acceptance. |
| Compile, export, contract, or behavioral failure | After both initial snapshots exist, return exact own-source compiler diagnostics or requirement ID plus failure class, not hidden test source/expected values, an algorithm, or peer code/output. One revision is allowed within budget. Reverify its entire independent suite. Exhaustion is a recorded Box failure. |
| Clarification of an existing unambiguous rule | Log exact question, response, actor, timing, and affected requirement. A human may point to already supplied text; this is an intervention even if no requirement changes. End the episode and use the one revision episode to proceed if available. Do not coach implementation. |
| Missing/ambiguous/conflicting requirement or new dependency/interface request | Stop the trial and mark it blocked/invalidated for the original frozen-input question. Product Owner resolves intent; apply M2 regeneration rules and approve a new trial ID before restarting. Retain original failures/costs; no clean-success claim under retroactively changed inputs. |
| Architectural change proposal | Record requested interface/responsibility/source impact for separate Architect/Product Owner review. Do not implement it, silently broaden context, or negotiate between agents. An approved redesign is a new trial, not repair of this one; M5 evolution is out of scope. |
| Infrastructure/model availability failure | Record separately from candidate failure, preserve partial history, and stop. No silent model switch, budget reset, or replacement agent. Product Owner may authorize a separately labelled rerun; both attempts remain reported. |
| Isolation or protected-context violation | Stop the authoring sandboxes/evaluation containers, preserve safe logs, classify the trial invalid, and return for review. A denied attempted violation is still counted; it is not a permission grant. |
| Integration failure after the independent pair is frozen | Record the first failing stage/requirement and all affected rows. **No implementation, interface, test, or wiring repair in this trial.** Further investigation/reimplementation needs a separately approved follow-up; this trial remains an integration failure. |

The controller can review each candidate to attribute failures to frozen requirements but may not debug by editing it. Final integration uses the frozen pair exactly once as a selection decision; rerunning unchanged cases for reproducibility is permitted and logged, not a candidate retry. If an independent revision occurred before freeze, distinguish it from first-pass success. No candidate is promoted to application use automatically.

## 8. Preregistered conventional TypeScript baseline (M6 prerequisite)

**Define now; do not implement or execute the comparison under 0020.** Before M3 pilot execution, the Product Owner must approve the baseline/task equivalence and evaluation rules below. A later assignment must prepare/freeze the concrete baseline assets and conventional test oracles before any pilot model calls; do not design them from observed agent failures. Executing the baseline/comparative evaluation remains separately authorized M6 work.

### 8.1 Minimal baseline arm

- Same scenario, requirements N-01–N-05/R-01–R-05, examples, exact input/output semantics, corpus, expected outcomes, scope, allowed tools, isolation, prompt intent, budgets, feedback/retry rules, and predefined wiring.
- One conventional human-owned TypeScript file is the interface authority, declaring the three flat interfaces and two operation signatures. Prepare per-Box read-only declaration subsets/`Input`/`Result`/`Implementation` aliases and the same seed import/export convention using ordinary TypeScript/Markdown. No `.bound` source, M2 derivation, portable JSON codec, or M1 verifier in that arm. Humans review agreement once before freeze; count the manual interface preparation/review labor rather than hiding it or deliberately planting drift.
- Match bounded context: each baseline agent sees only its relevant declarations/task/scope/policy, not the full system or peer implementation. Only format-specific instructions differ; prerecord those differences. Baseline may use normal explicit TypeScript assertions/tests for required own keys/primitive/finite outputs and business expectations, including nonempty reason/subject. Keep them small concrete tests, not another reusable schema/contract framework. Align semantic cases with the BoundScript arm, using independent human review so neither candidate nor a new BoundScript-only oracle defines expected answers.
- Use two fresh Pi sessions and the same prepared NodeNext environment; same absence of runtime declaration-module import. Conventional test checks and immutable TypeScript interfaces are a serious baseline, not an intentionally weak one. Count the different checking/authoring work as an outcome.

### 8.2 Evaluation plan fixed before outcomes

Propose a **descriptive paired feasibility comparison**, one two-Box pair per arm, not a statistically powered benchmark. The M3 observations may serve as the preregistered BoundScript arm; the conventional arm runs only under later authorization with fresh contexts and unchanged approved tasks/tests/settings. If models/tools or rules cannot be held comparable later, report non-comparability and seek approval for a new matched comparison; do not silently compare unlike runs.

Because M3 precedes a later M6 baseline, order is fixed BoundScript-first and the controller cannot unlearn it. Preserve the frozen baseline assets and ban ad hoc coaching in either arm. For a later replicated comparison, preregister counterbalanced arm order and independent operators before new runs; do not retrofit statistical claims onto this single trial.

Compare the metrics in Section 9, separately for preparation, authoring, independent verification, and integration. Primary feasibility outcome is unchanged frozen-pair integration under approved interfaces; primary coordination measures are intervention count and human coordination minutes. Report absolute values and arm differences, not only percentages or a combined success score. Report failures, missing usage/cost metadata, and unequal context/setup overhead. Do not declare superiority from one successful integration or invent a favorable threshold after results.

For a modest comprehension check, before execution fix five questions: responsibilities; shared boundary; suppression precedence; tested versus merely declared behavior; and which candidate/input/test revisions were evaluated. After a future authorized comparison, an uninvolved reviewer answers from each arm's architecture/task/summary evidence without implementation source, recording correct answers out of five and elapsed minutes. This is a diagnostic, not validated human-subject research or a universal readability claim. Broader M6 study design, recruitment, statistical analysis, and a continue/narrow/stop product decision remain M6 work.

## 9. Measurable outcomes and report

Use a controller-maintained Markdown event table and summary, not an evidence service. Per event record run/arm/Box/attempt, requirement/stage, actor, timestamp/duration, category, reason, and action. Record denied attempts as well as successful changes. Keep raw transcripts private/local and excluded from Git; publish only reviewed redacted summaries, not secrets or full session exports.

| Metric | Counting rule / report |
| --- | --- |
| Human interventions | Each unplanned human clarification, diagnostic feedback, implementation-directed suggestion, permission/context decision, or manual recovery action is one event. Scheduled launch/snapshot/check actions are separate operational work, not hidden coordination. Report count and active minutes by category. |
| Clarification requests | Count each distinct question and response; repeated unresolved questions remain events. Classify existing-text pointer vs missing requirement vs interface ambiguity. |
| Interface/architecture changes | Count proposals, attempted protected edits, approved changes, and actual source/interface/wiring changes separately. Qualifying frozen-trial success requires **zero actual changes**, zero interface negotiation, and zero controller implementation edits. |
| Boundary violations | Count attempted/denied and successful accesses/edits by protected category; any successful violation invalidates the trial. No attack-suite/security-certification claim. |
| Failures | Per Box and stage: setup, compile, export/load, M1 discriminant, behavior, process/resource/transport; separately integration cases failing and first failing stage. Do not merge invalid input, candidate exception, predicate mismatch, and infrastructure failure. |
| Retries and revisions | Initial/revision episode count, each submitted snapshot, private check loops/tool calls, provider transport retries, and authorized new-trial reruns separately. Never omit failed candidates. |
| Context requirements | Supplied handoff bytes/files, prompt/response tokens if available, additional context requests and granted additions. No peer implementation context may be granted. |
| Effort and overhead | Human preparation/review/coordination minutes, agent elapsed time, verification/integration time, tool calls, model tokens/cost where available; use `unknown` where not observable. Report environment qualification/setup cost separately and include it in total workflow cost. |
| Comprehension | For later baseline evaluation, fixed five-question score/time; no reading all implementation code. Report the limited instrument and operator familiarity. |
| Independent implementation success | Both selected candidates pass independent compile/export/M1/behavioral suites, then all frozen integration rows pass through unchanged wiring with no architecture/interface/manual repair or peer negotiation. Report first-submission unassisted success separately from success after permitted independent revision/clarification. |

An experiment conducted according to protocol can validly report **failure or inconclusive**. That is not M3's successful exit gate. Only the Product Owner may accept delivery and close M3 after evaluating actual results against its gate. This document does not preapprove closure or an arbitrary number of retries.

## 10. Limitations and threats to validity

- One scenario, two Boxes, one pair of model samples, fixed execution order, and a knowledgeable controller cannot establish causal superiority, general scalability, or statistical significance. Model training familiarity/provider drift and nondeterminism remain uncontrolled.
- Flat records, pure functions, and no external dependencies deliberately simplify the problem. This tests a meaningful semantic boundary but not stateful distributed systems, asynchronous side effects, rich types, production sandboxing, or capability enforcement.
- Human-authored tasks/tests/wiring can encode the wrong product intent or leak hints. Independent review and frozen examples reduce, not eliminate, this risk. Hidden cases must cover published rules, not introduce secret requirements. Controllers seeing A first can inadvertently coach B; log all messages and prohibit leakage.
- Typing and `ensure` prove little business behavior; finite tests do not prove arbitrary correctness, purity, nominal type origin, or absence of computed side effects. M1 permits live objects/getters; serialized observations do not authenticate a hostile worker or preserve every exotic JavaScript property. Do not tighten runtime semantics to disguise this limit.
- Authoring uses an existing microVM boundary; evaluation containers share their host kernel. Runtime/image supply chains and the host controller remain trusted. Guest root privileges do not imply host access, but host shares and permitted provider access still have consequences. Writable storage is not hard-quota-enforced in the minimal proposal. These are controlled-development restrictions, not proof against a determined adversary or a production isolation platform. Qualification/readiness failures block execution rather than trigger weaker fallbacks.
- Provider access exposes task contents to the selected provider; use synthetic contacts only and obtain policy approval. No real personal information, production data, or repository/provider secrets go into tasks or candidate tools.
- M3's small event log is an experiment record, not M4 authenticated evidence identity, stale-evidence enforcement, or promotion. If inputs/tests/candidates change, humans discard affected observations and reverify per protocol; there is no implemented automatic currentness system.
- Baseline manual interfaces create a different preparation cost by design. Report both fairness review and that cost, rather than using BoundScript derivation in both arms or hiding its setup cost. A later baseline with a different model/date/operator may be only exploratory, not comparable.

## 11. Approved design and remaining operational decisions

The Product Owner accepted the revised scenario, independent two-Box experiment, frozen integration/failure protocol, baseline, and simplified existing-tool isolation approach **at design level**. The table retains the pre-execution decisions: actual input/test versions, tooling qualification, provider/model compatibility, budgets, and implementation/execution authorization are not inferred from design acceptance. Preserve the existing OpenAI/Pi configuration; any provider/model change needs explicit Product Owner approval.

| ID | Decision |
| --- | --- |
| P-01 | Retain the endorsed contact-onboarding/two-Box direction and external wiring, with no grammar/spec/runtime changes; freeze the actual source version before execution. |
| P-02 | Retain the endorsed functional requirements unchanged; approve concrete task/test versions and complete the pre-execution corpus/oracle review. |
| P-03 | Approve existing whole-session Docker Sandboxes/Pi-kit authoring and ordinary credential-free Docker evaluation, the essential/optional split, and stated threat limits. Separately authorize the bounded existing-tool qualification prerequisite for B-01–B-03; unsupported essential controls block the pilot. No custom transport, proxy, or security platform. |
| P-04 | Resolve B-02 by prioritizing existing-tool qualification for the current OpenAI/Pi provider/model configuration. A different provider/model requires explicit Product Owner approval, not an inferred stock-kit fallback. Freeze matching model/reasoning/tool/image versions, synthetic-data provider policy, contexts, existing attempt/feedback budgets, and spending cap before execution; no repairs after integration freeze. |
| P-05 | Retain the endorsed preregistered TypeScript baseline/evaluation protocol unchanged; approve concrete corpus/prompt equivalence and baseline assets before M3 execution. Actual baseline execution/product comparison still requires separate M6 authorization. |
| P-06 | Approve later preparation of ordinary experiment assets, the small fixed driver/assertions and runbook, followed by separate execution authorization after qualification. Acceptance of 0020 alone does not authorize installing/configuring tooling, preparing the pilot, launching sessions, or marking M3 In Progress/Completed. |

No new public contract authority, provider integration, agent framework, orchestration service, scheduler, job manager, dependency language, hash manifest, evidence database, candidate promotion, M4 enforcement, M5 evolution, or M6 comparison execution is proposed here.

## 12. Acceptance criteria and delivery boundaries

### Assignment 0020 — design acceptance

| ID | Required evidence for review |
| --- | --- |
| D-01 | Proposed design cites accepted direction, current roadmap/workflow, inspected M1/M2 code/acceptance records, and distinguishes existing capabilities from future experiment tooling. Only this Markdown document is delivered; M3 stays Planned. |
| D-02 | Concrete nontrivial two-Box source uses current language; responsibilities, numbered functional requirements, public examples, frozen corpus coverage, and unchanged predefined integration are specified without manually duplicated BoundScript-arm public interfaces. |
| D-03 | Explicit M2 inputs/selection/package delivery and two fresh Pi contexts prevent sharing implementation context; fixed entrypoint, allowed dependencies/files, and session/resource configuration are documented. |
| D-04 | Isolation uses existing documented/upstream-tested whole-session/runtime facilities, with real boundaries, protected shares/credentials/tests, minimal manual controls, an essential/optional split, and explicit B-01–B-03 prerequisites/blockers. No custom transport or security platform; no pilot tooling, untrusted code, or agents execute during design delivery. |
| D-05 | Independent strict compilation, named-export/ESM loading, strict portable decoding, M1 semantics reuse inside isolation, external behavioral assertions, and frozen integration with no repairs are specified; failure classes stay distinct. |
| D-06 | Reproducible pre-execution freeze, attempt/feedback budgets, clarification/architecture/infrastructure handling, negative outcomes, and manual event/metric definitions are explicit and not an orchestration/evidence framework. |
| D-07 | Conventional TypeScript baseline and evaluation protocol are defined before execution with fairness controls, setup costs, order/sample limitations, and no comparison run or M6 completion claim. |
| D-08 | P-01–P-06, limitations, future pilot success gate, acceptance/implementation authorization boundaries, and documentation verification are clear. Product Owner acceptance is required before proceeding. |

### Gate for a later implementation/execution assignment

Require separate authorization to prepare actual approved assets and execute the pilot. Before execution: approve baseline/evaluation protocol and freeze concrete equivalent assets, source/tasks/policy/tests/wiring/prompts/tool versions; validate whole source and byte-identical M2 derivations; resolve B-01–B-03 through the separately authorized qualification prerequisite and pass essential readiness checks; exercise trusted harness controls; and pass repository `npm run check`, build, existing Box demos, Hello World CLI, and canonical export comparison. Untrusted candidate import/execution must remain exclusively inside the approved evaluation boundary, not a normal repository regression.

Actual pilot evidence must include both independent session/snapshot histories, all attempted submissions/failures/interventions/budgets, independent compile/M1/functional results, unchanged frozen-pair integration outcomes, protected-context observations, and unverified properties. M3's exit gate requires both candidates to pass their independent checks and all prewritten integration assertions **without integration-time implementation edits, interface negotiation, architecture changes, or controller repair**. Report allowed pre-freeze revisions transparently; a failed/inconclusive experiment cannot be relabelled as satisfying that gate.

For **this design-only delivery**, check local Markdown links/anchors, balanced fences, required sections/status, proposed-source parsing/extraction with existing APIs only, and `git diff --check`. Do not create pilot source/task/test files, generate operational handoffs, build new isolation tooling, launch Pi sessions/containers, or execute baseline/candidates. Existing regression counts above are reference evidence, not new pilot test results. Report document commit, unchanged experimental direction/baseline, design verification, and remaining operational decisions/blockers; wait for Product Owner review. Commit/push only this authorized design document to the current feature branch. No roadmap status or acceptance record changes are part of 0020 preparation.

### Design-delivery verification (before acceptance)

- Revision checks compare the complete functional source/rules/corpus (Section 3), M2 binding/package design (Section 4.1), frozen integration/failure rules (Section 7, except sandbox terminology), and preregistered baseline/evaluation protocol (Section 8) against the prior design. Their experimental substance is unchanged. The custom transport, duplicated host verification pipeline, and per-case container requirement are removed.
- Local Markdown targets/anchors, balanced code fences, Proposed status, and D-01–D-08/P-01–P-06/B-01–B-03 coverage checks pass; whitespace is checked with `git diff --check`.
- The proposed source block parses and passes whole-system extraction for both selected Boxes using existing built APIs. Strict canonical serialization/decoding round-trips, shared intermediate descriptors, supported predicate targets, and example binding identities agree. This in-memory validation creates no pilot files or operational handoffs and executes no Box implementation.
- No Pi agent session or container was launched, no candidate/baseline was implemented or executed, and no production regression result is claimed for new pilot functionality. The revised design was delivered as Proposed before acceptance; M3 remains Planned, and separate tooling qualification and pilot authorization are outstanding.

## Product Owner acceptance and completion evidence

The Product Owner explicitly accepted the revised Assignment 0020 design and authorized recording **Assignment 0020 — Completed**, while keeping **M3 — Planned**.

- **Accepted design revision:** `7b75de628a91b81ee0160ba34360297ff2b4e15c` — replaces the custom Pi Bash transport with existing whole-session sandbox tooling, separates essential controls from optional hardening, simplifies evaluation, and records B-01–B-03 as explicit prerequisites/blockers. It builds on initial design `d0aab112ea57ffb9dbfe2c84010976e50e1e489d`.
- **Approved at design level:** ContactOnboarding scenario, independent NormalizeContact/RenderWelcome decomposition and functional rules, protected separate M2/Pi contexts, frozen no-repair integration/failure protocol, preregistered conventional TypeScript baseline/evaluation protocol, and simplified existing-tool isolation direction. No experimental result or locally qualified sandbox is established by this approval.
- **Binding acceptance instruction:** Prioritize preserving the existing OpenAI/Pi provider/model configuration. No provider/model switch is authorized without explicit Product Owner approval. Prepare the minimal separate [0021 qualification proposal](0021-qualify-existing-pilot-tooling.md) to address B-01, B-02, and B-03 before M3 implementation or agent execution; its preparation is not permission to execute qualification.

| Design criterion | Accepted evidence |
| --- | --- |
| D-01 | Accepted direction, roadmap/workflow and completed M1/M2 implementations/acceptance records are investigated. Delivery was a Proposed design document only; M3 stayed Planned. |
| D-02 | Concrete two-Box source, numbered functional rules, public examples, corpus coverage, and fixed external wiring use existing language capabilities. In-memory parsing/extraction and strict canonical round-trip pass; shared intermediate descriptors agree. |
| D-03 | Explicit M2 bindings, eight-file package delivery, separate fresh Pi contexts, fixed export/import convention, and permitted files/dependencies are specified. No sessions were launched. |
| D-04 | Existing documented/upstream-tested isolation is preferred over custom infrastructure. Essential versus optional controls, protected credentials/workspaces/tests, and unqualified local gaps B-01–B-03 are explicit. No boundary is claimed from directories/prompts/Node processes. |
| D-05 | Independent compilation/export checks, M1 reuse inside a real boundary, external expected-value assertions, and unchanged frozen-pair wiring are specified without introducing a second evaluator or repair path. |
| D-06 | Pre-execution freeze, bounded independent revisions, failure/clarification/architecture handling, and manual event/metric definitions are retained; negative outcomes remain reportable. |
| D-07 | Conventional TypeScript baseline/evaluation protocol is preregistered and unchanged by the infrastructure revision. No baseline/comparison was executed. |
| D-08 | Design approval is separated from qualification/implementation/execution approval and milestone closure. Documentation links/anchors, fences/status checks, preserved experimental sections, and whitespace checks pass. |

No design-review correction remains pending. **Operational gaps are not resolved by acceptance:** no `sbx` was found in the inspected PATH; compatibility of the current OpenAI/Pi auth/model path with existing isolation tools is unverified; essential mounts/egress/cleanup/version controls remain unqualified. Assignment 0021 is Proposed for review, not completed or authorized for execution.

**M3 remains Planned and its exit gate is untested.** No tools were installed, pilot assets implemented, pilot agents launched, or comparison run. Qualification execution requires explicit authorization; even a successful accepted qualification report must be followed by a separately approved pilot implementation/execution assignment. Design acceptance alone starts neither M3 execution nor M6 comparison.
