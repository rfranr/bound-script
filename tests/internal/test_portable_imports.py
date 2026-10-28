"""Real TypeScript relocation checks; no model, credentials or container required."""
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from boundscript_internal.container_runtime import digest
from boundscript_internal.native_verifier import RUNNER

ROOT = Path(__file__).resolve().parents[2]


class PortableImportTests(unittest.TestCase):
    def test_both_boxes_compile_before_and_after_byte_identical_relocation(self):
        for directory in ('native-typescript-contracts', 'render-welcome-native'):
            generator = importlib.import_module(f'experiments.{directory}.generate')
            box = generator.BOX
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
                compiler.write_text(adapter)
                (root / 'check-contract.ts').write_text(box.contract_check(str(candidate)).replace(
                    box.contract_module, str(sandbox / 'contract.ts')))
                result = subprocess.run(['node', str(compiler)], capture_output=True, text=True, timeout=30)
                report = json.loads((sandbox / 'typescript-diagnostics.json').read_text())
                self.assertEqual(result.returncode, 0, report)
                self.assertEqual(report['errorCount'], 0)

                # Nest freely and retain existing promoted filenames: no runtime tooling or aliases.
                consumer = root / 'application' / 'boxes' / 'parent' / box.name
                consumer.mkdir(parents=True)
                promoted = consumer / Path(box.accepted_path).name
                shutil.copyfile(candidate, promoted)
                shutil.copyfile(contract, consumer / 'contract.ts')
                self.assertEqual(digest(promoted), before)
                result = subprocess.run([
                    'node', str(ROOT / 'node_modules/typescript/bin/tsc'), '--strict', '--noEmit',
                    '--target', 'ES2022', '--module', 'NodeNext', '--allowImportingTsExtensions',
                    str(promoted)], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(digest(promoted), before)

                for specifier in (str(sandbox / 'contract.ts'), '../inputs/contract'):
                    candidate.write_text(source.replace('./contract', specifier))
                    result = subprocess.run(['node', str(compiler)], capture_output=True, text=True, timeout=30)
                    report = json.loads((sandbox / 'typescript-diagnostics.json').read_text())
                    self.assertNotEqual(result.returncode, 0)
                    self.assertGreater(report['errorCount'], 0)
                self.assertIn("'./contract'", generator.generation_prompt(box))
                self.assertEqual(box.contract_module, '/implementation/contract.ts')


if __name__ == '__main__':
    unittest.main()
