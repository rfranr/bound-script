import { describe, expect, it } from 'vitest';

import { DIRECTOR_PROGRAM_VERSION, type ExecutableArtifact } from '@boundscript/artifact';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend, parseBoundScript } from '@boundscript/language';
import {
  BoundScriptRuntime, PostconditionViolationError, RuntimeExecutionError, type BoxImplementation
} from '@boundscript/runtime';
import { runStructuredTypesDemo } from '../examples/structured-types/host.js';
import { loadUser } from '../examples/structured-types/load-user.js';

const source = `system Contracts {
  type Greeting { message: string recipientId: string count: number active: boolean }
  box Greeter {
    operation greet(name: string): Greeting
    ensure result.message != ""
  }
  box Display { operation show(greeting: Greeting): void }
  director Main { on start {
    let greeting = Greeter.greet("World")
    Display.show(greeting)
  } }
}`;
const stringSource = source.replaceAll(': Greeting', ': string').replace('result.message', 'result');
const value = (message = 'Hello, World!') => ({ message, recipientId: '123', count: 1, active: true });
const bindings = { Greeter: 'host.greeter', Display: 'host.display' };

function parse(text: string) {
  const result = parseBoundScript({ uri: 'memory:contracts.bound', text });
  expect(result.diagnostics).toEqual([]);
  if (!result.program) throw new Error('Expected parsed source.');
  return result.program;
}

async function compile(text = source) {
  const result = await new BoundScriptCompiler().compile(parse(text), bindings);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  return result.artifact;
}

function execute(artifact: ExecutableArtifact, implementation: BoxImplementation) {
  const displayed: unknown[] = [];
  const runtime = new BoundScriptRuntime(
    { writeLine: () => { throw new Error('Director must not print.'); } },
    { 'host.greeter': implementation, 'host.display': (input: unknown) => { displayed.push(input); } }
  );
  return { displayed, execution: runtime.execute(artifact, { entrypoint: 'start' }) };
}

