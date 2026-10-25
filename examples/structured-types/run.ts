import { runStructuredTypesDemo } from './host.js';

try {
  await runStructuredTypesDemo({ writeLine: (value) => process.stdout.write(`${value}\n`) });
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}
