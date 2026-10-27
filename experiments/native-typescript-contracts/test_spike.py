"""Credential-free wiring regressions; mocks do not establish engine security."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
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
    def test_baseline_authorities_are_preserved(self):
        pair = HERE.parent / 'minimal-box/two-boxes'
        self.assertEqual((HERE / 'src/contract.ts').read_bytes(),
                         (pair / 'contracts/normalize-contact.ts').read_bytes())
        self.assertEqual((HERE / 'task.md').read_bytes(),
                         (pair / 'tasks/normalize-contact.md').read_bytes())
        self.assertEqual((HERE / 'check-contract.ts').read_bytes(),
                         (pair / 'check-normalize.ts').read_bytes())

    def test_verifier_failures_cleanup_and_do_not_run_baseline_checks(self):
        for stage in ('create', 'start', 'exec'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp:
                candidate = Path(tmp) / 'candidate.ts'
                candidate.write_text('export const normalizeContact = () => 0;')
                engine = MagicMock()
                getattr(engine, stage).side_effect = RuntimeError('synthetic failure')
                with patch.object(verifier, 'runtime', return_value=engine), \
                     patch.object(verifier, 'baseline_check') as baseline:
                    with self.assertRaises(RuntimeError):
                        verifier.check(candidate)
                engine.remove.assert_called_once()
                baseline.assert_not_called()
                mounts = engine.create.call_args.args[2]
                specs = mounts[1::2]
                self.assertEqual(sum('readonly' not in spec for spec in specs), 1)
                self.assertIn('dst=/implementation', specs[0])
                self.assertTrue(all('readonly' in spec for spec in specs[1:]))

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_negative_submissions(self):
        # Establish that this engine actually supports the positive path first.
        verifier.check(verifier.PAIR / 'accepted/normalize-contact.ts')
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

            def execute(name, *args, **kwargs):
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
                 patch.object(generator, 'run', return_value='experiment/typescript-contracts'), \
                 patch.object(generator, 'runtime', return_value=engine), \
                 patch.object(generator.sys, 'argv', ['generate.py']), \
                 patch.object(generator.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'verify')):
                with self.assertRaises(subprocess.CalledProcessError):
                    generator.main()
            self.assertEqual(accepted.read_text(), 'previously accepted bytes')
            engine.remove.assert_called_once()
            specs = engine.create.call_args.args[2][1::2]
            self.assertFalse(any('/checks' in s or '/tests' in s or '/repo' in s for s in specs))
            self.assertEqual(sum('/inputs/' in s for s in specs), 2)


if __name__ == '__main__':
    unittest.main()
