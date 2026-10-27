"""Extraction boundaries, independent roots and unchanged trusted assets."""
import ast
import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from boundscript_internal import native_verifier


class NativeVerifierBoundaryTests(unittest.TestCase):
    def test_shared_verifier_has_no_experiment_configuration_or_default_box(self):
        source = Path(native_verifier.__file__).read_text()
        imports = [node for node in ast.walk(ast.parse(source))
                   if isinstance(node, (ast.Import, ast.ImportFrom))]
        for node in imports:
            names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom):
                names.append(node.module or '')
            self.assertFalse(any(name.startswith('experiments') for name in names))
        self.assertNotIn('import_module', source)
        self.assertFalse(hasattr(native_verifier, 'BOX'))
        self.assertFalse(hasattr(native_verifier, 'SPIKE'))
        self.assertEqual(native_verifier.RUNNER, ROOT / 'boundscript_internal')
        for file in ('vitest.config.mts', 'compiler-diagnostics.mjs', 'diagnostic-reporter.mjs'):
            self.assertTrue((native_verifier.RUNNER / file).is_file())

    def test_two_fixed_entry_points_pass_separate_roots_and_definitions(self):
        definitions = []
        for directory in ('native-typescript-contracts', 'render-welcome-native'):
            entry = importlib.import_module(f'experiments.{directory}.verify')
            generate = importlib.import_module(f'experiments.{directory}.generate')
            self.assertIs(entry.BOX, generate.BOX)
            self.assertIs(entry.verify_candidate, native_verifier.check)
            with patch.object(entry, 'verify_candidate') as check:
                entry.check(Path('/candidate.ts'))
            check.assert_called_once_with(Path('/candidate.ts'), box_root=ROOT / 'experiments' / directory,
                                          box=entry.BOX)
            definitions.append(entry.BOX)
        self.assertNotEqual(definitions[0].fingerprint(), definitions[1].fingerprint())
        self.assertEqual(definitions[0].verification_path, '.')
        self.assertEqual(definitions[1].verification_path, '.')


if __name__ == '__main__':
    unittest.main()
