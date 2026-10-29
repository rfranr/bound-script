export type Scalar = string | number | boolean;

export type Condition =
  | { readonly op: 'eq' | 'gte'; readonly fact: string; readonly value: Scalar }
  | { readonly op: 'matched'; readonly ruleId: string }
  | { readonly op: 'all' | 'any'; readonly conditions: readonly Condition[] }
  | { readonly op: 'not'; readonly condition: Condition };

export interface Rule {
  readonly id: string;
  readonly when: Condition;
  readonly then: { readonly key: string; readonly value: Scalar };
}

export interface RuleRequest {
  readonly facts: Readonly<Record<string, Scalar>>;
  readonly rules: readonly Rule[];
}

export type RuleResult =
  | { readonly ok: true;
      readonly results: readonly { readonly id: string; readonly matched: boolean }[];
      readonly actions: readonly { readonly ruleId: string; readonly key: string; readonly value: Scalar }[] }
  | { readonly ok: false;
      readonly error: { readonly code: 'DUPLICATE_RULE' | 'UNKNOWN_RULE' | 'CYCLE'; readonly ruleId: string } };

export type EvaluateRules = (input: RuleRequest) => RuleResult;
