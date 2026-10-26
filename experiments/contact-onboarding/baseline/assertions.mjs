// Conventional arm concrete assertions, prepared only. No BoundScript imports.
import assert from 'node:assert/strict';
// Compare flat field observations, not hidden prototype/enumerability restrictions.
const observation = value => Object.fromEntries(Reflect.ownKeys(value).map(k => [k, value[k]]));
export function submission(x) {
    assert.ok(x !== null && typeof x === 'object' && !Array.isArray(x));
    assert.deepEqual(Reflect.ownKeys(x).sort(), ['consent', 'email', 'locale', 'name', 'requestId', 'trialDays']);
    for (const k of ['email', 'locale', 'name', 'requestId']) assert.equal(typeof x[k], 'string');
    assert.equal(typeof x.consent, 'boolean');
    assert.ok(typeof x.trialDays === 'number' && Number.isFinite(x.trialDays));
}
export function normalized(x) {
    assert.ok(x !== null && typeof x === 'object' && !Array.isArray(x));
    assert.deepEqual(Reflect.ownKeys(x).sort(), ['consent', 'displayName', 'email', 'locale', 'reason', 'requestId', 'trialDays', 'valid']);
    for (const k of ['displayName', 'email', 'locale', 'reason', 'requestId']) assert.equal(typeof x[k], 'string');
    assert.equal(typeof x.consent, 'boolean'); assert.equal(typeof x.valid, 'boolean');
    assert.ok(typeof x.trialDays === 'number' && Number.isFinite(x.trialDays));
}
export function welcome(x) {
    assert.ok(x !== null && typeof x === 'object' && !Array.isArray(x));
    assert.deepEqual(Reflect.ownKeys(x).sort(), ['html', 'reason', 'recipient', 'requestId', 'send', 'subject']);
    for (const k of ['html', 'reason', 'recipient', 'requestId', 'subject']) assert.equal(typeof x[k], 'string');
    assert.equal(typeof x.send, 'boolean'); assert.notEqual(x.subject, '');
}
export async function checkNormalize(implement, cases) {
    for (const row of cases) {
        const input = structuredClone(row.input), before = structuredClone(input);
        submission(input);
        const first = await implement(input); normalized(first); assert.notEqual(first.reason, '');
        assert.deepEqual(observation(first), row.expected, row.id); assert.deepEqual(input, before, row.id);
        const snapshot = observation(first), second = await implement(input);
        normalized(second); assert.notEqual(second.reason, '');
        assert.deepEqual(observation(second), snapshot, row.id); assert.deepEqual(input, before, row.id);
    }
}
export async function checkRender(implement, cases) {
    for (const row of cases) {
        const input = structuredClone(row.input), before = structuredClone(input);
        normalized(input); // Input has no nonempty-reason predicate.
        const first = await implement(input); welcome(first);
        assert.deepEqual(observation(first), row.expected, row.id); assert.deepEqual(input, before, row.id);
        const snapshot = observation(first), second = await implement(input);
        welcome(second); assert.deepEqual(observation(second), snapshot, row.id); assert.deepEqual(input, before, row.id);
    }
}
export async function checkIntegration(normalize, render, cases) {
    for (const row of cases) {
        const input = structuredClone(row.input), before = structuredClone(input);
        submission(input);
        const intermediate = await normalize(input);
        normalized(intermediate); assert.notEqual(intermediate.reason, '');
        const result = await render(intermediate); // Exact live output, not an adapted copy.
        welcome(result); assert.deepEqual(input, before, row.id);
        assert.deepEqual(observation(intermediate), row.intermediate, row.id);
        assert.deepEqual(observation(result), row.expected, row.id);
    }
}
