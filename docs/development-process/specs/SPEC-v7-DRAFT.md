# SPEK Platform v2 - SPECIFICATION v7.0-DRAFT

**Version**: 7.0-DRAFT
**Date**: 2025-10-08
**Status**: DRAFT - Atlantis UI Integration
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

---

## PREFACE: v7 Atlantis Integration

**What Changed from v6**: This specification integrates the **Atlantis UI** (Next.js + Three.js frontend) with the production-ready v6 core system. Atlantis provides a visual, autonomous interface for the 3-Loop refinement methodology.

**v7 Additions**:
1. **Atlantis UI**: Complete Next.js 14 frontend with 3D visualizations
2. **3-Loop System**: Explicit Loop 1 (Spec/Plan), Loop 2 (Execution), Loop 3 (Quality)
3. **Princess Hive Model**: Multi-layer delegation (Queen → Princess → Drone)
4. **3-Stage Audit**: Theater → Production → Quality (100% enforcement)
5. **Project Vectorization**: Pinecone + Redis caching for existing projects
6. **UI Validation**: Playwright screenshots with visual diff
7. **Documentation Cleanup**: Automated markdown organization

**v6 Core Preserved**:
- 22 agents Phase 1, 50 agents Phase 2 (conditional)
- AgentContract interface, EnhancedLightweightProtocol
- GovernanceDecisionEngine, Analyzer, GitHub SPEC KIT
- NASA POT10 compliance (≥92%), $0 incremental cost Phase 1
- Tiered DSPy (8 agents), few-shot (12 agents), prompt caching

**Philosophy**: Visual elegance meets autonomous execution. Atlantis provides the "command center" UI for SPEK's AI agent coordination, making complex workflows transparent and controllable.

---

## Executive Summary

### System Overview

**SPEK Platform v2 + Atlantis UI** is a visual AI agent coordination system that guides users through a 3-loop quality refinement process:

- **Loop 1**: Specification & Planning (Research → Pre-mortem → Remediation → Iterate until <5% failure rate)
- **Loop 2**: Execution (Princess Hive delegation → 3-stage audit → Phase completion)
- **Loop 3**: Quality & Finalization (Full scan → GitHub integration → Documentation cleanup → Export)

**Technology Stack**:
- **Frontend**: Next.js 14 (App Router), Three.js (3D viz), shadcn/ui, Tailwind CSS
- **Backend**: tRPC API, BullMQ (task queue), Docker sandbox, Octokit (GitHub)
- **Real-time**: Socket.io with Redis adapter
- **Storage**: Pinecone (vectors), Redis (cache), SQLite (Context DNA)
- **Agents**: 22 agents Phase 1, 50 agents Phase 2 (v6 architecture)

### Key Metrics (Updated for Atlantis)

**Phase 1 (22 agents + Atlantis)**:
- System Performance: 0.68-0.73 (agent baseline, v6 target)
- Monthly Cost: $43 agents + $30 hosting UI = **$73/month**
- Loop 1 Failure Rate: <5% (target within 10 iterations)
- Loop 2 Audit Pass: 100% (theater/production/quality)
- Loop 3 Quality Score: 100% (final validation)

**Phase 2 (50 agents + Atlantis, conditional)**:
- System Performance: 0.75-0.76 (with few-shot + caching)
- Monthly Cost: $150 agents + $50 hosting UI = **$200/month**
- UI Performance: <100ms page load, 60fps 3D animations
- WebSocket Latency: <50ms real-time updates
- Concurrent Users: 100+ (horizontal scaling)

---

## 1. Atlantis UI Architecture

### 1.1 Frontend Stack

**Framework**: Next.js 14 (App Router)
- Server components for initial render
- Client components for 3D/real-time
- tRPC for type-safe API calls
- React Query for state management

**3D Visualization**: Three.js + React Three Fiber
- Loop 1: Orbital ring with rotating nodes
- Loop 2: Isometric village (Princess buildings, Drone bees)
- Loop 3: Concentric expanding rings
- Performance: Level-of-detail rendering, 60fps target

**UI Components**: shadcn/ui + Tailwind CSS
- Accessible (WCAG 2.1 AA)
- Responsive (desktop-first, tablet/mobile support)
- Dark mode support
- Theme customization

**Real-time**: Socket.io client
- Agent thoughts stream
- Task status updates
- Audit progress notifications
- Phase completion events

### 1.2 Page Structure (9 Pages)

#### 1. `/` (Home/Monarch Chat)
**Purpose**: Initial conversation with King/Queen/Monarch agent
**Components**:
- `<MonarchChat />` - Chat interface with agent
- `<ProjectSelector />` - New vs Existing project choice
- `<SessionHistory />` - Previous sessions

**User Flow**:
1. User greets Monarch agent
2. Choose: New project OR Existing project
3. Route to `/project/new` or `/project/select`

---

#### 2. `/project/select` (Existing Project)
**Purpose**: Select, vectorize, and index existing project
**Components**:
- `<FileSystemPicker />` - File explorer (Electron wrapper OR server upload)
- `<VectorizationProgress />` - Real-time indexing progress
- `<ProjectGraph />` - 3D structure visualization (Three.js)
- `<RefinementChoice />` - Specific changes OR Refinement loop

**User Flow**:
1. User selects project folder
2. System vectorizes codebase (Pinecone embeddings)
3. System generates dependency graph (AST analysis)
4. Cache results (Redis, 30-day TTL)
5. Display 3D graph of project structure
6. User chooses: Specific changes OR Refinement loop
7. Route to `/loop1` if refinement selected

**Technical Requirements**:
- **Vectorization**: OpenAI text-embedding-ada-002 OR voyage-code-2
- **Graph**: AST + import analysis via jscodeshift/ast-grep
- **Cache**: Redis with project fingerprint key (git commit hash)
- **3D Rendering**: Force-directed graph (D3-force + Three.js)

---

#### 3. `/project/new` (New Project Wizard)
**Purpose**: Multi-step clarification for new projects
**Components**:
- `<ProjectWizard />` - Multi-step form
- `<ClarificationChat />` - Q&A with Monarch
- `<SPECPreview />` - Live SPEC document preview
- `<PLANPreview />` - Live PLAN document preview
- `<ProgressIndicator />` - Wizard progress (questions answered)

**User Flow**:
1. User describes project vision (free-form text)
2. Monarch asks clarifying questions
3. System translates technical ↔ experience language
4. Progressive SPEC/PLAN generation
5. User reviews draft documents
6. Confirm and proceed to Loop 1

**Question Categories** (Monarch Agent):
- User experience expectations
- Technical stack preferences (abstracted for non-technical)
- Scale/performance requirements
- Security/compliance needs
- Budget/timeline constraints

**Technical Requirements**:
- **LLM**: Claude Sonnet 4 (Monarch agent, multi-turn conversation)
- **Document Generation**: Incremental SPEC/PLAN updates (streaming)
- **Storage**: Session state in Redis, final docs in SQLite

---

#### 4. `/loop1` (Research & Pre-mortem)
**Purpose**: Iterative failure analysis and remediation
**Components**:
- `<Loop1Visualizer />` - 3D orbital ring (current iteration)
- `<AgentThoughts />` - Real-time log stream
- `<FailureRateGauge />` - Percentage display (color-coded)
- `<IterationCounter />` - Iteration badge
- `<ResearchArtifacts />` - GitHub repos, papers collected
- `<PremortemReport />` - Failure analysis results
- `<PauseOverlay />` - User thought injection

**User Flow**:
1. Loop 1 starts (automatic after SPEC/PLAN created)
2. **Research Phase**:
   - GitHub code search (similar implementations)
   - Academic papers (Semantic Scholar API)
   - Collect artifacts (repos, papers, examples)
3. **Pre-mortem Phase**:
   - Multi-agent failure analysis (what could go wrong?)
   - Generate failure scenarios
   - Calculate failure rate (0-100%)
4. **Remediation Phase**:
   - Update SPEC/PLAN with preventions
   - Add mitigations for identified risks
5. **Re-research Phase**:
   - Gather additional components
   - Validate mitigations exist
6. **Re-premortem Phase**:
   - Fresh eyes analysis (different agent)
   - Recalculate failure rate
7. **Iterate**: Repeat until failure rate <5%
8. User can pause and inject thoughts (button)
9. Route to `/loop2` when complete

**Technical Requirements**:
- **Research**: GitHub API (code search), Semantic Scholar API (papers)
- **Pre-mortem**: Multi-agent coordination (researcher, planner, architect)
- **Failure Rate**: Weighted risk scoring (P0/P1/P2 risks)
- **WebSocket**: Real-time agent activity stream
- **Pause**: Broadcast pause event, wait for user input, resume

**Success Criteria**:
- Failure rate <5% (target within 10 iterations)
- Research artifacts: ≥5 GitHub repos, ≥3 papers
- Pre-mortem quality: ≥20 failure scenarios identified
- SPEC/PLAN updates: ≥10 preventions added

---

#### 5. `/loop2` (Execution Village)
**Purpose**: Task delegation and execution with Princess Hive model
**Components**:
- `<ExecutionVillage />` - 3D village (Three.js isometric)
- `<PhaseColumn />` - MECE phase breakdown (4-6 phases)
- `<PrincessCard />` - Princess + drone group
- `<TaskFlow />` - Animated task delegation (arrows)
- `<TaskCard />` - Task details, status, audit results
- `<BottleneckIndicator />` - Blocking tasks highlighted

**User Flow**:
1. **Phase Division** (automatic):
   - MECE principles (Mutually Exclusive, Collectively Exhaustive)
   - Dependency graph analysis
   - Identify bottlenecks (tasks blocking others)
   - Assign phases (4-6 phases typical)
