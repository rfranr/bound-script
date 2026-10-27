import type { NormalizeContact } from "/inputs/contract";

export const normalizeContact: NormalizeContact = (contact) => ({
  name: contact.name.trim(),
  email: contact.email.trim().toLowerCase(),
});
