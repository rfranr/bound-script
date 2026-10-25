import { execFileSync } from 'node:child_process';
import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { expect, it } from 'vitest';
import { deriveHandoffs } from '../tooling/handoff.js';

const repository = process.cwd();
const tsc = path.join(repository, 'node_modules/typescript/bin/tsc');
const config = { compilerOptions: { target: 'ES2022', module: 'NodeNext', moduleResolution: 'NodeNext', strict: true,
  exactOptionalPropertyTypes: true, noUncheckedIndexedAccess: true, isolatedModules: true, verbatimModuleSyntax: true,
  types: [], skipLibCheck: false, outDir: 'built' }, include: ['candidate/*.ts', 'consumer.ts'] };
async function workspace(root: string, name: string, handoff: string, implementation: string) {
  const dir = path.join(root, name);
  await mkdir(path.join(dir, 'candidate'), { recursive: true });
  await cp(handoff, path.join(dir, 'handoff'), { recursive: true });
  await writeFile(path.join(dir, 'package.json'), '{"type":"module"}');
  await writeFile(path.join(dir, 'tsconfig.json'), JSON.stringify(config));
  await writeFile(path.join(dir, 'candidate/implementation.ts'), implementation);
  await writeFile(path.join(dir, 'consumer.ts'), "import { implement } from './candidate/implementation.js';\nexport { implement };\n");
  return dir;
}
function compile(dir: string): { ok: boolean; diagnostics: string } {
  try { execFileSync(process.execPath, [tsc, '-p', dir, '--pretty', 'false'], { encoding: 'utf8', stdio: 'pipe' }); return { ok: true, diagnostics: '' }; }
  catch (error) { return { ok: false, diagnostics: String((error as { stdout: unknown }).stdout) }; }
}
const annotation = (body: string) => `import type { Implementation } from '../handoff/generated/contract.js';\nexport const implement: Implementation = ${body};\n`;

it('AC-06: independent strict ESM/NodeNext projection cases, including all 16 design spike outcomes', async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), 'bound-independent-'));
  try {
    const fixtureRoot = path.join(repository, 'tests/fixtures/handoff');
    const boxes = ['EmptyBox', 'Shared', 'Collision', 'Text', 'Numeric', 'Flag', 'VoidBox'];
    await cp(fixtureRoot, path.join(root, 'inputs'), { recursive: true });
    await writeFile(path.join(root, 'input.json'), JSON.stringify({ format: 'boundscript/handoff-input', version: 1,
      architecture: 'inputs/projection.bound', policy: 'inputs/policy.md', boxes: boxes.map((box) => ({ system: 'Projection', box,
        task: 'inputs/greet-task.md', scope: 'inputs/scope.md' })) }));
    await deriveHandoffs({ root, binding: 'input.json', output: path.join(root, 'packages'), selection: 'all' });
    const cases: [string, string, string, boolean, string?][] = [
      ['record sync', 'Shared', annotation('(input) => input'), true],
      ['record async', 'Shared', annotation('async (input) => input'), true],
      ['throwing seed', 'Shared', await readFile(path.join(root, 'packages/Projection/Shared/seed/implementation.ts'), 'utf8'), true],
      ['void explicit', 'VoidBox', annotation('() => undefined'), true],
      ['void async', 'VoidBox', annotation('async () => undefined'), true],
      ['void implicit', 'VoidBox', annotation('() => {}'), false, 'TS2322'],
      ['wrong result', 'Shared', annotation('() => 7'), false, 'TS2322'],
      ['wrong parameter', 'Shared', annotation('(input: string) => input'), false, 'TS2322'],
      ['empty record', 'EmptyBox', annotation('() => ({})'), true],
      ['empty extra field', 'EmptyBox', annotation('() => ({ extra: 1 })'), false, 'TS2322'],
      ['empty number', 'EmptyBox', annotation('() => 7'), false, 'TS2322'],
      ['empty array', 'EmptyBox', annotation('() => []'), false, 'TS2322'],
      ['empty null', 'EmptyBox', annotation('() => null'), false, 'TS2322'],
      ['empty callable', 'EmptyBox', annotation('() => (() => undefined)'), false, 'TS2322'],
      ['empty symbol limitation', 'EmptyBox', annotation('() => ({ [Symbol()]: 1 })'), true],
      ['wrong export', 'Shared', annotation('(input) => input').replace('export const implement', 'export const other'), false, 'TS2305'],
      ['string primitive', 'Text', annotation('(input) => input'), true],
      ['number primitive', 'Numeric', annotation('(input) => input'), true],
      ['boolean primitive', 'Flag', annotation('(input) => input'), true],
      ['prefix collision', 'Collision', annotation('(input) => ({ value: input.z })'), true]
    ];
    expect(await readFile(path.join(root, 'packages/Projection/Shared/generated/contract.d.ts'), 'utf8')).toBe(
      'export type Record_Input = {\n  "a": number;\n  "enabled": boolean;\n  "z": string;\n};\n\nexport type Input = Record_Input;\nexport type Result = Record_Input;\nexport type Implementation = (input: Input) => Result | Promise<Result>;\n');
    expect(await readFile(path.join(root, 'packages/Projection/Collision/generated/contract.d.ts'), 'utf8')).toContain('export type Record_Record_Input');
    for (const [index, [name, box, code, expected, diagnostic]] of cases.entries()) {
      const dir = await workspace(root, `case-${index}`, path.join(root, `packages/Projection/${box}`), code);
      const compiled = compile(dir);
      expect(compiled.ok, `${name}: ${compiled.diagnostics}`).toBe(expected);
      if (diagnostic) expect(compiled.diagnostics, name).toContain(diagnostic);
      if (expected) {
        const js = await readFile(path.join(dir, 'built/candidate/implementation.js'), 'utf8');
        expect(js).not.toContain('contract.js');
        // Import only: the throwing seed is deliberately never invoked.
        const code = `import assert from 'node:assert/strict'; const m = await import(${JSON.stringify(pathToFileURL(path.join(dir, 'built/consumer.js')).href)}); assert.equal(typeof m.implement, 'function');`;
        execFileSync(process.execPath, ['--input-type=module', '--eval', code], { cwd: dir, stdio: 'pipe' });
      }
    }
  } finally { await rm(root, { recursive: true, force: true }); }
}, 120_000);

