import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import {
  BoxSpecValidationError, extractBoxDevelopmentSpec, parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec,
  type BoxDevelopmentSpec
} from '@boundscript/compiler';
import { parseBoundScript } from '@boundscript/language';

const base = {
  format: 'boundscript/box-development-spec', version: 1, system: 'Demo', box: 'Box',
  operation: {
    name: 'run', input: { name: 'value', type: 'string' }, resultType: 'string',
    postcondition: { kind: 'string-not-equal', target: { kind: 'result' }, value: '' }
  }
} as const;
const record = { kind: 'record', name: 'Data', fields: [{ name: 'text', type: 'string' }, { name: 'count', type: 'number' }] };
const fieldPredicate = { kind: 'string-not-equal', target: { kind: 'field', name: 'text' }, value: '' };
const operation = (patch: Record<string, unknown>) => ({ ...base, operation: { ...base.operation, ...patch } });
const inputType = (type: unknown) => operation({ input: { name: 'value', type } });

function decode(json: string) {
  const result = parseBoxDevelopmentSpec(json);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  expect(result.diagnostics).toEqual([]);
  return result.spec;
}

function serialize(value: unknown) {
  return serializeBoxDevelopmentSpec(value as BoxDevelopmentSpec);
}

describe('portable box specification JSON', () => {
  it('matches the published export and round-trips to byte-identical JSON', async () => {
    const published = await readFile('examples/specs/greeter.box-spec.json', 'utf8');
    const parsed = parseBoundScript({ uri: 'memory:structured.bound', text: await readFile('examples/structured-types.bound', 'utf8') });
    const extracted = extractBoxDevelopmentSpec(parsed.program!, 'Greeter');
    if (!extracted.ok) throw new Error(JSON.stringify(extracted.diagnostics));
    expect(serializeBoxDevelopmentSpec(extracted.spec)).toBe(published);
    expect(serializeBoxDevelopmentSpec(decode(published))).toBe(published);
    expect(published.endsWith('\n')).toBe(true);
    expect(published.endsWith('\n\n')).toBe(false);
    expect(published).not.toContain('\r');
  });

  it('normalizes key/field order without mutating the input and preserves record identity', () => {
    const fields = [{ name: 'a', type: 'number' }, { name: '_', type: 'boolean' }, { name: 'Z', type: 'string' }];
    const spec = operation({
      input: { type: { fields, name: 'Same', kind: 'record' }, name: 'value' },
      resultType: { kind: 'record', name: 'Same', fields: [...fields].reverse() },
      postcondition: { kind: 'string-not-equal', target: { kind: 'field', name: 'Z' }, value: 'bad\n"value"' }
    });
    const before = structuredClone(spec);
    const first = serialize(spec);
    expect(spec).toEqual(before);
    const reversed = Object.fromEntries(Object.entries(spec).reverse());
    expect(serialize(reversed)).toBe(first);
    const decoded = decode(first);
    expect(typeof decoded.operation.input.type).toBe('object');
    expect((decoded.operation.input.type as { fields: unknown[] }).fields).toEqual([
      { name: 'Z', type: 'string' }, { name: '_', type: 'boolean' }, { name: 'a', type: 'number' }
    ]);
    expect(decoded.operation.input.type).toEqual(decoded.operation.resultType);
    expect(serializeBoxDevelopmentSpec(decode(first.replaceAll('\n', '\r\n')))).toBe(first);
  });

  it.each(['string', 'number', 'boolean', 'void'])('round-trips the supported result type %s', (type) => {
    const { postcondition: _unused, ...withoutPostcondition } = base.operation;
    const spec = { ...base, operation: { ...withoutPostcondition, resultType: type } };
    expect(serializeBoxDevelopmentSpec(decode(serialize(spec)))).toBe(serialize(spec));
  });

  it('accepts empty record schemas and keeps distinct nominal names', () => {
    const spec = operation({ input: { name: 'value', type: { kind: 'record', name: 'First', fields: [] } },
      resultType: { kind: 'record', name: 'Second', fields: [] } });
    delete (spec.operation as Record<string, unknown>).postcondition;
    expect(decode(serialize(spec)).operation).toEqual(spec.operation);
  });

  it.each(['{', 'null trailing', '', 'undefined', '{"version": NaN}'])('reports malformed JSON: %s', (json) => {
    const result = parseBoxDevelopmentSpec(json);
    expect(result).toEqual({ ok: false, diagnostics: [{
      code: 'compiler.box-spec.invalid-json', message: 'Box specification is not valid JSON.', severity: 'error'
    }] });
    expect(result).not.toHaveProperty('spec');
  });

  it.each([
    ['null root', null, '$'], ['array root', [], '$'],
    ['wrong format', { ...base, format: 'other' }, '$.format'],
    ['wrong version', { ...base, version: 2 }, '$.version'],
    ['non-numeric version', { ...base, version: '1' }, '$.version'],
    ['missing top-level key', { ...base, system: undefined }, '$.system'],
    ['unknown top-level key', { ...base, implementation: 'host.fn' }, '$'],
    ['invalid identifier', { ...base, box: 'not an identifier' }, '$.box'],
    ['missing operation', { ...base, operation: undefined }, '$.operation'],
    ['array operation', { ...base, operation: [] }, '$.operation'],
    ['missing operation name', operation({ name: undefined }), '$.operation.name'],
    ['extra operation key', operation({ source: 'code' }), '$.operation'],
    ['missing input', operation({ input: undefined }), '$.operation.input'],
    ['missing input name', operation({ input: { type: 'string' } }), '$.operation.input.name'],
    ['extra input key', operation({ input: { name: 'value', type: 'string', default: 'x' } }), '$.operation.input'],
    ['void input', inputType('void'), '$.operation.input.type'],
    ['unknown primitive', inputType('integer'), '$.operation.input.type'],
    ['unresolved name', inputType('Data'), '$.operation.input.type'],
    ['null input type', inputType(null), '$.operation.input.type'],
    ['wrong record kind', inputType({ ...record, kind: 'array' }), '$.operation.input.type.kind'],
    ['extra record key', inputType({ ...record, optional: true }), '$.operation.input.type'],
    ['reserved record name', inputType({ ...record, name: 'string' }), '$.operation.input.type.name'],
    ['invalid record name', inputType({ ...record, name: '' }), '$.operation.input.type.name'],
    ['missing fields', inputType({ kind: 'record', name: 'Data' }), '$.operation.input.type.fields'],
    ['non-array fields', inputType({ ...record, fields: {} }), '$.operation.input.type.fields'],
    ['duplicate fields', inputType({ ...record, fields: [{ name: 'x', type: 'string' }, { name: 'x', type: 'number' }] }), '.fields[1].name'],
    ['unknown field key', inputType({ ...record, fields: [{ name: 'x', type: 'string', optional: true }] }), '.fields[0]'],
    ['missing field type', inputType({ ...record, fields: [{ name: 'x' }] }), '.fields[0].type'],
    ['void field', inputType({ ...record, fields: [{ name: 'x', type: 'void' }] }), '.fields[0].type'],
    ['nested field', inputType({ ...record, fields: [{ name: 'x', type: record }] }), '.fields[0].type'],
    ['invalid field name', inputType({ ...record, fields: [{ name: 'x.y', type: 'string' }] }), '.fields[0].name'],
    ['missing result', operation({ resultType: undefined }), '$.operation.resultType'],
    ['unknown result', operation({ resultType: 'Missing' }), '$.operation.resultType'],
    ['conflicting record schemas', operation({ input: { name: 'value', type: record }, resultType: { ...record, fields: [{ name: 'text', type: 'boolean' }] } }), '$.operation.resultType'],
    ['null postcondition', operation({ postcondition: null }), '$.operation.postcondition'],
    ['void postcondition', operation({ resultType: 'void' }), '$.operation.postcondition'],
    ['unknown predicate', operation({ postcondition: { ...base.operation.postcondition, kind: 'eval' } }), '.postcondition.kind'],
    ['extra predicate key', operation({ postcondition: { ...base.operation.postcondition, expression: 'result' } }), '.postcondition'],
    ['missing predicate value', operation({ postcondition: { kind: 'string-not-equal', target: { kind: 'result' } } }), '.postcondition.value'],
    ['non-string predicate value', operation({ postcondition: { ...base.operation.postcondition, value: 0 } }), '.postcondition.value'],
    ['unknown target', operation({ postcondition: { ...base.operation.postcondition, target: { kind: 'input' } } }), '.target.kind'],
    ['missing field name', operation({ resultType: record, postcondition: { ...fieldPredicate, target: { kind: 'field' } } }), '.target.name'],
    ['unknown field', operation({ resultType: record, postcondition: { ...fieldPredicate, target: { kind: 'field', name: 'unknown' } } }), '.target.name'],
    ['non-string field', operation({ resultType: record, postcondition: { ...fieldPredicate, target: { kind: 'field', name: 'count' } } }), '.target.name'],
    ['field on primitive', operation({ postcondition: fieldPredicate }), '.target.name'],
    ['result target on record', operation({ resultType: record }), '.postcondition.target'],
    ['result target on number', operation({ resultType: 'number' }), '.postcondition.target'],
    ['extra result-target key', operation({ postcondition: { ...base.operation.postcondition, target: { kind: 'result', name: 'text' } } }), '.target.name'],
    ['extra field-target key', operation({ resultType: record, postcondition: { ...fieldPredicate, target: { kind: 'field', name: 'text', path: [] } } }), '.target']
  ])('rejects %s on parse and serialization', (_label, value, path) => {
    const parsed = parseBoxDevelopmentSpec(JSON.stringify(value));
    expect(parsed.ok).toBe(false);
    expect(parsed).not.toHaveProperty('spec');
    expect(parsed.diagnostics[0]).toMatchObject({ code: 'compiler.box-spec.invalid-spec', severity: 'error' });
    expect(parsed.diagnostics[0]!.message).toContain(path);
    expect(() => serialize(value)).toThrow(BoxSpecValidationError);
    try { serialize(value); } catch (error) {
      expect((error as BoxSpecValidationError).diagnostics[0]!.code).toBe('compiler.box-spec.invalid-spec');
    }
  });

  it('rejects serialization-only hazards without invoking getters or JSON hooks', () => {
    let invoked = false;
    const getter = { ...base };
    Object.defineProperty(getter, 'system', { enumerable: true, get: () => { invoked = true; return 'Demo'; } });
    const hook = { ...base, toJSON: () => { invoked = true; return base; } };
    const symbol = { ...base, [Symbol('hidden')]: true };
    const hidden = { ...base };
    Object.defineProperty(hidden, 'metadata', { value: true, enumerable: false });
    const inherited = Object.create(base);
    const array = [...record.fields];
    Object.defineProperty(array, 'toJSON', { value: () => { invoked = true; return []; } });
    const sparse = new Array(1);
    const arrayGetter = [...record.fields];
    Object.defineProperty(arrayGetter, '0', { enumerable: true, get: () => { invoked = true; return record.fields[0]; } });
    const cycle: Record<string, unknown> = { ...base };
    cycle.operation = cycle;
    for (const value of [getter, hook, symbol, hidden, inherited, cycle,
      { ...base, box: () => 'Box' }, { ...base, version: 1n }, operation({ postcondition: undefined }),
      Object.assign(new Date(), base), inputType({ ...record, fields: array }),
      inputType({ ...record, fields: sparse }), inputType({ ...record, fields: arrayGetter })]) {
      expect(() => serialize(value)).toThrow(BoxSpecValidationError);
    }
    expect(invoked).toBe(false);
  });
});
