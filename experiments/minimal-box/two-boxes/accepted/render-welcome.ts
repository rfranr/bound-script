import type { RenderWelcome } from '/inputs/contract.ts';

export const renderWelcome: RenderWelcome = (contact, normalize) => {
  const result = normalize(contact);

  if (result.ok === true) {
    return `Welcome, ${result.contact.name}! <${result.contact.email}>`;
  }

  return `Invalid contact: ${result.errors.join(', ')}`;
};
