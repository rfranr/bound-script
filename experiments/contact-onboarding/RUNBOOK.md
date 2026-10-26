# Manual ContactOnboarding execution — Assignment 0022

**STOP: this guide does not authorize execution.** The Product Owner approved the frozen 0023 assets and will manually operate both Pi sessions. Wait for the Product Owner's **execution confirmation and spending-policy decision** before running this guide. M3 remains Planned until then. No agents were launched to prepare this document.

**Frozen inputs:** `aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9`. This newly added operator guide is **not** a change to that frozen input set and must never be attached to either agent. All executable assets come from a separate checkout of the frozen revision, which does not contain this guide. See [0022](../../docs/assignments/0022-run-bounded-independent-implementation-pilot.md) and the [freeze record](../../docs/development/0023-contact-onboarding-freeze.md).

## 1. Conventions, prerequisites and limits

- **TERMINAL — Bash** blocks go into your ordinary terminal, **not Pi**. **PI — local command** blocks go into Pi's editor; these built-in slash commands do not request model inference. **PI — send to agent** blocks are actual model prompts. Read the prose between blocks; do not paste the entire document as a script.
- Use **one Bash terminal**, kept open throughout. Pi temporarily occupies it; `/quit` returns you to Bash with the same variables. Run A then B sequentially, not concurrently. Separate directories **and separate empty session histories** provide independence; they are not OS sandboxes.
- Existing trusted installation: Linux x86_64, Bash, Git, GNU `timeout`, `dd`, `find`, `diff`, `tee`, Python 3, Node v24.16.0, repository dependencies matching `package-lock.json` (TypeScript 5.9.3), Docker daemon 29.1.3 with permission to create non-privileged containers, and native Pi 1.4.0 with the already approved OpenAI authentication. If these prerequisites are missing/different, stop for review; do not install frameworks, update Pi/model configuration, inspect credentials or improvise a host evaluation fallback.
- The terminal must already support Pi's `/copy` through its normal clipboard backend/OSC52 and UTF-8 paste. If copying is unavailable, empty or truncated, keep the native history and stop; do not regenerate the answer, install clipboard tooling mid-trial or use a sharing service as a workaround.
- Model is **`openai-codex/gpt-6.1-sol`**, thinking **medium**. Preserve native authentication. Do not use `pi auth`, `/login`, credential-printing commands, API-key command-line overrides, provider/model cycling or an authentication smoke prompt in this trial.
- One initial episode plus **at most one own-context revision per Box**. Each episode ends at submission/clarification/proposal/interruption or **30 elapsed minutes / 40 model-response turns**, whichever comes first. The terminal timer enforces time only; you must count logical turns/recovery activity and press Escape/quit at the turn limit (or stop if the count cannot be established). At most four episodes, **160 logical turns / 120 active generation minutes** overall; normally just **2–4 complete responses**. These ceilings do not authorize repeated attempts until success. Count automatic model-recovery turns; separately record native transport retries and missing visibility. Logical turns are not a hard HTTP/token/dollar cap. Do not trigger `/compact`, branch summaries, cache-warming requests or another model-judge/reporting agent; record any native automatic model activity against the allowance and stop if you cannot maintain the agreed budget. Do not change global settings to hide it.
- **Before starting:** obtain a monetary ceiling/enforcement policy, or explicit approval of response/time-only limits if native billing is unobservable. No dollar/token allowance defaults to unlimited. Provider quota/transport failure stops the trial; no manual retry or silent model switch. Any controller-assistant usage is separate workflow overhead, not zero or part of the 160 implementation-turn allowance.
- Pi generation needs its existing provider connection. **Candidate code does not:** every compile, private test, independent suite and integration runs only in disposable credential-free Docker containers with networking disabled. Never import/transpile/test generated `.ts` on the host, run suggested shell commands, use an executing preview/formatter/editor hook, or add candidates to repository tests.

## 2. Prepare the trusted controller checkout and handoffs

**TERMINAL — Bash.** Start inside your existing BoundScript repository. These commands create a new private run directory outside Git; note the printed path. Do not repeat this initialization to erase a failed trial.

