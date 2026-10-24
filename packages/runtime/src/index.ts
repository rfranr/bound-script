/** Public API version for the execution-runtime boundary. */
export const RUNTIME_API_VERSION = '0.1' as const;

export interface RuntimeArtifact {
  readonly format: string;
  readonly entrypoint: string;
  readonly files: Readonly<Record<string, string>>;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface RuntimeInvocation {
  readonly entrypoint?: string;
  readonly input?: unknown;
}

export interface RuntimeContext {
  readonly signal?: AbortSignal;
  readonly correlationId?: string;
}

export interface RuntimeResult {
  readonly output?: unknown;
  readonly events: readonly RuntimeEvent[];
}

export interface RuntimeEvent {
  readonly type: string;
  readonly source: string;
  readonly payload?: unknown;
  readonly timestamp: string;
}

/** Executes compiled directors and dispatches calls without knowing the source DSL. */
export interface ExecutionRuntime {
  execute(
    artifact: RuntimeArtifact,
    invocation: RuntimeInvocation,
    context?: RuntimeContext
  ): Promise<RuntimeResult>;
}
