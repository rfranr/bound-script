"""Existing offline verification mechanics, shared by fixed Box entry points.

No experiment configuration, generation or promotion policy belongs here.
"""
from contextlib import contextmanager, ExitStack
import json
import os
import sys
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import uuid

from boundscript_internal.container_runtime import IMAGE, TSC, digest, runtime
from boundscript_internal.source_tree import staged_source_tree

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
RUNNER = Path(__file__).resolve().parent  # Shared trusted tooling, never Box data.


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
if not DEBUG:
    PROCESS_RUN = '''
    import {spawnSync} from 'node:child_process';
    const result = spawnSync(process.execPath, ARGS, {stdio: 'ignore', timeout: TIMEOUT});
    console.log(JSON.stringify({exitStatus: result.status, signal: result.signal,
    launchError: Boolean(result.error), timedOut: result.error?.code === 'ETIMEDOUT'}));
    '''
else:
    PROCESS_RUN = '''
    import {spawnSync} from 'node:child_process';
    const result = spawnSync(process.execPath, ARGS, {
        encoding: 'utf8',
        timeout: TIMEOUT,
        maxBuffer: 1024 * 1024,
        env: {
            ...process.env,
            DEBUG: '1'
        }
    });
    console.log(JSON.stringify({
        exitStatus: result.status,
        signal: result.signal,
        launchError: Boolean(result.error),
        timedOut: result.error?.code === 'ETIMEDOUT',
        stdout: result.stdout,
        stderr: result.stderr
    }));
    '''



def process_status(engine, name, args, timeout):
    # Tool-owned HOME data (including Vitest's API token) belongs in writable
    # work storage, never the read-only source. Container policy stays unchanged.
    source = "process.env.HOME = '/verification-work';\n" + PROCESS_RUN.replace(
        'ARGS', json.dumps(args)).replace('TIMEOUT', str(timeout * 1000))
    try:
        status = json.loads(engine.exec(name, 'node', '--input-type=module', source=source, timeout=timeout + 5))

        if DEBUG:
            print('STDOUT:', status.get('stdout', ''), flush=True)
            print('STDERR:', status.get('stderr', ''), flush=True)

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


def run_compiler(engine, name, scratch, source_files=('/implementation/implementation.ts',),
                 contract_module='/implementation/contract.ts'):
    status = process_status(engine, name,
                            ['/checks/compiler-diagnostics.mjs', contract_module, *source_files], 30)
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
        if file not in ('/checks/check-contract.ts', contract_module, *source_files):
            file = '[tooling/other source]'
        location = ':'.join(str(item[key]) if type(item.get(key)) is int else '?' for key in ('line', 'column'))
        print(f'  TS{item["code"]} {file}:{location}: {quoted(item.get("message"))}', flush=True)
    if report['errorCount']:
        raise VerificationFailure('compilation', 'Strict TypeScript compilation failed')
    if status['exitStatus'] != 0:
        raise VerificationFailure('infrastructure', 'Compiler failed without compiler diagnostics')


def vitest_failure(status, report_path, expected_files):
    """Print bounded test details; return a classified failure, never raw errors."""
    report = read_report(report_path)
    tests, failed = report.get('tests'), report.get('failed')
    if (not isinstance(tests, list) or not tests or len(tests) > 100
            or not isinstance(failed, list) or len(failed) > 10
            or type(report.get('infrastructureErrors')) is not int or report['infrastructureErrors'] < 0):
        if DEBUG:
            print(f"DEBUG: Invalid report structure -> tests: {type(tests)} (len={len(tests) if isinstance(tests, list) else 'N/A'}), failed: {type(failed)} (len={len(failed) if isinstance(failed, list) else 'N/A'}), infraErrors: {report.get('infrastructureErrors')}", file=sys.stderr)
        raise VerificationFailure('infrastructure', 'Invalid Vitest report; raw output withheld')
    files = report.get('files')
    if (not isinstance(files, list) or not all(isinstance(file, str) for file in files) or
            len(files) != len(expected_files) or set(files) != set(expected_files)):
        raise VerificationFailure('infrastructure', 'Declared Vitest files were not all collected exactly once')
    counts = dict(passed=0, failed=0, skipped=0, pending=0)
    executed = {file: 0 for file in expected_files}
    for test in tests:
        if (not isinstance(test, dict) or test.get('file') not in executed
                or not isinstance(test.get('name'), str) or test.get('status') not in counts):
            raise VerificationFailure('infrastructure', 'Invalid Vitest test result; raw output withheld')
        counts[test['status']] += 1
        if test['status'] in ('passed', 'failed'):
            executed[test['file']] += 1
            print(f'{"PASS" if test["status"] == "passed" else "FAIL"} {quoted(test["file"], 300)}: {quoted(test["name"], 300)}', flush=True)
    kinds = set()
    for test in failed:
        if not isinstance(test, dict) or test.get('file') not in executed:
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
    if report['infrastructureErrors'] or counts['pending'] or counts['skipped'] or not all(executed.values()):
        return VerificationFailure('infrastructure', 'Vitest collection/unhandled/incomplete-run failure; details withheld')
    if counts['failed'] or failed:
        return VerificationFailure('/'.join(sorted(kinds)) or 'runtime', 'Vitest tests failed; see sanitized results above')
    if status['exitStatus'] != 0:
        return VerificationFailure('infrastructure', 'Vitest failed without failed tests; raw output withheld')
    return None