```bash
set -o pipefail
umask 077
export REPO="$(git rev-parse --show-toplevel)"
export FREEZE=aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9
export RUN="$(mktemp -d /tmp/contact-onboarding-M3-01.XXXXXX)"
mkdir -p "$RUN/controller/logs" "$RUN/controller/responses" \
  "$RUN/controller/sessions/A" "$RUN/controller/sessions/B" \
  "$RUN/agents/A" "$RUN/agents/B" "$RUN/submissions/A" "$RUN/submissions/B"
export FROZEN="$RUN/controller/frozen"
git -C "$REPO" worktree add --detach "$FROZEN" "$FREEZE"
export ASSETS="$FROZEN/experiments/contact-onboarding"
export STAGE="$RUN/controller/stage"
printf 'Run ID: M3-ContactOnboarding-01\nRUN=%s\nFROZEN=%s\n' "$RUN" "$FROZEN"
```

**Stop if any preparation command fails.** Do not continue with partial staging. Keep this terminal open; if it closes, recover the same `RUN` and paths from your notes, not a new trial/session. The trusted checkout contains the repository; it is **never** mounted wholesale into candidate containers or made available in either agent workspace.

**TERMINAL — Bash.** Record versions without opening credential stores. `pi --version` is metadata, not an implementation session or inference.

```bash
PI_BIN="$(type -P pi)"
if [[ "$PI_BIN" == /* && -x "$PI_BIN" ]]; then
  printf 'Native Pi executable: %s\n' "$PI_BIN"
  {
    printf 'Frozen revision: '; git -C "$FROZEN" rev-parse HEAD && \
    node --version && \
    "$PI_BIN" --version && \
    docker version --format '{{.Server.Version}}' && \
    uname -sm
  } | tee "$RUN/controller/logs/versions.txt"
else
  printf 'STOP: no absolute executable native Pi path found.\n' >&2
  false
fi
```

`PI_BIN` must be the absolute path of the existing trusted native Pi executable (a normal installation symlink is fine), not a custom launcher. Pinning its path avoids shell aliases/functions injecting extra startup options; stop if you cannot establish that prerequisite.

**TERMINAL — Bash.** Copy existing trusted dependencies, preserving relative workspace links into the **frozen** packages. Do not symlink the whole `node_modules` directory to a mutable checkout. Build only trusted language/core/tooling on the host, not evaluation fixtures. The full regression checks below run in Docker.

```bash
test -d "$REPO/node_modules" && test ! -e "$FROZEN/node_modules" && \
  cp -a "$REPO/node_modules" "$FROZEN/node_modules"
cd "$FROZEN"
node -p 'require("./node_modules/typescript/package.json").version'
npm run langium:generate --silent && \
  node node_modules/typescript/bin/tsc -b tooling/tsconfig.json packages/runtime/tsconfig.json --pretty false && \
  node experiments/contact-onboarding/prepare.mjs "$STAGE" \
    2>&1 | tee "$RUN/controller/logs/preparation.txt"
```

Require TypeScript **5.9.3** and the preparation `PASS` message. Preparation checks the exact source/binding, shared descriptors, strict codec round-trip, two byte-identical eight-file M2 derivations and conventional declaration agreement. The staged `PREPARATION.txt` is a historical review marker, **not** launch approval. Preserve both M2 symlinks/backing directories while staging exists; selected delivery directories below are real copies.

**TERMINAL — Bash.** Ensure the already pinned public image exists, then run the frozen trusted controls and repository regressions. Image acquisition is trusted preparation; it is not candidate networking. Do not send any prompt to test provider availability.

```bash
export IMAGE=node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker pull "$IMAGE"
bash "$ASSETS/check-controls.sh" "$STAGE" \
  2>&1 | tee "$RUN/controller/logs/trusted-controls.txt"
```

Require all expected-positive/negative/private/lifecycle controls to pass. Then:

```bash
bash "$ASSETS/check-regressions.sh" "$STAGE" \
  2>&1 | tee "$RUN/controller/logs/regressions.txt"
```

Require **416 tests / 17 files**, typecheck/build, three demos, Hello World and canonical export comparison. These are readiness observations, **not pilot results**. Both scripts deliberately require fresh staging subdirectories; do not rerun them over existing outputs to hide a failure. An infrastructure problem stops the trial for review. Record preparation time separately.

**TERMINAL — Bash.** Materialize **only the respective eight-file package** in each workspace. Never copy the M2 output parent, tests, source architecture, baseline or controls there.

