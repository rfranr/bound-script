import { defineConfig } from 'vitest/config';

// Only used by the independent offline verifier, never by the generating agent.
export default defineConfig({
  root: '/checks',
  cacheDir: '/implementation/.vite',
  test: {
    include: ['acceptance.test.ts', 'validators.test.ts'],
    pool: 'forks',
    maxWorkers: 1,
    fileParallelism: false,
    isolate: true,
    testTimeout: 15000,
  },
});
