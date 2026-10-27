import type { Contact, NormalizeContact } from './normalize-contact.ts';

export type RenderWelcome = (contact: Contact, normalize: NormalizeContact) => string;
