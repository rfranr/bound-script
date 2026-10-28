import ts from '/node_modules/typescript/lib/typescript.js';
import { writeFileSync } from 'node:fs';

// Same strict, no-emit compiler options as the original fixed CLI invocation.
// Compiler diagnostics only: candidate modules are never executed here.
const program = ts.createProgram(['/checks/check-contract.ts'], {
  noEmit: true, strict: true, target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.NodeNext, allowImportingTsExtensions: true,
});
const diagnostics = ts.getPreEmitDiagnostics(program);
// Source imports must survive relocation, not merely resolve in this sandbox.
// Current Boxes have no permitted package dependencies.
const candidate = program.getSourceFile('/implementation/implementation.ts');
function checkImports(node) {
  let specifier;
  if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node))
    specifier = node.moduleSpecifier;
  else if (ts.isImportTypeNode(node) && ts.isLiteralTypeNode(node.argument))
    specifier = node.argument.literal;
  else if (ts.isExternalModuleReference(node)) specifier = node.expression;
  else if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
           (ts.isIdentifier(node.expression) && node.expression.text === 'require')))
    specifier = node.arguments[0] ?? node;
  if (specifier && (!ts.isStringLiteralLike(specifier) ||
      !/^(\.\/|\.\.\/)/.test(specifier.text))) {
    diagnostics.push({ category: ts.DiagnosticCategory.Error, code: 95001,
      file: candidate, start: specifier.getStart(candidate), length: specifier.getWidth(candidate),
      messageText: 'Box imports must use literal relative paths, not sandbox or package paths.' });
  }
  ts.forEachChild(node, checkImports);
}
if (candidate) checkImports(candidate);
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
