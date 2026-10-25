import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

import { describe, expect, it } from 'vitest';

import { runBoundCli } from '@boundscript/cli';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend, parseBoundScript, type SystemNode } from '@boundscript/language';

const fixturePath = fileURLToPath(new URL('./fixtures/invalid/semantic-errors.bound', import.meta.url));
const expectedErrors = [
  { code: 'duplicate-box', message: 'Duplicate box "Greeter".', line: 3, column: 7, identifier: 'Greeter' },
  { code: 'unknown-box', message: 'Unknown box "Missing".', line: 6, column: 22, identifier: 'Missing' },
  { code: 'unknown-operation', message: 'Unknown operation "missing" on box "Greeter".', line: 7, column: 28, identifier: 'missing' },
  { code: 'unknown-variable', message: 'Unknown variable "unknown".', line: 8, column: 13, identifier: 'unknown' },
  { code: 'duplicate-variable', message: 'Duplicate variable "greeting".', line: 9, column: 11, identifier: 'greeting' },
  { code: 'unknown-variable', message: 'Unknown variable "unknown".', line: 10, column: 13, identifier: 'unknown' }
];

function parse(text: string): SystemNode {
  const parsed = parseBoundScript({ uri: fixturePath, text });
  expect(parsed.diagnostics).toEqual([]);
  if (!parsed.program) throw new Error('Expected syntactically valid fixture.');
  return parsed.program;
}

describe('source-located semantic diagnostics', () => {
  it.each(['\n', '\r\n'])('reports exact identifier ranges with %j line endings', async (newline) => {
    const text = (await readFile(fixturePath, 'utf8')).replaceAll('\n', newline);
    const program = parse(text);
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    const lines = text.split(newline);

    expect(diagnostics).toHaveLength(expectedErrors.length);
    for (const [index, expected] of expectedErrors.entries()) {
      const offset = lines.slice(0, expected.line - 1).reduce((total, line) => total + line.length + newline.length, 0)
        + expected.column - 1;
      expect(diagnostics[index]).toEqual({
        code: `language.${expected.code}`,
        message: expected.message,
        severity: 'error',
        range: {
          start: { line: expected.line, column: expected.column, offset },
          end: {
            line: expected.line,
            column: expected.column + expected.identifier.length,
            offset: offset + expected.identifier.length
          }
        }
      });
      const range = diagnostics[index]!.range!;
      expect(text.slice(range.start.offset, range.end.offset)).toBe(expected.identifier);
    }

    const compiled = await new BoundScriptCompiler().compile(program, { Greeter: 'host.greeter' });
    expect(compiled.ok).toBe(false);
    expect(compiled).not.toHaveProperty('artifact');
    expect(compiled.diagnostics).toEqual(diagnostics);
  });

  it('formats every semantic error with its file, line and column in the CLI', async () => {
    let stdout = '';
    let stderr = '';
    const exitCode = await runBoundCli([fixturePath], {
      stdout: { write: (value) => { stdout += value; } },
      stderr: { write: (value) => { stderr += value; } }
    });

    expect(exitCode).toBe(1);
    expect(stdout).toBe('');
    expect(stderr).toBe(expectedErrors.map((error) =>
      `${fixturePath}:${error.line}:${error.column}: error language.${error.code}: ${error.message}\n`
    ).join(''));
  });

  it('keeps validation usable for AST nodes without source locations', async () => {
    const program = parse('system Synthetic { director Main { on start { print(missing) } } }');
    const { $cstNode, ...statement } = program.director.start.statements[0]!;
    program.director.start.statements = [statement];
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    expect(diagnostics).toEqual([{
      code: 'language.unknown-variable', message: 'Unknown variable "missing".', severity: 'error'
    }]);
    const compiled = await new BoundScriptCompiler().compile(program);
    expect(compiled.ok).toBe(false);
    expect(compiled).not.toHaveProperty('artifact');
    expect(compiled.diagnostics).toEqual(diagnostics);
  });
});
