# RenderWelcome

Implement `/implementation/implementation.ts`, exporting `renderWelcome` conforming to `RenderWelcome` in `/inputs/contract.ts`.

This Box is a pure, synchronous formatter of an already-normalized contact. Return exactly `Welcome, NAME! <EMAIL>` using the supplied `contact.name` and `contact.email` verbatim, with the literal punctuation/spaces and no added newline. Phone is required by the input shape but ignored in the output.

Preserve case, whitespace, international characters, punctuation and Unicode code-unit sequences. Do not trim, normalize, escape markup, encode values, validate email/phone semantics, add fallbacks or call a normalizer. Even whitespace-only names and unusual email/phone strings that satisfy the public structural contract are formatted verbatim.

Do not mutate or retain the input; frozen input records must work. Be deterministic and independent of previous calls. Return a string, not a Promise or result object. No I/O, time/randomness/environment dependence, peer calls or external runtime dependencies. Use only type-only contract imports if needed.

The message is plain text, not HTML-safe markup. Its caller owns text-safe display, normalization and error handling. Missing/empty/non-string fields, null and normalization failure objects are outside the input contract; no invalid-call fallback or exception behavior is specified.

Only this task and your own public contract are authorized Box inputs. No peer source, task, tests or fixtures are available. Do not install packages or inspect, print, copy or disclose credentials. Only `/implementation` is writable submission space. Agent-readable authentication and unrestricted generation networking remain prototype risks, not import or egress enforcement.
