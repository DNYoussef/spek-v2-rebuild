# User Story Technical Breakdown - Atlantis UI

**Date**: 2025-10-08
**Purpose**: Break down long-form user story into technical components for v7 SPEC/PLAN

---

## 🎯 Core Vision

**Project Name**: Atlantis (Next.js + Three.js UI for SPEK Platform)
**Goal**: Visual, autonomous AI agent coordination system with 3-loop quality refinement

---

## 📋 User Story Components

### 1. Initial Interface - Monarch Chat

**User Experience**:
- Chat interface with King/Queen/Monarch agent
- Choose: New project OR Existing project
- Visual: Conversational UI, elegant design

**Technical Components**:
- Next.js page: `/` (landing with chat)
- Component: `<MonarchChat />` (chat interface)
- API: `/api/monarch/chat` (agent communication)
- State: Project selection (new vs existing)

**Features**:
- Real-time chat with Monarch agent
- Project type selection
- Session persistence

---

### 2. Existing Project Flow

**User Experience**:
- Dropdown menu OR file explorer
- Select project folder
- Vectorization + indexing (with visual progress)
- Structure graph generation
- Caching for future sessions
- Option: Specific changes OR Refinement loop

**Technical Components**:
- Component: `<ProjectSelector />` (file picker)
- API: `/api/project/index` (vectorization)
- API: `/api/project/graph` (structure analysis)
- Storage: Vector DB (Pinecone/Weaviate) + Cache (Redis)
- Component: `<ProjectGraph />` (3D graph visualization)
- Component: `<RefinementChoice />` (specific vs loop)

**Features**:
- File system access (Electron wrapper OR server-side)
- Project vectorization (embeddings)
- AST + dependency graph generation
- Cache layer (avoid re-indexing)
- Visual progress indicator

**Data Flow**:
```
User selects folder
  → Vectorize codebase
    → Generate structure graph
      → Cache results
        → Present options (specific changes / refinement loop)
```

---

### 3. New Project Flow - Clarification Phase

**User Experience**:
- User describes project vision
- Monarch asks clarifying questions
- Technical → Experience translation for non-technical users
- Fill out SPEC + PLAN documents
- Visual: Q&A interface with progress bar

**Technical Components**:
- Component: `<ProjectWizard />` (multi-step form)
- API: `/api/monarch/clarify` (question generation)
- API: `/api/spec/generate` (SPEC document creation)
- API: `/api/plan/generate` (PLAN document creation)
- Storage: Draft SPEC/PLAN in session

**Features**:
- Multi-turn conversation
- Technical complexity detection (adjust questions)
- Either/or options for non-technical users
- Progressive SPEC/PLAN generation
- Document preview

**Question Categories**:
- User experience expectations
- Technical stack preferences (abstracted)
- Scale/performance requirements
- Security/compliance needs
- Budget/timeline constraints

---

### 4. Loop 1 - Spec/Plan/Research/Pre-mortem

**User Experience**:
- Visual loop animation (3D rotation?)
- Current iteration count
- Failure rate percentage (target: <5%)
- Agent thoughts window (real-time)
- Pause/inject thoughts button

**Technical Components**:
- Component: `<Loop1Visualizer />` (3D loop animation)
- Component: `<AgentThoughts />` (real-time log stream)
- Component: `<FailureRateGauge />` (percentage display)
- API: `/api/loop1/research` (GitHub + academic search)
- API: `/api/loop1/premortem` (multi-agent analysis)
- API: `/api/loop1/remediate` (plan updates)
- WebSocket: Real-time agent activity

**Loop 1 Phases**:
1. **Research** - GitHub code search + academic papers
2. **Pre-mortem** - Multi-agent failure analysis
3. **Remediation** - Update SPEC/PLAN with preventions
4. **Re-research** - Gather additional components
5. **Re-premortem** - Fresh eyes analysis
6. **Iterate** - Until failure rate <5%

