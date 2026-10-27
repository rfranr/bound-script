#!/usr/bin/env python3
"""Fixed NormalizeContact spike; candidate code only executes offline in a container."""
import json
import os
from pathlib import Path
import re
import stat
import shutil
import sys
import tempfile
import uuid
import subprocess

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
BASE = SPIKE.parent / 'minimal-box'
sys.path.insert(0, str(BASE))
# Avoid importing this file again under its baseline sibling's module name.
from verify_pair import CASES, PAIR
from container_runtime import runtime
from verify import IMAGE, TSC, digest, run


# The child cannot stream candidate stdout/stderr into the diagnostic channel.
# Only this fixed parent emits process status; the reporter writes selected fields.
VITEST_RUN = '''
import {spawnSync} from 'node:child_process';
const result = spawnSync(process.execPath, [
 '/node_modules/vitest/vitest.mjs', 'run',
 '--config', '/checks/vitest.config.mts', '--configLoader', 'runner',
 '--no-cache', '--fsModuleCachePath', '/implementation/.vitest-cache',
 '--reporter', '/checks/diagnostic-reporter.mjs',
], {stdio: 'ignore', timeout: 85000});
console.log(JSON.stringify({exitStatus: result.status, signal: result.signal,
 launchError: Boolean(result.error)}));
'''


def sanitize(value, limit=2000):
    if not isinstance(value, str):
        return value if value is None or type(value) in (bool, int, float) else '[withheld]'
    # Redact before truncation so a partial token cannot escape the filter.
    value = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', value)
    for key, secret in os.environ.items():
        if secret and (len(secret) >= 8 or re.search(
                r'auth|token|secret|password|credential|key|cookie|session|database.?url', key, re.I)):
            value = value.replace(secret, '[REDACTED]')
    value = re.sub(r'(?i)bearer\s+[^\s\"\x27,}]+|sk-[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
                   '[REDACTED]', value)
    value = re.sub(r'(?i)((?:token|password|secret|api[_-]?key|authorization)\s*[\"\x27]?\s*[:=]\s*)[^\n,}]+',
                   r'\1[REDACTED]', value)
    # JSON quoting at the output boundary escapes terminal/control characters.
    return value[:limit] + (' [truncated]' if len(value) > limit else '')


def vitest_failure(status, report_path):
    """Return only allowlisted, bounded diagnostics; treat artifacts as untrusted."""
    code = status.get('exitStatus')
    if code is not None and (type(code) is not int or not -255 <= code <= 255):
        raise RuntimeError('Offline verifier infrastructure failure: invalid Vitest exit status')
    signal = status.get('signal')
    signal = signal if signal in ('SIGKILL', 'SIGTERM', 'SIGSEGV', 'SIGABRT') else None
    summary = f'Vitest exit status: {code}; signal: {signal or "none"}'
    try:
        fd = os.open(report_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError()
            raw = stream.read(131073)
        if len(raw) > 131072:
            raise ValueError()
        report = json.loads(raw)
        if (report.get('complete') is not True or type(report.get('failed')) is not list
                or type(report.get('infrastructureErrors')) is not int
                or report['infrastructureErrors'] < 0):
            raise ValueError()
        for test in report['failed']:
            if (not isinstance(test, dict)
                    or test.get('file') not in ('acceptance.test.ts', 'validators.test.ts')
                    or not isinstance(test.get('name'), str)
                    or not isinstance(test.get('assertions'), list)
                    or not all(isinstance(item, dict) for item in test['assertions'])):
                raise ValueError()
    except (OSError, ValueError, TypeError, AttributeError, RecursionError):
        return summary + '\nOffline verifier infrastructure failure: missing or invalid Vitest report; raw output withheld'
    lines = [summary]
    for test in report['failed'][:10]:
        lines.append('FAIL ' + test['file'] + ': ' + json.dumps(sanitize(test.get('name'), 300), ensure_ascii=True))
        assertions = test.get('assertions')
        if not isinstance(assertions, list) or not assertions:
            lines.append('  Test execution error; non-assertion details withheld')
            continue
        for assertion in assertions[:2]:
            if isinstance(assertion, dict):
                for key in ('expected', 'actual', 'diff'):
                    if key in assertion:
                        lines.append('  ' + key + ': ' + json.dumps(sanitize(assertion[key]), ensure_ascii=True))
    if report['infrastructureErrors'] or status.get('launchError') or signal:
        lines.append('Offline verifier infrastructure failure: collection, unhandled error, or process failure; details withheld')
    elif report['failed']:
        lines.append('Vitest test failures (not a verifier startup failure)')
    elif code != 0:
        lines.append('Offline verifier infrastructure failure: no failed tests reported; raw output withheld')
    else:
        return None
    return '\n'.join(lines)


def run_vitest(engine, name, scratch):
    try:
        status = json.loads(engine.exec(name, 'node', '--input-type=module', source=VITEST_RUN, timeout=90))
        if (not isinstance(status, dict) or set(status) != {'exitStatus', 'signal', 'launchError'}
                or type(status['launchError']) is not bool
                or (status['signal'] is not None and not isinstance(status['signal'], str))):
            raise ValueError()
    except Exception:
        raise RuntimeError('Offline verifier infrastructure failure: Vitest transport/status unavailable; raw output withheld') from None
    failure = vitest_failure(status, scratch / 'vitest-diagnostics.json')
    if failure:
        raise RuntimeError(failure)


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
        for filename in ('acceptance.test.ts', 'validators.test.ts', 'vitest.config.mts', 'check-contract.ts',
                         'diagnostic-reporter.mjs'):
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
            # TODO: TEMPORAL VERBOSE ADDED | engine.exec(name, 'node', '/node_modules/typescript/lib/tsc.js',
            # TODO: TEMPORAL VERBOSE ADDED |             '--noEmit', '--strict', '--target', 'es2022', '--module', 'nodenext',
            # TODO: TEMPORAL VERBOSE ADDED |             '--allowImportingTsExtensions', '/checks/check-contract.ts')


            result = subprocess.run(
                [
                    engine.executable, 'exec', name,
                    'node', '/node_modules/typescript/lib/tsc.js',
                    '--noEmit', '--strict', '--target', 'es2022',
                    '--module', 'nodenext',
                    '--allowImportingTsExtensions',
                    '/checks/check-contract.ts'
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode:
                print("TYPESCRIPT FAILED:")
                print(result.stdout)
                print(result.stderr)
                raise RuntimeError("TypeScript compilation failed")

            # Generated validators are trusted, read-only inputs; no Typia calls
            # requiring transformation are handed directly to Vite's transpiler.
            run_vitest(engine, name, scratch)
            assert all(digest(p) == old for p, old in before.items())
            print('PASS native: strict contract, Typia, 20 baseline examples, 5 properties, protected/offline probes')
        finally:
            engine.remove(name)


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
