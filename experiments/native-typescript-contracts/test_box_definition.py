"""Two explicit configurations exercise native wiring without a second business Box."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from test_spike import generator, verifier


class BoxDefinitionTests(unittest.TestCase):
    def test_entry_points_share_definition_and_reject_mismatch_before_verification(self):
        self.assertIs(generator.BOX, verifier.BOX)
        box = generator.BOX
        for field, value in (
            ('name', 'synthetic'), ('task_path', 'other-task.md'),
            ('contract_path', 'other-contract.ts'), ('contract_module', '/inputs/other.ts'),
            ('function_type', 'OtherFunction'), ('implementation_export', 'otherFunction'),
            ('accepted_path', 'other-accepted.ts'), ('verification_path', 'other-checks'),
        ):
            changed = replace(box, **{field: value})
            self.assertNotEqual(box.fingerprint(), changed.fingerprint())
            with self.subTest(field=field), patch.object(verifier, 'BOX', changed), \
                 patch.object(verifier.sys, 'argv', ['verify.py', '--box-definition',
                                                   box.fingerprint(), '/unused.ts']), \
                 patch.object(verifier, 'check') as check:
                with self.assertRaisesRegex(verifier.VerificationFailure, 'definition mismatch'):
                    verifier.main()
                check.assert_not_called()
        with patch.object(verifier.sys, 'argv', ['verify.py', '--box-definition',
                                               box.fingerprint(), '/unused.ts']), \
             patch.object(verifier, 'check') as check:
            verifier.main()
            check.assert_called_once_with(Path('/unused.ts'))

    def test_two_definitions_select_own_inputs_checks_and_exports(self):
        for label, type_name, export_name in [('first', 'FirstFunction', 'firstFunction'),
                                               ('second', 'SecondFunction', 'secondFunction')]:
            with self.subTest(box=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                box = replace(generator.BOX, name=label, task_path=f'{label}-task.md',
                              contract_path=f'{label}-contract.ts',
                              contract_module=f'/inputs/{label}.ts',
                              function_type=type_name, implementation_export=export_name,
                              accepted_path=f'{label}-accepted.ts', verification_path=label)
                (root / box.task_path).write_text('synthetic task')
                (root / box.contract_path).write_text(f'export type {type_name} = () => string;')
                suite = root / box.verification_path
                (suite / '.generated').mkdir(parents=True)
                (suite / '.generated/validators.ts').write_text('// synthetic Typia artifact')
                (suite / 'src').mkdir()
                (suite / 'src/validators.ts').write_text('// independently owned validators')
                for filename in ('acceptance.test.ts', 'validators.test.ts', 'vitest.config.mts',
                                 'diagnostic-reporter.mjs', 'compiler-diagnostics.mjs', 'cases.json'):
                    (suite / filename).write_text(f'// independently owned {label} {filename}')
                candidate = root / 'candidate.ts'
                candidate.write_text('// never executed')
                engine = MagicMock()
                engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5),
                                           json.dumps('ENETUNREACH')]

                def inspect_checks(*args):
                    specs = engine.create.call_args.args[2][1::2]
                    spec = next(s for s in specs if 'dst=/checks,' in s)
                    checks = Path(spec.split('src=', 1)[1].split(',')[0])
                    for file in suite.rglob('*'):
                        if file.is_file():
                            self.assertEqual((checks / file.relative_to(suite)).read_bytes(), file.read_bytes())
                    source = (checks / 'check-contract.ts').read_text()
                    self.assertIn(f'import type {{ {type_name} as Contract }}', source)
                    self.assertIn(f'import {{ {export_name} as implementation }}', source)
                    self.assertIn(json.dumps(box.contract_module), source)
                    self.assertIn(f'type=bind,src={root / box.contract_path},dst={box.contract_module},readonly', specs)

                with patch.object(verifier, 'SPIKE', root), \
                     patch.object(verifier, 'runtime', return_value=engine), \
                     patch.object(verifier, 'run_compiler', side_effect=inspect_checks), \
                     patch.object(verifier, 'run_vitest') as vitest:
                    verifier.check(candidate, box)
                self.assertEqual([call.args[3] for call in vitest.call_args_list],
                                 ['typia', 'acceptance', 'properties'])
                engine.remove.assert_called_once()
                probe = engine.exec.call_args_list[0].kwargs['source']
                self.assertIn(f'writeFileSync({json.dumps(box.contract_module)},', probe)
                self.assertIn(f'symlinkSync({json.dumps(box.contract_module)},', probe)
                prompt = generator.generation_prompt(box)
                for selected in (type_name, export_name, box.contract_module):
                    self.assertIn(selected, prompt)
                self.assertNotIn('NormalizeContact', prompt)
                submission = MagicMock()
                submission.__enter__.return_value = (candidate, generator.digest(candidate))
                with patch.object(generator, 'SPIKE', root), patch.object(generator, 'BOX', box), \
                     patch.object(generator.sys, 'argv', ['generate.py']), \
                     patch.object(generator, 'runtime'), \
                     patch.object(generator, 'agent_submission', return_value=submission) as agent, \
                     patch.object(generator.subprocess, 'run') as verification:
                    generator.main()
                self.assertEqual(agent.call_args.args[1], {
                    'task.md': root / box.task_path,
                    f'{label}.ts': root / box.contract_path,
                })
                self.assertEqual(agent.call_args.kwargs['prompt'], prompt)
                self.assertEqual(agent.call_args.kwargs['box'], label)
                self.assertEqual(verification.call_args.args[0][2:4],
                                 ['--box-definition', box.fingerprint()])
                self.assertEqual((root / box.accepted_path).read_bytes(), candidate.read_bytes())


if __name__ == '__main__':
    unittest.main()
