// TRUSTED HARNESS CONTROL ONLY. Never deliver to an implementation agent.
import type { Implementation } from '../handoff/generated/contract.js';
const trim = (s: string) => s.replace(/^[ \t\r\n]+|[ \t\r\n]+$/g, '');
const lower = (s: string) => s.replace(/[A-Z]/g, c => c.toLowerCase());
export const implement: Implementation = submission => {
    const requestId = trim(submission.requestId);
    const displayName = trim(submission.name).replace(/[ \t\r\n]+/g, ' ');
    const email = lower(trim(submission.email));
    const preferred = lower(trim(submission.locale));
    const locale = preferred === 'fr' ? 'fr' : 'en';
    const { consent, trialDays } = submission;
    const reason = !/^[A-Za-z0-9_-]{1,32}$/.test(requestId) ? 'BAD_ID'
        : displayName.length < 1 || displayName.length > 80 || /[\x00-\x1f\x7f]/.test(displayName) ? 'BAD_NAME'
        : !/^[a-z0-9]+(?:[._+-][a-z0-9]+)*@[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$/.test(email) ? 'BAD_EMAIL'
        : !Number.isInteger(trialDays) || trialDays < 0 || trialDays > 30 ? 'BAD_DAYS' : 'OK';
    return { requestId, displayName, email, locale, consent, trialDays, valid: reason === 'OK', reason };
};
