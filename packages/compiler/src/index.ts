import {
  DIRECTOR_PROGRAM_MEDIA_TYPE,
  DIRECTOR_PROGRAM_VERSION,
  EXECUTABLE_ARTIFACT_FORMAT,
  EXECUTABLE_ARTIFACT_VERSION,
  type DirectorProgram,
  type ExecutableArtifact
} from '@boundscript/artifact';
import type { SystemNode } from '@boundscript/language';

/** Public API version for the deterministic compilation boundary. */
export const COMPILER_API_VERSION = '0.1' as const;

export interface CompilationDiagnostic {
  readonly code: string;
  readonly message: string;
  readonly severity: 'error' | 'warning' | 'info';
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
  async compile(system: SystemNode): Promise<CompilationResult> {
    const target = `directors/${system.director.name}.json`;
    const program: DirectorProgram = {
      version: DIRECTOR_PROGRAM_VERSION,
      instructions: system.director.start.statements.map((statement) => ({
        operation: 'print',
        value: statement.value
      }))
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
