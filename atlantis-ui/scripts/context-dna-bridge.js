#!/usr/bin/env node
/**
 * Context DNA Bridge Script
 *
 * Node.js script called by Python to interact with Context DNA storage.
 * Provides CLI interface for Context DNA operations.
 *
 * Usage: node context-dna-bridge.js <payload-file>
 *
 * Week 20 Day 1
 * Version: 8.0.0
 */

const fs = require('fs');
const path = require('path');

// Import Context DNA modules (assume compiled TypeScript output)
const { getAgentContextManager } = require('../dist/services/context-dna');

/**
 * Main execution
 */
async function main() {
  try {
    // Read payload from file
    const payloadFile = process.argv[2];
    if (!payloadFile) {
      throw new Error('Usage: node context-dna-bridge.js <payload-file>');
    }

    const payload = JSON.parse(fs.readFileSync(payloadFile, 'utf-8'));

    // Get Context DNA manager
    const manager = getAgentContextManager();

    // Execute operation
    let result;

    switch (payload.operation) {
      case 'initialize_context':
        await manager.initializeContext(deserializeContext(payload.context));
        result = { success: true };
        break;

      case 'store_agent_thought':
        await manager.storeAgentThought(
          deserializeContext(payload.context),
          payload.thought,
          payload.metadata
        );
        result = { success: true };
        break;

      case 'store_agent_result':
        result = await manager.storeAgentResult(
          deserializeContext(payload.context),
          payload.result
        );
        break;

      case 'retrieve_context':
        const contextResult = await manager.retrieveContext(payload.query);
        result = {
          success: true,
          conversations: contextResult.conversations,
          memories: contextResult.memories,
          tasks: contextResult.tasks,
          performanceMs: contextResult.performanceMs,
        };
        break;

      case 'finalize_context':
        await manager.finalizeContext(deserializeContext(payload.context));
        result = { success: true };
        break;

      default:
        throw new Error(`Unknown operation: ${payload.operation}`);
    }

    // Output result as JSON
    console.log(JSON.stringify(result));
    process.exit(0);
  } catch (error) {
    // Output error as JSON
    console.log(
      JSON.stringify({
        success: false,
        error: error.message,
      })
    );
    process.exit(1);
  }
}

/**
 * Deserialize context from Python format
 */
function deserializeContext(context) {
  return {
    agentId: context.agentId,
    projectId: context.projectId,
    taskId: context.taskId || undefined,
    parentAgentId: context.parentAgentId || undefined,
    sessionId: context.sessionId,
    startTime: new Date(context.startTime),
    metadata: context.metadata || undefined,
  };
}

// Run main
main();
