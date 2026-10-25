import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import { DIRECTOR_PROGRAM_VERSION, type ExecutableArtifact } from '@boundscript/artifact';
import { BoundScriptCompiler, type BoxBindings } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend, parseBoundScript } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementation } from '@boundscript/runtime';

const source = `system Greeting {
  box Greeter { operation greet(name: string): string }
  director Main { on start {
    let greeting = Greeter.greet("World")
    print(greeting)
  } }
}`;
const bindings = { Greeter: 'host.greeter' };

function parse(text = source) {
  const parsed = parseBoundScript({ uri: 'memory:invocation.bound', text });
  expect(parsed.diagnostics).toEqual([]);
  if (!parsed.program) throw new Error('Expected a parsed program.');
  return parsed.program;
}

async function compile(text = source, resolvedBindings: BoxBindings = bindings) {
  const result = await new BoundScriptCompiler().compile(parse(text), resolvedBindings);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  return result.artifact;
}

function runtime(implementation?: BoxImplementation) {
  const output: string[] = [];
  return {
    output,
    runtime: new BoundScriptRuntime(
      { writeLine: (value) => output.push(value) },
      implementation ? { 'host.greeter': implementation } : {}
    )
  };
}

describe('Director → Box invocation', () => {
  it.each([false, true])('invokes a developer implementation (async: %s)', async (asynchronous) => {
    const text = await readFile('examples/director-box.bound', 'utf8');
    const inputs: string[] = [];
    const host = runtime((input) => {
      inputs.push(input);
      const result = `Hello, ${input}!`;
      return asynchronous ? Promise.resolve(result) : result;
    });

    await host.runtime.execute(await compile(text), { entrypoint: 'start' });

    expect(inputs).toEqual(['World']);
    expect(host.output).toEqual(['Hello, World!']);
  });

  it('preserves sequential calls, variables, and literal prints', async () => {
    const artifact = await compile(source.replace('print(greeting)', `
      print("before")
      let second = Greeter.greet("again")
      print(second)
      print(greeting)
    `));
    const host = runtime((input) => input.toUpperCase());
    await host.runtime.execute(artifact, { entrypoint: 'start' });
    expect(host.output).toEqual(['before', 'AGAIN', 'WORLD']);
  });

  it('compiles deterministically and includes only the resolved implementation ID', async () => {
    const first = await compile();
    expect(await compile()).toEqual(first);
    const program = JSON.parse(new TextDecoder().decode(first.assets[0]!.bytes));
    expect(program.instructions).toEqual([
      { operation: 'invoke', implementation: 'host.greeter', box: 'Greeter', boxOperation: 'greet', inputType: 'string', argument: { kind: 'literal', value: 'World' }, resultType: 'string', result: 'greeting' },
      { operation: 'print-variable', variable: 'greeting' }
    ]);
  });

  it.each([
    ['unknown-box', source.replace('= Greeter.greet', '= Missing.greet')],
    ['unknown-operation', source.replace('= Greeter.greet', '= Greeter.missing')],
    ['unknown-variable', source.replace('print(greeting)', 'print(missing)')],
    ['unknown-variable', source.replace('greet("World")', 'greet(greeting)')],
    ['unknown-variable', source.replace('let greeting =', 'print(greeting) let greeting =')],
    ['duplicate-variable', source.replace('print(greeting)', 'let greeting = Greeter.greet("again")')],
    ['duplicate-box', source.replace('director Main', 'box Greeter { operation greet(name: string): string } director Main')]
  ])('rejects %s in both frontend validation and compilation', async (code, text) => {
    const program = parse(text);
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    expect(diagnostics).toContainEqual(expect.objectContaining({ code: `language.${code}`, severity: 'error' }));
    const result = await new BoundScriptCompiler().compile(program, bindings);
    expect(result.ok).toBe(false);
    expect(result).not.toHaveProperty('artifact');
    expect(result.diagnostics).toEqual(diagnostics);
  });

  it.each([{}, { Greeter: '' }, { Greeter: '   ' }])('requires an explicit implementation binding: %j', async (resolvedBindings) => {
    const result = await new BoundScriptCompiler().compile(parse(), resolvedBindings);
    expect(result.ok).toBe(false);
    expect(result).not.toHaveProperty('artifact');
    expect(result.diagnostics).toContainEqual({
      code: 'compiler.missing-implementation',
      message: 'Missing implementation binding for box "Greeter".',
      severity: 'error'
    });
  });

  it('does not treat inherited properties as implementation bindings', async () => {
    const result = await new BoundScriptCompiler().compile(parse(source.replaceAll('Greeter', 'toString')));
    expect(result.ok).toBe(false);
    const artifact = await compile(source, { Greeter: 'toString' });
    const host = runtime();
    await expect(host.runtime.execute(artifact, { entrypoint: 'start' }))
      .rejects.toThrow('Missing implementation "toString".');
  });

  it('reports missing runtime implementations before producing output', async () => {
    const artifact = await compile(source.replace('let greeting', 'print("before") let greeting'));
    const host = runtime();
    await expect(host.runtime.execute(artifact, { entrypoint: 'start' }))
      .rejects.toThrow('Missing implementation "host.greeter".');
    expect(host.output).toEqual([]);
  });

  it.each([
    [() => { throw new Error('broken'); }, 'failed: broken'],
    [async () => { throw new Error('rejected'); }, 'failed: rejected'],
    [(() => 42) as unknown as BoxImplementation, 'must return a string']
  ] as const)('reports implementation failures and invalid results', async (implementation, message) => {
    const host = runtime(implementation);
    await expect(host.runtime.execute(await compile(), { entrypoint: 'start' }))
      .rejects.toThrow(message);
    expect(host.output).toEqual([]);
  });

  it('keeps variables local to an execution', async () => {
    const host = runtime((input) => input);
    const artifact = await compile();
    await host.runtime.execute(artifact, { entrypoint: 'start' });
    const variableOnly = withInstructions(artifact, [{ operation: 'print-variable', variable: 'greeting' }]);
    await expect(host.runtime.execute(variableOnly, { entrypoint: 'start' }))
      .rejects.toThrow('Unknown variable "greeting".');
  });

  it.each([
    { operation: 'invoke', implementation: 'host.greeter', argument: 42, result: 'greeting' },
    { operation: 'invoke', implementation: '', argument: 'World', result: 'greeting' },
    { operation: 'print-variable', variable: 42 },
    { operation: 'unknown' }
  ])('rejects malformed artifact instructions: %j', async (instruction) => {
    const host = runtime((input) => input);
    await expect(host.runtime.execute(withInstructions(await compile(), [instruction]), { entrypoint: 'start' }))
      .rejects.toThrow('unsupported structure');
  });

  it.each([
    source.replace('name: string', 'name: string[]'),
    source.replace('greet(name: string): string', 'greet(name: string, extra: string): string'),
    source.replace('greet("World")', 'greet()'),
    source.replace('greet("World")', 'greet("World", "extra")'),
    source.replace('print(greeting)', 'print("hello" + greeting)')
  ])('rejects syntax outside the minimal subset', (text) => {
    const parsed = parseBoundScript({ uri: 'memory:invalid.bound', text });
    expect(parsed.program).toBeUndefined();
    expect(parsed.diagnostics.length).toBeGreaterThan(0);
  });
});

function withInstructions(artifact: ExecutableArtifact, instructions: readonly unknown[]): ExecutableArtifact {
  return {
    ...artifact,
    assets: artifact.assets.map((asset) => ({
      ...asset,
      bytes: new TextEncoder().encode(JSON.stringify({ version: DIRECTOR_PROGRAM_VERSION, instructions }))
    }))
  };
}
