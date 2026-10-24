import {
  DIRECTOR_PROGRAM_MEDIA_TYPE,
  DIRECTOR_PROGRAM_VERSION,
  EXECUTABLE_ARTIFACT_FORMAT,
  EXECUTABLE_ARTIFACT_VERSION,
  type DirectorProgram,
  type ExecutableArtifact
} from '@boundscript/artifact';

/** Public API version for the execution-runtime boundary. */
export const RUNTIME_API_VERSION = '0.1' as const;

export interface ExecutionRequest {
  /** Must match an entrypoint declared by the artifact. */
  readonly entrypoint: string;
  readonly input?: unknown;
  readonly signal?: AbortSignal;
}

export interface ExecutionResult {
  readonly output?: unknown;
}

export interface PrintSink {
  writeLine(value: string): void;
}

export class RuntimeExecutionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RuntimeExecutionError';
  }
}

/** Executes an artifact without depending on source-language or compiler internals. */
export interface ExecutionRuntime {
  execute(
    artifact: ExecutableArtifact,
    request: ExecutionRequest
  ): Promise<ExecutionResult>;
}

/** Runtime for the first instruction format. `print` is a temporary built-in operation. */
export class BoundScriptRuntime implements ExecutionRuntime {
  constructor(private readonly output: PrintSink) {}

  async execute(
    artifact: ExecutableArtifact,
    request: ExecutionRequest
  ): Promise<ExecutionResult> {
    this.assertSupportedArtifact(artifact);
    if (request.signal?.aborted) throw new RuntimeExecutionError('Execution was aborted.');

    const entrypoint = artifact.entrypoints.find((candidate) => candidate.name === request.entrypoint);
    if (!entrypoint) {
      throw new RuntimeExecutionError(`Unknown entrypoint "${request.entrypoint}".`);
    }

    const asset = artifact.assets.find((candidate) => candidate.path === entrypoint.target);
    if (!asset) {
      throw new RuntimeExecutionError(`Entrypoint target "${entrypoint.target}" is missing.`);
    }
    if (asset.mediaType !== DIRECTOR_PROGRAM_MEDIA_TYPE) {
      throw new RuntimeExecutionError(`Unsupported asset media type "${asset.mediaType}".`);
    }

    const program = decodeDirectorProgram(asset.bytes);
    for (const instruction of program.instructions) {
      if (request.signal?.aborted) throw new RuntimeExecutionError('Execution was aborted.');
      this.output.writeLine(instruction.value);
    }

    return {};
  }

  private assertSupportedArtifact(artifact: ExecutableArtifact): void {
    if (artifact.format !== EXECUTABLE_ARTIFACT_FORMAT) {
      throw new RuntimeExecutionError(`Unsupported artifact format "${artifact.format}".`);
    }
    if (artifact.version !== EXECUTABLE_ARTIFACT_VERSION) {
      throw new RuntimeExecutionError(`Unsupported artifact version "${artifact.version}".`);
    }
  }
}

function decodeDirectorProgram(bytes: Uint8Array): DirectorProgram {
  let value: unknown;
  try {
    value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
  } catch {
    throw new RuntimeExecutionError('Director program is not valid UTF-8 JSON.');
  }

  if (!isDirectorProgram(value)) {
    throw new RuntimeExecutionError('Director program has an unsupported structure.');
  }
  return value;
}

function isDirectorProgram(value: unknown): value is DirectorProgram {
  if (!isRecord(value) || value.version !== DIRECTOR_PROGRAM_VERSION || !Array.isArray(value.instructions)) {
    return false;
  }

  return value.instructions.every(
    (instruction) =>
      isRecord(instruction) &&
      instruction.operation === 'print' &&
      typeof instruction.value === 'string'
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}
