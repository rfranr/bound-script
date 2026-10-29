# ProcessOrders

Implement `ProcessOrders` from the public TypeScript contract. Export `processOrders` from `/implementation/implementation.ts`.

The function receives one already-valid order and returns its monetary breakdown. All monetary amounts are **integer cents**, not floating-point currency. Preserve the order ID and line order. Each input line produces exactly one output line with the same SKU.

For every line, calculate **in this exact order**:

1. `subtotalCents = quantity * unitPriceCents`.
2. `discountCents = floor(subtotalCents * discountPercent / 100)`.
3. `taxableCents = subtotalCents - discountCents`.
4. `taxCents = floor(taxableCents * taxPercent / 100)`.
5. `totalCents = taxableCents + taxCents`.

The order-level `subtotalCents`, `discountCents`, `taxCents` and `totalCents` are sums of the corresponding **rounded line-level amounts**. Do not round only after aggregating.

The public contract describes valid input shapes. The caller supplies only valid orders. For this exercise, totals and intermediate arithmetic are guaranteed to stay within JavaScript's safe integer range. Duplicate SKUs may occur and must remain separate lines. Do not add extra fields, silently normalize SKUs, reorder lines, mutate input or retain state.

The result must be deterministic and independent of prior calls, environment, time, randomness and I/O. Do not install packages or depend on runtime libraries outside the standard JavaScript runtime. The implementation may organize its own supported TypeScript sources however it chooses; no particular architecture or file count is requested.

Only this task and the public contract are authorized agent inputs; tests, fixtures and any existing implementation are independent verifier-owned materials.
