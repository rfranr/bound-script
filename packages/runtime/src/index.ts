import {
  DIRECTOR_PROGRAM_MEDIA_TYPE,
  DIRECTOR_PROGRAM_VERSION,
  EXECUTABLE_ARTIFACT_FORMAT,
  EXECUTABLE_ARTIFACT_VERSION,
  type DirectorProgram,
  type ExecutableArtifact,
  type InvocationArgument
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

/** Host-provided code is trusted: this registry is not a sandbox. */
export type BoxImplementation = (input: string) => string | void | Promise<string | void>;
export type BoxImplementations = Readonly<Record<string, BoxImplementation>>;

/** Runtime for the supported director instruction format. `print` is a temporary built-in operation. */
export class BoundScriptRuntime implements ExecutionRuntime {
  constructor(
    private readonly output: PrintSink,
    private readonly implementations: BoxImplementations = {}
  ) {}

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
    // Resolve every dependency before executing any instructions or producing output.
    const implementations = new Map<string, BoxImplementation>();
    for (const instruction of program.instructions) {
      if (instruction.operation !== 'invoke') continue;
      const implementation = Object.hasOwn(this.implementations, instruction.implementation)
        ? this.implementations[instruction.implementation]
        : undefined;
      if (typeof implementation !== 'function') {
        throw new RuntimeExecutionError(`Missing implementation "${instruction.implementation}".`);
      }
      implementations.set(instruction.implementation, implementation);
    }

    const variables = new Map<string, string>();
    for (const instruction of program.instructions) {
      if (request.signal?.aborted) throw new RuntimeExecutionError('Execution was aborted.');
      if (instruction.operation === 'invoke') {
        const argument = resolveArgument(instruction.argument, variables);
        let result: unknown;
        try {
          result = await implementations.get(instruction.implementation)!(argument);
        } catch (error) {
          const message = error instanceof Error ? error.message : String(error);
          throw new RuntimeExecutionError(`Implementation "${instruction.implementation}" failed: ${message}`);
        }
        if (instruction.resultType === 'string') {
          if (typeof result !== 'string') {
            throw new RuntimeExecutionError(`Implementation "${instruction.implementation}" must return a string.`);
          }
          variables.set(instruction.result, result);
        } else if (result !== undefined) {
          throw new RuntimeExecutionError(`Implementation "${instruction.implementation}" must return undefined for a void operation.`);
        }
      } else if (instruction.operation === 'print-variable') {
        const value = variables.get(instruction.variable);
        if (value === undefined) {
          throw new RuntimeExecutionError(`Unknown variable "${instruction.variable}".`);
        }
        this.output.writeLine(value);
      } else {
        this.output.writeLine(instruction.value);
      }
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

  return value.instructions.every((instruction) => {
    if (!isRecord(instruction)) return false;
    switch (instruction.operation) {
      case 'print':
        return typeof instruction.value === 'string';
      case 'print-variable':
        return typeof instruction.variable === 'string';
      case 'invoke':
        return typeof instruction.implementation === 'string' &&
          instruction.implementation.length > 0 &&
          isInvocationArgument(instruction.argument) &&
          ((instruction.resultType === 'string' && typeof instruction.result === 'string') ||
            (instruction.resultType === 'void' && !Object.hasOwn(instruction, 'result')));
      default:
        return false;
    }
  });
}

function resolveArgument(argument: InvocationArgument, variables: ReadonlyMap<string, string>): string {
  if (argument.kind === 'literal') return argument.value;
  const value = variables.get(argument.name);
  if (value === undefined) throw new RuntimeExecutionError(`Unknown variable "${argument.name}".`);
  return value;
}

function isInvocationArgument(value: unknown): boolean {
  return isRecord(value) &&
    ((value.kind === 'literal' && typeof value.value === 'string') ||
      (value.kind === 'variable' && typeof value.name === 'string'));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}
