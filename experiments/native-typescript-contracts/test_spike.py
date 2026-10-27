"""Credential-free wiring regressions; mocks do not establish engine security."""
from contextlib import redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load('native_verifier', 'verify.py')
generator = load('native_generator', 'generate.py')


class SpikeTests(unittest.TestCase):
    def test_native_fixtures_have_phone_without_an_invented_phone_oracle(self):
        cases = json.loads((HERE / 'cases.json').read_text())
        self.assertEqual(len(cases), 20)
        for case in cases:
            self.assertEqual(set(case['input']), {'name', 'email', 'phone'})
            self.assertEqual(case['input']['phone'], '+34600111222')
            if case['expected']['ok']:
                self.assertEqual(set(case['expected']['contact']), {'name', 'email'})
        # Importing the native verifier must not import the frozen fixture module.
        with patch.dict(sys.modules, {'verify': None, 'verify_pair': None}):
            load('independent_native_verifier', 'verify.py')

    def test_verifier_failures_cleanup(self):
        for stage in ('create', 'start', 'exec'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp:
                candidate = Path(tmp) / 'candidate.ts'
                candidate.write_text('export const normalizeContact = () => 0;')
                engine = MagicMock()
                getattr(engine, stage).side_effect = RuntimeError('synthetic failure')
                with patch.object(verifier, 'runtime', return_value=engine):
                    with self.assertRaises(RuntimeError):
                        verifier.check(candidate)
                engine.remove.assert_called_once()
                mounts = engine.create.call_args.args[2]
                specs = mounts[1::2]
                self.assertEqual(sum('readonly' not in spec for spec in specs), 1)
                self.assertIn('dst=/implementation', specs[0])
                self.assertTrue(all('readonly' in spec for spec in specs[1:]))

    def test_native_verification_stages_its_own_human_owned_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / 'candidate.ts'
            candidate.write_text('// synthetic candidate; never executed on host')
            engine = MagicMock()
            engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5),
                                       json.dumps('ENETUNREACH')]

            def inspect_checks(_engine, _name, _scratch, _group):
                specs = engine.create.call_args.args[2][1::2]
                checks_spec = next(s for s in specs if 'dst=/checks,' in s)
                checks = Path(checks_spec.split('src=', 1)[1].split(',')[0])
                self.assertEqual((checks / 'cases.json').read_bytes(), (HERE / 'cases.json').read_bytes())
                self.assertEqual(len(json.loads((checks / 'cases.json').read_text())), 20)
                self.assertFalse((HERE / 'check-contract.ts').exists())
                self.assertEqual((checks / 'check-contract.ts').read_text(),
                                 verifier.BOX.contract_check('/implementation/implementation.ts'))
                self.assertIn(f'src={HERE / "src/contract.ts"},dst=/inputs/contract.ts,readonly',
                              ','.join(specs))

            with patch.object(verifier, 'runtime', return_value=engine), \
                 patch.object(verifier, 'run_vitest', side_effect=inspect_checks) as vitest, \
                 patch.object(verifier, 'run_compiler') as compiler, \
                 patch.dict(sys.modules, {'verify_pair': None}):
                verifier.check(candidate)
            self.assertEqual([call.args[3] for call in vitest.call_args_list], ['typia', 'acceptance', 'properties'])
            self.assertEqual(engine.exec.call_count, 2)
            compiler.assert_called_once()
            engine.remove.assert_called_once()

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_negative_submissions(self):
        # Establish that this engine actually supports the positive path first.
        verifier.check(HERE / 'accepted/normalize-contact.ts')
        accepted = HERE / 'accepted/normalize-contact.ts'
        before = accepted.read_bytes() if accepted.exists() else None
        negatives = {
            'signature': 'export const normalizeContact = () => 0;',
            'runtime-shape': 'export const normalizeContact = () => ({ok:true,contact:{name:3,email:"x"}} as any);',
            'behavior': 'export const normalizeContact = () => ({ok:false as const,errors:[]});',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, source in negatives.items():
                with self.subTest(name=name):
                    candidate = Path(tmp) / (name + '.ts')
                    candidate.write_text(source)
                    with self.assertRaises(RuntimeError):
                        verifier.check(candidate)
        self.assertEqual(accepted.read_bytes() if accepted.exists() else None, before)

    def test_failed_independent_verification_never_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / '.generated').mkdir()
            (root / 'accepted').mkdir()
            (root / '.generated/validators.ts').write_text('// synthetic build')
            (root / 'task.md').write_text('synthetic task')
            (root / 'src/contract.ts').write_text('// synthetic contract')
            accepted = root / 'accepted/normalize-contact.ts'
            accepted.write_text('previously accepted bytes')
            auth = root / 'auth.json'
            auth.write_text('{}')
            pi = root / 'pi'
            (pi / 'dist/bundle').mkdir(parents=True)
            (pi / 'dist/bundle/cli.js').write_text('// synthetic Pi')
            (pi / 'package.json').write_text('{"version":"1.4.0"}')
            engine = MagicMock()
            scan_failure = False

            def execute(name, *args, **kwargs):
                if 'function check(v)' in kwargs.get('source', ''):
                    if scan_failure:
                        raise RuntimeError('synthetic credential-scan failure; PRIVATE DIAGNOSTICS')
                    return generator.hashlib.sha256(b'// unverified candidate').hexdigest()
                if '/opt/pi/dist/bundle/cli.js' in args:
                    specs = engine.create.call_args.args[2][1::2]
                    spec = next(s for s in specs if 'dst=/implementation' in s)
                    candidate = Path(spec.split('src=', 1)[1].split(',')[0])
                    (candidate / 'implementation.ts').write_text('// unverified candidate')
                    return '\n'.join(json.dumps(event) for event in [
                        {'type': 'session', 'id': '00000000-0000-4000-8000-000000000030', 'cwd': '/implementation'},
                        {'type': 'tool_execution_start', 'toolName': 'write'},
                        {'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'stop'}},
                        {'type': 'agent_settled', 'aborted': False},
                    ])
                if 'observed' in kwargs.get('source', ''):
                    return json.dumps(['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT',
                                       'EROFS', 'ENOENT', 'ENOENT', 'ERR_MODULE_NOT_FOUND'])
                return ''

            engine.exec.side_effect = execute
            with patch.object(generator, 'SPIKE', root), \
                 patch.object(generator, 'AUTH', auth), \
                 patch.object(generator, 'PI', pi), \
                 patch.object(generator, 'runtime', return_value=engine), \
                 patch.object(generator.sys, 'argv', ['generate.py']), \
                 patch.object(generator.subprocess, 'run') as verification:
                for failure in (subprocess.CalledProcessError(1, 'verify'),
                                subprocess.TimeoutExpired('verify', 120), OSError('synthetic launch failure')):
                    verification.side_effect = failure
                    with self.subTest(failure=type(failure).__name__), self.assertRaises(type(failure)):
                        generator.main()
                    self.assertEqual(accepted.read_text(), 'previously accepted bytes')
                    self.assertEqual(verification.call_args.kwargs['timeout'], 360)
                    self.assertEqual(verification.call_args.args[0][2:4],
                                     ['--box-definition', generator.BOX.fingerprint()])
                retained = list((root / 'quarantine').glob('*/implementation.ts'))
                self.assertEqual(len(retained), 3)
                for candidate in retained:
                    self.assertEqual(candidate.read_text(), '// unverified candidate')
                    self.assertEqual(list(candidate.parent.iterdir()), [candidate])
                # A candidate failing the in-container credential scan must never
                # enter quarantine or verification, even if a file was produced.
                verification.reset_mock()
                scan_failure = True
                with self.assertRaises(RuntimeError):
                    generator.main()
                verification.assert_not_called()
                self.assertEqual(len(list((root / 'quarantine').glob('*/implementation.ts'))), 3)
                # The same fixed runner promotes only on independent success.
                scan_failure = False
                verification.side_effect = None
                generator.main()
                self.assertEqual(accepted.read_text(), '// unverified candidate')
                # A verifier-side source change must never be promoted.
                accepted.write_text('previously accepted bytes')
                def change_source(command, **kwargs):
                    Path(command[-1]).write_text('// changed after scan')
                verification.side_effect = change_source
                with self.assertRaises(AssertionError):
                    generator.main()
            self.assertEqual(accepted.read_text(), 'previously accepted bytes')
            self.assertEqual(engine.remove.call_count, 6)
            specs = engine.create.call_args.args[2][1::2]
            self.assertFalse(any('/checks' in s or '/tests' in s or '/repo' in s for s in specs))
            self.assertEqual(sum('/inputs/' in s for s in specs), 2)

    def test_generation_cli_does_not_serialize_arbitrary_errors(self):
        with patch.object(generator, 'main', side_effect=RuntimeError('PRIVATE PROVIDER OUTPUT')), \
             redirect_stderr(io.StringIO()) as output:
            self.assertEqual(generator.cli(), 1)
        self.assertNotIn('PRIVATE', output.getvalue())
        self.assertNotIn('Traceback', output.getvalue())


if __name__ == '__main__':
    unittest.main()
