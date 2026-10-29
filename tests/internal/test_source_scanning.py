"""Complete-source scan tests: actual trusted Node code, synthetic credentials only."""
from contextlib import contextmanager, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
import uuid
from unittest.mock import MagicMock, patch

from boundscript_internal import agent_workspace as workspace, source_tree as tree
from boundscript_internal.container_runtime import IMAGE, digest, runtime

ORIGINAL = 'synthetic-original-token-001'
REFRESHED = 'synthetic-refreshed-token-002'


def put(root, relative, data=b'// inert source\r\n'):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def fixture(root, files=None):
    source = root / 'source'
    for relative, data in (files or {'implementation.ts': b'// inert entry\n'}).items():
        put(source, relative, data)
    contract = put(source, 'contract.ts', b'export type Contract = () => void;\n')
    original = root / 'original.json'
    refreshed = root / 'refreshed.json'
    original.write_text(json.dumps({'nested': {'token': ORIGINAL}, 'small': 'tiny123'}))
    refreshed.write_text(json.dumps({'tokens': [None, REFRESHED]}))
    return source, (contract.stat(), digest(contract)), (original, refreshed)


def host_scan(args, source, candidate, credentials):
    """Run the exact stdin scanner with test-only paths, not a simulated verdict."""
    config = json.loads(args[-1])
    config['root'] = str(candidate)
    config['auth'] = [str(path) for path in credentials]
    command = [*args[:-1], json.dumps(config)]
    assert ORIGINAL not in repr(command) and REFRESHED not in repr(command)
    return subprocess.run(command, input=source, capture_output=True, text=True, timeout=10)


