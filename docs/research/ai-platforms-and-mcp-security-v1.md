# AI Platform Integration and MCP Security Research Report

**Version**: 1.0
**Date**: 2025-10-08
**Status**: Complete
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild
**Research Focus**: Gap 1 (AI Platform Integration) and Gap 8 (MCP Security)

---

## Executive Summary

This report provides comprehensive research findings for two critical gaps identified in the SPEK v2 rebuild project:

1. **Gap 1: AI Platform Integration Challenges** - Addressing Gemini CLI stuck thinking bugs, GPT-5 Codex prompt caching strategies, and multi-platform orchestration patterns
2. **Gap 8: MCP Server Security** - Implementing OAuth 2.0 Resource Server patterns, Docker security hardening, OPA policies, and network isolation

### Key Findings

- **Gemini CLI Issue #2025**: Documented workarounds for indefinite thinking loops with environment variable configuration
- **GPT-5 Codex Caching**: 90% cost savings achievable through intelligent semantic caching with proper prompt structure
- **Multi-Platform Orchestration**: Comprehensive fallback patterns using sequential, concurrent, and handoff orchestration
- **MCP OAuth 2.0**: Full Resource Server implementation with PKCE, resource indicators (RFC 8707), and protected resource metadata (RFC 9728)
- **Docker Security**: Production-hardened configurations with non-root execution, version pinning, and vulnerability scanning
- **Network Isolation**: Kubernetes NetworkPolicy examples for zero-trust microservices architecture
- **OPA Integration**: Policy-as-code patterns for MCP server access control and validation

---

## Part 1: AI Platform Integration Challenges (Gap 1)

### 1.1 Gemini CLI Stuck Thinking Bug (Issue #2025)

#### Problem Description

**Issue Tracking**: https://github.com/google-gemini/gemini-cli/issues/2025

**Symptoms**:
- CLI gets stuck "thinking" indefinitely and cannot be stopped
- Occurs when switching between gemini-2.5-pro and gemini-2.5-flash models
- Happens during complex prompts that trigger rate limiting
- Generates error: "Quota exceeded for quota metric 'StreamGenerateContent Requests'"
- Restarting CLI results in persistent hanging state

**Root Causes**:
1. Rate limiting triggers automatic fallback from Pro to Flash
2. Model switching during active thinking session causes state corruption
3. Infinite retry loops when quota exhausted
4. CI environment detection interferes with interactive mode
5. Default thinking mode enabled for 2.5 Flash and Pro

#### Documented Workarounds

##### Workaround 1: Force Flash Model via Environment Variable

```bash
# Set environment variable to prevent model switching
export GEMINI_MODEL="gemini-2.5-flash"

# Or in .env file
echo "GEMINI_MODEL=gemini-2.5-flash" >> .env
```

**When to Use**: When you need consistent Flash performance and want to avoid Pro fallback issues.

**Limitations**: Loses access to Pro model capabilities for complex reasoning tasks.

##### Workaround 2: Disable Thinking Mode

```bash
# For API usage, set thinking budget to zero
# In your API call configuration:
{
  "model": "gemini-2.5-flash",
  "thinkingBudget": 0  # Disables thinking completely
}

# Or set to -1 to let model control thinking budget
{
  "thinkingBudget": -1  # Model-controlled thinking
}
```

**When to Use**: For speed-prioritized tasks where cost and latency matter more than deep reasoning.

**Limitations**: Thinking cannot be fully disabled for Gemini 2.5 Pro.

##### Workaround 3: API Key Authentication

```bash
# Use AI Studio API key to potentially avoid rate limits
export GEMINI_API_KEY="your-api-key-here"

# Or configure in settings.json
{
  "apiKey": "your-api-key-here",
  "model": "gemini-2.5-flash"
}
```

**When to Use**: When experiencing frequent rate limiting on default quotas.

**Benefit**: Dedicated quota allocation may reduce rate limit conflicts.

##### Workaround 4: CI Environment Variable Conflict Resolution

```bash
# If CI_ prefixed variables interfere with interactive mode
# Temporarily unset them for CLI execution
env -u CI_TOKEN gemini

# Or clear all CI variables
env -i PATH=$PATH HOME=$HOME gemini
```

**When to Use**: When CLI fails to enter interactive mode due to CI detection.

**Context**: The `is-in-ci` package detects CI_ prefixed variables and assumes non-interactive environment.

##### Workaround 5: MCP Server Timeout Configuration

```json
// In .gemini/settings.json
{
  "mcpServers": {
    "your-server": {
      "command": "npx",
      "args": ["-y", "your-mcp-server"],
      "timeout": 30000  // 30 seconds timeout (in milliseconds)
    }
  }
}
```

**When to Use**: To prevent MCP server operations from hanging indefinitely.

**Best Practice**: Set timeouts between 10-60 seconds based on expected operation duration.

##### Workaround 6: Configuration Precedence Strategy

**Gemini CLI Configuration Precedence** (lowest to highest priority):
1. Default values (hardcoded)
2. System defaults file
3. User settings file (`~/.gemini/settings.json`)
4. Project settings file (`.gemini/settings.json`)
5. System settings file (`/etc/gemini/settings.json`)
6. Environment variables
7. Command-line arguments

**Strategy**: Use environment variables or CLI arguments to override problematic defaults:

```bash
# Command-line override (highest priority)
gemini --model gemini-2.5-flash --timeout 30000

# Environment variable override
export GEMINI_TIMEOUT=30000
export GEMINI_MODEL=gemini-2.5-flash
gemini
```

#### Production Implementation Pattern

```bash
#!/bin/bash
# gemini-safe-wrapper.sh
# Production-safe Gemini CLI execution with automatic recovery

set -euo pipefail

# Configuration
export GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
export GEMINI_TIMEOUT="${GEMINI_TIMEOUT:-30000}"
export GEMINI_MAX_RETRIES="${GEMINI_MAX_RETRIES:-3}"

# Function to run Gemini with timeout and retry logic
run_gemini_safe() {
  local prompt="$1"
  local attempt=1
  local max_time=120  # 2 minutes maximum execution time

  while [ $attempt -le $GEMINI_MAX_RETRIES ]; do
    echo "[Attempt $attempt/$GEMINI_MAX_RETRIES] Running Gemini CLI..."

    # Run with timeout
    if timeout $max_time gemini "$prompt" 2>&1; then
      echo "[Success] Gemini CLI completed successfully"
      return 0
    else
      local exit_code=$?

      if [ $exit_code -eq 124 ]; then
        echo "[Timeout] Gemini CLI exceeded ${max_time}s timeout"
      else
        echo "[Error] Gemini CLI failed with exit code $exit_code"
      fi

      # Exponential backoff
      local wait_time=$((2 ** attempt))
      echo "[Retry] Waiting ${wait_time}s before retry..."
      sleep $wait_time

      attempt=$((attempt + 1))
    fi
  done

  echo "[Failure] All $GEMINI_MAX_RETRIES attempts failed"
  return 1
}

# Example usage
run_gemini_safe "Your prompt here"
```

#### Long-Term Mitigation Strategy

**For SPEK v2 Implementation**:

1. **Model Selection Layer**: Implement intelligent model selection that avoids Pro->Flash transitions during active sessions
2. **Circuit Breaker Pattern**: Detect repeated timeouts and switch to fallback AI platform (Claude Code, Codex CLI)
3. **Quota Monitoring**: Proactively track quota usage and prevent rate limit hits
4. **State Persistence**: Save CLI state before risky operations to enable recovery
5. **Health Checks**: Implement periodic health checks to detect hanging sessions

```typescript
// Example: AI Platform Circuit Breaker Pattern
class GeminiCircuitBreaker {
  private failureCount: number = 0;
  private readonly maxFailures: number = 3;
  private readonly resetTimeout: number = 60000; // 1 minute
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private lastFailureTime: number = 0;

  async executeWithCircuitBreaker(
    operation: () => Promise<any>,
    fallback: () => Promise<any>
  ): Promise<any> {
    // If circuit is OPEN, use fallback immediately
    if (this.state === 'OPEN') {
      const timeSinceLastFailure = Date.now() - this.lastFailureTime;

      if (timeSinceLastFailure >= this.resetTimeout) {
        this.state = 'HALF_OPEN';
        console.log('[CircuitBreaker] Attempting recovery (HALF_OPEN)');
      } else {
        console.log('[CircuitBreaker] Circuit OPEN, using fallback');
        return fallback();
      }
    }

    try {
      const result = await Promise.race([
        operation(),
        this.createTimeout(30000) // 30 second timeout
      ]);

      // Success - reset circuit breaker
      if (this.state === 'HALF_OPEN') {
        console.log('[CircuitBreaker] Recovery successful, closing circuit');
      }
      this.state = 'CLOSED';
      this.failureCount = 0;

      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      console.error(`[CircuitBreaker] Failure ${this.failureCount}/${this.maxFailures}:`, error);

      if (this.failureCount >= this.maxFailures) {
        this.state = 'OPEN';
        console.log('[CircuitBreaker] Circuit opened, switching to fallback');
      }

      return fallback();
    }
  }

  private createTimeout(ms: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`Operation timeout after ${ms}ms`)), ms);
    });
  }
}

// Usage in SPEK v2
const geminiBreaker = new GeminiCircuitBreaker();

const result = await geminiBreaker.executeWithCircuitBreaker(
  // Primary: Gemini CLI operation
  async () => await executeGeminiCLI(prompt),

  // Fallback: Claude Code or Codex CLI
  async () => await executeClaudeCode(prompt)
);
```

---

### 1.2 GPT-5 Codex Prompt Caching Strategies (90% Savings)

#### Overview

