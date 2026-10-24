import {
  EXECUTABLE_ARTIFACT_FORMAT,
  EXECUTABLE_ARTIFACT_VERSION,
  type ExecutableArtifact
} from '@boundscript/artifact';
import type { CompilationResult } from '@boundscript/compiler';
import type { ExecutionRuntime } from '@boundscript/runtime';

const artifact = {
  format: EXECUTABLE_ARTIFACT_FORMAT,
  version: EXECUTABLE_ARTIFACT_VERSION,
  system: 'HelloWorld',
  entrypoints: [{ name: 'main', target: 'directors/main' }],
  assets: [
    {
      path: 'directors/main',
      mediaType: 'application/vnd.boundscript.director',
      bytes: new Uint8Array()
    }
  ]
} satisfies ExecutableArtifact;

const successfulCompilation = {
  ok: true,
  artifact,
  diagnostics: []
} satisfies CompilationResult;

const failedCompilation = {
  ok: false,
  diagnostics: [
    {
      code: 'compiler.invalid-input',
      message: 'The compilation input is invalid.',
      severity: 'error'
    }
  ]
} satisfies CompilationResult;

function executeCompiledArtifact(runtime: ExecutionRuntime): Promise<unknown> {
  return runtime.execute(successfulCompilation.artifact, {
    entrypoint: 'main'
  });
}

void failedCompilation;
void executeCompiledArtifact;
