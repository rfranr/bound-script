import type { RenderWelcome } from '/inputs/contract.ts';

export const renderWelcome: RenderWelcome = (contact, normalize) => {
  const normalized = normalize(contact);
  return `Welcome, ${normalized.name}! <${normalized.email}>`;
};
