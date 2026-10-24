import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { afterEach, describe, expect, it } from 'vitest';

import { runBoundCli } from '@boundscript/cli';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { parseBoundScript } from '@boundscript/language';

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((path) => rm(path, { recursive: true })));
});

describe('first executable BoundScript program', () => {
  it('executes the minimal hello world example', async () => {
    const output = captureIo();

    const exitCode = await runBoundCli(['examples/hello-minimal.bound'], output.io);

    expect(exitCode).toBe(0);
    expect(output.stdout()).toBe('Hello, World!\n');
    expect(output.stderr()).toBe('');
  });

  it('reports invalid syntax with a source location and fails', async () => {
    const directory = await mkdtemp(join(tmpdir(), 'boundscript-'));
    temporaryDirectories.push(directory);
    const sourcePath = join(directory, 'broken.bound');
    await writeFile(
      sourcePath,
      [
        'system Broken {',
        '    director Main {',
        '        on start {',
        '            print("missing parenthesis"',
        '        }',
        '    }',
        '}'
      ].join('\n')
    );
    const output = captureIo();

    const exitCode = await runBoundCli([sourcePath], output.io);

    expect(exitCode).toBe(1);
    expect(output.stdout()).toBe('');
    expect(output.stderr()).toContain(`${sourcePath}:5:9: error language.parser-error`);
    expect(output.stderr()).toContain("Expecting token of type ')' but found `}`.");
  });

  it('compiles the same AST into identical artifacts', async () => {
    const parsed = parseBoundScript({
      uri: 'memory:deterministic.bound',
      text: 'system Demo { director Main { on start { print("same") } } }'
    });
    expect(parsed.program?.$type).toBe('SystemNode');
    expect(parsed.program?.director.$type).toBe('DirectorNode');
    expect(parsed.program?.director.start.statements[0]?.$type).toBe('PrintStatementNode');
    const compiler = new BoundScriptCompiler();

    const first = await compiler.compile(parsed.program!);
    const second = await compiler.compile(parsed.program!);

    expect(first).toEqual(second);
  });
});

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
