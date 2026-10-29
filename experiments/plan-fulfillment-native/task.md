# PlanFulfillment — consumer-owned behavior

Implement `PlanFulfillment`, exporting `planFulfillment` from `/implementation/implementation.ts` using the declared `contract.ts`. Return a synchronous, pure, deterministic result. The engine sees this task and the public TypeScript contract, **not** the tests or fixtures.

The request contains stock lots, orders with demand lines, a canonical `today` date, a global warehouse priority list, and a picking method. All data satisfy the public structural TypeScript contract. Dates must additionally be valid Gregorian calendar dates (not merely match YYYY-MM-DD). Never mutate, retain or depend on object identity of inputs. Do not do I/O, use random/time, import packages or execute supplied data.

## Validation (before any allocation)

Perform validation in this exact precedence order:

1. `DUPLICATE_ID`: scan `lots` in their input order for the first repeated lot ID; then scan `orders` in input order for a repeated order ID; then, per order in input order, scan its lines for a repeated line ID **within that order**. Return the offending identifier. IDs of different entity categories may coincide. Repeated warehouse names in `warehousePriority` are not an error; use their first occurrence.
2. `UNKNOWN_WAREHOUSE`: scan lots in input order, then orders and their `allowedWarehouses` lists in input order. Return the first warehouse identifier that is not present in `warehousePriority`. `allowedWarehouses` may be empty, which permits no warehouses.
3. `INVALID_DATE`: validate `today` first, then lot `expiresOn` dates in input order. Return the invalid date string in `error.id`. Use real Gregorian dates including leap years. Dates are compared chronologically, not in local time.

If validation fails return only `{ok:false,error:{code,id}}`; no partial plan. Any otherwise structurally valid empty arrays are allowed. Semantic validation is the Box's responsibility.

## Allocation

- Work from each lot's `available` integer quantity. Blocked lots and lots whose `expiresOn` is **earlier than** `today` are unavailable. Lots expiring **on** today are eligible.
- Process orders by ascending numeric `priority`, ties by lexicographic `id` (JavaScript UTF-16 string ordering). Within an order, process demand lines in their original order. Output allocation and shortage entries in this processing order.
- Only consider eligible lots with the demand line's `sku`, a positive remaining quantity, and a warehouse in the order's `allowedWarehouses` list.
- Among eligible lots choose the lowest warehouse index in `warehousePriority` **first**. Within that warehouse: `FEFO` means earliest `expiresOn` first, ties by lowest `receivedSequence`; `FIFO` means lowest `receivedSequence` first, ties by earliest `expiresOn`. Remaining ties use lexicographic lot `id`.
- Repeatedly take `min(unfilled demand, lot remaining)` and emit one allocation per lot actually used. No zero-quantity allocations. A lot can supply multiple orders or lines until exhausted. If demand remains, emit exactly one positive shortage for that line; fully satisfied lines have no shortage. Do not consolidate lines, even when SKUs match.
- Output `remaining` contains **every** input lot in its original input order, including expired or blocked lots, with its final available quantity. Never reorder or omit them.
- If quantities exceed JavaScript safe integer range in intermediate arithmetic, return `{ok:false,error:{code:'INVALID_DATE',id:'UNSAFE_QUANTITY'}}` before producing a partial plan. This special error is only for arithmetic overflow and is checked during allocation. (Input integers are bounded by the public uint32 constraint.)

## Boundaries

`implementation.ts` and exported `planFulfillment` are the sole public entry point.

**Organize the implementation into multiple cohesive TypeScript modules**, separating distinct responsibilities where appropriate. Keep `implementation.ts` focused on coordinating the public operation, delegating implementation details to internal modules.

You are free to decide module boundaries, filenames, algorithms, abstractions and dependencies between internal modules. Avoid unnecessary abstractions or fragmentation.

Use relative imports. Type-only imports from `./contract` are permitted. Do not assume any tests, example source, or peer implementation is available.