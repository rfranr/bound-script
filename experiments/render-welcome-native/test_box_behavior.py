"""RenderWelcome-owned definition, fixtures and opt-in behavior checks."""
from importlib import import_module
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import unittest

from boundscript_internal.native_verifier import check, VerificationFailure

HERE = Path(__file__).resolve().parent
BOX = import_module('experiments.render-welcome-native.native_box').BOX


class WelcomeBehaviorTests(unittest.TestCase):
    def test_definition_is_local_and_complete(self):
        for value in (BOX.task_path, BOX.contract_path, BOX.verification_path, BOX.accepted_path):
            self.assertFalse(PurePosixPath(value).is_absolute())
            self.assertNotIn('..', PurePosixPath(value).parts)
        self.assertIn('fixtures/welcome-cases.json', BOX.verification_files(HERE))
        self.assertEqual({file for suite in BOX.suites for file in suite.files},
                         {'validators.test.ts', 'acceptance.test.ts'})
        self.assertEqual(BOX.suites[1].categories, ('acceptance', 'properties'))
        self.assertEqual(len(json.loads((HERE / 'fixtures/welcome-cases.json').read_text())), 6)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_WELCOME_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_wrong_signature_shape_behavior_and_mutation(self):
        accepted = HERE / BOX.accepted_path
        before = accepted.read_bytes()
        check(accepted, box_root=HERE, box=BOX)
        negatives = {
            'compilation': 'export const renderWelcome = () => 0;',
            'typia': 'export const renderWelcome = () => ({message:"wrong"}) as any;',
            'assertion': 'export const renderWelcome = () => "wrong";',
            'mutation': 'export const renderWelcome = (contact: any) => {contact.name="changed"; return "wrong";};',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for kind, source in negatives.items():
                candidate = Path(tmp) / f'{kind}.ts'
                candidate.write_text(source)
                with self.subTest(kind=kind), self.assertRaises(VerificationFailure) as failure:
                    check(candidate, box_root=HERE, box=BOX)
                self.assertIn('runtime' if kind == 'mutation' else kind, failure.exception.kind)
        self.assertEqual(accepted.read_bytes(), before)
