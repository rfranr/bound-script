"""Credential-free adapter checks: python3 -m unittest discover -s experiments/minimal-box."""
import copy
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import container_runtime as cr


def evidence(generation=False):
    return dict(uid=1000, gid=1000,
                status=dict(NoNewPrivs='1', **{k: '00000000' for k in
                            ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb')}),
                mounts=[dict(path='/', options=['ro'])],
                memory=str((512 if generation else 256) * 1024 * 1024),
                swap='0', cpu='100000 100000', pids='64' if generation else '32',
                tmpfs=dict(uid=1000, gid=1000, mode=0o700,
                           mount=dict(type='tmpfs', options=['rw', 'nosuid', 'nodev', 'noexec'],
                                      super=['size=65536k'])))


def config(provider, generation=False):
    env = ['PATH=/usr/bin', 'HOME=/pi-state' if generation else 'HOME=/implementation']
    if generation:
        env += ['PI_CODING_AGENT_DIR=/pi-state', 'PI_OFFLINE=1', 'PI_TELEMETRY=0',
                'PI_SKIP_VERSION_CHECK=1']
    if provider is cr.Podman:
        env += ['container=podman']
    return {'HostConfig': {'NetworkMode': 'bridge' if generation else 'none',
                           'ReadonlyRootfs': True, 'Privileged': False,
                           'CapDrop': ['CAP_CHOWN', 'CAP_NET_RAW'] if provider is cr.Podman else ['ALL']},
            'Config': {'User': '1000:1000', 'Env': env},
            'Mounts': [{'Type': 'bind', 'Source': '/tmp/input', 'Destination': '/inputs/task.md', 'RW': False}]}


class RuntimeTests(unittest.TestCase):
    def test_selection(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsInstance(cr.runtime(), cr.Docker)
            for name, cls in [('docker', cr.Docker), ('podman', cr.Podman)]:
                os.environ['BOUNDSCRIPT_RUNTIME'] = name
                self.assertIs(type(cr.runtime()), cls)
            for name in ('', 'unknown', 'Docker', 'docker --privileged'):
                os.environ['BOUNDSCRIPT_RUNTIME'] = name
                with self.assertRaises(ValueError):
                    cr.runtime()

    def create(self, engine, generation=False):
        engine.create('box', 'image', ['--mount', 'type=bind,src=/tmp/input,dst=/inputs/task.md,readonly'],
                      1000, 1000, generation=generation)

    def test_both_adapters_and_tmpfs_syntax(self):
        for cls in (cr.Docker, cr.Podman):
            for generation in (False, True):
                with self.subTest(provider=cls, generation=generation):
                    cfg = config(cls, generation)
                    data = evidence(generation)
                    data['mounts'].append(dict(path='/inputs/task.md', options=['ro']))
                    def reply(*args, **kwargs):
                        if args[1] == 'inspect':
                            return json.dumps([cfg])
                        if args[1] == 'exec':
                            return json.dumps(data)
                        return ''
                    with patch.object(cr, 'command', side_effect=reply) as call:
                        engine = cls()
                        self.create(engine, generation)
                        engine.start('box', 1000, 1000, generation=generation)
                        engine.remove('box')
                        create_args = call.call_args_list[0].args
                        self.assertEqual(create_args[0], cls.executable)
                        if generation:
                            flag = '--mount' if cls is cr.Podman else '--tmpfs'
                            spec = create_args[create_args.index(flag) + 1]
                            self.assertIn('U=true' if cls is cr.Podman else 'uid=1000,gid=1000', spec)
                        self.assertEqual(call.call_args.args, (cls.executable, 'rm', '-f', 'box'))

    def test_inspection_rejects_unsafe_or_unexpected_configuration(self):
        for cls in (cr.Docker, cr.Podman):
            mutations = [
                lambda c: c['HostConfig'].update(NetworkMode='host'),
                lambda c: c['HostConfig'].update(ReadonlyRootfs=False),
                lambda c: c['HostConfig'].update(Privileged=True),
                lambda c: c['Config'].update(User='0:0'),
                lambda c: c['Config']['Env'].append('TOKEN=secret'),
                lambda c: c['Config']['Env'].append('HOME=/root'),
                lambda c: c['Mounts'][0].update(RW=True),
                lambda c: c['Mounts'][0].update(Source='/etc/shadow'),
                lambda c: c['Mounts'].append(c['Mounts'][0].copy()),
                lambda c: c['Mounts'].clear(),
            ]
            for mutate in mutations:
                cfg = config(cls)
                mutate(cfg)
                with self.subTest(provider=cls, mutation=mutate), patch.object(cr, 'command'), \
                        patch.object(cls, 'inspect', return_value=cfg):
                    with self.assertRaises(AssertionError):
                        self.create(cls())

    def test_effective_policy_fails_closed(self):
        changes = [('uid', 0), ('gid', 0), ('memory', 'max'), ('memory', '1'),
                   ('swap', 'max'), ('swap', '1'), ('cpu', 'max 100000'),
                   ('cpu', '200000 100000'), ('pids', 'max'), ('pids', '65')]
        for generation in (False, True):
            cr.verify_effective(evidence(generation), 1000, 1000, generation)
            for field, value in changes:
                data = evidence(generation)
                data[field] = value
                with self.subTest(generation=generation, field=field, value=value):
                    with self.assertRaises((AssertionError, ValueError)):
                        cr.verify_effective(data, 1000, 1000, generation)
            for field in evidence()['status']:
                data = evidence(generation)
                data['status'][field] = '0' if field == 'NoNewPrivs' else '1'
                with self.assertRaises(AssertionError):
                    cr.verify_effective(data, 1000, 1000, generation)
            for field in evidence():
                data = evidence(generation)
                del data[field]
                if field == 'tmpfs' and not generation:
                    continue
                with self.assertRaises(KeyError):
                    cr.verify_effective(data, 1000, 1000, generation)
            data = evidence(generation)
            data['mounts'][0]['options'] = ['rw']
            with self.assertRaises(AssertionError):
                cr.verify_effective(data, 1000, 1000, generation)

    def test_effective_bind_flags(self):
        for cls in (cr.Docker, cr.Podman):
            for options in (['rw'], None):
                data = evidence()
                if options is not None:
                    data['mounts'].append(dict(path='/inputs/task.md', options=options))
                with patch.object(cr, 'command'), patch.object(cls, 'exec', return_value=json.dumps(data)), \
                        patch.object(cls, 'inspect', return_value=config(cls)):
                    with self.assertRaises(AssertionError):
                        cls().start('box', 1000, 1000)

    def test_tmpfs_restrictions(self):
        original = evidence(True)
        for field, value in [('uid', 0), ('gid', 0), ('mode', 0o777), ('mount',
                              dict(type='bind', options=['rw'], super=['size=65536k']))]:
            data = copy.deepcopy(original)
            data['tmpfs'][field] = value
            with self.assertRaises(AssertionError):
                cr.verify_effective(data, 1000, 1000, True)
        for option in ('rw', 'nosuid', 'nodev', 'noexec'):
            data = copy.deepcopy(original)
            data['tmpfs']['mount']['options'].remove(option)
            with self.assertRaises(AssertionError):
                cr.verify_effective(data, 1000, 1000, True)
        data = copy.deepcopy(original)
        data['tmpfs']['mount']['super'] = ['size=128m']
        with self.assertRaises(AssertionError):
            cr.verify_effective(data, 1000, 1000, True)

    @unittest.skipUnless(os.environ.get('BOUNDSCRIPT_ENGINE_TEST') == '1', 'opt-in real engine check')
    def test_real_engine_without_credentials(self):
        from verify import IMAGE
        engine = cr.runtime()
        engine.image(IMAGE)
        for generation in (False, True):
            with self.subTest(generation=generation), tempfile.TemporaryDirectory() as tmp:
                candidate = Path(tmp) / 'implementation'
                candidate.mkdir()
                name = 'boundscript-runtime-test-' + uuid.uuid4().hex[:12]
                try:
                    engine.create(name, IMAGE, ['--mount',
                                  f'type=bind,src={candidate},dst=/implementation'],
                                  os.getuid(), os.getgid(), generation=generation)
                    engine.start(name, os.getuid(), os.getgid(), generation=generation)
                    engine.exec(name, 'node', '-e',
                                "require('fs').writeFileSync('/implementation/probe', 'ok')")
                    self.assertEqual((candidate / 'probe').read_text(), 'ok')
                finally:
                    engine.remove(name)

    def test_pair_cleanup_on_create_start_or_exec_failure(self):
        import verify_pair
        for method in ('create', 'start', 'exec'):
            with patch.object(verify_pair, 'runtime') as factory:
                engine = factory.return_value
                getattr(engine, method).side_effect = RuntimeError('synthetic failure')
                with self.assertRaises(RuntimeError):
                    verify_pair.check('normalize-contact', verify_pair.PAIR / 'accepted/normalize-contact.ts')
                engine.remove.assert_called_once()
                self.assertEqual(engine.remove.call_args.args[0], engine.create.call_args.args[0])

    def test_cli_diagnostics_are_withheld(self):
        with patch.object(cr.subprocess, 'run', return_value=cr.subprocess.CompletedProcess(
                [], 1, stdout='TOKEN', stderr='SECRET')):
            with self.assertRaises(RuntimeError) as error:
                cr.command('podman', 'exec', 'box')
            self.assertNotIn('SECRET', str(error.exception))
            self.assertNotIn('TOKEN', str(error.exception))


if __name__ == '__main__':
    unittest.main()
