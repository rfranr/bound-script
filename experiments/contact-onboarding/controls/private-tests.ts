// Trusted private-check control, compiled and invoked only inside the container.
import { implement } from './implementation.js';
const result = await implement({ requestId: 'r1', name: 'Ada', email: 'ada@example.com', locale: 'en', consent: true, trialDays: 7 });
if (result.reason !== 'OK' || result.displayName !== 'Ada') throw new Error('Private check failed');
console.log('PRIVATE CHECK PASS: trusted normalizer control');
