import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { runBoundCli } from '@boundscript/cli';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { parseBoundScript } from '@boundscript/language';
import { BoundScriptRuntime } from '@boundscript/runtime';

const fixtureRoot = fileURLToPath(new URL('./fixtures/', import.meta.url));

const validFixtures = [
  {
    name: 'hello',
    expected: ['Hello, World!']
  },
  {
    name: 'multiple-prints',
    expected: ['first', 'second', 'third']
  },
  {
    name: 'escaped-strings',
    expected: ['line one\nline two', 'quoted: "hello"', 'slash: \\']
  },
  {
    name: 'whitespace',
    expected: ['formatted', 'after blank line']
  }
] as const;

const invalidFixtures = [
  { name: 'missing-brace', expectedMessage: "Expecting token of type '}'" },
  { name: 'unknown-statement', expectedMessage: "Expecting token of type '.'" },
  { name: 'malformed-string', expectedMessage: 'unexpected character' }
] as const;

describe('BoundScript language conformance fixtures', () => {
  it.each(validFixtures)('executes valid fixture: $name', async ({ name, expected }) => {
    const artifact = await compileFixture(`valid/${name}.bound`);
    const output: string[] = [];
    const runtime = new BoundScriptRuntime({ writeLine: (value) => output.push(value) });

    await runtime.execute(artifact, { entrypoint: 'start' });

    expect(output).toEqual(expected);
  });

  it.each(invalidFixtures)('rejects invalid fixture: $name', async ({ name, expectedMessage }) => {
    const source = await readFixture(`invalid/${name}.bound`);
    const parsed = parseBoundScript({ uri: `fixture://${name}.bound`, text: source });

    expect(parsed.program).toBeUndefined();
    expect(parsed.diagnostics).not.toHaveLength(0);
    expect(parsed.diagnostics[0]?.message).toContain(expectedMessage);
    expect(parsed.diagnostics[0]?.range?.start.line).toBeGreaterThan(0);

    const output = captureIo();
    const exitCode = await runBoundCli([`${fixtureRoot}/invalid/${name}.bound`], output.io);
    expect(exitCode).toBe(1);
    expect(output.stderr()).toContain('error language.');
  });

  it('changes observable output when a string literal changes', async () => {
    const first = await compileSource('system Demo { director Main { on start { print("before") } } }');
    const second = await compileSource('system Demo { director Main { on start { print("after") } } }');

    expect(await runArtifact(first)).toEqual(['before']);
    expect(await runArtifact(second)).toEqual(['after']);
  });

  it('compiles identical source into identical artifacts', async () => {
    const source = await readFixture('valid/multiple-prints.bound');

    const first = await compileSource(source);
    const second = await compileSource(source);

    expect(first).toEqual(second);
  });
});

async function compileFixture(path: string) {
  return compileSource(await readFixture(path));
}

async function compileSource(text: string) {
  const parsed = parseBoundScript({ uri: 'fixture://source.bound', text });
  expect(parsed.diagnostics).toEqual([]);
  expect(parsed.program).toBeDefined();

  const result = await new BoundScriptCompiler().compile(parsed.program!);
  expect(result.ok).toBe(true);
  if (!result.ok) throw new Error('Expected fixture compilation to succeed.');
  return result.artifact;
}

async function runArtifact(artifact: Awaited<ReturnType<typeof compileSource>>): Promise<string[]> {
  const output: string[] = [];
  const runtime = new BoundScriptRuntime({ writeLine: (value) => output.push(value) });
  await runtime.execute(artifact, { entrypoint: 'start' });
  return output;
}

async function readFixture(path: string): Promise<string> {
  return readFile(`${fixtureRoot}/${path}`, 'utf8');
}

function captureIo(): {
  readonly io: {
    readonly stdout: { write(value: string): void };
    readonly stderr: { write(value: string): void };
  };
  stdout(): string;
  stderr(): string;
} {
  let stdout = '';
  let stderr = '';
  return {
    io: {
      stdout: { write: (value) => { stdout += value; } },
      stderr: { write: (value) => { stderr += value; } }
    },
    stdout: () => stdout,
    stderr: () => stderr
  };
}
