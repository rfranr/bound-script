#!/usr/bin/env python3
"""Fixed 0018 checks: two contact Boxes and ordinary TypeScript composition."""
import json
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
from verify import HERE, IMAGE, TSC, digest, run

PAIR = HERE / 'two-boxes'
BOXES = ('normalize-contact', 'render-welcome')
INPUTS = [
    {'name': '  Ada Lovelace  ', 'email': ' ADA@EXAMPLE.TEST '},
    {'name': ' Grace  Hopper ', 'email': 'Grace@Example.Test'},
    {'name': ' \t\n', 'email': '  '},
    {'name': ' Zoë ', 'email': '\tZOE@EXAMPLE.TEST\n'},
]
EXPECTED = [
    {'name': 'Ada Lovelace', 'email': 'ada@example.test'},
    {'name': 'Grace  Hopper', 'email': 'grace@example.test'},
    {'name': '', 'email': ''},
    {'name': 'Zoë', 'email': 'zoe@example.test'},
]


def check(mode, submission=None):
    integration = mode == 'integrate'
    if integration:
        files = {PAIR / 'application.ts': '/app/application.ts'}
        files.update({PAIR / f'accepted/{box}.ts': f'/app/accepted/{box}.ts' for box in BOXES})
    else:
        files = {
            submission: '/implementation/implementation.ts',
            PAIR / f'contracts/{mode}.ts': '/inputs/contract.ts',
            PAIR / ('check-normalize.ts' if mode == BOXES[0] else 'check-render.ts'): '/checks/contract.ts',
        }
        if mode == BOXES[1]:
            files[PAIR / 'contracts/normalize-contact.ts'] = '/inputs/normalize-contact.ts'
    for source in files:
        assert source.is_file() and not source.is_symlink(), 'Expected regular trusted input/submission'
    assert all(p.stat().st_size <= 16384 for p in files), 'Oversized source'
    before = {p: digest(p) for p in files}
    mounts = []
    for source, destination in files.items():
        mounts += ['--mount', f'type=bind,src={source.resolve()},dst={destination},readonly']
    mounts += ['--mount', f'type=bind,src={TSC.parents[1]},dst=/tools/typescript,readonly']
    name = 'boundscript-contact-check-' + uuid.uuid4().hex[:12]
    uid, gid = (os.getuid(), os.getgid()) if os.getuid() else (65534, 65534)
    try:
        run('docker', 'create', '--name', name, '--pull', 'never', '--network', 'none',
            '--user', f'{uid}:{gid}', '--read-only', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges', '--memory', '256m', '--memory-swap', '256m',
            '--cpus', '1', '--pids-limit', '32', '--log-driver', 'none',
            *mounts, IMAGE, 'sleep', '300')
        config = json.loads(run('docker', 'inspect', name))[0]
        assert config['HostConfig']['NetworkMode'] == 'none'
        assert config['HostConfig']['ReadonlyRootfs'] and config['Config']['User'] == f'{uid}:{gid}'
        assert len(config['Mounts']) == len(files) + 1 and all(not m['RW'] for m in config['Mounts'])
        assert {m['Destination'] for m in config['Mounts']} == {*files.values(), '/tools/typescript'}
        run('docker', 'start', name)

        def observe(source):
            return json.loads(run('docker', 'exec', '-i', name, 'node', '--input-type=module', source=source))

        # Deliberate unauthorized implementation access. This is missing-file/module
        # denial, NOT a source-import allowlist or a universal dependency checker.
        denied = observe('''
import { readFileSync } from 'node:fs';
const errors = [];
try { readFileSync('/peer/implementation.ts'); errors.push('SUCCEEDED'); } catch(e) { errors.push(e.code); }
try { await import('/peer/implementation.ts'); errors.push('SUCCEEDED'); } catch(e) { errors.push(e.code); }
console.log(JSON.stringify(errors));
''')
        assert denied == ['ENOENT', 'ERR_MODULE_NOT_FOUND'], denied
        print(f'PASS {mode}: forbidden peer read ENOENT; import ERR_MODULE_NOT_FOUND (file not exposed)', flush=True)
        if not integration:
            # A human-owned native consumer checks the actual exported signature,
            # not just whether the candidate happens to annotate its own code.
            run('docker', 'exec', name, 'node', '/tools/typescript/lib/tsc.js', '--noEmit',
                '--strict', '--target', 'es2022', '--module', 'nodenext',
                '--allowImportingTsExtensions', '/checks/contract.ts')
            print(f'PASS {mode}: strict native contract consumer', flush=True)
        inputs = 'const inputs = ' + json.dumps(INPUTS) + ';\n'
        if mode == BOXES[0]:
            observed = observe(inputs + '''
import { normalizeContact } from '/implementation/implementation.ts';
console.log(JSON.stringify(inputs.map(input => {
 const result = normalizeContact(input);
 return {result, inputAfter: input, fresh: result !== input};
})));
''')
            assert observed == [dict(result=expected, inputAfter=raw, fresh=True)
                                for raw, expected in zip(INPUTS, EXPECTED)], 'NormalizeContact behavior'
        elif mode == BOXES[1]:
            observed = observe(inputs + '''
import { renderWelcome } from '/implementation/implementation.ts';
console.log(JSON.stringify(inputs.map((input, i) => {
 const calls = [];
 const result = renderWelcome(input, value => {
  calls.push({same: value === input, value: {...value}});
  return {name: 'Supplied ' + i, email: 'dependency' + i + '@example.test'};
 });
 return {result, inputAfter: input, calls};
})));
''')
            assert observed == [dict(result=f'Welcome, Supplied {i}! <dependency{i}@example.test>',
                                    inputAfter=raw, calls=[dict(same=True, value=raw)])
                                for i, raw in enumerate(INPUTS)], 'RenderWelcome must use its supplied dependency'
        else:
            observed = observe(inputs + '''
import { welcomeContact } from '/app/application.ts';
console.log(JSON.stringify(inputs.map(input => ({result: welcomeContact(input), inputAfter: input}))));
''')
            assert observed == [dict(result=f"Welcome, {row['name']}! <{row['email']}>", inputAfter=raw)
                                for raw, row in zip(INPUTS, EXPECTED)], 'End-to-end application behavior'
        assert all(digest(p) == old for p, old in before.items()), 'Input/artifact changed'
        print(f'PASS {mode}: four cases; inputs and artifacts unchanged', flush=True)
    finally:
        run('docker', 'rm', '-f', name)


def main():
    if not __debug__ or run('git', 'branch', '--show-current') != 'experiment/boundscript-next':
        raise RuntimeError('Use experiment/boundscript-next with assertions enabled')
    assert TSC.is_file(), 'Install existing dependencies first'
    run('docker', 'image', 'inspect', IMAGE)
    if len(sys.argv) == 3 and sys.argv[1] in BOXES:
        check(sys.argv[1], Path(sys.argv[2]))
    elif sys.argv[1:] == ['integrate']:
        check('integrate')
    elif len(sys.argv) == 1:
        for box in BOXES:
            check(box, PAIR / f'accepted/{box}.ts')
        check('integrate')
    else:
        raise RuntimeError('Expected no args, integrate, or one fixed Box name and submission path')


if __name__ == '__main__':
    main()
