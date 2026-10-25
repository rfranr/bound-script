# UC-04 — Reuse definitions across modules

**Status:** Target — not implemented

## Goal

Support modular system definitions without requiring every `.bound` file to declare a `system`.

## Illustrative scenario

A `contracts/order.bound` module declares a reusable `Order` type and `ValidateOrder` box contract. Two separate system modules import those definitions and use them without redefining the contract.

Exact import and export syntax, resolution rules, and package discovery are not yet fixed.

## Minimum acceptance criteria

1. A `.bound` file containing only reusable definitions is valid.
2. A system can explicitly import a type and a box contract from another file.
3. At least two distinct systems can import the same declarations successfully.
4. An unknown import or unresolved symbol produces a source-located diagnostic.
5. Imports resolve deterministically relative to an explicit, documented module-resolution rule.
6. A duplicate or ambiguous imported symbol is rejected unless the language provides an explicit disambiguation mechanism.

## Evidence

A multi-file conformance fixture proves successful reuse; negative fixtures verify missing and ambiguous symbols.

## Out of scope

Remote registries, package publishing, version solving, implicit global symbol discovery, and finalizing module-cycle semantics.