**Visual Elements**:
- 3D loop indicator (orbital rotation?)
- Iteration counter badge
- Failure rate gauge (color-coded: red >20%, yellow 5-20%, green <5%)
- Agent activity feed (scrolling thoughts)
- Pause overlay with input box

**Data Collected**:
- SPEC document (versioned)
- PLAN document (versioned)
- Research artifacts (GitHub repos, papers)
- Pre-mortem reports (per iteration)
- Failure rate trajectory

---

### 5. Loop 2 - Execution (Phase Division + Princess Hives)

**User Experience**:
- Visual: Village/hive/bee delegation
- Phases displayed as columns/sections
- Tasks flow from Monarch → Princesses → Drones
- Real-time task status updates
- Visual connections (arrows/lines) for information transfer

**Technical Components**:
- Component: `<ExecutionVillage />` (3D village/hive)
- Component: `<PhaseColumn />` (phase breakdown)
- Component: `<PrincessCard />` (princess + drone group)
- Component: `<TaskFlow />` (animated task delegation)
- API: `/api/loop2/divide-phases` (MECE phase division)
- API: `/api/loop2/assign-tasks` (princess allocation)
- API: `/api/loop2/execute` (drone execution)
- WebSocket: Task status updates

**Phase Division Logic**:
- MECE principles (Mutually Exclusive, Collectively Exhaustive)
- Dependency graph analysis
- Bottleneck identification
- Princess specialization matching

**Princess Hive Structure**:
```
Monarch
  ├─ Princess-Dev (coder, reviewer, debugger drones)
  ├─ Princess-Quality (tester, nasa-enforcer, analyzer drones)
  ├─ Princess-Coordination (orchestrator, task-tracker drones)
  └─ Princess-Documentation (docs-writer, spec-writer drones)
```

**Communication Protocol** (Queen → Princess → Drone):
1. Establish context (pwd, TodoWrite with absolute path)
2. Create .project-boundary marker
3. Use Agent2Agent protocol (with path validation)
4. Project management system integration
5. Context DNA for translation integrity

**Visual Design**:
- 3D village with buildings = princesses
- Bees/drones = agents
- Animated paths = task delegation
- Color coding = task status (pending/in-progress/complete)

---

### 6. Audit System (Theater → Production → Quality)

**User Experience**:
- Each drone task triggers 3-stage audit
- Visual: Checkmark progression (🎭 → ⚙️ → ✅)
- Failed audits = task returns to drone with notes

**Technical Components**:
- Component: `<AuditPipeline />` (3-stage visualizer)
- API: `/api/audit/theater` (mock detection)
- API: `/api/audit/production` (sandbox testing)
- API: `/api/audit/quality` (analyzer scan)
- Service: Sandbox runner (Docker)
- Service: Analyzer integration

**Audit Stage 1: Theater Detection**
- Scan for: mock code, TODOs, NotImplementedError, fake data
- Tool: Existing analyzer theater detection
- Action: If detected → return to drone with notes → retry
- Pass criteria: Zero theater indicators

**Audit Stage 2: Production Testing**
- Run code in sandbox (Docker container)
- Execute tests
- Attempt smallest possible debug if failed
- Loop: Run → Debug → Run until 100% functional
- Pass criteria: All tests pass, code executes

**Audit Stage 3: Quality Scan**
- Analyzer scan for:
  - Connascence issues
  - God objects
  - NASA Rule 10 violations
  - Enterprise code safety
  - Defense department standards (DFARS)
  - Duplications/redundancies
  - Linting/style errors
- Generate JSON error report
- Send to specialist drones for refactor
- Re-scan after refactor
- Pass criteria: 100% quality score

**Audit Loop**:
```
Drone completes task
  → Theater audit (loop until pass)
    → Production audit (loop until pass)
      → Quality audit (loop until pass)
        → Mark task COMPLETE
```

