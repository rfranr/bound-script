#!/usr/bin/env python3
"""Fixed external checks for this one Box. No candidate code executes on the host."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
from container_runtime import runtime

HERE = Path(__file__).resolve().parent
IMAGE = 'node@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205'
TSC = HERE.parents[1] / 'node_modules/typescript/lib/tsc.js'


def run(*args, source=None):
    result = subprocess.run(args, input=source, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): {result.stderr}{result.stdout}')
    return result.stdout.strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled; do not use python -O')
    if run('git', 'branch', '--show-current') != 'experiment/boundscript-next':
        raise RuntimeError('Run only on experiment/boundscript-next')
    if not TSC.is_file():
        raise RuntimeError('Install existing repository dependencies first')
    # Optional fresh agent submission; the acceptance checks below are unchanged.
    submission = Path(sys.argv[1]) if len(sys.argv) == 2 else HERE / 'implementation/greet.ts'
    if len(sys.argv) > 2 or submission.is_symlink() or not submission.is_file():
        raise RuntimeError('Expected one regular greet.ts submission')
    if submission.stat().st_size > 16384:
        raise RuntimeError('Submission exceeds 16 KiB')
    # Do not pull images or implicitly access the network.
    engine = runtime()
    engine.image(IMAGE)
    name = 'boundscript-minimal-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-boundary-') as tmp:
        root = Path(tmp)
        inputs = root / 'inputs'
        candidate = root / 'implementation'
        inputs.mkdir()
        candidate.mkdir()
        for filename in ('task.md', 'contract.ts', 'slugger.ts'):
            shutil.copyfile(HERE / filename, inputs / filename)
        shutil.copyfile(submission, candidate / 'greet.ts')
        # Docker uses the invoking user's uid; ensure it is never root in-container.
        uid, gid = os.getuid(), os.getgid()
        if uid == 0:
            uid = gid = 65534
            os.chown(candidate, uid, gid)
        sentinel = root / 'host-secret.txt'
        sentinel.write_text('synthetic host-only sentinel; not a credential\n')
        protected = [sentinel, *inputs.iterdir()]
        before = {p: digest(p) for p in protected}
        # An actual host service distinguishes host access from container loopback.
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            listener.settimeout(0.2)
            port = listener.getsockname()[1]
            mounts = []
            for p in inputs.iterdir():
                mounts += ['--mount', f'type=bind,src={p},dst=/inputs/{p.name},readonly']
            mounts += ['--mount', f'type=bind,src={candidate},dst=/implementation',
                       '--mount', f'type=bind,src={TSC.parents[1]},dst=/tools/typescript,readonly']
            try:
                engine.create(name, IMAGE, mounts, uid, gid, workdir='/implementation')
                engine.start(name, uid, gid)
                print('PASS effective configuration: four Box mounts plus read-only TypeScript tooling, nonroot, offline, limits')

                def probe(label, source):
                    output = engine.exec(name, 'node', '--input-type=module', source=source)
                    return json.loads(output)

                observed = probe('authorized access', '''
import { readFileSync, writeFileSync } from 'node:fs';
const inputs = ['task.md', 'contract.ts', 'slugger.ts'].map(name => readFileSync('/inputs/' + name, 'utf8'));
writeFileSync('/implementation/access.txt', 'authorized write');
console.log(JSON.stringify(inputs));
''')
                assert observed == [(inputs / n).read_text() for n in ('task.md', 'contract.ts', 'slugger.ts')]
                assert (candidate / 'access.txt').read_text() == 'authorized write'
                print('PASS authorized access: three exact inputs readable; submission writable')
                # Only fixed actions enter the sandbox over stdin. Expected results and
                # all assertions remain here, outside it. Actions themselves are visible.
                observed = probe('forbidden access', '''
import { readFileSync, writeFileSync, symlinkSync } from 'node:fs';
const secret = SECRET;
const attempts = [
 ['host read', () => readFileSync(secret)],
 ['host write', () => writeFileSync(secret, 'changed')],
 ['input write', () => writeFileSync('/inputs/task.md', 'changed')],
 ['root write', () => writeFileSync('/outside.txt', 'changed')],
 ['repository read', () => readFileSync('/repo/package.json')],
 ['host credentials', () => readFileSync('/root/.ssh/id_rsa')],
 ['Docker socket', () => readFileSync('/var/run/docker.sock')],
];
symlinkSync(secret, '/implementation/host-link');
symlinkSync('/inputs/task.md', '/implementation/input-link');
attempts.push(
 ['symlink host read', () => readFileSync('/implementation/host-link')],
 ['symlink host write', () => writeFileSync('/implementation/host-link', 'changed')],
 ['symlink input write', () => writeFileSync('/implementation/input-link', 'changed')]
);
const observed = {};
for (const [label, action] of attempts) {
 try { action(); observed[label] = 'SUCCEEDED'; } catch (e) { observed[label] = e.code; }
}
console.log(JSON.stringify(observed));
'''.replace('SECRET', json.dumps(str(sentinel))))
                expected = {
                    'host read': {'ENOENT', 'EACCES'},
                    'host write': {'ENOENT', 'EACCES', 'EROFS'},
                    'input write': {'EROFS', 'EACCES'},
                    'root write': {'EROFS', 'EACCES'},
                    'repository read': {'ENOENT', 'EACCES'},
                    'host credentials': {'ENOENT', 'EACCES'},
                    'Docker socket': {'ENOENT', 'EACCES'},
                    'symlink host read': {'ENOENT', 'EACCES'},
                    'symlink host write': {'ENOENT', 'EACCES', 'EROFS'},
                    'symlink input write': {'EROFS', 'EACCES'},
                }
                assert observed.keys() == expected.keys()
                for label, codes in expected.items():
                    assert observed[label] in codes, (label, observed[label])
                    print(f'PASS {label}: {observed[label]}')
                observed = probe('network access', '''
import net from 'node:net';
const observed = [];
for (const [host, port] of [['127.0.0.1', PORT], ['1.1.1.1', 443]]) {
 const result = await new Promise(resolve => {
  const s = net.createConnection({host, port});
  s.setTimeout(1500);
  s.once('connect', () => { s.destroy(); resolve('CONNECTED'); });
  s.once('timeout', () => { s.destroy(); resolve('TIMEOUT'); });
  s.once('error', e => resolve(e.code));
 });
 observed.push(result);
}
console.log(JSON.stringify(observed));
'''.replace('PORT', str(port)))
                assert observed[0] == 'ECONNREFUSED', observed
                assert observed[1] in ('ENETUNREACH', 'EHOSTUNREACH'), observed
                print(f'PASS network denied: host loopback:{port} -> {observed[0]}; 1.1.1.1:443 -> {observed[1]}')
                try:
                    connection, _ = listener.accept()
                except TimeoutError:
                    pass
                else:
                    connection.close()
                    raise AssertionError('Sandbox reached host listener')
                # Use the actual contract paths, including absolute /inputs imports.
                # The trusted compiler and all candidate execution remain offline in Docker.
                engine.exec(name, 'node', '/tools/typescript/lib/tsc.js',
                    '--noEmit', '--strict', '--target', 'es2022', '--module', 'nodenext',
                    '--allowImportingTsExtensions', '/implementation/greet.ts')
                print('PASS native TypeScript contract: strict tsc --noEmit')
                observed = probe('Box behavior', '''
import { greet } from '/implementation/greet.ts';
const observed = ['  Ada Lovelace  ', 'Grace', '   '].map(name => {
 const calls = [];
 const output = greet(name, value => { calls.push(value); return 'external-slug'; });
 return {calls, output};
});
console.log(JSON.stringify(observed));
''')
                assert observed == [
                    {'calls': [name], 'output': f'Hello, {name}! [external-slug]'}
                    for name in ('Ada Lovelace', 'Grace', '')
                ]
                print('PASS Box behavior: three cases; authorized dependency called once per case')
                assert all(digest(p) == before[p] for p in protected)
                assert not (root / 'outside.txt').exists()
                print('PASS external authority: input/sentinel hashes unchanged; host listener untouched')
            finally:
                engine.remove(name)
    print('PASS all checks; disposable container and workspace removed')


if __name__ == '__main__':
    main()
