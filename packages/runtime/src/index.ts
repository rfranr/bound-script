import type { ExecutableArtifact } from '@boundscript/artifact';

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

/** Executes an artifact without depending on source-language or compiler internals. */
export interface ExecutionRuntime {
  execute(
    artifact: ExecutableArtifact,
    request: ExecutionRequest
  ): Promise<ExecutionResult>;
}