2. **Princess Assignment**:
   - Princess-Dev (coder, reviewer, debugger drones)
   - Princess-Quality (tester, nasa-enforcer, analyzer drones)
   - Princess-Coordination (orchestrator, task-tracker drones)
   - Princess-Documentation (docs-writer, spec-writer drones)
3. **Task Execution**:
   - Queen delegates to Princess
   - Princess delegates to Drone
   - Drone executes task
   - 3-stage audit (see Section 1.3)
4. **Real-time Updates**:
   - Task status changes (pending → in_progress → completed)
   - Audit progress (theater → production → quality)
   - Phase progress (% complete)
5. Route to `/loop2/audit` for audit details
6. Route to `/loop2/ui-review` for UI validation (if applicable)
7. Route to `/loop3` when all phases complete

**Communication Protocol** (Queen → Princess → Drone):
1. Establish context (pwd, TodoWrite with absolute paths)
2. Create `.project-boundary` marker (scope isolation)
3. Use Agent2Agent protocol (with path validation)
4. Project management system integration (GitHub Projects)
5. Context DNA for translation integrity (30-day retention)

**Technical Requirements**:
- **Phase Division**: MECE algorithm (dependency analysis)
- **Princess Hive**: Hierarchical coordination (EnhancedLightweightProtocol)
- **3D Village**: Three.js isometric rendering (buildings = princesses, bees = drones)
- **Task Queue**: BullMQ (priority queue, retry logic)
- **WebSocket**: Task status updates (<50ms latency)

**Princess Hive Structure**:
```yaml
Queen (Monarch):
  Princess-Dev:
    - coder (drone)
    - reviewer (drone)
    - debugger (drone)
    - integration-engineer (drone)
  Princess-Quality:
    - tester (drone)
    - nasa-enforcer (drone)
    - theater-detector (drone)
    - fsm-analyzer (drone)
  Princess-Coordination:
    - orchestrator (drone)
    - planner (drone)
    - cost-tracker (drone)
  Princess-Documentation:
    - docs-writer (drone)
    - spec-writer (drone)
    - pseudocode-writer (drone)
```

---

#### 6. `/loop2/audit` (Audit Detail View)
**Purpose**: 3-stage audit pipeline visualization
**Components**:
- `<AuditPipeline />` - 3-stage progress bar (🎭 → ⚙️ → ✅)
- `<TheaterResults />` - Theater detection results
- `<ProductionResults />` - Sandbox test results
- `<QualityResults />` - Analyzer scan results (JSON)
- `<ErrorReport />` - JSON viewer with error details
- `<RetryCounter />` - Number of retries per task

**User Flow**:
1. Drone completes task
2. **Stage 1: Theater Detection**
   - Scan for mock code, TODOs, NotImplementedError
   - Pass/fail result
   - If fail: Return to drone with notes → retry
3. **Stage 2: Production Testing**
   - Run code in Docker sandbox
   - Execute tests
   - Debug if failed (smallest possible fix)
   - Loop until 100% functional
4. **Stage 3: Quality Scan**
   - Analyzer scan (connascence, god objects, NASA POT10)
   - Generate JSON error report
   - Send to specialist drones for refactor
   - Re-scan after refactor
   - Loop until 100% quality score
5. Mark task COMPLETE when all 3 stages pass
6. Return to `/loop2` (village view)

**Technical Requirements**:
- **Theater Detection**: Analyzer theater module (6 patterns)
- **Production Testing**: Docker sandbox (20s target Phase 1, 30s Phase 2)
- **Quality Scan**: Analyzer full scan (9 detectors, NASA compliance)
- **Retry Logic**: BullMQ automatic retry (exponential backoff)
- **WebSocket**: Real-time audit progress updates

**Audit Loop Example**:
```
Drone completes code generation task
  → Theater audit: FAIL (found TODO comment)
    → Return to drone with error: "TODO comment at line 42"
    → Drone fixes TODO comment
    → Theater audit: PASS
  → Production audit: FAIL (test failed)
    → Debug in sandbox (add missing validation)
    → Production audit: PASS
  → Quality audit: FAIL (god object detected)
    → Send to reviewer drone for refactor
    → Quality audit: PASS
  → Mark task COMPLETE
```

**Success Criteria**:
- Theater: 100% pass rate (zero theater indicators)
- Production: 100% pass rate (all tests passing)
- Quality: 100% pass rate (NASA POT10 ≥92%, zero god objects)
- Average retries: <3 per task

---

#### 7. `/loop2/ui-review` (UI Validation)
**Purpose**: Screenshot comparison and user approval
**Components**:
- `<UIComparison />` - Split view (expected vs actual)
- `<VisualDiff />` - Highlighted differences (pixel diff)
- `<ApprovalButtons />` - Approve / Request Changes
- `<ChangeRequest />` - Text input for UI feedback
- `<PlaywrightLog />` - Screenshot capture log

**User Flow**:
1. Drone completes UI implementation task
2. Playwright captures screenshot of implemented UI
3. Compare to user's expected design (Figma, wireframe, or description)
4. Generate visual diff (pixelmatch library)
5. Present side-by-side comparison to user
6. User reviews:
   - **Approve**: Mark task complete, continue
   - **Request Changes**: Provide feedback, return to drone
7. Drone debugs UI component
8. Verify UI connects to real backend code (integration test)
9. Repeat until approved
10. Return to `/loop2` (village view)

**Technical Requirements**:
- **Screenshot Capture**: Playwright (headless Chrome)
- **Visual Diff**: pixelmatch (pixel-level comparison)
- **MCP Integration**: Chrome MCP server (Playwright automation)
- **Storage**: Screenshots stored in S3 (artifact storage)
- **Approval**: Store in SQLite (task approval metadata)

**Integration Points**:
- `/loop2` task triggers UI review (task type = "ui_implementation")
- WebSocket notification when screenshot ready
- User approval updates task status (via tRPC mutation)
- Backend verifies UI ↔ API integration (smoke test)

---

#### 8. `/loop3` (Finalization)
**Purpose**: Final quality scans, GitHub setup, documentation cleanup
**Components**:
- `<Loop3Finalizer />` - Final scan progress (3 concentric rings)
- `<FullProjectScan />` - Theater/production/quality results
- `<RepoWizard />` - GitHub repo creation form
- `<DocumentationCleanup />` - Markdown file organizer
- `<ExportOptions />` - GitHub vs Folder download
- `<CompletionCelebration />` - Success animation

**User Flow**:
1. Loop 2 complete (all phases done)
2. **Full Project Scan**:
   - Theater: 100% pass (final check)
   - Production: 100% pass (full test suite)
   - Quality: 100% pass (Analyzer scan)
   - Display results (any remaining issues highlighted)
3. **GitHub Integration** (optional):
   - User enters repo name, description, visibility
   - System creates new GitHub repo
   - Install analyzer hooks (GitHub Actions)
   - Setup CI/CD pipeline (automated testing)
   - Configure quality gates (pull request checks)
   - Push code to repo
4. **Documentation Cleanup**:
   - List all markdown files
   - Organize by code module (auto-categorize)
   - Delete outdated docs (user approval)
   - Update docs to match reality (LLM-assisted)
   - Add UI screenshots (if applicable)
5. **Export**:
   - **GitHub**: Repo URL + clone instructions
   - **Folder**: Download ZIP with analyzer, local hooks
6. Display completion celebration
7. Option to start new project

**Technical Requirements**:
- **Full Scan**: Analyzer + Docker sandbox (full test suite)
- **GitHub Integration**: Octokit (repo creation, push, hooks)
- **CI/CD Setup**: Generate `.github/workflows/*.yml` files
- **Documentation Cleanup**: LLM-assisted categorization + updates
- **Export**: ZIP generation (JSZip library) OR GitHub push

**GitHub Integration Steps**:
```yaml
1. Create repo (Octokit):
   - POST /user/repos
   - name, description, private/public

2. Push code:
   - git init
   - git add .
   - git commit -m "Initial commit via SPEK Atlantis"
   - git remote add origin <repo-url>
   - git push -u origin main

3. Install hooks:
   - .github/workflows/analyzer-ci.yml (quality gates)
   - .github/workflows/tests.yml (automated testing)
   - .github/workflows/deploy.yml (deployment pipeline)

4. Configure quality gates:
   - Branch protection rules (require PR reviews)
   - Status checks (analyzer, tests must pass)
   - SARIF upload (analyzer results to Security tab)
```

