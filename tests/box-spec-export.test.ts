import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { afterEach, describe, expect, it } from 'vitest';

import { runBoundCli } from '@boundscript/cli';
import { parseBoxDevelopmentSpec } from '@boundscript/compiler';

const directories: string[] = [];
afterEach(async () => {
  await Promise.all(directories.splice(0).map((path) => rm(path, { recursive: true })));
});

async function run(args: readonly string[]) {
  let stdout = '';
  let stderr = '';
  const code = await runBoundCli(args, {
    stdout: { write: (value) => { stdout += value; } }, stderr: { write: (value) => { stderr += value; } }
  });
  return { code, stdout, stderr };
}

async function source(text: string) {
  const directory = await mkdtemp(join(tmpdir(), 'boundscript-spec-'));
  directories.push(directory);
  const path = join(directory, 'source.bound');
  await writeFile(path, text);
  return path;
}

describe('bound spec export', () => {
  it('exports only canonical JSON without requiring host bindings', async () => {
    const args = ['spec', 'examples/structured-types.bound', '--box', 'Greeter'];
    const first = await run(args);
    expect(first).toEqual({ code: 0, stderr: '', stdout: await readFile('examples/specs/greeter.box-spec.json', 'utf8') });
    expect(await run(args)).toEqual(first);
    expect(parseBoxDevelopmentSpec(first.stdout).ok).toBe(true);
    const text = (await readFile('examples/structured-types.bound', 'utf8')).replaceAll('\n', '\r\n');
    expect(await run(['spec', await source(text), '--box', 'Greeter'])).toEqual(first);
  });

  it('exports an unused declaration with no implementation or director invocation', async () => {
    const path = await source('system Unused { box Load { operation load(id: string): string } director Main { on start {} } }');
    const result = await run(['spec', path, '--box', 'Load']);
    expect(result.code).toBe(0);
    expect(result.stderr).toBe('');
    expect(JSON.parse(result.stdout).operation).toEqual({ name: 'load', input: { name: 'id', type: 'string' }, resultType: 'string' });
  });

  it('reports unknown selection on stderr with no JSON output', async () => {
    const result = await run(['spec', 'examples/structured-types.bound', '--box', 'Missing']);
    expect(result.code).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('error compiler.unknown-box: Unknown box "Missing"');
  });

  it.each([
    ['system Broken {', 'language.parser-error'],
    ['system Broken {\n box Selected { operation run(value: Missing): void }\n director Main { on start {} }\n}', 'language.unknown-type'],
    ['system Broken {\n box Selected { operation run(value: void): void ensure result != "" }\n director Main { on start {} }\n}', 'language.ensure-void-result']
  ])('reports invalid source with a source position and no JSON', async (text, code) => {
    const path = await source(text);
    const result = await run(['spec', path, '--box', 'Selected']);
    expect(result.code).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain(`${path}:`);
    expect(result.stderr).toMatch(/:\d+:\d+: error /);
    expect(result.stderr).toContain(code);
  });

  it.each([
    ['spec'], ['spec', 'example.bound'], ['spec', 'example.bound', '--box'],
    ['spec', 'example.bound', '--wrong', 'Greeter'], ['spec', 'example.bound', '--box', 'Greeter', 'extra']
  ])('rejects malformed arguments: %j', async (...args) => {
    const result = await run(args);
    expect(result.code).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('bound spec <source.bound> --box <name>');
  });
});