it('AC-06/07: separate trusted packages compile and wire without repairs; public consumption forbids frontend/root/director loading', async () => {
  execFileSync('npm', ['run', 'build', '--silent'], { cwd: repository, stdio: 'pipe' });
  const root = await mkdtemp(path.join(os.tmpdir(), 'bound-wiring-'));
  try {
    await deriveHandoffs({ root: repository, binding: 'tests/fixtures/handoff/input.json', output: path.join(root, 'packages'), selection: 'all' });
    const load = await workspace(root, 'load', path.join(root, 'packages/GreetingSystem/LoadUser'), await readFile('tests/fixtures/handoff/load-implementation.txt', 'utf8'));
    const greet = await workspace(root, 'greet', path.join(root, 'packages/GreetingSystem/Greeter'), await readFile('tests/fixtures/handoff/greet-implementation.txt', 'utf8'));
    expect(compile(load)).toEqual({ ok: true, diagnostics: '' });
    expect(compile(greet)).toEqual({ ok: true, diagnostics: '' });
    // Consume only strict codec/runtime public built entries and independent emitted fixtures.
    const loader = `export async function resolve(s,c,next) {
      if (['@boundscript/compiler','@boundscript/language','langium'].includes(s)) throw Error('Forbidden import '+s);
      const r = await next(s,c);
      if (/\\/(?:language|langium)\\//.test(r.url) || r.url.endsWith('/compiler/dist/index.js')) throw Error('Forbidden module '+r.url);
      return r;
    }`;
    const url = (file: string) => JSON.stringify(pathToFileURL(file).href);
    const code = `
      import assert from 'node:assert/strict';
      import { register } from 'node:module';
      import { readFile } from 'node:fs/promises';
      register('data:text/javascript,' + encodeURIComponent(${JSON.stringify(loader)}), import.meta.url);
      const { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec } = await import(${url(path.join(repository, 'packages/compiler/dist/box-spec-json.js'))});
      const { verifyBoxImplementation, BoundScriptRuntime } = await import(${url(path.join(repository, 'packages/runtime/dist/index.js'))});
      BoundScriptRuntime.prototype.execute = () => { throw Error('No director'); };
      const load = await import(${url(path.join(load, 'built/consumer.js'))});
      const greet = await import(${url(path.join(greet, 'built/consumer.js'))});
      async function spec(file) {
        const json = await readFile(file, 'utf8'); const parsed = parseBoxDevelopmentSpec(json);
        assert.equal(parsed.ok, true); assert.equal(serializeBoxDevelopmentSpec(parsed.spec), json); return parsed.spec;
      }
      const loadSpec = await spec(${JSON.stringify(path.join(load, 'handoff/contract.box-spec.json'))});
      const greetSpec = await spec(${JSON.stringify(path.join(greet, 'handoff/contract.box-spec.json'))});
      // Prewritten wiring, fixed input and human-owned expected outputs; no interface repair.
      const loaded = await verifyBoxImplementation(loadSpec, load.implement, '123');
      assert.deepEqual(loaded, { ok: true, output: { id: '123', name: 'World', active: true, score: 7 } });
      const greeted = await verifyBoxImplementation(greetSpec, greet.implement, loaded.output);
      assert.deepEqual(greeted, { ok: true, output: { message: 'Hello, World!', recipientId: '123' } });
      const bad = await verifyBoxImplementation(greetSpec, () => ({ message: '' }), loaded.output);
      assert.equal(bad.failure.kind, 'invalid-output');
      console.log('Independent packages and trusted wiring passed');
    `;
    expect(execFileSync(process.execPath, ['--input-type=module', '--eval', code], { cwd: root, encoding: 'utf8' }).trim()).toBe('Independent packages and trusted wiring passed');
  } finally { await rm(root, { recursive: true, force: true }); }
}, 30_000);
