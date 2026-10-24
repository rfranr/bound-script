import type { ExecutableArtifact } from '@boundscript/artifact';

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
