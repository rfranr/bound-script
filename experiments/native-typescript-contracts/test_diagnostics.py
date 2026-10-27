"""Offline diagnostics and quarantine regressions; no credentials or model calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from test_spike import HERE, generator, verifier


class DiagnosticTests(unittest.TestCase):
    def test_reporter_selects_assertion_fields_and_fast_check_causes(self):
        source = '''
import {collectDiagnostics} from REPORTER;
const assertion = {name:'AssertionError', expected:'expected contact', actual:'wrong contact',
 diff:'- expected contact\\n+ wrong contact', message:'PRIVATE MESSAGE', stack:'PRIVATE STACK'};
const test = {fullName:'known property', result:() => ({errors:[{name:'Error',
 message:'PRIVATE COUNTEREXAMPLE', cause:assertion}]})};
const module = {moduleId:'/checks/acceptance.test.ts', errors:() => [],
 children:{allTests:() => [test]}};
console.log(JSON.stringify(collectDiagnostics([module], [{message:'PRIVATE UNHANDLED'}])));
'''.replace('REPORTER', json.dumps((HERE / 'diagnostic-reporter.mjs').as_uri()))
        result = subprocess.run(['node', '--input-type=module'], input=source, text=True,
                                capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report['infrastructureErrors'], 1)
        self.assertEqual(report['failed'][0]['assertions'][0]['actual'], 'wrong contact')
        self.assertNotIn('PRIVATE', result.stdout)

    def report(self, path, **overrides):
        report = {'complete': True, 'infrastructureErrors': 0, 'failed': []}
        report.update(overrides)
        path.write_text(json.dumps(report))

    def test_sanitized_test_names_differences_and_exit_status_only(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'EXAMPLE_API_KEY': 'private-value-123'}):
            report = Path(tmp) / 'report.json'
            self.report(report, stdout='PRIVATE STDOUT', stderr='PRIVATE STDERR', failed=[{
                'file': 'acceptance.test.ts', 'name': 'known case\x1b[31m\nprivate-value-123',
                'message': 'PRIVATE ERROR', 'stack': 'PRIVATE STACK', 'assertions': [{
                    'expected': '{ok: true}', 'actual': 'private-value-123 sk-example123',
                    'diff': '- true\n+ false\x00', 'message': 'PRIVATE ASSERTION',
                }],
            }])
            diagnostic = verifier.vitest_failure({'exitStatus': 1, 'signal': None, 'launchError': False}, report)
            self.assertIn('Vitest exit status: 1', diagnostic)
            self.assertIn('known case', diagnostic)
            self.assertIn('expected: "{ok: true}"', diagnostic)
            self.assertIn('- true\\n+ false\\u0000', diagnostic)
            self.assertIn('[REDACTED]', diagnostic)
            self.assertIn('Vitest test failures', diagnostic)
            for forbidden in ('PRIVATE', 'private-value-123', 'sk-example123', '\x1b', '\x00'):
                self.assertNotIn(forbidden, diagnostic)

    def test_infrastructure_and_missing_invalid_oversized_or_symlink_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'report.json'
            status = {'exitStatus': 137, 'signal': None, 'launchError': False}
            for contents in (None, 'not JSON PRIVATE STDERR', 'x' * 131073, '[]'):
                if contents is not None:
                    report.write_text(contents)
                message = verifier.vitest_failure(status, report)
                self.assertIn('exit status: 137', message)
                self.assertIn('infrastructure failure', message)
                self.assertNotIn('PRIVATE', message)
            report.unlink()
            target = Path(tmp) / 'secret'
            target.write_text('PRIVATE FILE')
            report.symlink_to(target)
            self.assertIn('infrastructure failure', verifier.vitest_failure(status, report))
            report.unlink()
            self.report(report, infrastructureErrors=1)
            self.assertIn('infrastructure failure', verifier.vitest_failure(status, report))
            self.report(report)
            self.assertIsNone(verifier.vitest_failure({'exitStatus': 0}, report))
            self.assertIn('infrastructure failure', verifier.vitest_failure(status, report))
            engine = MagicMock()
            engine.exec.return_value = json.dumps({'exitStatus': 0, 'signal': None, 'launchError': False})
            report.rename(Path(tmp) / 'vitest-diagnostics.json')
            verifier.run_vitest(engine, 'fixed-name', Path(tmp))
            (Path(tmp) / 'vitest-diagnostics.json').unlink()
            with self.assertRaisesRegex(RuntimeError, 'missing or invalid Vitest report'):
                verifier.run_vitest(engine, 'fixed-name', Path(tmp))

    def test_transport_failures_never_echo_raw_diagnostics(self):
        engine = MagicMock()
        for result in ('PRIVATE STDOUT', json.dumps({'exitStatus': 'PRIVATE STATUS'})):
            engine.exec.return_value = result
            with self.assertRaisesRegex(RuntimeError, 'transport/status unavailable') as error:
                verifier.run_vitest(engine, 'fixed-name', Path('/unused'))
            self.assertNotIn('PRIVATE', str(error.exception))
        engine.exec.side_effect = subprocess.TimeoutExpired('PRIVATE COMMAND', 1, output='PRIVATE OUTPUT')
        with self.assertRaisesRegex(RuntimeError, 'transport/status unavailable') as error:
            verifier.run_vitest(engine, 'fixed-name', Path('/unused'))
        self.assertNotIn('PRIVATE', str(error.exception))
        self.assertIn("stdio: 'ignore'", verifier.VITEST_RUN)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine check')
    def test_engine_assertion_diagnostics_do_not_echo_candidate_console(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / 'candidate.ts'
            candidate.write_text('''export const normalizeContact = () => {
 console.log('PRIVATE CANDIDATE STDOUT');
 console.error('PRIVATE CANDIDATE STDERR');
 return {ok:false as const, errors:[]};
};''')
            with self.assertRaises(RuntimeError) as failure:
                verifier.check(candidate)
            diagnostic = str(failure.exception)
            self.assertIn('Vitest exit status: 1', diagnostic)
            self.assertIn('FAIL acceptance.test.ts:', diagnostic)
            self.assertIn('expected:', diagnostic)
            self.assertIn('actual:', diagnostic)
            self.assertNotIn('PRIVATE CANDIDATE', diagnostic)

    def test_quarantine_is_private_unique_exact_and_rejects_changed_or_symlink_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / 'candidate.ts'
            candidate.write_bytes(b'// credential-scanned candidate\n')
            expected = generator.digest(candidate)
            with patch.object(generator, 'SPIKE', root):
                first = generator.quarantine(candidate, expected)
                second = generator.quarantine(candidate, expected)
                self.assertNotEqual(first, second)
                self.assertEqual(first.read_bytes(), candidate.read_bytes())
                self.assertEqual(first.stat().st_mode & 0o777, 0o600)
                self.assertEqual(first.parent.stat().st_mode & 0o777, 0o700)
                self.assertEqual(list(first.parent.iterdir()), [first])
                candidate.write_text('changed after scan')
                with self.assertRaises(RuntimeError):
                    generator.quarantine(candidate, expected)
                candidate.unlink()
                candidate.symlink_to(first)
                with self.assertRaises(OSError):
                    generator.quarantine(candidate, expected)
            ignored = subprocess.run(['git', 'check-ignore', '--stdin'], text=True, capture_output=True,
                                     input='experiments/native-typescript-contracts/quarantine/failed-example/implementation.ts\n')
            self.assertEqual(ignored.returncode, 0)


if __name__ == '__main__':
    unittest.main()
