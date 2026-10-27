#!/usr/bin/env python3
"""Fixed 0018b checks: richer contact Boxes and ordinary TS composition."""
import json
import os
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from boundscript_internal.container_runtime import IMAGE, TSC, digest, runtime

HERE = Path(__file__).resolve().parent
PAIR = HERE / 'two-boxes'
BOXES = ('normalize-contact', 'render-welcome')
def success(name, email):
    return {'ok': True, 'contact': {'name': name, 'email': email}}


def failure(*errors):
    return {'ok': False, 'errors': list(errors)}


# Literal external examples, not a second implementation of the business rules.
CASES = [
    ({'name': '  Ada Lovelace  ', 'email': ' ADA@EXAMPLE.TEST '}, success('Ada Lovelace', 'ada@example.test')),
    ({'name': ' Grace  Hopper ', 'email': 'Grace@Example.Test'}, success('Grace Hopper', 'grace@example.test')),
    ({'name': '', 'email': ''}, failure('name.required', 'email.required')),
    ({'name': ' \t\r\n\u00a0\u2003', 'email': '\t\n '}, failure('name.required', 'email.required')),
    ({'name': ' Zoë\t\n李\u00a0\u2003雷 ', 'email': '\tÉ@例子.测试\n'}, success('Zoë 李 雷', 'é@例子.测试')),
    ({'name': ' e\u0301  👩🏽‍💻 ', 'email': 'A+B@X.Y'}, success('e\u0301 👩🏽‍💻', 'a+b@x.y')),
    ({'name': '\u200b', 'email': 'a@b.c'}, success('\u200b', 'a@b.c')),
    ({'name': '', 'email': 'bad'}, failure('name.required', 'email.invalid')),
    ({'name': 'Ada', 'email': ' '}, failure('email.required')),
    ({'name': '\t', 'email': 'A@B.C'}, failure('name.required')),
    ({'name': 'Ada', 'email': 'a@b'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': '@b.c'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a@.c'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a@b.'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a@@b.c'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a b@c.d'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a@b\u00a0.c'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': 'a@b.\nc'}, failure('email.invalid')),
    ({'name': 'Ada', 'email': ' A..B@C..D '}, success('Ada', 'a..b@c..d')),
    ({'name': 'Ada', 'email': 'A@B.\u200b'}, success('Ada', 'a@b.\u200b')),
]
INPUTS = [raw for raw, expected in CASES]
EXPECTED = [expected for raw, expected in CASES]
# Deliberately non-normalized successes and unusual errors detect duplicated rules.
DEPENDENCY_RESULTS = [
    success('  Supplied\tNAME  ', 'UPPER@NOT-NORMALIZED'),
    success('', ''),
    failure('email.invalid', 'name.required', 'email.invalid'),
    failure(),
]
DEPENDENCY_MESSAGES = [
    'Welcome,   Supplied\tNAME  ! <UPPER@NOT-NORMALIZED>',
    'Welcome, ! <>',
    'Invalid contact: email.invalid, name.required, email.invalid',
    'Invalid contact: ',
]


def check(mode, submission=None):
    engine = runtime()
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
        engine.create(name, IMAGE, mounts, uid, gid)
        engine.start(name, uid, gid)

        def observe(source):
            return json.loads(engine.exec(name, 'node', '--input-type=module', source=source))

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
            engine.exec(name, 'node', '/tools/typescript/lib/tsc.js', '--noEmit',
                '--strict', '--target', 'es2022', '--module', 'nodenext',
                '--allowImportingTsExtensions', '/checks/contract.ts')
            print(f'PASS {mode}: strict native contract consumer', flush=True)
        inputs = 'const inputs = ' + json.dumps(INPUTS) + ';\n'
        if mode == BOXES[0]:
            observed = observe(inputs + '''
import { normalizeContact } from '/implementation/implementation.ts';
console.log(JSON.stringify(inputs.map(input => {
 Object.freeze(input);
 const result = normalizeContact(input);
 const repeated = normalizeContact(input);
 return {result, repeated, inputAfter: input, fresh: !result.ok || result.contact !== input};
})));
''')
            assert observed == [dict(result=expected, repeated=expected, inputAfter=raw, fresh=True)
                                for raw, expected in zip(INPUTS, EXPECTED)], 'NormalizeContact behavior'
        elif mode == BOXES[1]:
            observed = observe(inputs + 'const supplied = ' + json.dumps(DEPENDENCY_RESULTS) + ';\n' + '''
import { renderWelcome } from '/implementation/implementation.ts';
for (const result of supplied) {
 Object.freeze(result.contact ?? result.errors);
 Object.freeze(result);
}
console.log(JSON.stringify(inputs.flatMap(input => supplied.map(dependencyResult => {
 Object.freeze(input);
 const calls = [];
 const result = renderWelcome(input, value => {
  calls.push({same: value === input, value: {...value}});
  return dependencyResult;
 });
 return {result, inputAfter: input, calls, dependencyResult};
}))));
''')
            assert observed == [dict(result=message, inputAfter=raw,
                                    calls=[dict(same=True, value=raw)], dependencyResult=result)
                                for raw in INPUTS
                                for result, message in zip(DEPENDENCY_RESULTS, DEPENDENCY_MESSAGES)], 'RenderWelcome must use its supplied dependency'
            thrown = observe('''
import { renderWelcome } from '/implementation/implementation.ts';
let calls = 0;
const sentinel = new Error('sentinel');
let same = false;
try { renderWelcome(Object.freeze({name: '', email: ''}), () => { calls++; throw sentinel; }); }
catch (error) { same = error === sentinel; }
console.log(JSON.stringify({same, calls}));
''')
            assert thrown == dict(same=True, calls=1), 'Dependency exceptions must propagate without retry'
        else:
            observed = observe(inputs + '''
import { welcomeContact } from '/app/application.ts';
console.log(JSON.stringify(inputs.map(input => {
 Object.freeze(input);
 return {result: welcomeContact(input), inputAfter: input};
})));
''')
            messages = [f"Welcome, {row['contact']['name']}! <{row['contact']['email']}>" if row['ok']
                        else 'Invalid contact: ' + ', '.join(row['errors']) for row in EXPECTED]
            assert observed == [dict(result=message, inputAfter=raw)
                                for raw, message in zip(INPUTS, messages)], 'End-to-end application behavior'
        assert all(digest(p) == old for p, old in before.items()), 'Input/artifact changed'
        count = len(INPUTS) * len(DEPENDENCY_RESULTS) + 1 if mode == BOXES[1] else len(INPUTS)
        print(f'PASS {mode}: {count} cases; frozen inputs and artifacts unchanged', flush=True)
    finally:
        engine.remove(name)


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    assert TSC.is_file(), 'Install existing dependencies first'
    runtime().image(IMAGE)
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
