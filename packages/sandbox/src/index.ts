/** Public API version for sandbox capability policy. */
export const SANDBOX_API_VERSION = '0.1' as const;

export type Capability = string;

export interface ResourceLimits {
  readonly timeoutMs?: number;
  readonly memoryMb?: number;
}

/**
 * Declarative restrictions for a future sandbox adapter.
 * This type describes policy; it does not enforce isolation by itself.
 */
export interface SandboxPolicy {
  readonly allow: readonly Capability[];
  readonly deny: readonly Capability[];
  readonly limits?: ResourceLimits;
}
