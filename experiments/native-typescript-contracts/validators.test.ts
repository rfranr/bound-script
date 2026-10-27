import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { assertContact, assertResult, isContact, isResult } from './.generated/validators';

const options = { seed: 30, numRuns: 200 };
const phone = '+34600111222'; // Illustrative input, not a phone business rule.

describe('Typia validators derived only from native TypeScript', () => {
  it('accepts Contact strings, not missing/null/non-string fields', () => {
    fc.assert(fc.property(fc.record({ name: fc.string(), email: fc.string(), phone: fc.constant(phone) }), input => {
      expect(isContact(input)).toBe(true);
      expect(assertContact(input)).toBe(input);
    }), options);
    for (const input of [null, undefined, {}, { name: 'Ada' }, { name: '', email: '' },
      { name: 1, email: '', phone }, { name: '', email: null, phone },
      { name: '', email: '', phone, extra: true }]) {
      expect(isContact(input)).toBe(false);
      expect(() => assertContact(input)).toThrow();
    }
  });

  it('checks the result discriminant, union branches and error literals', () => {
    for (const result of [
      { ok: true, contact: { name: 'Ada', email: 'a@b.c', phone } },
      { ok: false, errors: ['name.required', 'email.required', 'email.invalid'] },
      { ok: false, errors: [] },
    ]) {
      expect(isResult(result)).toBe(true);
      expect(assertResult(result)).toBe(result);
    }
    for (const result of [null, {}, { ok: 'true', contact: { name: 'Ada', email: 'a@b.c', phone } },
      { ok: true, contact: { name: 'Ada', email: 1, phone } }, { ok: false, errors: ['unknown'] },
      { ok: false, errors: [], contact: { name: 'Ada', email: 'a@b.c', phone } },
      { ok: true, contact: { name: 'Ada', email: 'a@b.c', phone }, errors: [] }]) {
      expect(isResult(result)).toBe(false);
      expect(() => assertResult(result)).toThrow();
    }
  });

  it('rejects invalid normalized contact data', () => {
    expect(isResult({
      ok: true,
      contact: { name: '', email: 'bad', phone }
    })).toBe(false);
  });
});