def suite_config(suite):
    """Exact file selection using native Vitest include, never test descriptions."""
    return ("import base from './vitest.config.mts';\n"
            'export default { ...base, test: { ...base.test, include: '
            + json.dumps(suite.files) + ' } };\n')

def run_vitest(engine, name, scratch, suite, index):
    args = ['/node_modules/vitest/vitest.mjs', 'run', '--config', f'/checks/suite-{index}.config.mts',
            '--configLoader', 'runner', '--no-cache', '--fsModuleCachePath', '/verification-work/.vitest-cache',
            '--allowOnly=false', '--reporter', '/checks/diagnostic-reporter.mjs']
    path = scratch / 'vitest-diagnostics.json'
    path.unlink(missing_ok=True)  # Never accept the preceding phase's report.
    status = process_status(engine, name, args, 85)
    try:
        failure = vitest_failure(status, path, suite.files)
    except VerificationFailure:
        print(f'Vitest exit status: {status["exitStatus"]}; report invalid/unavailable', flush=True)
        raise
    if failure:
        if DEBUG:
            print ( failure )
        raise failure


def _assert_source_view(root, expected):
    """Check complete membership as well as bytes of the private read-only view."""
    directories = {parent.as_posix() for file in expected for parent in Path(file).parents
                   if parent != Path('.')}
    seen = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root).as_posix()
        assert relative in expected or relative in directories, 'Unexpected source entry'
        assert not path.is_symlink(), 'Source view contains a symlink'
        seen.add(relative)
        if relative in directories:
            assert path.is_dir(), 'Source directory changed'
        else:
            size, sha = expected[relative]
            assert path.is_file() and path.stat().st_size == size, 'Source file changed'
            assert digest(path) == sha, 'Source bytes changed'
    assert seen == set(expected) | directories, 'Source membership changed'


def check(submission, *, box_root, box, source_tree=False):
    with ExitStack() as resources:
        records = None
        if source_tree:
            with phase('Source tree staging'):
                if not __debug__:
                    raise VerificationFailure('infrastructure', 'Assertions must be enabled')
                oracle = (box_root / box.verification_path).resolve()
                selected = submission.resolve()
                if selected.is_relative_to(oracle) or oracle.is_relative_to(selected):
                    raise VerificationFailure('infrastructure', 'Source tree and verification root must be disjoint')
                try:
                    submission, records = resources.enter_context(staged_source_tree(submission))
                except ValueError as error:
                    raise VerificationFailure('infrastructure', str(error)) from None
        _check(submission, box_root=box_root, box=box, source_records=records)


