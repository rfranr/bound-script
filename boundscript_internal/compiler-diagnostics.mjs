import ts from '/node_modules/typescript/lib/typescript.js';
import { writeFileSync } from 'node:fs';
import path from 'node:path';

// Only trusted host arguments define the source set and consumer contract.
const [contract = '/implementation/contract.ts', ...selected] = process.argv.slice(2);
const sources = selected.length ? selected : ['/implementation/implementation.ts'];
const owned = new Set(sources);
const options = {
  noEmit: true, strict: true, target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.NodeNext, allowImportingTsExtensions: true,
};
// Compile unused helpers as well as the signature consumer. No candidate executes.
const program = ts.createProgram(['/checks/check-contract.ts', ...sources], options);
const diagnostics = ts.getPreEmitDiagnostics(program);

function typeOnly(node) {
  if (ts.isImportTypeNode(node)) return true;
  if (ts.isExternalModuleReference(node)) return node.parent.isTypeOnly === true;
  if (ts.isImportDeclaration(node)) {
    const clause = node.importClause;
    return clause?.isTypeOnly === true || Boolean(clause && !clause.name &&
      clause.namedBindings && ts.isNamedImports(clause.namedBindings) &&
      clause.namedBindings.elements.length && clause.namedBindings.elements.every(e => e.isTypeOnly));
  }
  if (ts.isExportDeclaration(node)) return node.isTypeOnly || Boolean(node.exportClause &&
    ts.isNamedExports(node.exportClause) && node.exportClause.elements.length &&
    node.exportClause.elements.every(e => e.isTypeOnly));
  return false;
}

for (const filename of sources) {
  const source = program.getSourceFile(filename);
  if (!source) continue; // Missing roots produce ordinary compiler diagnostics.
  function reject(node, message) {
    diagnostics.push({category: ts.DiagnosticCategory.Error, code: 95001, file: source,
      start: node.getStart(source), length: node.getWidth(source), messageText: message});
  }
  function checkImports(node) {
    let specifier;
    if (ts.isImportDeclaration(node) || ts.isExportDeclaration(node))
      specifier = node.moduleSpecifier;
    else if (ts.isImportTypeNode(node))
      specifier = ts.isLiteralTypeNode(node.argument) ? node.argument.literal : node.argument;
    else if (ts.isExternalModuleReference(node)) specifier = node.expression;
    else if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword ||
             (ts.isIdentifier(node.expression) && node.expression.text === 'require')))
      specifier = node.arguments[0] ?? node;
    if (specifier) {
      if (!ts.isStringLiteralLike(specifier) || !/^(\.\/|\.\.\/)/.test(specifier.text)) {
        reject(specifier, 'Box imports must use literal relative paths, not sandbox or package paths.');
      } else {
        const resolved = ts.resolveModuleName(specifier.text, filename, options, ts.sys).resolvedModule;
        const target = resolved && path.posix.normalize(resolved.resolvedFileName);
        const requested = path.posix.resolve(path.posix.dirname(filename), specifier.text);
        // No .js-to-.ts rewriting, package redirects, aliases or query loaders.
        const direct = target && [requested, requested + '.ts', requested + '/index.ts'].includes(target);
        if (!direct || !(owned.has(target) || (target === contract && typeOnly(node))))
          reject(specifier, 'Box import must resolve to an inventoried source or the type-only consumer contract.');
      }
    }
    ts.forEachChild(node, checkImports);
  }
  checkImports(source);
  for (const reference of source.referencedFiles) {
    const target = path.posix.resolve(path.posix.dirname(filename), reference.fileName);
    if (path.posix.isAbsolute(reference.fileName) || reference.fileName.includes('\\') ||
        (!owned.has(target) && target !== contract))
      reject(source, 'Box reference must be relative and stay within the inventoried source or consumer contract.');
  }
  if (source.typeReferenceDirectives.length || source.libReferenceDirectives.length || source.hasNoDefaultLib)
    reject(source, 'Box reference directives cannot select external types or compiler libraries.');
}
const errors = diagnostics.filter(d => d.category === ts.DiagnosticCategory.Error);
writeFileSync('/verification-work/typescript-diagnostics.json', JSON.stringify({
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
