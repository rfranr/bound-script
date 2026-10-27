#!/usr/bin/env python3
"""Fixed offline Box verification; no candidate execution on the host."""
from contextlib import contextmanager
from importlib import import_module
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
SPIKE = Path(__file__).resolve().parent
sys.path.insert(0, str(SPIKE.parents[1]))
from boundscript_internal.container_runtime import IMAGE, TSC, digest, runtime
configuration = import_module('experiments.native-typescript-contracts.native_box')
BOX = configuration.BOX
BASELINE_SOURCE = configuration.BASELINE_SOURCE


class VerificationFailure(RuntimeError):
    """Only host-authored labels and explicitly sanitized details may enter here."""
    def __init__(self, kind, detail):
        self.kind = kind
        super().__init__(detail)


@contextmanager
def phase(label):
    print(f'START {label}', flush=True)
    try:
        yield
    except VerificationFailure as error:
        print(f'FAIL {label} [{error.kind}]', flush=True)
        raise
    except subprocess.TimeoutExpired:
        print(f'FAIL {label} [timeout]', flush=True)
        raise VerificationFailure('timeout', f'{label} timed out; raw diagnostics withheld') from None
    except AssertionError:
        print(f'FAIL {label} [security/integrity]', flush=True)
        raise VerificationFailure('security/integrity', f'{label} assertion failed; raw diagnostics withheld') from None
    except Exception:
        print(f'FAIL {label} [infrastructure]', flush=True)
        raise VerificationFailure('infrastructure', f'{label} failed; raw diagnostics withheld') from None
    else:
        print(f'PASS {label}', flush=True)


def sanitize(value, limit=2000):
    if not isinstance(value, str):
        return value if value is None or type(value) in (bool, int, float) else '[withheld]'
    value = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', value)
    for key, secret in os.environ.items():
        if secret and (len(secret) >= 8 or re.search(
                r'auth|token|secret|password|credential|key|cookie|session|database.?url', key, re.I)):
            value = value.replace(secret, '[REDACTED]')
    value = re.sub(r'(?i)bearer\s+[^\s\"\x27,}]+|sk-[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
                   '[REDACTED]', value)
    value = re.sub(r'(?i)((?:token|password|secret|api[_-]?key|authorization)\s*[\"\x27]?\s*[:=]\s*)[^\n,}]+',
                   r'\1[REDACTED]', value)
    return value[:limit] + (' [truncated]' if len(value) > limit else '')


def quoted(value, limit=2000):
    return json.dumps(sanitize(value, limit), ensure_ascii=True)


