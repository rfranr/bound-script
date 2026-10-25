# UC-05 — Enforce box capability boundaries

**Status:** Target — not implemented

## Goal

Prove that declaring capabilities has enforceable runtime consequences, not merely advisory effects.

## Illustrative scenario

A box is granted a narrowly scoped capability to call one approved HTTP endpoint, but no filesystem-read capability. Its implementation attempts an unauthorized local file read.

The precise capability syntax and sandbox technology remain undecided.

## Minimum acceptance criteria

1. An implementation can perform an explicitly granted operation through the supported capability interface.
2. An attempt to read an unauthorized local file is denied at execution time.
3. The denial is observable with an identifiable capability/security error.
4. Denied operations produce no unauthorized side effect or data disclosure.
5. Changing a prompt, static type annotation, or implementation declaration alone cannot grant a capability.
6. The test uses the **actual enforcement boundary**, not only a mocked permission-checking function.

## Evidence

An isolated integration/security test exercises both permitted and denied behavior and verifies that protected data was not returned. Document the sandbox's threat model and limits before claiming a security guarantee.

## Out of scope

A claim of complete isolation against arbitrary malicious native code, multi-tenant production security, or a particular sandbox provider.
