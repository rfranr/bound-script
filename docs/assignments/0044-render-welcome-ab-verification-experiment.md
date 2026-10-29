# 0044 — RenderWelcome A/B Verification Experiment

Status: In Review
Type: Credential-free experiment — step 3 of approved design 0041
Depends on: 0043 (approved subject to final diff review)

## Authorization and requirements

Prepare two independent implementations of the existing RenderWelcome contract: A single-file and B multi-file with freely chosen internal organization. Verify both with the existing shared independent verifier and unchanged consumer contract/acceptance suites. Collect evidence of equivalent externally observable behavior, consumer-asset preservation, source integrity and legacy single-file compatibility.

Do not modify the verifier to make the experiment pass. Report discovered limitations for separate review. No model-backed generation, promotion, quarantine, unrelated infrastructure changes, commits or pushes. Use Docker explicitly for verification.

## Experiment plan

- Add one opt-in Box-owned experiment test. Manually specified candidate text is materialized only into fresh temporary directories outside the Box verification root; existing implementations/accepted artifacts are not replaced or used to derive candidates.
- A uses a single pure formatter; B uses a small module/class organization with cross-directory relative imports. Both expose only the existing public entry/export required by the consumer.
- Run separate CLI verifier processes for A file, A one-file tree, B tree and reorganized B tree, preserving the public entry when helpers move and acquire a test-like filename. Assert identical suite selection/counts and successful strict compilation, validators, examples, seeded property, isolation, integrity and cleanup.
- Include focused business negatives to demonstrate that the unchanged oracle rejects a missing public export, type-correct wrong result, call-history dependence and input mutation. Reuse existing infrastructure tests for bounds, unsafe entries, import closure, tampering and cleanup rather than copying those suites per Box.
- Compare full source inventories and consumer-input/accepted/quarantine state before and after each run. Persist only experiment code and review evidence, not temporary candidates or verifier receipts.

Delivery requires Product Owner review; never self-accept.

## Delivery and reproduction

Added `experiments/render-welcome-native/test_ab_experiment.py` and an opt-in reproduction section in that Box's README. Candidate source text is hand-specified in the experiment test, not produced through a generation workflow. Each execution materializes it in private temporary storage outside the oracle root and removes it at completion. No existing implementation was copied to prepare A/B or edited/replaced. The verifier and consumer criteria were not modified.

```sh
npm run build:welcome
BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_WELCOME_AB_TEST=1 \
  python3 -B -m unittest discover -s experiments/render-welcome-native -p test_ab_experiment.py -v
```

The opt-in flag is separate from normal unit/engine checks. A clean checkout needs installed pinned tooling and the cached Docker image, but does not need an accepted Welcome candidate to run the A/B experiment.

### Implementations

- **A:** 1 file, 155 bytes. A typed pure function directly uses a template literal; no helpers or shared implementation with B.
- **B:** 4 files, 690 bytes. The typed entry delegates to `presentation/message.ts`, which composes a short-lived `GreetingText` class from `text/greeting.ts` and a separate mailbox helper from `text/mailbox.ts`. The helpers use string-array joining, not A's formatter body. Imports cross directory boundaries using relative paths.
- **B reorganized:** 4 files, 720 bytes. Move the helper bodies unchanged to `internal/fragments/line.ts` and `internal/fragments/brackets.test.ts`; update only their imports in the presentation module. The public entry bytes are identical to B. No definition, contract, fixture, suite or verifier configuration changes accompany this reorganization.

The same existing RenderWelcome BoxDefinition is selected for every invocation. No helper filenames, directory layout or class names are supplied to the verifier as configuration; only the selected candidate file/tree is passed.

### Final experiment results

One opt-in unittest passed in approximately **55 seconds**, making eight separate CLI verifier-process calls with Docker explicitly selected. Every call ran with normal, non-DEBUG diagnostics and no generation credentials/model workflow.

| Candidate/control | CLI input | Observed result |
| --- | --- | --- |
| A | legacy file | PASS |
| A, identical bytes | one-file tree | PASS |
| B | four-file tree | PASS |
| B reorganized | four-file tree, test-like helper name | PASS |
| Missing public export | separate temporary tree | Expected `compilation` rejection |
| Type-correct wrong message | separate temporary tree | Expected `assertion` rejection |
| Call-history-dependent formatter | separate temporary tree | Expected `assertion` rejection |
| Input-mutating formatter | separate temporary tree | Expected `runtime` rejection on the existing frozen-input oracle |

Each positive result included strict TypeScript compilation, **3 validator tests**, **6 unchanged fixture examples**, and **1 unchanged property with seed 36 and 100 runs**. Each collected exactly the existing 3 validator and 7 acceptance/property results, including after the `.test.ts` helper appeared. Sandbox/security, protected-input integrity and cleanup phases passed. Negative controls returned nonzero, did not report verification success, retained their input in place until test cleanup, and did not enter quarantine.

Thus both organizations separately matched the same externally controlled expected messages, shape requirements, frozen-input behavior, phone independence and call-history/determinism observations. This is finite, repeatable evidence of equivalent externally observable behavior on the existing oracle—not a proof of equivalence for all programs/inputs or a new acceptance criterion.

### Source identity and integrity evidence

The experiment compared complete candidate membership, object kinds/modes and file SHA-256 values before/after every invocation, and again for all positive candidates after all controls. No submitted source changed and no report/cache/contract file was added. Verifier success also required its existing full staged-source/input integrity checks. All temporary caller-side candidate directories were removed after the experiment; these are test fixtures, not promoted assets.

