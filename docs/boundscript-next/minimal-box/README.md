# One-Box boundary experiment

Self-contained experiment on `experiment/boundscript-next`; no DSL/compiler/runtime/pilot changes. Uses the existing locally cached, digest-pinned Node Docker image and repository TypeScript installation. No framework, model calls, image build, downloads, or dependency installation.

## Run

From the repository root, with Python 3, Node, existing `node_modules`, and Docker daemon access:

```bash
python3 docs/boundscript-next/minimal-box/verify.py
git diff --check
docker ps -a --filter name=boundscript-minimal- --format '{{.Names}}'
```

Do not run Python with `-O`: verification uses assertions. The script refuses other branches. All subprocess commands and flags are explicit in `verify.py`; temporary paths, container name, uid/gid and host-listener port are selected per run.

The native contract is `contract.ts`; `slugger.ts` is its one authorized dependency contract. `task.md` describes the task. `implementation/greet.ts` is a hand-authored witness, **not an agent-generated result**. Its type-only import resolves to the authorized contract inside the sandbox. The dependency implementation is injected only for the behavior check.

## Isolation and verification

The external Python verifier creates a disposable workspace and mounts exactly:

- `/inputs/task.md`, `/inputs/contract.ts`, `/inputs/slugger.ts`: read-only individual files;
- `/implementation`: writable disposable copy of the witness implementation.

Docker uses `--network none --read-only --cap-drop ALL --security-opt no-new-privileges`, a non-root uid/gid, 128 MiB memory/swap limit, one CPU, and 32-process limit. No host environment is forwarded. No repository, credentials, host directory containing the inputs, verification script, tests, or Docker socket is mounted. The base image supplies Node and ordinary OS utilities; these are also visible, not just the task files. Kernel-provided pseudo-filesystems and device facilities exist; `/implementation` is the only writable **host-backed** mount.

The verifier inspects the effective container configuration, sends fixed action probes over stdin, and receives observations. Expectations, assertions and host sentinel hashes remain outside the container. Behavioral invocation likewise returns data for external assertions; no test suite or oracle is copied into the container. Node executes the candidate only inside Docker. The trusted host TypeScript compiler performs a strict, no-emit type check without executing candidate code:

```bash
node <repository>/node_modules/typescript/lib/tsc.js --noEmit --strict --target es2022 --module nodenext --allowImportingTsExtensions <temporary-workspace>/implementation/greet.ts
```

Container and workspace are removed on ordinary completion/failure. An external interruption such as SIGKILL can require manual cleanup.

## Observed final run

`python3 docs/boundscript-next/minimal-box/verify.py` exited **0**:

| Check | Observation |
| --- | --- |
| Authorized inputs / submission | All three exact contents readable; write confirmed externally |
| Host sentinel read / write | `ENOENT` / `ENOENT`; host hash unchanged |
| Protected task write / root write | `EROFS` / `EROFS` |
| Repository / Docker socket read | `ENOENT` / `ENOENT` |
| Container `/root/.ssh/id_rsa` read | `EACCES`; no host credentials mounted |
| Symlink to host sentinel: read / write | `ENOENT` / `ENOENT` |
| Symlink to protected task: write | `EROFS`; input hashes unchanged |
| Host loopback listener (`127.0.0.1:59465`) | `ECONNREFUSED`; host received no connection |
| Numeric external address (`1.1.1.1:443`) | `ENETUNREACH`, not merely timeout |
| TypeScript contract | Strict no-emit check passed |
| Behavior / dependency | Three cases passed; injected dependency observed once per case |

`git diff --check` exited **0**. Container listing was empty after cleanup. Development runs also passed the access probes; the final version keeps all assertions outside the container.

## Scope of the evidence

This demonstrates authorized access and concrete blocked attempts under an inspected Docker configuration. It does not prove resistance to every possible escape. Docker shares the host kernel; trust includes Docker, its runtime, the image, Node, TypeScript and the external verifier. No actual autonomous agent, hostile-kernel exploit, DNS/IPv6 matrix, or production deployment was tested.

The witness is known code. Candidate-returned JSON is not security attestation: malicious JavaScript could fabricate behavior observations or tamper with its own process. The verifier's files and authority remain outside, but this tiny protocol does not establish arbitrary hostile-program correctness. Container-side probes are fixed actions run before candidate import, not candidate self-reports.

Dependency-interface exposure is restricted; use of built-in Node APIs is **not** denied by an import checker. The dependency call is observed for three cases, not proven universally. Writable submissions must never be promoted blindly: they can contain hostile symlinks. Neither sandboxing nor passing these finite checks establishes correctness or preserves restrictions after deployment.
