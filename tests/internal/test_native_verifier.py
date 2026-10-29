"""Extraction boundaries, independent roots and unchanged trusted assets."""
import ast
from contextlib import redirect_stderr
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from boundscript_internal import native_verifier, native_generator, native_cli
from experiments.native_cli import select_box, main, verification_command


class NativeVerifierBoundaryTests(unittest.TestCase):
    def test_shared_verifier_has_no_experiment_configuration_or_default_box(self):
        for module in (native_verifier, native_generator, native_cli):
            source = Path(module.__file__).read_text()
            imports = [node for node in ast.walk(ast.parse(source))
                       if isinstance(node, (ast.Import, ast.ImportFrom))]
            for node in imports:
                names = [alias.name for alias in node.names]
                if isinstance(node, ast.ImportFrom):
                    names.append(node.module or '')
                self.assertFalse(any(name.startswith('experiments') for name in names))
            self.assertNotIn('import_module', source)
            self.assertFalse(hasattr(module, 'BOX'))
            self.assertFalse(hasattr(module, 'SPIKE'))
        self.assertEqual(native_verifier.RUNNER, ROOT / 'boundscript_internal')
        for file in ('vitest.config.mts', 'compiler-diagnostics.mjs', 'diagnostic-reporter.mjs'):
            self.assertTrue((native_verifier.RUNNER / file).is_file())

    def test_one_entry_point_passes_separate_roots_and_definitions(self):
        definitions = []
        self.assertIs(native_cli.check, native_verifier.check)
        for selection, directory in (('normalize-contact', 'native-typescript-contracts'),
                                     ('render-welcome', 'render-welcome-native')):
            root, box, _ = select_box(selection)
            self.assertEqual(root, ROOT / 'experiments' / directory)
            with patch.object(native_cli, 'check') as check:
                self.assertEqual(main(['verify', selection, '/candidate.ts']), 0)
            check.assert_called_once_with(Path('/candidate.ts'), box_root=root, box=box)
            with patch.object(native_generator, 'generate') as generate:
                self.assertEqual(main(['generate', selection]), 0)
            self.assertIs(generate.call_args.kwargs['box'], box)
            self.assertEqual(generate.call_args.kwargs['box_root'], root)
            self.assertEqual(generate.call_args.kwargs['verification_command'], verification_command(selection))
            definitions.append(box)
        self.assertNotEqual(definitions[0].fingerprint(), definitions[1].fingerprint())
        self.assertEqual(definitions[0].verification_path, '.')
        self.assertEqual(definitions[1].verification_path, '.')

    def test_cli_requires_explicit_selection_and_never_generates_for_invalid_arguments(self):
        with patch.object(native_generator, 'generate') as generate, redirect_stderr(io.StringIO()):
            for args in ([], ['verify'], ['other', 'normalize-contact'], ['verify', 'unknown'],
                         ['generate', 'normalize-contact', 'unexpected'],
                         ['generate', 'render-welcome', 'unexpected']):
                with self.subTest(args=args):
                    self.assertEqual(main(args), 1)
            generate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
