import { expect, it } from 'vitest';
import fc from 'fast-check';
import { planFulfillment } from '/implementation/implementation.ts';
import { assertFulfillmentRequest, assertFulfillmentResult } from './.generated/validators';
import type { FulfillmentRequest } from './src/contract';
import cases from './fixtures/fulfillment-cases.json';

function freeze(value: unknown): void {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
}
function run(request: FulfillmentRequest) {
  assertFulfillmentRequest(request);
  freeze(request);
  return assertFulfillmentResult(planFulfillment(request));
}
it.each(cases)('matches consumer-owned fulfillment fixture %#', ({input, expected}) => {
  expect(run(input as FulfillmentRequest)).toEqual(expected);
});
it('conserves quantity, is deterministic, and does not mutate frozen input', () => {
  fc.assert(fc.property(
    fc.integer({min:0,max:100}), fc.integer({min:1,max:100}), (stock,demand) => {
      const request: FulfillmentRequest = {
        today:'2026-10-29', warehousePriority:['W1'], picking:'FEFO',
        lots:[{id:'LOT',sku:'X',warehouse:'W1',available:stock,expiresOn:'2026-10-29',receivedSequence:0,blocked:false}],
        orders:[{id:'ORDER',priority:0,allowedWarehouses:['W1'],lines:[{id:'LINE',sku:'X',quantity:demand}]}],
      };
      const result = run(request);
      expect(result.ok).toBe(true);
      if (!result.ok) return;
      const shipped = result.allocations.reduce((sum,a) => sum+a.quantity,0);
      const missing = result.shortages.reduce((sum,s) => sum+s.quantity,0);
      expect(shipped+missing).toBe(demand);
      expect(shipped+result.remaining[0].quantity).toBe(stock);
      expect(run(request)).toEqual(result);
    }), {seed:50,numRuns:60});
});