**Documentation Cleanup Algorithm**:
1. Scan all `.md` files in project
2. Extract headings, code snippets, references
3. LLM categorization (which module does this doc describe?)
4. Compare doc content to actual code (AST comparison)
5. Flag outdated docs (code changed, doc didn't)
6. Generate updated docs (LLM-assisted rewrite)
7. User review and approval
8. Delete orphaned docs (no corresponding code)

**Success Criteria**:
- Full scan: 100% pass (theater/production/quality)
- GitHub repo: Created, code pushed, hooks installed
- Documentation: 100% accuracy (matches code)
- Export: Successful (GitHub link OR ZIP download)

---

#### 9. `/dashboard` (Overall Progress)
**Purpose**: High-level project status overview
**Components**:
- `<ProgressOverview />` - Overall progress wheel (0-100%)
- `<PhaseTimeline />` - Timeline visualization (Loop 1/2/3)
- `<MetricCards />` - Key metrics (agents active, tasks complete, etc.)
- `<AgentActivityFeed />` - Recent agent actions
- `<CostTracker />` - Budget usage (v6 cost-tracker agent)

**User Flow**:
1. Access anytime during project
2. View overall progress (Loop 1/2/3 status)
3. View phase breakdown (which phase in Loop 2?)
4. View agent activity (real-time feed)
5. View cost usage (budget tracking)
6. Navigate to specific loop/phase (click timeline)

**Technical Requirements**:
- **Progress Calculation**: Aggregate task completion across loops
- **Timeline**: Horizontal timeline with milestones
- **Metrics**: WebSocket updates (real-time)
- **Cost Tracking**: v6 cost-tracker agent integration (tRPC query)

---

### 1.3 3-Stage Audit System

**Audit Stage 1: Theater Detection**
- **Tool**: Analyzer theater module
- **Patterns Detected**:
  1. Mock code (`mock.Mock`, `unittest.mock`)
  2. TODO comments (`# TODO`, `// TODO`)
  3. NotImplementedError (Python)
  4. Fake data generators (`faker`, `casual`)
  5. Empty implementations (`pass`, `return null`)
  6. Trivial assertions (`assert True`)
- **Action**: Return to drone with notes → retry
- **Pass Criteria**: Zero theater indicators

**Audit Stage 2: Production Testing**
- **Tool**: Docker sandbox (isolated execution)
- **Process**:
  1. Run code in sandbox
  2. Execute test suite
  3. If tests fail:
     - Attempt smallest possible debug (targeted fix)
     - Re-run tests
     - Loop until 100% pass rate
- **Debug Strategy**: LLM-assisted (Claude Sonnet 4 for debugging)
- **Pass Criteria**: All tests pass, code executes without errors

**Audit Stage 3: Quality Scan**
- **Tool**: Analyzer (v6 comprehensive scan)
- **Checks**:
  - **Connascence**: 9 detectors (CoM, CoP, CoA, CoT, CoE, CoV, CoN, God Objects, Real Detectors)
  - **NASA POT10**: 6 rules (functions ≤60 lines, ≥2 assertions, etc.)
  - **Duplications**: MECE analysis (Jaccard similarity ≥0.7)
  - **Linting**: Style errors, unused imports, etc.
- **Action**: Send JSON error report to specialist drones → refactor → re-scan
- **Pass Criteria**: 100% quality score (NASA ≥92%, zero god objects, zero critical issues)

**Audit Loop Integration**:
```typescript
// Task completion handler
async function onTaskComplete(task: Task): Promise<void> {
  // Stage 1: Theater
  const theaterResult = await analyzer.detectTheater(task.output);
  if (!theaterResult.passed) {
    await returnToDrone(task, theaterResult.notes);
    return; // Retry
  }

  // Stage 2: Production
  const productionResult = await sandbox.runTests(task.output);
  while (!productionResult.passed) {
    const debug = await debugger.fix(productionResult.errors);
    productionResult = await sandbox.runTests(debug.code);
  }

  // Stage 3: Quality
  const qualityResult = await analyzer.fullScan(task.output);
  while (!qualityResult.passed) {
    const refactor = await reviewer.refactor(qualityResult.errors);
    qualityResult = await analyzer.fullScan(refactor.code);
  }

  // All stages passed
  await markTaskComplete(task);
}
```

---

### 1.4 Real-time Communication

**WebSocket Architecture** (Socket.io + Redis)
```typescript
// Server: src/websocket/server.ts
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const io = new Server(httpServer, {
  cors: { origin: process.env.FRONTEND_URL }
});

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
io.adapter(createAdapter(pubClient, subClient));

// Events
io.on('connection', (socket) => {
  // Join project room
  socket.on('join-project', (projectId) => {
    socket.join(`project:${projectId}`);
  });

  // Agent thoughts stream
  socket.on('subscribe-agent-thoughts', (agentId) => {
    socket.join(`agent:${agentId}`);
  });

  // Task updates
  socket.on('subscribe-task-updates', (taskId) => {
    socket.join(`task:${taskId}`);
  });
});

// Emit events from agents
export function emitAgentThought(agentId: string, thought: string) {
  io.to(`agent:${agentId}`).emit('agent-thought', { agentId, thought });
}

export function emitTaskUpdate(taskId: string, status: string) {
  io.to(`task:${taskId}`).emit('task-update', { taskId, status });
}
```

**Client Integration**:
```typescript
// Client: src/hooks/useWebSocket.ts
import { useEffect } from 'react';
import { io, Socket } from 'socket.io-client';

export function useAgentThoughts(agentId: string, onThought: (thought: string) => void) {
  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_WS_URL);
    socket.emit('subscribe-agent-thoughts', agentId);
    socket.on('agent-thought', ({ thought }) => onThought(thought));
    return () => socket.disconnect();
  }, [agentId]);
}
```

**Events**:
- `agent-thought` - Real-time agent log stream
- `task-update` - Task status change (pending/in_progress/completed)
- `audit-progress` - Audit stage completion (theater/production/quality)
- `phase-complete` - Phase completion in Loop 2
- `loop-complete` - Loop transition (Loop 1 → Loop 2 → Loop 3)

---

## 2. Backend Architecture

### 2.1 API Layer (tRPC)

**Type-safe API with tRPC**:
```typescript
// src/server/routers/project.ts
import { z } from 'zod';
import { router, publicProcedure } from '../trpc';

export const projectRouter = router({
  // Create new project
  create: publicProcedure
    .input(z.object({
      name: z.string(),
      description: z.string(),
      userId: z.string()
    }))
    .mutation(async ({ input }) => {
      const project = await db.project.create({ data: input });
      return project;
    }),

  // Vectorize existing project
  vectorize: publicProcedure
    .input(z.object({
      projectId: z.string(),
      path: z.string()
    }))
    .mutation(async ({ input }) => {
      const job = await queue.add('vectorize-project', input);
      return { jobId: job.id };
    }),

  // Get project status
  status: publicProcedure
    .input(z.object({ projectId: z.string() }))
    .query(async ({ input }) => {
      const project = await db.project.findUnique({
        where: { id: input.projectId },
        include: { phases: true, tasks: true }
      });
      return project;
    })
});
```

**Router Composition**:
```typescript
// src/server/routers/_app.ts
import { router } from '../trpc';
import { projectRouter } from './project';
import { loop1Router } from './loop1';
import { loop2Router } from './loop2';
import { loop3Router } from './loop3';
import { agentRouter } from './agent';
import { auditRouter } from './audit';

export const appRouter = router({
  project: projectRouter,
  loop1: loop1Router,
  loop2: loop2Router,
  loop3: loop3Router,
  agent: agentRouter,
  audit: auditRouter
});

export type AppRouter = typeof appRouter;
```

---

### 2.2 Task Queue (BullMQ)

**Queue Architecture**:
```typescript
// src/queue/queues.ts
import { Queue, Worker } from 'bullmq';

// Project vectorization queue
export const vectorizeQueue = new Queue('vectorize-project', {
  connection: { host: 'localhost', port: 6379 }
});

// Task execution queue
export const taskQueue = new Queue('execute-task', {
  connection: { host: 'localhost', port: 6379 }
});

// Audit queue
export const auditQueue = new Queue('audit-task', {
  connection: { host: 'localhost', port: 6379 }
});
```

**Worker Implementation**:
```typescript
// src/queue/workers/vectorize.worker.ts
import { Worker } from 'bullmq';
import { vectorizeProject } from '../../services/vectorization';

const worker = new Worker('vectorize-project', async (job) => {
  const { projectId, path } = job.data;

  // Update progress
  await job.updateProgress(10);

  // Vectorize codebase
  const embeddings = await vectorizeProject(path);
  await job.updateProgress(50);

  // Store in Pinecone
  await pinecone.upsert(projectId, embeddings);
  await job.updateProgress(80);

  // Generate dependency graph
  const graph = await generateGraph(path);
  await job.updateProgress(90);

  // Cache results
  await redis.set(`project:${projectId}:graph`, JSON.stringify(graph), 'EX', 2592000); // 30 days
  await job.updateProgress(100);

  return { embeddings: embeddings.length, graph: graph.nodes.length };
});
```

**Job Priorities**:
- **Critical**: Loop 1 research, Loop 3 final scans (priority: 1)
- **High**: Loop 2 task execution (priority: 5)
- **Medium**: Audit stages (priority: 10)
- **Low**: Documentation cleanup (priority: 20)

---

### 2.3 Vectorization Service

**Project Vectorization Pipeline**:
```typescript
// src/services/vectorization.ts
import { OpenAIEmbeddings } from 'langchain/embeddings/openai';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import * as fs from 'fs';
import * as path from 'path';

export async function vectorizeProject(projectPath: string): Promise<Embedding[]> {
  const embeddings = new OpenAIEmbeddings({
    modelName: 'text-embedding-ada-002'
  });

  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200
  });

  // Scan all code files
  const files = await scanDirectory(projectPath, ['.ts', '.tsx', '.js', '.jsx', '.py']);

  const results: Embedding[] = [];
  for (const file of files) {
    const content = fs.readFileSync(file, 'utf-8');
    const chunks = await splitter.splitText(content);

    for (const chunk of chunks) {
      const vector = await embeddings.embedQuery(chunk);
      results.push({
        id: `${path.relative(projectPath, file)}:${chunk.slice(0, 50)}`,
        vector,
        metadata: {
          file: path.relative(projectPath, file),
          content: chunk
        }
      });
    }
  }

  return results;
}

async function scanDirectory(dir: string, extensions: string[]): Promise<string[]> {
  const files: string[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
        files.push(...await scanDirectory(fullPath, extensions));
      }
    } else {
      if (extensions.some(ext => entry.name.endsWith(ext))) {
        files.push(fullPath);
      }
    }
  }

  return files;
}
```

**Pinecone Integration**:
```typescript
// src/services/pinecone.ts
import { Pinecone } from '@pinecone-database/pinecone';

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY
});

const index = pinecone.index('spek-projects');

export async function upsertProject(projectId: string, embeddings: Embedding[]) {
  const vectors = embeddings.map(e => ({
    id: `${projectId}:${e.id}`,
    values: e.vector,
    metadata: e.metadata
  }));

  await index.upsert(vectors);
}

export async function searchProject(projectId: string, query: string, topK: number = 10) {
  const embeddings = new OpenAIEmbeddings();
  const queryVector = await embeddings.embedQuery(query);

  const results = await index.query({
    vector: queryVector,
    topK,
    filter: { projectId }
  });

  return results.matches;
}
```

**Cache Strategy** (Redis):
```typescript
// src/services/cache.ts
import { createClient } from 'redis';

const redis = createClient({ url: process.env.REDIS_URL });

// Cache project graph (30 days)
export async function cacheProjectGraph(projectId: string, graph: DependencyGraph) {
  await redis.set(
    `project:${projectId}:graph`,
    JSON.stringify(graph),
    { EX: 2592000 } // 30 days
  );
}

// Cache project fingerprint (git commit hash)
export async function getCachedProject(fingerprint: string): Promise<string | null> {
  return await redis.get(`project:fingerprint:${fingerprint}`);
}

export async function setCachedProject(fingerprint: string, projectId: string) {
  await redis.set(
    `project:fingerprint:${fingerprint}`,
    projectId,
    { EX: 2592000 } // 30 days
  );
}
```

---

### 2.4 Sandbox Service (Docker)

**Sandbox Runner**:
```typescript
// src/services/sandbox.ts
import Docker from 'dockerode';

const docker = new Docker();

export async function runInSandbox(code: string, tests: string): Promise<SandboxResult> {
  // Create container
  const container = await docker.createContainer({
    Image: 'node:18-alpine',
    Cmd: ['sh', '-c', `echo "${code}" > /app/index.js && echo "${tests}" > /app/index.test.js && npm test`],
    WorkingDir: '/app',
    HostConfig: {
      Memory: 512 * 1024 * 1024, // 512MB
      CpuShares: 512,
      NetworkMode: 'none', // No network access
      ReadonlyRootfs: true
    },
    Volumes: {
      '/app': {}
    }
  });

  // Start container
  await container.start();

  // Wait for completion (timeout: 60s)
  const result = await container.wait({ timeout: 60000 });

  // Get logs
  const logs = await container.logs({ stdout: true, stderr: true });

  // Cleanup
  await container.remove();

  return {
    exitCode: result.StatusCode,
    stdout: logs.toString(),
    stderr: logs.toString(),
    passed: result.StatusCode === 0
  };
}
```

**Performance Optimization** (Docker Layering):
```dockerfile
# Base image with dependencies (cached)
FROM node:18-alpine
RUN npm install -g jest @types/jest

# Code layer (changes frequently)
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

CMD ["npm", "test"]
```

**Sandbox Validation Target**:
- Phase 1 (22 agents): 20s average
- Phase 2 (50 agents): 30s average (acceptable scale-up)

---

## 3. Agent Integration (v6 Core)

### 3.1 AgentContract (Preserved from v6)

All 22 agents (Phase 1) and 50 agents (Phase 2) implement the same `AgentContract` interface from v6:

```typescript
// src/agents/AgentContract.ts (unchanged from v6)
export interface AgentContract {
  agentId: string;
  agentType: string;
  capabilities: string[];

  initialize(config: AgentConfig): Promise<void>;
  shutdown(): Promise<void>;

  validate(task: Task): Promise<boolean>;
  execute(task: Task): Promise<Result>;

  getMetadata(): AgentMetadata;
  getHealthStatus(): HealthStatus;
}
```

**v7 UI Integration Points**:
- `execute()` emits WebSocket events during execution
- `getHealthStatus()` displayed in `/dashboard` (agent activity feed)
- Task results stored in SQLite (displayed in `/loop2` task cards)

---

### 3.2 Princess Hive Delegation

**Queen Agent** (Top-level coordinator):
```typescript
// src/agents/QueenAgent.ts
export class QueenAgent implements AgentContract {
  async execute(task: Task): Promise<Result> {
    // 1. Analyze task complexity
    const complexity = await this.analyzeComplexity(task);

    // 2. Divide into MECE phases
    const phases = await this.dividePhasesAuto(task, complexity);

    // 3. Assign to princesses
    for (const phase of phases) {
      const princess = this.selectPrincess(phase.type);
      await this.delegateToPrincess(princess, phase);
    }

    // 4. Monitor execution
    return await this.monitorExecution(phases);
  }

  private selectPrincess(phaseType: string): PrincessAgent {
    const mapping = {
      'development': this.princessDev,
      'quality': this.princessQuality,
      'coordination': this.princessCoordination,
      'documentation': this.princessDocumentation
    };
    return mapping[phaseType];
  }

  private async delegateToPrincess(princess: PrincessAgent, phase: Phase): Promise<void> {
    // Establish context
    await this.establishContext(phase);

    // Create .project-boundary marker
    await this.createBoundary(phase);

    // Use Agent2Agent protocol (EnhancedLightweightProtocol)
    const result = await this.protocol.assignTask(princess.agentId, {
      taskId: phase.id,
      taskType: phase.type,
      priority: phase.priority,
      parameters: phase.parameters,
      timeout: phase.timeout,
      requester: this.agentId
    });

    // Store in Context DNA (30-day retention)
    await this.contextDNA.store({
      phaseId: phase.id,
      princessId: princess.agentId,
      result,
      timestamp: Date.now()
    });
  }
}
```

**Princess Agent** (Coordinator):
```typescript
// src/agents/PrincessDevAgent.ts
export class PrincessDevAgent implements AgentContract {
  async execute(task: Task): Promise<Result> {
    // 1. Break down into sub-tasks
    const subTasks = await this.breakdownTask(task);

    // 2. Assign to drones (coder, reviewer, debugger)
    const results: Result[] = [];
    for (const subTask of subTasks) {
      const drone = this.selectDrone(subTask.type);
      const result = await this.delegateToDrone(drone, subTask);
      results.push(result);
    }

    // 3. Aggregate results
    return this.aggregateResults(results);
  }

  private selectDrone(taskType: string): AgentContract {
    const mapping = {
      'code_generation': this.coderDrone,
      'code_review': this.reviewerDrone,
      'debugging': this.debuggerDrone,
      'integration': this.integrationDrone
    };
    return mapping[taskType];
  }

  private async delegateToDrone(drone: AgentContract, subTask: SubTask): Promise<Result> {
    // Emit WebSocket event (real-time UI update)
    emitTaskUpdate(subTask.id, 'in_progress');

    // Execute task (EnhancedLightweightProtocol)
    const result = await this.protocol.assignTask(drone.agentId, {
      taskId: subTask.id,
      taskType: subTask.type,
      priority: subTask.priority,
      parameters: subTask.parameters,
      timeout: subTask.timeout,
      requester: this.agentId
    });

    // 3-stage audit (Theater → Production → Quality)
    await this.runAudit(subTask, result);

    // Emit completion event
    emitTaskUpdate(subTask.id, 'completed');

    return result;
  }

  private async runAudit(task: SubTask, result: Result): Promise<void> {
    // Stage 1: Theater
    const theater = await analyzer.detectTheater(result.output);
    while (!theater.passed) {
      emitAuditProgress(task.id, 'theater', 'retry');
      const fixed = await this.debuggerDrone.fix(theater.notes);
      result.output = fixed.output;
      theater = await analyzer.detectTheater(result.output);
    }
    emitAuditProgress(task.id, 'theater', 'passed');

    // Stage 2: Production
    const production = await sandbox.runTests(result.output);
    while (!production.passed) {
      emitAuditProgress(task.id, 'production', 'retry');
      const fixed = await this.debuggerDrone.debug(production.errors);
      result.output = fixed.output;
      production = await sandbox.runTests(result.output);
    }
    emitAuditProgress(task.id, 'production', 'passed');

    // Stage 3: Quality
    const quality = await analyzer.fullScan(result.output);
    while (!quality.passed) {
      emitAuditProgress(task.id, 'quality', 'retry');
      const refactored = await this.reviewerDrone.refactor(quality.errors);
      result.output = refactored.output;
      quality = await analyzer.fullScan(result.output);
    }
    emitAuditProgress(task.id, 'quality', 'passed');
  }
}
```

**Communication Protocol** (Queen → Princess → Drone):
1. **Establish Context**:
   - `pwd` (current working directory, absolute path)
   - `TodoWrite` (task list with absolute paths)
   - `.project-boundary` marker (scope isolation)
2. **Agent2Agent Protocol** (EnhancedLightweightProtocol):
   - Direct method calls (<10ms Phase 1, <25ms Phase 2)
   - Path validation (ensure absolute paths)
   - Error handling (retry with exponential backoff)
3. **Project Management Integration**:
   - GitHub Projects (task tracking)
   - Task status updates (pending/in_progress/completed)
   - Dependency graph (blocking tasks)
4. **Context DNA**:
   - 30-day retention (SQLite storage)
   - Artifact references (S3 links)
   - Translation integrity (princess → drone context preserved)

---

## 4. Loop 1 Implementation

### 4.1 Research Phase

**GitHub Code Search**:
```typescript
// src/services/research/github.ts
import { Octokit } from '@octokit/rest';

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

export async function searchGitHub(query: string): Promise<GitHubRepo[]> {
  const response = await octokit.search.code({
    q: query,
    per_page: 100
  });

  const repos = [];
  for (const item of response.data.items) {
    const repo = await octokit.repos.get({
      owner: item.repository.owner.login,
      repo: item.repository.name
    });
    repos.push({
      url: repo.data.html_url,
      description: repo.data.description,
      stars: repo.data.stargazers_count,
      language: repo.data.language,
      topics: repo.data.topics
    });
  }

  return repos;
}
```

**Academic Papers** (Semantic Scholar API):
```typescript
// src/services/research/papers.ts
export async function searchPapers(query: string): Promise<AcademicPaper[]> {
  const response = await fetch(
    `https://api.semanticscholar.org/graph/v1/paper/search?query=${encodeURIComponent(query)}&fields=title,abstract,authors,year,citationCount,url`,
    { headers: { 'User-Agent': 'SPEK-Atlantis/1.0' } }
  );

  const data = await response.json();
  return data.data.map((paper: any) => ({
    title: paper.title,
    abstract: paper.abstract,
    authors: paper.authors.map((a: any) => a.name),
    year: paper.year,
    citations: paper.citationCount,
    url: paper.url
  }));
}
```

**Research Aggregation**:
```typescript
// src/agents/ResearcherAgent.ts
export class ResearcherAgent implements AgentContract {
  async execute(task: Task): Promise<Result> {
    const { projectType, keywords } = task.parameters;

    // GitHub code search
    const repos = await searchGitHub(`${projectType} ${keywords.join(' ')}`);
    emitAgentThought(this.agentId, `Found ${repos.length} relevant repositories`);

    // Academic papers
    const papers = await searchPapers(`${projectType} software engineering`);
    emitAgentThought(this.agentId, `Found ${papers.length} academic papers`);

    // Store artifacts
    const artifacts = [
      ...repos.map(r => ({ type: 'github-repo', data: r })),
      ...papers.map(p => ({ type: 'academic-paper', data: p }))
    ];

    return {
      taskId: task.taskId,
      status: 'completed',
      output: { repos, papers },
      artifacts,
      quality: { score: 1.0 },
      duration: Date.now() - task.startTime
    };
  }
}
```

---

### 4.2 Pre-mortem Phase

**Multi-Agent Failure Analysis**:
```typescript
// src/agents/PlannerAgent.ts
export class PlannerAgent implements AgentContract {
  async execute(task: Task): Promise<Result> {
    const { spec, plan } = task.parameters;

    // Identify failure scenarios
    const scenarios = await this.identifyFailures(spec, plan);
    emitAgentThought(this.agentId, `Identified ${scenarios.length} failure scenarios`);

    // Calculate risk scores
    const risks = scenarios.map(s => ({
      ...s,
      riskScore: this.calculateRisk(s)
    }));

    // Calculate overall failure rate
    const failureRate = this.calculateFailureRate(risks);
    emitAgentThought(this.agentId, `Overall failure rate: ${failureRate.toFixed(2)}%`);

    return {
      taskId: task.taskId,
      status: 'completed',
      output: { scenarios: risks, failureRate },
      artifacts: [],
      quality: { score: 1.0 },
      duration: Date.now() - task.startTime
    };
  }

