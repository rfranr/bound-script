import type { Contact, NormalizeContact } from './normalize-contact.ts';

// Success: Welcome, NAME! <EMAIL>
// Failure: Invalid contact: CODE[, CODE...] (dependency order, no sorting).
export type RenderWelcome = (contact: Contact, normalize: NormalizeContact) => string;