describe('minimal ensure postconditions', () => {
  it.each([
    ['record', false], ['record', true], ['string', false], ['string', true]
  ] as const)('checks a successful %s result after awaiting the host (async: %s)', async (kind, asynchronous) => {
    const result = kind === 'string' ? 'Hello, World!' : value();
    const events: string[] = [];
    const implementation: BoxImplementation = asynchronous ? async () => {
      events.push('start'); await Promise.resolve(); events.push('end'); return result;
    } : () => { events.push('start', 'end'); return result; };
    const run = execute(await compile(kind === 'string' ? stringSource : source), implementation);
    await run.execution;
    expect(events).toEqual(['start', 'end']);
    expect(run.displayed).toEqual([result]);
    expect(run.displayed[0]).toBe(result);
  });

  it.each(['record', 'string'])('fails a valid %s value with a distinct violation before the next statement', async (kind) => {
    let hostSideEffects = 0;
    const run = execute(await compile(kind === 'string' ? stringSource : source), async () => {
      hostSideEffects += 1;
      await Promise.resolve();
      return kind === 'string' ? '' : value('');
    });
    const error = await run.execution.catch((error: unknown) => error);
    expect(error).toBeInstanceOf(PostconditionViolationError);
    expect(error).toMatchObject({
      name: 'PostconditionViolationError', code: 'runtime.postcondition-violation',
      box: 'Greeter', operation: 'greet', observed: ''
    });
    const target = kind === 'string' ? 'result' : 'result.message';
    expect((error as Error).message).toBe(
      `Postcondition violation for box "Greeter.greet": ensure ${target} != ""; observed ${target} = "".`
    );
    expect(run.displayed).toEqual([]);
    expect(hostSideEffects).toBe(1); // No rollback or side-effect isolation is promised.
  });

  it('uses the extended structured demo host for both passing and failing implementations', async () => {
    const output: string[] = [];
    await runStructuredTypesDemo({ writeLine: (line) => output.push(line) });
    expect(output).toEqual(['Hello, World!']);
    let displayed = false;
    await expect(runStructuredTypesDemo({ writeLine: () => undefined }, {
      'structured.load-user': loadUser,
      'structured.greeter': () => ({ message: '', recipientId: '123' }),
      'structured.display': () => { displayed = true; }
    })).rejects.toBeInstanceOf(PostconditionViolationError);
    expect(displayed).toBe(false);
  });

  it.each([null, 'not a record', { message: '' }, { ...value(), message: 42 }])(
    'checks the entire data contract before the postcondition: %j', async (result) => {
      const run = execute(await compile(), () => result);
      const error = await run.execution.catch((error: unknown) => error);
      expect(error).toBeInstanceOf(RuntimeExecutionError);
      expect(error).not.toBeInstanceOf(PostconditionViolationError);
      expect((error as Error).message).toContain('Box "Greeter.greet" output expected "Greeting"');
      expect(run.displayed).toEqual([]);
    }
  );

  it.each([false, true])('keeps thrown/rejected host errors distinct (async: %s)', async (asynchronous) => {
    const implementation = asynchronous
      ? async () => { throw new Error('host failed'); }
      : () => { throw new Error('host failed'); };
    const run = execute(await compile(), implementation);
    const error = await run.execution.catch((error: unknown) => error);
    expect(error).toBeInstanceOf(RuntimeExecutionError);
    expect(error).not.toBeInstanceOf(PostconditionViolationError);
    expect((error as Error).message).toBe('Implementation "host.greeter" failed: host failed');
    expect(run.displayed).toEqual([]);
  });

  it.each([
    ['ensure-void-result', source.replace('greet(name: string): Greeting', 'greet(name: string): void'), 'result'],
    ['ensure-unknown-field', source.replace('result.message', 'result.unknown'), 'unknown'],
    ['ensure-non-string-field', source.replace('result.message', 'result.count'), 'count'],
    ['ensure-non-string-field', source.replace('result.message', 'result.active'), 'active'],
    ['ensure-invalid-target', source.replace('result.message', 'result'), 'result'],
    ['ensure-invalid-target', source.replace('result.message', 'name'), 'name'],
    ['ensure-invalid-target', stringSource.replace('result !=', 'result.message !='), 'message'],
    ['ensure-invalid-target', stringSource.replace('greet(name: string): string', 'greet(name: string): number'), 'result']
  ])('rejects %s statically with the exact target location', async (code, text, identifier) => {
    const program = parse(text);
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    const diagnostic = diagnostics.find((candidate) => candidate.code === `language.${code}`);
    expect(diagnostic).toBeDefined();
    const column = identifier === 'result' || identifier === 'name' ? 12 : 19;
    const offset = text.indexOf('ensure ') + 'ensure '.length + column - 12;
    expect(diagnostic!.range).toEqual({
      start: { line: 5, column, offset },
      end: { line: 5, column: column + identifier.length, offset: offset + identifier.length }
    });
    const result = await new BoundScriptCompiler().compile(program, bindings);
    expect(result.ok).toBe(false);
    expect(result).not.toHaveProperty('artifact');
    expect(result.diagnostics).toEqual(diagnostics);
  });

  it('serializes a deterministic data-only descriptor and preserves programs without ensures', async () => {
    for (const [text, target] of [[source, { kind: 'field', name: 'message' }], [stringSource, { kind: 'result' }]] as const) {
      const artifact = await compile(text);
      expect(await compile(text.replaceAll('\n', '\r\n'))).toEqual(artifact);
      const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
      expect(program.version).toBe(DIRECTOR_PROGRAM_VERSION);
      expect(artifact.version).toBe(1);
      expect(program.instructions[0].postcondition).toEqual({ kind: 'string-not-equal', target, value: '' });
      expect(JSON.stringify(program.instructions[0].postcondition)).not.toContain('ensure');
      const run = execute(withProgram(artifact, program), () => text === source ? value() : 'hello');
      await run.execution;
      expect(run.displayed).toHaveLength(1);
    }
    const artifact = await compile(source.replace('    ensure result.message != ""\n', ''));
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    expect(program.instructions[0]).not.toHaveProperty('postcondition');
    const run = execute(artifact, () => value(''));
    await run.execution;
    expect(run.displayed).toEqual([value('')]);
  });

  it('preserves result as an ordinary local identifier outside ensure', async () => {
    const text = source.replace('let greeting =', 'let result =').replace('Display.show(greeting)', 'Display.show(result)');
    const run = execute(await compile(text), () => value());
    await run.execution;
    expect(run.displayed).toEqual([value()]);
  });

  it('compares against the declared string literal, including escapes, without expression evaluation', async () => {
    const forbidden = 'line one\n"quoted"';
    const artifact = await compile(stringSource.replace('!= ""', `!= ${JSON.stringify(forbidden)}`));
    const failing = execute(artifact, () => forbidden);
    await expect(failing.execution).rejects.toMatchObject({ observed: forbidden, code: 'runtime.postcondition-violation' });
    const passing = execute(artifact, () => '');
    await passing.execution;
    expect(passing.displayed).toEqual(['']);
  });

  it.each([
    'ensure result.message == ""', 'ensure result.message != name', 'ensure result.message != 0',
    'ensure result.message != "Hello, " + name', 'ensure result.message != "" && true',
    'ensure result.message.length != ""', 'ensure result.message() != ""',
    'ensure result.message != "" ensure result.message != "bad"'
  ])('rejects unsupported contract syntax: %s', (contract) => {
    const parsed = parseBoundScript({ uri: 'memory:unsupported.bound', text: source.replace('ensure result.message != ""', contract) });
    expect(parsed.program).toBeUndefined();
    expect(parsed.diagnostics.length).toBeGreaterThan(0);
  });

  it('does not allow ensure as a director statement', () => {
    const parsed = parseBoundScript({ uri: 'memory:director.bound', text: source.replace('Display.show(greeting)', 'ensure result.message != ""') });
    expect(parsed.program).toBeUndefined();
  });

  it.each([
    null, { kind: 'javascript', expression: 'result.message !== ""' },
    { kind: 'string-not-equal', target: { kind: 'field', name: 'unknown' }, value: '' },
    { kind: 'string-not-equal', target: { kind: 'field', name: 'count' }, value: '' },
    { kind: 'string-not-equal', target: { kind: 'result' }, value: '' },
    { kind: 'string-not-equal', target: { kind: 'field', name: 'message' }, value: 0 }
  ])('rejects unsupported or incompatible artifact descriptors before execution: %j', async (postcondition) => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    program.instructions[0].postcondition = postcondition;
    let called = false;
    const run = execute(withProgram(artifact, program), () => { called = true; return value(); });
    await expect(run.execution).rejects.toThrow('unsupported structure');
    expect(called).toBe(false);
  });

  it('rejects a descriptor on a void instruction and rejects instruction v3', async () => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    program.instructions[1].postcondition = { kind: 'string-not-equal', target: { kind: 'result' }, value: '' };
    await expect(execute(withProgram(artifact, program), () => value()).execution).rejects.toThrow('unsupported structure');
    await expect(execute(withProgram(artifact, { version: 3, instructions: [] }), () => value()).execution).rejects.toThrow('unsupported structure');
  });
});

function withProgram(artifact: ExecutableArtifact, program: unknown): ExecutableArtifact {
  return { ...artifact, assets: artifact.assets.map((asset) => ({
    ...asset, bytes: new TextEncoder().encode(JSON.stringify(program))
  })) };
}
