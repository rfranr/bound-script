import { expect, it } from 'vitest';
import fc from 'fast-check';
import { processOrders } from '/implementation/implementation.ts';
import { assertOrder, assertProcessedOrder } from './.generated/validators';
import cases from './fixtures/order-cases.json';
import type { Order } from './src/contract';

function call(order: Order) {
  assertOrder(order);
  Object.freeze(order.lines);
  for (const line of order.lines) Object.freeze(line);
  Object.freeze(order);
  return assertProcessedOrder(processOrders(order));
}

it.each(cases)('matches monetary fixture %#', ({ input, expected }) => {
  expect(call(input)).toEqual(expected);
});

it('preserves totals and does not depend on call history', () => {
  const line = fc.record({
    sku: fc.string({ minLength: 1, maxLength: 12 }),
    quantity: fc.integer({ min: 1, max: 10 }),
    unitPriceCents: fc.integer({ min: 0, max: 10000 }),
    discountPercent: fc.integer({ min: 0, max: 100 }),
    taxPercent: fc.integer({ min: 0, max: 100 }),
  });
  fc.assert(fc.property(fc.array(line, { minLength: 1, maxLength: 5 }), lines => {
    const order: Order = { id: 'property', lines };
    const a = call(order);
    expect(a.lines.map(x => x.sku)).toEqual(lines.map(x => x.sku));
    for (const field of ['subtotalCents', 'discountCents', 'taxCents', 'totalCents'] as const) {
      expect(a[field]).toBe(a.lines.reduce((sum, x) => sum + x[field], 0));
    }
    expect(call(order)).toEqual(a);
  }), { seed: 49, numRuns: 30 });
});
