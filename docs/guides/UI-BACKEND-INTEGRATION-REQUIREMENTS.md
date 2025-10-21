# UI → Backend Integration Requirements

**Date**: 2025-10-11
**Status**: UI Complete - Backend Integration Pending
**Version**: 8.1.0 (Week 25)

---

## Overview

The Atlantis UI has been completed with bee hive theming, navigation fixes, and project selection workflow. This document outlines what needs to be connected to the backend Python agents.

---

## Critical Integration Points

### 1. **Project Context Management** 🚨 **HIGH PRIORITY**

**Location**: `app/page.tsx` (Home Page)

**User Flow**:
1. User selects "New Project" OR "Existing Project"
2. If existing → User selects folder from device
3. Project context must be passed to Queen agent
4. Queen must share context with ALL Princess and Drone agents

**Backend Requirements**:
```typescript
// Frontend sends to backend:
interface ProjectContext {
  type: 'new' | 'existing';
  folderPath?: string;  // Only for existing projects
  projectName: string;
  timestamp: Date;
}

// Backend must:
// 1. Store in Context DNA (SQLite)
// 2. Pass to Queen agent initialization
// 3. Queen broadcasts to all Princess agents
// 4. Princesses broadcast to their Drone agents
// 5. All agent communications include project context
```

**API Endpoints Needed**:
- `POST /api/project/new` - Initialize new project
- `POST /api/project/existing` - Analyze existing folder
- `POST /api/project/vectorize` - Vectorize codebase (existing projects)
- `GET /api/project/:id/context` - Retrieve project context

**Python Backend Integration**:
```python
# In Queen agent (__init__ or execute):
def __init__(self, project_context: ProjectContext):
    self.project_context = project_context
    self.working_directory = project_context.folder_path or "."

# In ALL agent communications (EnhancedLightweightProtocol):
message = {
    "task": task_description,
    "project_context": {
        "type": self.queen.project_context.type,
        "working_dir": self.queen.project_context.folder_path,
        "project_name": self.queen.project_context.project_name
    },
    "agent_id": self.agent_id
}
```

---

### 2. **WebSocket Real-Time Updates**

**Location**: Multiple components (Sidebar, Dashboard, Loop Pages)

**Required WebSocket Events**:
```typescript
// Agent status updates
interface AgentStatusEvent {
  type: 'agent:status';
  payload: {
    agentId: string;
    agentName: string;
    status: 'idle' | 'working' | 'completed' | 'error';
    currentTask?: string;
    timestamp: string;
  };
}

// Task progress updates
interface TaskUpdateEvent {
  type: 'task:update';
  payload: {
    taskId: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    progress: number; // 0-100
    assignedAgent: string;
    princessId?: string;
    timestamp: string;
  };
}

// Project analysis progress
interface AnalysisProgressEvent {
  type: 'project:analysis';
  payload: {
    stage: 'vectorizing' | 'indexing' | 'graphing' | 'complete';
    progress: number;
    filesProcessed: number;
    totalFiles: number;
    timestamp: string;
  };
}
```

**Components to Update**:
- `Sidebar` - Show live agent statuses
- `ProjectDashboard` - Show task progress
- `Loop1/2/3` pages - Show workflow progress

---

### 3. **MonarchChat Component Integration**

**Location**: `components/chat/MonarchChat.tsx`

**Backend Requirements**:
- Must connect to Queen agent via tRPC/WebSocket
- Send user messages to Queen
- Receive Queen responses
- Support streaming responses

**API Endpoints**:
```typescript
// tRPC mutations
trpc.monarch.sendMessage.useMutation();
trpc.monarch.getHistory.useQuery();

// WebSocket for streaming
socket.on('monarch:message', (message) => {
  // Append Queen's response to chat
});
```

---

### 4. **Project Analysis Flow** (Existing Projects)

**Location**: `app/page.tsx` → Folder selection

