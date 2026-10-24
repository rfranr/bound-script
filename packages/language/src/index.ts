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

export interface PrintStatementNode {
  readonly kind: 'PrintStatement';
  readonly value: string;
  readonly range: SourceRange;
}

export interface StartHandlerNode {
  readonly kind: 'StartHandler';
  readonly statements: readonly PrintStatementNode[];
  readonly range: SourceRange;
}

export interface DirectorNode {
  readonly kind: 'Director';
  readonly name: string;
  readonly start: StartHandlerNode;
  readonly range: SourceRange;
}

export interface SystemNode {
  readonly kind: 'System';
  readonly name: string;
  readonly director: DirectorNode;
  readonly range: SourceRange;
}

export interface LanguageFrontend<TProgram> {
  parse(document: SourceDocument): Promise<ParseResult<TProgram>>;
  validate(program: TProgram): Promise<readonly LanguageDiagnostic[]>;
}

type TokenKind = 'identifier' | 'string' | 'leftBrace' | 'rightBrace' | 'leftParen' | 'rightParen' | 'eof';

interface Token {
  readonly kind: TokenKind;
  readonly lexeme: string;
  readonly value?: string;
  readonly range: SourceRange;
}

class SyntaxFailure extends Error {
  constructor(
    readonly diagnostic: LanguageDiagnostic
  ) {
    super(diagnostic.message);
  }
}

class Lexer {
  private offset = 0;
  private line = 1;
  private column = 1;

  constructor(private readonly document: SourceDocument) {}

  tokenize(): Token[] {
    const tokens: Token[] = [];

    while (!this.atEnd()) {
      this.skipWhitespace();
      if (this.atEnd()) break;

      const start = this.position();
      const character = this.peek();

      if (isIdentifierStart(character)) {
        tokens.push(this.readIdentifier(start));
        continue;
      }

      if (character === '"') {
        tokens.push(this.readString(start));
        continue;
      }

      const punctuation = punctuationKind(character);
      if (punctuation) {
        this.advance();
        tokens.push({
          kind: punctuation,
          lexeme: character,
          range: { start, end: this.position() }
        });
        continue;
      }

      this.fail('language.unexpected-character', `Unexpected character ${JSON.stringify(character)}.`, {
        start,
        end: this.positionAfterCurrentCharacter()
      });
    }

    const position = this.position();
    tokens.push({ kind: 'eof', lexeme: '', range: { start: position, end: position } });
    return tokens;
  }

  private readIdentifier(start: SourcePosition): Token {
    let lexeme = '';
    while (!this.atEnd() && isIdentifierPart(this.peek())) lexeme += this.advance();
    return { kind: 'identifier', lexeme, range: { start, end: this.position() } };
  }

  private readString(start: SourcePosition): Token {
    let lexeme = this.advance();
    let value = '';

    while (!this.atEnd()) {
      const character = this.advance();
      lexeme += character;

      if (character === '"') {
        return {
          kind: 'string',
          lexeme,
          value,
          range: { start, end: this.position() }
        };
      }

      if (character === '\n' || character === '\r') {
        this.fail('language.unterminated-string', 'String literals must end before the next line.', {
          start,
          end: this.position()
        });
      }

      if (character !== '\\') {
        value += character;
        continue;
      }

      if (this.atEnd()) break;
      const escaped = this.advance();
      lexeme += escaped;
      const decoded = decodeEscape(escaped);
      if (decoded === undefined) {
        this.fail('language.invalid-escape', `Unsupported escape sequence \\${escaped}.`, {
          start,
          end: this.position()
        });
      }
      value += decoded;
    }

    this.fail('language.unterminated-string', 'Unterminated string literal.', {
      start,
      end: this.position()
    });
  }

  private skipWhitespace(): void {
    while (!this.atEnd() && /\s/u.test(this.peek())) this.advance();
  }

  private peek(): string {
    return this.document.text[this.offset] ?? '';
  }

  private advance(): string {
    const character = this.peek();
    this.offset += 1;
    if (character === '\n') {
      this.line += 1;
      this.column = 1;
    } else {
      this.column += 1;
    }
    return character;
  }

  private positionAfterCurrentCharacter(): SourcePosition {
    const character = this.peek();
    return character === '\n'
      ? { line: this.line + 1, column: 1, offset: this.offset + 1 }
      : { line: this.line, column: this.column + 1, offset: this.offset + 1 };
  }

  private position(): SourcePosition {
    return { line: this.line, column: this.column, offset: this.offset };
  }

  private atEnd(): boolean {
    return this.offset >= this.document.text.length;
  }