**Visual Elements**:
- Progress bar with 3 segments (🎭 ⚙️ ✅)
- Current audit stage highlighted
- Retry counter badge
- Error report preview

---

### 7. Phase Completion & GitHub Integration

**User Experience**:
- Phase progress bar
- Task checklist (with dependency visualization)
- Bottleneck indicators removed as tasks complete
- Full phase audit at completion
- Visual celebration when phase done

**Technical Components**:
- Component: `<PhaseProgress />` (completion tracker)
- Component: `<DependencyGraph />` (bottleneck visualization)
- API: `/api/github/projects` (project board sync)
- API: `/api/phase/audit` (full phase validation)

**Phase Completion Criteria**:
- All princess tasks complete
- Full theater audit: 100% pass
- Full production audit: 100% pass
- Full quality audit: 100% pass
- GitHub project board updated

**Next Phase Trigger**:
- Mark current phase complete in GitHub
- Unblock dependent tasks
- Begin next phase division
- Repeat Loop 2 process

---

### 8. UI Validation (Playwright + Screenshots)

**User Experience**:
- Side-by-side comparison (expected vs actual)
- Visual diff highlighting
- Iterative refinement with user approval

**Technical Components**:
- Component: `<UIComparison />` (split view)
- API: `/api/ui/screenshot` (Playwright capture)
- API: `/api/ui/compare` (visual diff)
- Service: Playwright automation
- MCP: Chrome server integration

**UI Audit Process**:
1. Take screenshot of implemented UI
2. Compare to user's expected design
3. Generate visual diff
4. Present to user for approval
5. If changes needed → debug UI component
6. Verify UI connects to real backend code
7. Repeat until approved

---

### 9. Loop 3 - Quality & Long-term Viability

**User Experience**:
- Final scanning phase
- GitHub repo creation wizard
- Analyzer + CI/CD setup
- Documentation cleanup
- Export options (GitHub vs folder)

**Technical Components**:
- Component: `<Loop3Finalizer />` (final scan visualizer)
- Component: `<RepoWizard />` (GitHub setup)
- Component: `<DocumentationCleanup />` (doc organizer)
- API: `/api/loop3/scan` (full project audit)
- API: `/api/github/repo/create` (new repo creation)
- API: `/api/github/hooks/install` (GitHub hooks)
- API: `/api/cicd/setup` (pipeline generation)
- API: `/api/docs/organize` (markdown cleanup)

**Loop 3 Phases**:
1. **Full Project Scan**
   - Theater: 100%
   - Production: 100%
   - Quality: 100%

2. **GitHub Integration** (if selected)
   - Create new repo
   - Install analyzer hooks
   - Setup CI/CD pipeline (GitHub Actions)
   - Configure quality gates

3. **Documentation Cleanup**
   - List all markdown files
   - Organize by code module
   - Delete outdated docs
   - Update docs to match reality
   - Add UI screenshots (if applicable)

4. **Export**
   - GitHub: Push code, setup complete
   - Folder: Download with analyzer, local hooks

**Visual Elements**:
- Final progress wheel (100% completion)
- Checklist of Loop 3 items
- GitHub repo link (if created)
- Download button (if folder export)

---

## 🏗️ Technical Architecture

### Frontend Stack
- **Framework**: Next.js 14 (App Router)
- **3D Visualization**: Three.js + React Three Fiber
- **UI Components**: shadcn/ui + Tailwind CSS
- **Real-time**: WebSockets (Socket.io)
- **State Management**: Zustand + React Query
- **Forms**: React Hook Form + Zod validation

### Backend Stack
- **API**: Next.js API routes + tRPC
- **Agent Orchestration**: Existing SPEK Platform
- **Vector DB**: Pinecone (project embeddings)
- **Cache**: Redis (project indexing)
- **Queue**: BullMQ (task processing)
- **Sandbox**: Docker (code execution)
- **GitHub**: Octokit (API integration)
- **Search**: GitHub API + Semantic Scholar API

