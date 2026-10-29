# EvaluateRules

Implement the public `EvaluateRules` TypeScript function exported as `evaluateRules` from `/implementation/implementation.ts` according to the consumer-owned contract. The input is structurally valid according to `RuleRequest`; the output is always a `RuleResult`. Pure, synchronous, no external packages, filesystem, network or environment access. Do not mutate or retain input. Repeated calls are independent.

## Conditions

- `eq`: true only when the fact exists and its scalar value equals `value` with strict TypeScript equality (no coercion). An absent fact is false. Scalar facts can be strings, finite numbers or booleans.
- `gte`: true only when the fact exists and both fact and `value` are numbers, and fact >= value; otherwise false. All numeric input is finite.
- `matched`: true if the referenced rule's condition evaluated true, false otherwise. References may point forward or backward; their value is **the condition match**, independent of any emitted action.
- `all`: true if every child matches (including empty list); `any`: true if any child matches (empty list is false); `not`: negation of child. Nested conditions can be arbitrarily composed within input size limits.

## Rules, ordering, and output

- A rule is uniquely identified by its exact, case-sensitive `id`. Reject duplicate IDs before evaluating any conditions.
- A `matched` reference to a non-existent rule is an error, even inside a branch whose truth value would otherwise short-circuit. Check all references across the full rule set first.
- Cycles in rule references, including self-dependencies, are errors even when hidden in a short-circuited branch. Detect them over the entire rule graph.
- Errors take precedence in this order: duplicate IDs, unknown references, cycles. When multiple of the same kind exist, report the offending rule with the smallest **input index**. For duplicates, choose the second occurrence's ID; for unknown references, choose the first input rule containing an unknown reference; for cycles, choose the earliest input rule *participating* in any cycle (not a rule which merely points into one). Return `{ok:false,error:{code,ruleId}}`, no partial results.
- On success, `results` contains one `{id,matched}` per rule, in the **original input order** even when dependency evaluation order differs. `actions` contains `{ruleId,key,value}` for each matched rule, likewise in original input order; unmatched rules emit nothing. Preserve the exact declared key and scalar value, including case and whitespace.
- Empty rule list returns `{ok:true,results:[],actions:[]}`. No implicit aggregation, priority, conflict resolution, arbitrary code execution or mutation.

## Boundary

The agent sees only this task and the public contract. It may organize supported implementation TypeScript sources freely under `/implementation`; no implementation file count or structure is mandated by the consumer. Do not inspect tests, fixtures, peer code or credentials.
