# One Box, no framework

This is the existing Greeting Box experiment, relocated from
`docs/boundscript-next/minimal-box/`. It is the entire working implementation of
BoundScript Next—not a generic runner or a two-Box pilot.

## Responsibilities and files

| Responsibility | Working code / authority |
| --- | --- |
| Box definition | Human-owned `task.md`, native `contract.ts`, authorized dependency interface `slugger.ts` |
| Agent execution | `generate.py`: fresh, restricted Docker workspace; Pi with read/write/edit/bash tools |
| Independent verification | `verify.py`: separate offline, credential-free container; assertions and expected results outside it |
| Controlled promotion | `generate.py` saves only a regular, size-bounded `greet.ts` after verification succeeds |

`implementation/greet.ts` is the accepted artifact, produced by real Pi without
manual repair. The dependency is injected by the consumer; only its interface is
exposed to the agent. There is no artifact registry or actual multi-Box consumer
yet. Other languages could use their own native contracts/checks; only TypeScript
is implemented. No custom type system or application orchestration is needed.

## Run

From the repository root, on `experiment/boundscript-next`:

```bash
npm ci
npm test          # Saved artifact: no model calls, no credentials
npm run generate # Fresh Pi session, verification, then replace accepted greet.ts
```

Requires Linux, Python 3, Docker, Node 24.16+ and locally cached image
`node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205`.
Generation uses the existing Pi **1.4.0** installation and `~/.pi/agent/auth.json`;
its explicit installation path, model (`openai-codex/gpt-6.1-sol`), prompt and
commands are in `generate.py`. This is an environment-specific reference, not a
portable provider integration. Generation incurs provider usage. Do not use
Python `-O`; checks require assertions. Neither script pulls images or installs
packages. The host invokes Docker, but all model-directed tools run inside it.

## Actual authority

Generation mounts exactly three read-only Box inputs, the read-only installed Pi
runtime, the explicitly authorized read-only **auth.json file only**, and an empty
writable `/implementation`. No repository, peer implementation, test suite,
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

## Foundation validation

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

Two-Box integration, artifact distribution/provenance, credential brokerage,
egress restrictions, stronger hostile-code verification and additional languages
remain deliberately unimplemented. Application logic and dependency wiring stay
in ordinary TypeScript, not in BoundScript.
