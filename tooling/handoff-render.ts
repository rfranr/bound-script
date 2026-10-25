import type { ValueType } from '@boundscript/artifact';
import type { BoxDevelopmentSpec } from '@boundscript/compiler';
import { serializeBoxDevelopmentSpec } from '@boundscript/compiler/box-spec';

/** Rendering behavior changes require an explicit rules-version decision. */
export const DERIVATION_VERSION = 1;
export interface InputPaths { architecture: string; task: string; scope: string; policy: string }
export const SEED = `import type { Implementation } from '../handoff/generated/contract.js';

export const implement: Implementation = (input) => {
  throw new Error('Not implemented');
};
`;
export function instructions(spec: BoxDevelopmentSpec): string {
  return `# Box implementation handoff

System: ${spec.system}; Box: ${spec.box}; operation: ${spec.operation.name}.
The identity and selected input paths are in [handoff.json](handoff.json).
The sole public contract is [contract.box-spec.json](contract.box-spec.json).
[Generated declarations](generated/contract.d.ts) are a read-only structural projection.
Read [task](task.md), [scope](scope.md), and [policy](policy.md) before implementation.
Task instructions are not formal contract semantics.

Successful derivation checks structure, NOT human approval. An authorized human must
approve the exact architecture, task, scope, and policy versions and their consistency
before operational use. Missing intent, conflicts, or context require human clarification;
do not invent requirements, redefine interfaces, or expand context automatically.

The external controller supplies read-only handoff/ beside writable candidate/.
Copy seed/implementation.ts to candidate/implementation.ts; export named implement.
Work only in candidate/**, further narrowed by scope. Private helpers/tests are permitted
only there and only under policy. Do not edit contracts, shared types, requirements,
trusted tests, wiring, dependency manifests/lockfiles, or policy. New dependencies,
interfaces, or responsibilities require human approval.

The external environment supplies ESM (type: module) and strict NodeNext TypeScript.
The seed's type-only .js import resolves to the .d.ts and disappears from emitted JS;
no runtime contract.js exists. Submit candidate/implementation.ts and permitted private
files for external trusted compilation, named-export checking, and verification.
Void operations must explicitly return undefined under this authoring convention;
the runtime still accepts implicit undefined. Static typing proves neither exact own
keys (symbol extras can type-check, including empty records), nominal origin, finite
numbers, nor predicates. The canonical contract and runtime verifier remain authoritative.

Do not modify packages: discard and rederive into fresh output after input changes.
Any architecture edit requires all still-selected Boxes from that source to be
regenerated with whole-system validation, even if resulting bytes are identical.
Task/scope edits affect referencing Boxes; shared policy affects all references.
Rules/environment changes require full comparison and regression checks; intentional
rendering changes require a rules-version decision. Retire removed/renamed selections
without silently migrating candidates. Candidate/private-test/trusted-test-only changes
require affected verification, not handoff regeneration. Approval changes may alter
authorization without changing bytes. There is no automated currentness or promotion gate.

These directories and Node subprocesses are NOT security boundaries. This adapter
loads/executes no candidates and provides no sandbox, dependency enforcement, or evidence
tracking. Untrusted execution requires M3 isolation; evidence enforcement belongs to M4.
`;
}

export function declarations(spec: BoxDevelopmentSpec): string {
  const records = new Map<string, Exclude<ValueType, string>>();
  const type = (value: ValueType | 'void'): string => {
    if (typeof value === 'string') return value === 'void' ? 'undefined' : value;
    records.set(value.name, value);
    return `Record_${value.name}`;
  };
  const input = type(spec.operation.input.type);
  const result = type(spec.operation.resultType);
  const aliases = [...records.keys()].sort().map((name) => {
    const fields = [...records.get(name)!.fields].sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
    return `export type Record_${name} = ${fields.length ? `{\n${fields.map((f) => `  ${JSON.stringify(f.name)}: ${f.type};`).join('\n')}\n}` : 'Record<string, never>'};\n`;
  });
  return `${aliases.length ? aliases.join('\n') + '\n' : ''}export type Input = ${input};\nexport type Result = ${result};\nexport type Implementation = (input: Input) => Result | Promise<Result>;\n`;
}

/** Pure rendering; snapshots are opaque bytes, not semantic requirements. */
export function renderPackage(spec: BoxDevelopmentSpec, paths: InputPaths,
  snapshots: { task: Uint8Array; scope: Uint8Array; policy: Uint8Array }): Record<string, Uint8Array> {
  const text = (s: string) => new TextEncoder().encode(s);
  // Strict serializer is also the supported-contract validation boundary.
  const contract = serializeBoxDevelopmentSpec(spec);
  return {
    'handoff.json': text(JSON.stringify({ format: 'boundscript/box-handoff', version: 1,
      derivationVersion: DERIVATION_VERSION, system: spec.system, box: spec.box, operation: spec.operation.name,
      inputs: { architecture: paths.architecture, task: paths.task, scope: paths.scope, policy: paths.policy },
      entrypoint: { source: 'candidate/implementation.ts', export: 'implement' } }, null, 2) + '\n'),
    'README.md': text(instructions(spec)),
    'contract.box-spec.json': text(contract),
    'task.md': snapshots.task,
    'scope.md': snapshots.scope,
    'policy.md': snapshots.policy,
    'generated/contract.d.ts': text(declarations(spec)),
    'seed/implementation.ts': text(SEED)
  };
}