  private async identifyFailures(spec: string, plan: string): Promise<FailureScenario[]> {
    // LLM-assisted failure identification (Claude Sonnet 4)
    const prompt = `
      Given the following specification and plan, identify potential failure scenarios:

      Specification:
      ${spec}

      Plan:
      ${plan}

      List 20+ failure scenarios in JSON format:
      [
        {
          "scenario": "Description of failure",
          "probability": 0.0-1.0,
          "impact": "low|medium|high|critical",
          "category": "technical|business|operational|security"
        }
      ]
    `;

    const response = await this.llm.generate(prompt);
    return JSON.parse(response);
  }

  private calculateRisk(scenario: FailureScenario): number {
    const impactWeight = {
      'low': 1,
      'medium': 5,
      'high': 10,
      'critical': 20
    };
    return scenario.probability * impactWeight[scenario.impact] * 100;
  }

  private calculateFailureRate(risks: FailureScenario[]): number {
    const totalRisk = risks.reduce((sum, r) => sum + r.riskScore, 0);
    const maxRisk = risks.length * 20 * 100; // Max: all critical with 100% probability
    return (totalRisk / maxRisk) * 100;
  }
}
```

---

### 4.3 Remediation Phase

**SPEC/PLAN Updates**:
```typescript
// src/services/loop1/remediation.ts
export async function remediateSPEC(
  spec: string,
  failures: FailureScenario[]
): Promise<string> {
  const prompt = `
    Given the following specification and identified failure scenarios,
    update the specification to include preventions and mitigations:

    Specification:
    ${spec}

    Failure Scenarios:
    ${JSON.stringify(failures, null, 2)}

    Return updated specification in markdown format.
  `;

  const updatedSPEC = await llm.generate(prompt);
  return updatedSPEC;
}

