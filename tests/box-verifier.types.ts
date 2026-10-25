import { parseBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';
import {
  verifyBoxImplementation, type BoxVerificationContract, type BoxVerificationFailure, type BoxVerificationResult
} from '@boundscript/runtime';

const decoded = parseBoxDevelopmentSpec('{}');
if (decoded.ok) {
  const view: BoxVerificationContract = decoded.spec;
  const stringCandidate = (input: string) => input;
  const recordCandidate = (user: { id: string }) => ({ message: user.id });
  const first: Promise<BoxVerificationResult> = verifyBoxImplementation(view, stringCandidate, 'fixed');
  const second: Promise<BoxVerificationResult> = verifyBoxImplementation(decoded.spec, recordCandidate, { id: '123' });
  void first;
  void second;
}

function consume(result: BoxVerificationResult): void {
  if (result.ok) {
    const output: unknown = result.output;
    // @ts-expect-error Dynamic descriptor validation does not prove a static string return type.
    const text: string = result.output;
    // @ts-expect-error Success has no failure field.
    void result.failure;
    void output;
    void text;
  } else {
    // @ts-expect-error Failed verification cannot expose partial output.
    void result.output;
    const failure = result.failure;
    switch (failure.kind) {
      case 'invalid-input':
      case 'invalid-output':
        void failure.expected;
        void failure.problem;
        break;
      case 'postcondition-failure': {
        const observed: string = failure.observed;
        void observed;
        void failure.predicate;
        break;
      }
      case 'inspection-failure': {
        const phase: 'input' | 'output' | 'postcondition' = failure.phase;
        void phase;
        void failure.message;
        break;
      }
      case 'invalid-contract':
      case 'invalid-implementation':
      case 'execution-failure':
        void failure.message;
        break;
      default: {
        const exhaustive: never = failure;
        void exhaustive;
      }
    }
  }
}

const failure: BoxVerificationFailure = { kind: 'inspection-failure', phase: 'input', message: 'getter' };
void consume;
void failure;
