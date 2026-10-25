import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import { DIRECTOR_PROGRAM_VERSION, type ExecutableArtifact } from '@boundscript/artifact';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend, parseBoundScript } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementations } from '@boundscript/runtime';
import { runStructuredTypesDemo } from '../examples/structured-types/host.js';
import { loadUser } from '../examples/structured-types/load-user.js';
import { greet } from '../examples/structured-types/greeter.js';
import type { Greeting, User } from '../examples/structured-types/types.js';

const bindings = { LoadUser: 'structured.load-user', Greeter: 'structured.greeter', Display: 'structured.display' };
const example = () => readFile('examples/structured-types.bound', 'utf8');
const userValue = () => ({ id: '123', name: 'World', active: true, score: 7 });
const greetingValue = () => ({ message: 'Hello, World!', recipientId: '123' });

function parse(text: string) {
  const parsed = parseBoundScript({ uri: 'memory:structured.bound', text });
  expect(parsed.diagnostics).toEqual([]);
  if (!parsed.program) throw new Error('Expected a parsed program.');
  return parsed.program;
}

async function compile(text?: string) {
  const result = await new BoundScriptCompiler().compile(parse(text ?? await example()), bindings);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  return result.artifact;
}

function execute(artifact: ExecutableArtifact, implementations: BoxImplementations) {
  return new BoundScriptRuntime(
    { writeLine: () => { throw new Error('Structured composition must not use print.'); } }, implementations
  ).execute(artifact, { entrypoint: 'start' });
}

function defaults(): BoxImplementations {
  return { 'structured.load-user': loadUser, 'structured.greeter': greet, 'structured.display': () => undefined };
}

