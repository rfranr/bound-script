"""Synthetic suite ownership, selection and opt-in offline verification regressions."""
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from test_spike import HERE, generator, verifier, entrypoint
from boundscript_internal.box_definition import VerificationSuite


def synthetic_box(root, label):
    """Trusted fixtures only; no second business Box or acceptance artifact."""
    numeric = label == 'first'
    type_name, export_name = ('FirstFunction', 'firstFunction') if numeric else ('SecondFunction', 'secondFunction')
    scalar, value = ('number', 7) if numeric else ('string', 'independent fixture')
    runtime_file = 'guards.test.ts' if numeric else 'checks/shapes.spec.ts'
    acceptance_file = 'examples/basic.spec.ts' if numeric else 'behavior/deep/check.test.ts'
    property_file = 'laws/invariants.test.ts' if numeric else acceptance_file
    fixture = 'numbers.json' if numeric else 'unrelated.json'
    suites = (VerificationSuite(('runtime',), (runtime_file,)),)
    if numeric:
        suites += (VerificationSuite(('acceptance',), (acceptance_file,)),
                   VerificationSuite(('properties',), (property_file,)))
    else:
        suites += (VerificationSuite(('acceptance', 'properties'), (acceptance_file,)),)
    box = replace(generator.BOX, name=label, task_path=f'{label}-task.md',
                  contract_path=f'{label}/types/model.ts', contract_module=f'/inputs/{label}.ts',
                  function_type=type_name, implementation_export=export_name,
                  accepted_path=f'{label}-accepted.ts', verification_path=label, suites=suites,
                  verification_inputs=('types', 'data', 'generated/shapes.ts'))
    suite = root / box.verification_path

    def put(file, text):
        path = suite / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    (root / box.task_path).write_text('Synthetic identity fixture, not a business task.')
    put('types/model.ts', f'export type Input = {scalar};\nexport type Output = {scalar};\n'
        f'export type {type_name} = (value: Input) => Output;\n')
    put('validator-source/shapes.ts', "import typia from 'typia';\n"
        "import type { Input, Output } from '../types/model';\n"
        'export const assertInput = typia.createAssertEquals<Input>();\n'
        'export const assertOutput = typia.createAssertEquals<Output>();\n')
    put('generated/shapes.ts', '// Replaced by actual Typia generation in engine tests.\n')
    put(f'data/{fixture}', json.dumps({'input': value, 'expected': value}))
    put(runtime_file, "import { describe, it, expect } from 'vitest';\n"
        "import { assertInput, assertOutput } from '/checks/generated/shapes';\n"
        f"describe('{label} structural boundaries', () => {{\n"
        f"it('accepts the declared scalar', () => expect(assertInput({json.dumps(value)})).toBe({json.dumps(value)}));\n"
        "it('rejects an unrelated shape', () => expect(() => assertOutput({bad:true})).toThrow());\n});\n")
    common = "import { describe, it, expect } from 'vitest';\nimport fc from 'fast-check';\n"
    common += f"import {{ {export_name} as run }} from '/implementation/implementation.ts';\n"
    common += "import { assertInput, assertOutput } from '/checks/generated/shapes';\n"
    common += f"import fixture from '/checks/data/{fixture}';\n"
    common += 'const invoke = value => assertOutput(run(assertInput(value)));\n'
    example = (f"describe('{label} independently owned examples', () => {{\n"
               "it('uses its own data file', () => expect(invoke(fixture.input)).toBe(fixture.expected));\n});\n")
    prop = (f"describe('{label} algebraic observations', () => {{\n"
            "it('retains all generated values', () => fc.assert(fc.property("
            + ('fc.integer()' if numeric else 'fc.string()')
            + ', value => { expect(invoke(value)).toBe(value); }), {seed:33,numRuns:50}));\n});\n')
    put(acceptance_file, common + example + (prop if property_file == acceptance_file else ''))
    if property_file != acceptance_file:
        put(property_file, common + prop)
    candidate = root / 'candidate.ts'
    candidate.write_text(f'export const {export_name} = (value: {scalar}): {scalar} => value;\n')
    return box, candidate


def build_synthetic_validators(root, box):
    suite = root / box.verification_path
    project = suite / 'tsconfig.json'
    project.write_text(json.dumps({'compilerOptions': {
        'strict': True, 'target': 'ES2022', 'module': 'NodeNext', 'moduleResolution': 'NodeNext',
        'skipLibCheck': True, 'types': [],
    }}))
    subprocess.run(['node', str(HERE.parents[1] / 'node_modules/typia/lib/executable/typia.js'),
                    'generate', '--input', str(suite / 'validator-source'),
                    '--output', str(suite / 'generated'), '--project', str(project)],
                   check=True, capture_output=True, timeout=45)


