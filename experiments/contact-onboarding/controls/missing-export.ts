import type { Implementation } from '../handoff/generated/contract.js';
export const other: Implementation = () => { throw new Error('Never invoked'); };
