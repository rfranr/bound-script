"""Shared Pi workspace lifecycle, not verification or task orchestration.

Only host-owned fixed runners call this helper. The yielded source has passed
literal credential scanning; the generation container is already destroyed.
The caller must independently verify before promotion, within this context.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from .container_runtime import IMAGE, digest


@contextmanager
def agent_submission(engine, inputs_from, *, pi, auth, box, filename, prompt, model, thinking):
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    if not auth.is_file() or not (pi / 'dist/bundle/cli.js').is_file():
        raise RuntimeError('Expected existing Pi 1.4.0 installation and auth.json')
    assert json.loads((pi / 'package.json').read_text())['version'] == '1.4.0'
    assert os.getuid() != 0, 'Run as the existing nonroot Pi user'
    print('Generation preflight: checking cached image', flush=True)
    engine.image(IMAGE)
    auth_before = digest(auth)
    name = 'boundscript-box-agent-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-agent-') as tmp:
        root = Path(tmp)
        candidate = root / 'implementation'
        candidate.mkdir()  # Empty: never seed with an accepted implementation.
        sentinel = root / 'host-only.txt'
        sentinel.write_text('synthetic host sentinel\n')
        inputs = root / 'inputs'
        inputs.mkdir()
        for input_name, source_path in inputs_from.items():
            shutil.copyfile(source_path, inputs / input_name)
        protected = {p: digest(p) for p in [sentinel, *inputs.iterdir()]}
        mounts = []
        for p in inputs.iterdir():
            mounts += ['--mount', f'type=bind,src={p},dst=/inputs/{p.name},readonly']
        mounts += ['--mount', f'type=bind,src={candidate},dst=/implementation',
                   '--mount', f'type=bind,src={pi},dst=/opt/pi,readonly',
                   '--mount', f'type=bind,src={auth},dst=/run/host-auth.json,readonly']
        try:
            print('Generation preflight: creating isolated container', flush=True)
            engine.create(name, IMAGE, mounts, os.getuid(), os.getgid(),
                          generation=True, workdir='/implementation')
            print('Generation preflight: checking effective filesystem/cgroup isolation', flush=True)
            engine.start(name, os.getuid(), os.getgid(), generation=True)
            print('Generation preflight: isolation passed; preparing private auth state', flush=True)
            # Secrets never enter stdout/stderr, command arguments or host files.
            engine.exec(name, 'sh', '-c',
                'umask 077; cp /run/host-auth.json /pi-state/auth.json; '
                '''printf '%s' '{"cacheWarming":"off","retry":{"enabled":false},"compaction":{"enabled":false}}' > /pi-state/settings.json''')
            # Actions run inside the agent container; assertions stay on the host.
            source = '''
import {readFileSync,writeFileSync,symlinkSync,unlinkSync} from 'node:fs';
const observed = [];
for (const action of [
 () => readFileSync(SECRET),
 () => writeFileSync('/inputs/task.md', 'changed'),
 () => readFileSync('/repo/package.json'),
 () => readFileSync('/verifier/verify.py'),
 () => readFileSync('/tests/acceptance.json'),
 () => writeFileSync('/outside.txt', 'changed'),
 () => { symlinkSync(SECRET, '/implementation/escape'); try { readFileSync('/implementation/escape'); } finally { unlinkSync('/implementation/escape'); } },
]) { try { action(); observed.push('SUCCEEDED'); } catch(e) { observed.push(e.code); } }
try { readFileSync('/peer/implementation.ts'); observed.push('SUCCEEDED'); } catch(e) { observed.push(e.code); }
try { await import('/peer/implementation.ts'); observed.push('SUCCEEDED'); } catch(e) { observed.push(e.code); }
console.log(JSON.stringify(observed));
'''.replace('SECRET', json.dumps(str(sentinel)))
            observed = json.loads(engine.exec(name, 'node', '--input-type=module', source=source))
            assert observed == ['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT', 'EROFS', 'ENOENT',
                                'ENOENT', 'ERR_MODULE_NOT_FOUND'], observed
            print(f'PASS {box} generation filesystem probes; forbidden peer read/import rejected because file is absent', flush=True)
            print(f'Generating {box}: {model}, {thinking} reasoning, fresh empty workspace', flush=True)
            command = ['node', '/opt/pi/dist/bundle/cli.js',
                       '--mode', 'json', '--no-session', '--model', model, '--thinking', thinking,
                       '--tools', 'read,write,edit,bash', '--no-extensions', '--no-mcp',
                       '--no-skills', '--no-prompt-templates', '--no-themes',
                       '--no-context-files', '--no-approve', '--offline', prompt]
            # Raw events/diagnostics remain in memory; never print or save them.
            output = engine.exec(name, *command, timeout=300)
            print('Generation: validating agent completion and tool events', flush=True)
            events = [json.loads(line) for line in output.split('\n') if line.strip()]
            settled = [e for e in events if e.get('type') == 'agent_settled']
            assert settled and settled[-1].get('aborted') is False, 'Pi did not settle successfully'
            messages = [e['message'] for e in events if e.get('type') == 'message_end' and e.get('message', {}).get('role') == 'assistant']
            assert messages and messages[-1].get('stopReason') == 'stop', 'Pi ended without successful completion'
            header = next(e for e in events if e.get('type') == 'session')
            assert header['cwd'] == '/implementation'
            print('Pi session: ' + str(uuid.UUID(header['id'])), flush=True)
            tools = [e for e in events if e.get('type') == 'tool_execution_start']
            reads = [e.get('args', {}).get('path') for e in tools if e.get('toolName') == 'read']
            allowed_reads = {'/inputs/' + p for p in inputs_from} | {'/implementation/' + filename}
            assert set(reads) <= allowed_reads, 'Unexpected agent read path'
            assert any(e.get('toolName') == 'write' for e in tools), 'No agent write observed'
            print('Pi tools: ' + json.dumps({t: sum(e.get('toolName') == t for e in tools) for t in ('read', 'write', 'edit', 'bash')}), flush=True)
            failures = sum(bool(e.get('isError')) for e in events if e.get('type') == 'tool_execution_end')
            print(f'Tool failures: {failures}; observed read paths within authorized inputs/own implementation', flush=True)
            submission = candidate / filename
            assert list(candidate.iterdir()) == [submission] and not submission.is_symlink()
            assert submission.is_file() and submission.stat().st_size <= 16384
            # Scan original AND refreshed literal credential values before the
            # host imports any bytes. Bind the scan to the yielded source hash.
            print('Generation: scanning submission for literal credentials (contents withheld)', flush=True)
            scanned_digest = engine.exec(name, 'node', '--input-type=module', source='''
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const bytes = readFileSync('/implementation/FILENAME');
const source = bytes.toString('utf8');
function check(v) {
 if (typeof v === 'string' && v.length >= 8 && source.includes(v)) process.exit(42);
 if (v && typeof v === 'object') for (const x of Object.values(v)) check(x);
}
for (const path of ['/run/host-auth.json', '/pi-state/auth.json']) check(JSON.parse(readFileSync(path, 'utf8')));
console.log(createHash('sha256').update(bytes).digest('hex'));
'''.replace('FILENAME', filename))
            assert len(scanned_digest) == 64 and all(c in '0123456789abcdef' for c in scanned_digest)
            assert digest(submission) == scanned_digest, 'Submission changed after credential scan'
            assert all(digest(p) == old for p, old in protected.items())
            assert digest(auth) == auth_before, 'Host authentication changed'
        finally:
            print('Generation cleanup: removing container', flush=True)
            engine.remove(name)
        # No credential-bearing generation process remains when verification runs.
        assert digest(submission) == scanned_digest, 'Submission changed during generation cleanup'
        yield submission, scanned_digest
