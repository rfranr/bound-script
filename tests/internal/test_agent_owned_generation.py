"""Credential-free orchestration fixtures; no Pi/provider execution."""
from contextlib import contextmanager, redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from boundscript_internal import native_generator as generator, source_tree as tree
from boundscript_internal.container_runtime import digest
from test_native_box_definition import synthetic_box, build_synthetic_validators
from test_native_workflow import HERE
from test_source_scanning import fixture


class AgentOwnedTests(unittest.TestCase):
    def exercise(self, organization, failure=None, docker=False):
        with tempfile.TemporaryDirectory(prefix='agent-owned-', dir=HERE) as tmp:
            root = Path(tmp)
            box, _ = synthetic_box(root, 'first')
            box = replace(box, contract_module='/implementation/contract.ts')
            accepted = root / box.accepted_path
            accepted.write_text('// unchanged accepted source')
            protected = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            files = {'implementation.ts': b"import type { FirstFunction } from './contract';\nexport const firstFunction: FirstFunction = value => value;\n"}
            if organization == 'nested':
                files = {'implementation.ts': b"import type { FirstFunction } from './contract';\nimport { identity } from './deep/helper';\nexport const firstFunction: FirstFunction = identity;\n",
                         'deep/helper.ts': b'export const identity = (value: number) => value;\n',
                         'unused.ts': b'export const unused = 1;\n'}
            candidate, proof, credentials = fixture(root / 'generation', files)
            # Trusted contract is an input, never part of the output digest.
            (candidate / 'contract.ts').write_bytes((root / box.contract_path).read_bytes())
            proof = ((candidate / 'contract.ts').stat(), digest(candidate / 'contract.ts'))
            snapshots = []
            destroyed = False

            @contextmanager
            def simulated_submission(*args, **kwargs):
                nonlocal destroyed
                self.assertTrue(kwargs['source_tree'])
                config = {'root': str(candidate), 'auth': list(map(str, credentials)),
                          'contract': {'size': proof[0].st_size, 'sha256': proof[1]},
                          'limits': {'files': tree.MAX_FILES, 'bytes': tree.MAX_BYTES,
                                     'depth': tree.MAX_DEPTH, 'path': tree.MAX_PATH, 'entries': tree.MAX_ENTRIES}}
                scanner = Path(generator.__file__).with_name('credential_scanner.mjs').read_text()
                result = subprocess.run(['node', '--input-type=module', '-', json.dumps(config)],
                                        input=scanner, text=True, capture_output=True, check=True)
                destroyed = True  # Simulated producer has ended before snapshot creation.
                with tree.staged_source_tree(candidate, protected_contract=proof) as (snapshot, records):
                    snapshots.append(snapshot)
                    self.assertEqual(tree.inventory_digest(records), result.stdout.strip())
                    yield snapshot, result.stdout.strip()

            real_run = subprocess.run
            def verify(command, **kwargs):
                self.assertTrue(destroyed)
                self.assertEqual(command[-2], '--source-tree')
                snapshot = Path(command[-1])
                self.assertEqual(snapshot, snapshots[0])
                self.assertNotEqual(snapshot, candidate)
                self.assertFalse((snapshot / 'contract.ts').exists())
                if failure == 'verifier':
                    raise subprocess.CalledProcessError(1, command)
                if failure == 'unused-change':
                    (snapshot / 'unused.ts').write_text('// changed unused member')
                if failure == 'task-change':
                    (root / box.task_path).write_text('changed')
                if docker:
                    return real_run(command, **kwargs)

            command = ['unused-verifier']
            if docker:
                build_synthetic_validators(root, box)
                # Independent process, same unchanged shared verification CLI and Box definition.
                runner = root / 'verify_fixture.py'
                runner.write_text('import sys\nfrom pathlib import Path\n'
                    'from boundscript_internal.box_definition import BoxDefinition, VerificationSuite\n'
                    'from boundscript_internal.native_cli import cli\n'
                    f'box = {box!r}\n'
                    f'sys.exit(cli(sys.argv[1:], box_root=Path({str(root)!r}), box=box))\n')
                command = [sys.executable, str(runner)]
                protected = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            # Scanner must use the real subprocess function; only verification is intercepted.
            original = generator.subprocess.run
            def dispatch(command, **kwargs):
                if command[0] == 'node':
                    return original(command, **kwargs)
                return verify(command, **kwargs)
            with patch.object(generator, 'agent_submission', side_effect=simulated_submission), \
                 patch.object(generator.subprocess, 'run', side_effect=dispatch), \
                 patch.object(generator, 'quarantine') as quarantine, \
                 patch.object(generator.shutil, 'copyfile') as copy, redirect_stdout(io.StringIO()) as out:
                if failure:
                    with self.assertRaises((RuntimeError, subprocess.CalledProcessError)):
                        generator.generate(box_root=root, box=box, verification_command=command, agent_owned=True)
                else:
                    generator.generate(box_root=root, box=box, verification_command=command, agent_owned=True)
                    self.assertIn(f'files={len(files)}', out.getvalue())
                quarantine.assert_not_called()
                copy.assert_not_called()
            self.assertFalse(snapshots[0].exists())
            for path, data in protected.items():
                if failure != 'task-change' or path != root / box.task_path:
                    self.assertEqual(path.read_bytes(), data)
            self.assertFalse((root / 'quarantine').exists())

    def test_single_and_nested_and_integrity_failures(self):
        for organization in ('single', 'nested'):
            for failure in (None, 'verifier', 'unused-change', 'task-change'):
                with self.subTest(organization=organization, failure=failure):
                    self.exercise(organization, failure)

    def test_explicit_cli_and_neutral_prompt(self):
        with patch.object(generator, 'generate') as generate:
            self.assertEqual(generator.cli(box_root=None, box=None, verification_command=[], args=['--agent-owned']), 0)
            self.assertTrue(generate.call_args.kwargs['agent_owned'])
            self.assertEqual(generator.cli(box_root=None, box=None, verification_command=[], args=['--agent-owned', 'extra']), 1)
        from test_native_workflow import BOX
        prompt = generator.agent_owned_prompt(BOX)
        for hint in ('helper', 'class', 'layer', 'split', 'multi-file', 'single-file'):
            self.assertNotIn(hint, prompt)
        self.assertIn(BOX.implementation_export, prompt)
        self.assertIn(BOX.function_type, prompt)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in independent Docker verification')
    def test_independent_docker_single_and_nested(self):
        for organization in ('single', 'nested'):
            with self.subTest(organization=organization):
                self.exercise(organization, docker=True)
