#!/usr/bin/env node
// Fixed Assignment 0022 recipe. Candidate source is only ever inert text on the host.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { closeSync, openSync, writeSync } from 'node:fs';
import { chmod, cp, mkdir, readFile, readdir, writeFile, access, realpath } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline/promises';

export const FREEZE = 'aee34e3f8445f1a0285c120f2a2bca5ef0b3e3f9';
const IMAGE = 'node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205';
const PROFILE = ['--provider', 'openai-codex', '--model', 'gpt-6.1-sol', '--thinking', 'medium',
    '--no-tools', '--exclude-tools', '*', '--no-extensions', '--no-mcp', '--no-skills',
    '--no-prompt-templates', '--no-themes', '--no-context-files', '--no-approve'];
const FILES = ['handoff.json', 'README.md', 'contract.box-spec.json', 'task.md', 'scope.md',
    'policy.md', 'generated/contract.d.ts', 'seed/implementation.ts'];
const BOXES = [['A', 'NormalizeContact', 'normalize', 39], ['B', 'RenderWelcome', 'render', 24]];
const PROMPT = 'Implement only your assigned operation from these eight files and the common system instructions. Emit complete permitted TypeScript files as text and finish with READY, CLARIFICATION, or ARCHITECTURE_PROPOSAL.';

// No shell interpolation, no candidate-chosen commands. Logs are private, bounded data.
export function command(executable, args, { cwd, log, timeout = 900_000, onLine, limit = 32 * 1024 * 1024 } = {}) {
    return new Promise((resolve, reject) => {
        const out = openSync(log, 'wx', 0o600), err = openSync(`${log}.stderr`, 'wx', 0o600);
        const child = spawn(executable, args, { cwd, detached: true, stdio: ['ignore', 'pipe', 'pipe'] });
        let stdout = '', pending = '', size = 0, failure, killer;
        const stop = error => {
            if (failure) return;
            failure = error;
            try { process.kill(-child.pid, 'SIGTERM'); } catch { /* already exited */ }
            killer = setTimeout(() => { try { process.kill(-child.pid, 'SIGKILL'); } catch { /* exited */ } }, 5000);
        };
        const interrupted = () => stop(Error('Operator interrupted; trial stopped'));
        process.once('SIGINT', interrupted); process.once('SIGTERM', interrupted);
        const timer = setTimeout(() => stop(Error('Command deadline exceeded; trial stopped')), timeout);
        child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
        const consume = (chunk, fd, isOut) => {
            if (failure) return;
            try {
                size += Buffer.byteLength(chunk);
                assert.ok(size <= limit, 'Command output limit exceeded');
                writeSync(fd, chunk);
                if (isOut) {
                    stdout += chunk;
                    pending += chunk;
                    let end;
                    while ((end = pending.indexOf('\n')) !== -1) {
                        const line = pending.slice(0, end).replace(/\r$/, '');
                        pending = pending.slice(end + 1);
                        onLine?.(line);
                    }
                }
            } catch (error) { stop(error); }
        };
        child.stdout.on('data', chunk => consume(chunk, out, true));
        child.stderr.on('data', chunk => consume(chunk, err, false));
        child.on('error', error => { failure = error; });
        child.on('close', (code, signal) => {
            clearTimeout(timer); clearTimeout(killer);
            process.removeListener('SIGINT', interrupted); process.removeListener('SIGTERM', interrupted);
            closeSync(out); closeSync(err);
            if (onLine && pending) failure ??= Error('Incomplete JSONL record');
            if (failure) reject(failure);
            else resolve({ code, signal, stdout });
        });
    });
}

