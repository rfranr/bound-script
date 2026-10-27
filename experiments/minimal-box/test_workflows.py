"""Baseline verification and promotion policies; infrastructure tests live in tests/internal."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from boundscript_internal.container_runtime import digest
import generate as baseline_generator
import verify as baseline_verifier
import verify_pair

HERE = Path(__file__).resolve().parent


class WorkflowTests(unittest.TestCase):
    def test_fixed_baseline_runners_verify_before_promotion_without_git(self):
        for box, filename, destination in (
                ('greeting', 'greet.ts', 'implementation/greet.ts'),
                ('normalize-contact', 'implementation.ts', 'two-boxes/accepted/normalize-contact.ts'),
                ('render-welcome', 'implementation.ts', 'two-boxes/accepted/render-welcome.ts')):
            for failure in (False, True):
                with self.subTest(box=box, failure=failure), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    candidate = root / filename
                    candidate.write_text('// verified source')
                    accepted = root / destination
                    accepted.parent.mkdir(parents=True)
                    accepted.write_text('// previous accepted source')
                    context = MagicMock()
                    context.__enter__.return_value = (candidate, digest(candidate))

                    def verify(command, **kwargs):
                        self.assertEqual(accepted.read_text(), '// previous accepted source')
                        self.assertEqual(command[0], sys.executable)
                        self.assertEqual(command[-1], str(candidate))
                        if failure:
                            raise subprocess.CalledProcessError(1, command)

                    args = ['generate.py'] + ([] if box == 'greeting' else [box])
                    with patch.object(baseline_generator, 'HERE', root), \
                         patch.object(baseline_generator, 'runtime'), \
                         patch.object(baseline_generator, 'agent_submission', return_value=context) as agent, \
                         patch.object(baseline_generator.sys, 'argv', args), \
                         patch.object(baseline_generator.subprocess, 'run', side_effect=verify) as process, \
                         redirect_stdout(io.StringIO()):
                        if failure:
                            with self.assertRaises(subprocess.CalledProcessError):
                                baseline_generator.main()
                        else:
                            baseline_generator.main()
                    process.assert_called_once()
                    self.assertEqual(accepted.read_text(), '// previous accepted source' if failure else '// verified source')
                    inputs = agent.call_args.args[1]
                    self.assertEqual(len(inputs), 2 if box == 'normalize-contact' else 3)

    def test_generator_cli_withholds_arbitrary_errors(self):
        with patch.object(baseline_generator, 'main', side_effect=RuntimeError('PRIVATE')), \
             redirect_stderr(io.StringIO()) as output:
            self.assertEqual(baseline_generator.cli(), 1)
        self.assertNotIn('PRIVATE', output.getvalue())

    def test_assertions_required_for_all_entry_points_on_any_branch(self):
        native = HERE.parent / 'native-typescript-contracts'
        welcome = HERE.parent / 'render-welcome-native'
        for path in (HERE / 'generate.py', HERE / 'verify.py', HERE / 'verify_pair.py',
                     native / 'generate.py', native / 'verify.py',
                     welcome / 'generate.py', welcome / 'verify.py'):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as cwd:
                # Absolute entry points must resolve internal imports even outside
                # the repository, including the independent verifier subprocess.
                result = subprocess.run([sys.executable, '-B', '-O', str(path)], cwd=cwd,
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Assertions must be enabled', result.stdout + result.stderr)
                source = path.read_text()
                self.assertNotIn('--show-current', source)
                self.assertNotIn("run('git'", source)

    def test_baseline_verifier_preflights_do_not_invoke_git(self):
        for module in (baseline_verifier, verify_pair):
            with self.subTest(module=module.__name__), \
                 patch.object(module, 'runtime') as factory, \
                 patch.object(module.sys, 'argv', ['verify.py']):
                factory.return_value.image.side_effect = RuntimeError('synthetic preflight stop')
                with self.assertRaisesRegex(RuntimeError, 'synthetic preflight stop'):
                    module.main()
                factory.return_value.image.assert_called_once()

    def test_entry_points_resolve_one_internal_package_without_peer_imports(self):
        root = HERE.parents[1]
        paths = [HERE / name for name in ('generate.py', 'verify.py', 'verify_pair.py')]
        paths += [HERE.parent / box / name
                  for box in ('native-typescript-contracts', 'render-welcome-native')
                  for name in ('generate.py', 'verify.py')]
        source = '''
import runpy, sys
from pathlib import Path
paths = PATHS
for path in paths:
    loaded = runpy.run_path(path, run_name='import_check')
    from boundscript_internal import container_runtime, agent_workspace
    if 'verify_candidate' in loaded:
        from boundscript_internal import native_verifier
        assert loaded['verify_candidate'] is native_verifier.check
        assert native_verifier.runtime is container_runtime.runtime
    else:
        assert loaded['runtime'] is container_runtime.runtime
    if path.endswith('generate.py'):
        assert loaded['agent_submission'] is agent_workspace.agent_submission
    assert Path(path).parent.as_posix() not in sys.path
assert not {'verify', 'verify_pair', 'generate', 'container_runtime', 'agent_workspace'} & sys.modules.keys()
assert container_runtime.ROOT == Path(CHECKOUT_ROOT)
'''.replace('PATHS', json.dumps([str(p) for p in paths])).replace('CHECKOUT_ROOT', json.dumps(str(root)))
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, '-I', '-B', '-c', source], cwd=cwd,
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pair_cleanup_on_create_start_or_exec_failure(self):
        for method in ('create', 'start', 'exec'):
            with patch.object(verify_pair, 'runtime') as factory:
                engine = factory.return_value
                getattr(engine, method).side_effect = RuntimeError('synthetic failure')
                with self.assertRaises(RuntimeError):
                    verify_pair.check('normalize-contact', verify_pair.PAIR / 'accepted/normalize-contact.ts')
                engine.remove.assert_called_once()
                self.assertEqual(engine.remove.call_args.args[0], engine.create.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
