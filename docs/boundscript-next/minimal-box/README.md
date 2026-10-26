# One-Box boundary experiment

Self-contained experiment on `experiment/boundscript-next`; no DSL/compiler/runtime/pilot changes. Uses the existing locally cached, digest-pinned Node Docker image, installed Pi 1.4.0, and repository TypeScript installation. No framework, broker, packages, image builds, or downloads.

## Reproduce

From the repository root, as the existing nonroot Pi user, with Python 3, Docker daemon access, existing repository dependencies, and the existing Pi installation/authentication at the paths in `generate.py`:

```bash
# Makes real provider calls and replaces greet.ts ONLY after successful verification.
python3 docs/boundscript-next/minimal-box/generate.py

# Independently recheck the saved implementation without model calls or credentials.
python3 docs/boundscript-next/minimal-box/verify.py

git diff --check
docker ps -a --filter name=boundscript-greeting-agent- --format '{{.Names}}'
docker ps -a --filter name=boundscript-minimal- --format '{{.Names}}'
```

Do not use Python `-O`: verification uses assertions. All commands/flags are explicit in the scripts; temporary paths, container names, uid/gid and host-listener port vary per run. Generation is nondeterministic and incurs provider usage; no superiority or reproducibility-of-output claim is made. The fixed prompt is in `generate.py`. The original task and contracts are unchanged.

`contract.ts` is the native Box contract; `slugger.ts` is its one authorized dependency contract. The checked-in `implementation/greet.ts` is now the **unmodified output of the successful real Pi run**, not the previous hand-written seed. Every generation starts with an empty implementation directory. The dependency implementation is injected only during independent verification.

## Generation boundary

Pi and its read/write/edit/bash tools run **inside** the container, using `openai-codex/gpt-6.1-sol`, reasoning `medium`. No host Pi generation or tool-forwarding substitute is used. Only these host-backed paths are mounted:

| Container path | Authority |
| --- | --- |
| `/inputs/task.md`, `/inputs/contract.ts`, `/inputs/slugger.ts` | Individual read-only files |
| `/implementation` | Fresh writable submission directory |
| `/opt/pi` | Installed Pi package/dependencies, read-only runtime tooling |
| `/run/host-auth.json` | Only existing host `auth.json`, read-only, explicitly authorized credential exception |

No repository, peer implementation, verification code, acceptance tests, host credential directory, Docker socket, or host settings/extensions/sessions are mounted. The base image supplies Node and OS utilities; kernel pseudo-filesystems/device facilities are also visible.

A private 64 MiB `/pi-state` tmpfs holds a container-local authentication copy and minimal settings. OAuth refresh can modify only that copy; the host authentication file is hashed before/after and checked unchanged. The tmpfs is writable **runtime state**, not part of the Box submission, and disappears with the container. Credentials remain readable to Pi/tools as explicitly accepted by the owner.

Docker uses a nonroot uid/gid, read-only root, all capabilities dropped, no-new-privileges, one CPU, 512 MiB memory/swap limit, and 64-process limit. Network is unrestricted Docker bridge networking, **not** host networking. Host services reachable over bridge networking are not protected by this experiment.

No host environment is forwarded. Pi disables sessions, extensions, MCP, skills, templates, themes, context discovery, project approval, automatic retries, compaction, cache warming, and automatic catalog/update activity. `--offline` disables Pi's automatic network activity, **not explicit inference requests**. It does not firewall agent tools.

Raw Pi JSON/stderr is captured only in memory and never printed, saved, or committed. Reporting retains only tool counts and an allowlisted read-path summary. Before promotion, a trusted in-container check rejects a submission containing literal credential string values from either original or refreshed auth; no credential values pass through that check's output. This is a precaution, not a general encoded-secret detector or exfiltration defense.

## Independent verification

