/** Public API version for sandbox capability enforcement. */
export const SANDBOX_API_VERSION = '0.1' as const;

export type Capability = string;

export interface ResourceLimits {
  readonly timeoutMs?: number;
  readonly memoryMb?: number;
  readonly cpuUnits?: number;
}

export interface SandboxPolicy {
  readonly allow: readonly Capability[];
  readonly deny: readonly Capability[];
  readonly limits?: ResourceLimits;
}

export interface SandboxCommand {
  readonly executable: string;
  readonly arguments: readonly string[];
  readonly environment?: Readonly<Record<string, string>>;
  readonly workingDirectory?: string;
}

export interface SandboxExecutionResult {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
}

/**
 * Enforces capabilities for development or execution environments.
 * A manifest may declare policy, but only an implementation of this boundary enforces it.
 */
export interface Sandbox {
  execute(
    command: SandboxCommand,
    policy: SandboxPolicy,
    signal?: AbortSignal
  ): Promise<SandboxExecutionResult>;
}
