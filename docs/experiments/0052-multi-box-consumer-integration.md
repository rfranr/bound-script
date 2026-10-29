# 0052 — Multi-Box Consumer Integration

**Status:** Completed — functional experiment  
**Type:** Integration experiment  
**Date:** 2026-10-29  
**Prerequisites:** 0050 — Manual Candidate Promotion; 0051 — Portable Box Consumption

## 1. Objective

Demonstrate that two independently generated, verified and promoted BoundScript Boxes can be consumed and composed by an external TypeScript application.

The experiment evaluates the portability and composability of published Box source trees without requiring BoundScript, Pi, Docker or the independent verifier at application runtime.

## 2. Boxes under test

| Box | Published version | Responsibility |
|---|---|---|
| `plan-fulfillment-native` | `0001` | Allocate stock lots to order demand |
| `evaluate-rules-native` | `0001` | Evaluate declarative business rules |

Both versions were promoted explicitly through the BoundScript workflow.

The consumer receives the published source files and their corresponding consumer-owned TypeScript contracts.

No Box implementation changes were required for integration.

## 3. Independent consumer

A separate project was created alongside the BoundScript repository:

```text
boundscript-consumer/
├── package.json
├── tsconfig.json
└── src/
    ├── main.ts
    ├── fulfillment/
    │   ├── implementation.ts
    │   ├── validation.ts
    │   ├── allocation.ts
    │   └── contract.ts
    └── evaluate-rules/
        ├── implementation.ts
        └── contract.ts
```

The consumer uses Node.js and TypeScript tooling, with `tsx` for execution. `typia` is installed for TypeScript contract compatibility.

No BoundScript runtime dependency is installed.

## 4. Execution procedure

### 4.1 Create the standalone consumer

From the BoundScript repository:

```bash
mkdir -p ../boundscript-consumer/src/fulfillment

cp -a experiments/plan-fulfillment-native/versions/0001/source/. \
  ../boundscript-consumer/src/fulfillment/

cp experiments/plan-fulfillment-native/src/contract.ts \
  ../boundscript-consumer/src/fulfillment/contract.ts

cd ../boundscript-consumer

npm init -y
npm install -D typescript tsx typia
npm install -D @types/node
```

A standalone `tsconfig.json` and `src/main.ts` were created.

The consumer's TypeScript configuration was adjusted to include Node.js types after the initial compilation reported missing declarations for `node:assert/strict`.

Compilation was subsequently executed using:

```bash
npx tsc --noEmit
```

### 4.2 Verify source preservation

The published fulfillment source was compared against the consumer copy:

```bash
diff -qr \
  ../bound-script/experiments/plan-fulfillment-native/versions/0001/source \
  src/fulfillment \
  --exclude=contract.ts
```

This command checks the copied implementation files without comparing the separately supplied consumer contract.

The shell history confirms execution of the comparison. Its exit status and output were not captured in the retained evidence.

### 4.3 Promote the second Box

From the BoundScript repository:

```bash
BOUNDSCRIPT_RUNTIME=docker \
python3 -B experiments/native_cli.py promote evaluate-rules \
  --candidate e9cc9f7950a646d8b460928c535c4b20
```

The promoted version was then copied into the standalone consumer:

```bash
mkdir -p ../boundscript-consumer/src/evaluate-rules

cp -a experiments/evaluate-rules-native/versions/0001/source/. \
  ../boundscript-consumer/src/evaluate-rules/

cp experiments/evaluate-rules-native/src/contract.ts \
  ../boundscript-consumer/src/evaluate-rules/contract.ts
```

The experiment's execution subsequently succeeded using the copied EvaluateRules implementation.

## 5. Application-level composition

The consumer imports the two independent public entry points:

```ts
import { evaluateRules } from './evaluate-rules/implementation';
import { planFulfillment } from './fulfillment/implementation';
```

The application evaluates business eligibility before invoking stock allocation.

The integration logic is consumer-owned:

1. Evaluate customer and order eligibility using `evaluateRules`.
2. Inspect the evaluation result.
3. If the order is eligible, invoke `planFulfillment`.
4. Assert the expected stock allocation results.

Neither Box imports or invokes the other directly.

The consumer controls the execution flow and owns the integration policy.

## 6. Observed results

The standalone consumer was executed using:

```bash
npx tsx src/main.ts
```

Observed output:

```text
PASS: standalone consumer
{
  "ok": true,
  "allocations": [
    {
      "orderId": "ORDER-001",
      "lineId": "LINE-001",
      "lotId": "LOT-001",
      "warehouse": "BCN",
      "quantity": 3
    }
  ],
  "shortages": [],
  "remaining": [
    {
      "lotId": "LOT-001",
      "quantity": 7
    }
  ]
}
PASS: rules approved fulfillment
```

The results demonstrate that:

- The EvaluateRules execution approved the test scenario.
- The consumer successfully invoked PlanFulfillment.
- Three units were allocated from `LOT-001`.
- Seven units remained available.
- No shortage was produced.
- Both Boxes executed together in the standalone Node.js application.

## 7. Acceptance assessment

| Criterion | Result |
|---|---|
| Independent consumer project | PASS |
| Two Boxes usable in the same application | PASS |
| Application-owned coordination | PASS |
| Successful standalone execution | PASS |
| Expected fulfillment behavior | PASS |
| No BoundScript or Pi required at runtime | PASS |
| No changes required to Box implementations | PASS |
| TypeScript compilation | Executed; final successful execution confirmed |
| Exact source integrity | Comparison executed; final result not recorded |
| Runtime compatibility across other environments | Not tested |

The functional multi-Box integration objective is achieved.

The integrity comparison and final compiler exit status should be retained separately if strict evidence completeness is required.

## 8. Architectural observations

### 8.1 Boxes remain independently developed

EvaluateRules and PlanFulfillment have separate contracts, tasks, verification suites and published source trees.

Their integration does not require a shared internal architecture.

### 8.2 Composition belongs to the consumer

The consumer decides when and how each Box is invoked.

BoundScript does not need to provide an application runtime, dependency-injection container or workflow engine to support this form of composition.

### 8.3 Published source can be consumed directly

The experiment uses ordinary TypeScript imports from copied source files.

The consumer does not require the generation infrastructure, independent verifier or model used to produce the implementation.

### 8.4 Integration remains manual

The experiment involved explicit copying of source and contracts, local TypeScript configuration and application-level imports.

It does not establish automatic dependency management, package distribution, compatibility guarantees or deployment support.

## 9. Limitations

This experiment demonstrates successful composition for two specific published Boxes and one standalone TypeScript consumer.

It does not establish:

- Universal Box portability.
- Automated installation, upgrades or rollback.
- Cross-language interoperability.
- Compatibility across different JavaScript module systems.
- Security guarantees for arbitrary generated code at application runtime.
- Correctness beyond the verified contracts and executed integration scenario.

Published source integrity and contract compatibility remain separate concerns from successful execution.

## 10. Conclusion

**0052 — Functional integration: PASS**

Two independently generated BoundScript Boxes were successfully composed and executed by an external TypeScript application.

The experiment provides evidence that BoundScript can act as a development-time construction, verification and publication mechanism without becoming a mandatory application runtime.

The next architectural discussion should focus on whether BoundScript requires a reusable delivery/integration mechanism, rather than assuming that a runtime orchestration framework is necessary.

No core migration or new integration framework is authorized by this experiment.