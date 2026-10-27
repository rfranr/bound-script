#!/usr/bin/env python3
"""Fixed NormalizeContact spike; candidate code only executes offline in a container."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
BASE = SPIKE.parent / 'minimal-box'
sys.path.insert(0, str(BASE))
# Avoid importing this file again under its baseline sibling's module name.
from verify_pair import CASES, PAIR, check as baseline_check
from container_runtime import runtime
from verify import IMAGE, TSC, digest, run


def check(submission):
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    if submission.is_symlink() or not submission.is_file() or submission.stat().st_size > 16384:
        raise RuntimeError('Expected regular submission of at most 16 KiB')
    if not (SPIKE / '.generated/validators.ts').is_file():
        raise RuntimeError('Run npm run build:native first')
    engine = runtime()
    engine.image(IMAGE)
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    name = 'boundscript-native-check-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-native-check-') as tmp:
        root = Path(tmp)
        checks = root / 'checks'
        checks.mkdir()
        for filename in ('acceptance.test.ts', 'validators.test.ts', 'vitest.config.mts', 'check-contract.ts'):
            shutil.copyfile(SPIKE / filename, checks / filename)
        shutil.copytree(SPIKE / '.generated', checks / '.generated')
        shutil.copytree(SPIKE / 'src', checks / 'src')
        (checks / 'cases.json').write_text(json.dumps([
            {'input': raw, 'expected': expected} for raw, expected in CASES
        ]))
        scratch = root / 'scratch'
        scratch.mkdir()
        if os.getuid() == 0:
            os.chown(scratch, uid, gid)
        protected = [submission, *[p for p in checks.rglob('*') if p.is_file()], SPIKE / 'src/contract.ts']
        before = {p: digest(p) for p in protected}
        bindings = {
            checks: '/checks',
            submission.resolve(): '/implementation/implementation.ts',
            SPIKE / 'src/contract.ts': '/inputs/contract.ts',
            TSC.parents[2]: '/node_modules',
        }
        mounts = ['--mount', f'type=bind,src={scratch},dst=/implementation']
        for source, destination in bindings.items():
            mounts += ['--mount', f'type=bind,src={source},dst={destination},readonly']
        try:
            engine.create(name, IMAGE, mounts, uid, gid, workdir='/implementation')
            engine.start(name, uid, gid)
            # Fixed probes before loading any candidate or test code.
            observed = json.loads(engine.exec(name, 'node', '--input-type=module', source='''
import {readFileSync, writeFileSync, symlinkSync, unlinkSync} from 'node:fs';
const result = [];
for (const action of [
 () => readFileSync('/repo/package.json'),
 () => readFileSync('/run/host-auth.json'),
 () => readFileSync('/peer/implementation.ts'),
 () => writeFileSync('/inputs/contract.ts', 'changed'),
 () => writeFileSync('/checks/acceptance.test.ts', 'changed'),
 () => writeFileSync('/implementation/implementation.ts', 'changed'),
 () => writeFileSync('/outside.txt', 'changed'),
 () => { symlinkSync('/inputs/contract.ts', '/implementation/escape');
         try { writeFileSync('/implementation/escape', 'changed'); }
         finally { unlinkSync('/implementation/escape'); } },
]) { try { action(); result.push('SUCCEEDED'); } catch (e) { result.push(e.code); } }
console.log(JSON.stringify(result));
'''))
            assert observed == ['ENOENT'] * 3 + ['EROFS'] * 5, observed
            network = json.loads(engine.exec(name, 'node', '--input-type=module', source='''
import net from 'node:net';
const result = await new Promise(resolve => {
 const s = net.createConnection({host: '1.1.1.1', port: 443});
 s.setTimeout(1500);
 s.once('connect', () => { s.destroy(); resolve('CONNECTED'); });
 s.once('timeout', () => { s.destroy(); resolve('TIMEOUT'); });
 s.once('error', e => resolve(e.code));
});
console.log(JSON.stringify(result));
'''))
            assert network in ('ENETUNREACH', 'EHOSTUNREACH'), network
            engine.exec(name, 'node', '/node_modules/typescript/lib/tsc.js',
                        '--noEmit', '--strict', '--target', 'es2022', '--module', 'nodenext',
                        '--allowImportingTsExtensions', '/checks/check-contract.ts')
            # Generated validators are trusted, read-only inputs; no Typia calls
            # requiring transformation are handed directly to Vite's transpiler.
            engine.exec(name, 'node', '/node_modules/vitest/vitest.mjs', 'run',
                        '--config', '/checks/vitest.config.mts', '--configLoader', 'runner',
                        '--no-cache', '--fsModuleCachePath', '/implementation/.vitest-cache',
                        timeout=90)
            assert all(digest(p) == old for p, old in before.items())
            print('PASS native: strict contract, Typia, 20 baseline examples, 5 properties, protected/offline probes')
        finally:
            engine.remove(name)
    # Reuse all original external acceptance assertions, not only a Vitest port.
    # Calling the fixed check directly avoids the baseline CLI's branch guard;
    # no baseline code, fixtures, assertions or source files are changed.
    baseline_check('normalize-contact', submission)


def main():
    if not __debug__ or run('git', 'branch', '--show-current') not in (
        'experiment/boundscript-next', 'experiment/typescript-contracts'
    ):
        raise RuntimeError('Use the baseline or dedicated TypeScript experiment branch with assertions enabled')
    args = sys.argv[1:]
    if args == ['--baseline']:
        submission = PAIR / 'accepted/normalize-contact.ts'
    elif len(args) <= 1:
        submission = Path(args[0]).resolve() if args else SPIKE / 'accepted/normalize-contact.ts'
    else:
        raise RuntimeError('Expected optional candidate path or --baseline')
    check(submission)


if __name__ == '__main__':
    main()
