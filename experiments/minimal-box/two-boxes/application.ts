import type { Contact } from './contracts/normalize-contact.ts';
import { normalizeContact } from './accepted/normalize-contact.ts';
import { renderWelcome } from './accepted/render-welcome.ts';

// Ordinary wiring forwards the richer success/failure result through the renderer.
// Neither agent receives this file or the peer artifact.
export function welcomeContact(contact: Contact): string {
  return renderWelcome(contact, normalizeContact);
}
