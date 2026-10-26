# Real Pi generation — stopped at the credential boundary

No agent generation was launched. `implementation/greet.ts`, contracts, task,
acceptance criteria, verifier and negative checks remain unchanged. No provider
call, credential read, installation, network-policy change, or host-side fallback
was attempted.

## Findings from the existing installation

- Pi is installed on the host at version 1.4.0. Current nonsecret session metadata
  names `openai-codex/gpt-6.1-sol`, reasoning `medium`; this does not establish the
  contents or actual source of its credentials.
- The existing minimal-box container has `--network none` and no provider broker.
  Its cached Node image does not contain the installed host Pi package.
- Neither `sbx` nor `openshell` is in PATH. `docker sandbox --help` displays only
  Docker's top-level command help, not an available Sandboxes integration.
- Installed Pi `docs/containerization.md` documents plain Docker by passing
  credentials into the container, managed credential substitution through Docker
  Sandboxes, inference routing through OpenShell, and host-Pi/tool-only Gondolin.
  Plain Docker credential passing violates this request; host-Pi/tool isolation
  also violates the explicit requirement to run the agent inside isolation.
- Installed pi-ai `dist/api/openai-codex-responses.js` parses an account claim from
  a JWT before transport and sets bearer/account headers. A generic opaque dummy
  credential is therefore not a drop-in replacement for this provider. No actual
  credential was opened or resolved to inspect this behavior.

There is **no established credential-safe provider route in this existing setup**.
This is not a claim that such a route is impossible. It requires an externally
managed, fixed-upstream inference/credential broker compatible with Pi, reachable
through a narrowly permitted channel, with no credentials returned to the guest.
It must not expose a general host proxy or unrestricted egress. No such service
was installed/configured or custom proxy built for this attempt. Do not substitute
a token mount, broader network access, host Pi, or a silent provider switch.

## Commands and results

Read-only checks (no secrets):

```bash
git status --short
git branch --show-current
command -v pi
for tool in sbx openshell; do command -v "$tool" || true; done
docker sandbox --help
```

There is **no reproduction command for a successful isolated agent generation**:
that step is blocked, and no generated implementation exists to verify.

The unchanged experiment was rerun:

```bash
python3 docs/boundscript-next/minimal-box/verify.py
```

Exit 0: authorized input reads/submission write, all ten forbidden file/write/
symlink probes, network denial, native TypeScript check, and three behavior cases
passed. Host-loopback port 44583 returned `ECONNREFUSED`; external `1.1.1.1:443`
returned `ENETUNREACH`. Input/sentinel hashes were unchanged and cleanup succeeded.
These results apply only to the existing **hand-written witness**, not an agent.

No agent had access to anything because none was started. The unchanged test
container saw the three authorized input files, writable disposable implementation,
base-image tools and OS pseudo-filesystems; no repository, verifier, tests, host
credentials or Docker socket was mounted. Existing shared-kernel and finite-test
limitations still apply. A future model connection additionally authorizes prompt
and tool-output transmission and metered calls; an upstream-only broker is still
an accessible capability, not proof against abuse of inference or fabricated
candidate observations.
