// Runs only inside the offline evaluation container. Fixed NodeNext config.
import assert from 'node:assert/strict';
import { cp, mkdir, readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import ts from '/tools/lib/typescript.js';
const boxes = process.argv.slice(2);
for (const box of boxes) {
    assert.ok(['normalize', 'render'].includes(box));
    const root = `/scratch/${box}`;
    await mkdir(root, { recursive: true });
    for (const name of ['candidate', 'handoff']) await cp(`/input/${box}/${name}`, `${root}/${name}`, { recursive: true });
    for (const name of ['consumer.ts', 'tsconfig.json', 'package.json']) await cp(`/libraries/${name}`, `${root}/${name}`);
    async function review(dir) {
        for (const e of await readdir(dir, { withFileTypes: true })) {
            const file = path.join(dir, e.name);
            if (e.isDirectory()) { await review(file); continue; }
            assert.ok(e.isFile() && e.name.endsWith('.ts') && !e.name.endsWith('.d.ts'), `Unapproved file: ${file}`);
            const source = ts.createSourceFile(file, await readFile(file, 'utf8'), ts.ScriptTarget.ES2022, true);
            function checkImport(spec, typeOnly) {
                assert.ok(spec && ts.isStringLiteral(spec), 'Computed import is not permitted');
                const target = path.resolve(path.dirname(file), spec.text);
                if (typeOnly && target === `${root}/handoff/generated/contract.js`) return;
                assert.ok(spec.text.startsWith('./') || spec.text.startsWith('../'), 'No external imports');
                assert.ok(spec.text.endsWith('.js'), 'Use explicit ESM .js paths');
                assert.ok(target.startsWith(`${root}/candidate/`), 'Import must stay within candidate');
            }
            function visit(node) {
                if (ts.isImportDeclaration(node)) checkImport(node.moduleSpecifier,
                    node.importClause?.isTypeOnly || (node.importClause?.namedBindings &&
                    ts.isNamedImports(node.importClause.namedBindings) && !node.importClause.name &&
                    node.importClause.namedBindings.elements.every(e => e.isTypeOnly)));
                if (ts.isExportDeclaration(node) && node.moduleSpecifier) checkImport(node.moduleSpecifier, node.isTypeOnly);
                assert.ok(!ts.isImportEqualsDeclaration(node), 'Import-equals is not permitted');
                if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) checkImport(node.arguments[0], false);
                ts.forEachChild(node, visit);
            }
            visit(source);
        }
    }
    await review(`${root}/candidate`);
    execFileSync(process.execPath, ['/tools/lib/tsc.js', '-p', root, '--pretty', 'false'], { stdio: 'inherit' });
    const emitted = await readFile(`${root}/built/candidate/implementation.js`, 'utf8');
    assert.ok(!emitted.includes('handoff/generated/contract.js'), 'Declaration runtime import survived');
    console.log(`COMPILE PASS: ${box}; strict named-export assignment and erased declaration import`);
}
