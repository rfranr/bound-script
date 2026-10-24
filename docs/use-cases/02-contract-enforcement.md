# UC-02 — Enforce box contracts

**Status:** Target — not implemented

## Goal

Show that box boundaries have enforceable meaning beyond documentation or TypeScript type annotations.

## Illustrative scenario

A `Divide` box accepts numeric `a` and `b`, with a precondition that `b` is not zero, and returns a numeric `result`. Its implementation can deliberately return an invalid output in a negative test.

The form of `ensure`, preconditions, and return schemas remains a language-design decision.

## Minimum acceptance criteria

1. Valid input (`a = 10`, `b = 2`) yields `result = 5`.
2. Calling with `b = 0` is rejected at the contract boundary **before** the implementation runs.
3. An implementation returning an output with an incorrect type or missing required field is rejected.
4. Each violation has an identifiable error category and identifies the affected box and contract boundary.
5. A violation cannot be silently converted into a successful box result.

## Evidence

Automated positive and negative tests use an implementation spy to prove the precondition prevents invocation and to verify output validation after invocation.

## Out of scope

A complete theorem prover, arbitrary user-defined predicates, static proof of all invariants, or finalized error-handling syntax.
