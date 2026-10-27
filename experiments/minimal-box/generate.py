#!/usr/bin/env python3
"""Fixed Greeting/0018 Pi runs; no generic runner or user-defined job format."""
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
from container_runtime import runtime

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
contract or task. The filesystem boundary is enforced by the container runtime, not this prompt.
'''


def main():
    if not __debug__ or run('git', 'branch', '--show-current') != 'experiment/boundscript-next':
        raise RuntimeError('Use experiment/boundscript-next with Python assertions enabled')
    if sys.argv[1:] == ['--pair']:
        # Two fresh processes/containers, not a shared agent session or context.
        for box in ('normalize-contact', 'render-welcome'):
            subprocess.run([sys.executable, __file__, box], check=True, timeout=450)
        subprocess.run([sys.executable, str(HERE / 'verify_pair.py'), 'integrate'], check=True, timeout=120)
        return
    if sys.argv[1:] not in ([], ['normalize-contact'], ['render-welcome']):
        raise RuntimeError('Expected no args, --pair, normalize-contact, or render-welcome')
    box = sys.argv[1] if len(sys.argv) == 2 else 'greeting'
    filename = 'greet.ts' if box == 'greeting' else 'implementation.ts'
    input_sources = {'task.md': HERE / 'task.md', 'contract.ts': HERE / 'contract.ts',
                     'slugger.ts': HERE / 'slugger.ts'}
    destination = HERE / 'implementation/greet.ts'
    prompt = PROMPT
    if box != 'greeting':
        pair = HERE / 'two-boxes'
        input_sources = {'task.md': pair / f'tasks/{box}.md', 'contract.ts': pair / f'contracts/{box}.ts'}
        if box == 'render-welcome':
            input_sources['normalize-contact.ts'] = pair / 'contracts/normalize-contact.ts'
        destination = pair / f'accepted/{box}.ts'
        prompt = ('Use the read tool to inspect these authorized inputs: '
                  + ', '.join('/inputs/' + name for name in input_sources)
                  + '. Implement the task in /implementation/implementation.ts using tools. '
                    'Export the exact named function required by the task. No tests, application '
                    'wiring or peer implementations are available. Do not install packages, '
                    'inspect or disclose credentials, or write any other submission file. '
                    'Do not change contracts or business requirements.')
    if not AUTH.is_file() or not (PI / 'dist/bundle/cli.js').is_file():
        raise RuntimeError('Expected existing Pi 1.4.0 installation and auth.json')
    assert json.loads((PI / 'package.json').read_text())['version'] == '1.4.0'
    assert os.getuid() != 0, 'Run as the existing nonroot Pi user'
    engine = runtime()
    engine.image(IMAGE)
    auth_before = digest(AUTH)
    name = 'boundscript-box-agent-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-greeting-agent-') as tmp:
        root = Path(tmp)
        candidate = root / 'implementation'
        candidate.mkdir()  # Empty: never seed with the hand-written implementation.
        sentinel = root / 'host-only.txt'
        sentinel.write_text('synthetic host sentinel\n')
        inputs = root / 'inputs'
        inputs.mkdir()
        for input_name, source_path in input_sources.items():
            shutil.copyfile(source_path, inputs / input_name)
        protected = {p: digest(p) for p in [sentinel, *inputs.iterdir()]}
        mounts = []
        for p in inputs.iterdir():
            mounts += ['--mount', f'type=bind,src={p},dst=/inputs/{p.name},readonly']
        mounts += ['--mount', f'type=bind,src={candidate},dst=/implementation',
                   '--mount', f'type=bind,src={PI},dst=/opt/pi,readonly',
                   '--mount', f'type=bind,src={AUTH},dst=/run/host-auth.json,readonly']
        try:
            engine.create(name, IMAGE, mounts, os.getuid(), os.getgid(),
                          generation=True, workdir='/implementation')
            engine.start(name, os.getuid(), os.getgid(), generation=True)
            # No secrets go through stdout/stderr, command arguments or host files.
            engine.exec(name, 'sh', '-c',
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
// Deliberate unauthorized dependency access, in the actual agent environment.
try { readFileSync('/peer/implementation.ts'); observed.push('SUCCEEDED'); } catch(e) { observed.push(e.code); }
try { await import('/peer/implementation.ts'); observed.push('SUCCEEDED'); } catch(e) { observed.push(e.code); }
console.log(JSON.stringify(observed));
'''.replace('SECRET', json.dumps(str(sentinel)))
            observed = json.loads(engine.exec(name, 'node', '--input-type=module', source=source))
            assert observed == ['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT', 'EROFS', 'ENOENT',
                                'ENOENT', 'ERR_MODULE_NOT_FOUND'], observed
            print(f'PASS {box} generation filesystem probes; forbidden peer read/import rejected because file is absent', flush=True)
            print(f'Generating {box}: {MODEL}, medium reasoning, fresh empty workspace', flush=True)
            command = ['node', '/opt/pi/dist/bundle/cli.js',
                       '--mode', 'json', '--no-session', '--model', MODEL, '--thinking', 'medium',
                       '--tools', 'read,write,edit,bash', '--no-extensions', '--no-mcp',
                       '--no-skills', '--no-prompt-templates', '--no-themes',
                       '--no-context-files', '--no-approve', '--offline', prompt]
            # Raw events/diagnostics stay in memory and are never printed or saved.
            output = engine.exec(name, *command, timeout=300)
            events = [json.loads(line) for line in output.split('\n') if line.strip()]
            settled = [e for e in events if e.get('type') == 'agent_settled']
            assert settled and settled[-1].get('aborted') is False, 'Pi did not settle successfully'
            messages = [e['message'] for e in events if e.get('type') == 'message_end' and e.get('message', {}).get('role') == 'assistant']
            assert messages and messages[-1].get('stopReason') == 'stop', 'Pi ended without successful completion'
            header = next(e for e in events if e.get('type') == 'session')
            assert header['cwd'] == '/implementation'
            print('Pi session: ' + str(uuid.UUID(header['id'])), flush=True)
            tools = [e for e in events if e.get('type') == 'tool_execution_start']
            # Report only allowlisted input paths, tool counts and aggregate metadata.
            reads = [e.get('args', {}).get('path') for e in tools if e.get('toolName') == 'read']
            allowed_reads = {'/inputs/' + p for p in input_sources} | {'/implementation/' + filename}
            assert set(reads) <= allowed_reads, 'Unexpected agent read path'
            assert any(e.get('toolName') == 'write' for e in tools), 'No agent write observed'
            print('Pi tools: ' + json.dumps({t: sum(e.get('toolName') == t for e in tools) for t in ('read', 'write', 'edit', 'bash')}), flush=True)
            failures = sum(bool(e.get('isError')) for e in events if e.get('type') == 'tool_execution_end')
            print(f'Tool failures: {failures}; observed read paths within authorized inputs/own implementation', flush=True)
            submission = candidate / filename
            assert list(candidate.iterdir()) == [submission] and not submission.is_symlink()
            assert submission.is_file() and submission.stat().st_size <= 16384
            # Check both original and refreshed credential string values IN the
            # container before importing any submission bytes to the repository.
            engine.exec(name, 'node', '--input-type=module', source='''
import {readFileSync} from 'node:fs';
const source = readFileSync('/implementation/FILENAME', 'utf8');
function check(v) {
 if (typeof v === 'string' && v.length >= 8 && source.includes(v)) process.exit(42);
 if (v && typeof v === 'object') for (const x of Object.values(v)) check(x);
}
for (const path of ['/run/host-auth.json', '/pi-state/auth.json']) check(JSON.parse(readFileSync(path, 'utf8')));
'''.replace('FILENAME', filename))
            assert all(digest(p) == old for p, old in protected.items())
            assert digest(AUTH) == auth_before, 'Host authentication changed'
        finally:
            engine.remove(name)
        # Generation has ended; independent offline verification receives only the submission.
        verification = ([sys.executable, str(HERE / 'verify.py'), str(submission)] if box == 'greeting'
                        else [sys.executable, str(HERE / 'verify_pair.py'), box, str(submission)])
        subprocess.run(verification, check=True, timeout=120)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(submission, destination)
        print(f'PASS {box} independently verified and promoted unchanged; sha256={digest(destination)}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never serialize arbitrary provider/tool diagnostics.
        print(f'Generation stopped: {type(error).__name__}; no raw diagnostics emitted', file=sys.stderr)
        sys.exit(1)
