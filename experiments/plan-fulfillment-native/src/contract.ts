import type { tags } from 'typia';
export type Id = string & tags.MinLength<1>;
export type Count = number & tags.Type<'uint32'>;
export type PositiveCount = Count & tags.Minimum<1>;
export type Priority = Count;
export type DateISO = string & tags.Pattern<'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'>;

export interface StockLot {
  readonly id: Id;
  readonly sku: Id;
  readonly warehouse: Id;
  readonly available: Count;
  readonly expiresOn: DateISO;
  readonly receivedSequence: Count;
  readonly blocked: boolean;
}
export interface DemandLine { readonly id: Id; readonly sku: Id; readonly quantity: PositiveCount; }
export interface DemandOrder {
  readonly id: Id;
  readonly priority: Priority;
  readonly allowedWarehouses: readonly Id[];
  readonly lines: readonly DemandLine[];
}
export interface FulfillmentRequest {
  readonly today: DateISO;
  readonly warehousePriority: readonly Id[];
  readonly picking: 'FEFO' | 'FIFO';
  readonly lots: readonly StockLot[];
  readonly orders: readonly DemandOrder[];
}
export interface Allocation {
  readonly orderId: Id;
  readonly lineId: Id;
  readonly lotId: Id;
  readonly warehouse: Id;
  readonly quantity: PositiveCount;
}
export interface Shortage { readonly orderId: Id; readonly lineId: Id; readonly quantity: PositiveCount; }
export interface RemainingLot { readonly lotId: Id; readonly quantity: Count; }
export interface FulfillmentPlan {
  readonly ok: true;
  readonly allocations: readonly Allocation[];
  readonly shortages: readonly Shortage[];
  readonly remaining: readonly RemainingLot[];
}
export type FulfillmentErrorCode = 'DUPLICATE_ID' | 'UNKNOWN_WAREHOUSE' | 'INVALID_DATE';
export interface FulfillmentFailure {
  readonly ok: false;
  readonly error: { readonly code: FulfillmentErrorCode; readonly id: string };
}
export type FulfillmentResult = FulfillmentPlan | FulfillmentFailure;
export type PlanFulfillment = (request: FulfillmentRequest) => FulfillmentResult;
