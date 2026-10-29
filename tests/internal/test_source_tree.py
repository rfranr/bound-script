"""Bounded staging and explicit source selection; no compiler, engine or model."""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from boundscript_internal import native_cli, source_tree
from experiments.native_cli import main


class SourceTreeTests(unittest.TestCase):
    def put(self, root, name='implementation.ts', data=b'// inert staging fixture\r\n'):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_private_exact_snapshot_inventory_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = {}
            for name in ('implementation.ts', 'deep/internal/helper.test.ts', 'other.ts'):
                expected[name] = self.put(root, name, b'\xef\xbb\xbf// unchanged bytes\r\n').read_bytes()
            with source_tree.staged_source_tree(root) as (snapshot, inventory):
                self.assertEqual(inventory, tuple(sorted(
                    (name, len(data), hashlib.sha256(data).hexdigest()) for name, data in expected.items())))
                self.assertEqual({p.relative_to(snapshot).as_posix() for p in snapshot.rglob('*') if p.is_file()},
                                 set(expected))
                self.assertEqual(snapshot.stat().st_mode & 0o777, 0o700)
                for name, data in expected.items():
                    self.assertEqual((snapshot / name).read_bytes(), data)
                    self.assertEqual((snapshot / name).stat().st_mode & 0o777, 0o600)
                    self.assertEqual((root / name).read_bytes(), data)
                (root / 'implementation.ts').write_bytes(b'// caller changed after staging')
                self.assertEqual((snapshot / 'implementation.ts').read_bytes(), expected['implementation.ts'])
            self.assertFalse(snapshot.exists())

    def test_file_count_and_aggregate_byte_boundaries(self):
        for count in (16, 17):
            with self.subTest(files=count), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root, data=b'')
                for i in range(count - 1):
                    self.put(root, f'helper-{i}.ts', b'')
                if count == 16:
                    with source_tree.staged_source_tree(root) as (_, inventory):
                        self.assertEqual(len(inventory), count)
                else:
                    with self.assertRaisesRegex(ValueError, 'file count'):
                        with source_tree.staged_source_tree(root):
                            self.fail('Oversized file set yielded')
        for size in (16384, 16385):
            with self.subTest(bytes=size), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root, data=b'/' * 8192)
                self.put(root, 'helper.ts', b'/' * (size - 8192))
                if size == 16384:
                    with source_tree.staged_source_tree(root) as (_, inventory):
                        self.assertEqual(sum(item[1] for item in inventory), size)
                else:
                    with self.assertRaisesRegex(ValueError, 'aggregate size'):
                        with source_tree.staged_source_tree(root):
                            self.fail('Oversized bytes yielded')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root, data=b'/' * 16385)
            with self.assertRaisesRegex(ValueError, 'aggregate size'):
                with source_tree.staged_source_tree(root):
                    self.fail('Oversized single file yielded')

    def test_depth_path_and_traversal_entry_bounds(self):
        for depth in (8, 9):
            with self.subTest(depth=depth), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root)
                self.put(root, '/'.join(['nested'] * depth + ['helper.ts']))
                if depth == 8:
                    with source_tree.staged_source_tree(root):
                        pass
                else:
                    with self.assertRaisesRegex(ValueError, 'depth'):
                        with source_tree.staged_source_tree(root):
                            self.fail('Excessive depth yielded')
        for length in (240, 241):
            with self.subTest(path_bytes=length), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root)
                self.put(root, 'a' * (length - 3) + '.ts')
                if length == 240:
                    with source_tree.staged_source_tree(root):
                        pass
                else:
                    with self.assertRaisesRegex(ValueError, 'source path'):
                        with source_tree.staged_source_tree(root):
                            self.fail('Excessive path yielded')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root)
            for i in range(source_tree.MAX_ENTRIES):
                (root / f'empty-{i}').mkdir()
            with self.assertRaisesRegex(ValueError, 'too many entries'):
                with source_tree.staged_source_tree(root):
                    self.fail('Unbounded empty directories yielded')

    def test_rejects_unexpected_reserved_ambiguous_and_non_utf8_files(self):
        names = ('contract.ts', 'Contract.ts', 'package.json', 'tsconfig.json', 'output.js',
                 'output.js.map', 'types.d.ts', 'node_modules/helper.ts', '.git/helper.ts',
                 'white space.ts', 'back\\slash.ts', 'unicodé.ts')
        for name in names:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.put(root)
                self.put(root, name)
                with self.assertRaises(ValueError):
                    with source_tree.staged_source_tree(root):
                        self.fail('Unsafe source yielded')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root)
            self.put(root, 'Same/helper.ts')
            self.put(root, 'same/other.ts')
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                with source_tree.staged_source_tree(root):
                    self.fail('Case-colliding directories yielded')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root, data=b'\xff')
            with self.assertRaisesRegex(ValueError, 'UTF-8'):
                with source_tree.staged_source_tree(root):
                    self.fail('Invalid encoding yielded')

    def test_rejects_missing_entry_file_roots_and_symlink_ancestors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for candidate in (root, root / 'absent'):
                with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                    with source_tree.staged_source_tree(candidate):
                        self.fail('Invalid root yielded')
            file = self.put(root)
            with self.assertRaises(ValueError):
                with source_tree.staged_source_tree(file):
                    self.fail('File treated as tree')
            real = root / 'real'
            self.put(real)
            (root / 'link').symlink_to(real, target_is_directory=True)
            (real / 'nested').mkdir()
            self.put(real / 'nested')
            for candidate in (root / 'link', root / 'link/nested'):
                with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                    with source_tree.staged_source_tree(candidate):
                        self.fail('Symlink root/ancestor followed')

    def test_rejects_links_fifo_socket_and_filesystem_crossing(self):
        for kind in ('symlink', 'broken-link', 'directory-link', 'hardlink', 'fifo', 'socket', 'device'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                entry = self.put(root)
                extra = root / 'extra.ts'
                server = None
                if kind == 'symlink':
                    extra.symlink_to(entry)
                elif kind == 'broken-link':
                    extra.symlink_to(root / 'absent')
                elif kind == 'directory-link':
                    extra.symlink_to(root, target_is_directory=True)
                elif kind == 'hardlink':
                    os.link(entry, extra)
                elif kind == 'fifo':
                    os.mkfifo(extra)
                elif kind == 'socket':
                    server = socket.socket(socket.AF_UNIX)
                    server.bind(str(extra))
                try:
                    if kind == 'device':
                        original = source_tree.os.stat

                        def different_device(*args, **kwargs):
                            info = original(*args, **kwargs)
                            if kwargs.get('dir_fd') is not None:
                                altered = list(info)
                                altered[2] += 1  # st_dev
                                return os.stat_result(altered)
                            return info
                        with patch.object(source_tree.os, 'stat', side_effect=different_device), \
                             self.assertRaisesRegex(ValueError, 'filesystem boundary'):
                            with source_tree.staged_source_tree(root):
                                self.fail('Different device yielded')
                    else:
                        with self.assertRaises(ValueError):
                            with source_tree.staged_source_tree(root):
                                self.fail('Unsafe object yielded')
                finally:
                    if server:
                        server.close()

    def test_detects_membership_content_and_root_substitution(self):
        for change in ('content', 'add', 'remove', 'root', 'snapshot'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'candidate'
                self.put(root)
                self.put(root, 'helper.ts')
                original = source_tree._inventory

                def mutate(fd, destination=None):
                    result = original(fd, destination)
                    if destination is not None:
                        if change == 'content':
                            (root / 'helper.ts').write_bytes(b'// changed')
                        elif change == 'add':
                            self.put(root, 'added.ts')
                        elif change == 'remove':
                            (root / 'helper.ts').unlink()
                        elif change == 'root':
                            root.rename(root.with_name('old'))
                            self.put(root)
                            self.put(root, 'helper.ts')
                        else:
                            (destination / 'helper.ts').write_bytes(b'// changed snapshot')
                    return result
                with patch.object(source_tree, '_inventory', side_effect=mutate), self.assertRaises(ValueError):
                    with source_tree.staged_source_tree(root):
                        self.fail('Changed source yielded')

    def test_detects_mutation_during_read_and_cleans_partial_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = self.put(root)
            original_open = source_tree.os.fdopen
            original_temp = source_tree.tempfile.TemporaryDirectory
            staging = []

            @contextmanager
            def altered_stream(*args, **kwargs):
                with original_open(*args, **kwargs) as stream:
                    proxy = MagicMock(wraps=stream)

                    def read(*args):
                        data = stream.read(*args)
                        entry.write_bytes(b'// changed during read')
                        return data
                    proxy.read.side_effect = read
                    yield proxy

            def track_temp(*args, **kwargs):
                directory = original_temp(*args, **kwargs)
                staging.append(Path(directory.name))
                return directory

            with patch.object(source_tree.os, 'fdopen', side_effect=altered_stream), \
                 patch.object(source_tree.tempfile, 'TemporaryDirectory', side_effect=track_temp), \
                 self.assertRaisesRegex(ValueError, 'changed during staging'):
                with source_tree.staged_source_tree(root):
                    self.fail('Changing read yielded')
            self.assertTrue(staging)
            self.assertTrue(all(not path.exists() for path in staging))

    def test_rejects_symlink_substitution_between_stat_and_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'candidate'
            self.put(root)
            helper = self.put(root, 'helper.ts')
            outside = self.put(Path(tmp), 'outside.ts', b'// outside source boundary')
            original = source_tree.os.open

            def substitute(path, flags, *args, **kwargs):
                if path == 'helper.ts' and kwargs.get('dir_fd') is not None:
                    helper.unlink()
                    helper.symlink_to(outside)
                return original(path, flags, *args, **kwargs)

            with patch.object(source_tree.os, 'open', side_effect=substitute), self.assertRaises(ValueError):
                with source_tree.staged_source_tree(root):
                    self.fail('Substituted symlink followed')
            self.assertEqual(outside.read_bytes(), b'// outside source boundary')

    def test_client_exception_propagates_and_snapshot_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root)
            error = OSError('caller failure')
            with self.assertRaises(OSError) as raised:
                with source_tree.staged_source_tree(root) as (snapshot, _):
                    raise error
            self.assertIs(raised.exception, error)
            self.assertFalse(snapshot.exists())

    def test_cli_explicit_tree_selects_shared_verifier_and_preserves_file_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.put(root)
            for selection in ('normalize-contact', 'render-welcome'):
                with self.subTest(box=selection), patch.object(native_cli, 'check') as check:
                    self.assertEqual(main(['verify', selection, '--source-tree', str(root)]), 0)
                    self.assertEqual(check.call_args.args, (root,))
                    self.assertIs(check.call_args.kwargs['source_tree'], True)
            with patch.object(native_cli, 'check') as check:
                for args in (['--source-tree'], ['--source-tree', '--baseline'], ['--source-tree', str(root), 'extra']):
                    with self.subTest(args=args), self.assertRaises(native_cli.VerificationFailure):
                        native_cli.verify(args, box_root=root, box=MagicMock())
                with self.assertRaisesRegex(native_cli.VerificationFailure, 'definition mismatch'):
                    native_cli.verify(['--box-definition', 'wrong', '--source-tree', str(root)],
                                      box_root=root, box=MagicMock())
                check.assert_not_called()
                box = MagicMock()
                box.fingerprint.return_value = 'known'
                native_cli.verify(['--box-definition', 'known', '--source-tree', str(root)],
                                  box_root=root, box=box)
                check.assert_called_once_with(root, box_root=root, box=box, source_tree=True)
                check.reset_mock()
                native_cli.verify([str(root / 'implementation.ts')], box_root=root, box=box)
                check.assert_called_once_with(root / 'implementation.ts', box_root=root, box=box)
