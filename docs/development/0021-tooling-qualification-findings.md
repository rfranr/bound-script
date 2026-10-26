# Assignment 0021 — Phase 1 tooling findings

**Assignment:** [0021 — Qualify Existing Pilot Tooling](../assignments/0021-qualify-existing-pilot-tooling.md), **Completed by Product Owner acceptance/conclusion**; qualification outcome remains **Inconclusive**.
**Phase:** Authorized documentation/source review and read-only environment inventory only.
**Outcome:** **Inconclusive for the exact current configuration; no mechanism is locally qualified.** The reviewed stock Pi kit does not supply its OpenAI Codex authentication path. Existing Gondolin tool isolation is provider-independent in principle, but neither examined example establishes all required protections unchanged. This is not proof that no existing tool can ever satisfy them.
**Milestone:** M3 remains **Planned**. No provider/model switch is proposed.

**Product Owner conclusion:** This phase-1 report is explicitly accepted as an **Inconclusive infrastructure investigation**, and Assignment 0021 is concluded **Completed** on that basis. No further OAuth proxy, Gondolin or Docker Sandboxes qualification is an M3 prerequisite. Its unknowns remain unknown, no runtime is qualified, and the further inquiry/setup proposals below are not authorized or needed for the bounded pilot. [Proposed 0023](../assignments/0023-prepare-and-freeze-independent-pilot-assets.md) is the assets-only next step; [0020's bounded design](../assignments/0020-design-independent-implementation-pilot.md#bounded-feasibility-amendment) still requires separate execution approval. Completion is an explicit scope conclusion, not automatic acceptance of unperformed checks.

## 1. Inventory and limits of observation

Read package metadata/shipped source, public upstream documentation, selected session metadata, executable locations/version banners, and filesystem existence/permission metadata only. Did not start Pi, connect to a runtime daemon, open credential/configuration contents, invoke an auth resolver, install/reconfigure anything, start a sandbox, make an authentication/refresh/inference probe, or implement experiment assets. Public documentation retrieval is not a provider compatibility test.

| Read-only observation | Finding / what it does not prove |
| --- | --- |
| Current session metadata | Provider `openai-codex`, model `gpt-6.1-sol`, reasoning `medium`. These identify the selected configuration, not independently verified upstream model availability or an authentication source. |
| Pi / Node / repository TypeScript | Installed Pi package 1.4.0; Node v24.16.0; TypeScript package 5.9.3. Pi version came from public package metadata, not a Pi startup. |
| Host | Linux 7.0.0-38-generic, x86_64. `/dev/kvm` exists and the current user has read/write access by a permission check; no device open or virtualization test was performed. |
| Runtime executables | Docker CLI 29.1.3, Podman 5.7.0, QEMU 10.2.1, bubblewrap 0.11.1 are present. No `sbx` executable in PATH. A Docker socket exists; the checked default Podman user socket does not. No daemon was contacted, so runtime readiness is unknown. |
| Pi configuration metadata | Default agent-directory selection; `auth.json` and `settings.json` exist. No `models.json` at the checked default user location. **None of their contents were opened.** This does not rule out other overrides/extensions or establish the active credential entry type. |
| Environment names only | No names matched the inspected OpenAI/Codex prefixes or common credential-suffix pattern. No credential-variable values were accessed/printed. This limited name scan does not certify a secret-free environment. |
| Gondolin | Pi ships an example extension declaring dependency `@earendil-works/gondolin` 0.12.0. No dependency installation at the checked default user-extension path or inside that shipped example was found. This is not an exhaustive inventory of every possible installation. |

**Current authentication method is not fully established within this permission boundary.** The built-in provider's supported mechanism is ChatGPT OAuth with a JWT bearer (Section 2). The selected provider, existing auth store, and lack of matched credential-variable names are consistent with that, but do not prove which credential entry/override this running session used. A nonsecret operator attestation is needed; no credential-value access is justified to close this gap. The browser-versus-device login choice is also not known; both shipped flows produce the same OAuth credential shape.

Even Pi's credential-metadata listing loads/parses the auth store internally, and `pi auth check` resolves authentication and can refresh by default. Neither was run, including `--no-refresh` or metadata-only-looking variants. Do not use credential-printing commands or inspect raw process arguments/session transcripts to infer this information.

## 2. Authentication compatibility: OpenAI is not enough

Static inspection of the **installed Pi 1.4.0 / pi-ai source** establishes the standard provider behavior, without resolving any real credential:

- `providers/openai-codex.js` registers `openai-codex` with ChatGPT OAuth and default base URL `https://chatgpt.com/backend-api`. It is not the ordinary `openai` API-key provider.
- `auth/oauth/openai-codex.js` implements browser/device OAuth, stores `type`, `access`, `refresh`, `expires`, and `accountId`, and refreshes at `https://auth.openai.com/oauth/token`. `toAuth()` passes the access token as `apiKey`; this field name does **not** mean a normal OpenAI API key is interchangeable.
- `api/openai-codex-responses.js` calls `extractAccountId(apiKey)` **before** attempting network transport. It parses the JWT payload's `https://api.openai.com/auth` object claim and its `chatgpt_account_id` field. It builds `Authorization: Bearer ...` and `chatgpt-account-id` headers. Both initial request processing and OAuth refresh credential construction depend on the JWT account claim. The transport can use WebSocket or SSE.

Consequently, a generic opaque `proxy-managed`/Codex-kit sentinel cannot simply replace Pi's access token: Pi's local account extraction would fail before a host HTTP proxy could substitute a real credential. This is a source-based compatibility finding, **not a test with a token or a request**. A supported existing integration would need to account for Pi's native credential-file shape, local JWT/account handling, applicable refresh behavior, and transport support without returning real credentials to model-directed code. No such integration was demonstrated in the reviewed stock Pi kit.

There is no evidence here that `gpt-6.1-sol` itself is incompatible with isolation. The identified obstacle is authentication/presentation and protected workspace configuration, not a reason to change the selected model/provider. Actual custom-provider/endpoint overrides remain uninspected.

## 3. Supported options and compatibility evidence

### Preferred path: whole-Pi Docker Sandboxes

The [reviewed Pi kit specification][pi-spec] exposes an Anthropic credential binding and Anthropic/auth/npm egress, with Pi's Anthropic-shaped auth-file sentinels. It contains **no `openai-codex` binding, Pi-native OpenAI OAuth file mapping, or OpenAI/ChatGPT egress**. Its image is rolling `latest`. This stock configuration is not the required current OpenAI/Pi configuration as shipped.

Docker's [Codex documentation][docker-codex] and [Codex kit specification][codex-spec] do document host-side OpenAI/ChatGPT OAuth substitution. That is useful evidence that the existing runtime has an OpenAI OAuth facility, **not evidence of Pi compatibility**: the Codex kit configures the **Codex CLI**, its `~/.codex` files, and a provider route using an opaque sentinel with `requires_openai_auth = false`. Replacing Pi with that agent would change the approved experiment. Reusing its sentinel does not satisfy Pi's local JWT parsing.

The [generic credential capability][credential-spec] supports declarative credential files and host-side substitution/refresh, but a specification is not a release-matched, tested Pi/OpenAI integration. Its `passthrough` option would return the real token to the guest and fails our credential-separation requirement. Do not enable it, copy tokens, invent a JWT placeholder, or build an adapter/proxy as a qualification shortcut. An existing documented settings-only solution, if maintained upstream, needs explicit evidence before setup.

**Verdict:** Existing host-credential-isolated architecture is documented; stock Pi/OpenAI compatibility is **not supplied/proven by the reviewed kit**. Installing `sbx` now would not by itself close B-02. No whole-session runtime test was authorized or performed.

### One existing alternative: Pi on host, tools in Gondolin

Pi's installed `docs/containerization.md` documents keeping Pi and file-based credentials on the host and routing built-in tools/`!` commands through a Gondolin microVM. Because the model client remains unchanged on the host, this architecture can preserve the selected OpenAI provider/model and its host-side refresh path **without needing a guest-facing OAuth proxy**. It is a narrower, existing tool-only boundary, not proof of full pilot readiness.

Two versions must not be conflated:

| Examined existing example | Credential/context protection evidence | Remaining gap |
| --- | --- | --- |
| Pi 1.4.0 shipped `examples/extensions/gondolin/index.ts`, dependency 0.12.0 | All its registered built-in tools use `ensureVm()`; `user_bash` also uses it. File-based host credentials are not deliberately mounted. | `sanitizeEnv()` copies all string-valued environment entries to `vm.exec`; it is **not secret redaction**. The sole workspace mount is `new RealFSProvider(localCwd)` read-write. No separate read-only handoff, deny-egress, or pilot resource policy is configured by this example. |
| [Upstream Gondolin example pinned at `e0c4385`][gondolin-example] | Explicitly does **not** forward the host shell-tool environment; read/write/edit/bash are VM-backed. This is already-published upstream code, not a proposed custom extension. | Still mounts the whole cwd read-write; no documented settings-only split for protected handoff versus writable candidate is established by this example. Its `user_bash` handler returns without routing if `vm` is not ready, so no unconditional fail-closed claim for manual `!` commands. Version/API matching, egress, resources, VFS path protections, and lifecycle behavior are untested here. |

Neither example was imported, enabled, installed, modified, or executed. The current environment-name scan does not make wholesale future environment forwarding safe. The upstream environment fix is not evidence that the installed example already has it. A core library read-only-provider API alone would not establish that these unmodified examples expose the required settings; writing new VM/tool-mount code is outside this assignment. There may be existing supported configuration facilities beyond these examples, but none was established by this review.

**Verdict:** A documented provider-independent route for preserving host Pi credentials exists **conditionally**, but a ready-to-use, unchanged configuration meeting all essential protected-workspace/egress/lifecycle requirements remains **unverified**. It would depart from 0020's whole-session preference and needs Product Owner approval before any setup/probes. No recommendation to revive the rejected custom Bash transport.

### Not a solution to the authentication requirement

Plain Docker/Podman authoring with a real token in an environment variable/auth file would expose it to agent-executed code. Read-only credential mounts still permit reads. This does not qualify. Ordinary credential-free containers remain a documented evaluation boundary, but their host operation/access/resource controls were not tested. Only the preferred path and one existing alternative were investigated; this is not an exhaustive sandbox-platform survey.

## 4. Blocker disposition

| Blocker | Phase 1 evidence and disposition | Still required |
| --- | --- | --- |
| B-01 — existing runtime | Executables/versions and KVM permission metadata inventoried. `sbx` unavailable in PATH; Gondolin example exists but its dependency was not found at checked locations. **Partial inventory only.** | A selected supported existing mechanism/version and separately approved setup, only after compatibility is established. No runtime is locally qualified. |
| B-02 — exact OpenAI/Pi auth | Built-in OAuth/JWT behavior established from shipped source; generic Codex sentinel mismatch identified; actual active credential source/type not read. **Blocked on exact-method confirmation and a supported credential-safe integration.** | Nonsecret operator attestation; existing release-matched Pi/OpenAI configuration evidence, or an approved provider-independent host-Pi route. No token access or provider/model change. |
| B-03 — protected context / controls | Stock examples do not establish the necessary read-only/writable split plus egress/resources/cleanup/version controls for the proposed use. **Unverified; no runtime checks run.** | Documented supported settings first; later, separately approved generic probes for protected shares, no host/peer/test access, network and resource/whole-environment cleanup, and reproducible versions. No chmod/prompt/directory substitute for the real boundary. |

No runtime acceptance criterion is marked Pass. This report contributes documentation/inventory evidence to Q-01/Q-02/Q-04/Q-05; Q-03 local qualification and any auth/lifecycle probe remain unperformed. Q-06's no-pilot constraint is retained. At phase-1 delivery Assignment 0021 awaited review. It is now **Completed with accepted Inconclusive outcome**; no unperformed check is marked Pass. M3 stays **Planned**.

## 5. Original proposed next step — not executed, no longer an M3 prerequisite

**Do not install a runtime or authorize a model probe yet.** First:

1. Ask the Product Owner/operator to attest only nonsecret metadata from their existing knowledge: whether the current `openai-codex` entry uses built-in ChatGPT OAuth stored on the host, or a different credential source/override. No token/account ID, file contents, screenshots of auth stores, or login/refresh commands are requested. If that cannot be attested without further access, keep it unknown and request a distinct permission decision rather than reading credentials.
2. Request approval for **one narrow upstream compatibility inquiry** about the preferred existing Pi kit: is there a released, documented configuration supporting Pi's `openai-codex` OAuth/JWT/account handling, native auth file and refresh, and SSE/WebSocket path while keeping real credentials host-side? Provide only the public Pi version/provider/model labels and source-based constraints above. Ask for existing release/settings/tests, not a new plugin, kit implementation, fake token scheme, or proxy. **No issue/message has been posted.**

If the existing tool has no such supported path, return that finding for an explicit decision about the documented Gondolin alternative and its settings-only protection gaps; do not install it or silently change the accepted isolation preference. If meeting an essential requirement needs custom code, record it as outside the approved qualification scope. A later go/no-go setup plan must name the supported mechanism and exact nonsecret settings before any installation, reconfiguration, sandbox, credential resolution, or metered model request can be approved.

The scenario, functional requirements, frozen wiring/failure accounting, and TypeScript baseline are untouched. No M3 implementation, pilot agent execution, or M6 comparison is authorized by these findings.

## Evidence references

Local paths below are relative to the **public installed Pi package**, not user configuration. Files were read as source/metadata only, never imported to resolve authentication:

- Pi 1.4.0: `docs/providers.md`, `docs/containerization.md`, `dist/core/auth-storage.js` (`load`, `list`, `readLatestData`), and `examples/extensions/gondolin/{index.ts,package.json}`.
- Bundled dependency `node_modules/@earendil-works/pi-ai/dist/`: `providers/openai-codex.js`; `auth/oauth/openai-codex.js` (`credentialsFromToken`, refresh, `toAuth`); `api/openai-codex-responses.js` (request initialization, `extractAccountId`, `buildBaseCodexHeaders`). Public source establishes built-in behavior, not the uninspected running session's credential selection.
- Upstream source links below are pinned where practical. Generic runtime documentation/specification describes capability, not a local runtime test or a promise that every release implements it.

[pi-spec]: https://github.com/docker/sbx-kits-contrib/blob/1a2d27f0a1c87bfdc2e9af5c393aeaa7532ed5d9/pi/spec.yaml
[codex-spec]: https://github.com/docker/sbx-kits-contrib/blob/b5e2012b4419a518f7dc9d9ea35c05303b65e2d6/codex/spec.yaml
[docker-codex]: https://docs.docker.com/ai/sandboxes/agents/codex/
[credential-spec]: https://github.com/docker/sandbox-kit-spec/blob/main/docs/spec/capabilities/com.docker.sandbox/credential@1.md
[gondolin-example]: https://github.com/earendil-works/gondolin/blob/e0c4385f16faacaf53e500d45d7776e789d2d139/host/examples/pi-gondolin.ts
