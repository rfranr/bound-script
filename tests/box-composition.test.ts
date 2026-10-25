import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import { DIRECTOR_PROGRAM_VERSION, type ExecutableArtifact } from '@boundscript/artifact';
import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend, parseBoundScript } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementation, type BoxImplementations } from '@boundscript/runtime';
import { runBoxCompositionDemo } from '../examples/box-composition/host.js';

const bindings = { Greeter: 'demo.greeter', Display: 'demo.display' };
const example = () => readFile('examples/box-composition.bound', 'utf8');

function parse(text: string) {
  const parsed = parseBoundScript({ uri: 'memory:composition.bound', text });
  expect(parsed.diagnostics).toEqual([]);
  if (!parsed.program) throw new Error('Expected a parsed program.');
  return parsed.program;
}

async function compile(text?: string) {
  const compiled = await new BoundScriptCompiler().compile(parse(text ?? await example()), bindings);
  if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));
  return compiled.artifact;
}

function execute(artifact: ExecutableArtifact, implementations: BoxImplementations) {
  return new BoundScriptRuntime(
    { writeLine: () => { throw new Error('Composition must not use built-in print.'); } },
    implementations
  ).execute(artifact, { entrypoint: 'start' });
}

describe('box composition', () => {
  it('runs the shipped demo with separate Greeter and Display implementations', async () => {
    const output: string[] = [];
    await runBoxCompositionDemo({ writeLine: (value) => output.push(value) });
    expect(output).toEqual(['Hello, World!']);
  });

  it.each([false, true])('propagates results to Display exactly once, in order (async: %s)', async (asynchronous) => {
    const events: string[] = [];
    const greeter: BoxImplementation = asynchronous
      ? async (input) => {
          events.push(`greet:${input}`);
          await Promise.resolve();
          events.push('greet:done');
          return `Hello, ${input}!`;
        }
      : (input) => { events.push(`greet:${input}`, 'greet:done'); return `Hello, ${input}!`; };
    const display: BoxImplementation = asynchronous
      ? async (input) => {
          events.push(`show:${input}`);
          await Promise.resolve();
          events.push('show:done');
        }
      : (input) => { events.push(`show:${input}`, 'show:done'); };

    await runBoxCompositionDemo(
      { writeLine: () => { throw new Error('Director must not print.'); } },
      { 'demo.greeter': greeter, 'demo.display': display }
    );

    expect(events).toEqual(['greet:World', 'greet:done', 'show:Hello, World!', 'show:done']);
  });

  it('serializes literal and variable arguments distinctly and awaits void calls before continuing', async () => {
    const source = (await example()).replace('Display.show(message)', 'Display.show(message) Display.show("message")');
    const artifact = await compile(source);
    expect(await compile(source)).toEqual(artifact);
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    expect(program.version).toBe(DIRECTOR_PROGRAM_VERSION);
    expect(program.instructions).toEqual([
      { operation: 'invoke', implementation: 'demo.greeter', box: 'Greeter', boxOperation: 'greet', inputType: 'string', argument: { kind: 'literal', value: 'World' }, resultType: 'string', result: 'message' },
      { operation: 'invoke', implementation: 'demo.display', box: 'Display', boxOperation: 'show', inputType: 'string', argument: { kind: 'variable', name: 'message' }, resultType: 'void' },
      { operation: 'invoke', implementation: 'demo.display', box: 'Display', boxOperation: 'show', inputType: 'string', argument: { kind: 'literal', value: 'message' }, resultType: 'void' }
    ]);
    const events: string[] = [];
    await execute(withProgram(artifact, program), {
      'demo.greeter': (input) => `Hello, ${input}!`,
      'demo.display': async (input) => {
        events.push(`start:${input}`);
        await Promise.resolve();
        events.push(`end:${input}`);
      }
    });
    expect(events).toEqual(['start:Hello, World!', 'end:Hello, World!', 'start:message', 'end:message']);
  });

  it('passes empty string arguments and results without treating them as missing variables', async () => {
    const source = (await example()).replace('"World"', '""');
    const received: string[] = [];
    await execute(await compile(source), {
      'demo.greeter': (input) => { expect(input).toBe(''); return ''; },
      'demo.display': (input) => { received.push(input); }
    });
    expect(received).toEqual(['']);
  });

  it('allows variable arguments to string-returning operations', async () => {
    const source = (await example()).replace('Display.show(message)', 'let second = Greeter.greet(message) Display.show(second)');
    const received: string[] = [];
    await execute(await compile(source), {
      'demo.greeter': (input) => `[${input}]`,
      'demo.display': (input) => { received.push(input); }
    });
    expect(received).toEqual(['[[World]]']);
  });

  it.each([
    ['unknown-variable', 'Display.show(message)', 'Display.show(missing)', 'missing'],
    ['unknown-variable', 'let message = Greeter.greet("World")', 'let message = Greeter.greet(message)', 'message'],
    ['unknown-variable', 'let message = Greeter.greet("World")', 'Display.show(message) let message = Greeter.greet("World")', 'message'],
    ['void-result-assignment', 'Display.show(message)', 'let shown = Display.show(message)', 'shown'],
    ['unassigned-string-result', 'let message = Greeter.greet("World")', 'Greeter.greet("World")', 'greet'],
    ['duplicate-variable', 'Display.show(message)', 'let message = Greeter.greet("again")', 'message'],
    ['unknown-box', 'Display.show(message)', 'Missing.show(message)', 'Missing'],
    ['unknown-operation', 'Display.show(message)', 'Display.missing(message)', 'missing']
  ])('rejects %s with an identifier range and no artifact', async (code, before, after, identifier) => {
    const text = (await example()).replace(before, after);
    const program = parse(text);
    const diagnostics = await new BoundScriptLanguageFrontend().validate(program);
    const diagnostic = diagnostics.find((candidate) => candidate.code === `language.${code}`);
    expect(diagnostic).toBeDefined();
    expect(diagnostic?.severity).toBe('error');
    expect(text.slice(diagnostic!.range!.start.offset, diagnostic!.range!.end.offset)).toBe(identifier);
    const compiled = await new BoundScriptCompiler().compile(program, bindings);
    expect(compiled.ok).toBe(false);
    expect(compiled).not.toHaveProperty('artifact');
    expect(compiled.diagnostics).toEqual(diagnostics);
  });

  it('reports missing runtime registrations before calling either implementation', async () => {
    let called = false;
    await expect(execute(await compile(), {
      'demo.greeter': () => { called = true; return 'hello'; }
    })).rejects.toThrow('Missing implementation "demo.display".');
    expect(called).toBe(false);
  });

  it.each([
    ['demo.greeter', () => { throw new Error('broken'); }, 'failed: broken'],
    ['demo.display', async () => { throw new Error('rejected'); }, 'failed: rejected'],
    ['demo.greeter', () => undefined, 'must return a string'],
    ['demo.greeter', async () => undefined, 'must return a string'],
    ['demo.greeter', (() => 42) as unknown as BoxImplementation, 'must return a string'],
    ['demo.display', () => 'not void', 'must return undefined for a void operation'],
    ['demo.display', async () => 'not void', 'must return undefined for a void operation'],
    ['demo.display', (() => null) as unknown as BoxImplementation, 'must return undefined for a void operation']
  ] as const)('reports invalid implementation behavior for %s', async (id, implementation, message) => {
    const implementations = { 'demo.greeter': () => 'hello', 'demo.display': () => undefined, [id]: implementation };
    await expect(execute(await compile(), implementations)).rejects.toThrow(`Implementation "${id}" ${message}`);
  });

  it('reports a variable reference missing from the runtime map without invoking the box', async () => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    program.instructions.shift();
    let called = false;
    await expect(execute(withProgram(artifact, program), {
      'demo.display': () => { called = true; }
    })).rejects.toThrow('Unknown variable "message".');
    expect(called).toBe(false);
  });

  it('rejects the old instruction version rather than guessing an invocation shape', async () => {
    const artifact = await compile();
    await expect(execute(withProgram(artifact, { version: 1, instructions: [] }), {}))
      .rejects.toThrow('unsupported structure');
  });

  it.each([
    { argument: 'message' },
    { argument: { kind: 'literal', value: 42 } },
    { argument: { kind: 'variable', value: 'message' } },
    { argument: { kind: 'unknown', value: 'message' } },
    { resultType: 'unknown' },
    { resultType: 'string', result: undefined },
    { resultType: 'void', result: 'forbidden' }
  ])('rejects malformed invocation artifacts: %j', async (patch) => {
    const artifact = await compile();
    const program = JSON.parse(new TextDecoder().decode(artifact.assets[0]!.bytes));
    Object.assign(program.instructions[0], patch);
    await expect(execute(withProgram(artifact, program), {})).rejects.toThrow('unsupported structure');
  });
});

function withProgram(artifact: ExecutableArtifact, program: unknown): ExecutableArtifact {
  return {
    ...artifact,
    assets: artifact.assets.map((asset) => ({
      ...asset, bytes: new TextEncoder().encode(JSON.stringify(program))
    }))
  };
}
