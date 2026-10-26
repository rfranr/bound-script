import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, mkdir, writeFile, readFile, rm, chmod, readdir } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { command, eventReader, extractSource, runPilot, checkNativeProfile } from '../tooling/run-contact-pilot.mjs';

const source = 'candidate/implementation.ts\n```typescript\nexport const implement = () => "inert";\n```\nREADY\n';
function events(cwd, id, text = source) {
    const message = { role: 'assistant', stopReason: 'stop', provider: 'openai-codex', model: 'gpt-6.1-sol',
        content: [{ type: 'text', text }], usage: { totalTokens: 123 } };
    return [{ type: 'session', id, cwd }, { type: 'agent_start' }, { type: 'turn_start' },
        { type: 'message_end', message }, { type: 'turn_end', message, toolResults: [] },
        { type: 'agent_end', willRetry: false }, { type: 'agent_settled', aborted: false }];
}

test('mechanical extraction preserves bytes, supports helpers, rejects ambiguity and unsafe output', () => {
    assert.equal(extractSource(source).get('candidate/implementation.ts'), 'export const implement = () => "inert";\n');
    const helper = '### `candidate/lib/helper.ts`\n```ts\n// inert\n```\n';
    assert.equal(extractSource(source.replace('READY', helper + 'READY')).size, 2);
    for (const text of [source + 'extra', 'Explanation\n' + source, source.replace('READY', 'CLARIFICATION'),
        source.replace('READY', 'ARCHITECTURE_PROPOSAL'), source.replace('```\nREADY', 'READY'),
        source.replace('candidate/implementation.ts', 'candidate/../implementation.ts'),
        source.replace('candidate/implementation.ts', '/candidate/implementation.ts'),
        source.replace('candidate/implementation.ts', 'candidate/implementation.d.ts'),
        source.replace('candidate/implementation.ts', 'candidate/.pi/implementation.ts'),
        source.replace('READY', source), source.replace('candidate/implementation.ts', 'candidate/helper.ts')]) {
        assert.throws(() => extractSource(text), text);
    }
    assert.throws(() => extractSource(source.replace('export const implement = () => "inert";', 'x'.repeat(10485761))));
});

test('JSON protocol rejects failures, tools, recovery, additional turns and wrong model', () => {
    const valid = events('/workspace', 'id');
    const reader = eventReader(); valid.forEach(e => reader.line(JSON.stringify(e)));
    assert.equal(reader.state.settled, true);
    const bad = [
        [{ type: 'turn_start' }],
        [...valid, { type: 'agent_start' }],
        [...valid.slice(0, 3), { type: 'turn_start' }],
        ...['tool_execution_start', 'auto_retry_start', 'compaction_start', 'queue_update'].map(type => [...valid.slice(0, 2), { type }]),
        ...['length', 'error', 'aborted', 'toolUse'].map(stopReason => valid.map(e => e.type === 'message_end' ? { ...e, message: { ...e.message, stopReason } } : e)),
        valid.map(e => e.type === 'message_end' ? { ...e, message: { ...e.message, model: 'other' } } : e),
        valid.map(e => e.type === 'message_end' ? { ...e, message: { ...e.message, content: [{ type: 'toolCall' }] } } : e),
        valid.map(e => e.type === 'agent_settled' ? { ...e, aborted: true } : e),
        valid.filter(e => e.type !== 'turn_end'),
    ];
    for (const stream of bad) assert.throws(() => {
        const r = eventReader(); stream.forEach(e => r.line(JSON.stringify(e)));
    });
    assert.throws(() => eventReader().line('{invalid'));
});

async function cleanup(root) {
    await chmod(root, 0o700);
    for (const e of await readdir(root, { withFileTypes: true })) if (e.isDirectory()) await cleanup(path.join(root, e.name));
    await rm(root, { recursive: true, force: true });
}

