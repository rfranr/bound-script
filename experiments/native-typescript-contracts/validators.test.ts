import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { assertContact, assertResult, isContact, isResult } from './.generated/validators';

const options = { seed: 30, numRuns: 200 };

describe('Typia validators derived only from native TypeScript', () => {
  it('accepts Contact strings, not missing/null/non-string fields', () => {
    fc.assert(fc.property(fc.record({ name: fc.string(), email: fc.string() }), input => {
      expect(isContact(input)).toBe(true);
      expect(assertContact(input)).toBe(input);
    }), options);
    for (const input of [null, undefined, {}, { name: 'Ada' }, { name: 1, email: '' },
      { name: '', email: null }, { name: '', email: '', extra: true }]) {
      expect(isContact(input)).toBe(false);
      expect(() => assertContact(input)).toThrow();
    }
  });

  it('checks the result discriminant, union branches and error literals', () => {
    for (const result of [
      { ok: true, contact: { name: 'Ada', email: 'a@b.c' } },
      { ok: false, errors: ['name.required', 'email.required', 'email.invalid'] },
      { ok: false, errors: [] },
    ]) {
      expect(isResult(result)).toBe(true);
      expect(assertResult(result)).toBe(result);
    }
    for (const result of [null, {}, { ok: 'true', contact: { name: '', email: '' } },
      { ok: true, contact: { name: '', email: 1 } }, { ok: false, errors: ['unknown'] },
      { ok: false, errors: [], contact: { name: '', email: '' } },
      { ok: true, contact: { name: '', email: '' }, errors: [] }]) {
      expect(isResult(result)).toBe(false);
      expect(() => assertResult(result)).toThrow();
    }
  });

  it('does not pretend native shape validation enforces business rules', () => {
    // These are structurally valid. Independent behavioral tests must reject
    // an implementation returning these for the wrong input.
    expect(isResult({ ok: true, contact: { name: '', email: 'bad' } })).toBe(true);
    expect(isResult({ ok: false, errors: [] })).toBe(true);
  });
});
