import { readFile } from 'node:fs/promises';

import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementations, type PrintSink } from '@boundscript/runtime';

import { greet } from './greeter.js';

/** Run from the repository root, using the same host path in the demo and tests. */
export async function runDirectorBoxDemo(
  output: PrintSink,
  implementations: BoxImplementations = { 'demo.greeter': greet },
  sourcePath = 'examples/director-box.bound'
): Promise<void> {
  const language = new BoundScriptLanguageFrontend();
  const parsed = await language.parse({ uri: sourcePath, text: await readFile(sourcePath, 'utf8') });
  if (!parsed.program) throw new Error(JSON.stringify(parsed.diagnostics));

  const diagnostics = await language.validate(parsed.program);
  if (diagnostics.some((diagnostic) => diagnostic.severity === 'error')) {
    throw new Error(JSON.stringify(diagnostics));
  }

  const compiled = await new BoundScriptCompiler().compile(parsed.program, {
    Greeter: 'demo.greeter'
  });
  if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));

  await new BoundScriptRuntime(output, implementations).execute(compiled.artifact, {
    entrypoint: 'start'
  });
}