```bash
cp -R "$STAGE/NormalizeContact/handoff" "$RUN/agents/A/handoff"
cp -R "$STAGE/RenderWelcome/handoff" "$RUN/agents/B/handoff"
find "$RUN/agents/A/handoff" -type f -printf '%P\n' | sort
find "$RUN/agents/B/handoff" -type f -printf '%P\n' | sort
diff -ru "$STAGE/NormalizeContact/handoff" "$RUN/agents/A/handoff"
diff -ru "$STAGE/RenderWelcome/handoff" "$RUN/agents/B/handoff"
chmod -R a-w "$RUN/agents/A/handoff" "$RUN/agents/B/handoff"
cp "$ASSETS/events.md" "$RUN/controller/results.md"
```

Each listing must contain exactly:

```text
README.md
contract.box-spec.json
generated/contract.d.ts
handoff.json
policy.md
scope.md
seed/implementation.ts
task.md
```

Do not attach this guide, `results.md`, the control checkout, hidden corpus, peer files/history or baseline to either agent. Human originals/logs/sessions/submissions remain outside both workspaces. Read-only permissions are organizational protection, not an OS sandbox or authenticated evidence.

## 3. Define the native Pi profile — no model call yet

**TERMINAL — Bash.** The same array is used in all four possible manual launches. No SDK, extension, launcher script or orchestration service is created.

```bash
PI_FLAGS=(
  --provider openai-codex --model gpt-6.1-sol --thinking medium
  --no-tools --exclude-tools '*'
  --no-extensions --no-mcp --no-skills --no-prompt-templates
  --no-themes --no-context-files --no-approve
  --system-prompt "$ASSETS/generation.md"
  --verbose
)
```

Global append instructions are separate from `AGENTS.md` discovery. **TERMINAL — Bash:** check metadata only; do not print configuration/credential contents or move global files.

```bash
NATIVE_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
if [[ "$NATIVE_AGENT_DIR" != /* ]]; then
  printf 'STOP: relative PI_CODING_AGENT_DIR needs review before changing cwd.\n'
elif test -e "$NATIVE_AGENT_DIR/APPEND_SYSTEM.md"; then
  printf 'STOP: unreviewed global APPEND_SYSTEM.md; do not launch either session.\n'
else
  printf 'No global APPEND_SYSTEM.md found.\n'
fi
```

A STOP above is a stop, **not** an invitation to change your native profile. The explicit system prompt replaces the default; context/resource discovery, extensions and MCP are disabled. Verify the exact flags and startup resource display: no unexpected instructions/resources and model/thinking exactly as above. Record the declared empty selection from the stock **`--no-tools --exclude-tools '*'`** semantics with extensions/MCP disabled. Pi 1.4 does **not** have a built-in `/tools` command; `/session` showing zero *calls* is usage, not a list of available tools. Do not ask the model to attest its tools: that would consume an extra inference and would not prove enforcement. If flags are unsupported or startup contradicts this profile, quit and report before prompting.

Do **not** pipe/redirect the Pi launch through `tee` or into a file: non-TTY stdin/stdout selects print mode. We use the interactive terminal UI so you can inspect startup before sending the first prompt. Native session persistence captures the conversation privately; `/copy` captures the raw last answer. Do not use `/share`, `/export`, `/bug`, `/debug`, `!`, `!!`, `/reload`, `/new`, `/fork`, `/clone`, `/tree`, `/import`, `/compact` or model/settings changes in the trial. Use only the local commands explicitly shown below. `/session` and `/copy` do not call the model.

## 4. Agent A — initial episode (NormalizeContact)

**TERMINAL — Bash.** The session directory must still be empty. This launch intentionally supplies **no initial prompt or `@file` arguments**; wait for Pi's editor. The wall timer includes startup/operator time, conservatively within the 30-minute episode. `--foreground` lets the interactive program read the terminal. The timer bounds the native client, not a security sandbox.

```bash
test -z "$(find "$RUN/controller/sessions/A" -type f -print -quit)" && \
  (cd "$RUN/agents/A" && \
   timeout --foreground --signal=TERM --kill-after=5s 30m \
     "$PI_BIN" "${PI_FLAGS[@]}" --session-dir "$RUN/controller/sessions/A" \
        --session-id M3-ContactOnboarding-01-A --name M3-ContactOnboarding-01-A)
```

**PI — local command**, after inspecting startup:

```text
/session
```

Record its session file/ID and initial zero conversation messages, model, thinking and usage in your private notes. If old messages appear, do not prompt: stop the independence violation. Confirm the empty configured tool selection as described above.

