"""Shared verifier/import-closure regressions; synthetic identity, not business A/B."""
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

from boundscript_internal import native_verifier as verifier
from test_native_box_definition import synthetic_box, build_synthetic_validators
from test_native_workflow import HERE

ROOT = HERE.parents[1]


def tree_fixture(root):
    box, _ = synthetic_box(root, 'first')
    box = replace(box, contract_module='/implementation/contract.ts')
    candidate = root / 'source'
    (candidate / 'deep').mkdir(parents=True)
    (candidate / 'implementation.ts').write_text(
        "import type { FirstFunction } from './contract';\n"
        "import { identity } from './deep/helper';\n"
        'export const firstFunction: FirstFunction = identity;\n')
    (candidate / 'deep/helper.ts').write_text('export const identity = (value: number) => value;\n')
    (candidate / 'unused.test.ts').write_text('export const unused = 1;\n')
    return box, candidate


class ImportClosureTests(unittest.TestCase):
    def compile(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'
            source.mkdir()
            (root / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
            (root / 'escape.ts').write_text('export const escaped = 1;')
            (source / 'contract.ts').write_text('export type Contract = (value: number) => number;')
            for file, content in files.items():
                path = source / file
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content.replace('__SOURCE__', str(source)))
            (root / 'check-contract.ts').write_text(
                f'import type {{ Contract }} from {json.dumps(str(source / "contract.ts"))};\n'
                f'import {{ run }} from {json.dumps(str(source / "implementation.ts"))};\n'
                'const check: Contract = run;\n')
            adapter = (verifier.RUNNER / 'compiler-diagnostics.mjs').read_text()
            adapter = adapter.replace('/node_modules', str(ROOT / 'node_modules'))
            adapter = adapter.replace('/checks/', str(root) + '/').replace('/verification-work/', str(root) + '/')
            compiler = root / 'compiler.mjs'
            compiler.write_text(adapter)
            result = subprocess.run(['node', str(compiler), str(source / 'contract.ts'),
                                     *[str(source / file) for file in files]],
                                    capture_output=True, text=True, timeout=30)
            report = json.loads((root / 'typescript-diagnostics.json').read_text())
            self.assertEqual(result.returncode, int(report['errorCount'] > 0), result.stderr)
            return report

    def test_supported_internal_import_export_and_contract_forms(self):
        entry = "import type { Contract } from './contract';\nimport { identity } from './deep/helper';\nexport const run: Contract = identity;\n"
        for extra in ("export type Shape = import('./deep/helper').Shape;",
                      "export type { Contract } from './contract';",
                      "import { type Contract as Other } from './contract';",
                      "import type ContractAlias = require('./contract');",
                      "export { identity } from './deep/helper';",
                      "export const later = () => import('./deep/helper.ts');",
                      "declare function require(id: string): unknown; export const loaded = require('./deep/helper.ts');"):
            with self.subTest(form=extra):
                report = self.compile({'implementation.ts': entry + extra,
                                       'deep/helper.ts': "export { identity } from '../internal';\nexport type Shape = number;",
                                       'internal.ts': 'export const identity = (value: number) => value;'})
                self.assertEqual(report['errorCount'], 0, report)

    def test_rejects_forbidden_and_unresolved_edges_even_in_unused_helpers(self):
        for bad in ("import fs from 'node:fs';", "import fc from 'fast-check';",
                    "export { escaped } from '../escape';", "import '../escape.ts';",
                    "export const later = () => import('../escape.ts');",
                    "const where = './implementation'; export const loaded = import(where);",
                    "const where = './implementation'; export const loaded = require(where);",
                    "export type Shape = import('node:fs').PathLike;",
                    "import './missing';", "import './internal.js';",
                    "import '/implementation/implementation.ts';",
                    "import { Contract } from './contract'; export type Used = Contract;",
                    '/// <reference path="../escape.ts" />\nexport {};',
                    '/// <reference types="node" />\nexport {};',
                    '/// <reference path="__SOURCE__/internal.ts" />\nexport {};',
                    '/// <reference lib="esnext" />\nexport {};',
                    "// @ts-ignore\nimport 'node:fs';"):
            with self.subTest(source=bad):
                report = self.compile({'implementation.ts': 'export const run = (value: number) => value;',
                                       'unused.ts': bad, 'internal.ts': 'export const internal = 1;'})
                self.assertGreater(report['errorCount'], 0)
                self.assertIn(95001, [item['code'] for item in report['diagnostics']], report)

    def test_relative_internal_reference_is_supported(self):
        report = self.compile({'implementation.ts': '/// <reference path="internal.ts" />\n'
                               'export const run = (value: number) => value;',
                               'internal.ts': 'export const internal = 1;'})
        self.assertEqual(report['errorCount'], 0, report)

    def test_unused_helpers_are_strictly_typechecked(self):
        report = self.compile({'implementation.ts': 'export const run = (value: number) => value;',
                               'unused.ts': 'export const wrong: number = "not a number";'})
        self.assertIn(2322, [item['code'] for item in report['diagnostics']], report)

    def test_helper_diagnostics_are_inventory_bound_and_sanitized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'typescript-diagnostics.json').write_text(json.dumps({
                'complete': True, 'errorCount': 2, 'diagnostics': [
                    {'code': 2322, 'file': '/implementation/deep/helper.ts', 'line': 1, 'column': 2, 'message': 'Mismatch'},
                    {'code': 2322, 'file': '/implementation/unknown.ts', 'message': 'Mismatch'}]}))
            with patch.object(verifier, 'process_status', return_value={'exitStatus': 1}), \
                 redirect_stdout(io.StringIO()) as out, self.assertRaises(verifier.VerificationFailure):
                verifier.run_compiler(MagicMock(), 'fixed', root,
                                      ('/implementation/implementation.ts', '/implementation/deep/helper.ts'))
            self.assertIn('/implementation/deep/helper.ts:1:2', out.getvalue())
            self.assertNotIn('/implementation/unknown.ts', out.getvalue())
            self.assertIn('[tooling/other source]', out.getvalue())


