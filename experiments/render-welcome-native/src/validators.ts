import typia from "typia";
import type { WelcomeContact, WelcomeMessage } from "./contract";

export const isContact = typia.createEquals<WelcomeContact>();
export const isMessage = typia.createEquals<WelcomeMessage>();
export const assertContact = typia.createAssertEquals<WelcomeContact>();
export const assertMessage = typia.createAssertEquals<WelcomeMessage>();
