# Minimal Box reference, no framework

This is the existing Greeting Box experiment, relocated from
`docs/boundscript-next/minimal-box/`, now extended with the fixed
[0018 two-Box exercise](two-boxes/README.md). No generic runner was introduced.

## Responsibilities and files

| Responsibility | Working code / authority |
| --- | --- |
| Box definition | Human-owned `task.md`, native `contract.ts`, authorized dependency interface `slugger.ts` |
| Agent execution | `generate.py`: fixed tasks/promotion; shared `../../boundscript_internal/agent_workspace.py`: fresh restricted Pi lifecycle and credential scan |
| Container mechanism/policy | `../../boundscript_internal/container_runtime.py`: Docker/Podman CLI adapters, shared fail-closed checks |
| Independent verification | `verify.py`: separate offline, credential-free container; assertions and expected results outside it |
| Controlled promotion | `generate.py` saves only a regular, size-bounded `greet.ts` after verification succeeds |

`implementation/greet.ts` is the accepted artifact, produced by real Pi without
manual repair. The dependency is injected by the consumer; only its interface is
exposed to the agent. The two-Box version uses ordinary `application.ts` to compose
accepted NormalizeContact and RenderWelcome sources. There is no artifact registry.
Other languages could use their own native contracts/checks; only TypeScript
is implemented. Current architecture and native workflow:
[architecture](../../docs/development/architecture.md),
[native contracts](../native-typescript-contracts/README.md). No custom type system or application orchestration is needed.

Shared mechanics are owned by the private [internal package](../../boundscript_internal/README.md),
not this experiment. Contracts, tasks, assertions and promotion choices stay here.
No compatibility shims or copied infrastructure remain in this directory.

## Run

From the repository root, on any branch (Python assertions must be enabled):

```bash
npm ci
npm test              # Saved Greeting + contact pair + integration; no model calls/credentials
npm run generate      # Fresh Pi session, verify, replace accepted greet.ts
npm run generate:pair # Fresh independent contact agents, verify each, then integrate
npm run test:pair     # Contact pair and integration only, no model calls
```

Requires Linux with verifiable cgroup v2 limits, Python 3, Docker or Podman,
Node 24.16+ and locally cached image
`node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205`.
Generation uses the existing Pi **1.4.0** installation and `~/.pi/agent/auth.json`;
its explicit installation path, model (`openai-codex/gpt-6.1-sol`), prompt and
commands are in `generate.py`. This is an environment-specific reference, not a
portable provider integration. Generation incurs provider usage. Do not use
Python `-O`; checks require assertions. Neither script pulls images or installs
packages. The host invokes the selected container CLI, but all model-directed
tools run inside the container.

### Runtime selection and security checks

Docker remains the default. Set `BOUNDSCRIPT_RUNTIME=podman` explicitly for Podman;
unknown values fail. Selection is inherited by fresh pair agents and independent
verifiers, without changing their arguments, contracts or acceptance cases:

```bash
BOUNDSCRIPT_RUNTIME=podman npm test
BOUNDSCRIPT_RUNTIME=podman npm run generate:pair # billable; explicitly authorized auth mount
python3 -B -m unittest discover -s experiments/minimal-box -v # baseline policies
python3 -B -m unittest discover -s tests/internal -v # shared mechanics
# Optional real-engine lifecycle/security smoke test, no Pi/auth/model calls:
BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman python3 -B -m unittest discover -s tests/internal -v
```

Run the same commands with `BOUNDSCRIPT_RUNTIME=docker` to check Docker. Each
engine needs the pinned image locally. Rootless engines need working cgroup
controller delegation (usually a systemd user session); warnings about ignored
limits are not considered success. Cgroup v1 or inaccessible/missing cgroup-v2
files are currently unsupported and fail closed. Python assertions must remain
enabled. SIGKILL still requires manual cleanup.

Docker uses `--tmpfs` with explicit `uid/gid`; Podman uses `--mount type=tmpfs`
with `U=true` to assign ownership to the configured nonroot user. Both require
64 MiB, mode 0700, nosuid/nodev/noexec. Podman's expanded `CapDrop` list is not
compared to Docker's literal `ALL`: all five actual process capability sets must
be zero, and `/proc/self/status` must report `NoNewPrivs=1`. Podman's extra
`container=podman` environment entry is allowed only by its adapter and must have
that exact value; arbitrary host environment entries remain forbidden.

Before credentials or candidate code are used, both adapters check exact bind
sources/destinations and read/write access, nonroot identity, read-only root,
nonprivileged mode and the requested network mode. A fixed Node probe then checks
actual identity, capability sets, no-new-privileges, root and bind mount flags,
cgroup memory/swap/CPU/PID limits, and (for generation) tmpfs ownership, mode,
size and mount flags. CLI inspection metadata alone is not evidence that limits
were enforced. Existing external filesystem/network/behavior checks are retained.
All create/start/probe/agent failures still pass through container cleanup, and
container CLI diagnostics are withheld.

