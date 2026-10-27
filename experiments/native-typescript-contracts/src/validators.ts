import typia from "typia";

import type {
  Contact,
  NormalizedContact,
  NormalizeContactResult
} from "./contract";

export const isContact =
  typia.createEquals<Contact>();

export const isResult =
  typia.createEquals<NormalizeContactResult>();

export const assertContact =
  typia.createAssertEquals<Contact>();

export const assertResult =
  typia.createAssertEquals<NormalizeContactResult>();

export const assertNormalizedContact =
  typia.createAssertEquals<NormalizedContact>();