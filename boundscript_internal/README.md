# Private shared infrastructure

This checkout-local Python package owns host-side mechanics used by the fixed
experiment/Box entry points. It is not a public SDK, generic job runner or installable framework.
There are no new framework APIs, plugin hooks, manifests or orchestration layers.

| Module | Responsibility |
| --- | --- |
| `container_runtime.py` | Docker/Podman CLI adapters; exact mounts/environment and effective procfs/cgroup-v2 checks; pinned image, repository-relative TypeScript path and file hashing. |
| `box_definition.py` | Immutable explicit native Box inputs and test-file suites, complete suite-directory ownership checks, signature-consumer rendering and definition fingerprint; no registry, source inference or acceptance oracle. |
| `native_verifier.py` | One offline verifier for file and explicitly selected tree inputs; read-only source views, separate writable work space, strict all-source import/type checks, unchanged declared suites and source/input integrity. No configuration discovery, generation or promotion. |
| `native_cli.py` | Shared verification entry point: file/tree/baseline arguments, fingerprint validation and failure reporting. Receives Box/root explicitly and delegates both layouts to the same verifier. |
| `source_tree.py` | Bounded, no-follow TypeScript tree staging with temporary snapshots and in-memory inventories; no execution, credentials, quarantine or promotion. |
| `native_generator.py` | Shared native prompt, preflight, independent verifier invocation, bounded scanned-source quarantine and unchanged implementation-only promotion. Reuses workspace/runtime lifecycle. |
| `vitest.config.mts`, `compiler-diagnostics.mjs`, `diagnostic-reporter.mjs` | Trusted verifier tooling staged read-only for independent verification; full source-set compilation/import closure and bounded reports to writable work storage. |
| `typescript_contract.py` | Deterministic TypeScript assignability-check text from contract/implementation module paths and named exports; no model, candidate access or acceptance criteria. |
| `agent_workspace.py` | Disposable Pi workspace, security probes, private credential state, bounded submission/literal scan, safe event summaries and cleanup before yielding a source. |

Dependency direction: experiment runners → internal mechanics. This package
imports only Python's standard library and sibling modules, never experiment
contracts, tests, verifiers or promotion code. It is not mounted into either Pi
or the offline verifier as a Python package. The three trusted JS/TS tooling
assets are explicitly staged read-only into the offline verifier, never into Pi.
Moving these mechanics adds no container authority.

Boxes still own their inputs, definitions and acceptance criteria. Native prompt,
model/auth defaults and quarantine/promotion mechanics are shared, preserving both
Boxes' behavior (including their different generation diagnostics). Explicit Box
selection and verifier commands live separately in `experiments/native_cli.py`;
no core workflow imports experiment configurations. A third Box can call the same
functions with its definition/root, extending only the fixed selector for CLI access.
No per-Box orchestration scripts or copied infrastructure tests are needed.
The workspace helper does not verify, quarantine or promote.
Existing generation bridge networking and agent-readable auth remain prototype
exceptions; see [architecture](../docs/development/architecture.md).

Run from the repository root:

```sh
python3 -B -m unittest discover -s tests/internal -v
BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_RUNTIME=podman \
  python3 -B -m unittest discover -s tests/internal -v
npm run test:unit # shared workflow/diagnostics plus each Box's local behavior checks
```

The opt-in engine check exercises both generation and verification security
profiles without Pi, credentials or provider calls. It requires the cached pinned
image and effective cgroup-v2 limits. The fixed experiments' direct Python entry points
add the checkout root to the import path; no package installation or `PYTHONPATH`
configuration is required. No old-path compatibility shim remains under experiments.
