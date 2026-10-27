# Assignment 0018 — actual run

**Outcome: passed on the first fresh pair.** No work on 0019 or 0020.
Tasks, contracts, native signature consumers, behavior expectations and ordinary
application wiring were committed **before generation** in `dbf844c`.
None was changed to accommodate the generated implementations.

## Reproduction commands

From `experiment/boundscript-next`, with the existing cached Node image, Pi 1.4.0
installation/authentication and TypeScript 5.9.3:

```bash
npm ci --ignore-scripts --offline
npm run generate:pair
npm run test:pair
npm run check
git diff --check
docker ps -a --filter name=boundscript-box-agent- --format '{{.Names}}'
docker ps -a --filter name=boundscript-contact-check- --format '{{.Names}}'
docker ps -a --filter name=boundscript-minimal- --format '{{.Names}}'
```

The generation command is exactly
`python3 experiments/minimal-box/generate.py --pair`. It makes metered model
calls; verification commands do not. Every generation starts empty, without
seeding from accepted code. Later runs may produce different source.

## Real agent runs

Both used **Pi 1.4.0**, selected model **openai-codex/gpt-6.1-sol**, medium reasoning,
read/write/edit/bash tools, separate containers, separate empty workspaces and
`--no-session`. These are the two observed JSON session headers, not raw transcripts:

| Box | Session UUID | read | write | edit | bash | tool failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| NormalizeContact | `01a17aae-4c02-7412-b5d6-cf764e2e1371` | 2 | 1 | 0 | 0 | 0 |
| RenderWelcome | `01a17aae-8d93-762b-99ff-b46b0b299220` | 3 | 1 | 0 | 0 | 0 |

NormalizeContact received only its task and public contract. RenderWelcome
received its own task/contract and NormalizeContact's public contract, never its
implementation. The explicit task dependency declaration and native type import
are the authority; the fixed per-Box mount selection exposes only those files.
Even though execution was sequential, no previous session, output, feedback,
peer task, accepted source, application or tests entered the second workspace.

All observed read-tool paths were authorized; each agent wrote exactly one
regular `implementation.ts`. Neither used Bash. Both host auth hashes and the
protected input/sentinel hashes remained unchanged. Literal credential-value
scans passed. No raw agent diagnostics/transcripts were saved or printed.
Provider billing and general network/syscall behavior were not independently
measured. Reported tool counts are observations, not complete security attestation.

## Independent verification and unchanged integration

Both candidates passed their own fresh, credential-free, offline verifier before
promotion. Native TypeScript consumers checked the actual named exports against
the approved public signatures. Four cases per Box covered whitespace, internal
spaces, case conversion, empty strings and a Unicode name. Input objects remained
unchanged; normalization returned a new record.

RenderWelcome was checked using a spy dependency returning `Supplied 0` through
`Supplied 3`, not the real normalized names. Exactly one call with the original
input object was observed per case, and the message used the supplied result.
This makes the authorized dependency exercised, not just a declaration.

After both individual promotions, a **separate integration container** loaded
human-owned `application.ts`. Its ordinary TypeScript passes the unchanged accepted
normalizer to the unchanged accepted renderer. Four end-to-end messages passed:

- `Welcome, Ada Lovelace! <ada@example.test>`
- `Welcome, Grace  Hopper! <grace@example.test>` (two internal spaces)
- `Welcome, ! <>`
- `Welcome, Zoë! <zoe@example.test>`

Accepted source SHA-256 values printed at promotion and unchanged by integration:

- `normalize-contact.ts`: `681cd172834d752f7681aa07cd98441db771972908c6ddd3797cbd5838037214`
- `render-welcome.ts`: `e8c5e8b24d60d726904aa66d3c01961599f52ff22b2849c304394b4b1b2c5b6b`

The checked-in accepted files are these exact outputs: no formatting, import
rewriting, repair or adaptation. Native Node TypeScript stripping erases type-only
imports at execution; contract aliases are used during independent type checking.
Read-only integration mounts and before/after hashes checked source immutability.

## Deliberate negative controls and failures

Before Pi started, fixed action probes ran in **each actual generation container**:

- Attempted unauthorized peer implementation read: **`ENOENT`**.
- Attempted dynamic import of that unexposed peer: **`ERR_MODULE_NOT_FOUND`**.
- Host/repository/verifier/test reads: **`ENOENT`**.
- Task/root writes: **`EROFS`**; host-target symlink read: **`ENOENT`**.

The host sentinel exists on the host before the attempt, and the protected task
is an actual mounted input: their failures demonstrate a real filesystem view /
read-only mount restriction, not merely an instruction to the model. The peer
probe targets an intentionally absent path; inspected mount allowlists establish
that no peer implementation was exposed. The first two checks were repeated in
each independent Box verifier and the integration environment. These are deliberate controller-issued operations under
the same filesystem authority, not claims that a model spontaneously attacked it.
The peer implementation is absent from the view; kernel/module resolution rejects
the attempt. **No source-import allowlist was implemented.** Imports of exposed
files, dynamic loading, Node built-ins and transitive imports are not generically
policed. Unrestricted networking could fetch public peer source.

Before freezing `dbf844c`, four temporary verifier controls were run through
`python3 experiments/minimal-box/verify_pair.py <box> <temporary-source.ts>`:
valid normalization/rendering specimens passed; a normalizer returning a string
failed its native signature check (`TS2322`); a type-correct renderer normalizing
input itself failed the external dependency-use assertion. Those expected failures
were not model submissions and were never promoted or supplied to an agent.

Actual pair: **zero generation, type, behavior or integration failures**, no retries,
no feedback, no manual implementation repair. The original Greeting regression
also passed. Clean dependency installation, saved-pair checks, Python syntax and
Git whitespace checks passed; no experiment containers remained afterward.

## Limits / deviations

No scope deviation: only the fixed 0018 experiment was added. The original branch
remains at `31dc3bf1eabc48f77d2024b9c421714dc205da6c`. Its source and historical pilot
were not modified.

Existing risks remain explicit: agent-readable credentials (only `auth.json`
mounted, read-only; refresh uses disposable tmpfs), unrestricted generation bridge
networking, writable runtime state, shared host kernel, finite tests, and a verifier
that cannot attest arbitrary hostile candidate-returned data. A passing TypeScript
assignment is not universal runtime correctness or protection against `any`/casts.
Credential literal scanning is not encoded-secret detection or exfiltration defense.

Promotions are individually gated, not an atomic pair transaction. No general
source/dependency enforcement, new configuration format, credential broker,
artifact registry, plugin system, reusable runner, custom runtime or DSL was added.
