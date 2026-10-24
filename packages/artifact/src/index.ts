/** Public API version for the compiler/runtime artifact boundary. */
export const ARTIFACT_API_VERSION = '0.1' as const;

/** Identifies the artifact envelope independently from its implementation target. */
export const EXECUTABLE_ARTIFACT_FORMAT = 'boundscript/executable' as const;

/** Version of the artifact envelope. Runtime implementations must reject unsupported versions. */
export const EXECUTABLE_ARTIFACT_VERSION = 1 as const;

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
