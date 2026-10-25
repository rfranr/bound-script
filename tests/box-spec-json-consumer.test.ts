import { readFile } from 'node:fs/promises';

import { expect, it, vi } from 'vitest';

// The pure codec module has type-only dependencies, so consuming JSON needs no language services.
vi.mock('@boundscript/language', () => { throw new Error('JSON consumption must not load the language frontend.'); });
import { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec } from '../packages/compiler/src/box-spec-json.js';

it('consumes the published JSON without BoundScript source, Langium or compiler execution', async () => {
  const json = await readFile('examples/specs/greeter.box-spec.json', 'utf8');
  const result = parseBoxDevelopmentSpec(json);
  expect(result.ok).toBe(true);
  if (!result.ok) throw new Error(JSON.stringify(result.diagnostics));
  expect(result.spec.box).toBe('Greeter');
  expect(result.spec.operation.input.name).toBe('user');
  expect(result.spec.operation.resultType).toEqual({ kind: 'record', name: 'Greeting', fields: [
    { name: 'message', type: 'string' }, { name: 'recipientId', type: 'string' }
  ] });
  expect(result.spec.operation.postcondition).toEqual({
    kind: 'string-not-equal', target: { kind: 'field', name: 'message' }, value: ''
  });
  expect(serializeBoxDevelopmentSpec(result.spec)).toBe(json);
});
