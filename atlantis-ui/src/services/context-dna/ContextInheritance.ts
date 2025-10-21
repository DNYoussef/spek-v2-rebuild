/**
 * Context Inheritance
 *
 * Handles parent → child context passing during agent delegation.
 * Tracks delegation chains and enables context flow through hierarchy.
 *
 * Week 20 Day 2
 * Version: 8.0.0
 */

import { getMemoryCoordinator, MemoryCoordinator } from './MemoryCoordinator';
import { AgentExecutionContext } from './AgentContextIntegration';

/**
 * Delegation chain node
 */
export interface DelegationChainNode {
  agentId: string;
  parentAgentId?: string;
  childrenAgentIds: string[];
  level: number; // 0 = Queen, 1 = Princess, 2 = Drone
  delegatedAt: Date;
}

/**
 * Context inheritance result
 */
export interface InheritanceResult {
  success: boolean;
  contextInherited: {
    conversations: number;
    memories: number;
    tasks: number;
  };
  delegationChain: DelegationChainNode[];
}

/**
 * ContextInheritance Manager
 *
 * Manages context flow during agent delegation.
 */
export class ContextInheritance {
  private memoryCoordinator: MemoryCoordinator;
  private delegationChains: Map<string, DelegationChainNode[]>;

  constructor(memoryCoordinator?: MemoryCoordinator) {
    this.memoryCoordinator = memoryCoordinator || getMemoryCoordinator();
    this.delegationChains = new Map();
  }

  /**
   * Delegate task from parent to child with context inheritance
   */
  async delegateWithContext(
    parentContext: AgentExecutionContext,
    childAgentId: string,
    childTaskId?: string
  ): Promise<InheritanceResult> {
    // Create delegation chain node
    const parentNode = this.getOrCreateNode(
      parentContext.agentId,
      parentContext.parentAgentId
    );

    const childNode: DelegationChainNode = {
      agentId: childAgentId,
      parentAgentId: parentContext.agentId,
      childrenAgentIds: [],
      level: parentNode.level + 1,
      delegatedAt: new Date(),
    };

    // Update parent's children
    parentNode.childrenAgentIds.push(childAgentId);

    // Store delegation chain
    const projectKey = parentContext.projectId;
    const chain = this.delegationChains.get(projectKey) || [];
    chain.push(childNode);
    this.delegationChains.set(projectKey, chain);

    // Inherit context from parent to child
    const result = await this.memoryCoordinator.inheritContext({
      parentAgentId: parentContext.agentId,
      childAgentId: childAgentId,
      projectId: parentContext.projectId,
      taskId: childTaskId,
      includeConversations: true,
      includeMemories: true,
      includeTasks: true,
    });

    return {
      success: true,
      contextInherited: result,
      delegationChain: this.getDelegationChain(projectKey),
    };
  }

  /**
   * Get full delegation chain for project
   */
  getDelegationChain(projectId: string): DelegationChainNode[] {
    return this.delegationChains.get(projectId) || [];
  }

  /**
   * Get delegation path from root to agent
   */
  getDelegationPath(projectId: string, agentId: string): DelegationChainNode[] {
    const chain = this.getDelegationChain(projectId);
    const path: DelegationChainNode[] = [];

    let currentAgentId: string | undefined = agentId;

    while (currentAgentId) {
      const node = chain.find(n => n.agentId === currentAgentId);
      if (!node) break;

      path.unshift(node);
      currentAgentId = node.parentAgentId;
    }

    return path;
  }

  /**
   * Clear delegation chain for project (called after completion)
   */
  clearDelegationChain(projectId: string): void {
    this.delegationChains.delete(projectId);
  }

  // Private helpers
  private getOrCreateNode(
    agentId: string,
    parentAgentId?: string
  ): DelegationChainNode {
    // If parent exists, find in chains
    if (parentAgentId) {
      for (const chain of this.delegationChains.values()) {
        const node = chain.find(n => n.agentId === agentId);
        if (node) return node;
      }
    }

    // Create root node (Queen)
    return {
      agentId,
      parentAgentId,
      childrenAgentIds: [],
      level: 0,
      delegatedAt: new Date(),
    };
  }
}

/**
 * Singleton instance
 */
let contextInheritanceInstance: ContextInheritance | null = null;

/**
 * Get or create ContextInheritance singleton
 */
export function getContextInheritance(): ContextInheritance {
  if (!contextInheritanceInstance) {
    contextInheritanceInstance = new ContextInheritance();
  }
  return contextInheritanceInstance;
}
