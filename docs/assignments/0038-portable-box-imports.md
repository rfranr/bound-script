# 0038 — Portable Box Imports

Status: In Review

## Requirements and authorization

Implement portable Box imports: define a stable per-Box directory structure and reproduce it during generation and independent verification so generated relative TypeScript imports remain valid in consuming projects. Expose only the public contract and explicitly permitted dependencies to the generator, never peer implementations. Preserve exact verified implementation bytes during promotion; do not rewrite imports after verification. Keep NormalizeContact and RenderWelcome regressions passing.

Prefer ordinary relative imports; avoid aliases, custom resolution, registries and unnecessary abstractions. Keep changes minimal and compatible with future hierarchical composition. Follow the development workflow and report structure, changes and test evidence. No commits or pushes are authorized.

## Implementation notes / evidence

**Correction:** Assignment [0039](0039-remove-contract-promotion-ownership.md)
removes the contract-promotion responsibility introduced in this delivery. The
contract is consumer-owned input; only the verified implementation is promoted.
The evidence below records the original 0038 delivery, not the corrected ownership
policy. Current integration places the implementation beside the consumer's
existing contract; the generator does not distribute contracts.

Implemented for the two current native Box workflows. Each Box has sibling `contract.ts` and implementation source; both sandboxes reproduce that layout under `/implementation/`. Generated type imports use `./contract`. Existing promoted implementation filenames remain unchanged, with a sibling public contract copied during promotion. Consumers can relocate the pair into nested directories. Historical baseline workflows/artifacts remain regression references, unchanged.

The generation helper optionally mounts only the public contract read-only beside the empty candidate slot. Native prompts require relative imports; the trusted compiler rejects non-relative module specifiers and nonliteral dynamic imports. Existing ordinary TypeScript resolution validates relative imports. No aliases, registry, peer implementation exposure, import rewriting or custom resolution were added. Source and contract hashes bind promotion to verified inputs. This does not claim universal hostile-program dependency enforcement or implement hierarchical composition. Current public contracts retain their existing type-only Typia tags dependency for consumer type checking.

## Verification evidence

- `BOUNDSCRIPT_RUNTIME=podman npm run check`: passed. Python suites: 55 tests total, six opt-in skips; both trusted validator suites passed (three tests each); public-contract composition compiled; baseline Greeting, NormalizeContact (20 cases), RenderWelcome (81 cases) and integration (20 cases) passed.
- Fresh `BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/native-typescript-contracts/generate.py`: generation isolation, scan, separate offline verification and unchanged promotion passed. Three validator tests, 20 examples and five properties passed. Source SHA-256: `63719cce541c316e0a20aae3e67528aa5851079f7fead2c54d9598a7568f5583`.
- Fresh `BOUNDSCRIPT_RUNTIME=podman python3 -B experiments/render-welcome-native/generate.py`: same complete lifecycle passed. Three validator tests, six examples and one property passed. Source SHA-256: `577f6d37a8745fc16fd59a3be89838e20c700f8948a0233293ea16d4bdee1892`.
- Both freshly promoted source/contract pairs copied into separate nested consumer directories compiled with strict ordinary NodeNext TypeScript resolution, with identical source hashes. Only the existing npm dependencies were provided; no BoundScript runtime was used.
- New real-compiler regressions cover both Box types, byte-identical relocation, absolute/sandbox-path rejection; mocked lifecycle regressions cover the read-only contract mount and promotion contents. No business tests were weakened.
- `git diff --check`: passed. An initial aggregate check hit a 240-second outer timeout near its final baseline phase; rerunning with a 600-second allowance passed completely. No containers remained after the interrupted run.

Generated artifacts remain ignored and excluded from version control. Following delivery, the Product Owner authorized a local commit; pushing remains unauthorized. Acceptance remains with the Product Owner.
