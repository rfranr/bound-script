import type { tags } from "typia";

export interface WelcomeContact {
  readonly name: string & tags.MinLength<1>;
  readonly email: string & tags.MinLength<1>;
  readonly phone: string & tags.MinLength<1>;
}

export type WelcomeMessage = string;

export type RenderWelcome =
  (contact: WelcomeContact) => WelcomeMessage;