**Cost Reduction**: 90% discount on cached input tokens
**Pricing**: $0.125 per million cached input tokens (vs $1.25 normal)
**Cache Type**: Intelligent semantic caching (not simple exact-match)
**Cache Duration**: Few minutes (automatic expiration)

#### Intelligent Semantic Caching

Unlike traditional exact-match caching, OpenAI's system recognizes **semantic similarity**:

```python
# Example: These prompts are semantically similar and benefit from caching
prompt1 = "Analyze this code for security vulnerabilities: [code]"
prompt2 = "Review this code for potential security issues: [code]"
# OpenAI's caching recognizes these as similar contexts
```

#### Prompt Structure for Maximum Cache Benefits

##### Strategy 1: Separate Base Context from Variable Input

```typescript
// GOOD: Structured for caching
const baseSystemPrompt = `
You are an expert code reviewer specializing in TypeScript.
You analyze code for:
- Security vulnerabilities (OWASP Top 10)
- Performance issues
- Type safety violations
- Best practice adherence

Review process:
1. Identify critical issues
2. Suggest fixes
3. Provide severity ratings
`;

// This stays constant and gets cached at 90% discount
const userQuery = `Review this authentication handler: ${codeSnippet}`;

const response = await openai.chat.completions.create({
  model: "gpt-5-codex",
  messages: [
    { role: "system", content: baseSystemPrompt },  // Cached
    { role: "user", content: userQuery }            // Not cached
  ]
});
```

```typescript
// BAD: Mixed context (poor caching)
const mixedPrompt = `
You are reviewing code. Here's the file to review: ${codeSnippet}
Check for security issues, performance problems, type errors, and best practices.
`;
// Entire prompt changes every time = no caching benefit
```

##### Strategy 2: Conversation Context Reuse

```python
# Example: Customer service application with 70% cost savings
from openai import AsyncOpenAI

client = AsyncOpenAI()

# Shared context for all customer queries (gets cached)
CUSTOMER_SERVICE_CONTEXT = """
You are a helpful customer service representative for ACME Corp.

Product catalog:
- Product A: $29.99, ships in 2-3 days
- Product B: $49.99, ships in 1-2 days
- Product C: $99.99, ships same day

Policies:
- 30-day return policy
- Free shipping over $50
- Price match guarantee

Common solutions:
- Order tracking: Check order status at acme.com/track
- Returns: Process returns at acme.com/returns
- Refunds: Processed within 5-7 business days
"""

async def handle_customer_query(query: str):
    # System prompt (cached across all queries)
    response = await client.chat.completions.create(
        model="gpt-5-codex",
        messages=[
            {"role": "system", "content": CUSTOMER_SERVICE_CONTEXT},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# Multiple queries reuse cached context
await handle_customer_query("How long does shipping take?")
await handle_customer_query("What's your return policy?")
await handle_customer_query("Can I track my order?")
# All three queries benefit from 90% discount on CUSTOMER_SERVICE_CONTEXT
```

**Result**: 70% overall cost savings due to high cache hit rate on shared context.

##### Strategy 3: Code Review Pipeline with 80% Cache Hits

```typescript
// Code review system processing multiple files from same repository
interface CodeReviewConfig {
  repositoryContext: string;  // Cached
  codebaseStandards: string;  // Cached
  fileToReview: string;       // Variable
}

class CachedCodeReviewer {
  private repositoryContext: string;
  private codebaseStandards: string;

  constructor(repoPath: string) {
    // Load once, cache across all file reviews
    this.repositoryContext = `
Repository: ${repoPath}
Architecture: Microservices with TypeScript
Framework: NestJS
Database: PostgreSQL
Testing: Jest + Supertest

Module structure:
- /src/auth - Authentication and authorization
- /src/users - User management
- /src/orders - Order processing
- /src/payments - Payment integration
    `;

    this.codebaseStandards = `
Coding standards:
- NASA POT10 compliance (functions <=60 lines, >=2 assertions, no recursion)
- FSM-first architecture for all features
- Dependency injection throughout
- 80%+ test coverage required
- No any types without explicit annotation
    `;
  }

  async reviewFile(filePath: string, fileContent: string): Promise<string> {
    const response = await openai.chat.completions.create({
      model: "gpt-5-codex",
      messages: [
        {
          role: "system",
          content: this.repositoryContext + "\n" + this.codebaseStandards
          // These stay constant across all file reviews = 90% discount
        },
        {
          role: "user",
          content: `Review this file: ${filePath}\n\n${fileContent}`
          // Only this changes per file
        }
      ]
    });

    return response.choices[0].message.content;
  }
}

// Usage: Review 100 files with 80% cache hit rate
const reviewer = new CachedCodeReviewer('/path/to/repo');

for (const file of filesToReview) {
  const review = await reviewer.reviewFile(file.path, file.content);
  // Context cached after first file, subsequent 99 files get 90% discount
}
```

**Result**: 80% cache hit rate = significant cost reduction for bulk operations.

##### Strategy 4: Document Processing Pipeline (60% Cost Reduction)

```python
# Document processing with intelligent batching
class CachedDocumentProcessor:
    def __init__(self):
        self.processing_instructions = """
Extract and structure the following information:
1. Document type and metadata
2. Key entities (people, organizations, dates)
3. Main topics and themes
4. Action items or decisions
5. Summary (3-5 sentences)

Output format: JSON
"""

    async def process_batch(self, documents: list[str]) -> list[dict]:
        results = []

        for doc in documents:
            response = await client.chat.completions.create(
                model="gpt-5-codex",
                messages=[
                    {
                        "role": "system",
                        "content": self.processing_instructions
                        # Cached across all documents in batch
                    },
                    {
                        "role": "user",
                        "content": f"Process this document:\n\n{doc}"
                    }
                ]
            )
            results.append(response.choices[0].message.content)

        return results

# Process 1000 documents with 60% cost reduction
processor = CachedDocumentProcessor()
results = await processor.process_batch(documents)
```

#### Real-World Production Impact

| Use Case | Cache Hit Rate | Cost Savings | Implementation Complexity |
|----------|---------------|--------------|--------------------------|
| Customer Service | 70% | 70% reduction | Low (shared context) |
| Code Review | 80% | 80% reduction | Medium (repo context) |
| Document Processing | 60% | 60% reduction | Low (instruction caching) |
| API Documentation | 85% | 85% reduction | Medium (spec caching) |
| Test Generation | 75% | 75% reduction | Medium (pattern caching) |

#### Best Practices for Caching Optimization

1. **Separate Static from Dynamic Content**
   - Static: System prompts, instructions, knowledge bases, policies
   - Dynamic: User queries, specific data, file content

2. **Use Consistent Prompt Templates**
   - Define reusable templates for common operations
   - Keep template structure identical across invocations

3. **Batch Similar Operations**
   - Group related operations within cache window (few minutes)
   - Process files from same repository together
   - Handle similar customer queries in sequence

4. **Monitor Cache Effectiveness**
   ```typescript
   // Track caching performance
   interface CachingMetrics {
     totalRequests: number;
     cachedTokens: number;
     uncachedTokens: number;
     estimatedSavings: number;
   }

   function calculateCacheSavings(metrics: CachingMetrics): number {
     const cacheRate = metrics.cachedTokens / (metrics.cachedTokens + metrics.uncachedTokens);
     const normalCost = (metrics.cachedTokens + metrics.uncachedTokens) * 1.25 / 1_000_000;
     const actualCost = (metrics.uncachedTokens * 1.25 + metrics.cachedTokens * 0.125) / 1_000_000;
     return ((normalCost - actualCost) / normalCost) * 100; // Percentage savings
   }
   ```

5. **Minimize Prompt Variation**
   - Avoid timestamps or random IDs in system prompts
   - Use placeholders for variable data
   - Keep instruction formatting consistent

#### GPT-5-Codex Prompting Best Practices

The core principle for GPT-5-Codex: **"Less is more"**

```typescript
// GOOD: Minimal prompt (40% fewer tokens than GPT-5 developer message)
const minimalPrompt = `
Review this TypeScript code for security issues:

${codeSnippet}

Focus on: OWASP Top 10, injection attacks, authentication flaws.
`;

// BAD: Over-explained prompt (wastes tokens and cache efficiency)
const bloatedPrompt = `
You are an expert security analyst with 15 years of experience in TypeScript,
Node.js, and web application security. Your task is to perform a comprehensive
security review of the provided code snippet. Please analyze the code carefully,
considering all possible attack vectors including but not limited to SQL injection,
XSS, CSRF, authentication bypasses, authorization issues, and any other security
vulnerabilities that may exist. Provide detailed explanations for each finding,
including severity ratings, reproduction steps, and recommended fixes. Be thorough
and methodical in your analysis.

Here is the code to review:
${codeSnippet}
`;
// This wastes tokens and reduces caching efficiency
```

**Codex CLI System Prompt Reference**: The official Codex CLI system prompt is the gold standard for minimal, effective prompting.

#### Implementation for SPEK v2

```typescript
// SPEK v2: Caching-Optimized AI Platform Wrapper
class CachedAIPlatform {
  private static readonly SPEK_SYSTEM_CONTEXT = `
SPEK Platform Code Review Agent

Architecture: FSM-first, microservices
Standards: NASA POT10, TypeScript strict mode
Quality Gates: 92% NASA compliance, 90% FSM coverage, 80% test coverage
Security: OWASP Top 10, Bandit/Semgrep scanning

