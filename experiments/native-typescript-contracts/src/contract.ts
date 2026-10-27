export interface Contact {
  readonly name: string;
  readonly email: string;
}

export type ContactError = 'name.required' | 'email.required' | 'email.invalid';

export type NormalizeContactResult =
  | { ok: true; contact: Contact }
  | { ok: false; errors: ContactError[] };

export type NormalizeContact = (contact: Contact) => NormalizeContactResult;
