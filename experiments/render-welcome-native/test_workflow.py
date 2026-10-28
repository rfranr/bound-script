"""Box-local wiring checks; mocks are not engine security evidence."""
from contextlib import redirect_stdout, redirect_stderr
from importlib import import_module
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from boundscript_internal import native_verifier

generator = import_module('experiments.render-welcome-native.generate')
verifier = import_module('experiments.render-welcome-native.verify')


class WelcomeWorkflowTests(unittest.TestCase):
    def test_definition_is_local_complete_and_shared_by_fixed_entry_points(self):
        box = generator.BOX
        self.assertIs(box, verifier.BOX)
        for value in (box.task_path, box.contract_path, box.verification_path, box.accepted_path):
            self.assertFalse(PurePosixPath(value).is_absolute())
            self.assertNotIn('..', PurePosixPath(value).parts)
        files = box.verification_files(HERE)
        self.assertIn('fixtures/welcome-cases.json', files)
        self.assertEqual({file for suite in box.suites for file in suite.files},
                         {'validators.test.ts', 'acceptance.test.ts'})
        self.assertEqual(box.suites[1].categories, ('acceptance', 'properties'))
        self.assertEqual(len(json.loads((HERE / 'fixtures/welcome-cases.json').read_text())), 6)
        with patch.object(verifier, 'verify_candidate') as check:
            verifier.check(Path('/candidate.ts'))
        check.assert_called_once_with(Path('/candidate.ts'), box_root=HERE, box=box)

    def test_fingerprint_mismatch_fails_before_verification(self):
        with patch.object(verifier.sys, 'argv', ['verify.py', '--box-definition', 'wrong', '/unused.ts']), \
             patch.object(verifier, 'check') as check:
            with self.assertRaisesRegex(native_verifier.VerificationFailure, 'definition mismatch'):
                verifier.main()
            check.assert_not_called()
        with patch.object(verifier.sys, 'argv', ['verify.py', '--box-definition',
                                                verifier.BOX.fingerprint(), '/unused.ts']), \
             patch.object(verifier, 'check') as check:
            verifier.main()
            check.assert_called_once_with(Path('/unused.ts'))

    def test_standalone_import_and_preflight_never_read_peer_experiment(self):
        # Block both imports and file access to the peer root in a fresh process.
        source = '''
import builtins, importlib, pathlib, sys
sys.path.insert(0, ROOT)
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        assert 'native-typescript-contracts' not in str(args[0]), 'peer file access'
sys.addaudithook(audit)
sys.modules['experiments.native-typescript-contracts.native_box'] = None
verify = importlib.import_module('experiments.render-welcome-native.verify')
generate = importlib.import_module('experiments.render-welcome-native.generate')
assert verify.BOX is generate.BOX
verify.BOX.verification_files(pathlib.Path(BOX_ROOT))
assert 'NormalizeContact' not in generate.generation_prompt(generate.BOX)
'''.replace('BOX_ROOT', repr(str(HERE))).replace('ROOT', repr(str(HERE.parents[1])))
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, '-I', '-B', '-c', source], cwd=cwd,
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_shared_verifier_stages_only_local_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / 'candidate.ts'
            candidate.write_text('// synthetic candidate, never executed on host')
            engine = MagicMock()
            engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5), json.dumps('ENETUNREACH')]

            def inspect_checks(*args):
                specs = engine.create.call_args.args[2][1::2]
                checks = Path(next(spec for spec in specs if 'dst=/checks,' in spec)
                              .split('src=', 1)[1].split(',')[0])
                for file in generator.BOX.verification_files(HERE):
                    self.assertEqual((checks / file).read_bytes(), (HERE / file).read_bytes())
                self.assertEqual((checks / 'diagnostic-reporter.mjs').read_bytes(),
                                 (native_verifier.RUNNER / 'diagnostic-reporter.mjs').read_bytes())
                self.assertIn('renderWelcome', (checks / 'check-contract.ts').read_text())
                self.assertNotIn('native-typescript-contracts', ','.join(specs))

            with patch.object(native_verifier, 'runtime', return_value=engine), \
                 patch.object(native_verifier, 'run_compiler', side_effect=inspect_checks), \
                 patch.object(native_verifier, 'run_vitest') as tests, redirect_stdout(io.StringIO()):
                verifier.check(candidate)
            self.assertEqual([call.args[3] for call in tests.call_args_list], list(generator.BOX.suites))
            engine.remove.assert_called_once()

    def test_generation_is_local_and_never_promotes_failed_or_changed_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / 'implementation.ts'
            candidate.write_text('// scanned synthetic candidate')
            scanned = generator.digest(candidate)
            destination = root / generator.BOX.accepted_path
            destination.parent.mkdir()
            destination.write_text('// previous bytes')
            context = MagicMock()
            context.__enter__.return_value = (candidate, scanned)
            with patch.object(generator, 'SPIKE', root), \
                 patch.object(generator.BOX.__class__, 'verification_files', return_value=()), \
                 patch.object(generator, 'runtime'), \
                 patch.object(generator, 'agent_submission', return_value=context) as agent, \
                 patch.object(generator.sys, 'argv', ['generate.py']), \
                 patch.object(generator.subprocess, 'run') as verification, redirect_stdout(io.StringIO()):
                for failure in (subprocess.CalledProcessError(1, 'verify'),
                                subprocess.TimeoutExpired('verify', 360), OSError('launch failed')):
                    verification.side_effect = failure
                    with self.assertRaises(type(failure)):
                        generator.main()
                    self.assertEqual(destination.read_text(), '// previous bytes')
                self.assertEqual(len(list((root / 'quarantine').glob('*/implementation.ts'))), 3)
                verification.side_effect = None
                generator.main()
                self.assertEqual(destination.read_bytes(), candidate.read_bytes())
                self.assertEqual(agent.call_args.args[1], {'task.md': root / 'task.md',
                                                          'contract.ts': root / 'src/contract.ts'})
                self.assertEqual(verification.call_args.args[0],
                                 [sys.executable, str(root / 'verify.py'), '--box-definition',
                                  generator.BOX.fingerprint(), str(candidate)])
                self.assertEqual(verification.call_args.kwargs['timeout'], 360)
                destination.write_text('// previous bytes')

                def change_source(*args, **kwargs):
                    candidate.write_text('// changed after scan')
                verification.side_effect = change_source
                with self.assertRaises(AssertionError):
                    generator.main()
                self.assertEqual(destination.read_text(), '// previous bytes')

    def test_cli_withholds_arbitrary_diagnostics(self):
        for module in (generator, verifier):
            with self.subTest(module=module.__name__), \
                 patch.object(module, 'main', side_effect=RuntimeError('PRIVATE')), \
                 redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                self.assertEqual(module.cli(), 1)
                self.assertNotIn('PRIVATE', out.getvalue() + err.getvalue())

    def test_cli_reports_resource_root_cause_and_safe_location(self):
        from boundscript_internal.container_runtime import check_resource

        def fail():
            check_resource('memory.max', 'max', (512 * 1024 * 1024,))

        with patch.object(generator, 'main', side_effect=fail), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(generator.cli(), 1)
        message = err.getvalue()
        self.assertIn('memory.max: unlimited', message)
        self.assertIn('cgroup-v2', message)
        self.assertIn('boundscript_internal/container_runtime.py:', message)
        self.assertIn('(check_resource)', message)
        self.assertNotIn(str(Path.home()), message)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_WELCOME_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_wrong_signature_shape_behavior_and_mutation(self):
        # Require an independently generated positive candidate first.
        accepted = HERE / verifier.BOX.accepted_path
        before = accepted.read_bytes()
        verifier.check(accepted)
        negatives = {
            'compilation': 'export const renderWelcome = () => 0;',
            'typia': 'export const renderWelcome = () => ({message:"wrong"}) as any;',
            'assertion': 'export const renderWelcome = () => "wrong";',
            'mutation': 'export const renderWelcome = (contact: any) => {contact.name="changed"; return "wrong";};',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for kind, source in negatives.items():
                candidate = Path(tmp) / f'{kind}.ts'
                candidate.write_text(source)
                with self.subTest(kind=kind), self.assertRaises(native_verifier.VerificationFailure) as failure:
                    verifier.check(candidate)
                self.assertIn('runtime' if kind == 'mutation' else kind, failure.exception.kind)
        self.assertEqual(accepted.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
