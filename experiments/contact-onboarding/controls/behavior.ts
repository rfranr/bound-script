import type { Implementation } from '../handoff/generated/contract.js';
export const implement: Implementation = () => ({
    requestId: 'r1', displayName: 'WRONG', email: 'ada@example.com', locale: 'en',
    consent: true, trialDays: 7, valid: true, reason: 'OK'
});
