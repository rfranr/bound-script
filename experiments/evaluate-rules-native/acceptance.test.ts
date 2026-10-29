import { expect, it } from 'vitest';
import fc from 'fast-check';
import { evaluateRules } from '/implementation/implementation.ts';
import { assertRuleRequest, assertRuleResult } from './.generated/validators';
import cases from './fixtures/rule-cases.json';
import type { RuleRequest } from './src/contract';

function deepFreeze(value: unknown): void {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(deepFreeze);
    Object.freeze(value);
  }
}
function evaluate(input: RuleRequest) {
  assertRuleRequest(input);
  deepFreeze(input);
  return assertRuleResult(evaluateRules(input));
}
it.each(cases)('matches independent rule fixture %#', ({ input, expected }) => {
  expect(evaluate(input)).toEqual(expected);
});
it('is deterministic and preserves original input order on independent scalar predicates', () => {
  fc.assert(fc.property(fc.array(fc.integer({ min: -100, max: 100 }), { maxLength: 20 }), values => {
    const input: RuleRequest = { facts: { threshold: 0 }, rules: values.map((n, i) => ({
      id: `r${i}`, when: {op:'gte',fact:'threshold',value:n}, then: {key:`k${i}`,value:n},
    })) };
    const expected = values.map(n => n <= 0);
    const output = evaluate(input);
    expect(output.ok).toBe(true);
    if (!output.ok) return;
    expect(output.results.map(r => r.matched)).toEqual(expected);
    expect(output.actions.map(a => a.ruleId)).toEqual(values.flatMap((_, i) => expected[i] ? [`r${i}`] : []));
    expect(evaluate(input)).toEqual(output);
  }), {seed: 50, numRuns: 40});
});
