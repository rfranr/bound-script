// All imports and invocations of candidate-shaped code occur inside the container.
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { readFile } from 'node:fs/promises';
import { wire } from './wiring.mjs';
register('data:text/javascript,' + encodeURIComponent(`export async function resolve(s,c,next) {
    if (['@boundscript/compiler','@boundscript/language','langium'].includes(s)) throw Error('Forbidden import '+s);
    const r = await next(s,c);
    if (/\\/(?:language|langium)\\//.test(r.url) || r.url.endsWith('/compiler/dist/index.js')) throw Error('Forbidden module '+r.url);
    return r;
}`), import.meta.url);
const { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec } = await import('@boundscript/compiler/box-spec');
const { verifyBoxImplementation: verify, BoundScriptRuntime } = await import('@boundscript/runtime');
BoundScriptRuntime.prototype.execute = () => { throw Error('Director execution forbidden'); };
for (const forbidden of ['@boundscript/compiler', '@boundscript/language', 'langium'])
    await assert.rejects(import(forbidden), /Forbidden import/);
async function spec(box) {
    const text = await readFile(`/input/${box}/handoff/contract.box-spec.json`, 'utf8');
    const decoded = parseBoxDevelopmentSpec(text);
    assert.ok(decoded.ok, 'setup/strict-decode');
    assert.equal(serializeBoxDevelopmentSpec(decoded.spec), text);
    return decoded.spec;
}
async function implementation(box) {
    const m = await import(`/scratch/${box}/built/consumer.js`);
    assert.equal(typeof m.implement, 'function', 'export/load failure');
    return m.implement;
}
// Snapshot flat record values for assertions, without adding prototype/enumerability
// restrictions to M1 or adapting the live value passed through the wiring.
const recordObservation = value => Object.fromEntries(Reflect.ownKeys(value).map(k => [k, value[k]]));
const mode = process.argv[2];
if (mode === 'controls') {
    const contract = await spec('normalize');
    const sample = JSON.parse(await readFile('/cases/corpus.json', 'utf8'))[0];
    let calls = 0;
    for (const input of [{}, { ...sample.input, trialDays: Infinity }, { ...sample.input, trialDays: NaN },
        { ...sample.input, extra: 1 }, { ...sample.input, [Symbol('extra')]: 1 }]) {
        const r = await verify(contract, () => { calls++; throw Error('must not invoke'); }, input);
        assert.equal(r.failure.kind, 'invalid-input');
    }
    assert.equal(calls, 0);
    assert.equal(parseBoxDevelopmentSpec('{"format":"wrong","version":1}').ok, false);
    for (const [fn, kind] of [
        [() => ({}), 'invalid-output'],
        [() => ({ ...sample.expected, extra: 1 }), 'invalid-output'],
        [() => ({ ...sample.expected, [Symbol('extra')]: 1 }), 'invalid-output'],
        [() => ({ ...sample.expected, trialDays: Infinity }), 'invalid-output'],
        [() => ({ ...sample.expected, reason: '' }), 'postcondition-failure'],
        [() => { throw Error('trusted negative'); }, 'execution-failure'],
        [() => Object.defineProperty({ ...sample.expected }, 'reason', { get() { throw Error('inspection'); } }), 'inspection-failure']
    ]) assert.equal((await verify(contract, fn, sample.input)).failure.kind, kind);
    const wrong = await verify(contract, () => ({ ...sample.expected, displayName: 'WRONG' }), sample.input);
    assert.equal(wrong.ok, true); // M1 conformance is not a functional oracle.
    assert.throws(() => assert.deepEqual(wrong.output, sample.expected));
    const exotic = Object.create({ inherited: 'not an own field' });
    for (const [key, value] of Object.entries(sample.expected)) Object.defineProperty(exotic, key, { value, enumerable: false });
    const liveRecord = await verify(contract, () => exotic, sample.input);
    assert.ok(liveRecord.ok);
    assert.equal(liveRecord.output, exotic);
    assert.deepEqual(recordObservation(liveRecord.output), sample.expected);
    const noExport = await import('data:text/javascript,export const other=1');
    assert.notEqual(typeof noExport.implement, 'function');
    // Preparation-only baseline checks use frozen expected DATA, never a baseline candidate.
    const baseline = await import('/baseline/assertions.mjs');
    baseline.normalized(exotic); // No extra prototype/enumerability restriction in either arm.
    for (const row of JSON.parse(await readFile('/cases/corpus.json', 'utf8'))) {
        baseline.submission(row.input); baseline.normalized(row.expected); assert.notEqual(row.expected.reason, '');
    }
    for (const row of JSON.parse(await readFile('/baseline-cases/render.json', 'utf8'))) {
        baseline.normalized(row.input); baseline.welcome(row.expected);
    }
    for (const row of JSON.parse(await readFile('/baseline-cases/integration.json', 'utf8'))) {
        baseline.submission(row.input); baseline.normalized(row.intermediate); baseline.welcome(row.expected);
    }
    assert.throws(() => baseline.normalized({ ...sample.expected, extra: 1 }));
    assert.throws(() => baseline.normalized({ ...sample.expected, trialDays: Infinity }));
    assert.throws(() => baseline.normalized({ ...sample.expected, [Symbol('extra')]: 1 }));
    console.log('BASELINE PREPARATION PASS: declarations checked bidirectionally; concrete assertions accept frozen expected data and reject extra/symbol/nonfinite fields; no baseline candidate invoked');
    console.log('CONTROLS PASS: strict decode, no invocation on invalid input, malformed/extra/symbol/nonfinite output, predicate, execution/inspection, behavior and missing runtime export');
} else if (mode === 'integration') {
    const nSpec = await spec('normalize'), rSpec = await spec('render');
    assert.deepEqual(nSpec.operation.resultType, rSpec.operation.input.type);
    const normalize = await implementation('normalize'), render = await implementation('render');
    const cases = JSON.parse(await readFile('/cases/corpus.json', 'utf8'));
    for (const row of cases) {
        const input = structuredClone(row.input), before = structuredClone(input);
        const observed = await wire(verify, nSpec, normalize, rSpec, render, input);
        assert.equal(observed.stage, 'render', `${row.id}: integration normalize stage`);
        assert.ok(observed.result.ok, `${row.id}: integration/M1 ${JSON.stringify(observed.result)}`);
        assert.deepEqual(input, before, `${row.id}: input mutation`);
        assert.deepEqual(recordObservation(observed.intermediate), row.intermediate, `${row.id}: intermediate ${row.requirements}`);
        assert.deepEqual(recordObservation(observed.result.output), row.expected, `${row.id}: final ${row.requirements}`);
    }
    // Prove the fixed wiring passes the exact live object, not an adapted copy.
    const row = cases[0]; let live;
    const result = await wire(verify, nSpec, async input => (live = await normalize(input)), rSpec,
        input => { assert.equal(input, live); return render(input); }, structuredClone(row.input));
    assert.ok(result.result.ok);
    console.log(`INTEGRATION PASS: ${cases.length} complete intermediate/final rows; unchanged live value; no director/frontend`);
} else {
    assert.ok(['normalize', 'render'].includes(mode));
    const contract = await spec(mode), implement = await implementation(mode);
    const cases = JSON.parse(await readFile('/cases/corpus.json', 'utf8'));
    for (const row of cases) {
        const input = structuredClone(row.input), before = structuredClone(input);
        const first = await verify(contract, implement, input);
        assert.ok(first.ok, `${row.id}: M1 ${JSON.stringify(first)}`);
        assert.deepEqual(input, before, `${row.id}: input mutation ${row.requirements}`);
        assert.deepEqual(recordObservation(first.output), row.expected, `${row.id}: functional ${row.requirements}`);
        const firstSnapshot = recordObservation(first.output);
        const second = await verify(contract, implement, input);
        assert.ok(second.ok, `${row.id}: repeat M1`);
        assert.deepEqual(input, before, `${row.id}: repeat input mutation`);
        assert.deepEqual(recordObservation(second.output), firstSnapshot, `${row.id}: repeated-call equality`);
    }
    console.log(`INDEPENDENT PASS: ${mode}, ${cases.length} rows, repeated-call equality and no input mutation`);
}