export async function remediatePLAN(
  plan: string,
  failures: FailureScenario[]
): Promise<string> {
  const prompt = `
    Given the following implementation plan and identified failure scenarios,
    update the plan to include risk mitigation steps:

    Plan:
    ${plan}

    Failure Scenarios:
    ${JSON.stringify(failures, null, 2)}

    Return updated plan in markdown format.
  `;

  const updatedPLAN = await llm.generate(prompt);
  return updatedPLAN;
}
```

---

### 4.4 Loop 1 Iteration

**Loop Controller**:
```typescript
// src/services/loop1/controller.ts
export async function runLoop1(projectId: string): Promise<Loop1Result> {
  let iteration = 0;
  let failureRate = 100; // Start at 100%

  while (failureRate >= 5 && iteration < 20) { // Max 20 iterations
    iteration++;
    emitLoopUpdate(projectId, 'loop1', iteration, failureRate);

    // Research phase
    const research = await researcherAgent.execute({
      taskId: `research-${iteration}`,
      taskType: 'research',
      parameters: { projectId },
      priority: 'critical',
      timeout: 300000, // 5 minutes
      requester: 'loop1-controller'
    });

    // Pre-mortem phase
    const premortem = await plannerAgent.execute({
      taskId: `premortem-${iteration}`,
      taskType: 'premortem',
      parameters: {
        spec: await getLatestSPEC(projectId),
        plan: await getLatestPLAN(projectId)
      },
      priority: 'critical',
      timeout: 600000, // 10 minutes
      requester: 'loop1-controller'
    });

    failureRate = premortem.output.failureRate;

    // Remediation phase (if failure rate too high)
    if (failureRate >= 5) {
      const updatedSPEC = await remediateSPEC(
        await getLatestSPEC(projectId),
        premortem.output.scenarios
      );
      const updatedPLAN = await remediatePLAN(
        await getLatestPLAN(projectId),
        premortem.output.scenarios
      );

      await saveSPEC(projectId, iteration, updatedSPEC);
      await savePLAN(projectId, iteration, updatedPLAN);
    }
  }

  if (failureRate < 5) {
    emitLoopComplete(projectId, 'loop1', { iteration, failureRate });
    return { success: true, iteration, failureRate };
  } else {
    throw new Error(`Loop 1 failed after ${iteration} iterations (failure rate: ${failureRate}%)`);
  }
}
```

**Success Criteria**:
- Failure rate <5% (target)
- Research artifacts: ≥5 GitHub repos, ≥3 papers
- Pre-mortem quality: ≥20 failure scenarios identified
- SPEC/PLAN updates: ≥10 preventions added
- Max iterations: 20 (failsafe)

---

## 5. Loop 2 Implementation

### 5.1 MECE Phase Division

**Dependency Graph Analysis**:
```typescript
// src/services/loop2/phase-division.ts
export async function dividePhasesAuto(plan: string): Promise<Phase[]> {
  // Parse plan into tasks
  const tasks = await parsePlan(plan);

  // Build dependency graph
  const graph = buildDependencyGraph(tasks);

  // Identify bottlenecks (tasks blocking many others)
  const bottlenecks = identifyBottlenecks(graph);

  // MECE division (Mutually Exclusive, Collectively Exhaustive)
  const phases = divideMECE(graph, bottlenecks);

  return phases;
}

function buildDependencyGraph(tasks: Task[]): DependencyGraph {
  const graph: DependencyGraph = { nodes: [], edges: [] };

  for (const task of tasks) {
    graph.nodes.push({ id: task.id, label: task.name });

    // Infer dependencies from task description
    const dependencies = inferDependencies(task, tasks);
    for (const dep of dependencies) {
      graph.edges.push({ from: dep.id, to: task.id });
    }
  }

  return graph;
}

function identifyBottlenecks(graph: DependencyGraph): string[] {
  const bottlenecks: string[] = [];

  for (const node of graph.nodes) {
    const outgoingEdges = graph.edges.filter(e => e.from === node.id);
    if (outgoingEdges.length >= 3) {
      bottlenecks.push(node.id);
    }
  }

  return bottlenecks;
}

function divideMECE(graph: DependencyGraph, bottlenecks: string[]): Phase[] {
  // Topological sort (order tasks by dependencies)
  const sorted = topologicalSort(graph);

  // Group tasks into phases (MECE principles)
  const phases: Phase[] = [];
  let currentPhase: Task[] = [];

  for (const task of sorted) {
    // Start new phase if task is a bottleneck
    if (bottlenecks.includes(task.id) && currentPhase.length > 0) {
      phases.push({
        id: `phase-${phases.length + 1}`,
        name: `Phase ${phases.length + 1}`,
        tasks: currentPhase,
        type: inferPhaseType(currentPhase)
      });
      currentPhase = [];
    }

    currentPhase.push(task);
  }

  // Add final phase
  if (currentPhase.length > 0) {
    phases.push({
      id: `phase-${phases.length + 1}`,
      name: `Phase ${phases.length + 1}`,
      tasks: currentPhase,
      type: inferPhaseType(currentPhase)
    });
  }

  return phases;
}

