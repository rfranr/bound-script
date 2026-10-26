// Trusted preparation only: never imports, compiles or invokes a submission.
import assert from 'node:assert/strict';
import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';
import { deriveHandoffs } from '../../.tool-dist/handoff.js';
import { BoundScriptLanguageFrontend } from '@boundscript/language';
import { extractBoxDevelopmentSpec } from '@boundscript/compiler';
import { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';

const root = fileURLToPath(new URL('../../', import.meta.url));
const assets = fileURLToPath(new URL('./', import.meta.url));
const stage = process.argv[2];
assert.ok(stage && path.isAbsolute(stage), 'Pass a fresh absolute staging path');
await mkdir(stage); // No overwrite, reuse or clean-up of an existing directory.
const source = await readFile(path.join(assets, 'system.bound'), 'utf8');
const design = await readFile(path.join(root, 'docs/assignments/0020-design-independent-implementation-pilot.md'), 'utf8');
assert.equal(source, /```boundscript\n([\s\S]*?)\n```/.exec(design)[1] + '\n');
assert.deepEqual(JSON.parse(await readFile(path.join(assets, 'input.json'), 'utf8')),
    JSON.parse(/```json\n([\s\S]*?)\n```/.exec(design)[1]));
const parsed = await new BoundScriptLanguageFrontend().parse({ uri: 'contact-onboarding.bound', text: source });
assert.ok(parsed.program, JSON.stringify(parsed.diagnostics));
assert.equal(parsed.diagnostics.filter(d => d.severity === 'error').length, 0);
const specs = ['NormalizeContact', 'RenderWelcome'].map(box => {
    const extracted = extractBoxDevelopmentSpec(parsed.program, box);
    assert.ok(extracted.ok, JSON.stringify(extracted.diagnostics));
    const bytes = serializeBoxDevelopmentSpec(extracted.spec);
    const decoded = parseBoxDevelopmentSpec(bytes);
    assert.ok(decoded.ok);
    assert.equal(serializeBoxDevelopmentSpec(decoded.spec), bytes);
    return decoded.spec;
});
assert.deepEqual(specs[0].operation.resultType, specs[1].operation.input.type);
for (const name of ['a', 'b']) await deriveHandoffs({ root, binding: 'experiments/contact-onboarding/input.json',
    output: path.join(stage, name), selection: 'all' });
async function files(dir, prefix = '') {
    const result = [];
    for (const e of await readdir(dir, { withFileTypes: true })) {
        const rel = prefix + e.name;
        if (e.isDirectory()) result.push(...await files(path.join(dir, e.name), rel + '/'));
        else { assert.ok(e.isFile(), rel); result.push(rel); }
    }
    return result.sort();
}
const expected = ['README.md', 'contract.box-spec.json', 'generated/contract.d.ts', 'handoff.json',
    'policy.md', 'scope.md', 'seed/implementation.ts', 'task.md'].sort();
for (const box of ['NormalizeContact', 'RenderWelcome']) {
    const a = path.join(stage, 'a/ContactOnboarding', box), b = path.join(stage, 'b/ContactOnboarding', box);
    assert.deepEqual(await files(a), expected); assert.deepEqual(await files(b), expected);
    for (const f of expected) assert.deepEqual(await readFile(path.join(a, f)), await readFile(path.join(b, f)));
    // Delivery copies are real, self-contained directories, not dangling publication links.
    await cp(a, path.join(stage, box, 'handoff'), { recursive: true });
    const spec = parseBoxDevelopmentSpec(await readFile(path.join(a, 'contract.box-spec.json'), 'utf8'));
    assert.ok(spec.ok); assert.deepEqual(spec.spec, specs[box === 'NormalizeContact' ? 0 : 1]);
}
// Static declaration review, not baseline candidate execution or a comparison.
const authority = ts.createSourceFile('interfaces.d.ts', await readFile(path.join(assets, 'baseline/interfaces.d.ts'), 'utf8'), ts.ScriptTarget.ES2022, true);
const records = new Map(specs.flatMap(s => [s.operation.input.type, s.operation.resultType]).map(t => [t.name, t]));
for (const file of ['interfaces.d.ts', 'NormalizeContact/generated/contract.d.ts', 'RenderWelcome/generated/contract.d.ts']) {
    const ast = ts.createSourceFile(file, await readFile(path.join(assets, 'baseline', file), 'utf8'), ts.ScriptTarget.ES2022, true);
    const names = [];
    for (const node of ast.statements.filter(ts.isInterfaceDeclaration)) {
        names.push(node.name.text);
        const expected = records.get(node.name.text); assert.ok(expected);
        const fields = node.members.map(m => {
            assert.ok(ts.isPropertySignature(m) && !m.questionToken && !m.modifiers?.length);
            return { name: m.name.getText(ast), type: m.type.getText(ast) };
        }).sort((a,b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
        assert.deepEqual(fields, expected.fields);
    }
    assert.equal(names.length, file === 'interfaces.d.ts' ? 3 : 2);
}
assert.deepEqual(authority.statements.filter(ts.isFunctionDeclaration).map(n => [n.name.text, n.parameters[0].type.getText(authority), n.type.getText(authority)]), [
    ['normalize', 'ContactSubmission', 'NormalizedContact | Promise<NormalizedContact>'],
    ['render', 'NormalizedContact', 'WelcomeMessage | Promise<WelcomeMessage>']
]);
await cp(path.join(assets, 'baseline'), path.join(stage, 'baseline'), { recursive: true });
// Explicit runtime/codec closure only; no frontend, compiler root, home, repository or credentials.
for (const [pkg, names] of Object.entries({ compiler: ['box-spec-json.js'],
    runtime: ['index.js', 'box-verifier.js', 'contract-checks.js'], artifact: ['index.js'] })) {
    const target = path.join(stage, 'libraries/node_modules/@boundscript', pkg);
    await mkdir(path.join(target, 'dist'), { recursive: true });
    await cp(path.join(root, 'packages', pkg, 'package.json'), path.join(target, 'package.json'));
    for (const name of names) await cp(path.join(root, 'packages', pkg, 'dist', name), path.join(target, 'dist', name));
}
// Freeze the actual validation script inputs in the staging snapshot too.
for (const name of ['evaluate.mjs', 'build.mjs', 'wiring.mjs', 'tsconfig.json', 'consumer.ts', 'package.json'])
    await cp(path.join(assets, 'tests', name), path.join(stage, 'libraries', name));
await writeFile(path.join(stage, 'PREPARATION.txt'), 'Review evidence only. Not operational approval. Two exact eight-file derivations match.\n');
console.log('PASS: exact approved-design source/bindings, whole-source extraction, strict codec round-trip/shared schema, two byte-identical eight-file packages.');
console.log('Staging:', stage);
