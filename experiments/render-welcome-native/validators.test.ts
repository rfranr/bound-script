import { expect, it } from 'vitest';
import { assertContact, assertMessage, isContact, isMessage } from './.generated/validators';

const valid = { name: 'Ada', email: 'ada@example.com', phone: 'x' };

it('accepts the declared contact shape and strings, not business semantics', () => {
  expect(isContact(valid)).toBe(true);
  expect(assertContact(valid)).toEqual(valid);
  expect(isContact({ name: ' ', email: 'x', phone: '?' })).toBe(true);
  expect(isMessage('Welcome, Ada! <ada@example.com>')).toBe(true);
  // Shape validation cannot establish correct formatting.
  expect(assertMessage('incorrect greeting')).toBe('incorrect greeting');
});

it('rejects missing, empty, non-string and extra input fields', () => {
  const invalid: unknown[] = [null, { ok: false, errors: [] }, { ...valid, extra: true }];
  for (const field of ['name', 'email', 'phone'] as const) {
    const missing: Partial<typeof valid> = { ...valid };
    delete missing[field];
    invalid.push(missing, { ...valid, [field]: '' }, { ...valid, [field]: 1 });
  }
  for (const value of invalid) {
    expect(isContact(value)).toBe(false);
    expect(() => assertContact(value)).toThrow();
  }
});

it('rejects representative non-string outputs', () => {
  for (const value of [{ message: 'Welcome' }, null]) {
    expect(isMessage(value)).toBe(false);
    expect(() => assertMessage(value)).toThrow();
  }
});