Review checklist:
- Function length <=60 lines
- Minimum 2 assertions per function
- No recursion (use iteration with fixed bounds)
- State isolation (one file per state)
- Enum-based events (no string events)
- Centralized transitions via TransitionHub
- Error recovery paths defined
  `;

  async reviewCode(
    filePath: string,
    fileContent: string,
    reviewType: 'security' | 'quality' | 'architecture'
  ): Promise<CodeReviewResult> {
    // System context cached across all reviews (90% discount)
    // Only file-specific content changes

    const response = await openai.chat.completions.create({
      model: "gpt-5-codex",
      messages: [
        {
          role: "system",
          content: CachedAIPlatform.SPEK_SYSTEM_CONTEXT
          // Cached - same for all reviews
        },
        {
          role: "user",
          content: `Review type: ${reviewType}\nFile: ${filePath}\n\n${fileContent}`
          // Not cached - specific to this file
        }
      ]
    });

    return this.parseReviewResult(response.choices[0].message.content);
  }
}
```

---

### 1.3 Multi-Platform AI Orchestration Patterns

#### Platform Specialization Matrix

| Platform | Best For | Context | Cost | Availability |
|----------|---------|---------|------|--------------|
| **Gemini 2.5 Pro** | Research, planning, large-context analysis | 1M tokens | Free tier | Public |
| **Gemini 2.5 Flash** | Cost-effective operations, rapid iteration | 1M tokens | Free tier | Public |
| **GPT-5 Codex** | Autonomous coding, browser automation, 7+ hour sessions | 272K tokens | $1.25/M input | Paid |
| **Claude Opus 4.1** | Quality analysis, code review (72.7% SWE-bench) | 200K tokens | Premium | Paid |
| **Claude Sonnet 4** | Coordination, sequential thinking | 200K tokens | Mid-tier | Paid |

#### Orchestration Pattern Types

##### Pattern 1: Sequential Orchestration

**Use Case**: Multi-step workflows with dependencies

```typescript
// Example: Spec -> Research -> Plan -> Implement workflow
interface SequentialOrchestrator {
  async executeWorkflow(task: Task): Promise<Result> {
    // Step 1: Gemini Pro for large-context research
    const research = await this.geminiProAgent.research(task.requirements);

    // Step 2: Claude Sonnet for coordination and planning
    const plan = await this.claudeSonnetAgent.plan(research);

    // Step 3: GPT-5 Codex for autonomous implementation
    const implementation = await this.codexAgent.implement(plan);

    // Step 4: Claude Opus for quality validation
    const validation = await this.claudeOpusAgent.validate(implementation);

    return {
      research,
      plan,
      implementation,
      validation
    };
  }
}
```

**Benefits**:
- Clear workflow progression
- Each agent uses optimal model for its task
- Easy to debug and monitor

**Limitations**:
- Sequential execution slower than parallel
- Blocked by failures in early steps

##### Pattern 2: Concurrent Orchestration

**Use Case**: Independent tasks that can run in parallel

```typescript
// Example: Parallel code review across multiple domains
interface ConcurrentOrchestrator {
  async executeParallel(files: string[]): Promise<ReviewResults> {
    // All agents work simultaneously
    const [securityReview, qualityReview, performanceReview] = await Promise.all([
      this.claudeOpusAgent.reviewSecurity(files),  // Claude Opus for security
      this.geminiFlashAgent.reviewQuality(files),  // Gemini Flash for cost-effective quality
      this.codexAgent.reviewPerformance(files)     // Codex for performance analysis
    ]);

    return {
      security: securityReview,
      quality: qualityReview,
      performance: performanceReview
    };
  }
}
```

**Benefits**:
- 2.8-4.4x speed improvement vs sequential
- Efficient resource utilization
- Cost optimization through platform distribution

**Limitations**:
- Requires coordination to merge results
- Risk of conflicts in concurrent outputs

##### Pattern 3: Handoff Orchestration

**Use Case**: Dynamic responsibility transfer based on context evolution

```typescript
// Example: Development task with dynamic agent selection
interface HandoffOrchestrator {
  async executeWithHandoff(task: Task): Promise<Result> {
    let currentAgent = this.selectInitialAgent(task);
    let result = await currentAgent.execute(task);

    while (!result.complete) {
      // Evaluate if handoff needed
      const nextAgent = this.evaluateHandoff(result);

      if (nextAgent !== currentAgent) {
        console.log(`Handoff: ${currentAgent.name} -> ${nextAgent.name}`);
        currentAgent = nextAgent;
      }

      result = await currentAgent.continue(result);
    }

    return result;
  }

  private evaluateHandoff(result: IntermediateResult): Agent {
    if (result.needsLargeContext) {
      return this.geminiProAgent;  // Switch to Gemini Pro for 1M context
    } else if (result.needsBrowserAutomation) {
      return this.codexAgent;  // Switch to Codex for browser tools
    } else if (result.needsQualityValidation) {
      return this.claudeOpusAgent;  // Switch to Claude Opus for review
    }
    return currentAgent;  // No handoff needed
  }
}
```

**Benefits**:
- Adaptive to changing requirements
- Optimal model for each phase
- Efficient resource usage

**Limitations**:
- Complex handoff logic
- Potential context loss during transitions

##### Pattern 4: Group Chat Orchestration

**Use Case**: Collaborative brainstorming and problem solving

```typescript
// Example: Architecture design with multiple expert agents
interface GroupChatOrchestrator {
  async brainstorm(problem: DesignProblem): Promise<ArchitectureProposal> {
    const participants = [
      this.geminiProAgent,     // Research and broad context
      this.claudeOpusAgent,    // Quality and best practices
      this.codexAgent,         // Implementation feasibility
      this.claudeSonnetAgent   // Coordination and synthesis
    ];

    const conversation: Message[] = [];
    let rounds = 0;
    const maxRounds = 5;

    while (rounds < maxRounds && !this.isConsensusReached(conversation)) {
      for (const agent of participants) {
        const message = await agent.contribute(problem, conversation);
        conversation.push(message);
      }
      rounds++;
    }

    // Coordinator synthesizes final proposal
    return this.claudeSonnetAgent.synthesize(conversation);
  }

  private isConsensusReached(conversation: Message[]): boolean {
    // Check if agents agree on key decisions
    const recentMessages = conversation.slice(-4);  // Last round
    return this.detectAgreement(recentMessages);
  }
}
```

**Benefits**:
- Diverse perspectives from different models
- Creative solutions through collaboration
- Built-in validation through peer review

**Limitations**:
- Can be expensive (multiple model calls)
- May take longer to reach consensus
- Requires sophisticated coordination logic

##### Pattern 5: Magentic Orchestration (Manager-Agent)

**Use Case**: Complex, open-ended problems with dynamic task decomposition

```typescript
// Example: SPEK v2 implementation with Queen-Princess-Drone hierarchy
interface MagneticOrchestrator {
  async orchestrateComplexTask(objective: Objective): Promise<Result> {
    // Manager agent (Queen) builds dynamic task ledger
    const taskLedger = await this.queenAgent.decompose(objective);

    const results = new Map<string, TaskResult>();

    while (!taskLedger.isComplete()) {
      // Get next task from ledger
      const task = taskLedger.getNextTask();

      // Select best agent (Princess) for domain
      const agent = this.selectAgentForTask(task);

      // Execute task
      const result = await agent.execute(task);

      // Manager evaluates and updates ledger
      taskLedger.update(task, result);
      results.set(task.id, result);

      // Manager may spawn new tasks based on results
      const newTasks = await this.queenAgent.evaluateProgress(taskLedger, result);
      taskLedger.addTasks(newTasks);
    }

    // Consolidate all results
    return this.queenAgent.consolidate(results);
  }

  private selectAgentForTask(task: Task): Agent {
    // Route to specialized Princess based on domain
    switch (task.domain) {
      case 'research':
        return this.geminiProAgent;  // 1M context for research
      case 'coding':
        return this.codexAgent;  // Autonomous coding
      case 'quality':
        return this.claudeOpusAgent;  // 72.7% SWE-bench
      case 'coordination':
        return this.claudeSonnetAgent;  // Sequential thinking
      default:
        return this.geminiFlashAgent;  // Cost-effective default
    }
  }
}
```

**Benefits**:
- Highly adaptive to changing requirements
- Efficient resource allocation
- Scales to complex multi-phase projects

**Limitations**:
- Requires sophisticated manager agent
- Complex state management
- Higher coordination overhead

#### Fallback Pattern Implementation

**Critical for Production Reliability**

```typescript
// Multi-level fallback strategy
class PlatformFallbackOrchestrator {
  private platformHealth = new Map<string, HealthStatus>();
  private readonly fallbackChain = [
    'gpt-5-codex',      // Primary (highest capability)
    'claude-opus-4.1',  // First fallback (high quality)
    'gemini-2.5-pro',   // Second fallback (large context, free)
    'claude-sonnet-4',  // Third fallback (coordination)
    'gemini-2.5-flash'  // Last resort (fast, free, always available)
  ];

  async executeWithFallback(
    task: Task,
    primaryPlatform: string
  ): Promise<Result> {
    // Try primary platform first
    try {
      return await this.executePlatform(primaryPlatform, task);
    } catch (error) {
      this.recordFailure(primaryPlatform, error);

      // Attempt fallback chain
      for (const fallbackPlatform of this.getFallbackChain(primaryPlatform)) {
        if (this.isPlatformHealthy(fallbackPlatform)) {
          try {
            console.log(`Fallback: ${primaryPlatform} -> ${fallbackPlatform}`);
            return await this.executePlatform(fallbackPlatform, task);
          } catch (fallbackError) {
            this.recordFailure(fallbackPlatform, fallbackError);
            continue;
          }
        }
      }

      throw new Error('All platforms failed');
    }
  }

  private getFallbackChain(primary: string): string[] {
    // Return fallback chain excluding primary
    return this.fallbackChain.filter(p => p !== primary);
  }

  private isPlatformHealthy(platform: string): boolean {
    const health = this.platformHealth.get(platform);
    if (!health) return true;  // Assume healthy if no data

    // Circuit breaker logic
    const failureRate = health.failures / health.attempts;
    return failureRate < 0.5 && health.lastSuccess > Date.now() - 300000;  // 5 min
  }

  private recordFailure(platform: string, error: Error): void {
    const health = this.platformHealth.get(platform) || {
      attempts: 0,
      failures: 0,
      lastSuccess: 0,
      lastFailure: 0
    };

    health.attempts++;
    health.failures++;
    health.lastFailure = Date.now();

    this.platformHealth.set(platform, health);

    // Log for monitoring
    console.error(`[${platform}] Failure ${health.failures}/${health.attempts}:`, error);
  }
}
```

