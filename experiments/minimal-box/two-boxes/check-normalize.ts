import type { NormalizeContact } from '/inputs/contract.ts';
import { normalizeContact } from '/implementation/implementation.ts';

const checked: NormalizeContact = normalizeContact;
const result = checked({ name: 'Ada', email: 'ada@example.test' });
if (result.ok) {
  const contact: import('/inputs/contract.ts').Contact = result.contact;
  void contact;
  // @ts-expect-error Success has no validation errors.
  void result.errors;
} else {
  const errors: import('/inputs/contract.ts').ContactError[] = result.errors;
  void errors;
  // @ts-expect-error Failure exposes no partial contact.
  void result.contact;
}
