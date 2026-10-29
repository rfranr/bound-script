import { defineConfig } from 'vitest/config';

// Only used by the independent offline verifier, never by the generating agent.
export default defineConfig({
  root: '/checks',
  cacheDir: '/implementation/.vite',
  test: {
    // The verifier's generated per-suite config supplies exact declared files.
    include: [],
    pool: 'threads',
    maxWorkers: 1,
    fileParallelism: false,
    isolate: true,
    testTimeout: 15000,
  },
});
