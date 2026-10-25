import { readFile } from 'node:fs/promises';

import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementations, type PrintSink } from '@boundscript/runtime';

import { greet } from './greeter.js';
import { createDisplay } from './display.js';

/** Explicitly compose two independent implementations; no discovery or code generation. */
export async function runBoxCompositionDemo(
  output: PrintSink,
  implementations: BoxImplementations = {
    'demo.greeter': greet,
    'demo.display': createDisplay((message) => output.writeLine(message))
  },
  sourcePath = 'examples/box-composition.bound'
): Promise<void> {
  const language = new BoundScriptLanguageFrontend();
  const parsed = await language.parse({ uri: sourcePath, text: await readFile(sourcePath, 'utf8') });
  if (!parsed.program) throw new Error(JSON.stringify(parsed.diagnostics));

  const diagnostics = await language.validate(parsed.program);
  if (diagnostics.some((diagnostic) => diagnostic.severity === 'error')) {
    throw new Error(JSON.stringify(diagnostics));
  }

  const compiled = await new BoundScriptCompiler().compile(parsed.program, {
    Greeter: 'demo.greeter',
    Display: 'demo.display'
  });
  if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));

  await new BoundScriptRuntime(output, implementations).execute(compiled.artifact, {
    entrypoint: 'start'
  });
}
