/** Public API version for the language-definition boundary. */
export const LANGUAGE_API_VERSION = '0.1' as const;

export interface SourceDocument {
  readonly uri: string;
  readonly text: string;
}

export interface SourcePosition {
  readonly line: number;
  readonly column: number;
  readonly offset: number;
}

export interface SourceRange {
  readonly start: SourcePosition;
  readonly end: SourcePosition;
}

export type DiagnosticSeverity = 'error' | 'warning' | 'info';

export interface LanguageDiagnostic {
  readonly code: string;
  readonly message: string;
  readonly severity: DiagnosticSeverity;
  readonly range?: SourceRange;
}

export interface ParseResult<TProgram> {
  readonly program?: TProgram;
  readonly diagnostics: readonly LanguageDiagnostic[];
}

/**
 * Boundary for a future parser and semantic validator.
 * The concrete AST is intentionally left undefined until the language is designed.
 */
export interface LanguageFrontend<TProgram> {
  parse(document: SourceDocument): Promise<ParseResult<TProgram>>;
  validate(program: TProgram): Promise<readonly LanguageDiagnostic[]>;
}