class CompleteSourceScannerTests(unittest.TestCase):
    def scan(self, candidate, proof, credentials, expected=0, prefix=''):
        engine = MagicMock()

        def execute(name, *args, source):
            self.assertEqual(args[:4], ('node', '--input-type=module', '-', args[-1]))
            config = json.loads(args[-1])
            self.assertEqual(config['root'], '/implementation')
            self.assertEqual(config['auth'], ['/run/host-auth.json', '/pi-state/auth.json'])
            self.assertEqual(config['limits'], {'files': tree.MAX_FILES, 'bytes': tree.MAX_BYTES,
                                               'depth': tree.MAX_DEPTH, 'path': tree.MAX_PATH,
                                               'entries': tree.MAX_ENTRIES})
            result = host_scan(args, prefix + source, candidate, credentials)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertEqual(result.stderr, '')
            self.assertNotIn(ORIGINAL, result.stdout)
            self.assertNotIn(REFRESHED, result.stdout)
            if expected:
                self.assertEqual(result.stdout, '')
                raise RuntimeError('Scanner rejected source; diagnostics withheld')
            self.assertRegex(result.stdout, r'^[a-f0-9]{64}\n$')
            return result.stdout.strip()

        engine.exec.side_effect = execute
        if expected:
            with self.assertRaisesRegex(RuntimeError, 'diagnostics withheld'):
                workspace.scan_source_tree(engine, 'synthetic', protected_contract=proof)
            return None
        return workspace.scan_source_tree(engine, 'synthetic', protected_contract=proof)

    def test_real_scanner_inventory_parity_and_byte_preservation(self):
        for files in ({'implementation.ts': b''},
                      {'z/last.ts': b'// last\n', 'implementation.ts': b'\xef\xbb\xbf// entry\r\n',
                       'A/empty.ts': b'', 'deep/unused.test.ts': '// Unicode \u2603\n'.encode()}):
            with self.subTest(files=list(files)), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                candidate, proof, credentials = fixture(root, files)
                scanned = self.scan(candidate, proof, credentials)
                with tree.staged_source_tree(candidate, protected_contract=proof) as (snapshot, records):
                    self.assertEqual(scanned, tree.inventory_digest(records))
                    self.assertEqual(scanned, hashlib.sha256(json.dumps(
                        sorted(records), separators=(',', ':')).encode('ascii')).hexdigest())
                    self.assertEqual(scanned, tree.inventory_digest(reversed(records)))
                    self.assertFalse((snapshot / 'contract.ts').exists())
                    for relative, data in files.items():
                        self.assertEqual((snapshot / relative).read_bytes(), data)
                self.assertFalse(snapshot.exists())
                self.assertEqual(digest(candidate / 'contract.ts'), proof[1])
                with self.assertRaisesRegex(ValueError, 'collides'):
                    with tree.staged_source_tree(candidate):
                        self.fail('Standalone staging accepted a protected-contract exception')

    def test_empty_inventory_vector_and_unicode_literal_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate, proof, credentials = fixture(Path(tmp), {'implementation.ts': b''})
            empty_sha = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
            encoded = ('[["implementation.ts",0,"' + empty_sha + '"]]').encode('ascii')
            self.assertEqual(self.scan(candidate, proof, credentials), hashlib.sha256(encoded).hexdigest())
            secret = 'synthetic-Unicode-\u2603-token'
            credentials[1].write_text(json.dumps({'nested': [{'token': secret}]}))
            put(candidate, 'implementation.ts', ('// ' + secret).encode('utf-8'))
            self.scan(candidate, proof, credentials, expected=42)

    def test_changes_during_actual_node_reads_fail_silently(self):
        for mutation in ('content', 'membership'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                candidate, proof, credentials = fixture(Path(tmp))
                action = ("injectionFS.writeFileSync(cfg.root + '/implementation.ts', '// raced');" if mutation == 'content' else
                          "injectionFS.writeFileSync(cfg.root + '/late.ts', '// added');")
                # Test-only fault injection wraps Node's real read; scanner body is unchanged.
                prefix = """import injectionFS from 'node:fs';
const actualRead = injectionFS.readSync;
let injected = false;
injectionFS.readSync = (...args) => {
  const n = actualRead(...args);
  if (n > 0 && !injected && injectionFS.readlinkSync('/proc/self/fd/' + args[0]).endsWith('/implementation.ts')) {
    injected = true;
    const cfg = JSON.parse(process.argv[2]);
    ACTION
  }
  return n;
};
""".replace('ACTION', action)
                self.scan(candidate, proof, credentials, expected=43, prefix=prefix)
                target = candidate / ('implementation.ts' if mutation == 'content' else 'late.ts')
                self.assertEqual(target.read_bytes(), b'// raced' if mutation == 'content' else b'// added')

    def test_credentials_in_every_file_and_path_are_silently_rejected(self):
        for secret in (ORIGINAL, REFRESHED):
            for placement in ('entry', 'helper', 'unused', 'filename', 'directory'):
                with self.subTest(secret_source=secret == ORIGINAL, placement=placement), tempfile.TemporaryDirectory() as tmp:
                    candidate, proof, credentials = fixture(Path(tmp))
                    if placement == 'entry':
                        put(candidate, 'implementation.ts', ('// ' + secret).encode())
                    elif placement in ('helper', 'unused'):
                        put(candidate, f'deep/{placement}.ts', ('// ' + secret).encode())
                    elif placement == 'filename':
                        put(candidate, secret + '.ts')
                    else:
                        (candidate / secret).mkdir()
                    self.scan(candidate, proof, credentials, expected=42)

    def test_current_literal_threshold_is_preserved_and_bad_auth_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate, proof, credentials = fixture(Path(tmp), {'implementation.ts': b'// tiny123'})
            self.scan(candidate, proof, credentials)
            credentials[1].write_text('PRIVATE malformed credential JSON')
            self.scan(candidate, proof, credentials, expected=43)

    def test_policy_boundaries_match_host_staging(self):
        cases = ('count-ok', 'count-over', 'bytes-ok', 'bytes-over', 'depth-ok', 'depth-over',
                 'path-ok', 'path-over', 'entries-over', 'missing-entry', 'unexpected-js',
                 'declaration', 'package', 'node-modules', 'non-utf8', 'case-collision', 'unsafe-name',
                 'newline-directory')
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                candidate, proof, credentials = fixture(Path(tmp))
                if case.startswith('count'):
                    for i in range(15 if case.endswith('ok') else 16):
                        put(candidate, f'helper-{i}.ts', b'')
                elif case.startswith('bytes'):
                    put(candidate, 'implementation.ts', b'/' * 8192)
                    put(candidate, 'helper.ts', b'/' * (8192 if case.endswith('ok') else 8193))
                elif case.startswith('depth'):
                    put(candidate, '/'.join(['nested'] * (8 if case.endswith('ok') else 9) + ['helper.ts']))
                elif case.startswith('path'):
                    put(candidate, 'a' * (237 if case.endswith('ok') else 238) + '.ts')
                elif case == 'entries-over':
                    for i in range(tree.MAX_ENTRIES):
                        (candidate / f'empty-{i}').mkdir()
                elif case == 'missing-entry':
                    (candidate / 'implementation.ts').unlink()
                elif case == 'case-collision':
                    put(candidate, 'Same/helper.ts')
                    put(candidate, 'same/other.ts')
                elif case == 'newline-directory':
                    (candidate / 'unsafe\n').mkdir()
                else:
                    name = {'unexpected-js': 'emitted.js', 'declaration': 'types.d.ts',
                            'package': 'package.json', 'node-modules': 'node_modules/x.ts',
                            'non-utf8': 'invalid.ts', 'unsafe-name': 'unsafe name.ts'}[case]
                    put(candidate, name, b'\xff' if case == 'non-utf8' else b'// inert')
                accepted = case.endswith('-ok')
                self.scan(candidate, proof, credentials, expected=0 if accepted else 43)
                if accepted:
                    with tree.staged_source_tree(candidate, protected_contract=proof):
                        pass
                else:
                    with self.assertRaises(ValueError):
                        with tree.staged_source_tree(candidate, protected_contract=proof):
                            self.fail('Host accepted scanner-rejected structure')

    def test_unsafe_objects_and_contract_changes_never_become_source(self):
        for case in ('symlink', 'broken', 'directory-link', 'hardlink', 'fifo', 'socket',
                     'root-link', 'ancestor-link', 'contract-content', 'contract-link',
                     'contract-hardlink', 'contract-missing', 'contract-case'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                candidate, proof, credentials = fixture(root)
                extra = candidate / 'extra.ts'
                contract = candidate / 'contract.ts'
                server = None
                if case in ('symlink', 'broken', 'directory-link'):
                    extra.symlink_to(candidate / ('implementation.ts' if case == 'symlink' else
                                                 'absent' if case == 'broken' else '.'), target_is_directory=case == 'directory-link')
                elif case == 'hardlink':
                    os.link(candidate / 'implementation.ts', extra)
                elif case == 'fifo':
                    os.mkfifo(extra)
                elif case == 'socket':
                    server = socket.socket(socket.AF_UNIX)
                    server.bind(str(extra))
                elif case in ('root-link', 'ancestor-link'):
                    (root / 'alias').symlink_to(candidate, target_is_directory=True)
                    if case == 'root-link':
                        candidate = root / 'alias'
                    else:
                        put(candidate, 'nested/implementation.ts')
                        put(candidate, 'nested/contract.ts', contract.read_bytes())
                        nested_contract = candidate / 'nested/contract.ts'
                        proof = (nested_contract.stat(), digest(nested_contract))
                        candidate = root / 'alias/nested'
                elif case == 'contract-content':
                    contract.write_text('// changed input')
                elif case == 'contract-link':
                    contract.unlink()
                    contract.symlink_to(credentials[0])
                elif case == 'contract-hardlink':
                    os.link(contract, root / 'contract-alias')
                elif case == 'contract-missing':
                    contract.unlink()
                else:
                    put(candidate, 'Contract.ts')
                try:
                    self.scan(candidate, proof, credentials, expected=43)
                    with self.assertRaises(ValueError):
                        with tree.staged_source_tree(candidate, protected_contract=proof):
                            self.fail('Unsafe workspace yielded')
                finally:
                    if server:
                        server.close()

    def test_contract_identity_is_checked_even_for_identical_replacement_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate, proof, credentials = fixture(Path(tmp))
            self.scan(candidate, proof, credentials)
            contract = candidate / 'contract.ts'
            contract.rename(candidate.parent / 'old-contract')
            put(candidate, 'contract.ts', b'export type Contract = () => void;\n')
            with self.assertRaisesRegex(ValueError, 'Protected contract changed'):
                with tree.staged_source_tree(candidate, protected_contract=proof):
                    self.fail('Replacement input accepted by content alone')

    def test_malformed_scan_results_are_not_valid_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, proof, _ = fixture(Path(tmp))
            for value in (None, '', 'f' * 63, 'F' * 64, 'g' * 64, 'f' * 64 + '\n', 'PRIVATE'):
                engine = MagicMock()
                engine.exec.return_value = value
                with self.subTest(value_type=type(value).__name__), self.assertRaisesRegex(RuntimeError, 'Invalid complete-source'):
                    workspace.scan_source_tree(engine, 'synthetic', protected_contract=proof)


class WorkspaceTreeBindingTests(unittest.TestCase):
    def test_scan_cleanup_snapshot_order_binding_and_legacy_mount_authority(self):
        cases = ('single', 'nested', 'scan-secret', 'scan-change', 'cleanup-change', 'add',
                 'remove', 'rename', 'contract-replace', 'protected-input', 'auth-change',
                 'bad-read', 'cleanup-failure', 'client-failure')
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                auth = root / 'auth.json'
                refreshed = root / 'refreshed.json'
                auth.write_text(json.dumps({'token': ORIGINAL}))
                refreshed.write_text(json.dumps({'token': REFRESHED}))
                task = put(root, 'task.md')
                public = put(root, 'public.ts', b'export type Contract = () => void;\n')
                pi = root / 'pi'
                put(pi, 'dist/bundle/cli.js', b'// fake; never executed')
                put(pi, 'package.json', b'{"version":"1.4.0"}')
                engine = MagicMock()
                candidate = None
                snapshot = None
                stages = []
                original_stage = tree.staged_source_tree

                @contextmanager
                def track_stage(*args, **kwargs):
                    with original_stage(*args, **kwargs) as result:
                        stages.append(result[0])
                        yield result

                yielded = False
                scanned = False

                def execute(name, *args, **kwargs):
                    nonlocal candidate, scanned
                    if '/opt/pi/dist/bundle/cli.js' in args:
                        specs = engine.create.call_args.args[2][1::2]
                        spec = next(s for s in specs if s.split('dst=')[1].split(',')[0] == '/implementation')
                        candidate = Path(spec.split('src=')[1].split(',')[0])
                        put(candidate, 'implementation.ts')
                        if case != 'single':
                            put(candidate, 'deep/helper.ts')
                        if case == 'scan-secret':
                            put(candidate, 'unused.ts', ('// ' + REFRESHED).encode())
                        return '\n'.join(json.dumps(event) for event in (
                            {'type': 'session', 'id': '00000000-0000-4000-8000-000000000046', 'cwd': '/implementation'},
                            {'type': 'tool_execution_start', 'toolName': 'write'},
                            {'type': 'tool_execution_start', 'toolName': 'read',
                             'args': {'path': '/run/host-auth.json' if case == 'bad-read' else 'deep/helper.ts'}},

                            {'type': 'message_end', 'message': {'role': 'assistant', 'stopReason': 'stop'}},
                            {'type': 'agent_settled', 'aborted': False}))
                    if args[:3] == ('node', '--input-type=module', '-'):
                        result = host_scan(args, kwargs['source'], candidate, (auth, refreshed))
                        self.assertEqual(result.stderr, '')
                        if result.returncode:
                            self.assertEqual(result.stdout, '')
                            raise RuntimeError('Scanner rejected source; diagnostics withheld')
                        scanned = True
                        if case == 'scan-change':
                            put(candidate, 'deep/helper.ts', b'// changed after scan')
                        return result.stdout.strip()
                    if 'const observed' in kwargs.get('source', ''):
                        return json.dumps(['ENOENT', 'EROFS', 'ENOENT', 'ENOENT', 'ENOENT',
                                           'EROFS', 'ENOENT', 'ENOENT', 'ERR_MODULE_NOT_FOUND'])
                    return ''

                def cleanup(name):
                    if candidate is None:
                        return
                    if case == 'cleanup-change':
                        put(candidate, 'deep/helper.ts', b'// changed during cleanup')
                    elif case == 'add':
                        put(candidate, 'extra.ts')
                    elif case == 'remove':
                        (candidate / 'deep/helper.ts').unlink()
                    elif case == 'rename':
                        (candidate / 'deep/helper.ts').rename(candidate / 'deep/renamed.ts')
                    elif case == 'contract-replace':
                        (candidate / 'contract.ts').rename(root / 'old-contract')
                        put(candidate, 'contract.ts', public.read_bytes())
                    elif case == 'protected-input':
                        (candidate.parent / 'inputs/task.md').write_text('// changed task copy')
                    elif case == 'auth-change':
                        auth.write_text('{}')
                    elif case == 'cleanup-failure':
                        raise RuntimeError('Synthetic cleanup failure')

                engine.exec.side_effect = execute
                engine.remove.side_effect = cleanup
                with patch.object(tree, 'staged_source_tree', side_effect=track_stage), \
                     redirect_stdout(io.StringIO()) as out:
                    try:
                        with workspace.agent_submission(engine, {'task.md': task}, pi=pi, auth=auth,
                                box='synthetic', filename='implementation.ts', prompt='unchanged fixture prompt',
                                model='never-invoked', thinking='low', public_contract=public,
                                source_tree=True) as (snapshot, scanned_digest):
                            yielded = True
                            self.assertIn(case, ('single', 'nested', 'client-failure'))
                            engine.remove.assert_called_once()
                            self.assertTrue(scanned)
                            self.assertNotEqual(snapshot, candidate)
                            self.assertFalse((snapshot / 'contract.ts').exists())
                            with tree.staged_source_tree(snapshot) as (_, records):
                                self.assertEqual(tree.inventory_digest(records), scanned_digest)
                            if case == 'client-failure':
                                raise OSError('Synthetic caller failure')
                    except (ValueError, RuntimeError, AssertionError, OSError):
                        if case in ('single', 'nested'):
                            raise
                self.assertEqual(yielded, case in ('single', 'nested', 'client-failure'))
                engine.remove.assert_called_once()
                if snapshot:
                    self.assertFalse(snapshot.exists())
                self.assertFalse(candidate.exists())
                self.assertTrue(all(not path.exists() for path in stages))
                for secret in (ORIGINAL, REFRESHED):
                    self.assertNotIn(secret, out.getvalue())
                specs = engine.create.call_args.args[2][1::2]
                mounts = {s.split('dst=')[1].split(',')[0]: 'readonly' in s for s in specs}
                self.assertEqual(mounts, {'/inputs/task.md': True, '/implementation': False,
                                          '/opt/pi': True, '/run/host-auth.json': True,
                                          '/implementation/contract.ts': True})
                self.assertTrue(engine.create.call_args.kwargs['generation'])
                if case != 'auth-change':
                    self.assertEqual(digest(auth), hashlib.sha256(json.dumps({'token': ORIGINAL}).encode()).hexdigest())
                if case in ('bad-read', 'scan-secret'):
                    self.assertFalse(scanned)
                if case == 'cleanup-failure':
                    self.assertFalse(stages)

    def test_own_source_read_audit_does_not_authorize_other_namespaces(self):
        for value in ('implementation.ts', 'deep/helper.ts', 'deep/../implementation.ts',
                      '/implementation', '/implementation/deep', '/implementation/contract.ts', '/inputs/task.md'):
            self.assertTrue(workspace._own_source_read(value, {'task.md': None}), value)
        for value in ('../peer/implementation.ts', '/implementation-else/file.ts', '/run/host-auth.json',
                      '/repo/package.json', '../../outside.ts', None, '', 'back\\slash.ts', 'nul\x00.ts'):
            self.assertFalse(workspace._own_source_read(value, {'task.md': None}))

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_ENGINE_TEST') == '1', 'opt-in Docker scan, synthetic credentials')
    def test_scanner_in_unchanged_generation_sandbox_without_pi(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate, proof, credentials = fixture(Path(tmp), {'implementation.ts': b'// entry\r\n',
                                                              'deep/unused.ts': b'// helper\n'})
            engine = runtime()
            engine.image(IMAGE)
            name = 'boundscript-scan-test-' + uuid.uuid4().hex[:12]
            mounts = ['--mount', f'type=bind,src={candidate},dst=/implementation',
                      '--mount', f'type=bind,src={candidate / "contract.ts"},dst=/implementation/contract.ts,readonly',
                      '--mount', f'type=bind,src={credentials[0]},dst=/run/host-auth.json,readonly']
            try:
                engine.create(name, IMAGE, mounts, os.getuid(), os.getgid(), generation=True, workdir='/implementation')
                engine.start(name, os.getuid(), os.getgid(), generation=True)
                engine.exec(name, 'sh', '-c', 'umask 077; cp /run/host-auth.json /pi-state/auth.json')
                scanned = workspace.scan_source_tree(engine, name, protected_contract=proof)
                put(candidate, 'deep/unused.ts', ('// ' + ORIGINAL).encode())
                with self.assertRaises(RuntimeError):
                    workspace.scan_source_tree(engine, name, protected_contract=proof)
                put(candidate, 'deep/unused.ts', b'// helper\n')
            finally:
                engine.remove(name)
            with tree.staged_source_tree(candidate, protected_contract=proof) as (_, records):
                self.assertEqual(tree.inventory_digest(records), scanned)
