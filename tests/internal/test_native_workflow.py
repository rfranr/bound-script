"""Credential-free shared workflow regressions; mocks are not engine evidence."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from boundscript_internal import native_generator as generator
from boundscript_internal import native_cli as entrypoint
from boundscript_internal import native_verifier as verifier
from experiments.native_cli import ROOT, select_box, verification_command

HERE, BOX, BASELINE = select_box('normalize-contact')
SELECTIONS = ('normalize-contact', 'render-welcome')


class NativeWorkflowTests(unittest.TestCase):
    def test_fingerprint_and_candidate_selection(self):
        for selection in SELECTIONS:
            root, box, baseline = select_box(selection)
            with self.subTest(box=selection), patch.object(entrypoint, 'check') as check:
                with self.assertRaisesRegex(verifier.VerificationFailure, 'definition mismatch'):
                    entrypoint.verify(['--box-definition', 'wrong', '/unused.ts'], box_root=root, box=box)
                check.assert_not_called()
                entrypoint.verify(['--box-definition', box.fingerprint(), '/unused.ts'], box_root=root, box=box)
                check.assert_called_once_with(Path('/unused.ts'), box_root=root, box=box)
                check.reset_mock()
                entrypoint.verify([], box_root=root, box=box)
                check.assert_called_once_with(root / box.accepted_path, box_root=root, box=box)
                check.reset_mock()
                if baseline is not None:
                    entrypoint.verify(['--baseline'], box_root=root, box=box, baseline_source=baseline)
                    check.assert_called_once_with((root / baseline).resolve(), box_root=root, box=box)
                else:
                    with self.assertRaises(verifier.VerificationFailure):
                        entrypoint.verify(['--baseline'], box_root=root, box=box)
                    check.assert_not_called()

    def test_standalone_selection_never_reads_peer_or_baseline_verifiers(self):
        for selection in SELECTIONS:
            root, box, _ = select_box(selection)
            peer = 'native-typescript-contracts' if selection == 'render-welcome' else 'render-welcome-native'
            source = f'''
import pathlib, sys
sys.path.insert(0, {str(ROOT)!r})
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        assert {peer!r} not in str(args[0]), 'peer file access'
sys.addaudithook(audit)
sys.modules['experiments.' + {peer!r} + '.native_box'] = None
sys.modules['verify'] = None
sys.modules['verify_pair'] = None
from experiments.native_cli import select_box
from boundscript_internal.native_generator import generation_prompt
root, box, _ = select_box({selection!r})
box.verification_files(root / box.verification_path)
assert {'NormalizeContact' if selection == 'render-welcome' else 'RenderWelcome'!r} not in generation_prompt(box)
'''
            with self.subTest(box=selection), tempfile.TemporaryDirectory() as cwd:
                result = subprocess.run([sys.executable, '-I', '-B', '-c', source], cwd=cwd,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_verifier_failures_cleanup_and_read_only_mounts(self):
        for selection in SELECTIONS:
            root, box, _ = select_box(selection)
            for stage in ('create', 'start', 'exec'):
                with self.subTest(box=selection, stage=stage), tempfile.TemporaryDirectory() as tmp:
                    candidate = Path(tmp) / 'candidate.ts'
                    candidate.write_text('// synthetic candidate')
                    engine = MagicMock()
                    getattr(engine, stage).side_effect = RuntimeError('synthetic failure')
                    with patch.object(verifier, 'runtime', return_value=engine):
                        with self.assertRaises(RuntimeError):
                            verifier.check(candidate, box_root=root, box=box)
                    engine.remove.assert_called_once()
                    specs = engine.create.call_args.args[2][1::2]
                    self.assertEqual(sum('readonly' not in spec for spec in specs), 1)
                    self.assertIn('dst=/implementation', specs[0])
                    self.assertTrue(all('readonly' in spec for spec in specs[1:]))

    def test_verification_stages_only_owned_assets_and_exact_suites(self):
        for selection in SELECTIONS:
            root, box, _ = select_box(selection)
            with self.subTest(box=selection), tempfile.TemporaryDirectory() as tmp:
                candidate = Path(tmp) / 'candidate.ts'
                candidate.write_text('// synthetic candidate; never executed on host')
                engine = MagicMock()
                engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5), json.dumps('ENETUNREACH')]

                def inspect_checks(*args):
                    specs = engine.create.call_args.args[2][1::2]
                    checks = Path(next(s for s in specs if 'dst=/checks,' in s).split('src=', 1)[1].split(',')[0])
                    for file in box.verification_files(root / box.verification_path):
                        self.assertEqual((checks / file).read_bytes(), (root / box.verification_path / file).read_bytes())
                    self.assertEqual((checks / 'diagnostic-reporter.mjs').read_bytes(),
                                     (verifier.RUNNER / 'diagnostic-reporter.mjs').read_bytes())
                    self.assertFalse((root / 'check-contract.ts').exists())
                    self.assertEqual((checks / 'check-contract.ts').read_text(),
                                     box.contract_check('/implementation/implementation.ts'))
                    self.assertIn(f'src={root / box.contract_path},dst={box.contract_module},readonly', ','.join(specs))
                    peer = 'native-typescript-contracts' if selection == 'render-welcome' else 'render-welcome-native'
                    self.assertNotIn(peer, ','.join(specs))

                with patch.object(verifier, 'runtime', return_value=engine), \
                     patch.object(verifier, 'run_compiler', side_effect=inspect_checks) as compiler, \
                     patch.object(verifier, 'run_vitest') as vitest, redirect_stdout(io.StringIO()):
                    verifier.check(candidate, box_root=root, box=box)
                self.assertEqual([call.args[3] for call in vitest.call_args_list], list(box.suites))
                self.assertEqual(engine.exec.call_count, 2)
                compiler.assert_called_once()
                engine.remove.assert_called_once()

    def test_generation_scan_quarantine_integrity_and_promotion(self):
        for selection in SELECTIONS:
            box_root, box, _ = select_box(selection)
            with self.subTest(box=selection), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'src').mkdir()
                (root / '.generated').mkdir()
                (root / box.accepted_path).parent.mkdir()
                for file in box.verification_files(box_root / box.verification_path):
                    path = root / file
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('// independently owned synthetic fixture')
                # Preflight needs exact declared test files as well.
                for suite in box.suites:
                    for file in suite.files:
                        (root / file).write_text('// independently owned synthetic test')
                (root / box.task_path).write_text('synthetic task')
                (root / box.contract_path).write_text('// synthetic contract')
                accepted = root / box.accepted_path
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
                command = verification_command(selection)
                options = dict(box_root=root, box=box, verification_command=command,
                               detailed_diagnostics=selection == 'render-welcome')
                with patch.object(generator, 'AUTH', auth), patch.object(generator, 'PI', pi), \
                     patch.object(generator, 'runtime', return_value=engine), \
                     patch.object(generator.subprocess, 'run') as verification, redirect_stdout(io.StringIO()):
                    for failure in (subprocess.CalledProcessError(1, 'verify'),
                                    subprocess.TimeoutExpired('verify', 360), OSError('synthetic launch failure')):
                        verification.side_effect = failure
                        with self.assertRaises(type(failure)):
                            generator.generate(**options)
                        self.assertEqual(accepted.read_text(), 'previously accepted bytes')
                        self.assertEqual(verification.call_args.kwargs, {'check': True, 'timeout': 360})
                        self.assertEqual(verification.call_args.args[0][:-1], [*command, '--box-definition', box.fingerprint()])
                    retained = list((root / 'quarantine').glob('*/implementation.ts'))
                    self.assertEqual(len(retained), 3)
                    for candidate in retained:
                        self.assertEqual(candidate.read_text(), '// unverified candidate')
                        self.assertEqual(list(candidate.parent.iterdir()), [candidate])
                    verification.reset_mock()
                    scan_failure = True
                    with self.assertRaises(RuntimeError):
                        generator.generate(**options)
                    verification.assert_not_called()
                    self.assertEqual(len(list((root / 'quarantine').glob('*/implementation.ts'))), 3)
                    scan_failure = False
                    verification.side_effect = None
                    generator.generate(**options)
                    self.assertEqual(accepted.read_text(), '// unverified candidate')
                    accepted.write_text('previously accepted bytes')

                    def change_source(command, **kwargs):
                        Path(command[-1]).write_text('// changed after scan')
                    verification.side_effect = change_source
                    with self.assertRaises(AssertionError):
                        generator.generate(**options)
                self.assertEqual(accepted.read_text(), 'previously accepted bytes')
                self.assertEqual(engine.remove.call_count, 6)
                specs = engine.create.call_args.args[2][1::2]
                self.assertFalse(any('/checks' in s or '/tests' in s or '/repo' in s for s in specs))
                self.assertEqual(sum('/inputs/' in s for s in specs), 1)
                self.assertEqual(sum('dst=/implementation/contract.ts,readonly' in s for s in specs), 1)
                self.assertEqual(set(accepted.parent.iterdir()), {accepted})
                self.assertEqual((root / box.contract_path).read_text(), '// synthetic contract')

    def test_cli_withholds_arbitrary_errors_and_preserves_generation_diagnostics(self):
        for selection in SELECTIONS:
            root, box, _ = select_box(selection)
            options = dict(box_root=root, box=box, verification_command=verification_command(selection),
                           detailed_diagnostics=selection == 'render-welcome')
            with self.subTest(box=selection), patch.object(generator, 'generate', side_effect=RuntimeError('PRIVATE')), \
                 redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                self.assertEqual(generator.cli(**options), 1)
                self.assertNotIn('PRIVATE', out.getvalue() + err.getvalue())
                self.assertNotIn('Traceback', out.getvalue() + err.getvalue())
        from boundscript_internal.container_runtime import check_resource

        def fail(**kwargs):
            check_resource('memory.max', 'max', (512 * 1024 * 1024,))

        with patch.object(generator, 'generate', side_effect=fail), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(generator.cli(**options), 1)
        message = err.getvalue()
        for text in ('memory.max: unlimited', 'cgroup-v2', 'boundscript_internal/container_runtime.py:', '(check_resource)'):
            self.assertIn(text, message)
        self.assertNotIn(str(Path.home()), message)
