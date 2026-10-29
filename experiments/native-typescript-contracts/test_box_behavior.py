"""NormalizeContact-owned fixture and opt-in behavior checks."""
from importlib import import_module
import json
import os
from pathlib import Path
import tempfile
import unittest

from boundscript_internal.native_verifier import check

HERE = Path(__file__).resolve().parent
BOX = import_module('experiments.native-typescript-contracts.native_box').BOX


class ContactBehaviorTests(unittest.TestCase):
    def test_native_fixtures_have_phone_without_an_invented_phone_oracle(self):
        cases = json.loads((HERE / 'cases.json').read_text())
        self.assertEqual(len(cases), 20)
        for case in cases:
            self.assertEqual(set(case['input']), {'name', 'email', 'phone'})
            self.assertEqual(case['input']['phone'], '+34600111222')
            if case['expected']['ok']:
                self.assertEqual(set(case['expected']['contact']), {'name', 'email'})

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_negative_submissions(self):
        accepted = HERE / BOX.accepted_path
        check(accepted, box_root=HERE, box=BOX)
        before = accepted.read_bytes() if accepted.exists() else None
        negatives = {
            'signature': 'export const normalizeContact = () => 0;',
            'runtime-shape': 'export const normalizeContact = () => ({ok:true,contact:{name:3,email:"x"}} as any);',
            'behavior': 'export const normalizeContact = () => ({ok:false as const,errors:[]});',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, source in negatives.items():
                candidate = Path(tmp) / (name + '.ts')
                candidate.write_text(source)
                with self.subTest(name=name), self.assertRaises(RuntimeError):
                    check(candidate, box_root=HERE, box=BOX)
        self.assertEqual(accepted.read_bytes() if accepted.exists() else None, before)