// Deliberately conservative: one complete tools-off response, no recovery or hidden extra inference.
export function eventReader() {
    const state = { header: null, started: false, turns: 0, message: null, turnEnded: false, ended: false, settled: false };
    return { state, line(line) {
        const e = JSON.parse(line);
        assert.ok(e && typeof e.type === 'string' && !state.settled, 'Invalid/post-settlement event');
        assert.ok(!/^(tool_|auto_retry|compaction|summarization|queue_|entry_)/.test(e.type), 'Unexpected tools, retry, compaction or queued work');
        if (e.type === 'session') {
            assert.ok(!state.header && !state.turns, 'Duplicate/late session header'); state.header = e;
        } else {
            assert.ok(state.header, 'Missing session header');
            if (e.type === 'agent_start') { assert.equal(state.started, false); state.started = true; }
            if (e.type === 'turn_start') { assert.ok(state.started); assert.equal(++state.turns, 1, 'Unexpected additional model response'); }
            if (e.type === 'message_end') {
                const m = e.message;
                if (m.role === 'assistant') {
                    assert.equal(state.turns, 1); assert.equal(state.message, null);
                    assert.equal(m.stopReason, 'stop', 'Incomplete/failed assistant response');
                    assert.equal(m.provider, 'openai-codex'); assert.equal(m.model, 'gpt-6.1-sol');
                    if (m.thinkingLevel !== undefined) assert.equal(m.thinkingLevel, 'medium');
                    assert.ok(Array.isArray(m.content) && m.content.every(b => ['text', 'thinking'].includes(b.type)), 'Non-text/tool response');
                    state.message = m;
                } else {
                    assert.ok(['system', 'user'].includes(m.role), 'Unexpected message role');
                    assert.ok(!m.toolsAdded?.length, 'Nonempty declared tools');
                }
            }
            if (e.type === 'message_update') assert.ok(!e.assistantMessageEvent?.type?.startsWith('toolcall'), 'Attempted tool call');
            if (e.type === 'turn_end') { assert.ok(state.message && !state.turnEnded); assert.deepEqual(e.toolResults, []); state.turnEnded = true; }
            if (e.type === 'agent_end') { assert.ok(state.turnEnded && !state.ended); assert.equal(e.willRetry, false); state.ended = true; }
            if (e.type === 'agent_settled') {
                assert.equal(e.aborted, false); assert.ok(state.ended && state.message); state.settled = true;
            }
            assert.ok(['agent_start', 'turn_start', 'message_start', 'message_update', 'message_end',
                'turn_end', 'agent_end', 'agent_settled', 'session_info_changed'].includes(e.type), `Unexpected event: ${e.type}`);
        }
    } };
}

