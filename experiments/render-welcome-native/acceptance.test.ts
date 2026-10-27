import { expect, it } from 'vitest';
import fc from 'fast-check';
import { renderWelcome } from '/implementation/implementation.ts';
import { assertContact, assertMessage } from './.generated/validators';
import cases from './fixtures/welcome-cases.json';
import type { WelcomeContact } from './src/contract';

function invoke(input: WelcomeContact) {
  assertContact(input);
  const before = { ...input };
  Object.freeze(input);
  const result = assertMessage(renderWelcome(input));
  expect(input).toEqual(before);
  return result;
}

it.each(cases)('matches welcome fixture %#', ({ input, expected }) => {
  expect(invoke(input)).toBe(expected);
});

const text = fc.string({ minLength: 1, maxLength: 80 });
const contact = fc.record({ name: text, email: text, phone: text });

it('formats exactly, independently of phone and call history, without mutation', () => {
  fc.assert(fc.property(contact, text, contact, (input, otherPhone, unrelated) => {
    const variant = { ...input, phone: otherPhone };
    const records = [input, unrelated, variant];
    const snapshots = records.map(record => ({ ...record }));
    records.forEach(record => Object.freeze(record));

    const expected = `Welcome, ${input.name}! <${input.email}>`;
    const first = invoke(input);
    expect(first).toBe(expected);
    expect(invoke(unrelated)).toBe(`Welcome, ${unrelated.name}! <${unrelated.email}>`);
    expect(invoke(input)).toBe(first);
    expect(invoke(variant)).toBe(first);
    records.forEach((record, index) => expect(record).toEqual(snapshots[index]));
  }), { seed: 36, numRuns: 100 });
});