  private fail(code: string, message: string, range: SourceRange): never {
    throw new SyntaxFailure({ code, message, severity: 'error', range });
  }
}

class Parser {
  private current = 0;

  constructor(private readonly tokens: readonly Token[]) {}

  parseSystem(): SystemNode {
    const start = this.expectWord('system').range.start;
    const name = this.expectIdentifier('Expected a system name.').lexeme;
    this.expect('leftBrace', 'Expected "{" after the system name.');
    const director = this.parseDirector();
    const end = this.expect('rightBrace', 'Expected "}" after the system declaration.').range.end;
    this.expect('eof', 'Expected the end of the source file.');

    return { kind: 'System', name, director, range: { start, end } };
  }

  private parseDirector(): DirectorNode {
    const start = this.expectWord('director').range.start;
    const name = this.expectIdentifier('Expected a director name.').lexeme;
    this.expect('leftBrace', 'Expected "{" after the director name.');
    const handler = this.parseStartHandler();
    const end = this.expect('rightBrace', 'Expected "}" after the director declaration.').range.end;
    return { kind: 'Director', name, start: handler, range: { start, end } };
  }

  private parseStartHandler(): StartHandlerNode {
    const start = this.expectWord('on').range.start;
    this.expectWord('start');
    this.expect('leftBrace', 'Expected "{" after "on start".');

    const statements: PrintStatementNode[] = [];
    while (!this.check('rightBrace') && !this.check('eof')) statements.push(this.parsePrint());

    const end = this.expect('rightBrace', 'Expected "}" after the start block.').range.end;
    return { kind: 'StartHandler', statements, range: { start, end } };
  }

  private parsePrint(): PrintStatementNode {
    const start = this.expectWord('print').range.start;
    this.expect('leftParen', 'Expected "(" after "print".');
    const value = this.expect('string', 'Expected a string literal as the print argument.');
    const end = this.expect('rightParen', 'Expected ")" after the print argument.').range.end;
    return { kind: 'PrintStatement', value: value.value ?? '', range: { start, end } };
  }

  private expectWord(word: string): Token {
    const token = this.peek();
    if (token.kind === 'identifier' && token.lexeme === word) return this.advance();
    this.fail(token, `Expected "${word}".`);
  }

  private expectIdentifier(message: string): Token {
    return this.expect('identifier', message);
  }

  private expect(kind: TokenKind, message: string): Token {
    const token = this.peek();
    if (token.kind === kind) return this.advance();
    this.fail(token, message);
  }

  private check(kind: TokenKind): boolean {
    return this.peek().kind === kind;
  }

  private peek(): Token {
    return this.tokens[this.current] ?? this.tokens[this.tokens.length - 1]!;
  }

  private advance(): Token {
    const token = this.peek();
    if (token.kind !== 'eof') this.current += 1;
    return token;
  }

  private fail(token: Token, message: string): never {
    const found = token.kind === 'eof' ? 'end of file' : JSON.stringify(token.lexeme);
    throw new SyntaxFailure({
      code: 'language.unexpected-token',
      message: `${message} Found ${found}.`,
      severity: 'error',
      range: token.range
    });
  }
}

/** Parses the deliberately small language subset used by the first executable slice. */
export function parseBoundScript(document: SourceDocument): ParseResult<SystemNode> {
  try {
    const tokens = new Lexer(document).tokenize();
    return { program: new Parser(tokens).parseSystem(), diagnostics: [] };
  } catch (error) {
    if (error instanceof SyntaxFailure) return { diagnostics: [error.diagnostic] };
    throw error;
  }
}

export class BoundScriptLanguageFrontend implements LanguageFrontend<SystemNode> {
  async parse(document: SourceDocument): Promise<ParseResult<SystemNode>> {
    return parseBoundScript(document);
  }

  async validate(_program: SystemNode): Promise<readonly LanguageDiagnostic[]> {
    return [];
  }
}

function isIdentifierStart(character: string): boolean {
  return /[A-Za-z_]/u.test(character);
}

function isIdentifierPart(character: string): boolean {
  return /[A-Za-z0-9_]/u.test(character);
}

function punctuationKind(character: string): TokenKind | undefined {
  switch (character) {
    case '{': return 'leftBrace';
    case '}': return 'rightBrace';
    case '(': return 'leftParen';
    case ')': return 'rightParen';
    default: return undefined;
  }
}

function decodeEscape(character: string): string | undefined {
  switch (character) {
    case '"': return '"';
    case '\\': return '\\';
    case 'n': return '\n';
    case 'r': return '\r';
    case 't': return '\t';
    default: return undefined;
  }
}
