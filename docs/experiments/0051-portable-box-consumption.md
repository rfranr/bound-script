# 0051 — Portable Box Consumption Experiment

**Status:** Proposed — awaiting Product Owner approval  
**Type:** Integration experiment  
**Prerequisite:** Assignment 0050 — Manual Candidate Promotion

## 1. Goal

Demonstrate that a promoted, multi-file BoundScript Box can be consumed by an independent TypeScript application without requiring BoundScript, Pi, Docker or the verification infrastructure at application runtime.

The experiment validates the portability of the **exact promoted source**, not a rewritten or adapted implementation.

## 2. Subject

Use the existing promoted artifact:

`experiments/plan-fulfillment-native/versions/0001/`

The version was created through explicit human-authorized promotion after independent verification.

Its source tree contains:

- `implementation.ts` — public entry point.
- `validation.ts` — input validation.
- `allocation.ts` — stock allocation.

The consumer-owned `contract.ts` remains separate from the generated implementation.

Before execution, inspect the actual version manifest and source inventory. Do not assume additional metadata or runtime dependencies.

## 3. Experiment setup

Create a minimal standalone TypeScript consumer outside the BoundScript repository.

Illustrative layout:

```text
consumer/
├── package.json
├── tsconfig.json
└── src/
    ├── main.ts
    └── fulfillment/
        ├── implementation.ts
        ├── validation.ts
        ├── allocation.ts
        └── contract.ts
```

Copy the promoted source tree without modifying its contents.

Supply the original consumer-owned contract alongside the implementation, preserving the expected relative import relationship.

The standalone project may use TypeScript as a development dependency. It must not depend on BoundScript packages, internal helpers, verification tooling or Pi.

## 4. Procedure

1. Inspect the promoted version and its manifest.
2. Record the source inventory digest and contract hash.
3. Create the standalone consumer project.
4. Copy the complete promoted source tree, preserving all relative paths and exact bytes.
5. Supply the matching consumer-owned TypeScript contract.
6. Write a minimal `main.ts` that imports `planFulfillment`.
7. Compile the consumer with TypeScript.
8. Execute a representative fulfillment request.
9. Confirm the expected allocations, shortages and remaining quantities.
10. Confirm that the promoted source files remain unchanged.

The consumer may use its own integration code, but must not alter the Box implementation to make the experiment pass.

## 5. Acceptance criteria

The experiment passes only if:

- The standalone consumer compiles successfully.
- `planFulfillment` can be imported and executed.
- The observed behavior matches the declared functional contract for the selected integration scenario.
- Internal relative imports resolve without modification.
- Every promoted source file remains byte-identical.
- The consumer requires no BoundScript, Pi, Docker or verifier dependency at runtime.
- No generated implementation is repaired, rewritten or regenerated.
- The original published version remains unchanged.

A passing integration scenario demonstrates portability for this Box and environment. It does not prove portability for every Box or TypeScript configuration.

## 6. Failure classification

Record failures according to their cause:

- **Packaging:** missing files or incorrect source-tree layout.
- **Import resolution:** relative imports or module configuration cannot resolve.
- **Contract compatibility:** consumer and implementation public interfaces do not agree.
- **Compilation:** TypeScript rejects the integration.
- **Runtime:** execution fails in the standalone consumer.
- **Behavior:** observed output violates the selected expected scenario.
- **Integrity:** copied source differs from the published version.

Do not modify the promoted source, contract or acceptance criteria to hide a failure.

## 7. Evidence

Retain a concise experiment report containing:

- Published Box version and candidate identifier.
- Source inventory digest.
- Contract SHA-256.
- TypeScript and Node versions used by the consumer.
- Compilation and execution commands.
- PASS/FAIL for each acceptance criterion.
- Any limitations or integration changes needed outside the Box.
- Final conclusion supported by the observed evidence.

## 8. Out of scope

This experiment does not implement:

- Automatic installation or integration of Boxes.
- npm packaging or distribution.
- A Box registry.
- Dependency resolution across Boxes.
- Version upgrades or rollback.
- Automatic acceptance or promotion.
- Changes to the core architecture.
- Migration of the Python core to TypeScript.
- New generation, model calls or repair loops.

## 9. Product Owner decision

**Awaiting approval to execute.**

The initial deliverable is an independently runnable consumer and an evidence report.

Only after reviewing the experiment should the Product Owner decide whether BoundScript needs an explicit integration mechanism.

**Success condition:** a consumer can use the exact promoted multi-file Box as ordinary TypeScript source, independently of BoundScript.