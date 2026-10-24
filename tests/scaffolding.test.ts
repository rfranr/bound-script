import { describe, expect, it } from 'vitest';

import { COMPILER_API_VERSION } from '../packages/compiler/src/index.js';
import { LANGUAGE_API_VERSION } from '../packages/language/src/index.js';
import { RUNTIME_API_VERSION } from '../packages/runtime/src/index.js';
import { SANDBOX_API_VERSION } from '../packages/sandbox/src/index.js';

describe('project scaffolding', () => {
  it('exposes each architectural boundary as an independent module', () => {
    expect({
      language: LANGUAGE_API_VERSION,
      compiler: COMPILER_API_VERSION,
      runtime: RUNTIME_API_VERSION,
      sandbox: SANDBOX_API_VERSION
    }).toEqual({
      language: '0.1',
      compiler: '0.1',
      runtime: '0.1',
      sandbox: '0.1'
    });
  });
});
