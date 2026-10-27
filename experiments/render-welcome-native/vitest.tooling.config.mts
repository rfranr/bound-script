import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['experiments/render-welcome-native/validators.test.ts'],
    maxWorkers: 1,
    fileParallelism: false,
    isolate: true,
  },
});
