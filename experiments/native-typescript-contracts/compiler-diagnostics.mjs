import ts from '/node_modules/typescript/lib/typescript.js';
import { writeFileSync } from 'node:fs';

// Same strict, no-emit compiler options as the original fixed CLI invocation.
// Compiler diagnostics only: candidate modules are never executed here.
const program = ts.createProgram(['/checks/check-contract.ts'], {
  noEmit: true, strict: true, target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.NodeNext, allowImportingTsExtensions: true,
});
const diagnostics = ts.getPreEmitDiagnostics(program);
const errors = diagnostics.filter(d => d.category === ts.DiagnosticCategory.Error);
writeFileSync('/implementation/typescript-diagnostics.json', JSON.stringify({
  complete: true, errorCount: errors.length,
  diagnostics: errors.slice(0, 20).map(d => {
    const location = d.file && d.start !== undefined
      ? d.file.getLineAndCharacterOfPosition(d.start) : null;
    const message = ts.flattenDiagnosticMessageText(d.messageText, '\n');
    return {
      code: d.code, file: d.file?.fileName,
      line: location ? location.line + 1 : null,
      column: location ? location.character + 1 : null,
      message: message.length <= 2000 ? message : '[oversized compiler diagnostic withheld]',
    };
  }),
}));
process.exitCode = errors.length ? 1 : 0;
