# 0034 — Document Boxes as Generated Software Assets

## Status

Completed

## Objective and scope

Clarify BoundScript's architectural purpose and the lifecycle of generated Boxes in `README.md` and `docs/development/architecture.md`. Keep the documentation concise and developer-oriented, distinguish current functionality from future intentions, and preserve existing experimental evidence and limitations.

## Requirements and acceptance criteria

- Describe BoundScript as a developer tool, not an AI runtime platform, and a Box as a generated software asset intended for a consuming project.
- Developers own contracts, requirements and acceptance criteria; AI agents implement within those boundaries.
- Independent verification and explicit human acceptance are required before generated implementations are trusted project assets.
- Once accepted, a Box should be reproducible and usable without BoundScript, Pi or an LLM at application runtime.
- Possible future integrations include libraries, modules, UI components, services and runtime-loaded components; execution and security guarantees may differ by integration model.
- Mark Box versioning as planned, not implemented. Describe the intended sequence: generate a candidate, independently verify, obtain human acceptance, publish an immutable identifiable version, and integrate that specific version.
- Regeneration must create a new candidate rather than silently overwrite an accepted version. Publishing a new version must not automatically update existing consumers.
- Leave version numbering, compatibility rules, storage and distribution mechanisms undecided.

## Constraints

Documentation only. Do not implement versioning, change code, or introduce registries, manifests, runtime loaders or new abstractions. Do not commit or push. Do not mark this delivery accepted without explicit human acceptance.

## Verification

- Updated both target documents with the developer-tool purpose, asset lifecycle, trust requirements and planned versioning constraints.
- Distinguished current automatic local promotion/replacement from human acceptance and immutable publication; checked existing generator promotion paths.
- Reviewed the diff against the requirements; existing experimental evidence and limitations remain intact.
- `git diff --check` passed. No code changed; runtime tests were not run for this documentation-only delivery.
- The Product Owner reviewed and explicitly accepted the delivery and authorized a local commit. No push was authorized.
