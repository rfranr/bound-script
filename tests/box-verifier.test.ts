import { describe, expect, it, vi } from 'vitest';

import {
  DIRECTOR_PROGRAM_MEDIA_TYPE, DIRECTOR_PROGRAM_VERSION,
  EXECUTABLE_ARTIFACT_FORMAT, EXECUTABLE_ARTIFACT_VERSION,
  type ExecutableArtifact, type Postcondition, type ValueType
} from '@boundscript/artifact';
import {
  BoundScriptRuntime, PostconditionViolationError, RuntimeExecutionError, verifyBoxImplementation,
  type BoxImplementation, type BoxVerificationContract
} from '@boundscript/runtime';

const record: ValueType = { kind: 'record', name: 'Data', fields: [
  { name: 'text', type: 'string' }, { name: 'count', type: 'number' }, { name: 'active', type: 'boolean' }
] };
const value = () => ({ text: 'hello', count: 0, active: false });
const predicate = (field = false, forbidden = ''): Postcondition => ({
  kind: 'string-not-equal', target: field ? { kind: 'field', name: 'text' } : { kind: 'result' }, value: forbidden
});
function contract(inputType: ValueType = 'string', resultType: ValueType | 'void' = 'string', postcondition?: Postcondition): BoxVerificationContract {
  return { box: 'Box', operation: { name: 'run', input: { type: inputType }, resultType,
    ...(postcondition ? { postcondition } : {}) } };
}

// Only parity tests use artifacts. The standalone consumer has a separate frontend-blocked test.
function execute(type: ValueType | 'void', implementation: BoxImplementation, postcondition?: Postcondition) {
  const invocation = {
    operation: 'invoke', implementation: 'host.box', box: 'Box', boxOperation: 'run',
    inputType: 'string', argument: { kind: 'literal', value: 'fixed' }, resultType: type,
    ...(type === 'void' ? {} : { result: 'result' }), ...(postcondition ? { postcondition } : {})
  };
  const artifact: ExecutableArtifact = {
    format: EXECUTABLE_ARTIFACT_FORMAT, version: EXECUTABLE_ARTIFACT_VERSION, system: 'Parity',
    entrypoints: [{ name: 'start', target: 'main.json' }], assets: [{ path: 'main.json',
      mediaType: DIRECTOR_PROGRAM_MEDIA_TYPE,
      bytes: new TextEncoder().encode(JSON.stringify({ version: DIRECTOR_PROGRAM_VERSION, instructions: [invocation] })) }]
  };
  return new BoundScriptRuntime({ writeLine: () => { throw new Error('No printing'); } }, { 'host.box': implementation })
    .execute(artifact, { entrypoint: 'start' });
}

