import {
  DIRECTOR_PROGRAM_MEDIA_TYPE,
  DIRECTOR_PROGRAM_VERSION,
  EXECUTABLE_ARTIFACT_FORMAT,
  EXECUTABLE_ARTIFACT_VERSION,
  type DirectorProgram,
  type InvocationArgument,
  type ExecutableArtifact
} from '@boundscript/artifact';
import { validateBoundScript, type SourceRange, type SystemNode } from '@boundscript/language';

import { resolveBoxOperation } from './box-development-spec.js';

export { extractBoxDevelopmentSpec } from './box-development-spec.js';
export type { BoxDevelopmentSpec, BoxSpecResult } from './box-development-spec.js';
export { BoxSpecValidationError, parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec } from './box-spec-json.js';

/** Explicit box name to host implementation ID bindings, resolved before compilation. */
export type BoxBindings = Readonly<Record<string, string>>;

/** Public API version for the deterministic compilation boundary. */
export const COMPILER_API_VERSION = '0.1' as const;

export interface CompilationDiagnostic {
  readonly code: string;
  readonly message: string;
  readonly severity: 'error' | 'warning' | 'info';
  readonly range?: SourceRange;
}

export type CompilationResult =
  | {
      readonly ok: true;
      readonly artifact: ExecutableArtifact;
      readonly diagnostics: readonly CompilationDiagnostic[];
    }
  | {
      readonly ok: false;
      readonly diagnostics: readonly CompilationDiagnostic[];
    };

/**
 * Deterministically transforms a fully resolved compilation input into an
 * executable artifact. The compiler must not invoke build-time AI agents.
 */
export interface Compiler<TCompilationInput> {
  compile(input: TCompilationInput): Promise<CompilationResult>;
}

/** Compiles the first language subset into a small, runtime-neutral artifact envelope. */
export class BoundScriptCompiler implements Compiler<SystemNode> {
  async compile(system: SystemNode, bindings: BoxBindings = {}): Promise<CompilationResult> {
    const diagnostics: CompilationDiagnostic[] = [...validateBoundScript(system)];
    for (const box of system.boxes) {
      if (!Object.hasOwn(bindings, box.name) || !bindings[box.name]?.trim()) {
        diagnostics.push({
          code: 'compiler.missing-implementation',
          message: `Missing implementation binding for box "${box.name}".`,
          severity: 'error'
        });
      }
    }
    if (diagnostics.length > 0) return { ok: false, diagnostics };

    const target = `directors/${system.director.name}.json`;
    const program: DirectorProgram = {
      version: DIRECTOR_PROGRAM_VERSION,
      instructions: system.director.start.statements.map((statement) => {
        if (statement.$type === 'InvocationStatementNode') {
          const box = system.boxes.find((box) => box.name === statement.box)!;
          const contract = resolveBoxOperation(system, box);
          const argument: InvocationArgument = statement.variable
            ? { kind: 'variable', name: statement.variable }
            : { kind: 'literal', value: statement.argument! };
          const invocation = {
            operation: 'invoke' as const,
            implementation: bindings[statement.box]!,
            box: box.name,
            boxOperation: contract.name,
            inputType: contract.input.type,
            argument
          };
          return contract.resultType === 'void'
            ? { ...invocation, resultType: 'void' }
            : {
                ...invocation, resultType: contract.resultType, result: statement.name!,
                ...(contract.postcondition ? { postcondition: contract.postcondition } : {})
              };
        }
        return statement.variable
          ? { operation: 'print-variable', variable: statement.variable }
          : { operation: 'print', value: statement.value! };
      })
    };

    return {
      ok: true,
      diagnostics: [],
      artifact: {
        format: EXECUTABLE_ARTIFACT_FORMAT,
        version: EXECUTABLE_ARTIFACT_VERSION,
        system: system.name,
        entrypoints: [{ name: 'start', target }],
        assets: [
          {
            path: target,
            mediaType: DIRECTOR_PROGRAM_MEDIA_TYPE,
            bytes: new TextEncoder().encode(JSON.stringify(program))
          }
        ]
      }
    };
  }
}