**PI — send to Agent A.** Paste the following **single line**, then press Enter once. `@handoff/...` instructs Pi itself to embed exactly these controller-selected text files from A's current directory; it does not enable a model-callable file tool. The common frozen `generation.md` is already the system prompt. Do not add any architecture, algorithms or extra files.

```text
@handoff/handoff.json @handoff/README.md @handoff/contract.box-spec.json @handoff/task.md @handoff/scope.md @handoff/policy.md @handoff/generated/contract.d.ts @handoff/seed/implementation.ts Implement only your assigned operation from these eight files and the common system instructions. Emit complete permitted TypeScript files as text and finish with READY, CLARIFICATION, or ARCHITECTURE_PROPOSAL.
```

Wait for its response. Do not steer, queue another message, approve tools or request private execution. At READY, clarification/proposal, interruption or budget exhaustion the episode ends. A request to change architecture/resolve missing or conflicting intent stops the **trial**, not a chance to coach B. An unambiguous existing-text clarification ends A's initial episode and is held until after B's initial episode; the only possible continuation is A's one revision.

At a normal completed response, **PI — local commands**, one at a time:

```text
/session
```

Record turns, elapsed time, token/cost metadata (or `unknown`) and any automatic activity. Then:

```text
/copy
```

This copies the **raw last assistant response**, not rendered terminal code. Then:

```text
/quit
```

If generation must be interrupted, press **Escape**, then quit; retain the partial history and record the outcome. A timeout/nonzero client exit is not permission to relaunch. Do not submit another prompt simply to obtain a cleaner copy. All keybindings assume stock Pi defaults; use the slash commands rather than guessing reconfigured shortcuts.

## 5. Save A's response and inert source — ordinary terminal only

**TERMINAL — Bash.** Immediately after returning from A's Pi invocation, before any other terminal command, record its exit status. Do not proceed as if a timeout/aborted/incomplete response were a clean submission.

```bash
PI_EXIT_A=$?
printf 'pi=%s\n' "$PI_EXIT_A" | tee "$RUN/controller/logs/A-initial-client.status"
```

**TERMINAL — Bash.** Start this command, paste the **entire copied answer as data**, including its file labels/fences/status, then press **Ctrl+D on an empty line**. If no final newline was pasted, ensure the last complete line is submitted before EOF. `dd` is reading stdin; the pasted text is **not evaluated by Bash**. Do not use a shell heredoc or paste generated code at a shell prompt. `conv=excl` refuses overwrite.

```bash
dd of="$RUN/controller/responses/A-initial.md" conv=excl status=none
```

If no complete usable source was submitted, **skip the source-writing commands**: keep the raw answer/history, record no usable candidate and all checks unrun. A scope/architecture/infrastructure stop ends the trial; an unambiguous existing-text clarification can wait until after B's initial episode for the single permitted A revision. Never write a dummy implementation. Otherwise, mechanically identify each complete permitted `candidate/...ts` block in that answer. Reject absolute paths, `..` traversal, links, `.d.ts`, configs/manifests/resources, unexpected public entrypoints or more than 10 MiB of submitted source. Ambiguous/incomplete output is a logged clarification/failure, **not a transcription repair**. Do not invent missing code, fix syntax/logic, rename fields, add declarations or run suggested commands.

**TERMINAL — Bash.** For the required file, run this command, paste **only the exact TypeScript body** (no Markdown fence/path/status), including its final newline, and end stdin with Ctrl+D on an empty line:

```bash
mkdir -p "$RUN/submissions/A/initial/candidate"
dd of="$RUN/submissions/A/initial/candidate/implementation.ts" conv=excl status=none
```

For any additional permitted private helper/test, create its reported subdirectory under that same `candidate/`, then use `dd conv=excl` with its exact reported relative filename. For example, only if the answer actually contains `candidate/private-tests.ts`:

```bash
dd of="$RUN/submissions/A/initial/candidate/private-tests.ts" conv=excl status=none
```

Compare saved bodies visually with the raw copied answer in a **non-executing plain-text viewer**, without hooks/language-server builds. A clearly identified paste error may be mechanically recopied from that same original answer to a new local file and logged as transcription overhead; no substantive correction is allowed. Never compile or import to help decide how to fix it. Freeze the snapshot after checking the copy:

