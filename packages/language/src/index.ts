import { GrammarUtils, type AstNode } from 'langium';

import { createBoundScriptServices } from './boundscript-services.js';
import type { SystemNode } from './generated/ast.js';

export type {
  BoxNode,
  EnsureNode,
  RecordTypeNode,
  FieldNode,
  InvocationStatementNode,
  StatementNode,
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

  async validate(program: SystemNode): Promise<readonly LanguageDiagnostic[]> {
    return validateBoundScript(program);
  }
}

/** Semantic checks shared by the frontend and compiler; no implementation loading. */
export function validateBoundScript(program: SystemNode): readonly LanguageDiagnostic[] {
  const diagnostics: LanguageDiagnostic[] = [];
  const report = (code: string, message: string, node: AstNode, property: string) => {
    const cst = GrammarUtils.findNodeForProperty(node.$cstNode, property);
    diagnostics.push({
      code: `language.${code}`,
      message,
      severity: 'error',
      ...(cst ? {
        range: {
          start: { line: cst.range.start.line + 1, column: cst.range.start.character + 1, offset: cst.offset },
          end: { line: cst.range.end.line + 1, column: cst.range.end.character + 1, offset: cst.end }
        }
      } : {})
    });
  };
  const primitiveTypes = new Set(['string', 'number', 'boolean']);
  const types = new Set<string>();
  for (const type of program.types) {
    if (types.has(type.name)) report('duplicate-type', `Duplicate type "${type.name}".`, type, 'name');
    types.add(type.name);
  }
  for (const type of program.types) {
    const fields = new Set<string>();
    for (const field of type.fields) {
      if (fields.has(field.name)) report('duplicate-field', `Duplicate field "${field.name}" in type "${type.name}".`, field, 'name');
      fields.add(field.name);
      if (!primitiveTypes.has(field.type)) {
        const known = field.type === 'void' || types.has(field.type);
        report(known ? 'invalid-field-type' : 'unknown-type',
          known ? `Field "${type.name}.${field.name}" must have a primitive type, not "${field.type}".`
            : `Unknown type "${field.type}".`, field, 'type');
      }
    }
  }
  const boxes = new Map<string, SystemNode['boxes'][number]>();
  for (const box of program.boxes) {
    if (boxes.has(box.name)) report('duplicate-box', `Duplicate box "${box.name}".`, box, 'name');
    boxes.set(box.name, box);
    for (const property of ['inputType', 'resultType'] as const) {
      const type = box[property];
      if (type === 'void' && property === 'inputType') {
        report('void-input', `Input of "${box.name}.${box.operation}" cannot be void.`, box, property);
      } else if (type !== 'void' && !primitiveTypes.has(type) && !types.has(type)) {
        report('unknown-type', `Unknown type "${type}".`, box, property);
      }
    }
    const ensure = box.ensure;
    if (ensure) {
      const record = program.types.find((type) => type.name === box.resultType);
      if (ensure.target !== 'result') {
        report('ensure-invalid-target', 'Postcondition target must be result or result.field, not an input or variable.', ensure, 'target');
      } else if (box.resultType === 'void') {
        report('ensure-void-result', `Postcondition on "${box.name}.${box.operation}" cannot target a void result.`, ensure, 'target');
      } else if (ensure.field && record) {
        const field = record.fields.find((field) => field.name === ensure.field);
        if (!field) {
          report('ensure-unknown-field', `Unknown postcondition field "${ensure.field}" on type "${record.name}".`, ensure, 'field');
        } else if (field.type !== 'string') {
          report('ensure-non-string-field', `Postcondition field "${record.name}.${field.name}" must be string, not "${field.type}".`, ensure, 'field');
        }
      } else if (ensure.field || box.resultType !== 'string') {
        report('ensure-invalid-target', `Postcondition must target a string result or a string record field, not "${box.resultType}".`,
          ensure, ensure.field ? 'field' : 'target');
      }
    }
  }
  const variables = new Map<string, string>();
  for (const statement of program.director.start.statements) {
    if (statement.$type === 'InvocationStatementNode') {
      const box = boxes.get(statement.box);
      if (!box) report('unknown-box', `Unknown box "${statement.box}".`, statement, 'box');
      else if (box.operation !== statement.operation) {
        report('unknown-operation', `Unknown operation "${statement.operation}" on box "${box.name}".`, statement, 'operation');
      } else if (box.resultType === 'void' && statement.name) {
        report('void-result-assignment', `Cannot assign the void result of "${box.name}.${box.operation}".`, statement, 'name');
      } else if (box.resultType !== 'void' && !statement.name) {
        report(box.resultType === 'string' ? 'unassigned-string-result' : 'unassigned-result',
          `${box.resultType === 'string' ? 'String' : `Type "${box.resultType}"`} result of "${box.name}.${box.operation}" must be assigned.`, statement, 'operation');
      }
      // Check the argument before declaring the result, so self-references are invalid.
      if (statement.variable && !variables.has(statement.variable)) {
        report('unknown-variable', `Unknown variable "${statement.variable}".`, statement, 'variable');
      }
      const argumentType = statement.variable ? variables.get(statement.variable) : 'string';
      if (box && box.operation === statement.operation && argumentType !== undefined && argumentType !== box.inputType) {
        report('incompatible-argument', `Argument of "${box.name}.${box.operation}" expects "${box.inputType}", got "${argumentType}".`,
          statement, statement.variable ? 'variable' : 'argument');
      }
      if (statement.name) {
        if (variables.has(statement.name)) {
          report('duplicate-variable', `Duplicate variable "${statement.name}".`, statement, 'name');
        }
        // The type comes only from the declared operation result, not expression inference.
        variables.set(statement.name, box?.resultType ?? 'void');
      }
    } else if (statement.variable) {
      if (!variables.has(statement.variable)) {
        report('unknown-variable', `Unknown variable "${statement.variable}".`, statement, 'variable');
      } else if (variables.get(statement.variable) !== 'string') {
        report('incompatible-print', `print expects "string", got "${variables.get(statement.variable)}".`, statement, 'variable');
      }
    }
  }
  return diagnostics;
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
