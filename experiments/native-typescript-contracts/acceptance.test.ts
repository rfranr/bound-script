import { expect, it } from 'vitest';
import fc from 'fast-check';
import { normalizeContact } from '/implementation/implementation.ts';
import { assertContact, assertResult } from './.generated/validators';
import cases from './cases.json';
import type { Contact, NormalizeContactResult } from './src/contract';

const options = { seed: 30, numRuns: 300 };
const phone = '+34600111222'; // Illustrative input only; no phone normalization oracle.

// Preserve exact name/email and error assertions without inventing phone output.
// invoke() still validates the complete result against the authoritative types.
function nameEmailResult(result: NormalizeContactResult) {
  if (!result.ok) return result;
  const { name, email } = result.contact;
  return { ok: true, contact: { name, email } };
}

function invoke(input: Contact) {
  assertContact(input);
  const before = { ...input };
  Object.freeze(input);
  const result = assertResult(normalizeContact(input));
  expect(input).toEqual(before);
  expect(Object.keys(result).sort()).toEqual(result.ok ? ['contact', 'ok'] : ['errors', 'ok']);
  if (result.ok) {
    expect(Object.keys(result.contact).sort()).toEqual(['email', 'name', 'phone']);
    expect(result.contact).not.toBe(input);
  }
  return result;
}

it.each(cases)('matches native acceptance case %#', ({ input, expected }) => {
  expect(nameEmailResult(invoke(input))).toEqual(expected);
  expect(nameEmailResult(invoke(input))).toEqual(expected);
});

it('is deterministic, non-mutating, structurally valid, with normalized successes', () => {
  fc.assert(fc.property(fc.record({ name: fc.string(), email: fc.string(), phone: fc.constant(phone) }), input => {
    const first = invoke(input);
    expect(invoke(input)).toEqual(first);
    if (first.ok) {
      // Only name/email have an approved normalization oracle. Keep the
      // illustrative phone input fixed when checking their idempotence.
      expect(nameEmailResult(invoke({ ...first.contact, phone }))).toEqual(nameEmailResult(first));
      expect(first.contact.name.length).toBeGreaterThan(0);
      expect(first.contact.name).toBe(first.contact.name.trim());
      expect(first.contact.name.replace(/ /g, '')).not.toMatch(/\s/u);
      expect(first.contact.name).not.toMatch(/ {2}/u);
      expect(first.contact.email).toBe(first.contact.email.trim().toLowerCase());
    }
  }), options);
});

// Construct known-valid data independently instead of reproducing the algorithm.
const word = fc.array(fc.constantFrom('A', 'z', 'é', '李', '雷', '👩🏽‍💻', 'e\u0301', '\u200b'),
  { minLength: 1, maxLength: 12 }).map(parts => parts.join(''));
const whitespace = fc.constantFrom(' ', '\t', '\n', '\r\n', '\u00a0', '\u2003', ' \t\n ');

it('preserves Unicode and collapses ECMAScript whitespace on known-valid contacts', () => {
  fc.assert(fc.property(word, word, whitespace, whitespace, (a, b, pad, gap) => {
    expect(nameEmailResult(invoke({ name: pad + a + gap + b + pad, email: pad + 'A+B@X.Y' + pad, phone })))
      .toEqual({ ok: true, contact: { name: a + ' ' + b, email: 'a+b@x.y' } });
  }), options);
});

it('trims and lowercases valid emails without rejecting permitted punctuation', () => {
  const local = fc.array(fc.constantFrom('a', 'z', '0', '1', '+', '.'),
    { minLength: 1, maxLength: 20 }).map(parts => parts.join(''));
  fc.assert(fc.property(local, whitespace, (part, pad) => {
    const email = part + '@example.test';
    expect(nameEmailResult(invoke({ name: 'Ada', email: pad + email.toUpperCase() + pad, phone })))
      .toEqual({ ok: true, contact: { name: 'Ada', email } });
  }), options);
});

it('accumulates required errors in order and never calls empty email invalid', () => {
  fc.assert(fc.property(whitespace, whitespace, (name, email) => {
    expect(invoke({ name, email, phone })).toEqual({ ok: false, errors: ['name.required', 'email.required'] });
  }), options);
});

it('accumulates invalid email after required name for malformed email families', () => {
  const badEmail = fc.oneof(
    word,
    word.map(value => value + '@domain'),
    word.map(value => value + '@@x.y'),
    whitespace.map(value => 'a@b.' + value + 'c'),
  );
  fc.assert(fc.property(whitespace, badEmail, (name, email) => {
    expect(invoke({ name, email, phone })).toEqual({ ok: false, errors: ['name.required', 'email.invalid'] });
  }), options);
});
