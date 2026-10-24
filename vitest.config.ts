import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

function packageSource(name: string): string {
  return fileURLToPath(new URL(`./packages/${name}/src/index.ts`, import.meta.url));
}

export default defineConfig({
  resolve: {
    alias: {
      '@boundscript/artifact': packageSource('artifact'),
      '@boundscript/cli': packageSource('cli'),
      '@boundscript/compiler': packageSource('compiler'),
      '@boundscript/language': packageSource('language'),
      '@boundscript/runtime': packageSource('runtime'),
      '@boundscript/sandbox': packageSource('sandbox')
    }
  },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node'
  }
});
