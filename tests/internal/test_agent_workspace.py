"""Shared generation regressions; no credentials, model calls or real engines."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from boundscript_internal import agent_workspace as workspace


class WorkspaceTests(unittest.TestCase):
    def test_generation_cleanup_scan_and_lifetime(self):
        for failure in (None, 'create', 'start', 'agent', 'scan', 'changed-scan', 'cleanup-change'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                auth = root / 'auth.json'
                auth.write_text('{}')
                pi = root / 'pi'
                (pi / 'dist/bundle').mkdir(parents=True)
                (pi / 'dist/bundle/cli.js').write_text('// synthetic Pi')
                (pi / 'package.json').write_text('{"version":"1.4.0"}')
                task = root / 'task.md'
                task.write_text('synthetic task')
                engine = MagicMock()
                submission = None

                def execute(name, *args, **kwargs):
                    nonlocal submission
                    source = kwargs.get('source', '')
                    if '/opt/pi/dist/bundle/cli.js' in args:
                        if failure == 'agent':
                            raise RuntimeError('PRIVATE AGENT DIAGNOSTICS')
                        specs = engine.create.call_args.args[2][1::2]
                        spec = next(s for s in specs if 'dst=/implementation' in s)
                        directory = Path(spec.split('src=', 1)[1].split(',')[0])
                        submission = directory / 'implementation.ts'
                        submission.write_text('// scanned source')
                        return '\n'.join(json.dumps(e) for e in [
                            {'type': 'session', 'id': '00000000-0000-4000-8000-000000000031', 'cwd': '/implementation'},
                            {'type': 'tool_execution_start', 'toolName': 'write'},
                            {'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'stop'}},
                            {'type': 'agent_settled', 'aborted': False},
                        ])
                    if 'function check(v)' in source:
                        if failure == 'scan':
                            raise RuntimeError('PRIVATE SCAN DIAGNOSTICS')
                        return '0' * 64 if failure == 'changed-scan' else workspace.digest(submission)
                    if 'observed' in source:
                        return json.dumps(['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT',
                                           'EROFS', 'ENOENT', 'ENOENT', 'ERR_MODULE_NOT_FOUND'])
                    return ''

                engine.exec.side_effect = execute
                if failure in ('create', 'start'):
                    getattr(engine, failure).side_effect = RuntimeError('PRIVATE ENGINE DIAGNOSTICS')
                if failure == 'cleanup-change':
                    engine.remove.side_effect = lambda _: submission.write_text('changed during cleanup')
                output = io.StringIO()
                yielded = False
                try:
                    with redirect_stdout(output), workspace.agent_submission(
                            engine, {'task.md': task}, pi=pi, auth=auth, box='synthetic',
                            filename='implementation.ts', prompt='synthetic', model='synthetic', thinking='low') as (candidate, scanned):
                        yielded = True
                        engine.remove.assert_called_once()
                        self.assertTrue(candidate.is_file())
                        self.assertEqual(workspace.digest(candidate), scanned)
                        self.assertEqual(candidate.read_text(), '// scanned source')
                        self.assertIsNone(failure)
                except (RuntimeError, AssertionError):
                    if failure is None:
                        raise
                self.assertEqual(yielded, failure is None)
                engine.remove.assert_called_once()
                if submission:
                    self.assertFalse(submission.exists())
                self.assertNotIn('PRIVATE', output.getvalue())


if __name__ == '__main__':
    unittest.main()
