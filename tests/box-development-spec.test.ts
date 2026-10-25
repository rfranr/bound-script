import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import type { RecordType } from '@boundscript/artifact';
import { BoundScriptCompiler, extractBoxDevelopmentSpec } from '@boundscript/compiler';
import { parseBoundScript, validateBoundScript, type SystemNode } from '@boundscript/language';

const example = () => readFile('examples/structured-types.bound', 'utf8');
const userType: RecordType = {
  kind: 'record', name: 'User', fields: [
    { name: 'id', type: 'string' }, { name: 'name', type: 'string' },
    { name: 'active', type: 'boolean' }, { name: 'score', type: 'number' }
  ]
};
const greetingType: RecordType = {
  kind: 'record', name: 'Greeting', fields: [
    { name: 'message', type: 'string' }, { name: 'recipientId', type: 'string' }
  ]
};
const postcondition = { kind: 'string-not-equal', target: { kind: 'field', name: 'message' }, value: '' };

function parse(text: string, uri = 'memory:box-spec.bound'): SystemNode {
  const parsed = parseBoundScript({ uri, text });
  expect(parsed.diagnostics).toEqual([]);
  if (!parsed.program) throw new Error('Expected parsed source.');
  return parsed.program;
}

function extract(program: SystemNode, name: string) {
  const result = extractBoxDevelopmentSpec(program, name);
  expect(result.ok).toBe(true);
  expect(result.diagnostics).toEqual([]);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  return result.spec;
}