async function fixture(t, { revise = false, integrationFail = false, invalid = false, incomplete = false, infrastructure = false, deny = false, readiness = false, feedback = 'N-01 behavioral', exhausted = false } = {}) {
    const root = await mkdtemp(path.join(os.tmpdir(), 'contact-runner-test-'));
    t.after(() => cleanup(root));
    const repo = path.join(root, 'repo'), runDir = path.join(root, 'trial'), agentDir = path.join(root, 'native-profile');
    await mkdir(path.join(repo, 'node_modules'), { recursive: true });
    await mkdir(agentDir);
    await writeFile(path.join(agentDir, 'settings.json'), '{"cacheWarming":"off"}');
    const calls = [], prompts = [], answers = ['RUN', 'usage-time-only', feedback];
    let normalized = 0;
    const exec = async (exe, args, opts) => {
        calls.push({ exe, args, cwd: opts.cwd });
        const result = (stdout = '', code = 0) => ({ stdout, code });
        if (exe === 'git' && args[0] === 'worktree') await mkdir(args[3], { recursive: true });
        if (args.includes('--version')) return result(exe === process.execPath ? 'v24.16.0\n' : '1.4.0\n');
        if (exe === 'docker' && args[0] === 'version') return result(readiness ? 'wrong-version\n' : '29.1.3\n');
        if (args[0] === '-p') return result('5.9.3\n');
        if (args[0]?.endsWith('/prepare.mjs')) {
            const tests = path.join(path.dirname(args[0]), 'tests');
            await mkdir(tests, { recursive: true });
            for (const mode of ['normalize', 'render', 'integration']) await writeFile(path.join(tests, `${mode}.json`), JSON.stringify([{ id: 'mock-1' }, { id: 'mock-2' }]));
            for (const box of ['NormalizeContact', 'RenderWelcome']) {
                await mkdir(path.join(args[1], box, 'handoff'), { recursive: true });
                for (const file of ['handoff.json', 'README.md', 'contract.box-spec.json', 'task.md', 'scope.md', 'policy.md', 'generated/contract.d.ts', 'seed/implementation.ts']) {
                    const target = path.join(args[1], box, 'handoff', file);
                    await mkdir(path.dirname(target), { recursive: true });
                    await writeFile(target, box);
                }
            }
        }
        if (exe === 'mock-pi' && args.includes('--mode')) {
            assert.equal(args[args.indexOf('--mode') + 1], 'json');
            assert.ok(args.includes('--no-tools') && args.includes('--no-mcp') && args.includes('--no-context-files'));
            const id = path.basename(opts.cwd), sessionId = `M3-ContactOnboarding-01-${id}`;
            const sessionDir = args[args.indexOf('--session-dir') + 1];
            const resuming = args.includes('--session');
            if (resuming) assert.equal(args[args.indexOf('--session') + 1], path.join(sessionDir, 'session.jsonl'));
            else {
                assert.equal(args.filter(a => a.startsWith('@handoff/')).length, 8);
                await writeFile(path.join(sessionDir, 'session.jsonl'), '{}\n');
            }
            prompts.push(args.at(-1));
            const stream = events(opts.cwd, sessionId, invalid ? 'CLARIFICATION\n' : source);
            if (incomplete) stream.pop();
            stream.forEach(e => opts.onLine(JSON.stringify(e)));
            return result();
        }
        if (args[0]?.endsWith('/evaluate.sh')) {
            const mode = args[2];
            if (mode === 'normalize' && (normalized++ === 0 || exhausted) && (revise || infrastructure)) {
                return result(infrastructure ? 'daemon failed' : 'CONTAINER SETTINGS PASS\nAssertionError: HIDDEN-CASE HIDDEN-EXPECTED\n', infrastructure ? 125 : 1);
            }
            if (mode === 'integration') return result(integrationFail ? 'CONTAINER SETTINGS PASS\nAssertionError: HIDDEN-INTEGRATION\n' : 'INTEGRATION PASS: 18 complete intermediate/final rows; unchanged live value', integrationFail ? 1 : 0);
            return result(`INDEPENDENT PASS: ${mode}, ${mode === 'normalize' ? 39 : 24} rows`);
        }
        return result();
    };
    const invoke = () => runPilot({ repo, runDir, agentDir, pi: 'mock-pi', exec,
        ask: async () => deny ? 'NO' : answers.shift() });
    return { root, runDir, calls, prompts, invoke };
}

test('complete mocked pilot: independent A/B, both submissions before checks, frozen integration', async t => {
    const f = await fixture(t);
    const report = await f.invoke();
    assert.equal(report.status, 'passed');
    assert.deepEqual(report.episodes.map(e => [e.id, e.attempt]), [['A', 'initial'], ['B', 'initial']]);
    const generations = f.calls.filter(c => c.exe === 'mock-pi' && c.args.includes('--mode'));
    assert.notEqual(generations[0].cwd, generations[1].cwd);
    const firstCheck = f.calls.findIndex(c => c.args[0]?.endsWith('/evaluate.sh'));
    assert.ok(f.calls.indexOf(generations[1]) < firstCheck);
    assert.equal(f.calls.filter(c => c.args[2] === 'integration').length, 1);
    assert.equal(await readFile(path.join(f.runDir, 'A-initial/candidate/implementation.ts'), 'utf8'), 'export const implement = () => "inert";\n');
    assert.equal(JSON.parse(await readFile(path.join(f.runDir, 'results.json'), 'utf8')).status, 'passed');
    await assert.rejects(f.invoke(), /EEXIST/);
});

