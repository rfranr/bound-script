import { expect, it } from 'vitest';
import { isFulfillmentRequest, assertFulfillmentRequest, isFulfillmentResult } from './.generated/validators';
const valid = {today:'2026-10-29', warehousePriority:['W1'], picking:'FEFO', lots:[], orders:[]};
it('enforces structural request and result contracts', () => {
  expect(isFulfillmentRequest(valid)).toBe(true);
  expect(assertFulfillmentRequest(valid)).toEqual(valid);
  expect(isFulfillmentRequest({...valid, picking:'RANDOM'})).toBe(false);
  expect(isFulfillmentRequest({...valid, lots:[{id:'L',sku:'X',warehouse:'W1',available:-1,expiresOn:'2026-10-29',receivedSequence:0,blocked:false}]})).toBe(false);
  expect(isFulfillmentResult({ok:true,allocations:[],shortages:[],remaining:[]})).toBe(true);
  expect(isFulfillmentResult({ok:false,error:{code:'DUPLICATE_ID',id:'x'}})).toBe(true);
  expect(isFulfillmentResult({ok:true,allocations:[{quantity:0}],shortages:[],remaining:[]})).toBe(false);
});