**Backend Workflow**:
1. User selects folder → Frontend sends path
2. Backend starts vectorization:
   - Read all files in folder
   - Generate embeddings (Pinecone + OpenAI)
   - Create structure graph (AST analysis)
   - Store in Context DNA (SQLite)
   - Cache results (Redis)
3. Progress updates via WebSocket
4. On completion → Enable chat with Queen

**Estimated Time**: 15-60 seconds for 10K files (per Week 4 benchmarks)

**API Endpoints**:
```typescript
POST /api/project/analyze
{
  folderPath: string,
  projectName: string
}

// Returns:
{
  analysisId: string,
  status: 'started',
  estimatedTime: number // seconds
}

// WebSocket updates:
'project:analysis' events with progress
```

---

### 5. **Context DNA Storage Integration**

**Location**: Backend ContextDNAStorage service

**What to Store**:
```typescript
// On project selection
await contextDNA.saveProject({
  id: projectId,
  name: projectName,
  description: 'User-selected project',
  repositoryUrl: null,
  createdAt: new Date(),
  lastAccessedAt: new Date(),
  metadata: {
    type: 'new' | 'existing',
    folderPath: folderPath, // if existing
    agentCount: 22,
    loopsCompleted: 0
  }
});

// On every Queen → Princess delegation
await contextDNA.saveTask({
  id: taskId,
  projectId: projectId,
  description: taskDescription,
  status: 'pending',
  assignedTo: 'princess-dev',
  princessId: 'princess-dev',
  droneId: null, // Set when princess delegates
  createdAt: new Date()
});

// On every agent conversation
await contextDNA.saveConversation({
  id: messageId,
  projectId: projectId,
  taskId: taskId,
  role: 'agent', // or 'user'
  agentId: 'queen',
  content: messageContent,
  createdAt: new Date()
});
```

---

### 6. **Loop Page Data Integration**

**Loop 1 Page** (`app/loop1/page.tsx`):
- Show research artifacts
- Show pre-mortem scenarios
- Show failure rate trajectory
- Connect to `ResearchArtifactDisplay` component

**Loop 2 Page** (`app/loop2/page.tsx`):
- Show active Princess agents
- Show Drone task assignments
- Show audit pipeline statuses
- Connect to `AgentStatusMonitor` component

**Loop 3 Page** (`app/loop3/page.tsx`):
- Show quality audit results
- Show GitHub integration status
- Show documentation cleanup progress
- Connect to `AuditResultsPanel` component

---

## Implementation Priority

### Phase 1: Critical (Week 25) 🚨
1. ✅ UI Complete - Navigation, theming, folder selection
2. **Project context passing** - Queen → Princess → Drones
3. **Folder analysis API** - Vectorize existing projects
4. **Basic WebSocket setup** - Agent status updates

### Phase 2: High Priority (Week 26)
1. MonarchChat ↔ Queen agent integration
2. Real-time agent status in Sidebar
3. Task progress tracking
4. Context DNA storage for all operations

### Phase 3: Medium Priority (Post-Launch)
1. Loop page real data integration
2. Advanced WebSocket events
3. Performance optimization
4. Error handling & retries

---

## Frontend Components Ready for Integration

**Already Implemented** (Just need backend connection):
- ✅ `MonarchChat` - Chat UI ready, needs Queen agent connection
- ✅ `ProjectDashboard` - Dashboard UI ready, needs real metrics
- ✅ `AgentStatusMonitor` - Component exists, needs WebSocket data
- ✅ `ResearchArtifactDisplay` - Component exists, needs Loop 1 data
- ✅ `AuditResultsPanel` - Component exists, needs Loop 3 data
- ✅ `Sidebar` - Shows placeholders, needs WebSocket agent statuses
- ✅ `WebSocketManager` - Client-side manager ready, needs server

**Partially Implemented** (Needs completion):
- ⚠️ Project context global state (React Context or Zustand)
- ⚠️ tRPC client configuration
- ⚠️ Error boundary handling

