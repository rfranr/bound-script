# 0035 — Clarify the Architectural Definition of a Box

## Status

Completed

## Objective and scope

Update `docs/development/architecture.md` to clarify the architectural definition of a Box while preserving the existing architecture and roadmap.

## Requirements and acceptance criteria

- Define a Box as a bounded software unit with a public contract, independent verification and an integration interface.
- Explain that implementations may consist of functions, classes, modules or components; a Box is not restricted to one function or source file.
- State that Boxes are intended to integrate into consuming projects through public interfaces.
- Identify hierarchical composition and imports between Boxes as possible future integration capabilities.
- Identify standalone executable artifacts, such as CLI tools, as possible future outputs, not current capabilities.
- Preserve BoundScript's role as a developer tool; consuming applications should not require an AI agent at runtime.
- Clearly distinguish implemented capabilities from architectural intentions.

## Constraints

Documentation only. Do not modify code or tests, introduce new abstractions, implementation tasks or speculative technical designs, or change the existing roadmap. Do not commit or push. Report the documentation changes for review; acceptance remains with the Product Owner.

## Verification

- Updated the purpose and lifecycle section with the bounded-unit definition, implementation forms and public-interface integration intent.
- Distinguished current fixed TypeScript function exports/single-file candidates and baseline composition from possible future hierarchical composition, inter-Box imports and executable outputs.
- Retained the existing lifecycle, architecture, roadmap and limitations; no code or tests changed.
- Reviewed the documentation diff against the requirements; `git diff --check` passed. Runtime tests were not run for this documentation-only change.
- The Product Owner reviewed and explicitly accepted the delivery and authorized a local commit. No push was authorized.
