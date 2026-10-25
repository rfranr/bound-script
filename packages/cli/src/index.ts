import { readFile } from 'node:fs/promises';

import { BoundScriptCompiler } from '@boundscript/compiler';
import {
  BoundScriptLanguageFrontend,
  type LanguageDiagnostic,
  type SourceDocument
} from '@boundscript/language';
import { BoundScriptRuntime } from '@boundscript/runtime';

export const CLI_API_VERSION = '0.1' as const;

export interface CliIo {
  readonly stdout: { write(value: string): void };
  readonly stderr: { write(value: string): void };
}

export async function runBoundCli(arguments_: readonly string[], io: CliIo): Promise<number> {
  const sourcePath = arguments_[0];
  if (!sourcePath || arguments_.length !== 1) {
    io.stderr.write('Usage: bound <source.bound>\n');
    return 1;
  }

  try {
    const document: SourceDocument = {
      uri: sourcePath,
      text: await readFile(sourcePath, 'utf8')
    };
    const language = new BoundScriptLanguageFrontend();
    const parsed = await language.parse(document);

    if (!parsed.program) {
      for (const diagnostic of parsed.diagnostics) {
        io.stderr.write(`${formatDiagnostic(document, diagnostic)}\n`);
      }
      return 1;
    }

    const validationDiagnostics = await language.validate(parsed.program);
    if (validationDiagnostics.some((diagnostic) => diagnostic.severity === 'error')) {
      for (const diagnostic of validationDiagnostics) {
        io.stderr.write(`${formatDiagnostic(document, diagnostic)}\n`);
      }
      return 1;
    }

    const compilation = await new BoundScriptCompiler().compile(parsed.program);
    if (!compilation.ok) {
      for (const diagnostic of compilation.diagnostics) {
        io.stderr.write(`${formatDiagnostic(document, diagnostic)}\n`);
      }
      return 1;
    }

    const runtime = new BoundScriptRuntime({
      writeLine(value) {
        io.stdout.write(`${value}\n`);
      }
    });
    await runtime.execute(compilation.artifact, { entrypoint: 'start' });
    return 0;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    io.stderr.write(`bound: ${message}\n`);
    return 1;
  }
}

function formatDiagnostic(document: SourceDocument, diagnostic: LanguageDiagnostic): string {
  const location = diagnostic.range
    ? `${document.uri}:${diagnostic.range.start.line}:${diagnostic.range.start.column}`
    : document.uri;
  return `${location}: ${diagnostic.severity} ${diagnostic.code}: ${diagnostic.message}`;
}