class SharedTreeVerificationTests(unittest.TestCase):
    def engine(self):
        engine = MagicMock()
        engine.exec.side_effect = [json.dumps(['ENOENT'] * 3 + ['EROFS'] * 7), json.dumps('ENETUNREACH')]
        return engine

    def views(self, engine):
        specs = engine.create.call_args.args[2][1::2]
        return {spec.split('dst=')[1].split(',')[0]: Path(spec.split('src=')[1].split(',')[0]) for spec in specs}

    def test_one_engine_read_only_sources_separate_work_and_exact_suites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            box, candidate = tree_fixture(root)
            before = {p: p.read_bytes() for p in candidate.rglob('*.ts')}
            engine = self.engine()
            staged = []

            def inspect(_engine, _name, work, sources, contract):
                views = self.views(engine)
                source = views['/implementation']
                staged.append(source)
                self.assertEqual(work, views['/verification-work'])
                self.assertEqual(set(sources), {'/implementation/' + p.relative_to(candidate).as_posix() for p in before})
                self.assertEqual(contract, box.contract_module)
                for p, data in before.items():
                    self.assertEqual((source / p.relative_to(candidate)).read_bytes(), data)
                self.assertEqual((source / 'contract.ts').read_bytes(), (root / box.contract_path).read_bytes())
                (work / 'typescript-diagnostics.json').write_text('{}')
                self.assertFalse((source / 'typescript-diagnostics.json').exists())
                # External producer edits do not change the staged/verified view.
                (candidate / 'deep/helper.ts').write_text('// changed original after snapshot')

            with patch.object(verifier, 'runtime', return_value=engine), \
                 patch.object(verifier, 'run_compiler', side_effect=inspect), \
                 patch.object(verifier, 'run_vitest') as tests, redirect_stdout(io.StringIO()):
                verifier.check(candidate, box_root=root, box=box, source_tree=True)
            self.assertEqual([call.args[3] for call in tests.call_args_list], list(box.suites))
            specs = engine.create.call_args.args[2][1::2]
            self.assertEqual(sum('readonly' not in spec for spec in specs), 1)
            self.assertIn('dst=/verification-work', specs[0])
            self.assertTrue(all('readonly' in spec for spec in specs[1:]))
            engine.remove.assert_called_once()
            self.assertTrue(staged)
            self.assertTrue(all(not p.exists() for p in staged))

    def test_changed_source_view_membership_or_contract_fails_and_cleans_up(self):
        for mutation in ('content', 'add', 'remove', 'symlink', 'contract'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                box, candidate = tree_fixture(root)
                engine = self.engine()
                staged = []

                def tamper(*args):
                    source = self.views(engine)['/implementation']
                    staged.append(source)
                    helper = source / 'deep/helper.ts'
                    if mutation == 'content':
                        helper.write_text('// changed')
                    elif mutation == 'add':
                        (source / 'unexpected.ts').write_text('// unexpected')
                    elif mutation == 'remove':
                        helper.unlink()
                    elif mutation == 'symlink':
                        helper.unlink()
                        helper.symlink_to(candidate / 'deep/helper.ts')
                    else:
                        (root / box.contract_path).write_text('// changed consumer input')

                with patch.object(verifier, 'runtime', return_value=engine), \
                     patch.object(verifier, 'run_compiler', side_effect=tamper), \
                     patch.object(verifier, 'run_vitest'), redirect_stdout(io.StringIO()), \
                     self.assertRaises(verifier.VerificationFailure) as error:
                    verifier.check(candidate, box_root=root, box=box, source_tree=True)
                self.assertEqual(error.exception.kind, 'security/integrity')
                engine.remove.assert_called_once()
                self.assertTrue(all(not p.exists() for p in staged))

    def test_invalid_or_overlapping_tree_never_starts_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            box, candidate = tree_fixture(root)
            with patch.object(verifier, 'runtime') as runtime, redirect_stdout(io.StringIO()):
                for selected in (root / 'absent', root / box.verification_path):
                    with self.subTest(selected=selected), self.assertRaises(verifier.VerificationFailure):
                        verifier.check(selected, box_root=root, box=box, source_tree=True)
                (candidate / 'contract.ts').write_text('// not consumer owned')
                with self.assertRaises(verifier.VerificationFailure):
                    verifier.check(candidate, box_root=root, box=box, source_tree=True)
                runtime.assert_not_called()

    def test_compiler_failure_cleans_tree_snapshot_and_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            box, candidate = tree_fixture(root)
            engine = self.engine()
            views = []

            def fail(*args):
                views.append(self.views(engine)['/implementation'])
                raise verifier.VerificationFailure('compilation', 'Synthetic compiler rejection')

            with patch.object(verifier, 'runtime', return_value=engine), \
                 patch.object(verifier, 'run_compiler', side_effect=fail), \
                 patch.object(verifier, 'run_vitest') as tests, redirect_stdout(io.StringIO()), \
                 self.assertRaises(verifier.VerificationFailure):
                verifier.check(candidate, box_root=root, box=box, source_tree=True)
            tests.assert_not_called()
            engine.remove.assert_called_once()
            self.assertTrue(all(not p.exists() for p in views))

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in offline synthetic engine check')
    def test_synthetic_tree_real_compiler_and_unchanged_suites(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-tree-', dir=HERE) as tmp:
            root = Path(tmp)
            box, candidate = tree_fixture(root)
            build_synthetic_validators(root, box)
            protected = {p: p.read_bytes() for p in candidate.rglob('*.ts')}
            with redirect_stdout(io.StringIO()) as out:
                verifier.check(candidate, box_root=root, box=box, source_tree=True)
            for label in ('PASS TypeScript compilation', 'PASS Typia runtime validation',
                          'PASS Vitest acceptance tests', 'PASS fast-check properties', 'PASS Protected input integrity'):
                self.assertIn(label, out.getvalue())
            for p, data in protected.items():
                self.assertEqual(p.read_bytes(), data)
            for file, content, kind in (
                ('unused.test.ts', "import 'node:fs'; export const unused = 1;", 'compilation'),
                ('implementation.ts', 'export const wrongExport = (value: number) => value;', 'compilation'),
                ('deep/helper.ts', 'export const identity = (value: string) => value;', 'compilation'),
                ('deep/helper.ts', 'export const identity = (value: number) => value + 1;', 'assertion'),
            ):
                for path, data in protected.items():
                    path.write_bytes(data)
                (candidate / file).write_text(content)
                with self.subTest(kind=kind, file=file), redirect_stdout(io.StringIO()) as out, \
                     self.assertRaises(verifier.VerificationFailure) as error:
                    verifier.check(candidate, box_root=root, box=box, source_tree=True)
                self.assertIn(kind, error.exception.kind)
                if kind == 'compilation':
                    self.assertNotIn('[RUN VITEST]', out.getvalue())
                else:
                    self.assertIn('FAIL Vitest acceptance tests', out.getvalue())