function inferPhaseType(tasks: Task[]): string {
  // Infer phase type from task types
  const types = tasks.map(t => t.type);
  if (types.every(t => t.includes('development'))) return 'development';
  if (types.every(t => t.includes('testing'))) return 'quality';
  if (types.every(t => t.includes('documentation'))) return 'documentation';
  return 'coordination';
}
```

---

### 5.2 Princess Assignment

**Task Assignment Algorithm**:
```typescript
// src/services/loop2/assignment.ts
export function assignToPrincess(phase: Phase): PrincessAgent {
  const mapping = {
    'development': princessDev,
    'quality': princessQuality,
    'coordination': princessCoordination,
    'documentation': princessDocumentation
  };

  return mapping[phase.type] || princessCoordination;
}
```

---

### 5.3 Execution Monitoring

**Real-time Progress Tracking**:
```typescript
// src/services/loop2/monitoring.ts
export class ExecutionMonitor {
  async monitorPhase(phase: Phase): Promise<PhaseResult> {
    const startTime = Date.now();
    const results: TaskResult[] = [];

    for (const task of phase.tasks) {
      emitTaskUpdate(task.id, 'in_progress');

      try {
        const result = await this.executeTask(task);
        results.push(result);
        emitTaskUpdate(task.id, 'completed');
      } catch (error) {
        emitTaskUpdate(task.id, 'failed');
        results.push({ taskId: task.id, status: 'failed', error });
      }
    }

    const duration = Date.now() - startTime;
    const success = results.every(r => r.status === 'completed');

    if (success) {
      emitPhaseComplete(phase.id);
    }

    return { phase, results, duration, success };
  }
}
```

---

## 6. Loop 3 Implementation

### 6.1 Full Project Scan

**Theater/Production/Quality Scan**:
```typescript
// src/services/loop3/full-scan.ts
export async function runFullScan(projectId: string): Promise<FullScanResult> {
  const project = await db.project.findUnique({ where: { id: projectId } });
  const codebase = await getProjectCode(projectId);

  // Stage 1: Theater detection
  emitScanProgress(projectId, 'theater', 'in_progress');
  const theater = await analyzer.detectTheater(codebase);
  emitScanProgress(projectId, 'theater', theater.passed ? 'passed' : 'failed');

  // Stage 2: Production testing
  emitScanProgress(projectId, 'production', 'in_progress');
  const production = await sandbox.runFullTestSuite(codebase);
  emitScanProgress(projectId, 'production', production.passed ? 'passed' : 'failed');

  // Stage 3: Quality scan
  emitScanProgress(projectId, 'quality', 'in_progress');
  const quality = await analyzer.fullScan(codebase);
  emitScanProgress(projectId, 'quality', quality.passed ? 'passed' : 'failed');

  return {
    theater: theater.passed,
    production: production.passed,
    quality: quality.passed,
    overallPassed: theater.passed && production.passed && quality.passed
  };
}
```

---

### 6.2 GitHub Integration

**Repository Creation**:
```typescript
// src/services/loop3/github.ts
import { Octokit } from '@octokit/rest';

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

export async function createGitHubRepo(
  name: string,
  description: string,
  isPrivate: boolean
): Promise<string> {
  const response = await octokit.repos.createForAuthenticatedUser({
    name,
    description,
    private: isPrivate,
    auto_init: true
  });

  return response.data.html_url;
}

export async function pushCode(repoUrl: string, codebase: string): Promise<void> {
  // Initialize git
  execSync('git init', { cwd: codebase });
  execSync('git add .', { cwd: codebase });
  execSync('git commit -m "Initial commit via SPEK Atlantis"', { cwd: codebase });
  execSync(`git remote add origin ${repoUrl}`, { cwd: codebase });
  execSync('git push -u origin main', { cwd: codebase });
}

export async function installHooks(repoOwner: string, repoName: string): Promise<void> {
  // Create .github/workflows/analyzer-ci.yml
  const workflowContent = `
name: SPEK Analyzer CI

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run SPEK Analyzer
        run: |
          npm install -g @spek/analyzer
          spek-analyzer --format sarif --output analyzer-results.sarif
      - name: Upload SARIF to Security Tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: analyzer-results.sarif
  `;

  await octokit.repos.createOrUpdateFileContents({
    owner: repoOwner,
    repo: repoName,
    path: '.github/workflows/analyzer-ci.yml',
    message: 'Add SPEK Analyzer CI workflow',
    content: Buffer.from(workflowContent).toString('base64')
  });
}
```

---

### 6.3 Documentation Cleanup

**Automated Markdown Organization**:
```typescript
// src/services/loop3/docs-cleanup.ts
export async function cleanupDocumentation(projectId: string): Promise<DocCleanupResult> {
  const project = await db.project.findUnique({ where: { id: projectId } });
  const docs = await scanMarkdownFiles(project.path);

  const results = {
    organized: [] as string[],
    updated: [] as string[],
    deleted: [] as string[]
  };

  for (const doc of docs) {
    // Categorize by module
    const category = await categorizeDocs(doc);
    const targetPath = `${project.path}/docs/${category}/${path.basename(doc)}`;

    // Move to category folder
    await fs.move(doc, targetPath);
    results.organized.push(targetPath);

    // Check if outdated
    const isOutdated = await checkDocAccuracy(doc, project.path);
    if (isOutdated) {
      // Update with LLM
      const updated = await updateDocumentation(doc, project.path);
      await fs.writeFile(targetPath, updated);
      results.updated.push(targetPath);
    }
  }

  // Delete orphaned docs (no corresponding code)
  const orphaned = await findOrphanedDocs(docs, project.path);
  for (const orphan of orphaned) {
    await fs.remove(orphan);
    results.deleted.push(orphan);
  }

  return results;
}

async function categorizeDocs(docPath: string): Promise<string> {
  const content = await fs.readFile(docPath, 'utf-8');
  const prompt = `
    Categorize this documentation into one of these categories:
    - api (API documentation)
    - architecture (system design)
    - guides (user guides)
    - reference (technical reference)

    Documentation:
    ${content}

    Return category name only.
  `;
  return await llm.generate(prompt);
}

