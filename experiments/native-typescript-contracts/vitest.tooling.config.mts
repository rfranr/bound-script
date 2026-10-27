import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['experiments/native-typescript-contracts/validators.test.ts'],
    maxWorkers: 1,
    fileParallelism: false,
    isolate: true,
  },
});
