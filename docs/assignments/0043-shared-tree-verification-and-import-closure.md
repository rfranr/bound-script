# 0043 — Shared Tree Verification and Import Closure

Status: In Review
Type: Implementation — step 2 only
Depends on: approved revised design 0041 and 0042 (approved subject to final code review)

## Authorization and scope

The Product Owner authorized step 2: extend the existing independent verifier to execute staged multi-file TypeScript Boxes through the same compiler, contracts and acceptance tests. Preserve single-file compatibility and security guarantees; do not introduce a second verification engine.

Implement shared execution with read-only source and independent writable report/cache space, full source-set integrity, all-source strict compilation, import closure/containment and bounded helper diagnostics. Retain explicit selection and bounded staging from 0042. Keep existing contract/suite ownership, offline credential-free isolation, resource limits, failure classifications and cleanup.

Do not implement step 3 (RenderWelcome A/B experiment), multi-file generation, promotion or quarantine. Do not modify the generator or BoxDefinition. No model-backed generation, commits or pushes. Use Docker explicitly for real-engine checks. Existing uncommitted 0041/0042 work must remain intact.

## Implementation plan

- Forward explicit tree input into one shared verifier; keep file/default/baseline/fingerprint dispatch compatible.
- Compose staged source views with consumer-owned contracts mounted read-only; place compiler/Vitest reports and caches in separate writable work storage without changing runtime policy.
- Compile/check every submitted source, including unused helpers. Permit only supported literal relative resolutions within inventoried implementation sources or the exact authorized type-only consumer contract. Preserve trusted contract/tooling dependency access; deny candidate package/builtin/escaping/nonliteral imports and reference escapes.
- Extend bounded compiler locations to validated inventory members. Check full source membership/content and protected inputs before/after execution; retain cleanup on failures.
- Add focused mocked/compiler and opt-in Docker tests using synthetic infrastructure contracts/suites, not RenderWelcome A/B candidates. Retain existing single-file and sandbox assertions.

Delivery remains subject to Product Owner review; never mark this implementation accepted.

## Delivery

### Shared execution and import closure

- `boundscript_internal/native_cli.py` forwards explicit tree selection to `native_verifier.check(..., source_tree=True)`. The former staging-only rejection is removed; file/default/baseline/fingerprint paths retain their dispatch behavior and failures retain candidates in place.
- `native_verifier.py` uses bounded 0042 staging for trees, then one `_check` compiler/suite execution path for both layouts. Source and oracle roots must be disjoint. A private source view contains exact implementation bytes and the trusted contract view, is mounted read-only, and is checked for full path membership/content before and after execution. Original protected inputs remain hash-checked. Cleanup retains the staging lifetime across the entire verification call.
- Only `/verification-work` is a writable bind. Compiler/Vitest reports, Vite/module caches and tool HOME data use that area. Vitest 5 also writes its local API token via HOME; redirecting the trusted tool subprocess HOME is necessary for read-only sources. Container HOME/allowlists, runtime implementation, credentials policy, resource limits and timeouts are unchanged.
- The trusted compiler adapter receives the host-selected contract/source paths, compiles all submitted sources (including unused helpers), and applies module-policy checks to every candidate source. Literal relative import/export/type/dynamic-import/require edges must resolve directly to an inventoried file or the exact type-only consumer contract. Resolution cannot rely on package redirects or `.js`-to-`.ts` rewriting. Candidate reference directives cannot escape, use absolute sandbox paths or request external type/library sets. Trusted contract/tooling dependencies are not treated as candidate permissions.
- Compiler diagnostics accept only known source/contract/check paths and retain existing bounds/sanitization/classifications. No second engine, registry, artifact protocol or configuration fields were introduced.

### Tests and compatibility evidence

All real engine commands used `BOUNDSCRIPT_RUNTIME=docker` explicitly.

- `npm run check`: PASS. 64 shared Python tests (five opt-in skips), six baseline workflow tests, two local tests per native Box (one opt-in skip each), both three-test validator suites, public-contract compilation and isolated baseline regressions.
- `BOUNDSCRIPT_ENGINE_TEST=1 BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 python3 -B -m unittest discover -s tests/internal -v`: PASS, all 64 tests, no skips (approximately 187 seconds).
- New `tests/internal/test_tree_verification.py`: ten tests covering supported imports/type imports/re-exports/dynamic loads/internal references; forbidden/package/builtin/nonliteral/escaping/absolute-reference/alternate-resolution edges in unused helpers; unused-file type errors; inventory-bound helper diagnostics; read-only source versus writable work; source-set/contract tampering; invalid/overlapping inputs; failure cleanup; and real synthetic Docker verification.
- The real tree test reuses the existing synthetic identity contract and its unchanged Typia/example/property suites. A nested helper and an unused test-like filename verify successfully. Unauthorized unused imports, missing public export and a wrong helper type fail compilation before Vitest; a type-correct wrong result fails the unchanged assertion suite. No RenderWelcome A/B implementations were prepared.
- Updated the 0042 CLI dispatch test for shared execution while retaining all bounded staging tests. Existing native mount assertions now require only work storage to be writable and implementation storage to be read-only. Portability tests map the new report path without weakening relocation/byte/contract assertions.
- `npm run test:welcome`: PASS against the existing single-file candidate (three validators, six examples, one property, integrity/cleanup).
- `npm run test:native -- experiments/native-typescript-contracts/quarantine/failed-8ifizg1w/implementation.ts`: PASS against an existing single-file candidate (three validators, 20 examples, five properties, integrity/cleanup). No promotion.
- Existing local Welcome negative suite with `BOUNDSCRIPT_WELCOME_ENGINE_TEST=1`: PASS, two tests on rerun. One earlier run hit the unchanged 30-second compiler timeout on a negative; it correctly classified timeout and cleaned up. No timeout/resource changes were made. The rerun passed unchanged; treat this observed timing variability separately from deterministic test success.
- Whitespace checks pass; generator, BoxDefinition, workspace, container runtime, npm dependencies, native definitions and consumer contracts/fixtures/acceptance tests remain unchanged.

### Files

Modified for 0043: `boundscript_internal/native_cli.py`, `native_verifier.py`, `compiler-diagnostics.mjs`, `diagnostic-reporter.mjs`, `vitest.config.mts`; `tests/internal/test_native_workflow.py`, `test_portable_imports.py`, the pending 0042 `test_source_tree.py`; root/internal README and architecture documentation. Added `tests/internal/test_tree_verification.py` and this assignment record. Updated prior assignment records only to reflect explicit authorizations and the superseded staging-only CLI limitation. The pending 0041/0042 files remain uncommitted alongside this delivery.

### Boundaries and remaining limits

Tree verification concerns the bounded staged snapshot, not atomic capture of a live producer or an immutable published artifact. Default single-file accepted paths and generation/promotion/quarantine remain unchanged. There are no tree generation, promotion, quarantine, persisted inventories or verification receipts, and no step-3 RenderWelcome A/B experiment. A clean checkout may still lack an accepted Contact implementation; an explicit existing candidate was used for its positive regression.

Static module-policy checks are not universal JavaScript capability enforcement or hostile-code attestation; reflective loader tricks and malicious same-authority host/kernel actors remain outside the stated guarantee. Safe normal diagnostics are preserved; existing raw DEBUG behavior is not changed or presented as safe.

No model calls or pushes occurred. The Product Owner subsequently authorized a local commit of this delivery, including the pending 0041/0042 design and staging work. This does not constitute acceptance of 0043. Awaiting Product Owner review.
