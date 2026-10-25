import type { Postcondition, ValueType } from '@boundscript/artifact';

import {
  isPostcondition, isRecord, isValueType, postconditionViolation, resultTypeProblem, valueTypeProblem
} from './contract-checks.js';
import type { BoxImplementation } from './index.js';

/** Structural consumer view of a decoded BoxDevelopmentSpec, not another spec/schema. */
export interface BoxVerificationContract {
  readonly box: string;
  readonly operation: {
    readonly name: string;
    readonly input: { readonly type: ValueType };
    readonly resultType: ValueType | 'void';
    readonly postcondition?: Postcondition;
  };
}

export type BoxVerificationFailure =
  | { readonly kind: 'invalid-contract'; readonly message: string }
  | { readonly kind: 'invalid-implementation'; readonly message: string }
  | { readonly kind: 'invalid-input'; readonly expected: ValueType; readonly problem: string }
  | { readonly kind: 'execution-failure'; readonly message: string }
  | { readonly kind: 'invalid-output'; readonly expected: ValueType | 'void'; readonly problem: string }
  | { readonly kind: 'postcondition-failure'; readonly predicate: Postcondition; readonly observed: string }
  | { readonly kind: 'inspection-failure'; readonly phase: 'input' | 'output' | 'postcondition'; readonly message: string };

export type BoxVerificationResult =
  | { readonly ok: true; readonly output: unknown }
  | { readonly ok: false; readonly failure: BoxVerificationFailure };

/**
 * Check one fixed-input invocation of trusted, already-loaded code. Decode portable specs with
 * the strict codec first; this view does not validate their envelope/version. Keep the contract
 * stable during verification. Values pass by reference; getters/mutation need not be deterministic.
 * Inspection errors are not proven contract violations. No isolation, rollback or timeout is provided.
 */
export async function verifyBoxImplementation(
  contract: BoxVerificationContract,
  implementation: BoxImplementation<any>,
  input: unknown
): Promise<BoxVerificationResult> {
  if (!isVerificationContract(contract)) {
    return { ok: false, failure: { kind: 'invalid-contract', message: 'Invalid Box verification contract view.' } };
  }
  if (typeof implementation !== 'function') {
    return { ok: false, failure: { kind: 'invalid-implementation', message: 'Implementation must be a function.' } };
  }

  const operation = contract.operation;
  try {
    const problem = valueTypeProblem(input, operation.input.type);
    if (problem) return { ok: false, failure: { kind: 'invalid-input', expected: operation.input.type, problem } };
  } catch (error) {
    return inspectionFailure('input', error);
  }

  let output: unknown;
  try {
    output = await implementation(input);
  } catch (error) {
    return { ok: false, failure: { kind: 'execution-failure', message: errorMessage(error) } };
  }

  try {
    const problem = resultTypeProblem(output, operation.resultType);
    if (problem) return { ok: false, failure: { kind: 'invalid-output', expected: operation.resultType, problem } };
  } catch (error) {
    return inspectionFailure('output', error);
  }

  if (operation.postcondition) {
    try {
      const observed = postconditionViolation(output, operation.postcondition);
      if (observed !== undefined) {
        return { ok: false, failure: { kind: 'postcondition-failure', predicate: operation.postcondition, observed } };
      }
    } catch (error) {
      return inspectionFailure('postcondition', error);
    }
  }
  return { ok: true, output };
}

/** Defensive descriptor check only; portable-envelope authority remains with the strict decoder. */
function isVerificationContract(value: unknown): value is BoxVerificationContract {
  if (!isRecord(value) || typeof value.box !== 'string' || !value.box || !isRecord(value.operation)) return false;
  const operation = value.operation;
  if (typeof operation.name !== 'string' || !operation.name || !isRecord(operation.input) ||
      !isValueType(operation.input.type)) return false;
  const hasPostcondition = 'postcondition' in operation;
  return operation.resultType === 'void'
    ? !hasPostcondition
    : isValueType(operation.resultType) &&
      (!hasPostcondition || isPostcondition(operation.postcondition, operation.resultType));
}

function inspectionFailure(phase: 'input' | 'output' | 'postcondition', error: unknown): BoxVerificationResult {
  return { ok: false, failure: { kind: 'inspection-failure', phase, message: errorMessage(error) } };
}

/** Do not serialize arbitrary thrown objects or invoke their conversion hooks. */
function errorMessage(error: unknown): string {
  try {
    if (error instanceof Error && typeof error.message === 'string') return error.message;
    if (error === null || (typeof error !== 'object' && typeof error !== 'function')) return String(error);
  } catch {
    // A thrown object's message may itself be an accessor. Never mask the original stage.
  }
  return 'An error was thrown without a readable message.';
}
