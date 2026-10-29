import typia from 'typia';
import type { FulfillmentRequest, FulfillmentResult } from './contract';
export const isFulfillmentRequest = typia.createEquals<FulfillmentRequest>();
export const assertFulfillmentRequest = typia.createAssertEquals<FulfillmentRequest>();
export const isFulfillmentResult = typia.createEquals<FulfillmentResult>();
export const assertFulfillmentResult = typia.createAssertEquals<FulfillmentResult>();
