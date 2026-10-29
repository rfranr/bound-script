import typia from 'typia';
import type { RuleRequest, RuleResult } from './contract';
export const isRuleRequest = typia.createEquals<RuleRequest>();
export const assertRuleRequest = typia.createAssertEquals<RuleRequest>();
export const isRuleResult = typia.createEquals<RuleResult>();
export const assertRuleResult = typia.createAssertEquals<RuleResult>();