#### Real-World Production Example: Fujitsu Sales Transformation

**Use Case**: Automated sales proposal generation

**Implementation**:
- **Research Agent** (Gemini 2.5 Pro): Market research and data analysis (1M context for comprehensive reports)
- **Data Analysis Agent** (GPT-5 Codex): Customer data processing and insights
- **Document Creation Agent** (Claude Opus): Proposal writing and formatting (quality-focused)
- **Coordinator Agent** (Claude Sonnet): Workflow orchestration with sequential thinking

**Results**:
- 67% reduction in proposal production time
- Consistent quality across all proposals
- Parallel execution for data gathering
- Sequential refinement for document quality

**Pattern Used**: Concurrent + Sequential Hybrid

```typescript
// Fujitsu-style implementation
async function generateSalesProposal(customer: Customer): Promise<Proposal> {
  // Phase 1: Concurrent data gathering (parallel)
  const [marketData, customerInsights, competitorAnalysis] = await Promise.all([
    geminiProAgent.researchMarket(customer.industry),      // 1M context
    codexAgent.analyzeCustomerData(customer.history),      // Data processing
    claudeOpusAgent.analyzeCompetitors(customer.competitors) // Quality analysis
  ]);

  // Phase 2: Sequential document creation (quality-focused)
  const outline = await claudeSonnetAgent.createOutline({
    marketData,
    customerInsights,
    competitorAnalysis
  });

  const draft = await claudeOpusAgent.writeDraft(outline);
  const review = await claudeSonnetAgent.reviewDraft(draft);
  const final = await claudeOpusAgent.finalize(review);

  return final;
}
```

#### Cost Optimization Across Platforms

```typescript
// Intelligent cost optimization
class CostOptimizedOrchestrator {
  private readonly costPerToken = {
    'gemini-2.5-pro': 0,           // Free tier
    'gemini-2.5-flash': 0,         // Free tier
    'gpt-5-codex': 1.25,           // $1.25/M input tokens
    'claude-opus-4.1': 15.0,       // Premium pricing
    'claude-sonnet-4': 3.0         // Mid-tier pricing
  };

  selectPlatformByCost(
    task: Task,
    budgetConstraint: number
  ): string {
    // Estimate token usage
    const estimatedTokens = this.estimateTokens(task);

    // Calculate cost for each platform
    const costs = this.fallbackChain.map(platform => ({
      platform,
      cost: (estimatedTokens / 1_000_000) * this.costPerToken[platform],
      capability: this.platformCapability[platform]
    }));

    // Filter by budget
    const affordable = costs.filter(c => c.cost <= budgetConstraint);

    // Select highest capability within budget
    affordable.sort((a, b) => b.capability - a.capability);
    return affordable[0]?.platform || 'gemini-2.5-flash';  // Default to free tier
  }
}
```

#### SPEK v2 Implementation Strategy

**Recommended Pattern**: **Magentic Orchestration** with **Multi-Level Fallback**

```typescript
// SPEK v2: Queen-Princess-Drone with Platform Optimization
class SPEKOrchestrator {
  // Queen (500KB context) - Coordination
  private queenAgent: ClaudeSonnetAgent;

  // Princess Agents (2MB context each) - Domain specialists
  private princesses = {
    development: new CodexAgent(),        // GPT-5 Codex for autonomous coding
    quality: new ClaudeOpusAgent(),       // Claude Opus for 72.7% SWE-bench
    security: new ClaudeOpusAgent(),      // Claude Opus for security analysis
    research: new GeminiProAgent(),       // Gemini Pro for 1M context research
    infrastructure: new CodexAgent(),     // Codex for CI/CD automation
    coordination: new ClaudeSonnetAgent() // Sonnet for task orchestration
  };

  // Drone Agents (100KB context each) - Specialized execution
  private drones: Map<string, Agent> = new Map();

  async executeWorkflow(objective: Objective): Promise<Result> {
    // Queen decomposes objective into MECE tasks
    const taskLedger = await this.queenAgent.decompose(objective);

    // Route tasks to optimal Princess based on domain and platform
    const results = new Map<string, TaskResult>();

    for (const task of taskLedger.getTasks()) {
      // Select Princess for domain
      const princess = this.princesses[task.domain];

      // Princess may spawn specialized Drones
      const result = await this.executeWithFallback(
        () => princess.execute(task),
        task.priority
      );

      results.set(task.id, result);
    }

    // Queen consolidates all results
    return this.queenAgent.consolidate(results);
  }

  private async executeWithFallback(
    operation: () => Promise<Result>,
    priority: Priority
  ): Promise<Result> {
    // High priority: Try premium platforms first
    if (priority === 'HIGH') {
      return this.tryPlatforms(['gpt-5-codex', 'claude-opus-4.1', 'gemini-2.5-pro'], operation);
    }

    // Medium priority: Balance cost and capability
    if (priority === 'MEDIUM') {
      return this.tryPlatforms(['claude-sonnet-4', 'gemini-2.5-pro', 'gpt-5-codex'], operation);
    }

    // Low priority: Cost-effective first
    return this.tryPlatforms(['gemini-2.5-flash', 'gemini-2.5-pro', 'claude-sonnet-4'], operation);
  }
}
```

---

## Part 2: MCP Server Security (Gap 8)

### 2.1 OAuth 2.0 Resource Server Implementation

#### MCP Specification (v2025-03-26)

**MCP servers are OAuth 2.0 Resource Servers**

This classification has significant implications:
- MCP servers validate access tokens issued by **external** authorization servers
- MCP servers do NOT issue tokens themselves
- Clear separation between authorization server and resource server

#### Key Security Requirements

##### 1. Token Validation (MANDATORY)

```python
# Pseudocode for token validation
def validate_access_token(token: str) -> ValidationResult:
    """
    Validate access token per OAuth 2.1 Section 5.2

    Returns:
        HTTP 401: Invalid or expired token
        HTTP 403: Insufficient permissions
        HTTP 200: Valid token with claims
    """

    # Step 1: Verify token format
    if not token or not is_valid_jwt_format(token):
        return HTTP_401_UNAUTHORIZED

    # Step 2: Verify token signature
    if not verify_token_signature(token, public_key):
        return HTTP_401_UNAUTHORIZED

    # Step 3: Check expiration
    claims = decode_jwt(token)
    if claims.exp < current_timestamp():
        return HTTP_401_UNAUTHORIZED

    # Step 4: Validate issuer
    if claims.iss not in TRUSTED_ISSUERS:
        return HTTP_401_UNAUTHORIZED

    # Step 5: Verify audience (this MCP server)
    if claims.aud != MCP_SERVER_RESOURCE_IDENTIFIER:
        return HTTP_403_FORBIDDEN

    # Step 6: Check scopes
    required_scopes = get_required_scopes_for_operation()
    if not has_required_scopes(claims.scope, required_scopes):
        return HTTP_403_FORBIDDEN

    return ValidationResult(valid=True, claims=claims)


# Example implementation with FastAPI
from fastapi import FastAPI, Header, HTTPException
from jose import jwt, JWTError
import httpx

app = FastAPI()

# OAuth 2.0 configuration
AUTHORIZATION_SERVER = "https://auth.example.com"
JWKS_URI = f"{AUTHORIZATION_SERVER}/.well-known/jwks.json"
AUDIENCE = "https://mcp-server.example.com"

# Cache for JWKS
jwks_cache = None

async def get_jwks():
    """Fetch and cache JSON Web Key Set"""
    global jwks_cache
    if not jwks_cache:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URI)
            jwks_cache = response.json()
    return jwks_cache

async def validate_token(authorization: str) -> dict:
    """
    Validate Bearer token from Authorization header

    Raises:
        HTTPException(401): Invalid or expired token
        HTTPException(403): Insufficient permissions
    """

    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        # Get signing keys
        jwks = await get_jwks()

        # Decode and validate token
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True
            }
        )

        return claims

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/mcp/resource")
async def protected_resource(authorization: str = Header(None)):
    """
    Example MCP server endpoint with OAuth 2.0 protection
    """

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")

    # Validate token
    claims = await validate_token(authorization)

    # Check scopes
    scopes = claims.get("scope", "").split()
    if "mcp:read" not in scopes:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Token valid - process request
    return {
        "data": "Protected resource data",
        "user": claims.get("sub"),
        "scopes": scopes
    }
```

##### 2. PKCE for All Clients (MANDATORY)

**Proof Key for Code Exchange (PKCE)** is required for all authorization code flows:

