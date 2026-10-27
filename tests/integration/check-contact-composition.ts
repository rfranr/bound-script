// Application-owned compile-only check, never a standalone Box input or oracle.
import type {
  Contact, NormalizeContact, NormalizeContactResult,
} from '../../experiments/native-typescript-contracts/src/contract.ts';
import type {
  RenderWelcome, WelcomeContact, WelcomeMessage,
} from '../../experiments/render-welcome-native/src/contract.ts';

declare const rawContact: Contact;
declare const normalizeContact: NormalizeContact;
declare const renderWelcome: RenderWelcome;
declare const publicSuccess: Extract<NormalizeContactResult, { ok: true }>;

const consumerInput: WelcomeContact = publicSuccess.contact;
const directMessage: WelcomeMessage = renderWelcome(consumerInput);

const result = normalizeContact(rawContact);
if (result.ok) {
  const message: WelcomeMessage = renderWelcome(result.contact);
  void message;
} else {
  // The application handles errors. The failure branch is not formatter input.
  // @ts-expect-error Normalization failures are not normalized contacts.
  renderWelcome(result);
}
void directMessage;