describe('structured box contracts', () => {
  it('runs the shipped three-box demo', async () => {
    const output: string[] = [];
    await runStructuredTypesDemo({ writeLine: (value) => output.push(value) });
    expect(output).toEqual(['Hello, World!']);
  });

  it('awaits each independent implementation and transfers the actual records in order', async () => {
    const events: string[] = [];
    const user = userValue();
    const greeting = greetingValue();
    await execute(await compile(), {
      'structured.load-user': async (id: string) => {
        expect(id).toBe('123'); events.push('load:start');
        await Promise.resolve(); events.push('load:end'); return user;
      },
      'structured.greeter': async (input: User) => {
        expect(input).toBe(user); expect(input).toEqual(userValue()); events.push('greet:start');
        await Promise.resolve(); events.push('greet:end'); return greeting;
      },
      'structured.display': async (input: Greeting) => {
        expect(input).toBe(greeting); expect(input).toEqual(greetingValue()); events.push('display:start');
        await Promise.resolve(); events.push('display:end');
      }
    });
    expect(events).toEqual(['load:start', 'load:end', 'greet:start', 'greet:end', 'display:start', 'display:end']);
  });

  it('emits deterministic JSON-only resolved metadata, without ASTs or implementation code', async () => {
    const source = await example();
    const artifact = await compile(source);
    expect(await compile(source.replaceAll('\n', '\r\n'))).toEqual(artifact);
    const reorderedBindings = await new BoundScriptCompiler().compile(parse(source), {
      Display: 'structured.display', Greeter: 'structured.greeter', LoadUser: 'structured.load-user'
    });
    expect(reorderedBindings.ok && reorderedBindings.artifact).toEqual(artifact);
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    expect(program.version).toBe(DIRECTOR_PROGRAM_VERSION);
    expect(artifact.version).toBe(1);
    const userType = { kind: 'record', name: 'User', fields: [
      { name: 'id', type: 'string' }, { name: 'name', type: 'string' },
      { name: 'active', type: 'boolean' }, { name: 'score', type: 'number' }
    ] };
    expect(program.instructions[0].resultType).toEqual(userType);
    expect(program.instructions[1].inputType).toEqual(userType);
    expect(program.instructions[1].argument).toEqual({ kind: 'variable', name: 'user' });
    expect(program.instructions[0].argument).toEqual({ kind: 'literal', value: '123' });
    const json = JSON.stringify(program);
    expect(json).not.toContain('$');
    expect(json).not.toContain('function');
    expect(json).not.toContain('return');
    await execute(withProgram(artifact, program), defaults());
  });

  it.each([
    ['unknown-type', 'load(id: string): User', 'load(id: string): Missing', 'Missing'],
    ['unknown-type', 'greet(user: User)', 'greet(user: Missing)', 'Missing'],
    ['unknown-type', 'score: number', 'score: Missing', 'Missing'],
    ['duplicate-type', 'type Greeting {', 'type User {} type Greeting {', 'User'],
    ['duplicate-field', 'score: number', 'score: number score: number', 'score'],
    ['invalid-field-type', 'score: number', 'score: void', 'void'],
    ['invalid-field-type', 'score: number', 'score: Greeting', 'Greeting'],
    ['void-input', 'load(id: string)', 'load(id: void)', 'void'],
    ['incompatible-argument', 'Greeter.greet(user)', 'Greeter.greet("user")', '"user"'],
    ['incompatible-argument', 'Display.show(greeting)', 'Display.show(user)', 'user'],
    ['incompatible-print', 'Display.show(greeting)', 'print(greeting)', 'greeting'],
    ['unassigned-result', 'let user = LoadUser.load("123")', 'LoadUser.load("123")', 'load']
  ])('rejects %s before compilation, with a source range', async (code, before, after, identifier) => {
    const text = (await example()).replace(before, after);
    const program = parse(text);
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    const diagnostic = diagnostics.find((candidate) => candidate.code === `language.${code}`);
    expect(diagnostic).toBeDefined();
    expect(text.slice(diagnostic!.range!.start.offset, diagnostic!.range!.end.offset)).toBe(identifier);
    const compiled = await new BoundScriptCompiler().compile(program, bindings);
    expect(compiled.ok).toBe(false);
    expect(compiled).not.toHaveProperty('artifact');
    expect(compiled.diagnostics).toEqual(diagnostics);
  });

  it('uses named record identity rather than accepting unrelated records with the same fields', async () => {
    const text = (await example()).replace('type Greeting {', 'type OtherUser { id: string name: string active: boolean score: number } type Greeting {')
      .replace('greet(user: User)', 'greet(user: OtherUser)');
    const result = await new BoundScriptCompiler().compile(parse(text), bindings);
    expect(result.ok).toBe(false);
    expect(result.diagnostics).toContainEqual(expect.objectContaining({ code: 'language.incompatible-argument' }));
  });

  it.each([
    [undefined, 'expected record, got undefined'],
    [null, 'expected record, got null'],
    [false, 'expected record, got boolean'],
    [[], 'expected record, got array'],
    ['not a record', 'expected record, got string'],
    [42, 'expected record, got number'],
    [{ id: '123', name: 'World', score: 7 }, 'missing required field "active"'],
    [{ ...userValue(), active: 'yes' }, 'field "active" expected boolean, got string'],
    [{ ...userValue(), score: '7' }, 'field "score" expected number, got string'],
    [{ ...userValue(), score: NaN }, 'field "score" expected number, got non-finite number'],
    [{ ...userValue(), id: 123 }, 'field "id" expected string, got number'],
    [{ ...userValue(), name: null }, 'field "name" expected string, got null'],
    [{ ...userValue(), extra: true }, 'unexpected field "extra"'],
    [Object.assign(Object.create({ active: true }), { id: '123', name: 'World', score: 7 }), 'missing required field "active"']
  ])('rejects invalid record outputs at the producing boundary: %j', async (value, problem) => {
    let nextCalled = false;
    await expect(execute(await compile(), {
      ...defaults(), 'structured.load-user': async () => value,
      'structured.greeter': () => { nextCalled = true; return greetingValue(); }
    })).rejects.toThrow(`Box "LoadUser.load" output expected "User": ${problem}`);
    expect(nextCalled).toBe(false);
  });

  it('rejects invalid downstream outputs and incorrect void results with box/operation context', async () => {
    const artifact = await compile();
    await expect(execute(artifact, { ...defaults(), 'structured.greeter': () => userValue() }))
      .rejects.toThrow('Box "Greeter.greet" output expected "Greeting": missing required field "message"');
    await expect(execute(artifact, { ...defaults(), 'structured.display': () => 'not void' }))
      .rejects.toThrow('Box "Display.show" output expected "void", got string');
  });

  it.each([
    [(input: User) => { Object.assign(input, { active: 'invalid' }); }, 'field "active" expected boolean, got string'],
    [(input: User) => { Reflect.deleteProperty(input, 'score'); }, 'missing required field "score"']
  ] as const)('revalidates record inputs on each call, including host-mutated records', async (mutate, problem) => {
    const text = (await example()).replace('Display.show(greeting)', 'let second = Greeter.greet(user) Display.show(second)');
    const user = userValue();
    let calls = 0;
    await expect(execute(await compile(text), {
      ...defaults(), 'structured.load-user': () => user,
      'structured.greeter': (input: User) => {
        calls += 1;
        mutate(input);
        return greetingValue();
      }
    })).rejects.toThrow(`Box "Greeter.greet" input expected "User": ${problem}`);
    expect(calls).toBe(1);
  });

  it('checks runtime inputs even when instruction metadata was externally altered', async () => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    program.instructions[0].resultType = 'string';
    let called = false;
    await expect(execute(withProgram(artifact, program), {
      ...defaults(), 'structured.load-user': () => 'wrong record',
      'structured.greeter': () => { called = true; return greetingValue(); }
    })).rejects.toThrow('Box "Greeter.greet" input expected "User": expected record, got string');
    expect(called).toBe(false);
  });

  it.each(['number', 'boolean'])('supports primitive %s results and variable inputs without coercion', async (type) => {
    const text = `system Primitives {
      box Load { operation load(id: string): ${type} }
      box Use { operation use(value: ${type}): void }
      director Main { on start { let value = Load.load("id") Use.use(value) } }
    }`;
    const result = await new BoundScriptCompiler().compile(parse(text), { Load: 'load', Use: 'use' });
    if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
    const value = type === 'number' ? 0 : false;
    const received: unknown[] = [];
    await execute(result.artifact, { load: () => value, use: (input: unknown) => { received.push(input); } });
    expect(received).toEqual([value]);
    await expect(execute(result.artifact, { load: () => String(value), use: () => undefined }))
      .rejects.toThrow(`Box "Load.load" output expected "${type}": got string`);
    const incompatible = await new BoundScriptCompiler().compile(parse(text.replace('Use.use(value)', 'Use.use("value")')), { Load: 'load', Use: 'use' });
    expect(incompatible.ok).toBe(false);
    expect(incompatible.diagnostics).toContainEqual(expect.objectContaining({ code: 'language.incompatible-argument' }));
  });

  it.each([
    { kind: 'record', name: 'Bad', fields: [{ name: 'nested', type: 'User' }] },
    { kind: 'record', name: 'Bad', fields: [{ name: 'x', type: 'void' }] },
    { kind: 'record', name: 'Bad', fields: [{ name: 'x', type: 'string' }, { name: 'x', type: 'number' }] },
    'Unknown', 'void'
  ])('rejects invalid serialized input type metadata: %j', async (inputType) => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    program.instructions[0].inputType = inputType;
    await expect(execute(withProgram(artifact, program), defaults())).rejects.toThrow('unsupported structure');
  });

  it.each([
    'type User { names: string[] }',
    'type User { name?: string }',
    'type User { name: string | number }',
    'type User { child: { name: string } }'
  ])('rejects structured syntax beyond flat required fields: %s', (declaration) => {
    const parsed = parseBoundScript({
      uri: 'memory:unsupported.bound',
      text: `system Unsupported { ${declaration} director Main { on start {} } }`
    });
    expect(parsed.program).toBeUndefined();
    expect(parsed.diagnostics.length).toBeGreaterThan(0);
  });

  it.each([1, 2, 999])('rejects unsupported instruction version %s', async (version) => {
    const artifact = await compile();
    await expect(execute(withProgram(artifact, { version, instructions: [] }), defaults())).rejects.toThrow('unsupported structure');
  });
});

function withProgram(artifact: ExecutableArtifact, program: unknown): ExecutableArtifact {
  return { ...artifact, assets: artifact.assets.map((asset) => ({
    ...asset, bytes: new TextEncoder().encode(JSON.stringify(program))
  })) };
}
