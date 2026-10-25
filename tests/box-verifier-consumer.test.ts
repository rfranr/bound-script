import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';

import { expect, it, vi } from 'vitest';

// Source-level consumption must not execute the compiler root or frontend.
vi.mock('@boundscript/compiler', () => { throw new Error('Do not load compiler root'); });
vi.mock('@boundscript/language', () => { throw new Error('Do not load language frontend'); });
vi.mock('langium', () => { throw new Error('Do not load Langium'); });
import { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec, BoxSpecValidationError } from '@boundscript/compiler/box-spec';
import { BoundScriptRuntime, verifyBoxImplementation } from '@boundscript/runtime';
import { greet } from '../examples/structured-types/greeter.js';
import { loadUser } from '../examples/structured-types/load-user.js';
import { greet as greetString } from '../examples/director-box/greeter.js';

it('consumes published JSON and existing trusted functions without source, compiler or director execution', async () => {
  const director = vi.spyOn(BoundScriptRuntime.prototype, 'execute').mockImplementation(() => { throw new Error('No director'); });
  try {
    const json = await readFile('examples/specs/greeter.box-spec.json', 'utf8');
    const decoded = parseBoxDevelopmentSpec(json);
    if (!decoded.ok) throw new Error(JSON.stringify(decoded.diagnostics));
    expect(serializeBoxDevelopmentSpec(decoded.spec)).toBe(json);
    expect(BoxSpecValidationError).toBeTypeOf('function');
    const user = { id: '123', name: 'World', active: true, score: 7 };
    expect(await verifyBoxImplementation(decoded.spec, greet, user)).toEqual({
      ok: true, output: { message: 'Hello, World!', recipientId: '123' }
    });
    expect(await verifyBoxImplementation(decoded.spec, () => ({ message: '', recipientId: '123' }), user))
      .toMatchObject({ failure: { kind: 'postcondition-failure' } });
    expect(await verifyBoxImplementation(decoded.spec, () => ({ message: '' }), user))
      .toMatchObject({ failure: { kind: 'invalid-output' } });

    // Prepare portable contracts as ordinary data, not by extracting from source or an artifact.
    const portable = (box: string, operation: object) => {
      const parsed = parseBoxDevelopmentSpec(JSON.stringify({ format: 'boundscript/box-development-spec', version: 1,
        system: decoded.spec.system, box, operation }));
      if (!parsed.ok) throw new Error(JSON.stringify(parsed.diagnostics));
      return parsed.spec;
    };
    const load = portable('LoadUser', { name: 'load', input: { name: 'id', type: 'string' }, resultType: decoded.spec.operation.input.type });
    expect(await verifyBoxImplementation(load, loadUser, '123')).toEqual({ ok: true, output: user });
    const simple = portable('SimpleGreeter', { name: 'greet', input: { name: 'name', type: 'string' }, resultType: 'string' });
    expect(await verifyBoxImplementation(simple, greetString, 'World')).toEqual({ ok: true, output: 'Hello, World!' });
    const display = portable('Display', { name: 'show', input: { name: 'greeting', type: decoded.spec.operation.resultType }, resultType: 'void' });
    const show = vi.fn(() => undefined);
    const greeting = { message: 'Hello, World!', recipientId: '123' };
    expect(await verifyBoxImplementation(display, show, greeting)).toEqual({ ok: true, output: undefined });
    expect(show).toHaveBeenCalledExactlyOnceWith(greeting);
    expect(director).not.toHaveBeenCalled();
  } finally {
    director.mockRestore();
  }
});

it('uses built public exports without loading compiler root, frontend or Langium in Node', () => {
  // Build explicitly so this smoke check works with `npm test` from a clean checkout too.
  execFileSync('npm', ['run', 'build', '--silent'], { stdio: 'pipe' });
  const loader = `
    export async function resolve(specifier, context, nextResolve) {
      if (specifier === '@boundscript/compiler' || specifier === '@boundscript/language' ||
          specifier === 'langium' || specifier.startsWith('langium/')) throw new Error('Forbidden import: ' + specifier);
      const resolved = await nextResolve(specifier, context);
      if (/\\/(?:language|langium)\\//.test(resolved.url) || resolved.url.endsWith('/compiler/dist/index.js')) {
        throw new Error('Forbidden module: ' + resolved.url);
      }
      return resolved;
    }
  `;
  const code = `
    import { register } from 'node:module';
    import { readFile } from 'node:fs/promises';
    import assert from 'node:assert/strict';
    register('data:text/javascript,' + encodeURIComponent(${JSON.stringify(loader)}), import.meta.url);
    const { parseBoxDevelopmentSpec, serializeBoxDevelopmentSpec, BoxSpecValidationError } = await import('@boundscript/compiler/box-spec');
    const { verifyBoxImplementation, BoundScriptRuntime } = await import('@boundscript/runtime');
    BoundScriptRuntime.prototype.execute = () => { throw new Error('No director execution'); };
    const { greet } = await import('./examples/structured-types/dist/greeter.js');
    const json = await readFile('examples/specs/greeter.box-spec.json', 'utf8');
    const parsed = parseBoxDevelopmentSpec(json);
    assert.equal(parsed.ok, true);
    assert.equal(serializeBoxDevelopmentSpec(parsed.spec), json);
    assert.equal(typeof BoxSpecValidationError, 'function');
    const result = await verifyBoxImplementation(parsed.spec, greet, { id: '123', name: 'World', active: true, score: 7 });
    assert.deepEqual(result, { ok: true, output: { message: 'Hello, World!', recipientId: '123' } });
    console.log('public codec and verifier import smoke passed');
  `;
  expect(execFileSync(process.execPath, ['--input-type=module', '--eval', code], { encoding: 'utf8' }).trim())
    .toBe('public codec and verifier import smoke passed');
}, 30_000);
