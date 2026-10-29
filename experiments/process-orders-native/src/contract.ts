import type { tags } from 'typia';

export interface OrderLine {
  readonly sku: string & tags.MinLength<1>;
  readonly quantity: number & tags.Type<'uint32'> & tags.Minimum<1>;
  readonly unitPriceCents: number & tags.Type<'uint32'>;
  readonly discountPercent: number & tags.Type<'uint32'> & tags.Maximum<100>;
  readonly taxPercent: number & tags.Type<'uint32'> & tags.Maximum<100>;
}

export interface Order {
  readonly id: string & tags.MinLength<1>;
  readonly lines: readonly OrderLine[] & tags.MinItems<1>;
}

export interface ProcessedLine {
  readonly sku: string;
  readonly subtotalCents: number;
  readonly discountCents: number;
  readonly taxCents: number;
  readonly totalCents: number;
}

export interface ProcessedOrder {
  readonly id: string;
  readonly lines: readonly ProcessedLine[];
  readonly subtotalCents: number;
  readonly discountCents: number;
  readonly taxCents: number;
  readonly totalCents: number;
}

export type ProcessOrders = (order: Order) => ProcessedOrder;