```bash
if test -d "$RUN/submissions/A/initial"; then chmod -R a-w "$RUN/submissions/A/initial"; fi
SESSION_A="$(find "$RUN/controller/sessions/A" -maxdepth 1 -type f -name '*.jsonl' -print)"
test -f "$SESSION_A" && printf '%s\n' "$SESSION_A" > "$RUN/controller/session-A.path"
diff -ru "$STAGE/NormalizeContact/handoff" "$RUN/agents/A/handoff"
```

The session lookup must produce **exactly one existing file**, matching `/session`; multiple/missing files are a stop, not permission to choose another history. Record the initial snapshot even if no usable code was submitted. **No acceptance feedback, checks/revision discussion with A, or B context leakage before both initial responses/snapshots are collected.**

## 6. Agent B — independent initial episode (RenderWelcome)

Keep A closed. Do not carry A's question, code, tests, output, failures or lessons into B. B gets the identical fixed prompt structure, only its own eight files. **TERMINAL — Bash:**

```bash
test -z "$(find "$RUN/controller/sessions/B" -type f -print -quit)" && \
  (cd "$RUN/agents/B" && \
   timeout --foreground --signal=TERM --kill-after=5s 30m \
     "$PI_BIN" "${PI_FLAGS[@]}" --session-dir "$RUN/controller/sessions/B" \
        --session-id M3-ContactOnboarding-01-B --name M3-ContactOnboarding-01-B)
```

Inspect startup and run **PI — local command** `/session` exactly as for A. Require an empty history, the same model/thinking and empty configured tool selection. Then **PI — send to Agent B** (same line as A):

```text
@handoff/handoff.json @handoff/README.md @handoff/contract.box-spec.json @handoff/task.md @handoff/scope.md @handoff/policy.md @handoff/generated/contract.d.ts @handoff/seed/implementation.ts Implement only your assigned operation from these eight files and the common system instructions. Emit complete permitted TypeScript files as text and finish with READY, CLARIFICATION, or ARCHITECTURE_PROPOSAL.
```

At episode end, record `/session`, use `/copy`, then `/quit`. Follow the same interrupt/stop rules. **TERMINAL — Bash:** immediately on returning, record the client exit status:

```bash
PI_EXIT_B=$?
printf 'pi=%s\n' "$PI_EXIT_B" | tee "$RUN/controller/logs/B-initial-client.status"
```

Paste the entire raw response into this command and end with Ctrl+D:

```bash
dd of="$RUN/controller/responses/B-initial.md" conv=excl status=none
```

Only if complete usable source was actually submitted, paste the required source body into the following `dd`, ending with Ctrl+D. Otherwise skip source writing and record no usable candidate/all checks unrun. Repeat for any permitted helpers, just as for A.

```bash
mkdir -p "$RUN/submissions/B/initial/candidate"
dd of="$RUN/submissions/B/initial/candidate/implementation.ts" conv=excl status=none
```

Run the block **one command at a time**: each `dd` waits for its own pasted data/EOF before the next command. Freeze and record:

```bash
if test -d "$RUN/submissions/B/initial"; then chmod -R a-w "$RUN/submissions/B/initial"; fi
SESSION_B="$(find "$RUN/controller/sessions/B" -maxdepth 1 -type f -name '*.jsonl' -print)"
test -f "$SESSION_B" && printf '%s\n' "$SESSION_B" > "$RUN/controller/session-B.path"
diff -ru "$STAGE/RenderWelcome/handoff" "$RUN/agents/B/handoff"
```

Both initial snapshots now exist. If an episode ended without code, keep its raw response/history and record all checks unrun; do not fabricate an implementation file. A scope/architecture/infrastructure/context stop takes precedence over proceeding to evaluations.

## 7. Evaluate both initial snapshots — Docker only

A nonzero evaluation result is data to classify, not permission to edit code. Check **both** exit codes printed below: the evaluator and log writer must succeed for an observed pass. Keep raw logs private; they can contain hidden expected values and untrusted output. Do not paste them wholesale into either Pi session.

For each snapshot, optionally run each explicitly supplied private-test entrypoint in a **separate fresh container** before independent acceptance; this does not replace acceptance. Example for an actual `candidate/private-tests.ts` in A's submission:

**TERMINAL — Bash:**

```bash
bash "$ASSETS/evaluate.sh" "$STAGE" normalize \
  "$RUN/submissions/A/initial/candidate" private:private-tests.js \
  2>&1 | tee "$RUN/controller/logs/A-initial-private.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/A-initial-private.status"
```

