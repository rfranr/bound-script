"""Opt-in 0044 experiment: manual fixtures, unchanged oracle, shared CLI only."""
from importlib import import_module
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

from experiments.native_cli import ROOT, verification_command

HERE = Path(__file__).resolve().parent
BOX = import_module('experiments.render-welcome-native.native_box').BOX

# Independently organized test implementations, not accepted/generated assets.
A = {
    'implementation.ts': """import type { RenderWelcome } from './contract';

export const renderWelcome: RenderWelcome = contact =>
  `Welcome, ${contact.name}! <${contact.email}>`;
""",
}

B = {
    'implementation.ts': """import type { RenderWelcome } from './contract';
import { formatGreeting } from './presentation/message';

export const renderWelcome: RenderWelcome = ({ name, email }) => formatGreeting(name, email);
""",
    'presentation/message.ts': """import { GreetingText } from '../text/greeting';
import { mailbox } from '../text/mailbox';

export function formatGreeting(name: string, email: string): string {
  return new GreetingText(name).withAddress(mailbox(email));
}
""",
    'text/greeting.ts': """export class GreetingText {
  constructor(private readonly name: string) {}

  withAddress(address: string): string {
    return ['Welcome, ', this.name, '! ', address].join('');
  }
}
""",
    'text/mailbox.ts': """export const mailbox = (email: string): string => ['<', email, '>'].join('');
""",
}

