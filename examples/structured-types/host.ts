import { readFile } from 'node:fs/promises';

import { BoundScriptCompiler } from '@boundscript/compiler';
import { BoundScriptLanguageFrontend } from '@boundscript/language';
import { BoundScriptRuntime, type BoxImplementations, type PrintSink } from '@boundscript/runtime';

import { loadUser } from './load-user.js';
import { greet } from './greeter.js';
import { createDisplay } from './display.js';

export async function runStructuredTypesDemo(
  output: PrintSink,
  implementations: BoxImplementations = {
    'structured.load-user': loadUser,
    'structured.greeter': greet,
    'structured.display': createDisplay((message) => output.writeLine(message))
  },
  sourcePath = 'examples/structured-types.bound'
): Promise<void> {
  const language = new BoundScriptLanguageFrontend();
  const parsed = await language.parse({ uri: sourcePath, text: await readFile(sourcePath, 'utf8') });
  if (!parsed.program) throw new Error(JSON.stringify(parsed.diagnostics));
  const diagnostics = await language.validate(parsed.program);
  if (diagnostics.some((diagnostic) => diagnostic.severity === 'error')) {
    throw new Error(JSON.stringify(diagnostics));
  }

  const compiled = await new BoundScriptCompiler().compile(parsed.program, {
    LoadUser: 'structured.load-user', Greeter: 'structured.greeter', Display: 'structured.display'
  });
  if (!compiled.ok) throw new Error(JSON.stringify(compiled.diagnostics));
  await new BoundScriptRuntime(output, implementations).execute(compiled.artifact, { entrypoint: 'start' });
}
