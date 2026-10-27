# Assignment 0018b — richer contact domain

**Outcome: both fresh pairs passed without retries or source repair.** Definition
freeze: `61a8ef9`, committed before either `npm run generate:pair` invocation.
Contracts, tasks, acceptance checks and ordinary application wiring were unchanged
between generations. No work on 0019 or 0020; no new packages or harness changes.

## Contract and independent checks

Inputs contain two required string fields; missing/non-string fields are outside
the native contract. The task defines ECMAScript whitespace, Unicode preservation,
a deliberately simple email regex and ordered error codes. NormalizeContact
returns a discriminated success/failure union. RenderWelcome retains a string API
and consumes that union through its injected dependency, without duplicating rules.

Each generation passed the same frozen external checks:

- NormalizeContact: strict native signature/union consumer and 20 literal cases,
  each called twice for deterministic results. Frozen inputs, fresh success contact,
  ordered simultaneous errors, required-vs-invalid email distinction, whitespace,
  composed/decomposed Unicode, emoji and email format boundaries were checked.
- RenderWelcome: strict native signature consumer, 80 injected-result cases
  (20 inputs × four results), plus one throwing-dependency case. Exactly one call
  with the original input; authoritative non-normalized/empty success values;
  ordered/duplicate/empty failure errors; frozen input/result objects; and exception
  identity propagation were checked.
- Integration: 20 cases through unchanged ordinary `application.ts` wiring in a
  separate offline container. Accepted artifact hashes remained unchanged.

Pre-generation `npm test` passed Greeting and rejected the old normalizer with
TS2322 against the new union, as expected. It was not manually adapted. After the
second generation, full `npm test` passed Greeting, both richer Boxes and integration.
Python syntax and Git whitespace checks passed; no experiment containers remained.

## Fresh sessions and hashes

All four runs used Pi 1.4.0, `openai-codex/gpt-6.1-sol`, medium reasoning, separate
empty Docker workspaces and fresh `--no-session` processes. Tools were read/write/
edit/bash; actual counts below. Raw transcripts/diagnostics were not retained.

| Pair | Box | Session UUID | read/write/edit/bash | failures |
| --- | --- | --- | --- | ---: |
| 1 | NormalizeContact | `01a17c4b-0f4f-7797-bd9c-4126cd24e2a9` | 2/1/0/0 | 0 |
| 1 | RenderWelcome | `01a17c4b-730c-7290-ab32-8fb20e7ed8ce` | 3/1/0/0 | 0 |
| 2 | NormalizeContact | `01a17c4b-ff1a-7720-8fb7-e9744995b16e` | 2/1/0/0 | 0 |
| 2 | RenderWelcome | `01a17c4c-5407-75b4-b14b-f386dc5cab66` | 3/1/0/0 | 0 |

SHA-256 at individually verified, unchanged promotion:

| Pair | Box | SHA-256 |
| --- | --- | --- |
| 1 | NormalizeContact | `ffbe49708ca9c0e741ceed0269e8e3c77c4bf2e4d7933e5cd571bd448c9bb591` |
| 1 | RenderWelcome | `70259267c775b7695872600a864b6e3a93d01d269580aae786a16b4fcf154f23` |
| 2 | NormalizeContact | `ffbe49708ca9c0e741ceed0269e8e3c77c4bf2e4d7933e5cd571bd448c9bb591` |
| 2 | RenderWelcome | `6cb8ab04afc098f2d1f4832b50df1e1517731637a5355f3d0a00f7fd23caf74a` |

NormalizeContact was byte-identical across generations, which is acceptable.
RenderWelcome differed only in its type-only import path: pair 1 used
`../inputs/contract.ts`, pair 2 `/inputs/contract.ts`. Both paths resolved under
independent native type checking; erased type imports do not affect integration.
Both satisfied the same contract and produced identical observed behavior on all
checks. The saved accepted artifacts are pair 2's exact bytes, with no formatting,
import rewriting or other manual changes. Pair 1 was superseded after passing;
only its safe metadata is retained, not temporary generated copies.

## Isolation, interventions and limits

NormalizeContact received only its task/contract. RenderWelcome received only its
own task/contract and NormalizeContact's public contract. Neither received peer
implementation, application, tests, verifier, previous output or session context.
Every candidate passed independent credential-free offline verification before
promotion; each pair then passed separate integration.

All generation filesystem probes passed (unexposed host/repository/tests/peer
reads denied, protected writes denied, symlink host read denied). Peer read/import
probes also passed in individual and integration verifiers. Host auth and protected
input hashes were unchanged; credential literal scans passed. No manual source
intervention, feedback, retry, test relaxation or requirement deviation occurred.

Reproduce with two `npm run generate:pair` calls, then `npm test`. Generation makes
real provider calls and exposes the explicitly authorized auth file to Pi tools.
Existing prototype risks remain: unrestricted generation networking, agent-readable
credentials, shared kernel, per-Box rather than atomic pair promotion, no generic
import enforcement, and finite observations rather than correctness/security proof.
See the [experiment limitations](README.md#boundary-control-and-limits).