**Historical adapter-only validation (not current host status):** eight credential-free unit tests passed
(the optional engine test is skipped by default). Real Podman creation and tmpfs
ownership/mode/size/flags were observed, and containers were removed after failed
security checks. Full engine smoke tests (generation and verifier profiles) fail
closed because this host exposes unlimited memory/swap/CPU and the wrong PID
limit, rather than enforcing the requested limits. The Podman `npm test` run
therefore stops at the resource check. Plain `npm test` also fails:
`docker` here is a Podman wrapper and injects `container=podman`, rejected by the
Docker adapter. No genuine Docker engine, successful end-to-end Podman acceptance
run, or real Pi generation was verified for this change. No credentials or model
calls were used. These failures were not bypassed. Later successful Podman baseline runs are
recorded in the [0030 report](../native-typescript-contracts/REPORT.md); current
consolidation results are in [0031](../../docs/development/consolidation-report.md).
Genuine Docker validation remains a separate requirement.

## Actual authority

Greeting generation mounts three read-only Box inputs; NormalizeContact gets only
its task/contract, while RenderWelcome additionally gets NormalizeContact's public
contract. All use the read-only installed Pi runtime, the explicitly authorized
read-only **auth.json file only**, and an empty writable `/implementation`. No repository, peer implementation, test suite,
verifier, host settings/extensions/sessions, credential directory or Docker
socket is mounted. Host environment variables are not forwarded.

Pi runs nonroot with read-only root, dropped capabilities, no-new-privileges,
one CPU, 512 MiB memory/swap and 64-process limit. Node/OS tooling and kernel
pseudo-filesystems are visible. `/pi-state` is a private 64 MiB writable tmpfs for
minimal settings and an auth copy: OAuth refresh cannot modify the host file.
Generation uses unrestricted **bridge networking**. Credential exposure and
networking are explicitly accepted prototype exceptions, not security guarantees.

Pi sessions, extensions, MCP, skills, templates, context discovery, automatic
retries, compaction and cache warming are disabled. Raw JSON/stderr stays only
in memory; the script reports tool counts/allowlisted paths, never raw diagnostics.
A literal credential-value scan runs before promotion; it cannot detect arbitrary
encoded secrets or prevent exfiltration. Original/refreshed credentials are never
copied to the submission or Git by the scripts. Host auth hashes are checked
unchanged.

Generation is destroyed before verification. A fresh network-disabled container
receives only the source and authorized inputs, plus read-only TypeScript tooling.
It has one CPU, **256 MiB** memory/swap and 32-process limit. At the old 128 MiB
setting the baseline compiler exited 137; the 256 MiB run passed. The exact kill
cause was not captured. This bounded increase changes resources, not acceptance
criteria. Type checking runs against
the actual container paths, supporting absolute and relative contract imports.

Checks cover authorized access, forbidden host reads/writes, protected writes,
symlink escapes, offline networking, strict TypeScript compilation, and three
behavior cases with exactly one dependency call using the trimmed name. The
agent cannot change those assertions or expected results. The saved artifact is
replaced only on success. Cleanup removes disposable containers/workspaces on
ordinary completion/failure; SIGKILL may require manual cleanup.

## Foundation validation (0017, before the two-Box extension)

- `npm ci --ignore-scripts --offline`: clean installation, TypeScript 5.9.3 only.
- `npm run check` and `npm test`: all saved-artifact checks passed.
- `npm run generate`: real containerized Pi made three authorized reads and one
  write (no Bash or edit calls), then passed independent verification and promotion.
  The saved source is that unmodified generated artifact.
- Temporary negative submissions were rejected: a native return-type mismatch
  (`TS2322`) and a type-correct but behaviorally wrong implementation (external
  assertion failure). Neither replaced the accepted artifact.
- Python syntax and Git whitespace checks passed; no experiment containers remained.

## Limits and deliberately deferred work

Docker shares the host kernel. The agent can read mounted credentials and use
networking to exfiltrate data, download public peer/repository code or reach
host/LAN services. Mount isolation is not global information isolation. Runtime
state and OS pseudo-filesystems are writable exceptions to Box-only writes.
There is no full Bash/syscall/network audit or universal escape proof.

The public dependency contract is the only peer material exposed, but there is
no transitive import allowlist. Candidate-returned data can be fabricated by
malicious code; external assertions are not hostile-program attestation. Finite
checks do not prove general correctness or deployed-runtime restrictions.

The fixed two-Box integration is now implemented; its [run report](two-boxes/REPORT.md)
records fresh sessions and unchanged artifact hashes. General boundary enforcement,
a reusable runner, artifact distribution/provenance, credential brokerage, egress
restrictions, stronger hostile-code verification and additional languages remain
unimplemented. Application logic and dependency wiring stay
in ordinary TypeScript, not in BoundScript.
