# Assignment 0018b — richer contact domain

## Definition freeze (before generation)

The contracts, tasks, external acceptance checks and ordinary application wiring
are committed before any fresh Pi generation for this assignment. Generation
will reuse the unchanged fixed Docker/Pi harness and dependency visibility rules.
No work on 0019 or 0020 is included.

The input domain is two required string fields (missing/non-string fields are
outside the native contract). The task explicitly defines ECMAScript whitespace,
Unicode preservation, a deliberately simple email regex and ordered error codes.
RenderWelcome remains a string-returning API, now consuming the dependency's
success/failure union. No additional Box or dependency is introduced.

Pre-generation verification: Python syntax parsed successfully. `npm test` passed
the saved Greeting regression and rejected the old accepted normalizer with
TS2322 against the new union contract, as expected. Old artifacts are intentionally
not hand-adapted; fresh accepted sources will replace them after verification.

Planned comparison: two `npm run generate:pair` invocations, four independent
empty agent workspaces in total. Record sessions, source hashes, individual and
integration results, any failures and manual intervention below after execution.
Only safe metadata is retained; no raw transcripts or temporary artifacts.
