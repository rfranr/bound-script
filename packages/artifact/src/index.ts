/** Public API version for the compiler/runtime artifact boundary. */
export const ARTIFACT_API_VERSION = '0.1' as const;

/** Identifies the artifact envelope independently from its implementation target. */
export const EXECUTABLE_ARTIFACT_FORMAT = 'boundscript/executable' as const;

/** Version of the artifact envelope. Runtime implementations must reject unsupported versions. */
export const EXECUTABLE_ARTIFACT_VERSION = 1 as const;

/** Media type for the first executable director instruction format. */
export const DIRECTOR_PROGRAM_MEDIA_TYPE =
  'application/vnd.boundscript.director-program+json' as const;

export const DIRECTOR_PROGRAM_VERSION = 1 as const;

export interface PrintInstruction {
  readonly operation: 'print';
  readonly value: string;
}

export interface PrintVariableInstruction {
  readonly operation: 'print-variable';
  readonly variable: string;
}

export interface InvokeInstruction {
  readonly operation: 'invoke';
  readonly implementation: string;
  readonly argument: string;
  readonly result: string;
}

export type DirectorInstruction = PrintInstruction | PrintVariableInstruction | InvokeInstruction;

export interface DirectorProgram {
  readonly version: typeof DIRECTOR_PROGRAM_VERSION;
  readonly instructions: readonly DirectorInstruction[];
}

export interface ArtifactEntrypoint {
  /** Public name used by an execution request. */
  readonly name: string;

  /** Runtime-defined logical target contained in this artifact. */
  readonly target: string;
}

export interface ArtifactAsset {
  /** Unique, relative, POSIX-style path within the artifact. */
  readonly path: string;

  /** Media type describing the asset contents. */
  readonly mediaType: string;

  /** Exact bytes emitted by the compiler. Consumers must treat them as immutable. */
  readonly bytes: Uint8Array;
}

/**
 * The complete, immutable hand-off from deterministic compilation to execution.
 * It contains runtime inputs only; build-time agents and their internal state are excluded.
 */
export interface ExecutableArtifact {
  readonly format: typeof EXECUTABLE_ARTIFACT_FORMAT;
  readonly version: typeof EXECUTABLE_ARTIFACT_VERSION;
  readonly system: string;
  readonly entrypoints: readonly ArtifactEntrypoint[];
  readonly assets: readonly ArtifactAsset[];
}
