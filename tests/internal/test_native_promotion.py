"""Credential-free promotion regressions; independent engine check is opt-in."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from boundscript_internal import native_promotion as promotion
from boundscript_internal import source_tree as tree
from test_tree_verification import tree_fixture
from test_native_box_definition import build_synthetic_validators
from test_native_workflow import HERE


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='promotion-fixture-', dir=HERE.parents[1] / 'tests')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.box, source = tree_fixture(self.root)
        self.identifier = 'a' * 32
        self.directory = self.root / 'candidates' / self.identifier
        self.directory.mkdir(parents=True)
        source.rename(self.directory / 'source')
        self.review()

    def review(self, **changes):
        with tree.staged_source_tree(self.directory / 'source') as (_, records):
            metadata = dict(box=self.box.name, candidate_id=self.identifier,
                            source_inventory_digest=tree.inventory_digest(records),
                            source_file_count=len(records), verification_result='PASS',
                            model='synthetic', reasoning='unknown')
        metadata.update(changes)
        (self.directory / 'review.json').write_text(json.dumps(metadata))

    def promote(self):
        return promotion.promote(box_root=self.root, box=self.box, candidate_id=self.identifier)

    def snapshot(self):
        return {str(p.relative_to(self.directory)): p.read_bytes()
                for p in self.directory.rglob('*') if p.is_file()}

    def test_cli_explicit_selection_does_not_generate(self):
        from experiments import native_cli
        with patch.object(native_cli, 'select_box', return_value=(self.root, self.box, None)), \
             patch.object(promotion.native_verifier, 'check'), \
             patch.object(native_cli.native_generator, 'cli') as generate, redirect_stdout(io.StringIO()):
            self.assertEqual(native_cli.main(['promote', 'explicit-box', '--candidate', self.identifier]), 0)
        generate.assert_not_called()
        self.assertTrue((self.root / 'versions/0001/manifest.json').exists())

    def test_single_and_multifile_exact_preservation_and_sequence(self):
        for single in (False, True):
            with self.subTest(single=single):
                if single:
                    (self.directory / 'source/deep/helper.ts').unlink()
                    (self.directory / 'source/deep').rmdir()
                    (self.directory / 'source/unused.test.ts').unlink()
                    (self.directory / 'source/implementation.ts').write_bytes(b'// synthetic\r\n')
                    self.review()
                before = self.snapshot()
                with patch.object(promotion.native_verifier, 'check') as verify:
                    version = self.promote()
                verify.assert_called_once()
                self.assertEqual(version, '0002' if single else '0001')
                self.assertEqual(before, self.snapshot())
                destination = self.root / 'versions' / version
                for name, data in before.items():
                    if name.startswith('source/'):
                        self.assertEqual((destination / name).read_bytes(), data)
                manifest = json.loads((destination / 'manifest.json').read_text())
                self.assertEqual(manifest['box_definition_fingerprint'], self.box.fingerprint())
                self.assertEqual(set(manifest['verification_inputs']), set(promotion.inputs(self.root, self.box)))

    def test_invalid_metadata_and_modified_source(self):
        for change in ({'verification_result': 'FAIL'}, {'box': 'other'},
                       {'candidate_id': 'b' * 32}, {'source_file_count': True},
                       {'source_inventory_digest': 'bad'}, {'extra': 1}):
            with self.subTest(change=change):
                self.review(**change)
                with patch.object(promotion.native_verifier, 'check') as verify, self.assertRaises(ValueError):
                    self.promote()
                verify.assert_not_called()
        self.review()
        (self.directory / 'source/unused.test.ts').write_text('// modified')
        with self.assertRaises(ValueError):
            self.promote()
        self.assertFalse((self.root / 'versions').exists())

    def test_malformed_unexpected_and_unsafe(self):
        review = self.directory / 'review.json'
        saved = review.read_bytes()
        for data in (b'[]', b'{', b'{"box":1,"box":2}'):
            review.write_bytes(data)
            with self.assertRaises(ValueError):
                self.promote()
        review.write_bytes(saved)
        extra = self.directory / 'extra'
        extra.touch()
        with self.assertRaises(ValueError):
            self.promote()
        extra.unlink()
        helper = self.directory / 'source/deep/helper.ts'
        helper.unlink()
        helper.symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            self.promote()
        with self.assertRaises(ValueError):
            promotion.promote(box_root=self.root, box=self.box, candidate_id='../escape')

    def test_reverification_and_integrity_fail_closed(self):
        targets = [self.root / self.box.contract_path, self.root / self.box.task_path,
                   self.root / self.box.verification_path / self.box.suites[0].files[0],
                   self.directory / 'source/deep/helper.ts', self.directory / 'review.json']
        for target in targets:
            before = target.read_bytes()
            def mutate(*args, **kwargs):
                target.write_bytes(before + b'\n ')
            with self.subTest(target=target), patch.object(promotion.native_verifier, 'check', side_effect=mutate):
                with self.assertRaises(ValueError):
                    self.promote()
            target.write_bytes(before)
            self.assertFalse((self.root / 'versions').exists())
        with patch.object(promotion.native_verifier, 'check', side_effect=RuntimeError('reject')):
            with self.assertRaises(RuntimeError):
                self.promote()

    def test_frozen_inputs_source_and_suite_inventory_changes(self):
        def frozen_contract(source, *, box_root, box, **kwargs):
            (box_root / box.contract_path).write_text('// changed snapshot')
        def frozen_source(source, **kwargs):
            (source / 'implementation.ts').write_text('// changed snapshot')
        def new_suite(*args, **kwargs):
            (self.root / self.box.verification_path / 'new.test.ts').write_text('// undeclared')
        for mutate in (frozen_contract, frozen_source, new_suite):
            with self.subTest(mutate=mutate.__name__), patch.object(promotion.native_verifier, 'check', side_effect=mutate):
                with self.assertRaises(ValueError):
                    self.promote()
            self.assertFalse((self.root / 'versions').exists())

    def test_missing_files_and_symlinked_containers(self):
        helper = self.directory / 'source/deep/helper.ts'
        helper.unlink()
        with self.assertRaises(ValueError):
            self.promote()
        self.review()
        with tempfile.TemporaryDirectory() as tmp:
            (self.root / 'versions').symlink_to(tmp, target_is_directory=True)
            with patch.object(promotion.native_verifier, 'check'), self.assertRaises(OSError):
                self.promote()
            self.assertEqual(os.listdir(tmp), [])
        review = self.directory / 'review.json'
        review.unlink()
        review.symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            self.promote()

    def test_failed_publication_cleanup_no_overwrite_and_symlink(self):
        with patch.object(promotion.native_verifier, 'check'):
            self.promote()
            first = (self.root / 'versions/0001/manifest.json').read_bytes()
            with patch.object(promotion, 'publish_noreplace', side_effect=OSError('failure')):
                with self.assertRaises(OSError):
                    self.promote()
            self.assertEqual(os.listdir(self.root / 'versions'), ['0001'])
            self.assertEqual((self.root / 'versions/0001/manifest.json').read_bytes(), first)
            (self.root / 'versions/0002').symlink_to(self.directory, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.promote()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pending').mkdir()
            (root / '0001').mkdir()
            fd = tree._open_directory(root)
            try:
                with self.assertRaises(OSError):
                    promotion.publish_noreplace(fd, 'pending', '0001')
            finally:
                os.close(fd)
            self.assertTrue((root / 'pending').exists())

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_NATIVE_ENGINE_TEST') == '1', 'opt-in Docker promotion')
    def test_docker_independent_promotion(self):
        build_synthetic_validators(self.root, self.box)
        before = self.snapshot()
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(self.promote(), '0001')
        self.assertIn('PASS Protected input integrity', output.getvalue())
        self.assertEqual(before, self.snapshot())


if __name__ == '__main__':
    unittest.main()
