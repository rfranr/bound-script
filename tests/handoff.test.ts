import { execFileSync } from 'node:child_process';
import { cp, lstat, mkdir, mkdtemp, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

import { afterEach, expect, it } from 'vitest';
import { deriveHandoffs } from '../tooling/handoff.js';
import { DERIVATION_VERSION } from '../tooling/handoff-render.js';

const repository = process.cwd();
const temps: string[] = [];
async function temp() { const dir = await mkdtemp(path.join(os.tmpdir(), 'bound-handoff-')); temps.push(dir); return dir; }
afterEach(async () => { await Promise.all(temps.splice(0).map((dir) => rm(dir, { recursive: true, force: true }))); });
async function fixture() {
  const root = await temp();
  await mkdir(path.join(root, 'examples'));
  await cp('examples/structured-types.bound', path.join(root, 'examples/structured-types.bound'));
  await mkdir(path.join(root, 'tests/fixtures'), { recursive: true });
  await cp('tests/fixtures/handoff', path.join(root, 'tests/fixtures/handoff'), { recursive: true });
  const input = JSON.parse(await readFile(path.join(root, 'tests/fixtures/handoff/input.json'), 'utf8'));
  const save = () => writeFile(path.join(root, 'tests/fixtures/handoff/input.json'), JSON.stringify(input));
  const derive = (output: string, selection: 'all' | { system: string; box: string } = 'all') =>
    deriveHandoffs({ root, binding: 'tests/fixtures/handoff/input.json', output: path.join(root, output), selection });
  return { root, input, save, derive };
}
async function tree(root: string, prefix = ''): Promise<Record<string, string>> {
  const entries: Record<string, string> = {};
  for (const file of (await readdir(path.join(root, prefix))).sort()) {
    const key = prefix ? `${prefix}/${file}` : file;
    if ((await lstat(path.join(root, key))).isDirectory()) Object.assign(entries, await tree(root, key));
    else entries[key] = (await readFile(path.join(root, key))).toString('base64');
  }
  return entries;
}
const greeter = { system: 'GreetingSystem', box: 'Greeter' };

it('AC-01/02/03: exact eight-file golden, unchanged canonical export, snapshots, repeated roots and explicit selections', async () => {
  const f = await fixture();
  await writeFile(path.join(f.root, f.input.boxes[1].task), '\uFEFF# Unapproved Ω "quotes"\r\nNonempty intent\r\n');
  await writeFile(path.join(f.root, f.input.boxes[1].scope), 'Scope without final newline');
  await f.derive('one');
  const original = await tree(path.join(f.root, 'one/GreetingSystem/Greeter'));
  expect(Object.keys(original)).toHaveLength(8);
  const decoded = Object.fromEntries(Object.entries(original).map(([key, bytes]) => [key, Buffer.from(bytes, 'base64').toString('utf8')]));
  expect(decoded).toMatchSnapshot();
  for (const field of ['task', 'scope', 'policy'] as const) {
    expect(await readFile(path.join(f.root, `one/GreetingSystem/Greeter/${field}.md`)))
      .toEqual(await readFile(path.join(f.root, field === 'policy' ? f.input.policy : f.input.boxes[1][field])));
  }
  expect(decoded['contract.box-spec.json']).toBe(await readFile('examples/specs/greeter.box-spec.json', 'utf8'));
  expect(DERIVATION_VERSION).toBe(1);
  const metadata = JSON.parse(decoded['handoff.json']!);
  expect(Object.keys(metadata)).toEqual(['format', 'version', 'derivationVersion', 'system', 'box', 'operation', 'inputs', 'entrypoint']);
  // Deliberately reverse keys and Box order; filesystem creation order is irrelevant.
  f.input.boxes.reverse();
  const reversed = Object.fromEntries(Object.entries(f.input).reverse());
  await writeFile(path.join(f.root, 'tests/fixtures/handoff/input.json'), JSON.stringify(reversed));
  await f.derive('two');
  expect(await tree(path.join(f.root, 'two'))).toEqual(await tree(path.join(f.root, 'one')));
  // Recreate the same inputs in reverse filesystem creation/enumeration order.
  const otherRoot = await temp();
  const inputs = [...new Set<string>([f.input.architecture, f.input.policy, 'tests/fixtures/handoff/input.json',
    ...f.input.boxes.flatMap((b: any) => [b.task, b.scope])])];
  for (const file of inputs.reverse()) {
    await mkdir(path.dirname(path.join(otherRoot, file)), { recursive: true });
    await cp(path.join(f.root, file), path.join(otherRoot, file));
  }
  await deriveHandoffs({ root: otherRoot, binding: 'tests/fixtures/handoff/input.json', output: path.join(otherRoot, 'out'), selection: 'all' });
  expect(await tree(path.join(otherRoot, 'out'))).toEqual(await tree(path.join(f.root, 'one')));
  await f.derive('single', greeter);
  expect(await tree(path.join(f.root, 'single/GreetingSystem/Greeter'))).toEqual(original);
  // An unrelated valid binding must not change the selected package.
  f.input.boxes.push({ system: 'GreetingSystem', box: 'Display', task: f.input.boxes[0].task, scope: f.input.boxes[0].scope });
  await f.save();
  await f.derive('extra', greeter);
  expect(await tree(path.join(f.root, 'extra/GreetingSystem/Greeter'))).toEqual(original);
  const entry = f.input.boxes.find((b: any) => b.box === 'Greeter');
  await cp(path.join(f.root, entry.task), path.join(f.root, 'same-content.md'));
  entry.task = 'same-content.md'; await f.save();
  await f.derive('path-change', greeter);
  const moved = await tree(path.join(f.root, 'path-change/GreetingSystem/Greeter'));
  expect(Object.keys(original).filter((file) => original[file] !== moved[file])).toEqual(['handoff.json']);
});

it('AC-01: unused valid Box can be explicitly selected', async () => {
  const f = await fixture();
  const file = path.join(f.root, f.input.architecture);
  await writeFile(file, (await readFile(file, 'utf8')).replace('    director Main', '    box Unused { operation unused(value: string): string }\n    director Main'));
  f.input.boxes.push({ ...f.input.boxes[0], box: 'Unused' });
  await f.save();
  await f.derive('unused', { system: 'GreetingSystem', box: 'Unused' });
  expect(Object.keys(await tree(path.join(f.root, 'unused')))).toHaveLength(8);
});

const badBindings: [string, (input: any) => void][] = [
  ['unknown root key', (i) => { i.approved = true; }],
  ['missing root key', (i) => { delete i.policy; }],
  ['unsupported version', (i) => { i.version = 2; }],
  ['unsupported format', (i) => { i.format = 'other'; }],
  ['empty selections', (i) => { i.boxes = []; }],
  ['malformed selections', (i) => { i.boxes = {}; }],
  ['duplicate', (i) => { i.boxes.push(i.boxes[0]); }],
  ['invalid identity', (i) => { i.boxes[0].box = '../bad'; }],
  ['unknown selection', (i) => { i.boxes[1].box = 'Missing'; }],
  ['identity mismatch', (i) => { i.boxes[1].system = 'Other'; }],
  ['unknown entry key', (i) => { i.boxes[0].extra = 1; }],
  ['missing entry key', (i) => { delete i.boxes[0].task; }],
  ['absolute', (i) => { i.boxes[0].task = '/etc/passwd'; }],
  ['traversal', (i) => { i.boxes[0].task = '../outside'; }],
  ['embedded traversal', (i) => { i.policy = 'tests/../outside'; }],
  ['windows path', (i) => { i.architecture = 'C:\\source.bound'; }],
  ['noncanonical path', (i) => { i.policy = './policy.md'; }],
  ['missing file', (i) => { i.boxes[1].task = 'missing.md'; }],
  ['directory', (i) => { i.boxes[1].task = 'tests'; }]
];
it.each(badBindings)('AC-04: rejects %s without publishing any Box', async (_name, mutate) => {
  const f = await fixture(); mutate(f.input); await f.save();
  await expect(f.derive('out')).rejects.toThrow(/\[.+\]/);
  await expect(lstat(path.join(f.root, 'out'))).rejects.toMatchObject({ code: 'ENOENT' });
  expect((await readdir(f.root)).filter((p) => p.startsWith('.handoff-stage-'))).toEqual([]);
});
it.each(['empty', 'invalid UTF8', 'source UTF8', 'binding UTF8', 'symlink', 'parent symlink', 'fifo', 'missing director', 'invalid unused', 'invalid JSON'])('AC-04: rejects %s before publication', async (kind) => {
  const f = await fixture();
  const task = path.join(f.root, f.input.boxes[1].task);
  if (kind === 'empty') await writeFile(task, ' \r\n\t');
  if (kind === 'invalid UTF8') await writeFile(task, Buffer.from([0xc0, 0xaf]));
  if (kind === 'source UTF8') await writeFile(path.join(f.root, f.input.architecture), Buffer.from([0xff]));
  if (kind === 'binding UTF8') await writeFile(path.join(f.root, 'tests/fixtures/handoff/input.json'), Buffer.from([0xff]));
  if (kind === 'symlink') { await rm(task); await symlink(path.join(f.root, f.input.policy), task); }
  if (kind === 'parent symlink') { await symlink('tests/fixtures/handoff', path.join(f.root, 'linked')); f.input.boxes[1].task = 'linked/greet-task.md'; await f.save(); }
  if (kind === 'fifo') { await rm(task); execFileSync('mkfifo', [task]); }
  if (kind === 'invalid JSON') await writeFile(path.join(f.root, 'tests/fixtures/handoff/input.json'), '{');
  if (kind === 'missing director' || kind === 'invalid unused') {
    const source = path.join(f.root, f.input.architecture);
    const text = await readFile(source, 'utf8');
    await writeFile(source, kind === 'missing director' ? text.slice(0, text.indexOf('    director')) + '}' : text.replace('    director', '    box Bad { operation bad(value: Missing): string }\n    director'));
  }
  await expect(f.derive('out')).rejects.toThrow(/\[.+\]/);
  await expect(lstat(path.join(f.root, 'out'))).rejects.toMatchObject({ code: 'ENOENT' });
});
it('AC-04: existing outputs and candidate destinations remain untouched; unknown explicit selection fails', async () => {
  const f = await fixture();
  await f.derive('existing');
  const before = await tree(path.join(f.root, 'existing'));
  await expect(f.derive('existing')).rejects.toThrow('already exists');
  expect(await tree(path.join(f.root, 'existing'))).toEqual(before);
  await mkdir(path.join(f.root, 'candidate'));
  await writeFile(path.join(f.root, 'candidate/implementation.ts'), 'protected');
  await expect(f.derive('candidate')).rejects.toThrow('already exists');
  expect(await readFile(path.join(f.root, 'candidate/implementation.ts'), 'utf8')).toBe('protected');
  await expect(f.derive('unknown', { system: 'GreetingSystem', box: 'Unknown' })).rejects.toThrow('Unknown explicit selection');
});

it('AC-02: built command works from another cwd with identical bytes and nonzero diagnostics', async () => {
  execFileSync('npm', ['run', 'build', '--silent'], { cwd: repository, stdio: 'pipe' });
  const f = await fixture();
  await f.derive('direct');
  const args = [path.join(repository, '.tool-dist/derive-handoff.js'), f.root, 'tests/fixtures/handoff/input.json', path.join(f.root, 'external'), '--all'];
  expect(execFileSync(process.execPath, args, { cwd: os.tmpdir(), encoding: 'utf8' })).toContain('human approval was not verified');
  expect(await tree(path.join(f.root, 'external'))).toEqual(await tree(path.join(f.root, 'direct')));
  expect(() => execFileSync(process.execPath, args, { cwd: os.tmpdir(), stdio: 'pipe' })).toThrow();
}, 30_000);

it('AC-05: human-invoked two-Box regeneration scope is separate from changed output bytes', async () => {
  const f = await fixture();
  await f.derive('baseline');
  const before = await tree(path.join(f.root, 'baseline'));
  const source = path.join(f.root, f.input.architecture);
  const original = await readFile(source, 'utf8');
  const cases = [
    { name: 'whitespace/director/unrelated', text: original.replace('on start {', 'on start {\n            print("irrelevant director edit")').replace('    director', '    box Unused { operation x(v: string): string }\n    director'), changed: [] },
    { name: 'shared record', text: original.replace('score: number', 'score: string'), changed: ['Greeter', 'LoadUser'] },
    { name: 'predicate', text: original.replace('result.message != ""', 'result.message != "blocked"'), changed: ['Greeter'] }
  ];
  for (const [index, row] of cases.entries()) {
    await writeFile(source, row.text);
    // Policy requires BOTH even when only one or neither changes bytes.
    const affected = ['Greeter', 'LoadUser'];
    await f.derive(`source-${index}`);
    const after = await tree(path.join(f.root, `source-${index}`));
    expect(Object.keys(after).filter((p) => p.endsWith('handoff.json')).map((p) => p.split('/')[1])).toEqual(affected);
    const changed = affected.filter((box) => Object.keys(before).some((key) => key.startsWith(`GreetingSystem/${box}/`) && before[key] !== after[key]));
    expect(changed, row.name).toEqual(row.changed);
  }
  // Existing grammar has no comment tokens: comment edits still affect all Boxes,
  // but whole-source validation rejects them instead of changing the language here.
  await writeFile(source, '// comment\n' + original);
  await expect(f.derive('comment')).rejects.toThrow('source');
  await expect(lstat(path.join(f.root, 'comment'))).rejects.toMatchObject({ code: 'ENOENT' });
  await writeFile(source, original);
  for (const field of ['task', 'scope'] as const) {
    // Give Greeter a private scope for this row, so only it references the edit.
    const file = f.input.boxes[1][field];
    if (field === 'scope') { f.input.boxes[0].scope = 'other-scope.md'; await cp(path.join(f.root, file), path.join(f.root, 'other-scope.md')); await f.save(); }
    await f.derive(`before-${field}`);
    await writeFile(path.join(f.root, file), `Changed ${field}`);
    await f.derive(`after-${field}`, greeter);
    const a = await tree(path.join(f.root, `before-${field}/GreetingSystem/Greeter`));
    const b = await tree(path.join(f.root, `after-${field}/GreetingSystem/Greeter`));
    expect(Object.keys(a).filter((key) => a[key] !== b[key])).toEqual([`${field}.md`]);
    expect(Object.keys(await tree(path.join(f.root, `after-${field}`)))).toHaveLength(8);
  }
  await f.derive('pre-policy');
  await writeFile(path.join(f.root, f.input.policy), 'Changed shared policy');
  await f.derive('policy');
  for (const box of ['Greeter', 'LoadUser']) {
    const a = await tree(path.join(f.root, `pre-policy/GreetingSystem/${box}`));
    const b = await tree(path.join(f.root, `policy/GreetingSystem/${box}`));
    expect(Object.keys(a).filter((key) => a[key] !== b[key])).toEqual(['policy.md']);
  }
  // Rules/tool environment review invokes the full set; same supported rules can yield equal bytes.
  await f.derive('rules-environment-review');
  expect(await tree(path.join(f.root, 'rules-environment-review'))).toEqual(await tree(path.join(f.root, 'policy')));
  await writeFile(path.join(f.root, 'candidate.ts'), '// candidate-only change');
  await writeFile(path.join(f.root, 'private-test.ts'), '// private-test-only change');
  await writeFile(path.join(f.root, 'trusted-test.ts'), '// trusted-acceptance-test-only change');
  // No regeneration required by policy; an optional comparison demonstrates unchanged inputs.
  await f.derive('test-only-comparison');
  expect(await tree(path.join(f.root, 'test-only-comparison'))).toEqual(await tree(path.join(f.root, 'policy')));
  await writeFile(source, original.replace(/    box LoadUser \{[\s\S]*?\n    \}/, '').replace('let user = LoadUser.load("123")', 'print("retired")').replace('let greeting = Greeter.greet(user)', 'print("retired")').replace('Display.show(greeting)', 'print("retired")'));
  await expect(f.derive('removed')).rejects.toThrow('Unknown box');
  f.input.boxes = f.input.boxes.filter((b: any) => b.box !== 'LoadUser'); await f.save();
  await f.derive('retired');
  expect(Object.keys(await tree(path.join(f.root, 'retired')))).toHaveLength(8);
  // Old output remains disposable, not automatically migrated or promoted.
  expect(await tree(path.join(f.root, 'baseline'))).toEqual(before);
});