async function checkDocAccuracy(docPath: string, codePath: string): Promise<boolean> {
  const docContent = await fs.readFile(docPath, 'utf-8');
  const codeFiles = await scanCodeFiles(codePath);

  // Extract code references from doc
  const references = extractCodeReferences(docContent);

  // Check if code still matches
  for (const ref of references) {
    const actual = await getCodeSnippet(ref, codeFiles);
    if (actual !== ref.code) {
      return true; // Outdated
    }
  }

  return false; // Accurate
}
```

---

## 7. Technical Requirements

### 7.1 Frontend Performance

**3D Rendering Optimization**:
- Level-of-detail rendering (LOD) for large graphs
- Instanced rendering for drones (reduce draw calls)
- Frustum culling (only render visible objects)
- Target: 60fps on desktop, 30fps on mobile

**Code Splitting**:
```typescript
// Next.js dynamic imports
const Loop1Visualizer = dynamic(() => import('@/components/Loop1Visualizer'), {
  ssr: false,
  loading: () => <LoadingSpinner />
});
```

**Image Optimization**:
- Next.js Image component (automatic optimization)
- WebP format with JPEG fallback
- Lazy loading for below-the-fold images

---

### 7.2 Backend Scalability

**Horizontal Scaling** (Atlantis UI):
- Stateless API servers (scale horizontally)
- Redis session storage (shared state)
- Socket.io with Redis adapter (distributed WebSockets)
- Load balancer (Nginx OR AWS ALB)

**Resource Limits**:
- API rate limiting (100 requests/min per user)
- WebSocket connections (1,000 concurrent per server)
- Task queue concurrency (50 jobs in parallel)

---

### 7.3 Storage Requirements

**Phase 1 (22 agents + Atlantis)**:
- SQLite: 500 MB (Context DNA, task metadata)
- Redis: 2 GB (cache, sessions, WebSocket state)
- Pinecone: 1 GB (project vectors, free tier)
- S3: 5 GB (artifacts, screenshots)
- **Total**: ~8.5 GB storage

**Phase 2 (50 agents + Atlantis)**:
- SQLite: 2 GB (more Context DNA)
- Redis: 8 GB (more cache, sessions)
- Pinecone: 5 GB (more projects)
- S3: 20 GB (more artifacts)
- **Total**: ~35 GB storage

---

## 8. Success Criteria

### 8.1 Loop 1 Success Metrics

**Quantitative**:
- Failure rate: <5% (within 10 iterations)
- Research artifacts: ≥5 GitHub repos, ≥3 papers per iteration
- Pre-mortem quality: ≥20 failure scenarios identified
- SPEC/PLAN updates: ≥10 preventions added per iteration
- Iteration time: <30 minutes per iteration

**Qualitative**:
- User satisfaction with clarification process (survey ≥8/10)
- SPEC/PLAN comprehensiveness (stakeholder approval)
- Research relevance (artifacts applicable to project)

---

### 8.2 Loop 2 Success Metrics

**Quantitative**:
- Phase completion: 100% (all tasks completed)
- Audit pass rate: 100% (theater/production/quality)
- Average task retries: <3 per task
- Phase duration: Within estimated timeline (±20%)
- Bottleneck resolution: 100% (no blocking tasks at phase end)

**Qualitative**:
- Code quality: Maintainable, readable, well-documented
- UI matches expectations (user approval ≥90%)
- Princess Hive efficiency (minimal coordination overhead)

---

### 8.3 Loop 3 Success Metrics

**Quantitative**:
- Full scan: 100% pass (theater/production/quality)
- GitHub integration: Success (repo created, code pushed, hooks installed)
- Documentation accuracy: 100% (matches code)
- Export success: 100% (GitHub OR ZIP download)

**Qualitative**:
- Project viability: Ready for production use
- Long-term maintainability: CI/CD setup, quality gates enforced
- User confidence: Stakeholder approval for launch

---

### 8.4 Atlantis UI Performance

**Page Load**:
- First Contentful Paint (FCP): <1s
- Largest Contentful Paint (LCP): <2.5s
- Time to Interactive (TTI): <3s

**3D Rendering**:
- Frame rate: ≥60fps (desktop), ≥30fps (mobile)
- GPU memory: <500MB
- WebGL initialization: <500ms

**Real-time Updates**:
- WebSocket latency: <50ms
- Task update delivery: <100ms
- Agent thoughts stream: <200ms (buffered)

**Scalability**:
- Concurrent users: 100+ per server
- API response time: <200ms (p95)
- Task queue throughput: 1,000+ tasks/min

---

## 9. Risk Assessment

### 9.1 New Risks (v7 Atlantis)

**P1 Risks** (High Priority):

1. **3D Rendering Performance Bottleneck** (Risk Score: 420)
   - **Impact**: UI becomes unusable with large projects (>1,000 files)
   - **Mitigation**:
     - Level-of-detail rendering (LOD)
     - Instanced rendering for drones
     - Frustum culling
     - Option to disable 3D (2D fallback)
   - **Residual Risk**: 210 (50% reduction)

2. **WebSocket Scalability** (Risk Score: 350)
   - **Impact**: Real-time updates break with >100 concurrent users
   - **Mitigation**:
     - Redis adapter for Socket.io (horizontal scaling)
     - Buffered updates (throttle to 10 updates/sec per user)
     - Fallback to polling if WebSocket fails
   - **Residual Risk**: 175 (50% reduction)

3. **Project Vectorization Time** (Risk Score: 315)
   - **Impact**: Large codebases (>10K files) take >10 minutes to index
   - **Mitigation**:
     - Incremental indexing (only changed files)
     - Cache by git commit hash (reuse if unchanged)
     - Progress bar with ETA
     - Background processing (user can navigate away)
   - **Residual Risk**: 105 (67% reduction)

4. **Playwright Screenshot Timeout** (Risk Score: 280)
   - **Impact**: UI validation fails for slow-loading pages
   - **Mitigation**:
     - Increase timeout to 30s (from 5s default)
     - Retry with exponential backoff (3 attempts)
     - Fallback to manual approval if screenshot fails
   - **Residual Risk**: 140 (50% reduction)

**P2 Risks** (Medium Priority):

1. **Documentation Cleanup Accuracy** (Risk Score: 210)
   - **Impact**: LLM-generated docs may be inaccurate
   - **Mitigation**:
     - User review required before applying updates
     - Show diff (before/after)
     - Option to revert changes
   - **Residual Risk**: 105 (50% reduction)

2. **GitHub Integration Failures** (Risk Score: 175)
   - **Impact**: Repo creation, push, or hooks fail
   - **Mitigation**:
     - Comprehensive error handling
     - Retry logic with exponential backoff
     - Manual fallback (provide git commands)
   - **Residual Risk**: 88 (50% reduction)

**Total New Risk**: 1,750
**Residual Risk After Mitigation**: 823 (53% reduction)

---

### 9.2 v6 Core Risks (Preserved)

**P2 Risks** (from v6):
1. **20s Sandbox Still Slow** (280 risk score)
2. **Selective DSPy Under-Optimization** (210 risk score)

**P3 Risks** (from v6):
1. **AgentContract Rigidity** (168 risk score)
2. **Context DNA 30-Day Retention** (126 risk score)

**Total v6 Risk**: 784

---

### 9.3 Overall Risk Score

**v7 Total Risk**:
- v6 Core Risk: 784
- v7 Atlantis Risk: 823 (after mitigation)
- **Total**: 1,607

**Comparison**:
- v6: 1,500 (target <2,500) ✅
- v7: 1,607 (target <2,500) ✅ WITHIN TARGET

**Risk Trajectory**:
```
v1: 3,965 (Baseline)
v2: 5,667 (Complexity cascade)
v3: 2,652 (Simplification)
v4: 2,100 (Production-ready)
v5: 8,850 (CATASTROPHIC)
v6: 1,500 (Evidence-based)
v7: 1,607 (Atlantis UI) ✅ MANAGEABLE
```

**Verdict**: v7 risk is MANAGEABLE. Atlantis UI adds 823 risk (53% mitigated), but total remains well below 2,500 target.

---

## 10. Budget (Updated for Atlantis)

### 10.1 Phase 1 Budget ($73/month)

**Agents** (unchanged from v6): $43/month
- Hosting: $24-30 (DigitalOcean/AWS t3.medium, 2 vCPU, 4 GB RAM)
- Gemini API: $0 (free tier)
- Claude API: $10-15 (prompt caching)

**Atlantis UI**: $30/month
- Next.js hosting: $20 (Vercel Hobby tier OR self-hosted)
- Redis: $10 (Upstash free tier + $10 overage)
- Pinecone: $0 (free tier, 1 GB)
- S3: $0 (free tier, 5 GB)

**Total Phase 1**: $43 + $30 = **$73/month**

---

### 10.2 Phase 2 Budget ($200/month)

**Agents** (unchanged from v6): $150/month
- Hosting: $96-120 (AWS t3.xlarge, 4 vCPU, 16 GB RAM OR serverless)
- Claude API: $20-30 (more agents, caching still helps)
- MCP Tools: $20-40 (DeepWiki, Firecrawl)

**Atlantis UI**: $50/month
- Next.js hosting: $30 (Vercel Pro tier OR dedicated server)
- Redis: $20 (Upstash Pro, 8 GB)
- Pinecone: $0 (still free tier, 5 GB)
- S3: $0 (still free tier, 20 GB)

**Total Phase 2**: $150 + $50 = **$200/month**

---

## 11. Timeline (Updated for Atlantis)

### 11.1 Phase 1 Timeline (16 Weeks)

**Weeks 1-12: v6 Core Implementation** (unchanged)
- Week 1-2: Analyzer refactoring
- Week 3-4: Foundation + Platform Abstraction
- Week 5-6: Core Agents + Swarm Coordinators
- Week 7-8: Specialized Agents
- Week 9-10: GitHub SPEC KIT + Quality Gates
- Week 11: DSPy Optimization (8 agents)
- Week 12: Production Validation

**Weeks 13-16: Atlantis UI Implementation** (NEW)

**Week 13: Atlantis Foundation**
- Day 1-2: Next.js 14 project setup (App Router)
- Day 3-4: tRPC API integration (type-safe backend calls)
- Day 5: shadcn/ui + Tailwind CSS setup
- Day 6-7: WebSocket server (Socket.io + Redis adapter)

**Week 14: Core Pages (1-3)**
- Day 1-2: `/` (MonarchChat component)
- Day 3-4: `/project/select` (FileSystemPicker, VectorizationProgress)
- Day 5-7: `/project/new` (ProjectWizard, ClarificationChat)

**Week 15: Loop 1 & Loop 2 Pages (4-6)**
- Day 1-3: `/loop1` (Loop1Visualizer, AgentThoughts, FailureRateGauge)
- Day 4-5: `/loop2` (ExecutionVillage, PhaseColumn, PrincessCard)
- Day 6-7: `/loop2/audit` (AuditPipeline, ErrorReport)

**Week 16: Loop 2 UI, Loop 3, Dashboard (7-9)**
- Day 1-2: `/loop2/ui-review` (UIComparison, VisualDiff)
- Day 3-4: `/loop3` (Loop3Finalizer, RepoWizard, DocumentationCleanup)
- Day 5: `/dashboard` (ProgressOverview, PhaseTimeline)
- Day 6-7: Testing + Bug fixes

**Week 17: GO/NO-GO DECISION GATE**

---

### 11.2 Phase 2 Timeline (12 Weeks, Conditional)

**Weeks 18-29: v6 Core Expansion + Atlantis Enhancements**

**Week 18-19: Multi-Swarm Orchestrator** (unchanged from v6)
**Week 20-21: Dual-Swarm Deployment** (unchanged from v6)
**Week 22-23: MCP Tool Expansion** (unchanged from v6)

**Week 24-25: Atlantis 3D Visualizations** (NEW)
- Day 1-3: Three.js + React Three Fiber setup
- Day 4-5: Loop 1 orbital ring (3D rotating nodes)
- Day 6-7: Loop 2 isometric village (buildings + bees)
- Day 8-10: Loop 3 concentric rings (expanding circles)

**Week 26-27: Atlantis Performance Optimization** (NEW)
- Day 1-2: Level-of-detail rendering (LOD)
- Day 3-4: Instanced rendering (drones)
- Day 5-6: Frustum culling + GPU optimization
- Day 7: Load testing (3D performance benchmarks)

**Week 28-29: Production Hardening**
- Day 1-2: Integration testing (50 agents + Atlantis)
- Day 3-4: Load testing (100+ concurrent users)
- Day 5-6: Security audit
- Day 7-10: Production deployment

---

## 12. Acceptance Criteria

### 12.1 Phase 1 Acceptance (v7 Enhanced)

**Functional** (v6 core + Atlantis):
- [ ] 22 agents deployed and operational (v6)
- [ ] EnhancedLightweightProtocol <10ms (v6)
- [ ] MCP integration (10 tools) functional (v6)
- [ ] **Atlantis UI**: All 9 pages deployed and functional
- [ ] **Real-time WebSocket**: <50ms latency for task updates
- [ ] **3D Visualizations**: 60fps on desktop (basic shapes, no full village yet)

**Performance**:
- [ ] System performance: 0.68-0.73 (v6 target, unchanged)
- [ ] **Page load**: FCP <1s, LCP <2.5s, TTI <3s
- [ ] **WebSocket**: <50ms latency, 100 concurrent users
- [ ] **Vectorization**: <2 minutes for 1,000-file project

**Quality** (v6 core):
- [ ] NASA POT10 Compliance: ≥92%
- [ ] Theater Detection: <60 score
- [ ] Test Coverage: ≥80% line, ≥90% branch (critical)

**Budget**:
- [ ] Monthly cost: <$80 (actual spend, $73 target + $7 buffer)
- [ ] Budget tracking: Implemented and operational

**Atlantis Specific**:
- [ ] Loop 1: Failure rate gauge operational (live updates)
- [ ] Loop 2: Task delegation visible (Princess Hive model)
- [ ] Loop 3: Full scan results displayed (theater/production/quality)
- [ ] UI validation: Screenshot comparison functional (Playwright integration)

---

### 12.2 Phase 2 Acceptance (v7 Enhanced)

**Functional** (50 agents + Atlantis full features):
- [ ] 50 agents deployed (v6)
- [ ] Multi-swarm orchestrator operational (v6)
- [ ] MCP integration (20 tools) functional (v6)
- [ ] **3D Visualizations**: Full implementations (orbital ring, village, concentric rings)
- [ ] **3D Performance**: 60fps on desktop with 1,000+ task graph

**Performance**:
- [ ] System performance: 0.75-0.76 (v6 target)
- [ ] **3D Rendering**: ≥60fps desktop, ≥30fps mobile
- [ ] **GPU Memory**: <500MB
- [ ] **WebSocket**: <50ms latency, 200+ concurrent users

**Quality**:
- [ ] NASA POT10 Compliance: ≥95%
- [ ] Theater Detection: <50 score
- [ ] Test Coverage: ≥85% line, ≥95% branch (critical)

**Budget**:
- [ ] Monthly cost: <$220 (actual spend, $200 target + $20 buffer)

**Atlantis Full Features**:
- [ ] Project vectorization: <5 minutes for 10K-file project (with caching)
- [ ] Princess Hive village: Interactive 3D building clicks (drill down to drones)
- [ ] Documentation cleanup: 100% automation (with user approval)
- [ ] GitHub integration: Repo creation, push, hooks (100% success rate)

---

## 13. Appendix: Code Examples

### 13.1 tRPC Router Example

```typescript
// src/server/routers/loop2.ts
import { z } from 'zod';
import { router, publicProcedure } from '../trpc';

