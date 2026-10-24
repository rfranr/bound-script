import { createBoundScriptServices } from './boundscript-services.js';
import type { SystemNode } from './generated/ast.js';

export type {
  DirectorNode,
  PrintStatementNode,
  StartHandlerNode,
  SystemNode
} from './generated/ast.js';
export { createBoundScriptServices } from './boundscript-services.js';

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

export interface LanguageFrontend<TProgram> {
  parse(document: SourceDocument): Promise<ParseResult<TProgram>>;
  validate(program: TProgram): Promise<readonly LanguageDiagnostic[]>;
}

const services = createBoundScriptServices();

/** Parses the deliberately small executable subset defined in `boundscript.langium`. */
export function parseBoundScript(document: SourceDocument): ParseResult<SystemNode> {
  const result = services.language.parser.LangiumParser.parse<SystemNode>(document.text);
  const diagnostics: LanguageDiagnostic[] = [
    ...result.lexerErrors.map((error) => ({
      code: 'language.lexer-error',
      message: error.message,
      severity: 'error' as const,
      range: lexerErrorRange(error)
    })),
    ...result.parserErrors.map((error) => ({
      code: 'language.parser-error',
      message: error.message,
      severity: 'error' as const,
      range: tokenRange(error.token, document.text)
    }))
  ];

  return diagnostics.length === 0
    ? { program: result.value, diagnostics }
    : { diagnostics };
}

export class BoundScriptLanguageFrontend implements LanguageFrontend<SystemNode> {
  async parse(document: SourceDocument): Promise<ParseResult<SystemNode>> {
    return parseBoundScript(document);
  }

  async validate(_program: SystemNode): Promise<readonly LanguageDiagnostic[]> {
    return [];
  }
}

interface LexerErrorLocation {
  readonly line: number | undefined;
  readonly column: number | undefined;
  readonly offset: number;
  readonly length: number;
}

interface TokenLocation {
  readonly image: string;
  readonly startLine?: number | undefined;
  readonly startColumn?: number | undefined;
  readonly startOffset: number;
  readonly endLine?: number | undefined;
  readonly endColumn?: number | undefined;
  readonly endOffset?: number | undefined;
}

function lexerErrorRange(error: LexerErrorLocation): SourceRange {
  const line = error.line ?? 1;
  const column = error.column ?? 1;
  return {
    start: { line, column, offset: error.offset },
    end: {
      line,
      column: column + Math.max(error.length, 1),
      offset: error.offset + Math.max(error.length, 1)
    }
  };
}

function tokenRange(token: TokenLocation, source: string): SourceRange {
  const startOffset = Number.isInteger(token.startOffset) && token.startOffset >= 0
    ? token.startOffset
    : source.length;
  const fallback = positionAtOffset(source, startOffset);
  const startLine = isPositiveInteger(token.startLine) ? token.startLine : fallback.line;
  const startColumn = isPositiveInteger(token.startColumn) ? token.startColumn : fallback.column;
  const endOffset = token.endOffset !== undefined &&
      Number.isInteger(token.endOffset) &&
      token.endOffset >= 0
    ? token.endOffset + 1
    : startOffset + token.image.length;
  return {
    start: { line: startLine, column: startColumn, offset: startOffset },
    end: {
      line: isPositiveInteger(token.endLine) ? token.endLine : startLine,
      column: isPositiveInteger(token.endColumn)
        ? token.endColumn + 1
        : startColumn + token.image.length,
      offset: endOffset
    }
  };
}

function isPositiveInteger(value: number | undefined): value is number {
  return value !== undefined && Number.isInteger(value) && value > 0;
}

function positionAtOffset(source: string, targetOffset: number): SourcePosition {
  let line = 1;
  let column = 1;
  for (let offset = 0; offset < targetOffset; offset += 1) {
    if (source[offset] === '\n') {
      line += 1;
      column = 1;
    } else {
      column += 1;
    }
  }
  return { line, column, offset: targetOffset };
}