def _check(submission, *, box_root, box, source_records=None):
    verification_root = box_root / box.verification_path
    contract = box_root / box.contract_path
    with phase('Verifier preflight'):
        if not __debug__:
            raise VerificationFailure('infrastructure', 'Assertions must be enabled')
        if source_records is None and (submission.is_symlink() or not submission.is_file()
                                       or submission.stat().st_size > 16384):
            raise VerificationFailure('infrastructure', 'Expected regular submission of at most 16 KiB')
        try:
            verification_files = box.verification_files(verification_root)
        except ValueError as error:
            raise VerificationFailure('infrastructure', str(error)) from None
        engine = runtime()
        engine.image(IMAGE)
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    name = 'boundscript-native-check-' + uuid.uuid4().hex[:12]
    with tempfile.TemporaryDirectory(prefix='boundscript-native-check-') as tmp:
        root = Path(tmp)
        checks = root / 'checks'
        checks.mkdir()
        reserved = {'check-contract.ts', 'vitest.config.mts', 'diagnostic-reporter.mjs',
                    'compiler-diagnostics.mjs', *[f'suite-{i}.config.mts' for i in range(len(box.suites))]}
        if reserved.intersection(verification_files):
            raise VerificationFailure('infrastructure', 'Verification inputs collide with runner files')
        for filename in verification_files:
            destination = checks / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verification_root / filename, destination)
        for filename in ('vitest.config.mts', 'diagnostic-reporter.mjs', 'compiler-diagnostics.mjs'):
            shutil.copyfile(RUNNER / filename, checks / filename)
        for index, suite in enumerate(box.suites):
            (checks / f'suite-{index}.config.mts').write_text(suite_config(suite), encoding='utf-8')
        (checks / 'check-contract.ts').write_text(box.contract_check(
            '/implementation/implementation.ts'), encoding='utf-8')
        scratch = root / 'scratch'
        scratch.mkdir()
        if os.getuid() == 0:
            os.chown(scratch, uid, gid)
        inputs = ({'implementation.ts': submission} if source_records is None else
                  {relative: submission / relative for relative, _, _ in source_records})
        protected = [*inputs.values(), *[p for p in checks.rglob('*') if p.is_file()], contract]
        before = {p: digest(p) for p in protected}
        source = root / 'source'
        source.mkdir(mode=0o755)
        expected = {}
        with phase('Source view integrity'):
            for relative, path in inputs.items():
                target = source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                target.chmod(0o644)
                expected[relative] = (path.stat().st_size, before[path])
            if source_records is not None:
                assert tuple(sorted((file, size, sha) for file, (size, sha) in expected.items())) == source_records
            try:
                contract_relative = Path(box.contract_module).relative_to('/implementation')
            except ValueError:
                contract_relative = None
            if contract_relative is not None:
                if (not contract_relative.parts or '..' in contract_relative.parts
                        or contract_relative.as_posix() in expected):
                    raise VerificationFailure('infrastructure', 'Contract mount collides with source')
                target = source / contract_relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(contract, target)
                target.chmod(0o644)
                expected[contract_relative.as_posix()] = (contract.stat().st_size, before[contract])
            _assert_source_view(source, expected)
        source_files = tuple('/implementation/' + file for file in inputs)
        bindings = {source: '/implementation', checks: '/checks',
                    contract: box.contract_module, TSC.parents[2]: '/node_modules'}
        mounts = ['--mount', f'type=bind,src={scratch},dst=/verification-work']
        for binding_source, destination in bindings.items():
            mounts += ['--mount', f'type=bind,src={binding_source},dst={destination},readonly']
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
 () => writeFileSync(CHECK_FILE, 'changed'),
 ...SOURCE_FILES.map(file => () => writeFileSync(file, 'changed')),
 () => writeFileSync('/outside.txt', 'changed'),
 () => { symlinkSync(CONTRACT_MODULE, '/verification-work/escape');
         try { writeFileSync('/verification-work/escape', 'changed'); }
         finally { unlinkSync('/verification-work/escape'); } },
]) { try { action(); result.push('SUCCEEDED'); } catch (e) { result.push(e.code); } }
console.log(JSON.stringify(result));
'''.replace('CONTRACT_MODULE', json.dumps(box.contract_module))
   .replace('CHECK_FILE', json.dumps('/checks/' + box.suites[0].files[0]))
   .replace('SOURCE_FILES', json.dumps(source_files))))
                assert observed == ['ENOENT'] * 3 + ['EROFS'] * (4 + len(source_files))
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
                run_compiler(engine, name, scratch, source_files, box.contract_module)
            labels = {'runtime': 'Typia runtime validation', 'acceptance': 'Vitest acceptance tests',
                      'properties': 'fast-check properties'}
            for category in box.optional_categories:
                print(f'NOT APPLICABLE {labels[category]} (explicit Box declaration)', flush=True)
            for index, suite in enumerate(box.suites):
                with phase(' + '.join(labels[category] for category in suite.categories)):
                    print(f'[RUN VITEST] {suite}')
                    run_vitest(engine, name, scratch, suite, index)
            with phase('Protected input integrity'):
                _assert_source_view(source, expected)
                assert all(digest(p) == old for p, old in before.items())
        finally:
            with phase('Sandbox cleanup'):
                engine.remove(name)
    print('PASS independent native verification; no promotion performed by verifier', flush=True)
