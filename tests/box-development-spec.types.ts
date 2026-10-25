import type { ValueType } from '@boundscript/artifact';
import {
  extractBoxDevelopmentSpec,
  parseBoxDevelopmentSpec,
  serializeBoxDevelopmentSpec,
  type BoxDevelopmentSpec,
  type BoxSpecResult
} from '@boundscript/compiler';
import type { SystemNode } from '@boundscript/language';

// Extraction is synchronous and does not accept implementation bindings.
const extract: (system: SystemNode, name: string) => BoxSpecResult = extractBoxDevelopmentSpec;
const parse: (json: string) => BoxSpecResult = parseBoxDevelopmentSpec;
const serialize: (spec: BoxDevelopmentSpec) => string = serializeBoxDevelopmentSpec;

function consume(result: BoxSpecResult): void {
  if (result.ok) {
    const spec: BoxDevelopmentSpec = result.spec;
    const input: ValueType = spec.operation.input.type;
    const output: ValueType | 'void' = spec.operation.resultType;
    // @ts-expect-error The public specification is readonly.
    spec.box = 'Changed';
    void input;
    void output;
  } else {
    // @ts-expect-error Failed extraction cannot expose a partial specification.
    void result.spec;
  }
}

void extract;
void parse;
void serialize;
void consume;
