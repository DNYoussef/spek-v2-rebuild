/**
 * Context DNA Service Exports
 *
 * Centralized exports for Context DNA storage and memory retrieval.
 */

export * from './types';
export * from './ContextDNAStorage';
export * from './MemoryRetrieval';
export * from './RetentionManager';
export * from './ArtifactManager';
export * from './PerformanceBenchmark';

export {
  getContextDNAStorage,
  ContextDNAStorage,
} from './ContextDNAStorage';

export {
  getMemoryRetrieval,
  MemoryRetrieval,
} from './MemoryRetrieval';

export {
  getRetentionManager,
  RetentionManager,
} from './RetentionManager';

export {
  getArtifactManager,
  ArtifactManager,
} from './ArtifactManager';

export {
  getAgentContextManager,
  AgentContextManager,
  withContextPersistence,
} from './AgentContextIntegration';

export type {
  AgentExecutionContext,
  ContextPersistenceResult,
  AgentMemoryQueryOptions,
} from './AgentContextIntegration';

export {
  getRedisSessionManager,
  RedisSessionManager,
} from './RedisSessionManager';

export type {
  SessionState,
  SessionStats,
} from './RedisSessionManager';

export {
  getMemoryCoordinator,
  MemoryCoordinator,
} from './MemoryCoordinator';

export type {
  MemorySharingOptions,
  ContextInheritanceConfig,
  ContextSearchFilters,
} from './MemoryCoordinator';

export {
  getContextInheritance,
  ContextInheritance,
} from './ContextInheritance';

export type {
  DelegationChainNode,
  InheritanceResult,
} from './ContextInheritance';

export {
  getRetentionPolicyEnforcer,
  RetentionPolicyEnforcer,
} from './RetentionPolicyEnforcer';

export type {
  RetentionPolicyConfig,
  CleanupResult,
} from './RetentionPolicyEnforcer';
