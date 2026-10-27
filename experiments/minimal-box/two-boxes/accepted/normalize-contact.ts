import type { ContactError, NormalizeContact } from '/inputs/contract';

export const normalizeContact: NormalizeContact = (contact) => {
  const name = contact.name.trim().replace(/\s+/gu, ' ');
  const email = contact.email.trim().toLowerCase();
  const errors: ContactError[] = [];

  if (name === '') {
    errors.push('name.required');
  }

  if (email === '') {
    errors.push('email.required');
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(email)) {
    errors.push('email.invalid');
  }

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  return { ok: true, contact: { name, email } };
};