describe('in-memory box development specification extraction', () => {
  it('extracts a complete Greeter contract without implementation bindings or source machinery', async () => {
    const program = parse(await example(), '/private/source/path.bound');
    const spec = extract(program, 'Greeter');
    // Exact shape excludes AST/CST, paths, director instructions, implementation IDs and unrelated declarations.
    expect(spec).toEqual({
      format: 'boundscript/box-development-spec', version: 1,
      system: 'GreetingSystem', box: 'Greeter',
      operation: {
        name: 'greet', input: { name: 'user', type: userType },
        resultType: greetingType, postcondition
      }
    });
    expect(JSON.parse(JSON.stringify(spec))).toEqual(spec);
    expect(program.$cstNode).toBeDefined();
    expect(program.types[0]?.$type).toBe('RecordTypeNode');
  });

  it('extracts string-to-record LoadUser even when the box is not invoked', async () => {
    const text = (await example()).replace(
      'let user = LoadUser.load("123")\n            let greeting = Greeter.greet(user)\n            Display.show(greeting)', ''
    );
    const program = parse(text);
    expect(program.director.start.statements).toEqual([]);
    expect(extract(program, 'LoadUser')).toEqual({
      format: 'boundscript/box-development-spec', version: 1,
      system: 'GreetingSystem', box: 'LoadUser',
      operation: { name: 'load', input: { name: 'id', type: 'string' }, resultType: userType }
    });
    // Extraction succeeds even though ordinary compilation still requires all host bindings.
    const compilation = await new BoundScriptCompiler().compile(program);
    expect(compilation.ok).toBe(false);
    expect(compilation.diagnostics.every((diagnostic) => diagnostic.code === 'compiler.missing-implementation')).toBe(true);
  });

  it.each([
    ['string', 'string'], ['number', 'number'], ['boolean', 'boolean'],
    ['string', 'void']
  ])('resolves primitive/void interface %s → %s without an invocation', (inputType, resultType) => {
    const program = parse(`system Primitive {
      box Selected { operation run(value: ${inputType}): ${resultType} }
      director Main { on start {} }
    }`);
    const spec = extract(program, 'Selected');
    expect(spec.operation).toEqual({ name: 'run', input: { name: 'value', type: inputType }, resultType });
    expect(spec.operation).not.toHaveProperty('postcondition');
  });

  it('extracts string-result postconditions, retaining decoded comparison literals', () => {
    const program = parse(`system Strings {
      box Selected { operation run(value: string): string ensure result != "forbidden\\nvalue" }
      director Main { on start {} }
    }`);
    expect(extract(program, 'Selected').operation).toEqual({
      name: 'run', input: { name: 'value', type: 'string' }, resultType: 'string',
      postcondition: { kind: 'string-not-equal', target: { kind: 'result' }, value: 'forbidden\nvalue' }
    });
  });

  it('is unaffected by whitespace, source URI, unrelated valid declarations or director statements', async () => {
    const text = await example();
    const expected = extract(parse(text), 'Greeter');
    const modified = text.replace('    type User {', '    type Unrelated { field: boolean }\n    type User {')
      .replace('    box LoadUser {', '    box Other { operation other(value: number): void }\n    box LoadUser {')
      .replace('            Display.show(greeting)', '            Display.show(greeting)\n            print("unrelated")')
      .replaceAll('\n', '\r\n');
    expect(extract(parse(modified, 'memory:another-location.bound'), 'Greeter')).toEqual(expected);
    expect(extract(parse(text), 'Greeter')).toEqual(expected);
  });

  it('preserves nominal record names even when different records have identical fields', () => {
    const program = parse(`system Named {
      type First { value: string }
      type Second { value: string }
      box Selected { operation convert(input: First): Second }
      director Main { on start {} }
    }`);
    expect(extract(program, 'Selected').operation).toEqual({
      name: 'convert', input: { name: 'input', type: { kind: 'record', name: 'First', fields: [{ name: 'value', type: 'string' }] } },
      resultType: { kind: 'record', name: 'Second', fields: [{ name: 'value', type: 'string' }] }
    });
  });

  it('creates detached descriptors rather than retaining references to AST fields', async () => {
    const program = parse(await example());
    const spec = extract(program, 'Greeter');
    program.types.find((type) => type.name === 'User')!.fields.find((field) => field.name === 'score')!.type = 'boolean';
    expect(spec.operation.input.type).toEqual(userType);
    expect(extract(program, 'Greeter').operation.input.type).not.toEqual(userType);
  });

  it('reports unknown selection without a partial spec or an invented source location', async () => {
    const result = extractBoxDevelopmentSpec(parse(await example()), 'Missing');
    expect(result).toEqual({
      ok: false, diagnostics: [{
        code: 'compiler.unknown-box', message: 'Unknown box "Missing" in system "GreetingSystem".', severity: 'error'
      }]
    });
    expect(result).not.toHaveProperty('spec');
  });

  it.each([
    ['unknown-type', 'score: number', 'score: Missing'],
    ['unknown-type', 'greet(user: User)', 'greet(user: Missing)'],
    ['unknown-type', 'greet(user: User): Greeting', 'greet(user: User): Missing'],
    ['duplicate-type', 'type Greeting {', 'type User {} type Greeting {'],
    ['duplicate-field', 'score: number', 'score: number score: boolean'],
    ['invalid-field-type', 'score: number', 'score: Greeting'],
    ['void-input', 'greet(user: User)', 'greet(user: void)'],
    ['duplicate-box', 'box LoadUser {', 'box Greeter { operation other(value: string): void } box LoadUser {'],
    ['ensure-unknown-field', 'ensure result.message', 'ensure result.unknown'],
    ['ensure-non-string-field', 'operation load(id: string): User', 'operation load(id: string): User ensure result.score != ""'],
    ['ensure-invalid-target', 'ensure result.message', 'ensure result'],
    ['ensure-void-result', 'operation show(greeting: Greeting): void', 'operation show(greeting: Greeting): void ensure result != ""'],
    ['unknown-variable', 'Display.show(greeting)', 'Display.show(missing)'],
    ['incompatible-argument', 'Display.show(greeting)', 'Display.show(user)']
  ])('rejects whole-system %s errors with preserved diagnostic ranges and no partial spec', async (code, before, after) => {
    const program = parse((await example()).replace(before, after));
    const diagnostics = validateBoundScript(program);
    expect(diagnostics).toContainEqual(expect.objectContaining({ code: `language.${code}`, range: expect.any(Object) }));
    const result = extractBoxDevelopmentSpec(program, 'Greeter');
    expect(result).toEqual({ ok: false, diagnostics });
    expect(result).not.toHaveProperty('spec');
  });

  it('rejects an invalid unrelated, unused box declaration', async () => {
    const text = (await example()).replace('    box LoadUser {',
      '    box Unrelated { operation run(value: Missing): void }\n    box LoadUser {');
    const result = extractBoxDevelopmentSpec(parse(text), 'Greeter');
    expect(result.ok).toBe(false);
    expect(result).not.toHaveProperty('spec');
    expect(result.diagnostics).toContainEqual(expect.objectContaining({ code: 'language.unknown-type' }));
  });

  it('matches declaration-derived instruction metadata for every box in ordinary compilation', async () => {
    const program = parse(await example());
    const compilation = await new BoundScriptCompiler().compile(program, {
      LoadUser: 'private.load', Greeter: 'private.greeter', Display: 'private.display'
    });
    if (!compilation.ok) throw new Error(JSON.stringify(compilation.diagnostics));
    const director = JSON.parse(new TextDecoder().decode(compilation.artifact.assets[0]!.bytes));
    for (const instruction of director.instructions) {
      const spec = extract(program, instruction.box);
      expect(spec.operation.name).toBe(instruction.boxOperation);
      expect(spec.operation.input.type).toEqual(instruction.inputType);
      expect(spec.operation.resultType).toEqual(instruction.resultType);
      expect(spec.operation.postcondition).toEqual(instruction.postcondition);
      expect(spec).not.toHaveProperty('implementation');
    }
  });
});
