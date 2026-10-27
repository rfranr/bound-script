# Private shared infrastructure

This checkout-local Python package owns host-side mechanics used by the fixed
experiment/Box entry points. It is not a public SDK, generic job runner or installable framework.
There are no new framework APIs, plugin hooks, manifests or orchestration layers.

| Module | Responsibility |
| --- | --- |
| `container_runtime.py` | Docker/Podman CLI adapters; exact mounts/environment and effective procfs/cgroup-v2 checks; pinned image, repository-relative TypeScript path and file hashing. |
| `box_definition.py` | Immutable explicit native Box inputs and test-file suites, complete suite-directory ownership checks, signature-consumer rendering and definition fingerprint; no registry, source inference or acceptance oracle. |
| `native_verifier.py` | Existing offline verification mechanics extracted without policy changes; explicit Box root/definition, no configuration discovery, generation or promotion. |
| `vitest.config.mts`, `compiler-diagnostics.mjs`, `diagnostic-reporter.mjs` | Unchanged trusted verifier tooling moved out of NormalizeContact; staged read-only for each independent verification. |
| `typescript_contract.py` | Deterministic TypeScript assignability-check text from contract/implementation module paths and named exports; no model, candidate access or acceptance criteria. |
| `agent_workspace.py` | Disposable Pi workspace, security probes, private credential state, bounded submission/literal scan, safe event summaries and cleanup before yielding a source. |

Dependency direction: experiment runners → internal mechanics. This package
imports only Python's standard library and sibling modules, never experiment
contracts, tests, verifiers or promotion code. It is not mounted into either Pi
or the offline verifier as a Python package. The three trusted JS/TS tooling
assets are explicitly staged read-only into the offline verifier, never into Pi.
Moving these mechanics adds no container authority.

Experiments still own their inputs, prompts/models/auth locations, verification
commands, semantic rules and promotion policies. Native quarantine is likewise
experiment-owned. The workspace helper does not verify, quarantine or promote.
Existing generation bridge networking and agent-readable auth remain prototype
exceptions; see [architecture](../docs/development/architecture.md).

Run from the repository root:

```sh
python3 -B -m unittest discover -s tests/internal -v
BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman \
  python3 -B -m unittest discover -s tests/internal -v
npm run test:unit # also each experiment's separate policy/diagnostic tests
```

The opt-in engine check exercises both generation and verification security
profiles without Pi, credentials or provider calls. It requires the cached pinned
image and effective cgroup-v2 limits. The fixed experiments' direct Python entry points
add the checkout root to the import path; no package installation or `PYTHONPATH`
configuration is required. No old-path compatibility shim remains under experiments.
