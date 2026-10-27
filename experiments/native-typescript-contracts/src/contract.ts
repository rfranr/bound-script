import type { tags } from "typia";

export interface Contact {
  readonly name: string;
  readonly email: string;
  readonly phone: string;
}

export interface NormalizedContact {
  readonly name: string & tags.MinLength<1>;
  readonly email: string & tags.MinLength<1>;
  readonly phone: string & tags.MinLength<1>;
}

export type ContactError =
  | "name.required"
  | "email.required"
  | "email.invalid"
  | "phone.required"
  | "phone.invalid";

export type NormalizeContactResult =
  | { readonly ok: true; readonly contact: NormalizedContact }
  | { readonly ok: false; readonly errors: ContactError[] };

export type NormalizeContact =
  (contact: Contact) => NormalizeContactResult;