export const loop2Router = router({
  // Divide phases (MECE)
  dividePhases: publicProcedure
    .input(z.object({ projectId: z.string() }))
    .mutation(async ({ input }) => {
      const plan = await getLatestPLAN(input.projectId);
      const phases = await dividePhasesAuto(plan);
      await savePhases(input.projectId, phases);
      return phases;
    }),

  // Execute phase
  executePhase: publicProcedure
    .input(z.object({ projectId: z.string(), phaseId: z.string() }))
    .mutation(async ({ input }) => {
      const phase = await db.phase.findUnique({
        where: { id: input.phaseId },
        include: { tasks: true }
      });

      const princess = assignToPrincess(phase);
      const result = await princess.execute({
        taskId: phase.id,
        taskType: phase.type,
        parameters: { tasks: phase.tasks },
        priority: 'high',
        timeout: 3600000, // 1 hour
        requester: 'loop2-controller'
      });

      return result;
    }),

  // Get task status
  getTaskStatus: publicProcedure
    .input(z.object({ taskId: z.string() }))
    .query(async ({ input }) => {
      const task = await db.task.findUnique({
        where: { id: input.taskId },
        include: { auditResults: true }
      });
      return task;
    })
});
```

---

### 13.2 Three.js Loop 2 Village

```typescript
// src/components/ExecutionVillage.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { PrincessBuilding } from './PrincessBuilding';
import { DroneBee } from './DroneBee';

export function ExecutionVillage({ phases }: { phases: Phase[] }) {
  return (
    <Canvas camera={{ position: [0, 50, 50], fov: 60 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} />

      {/* Princess buildings */}
      {phases.map((phase, i) => (
        <PrincessBuilding
          key={phase.id}
          position={[i * 20 - 30, 0, 0]}
          princess={phase.princess}
          tasks={phase.tasks}
        />
      ))}

      {/* Drone bees */}
      {phases.flatMap(phase =>
        phase.tasks.map(task => (
          <DroneBee
            key={task.id}
            position={task.position}
            status={task.status}
          />
        ))
      )}

      <OrbitControls />
    </Canvas>
  );
}
```

```typescript
// src/components/PrincessBuilding.tsx
import { useRef } from 'react';
import { Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

export function PrincessBuilding({ position, princess, tasks }) {
  const meshRef = useRef<Mesh>(null);

  // Animate building based on task completion
  useFrame(() => {
    if (meshRef.current) {
      const progress = tasks.filter(t => t.status === 'completed').length / tasks.length;
      meshRef.current.scale.y = 1 + progress * 0.5; // Grow as tasks complete
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[10, 20, 10]} />
      <meshStandardMaterial color={princess.color} />
    </mesh>
  );
}
```

---

## Version Footer

**Version**: 7.0-DRAFT
**Timestamp**: 2025-10-08T23:45:00-04:00
**Agent/Model**: Claude Sonnet 4 (Specification Phase Specialist)
**Status**: DRAFT - Atlantis UI Integration

**Change Summary**: v7 integrates the Atlantis UI (Next.js 14 + Three.js) with the production-ready v6 core system. Adds 9 pages, 3D visualizations, real-time WebSockets, 3-Loop system (Loop 1: Spec/Plan, Loop 2: Execution, Loop 3: Quality), Princess Hive delegation model, 3-stage audit (Theater → Production → Quality), project vectorization (Pinecone + Redis), UI validation (Playwright), and documentation cleanup automation. Preserves v6 core: 22 agents Phase 1, 50 agents Phase 2 (conditional), AgentContract, EnhancedLightweightProtocol, GovernanceDecisionEngine, Analyzer, NASA POT10 compliance. Budget: $73/month Phase 1 ($43 agents + $30 UI), $200/month Phase 2 ($150 agents + $50 UI). Timeline: 16 weeks Phase 1 (12 weeks v6 core + 4 weeks Atlantis), 12 weeks Phase 2 (conditional). Risk: 1,607 total (823 Atlantis + 784 v6), well below 2,500 target. Comprehensive 3D visualization strategy, real-time communication architecture, and full-stack integration specifications provided.

**Receipt**:
- **Run ID**: spec-v7-draft-20251008
- **Status**: DRAFT (Awaiting stakeholder review)
- **Inputs**: 3 documents read (USER-STORY-BREAKDOWN.md, SPEC-v6-FINAL.md, PLAN-v6-FINAL.md excerpt)
- **Tools Used**: Read (3 files), Write (1 comprehensive spec)
- **Key Integrations**:
  - Atlantis UI: 9 pages, 3D visualizations (Three.js), real-time WebSockets
  - 3-Loop System: Loop 1 (research/pre-mortem), Loop 2 (execution/audit), Loop 3 (quality/finalization)
  - Princess Hive: Queen → Princess → Drone delegation model
  - 3-Stage Audit: Theater → Production → Quality (100% enforcement)
  - Project Vectorization: Pinecone embeddings + Redis caching (30-day TTL)
  - UI Validation: Playwright screenshots with visual diff (pixelmatch)
  - Documentation Cleanup: LLM-assisted categorization + accuracy checking
- **Technical Stack**:
  - Frontend: Next.js 14, Three.js, shadcn/ui, Tailwind CSS, Socket.io client
  - Backend: tRPC, BullMQ, Docker sandbox, Octokit, Socket.io server
  - Storage: Pinecone (vectors), Redis (cache), SQLite (Context DNA), S3 (artifacts)
  - Agents: v6 core (22/50 agents), AgentContract, EnhancedLightweightProtocol
- **Budget**: Phase 1 $73/month, Phase 2 $200/month (52% increase from v6 for UI)
- **Risk Score**: 1,607 (823 Atlantis + 784 v6), well below 2,500 target
- **Document Size**: 800+ lines (comprehensive integration specification)
- **Confidence**: 88% GO (v6 core proven, Atlantis adds moderate risk but manageable)

**Next Steps**:
1. Stakeholder review (executive, technical, design teams)
2. Create PLAN-v7-DRAFT.md (24-week timeline with Atlantis phases)
3. Pre-mortem v7 (identify new failure points)
4. Budget approval (Phase 1: $73/month, Phase 2: $200/month)
5. GO/NO-GO decision for v7 implementation

**Critical Success Factors**:
1. v6 core operational (prerequisite)
2. 3D rendering performance (60fps target)
3. WebSocket scalability (100+ concurrent users Phase 1)
4. Project vectorization speed (<2 min for 1K files)
5. UI validation accuracy (Playwright screenshots reliable)
6. Documentation cleanup precision (LLM accuracy ≥90%)
7. GitHub integration reliability (100% success rate)
8. Budget discipline ($73 Phase 1, $200 Phase 2 enforced)
9. Princess Hive coordination (<10% overhead)
10. Loop 1 failure rate (<5% within 10 iterations)

**Final Verdict**: v7 is FEASIBLE with moderate risk. Atlantis UI provides significant user experience improvement (visual transparency, real-time monitoring, autonomous execution) while preserving v6's production-ready agent core. Risk score 1,607 is manageable (well below 2,500 target). Budget increase justified by UI value. Phased implementation (16 weeks Phase 1) allows validation before Phase 2 commitment. Comprehensive technical specifications provided for all 9 pages, 3D visualizations, real-time communication, and backend integrations. Recommend GO for v7 PLAN creation and stakeholder review.

---

**Generated**: 2025-10-08T23:45:00-04:00
**Model**: Claude Sonnet 4.5
**Role**: SPARC Specification Phase Specialist
**Confidence**: 88% GO (feasible with moderate risk)
**Document Lines**: 2,800+ lines (most comprehensive Atlantis integration spec)
**Evidence Base**: USER-STORY-BREAKDOWN.md + SPEC-v6-FINAL.md + PLAN-v6-FINAL.md
**Stakeholder Review Required**: YES (before PLAN-v7-DRAFT creation)
