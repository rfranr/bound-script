# Assignment 0020 — Design Independent Implementation Pilot (M3)

**Status:** Proposed
**Milestone:** [M3 — Independent implementation pilot](../roadmap.md#m3--independent-implementation-pilot)
**Direction:** [Accepted Proposal 0013](../proposals/0013-deterministic-architecture-for-probabilistic-construction.md), especially Sections 2, 6, 7, 10, and 11.
**Scope:** Design only. No pilot implementation, agent launch, comparison execution, or milestone-status change is authorized by this document. M3 remains **Planned**. Product Owner review must precede further work; design acceptance must be followed by a separately authorized implementation/execution assignment.

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

M1/M2 acceptance records report Node v24.16.0, TypeScript 5.9.3, Linux, and 416 passing tests in 17 files after M2 correction. Those are existing foundation results, **not pilot evidence**. Pi and container configuration described below have not been exercised under this assignment. Existing Pi examples are API references, not vetted isolation policies: the SSH/sandbox examples have local fallback paths and must not be treated as fail-closed pilot controls unchanged.

## 3. Proposed scenario and architecture

### 3.1 Contact onboarding with safe welcome rendering

An application receives a contact submission containing inconsistent whitespace/case, an email address, locale preference, consent, and trial duration. It must normalize and classify the submission, then produce either an exact localized welcome message or a deterministic suppression result. No message is actually sent.

This is more meaningful than a greeting echo: the producer handles canonicalization, multiple validation failures and precedence, and numeric limits; the consumer handles consent/invalid-state policy, localization, zero-day behavior, and HTML escaping. Integration must preserve identity and carry a complete shared record across independently implemented boundaries. Type-correct code can still disagree on error priority, canonicalization, suppression, escaping, or exact output. There are enough interacting requirements to expose coordination problems without introducing databases, services, nested types, clocks, or network dependencies.

This selects and elaborates Proposal 0013's suggested `NormalizeContact`/`RenderWelcome` scenario **for approval**, not as an already accepted pilot selection.

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

Use two ordinary Pi CLI processes, one per Box; run A then B for this minimal trial. They start from empty session history, not forks/clones/continuations of the design session or each other. Give them separate clean host agent/config directories, separate controller-owned session directories, and separate sandbox candidate directories. Session persistence is for same-Box revision only. No shared user memory, skills, MCP, custom providers, web/search tools, source repository, reference implementations, or auto-discovered instructions.

Use Pi's documented resource-disabling flags (`--no-extensions` with only the explicit trusted tool extension, `--no-mcp`, `--no-skills`, `--no-prompt-templates`, `--no-context-files`, `--no-approve`) and `--tools bash`. There is one sandbox-backed Bash tool, not the unrestricted built-in. Pin provider/model/thinking explicitly; proposal: the same `openai-codex/gpt-6.1-sol`, medium reasoning, Pi 1.4.0, Node v24.16.0, TypeScript 5.9.3 for both, subject to availability/cost approval. Record actual versions/selected IDs and provider-reported revision metadata if available; an alias is not an immutable model guarantee. Disable unrelated configured resources in the clean profiles, not merely prompt their non-use.

An initial prompt, identical except Box identity, says: read your protected handoff; implement only your Box inside candidate; run permitted private checks; do not change interfaces or seek another implementation; report `READY`, `CLARIFICATION` with requirement references, or `ARCHITECTURE_PROPOSAL`. These labels are human-readable conventions, not a new task DSL. The controller verifies completion rather than trusting `READY` or process exit status. Do not use RPC, SDK subagents, delegation, or a new session runner.

## 5. Proposed isolation and trusted controller

### 5.1 Minimal boundary, not directories-as-security

Use existing **rootless Podman containers** on a supported Linux host for tool execution and, separately, compilation/evaluation. Pi itself stays on the controller side solely as a trusted model client/tool broker; its provider credentials and session logs never enter candidate containers. This avoids putting an API key in the same environment where arbitrary generated Node/Bash code can read it. Two folders/worktrees, a Node child process, or a read-only instruction alone are explicitly insufficient.

The only proposed Pi-specific glue is a small, audited, **fail-closed Bash tool transport** following the installed tool-operations examples. It forwards command text as an argument through `spawn`/`execFile` to a controller-selected fixed container and fixed working directory. It never interpolates agent text into a host shell, accepts no agent-selected container/mount/env/runtime flags, and has no local-execution fallback. Built-in read/write/edit and every other tool are disabled; file work is done through that container's Bash. User `!` commands must be routed identically or rejected. Missing container, initialization failure, cancellation, or resource exhaustion returns a tool error and stops the run, never executes locally. This is an environment adapter, not an agent framework, provider integration, or scheduler. It requires explicit approval under decision P-03.

Host Pi, the reviewed transport, runtime/tool images, and controller account are trusted computing base. All model-directed executable work is confined to the containers. No candidate-authored extension/config is loaded by host Pi; no arbitrary host tool can be enabled mid-trial. Human operators must not execute agent-suggested host commands outside the approved runbook.

### 5.2 Mounts, privileges, and limits

| Item | Candidate tool container | Controller / verification boundary |
| --- | --- | --- |
| Own handoff | Read-only bind of the selected materialized package | Original approved inputs retained outside agent access |
| Candidate | Only per-Box `candidate/**` is writable submission content | Separate directories; never mount a sibling Box or repository root |
| Environment | Read-only ESM package/config and preinstalled Node/tsc/Bash; nonroot UID, read-only rootfs, no capabilities, no privilege escalation | Build images beforehand from recorded versions; no agent `npm install`, package scripts, git, or mutable lockfiles |
| Temporary runtime data | Bounded private tmpfs for `/tmp`; not a submission channel | No host temp/home mounts, container socket, SSH agent, host PID namespace, or credentials |
| Network | `--network=none`; no service discovery or peer channel | Only host Pi needs the approved model-provider connection; no provider secrets forwarded to `podman exec` or inherited tool environment |
| Acceptance tests / wiring | Not mounted during authoring; expected values/test sources never mounted into candidate execution | Controller owns read-only originals and performs expected-output assertions outside the candidate container |
| Resources | Proposed 1 CPU, 512 MiB memory, 64 PIDs, 64 MiB temporary storage; tool command deadline 60 s | External deadline cleanup kills/removes the whole container, including descendants, not just the exec client |

Working-source storage uses a dedicated disposable candidate directory. A 10 MiB submission cap is checked by the controller; it is **not** a hard disk quota. Monitor the disposable filesystem and stop on storage abuse; host disk exhaustion remains a limitation unless an approved host quota is available. Runtime `/tmp` and memory/process limits are enforced by the container configuration, not claimed from a policy string. Implementation must confirm rootless cgroup/network/read-only support before execution; fail closed if required controls cannot be established. Do not silently substitute host execution, add credentials to a container, or weaken isolation for convenience.

Before the first model call, use trusted, bounded probes to confirm: own handoff/config cannot be changed; host sentinel/auth paths and other Box/test paths cannot be read; candidate can be written; networking is unavailable; no sensitive environment/process state is inherited; cleanup removes descendant processes; no tool bypass or fallback is active. Verify limits/configuration and a bounded timeout-control fixture without intentionally running hostile code on the host. These are proposed readiness tests, not checks performed in this design assignment. A failed probe blocks execution and returns to the Product Owner.

### 5.3 Controller duties and candidate export

The human controller selects approved versions, prepares images/mounts/config, runs preflight, launches each Pi session manually, watches deadlines/budgets, records events, answers only authorized clarifications, snapshots candidates, runs checks, and reports negative as well as positive outcomes. It never writes implementation code, supplies an algorithm, edits interfaces/tests to fit results, or moves peer context between sessions.

At submission, terminate all authoring/container processes before copying files so agents cannot race the snapshot. Only allow bounded regular UTF-8 `.ts` source files from candidate; reject links, special files, unexpected paths, manifests/config, and oversized submissions without following them on the host. Copy data without executing scripts or preserving executable hooks. Retain an immutable per-attempt source snapshot outside both sessions. Local raw Pi logs/transcripts, candidate/build outputs, and credentials are excluded from Git; a later redacted human-readable experiment report can reference local snapshots and approved source/test revisions without inventing M4 identity infrastructure.

## 6. Compilation, M1 verification, and fixed integration

1. **Compile each snapshot independently** in a fresh restricted build container, using the prepared ESM/strict NodeNext configuration from M2's consumer pattern: ES2022, strict, exact optional properties, unchecked-index checks, isolated modules, verbatim module syntax, `types: []`, `skipLibCheck: false`. Include the named-export consumer and all permitted reachable private modules. No repo config inheritance, candidate-selected compiler flags, dependency install, or lifecycle scripts. Use a 60 s external build deadline; retain diagnostics. Missing `implement`, wrong parameter/result, unapproved imports, or config changes are failures, not opportunities for controller repair.
2. Emitted type-only imports must disappear; no runtime `handoff/generated/contract.js` is created. Inspect allowed import paths before execution: implementation imports may reach only permitted candidate helpers, with no external runtime dependencies. This review is not a proof against computed dynamic behavior; OS confinement remains necessary.
3. **Load/execute only inside a fresh restricted evaluation container**, never the host developer/Vitest process. A small fixed experiment driver imports named `implement`, strictly decodes controller-supplied packaged JSON through the public codec subpath, and calls the existing M1 verifier on fixed input. The M1 API is unchanged: it receives an already-loaded function inside that boundary, not a container handle. An import/load exception is a harness load failure, not a fabricated M1 failure discriminant. Reuse M1/M2 consumer import guards to forbid compiler-root/frontend/Langium loading and director execution in this consumption path; only the public codec/runtime built dependency closure is supplied, not the source repository.
4. Keep expected-output assertions and hidden corpus/test sources on the controller, outside the execution container. Feed one fixed case per fresh evaluation process/container via bounded stdin; the driver contains no expected answers. It uses M1 on the **live** returned value before serializing observations. Record both M1 stage results and the serializable observed values; independently check returned data shape/predicates on the controller using existing codec/M1 checks with trusted value-returning fixtures before comparing to the human-owned expected record. No candidate code is imported on the controller. Serialization failures are transport failures, not new formal contract semantics. Bound output size and apply a 5 s external deadline per evaluation; kill all descendants on failure.
5. Worker logs/results are untrusted data, never executable instructions or authoritative pass flags. Controller assertions, not agent claims or a worker exit code, determine observed functional pass/fail. Candidate and driver share a JavaScript realm, so a deliberately malicious candidate could spoof worker observations or tamper with globals. Outside assertions protect expected values/files, but do not authenticate execution or prove honest M1 operation inside a compromised worker. Code review, bounded honest-task assumptions, and this explicit limitation are part of the pilot; do not claim anti-cheating/security attestation. Requests for stronger adversarial assurance require a separate design, not a new verifier here.
6. Independent normalizer and renderer tests use **human-written** records, not the peer candidate, so one Box can fail without blaming the other. Fresh processes per case avoid cross-case filesystem/module state. Repeated invocation/input-mutation checks may make bounded calls in one designated case to observe those requirements; preserve M1's live-object semantics, do not silently add cloning/freezing to the verifier.
7. After independent verification/revision is complete, freeze the exact two selected snapshots. Only then mount both compiled modules read-only in a fresh integration evaluator. Prewritten wiring aliases their existing named exports, invokes normalizer through M1 on the fixed raw record, and, only on success, invokes renderer through M1 on the **unchanged live output**. No intermediate coercion, field rename, default insertion, schema adaptation, added responsibility, or candidate edit is permitted. The controller asserts both recorded intermediate and final values against the frozen corpus. Agents are no longer running and receive no peer source even though the evaluator necessarily contains both modules.

Classify results separately: setup/strict-decode failure; compile failure; export/load failure; each existing M1 `failure.kind` (inspection errors are not proven mismatches); functional assertion failure; integration failure; timeout/resource/transport failure; isolation violation; infrastructure interruption. Invalid input is a harness-negative control and must prevent invocation, not be misreported as a business-invalid contact. A shape-conforming but wrong message is a functional failure, not M1 success establishing correctness. Do not copy M1 evaluators or change compiler/runtime behavior.

The driver and transport would be narrow disposable experiment tooling under a later assignment, not a production candidate loader/transpiler service, orchestration API, sandbox package, or M4 promotion/evidence system.

## 7. Reproducible protocol and failure handling

### 7.1 Readiness and ordering

Before **either** agent session:

1. Obtain explicit design acceptance and separate implementation/execution authorization. Freeze the actual source, per-Box tasks/examples/scope/policy, public/private corpus, expected outputs, wiring, baseline specification/evaluation rules, prompts, feedback policy, budgets, and model/tool/isolation configuration. Record ordinary Git revisions for human-owned inputs/tests; retain exact local snapshots of generated handoffs. No hashes/package manifests or evidence database are required.
2. Validate source/extraction and compare fresh M2 outputs. Review responsibility/interface consistency and every expected test row manually. Exercise the harness with trusted controls and complete isolation probes; run repository regressions before agents. Fix preparation defects **before** execution, not after seeing candidate outcomes.
3. Assign local run ID and Box session IDs; start fresh A then fresh B with the identical approved prompt template. Finish and snapshot **both initial submissions before sending any acceptance feedback or revisions**. The operator must not leak learning from A to B. Sequential ordering is recorded as a validity limitation, not independence proof.

### 7.2 Attempt limits and responses

Proposed per Box: **one initial attempt plus at most one independent revision**, each capped at 30 elapsed minutes and 40 model-response turns, whichever ends first. Count automatic model recovery turns in that turn budget; record provider transport retries separately. The controller tracks session usage/turns and stops at the budget; an external wall deadline terminates tool containers. Human waiting outside an attempt is measured separately, not hidden as zero effort. Do not select the best of unreported extra runs.

An attempt is a generation episode ending in a submission, clarification/proposal, budget exhaustion, or interruption. Private test/edit loops within an episode are not extra submitted attempts; count their tool calls and elapsed time separately. An allowed revision resumes **only that Box's own** session/candidate, never forks peer context. Every episode and snapshot is retained, including failures.

| Event | Required controller response |
| --- | --- |
| Agent says READY | Snapshot and run trusted checks; claim alone is not acceptance. |
| Compile, export, contract, or behavioral failure | After both initial snapshots exist, return exact own-source compiler diagnostics or requirement ID plus failure class, not hidden test source/expected values, an algorithm, or peer code/output. One revision is allowed within budget. Reverify its entire independent suite. Exhaustion is a recorded Box failure. |
| Clarification of an existing unambiguous rule | Log exact question, response, actor, timing, and affected requirement. A human may point to already supplied text; this is an intervention even if no requirement changes. End the episode and use the one revision episode to proceed if available. Do not coach implementation. |
| Missing/ambiguous/conflicting requirement or new dependency/interface request | Stop the trial and mark it blocked/invalidated for the original frozen-input question. Product Owner resolves intent; apply M2 regeneration rules and approve a new trial ID before restarting. Retain original failures/costs; no clean-success claim under retroactively changed inputs. |
| Architectural change proposal | Record requested interface/responsibility/source impact for separate Architect/Product Owner review. Do not implement it, silently broaden context, or negotiate between agents. An approved redesign is a new trial, not repair of this one; M5 evolution is out of scope. |
| Infrastructure/model availability failure | Record separately from candidate failure, preserve partial history, and stop. No silent model switch, budget reset, or replacement agent. Product Owner may authorize a separately labelled rerun; both attempts remain reported. |
| Isolation or protected-context violation | Stop/kill containers, preserve safe logs, classify the trial invalid, and return for review. A denied attempted violation is still counted; it is not a permission grant. |
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
| Effort and overhead | Human preparation/review/coordination minutes, agent elapsed time, verification/integration time, tool calls, model tokens/cost where available; use `unknown` where not observable. Report environment/adapter setup cost separately and include it in total workflow cost. |
| Comprehension | For later baseline evaluation, fixed five-question score/time; no reading all implementation code. Report the limited instrument and operator familiarity. |
| Independent implementation success | Both selected candidates pass independent compile/export/M1/behavioral suites, then all frozen integration rows pass through unchanged wiring with no architecture/interface/manual repair or peer negotiation. Report first-submission unassisted success separately from success after permitted independent revision/clarification. |

An experiment conducted according to protocol can validly report **failure or inconclusive**. That is not M3's successful exit gate. Only the Product Owner may accept delivery and close M3 after evaluating actual results against its gate. This document does not preapprove closure or an arbitrary number of retries.

## 10. Limitations and threats to validity

- One scenario, two Boxes, one pair of model samples, fixed execution order, and a knowledgeable controller cannot establish causal superiority, general scalability, or statistical significance. Model training familiarity/provider drift and nondeterminism remain uncontrolled.
- Flat records, pure functions, and no external dependencies deliberately simplify the problem. This tests a meaningful semantic boundary but not stateful distributed systems, asynchronous side effects, rich types, production sandboxing, or capability enforcement.
- Human-authored tasks/tests/wiring can encode the wrong product intent or leak hints. Independent review and frozen examples reduce, not eliminate, this risk. Hidden cases must cover published rules, not introduce secret requirements. Controllers seeing A first can inadvertently coach B; log all messages and prohibit leakage.
- Typing and `ensure` prove little business behavior; finite tests do not prove arbitrary correctness, purity, nominal type origin, or absence of computed side effects. M1 permits live objects/getters; transport observations and postserialization checks do not authenticate a hostile worker or preserve every exotic JavaScript property. Do not tighten runtime semantics to disguise this limit.
- Containers share a kernel, rootless controls vary by host, runtime/image supply chains and the host Pi/transport remain trusted, and writable candidate storage is not hard-quota-enforced in the minimal proposal. These are controlled-development restrictions, not proof against a determined malicious adversary or a production isolation platform. Readiness failures block rather than trigger weaker fallbacks.
- Provider access exposes task contents to the selected provider; use synthetic contacts only and obtain policy approval. No real personal information, production data, or repository/provider secrets go into tasks or candidate tools.
- M3's small event log is an experiment record, not M4 authenticated evidence identity, stale-evidence enforcement, or promotion. If inputs/tests/candidates change, humans discard affected observations and reverify per protocol; there is no implemented automatic currentness system.
- Baseline manual interfaces create a different preparation cost by design. Report both fairness review and that cost, rather than using BoundScript derivation in both arms or hiding its setup cost. A later baseline with a different model/date/operator may be only exploratory, not comparable.

## 11. Decisions requiring explicit Product Owner approval

All are **proposed**, not approvals inferred from M1/M2 completion:

| ID | Decision |
| --- | --- |
| P-01 | Select contact onboarding and the exact two-Box decomposition/source, external wiring instead of director execution, and no changes to current grammar/spec/runtime semantics. |
| P-02 | Approve functional rules, email subset, ASCII normalization, failure priority, numeric bounds, consent/suppression, exact English/French text/escaping, and complete pre-execution corpus/oracle review. |
| P-03 | Approve tool-only rootless Podman isolation with host Pi, a single fail-closed container Bash transport, required preflight, resource limits, storage limitation, and the stated non-adversarial/worker-attestation threat boundary. If inadequate, stop for a revised design rather than add services or weaken controls. |
| P-04 | Approve provider/model/reasoning/tool versions, synthetic-data provider policy, two fresh sequential Pi contexts, budgets of two maximum episodes per Box, restricted feedback, and no repairs after integration freeze. Confirm availability and any monetary spending cap before execution. |
| P-05 | Approve the preregistered serious TypeScript baseline, fixed corpus/prompt equivalence, metrics/definitions, BoundScript-first order limitation, and descriptive evaluation plan before M3 execution; reserve actual baseline execution/product comparison for separate M6 authorization. |
| P-06 | Approve later preparation of the minimal experiment assets/transport/driver/runbook and separate execution assignment. Acceptance of 0020 alone does not authorize building them, launching sessions, or marking M3 In Progress/Completed. |

No new public contract authority, provider integration, agent framework, orchestration service, scheduler, job manager, dependency language, hash manifest, evidence database, candidate promotion, M4 enforcement, M5 evolution, or M6 comparison execution is proposed here.

## 12. Acceptance criteria and delivery boundaries

### Assignment 0020 — design acceptance

| ID | Required evidence for review |
| --- | --- |
| D-01 | Proposed design cites accepted direction, current roadmap/workflow, inspected M1/M2 code/acceptance records, and distinguishes existing capabilities from future experiment tooling. Only this Markdown document is delivered; M3 stays Planned. |
| D-02 | Concrete nontrivial two-Box source uses current language; responsibilities, numbered functional requirements, public examples, frozen corpus coverage, and unchanged predefined integration are specified without manually duplicated BoundScript-arm public interfaces. |
| D-03 | Explicit M2 inputs/selection/package delivery and two fresh Pi contexts prevent sharing implementation context; fixed entrypoint, allowed dependencies/files, and session/resource configuration are documented. |
| D-04 | Isolation proposal specifies real OS boundary, mounts, credential/test separation, fail-closed tool routing, trusted controller/export duties, resource limits, readiness tests, and honest enforcement/attestation limitations. No untrusted code or pilot agents execute during design delivery. |
| D-05 | Independent strict compilation, named-export/ESM loading, strict portable decoding, M1 semantics reuse inside isolation, external behavioral assertions, and frozen integration with no repairs are specified; failure classes stay distinct. |
| D-06 | Reproducible pre-execution freeze, attempt/feedback budgets, clarification/architecture/infrastructure handling, negative outcomes, and manual event/metric definitions are explicit and not an orchestration/evidence framework. |
| D-07 | Conventional TypeScript baseline and evaluation protocol are defined before execution with fairness controls, setup costs, order/sample limitations, and no comparison run or M6 completion claim. |
| D-08 | P-01–P-06, limitations, future pilot success gate, acceptance/implementation authorization boundaries, and documentation verification are clear. Product Owner acceptance is required before proceeding. |

### Gate for a later implementation/execution assignment

Require separate authorization to prepare actual approved assets and execute the pilot. Before execution: approve baseline/evaluation protocol and freeze concrete equivalent assets, source/tasks/policy/tests/wiring/prompts/tool versions; validate whole source and byte-identical M2 derivations; prove isolation preflight; exercise trusted harness controls; and pass repository `npm run check`, build, existing Box demos, Hello World CLI, and canonical export comparison. Untrusted candidate import/execution must remain exclusively inside the approved evaluation boundary, not a normal repository regression.

Actual pilot evidence must include both independent session/snapshot histories, all attempted submissions/failures/interventions/budgets, independent compile/M1/functional results, unchanged frozen-pair integration outcomes, protected-context observations, and unverified properties. M3's exit gate requires both candidates to pass their independent checks and all prewritten integration assertions **without integration-time implementation edits, interface negotiation, architecture changes, or controller repair**. Report allowed pre-freeze revisions transparently; a failed/inconclusive experiment cannot be relabelled as satisfying that gate.

For **this design-only delivery**, check local Markdown links/anchors, balanced fences, required sections/status, proposed-source parsing/extraction with existing APIs only, and `git diff --check`. Do not create pilot source/task/test files, generate operational handoffs, build new isolation tooling, launch Pi sessions/containers, or execute baseline/candidates. Existing regression counts above are reference evidence, not new pilot test results. Report document commit, design verification, and pending P-01–P-06; wait for Product Owner review. Commit/push only this authorized design document to the current feature branch. No roadmap status or acceptance record changes are part of 0020 preparation.

### Design-delivery verification

- Local Markdown targets/anchors, balanced code fences, Proposed status, and D-01–D-08/P-01–P-06 coverage checks pass; whitespace is checked with `git diff --check`.
- The proposed source block parses and passes whole-system extraction for both selected Boxes using existing built APIs. Strict canonical serialization/decoding round-trips, shared intermediate descriptors, supported predicate targets, and example binding identities agree. This in-memory validation creates no pilot files or operational handoffs and executes no Box implementation.
- No Pi agent session or container was launched, no candidate/baseline was implemented or executed, and no production regression result is claimed for new pilot functionality. Only this Proposed design document is delivered; M3 remains Planned pending Product Owner review and separate authorization.