---

## Example Integration Code

### Frontend → Backend Project Selection

```typescript
// In app/page.tsx
const handleStartAnalysis = async () => {
  setIsLoading(true);

  try {
    // Send project context to backend
    const response = await fetch('/api/project/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: projectChoice, // 'new' | 'existing'
        folderPath: selectedFolder,
        projectName: selectedFolder || 'New Project'
      })
    });

    const { projectId, analysisId } = await response.json();

    // Connect to WebSocket for progress
    socket.emit('subscribe:analysis', { analysisId });
    socket.on('project:analysis', (progress) => {
      console.log(`Analysis: ${progress.progress}%`);
    });

    // On complete, enable chat
    socket.on('project:analysis:complete', () => {
      setIsLoading(false);
      // Show chat interface
    });

  } catch (error) {
    console.error('Analysis failed:', error);
    setIsLoading(false);
  }
};
```

### Backend → All Agents Context Injection

```python
# In Queen agent (src/agents/core/QueenAgent.py)
class QueenAgent(AgentBase):
    def __init__(self, project_context: ProjectContext):
        super().__init__(...)
        self.project_context = project_context
        self.working_directory = project_context.folder_path or os.getcwd()

    async def delegate_to_princess(self, task: Task, princess_type: str):
        # Inject project context into task
        enhanced_task = {
            **task,
            "project_context": {
                "type": self.project_context.type,
                "working_dir": self.working_directory,
                "project_name": self.project_context.project_name,
                "project_id": self.project_context.id
            }
        }

        # Send to Princess agent
        princess = self.get_princess(princess_type)
        result = await princess.execute(enhanced_task)
        return result

# In Princess agents (src/agents/swarm/Princess*.py)
class PrincessDevAgent(AgentBase):
    async def delegate_to_drone(self, task: Task, drone_type: str):
        # Extract project context from task
        project_context = task["project_context"]

        # Pass to Drone agent with context
        drone = self.get_drone(drone_type)
        result = await drone.execute({
            **task,
            "project_context": project_context,
            "working_directory": project_context["working_dir"]
        })
        return result

# In Drone agents (src/agents/core/Coder*.py, Tester*.py, etc.)
class CoderAgent(AgentBase):
    async def execute(self, task: Task):
        # Use project context to know where to work
        project_context = task.get("project_context", {})
        working_dir = project_context.get("working_dir", ".")

        # All file operations use working_dir as base
        file_path = os.path.join(working_dir, task["file_name"])

        # Write code to correct location
        with open(file_path, 'w') as f:
            f.write(generated_code)
```

---

## Testing Checklist

### Manual Testing
- [ ] Select "New Project" → Chat opens → Queen responds
- [ ] Select "Existing Project" → Folder picker → Analysis progress → Chat opens
- [ ] Navigate between Loop 1/2/3 pages → Sidebar highlights correctly
- [ ] Send message to Queen → Response appears in chat
- [ ] Sidebar shows real agent statuses (from WebSocket)
- [ ] Dashboard shows real task progress (from backend)

### Integration Testing
- [ ] Queen receives project context on initialization
- [ ] Princess agents receive project context from Queen
- [ ] Drone agents receive project context from Princesses
- [ ] All file operations use correct working directory
- [ ] Context DNA stores all conversations and tasks

---

## Next Steps

1. **Week 25 Remaining**:
   - Create global project context state (React Context)
   - Connect folder analysis API
   - Setup basic WebSocket server

2. **Week 26**:
   - Full Queen ↔ MonarchChat integration
   - Real-time agent status updates
   - Complete Context DNA storage

3. **Post-Launch**:
   - Loop page data integration
   - Advanced features (streaming, retries)
   - Performance optimization

---

**Document Created**: 2025-10-11
**Author**: Claude Sonnet 4.5
**Status**: ✅ UI Complete - Backend Integration Pending