# Move only internal helpers; the public entry and helper bodies stay identical.
B_REORGANIZED = {
    'implementation.ts': B['implementation.ts'],
    'presentation/message.ts': """import { GreetingText } from '../internal/fragments/line';
import { mailbox } from '../internal/fragments/brackets.test';

export function formatGreeting(name: string, email: string): string {
  return new GreetingText(name).withAddress(mailbox(email));
}
""",
    'internal/fragments/line.ts': B['text/greeting.ts'],
    'internal/fragments/brackets.test.ts': B['text/mailbox.ts'],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(root):
    """Experiment observation only: membership, kinds, modes and content hashes."""
    if not root.exists() and not root.is_symlink():
        return ()
    records = []
    for path in sorted([root, *root.rglob('*')]):
        info = path.lstat()
        content = (os.readlink(path) if stat.S_ISLNK(info.st_mode) else
                   sha(path) if stat.S_ISREG(info.st_mode) else '')
        records.append((path.relative_to(root).as_posix(), info.st_mode, content))
    return tuple(records)


def measurement_digest(value):
    """Compact evidence summary, not an artifact identity or verifier receipt."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def prepare(root, files):
    for relative, source in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.encode('utf-8'))


@unittest.skipUnless(os.environ.get('BOUNDSCRIPT_WELCOME_AB_TEST') == '1', 'opt-in Docker A/B experiment')
class WelcomeABExperiment(unittest.TestCase):
    def test_independent_implementations_against_the_unchanged_oracle(self):
        oracle_files = BOX.verification_files(HERE / BOX.verification_path)
        consumer_files = set(oracle_files)
        consumer_files.update(('native_box.py', 'task.md', 'tsconfig.json', 'vitest.tooling.config.mts'))
        consumer_before = {relative: sha(HERE / relative) for relative in sorted(consumer_files)}
        workflow_files = sorted(p for p in (ROOT / 'boundscript_internal').iterdir()
                                if p.suffix in ('.py', '.mjs', '.mts'))
        workflow_files.append(ROOT / 'experiments/native_cli.py')
        workflow_before = {p.relative_to(ROOT).as_posix(): sha(p) for p in workflow_files}
        outputs_before = {name: state(HERE / name) for name in ('accepted', 'quarantine')}
        definition = BOX.fingerprint()

        with tempfile.TemporaryDirectory(prefix='boundscript-welcome-ab-') as tmp:
            area = Path(tmp)
            candidates = {'A': area / 'a', 'B': area / 'b', 'B-reorganized': area / 'b-reorganized'}
            for label, files in (('A', A), ('B', B), ('B-reorganized', B_REORGANIZED)):
                prepare(candidates[label], files)
            self.assertEqual((candidates['B'] / 'implementation.ts').read_bytes(),
                             (candidates['B-reorganized'] / 'implementation.ts').read_bytes())
            baseline_sources = {label: state(path) for label, path in candidates.items()}

            def verify(label, candidate, *, tree, failure=None):
                before = state(candidate)
                args = ['--box-definition', definition]
                args += ['--source-tree', str(candidate)] if tree else [str(candidate / 'implementation.ts')]
                try:
                    result = subprocess.run([*verification_command('render-welcome'), *args], cwd=area,
                                            env={**os.environ, 'BOUNDSCRIPT_RUNTIME': 'docker', 'DEBUG': 'False'},
                                            capture_output=True, text=True, timeout=360)
                    self.assertEqual(result.returncode, 1 if failure else 0, result.stdout + result.stderr)
                    for phase in ('Sandbox/security checks', 'Protected input integrity', 'Sandbox cleanup'):
                        if failure is None or phase == 'Sandbox cleanup':
                            self.assertIn('PASS ' + phase, result.stdout)
                    if failure:
                        self.assertIn(f'FAIL [{failure}]', result.stdout)
                        self.assertIn('Candidate retained in place (not promoted)', result.stdout)
                        self.assertNotIn('PASS independent native verification', result.stdout)
                    else:
                        self.assertIn('PASS TypeScript compilation', result.stdout)
                        self.assertIn('Vitest exit status: 0; 3 passed, 0 failed, 0 skipped, 0 pending', result.stdout)
                        self.assertIn('Vitest exit status: 0; 7 passed, 0 failed, 0 skipped, 0 pending', result.stdout)
                        self.assertEqual(result.stdout.count('PASS "validators.test.ts":'), 3)
                        self.assertEqual(result.stdout.count('PASS "acceptance.test.ts":'), 7)
                        self.assertIn('PASS independent native verification; no promotion performed by verifier', result.stdout)
                    summary = {'scenario': label, 'mode': 'tree' if tree else 'file',
                               'result': failure or 'PASS', 'definition': definition,
                               'consumer_sha256': measurement_digest(consumer_before),
                               'workflow_sha256': measurement_digest(workflow_before),
                               'files': {p.relative_to(candidate).as_posix(): sha(p)
                                         for p in sorted(candidate.rglob('*.ts'))}}
                finally:
                    self.assertEqual(state(candidate), before, label + ': submitted source changed')
                    self.assertEqual({relative: sha(HERE / relative) for relative in sorted(consumer_files)}, consumer_before)
                    self.assertEqual(BOX.verification_files(HERE / BOX.verification_path), oracle_files)
                    self.assertEqual({p.relative_to(ROOT).as_posix(): sha(p) for p in workflow_files}, workflow_before)
                    self.assertEqual({name: state(HERE / name) for name in outputs_before}, outputs_before)
                    self.assertEqual(BOX.fingerprint(), definition)
                print(json.dumps(summary), flush=True)

            for label, tree in (('A', False), ('A', True), ('B', True), ('B-reorganized', True)):
                with self.subTest(candidate=label, tree=tree):
                    verify(label, candidates[label], tree=tree)

            # Negative controls consume the same oracle, not adjusted expectations.
            for label, text, failure in (
                ('missing-export', 'export const other = () => "wrong";\n', 'compilation'),
                ('wrong-format', "import type { RenderWelcome } from './contract';\n"
                 'export const renderWelcome: RenderWelcome = () => "wrong";\n', 'assertion'),
                ('call-history', "import type { RenderWelcome } from './contract';\n"
                 'let calls = 0;\nexport const renderWelcome: RenderWelcome = contact =>\n'
                 '  ++calls === 1 ? `Welcome, ${contact.name}! <${contact.email}>` : "wrong";\n', 'assertion'),
                ('input-mutation', "import type { RenderWelcome } from './contract';\n"
                 'export const renderWelcome: RenderWelcome = contact => {\n'
                 '  Object.assign(contact, { name: "changed" });\n'
                 '  return `Welcome, ${contact.name}! <${contact.email}>`;\n};\n', 'runtime'),
            ):
                negative = area / label
                prepare(negative, {'implementation.ts': text})
                with self.subTest(negative=label):
                    verify(label, negative, tree=True, failure=failure)

            self.assertEqual({label: state(path) for label, path in candidates.items()}, baseline_sources)
        self.assertFalse(area.exists())