describe('standalone Box verification', () => {
  it.each([
    null, {}, { ...contract(), box: '' }, { ...contract(), box: undefined },
    { ...contract(), operation: {} }, { ...contract(), operation: { ...contract().operation, name: '' } },
    contract('void' as ValueType), contract('Unknown' as ValueType), contract('string', 'Unknown' as ValueType),
    contract('string', 'void', predicate()), contract('string', 'number', predicate()),
    contract('string', record, predicate()), contract('string', 'string', predicate(true)),
    contract('string', record, { ...predicate(true), target: { kind: 'field', name: 'count' } }),
    contract('string', record, { ...predicate(true), kind: 'eval' } as unknown as Postcondition),
    contract({ kind: 'record', name: 'Bad', fields: [{ name: 'x', type: 'string' }, { name: 'x', type: 'string' }] }),
    { ...contract(), operation: { ...contract().operation, postcondition: undefined } },
    { ...contract(), operation: Object.assign(Object.create({ postcondition: { kind: 'eval' } }), contract().operation) }
  ])('rejects a malformed consumer view before execution: %j', async (view) => {
    const candidate = vi.fn();
    expect(await verifyBoxImplementation(view as BoxVerificationContract, candidate, 'fixed'))
      .toMatchObject({ ok: false, failure: { kind: 'invalid-contract' } });
    expect(candidate).not.toHaveBeenCalled();
  });

  it.each([undefined, null, {}, 'function'])('rejects non-function candidates: %j', async (candidate) => {
    expect(await verifyBoxImplementation(contract(), candidate as BoxImplementation, 'fixed'))
      .toMatchObject({ ok: false, failure: { kind: 'invalid-implementation' } });
  });

  it.each([
    ['string', '', true], ['string', 'hello', true], ['number', 0, true], ['number', -2.5, true],
    ['boolean', false, true], ['boolean', true, true],
    ['string', null, false], ['string', undefined, false], ['string', 1, false], ['string', new String('x'), false],
    ['number', '7', false], ['number', NaN, false], ['number', Infinity, false], ['number', -Infinity, false],
    ['number', new Number(1), false], ['boolean', 'false', false], ['boolean', new Boolean(false), false]
  ] as const)('checks primitive %s value %j at both boundaries (valid: %s)', async (type, input, valid) => {
    const identity = vi.fn((input: unknown) => input);
    const checkedInput = await verifyBoxImplementation(contract(type, type), identity, input);
    expect(checkedInput.ok).toBe(valid);
    if (valid) expect(checkedInput).toEqual({ ok: true, output: input });
    else expect(checkedInput).toMatchObject({ ok: false, failure: { kind: 'invalid-input', expected: type } });
    expect(identity).toHaveBeenCalledTimes(valid ? 1 : 0);
    const checkedOutput = await verifyBoxImplementation(contract('string', type), () => input, 'fixed');
    expect(checkedOutput.ok).toBe(valid);
    if (!valid) {
      expect(checkedOutput).toMatchObject({ ok: false, failure: { kind: 'invalid-output', expected: type } });
      expect(checkedOutput).not.toHaveProperty('output');
    }
  });

  const badRecords = [null, [], undefined, 'record', {}, { text: 'x', count: 1 },
    { ...value(), text: 3 }, { ...value(), count: '0' }, { ...value(), count: NaN },
    { ...value(), count: Infinity }, { ...value(), count: -Infinity }, { ...value(), active: 'false' },
    { ...value(), extra: true }, { ...value(), [Symbol('extra')]: true },
    Object.defineProperty(value(), 'hidden', { value: true }),
    Object.assign(Object.create({ text: 'inherited' }), { count: 0, active: false })];
  it.each(badRecords.map((input) => [input]))('checks record problems at both boundaries: %j', async (input) => {
    const candidate = vi.fn(() => value());
    const result = await verifyBoxImplementation(contract(record, record), candidate, input);
    expect(result).toMatchObject({ ok: false, failure: { kind: 'invalid-input', expected: record } });
    expect(candidate).not.toHaveBeenCalled();
    const output = await verifyBoxImplementation(contract('string', record), () => input, 'fixed');
    expect(output).toMatchObject({ ok: false, failure: { kind: 'invalid-output', expected: record } });
    expect(output).not.toHaveProperty('output');
  });

  const validRecords = [value(), Object.assign(Object.create(null), value()),
    new class { text = 'hello'; count = 0; active = false; }(),
    Object.assign(Object.create({ ignored: true }), value()),
    { get text() { return 'hello'; }, count: 0, active: false }];
  it.each(validRecords.map((input) => [input]))('preserves record representation/reference semantics: %j', async (input) => {
    const result = await verifyBoxImplementation(contract(record, record), (received) => {
      expect(received).toBe(input); return received;
    }, input);
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.output).toBe(input);
    await expect(execute(record, () => input)).resolves.toEqual({});
  });

  it('accepts empty record schemas and retains first-problem descriptor order', async () => {
    const empty: ValueType = { kind: 'record', name: 'Empty', fields: [] };
    expect(await verifyBoxImplementation(contract(empty, empty), (input) => input, {})).toEqual({ ok: true, output: {} });
    await expect(execute(empty, () => ({}))).resolves.toEqual({});
    expect(await verifyBoxImplementation(contract(record), () => 'x', {})).toMatchObject({
      ok: false, failure: { kind: 'invalid-input', problem: 'missing required field "text"' }
    });
  });

  it.each([false, true])('invokes once and awaits completion (async: %s)', async (asynchronous) => {
    const events: string[] = [];
    const candidate = vi.fn(asynchronous ? async (input: string) => {
      events.push('start'); await Promise.resolve(); events.push('end'); return input;
    } : (input: string) => { events.push('start', 'end'); return input; });
    expect(await verifyBoxImplementation(contract(), candidate, 'fixed')).toEqual({ ok: true, output: 'fixed' });
    expect(events).toEqual(['start', 'end']);
    expect(candidate).toHaveBeenCalledExactlyOnceWith('fixed');
  });

  it.each([
    () => { throw new Error('broken'); }, async () => { throw new Error('rejected'); },
    () => { throw 'non-Error'; }, () => { throw new RuntimeExecutionError('runtime'); },
    () => { throw new PostconditionViolationError('Box', 'run', predicate(), ''); },
    () => ({ then: (_resolve: unknown, reject: (error: Error) => void) => reject(new Error('thenable')) }),
    () => Object.defineProperty({}, 'then', { get: () => { throw new Error('then getter'); } })
  ])('classifies only candidate execution/await failures as execution-failure', async (implementation) => {
    const candidate = vi.fn(implementation);
    const result = await verifyBoxImplementation(contract(), candidate as BoxImplementation, 'fixed');
    expect(result).toMatchObject({ ok: false, failure: { kind: 'execution-failure' } });
    expect(result).not.toHaveProperty('output');
    expect(candidate).toHaveBeenCalledTimes(1);
  });

  it('does not serialize thrown objects or mask their stage with conversion errors', async () => {
    const convert = vi.fn(() => { throw new Error('do not convert'); });
    const result = await verifyBoxImplementation(contract(), () => { throw { toString: convert }; }, 'fixed');
    expect(result).toMatchObject({ ok: false, failure: { kind: 'execution-failure' } });
    expect(convert).not.toHaveBeenCalled();
  });

  it.each([() => {}, () => undefined, async () => undefined])('accepts sync/async void and includes undefined output', async (implementation) => {
    const result = await verifyBoxImplementation(contract('string', 'void'), implementation, 'fixed');
    expect(result).toEqual({ ok: true, output: undefined });
    expect(Object.hasOwn(result, 'output')).toBe(true);
    await expect(execute('void', implementation)).resolves.toEqual({});
  });

  it.each([null, 'wrong', {}, 0, false])('rejects non-undefined void output: %j', async (output) => {
    expect(await verifyBoxImplementation(contract('string', 'void'), () => output, 'fixed'))
      .toMatchObject({ ok: false, failure: { kind: 'invalid-output', expected: 'void' } });
  });

  it.each([false, true])('evaluates exact result/field predicates (field: %s)', async (field) => {
    for (const forbidden of ['', 'forbidden', 'line\n"quoted"']) {
      const check = predicate(field, forbidden);
      for (const observed of [forbidden, `${forbidden}!`]) {
        const output = field ? { ...value(), text: observed } : observed;
        const result = await verifyBoxImplementation(contract('string', field ? record : 'string', check), () => output, 'fixed');
        expect(result).toEqual(observed === forbidden
          ? { ok: false, failure: { kind: 'postcondition-failure', predicate: check, observed } }
          : { ok: true, output });
      }
    }
    expect(await verifyBoxImplementation(contract('string', field ? record : 'string'), () => field ? value() : '', 'fixed'))
      .toMatchObject({ ok: true });
  });

  it('stops on bad input and checks all output fields before the predicate', async () => {
    const candidate = vi.fn(() => { throw new Error('must not run'); });
    expect(await verifyBoxImplementation(contract(), candidate, 1)).toMatchObject({ failure: { kind: 'invalid-input' } });
    expect(candidate).not.toHaveBeenCalled();
    let reads = 0;
    const output = { get text() { reads++; return ''; }, count: 'wrong', active: false };
    const result = await verifyBoxImplementation(contract('string', record, predicate(true)), () => output, 'fixed');
    expect(result).toMatchObject({ failure: { kind: 'invalid-output', problem: 'field "count" expected number, got string' } });
    expect(reads).toBe(1); // Predicate would read text a second time.
  });

  it.each(['input', 'output', 'postcondition'] as const)('reports inspection errors at the %s phase', async (phase) => {
    let reads = 0;
    const output = { get text() {
      if (phase !== 'postcondition' || ++reads === 2) throw new Error('inspection');
      return 'valid';
    }, count: 0, active: false };
    const candidate = vi.fn(() => output);
    const result = await verifyBoxImplementation(
      contract(phase === 'input' ? record : 'string', record, predicate(true)), candidate, phase === 'input' ? output : 'fixed'
    );
    expect(result).toEqual({ ok: false, failure: { kind: 'inspection-failure', phase, message: 'inspection' } });
    expect(candidate).toHaveBeenCalledTimes(phase === 'input' ? 0 : 1);
  });

  it('rechecks mutated inputs and does not freeze, clone or roll back side effects', async () => {
    const input = value();
    const candidate = vi.fn((received) => { expect(received).toBe(input); received.count = 'invalid'; return ''; });
    expect(await verifyBoxImplementation(contract(record, 'string', predicate()), candidate, input))
      .toMatchObject({ failure: { kind: 'postcondition-failure' } });
    expect(input.count).toBe('invalid');
    expect(Object.isFrozen(input)).toBe(false);
    expect(await verifyBoxImplementation(contract(record), candidate, input)).toMatchObject({ failure: { kind: 'invalid-input' } });
    expect(candidate).toHaveBeenCalledTimes(1);
  });
});