### Data Flow
```
User → Next.js UI → tRPC API → SPEK Agents → MCP Tools → Results → WebSocket → UI Update
```

---

## 📊 Page Structure

### Pages & Routes

1. **`/` (Home/Landing)**
   - Component: `<MonarchChat />`
   - Purpose: Initial conversation, project selection

2. **`/project/select` (Existing Project)**
   - Component: `<ProjectSelector />`
   - Component: `<ProjectGraph />` (after indexing)
   - Purpose: File picker, indexing, graph visualization

3. **`/project/new` (New Project Wizard)**
   - Component: `<ProjectWizard />`
   - Purpose: Multi-step clarification, SPEC/PLAN generation

4. **`/loop1` (Research & Pre-mortem)**
   - Component: `<Loop1Visualizer />`
   - Component: `<AgentThoughts />`
   - Component: `<FailureRateGauge />`
   - Purpose: Loop 1 iteration visualization

5. **`/loop2` (Execution Village)**
   - Component: `<ExecutionVillage />`
   - Component: `<PhaseColumn />` (multiple)
   - Component: `<PrincessCard />` (multiple)
   - Component: `<TaskFlow />`
   - Purpose: Task delegation, execution, audit visualization

6. **`/loop2/audit` (Audit Detail View)**
   - Component: `<AuditPipeline />`
   - Component: `<ErrorReport />` (JSON viewer)
   - Purpose: Detailed audit results, retry management

7. **`/loop2/ui-review` (UI Validation)**
   - Component: `<UIComparison />`
   - Purpose: Screenshot comparison, user approval

8. **`/loop3` (Finalization)**
   - Component: `<Loop3Finalizer />`
   - Component: `<RepoWizard />`
   - Component: `<DocumentationCleanup />`
   - Purpose: Final scans, GitHub setup, export

9. **`/dashboard` (Overall Progress)**
   - Component: `<ProgressOverview />`
   - Component: `<PhaseTimeline />`
   - Purpose: High-level project status

---

## 🔄 Reusable Components

### Cards (Reusable across pages)
- `<AgentCard />` - Display agent status, thoughts
- `<TaskCard />` - Task details, status, audit results
- `<PhaseCard />` - Phase summary, progress
- `<DocumentCard />` - SPEC/PLAN document preview
- `<ErrorCard />` - Error display with severity

### Tabs (Switch content within pages)
- `/loop2` tabs: Execution / Audit / UI Review
- `/loop3` tabs: Scan / GitHub / Documentation
- `/dashboard` tabs: Overview / Phases / Agents

### Modals/Overlays
- Pause overlay (inject thoughts)
- Task detail modal
- Agent log viewer
- Document editor (SPEC/PLAN)

---

## 🎨 Visual Design Principles

### Aesthetic Goals
- **Elegant**: Clean, modern, professional
- **Informative**: Clear status, minimal cognitive load
- **Engaging**: 3D visualizations, smooth animations
- **Responsive**: Works on desktop (primary), tablet, mobile

### 3D Visualization Ideas

**Loop 1**:
- Orbital ring with rotating nodes (iterations)
- Center: Failure rate percentage
- Satellites: Research artifacts

**Loop 2 (Village)**:
- Isometric village layout
- Buildings = Princesses
- Flying bees/drones = Agents
- Paths = Task delegation (animated lines)

**Loop 3**:
- Concentric circles expanding outward
- Center: Project core
- Rings: Scan → GitHub → Docs → Export

### Color Coding
- **Red**: Critical issues, >20% failure
- **Yellow**: Warnings, 5-20% failure
- **Green**: Passing, <5% failure
- **Blue**: Information, neutral status
- **Purple**: Special actions (user input needed)

---

## 🔌 Integration Points

### Existing SPEK Platform
- AgentContract interface
- EnhancedLightweightProtocol
- GovernanceDecisionEngine
- Analyzer (theater, quality, NASA)
- GitHub SPEC KIT
- Context DNA