| Source | SHA-256 before = after |
| --- | --- |
| A `implementation.ts` in both modes | `a48c7f68a46408e22051eff2b2e2a0c5f63cba9219dde65700046286c11f473d` |
| B and reorganized B `implementation.ts` | `934284857110ab75038f65363416e11bf5443a62a4459f790cc9964f7563283e` |
| B `presentation/message.ts` | `b92c54c6c12557db81b9b60b2d1a14ea5a6fa76871d37de0c8d92c90322c6106` |
| Reorganized B `presentation/message.ts` | `e5ac182057848ccab5a81a0876b7baab6603e02b516391b505f3ab85fdde9b89` |
| B `text/greeting.ts`, moved to `internal/fragments/line.ts` | `8eae2e7d60fc90eac5eb279ee386f76bc15219f227d1fd777d2dc77556118536` |
| B `text/mailbox.ts`, moved to `internal/fragments/brackets.test.ts` | `b047f0147935402b65f479ee2334102969a0a8d76ae42da60e16c08b5ebd2d56` |

The presentation module's different hash is intentional between B layouts because its internal import paths changed; each layout is individually unchanged by verification. A and B need not have equal content hashes to exhibit equal behavior.

### Consumer assets and unchanged verifier

All eight calls used definition fingerprint:

`8ffc3fc476a448f3e82624de1f51c081de32e51d51516bcccb56c5ffb52894d3`

The experiment checked all seven declared verification files plus `native_box.py`, `task.md`, `tsconfig.json` and `vitest.tooling.config.mts`: **11 consumer/input files**, unchanged after every call. Oracle file membership was also unchanged. Selected source hashes:

| Consumer asset | SHA-256 before = after |
| --- | --- |
| `src/contract.ts` | `9aa7e6284df40dd9d16ece65b87a88506494c5e1e876b7ea7b7b8cd10308fadb` |
| `acceptance.test.ts` | `25abc5da274f97a30d47332f7826da897224f14155c60aa5fbffe5e42c78d3bc` |
| `validators.test.ts` | `ac3f5c840ff7797872aa1d00367930a1c612d84f0d8439dc3aa1b59f83628dfa` |
| `fixtures/welcome-cases.json` | `7499c24954640a5a32331fcad5af4b0b4b1f28db4f237d7bb4656e4105936756` |

The test's compact consumer-file measurement was identical for all calls and after subsequent credential-free regressions:

`2f6d87a9e5232fc8496e000424ed4319f81d35e6d89e7193f7b33ed3b1db8b25`

Existing internal Python/JS/TS workflow files and the selection CLI were also hash-checked unchanged on every call; their compact measurement was:

`c9141a89fe40255b040cff3fbc3b96b9b94436cd889dd36bf91c78326ff2c523`

These measurements use SHA-256 of sorted compact JSON file-hash maps, solely as experiment evidence. They introduce no runtime artifact identity scheme, persisted verifier inventory or receipt protocol. The workflow under test remains the committed 0043 implementation (`9787a73`). Existing accepted/quarantine directory membership, kinds/modes and content hashes were checked unchanged on every call, without reproducing their contents in this report.

### Other credential-free checks

- `BOUNDSCRIPT_RUNTIME=docker BOUNDSCRIPT_NATIVE_ENGINE_TEST=1 PYTHONPATH=tests/internal python3 -B -m unittest test_source_tree test_tree_verification -v`: PASS, **21 tests**, including the real synthetic-tree engine check. Reuses the existing bounds, symlink/special-object, source/contract tampering, cleanup, import-closure, unused-helper type checks and security tests instead of copying infrastructure negatives into this Box.
- `BOUNDSCRIPT_RUNTIME=docker npm run check`: PASS. **64** shared Python tests (5 opt-in skips), **6** baseline workflow tests, **2** local Contact tests (1 opt-in skip), **3** local Welcome tests (2 opt-in skips, including this explicitly opt-in experiment), both **3-test** tooling suites, public-contract compilation and isolated baseline regressions.
- `BOUNDSCRIPT_RUNTIME=docker npm run test:welcome`: PASS against the pre-existing single-file accepted candidate, with the existing 3 validators, 6 examples, property, integrity and cleanup. No accepted source was repaired or regenerated.
- Whitespace checks pass. Git diff confirms no verifier, compiler, runtime, generator, BoxDefinition, native definition, dependency, consumer source/contract/fixture/acceptance-suite changes for 0044.

### Limitations and separate-review notes

- No new blocking verifier limitation was encountered and no verifier workaround was made. Freedom of organization remains bounded by the existing TypeScript profile: public `implementation.ts`, relative import closure, no candidate-owned contract, disjoint source/oracle roots and the existing count/size/path limits.
- This proves verification of manual fixture organizations, not autonomous agent design/generation, production installation, publication, general hostile-code safety or universal equivalence. Those claims remain outside scope.
- Existing documentation drift remains: the opening of `task.md` names `/inputs/contract.ts`, whereas the unchanged Box definition uses `/implementation/contract.ts` and the supported portable source import is `./contract`. The experiment used the existing definition/layout without changing the task, contract or verifier. Any task-wording correction requires separate review.

## Files and review state

Added this assignment/evidence record and `experiments/render-welcome-native/test_ab_experiment.py`; updated the Welcome README with reproduction instructions. Prior 0041/0043 records were updated only to reflect explicit authorizations/conditional approval.

No generation command, agent/provider invocation, promotion or experiment quarantine occurred. The Product Owner subsequently authorized a local commit; pushing remains unauthorized. The delivery remains In Review; commit authorization does not constitute acceptance of 0044.
