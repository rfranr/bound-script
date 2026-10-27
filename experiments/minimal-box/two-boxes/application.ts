import type { Contact } from './contracts/normalize-contact.ts';
import { normalizeContact } from './accepted/normalize-contact.ts';
import { renderWelcome } from './accepted/render-welcome.ts';

// Ordinary application wiring; neither agent receives this file or the peer artifact.
export function welcomeContact(contact: Contact): string {
  return renderWelcome(contact, normalizeContact);
}
