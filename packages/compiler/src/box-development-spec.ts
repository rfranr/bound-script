import type { Postcondition, PrimitiveType, ValueType } from '@boundscript/artifact';
import { validateBoundScript, type BoxNode, type SystemNode } from '@boundscript/language';

import type { CompilationDiagnostic } from './index.js';

/** One box's fully resolved data/behavior contract, independent of host bindings. */
export interface BoxDevelopmentSpec {
  readonly format: 'boundscript/box-development-spec';
  readonly version: 1;
  readonly system: string;
  readonly box: string;
  readonly operation: {
    readonly name: string;
    readonly input: { readonly name: string; readonly type: ValueType };
    readonly resultType: ValueType | 'void';
    readonly postcondition?: Postcondition;
  };
}

export type BoxSpecResult =
  | {
      readonly ok: true;
      readonly spec: BoxDevelopmentSpec;
      readonly diagnostics: readonly CompilationDiagnostic[];
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly CompilationDiagnostic[];
    };

/** Pure, synchronous extraction. Invalid systems never expose a partial specification. */
export function extractBoxDevelopmentSpec(system: SystemNode, boxName: string): BoxSpecResult {
  const diagnostics = validateBoundScript(system);
  if (diagnostics.some((diagnostic) => diagnostic.severity === 'error')) {
    return { ok: false, diagnostics };
  }
  const box = system.boxes.find((candidate) => candidate.name === boxName);
  if (!box) {
    return {
      ok: false,
      diagnostics: [{
        code: 'compiler.unknown-box',
        message: `Unknown box "${boxName}" in system "${system.name}".`,
        severity: 'error'
      }]
    };
  }
  return {
    ok: true,
    diagnostics,
    spec: {
      format: 'boundscript/box-development-spec',
      version: 1,
      system: system.name,
      box: box.name,
      operation: resolveBoxOperation(system, box)
    }
  };
}

/** @internal Shared declaration lowering; callers must first validate the whole system. */
export function resolveBoxOperation(system: SystemNode, box: BoxNode): BoxDevelopmentSpec['operation'] {
  const resolveType = (name: string): ValueType => {
    const record = system.types.find((type) => type.name === name);
    return record ? {
      kind: 'record',
      name: record.name,
      fields: record.fields.map((field) => ({ name: field.name, type: field.type as PrimitiveType }))
    } : name as PrimitiveType;
  };
  return {
    name: box.operation,
    input: { name: box.input, type: resolveType(box.inputType) },
    resultType: box.resultType === 'void' ? 'void' : resolveType(box.resultType),
    ...(box.ensure ? {
      postcondition: {
        kind: 'string-not-equal',
        target: box.ensure.field ? { kind: 'field', name: box.ensure.field } : { kind: 'result' },
        value: box.ensure.value
      }
    } : {})
  };
}
