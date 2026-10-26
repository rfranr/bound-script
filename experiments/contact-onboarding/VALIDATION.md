# 0023 — asset delivery / proposed freeze validation

**Outcome:** technical preparation delivered; **pending independent human/Product Owner asset and expected-value acceptance**. The Product Owner authorized 0023 implementation after documentation revision `0cfc96ce4e1b5f52ba395aed8ee4104fa4b9e3e6`. The Git commit containing this report identifies the proposed frozen source/tasks/tests/wiring/prompts/baseline. This is not automatic approval/currentness evidence. Owner-controlled assignments are not marked accepted by this delivery. **M3 stays Planned.** 0021 remains concluded Inconclusive/non-gating; 0022 execution remains deferred.

## Actual inventory / authority

| Paths under this directory | Role / review boundary |
| --- | --- |
| `system.bound`, `input.json` | Exact approved 0020 source/version-1 M2 bindings; unchanged two Boxes, fields, predicates and mandatory unused director. |
| `normalize-task.md`, `render-task.md`, `normalize-scope.md`, `render-scope.md`, `policy.md` | Actual human-owned requirements/examples/responsibilities/constraints; public interfaces derived only from source in the BoundScript arm. |
| `generation.md`, `events.md`, `README.md` | Common agent-neutral instructions, frozen failure/metric recording and external operator runbook. |
| `tests/normalize.json`, `tests/render.json`, `tests/integration.json`, `tests/coverage.md` | Literal complete expected records, fixed order and requirement-to-case mapping; 39/24/18 rows respectively. |
| `tests/tsconfig.json`, `tests/package.json`, `tests/consumer.ts`, `tests/build.mjs`, `tests/evaluate.mjs`, `tests/wiring.mjs` | Strict compile/export/ESM/import review; existing public codec/M1; independent behavioral checks and exact live-value integration. |
| `controls/normalize.ts`, `controls/render.ts`, `controls/private-tests.ts` | Trusted positive pair/private-check control only; never delivered as agent/baseline solutions. |
| `controls/compile-error.ts`, `controls/missing-export.ts`, `controls/load-error.ts`, `controls/malformed.ts`, `controls/predicate.ts`, `controls/behavior.ts`, `controls/lifecycle.mjs` | Compile/export/load/output/predicate/functional/timeout-descendant negatives. |
| `baseline/interfaces.d.ts`, `baseline/assertions.mjs`, `baseline/equivalence.ts`, `baseline/tsconfig.json`, `baseline/README.md` | Conventional manual authority/concrete expected-value assertions/preregistration/static signature checks. No baseline candidate. |
| `baseline/NormalizeContact/` and `baseline/RenderWelcome/`: each `README.md`, `task.md`, `scope.md`, `policy.md`, `generated/contract.d.ts`, `seed/implementation.ts` | Actual six-file bounded conventional contexts, same business intent/examples. Declarations are human-owned inputs despite matching generated-path convention; seeds only throw. |
| `prepare.mjs`, `evaluate.sh`, `check-controls.sh`, `check-regressions.sh` | Fixed ordinary preparation/container commands; no agent runner, adapter, service, new framework or infrastructure. |
| `VALIDATION.md` | This report, not a test oracle or approval engine. |

Generated M2 trees/publication links, staged libraries, build output, logs and fixture workspaces are temporary outside the repository and uncommitted. No source/contract/API/schema/rules/template/dependency changes in `packages/`, `tooling/`, root configuration or existing tests. No credential values or raw transcripts were inspected/copied/committed.

## Observed checks