For an actually supplied B `candidate/private-tests.ts`, the corresponding **TERMINAL — Bash** block is:

```bash
bash "$ASSETS/evaluate.sh" "$STAGE" render \
  "$RUN/submissions/B/initial/candidate" private:private-tests.js \
  2>&1 | tee "$RUN/controller/logs/B-initial-private.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/B-initial-private.status"
```

The selector is the **emitted relative `.js` path**, not a host executable; include it only when the corresponding `.ts` file was actually supplied. No automatic private-test discovery or host execution. Record all selected private checks, including failures.

**TERMINAL — Bash:** full A independent suite, then full B independent suite. Skip a missing/unusable snapshot and explicitly record its stage/all rows unrun rather than creating dummy source.

```bash
bash "$ASSETS/evaluate.sh" "$STAGE" normalize "$RUN/submissions/A/initial/candidate" \
  2>&1 | tee "$RUN/controller/logs/A-initial.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/A-initial.status"
```

```bash
bash "$ASSETS/evaluate.sh" "$STAGE" render "$RUN/submissions/B/initial/candidate" \
  2>&1 | tee "$RUN/controller/logs/B-initial.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/B-initial.status"
```

Expected positive output: inspected container settings, strict NodeNext/named-export compilation with erased declaration imports, then **39 normalizer** or **24 renderer** independent rows, repeated-call equality and unchanged inputs. This is not acceptance merely because an agent said READY.

Frozen evaluator limits: 1 CPU, 512 MiB, 64 PIDs; read-only selected source/handoff/tests/library/compiler mounts; private scratch; nonroot/dropped capabilities/no-new-privileges; no credentials/socket/home/full repository/host namespaces; network none. Build/suite each at most 60 seconds, outer 130-second deadline with full-container cleanup. Source cap is 10 MiB, not a hard host disk quota. Do not change these settings to make a candidate pass.

## 8. At most one own-history revision per Box

If a revision response contains no complete usable source, retain its raw answer/history, skip that Box's source-writing/evaluation commands below and report the exhausted Box failure. Do not create dummy source or add another episode.

Only after **both initial snapshots** and their available independent results are recorded: an existing-text clarification, own-source compile/export failure, M1/behavioral failure or private-check failure may use that Box's one revision episode. Process A then B if needed. A passing initial submission needs no optimization round. Preserve all failed initial source/results.

Allowed feedback: an exact pointer to already supplied text; exact **own-source compiler diagnostics**; or **requirement ID plus failure class**. Do not give hidden case IDs/data/expected values, algorithms, fixes, architecture originals or peer source/history/results. Source-conflicting/missing intent, new dependencies or architecture requests stop the trial for Product Owner review/new trial; infrastructure failure stops without a replacement run. Integration will have no repair round.

**TERMINAL — Bash: A revision, only if actually needed and allowed.** The file is the exact same saved session, not a fresh/forked history. Do not use `--continue`, `--resume` or `--session-id` as a fallback if the path is missing.

```bash
test -f "$SESSION_A" && \
  (cd "$RUN/agents/A" && \
   timeout --foreground --signal=TERM --kill-after=5s 30m \
     "$PI_BIN" "${PI_FLAGS[@]}" --session-dir "$RUN/controller/sessions/A" --session "$SESSION_A")
```

**PI — local command:** `/session`. Verify the exact A file/ID and own history; no B material. **PI — send to A**, using this template after replacing the bracketed fields with only permitted feedback (do not send unfilled brackets):

```text
This is your one permitted revision episode. Use only your existing own handoff and history. Verification: [own failure class and applicable supplied requirement IDs, or existing-text clarification pointer]. [Include exact own-source compiler diagnostics only when applicable; otherwise omit this sentence.] Emit the complete permitted TypeScript source set, including unchanged helpers, as full files, not patches. Do not change interfaces, responsibilities or dependencies. Finish with READY, CLARIFICATION, or ARCHITECTURE_PROPOSAL.
```

At episode end record `/session`, `/copy`, `/quit`. Save the entire raw answer into a **new** `A-revision.md`, then exact complete file bodies under **new** `A/revision/candidate/`; do not edit/overwrite the initial snapshot. The revision must supply the complete selected source set; ambiguous partial/diff-only output is not permission for human code assembly/repair.

