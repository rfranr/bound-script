# UC-01 — Define a system and execute a box

**Status:** Target — not implemented

## Goal

Demonstrate the core value proposition: a declared system contains a director that invokes a box through an explicit contract, without embedding the box implementation in the director.

## Illustrative scenario

A `GreetingSystem` declares a `Greeter` box receiving `name: string` and producing `greeting: string`. On start, the director passes `"Paco"` to `Greeter` and prints the returned greeting. A developer-written implementation returns `"Hello, Paco"`.

This is a behavior description, **not finalized BoundScript syntax**.

## Minimum acceptance criteria

1. The system, director, box interface, and entrypoint can be declared and resolved.
2. A concrete implementation is explicitly bound to the declared `Greeter` box.
3. Starting the director invokes that implementation exactly once with `name = "Paco"`.
4. The director receives the named output and emits `Hello, Paco`.
5. A missing box implementation produces an identifiable binding error rather than a silent no-op.
6. The director depends on the box contract, not on the implementation's internal code.

## Evidence

An automated integration test supplies a deterministic stub implementation, runs the system, asserts the input and output, and separately verifies the missing-binding failure.

## Out of scope

AI-generated implementations, networking, persistence, deployment, and a particular output target such as JavaScript.
