import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

function packageSource(name: string): string {
  return fileURLToPath(new URL(`./packages/${name}/src/index.ts`, import.meta.url));
}

export default defineConfig({
  resolve: {
    alias: [
      { find: /^@boundscript\/compiler\/box-spec$/, replacement: fileURLToPath(new URL('./packages/compiler/src/box-spec-json.ts', import.meta.url)) },
      { find: '@boundscript/artifact', replacement: packageSource('artifact') },
      { find: '@boundscript/cli', replacement: packageSource('cli') },
      { find: '@boundscript/compiler', replacement: packageSource('compiler') },
      { find: '@boundscript/language', replacement: packageSource('language') },
      { find: '@boundscript/runtime', replacement: packageSource('runtime') },
      { find: '@boundscript/sandbox', replacement: packageSource('sandbox') }
    ]
  },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node'
  }
});
