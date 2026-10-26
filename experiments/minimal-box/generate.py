#!/usr/bin/env python3
"""One fixed Pi generation for this experiment; credentials/network explicitly authorized."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
from verify import HERE, IMAGE, digest, run

PI = Path.home() / '.nvm/versions/node/v24.16.0/lib/node_modules/@earendil-works/pi-coding-agent'
AUTH = Path.home() / '.pi/agent/auth.json'
MODEL = 'openai-codex/gpt-6.1-sol'
PROMPT = '''Read /inputs/task.md, /inputs/contract.ts and /inputs/slugger.ts using tools.
Implement the existing Greeting Box in /implementation/greet.ts. Use the tools to
write the file, not just describe it. No acceptance tests or peer code are available.
Network and authentication are provisioned as runtime capabilities per the task.
Do not inspect, print, copy into the submission, or transmit credential files or
runtime state.
Do not install packages. Keep your only submission file greet.ts. Do not alter the
contract or task. The filesystem boundary is enforced by Docker, not this prompt.
'''


def main():
    if not __debug__ or run('git', 'branch', '--show-current') != 'experiment/boundscript-next':
        raise RuntimeError('Use experiment/boundscript-next with Python assertions enabled')
    if not AUTH.is_file() or not (PI / 'dist/bundle/cli.js').is_file():
        raise RuntimeError('Expected existing Pi 1.4.0 installation and auth.json')
    assert json.loads((PI / 'package.json').read_text())['version'] == '1.4.0'
    assert os.getuid() != 0, 'Run as the existing nonroot Pi user'
    run('docker', 'image', 'inspect', IMAGE)
    auth_before = digest(AUTH)
    name = 'boundscript-greeting-agent-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-greeting-agent-') as tmp:
        root = Path(tmp)
        candidate = root / 'implementation'
        candidate.mkdir()  # Empty: never seed with the hand-written implementation.
        sentinel = root / 'host-only.txt'
        sentinel.write_text('synthetic host sentinel\n')
        inputs = root / 'inputs'
        inputs.mkdir()
        for filename in ('task.md', 'contract.ts', 'slugger.ts'):
            shutil.copyfile(HERE / filename, inputs / filename)
        protected = {p: digest(p) for p in [sentinel, *inputs.iterdir()]}
        mounts = []
        for p in inputs.iterdir():
            mounts += ['--mount', f'type=bind,src={p},dst=/inputs/{p.name},readonly']
        mounts += ['--mount', f'type=bind,src={candidate},dst=/implementation',
                   '--mount', f'type=bind,src={PI},dst=/opt/pi,readonly',
                   '--mount', f'type=bind,src={AUTH},dst=/run/host-auth.json,readonly']
        try:
            run('docker', 'create', '--name', name, '--pull', 'never',
                '--network', 'bridge', '--user', f'{os.getuid()}:{os.getgid()}',
                '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                '--memory', '512m', '--memory-swap', '512m', '--cpus', '1', '--pids-limit', '64',
                '--log-driver', 'none', '--workdir', '/implementation',
                '--tmpfs', f'/pi-state:rw,nosuid,nodev,noexec,size=64m,mode=700,uid={os.getuid()},gid={os.getgid()}',
                '--env', 'HOME=/pi-state', '--env', 'PI_CODING_AGENT_DIR=/pi-state',
                '--env', 'PI_OFFLINE=1', '--env', 'PI_TELEMETRY=0',
                '--env', 'PI_SKIP_VERSION_CHECK=1', *mounts, IMAGE, 'sleep', '600')
            config = json.loads(run('docker', 'inspect', name))[0]
            h = config['HostConfig']
            assert h['NetworkMode'] == 'bridge' and h['ReadonlyRootfs'] and not h['Privileged']
            assert h['CapDrop'] == ['ALL'] and 'no-new-privileges' in h['SecurityOpt']
            expected = {'/inputs/task.md', '/inputs/contract.ts', '/inputs/slugger.ts',
                        '/implementation', '/opt/pi', '/run/host-auth.json'}
            binds = [m for m in config['Mounts'] if m['Type'] == 'bind']
            assert {m['Destination'] for m in binds} == expected and len(binds) == 6
            assert all(m['RW'] == (m['Destination'] == '/implementation') for m in binds)
            assert set(e.split('=', 1)[0] for e in config['Config']['Env']) <= {
                'PATH', 'NODE_VERSION', 'YARN_VERSION', 'HOME', 'PI_CODING_AGENT_DIR',
                'PI_OFFLINE', 'PI_TELEMETRY', 'PI_SKIP_VERSION_CHECK'}
            run('docker', 'start', name)
            # No secrets go through stdout/stderr, command arguments or host files.
            run('docker', 'exec', name, 'sh', '-c',
                'umask 077; cp /run/host-auth.json /pi-state/auth.json; '
                '''printf '%s' '{"cacheWarming":"off","retry":{"enabled":false},"compaction":{"enabled":false}}' > /pi-state/settings.json''')
            # Fixed action probes run in the actual generation container. Assertions
            # remain on the host; no verifier/test files are mounted.
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
console.log(JSON.stringify(observed));
'''.replace('SECRET', json.dumps(str(sentinel)))
            observed = json.loads(run('docker', 'exec', '-i', name, 'node', '--input-type=module', source=source))
            assert observed == ['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT', 'EROFS', 'ENOENT'], observed
            print('PASS generation filesystem probes: host/repo/tests/verifier absent; protected writes and symlink escape denied', flush=True)
            command = ['docker', 'exec', name, 'node', '/opt/pi/dist/bundle/cli.js',
                       '--mode', 'json', '--no-session', '--model', MODEL, '--thinking', 'medium',
                       '--tools', 'read,write,edit,bash', '--no-extensions', '--no-mcp',
                       '--no-skills', '--no-prompt-templates', '--no-themes',
                       '--no-context-files', '--no-approve', '--offline', PROMPT]
            # Raw events/diagnostics stay in memory and are never printed or saved.
            result = subprocess.run(command, text=True, capture_output=True, timeout=300)
            if result.returncode:
                raise RuntimeError(f'Pi exited {result.returncode}; raw diagnostics withheld to protect credentials')
            events = [json.loads(line) for line in result.stdout.split('\n') if line.strip()]
            settled = [e for e in events if e.get('type') == 'agent_settled']
            assert settled and settled[-1].get('aborted') is False, 'Pi did not settle successfully'
            messages = [e['message'] for e in events if e.get('type') == 'message_end' and e.get('message', {}).get('role') == 'assistant']
            assert messages and messages[-1].get('stopReason') == 'stop', 'Pi ended without successful completion'
            tools = [e for e in events if e.get('type') == 'tool_execution_start']
            # Report only allowlisted input paths, tool counts and aggregate metadata.
            reads = [e.get('args', {}).get('path') for e in tools if e.get('toolName') == 'read']
            assert set(reads) == {'/inputs/task.md', '/inputs/contract.ts', '/inputs/slugger.ts'}, 'Unexpected agent read path'
            assert any(e.get('toolName') == 'write' for e in tools), 'No agent write observed'
            print('Pi tools: ' + json.dumps({t: sum(e.get('toolName') == t for e in tools) for t in ('read', 'write', 'edit', 'bash')}), flush=True)
            print('Observed read paths: three authorized inputs only', flush=True)
            submission = candidate / 'greet.ts'
            assert list(candidate.iterdir()) == [submission] and not submission.is_symlink()
            assert submission.is_file() and submission.stat().st_size <= 16384
            # Check both original and refreshed credential string values IN the
            # container before importing any submission bytes to the repository.
            run('docker', 'exec', '-i', name, 'node', '--input-type=module', source='''
import {readFileSync} from 'node:fs';
const source = readFileSync('/implementation/greet.ts', 'utf8');
function check(v) {
 if (typeof v === 'string' && v.length >= 8 && source.includes(v)) process.exit(42);
 if (v && typeof v === 'object') for (const x of Object.values(v)) check(x);
}
for (const path of ['/run/host-auth.json', '/pi-state/auth.json']) check(JSON.parse(readFileSync(path, 'utf8')));
''')
            assert all(digest(p) == old for p, old in protected.items())
            assert digest(AUTH) == auth_before, 'Host authentication changed'
        finally:
            run('docker', 'rm', '-f', name)
        # Generation has ended; independent offline verifier receives only greet.ts.
        subprocess.run([sys.executable, str(HERE / 'verify.py'), str(submission)], check=True, timeout=120)
        shutil.copyfile(submission, HERE / 'implementation/greet.ts')
        print('PASS agent-generated greet.ts verified and saved; auth/runtime state/container discarded')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never serialize arbitrary provider/tool diagnostics.
        print(f'Generation stopped: {type(error).__name__}; no raw diagnostics emitted', file=sys.stderr)
        sys.exit(1)