**TERMINAL — Bash:** immediately record the client exit code, then capture raw text:

```bash
PI_EXIT_A_REV=$?
printf 'pi=%s\n' "$PI_EXIT_A_REV" | tee "$RUN/controller/logs/A-revision-client.status"
```

```bash
dd of="$RUN/controller/responses/A-revision.md" conv=excl status=none
```

After its data/EOF, save only the implementation body with its own data/EOF:

```bash
mkdir -p "$RUN/submissions/A/revision/candidate"
dd of="$RUN/submissions/A/revision/candidate/implementation.ts" conv=excl status=none
```

If no complete usable revision source was supplied, skip source-writing/evaluation commands, retain the raw response/history and report the exhausted Box failure. Never fabricate source or merge ambiguous patches. Otherwise save every complete permitted helper, freeze that snapshot, run any explicitly selected private checks as in Section 7 (use `/revision/candidate` and distinct revision-private log names), then rerun the **entire** independent suite:

```bash
chmod -R a-w "$RUN/submissions/A/revision"
bash "$ASSETS/evaluate.sh" "$STAGE" normalize "$RUN/submissions/A/revision/candidate" \
  2>&1 | tee "$RUN/controller/logs/A-revision.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/A-revision.status"
```

**TERMINAL — Bash: B revision**, separately and only if needed/allowed:

```bash
test -f "$SESSION_B" && \
  (cd "$RUN/agents/B" && \
   timeout --foreground --signal=TERM --kill-after=5s 30m \
     "$PI_BIN" "${PI_FLAGS[@]}" --session-dir "$RUN/controller/sessions/B" --session "$SESSION_B")
```

Use `/session` to verify B, then the same **revision prompt template** with **only B feedback**. Record `/session`, `/copy`, `/quit`. **TERMINAL — Bash:** immediately capture the client exit code, then save each text with its own data/EOF:

```bash
PI_EXIT_B_REV=$?
printf 'pi=%s\n' "$PI_EXIT_B_REV" | tee "$RUN/controller/logs/B-revision-client.status"
```

```bash
dd of="$RUN/controller/responses/B-revision.md" conv=excl status=none
```

```bash
mkdir -p "$RUN/submissions/B/revision/candidate"
dd of="$RUN/submissions/B/revision/candidate/implementation.ts" conv=excl status=none
```

Save any complete permitted helpers, freeze it, run selected private checks, then:

```bash
chmod -R a-w "$RUN/submissions/B/revision"
bash "$ASSETS/evaluate.sh" "$STAGE" render "$RUN/submissions/B/revision/candidate" \
  2>&1 | tee "$RUN/controller/logs/B-revision.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/B-revision.status"
```

No second revision, extra agent, clean restart, budget reset, compiler/config/test tweak or manual implementation repair. Record a failed/exhausted Box and all unrun integration work if there is no eligible passing pair. Do not relaunch to hide an interruption or choose among undisclosed runs.

## 9. Freeze the selected passing pair, then integrate once

Both Pi sessions must be stopped. Select the independently passing initial snapshot for a Box with no revision, or its independently passing permitted revision. No best-of-unreported variants. Record first-pass versus revision-assisted success. If either Box lacks an eligible passing snapshot, report failure and integration **unrun**.

**TERMINAL — Bash.** Set the actual selected paths; change an assignment to `/revision/candidate` only when that permitted revision passed. Never point to a mutable agent workspace.

```bash
A_SELECTED="$RUN/submissions/A/initial/candidate"
B_SELECTED="$RUN/submissions/B/initial/candidate"
# Only if the respective passing revision is selected, use these assignments instead:
# A_SELECTED="$RUN/submissions/A/revision/candidate"
# B_SELECTED="$RUN/submissions/B/revision/candidate"
diff -ru "$STAGE/NormalizeContact/handoff" "$RUN/agents/A/handoff"
diff -ru "$STAGE/RenderWelcome/handoff" "$RUN/agents/B/handoff"
git -C "$FROZEN" diff --exit-code "$FREEZE" -- experiments/contact-onboarding
printf 'freeze=%s\nA=%s\nB=%s\n' "$FREEZE" "$A_SELECTED" "$B_SELECTED" \
  > "$RUN/controller/selected-pair.txt"
```

Any protected-input difference is a stop. Only after recording this selection, **TERMINAL — Bash**:

