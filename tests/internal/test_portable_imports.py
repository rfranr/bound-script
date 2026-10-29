"""Real TypeScript relocation checks; no model, credentials or container required."""
from contextlib import redirect_stdout
import importlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from boundscript_internal import native_generator as generator
from experiments.native_cli import verification_command
from boundscript_internal.container_runtime import digest
from boundscript_internal.native_verifier import RUNNER

ROOT = Path(__file__).resolve().parents[2]


class PortableImportTests(unittest.TestCase):
    def test_both_boxes_compile_before_and_after_byte_identical_relocation(self):
        for directory in ('native-typescript-contracts', 'render-welcome-native'):
            box = importlib.import_module(f'experiments.{directory}.native_box').BOX
            with self.subTest(box=box.name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
                sandbox = root / 'sandbox'
                sandbox.mkdir()
                contract = ROOT / 'experiments' / directory / box.contract_path
                shutil.copyfile(contract, sandbox / 'contract.ts')
                candidate = sandbox / 'implementation.ts'
                # A compile-only fixture, not a behavioral implementation or accepted asset.
                source = (f"import type {{ {box.function_type} }} from './contract';\n"
                          f'export const {box.implementation_export}: {box.function_type} = '
                          '() => { throw new Error("compile-only fixture"); };\n')
                candidate.write_text(source)
                before = digest(candidate)
                compiler = root / 'compiler.mjs'
                adapter = (RUNNER / 'compiler-diagnostics.mjs').read_text()
                adapter = adapter.replace('/node_modules', str(ROOT / 'node_modules'))
                adapter = adapter.replace('/implementation/', str(sandbox) + '/').replace('/checks/', str(root) + '/')
                adapter = adapter.replace('/verification-work/', str(sandbox) + '/')
                compiler.write_text(adapter)
                (root / 'check-contract.ts').write_text(box.contract_check(str(candidate)).replace(
                    box.contract_module, str(sandbox / 'contract.ts')))
                result = subprocess.run(['node', str(compiler)], capture_output=True, text=True, timeout=30)
                report = json.loads((sandbox / 'typescript-diagnostics.json').read_text())
                self.assertEqual(result.returncode, 0, report)
                self.assertEqual(report['errorCount'], 0)

                # Consumer-owned fixture setup, not a generation/promotion output.
                consumer = root / 'application' / 'boxes' / 'parent' / box.name
                consumer.mkdir(parents=True)
                consumer_contract = consumer / 'contract.ts'
                consumer_contract.write_bytes(contract.read_bytes())
                contract_before = digest(consumer_contract)
                # Integrate only the implementation beside the existing consumer contract.
                promoted = consumer / Path(box.accepted_path).name
                shutil.copyfile(candidate, promoted)
                self.assertEqual(digest(promoted), before)
                result = subprocess.run([
                    'node', str(ROOT / 'node_modules/typescript/bin/tsc'), '--strict', '--noEmit',
                    '--target', 'ES2022', '--module', 'NodeNext', '--allowImportingTsExtensions',
                    str(promoted)], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(digest(promoted), before)
                self.assertEqual(digest(consumer_contract), contract_before)

                for specifier in (str(sandbox / 'contract.ts'), '../inputs/contract'):
                    candidate.write_text(source.replace('./contract', specifier))
                    result = subprocess.run(['node', str(compiler)], capture_output=True, text=True, timeout=30)
                    report = json.loads((sandbox / 'typescript-diagnostics.json').read_text())
                    self.assertNotEqual(result.returncode, 0)
                    self.assertGreater(report['errorCount'], 0)
                self.assertIn("'./contract'", generator.generation_prompt(box))
                self.assertEqual(box.contract_module, '/implementation/contract.ts')

    def test_native_promotion_leaves_existing_contracts_untouched(self):
        for directory in ('native-typescript-contracts', 'render-welcome-native'):
            box = importlib.import_module(f'experiments.{directory}.native_box').BOX
            with self.subTest(box=box.name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                contract = root / box.contract_path
                contract.parent.mkdir(parents=True)
                contract.write_bytes(b'// consumer-owned input\n')
                destination = root / box.accepted_path
                destination.parent.mkdir(parents=True)
                existing_contract = destination.parent / 'contract.ts'
                existing_contract.write_bytes(b'// existing consumer contract; do not overwrite\n')
                protected = {p: p.read_bytes() for p in (contract, existing_contract)}
                candidate = root / 'candidate.ts'
                candidate.write_bytes(b'// independently verified fixture\r\n')
                scanned = digest(candidate)
                context = MagicMock()
                context.__enter__.return_value = (candidate, scanned)
                with patch.object(box.__class__, 'verification_files', return_value=()), \
                     patch.object(generator, 'runtime'), \
                     patch.object(generator, 'agent_submission', return_value=context), \
                     patch.object(generator.subprocess, 'run') as verification, \
                     patch.object(generator.shutil, 'copyfile', wraps=shutil.copyfile) as copy, \
                     redirect_stdout(io.StringIO()):
                    generator.generate(box_root=root, box=box, verification_command=verification_command(
                        'normalize-contact' if directory == 'native-typescript-contracts' else 'render-welcome'))
                verification.assert_called_once()
                copy.assert_called_once_with(candidate, destination)
                self.assertEqual(destination.read_bytes(), candidate.read_bytes())
                self.assertEqual(digest(destination), scanned)
                self.assertEqual(set(destination.parent.iterdir()), {destination, existing_contract})
                for path, before in protected.items():
                    self.assertEqual(path.read_bytes(), before)

                # Verification must not authorize promotion if the public input changes.
                destination.write_bytes(b'// previous accepted implementation\n')

                def change_contract(*args, **kwargs):
                    contract.write_bytes(b'// changed during verification\n')

                with patch.object(box.__class__, 'verification_files', return_value=()), \
                     patch.object(generator, 'runtime'), \
                     patch.object(generator, 'agent_submission', return_value=context), \
                     patch.object(generator.subprocess, 'run', side_effect=change_contract), \
                     redirect_stdout(io.StringIO()):
                    with self.assertRaisesRegex(AssertionError, 'Public contract changed'):
                        generator.generate(box_root=root, box=box, verification_command=verification_command(
                            'normalize-contact' if directory == 'native-typescript-contracts' else 'render-welcome'))
                self.assertEqual(destination.read_bytes(), b'// previous accepted implementation\n')
                self.assertEqual(existing_contract.read_bytes(), protected[existing_contract])


if __name__ == '__main__':
    unittest.main()