class BoxDefinitionTests(unittest.TestCase):
    def test_entry_points_share_definition_and_reject_mismatch_before_verification(self):
        self.assertIs(generator.BOX, entrypoint.BOX)
        box = generator.BOX
        for field, value in (
            ('name', 'synthetic'), ('task_path', 'other-task.md'),
            ('contract_path', 'other-contract.ts'), ('contract_module', '/inputs/other.ts'),
            ('function_type', 'OtherFunction'), ('implementation_export', 'otherFunction'),
            ('accepted_path', 'other-accepted.ts'), ('verification_path', 'other-checks'),
            ('suites', (VerificationSuite(('runtime',), ('other.spec.ts',)),)),
            ('verification_inputs', ('other-data.json',)), ('optional_categories', ('properties',)),
        ):
            changed = replace(box, **{field: value})
            self.assertNotEqual(box.fingerprint(), changed.fingerprint())
            with self.subTest(field=field), patch.object(entrypoint, 'BOX', changed), \
                 patch.object(entrypoint.sys, 'argv', ['verify.py', '--box-definition', box.fingerprint(), '/unused.ts']), \
                 patch.object(entrypoint, 'check') as check:
                with self.assertRaisesRegex(verifier.VerificationFailure, 'definition mismatch'):
                    entrypoint.main()
                check.assert_not_called()
        with patch.object(entrypoint.sys, 'argv', ['verify.py', '--box-definition', box.fingerprint(), '/unused.ts']), \
             patch.object(entrypoint, 'check') as check:
            entrypoint.main()
            check.assert_called_once_with(Path('/unused.ts'))

    def test_two_definitions_select_own_inputs_checks_and_exports(self):
        for label in ('first', 'second'):
            with self.subTest(box=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                box, candidate = synthetic_box(root, label)
                suite_root = root / box.verification_path
                engine = MagicMock()
                engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5), json.dumps('ENETUNREACH')]

                def inspect_checks(*args):
                    specs = engine.create.call_args.args[2][1::2]
                    spec = next(s for s in specs if 'dst=/checks,' in s)
                    checks = Path(spec.split('src=', 1)[1].split(',')[0])
                    for file in box.verification_files(suite_root):
                        self.assertEqual((checks / file).read_bytes(), (suite_root / file).read_bytes())
                    self.assertFalse((checks / 'validator-source').exists())
                    source = (checks / 'check-contract.ts').read_text()
                    self.assertIn(f'import type {{ {box.function_type} as Contract }}', source)
                    self.assertIn(f'import {{ {box.implementation_export} as implementation }}', source)
                    self.assertIn(json.dumps(box.contract_module), source)
                    self.assertIn(f'type=bind,src={root / box.contract_path},dst={box.contract_module},readonly', specs)
                    for index, suite in enumerate(box.suites):
                        config = (checks / f'suite-{index}.config.mts').read_text()
                        self.assertIn(json.dumps(suite.files), config)
                        self.assertNotIn('testNamePattern', config)

                with patch.object(verifier, 'runtime', return_value=engine), \
                     patch.object(verifier, 'run_compiler', side_effect=inspect_checks), \
                     patch.object(verifier, 'run_vitest') as vitest:
                    verifier.check(candidate, box_root=root, box=box)
                self.assertEqual([call.args[3] for call in vitest.call_args_list], list(box.suites))
                engine.remove.assert_called_once()
                probe = engine.exec.call_args_list[0].kwargs['source']
                self.assertIn(f'writeFileSync({json.dumps(box.contract_module)},', probe)
                self.assertIn(f'writeFileSync({json.dumps("/checks/" + box.suites[0].files[0])},', probe)
                prompt = generator.generation_prompt(box)
                for selected in (box.function_type, box.implementation_export, box.contract_module):
                    self.assertIn(selected, prompt)
                self.assertNotIn('NormalizeContact', prompt)
                submission = MagicMock()
                submission.__enter__.return_value = (candidate, generator.digest(candidate))
                with patch.object(generator, 'SPIKE', root), patch.object(generator, 'BOX', box), \
                     patch.object(generator.sys, 'argv', ['generate.py']), patch.object(generator, 'runtime'), \
                     patch.object(generator, 'agent_submission', return_value=submission) as agent, \
                     patch.object(generator.subprocess, 'run') as verification:
                    generator.main()
                self.assertEqual(agent.call_args.args[1], {'task.md': root / box.task_path})
                self.assertEqual(agent.call_args.kwargs['public_contract'], root / box.contract_path)
                self.assertFalse((root / box.accepted_path).parent.joinpath('contract.ts').exists())
                self.assertEqual(agent.call_args.kwargs['prompt'], prompt)
                self.assertEqual(agent.call_args.kwargs['box'], label)
                self.assertEqual(verification.call_args.args[0][2:4], ['--box-definition', box.fingerprint()])
                self.assertEqual((root / box.accepted_path).read_bytes(), candidate.read_bytes())

    def test_missing_undeclared_duplicate_and_unsafe_tests_or_inputs_fail_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            box, candidate = synthetic_box(root, 'first')
            suite_root = root / box.verification_path
            invalid = [
                replace(box, suites=()),
                replace(box, suites=box.suites[:-1]),
                replace(box, suites=box.suites + (box.suites[0],)),
                replace(box, suites=(VerificationSuite(('runtime',), ('absent.spec.ts',)), *box.suites[1:])),
                replace(box, verification_inputs=('missing.json',)),
                replace(box, verification_inputs=('../escape.json',)),
                replace(box, suites=(VerificationSuite(('runtime',), ('*.test.ts',)), *box.suites[1:])),
                replace(box, optional_categories=('runtime',)),
                replace(box, optional_categories=('properties',)),  # Cannot both run and omit a category.
            ]
            for changed in invalid:
                with self.subTest(box=changed), patch.object(verifier, 'runtime') as runtime:
                    with self.assertRaises(verifier.VerificationFailure):
                        verifier.check(candidate, box_root=root, box=changed)
                    runtime.assert_not_called()
            extra = suite_root / 'unassigned.spec.ts'
            extra.write_text('// must not silently disappear')
            with self.assertRaises(ValueError):
                box.verification_files(suite_root)
            extra.unlink()
            target = suite_root / box.suites[0].files[0]
            target.unlink()
            target.symlink_to(candidate)
            with self.assertRaises(ValueError):
                box.verification_files(suite_root)

    def test_properties_can_only_be_absent_with_explicit_not_applicable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            box, candidate = synthetic_box(root, 'first')
            (root / box.verification_path / box.suites[-1].files[0]).unlink()
            box = replace(box, suites=box.suites[:-1])
            with self.assertRaises(ValueError):
                box.verification_files(root / box.verification_path)
            box = replace(box, optional_categories=('properties',))
            box.verification_files(root / box.verification_path)
            engine = MagicMock()
            engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 5), json.dumps('ENETUNREACH')]
            with patch.object(verifier, 'runtime', return_value=engine), \
                 patch.object(verifier, 'run_compiler'), patch.object(verifier, 'run_vitest') as vitest, \
                 redirect_stdout(io.StringIO()) as output:
                verifier.check(candidate, box_root=root, box=box)
            self.assertIn('NOT APPLICABLE fast-check properties (explicit Box declaration)', output.getvalue())
            self.assertEqual(len(vitest.call_args_list), 2)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_two_synthetic_boxes_pass_and_reject_invalid_candidates_with_real_typia_and_vitest(self):
        for label in ('first', 'second'):
            # Under the checkout solely so trusted Typia input resolves installed tooling.
            with self.subTest(box=label), tempfile.TemporaryDirectory(prefix='synthetic-suite-', dir=HERE) as tmp:
                root = Path(tmp)
                box, candidate = synthetic_box(root, label)
                build_synthetic_validators(root, box)
                with redirect_stdout(io.StringIO()) as output:
                    verifier.check(candidate, box_root=root, box=box)
                    positive = output.getvalue()
                    self.assertIn('PASS TypeScript compilation', positive)
                    self.assertIn('PASS Typia runtime validation', positive)
                    self.assertIn('Vitest acceptance tests', positive)
                    self.assertIn('fast-check properties', positive)
                    self.assertIn('uses its own data file', positive)
                    self.assertIn('retains all generated values', positive)
                    scalar = 'number' if label == 'first' else 'string'
                    for kind, value in [('compilation', 'false'), ('typia', 'false as any'),
                                        ('assertion', '999' if label == 'first' else '"BROKEN"')]:
                        candidate.write_text(f'export const {box.implementation_export} = (value: {scalar}) => {value};')
                        with self.subTest(failure=kind), self.assertRaises(verifier.VerificationFailure) as failure:
                            verifier.check(candidate, box_root=root, box=box)
                        self.assertIn(kind, failure.exception.kind)
                        if kind != 'compilation':
                            self.assertIn('uses its own data file', output.getvalue())
                            self.assertIn('FAIL Vitest acceptance tests', output.getvalue())

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline engine checks')
    def test_engine_rejects_empty_skipped_pending_and_focused_suites(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-suite-', dir=HERE) as tmp:
            root = Path(tmp)
            box, candidate = synthetic_box(root, 'first')
            build_synthetic_validators(root, box)
            test = root / box.verification_path / box.suites[0].files[0]
            original = test.read_text()
            for case, source in (
                ('empty', 'export {};'),
                ('skipped', original.replace("it('accepts", "it.skip('accepts")),
                ('pending', original.replace("it('accepts", "it.todo('accepts")),
                ('focused', original.replace("it('accepts", "it.only('accepts")),
            ):
                with self.subTest(case=case), redirect_stdout(io.StringIO()) as output:
                    test.write_text(source)
                    with self.assertRaises(verifier.VerificationFailure):
                        verifier.check(candidate, box_root=root, box=box)
                    self.assertIn('FAIL Typia runtime validation', output.getvalue())
                    self.assertIn('PASS Sandbox cleanup', output.getvalue())


if __name__ == '__main__':
    unittest.main()
