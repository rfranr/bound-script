# PlanFulfillment native Box

Consumer-owned specification, fixtures and independent tests; **no implementation**. This is a challenging allocation/planning problem, not a request to generate a particular file structure. A correct one-file solution is acceptable.

## Setup

Copy directory to `experiments/plan-fulfillment-native/` in BoundScript. Register in `select_box()` in `experiments/native_cli.py`:

```python
if selection == 'plan-fulfillment':
    configuration = import_module('experiments.plan-fulfillment-native.native_box')
    return ROOT / 'experiments/plan-fulfillment-native', configuration.BOX, None
```

Generate the Typia validators **before** asking Pi to generate code:

```sh
npx typia generate --input experiments/plan-fulfillment-native/src --output experiments/plan-fulfillment-native/.generated --project experiments/plan-fulfillment-native/tsconfig.json
npx vitest run --config experiments/plan-fulfillment-native/vitest.tooling.config.mts
```

Then invoke Pi (billable, real model call):

```sh
BOUNDSCRIPT_RUNTIME=docker python3 -B experiments/native_cli.py generate plan-fulfillment --agent-owned --retain-candidate
```

The result, if safe to retain, is stored under `experiments/plan-fulfillment-native/candidates/<id>/`. The generator verifies using the same independent suite and does not promote automatically.

## Test intent

Eleven fixtures check empty requests, partial fills, warehouse precedence, FEFO/FIFO, exclusions, priority, warehouse allow-lists and validation precedence. One bounded fast-check property checks conservation and determinism. No existing task, test, verifier or runtime code needs to change besides explicit CLI registration.

**Limits:** source generation is capped at 16 files / 16 KiB total. This may encourage a compact implementation. No file-count objective is imposed. The ZIP's tests have not been run inside your repository.
