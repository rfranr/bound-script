"""Small local CLI adapters; one fail-closed security policy for both engines."""
import json
import os
from pathlib import Path
import subprocess


def command(*args, source=None, timeout=30):
    # Never propagate CLI output: it may contain agent diagnostics or credentials.
    result = subprocess.run(args, input=source, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Container command failed; diagnostics withheld')
    return result.stdout.strip()


# Executed before credentials are copied or any candidate code runs. Missing
# procfs/cgroup-v2 evidence is an error, not permission to trust CLI flags.
PROBE = r'''
import {readFileSync, statSync} from 'node:fs';
const read = p => readFileSync(p, 'utf8').trim();
const status = Object.fromEntries(read('/proc/self/status').split('\n').map(l => l.split(/:\s*/)));
const mounts = read('/proc/self/mountinfo').split('\n').map(l => {
 const [a,b] = l.split(' - '); const f = a.split(' '), g = b.split(' ');
 return {path:f[4], options:f[5].split(','), type:g[0], super:g[2].split(',')};
});
const state = mounts.find(m => m.path === '/pi-state');
let tmpfs = null;
if (state) {
 const s = statSync('/pi-state');
 tmpfs = {mount:state, uid:s.uid, gid:s.gid, mode:s.mode & 0o777};
}
console.log(JSON.stringify({uid:process.getuid(), gid:process.getgid(), status, mounts, tmpfs,
 memory:read('/sys/fs/cgroup/memory.max'), swap:read('/sys/fs/cgroup/memory.swap.max'),
 cpu:read('/sys/fs/cgroup/cpu.max'), pids:read('/sys/fs/cgroup/pids.max')}));
'''


def verify_effective(data, uid, gid, generation):
    assert uid != 0 and data['uid'] == uid and data['gid'] == gid
    status = data['status']
    assert status['NoNewPrivs'] == '1'
    for field in ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb'):
        assert int(status[field], 16) == 0
    root = [m for m in data['mounts'] if m['path'] == '/']
    assert len(root) == 1 and 'ro' in root[0]['options']
    assert int(data['memory']) == (512 if generation else 256) * 1024 * 1024
    assert int(data['swap']) == 0
    quota, period = map(int, data['cpu'].split())
    assert quota > 0 and quota == period
    assert int(data['pids']) == (64 if generation else 32)
    if generation:
        state = data['tmpfs']
        assert state['uid'] == uid and state['gid'] == gid and state['mode'] == 0o700
        mount = state['mount']
        assert mount['type'] == 'tmpfs'
        assert {'rw', 'nosuid', 'nodev', 'noexec'} <= set(mount['options'])
        sizes = [o[5:] for o in mount['super'] if o.startswith('size=')]
        assert len(sizes) == 1 and sizes[0] in ('65536k', '64m', '67108864')


class Docker:
    executable = 'docker'
    extra_env = {}

    def image(self, image):
        command(self.executable, 'image', 'inspect', image)

    def tmpfs(self, uid, gid):
        return ['--tmpfs', f'/pi-state:rw,nosuid,nodev,noexec,size=64m,mode=700,uid={uid},gid={gid}']

    def create(self, name, image, mounts, uid, gid, *, generation=False, workdir=None):
        args = ['--name', name, '--pull', 'never', '--network', 'bridge' if generation else 'none',
                '--user', f'{uid}:{gid}', '--read-only', '--cap-drop', 'ALL',
                '--security-opt', 'no-new-privileges', '--memory', '512m' if generation else '256m',
                '--memory-swap', '512m' if generation else '256m', '--cpus', '1',
                '--pids-limit', '64' if generation else '32', '--log-driver', 'none']
        if workdir:
            args += ['--workdir', workdir]
        if generation:
            args += self.tmpfs(uid, gid)
            env = {'HOME': '/pi-state', 'PI_CODING_AGENT_DIR': '/pi-state', 'PI_OFFLINE': '1',
                   'PI_TELEMETRY': '0', 'PI_SKIP_VERSION_CHECK': '1'}
        else:
            env = {'HOME': '/implementation'}
        for key, value in env.items():
            args += ['--env', f'{key}={value}']
        command(self.executable, 'create', *args, *mounts, image, 'sleep', '600')
        config = self.inspect(name)
        h = config['HostConfig']
        assert h['NetworkMode'] == ('bridge' if generation else 'none')
        assert h['ReadonlyRootfs'] is True and h['Privileged'] is False
        assert config['Config']['User'] == f'{uid}:{gid}' and uid != 0
        # CapDrop differs (ALL vs expanded capability names). The actual process
        # capability sets and no-new-privileges are checked after start instead.
        expected = {}
        for spec in mounts[1::2]:
            fields = spec.split(',')
            values = dict(f.split('=', 1) for f in fields if '=' in f)
            expected[values['dst']] = (str(Path(values['src']).resolve()), 'readonly' not in fields)
        binds = [m for m in config['Mounts'] if m['Type'] == 'bind']
        assert len(binds) == len(expected)
        assert {m['Destination']: (m['Source'], m['RW']) for m in binds} == expected
        assert all(m['Type'] == 'bind' or (generation and m['Type'] == 'tmpfs'
                   and m['Destination'] == '/pi-state') for m in config['Mounts'])
        actual_env = dict(e.split('=', 1) for e in config['Config']['Env'])
        assert set(actual_env) <= {'PATH', 'NODE_VERSION', 'YARN_VERSION', *env, *self.extra_env}
        assert all(actual_env.get(k) == v for k, v in {**env, **self.extra_env}.items())

    def inspect(self, name):
        return json.loads(command(self.executable, 'inspect', name))[0]

    def start(self, name, uid, gid, *, generation=False):
        command(self.executable, 'start', name)
        data = json.loads(self.exec(name, 'node', '--input-type=module', source=PROBE))
        verify_effective(data, uid, gid, generation)
        for bind in self.inspect(name)['Mounts']:
            if bind['Type'] == 'bind':
                actual = [m for m in data['mounts'] if m['path'] == bind['Destination']]
                assert len(actual) == 1
                assert ('rw' if bind['RW'] else 'ro') in actual[0]['options']

    def exec(self, name, *args, source=None, timeout=30):
        return command(self.executable, 'exec', *(['-i'] if source is not None else []),
                       name, *args, source=source, timeout=timeout)

    def remove(self, name):
        command(self.executable, 'rm', '-f', name)


class Podman(Docker):
    executable = 'podman'
    extra_env = {'container': 'podman'}

    def tmpfs(self, uid, gid):
        # Podman assigns ownership to the configured container user.
        return ['--mount', 'type=tmpfs,destination=/pi-state,tmpfs-size=64m,'
                'tmpfs-mode=0700,rw,nosuid,nodev,noexec,U=true']


def runtime():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    selection = os.environ.get('BOUNDSCRIPT_RUNTIME', 'docker')
    if selection not in ('docker', 'podman'):
        raise ValueError('BOUNDSCRIPT_RUNTIME must be docker or podman')
    return {'docker': Docker, 'podman': Podman}[selection]()