test('one own-history revision with restricted feedback, never hidden logs', async t => {
    const f = await fixture(t, { revise: true });
    const report = await f.invoke();
    assert.equal(report.status, 'passed');
    assert.deepEqual(report.episodes.map(e => `${e.id}-${e.attempt}`), ['A-initial', 'B-initial', 'A-revision']);
    assert.ok(f.prompts.at(-1).includes('N-01 behavioral'));
    assert.ok(f.prompts.every(p => !p.includes('HIDDEN')));
    const selected = JSON.parse(await readFile(path.join(f.runDir, 'selected-pair.json'), 'utf8'));
    assert.ok(selected.A.includes('A-revision') && selected.B.includes('B-initial'));
});

test('integration failure is final, never starts another model call', async t => {
    const f = await fixture(t, { integrationFail: true });
    const report = await f.invoke();
    assert.equal(report.status, 'failed'); assert.equal(report.episodes.length, 2);
});

for (const [name, options] of Object.entries({ ambiguous: { invalid: true }, truncated: { incomplete: true }, infrastructure: { infrastructure: true }, unauthorized: { deny: true }, readiness: { readiness: true }, feedbackLeak: { revise: true, feedback: 'N-01 HIDDEN-EXPECTED' } })) {
    test(`${name} stops and retains a failure report`, async t => {
        const f = await fixture(t, options);
        await assert.rejects(f.invoke());
        assert.equal(JSON.parse(await readFile(path.join(f.runDir, 'results.json'), 'utf8')).status, 'stopped');
        assert.equal(f.calls.filter(c => c.args[2] === 'integration').length, 0);
        if (options.deny) assert.equal(f.calls.length, 0);
        if (options.readiness) assert.equal(f.prompts.length, 0);
        if (options.feedback) assert.equal(f.prompts.length, 2);
    });
}

test('exhausted revision retains both failed snapshots and never integrates', async t => {
    const f = await fixture(t, { revise: true, exhausted: true });
    const report = await f.invoke();
    assert.equal(report.status, 'failed; integration unrun');
    assert.equal(report.episodes.length, 3);
    assert.equal(f.calls.filter(c => c.args[2] === 'integration').length, 0);
    assert.equal(report.integration, 'unrun');
});

test('native profile check refuses automatic warming and inherited append instructions', async t => {
    const root = await mkdtemp(path.join(os.tmpdir(), 'contact-profile-test-'));
    t.after(() => cleanup(root));
    await assert.rejects(checkNativeProfile(root), /Cannot verify/);
    await writeFile(path.join(root, 'settings.json'), '{"cacheWarming":"streaming"}');
    await assert.rejects(checkNativeProfile(root), /must already be off/);
    await writeFile(path.join(root, 'settings.json'), '{"cacheWarming":"off"}');
    await checkNativeProfile(root);
    await writeFile(path.join(root, 'APPEND_SYSTEM.md'), 'not supplied to agents');
    await assert.rejects(checkNativeProfile(root), /APPEND_SYSTEM/);
});

test('subprocess JSONL reader handles Unicode separators, nonzero status and deadlines using mock processes', async t => {
    const root = await mkdtemp(path.join(os.tmpdir(), 'contact-process-test-'));
    t.after(() => rm(root, { recursive: true, force: true }));
    const lines = [];
    const result = await command(process.execPath, ['-e', 'process.stdout.write(JSON.stringify({text:"a\\u2028b"})+"\\n"); process.exitCode=7'],
        { log: path.join(root, 'unicode'), onLine: line => lines.push(JSON.parse(line)) });
    assert.equal(result.code, 7); assert.equal(lines.length, 1); assert.equal(lines[0].text, 'a\u2028b');
    const reader = eventReader();
    const jsonl = events('/mock', 'mock-session').map(e => JSON.stringify(e)).join('\n') + '\n';
    await command(process.execPath, ['-e', 'process.stdout.write(process.argv[1])', jsonl],
        { log: path.join(root, 'mock-pi-stream'), onLine: reader.line });
    assert.equal(reader.state.settled, true);
    assert.equal(extractSource(reader.state.message.content[0].text).size, 1);
    await assert.rejects(command(process.execPath, ['-e', 'setInterval(()=>{},1000)'], { log: path.join(root, 'timeout'), timeout: 100 }), /deadline/);
    await assert.rejects(command(process.execPath, ['-e', 'process.stdout.write("{}")'], { log: path.join(root, 'partial'), onLine() {} }), /Incomplete JSONL/);
});
