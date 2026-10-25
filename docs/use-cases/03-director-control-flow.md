# UC-03 — Orchestrate with explicit control flow

**Status:** Target — not implemented

## Goal

Show that directors express actual execution decisions, not merely a static dependency graph.

## Illustrative scenario

An `OrderSystem` director calls `ValidateOrder`. It calls `ChargePayment` only if validation succeeds; otherwise it returns a rejected result. A second minimal scenario repeats a box operation over a bounded collection or count.

Branching and loop syntax is deliberately unspecified.

## Minimum acceptance criteria

1. For a valid order, validation runs before payment and payment runs exactly once.
2. For an invalid order, the payment box is never invoked.
3. The director produces a distinguishable result for each branch.
4. Repetition can invoke a box multiple times under explicit control, with deterministic order for a sequential case.
5. A zero-iteration case invokes the repeated box zero times.
6. Errors from an invoked box are observable and are not silently treated as successful results.

## Evidence

Automated tests use instrumented box implementations to record the invocation sequence and assert positive, negative, zero-iteration, and error outcomes.

## Out of scope

Concurrency, automatic DAG scheduling, distributed retries, transactions, or arbitrary general-purpose scripting functionality.