The agent container is destroyed **before** verification. `verify.py` receives only the candidate source (optional positional path), copies it into a new credential-free, network-disabled container, and runs the existing acceptance checks. Expected results/assertions stay on the host. There are four Box mounts plus read-only TypeScript tooling; no verifier/test files are mounted.

The compiler now runs in the verification container so both absolute `/inputs/contract.ts` and relative contract imports resolve against the real authorized filesystem:

```bash
docker exec <verification-container> node /tools/typescript/lib/tsc.js --noEmit --strict --target es2022 --module nodenext --allowImportingTsExtensions /implementation/greet.ts
```

Contract, task, required behavior, dependency call expectations, and negative access checks were not relaxed. The source is never executed on the host. Promotion copies only a regular, size-bounded, verified `greet.ts`; raw events, session files, runtime state, and credentials are not copied.

## Actual runs

Two real Pi invocations occurred; neither received acceptance-test feedback or a revised business task:

1. **First attempt: failed verification.** Generation succeeded (3 reads, 1 write, 1 bash call), but used an absolute `/inputs/contract.ts` type import. The old host-side compiler could not resolve that container path (`TS2307`, then implicit-any diagnostics). Its temporary submission was discarded and never promoted. This exposed a verifier filesystem assumption, not evidence that the contract should change.
2. **Fresh second attempt: passed.** After moving the same compiler checks into the independent verification container, Pi again used 3 reads, 1 write, 1 bash call, no edits, and wrote only `greet.ts`. Its three `read` calls named exactly the authorized input files. The saved implementation uses a relative type import. It was not manually repaired.

For the successful generation command, exit **0**:

- Inspected generation mounts and fixed action probes: host sentinel, repository, tests and verifier absent (`ENOENT`); protected writes denied (`EROFS`); symlink host escape denied (`ENOENT`). These actions ran in the actual agent environment before generation, with assertions external.
- Generation inputs/sentinel and host authentication hashes unchanged; one regular submission file; credential literal scan passed.
- Independent strict TypeScript check passed.
- All three existing behavior cases passed, including exactly one injected dependency call with the trimmed name per case.
- All ten existing forbidden read/write/symlink checks passed.
- Offline verifier only: host listener `127.0.0.1:53381` returned `ECONNREFUSED`; `1.1.1.1:443` returned `ENETUNREACH`. These results **do not claim network denial during generation**.
- All containers and temporary workspaces removed. The host auth file was not changed.

A separate saved-source verification was also run; see command above. Provider billing was not independently measured. No raw transcript is retained for retrospective command-by-command audit.

## What this establishes—and does not

Observed generation used the three authorized read-tool paths and produced only the permitted source file; protected inputs remained unchanged and controlled filesystem escape attempts failed. This is concrete filesystem-boundary evidence, **not proof that the agent attempted every possible escape or never used Bash to inspect runtime state**. Bash was available, and its raw command/results are not retained. There is no comprehensive syscall/network audit.

The accepted credential exception is real: Pi/tools can read original and refreshed authentication and unrestricted networking permits exfiltration, arbitrary downloads, and access to reachable host/LAN services. Read-only credential mounts do not protect secrecy. No such exfiltration is established by these observations, but this setup does not prevent it. Only literal credential inclusion in the submitted source was checked.

Docker shares the host kernel; trust includes Docker/runtime, base image, Pi, Node, TypeScript and external verifier. Agent code can consume resources within configured limits. Writable runtime state and OS pseudo-filesystems are exceptions to “only implementation writes.” Ordinary completion/failure cleans up; SIGKILL can require manual cleanup.

Dependency-interface exposure is restricted, but there is no import allowlist or universal proof of dependency usage. Candidate-returned data can be fabricated by malicious code; external assertions do not turn this protocol into hostile-program attestation. Passing finite tests does not prove general correctness or preserve build-time restrictions after deployment.

The historical credential blocker in `agent-blocker.md` is superseded only by the owner's explicit authorization to expose `auth.json` and enable generation networking, not by a new security mechanism.
