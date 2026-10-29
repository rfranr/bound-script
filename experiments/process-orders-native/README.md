# ProcessOrders Box — consumer-owned inputs

This ZIP contains **no candidate implementation**. It follows the existing native Box structure.

After extracting to `experiments/render-ProcessOrders-native/`, register this Box explicitly in `experiments/native_cli.py` (the CLI has a fixed selector), and add a build step before generation:

```sh
npx typia generate --input experiments/render-ProcessOrders-native/src --output experiments/render-ProcessOrders-native/.generated --project experiments/render-ProcessOrders-native/tsconfig.json
BOUNDSCRIPT_RUNTIME=docker python3 -B experiments/native_cli.py generate process-orders --agent-owned --retain-candidate
```

The CLI's literal selection name should be `process-orders`, pointing to `experiments.render-ProcessOrders-native.native_box` and the Box root directory. If the native CLI rejects the combined flags, check that assignment 0048's `--retain-candidate` change is present.

`task.md` and `src/contract.ts` are the only materials the generation agent should see. Tests and fixtures are verifier-owned. The Box name and directory name differ intentionally: CLI selector `process-orders`, Box name `process-orders-native`, directory `render-ProcessOrders-native`.

NOTE: Existing verifier's sanitized Typia field allowlist is specialized for contact data; it may withhold diagnostic field paths for this Box. This is safe but less descriptive.
