/** Public API version for the deterministic compilation boundary. */
export const COMPILER_API_VERSION = '0.1' as const;

export interface GeneratedFile {
  readonly path: string;
  readonly content: string;
}

export interface CompilationArtifact {
  readonly format: string;
  readonly entrypoint: string;
  readonly files: readonly GeneratedFile[];
  readonly metadata: Readonly<Record<string, unknown>>;
}

export interface CompilationDiagnostic {
  readonly code: string;
  readonly message: string;
  readonly severity: 'error' | 'warning' | 'info';
}

export interface CompilationResult {
  readonly artifact?: CompilationArtifact;
  readonly diagnostics: readonly CompilationDiagnostic[];
}

/**
 * Deterministically transforms a validated language model into runtime artifacts.
 * Agent-driven implementation generation belongs outside this boundary.
 */
export interface Compiler<TProgram> {
  compile(program: TProgram): Promise<CompilationResult>;
}
