# EvaluateRules native Box

Consumer-owned specification and independent tests. **No implementation is included.**

## Install into BoundScript

Copy this whole directory to `experiments/evaluate-rules-native/`.

Add this selection to `select_box()` in `experiments/native_cli.py` (before its final error):

```python
if selection == 'evaluate-rules':
    configuration = import_module('experiments.evaluate-rules-native.native_box')
    return ROOT / 'experiments/evaluate-rules-native', configuration.BOX, None
```

Generate Typia files first:

```sh
npx typia generate --input experiments/evaluate-rules-native/src --output experiments/evaluate-rules-native/.generated --project experiments/evaluate-rules-native/tsconfig.json
```

For a credential-free validator smoke test:

```sh
npx vitest run --config experiments/evaluate-rules-native/vitest.tooling.config.mts
```

Then **only when you want billable Pi generation**:

```sh
DEBUG=1 BOUNDSCRIPT_RUNTIME=docker python3 -B experiments/native_cli.py generate evaluate-rules --agent-owned --retain-candidate
```

Output is retained in `experiments/evaluate-rules-native/candidates/<id>/` when retention checks allow. The agent may choose one or several implementation files; no file-count requirement. Nothing is promoted automatically.

12 fixtures include forward dependencies, nested logic, empty combinators, duplicates, unknown references and cycles. One bounded fast-check property checks independent predicates and output order. The fixtures are consumer-owned and must never be supplied to Pi.

This ZIP has not been tested against your local checkout. Generated `.generated/` files are intentionally omitted.
