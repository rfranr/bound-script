"""Credential-free diagnostics regressions. Optional tests execute only offline."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from test_native_workflow import HERE, BOX, generator, verifier, entrypoint
from experiments.native_cli import verification_command
from boundscript_internal.box_definition import VerificationSuite

STATUS = {'exitStatus': 0, 'signal': None, 'launchError': False, 'timedOut': False}


def test_result(status='passed', **extra):
    return dict({'file': 'acceptance.test.ts', 'name': 'known case', 'status': status}, **extra)


class DiagnosticTests(unittest.TestCase):
    def report(self, path, **overrides):
        report = {'complete': True, 'infrastructureErrors': 0,
                  'files': ['acceptance.test.ts'], 'tests': [test_result()], 'failed': []}
        report.update(overrides)
        path.write_text(json.dumps(report))

    def test_reporter_selects_assertion_and_typia_fields_not_values_or_messages(self):
        source = '''
import {collectDiagnostics} from REPORTER;
const errors = [{name:'Error', message:'PRIVATE COUNTEREXAMPLE', cause:{
 name:'AssertionError', expected:'expected contact', actual:'wrong contact',
 diff:'- expected contact\\n+ wrong contact', stack:'PRIVATE STACK'}},
 {method:'typia.assertEquals', path:'$input.contact.name', expected:'string',
 value:123, message:'PRIVATE MESSAGE'},
 {method:'typia.assertEquals', path:'$input.phone', expected:'string', value:{secret:'PRIVATE VALUE'}},
 {message:'Test timed out in 10ms PRIVATE TIMEOUT DETAILS'}];
const test = {fullName:'known property', result:() => ({state:'failed', errors})};
const module = {moduleId:'/checks/acceptance.test.ts', errors:() => [],
 children:{allTests:() => [test]}};
console.log(JSON.stringify(collectDiagnostics([module], [{message:'PRIVATE UNHANDLED'}])));
'''.replace('REPORTER', json.dumps((verifier.RUNNER / 'diagnostic-reporter.mjs').as_uri()))
        result = subprocess.run(['node', '--input-type=module'], input=source, text=True,
                                capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report['infrastructureErrors'], 1)
        self.assertEqual(report['tests'][0]['status'], 'failed')
        self.assertEqual(report['failed'][0]['assertions'][0]['actual'], 'wrong contact')
        self.assertEqual(report['failed'][0]['typia'][0]['actualType'], 'number')
        self.assertEqual(report['failed'][0]['typia'][1]['actualType'], 'object')
        self.assertTrue(report['failed'][0]['timedOut'])
        self.assertNotIn('PRIVATE', result.stdout)

    def test_success_counts_and_assertion_differences_are_sanitized(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'EXAMPLE_API_KEY': 'private-value-123'}):
            report = Path(tmp) / 'report.json'
            self.report(report)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertIsNone(verifier.vitest_failure(STATUS, report, ('acceptance.test.ts',)))
            self.assertIn('PASS "acceptance.test.ts":', output.getvalue())
            self.assertIn('1 passed, 0 failed', output.getvalue())
            failed = test_result('failed', assertions=[{
                'expected': '{ok: true}', 'actual': 'private-value-123 sk-example123',
                'diff': '- true\n+ false\x00', 'message': 'PRIVATE ASSERTION',
            }], typia=[])
            failed['name'] = 'known case\x1b[31m\nprivate-value-123'
            self.report(report, stdout='PRIVATE STDOUT', stderr='PRIVATE STDERR', tests=[failed], failed=[failed])
            output = io.StringIO()
            with redirect_stdout(output):
                failure = verifier.vitest_failure(dict(STATUS, exitStatus=1), report, ('acceptance.test.ts',))
            text = output.getvalue()
            self.assertEqual(failure.kind, 'assertion')
            self.assertIn('Vitest exit status: 1', text)
            self.assertIn('expected: "{ok: true}"', text)
            self.assertIn('| - true', text)
            self.assertIn('| + false\\u0000', text)
            self.assertIn('[REDACTED]', text)
            for forbidden in ('PRIVATE', 'private-value-123', 'sk-example123', '\x1b', '\x00'):
                self.assertNotIn(forbidden, text)

    def test_typia_and_runtime_failure_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'report.json'
            failed = test_result('failed', assertions=[], typia=[{
                'path': '$input.contact.name', 'expected': 'string', 'actualType': 'number',
                'value': 'PRIVATE VALUE', 'message': 'PRIVATE MESSAGE',
            }, {'path': '$input["PRIVATE KEY"]', 'expected': 'undefined', 'actualType': 'string'}])
            self.report(report, tests=[failed], failed=[failed])
            output = io.StringIO()
            with redirect_stdout(output):
                failure = verifier.vitest_failure(dict(STATUS, exitStatus=1), report, ('acceptance.test.ts',))
            self.assertEqual(failure.kind, 'typia')
            self.assertIn('$input.contact.name', output.getvalue())
            self.assertIn('actual type=number', output.getvalue())
            self.assertNotIn('PRIVATE', output.getvalue())
            failed['typia'] = []
            self.report(report, tests=[failed], failed=[failed])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(verifier.vitest_failure(dict(STATUS, exitStatus=1), report, ('acceptance.test.ts',)).kind, 'runtime')
            failed['timedOut'] = True
            self.report(report, tests=[failed], failed=[failed])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(verifier.vitest_failure(dict(STATUS, exitStatus=1), report, ('acceptance.test.ts',)).kind, 'timeout')

    def test_missing_invalid_oversized_and_symlink_reports_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'report.json'
            for contents in (None, 'PRIVATE INVALID JSON', 'x' * 262145, '[]'):
                if contents is not None:
                    report.write_text(contents)
                with self.assertRaises(verifier.VerificationFailure) as failure:
                    verifier.vitest_failure(STATUS, report, ('acceptance.test.ts',))
                self.assertEqual(failure.exception.kind, 'infrastructure')
                self.assertNotIn('PRIVATE', str(failure.exception))
            report.unlink()
            target = Path(tmp) / 'secret'
            target.write_text('PRIVATE FILE')
            report.symlink_to(target)
            with self.assertRaises(verifier.VerificationFailure):
                verifier.read_report(report)
            report.unlink()
            self.report(report, infrastructureErrors=1)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(verifier.vitest_failure(STATUS, report, ('acceptance.test.ts',)).kind, 'infrastructure')
            self.report(report, tests=[])
            with self.assertRaises(verifier.VerificationFailure):
                verifier.vitest_failure(STATUS, report, ('acceptance.test.ts',))

    def test_process_startup_timeout_and_transport_errors_withhold_raw_output(self):
        engine = MagicMock()
        for result, kind in [(dict(STATUS, launchError=True), 'infrastructure'),
                             (dict(STATUS, timedOut=True), 'timeout'),
                             (dict(STATUS, signal='SIGKILL'), 'infrastructure'),
                             ({'exitStatus': 'PRIVATE STATUS'}, 'infrastructure')]:
            engine.exec.return_value = json.dumps(result)
            with self.assertRaises(verifier.VerificationFailure) as error:
                verifier.process_status(engine, 'fixed-name', [], 1)
            self.assertEqual(error.exception.kind, kind)
            self.assertNotIn('PRIVATE', str(error.exception))
        engine.exec.return_value = 'PRIVATE STDOUT'
        with self.assertRaises(verifier.VerificationFailure):
            verifier.process_status(engine, 'fixed-name', [], 1)
        engine.exec.side_effect = subprocess.TimeoutExpired('PRIVATE COMMAND', 1, output='PRIVATE OUTPUT')
        with self.assertRaises(verifier.VerificationFailure) as error:
            verifier.process_status(engine, 'fixed-name', [], 1)
        self.assertEqual(error.exception.kind, 'timeout')
        self.assertNotIn('PRIVATE', str(error.exception))
        self.assertIn("stdio: 'ignore'", verifier.PROCESS_RUN)

    def test_compiler_structured_diagnostics_and_startup_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'typescript-diagnostics.json').write_text(json.dumps({
                'complete': True, 'errorCount': 1, 'diagnostics': [{
                    'code': 2322, 'file': '/implementation/implementation.ts', 'line': 2, 'column': 3,
                    'message': 'Type mismatch sk-private-token', 'stack': 'PRIVATE STACK',
                }], 'stdout': 'PRIVATE STDOUT',
            }))
            output = io.StringIO()
            with patch.object(verifier, 'process_status', return_value=dict(STATUS, exitStatus=1)), redirect_stdout(output):
                with self.assertRaises(verifier.VerificationFailure) as failure:
                    verifier.run_compiler(MagicMock(), 'fixed-name', root)
            self.assertEqual(failure.exception.kind, 'compilation')
            self.assertIn('TS2322 /implementation/implementation.ts:2:3:', output.getvalue())
            self.assertNotIn('sk-private-token', output.getvalue())
            self.assertNotIn('PRIVATE', output.getvalue())
            (root / 'typescript-diagnostics.json').unlink()
            with patch.object(verifier, 'process_status', return_value=dict(STATUS, exitStatus=1)):
                with self.assertRaises(verifier.VerificationFailure) as failure:
                    verifier.run_compiler(MagicMock(), 'fixed-name', root)
            self.assertEqual(failure.exception.kind, 'infrastructure')

    def test_phase_updates_are_flushed_and_cli_never_prints_tracebacks(self):
        with patch('builtins.print') as output:
            with verifier.phase('fixed phase'):
                pass
            self.assertEqual([call.args[0] for call in output.call_args_list], ['START fixed phase', 'PASS fixed phase'])
            self.assertTrue(all(call.kwargs.get('flush') for call in output.call_args_list))
        for error in (verifier.VerificationFailure('assertion', 'Safe assertion summary'),
                      RuntimeError('PRIVATE EXCEPTION')):
            output = io.StringIO()
            with patch.object(entrypoint, 'verify', side_effect=error), redirect_stdout(output):
                self.assertEqual(entrypoint.cli([], box_root=HERE, box=BOX), 1)
            self.assertNotIn('PRIVATE', output.getvalue())
            self.assertNotIn('Traceback', output.getvalue())
        with patch.object(entrypoint, 'verify'):
            self.assertEqual(entrypoint.cli([], box_root=HERE, box=BOX), 0)

    def test_phase_reports_group_selection_and_rejects_stale_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / 'vitest-diagnostics.json'
            self.report(report)
            with patch.object(verifier, 'process_status', return_value=STATUS) as run:
                with self.assertRaises(verifier.VerificationFailure):
                    verifier.run_vitest(MagicMock(), 'fixed-name', root,
                                        VerificationSuite(('properties',), ('laws/own.spec.ts',)), 2)
            self.assertIn('/checks/suite-2.config.mts', run.call_args.args[2])
            self.assertIn('--allowOnly=false', run.call_args.args[2])
            self.assertNotIn('--testNamePattern', run.call_args.args[2])
            self.assertFalse(report.exists())

    def test_declared_file_coverage_empty_collections_skips_and_pending_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'vitest-diagnostics.json'
            expected = ('nested/one.spec.ts', 'elsewhere/two.test.ts')
            tests = [test_result(file=file, name='description unrelated to selection') for file in expected]
            for overrides in (
                {'files': list(expected[:1]), 'tests': tests[:1]},
                {'files': list(expected), 'tests': tests[:1]},  # Empty second file.
                {'files': [expected[0], expected[0]], 'tests': tests},
                {'files': [*expected, 'undeclared.spec.ts'], 'tests': tests},
                {'files': list(expected), 'tests': [tests[0], dict(tests[1], status='skipped')]},
                {'files': list(expected), 'tests': [tests[0], dict(tests[1], status='pending')]},
                {'files': list(expected), 'tests': [*tests, test_result(file='unknown.spec.ts')]},
            ):
                self.report(report, **overrides)
                with self.subTest(report=overrides), redirect_stdout(io.StringIO()):
                    try:
                        failure = verifier.vitest_failure(STATUS, report, expected)
                    except verifier.VerificationFailure as error:
                        failure = error
                    self.assertIsNotNone(failure)
                    self.assertEqual(failure.kind, 'infrastructure')
            self.report(report, files=list(expected), tests=tests)
            with redirect_stdout(io.StringIO()) as output:
                self.assertIsNone(verifier.vitest_failure(STATUS, report, expected))
            self.assertIn('nested/one.spec.ts', output.getvalue())
            self.assertIn('elsewhere/two.test.ts', output.getvalue())

    def test_reporter_retains_nested_paths_and_fails_closed_on_truncation(self):
        source = '''
import {collectDiagnostics} from REPORTER;
const test = {fullName:'unrelated description', result:() => ({state:'passed'})};
const module = path => ({moduleId:path, errors:() => [],
 children:{allTests:() => [test]}});
const report = collectDiagnostics([
 module('/checks/one/custom.spec.ts'), module('/checks/two/custom.spec.ts')], []);
const overflow = collectDiagnostics([{moduleId:'/checks/huge.test.ts', errors:() => [],
 children:{allTests:() => Array(101).fill(test)}}], []);
console.log(JSON.stringify({report, overflow}));
'''.replace('REPORTER', json.dumps((verifier.RUNNER / 'diagnostic-reporter.mjs').as_uri()))
        result = subprocess.run(['node', '--input-type=module'], input=source, text=True,
                                capture_output=True, check=True)
        reports = json.loads(result.stdout)
        self.assertEqual(reports['report']['files'], ['one/custom.spec.ts', 'two/custom.spec.ts'])
        self.assertEqual([test['file'] for test in reports['report']['tests']], reports['report']['files'])
        self.assertEqual(reports['overflow']['infrastructureErrors'], 1)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_failures_are_readable_and_never_echo_candidate_output(self):
        sources = {
            'compilation': 'export const normalizeContact = () => 0;',
            'assertion': 'export const normalizeContact = () => ({ok:false as const, errors:[]});',
            'typia': '''export const normalizeContact = () => {
console.log('PRIVATE CANDIDATE STDOUT'); console.error('PRIVATE CANDIDATE STDERR');
return {ok:true,contact:{name:3,email:'a@b.c',phone:'PRIVATE VALUE'}} as any; };''',
            'runtime': "export const normalizeContact = () => { throw new Error('PRIVATE EXCEPTION'); };",
        }
        with tempfile.TemporaryDirectory() as tmp:
            for kind, source in sources.items():
                with self.subTest(kind=kind):
                    candidate = Path(tmp) / (kind + '.ts')
                    candidate.write_text(source)
                    result = subprocess.run([*verification_command('normalize-contact'), str(candidate)],
                                            capture_output=True, text=True, timeout=180)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(f'FAIL [{kind}]', result.stdout)
                    self.assertIn('Candidate retained in place', result.stdout)
                    if kind == 'typia':
                        self.assertIn('Typia path="$input.contact.name"', result.stdout)
                        self.assertIn('actual type=number', result.stdout)
                    self.assertNotIn('PRIVATE', result.stdout + result.stderr)
                    self.assertNotIn('Traceback', result.stdout + result.stderr)
                    self.assertTrue(candidate.is_file())

    def test_quarantine_is_private_unique_exact_and_rejects_changed_or_symlink_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / 'candidate.ts'
            candidate.write_bytes(b'// credential-scanned candidate\n')
            expected = generator.digest(candidate)
            first = generator.quarantine(candidate, expected, box_root=root)
            second = generator.quarantine(candidate, expected, box_root=root)
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), candidate.read_bytes())
            self.assertEqual(first.stat().st_mode & 0o777, 0o600)
            self.assertEqual(first.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(list(first.parent.iterdir()), [first])
            candidate.write_text('changed after scan')
            with self.assertRaises(RuntimeError):
                generator.quarantine(candidate, expected, box_root=root)
            candidate.unlink()
            candidate.symlink_to(first)
            with self.assertRaises(OSError):
                generator.quarantine(candidate, expected, box_root=root)
            ignored = subprocess.run(['git', 'check-ignore', '--stdin'], text=True, capture_output=True,
                                     input='experiments/native-typescript-contracts/quarantine/failed-example/implementation.ts\n')
            self.assertEqual(ignored.returncode, 0)


if __name__ == '__main__':
    unittest.main()