export function extractSource(text) {
    assert.equal(text.trimEnd().split('\n').at(-1), 'READY', 'Response must finish with READY; clarification/proposal stops for review');
    const sources = new Map();
    // Accept an optional Markdown heading/backticks around a standalone exact file label.
    const block = /^(?:#{1,6} )?`?(candidate\/[A-Za-z0-9_./-]+\.ts)`?\r?\n```(?:typescript|ts)\r?\n([\s\S]*?)^```\r?$/gm;
    let match, remainder = text;
    while ((match = block.exec(text))) {
        const [, name, body] = match;
        assert.ok(!name.split('/').some(p => !p || p === '.' || p === '..' || p === '.pi'), 'Unsafe source path');
        assert.ok(!name.endsWith('.d.ts') && !sources.has(name) && body.trim(), 'Duplicate/declaration/empty source');
        sources.set(name, body); remainder = remainder.replace(match[0], '');
    }
    assert.ok(sources.has('candidate/implementation.ts'), 'Missing complete implementation');
    assert.equal(remainder.trim(), 'READY', 'Ambiguous response outside labelled source blocks');
    assert.ok([...sources.values()].reduce((n, s) => n + Buffer.byteLength(s), 0) <= 10485760, 'Source exceeds 10 MiB');
    return sources;
}

async function lockTree(dir) {
    for (const e of await readdir(dir, { withFileTypes: true })) {
        const p = path.join(dir, e.name);
        if (e.isDirectory()) await lockTree(p);
        else { assert.ok(e.isFile(), 'Unexpected link/special file'); await chmod(p, 0o444); }
    }
    await chmod(dir, 0o555);
}

async function snapshot(dir, sources) {
    await mkdir(dir);
    for (const [name, body] of sources) {
        const target = path.join(dir, name);
        await mkdir(path.dirname(target), { recursive: true });
        await writeFile(target, body, { flag: 'wx', mode: 0o444 });
    }
    // No links or existing paths can enter a new, controller-created snapshot.
    await lockTree(dir);
    return path.join(dir, 'candidate');
}

export async function checkNativeProfile(agentDir) {
    assert.ok(path.isAbsolute(agentDir), 'Relative native agent directory');
    await access(path.join(agentDir, 'APPEND_SYSTEM.md')).then(() => { throw Error('Global APPEND_SYSTEM.md requires review'); }, e => { if (e.code !== 'ENOENT') throw e; });
    let warming;
    try { warming = JSON.parse(await readFile(path.join(agentDir, 'settings.json'), 'utf8')).cacheWarming; }
    catch { throw Error('Cannot verify native cache-warming setting; profile review required'); }
    // Streaming is Pi 1.4's default and can make extra, unprompted model requests.
    assert.equal(warming, 'off', 'Native cacheWarming must already be off; no global settings are changed by this runner');
}

export async function runPilot({ repo, runDir, ask, exec = command, pi = 'pi', signal,
    agentDir = process.env.PI_CODING_AGENT_DIR ?? path.join(process.env.HOME, '.pi/agent') }) {
    assert.ok(path.isAbsolute(runDir), 'Absolute run directory required');
    repo = await realpath(repo);
    runDir = path.join(await realpath(path.dirname(runDir)), path.basename(runDir));
    assert.ok(path.relative(repo, runDir).startsWith(`..${path.sep}`), 'Run directory must be outside the repository');
    await mkdir(runDir, { mode: 0o700 }); // Never reuse/overwrite a trial.
    const frozen = path.join(runDir, 'frozen'), stage = path.join(runDir, 'stage');
    const assets = path.join(frozen, 'experiments/contact-onboarding');
    const report = { freeze: FREEZE, status: 'incomplete', integration: 'unrun', episodes: [], evaluations: [],
        actualCharges: 'unknown', humanActiveMinutes: 'unknown', transportRetriesNotExposed: 'unknown',
        limitations: 'Directories are not OS sandboxes. Docker/shared-realm results are not authenticated. Review raw logs privately. No automatic M3 closure or baseline execution.' };
    let sequence = 0, containersUsed = false;
    report.versions = {}; report.contexts = {};
    const call = async (exe, args, options = {}) => {
        assert.ok(!signal?.aborted || options.cleanup, 'Operator interrupted; trial stopped');
        return exec(exe, args, { cwd: frozen, log: path.join(runDir, `${++sequence}-${path.basename(exe)}.log`), ...options });
    };
    const must = async (exe, args, options) => {
        const r = await call(exe, args, options); assert.equal(r.code, 0, `${exe} failed; inspect private logs`); return r;
    };
    const unchanged = async () => {
        await must('git', ['diff', '--exit-code', FREEZE, '--', 'experiments/contact-onboarding']);
        for (const [id, box] of BOXES) await must('diff', ['-r', path.join(stage, box, 'handoff'), path.join(runDir, id, 'handoff')]);
    };
    try {
        console.log(`Private trial directory: ${runDir}\nFrozen inputs: ${FREEZE}\nModel: openai-codex/gpt-6.1-sol, medium; at most four one-response episodes, 30 minutes each.`);
        assert.equal(await ask('Authorize this single trial now? Type RUN: '), 'RUN', 'Execution not confirmed');
        report.spendingPolicy = await ask('Enter approved spending policy (usage-time-only, or externally-enforced with description): ');
        assert.ok(/^(usage-time-only|externally-enforced .+)$/.test(report.spendingPolicy), 'Approved spending policy required');
        report.started = new Date().toISOString();
        await checkNativeProfile(agentDir);
        report.cacheWarming = 'off';
        await must('git', ['worktree', 'add', '--detach', frozen, FREEZE], { cwd: repo });
        await cp(path.join(repo, 'node_modules'), path.join(frozen, 'node_modules'), { recursive: true, verbatimSymlinks: true });
        for (const [exe, args, expected] of [
            [process.execPath, ['--version'], 'v24.16.0'], [pi, ['--version'], '1.4.0'],
            ['docker', ['version', '--format', '{{.Server.Version}}'], '29.1.3'],
            [process.execPath, ['-p', 'require("./node_modules/typescript/package.json").version'], '5.9.3']]) {
            const r = await must(exe, args);
            report.versions[expected] = r.stdout.trim();
            assert.equal(r.stdout.trim(), expected, 'Tool version mismatch; profile review required');
        }
        await must('npm', ['run', 'langium:generate', '--silent']);
        await must(process.execPath, ['node_modules/typescript/bin/tsc', '-b', 'tooling/tsconfig.json', 'packages/runtime/tsconfig.json', '--pretty', 'false']);
        if ((await call('docker', ['image', 'inspect', IMAGE])).code !== 0) await must('docker', ['pull', IMAGE]);
        await must(process.execPath, [path.join(assets, 'prepare.mjs'), stage]);
        containersUsed = true;
        for (const script of ['check-controls.sh', 'check-regressions.sh']) await must('bash', [path.join(assets, script), stage]);
        for (const [id, box] of BOXES) {
            await mkdir(path.join(runDir, id)); await mkdir(path.join(runDir, `sessions-${id}`));
            const handoff = path.join(runDir, id, 'handoff');
            await cp(path.join(stage, box, 'handoff'), handoff, { recursive: true });
            await lockTree(handoff);
            report.contexts[id] = { files: FILES, bytes: 0, declaredTools: [], profile: PROFILE };
            for (const file of FILES) report.contexts[id].bytes += (await readFile(path.join(handoff, file))).length;
        }
        await unchanged();
        const sessions = {}, selected = {};
        const episode = async (id, attempt, feedback) => {
            await checkNativeProfile(agentDir);
            const cwd = path.join(runDir, id), sessionDir = path.join(runDir, `sessions-${id}`);
            const reader = eventReader();
            if (!feedback) assert.deepEqual(await readdir(sessionDir), [], 'Initial session storage not empty');
            const args = [...PROFILE, '--mode', 'json', '--system-prompt', path.join(assets, 'generation.md'), '--session-dir', sessionDir,
                ...(feedback ? ['--session', sessions[id]] : ['--session-id', `M3-ContactOnboarding-01-${id}`]),
                ...(feedback ? [] : FILES.map(f => `@handoff/${f}`)),
                feedback ?? PROMPT];
            const record = { id, attempt, started: new Date().toISOString(), status: 'incomplete', feedback: feedback ?? null };
            report.episodes.push(record);
            let r;
            try { r = await must(pi, args, { cwd, timeout: 30 * 60_000, onLine: reader.line }); }
            finally {
                record.ended = new Date().toISOString(); record.turns = reader.state.turns;
                record.usage = reader.state.message?.usage ?? 'unknown'; record.sessionDir = sessionDir;
            }
            assert.ok(reader.state.settled && r.code === 0, 'Missing complete settled response');
            assert.equal(reader.state.header.cwd, cwd, 'Session workspace mismatch');
            assert.equal(reader.state.header.id, `M3-ContactOnboarding-01-${id}`, 'Session ID mismatch');
            const files = (await readdir(sessionDir)).filter(f => f.endsWith('.jsonl'));
            assert.equal(files.length, 1, 'Missing/ambiguous persisted session');
            const session = path.join(sessionDir, files[0]);
            if (feedback) assert.equal(session, sessions[id]);
            sessions[id] = session;
            const m = reader.state.message;
            const text = m.content.filter(b => b.type === 'text').map(b => b.text).join('');
            await writeFile(path.join(runDir, `${id}-${attempt}-response.md`), text, { flag: 'wx', mode: 0o600 });
            record.session = session;
            const sources = extractSource(text);
            record.candidate = await snapshot(path.join(runDir, `${id}-${attempt}`), sources);
            record.status = 'submitted';
            record.privateEntries = [...sources.keys()].filter(n => /(?:^|\/)private-tests\.ts$/.test(n)).map(n => n.slice('candidate/'.length, -3) + '.js');
            await unchanged();
            return record;
        };
        const evaluate = async (mode, candidates, expected, privateEntry) => {
            await unchanged();
            const rowIds = privateEntry ? [] : JSON.parse(await readFile(path.join(assets, 'tests', `${mode}.json`), 'utf8')).map(row => row.id);
            const record = { mode, candidates, privateEntry, status: 'incomplete', log: sequence + 1,
                started: new Date().toISOString(), rows: rowIds, unrunRows: rowIds, rowAccounting: 'no row progress established; listed rows unverified' };
            report.evaluations.push(record);
            let r;
            try { r = await call('bash', [path.join(assets, 'evaluate.sh'), stage, mode, ...candidates, ...(privateEntry ? [`private:${privateEntry}`] : [])]); }
            finally { record.ended = new Date().toISOString(); }
            const passed = r.code === 0;
            record.code = r.code;
            if (passed && expected) assert.ok(r.stdout.includes(expected), 'Missing complete evaluator success marker');
            const failed = rowIds.findIndex(id => r.stdout.includes(`${id}:`));
            Object.assign(record, { status: passed ? 'passed' : 'failed', passed, firstFailedRow: passed ? null : rowIds[failed] ?? 'unknown',
                unrunRows: passed ? [] : failed >= 0 ? rowIds.slice(failed + 1) : rowIds,
                rowAccounting: passed || failed >= 0 ? 'from frozen suite/log order' : record.rowAccounting });
            assert.ok(!/No external imports|Import must stay within candidate|Unapproved file|Computed import|Import-equals/.test(r.stdout), 'Candidate scope/import violation; stop');
            // Docker wrapper errors/timeouts and setup failures are not candidate revision opportunities.
            if (!passed) assert.ok(r.code === 1 && /(?:error TS\d+|AssertionError)/.test(r.stdout) && r.stdout.includes('CONTAINER SETTINGS PASS'), 'Infrastructure/unknown evaluation failure; stop');
            return passed;
        };
        const initial = {};
        for (const [id] of BOXES) initial[id] = await episode(id, 'initial');
        const check = async (record, mode, rows) => {
            let privatePass = true;
            for (const entry of record.privateEntries) {
                assert.equal(await ask(`Run explicitly supplied ${record.id} private check ${entry}? Type YES (otherwise stop): `), 'YES');
                privatePass = await evaluate(mode, [record.candidate], null, entry) && privatePass;
            }
            return (await evaluate(mode, [record.candidate], `INDEPENDENT PASS: ${mode}, ${rows} rows`)) && privatePass;
        };
        const passed = {};
        for (const [id, , mode, rows] of BOXES) passed[id] = await check(initial[id], mode, rows);
        for (const [id, , mode, rows] of BOXES) {
            let record = initial[id];
            if (!passed[id]) {
                console.log(`${id} failed. Inspect only its private local logs; never forward logs or hidden case data.`);
                const feedback = await ask(`Optional one ${id} revision: enter supplied requirement IDs and class, e.g. ${id === 'A' ? 'N-01' : 'R-01'} behavioral (or STOP): `);
                const prefix = id === 'A' ? 'N' : 'R';
                assert.ok(new RegExp(`^${prefix}-0[1-5](?:,${prefix}-0[1-5])* (compile|export|M1|behavioral|private-check)$`).test(feedback), 'No permitted revision feedback; trial stopped');
                record = await episode(id, 'revision', `This is your one permitted revision episode. Verification: ${feedback}. Use only your own handoff and history. Emit the complete permitted TypeScript source set as full files, not patches. Do not change interfaces, responsibilities or dependencies. Finish with READY, CLARIFICATION, or ARCHITECTURE_PROPOSAL.`);
                passed[id] = await check(record, mode, rows);
            }
            if (passed[id]) selected[id] = record.candidate;
        }
        await unchanged();
        if (passed.A && passed.B) {
            await writeFile(path.join(runDir, 'selected-pair.json'), JSON.stringify(selected, null, 2), { flag: 'wx', mode: 0o444 });
            report.integration = 'incomplete';
            report.status = await evaluate('integration', [selected.A, selected.B], 'INTEGRATION PASS: 18 complete intermediate/final rows; unchanged live value') ? 'passed' : 'failed';
            report.integration = report.status;
        } else report.status = 'failed; integration unrun';
        await unchanged();
    } catch (error) {
        report.status = 'stopped'; report.error = error.message; throw error;
    } finally {
        if (containersUsed) {
            try {
                const containers = await must('docker', ['ps', '-aq', '--filter', 'name=boundscript-contact-'], { cleanup: true });
                assert.equal(containers.stdout.trim(), '', 'Evaluation container survived cleanup');
                report.cleanup = 'no surviving experiment containers';
            } catch (error) { report.cleanup = error.message; report.status = 'stopped'; }
        }
        report.ended = new Date().toISOString();
        await writeFile(path.join(runDir, 'results.json'), JSON.stringify(report, null, 2), { mode: 0o600 });
        console.log(`Results (private; review/redact before sharing): ${path.join(runDir, 'results.json')}`);
    }
    return report;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
    process.umask(0o077);
    const args = process.argv.slice(2);
    if (args.length !== 2 || args[0] !== '--run-dir' || !path.isAbsolute(args[1]) || !process.stdin.isTTY) {
        console.error('Usage (interactive approval required): node tooling/run-contact-pilot.mjs --run-dir /absolute/fresh/external/directory');
        process.exitCode = 1;
    } else {
        const terminal = createInterface({ input: process.stdin, output: process.stdout });
        const abort = new AbortController();
        const interrupted = () => abort.abort();
        terminal.on('SIGINT', () => process.emit('SIGINT'));
        process.once('SIGINT', interrupted); process.once('SIGTERM', interrupted);
        try {
            const report = await runPilot({ repo: fileURLToPath(new URL('../', import.meta.url)).replace(/\/$/, ''), runDir: args[1], signal: abort.signal, ask: q => terminal.question(q, { signal: abort.signal }) });
            if (report.status !== 'passed') process.exitCode = 1;
        } catch (error) { console.error(`STOP: ${error.message}`); process.exitCode = 1; }
        finally {
            process.removeListener('SIGINT', interrupted); process.removeListener('SIGTERM', interrupted);
            terminal.close();
        }
    }
}
