// TRUSTED HARNESS CONTROL ONLY. Never deliver to an implementation agent.
import type { Implementation } from '../handoff/generated/contract.js';
const escaped: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const implement: Implementation = contact => {
    const { requestId, displayName, email, locale, consent, trialDays, valid, reason } = contact;
    if (!valid || !consent) return {
        requestId, send: false, recipient: '', subject: 'Not sent', html: '', reason: !valid ? reason : 'NO_CONSENT'
    };
    const name = displayName.replace(/[&<>"']/g, c => escaped[c]!);
    const fr = locale === 'fr';
    const greeting = fr ? `<p>Bonjour, ${name} !</p>` : `<p>Hello, ${name}!</p>`;
    const trial = trialDays === 0
        ? fr ? '<p>Aucun essai inclus.</p>' : '<p>No trial is included.</p>'
        : fr ? `<p>Votre essai dure ${trialDays} jours.</p>` : `<p>Your trial lasts ${trialDays} days.</p>`;
    return { requestId, send: true, recipient: email, subject: fr ? 'Bienvenue' : 'Welcome', html: greeting + trial, reason: 'OK' };
};
