import { expect, it } from 'vitest';
import { isRuleRequest, assertRuleRequest, isRuleResult } from './.generated/validators';

it('validates public request/result shapes', () => {
  const valid = { facts: { age: 25, active: true }, rules: [
    { id: 'adult', when: { op: 'gte', fact: 'age', value: 18 }, then: { key: 'allowed', value: true } },
  ] };
  expect(isRuleRequest(valid)).toBe(true);
  expect(assertRuleRequest(valid)).toEqual(valid);
  expect(isRuleRequest({ ...valid, rules: [ { ...valid.rules[0], when: { op: 'execute', script: 'x' } } ] })).toBe(false);
  expect(isRuleRequest({ ...valid, facts: {age: null} })).toBe(false);
  expect(isRuleResult({ok:false,error:{code:'CYCLE',ruleId:'a'}})).toBe(true);
  expect(isRuleResult({ok:true,results:[],actions:[]})).toBe(true);
  expect(isRuleResult({ok:true,results:[],actions:[{ruleId:'x',key:'y',value:null}]})).toBe(false);
});