| Check | Result |
| --- | --- |
| Source/binding match to accepted design; whole-source validation/extraction | PASS; both Boxes including exact predicates. Director not executed in consumption. |
| Strict codec canonical round-trip/shared NormalizedContact descriptors | PASS; spec version 1, derivation rules version 1; runtime/codec public APIs unchanged. |
| Two fresh M2 outputs | PASS; identical exact eight-file sets and bytes per Box; each packaged spec equals its selected extraction. Real-directory delivery copies exclude full architecture/tests/peer/reference/baseline code. These review renders are not approved operational releases. |
| Independent trusted positives | PASS; 39 normalizer and 24 renderer rows, each repeated with complete-output and unchanged-input assertions. Includes ASCII/Unicode/code-unit boundaries, error priority, direct inconsistent renderer records and exact templates/escaping. |
| Frozen trusted integration | PASS; 18 complete intermediate/final rows plus unchanged-live-object probe, predefined wiring, no adaptation or source edits. No pilot observation. |
| Strict NodeNext / named `implement` / declaration import erasure | PASS inside offline containers; positive sync controls; bad return TS2322 and missing named export TS2305 rejected. |
| Runtime negatives | PASS; compiled load exception, malformed output, predicate mismatch and shape-conforming wrong behavior fail distinctly. Direct M1 controls cover strict-decode rejection, missing/extra/symbol/nonfinite inputs with **zero invocation**, extra/symbol/nonfinite outputs, execution and inspection exceptions. Existing M1 evaluator reused, not copied. |
| Private-check route / consumption boundary | PASS; separately selected emitted private module only in a fresh offline container. Public codec/runtime work without compiler root/frontend/Langium; guarded forbidden imports fail; director execution prohibited. |
| Actual container settings | PASS inspected: network none, UID 1000, read-only root/bind inputs, 1 CPU/512 MiB/64 PIDs, dropped capabilities/no-new-privileges, no privileged/host PID/IPC mode/device mounts, no host credentials/socket/home/repository exposure. Private scratch; explicit nonsecret variables only. |
| Timeout/process cleanup | PASS; observed trusted parent/detached child, test-only 2 s timeout exits 124; full container removed; no evaluation containers remain. Normal build/suite deadlines remain 60 s each/130 s outer cleanup. Not an exhaustive OOM/kernel/escape qualification. |
| Baseline preparation | PASS static fields against extracted schemas and bidirectional signature compilation; same literal oracle data accepted by concrete conventional assertions, extra/symbol/nonfinite fields rejected. **No baseline candidate or comparison executed.** Format differences and future paired evaluation/comprehension plan preregistered. |
| Existing repository regressions | PASS **416 tests / 17 files**, typecheck and build, three Box demos with exact Hello World output, Hello World CLI, canonical Greeter export byte comparison. All executable trusted regression fixtures ran offline in a disposable container, not the host. `typecheck` + `test --maxWorkers=1` are the existing `check` components, not reduced test selection. |
| Documentation/source-only checks | PASS local links/anchors/fences, coverage IDs/counts, shell syntax, unchanged core/approved design, whitespace and review/execution gates. |

## Actual tools / preparation corrections

- Linux x86_64; host Node **v24.16.0** for trusted build/source preparation only; TypeScript **5.9.3**; Docker daemon **29.1.3**. BoundScript package versions `0.0.0`, public runtime/compiler API `0.1`; portable spec/rules version 1. Image `node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205` (official `node:24-bookworm-slim` resolution), **container Node v24.22.1**. No custom image/service/install or core integration needed; the public image was pulled during authorized preparation. Record this host/evaluator version difference, not the older foundation environment as a new result.
- An initial lifecycle observer command omitted Docker's required PID column; corrected to `pid,args` before freeze. Initial repository regression scratch was non-executable, preventing existing tool binaries; corrected **only the trusted regression scratch** to `exec`. A subsequent regression run had 413 passes/3 nested npm-build aborts at default thread pools; single Vitest worker and single libuv/V8 pool settings then produced 416/416 passes under unchanged 1 CPU/512 MiB/64 PID limits. No test assertion, business expectation or candidate evaluator limit was relaxed. Successful/failing temporary containers were removed, with no host-fixture fallback.
- Author coverage review added decomposed Unicode/one-character identity, French all-character/entity escaping and direct renderer exponent representation before final controls. All final literal expectations pass the trusted reference pair; this is **not independent human validation of product intent**. Full requirement/expected-value/baseline review remains the Product Owner gate.
- Actual human active preparation/review minutes and model-development token/cost allocation are **unknown**, not zero. Future event template records preparation/qualification/setup separately and includes it in total workflow effort. Generation profile remains the approved `openai-codex/gpt-6.1-sol`/medium; Pi was not started and effective tools/model availability are **not tested** in preparation. Verify them only at separately authorized execution. Spending ceiling is not specified; require owner approval before launch, not an invented value.

## Acceptance / unresolved limits

AC-01/02/04/05/06 technical assets/checks are delivered. AC-03's full literal corpus and requirement mapping are delivered, but **independent human oracle review remains pending**. AC-07/08: this is a review/freeze candidate, no automatic acceptance or milestone progress. Owner must accept the actual revision/baseline equivalence before separately approving revised execution.

No implementation agent, candidate generation episode, provider/auth probe, pilot, baseline candidate/comparison or M4 evidence/promotion system was launched. Existing native client/operator and container image/kernel remain trusted. Organizational workspaces/tool disabling do not OS-isolate the agent client; read-only tests preserve originals, not secrecy or shared-realm honesty. Finite tests/static import review do not prove arbitrary correctness/purity or hostile-result authenticity. These are residual experimental risks, not claimed qualifications. A passing trusted fixture pair is not M3's exit gate.
