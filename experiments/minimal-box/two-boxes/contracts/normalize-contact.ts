export interface Contact {
  name: string;
  email: string;
}

export type NormalizeContact = (contact: Contact) => Contact;