### New Components Needed
- **Atlantis UI** (Next.js frontend)
- **Project Vectorization Service** (embeddings)
- **3D Visualization Engine** (Three.js)
- **WebSocket Server** (real-time updates)
- **Task Queue System** (BullMQ)
- **Sandbox Service** (Docker runner)
- **Documentation Organizer** (markdown cleanup)

### MCP Servers Used
- GitHub MCP (repo, projects, issues)
- Chrome MCP (Playwright screenshots)
- Memory MCP (cross-agent state)
- Filesystem MCP (project indexing)

---

## 📈 Success Metrics

### Loop 1
- Failure rate trajectory (aim: <5% within 10 iterations)
- Research artifacts collected (GitHub repos, papers)
- Pre-mortem quality (number of issues identified)

### Loop 2
- Task completion rate (per princess, per phase)
- Audit pass rate (theater, production, quality)
- Average retries per task
- Phase duration

### Loop 3
- Final quality score (100% target)
- Documentation accuracy (% matching code)
- GitHub integration success
- Export success rate

### Overall
- Time to project completion
- User satisfaction (post-project survey)
- Code quality maintained (6 months post-launch)

---

## 🚧 Technical Challenges

### Identified Challenges
1. **File system access in browser** - Requires Electron wrapper OR server-side handling
2. **Project vectorization at scale** - Large codebases may take minutes
3. **Real-time agent communication** - WebSocket scaling, reconnection handling
4. **3D rendering performance** - Optimize Three.js for large task graphs
5. **Sandbox security** - Docker isolation, resource limits
6. **GitHub API rate limits** - Caching, batch operations
7. **Documentation accuracy** - Comparing docs to code reliably

### Proposed Solutions
1. **Electron wrapper** for desktop app with file access
2. **Incremental indexing** + cache layer (Redis)
3. **Socket.io with Redis adapter** for horizontal scaling
4. **Level-of-detail rendering** in Three.js (LOD)
5. **Docker with resource limits**, network isolation
6. **GraphQL batching** + aggressive caching
7. **AST comparison** + LLM validation for doc accuracy

---

## 🎯 v7 Integration Plan

### What's New for v7
1. **Atlantis UI** - Complete Next.js frontend (new)
2. **3-Loop System** - Explicit Loop 1/2/3 workflow (refinement of existing)
3. **Princess Hive Model** - Multi-layer agent delegation (refinement of existing)
4. **3-Stage Audit** - Theater → Production → Quality (new enforcement)
5. **Project Vectorization** - Caching, graph generation (new)
6. **UI Validation** - Playwright screenshots, visual diff (new)
7. **Documentation Cleanup** - Automated markdown organization (new)

### What Stays from v6
- AgentContract interface
- EnhancedLightweightProtocol
- GovernanceDecisionEngine
- 22 agent roster
- NASA POT10 compliance
- Analyzer infrastructure
- GitHub SPEC KIT

### Integration Strategy
- **Week 3-4**: Core system (as planned) + Atlantis backend API
- **Week 5-6**: Atlantis UI foundation (Next.js, routing, basic components)
- **Week 7-8**: Loop 1 visualization + Project vectorization
- **Week 9-10**: Loop 2 execution village + Audit system
- **Week 11-12**: Loop 3 finalization + Documentation cleanup
- **Week 13-14**: 3D visualizations (Three.js)
- **Week 15-16**: UI polish, testing, production validation

---

**Next Steps**:
1. Create v7 SPEC document with Atlantis UI requirements
2. Create v7 PLAN document with 24-week timeline including UI phases
3. Pre-mortem v7 for failure points
4. Research identified issues
5. Create v8 SPEC/PLAN incorporating research findings

**Prepared By**: Claude Sonnet 4
**Date**: 2025-10-08
**Status**: User story breakdown complete - Ready for v7 SPEC/PLAN creation
