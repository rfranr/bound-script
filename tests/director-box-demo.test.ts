import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { afterEach, describe, expect, it } from 'vitest';

import { RuntimeExecutionError } from '@boundscript/runtime';
import { runDirectorBoxDemo } from '../examples/director-box/host.js';
import { greet } from '../examples/director-box/greeter.js';

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((path) => rm(path, { recursive: true })));
});

describe('executable Director → Box demo host', () => {
  it('runs the actual example with the separate default Greeter implementation', async () => {
    let stdout = '';

    await runDirectorBoxDemo({ writeLine: (value) => { stdout += `${value}\n`; } });

    expect(stdout).toBe('Hello, World!\n');
  });

  it('reports an identifiable failure when the runtime implementation is missing', async () => {
    const output: string[] = [];
    const execution = runDirectorBoxDemo({ writeLine: (value) => output.push(value) }, {});

    await expect(execution).rejects.toBeInstanceOf(RuntimeExecutionError);
    await expect(execution).rejects.toThrow('Missing implementation "demo.greeter".');
    expect(output).toEqual([]);
  });

  it('uses the source argument and prints the implementation result, not hardcoded host output', async () => {
    const source = await readFile('examples/director-box.bound', 'utf8');
    const sourcePath = await temporarySource(source.replace('"World"', '"BoundScript"'));
    const inputs: string[] = [];
    const output: string[] = [];

    await runDirectorBoxDemo(
      { writeLine: (value) => output.push(value) },
      { 'demo.greeter': (input) => { inputs.push(input); return greet(input); } },
      sourcePath
    );

    expect(inputs).toEqual(['BoundScript']);
    expect(output).toEqual(['Hello, BoundScript!']);
  });

  it.each([
    ['syntax', 'system Broken {', 'language.parser-error'],
    ['semantic', 'system Broken { director Main { on start { print(missing) } } }', 'language.unknown-variable']
  ])('rejects %s errors before execution', async (_kind, source, code) => {
    const output: string[] = [];
    await expect(runDirectorBoxDemo(
      { writeLine: (value) => output.push(value) },
      undefined,
      await temporarySource(source)
    )).rejects.toThrow(code);
    expect(output).toEqual([]);
  });
});

async function temporarySource(source: string): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), 'boundscript-demo-'));
  temporaryDirectories.push(directory);
  const path = join(directory, 'demo.bound');
  await writeFile(path, source);
  return path;
}
