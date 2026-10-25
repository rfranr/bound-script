import { deriveHandoffs } from './handoff.js';

const [root, binding, output, system, box, ...extra] = process.argv.slice(2);
if (!root || !binding || !output || !system || extra.length || (system === '--all' ? box !== undefined : !box)) {
  console.error('Usage: npm run handoff -- <repository-root> <binding-relative-path> <fresh-output> <--all | system box>');
  process.exitCode = 1;
} else {
  try {
    await deriveHandoffs({ root, binding, output, selection: system === '--all' ? 'all' : { system, box: box! } });
    console.log('Structural derivation succeeded; human approval was not verified.');
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
