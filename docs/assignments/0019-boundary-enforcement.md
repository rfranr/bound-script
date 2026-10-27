# Assignment 0019 — Enforce Declared Box Boundaries

**Prerequisite:** review the actual findings of assignment 0018 before implementation. Adjust this assignment with Product Owner approval if those findings change its scope.

## Goal

Make the architectural dependency boundary enforceable, not merely descriptive.

## Scope

Using the two-Box experiment, define the smallest human-owned source of truth for each Box's authorized dependencies and relevant read/write capabilities. Demonstrate that the execution and verification paths honor it.

## Required checks

- An agent cannot read or modify another Box's implementation, contracts, acceptance checks, or unrelated repository files unless explicitly authorized.
- A candidate cannot consume an undeclared Box or import implementation internals simply by using a path or package alias.
- Authorized public-contract imports and normal TypeScript composition continue to work.
- Negative tests exercise actual denial mechanisms, not only instructions in prompts.
- Verification and promotion remain independent of agent-controlled files.

Document where enforcement occurs (workspace mounts, TypeScript resolution, import checks, integration, etc.) and the limits of each control. Consider transitive dependencies and alternate import paths explicitly; do not claim universal enforcement if the experiment only covers a subset.

## Constraints

Keep changes focused on observed gaps from 0018. Do not build a generalized security policy engine, DSL, custom runtime, or full package manager. Do not silently treat unrestricted prototype network access or agent-readable credentials as secure isolation.

## Acceptance

Demonstrate passing authorized dependency use and failing unauthorized read, write, and dependency attempts. Provide reproducible commands and a concise statement of guarantees versus limitations. Keep the original branch untouched.