def read_report(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError()
            raw = stream.read(262145)
        if len(raw) > 262144:
            raise ValueError()
        report = json.loads(raw)
        if not isinstance(report, dict) or report.get('complete') is not True:
            raise ValueError()
        return report
    except (OSError, ValueError, TypeError, RecursionError):
        raise VerificationFailure('infrastructure', 'Missing or invalid structured report; raw output withheld') from None


# Fixed parent process: candidate stdout/stderr never reaches the host channel.
# Only bounded reports and process status are consumed. Not an agent capability.
PROCESS_RUN = '''
import {spawnSync} from 'node:child_process';
const result = spawnSync(process.execPath, ARGS, {stdio: 'ignore', timeout: TIMEOUT});
console.log(JSON.stringify({exitStatus: result.status, signal: result.signal,
 launchError: Boolean(result.error), timedOut: result.error?.code === 'ETIMEDOUT'}));
'''


def process_status(engine, name, args, timeout):
    source = PROCESS_RUN.replace('ARGS', json.dumps(args)).replace('TIMEOUT', str(timeout * 1000))
    try:
        status = json.loads(engine.exec(name, 'node', '--input-type=module', source=source, timeout=timeout + 5))
        if (not isinstance(status, dict) or type(status.get('launchError')) is not bool
                or type(status.get('timedOut')) is not bool
                or (status.get('exitStatus') is not None and
                    (type(status['exitStatus']) is not int or not -255 <= status['exitStatus'] <= 255))
                or status.get('signal') not in (None, 'SIGKILL', 'SIGTERM', 'SIGSEGV', 'SIGABRT', 'SIGINT')):
            raise ValueError()
    except subprocess.TimeoutExpired:
        raise VerificationFailure('timeout', 'Verifier transport timed out; raw output withheld') from None
    except Exception:
        raise VerificationFailure('infrastructure', 'Verifier transport/status unavailable; raw output withheld') from None
    if status['timedOut'] or status['launchError'] or status.get('signal'):
        print(f'Offline tool exit status: {status.get("exitStatus")}; signal: {status.get("signal") or "none"}', flush=True)
        if status['timedOut']:
            raise VerificationFailure('timeout', 'Offline tool timed out; raw output withheld')
        raise VerificationFailure('infrastructure', 'Offline tool startup/process failure; raw output withheld')
    return status


def run_compiler(engine, name, scratch):
    status = process_status(engine, name, ['/checks/compiler-diagnostics.mjs'], 30)
    try:
        report = read_report(scratch / 'typescript-diagnostics.json')
    except VerificationFailure:
        print(f'TypeScript exit status: {status["exitStatus"]}; report unavailable', flush=True)
        raise
    if (type(report.get('errorCount')) is not int or report['errorCount'] < 0
            or not isinstance(report.get('diagnostics'), list)):
        raise VerificationFailure('infrastructure', 'Invalid compiler report; raw output withheld')
    print(f'TypeScript exit status: {status["exitStatus"]}; errors: {report["errorCount"]}', flush=True)
    for item in report['diagnostics'][:20]:
        if not isinstance(item, dict) or type(item.get('code')) is not int:
            raise VerificationFailure('infrastructure', 'Invalid compiler diagnostic; raw output withheld')
        file = item.get('file')
        if file not in ('/checks/check-contract.ts', '/implementation/implementation.ts', '/inputs/contract.ts'):
            file = '[tooling/other source]'
        location = ':'.join(str(item[key]) if type(item.get(key)) is int else '?' for key in ('line', 'column'))
        print(f'  TS{item["code"]} {file}:{location}: {quoted(item.get("message"))}', flush=True)
    if report['errorCount']:
        raise VerificationFailure('compilation', 'Strict TypeScript compilation failed')
    if status['exitStatus'] != 0:
        raise VerificationFailure('infrastructure', 'Compiler failed without compiler diagnostics')


def vitest_failure(status, report_path):
    """Print bounded test details; return a classified failure, never raw errors."""
    report = read_report(report_path)
    tests, failed = report.get('tests'), report.get('failed')
    if (not isinstance(tests, list) or not tests or len(tests) > 100
            or not isinstance(failed, list) or len(failed) > 10
            or type(report.get('infrastructureErrors')) is not int or report['infrastructureErrors'] < 0):
        raise VerificationFailure('infrastructure', 'Invalid Vitest report; raw output withheld')
    counts = dict(passed=0, failed=0, skipped=0, pending=0)
    for test in tests:
        if (not isinstance(test, dict) or test.get('file') not in ('acceptance.test.ts', 'validators.test.ts')
                or not isinstance(test.get('name'), str) or test.get('status') not in counts):
            raise VerificationFailure('infrastructure', 'Invalid Vitest test result; raw output withheld')
        counts[test['status']] += 1
        if test['status'] in ('passed', 'failed'):
            print(f'{"PASS" if test["status"] == "passed" else "FAIL"} {test["file"]}: {quoted(test["name"], 300)}', flush=True)
    kinds = set()
    for test in failed:
        if not isinstance(test, dict):
            raise VerificationFailure('infrastructure', 'Invalid Vitest failure; raw output withheld')
        assertions, guards = test.get('assertions'), test.get('typia')
        if not isinstance(assertions, list) or not isinstance(guards, list):
            raise VerificationFailure('infrastructure', 'Invalid Vitest error fields; raw output withheld')
        print(f'  Details for {quoted(test.get("name"), 300)}:', flush=True)
        for guard in guards[:2]:
            if not isinstance(guard, dict):
                continue
            actual = guard.get('actualType')
            if actual not in ('undefined', 'null', 'array', 'object', 'string', 'number', 'boolean', 'bigint', 'symbol', 'function'):
                actual = 'unknown'
            # Dynamic property keys may themselves contain input values. Only
            # expose declared contact fields, never arbitrary bracket/path text.
            path = guard.get('path')
            if not isinstance(path, str) or not re.fullmatch(r'\$input(?:\.(?:contact|name|email|phone|ok|errors)|\[\d{1,4}\])*', path):
                path = '[dynamic path withheld]'
            print(f'    Typia path={quoted(path)} expected={quoted(guard.get("expected"), 500)} actual type={actual}', flush=True)
            kinds.add('typia')
        for assertion in assertions[:2]:
            if isinstance(assertion, dict):
                for key in ('expected', 'actual', 'diff'):
                    if key in assertion:
                        if key == 'diff' and isinstance(assertion[key], str):
                            print('    diff:', flush=True)
                            for line in sanitize(assertion[key]).split('\n')[:40]:
                                print('      | ' + json.dumps(line, ensure_ascii=True)[1:-1], flush=True)
                        else:
                            print(f'    {key}: {quoted(assertion[key])}', flush=True)
                kinds.add('assertion')
        if test.get('timedOut') is True:
            print('    Vitest test/hook timeout; message/stack withheld', flush=True)
            kinds.add('timeout')
        elif not assertions and not guards:
            print('    Runtime exception; message/stack withheld', flush=True)
            kinds.add('runtime')
    if counts['failed'] > len(failed):
        print('Additional failed-test details omitted by the bounded reporter', flush=True)
    print(f'Vitest exit status: {status["exitStatus"]}; ' + ', '.join(f'{n} {key}' for key, n in counts.items()), flush=True)
    if report['infrastructureErrors'] or counts['pending'] or not (counts['passed'] + counts['failed']):
        return VerificationFailure('infrastructure', 'Vitest collection/unhandled/incomplete-run failure; details withheld')
    if counts['failed'] or failed:
        return VerificationFailure('/'.join(sorted(kinds)) or 'runtime', 'Vitest tests failed; see sanitized results above')
    if status['exitStatus'] != 0:
        return VerificationFailure('infrastructure', 'Vitest failed without failed tests; raw output withheld')
    return None


def run_vitest(engine, name, scratch, group='all'):
    args = ['/node_modules/vitest/vitest.mjs', 'run', '--config', '/checks/vitest.config.mts',
            '--configLoader', 'runner', '--no-cache', '--fsModuleCachePath', '/implementation/.vitest-cache',
            '--reporter', '/checks/diagnostic-reporter.mjs']
    if group == 'typia':
        args += ['validators.test.ts']
    elif group == 'acceptance':
        args += ['acceptance.test.ts', '--testNamePattern', '^matches native acceptance case ']
    elif group == 'properties':
        args += ['acceptance.test.ts', '--testNamePattern', '^(?!matches native acceptance case )']
    path = scratch / 'vitest-diagnostics.json'
    path.unlink(missing_ok=True)  # Never accept the preceding phase's report.
    status = process_status(engine, name, args, 85)
    try:
        failure = vitest_failure(status, path)
    except VerificationFailure:
        print(f'Vitest exit status: {status["exitStatus"]}; report invalid/unavailable', flush=True)
        raise
    if failure:
        raise failure


def check(submission, box=None):
    box = BOX if box is None else box
    verification_root = SPIKE / box.verification_path
    contract = SPIKE / box.contract_path
    with phase('Verifier preflight'):
        if not __debug__:
            raise VerificationFailure('infrastructure', 'Assertions must be enabled')
        if submission.is_symlink() or not submission.is_file() or submission.stat().st_size > 16384:
            raise VerificationFailure('infrastructure', 'Expected regular submission of at most 16 KiB')
        if not (verification_root / '.generated/validators.ts').is_file():
            raise VerificationFailure('infrastructure', 'Run npm run build:native first')
        engine = runtime()
        engine.image(IMAGE)
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    name = 'boundscript-native-check-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-native-check-') as tmp:
        root = Path(tmp)
        checks = root / 'checks'
        checks.mkdir()
        for filename in ('acceptance.test.ts', 'validators.test.ts', 'vitest.config.mts',
                         'diagnostic-reporter.mjs', 'compiler-diagnostics.mjs', 'cases.json'):
            shutil.copyfile(verification_root / filename, checks / filename)
        (checks / 'check-contract.ts').write_text(box.contract_check(
            '/implementation/implementation.ts'), encoding='utf-8')
        shutil.copytree(verification_root / '.generated', checks / '.generated')
        shutil.copytree(verification_root / 'src', checks / 'src')
        scratch = root / 'scratch'
        scratch.mkdir()
        if os.getuid() == 0:
            os.chown(scratch, uid, gid)
        protected = [submission, *[p for p in checks.rglob('*') if p.is_file()], contract]
        before = {p: digest(p) for p in protected}
        bindings = {checks: '/checks', submission.resolve(): '/implementation/implementation.ts',
                    contract: box.contract_module, TSC.parents[2]: '/node_modules'}
        mounts = ['--mount', f'type=bind,src={scratch},dst=/implementation']
        for source, destination in bindings.items():
            mounts += ['--mount', f'type=bind,src={source},dst={destination},readonly']
        try:
            with phase('Sandbox/security checks'):
                engine.create(name, IMAGE, mounts, uid, gid, workdir='/implementation')
                engine.start(name, uid, gid)
                observed = json.loads(engine.exec(name, 'node', '--input-type=module', source='''
import {readFileSync, writeFileSync, symlinkSync, unlinkSync} from 'node:fs';
const result = [];
for (const action of [
 () => readFileSync('/repo/package.json'),
 () => readFileSync('/run/host-auth.json'),
 () => readFileSync('/peer/implementation.ts'),
 () => writeFileSync(CONTRACT_MODULE, 'changed'),
 () => writeFileSync('/checks/acceptance.test.ts', 'changed'),
 () => writeFileSync('/implementation/implementation.ts', 'changed'),
 () => writeFileSync('/outside.txt', 'changed'),
 () => { symlinkSync(CONTRACT_MODULE, '/implementation/escape');
         try { writeFileSync('/implementation/escape', 'changed'); }
         finally { unlinkSync('/implementation/escape'); } },
]) { try { action(); result.push('SUCCEEDED'); } catch (e) { result.push(e.code); } }
console.log(JSON.stringify(result));
'''.replace('CONTRACT_MODULE', json.dumps(box.contract_module))))
                assert observed == ['ENOENT'] * 3 + ['EROFS'] * 5
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
                assert network in ('ENETUNREACH', 'EHOSTUNREACH')
            with phase('TypeScript compilation'):
                run_compiler(engine, name, scratch)
            for label, group in [('Typia runtime validation (validator suite)', 'typia'),
                                 ('Vitest acceptance tests (with runtime input/output guards)', 'acceptance'),
                                 ('fast-check properties', 'properties')]:
                with phase(label):
                    run_vitest(engine, name, scratch, group)
            with phase('Protected input integrity'):
                assert all(digest(p) == old for p, old in before.items())
        finally:
            with phase('Sandbox cleanup'):
                engine.remove(name)
    print('PASS independent native verification; no promotion performed by verifier', flush=True)


def main():
    args = sys.argv[1:]
    if args[:1] == ['--box-definition']:
        if len(args) < 2 or args[1] != BOX.fingerprint():
            raise VerificationFailure('infrastructure', 'Generation/verification Box definition mismatch')
        args = args[2:]
    if args == ['--baseline']:
        submission = (SPIKE / BASELINE_SOURCE).resolve()
    elif len(args) <= 1 and (not args or not args[0].startswith('--')):
        submission = Path(args[0]).absolute() if args else SPIKE / BOX.accepted_path
    else:
        raise VerificationFailure('infrastructure', 'Expected optional candidate path or --baseline')
    try:
        check(submission)
    except Exception:
        print('Candidate retained in place (not promoted): ' + quoted(str(submission)), flush=True)
        raise


def cli():
    try:
        main()
    except VerificationFailure as error:
        print(f'FAIL [{error.kind}] {error}', flush=True)
        return 1
    except Exception:
        print('FAIL [infrastructure] Verifier failed; raw diagnostics withheld', flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(cli())
