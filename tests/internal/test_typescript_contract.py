"""Generator regressions: compile trusted synthetic fixtures, never execute them."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from boundscript_internal.typescript_contract import generate_contract_check
from boundscript_internal.box_definition import BoxDefinition


class TypeScriptContractTests(unittest.TestCase):
    def test_reproducible_and_escaped(self):
        args = ('./contract"file.ts', 'Contract', './implementation.ts', 'implementation')
        source = generate_contract_check(*args)
        self.assertEqual(source, generate_contract_check(*args))
        self.assertIn(r'./contract\"file.ts', source)
        self.assertIn('const checked: Contract = implementation;', source)

    def test_rejects_source_injection(self):
        for index, value in ((0, ''), (0, './contract\n.ts'),
                             (1, 'F; throw 0'), (3, 'f()')):
            args = ['./contract.ts', 'F', './implementation.ts', 'f']
            args[index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                generate_contract_check(*args)

    def test_two_independent_contracts_and_compilation_failures(self):
        # Only static, trusted fixtures reach the host compiler. noEmit is always
        # set; no candidate is loaded or executed, and no model is involved.
        fixtures = [
            ('FormatLabel', 'formatLabel', '(value: string) => string',
             '(value: string): string => value',
             '(value: number): string => String(value)',
             '(value: string): number => value.length'),
            ('SumValues', 'sumValues', '(values: readonly number[], scale: number) => number',
             '(values: readonly number[], scale: number): number => values.length * scale',
             '(values: string, scale: number): number => values.length * scale',
             '(values: readonly number[], scale: number): string => String(scale)'),
        ]
        with tempfile.TemporaryDirectory(prefix='boundscript-contract-test-') as tmp:
            root = Path(tmp)
            for type_name, export_name, signature, valid, bad_input, bad_output in fixtures:
                (root / 'contract.ts').write_text(f'export type {type_name} = {signature};\n')
                box = BoxDefinition(type_name, 'task.md', 'contract.ts', './contract.ts',
                                    type_name, export_name, 'accepted.ts', '.')
                (root / 'check-contract.ts').write_text(box.contract_check('./implementation.ts'))
                for case, source, diagnostic in (
                    ('valid', f'export const {export_name} = {valid};', None),
                    ('parameter', f'export const {export_name} = {bad_input};', 'TS2322'),
                    ('return', f'export const {export_name} = {bad_output};', 'TS2322'),
                    ('missing-implementation', 'export const unrelated = 0;', 'TS2305'),
                ):
                    with self.subTest(contract=type_name, case=case):
                        (root / 'implementation.ts').write_text(source)
                        self.compile(root, diagnostic)
                (root / 'implementation.ts').write_text(f'export const {export_name} = {valid};')
                (root / 'contract.ts').write_text('export type Unrelated = string;')
                with self.subTest(contract=type_name, case='missing-contract-type'):
                    self.compile(root, 'TS2305')

    def compile(self, root, diagnostic):
        result = subprocess.run([
            'node', str(ROOT / 'node_modules/typescript/lib/tsc.js'),
            '--noEmit', '--strict', '--target', 'ES2022', '--module', 'NodeNext',
            '--allowImportingTsExtensions', '--typeRoots', str(root / 'no-ambient-types'),
            str(root / 'check-contract.ts'),
        ], capture_output=True, text=True, timeout=30)
        if diagnostic is None:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(diagnostic, result.stdout)
        self.assertEqual(sorted(p.name for p in root.iterdir()),
                         ['check-contract.ts', 'contract.ts', 'implementation.ts'])


if __name__ == '__main__':
    unittest.main()