describe('legacy runtime parity', () => {
  it.each([
    ['string', 42, 'got number'], ['number', NaN, 'got non-finite number'],
    [record, {}, 'missing required field "text"'], [record, { ...value(), extra: true }, 'unexpected field "extra"'],
    [record, Object.defineProperty(value(), 'hidden', { value: true }), 'unexpected field "hidden"'],
    [record, { ...value(), [Symbol('extra')]: true }, 'unexpected field "Symbol(extra)"'],
    ['void', null, 'got null']
  ] as const)('retains output errors for %j', async (type, output, problem) => {
    const result = await verifyBoxImplementation(contract('string', type), () => output, 'fixed');
    expect(result).toEqual({ ok: false, failure: { kind: 'invalid-output', expected: type, problem } });
    const error = await execute(type, () => output).catch((error: unknown) => error);
    expect(error).toBeInstanceOf(RuntimeExecutionError);
    const prefix = type === 'void' ? 'must return undefined for a void operation.'
      : type === 'string' ? 'must return a string.' : 'output contract failed.';
    const expected = typeof type === 'string' ? type : type.name;
    expect((error as Error).message).toBe(`Implementation "host.box" ${prefix} Box "Box.run" output expected "${expected}"${type === 'void' ? ', ' : ': '}${problem}.`);
  });

  it('retains postcondition code/context/message and candidate-error distinction', async () => {
    const check = predicate();
    const error = await execute('string', () => '', check).catch((error: unknown) => error);
    expect(error).toBeInstanceOf(PostconditionViolationError);
    expect(error).toMatchObject({ code: 'runtime.postcondition-violation', box: 'Box', operation: 'run', predicate: check, observed: '' });
    expect((error as Error).message).toBe('Postcondition violation for box "Box.run": ensure result != ""; observed result = "".');
    await expect(execute('string', () => { throw error; }, check)).rejects.toThrow(`Implementation "host.box" failed: ${(error as Error).message}`);
    expect(await verifyBoxImplementation(contract('string', 'string', check), () => { throw error; }, 'fixed'))
      .toMatchObject({ failure: { kind: 'execution-failure' } });
  });

  it('preserves raw inspection exceptions in the legacy runtime', async () => {
    const marker = new Error('getter');
    const output = { get text() { throw marker; }, count: 0, active: false };
    await expect(execute(record, () => output, predicate(true))).rejects.toBe(marker);
    let reads = 0;
    const unstable = { get text() { if (++reads === 2) throw marker; return 'valid'; }, count: 0, active: false };
    await expect(execute(record, () => unstable, predicate(true))).rejects.toBe(marker);
  });

  it('retains full output validation before a predicate and does not roll back host mutations', async () => {
    let reads = 0;
    const output = { get text() { reads++; return ''; }, count: 'wrong', active: false };
    let effects = 0;
    await expect(execute(record, () => { effects++; return output; }, predicate(true)))
      .rejects.toThrow('Implementation "host.box" output contract failed. Box "Box.run" output expected "Data": field "count" expected number, got string.');
    expect(reads).toBe(1);
    expect(effects).toBe(1);
  });
});
