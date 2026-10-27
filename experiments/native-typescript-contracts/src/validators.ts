import typia from 'typia';
import type { Contact, NormalizeContactResult } from './contract';

// Typia's standard code generation expands these calls from the native types.
// equals rejects additional fields, including partial contact data on failures.
export const isContact = typia.createEquals<Contact>();
export const isResult = typia.createEquals<NormalizeContactResult>();
export const assertContact = typia.createAssertEquals<Contact>();
export const assertResult = typia.createAssertEquals<NormalizeContactResult>();
