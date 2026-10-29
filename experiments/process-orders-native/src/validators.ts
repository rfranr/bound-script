import typia from 'typia';
import type { Order, ProcessedOrder } from './contract';

export const isOrder = typia.createEquals<Order>();
export const assertOrder = typia.createAssertEquals<Order>();
export const isProcessedOrder = typia.createEquals<ProcessedOrder>();
export const assertProcessedOrder = typia.createAssertEquals<ProcessedOrder>();
