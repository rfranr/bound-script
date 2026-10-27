#!/usr/bin/env python3
"""Fixed 0030 Pi spike, retaining the baseline generation security/promotion path."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
sys.path.insert(0, str(SPIKE.parent / 'minimal-box'))
from verify import IMAGE, digest, run
from container_runtime import runtime

PI = Path.home() / '.nvm/versions/node/v24.16.0/lib/node_modules/@earendil-works/pi-coding-agent'
AUTH = Path.home() / '.pi/agent/auth.json'
#MODEL = 'openai-codex/gpt-6.1-sol'
MODEL = 'openai-codex/gpt-5.6-luna'
MODEL_THINKING = 'low'
PROMPT = '''Read /inputs/task.md and /inputs/contract.ts using the read tool.
Implement NormalizeContact in /implementation/implementation.ts and export the
normalizeContact function. Use tools to write the file. Only the task and native
TypeScript contract are authorized inputs. No peer code, tests or repository are
available. Do not install packages, inspect or disclose credentials, or write
any other submission file. Use type-only contract imports. Do not change the
contract or task. The container, not this prompt, enforces the filesystem boundary.
'''


def quarantine(submission, expected_digest):
    """Retain only the same bounded, credential-scanned bytes, never agent logs."""
    fd = os.open(submission, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise RuntimeError('Unsafe quarantine submission')
        source = stream.read(16385)
    if len(source) > 16384 or hashlib.sha256(source).hexdigest() != expected_digest:
        raise RuntimeError('Quarantine submission differs from credential-scanned source')
    directory = SPIKE / 'quarantine'
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError('Unsafe quarantine directory')
    saved = Path(tempfile.mkdtemp(prefix='failed-', dir=directory)) / 'implementation.ts'
    fd = os.open(saved, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(source)
    return saved


def main():
    if not __debug__ or run('git', 'branch', '--show-current') not in (
        'experiment/boundscript-next', 'experiment/typescript-contracts'
    ):
        raise RuntimeError('Use the baseline or dedicated TypeScript experiment branch with assertions enabled')
    if sys.argv[1:]:
        raise RuntimeError('This spike generates only NormalizeContact; no arguments expected')
    if not (SPIKE / '.generated/validators.ts').is_file():
        raise RuntimeError('Run npm run build:native first')
    box = 'normalize-contact-native'
    filename = 'implementation.ts'
    input_sources = {'task.md': SPIKE / 'task.md', 'contract.ts': SPIKE / 'src/contract.ts'}
    destination = SPIKE / 'accepted/normalize-contact.ts'
    prompt = PROMPT
    if not AUTH.is_file() or not (PI / 'dist/bundle/cli.js').is_file():
        raise RuntimeError('Expected existing Pi 1.4.0 installation and auth.json')
    assert json.loads((PI / 'package.json').read_text())['version'] == '1.4.0'
    assert os.getuid() != 0, 'Run as the existing nonroot Pi user'
    engine = runtime()
    engine.image(IMAGE)
    auth_before = digest(AUTH)
    name = 'boundscript-box-agent-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-native-agent-') as tmp:
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
            print(f'Generating {box}: {MODEL}, {MODEL_THINKING} reasoning, fresh empty workspace', flush=True)
            command = ['node', '/opt/pi/dist/bundle/cli.js',
                       '--mode', 'json', '--no-session', '--model', MODEL, '--thinking', MODEL_THINKING,
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
            assert digest(AUTH) == auth_before, 'Host authentication changed'
        finally:
            engine.remove(name)
        # Generation has ended; independent offline verification receives only the submission.
        verification = [sys.executable, str(SPIKE / 'verify.py'), str(submission)]
        try:
            subprocess.run(verification, check=True, timeout=120)
        except (subprocess.SubprocessError, OSError):
            # Generation has ended and the literal credential scan has passed.
            # Never retain failed generation output or a credential-scan failure.
            saved = quarantine(submission, scanned_digest)
            print(f'Verification failed; candidate quarantined: {saved.relative_to(SPIKE)}; '
                  f'sha256={scanned_digest}; not promoted', flush=True)
            raise
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