```bash
bash "$ASSETS/evaluate.sh" "$STAGE" integration "$A_SELECTED" "$B_SELECTED" \
  2>&1 | tee "$RUN/controller/logs/integration.txt"
codes=("${PIPESTATUS[@]}")
printf 'evaluator=%s log=%s\n' "${codes[0]}" "${codes[1]}" \
  | tee "$RUN/controller/logs/integration.status"
```

Require both compilations and **18 complete intermediate/final rows plus the live-identity probe**. The prewritten wiring invokes normalizer via strict-decoded M1, then passes the **unchanged live output** to renderer via M1; no conversion/default/renaming/architecture change. Integration failure is a result: **do not repair implementations, interfaces, tests or wiring in this trial**. An unchanged reproducibility rerun must be explicitly labelled/logged, never used to select a different candidate or conceal a failure.

## 10. Record and return the final result

Complete the private `$RUN/controller/results.md` copied from the frozen event template, using a non-executing text editor/viewer. Include:

1. Run ID, frozen Git revision, actual versions/model/thinking, initial tool/resource checks, supplied own files/bytes and exact session/snapshot paths. No peer context was supplied; report any attempted/denied/successful violation.
2. Every episode/clarification/feedback/interruption/revision and its elapsed time/turns; automatic model activity/transport retries; tokens/cost or **unknown**. Capture `/session` metadata before closing each episode. A UI/catalog estimate (even zero) is not proof of actual subscription/provider charges; report estimates separately and real charges `unknown` when unobservable. No fabricated zeros for unavailable billing or human effort.
3. Exact source set selected for each Box, all initial/revision results, private-check entries, compile/export/load/M1/functional outcomes, evaluator/log exit codes, first failed stage/requirement/row and **every remaining unrun row** in the frozen array order. Setup/load failure leaves all rows unrun. Invalid-input/no-invocation controls are not business BAD_DAYS results; inspection failure is not a proven mismatch.
4. Integration selected-pair record, full intermediate/final outcome summary and cleanup. First-submission unassisted success must remain distinct from permitted-revision success; failed/inconclusive trials remain failed/inconclusive.
5. Human preparation/review/transcription/coordination minutes and container/check time, separated from agent time. Planned launch/copy/check actions are operational overhead, not hidden interventions; count every unplanned pointer, diagnostic feedback, recovery or permission/context decision. Preserve architecture-change proposals, including denied ones. Include setup effort in total workflow cost.

For unrun-case accounting you can list the **trusted frozen data's** row IDs (never attach these lists to agents). **TERMINAL — Bash:**

```bash
grep '"id":' "$ASSETS/tests/normalize.json"
grep '"id":' "$ASSETS/tests/render.json"
grep '"id":' "$ASSETS/tests/integration.json"
```

**TERMINAL — Bash:** confirm no evaluation container is left. This lists matching containers; do not indiscriminately remove unrelated containers or rerun a trial to clear evidence.

```bash
docker ps -a --filter 'name=boundscript-contact-'
printf 'Private results: %s\n' "$RUN/controller/results.md"
printf 'Selected pair: %s\n' "$RUN/controller/selected-pair.txt"
```

The frozen evaluation scripts remove their own full containers/descendants on exit, failure or timeout. If something survives, record an infrastructure failure and stop for review; do not invoke the candidate on the host. Retain local histories/snapshots/logs until review; do not delete a failed attempt. No raw session, source submission, generated handoff/build, transcript, credential or unreviewed log goes into Git or a sharing service. Return only a **reviewed redacted report** to the Product Owner. No automatic promotion, M3 completion or M6 baseline execution follows from a pass.

**Residual risk:** native Pi/operator are trusted host software using native authentication; tools-off/directories are not OS isolation. Docker shares its kernel and trusts the image/runtime. Candidate code can read mounted tests or tamper with the shared JavaScript realm; read-only originals preserve file authority, not secrecy or authenticated outcomes. Finite tests do not prove arbitrary correctness/purity. No new framework, provider adapter, proxy, orchestration or security attestation is introduced by this manual guide.

**Documentation validation:** commands and local slash-command behavior were checked against the installed Pi 1.4 CLI/usage/session/settings documentation and frozen scripts; shell blocks are syntax-checked. No live Pi generation, provider/auth probe, candidate execution or container launch was performed to write this guide. Wait for the Product Owner's execution confirmation and spending-policy approval before beginning.
