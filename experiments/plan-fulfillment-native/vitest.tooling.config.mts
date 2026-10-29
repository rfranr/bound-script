import { defineConfig } from 'vitest/config';
export default defineConfig({test:{include:['experiments/plan-fulfillment-native/validators.test.ts'],maxWorkers:1,fileParallelism:false,isolate:true}});
