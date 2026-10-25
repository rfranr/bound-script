import { runBoxCompositionDemo } from './host.js';

try {
  await runBoxCompositionDemo({ writeLine: (value) => process.stdout.write(`${value}\n`) });
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}