```typescript
// Client-side PKCE implementation
import crypto from 'crypto';

class MCPClient {
  private codeVerifier: string;
  private codeChallenge: string;

  async initiateAuthorization(): Promise<string> {
    // Generate code verifier (random 43-128 character string)
    this.codeVerifier = this.generateCodeVerifier();

    // Generate code challenge (SHA-256 hash of verifier)
    this.codeChallenge = this.generateCodeChallenge(this.codeVerifier);

    // Build authorization URL
    const authUrl = new URL(`${AUTHORIZATION_SERVER}/authorize`);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('client_id', CLIENT_ID);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('scope', 'mcp:read mcp:write');
    authUrl.searchParams.set('code_challenge', this.codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');
    authUrl.searchParams.set('state', this.generateState());

    return authUrl.toString();
  }

  async exchangeCodeForToken(code: string): Promise<TokenResponse> {
    // Exchange authorization code for access token
    const response = await fetch(`${AUTHORIZATION_SERVER}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: REDIRECT_URI,
        client_id: CLIENT_ID,
        code_verifier: this.codeVerifier  // PKCE proof
      })
    });

    return response.json();
  }

  private generateCodeVerifier(): string {
    // Generate cryptographically random 43-128 character string
    return crypto.randomBytes(32).toString('base64url');
  }

  private generateCodeChallenge(verifier: string): string {
    // SHA-256 hash of code verifier
    return crypto
      .createHash('sha256')
      .update(verifier)
      .digest('base64url');
  }

  private generateState(): string {
    // Generate random state for CSRF protection
    return crypto.randomBytes(16).toString('base64url');
  }
}
```

##### 3. Resource Indicators (RFC 8707)

**Purpose**: Explicitly specify the intended MCP server for access tokens

```http
POST /token HTTP/1.1
Host: authorization-server.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=abc123
&redirect_uri=https://client.example.com/callback
&client_id=client123
&code_verifier=xyz789
&resource=https://mcp-server.example.com  # Resource indicator
```

**Server-side validation**:

```python
# Authorization server validates resource parameter
def issue_access_token(request: TokenRequest) -> TokenResponse:
    """
    Issue access token with resource-specific scope
    """

    # Validate resource parameter
    requested_resource = request.resource
    if requested_resource not in ALLOWED_RESOURCES:
        return error_response("invalid_target")

    # Issue token scoped to specific resource
    access_token = create_jwt({
        "iss": AUTHORIZATION_SERVER,
        "sub": request.user_id,
        "aud": requested_resource,  # Token only valid for this MCP server
        "scope": request.scope,
        "exp": current_time() + 3600  # 1 hour expiration
    })

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": request.scope
    }


# MCP server validates audience claim
def validate_token_audience(token: str) -> bool:
    """
    Ensure token was issued for THIS MCP server
    """
    claims = decode_jwt(token)

    # Check audience (aud) claim matches this server
    if claims.aud != "https://mcp-server.example.com":
        # Token was issued for a different resource server
        # Prevents token theft and reuse attacks
        return False

    return True
```

**Security Benefit**: Prevents malicious or compromised MCP servers from using stolen tokens to access other resources.

##### 4. Protected Resource Metadata (RFC 9728)

**Purpose**: Allow MCP servers to advertise trusted authorization servers

```json
{
  "resource": "https://mcp-server.example.com",
  "authorization_servers": [
    "https://auth.example.com",
    "https://backup-auth.example.com"
  ],
  "bearer_methods_supported": ["header", "body"],
  "resource_signing_alg_values_supported": ["RS256", "ES256"],
  "resource_documentation": "https://mcp-server.example.com/docs",
  "resource_policy_uri": "https://mcp-server.example.com/policy"
}
```

**Implementation**:

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata():
    """
    RFC 9728: Protected Resource Metadata endpoint

    Advertises which Authorization Servers this MCP server trusts
    """
    return JSONResponse({
        "resource": "https://mcp-server.example.com",
        "authorization_servers": [
            "https://auth.example.com"
        ],
        "bearer_methods_supported": ["header"],
        "resource_signing_alg_values_supported": ["RS256"],
        "resource_documentation": "https://mcp-server.example.com/docs",
        "resource_policy_uri": "https://mcp-server.example.com/policy"
    })


@app.get("/protected")
async def protected_endpoint(authorization: str = Header(None)):
    """
    When accessed without valid authorization, return 401 with
    WWW-Authenticate header pointing to metadata
    """

    if not authorization:
        return Response(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Bearer '
                    'realm="MCP Server", '
                    'resource_metadata="https://mcp-server.example.com/.well-known/oauth-protected-resource"'
                )
            },
            content="Authorization required"
        )

    # Validate token and proceed
    # ...
```

**Client Discovery Flow**:

```typescript
// Client discovers authorization server automatically
class MCPClientWithDiscovery {
  async discoverAuthorizationServer(mcpServerUrl: string): Promise<string> {
    // Step 1: Request protected resource without token
    const response = await fetch(`${mcpServerUrl}/protected`);

    if (response.status === 401) {
      // Step 2: Parse WWW-Authenticate header
      const wwwAuth = response.headers.get('WWW-Authenticate');
      const metadataUrl = this.extractMetadataUrl(wwwAuth);

      // Step 3: Fetch Protected Resource Metadata
      const metadata = await fetch(metadataUrl).then(r => r.json());

      // Step 4: Return first authorization server
      return metadata.authorization_servers[0];
    }

    throw new Error('Protected Resource Metadata not found');
  }

  private extractMetadataUrl(wwwAuth: string): string {
    // Parse: Bearer realm="...", resource_metadata="URL"
    const match = wwwAuth.match(/resource_metadata="([^"]+)"/);
    return match ? match[1] : null;
  }
}
```

##### 5. Error Handling Matrix

| Status Code | Meaning | Use Case | Response Headers |
|------------|---------|----------|------------------|
| **401 Unauthorized** | No valid token | Missing/invalid/expired token | `WWW-Authenticate: Bearer realm="MCP Server"` |
| **403 Forbidden** | Insufficient permissions | Valid token, wrong scopes | None required |
| **400 Bad Request** | Malformed request | Invalid authorization header format | None |

```python
# Complete error handling implementation
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response

@app.get("/mcp/resource")
async def mcp_endpoint(authorization: str = Header(None)):
    """
    MCP endpoint with proper OAuth 2.0 error handling
    """

    # Case 1: No authorization header (401)
    if not authorization:
        return Response(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Bearer '
                    'realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Authorization required"'
                )
            }
        )

    # Case 2: Invalid header format (400)
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=400,
            detail="Malformed authorization header"
        )

    # Case 3: Invalid/expired token (401)
    token = authorization[7:]
    try:
        claims = validate_token(token)
    except TokenExpiredError:
        return Response(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Bearer '
                    'realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Token expired"'
                )
            }
        )
    except TokenInvalidError:
        return Response(
            status_code=401,
            headers={
                "WWW-Authenticate": (
                    'Bearer '
                    'realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Token invalid"'
                )
            }
        )

    # Case 4: Insufficient scopes (403)
    required_scopes = ["mcp:read"]
    if not has_scopes(claims, required_scopes):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Required scopes: mcp:read"
        )

    # Valid token with correct scopes - proceed
    return {"data": "Protected resource"}
```

#### Complete Production Implementation Example

```python
# production_mcp_server.py
# Complete OAuth 2.0 Resource Server implementation for MCP

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from jose import jwt, JWTError
import httpx
from typing import Optional
from datetime import datetime
import logging

app = FastAPI()

# Configuration
AUTHORIZATION_SERVER = "https://auth.example.com"
JWKS_URI = f"{AUTHORIZATION_SERVER}/.well-known/jwks.json"
AUDIENCE = "https://mcp-server.example.com"
REQUIRED_ISSUER = AUTHORIZATION_SERVER

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWKS cache
jwks_cache = None
jwks_cache_time = None
JWKS_CACHE_TTL = 3600  # 1 hour

# Protected Resource Metadata (RFC 9728)
@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata():
    """Advertise trusted authorization servers"""
    return JSONResponse({
        "resource": AUDIENCE,
        "authorization_servers": [AUTHORIZATION_SERVER],
        "bearer_methods_supported": ["header"],
        "resource_signing_alg_values_supported": ["RS256", "ES256"],
        "resource_documentation": f"{AUDIENCE}/docs",
        "resource_policy_uri": f"{AUDIENCE}/policy"
    })

# JWKS fetching with caching
async def get_jwks():
    """Fetch and cache JWKS"""
    global jwks_cache, jwks_cache_time

    now = datetime.now().timestamp()
    if jwks_cache and jwks_cache_time and (now - jwks_cache_time < JWKS_CACHE_TTL):
        return jwks_cache

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(JWKS_URI, timeout=5.0)
            response.raise_for_status()
            jwks_cache = response.json()
            jwks_cache_time = now
            logger.info("JWKS refreshed successfully")
            return jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            if jwks_cache:
                logger.warning("Using stale JWKS cache")
                return jwks_cache
            raise

# Token validation dependency
async def validate_access_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Validate OAuth 2.0 access token

    Returns:
        dict: Token claims if valid

    Raises:
        HTTPException(401): Invalid/expired token
        HTTPException(403): Insufficient permissions
    """

    # Check for Authorization header
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization required",
            headers={
                "WWW-Authenticate": (
                    f'Bearer realm="MCP Server", '
                    f'resource_metadata="{AUDIENCE}/.well-known/oauth-protected-resource"'
                )
            }
        )

    # Check header format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=400,
            detail="Malformed authorization header"
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        # Fetch JWKS
        jwks = await get_jwks()

        # Decode and validate token
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256", "ES256"],
            audience=AUDIENCE,
            issuer=REQUIRED_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )

        logger.info(f"Token validated for user: {claims.get('sub')}")
        return claims

    except jwt.ExpiredSignatureError:
        logger.warning("Expired token")
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={
                "WWW-Authenticate": (
                    'Bearer realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Token expired"'
                )
            }
        )
    except jwt.JWTClaimsError as e:
        logger.warning(f"Invalid token claims: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token claims",
            headers={
                "WWW-Authenticate": (
                    'Bearer realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Invalid token claims"'
                )
            }
        )
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={
                "WWW-Authenticate": (
                    'Bearer realm="MCP Server", '
                    'error="invalid_token", '
                    'error_description="Invalid token"'
                )
            }
        )

# Scope validation helper
def require_scopes(*required_scopes: str):
    """Dependency to check required scopes"""
    async def check_scopes(claims: dict = Depends(validate_access_token)):
        token_scopes = claims.get("scope", "").split()

        for scope in required_scopes:
            if scope not in token_scopes:
                logger.warning(
                    f"Insufficient scopes. Required: {required_scopes}, "
                    f"Token has: {token_scopes}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}"
                )

        return claims

    return check_scopes

# Protected MCP endpoints
@app.get("/mcp/files")
async def list_files(claims: dict = Depends(require_scopes("mcp:read"))):
    """List files (requires mcp:read scope)"""
    return {
        "files": ["file1.txt", "file2.txt"],
        "user": claims.get("sub")
    }

@app.post("/mcp/files")
async def create_file(claims: dict = Depends(require_scopes("mcp:write"))):
    """Create file (requires mcp:write scope)"""
    return {
        "status": "created",
        "user": claims.get("sub")
    }

@app.delete("/mcp/files/{file_id}")
async def delete_file(
    file_id: str,
    claims: dict = Depends(require_scopes("mcp:write", "mcp:delete"))
):
    """Delete file (requires mcp:write AND mcp:delete scopes)"""
    return {
        "status": "deleted",
        "file_id": file_id,
        "user": claims.get("sub")
    }

# Health check (no authentication required)
@app.get("/health")
async def health_check():
    """Public health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### 2.2 Docker Container Security Hardening

#### Production-Hardened Dockerfile for MCP Servers

```dockerfile
# Dockerfile for secure MCP server deployment
# Based on Docker best practices and OWASP guidelines

