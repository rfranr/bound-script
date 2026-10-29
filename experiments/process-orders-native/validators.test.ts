import { expect, it } from 'vitest';
import { assertOrder, assertProcessedOrder, isOrder, isProcessedOrder } from './.generated/validators';

const input = { id: 'o-1', lines: [{ sku: 'A', quantity: 2, unitPriceCents: 125, discountPercent: 10, taxPercent: 20 }] };

it('validates the consumer-owned public input and output shapes', () => {
  expect(isOrder(input)).toBe(true);
  expect(assertOrder(input)).toEqual(input);
  expect(isOrder({ ...input, lines: [] })).toBe(false);
  expect(isOrder({ ...input, extra: true })).toBe(false);
  expect(isOrder({ ...input, lines: [{ ...input.lines[0], discountPercent: 101 }] })).toBe(false);
  expect(isProcessedOrder(null)).toBe(false);
  expect(() => assertProcessedOrder(null)).toThrow();
});