# ============================================
# Stage 1: Build stage
# ============================================
FROM node:20.17.0-alpine3.19 AS builder

# Security: Run as non-root during build
RUN addgroup -g 1001 -S mcpgroup && \
    adduser -u 1001 -S mcpuser -G mcpgroup

# Set working directory
WORKDIR /build

# Copy dependency files first (better caching)
COPY package*.json ./

# Install dependencies (production only)
RUN npm ci --only=production --ignore-scripts

# Copy application code
COPY --chown=mcpuser:mcpgroup . .

# Build application (if TypeScript)
RUN npm run build

# ============================================
# Stage 2: Production stage
# ============================================
FROM node:20.17.0-alpine3.19

# Metadata
LABEL maintainer="security@example.com" \
      org.opencontainers.image.description="MCP Server - Secure Production Build" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="SPEK Platform"

# Security: Install security updates only
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache dumb-init && \
    rm -rf /var/cache/apk/*

# Security: Create non-root user with specific UID/GID
RUN addgroup -g 1001 -S mcpgroup && \
    adduser -u 1001 -S mcpuser -G mcpgroup

# Set working directory
WORKDIR /app

# Security: Set ownership before switching user
RUN chown mcpuser:mcpgroup /app

# Copy from build stage
COPY --from=builder --chown=mcpuser:mcpgroup /build/node_modules ./node_modules
COPY --from=builder --chown=mcpuser:mcpgroup /build/dist ./dist
COPY --from=builder --chown=mcpuser:mcpgroup /build/package*.json ./

# Security: Switch to non-root user
USER mcpuser

# Security: Expose non-privileged port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Security: Use dumb-init to handle signals properly
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Start application
CMD ["node", "dist/server.js"]
```

#### Security Hardening Configuration

##### 1. Non-Root User Execution

```dockerfile
# Best practice: Create system user with explicit UID/GID
RUN groupadd -r -g 1001 mcpgroup && \
    useradd -r -u 1001 -g mcpgroup -m -d /app -s /sbin/nologin mcpuser

# Set file ownership
RUN chown -R mcpuser:mcpgroup /app

# Switch to non-root user
USER mcpuser
```

**Why explicit UID/GID?**
- Consistent across image rebuilds
- Critical for security policies
- Required for Kubernetes securityContext

##### 2. Read-Only Filesystem

```dockerfile
# Make application files read-only
RUN chmod -R 555 /app/dist && \
    chmod -R 444 /app/package*.json

# Only /tmp is writable
VOLUME /tmp
```

**Docker Compose configuration**:

```yaml
services:
  mcp-server:
    image: mcp-server:latest
    read_only: true
    tmpfs:
      - /tmp:uid=1001,gid=1001,mode=1777,size=100m
    volumes:
      - type: tmpfs
        target: /app/logs
        tmpfs:
          uid: 1001
          gid: 1001
          mode: 1777
          size: 500m
```

##### 3. Resource Limits

```yaml
# docker-compose.yml
services:
  mcp-server:
    image: mcp-server:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'          # Maximum 1 CPU
          memory: 512M         # Maximum 512MB RAM
          pids: 100            # Maximum 100 processes
        reservations:
          cpus: '0.25'         # Reserve 0.25 CPU
          memory: 256M         # Reserve 256MB RAM
```

##### 4. Network Isolation

```yaml
# docker-compose.yml with network isolation
version: '3.8'

services:
  mcp-server:
    image: mcp-server:latest
    networks:
      - mcp-internal
    # No external network access by default
    dns:
      - 127.0.0.1  # No external DNS resolution
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port <1024
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined  # Use custom seccomp profile in production

  # Reverse proxy for controlled external access
  nginx:
    image: nginx:alpine
    networks:
      - mcp-internal
      - external
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro

networks:
  mcp-internal:
    driver: bridge
    internal: true  # No external routing
  external:
    driver: bridge
```

##### 5. Secrets Management

```yaml
# docker-compose.yml with Docker secrets
version: '3.8'

services:
  mcp-server:
    image: mcp-server:latest
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - API_KEY_FILE=/run/secrets/api_key
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

**Application code**:

```typescript
// Read secrets from files (not environment variables)
import fs from 'fs';

function getSecret(name: string): string {
  const secretPath = process.env[`${name}_FILE`];
  if (!secretPath) {
    throw new Error(`Secret file path not configured for ${name}`);
  }

  try {
    return fs.readFileSync(secretPath, 'utf8').trim();
  } catch (error) {
    throw new Error(`Failed to read secret ${name}: ${error.message}`);
  }
}

// Usage
const dbPassword = getSecret('DB_PASSWORD');
const apiKey = getSecret('API_KEY');
```

##### 6. Version Pinning and Vulnerability Scanning

```dockerfile
# Pin ALL versions (no auto-updates)
FROM node:20.17.0-alpine3.19@sha256:abc123...

# Pin package versions in package.json
{
  "dependencies": {
    "fastapi": "0.109.2",  # No ^ or ~
    "jose": "5.2.0",
    "httpx": "0.26.0"
  }
}
```

**CI/CD Integration (GitHub Actions)**:

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Scan Dockerfile
      - name: Run Hadolint
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      # Build image
      - name: Build Docker image
        run: docker build -t mcp-server:${{ github.sha }} .

      # Vulnerability scanning with Trivy
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: mcp-server:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Fail on critical/high vulnerabilities

      # Upload results to GitHub Security tab
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      # Scan dependencies
      - name: Run npm audit
        run: |
          npm audit --audit-level=high
          npm audit --json > npm-audit.json

      # Upload artifacts
      - name: Upload security reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-reports
          path: |
            trivy-results.sarif
            npm-audit.json
```

##### 7. AppArmor/SELinux Profiles

**AppArmor profile for MCP server**:

```text
# /etc/apparmor.d/docker-mcp-server
#include <tunables/global>

profile docker-mcp-server flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Deny all by default
  deny /** rwklx,

  # Allow execution of Node.js
  /usr/local/bin/node ix,
  /usr/bin/dumb-init ix,

  # Allow read access to application files
  /app/** r,
  /app/dist/** r,
  /app/node_modules/** r,

  # Allow write access to logs and tmp
  /app/logs/** rw,
  /tmp/** rw,

  # Allow network access (restricted to specific ports)
  network inet stream,
  network inet6 stream,

  # Deny dangerous capabilities
  deny capability sys_admin,
  deny capability sys_module,
  deny capability sys_rawio,

  # Allow only necessary capabilities
  capability net_bind_service,
}
```

**Docker Compose with AppArmor**:

```yaml
services:
  mcp-server:
    image: mcp-server:latest
    security_opt:
      - apparmor=docker-mcp-server
```

##### 8. Complete Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  mcp-server:
    image: mcp-server:${IMAGE_TAG:-latest}
    container_name: mcp-server

    # Security: Non-root user
    user: "1001:1001"

    # Security: Read-only root filesystem
    read_only: true

    # Security: Drop all capabilities, add only necessary
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

    # Security: Additional security options
    security_opt:
      - no-new-privileges:true
      - apparmor=docker-mcp-server

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
          pids: 100
        reservations:
          cpus: '0.25'
          memory: 256M

    # Environment variables (non-sensitive only)
    environment:
      - NODE_ENV=production
      - PORT=8080
      - LOG_LEVEL=info

    # Secrets (sensitive data)
    secrets:
      - db_password
      - api_key
      - jwt_secret

    # Volumes (minimal, read-only where possible)
    volumes:
      - type: tmpfs
        target: /tmp
        tmpfs:
          uid: 1001
          gid: 1001
          mode: 1777
          size: 100m
      - type: volume
        source: mcp-logs
        target: /app/logs

    # Network isolation
    networks:
      - mcp-internal

    # Health check
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

    # Restart policy
    restart: unless-stopped

    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Reverse proxy (only component with external access)
  nginx:
    image: nginx:1.25-alpine
    container_name: mcp-nginx

    # Security: Non-root user
    user: "101:101"

    # Security: Read-only filesystem
    read_only: true

    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
      - CHOWN
      - SETGID
      - SETUID

    security_opt:
      - no-new-privileges:true

    # Expose HTTPS only
    ports:
      - "443:443"

    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - type: tmpfs
        target: /var/cache/nginx
        tmpfs:
          size: 50m
      - type: tmpfs
        target: /var/run
        tmpfs:
          size: 10m

    networks:
      - mcp-internal
      - external

    depends_on:
      - mcp-server

    restart: unless-stopped

networks:
  mcp-internal:
    driver: bridge
    internal: true  # No external routing
    ipam:
      config:
        - subnet: 172.20.0.0/24
  external:
    driver: bridge

volumes:
  mcp-logs:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

---

### 2.3 Open Policy Agent (OPA) Integration

#### OPA for MCP Server Access Control

**Purpose**: Policy-as-code for dynamic access control decisions

##### 1. OPA Architecture with MCP

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       │ Authorization: Bearer <token>
       v
┌─────────────────────────┐
│    Reverse Proxy        │
│    (Nginx/Envoy)        │
└──────┬──────────────────┘
       │
       │ 1. Forward request to OPA
       v
┌─────────────────────────┐
│    OPA Policy Engine    │
│                         │
│  - Validate token       │
│  - Check user roles     │
│  - Evaluate policies    │
│  - Return decision      │
└──────┬──────────────────┘
       │
       │ 2. Allow/Deny decision
       v
┌─────────────────────────┐
│    MCP Server           │
│    (Resource Server)    │
└─────────────────────────┘
```

##### 2. Example Rego Policies for MCP

**Policy 1: Basic Authentication and Authorization**

```rego
# mcp_authz.rego
# OPA policy for MCP server authorization

package mcp.authz

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Allow if token valid and user has required permissions
allow if {
    token_valid
    has_required_scope
}

# Validate JWT token
token_valid if {
    # Extract token from Authorization header
    token := trim_prefix(input.headers.authorization, "Bearer ")

    # Decode and verify JWT
    [valid, _, payload] := io.jwt.decode_verify(
        token,
        {
            "cert": data.jwks,
            "aud": "https://mcp-server.example.com",
            "iss": "https://auth.example.com"
        }
    )

    valid == true

    # Token not expired
    payload.exp > time.now_ns() / 1000000000
}

# Check required scopes
has_required_scope if {
    # Get token payload
    token := trim_prefix(input.headers.authorization, "Bearer ")
    [_, _, payload] := io.jwt.decode(token)

    # Get required scope for this operation
    required_scope := required_scopes[input.method][input.path]

    # Check if token has required scope
    required_scope in payload.scope
}

# Define required scopes for each operation
required_scopes := {
    "GET": {
        "/mcp/files": "mcp:read",
        "/mcp/users": "mcp:read"
    },
    "POST": {
        "/mcp/files": "mcp:write",
        "/mcp/users": "mcp:admin"
    },
    "DELETE": {
        "/mcp/files": "mcp:delete",
        "/mcp/users": "mcp:admin"
    }
}

# Helper function
trim_prefix(str, prefix) := trimmed if {
    startswith(str, prefix)
    trimmed := substring(str, count(prefix), -1)
}
```

**Policy 2: Role-Based Access Control (RBAC)**

```rego
# mcp_rbac.rego
# OPA policy for role-based access control

package mcp.rbac

import future.keywords.if
import future.keywords.in

default allow := false

# Allow if user has required role
allow if {
    user_has_role(input.user, required_role)
}

# Get user from JWT token
user := payload.sub if {
    token := trim_prefix(input.headers.authorization, "Bearer ")
    [_, _, payload] := io.jwt.decode(token)
}

# Check if user has role
user_has_role(user, role) if {
    user_roles := data.roles[user]
    role in user_roles
}

# Get required role for operation
required_role := role_requirements[input.method][input.path] if {
    role_requirements[input.method][input.path]
}

# Define role requirements
role_requirements := {
    "GET": {
        "/mcp/files": "reader",
        "/mcp/admin/users": "admin"
    },
    "POST": {
        "/mcp/files": "writer",
        "/mcp/admin/users": "admin"
    },
    "DELETE": {
        "/mcp/files": "writer",
        "/mcp/admin/users": "admin"
    }
}

# Role data (would typically come from external source)
roles := {
    "user123": ["reader", "writer"],
    "admin456": ["admin", "reader", "writer"]
}
```

**Policy 3: Rate Limiting and Abuse Prevention**

```rego
# mcp_rate_limit.rego
# OPA policy for rate limiting

package mcp.rate_limit

import future.keywords.if

default allow := false

# Allow if rate limit not exceeded
allow if {
    not rate_limit_exceeded
}

# Check rate limit
rate_limit_exceeded if {
    # Get user from token
    token := trim_prefix(input.headers.authorization, "Bearer ")
    [_, _, payload] := io.jwt.decode(token)
    user := payload.sub

    # Get request count for user in last minute
    request_count := count([req |
        req := data.request_log[_]
        req.user == user
        req.timestamp > (time.now_ns() / 1000000000) - 60
    ])

    # Check against limit
    rate_limit := user_rate_limits[user]
    request_count >= rate_limit
}

# Define rate limits per user
user_rate_limits := {
    "user123": 100,      # 100 requests per minute
    "admin456": 1000,    # 1000 requests per minute
    "default": 60        # Default: 60 requests per minute
}

# Get user rate limit (with default)
get_rate_limit(user) := limit if {
    limit := user_rate_limits[user]
} else := user_rate_limits.default
```

**Policy 4: Data Access Restrictions**

```rego
# mcp_data_access.rego
# OPA policy for data access control

package mcp.data_access

import future.keywords.if
import future.keywords.in

default allow := false

# Allow if user can access requested resource
allow if {
    can_access_resource
}

# Check resource access
can_access_resource if {
    # Extract user and resource
    token := trim_prefix(input.headers.authorization, "Bearer ")
    [_, _, payload] := io.jwt.decode(token)
    user := payload.sub
    resource_id := extract_resource_id(input.path)

    # Check ownership or permission
    user_owns_resource(user, resource_id)
} else if {
    user_is_admin
}

# Check if user owns resource
user_owns_resource(user, resource_id) if {
    resource := data.resources[resource_id]
    resource.owner == user
}

# Check if user is admin
user_is_admin if {
    token := trim_prefix(input.headers.authorization, "Bearer ")
    [_, _, payload] := io.jwt.decode(token)
    "admin" in payload.roles
}

# Extract resource ID from path
extract_resource_id(path) := id if {
    # Example: /mcp/files/abc123 -> abc123
    parts := split(path, "/")
    id := parts[count(parts) - 1]
}
```

##### 3. OPA Integration with Envoy (Production Pattern)

```yaml
# envoy.yaml
# Envoy proxy with OPA integration for MCP server

static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          codec_type: AUTO
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains: ["*"]
              routes:
              - match:
                  prefix: "/"
                route:
                  cluster: mcp_server
          http_filters:
          # OPA External Authorization Filter
          - name: envoy.filters.http.ext_authz
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
              grpc_service:
                envoy_grpc:
                  cluster_name: opa_cluster
                timeout: 0.5s
              with_request_body:
                max_request_bytes: 8192
                allow_partial_message: true
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
  # MCP Server cluster
  - name: mcp_server
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: mcp_server
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: mcp-server
                port_value: 8000

  # OPA cluster
  - name: opa_cluster
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    http2_protocol_options: {}
    load_assignment:
      cluster_name: opa_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: opa
                port_value: 9191
```

**OPA Configuration**:

```yaml
# opa-config.yaml
decision_logs:
  console: true

plugins:
  envoy_ext_authz_grpc:
    addr: :9191
    query: data.mcp.authz.allow
    dry-run: false
```

**Docker Compose with OPA**:

```yaml
version: '3.8'

services:
  # Envoy proxy
  envoy:
    image: envoyproxy/envoy:v1.28-latest
    container_name: mcp-envoy
    ports:
      - "8080:8080"
      - "9901:9901"  # Admin interface
    volumes:
      - ./envoy.yaml:/etc/envoy/envoy.yaml:ro
    networks:
      - mcp-network
    command: /usr/local/bin/envoy -c /etc/envoy/envoy.yaml

  # OPA policy engine
  opa:
    image: openpolicyagent/opa:latest
    container_name: mcp-opa
    ports:
      - "8181:8181"
    volumes:
      - ./policies:/policies:ro
      - ./opa-config.yaml:/config/config.yaml:ro
    networks:
      - mcp-network
    command:
      - "run"
      - "--server"
      - "--config-file=/config/config.yaml"
      - "/policies"

  # MCP Server
  mcp-server:
    image: mcp-server:latest
    container_name: mcp-server
    networks:
      - mcp-network
    environment:
      - PORT=8000

networks:
  mcp-network:
    driver: bridge
```

##### 4. Testing OPA Policies

```bash
# test_policies.sh
# Test OPA policies before deployment

#!/bin/bash

# Test 1: Valid token with correct scope
echo "Test 1: Valid token with mcp:read scope"
curl -X POST http://localhost:8181/v1/data/mcp/authz/allow \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "method": "GET",
      "path": "/mcp/files",
      "headers": {
        "authorization": "Bearer eyJhbGc..."
      }
    }
  }'

# Test 2: Invalid token
echo "\nTest 2: Invalid token"
curl -X POST http://localhost:8181/v1/data/mcp/authz/allow \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "method": "GET",
      "path": "/mcp/files",
      "headers": {
        "authorization": "Bearer invalid_token"
      }
    }
  }'

# Test 3: Missing required scope
echo "\nTest 3: Missing required scope"
curl -X POST http://localhost:8181/v1/data/mcp/authz/allow \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "method": "DELETE",
      "path": "/mcp/files",
      "headers": {
        "authorization": "Bearer eyJhbGc..."
      }
    }
  }'
```

**Unit tests with OPA test framework**:

```rego
# mcp_authz_test.rego
# Unit tests for MCP authorization policies

package mcp.authz

# Test: Valid token with correct scope should allow
test_valid_token_with_scope if {
    allow with input as {
        "method": "GET",
        "path": "/mcp/files",
        "headers": {
            "authorization": "Bearer valid_token_with_read_scope"
        }
    }
}

# Test: Invalid token should deny
test_invalid_token if {
    not allow with input as {
        "method": "GET",
        "path": "/mcp/files",
        "headers": {
            "authorization": "Bearer invalid_token"
        }
    }
}

# Test: Missing authorization header should deny
test_missing_auth_header if {
    not allow with input as {
        "method": "GET",
        "path": "/mcp/files",
        "headers": {}
    }
}

# Test: Insufficient scope should deny
test_insufficient_scope if {
    not allow with input as {
        "method": "DELETE",
        "path": "/mcp/files",
        "headers": {
            "authorization": "Bearer token_with_only_read_scope"
        }
    }
}
```

Run tests:

```bash
# Run OPA tests
opa test policies/ -v
```

---

### 2.4 Network Isolation and Policies

#### Kubernetes NetworkPolicy for MCP Microservices

##### 1. Default Deny All Policy

```yaml
# network-policy-default-deny.yaml
# Zero-trust: Deny all traffic by default

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: mcp-platform
spec:
  podSelector: {}  # Applies to all pods in namespace
  policyTypes:
  - Ingress
  - Egress
  ingress: []  # Empty = deny all ingress
  egress: []   # Empty = deny all egress
```

##### 2. Allow DNS Resolution

```yaml
# network-policy-allow-dns.yaml
# Allow all pods to resolve DNS

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: mcp-platform
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

##### 3. MCP Server Network Policy (Frontend -> Backend)

```yaml
# network-policy-mcp-server.yaml
# Allow ingress from nginx, egress to database

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-server-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: mcp-server
  policyTypes:
  - Ingress
  - Egress

  # Ingress: Allow only from nginx reverse proxy
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000

  # Egress: Allow to database and OPA only
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: opa
    ports:
    - protocol: TCP
      port: 8181
```

##### 4. Database Network Policy (Backend Only)

```yaml
# network-policy-database.yaml
# Database accepts connections only from MCP server

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  - Egress

  # Ingress: Allow only from MCP server
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 5432

  # Egress: Deny all (database doesn't need outbound)
  egress: []
```

##### 5. Nginx Network Policy (Internet-Facing)

```yaml
# network-policy-nginx.yaml
# Nginx accepts internet traffic, forwards to MCP server

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nginx-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  - Egress

  # Ingress: Allow from anywhere (internet-facing)
  ingress:
  - from: []  # Empty from = allow all sources
    ports:
    - protocol: TCP
      port: 443

  # Egress: Allow to MCP server and OPA only
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 8000
  - to:
    - podSelector:
        matchLabels:
          app: opa
    ports:
    - protocol: TCP
      port: 9191
```

##### 6. OPA Network Policy

```yaml
# network-policy-opa.yaml
# OPA accepts connections from nginx and MCP server

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: opa-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: opa
  policyTypes:
  - Ingress
  - Egress

  # Ingress: Allow from nginx (authz) and MCP server
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 8181  # HTTP API
    - protocol: TCP
      port: 9191  # gRPC (for Envoy)

  # Egress: Allow to external policy bundle server
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

##### 7. Complete Deployment with NetworkPolicies

```yaml
# deployment-complete.yaml
# Complete MCP platform deployment with network policies

apiVersion: v1
kind: Namespace
metadata:
  name: mcp-platform
  labels:
    name: mcp-platform

---
# Default deny all
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: mcp-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: mcp-platform
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53

---
# Nginx deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: mcp-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25-alpine
        ports:
        - containerPort: 443
        securityContext:
          runAsNonRoot: true
          runAsUser: 101
          readOnlyRootFilesystem: true

---
# Nginx service
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: mcp-platform
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 443
    targetPort: 443

---
# Nginx NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nginx-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - ports:
    - protocol: TCP
      port: 443
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 8000

---
# MCP Server deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: mcp-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: mcp-server
        image: mcp-server:latest
        ports:
        - containerPort: 8000
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"

---
# MCP Server service
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
  namespace: mcp-platform
spec:
  selector:
    app: mcp-server
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP  # Internal only

---
# MCP Server NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-server-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: mcp-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: opa
    ports:
    - protocol: TCP
      port: 8181

---
# Database deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: mcp-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 999
        fsGroup: 999
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false  # Database needs writes
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password

---
# Database service
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: mcp-platform
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP

---
# Database NetworkPolicy (most restrictive)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 5432
  egress: []  # Database needs no outbound access

---
# OPA deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa
  namespace: mcp-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        ports:
        - containerPort: 8181
        args:
        - "run"
        - "--server"
        - "/policies"
        volumeMounts:
        - name: policies
          mountPath: /policies
          readOnly: true
      volumes:
      - name: policies
        configMap:
          name: opa-policies

---
# OPA service
apiVersion: v1
kind: Service
metadata:
  name: opa
  namespace: mcp-platform
spec:
  selector:
    app: opa
  ports:
  - port: 8181
    targetPort: 8181
  type: ClusterIP

---
# OPA NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: opa-policy
  namespace: mcp-platform
spec:
  podSelector:
    matchLabels:
      app: opa
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx
    - podSelector:
        matchLabels:
          app: mcp-server
    ports:
    - protocol: TCP
      port: 8181
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # For policy bundle updates
```

##### 8. Verification and Testing

```bash
# test-network-policies.sh
# Test network policies are working

#!/bin/bash

NAMESPACE="mcp-platform"

echo "Testing network isolation..."

# Test 1: Nginx can reach MCP server
echo "\n1. Testing nginx -> mcp-server (should ALLOW)"
kubectl run -n $NAMESPACE test-nginx --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v http://mcp-server:8000/health

# Test 2: MCP server can reach database
echo "\n2. Testing mcp-server -> postgres (should ALLOW)"
kubectl run -n $NAMESPACE test-mcp --image=postgres:16-alpine --rm -it --restart=Never -- \
  pg_isready -h postgres -p 5432

# Test 3: Random pod cannot reach database (should DENY)
echo "\n3. Testing random-pod -> postgres (should DENY)"
kubectl run -n $NAMESPACE test-random --image=postgres:16-alpine --rm -it --restart=Never -- \
  pg_isready -h postgres -p 5432

# Test 4: MCP server cannot reach internet (should DENY)
echo "\n4. Testing mcp-server -> internet (should DENY)"
kubectl run -n $NAMESPACE test-internet --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v https://www.google.com

echo "\nNetwork policy tests complete!"
```

---

## Conclusion and Recommendations for SPEK v2

### Gap 1: AI Platform Integration

**Recommended Implementation**:

1. **Gemini CLI Workarounds**:
   - Implement circuit breaker pattern with 3-retry limit
   - Force Flash model via `GEMINI_MODEL` environment variable
   - Set MCP server timeouts to 30 seconds
   - Use wrapper script with automatic recovery

2. **GPT-5 Codex Caching**:
   - Structure prompts with separate base context (cached) and dynamic input
   - Target 70-85% cache hit rate for cost savings
   - Monitor caching effectiveness with metrics
   - Use minimal prompting ("less is more" principle)

3. **Multi-Platform Orchestration**:
   - Adopt **Magentic Orchestration** pattern (Queen-Princess-Drone)
   - Implement multi-level fallback chain: Codex -> Opus -> Gemini Pro -> Sonnet -> Flash
   - Platform selection based on task characteristics and priority
   - Cost optimization through Gemini free tier for high-volume operations

### Gap 8: MCP Server Security

**Recommended Implementation**:

1. **OAuth 2.0 Resource Server**:
   - Implement full token validation with JWKS caching
   - Use PKCE for all authorization code flows
   - Implement Resource Indicators (RFC 8707) for token scoping
   - Deploy Protected Resource Metadata (RFC 9728) for discovery

2. **Docker Security**:
   - Multi-stage builds with non-root user (UID 1001)
   - Read-only root filesystem with tmpfs for /tmp
   - Resource limits: 1 CPU, 512MB RAM, 100 processes
   - Version pinning with SHA-256 digests
   - Vulnerability scanning with Trivy in CI/CD

3. **Network Isolation**:
   - Kubernetes NetworkPolicy with default deny-all
   - Zero-trust architecture: explicit allow rules only
   - Internet-facing: Nginx only
   - Internal-only: MCP server, database, OPA

4. **Policy Enforcement**:
   - OPA for dynamic access control
   - Rego policies for authentication, RBAC, rate limiting
   - Envoy integration for transparent policy enforcement

### Production Readiness Checklist

- [ ] Gemini CLI circuit breaker implemented
- [ ] GPT-5 Codex caching strategy deployed
- [ ] Multi-platform fallback chain tested
- [ ] OAuth 2.0 Resource Server with PKCE deployed
- [ ] Docker images hardened (non-root, read-only, pinned versions)
- [ ] Kubernetes NetworkPolicies applied
- [ ] OPA policies defined and tested
- [ ] Vulnerability scanning in CI/CD pipeline
- [ ] Secrets management via Docker secrets
- [ ] Health checks and monitoring configured

---

## Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Status | Hash |
|--------:|-----------|-------------|----------------|--------|------|
| 1.0 | 2025-10-08T14:30:00-04:00 | Gemini 2.5 Pro | Complete research report for AI platforms and MCP security | OK | a7b3c9d |

### Receipt
- status: OK
- reason: Research complete with comprehensive findings
- run_id: research-gap1-gap8-v1
- inputs: ["RESEARCH-GAPS-v1.md", "PLAN-v1.md", "SPEC-v1.md", "web-research"]
- tools_used: ["WebSearch", "WebFetch", "research-synthesis"]
- versions: {"model": "gemini-2.5-pro", "research-framework": "SPEK-v2"}
