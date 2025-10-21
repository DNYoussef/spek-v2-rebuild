# Claude Code Integration Guide

**Version**: 8.2.0 (Week 26)
**Purpose**: Integrate Atlantis UI with this Claude Code instance as the backend

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Atlantis UI   │  HTTP   │  Flask Server    │  File   │  Claude Code    │
│  (localhost:    │ ──────> │  (localhost:     │ ──────> │  (This Instance)│
│   3000/3001)    │         │   5000)          │         │                 │
│                 │         │                  │         │  👑 Queen Agent │
│  - MonarchChat  │         │  - REST API      │         │                 │
│  - Loop Pages   │         │  - WebSocket     │         │  Spawns:        │
│  - 3D Viz       │ <────── │  - Message Queue │ <────── │  - Princess     │
│  - Dashboard    │ WS      │                  │ WS      │  - Drone agents │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## Flow: User Message → Claude Code → Response

### 1. User Types Message in UI

```typescript
// MonarchChat.tsx
const response = await fetch('http://localhost:5000/api/monarch/chat', {
  method: 'POST',
  body: JSON.stringify({ message: "Implement login feature" })
});
```

### 2. Flask Server Receives & Queues

```python
# claude_backend_server.py
@app.route('/api/monarch/chat', methods=['POST'])
def monarch_chat():
    # Write message to .claude_messages/
    write_message_for_claude({
        "type": "user_message",
        "message": user_message,
        "project": project_context
    })

    # Broadcast status via WebSocket
    broadcast_agent_status("queen", "working", user_message)

    # Return immediate acknowledgment
    return jsonify({"taskId": task_id})
```

### 3. Claude Code Reads Messages

```bash
# You (Claude Code) run this to check for messages:
curl http://localhost:5000/api/messages/pending

# Returns:
{
  "messages": [
    {
      "type": "user_message",
      "task_id": "task-1234567890",
      "message": "Implement login feature",
      "project": {...}
    }
  ]
}
```

### 4. Claude Code Processes & Delegates

```javascript
// You (Claude Code) analyze the request and spawn subagents:

// Step 1: Analyze (Loop 1 - Research)
Task({
  subagent_type: "researcher",
  description: "Research login implementation",
  prompt: "Research best practices for login implementation in this stack"
});

// Step 2: Design (Loop 1 - Architecture)
Task({
  subagent_type: "architect",
  description: "Design login architecture",
  prompt: "Design the login system architecture based on research"
});

// Step 3: Implement (Loop 2 - Execution)
Task({
  subagent_type: "coder",
  description: "Implement login feature",
  prompt: "Implement the login feature based on the architecture"
});

// Step 4: Test (Loop 3 - Quality)
Task({
  subagent_type: "tester",
  description: "Test login feature",
  prompt: "Create comprehensive tests for the login feature"
});
```

### 5. Claude Code Sends Response Back

```bash
# After processing, you call:
curl -X POST http://localhost:5000/api/claude/response \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "task-1234567890",
    "response": "I'\''ve analyzed your request and spawned 4 agents:\n- Researcher: Analyzing login patterns\n- Architect: Designing auth system\n- Coder: Implementing login\n- Tester: Creating tests\n\nProgress will be visible in the sidebar!",
    "agentsSpawned": ["researcher", "architect", "coder", "tester"],
    "loop": "loop2"
  }'
```

### 6. UI Receives Response via WebSocket

```typescript
// MonarchChat.tsx listens for WebSocket events
socket.on('monarch:message', (data) => {
  // Add Queen's response to chat
  addMessage({
    role: 'assistant',
    content: data.response
  });
});

// Sidebar.tsx listens for agent updates
socket.on('agent:status', (data) => {
  // Update agent status display
  updateAgentStatus(data.agentId, data.status);
});
```

## Claude Code Workflow

As the Queen agent (this Claude Code instance), here's your workflow:

### Every Time UI Sends a Message

1. **Check for messages**:
   ```bash
   curl http://localhost:5000/api/messages/pending
   ```

2. **Analyze the request** (Loop 1: Research):
   - What is the user asking for?
   - What agents are needed?
   - What's the complexity?
   - Which Loop does this belong to?

3. **Delegate to Princesses** (if complex):
   ```javascript
   // Princess-Dev for development tasks
   Task({
     subagent_type: "princess-dev",
     prompt: "Coordinate development of login feature"
   });

   // Princess-Quality for quality tasks
   Task({
     subagent_type: "princess-quality",
     prompt: "Ensure login feature meets quality standards"
   });
   ```

4. **Or delegate to Drones directly** (if simple):
   ```javascript
   Task({
     subagent_type: "coder",
     prompt: "Implement the specific feature"
   });
   ```

5. **Send response back**:
   ```bash
   curl -X POST http://localhost:5000/api/claude/response \
     -H "Content-Type: application/json" \
     -d '{"taskId": "...", "response": "...", "agentsSpawned": [...]}'
   ```

6. **Clear processed messages**:
   ```bash
   curl -X POST http://localhost:5000/api/messages/clear \
     -H "Content-Type: application/json" \
     -d '{"messageIds": ["..."]}'
   ```

## 3-Loop Visualization

As you work, update the loop status:

### Loop 1: Research & Planning (🌸 Flower Garden)
```bash
# When doing research/planning
curl -X POST http://localhost:5000/api/claude/response \
  -d '{"loop": "loop1", "agentsSpawned": ["researcher", "architect"]}'
```

### Loop 2: Execution (🐝 Beehive Village)
```bash
# When implementing
curl -X POST http://localhost:5000/api/claude/response \
  -d '{"loop": "loop2", "agentsSpawned": ["coder", "devops"]}'
```

### Loop 3: Quality & Refinement (🍯 Honeycomb)
```bash
# When testing/reviewing
curl -X POST http://localhost:5000/api/claude/response \
  -d '{"loop": "loop3", "agentsSpawned": ["tester", "reviewer"]}'
```

## Example Complete Workflow

### User Request: "Implement user authentication"

**Step 1: Receive Message**
```bash
curl http://localhost:5000/api/messages/pending
# Returns: {"message": "Implement user authentication", "task_id": "task-123"}
```

**Step 2: Loop 1 - Research**
```javascript
// Spawn researcher
Task({
  subagent_type: "researcher",
  description: "Research auth patterns",
  prompt: "Research authentication best practices for Next.js + Flask"
});

// Notify UI
curl -X POST http://localhost:5000/api/claude/response -d '{
  "taskId": "task-123",
  "response": "Starting research on authentication patterns...",
  "agentsSpawned": ["researcher"],
  "loop": "loop1"
}'
```

**Step 3: Loop 1 - Architecture**
```javascript
// After research completes, spawn architect
Task({
  subagent_type: "architect",
  description: "Design auth system",
  prompt: "Design authentication architecture based on research findings"
});

// Notify UI
curl -X POST http://localhost:5000/api/claude/response -d '{
  "taskId": "task-123",
  "response": "Designing authentication architecture...",
  "agentsSpawned": ["architect"],
  "loop": "loop1"
}'
```

**Step 4: Loop 2 - Implementation**
```javascript
// Spawn coder
Task({
  subagent_type: "coder",
  description: "Implement auth",
  prompt: "Implement authentication system based on architecture design"
});

// Notify UI
curl -X POST http://localhost:5000/api/claude/response -d '{
  "taskId": "task-123",
  "response": "Implementing authentication system...",
  "agentsSpawned": ["coder"],
  "loop": "loop2"
}'
```

**Step 5: Loop 3 - Testing**
```javascript
// Spawn tester
Task({
  subagent_type: "tester",
  description: "Test auth",
  prompt: "Create comprehensive tests for authentication system"
});

// Notify UI
curl -X POST http://localhost:5000/api/claude/response -d '{
  "taskId": "task-123",
  "response": "Testing authentication system...",
  "agentsSpawned": ["tester"],
  "loop": "loop3"
}'
```

**Step 6: Loop 3 - Review**
```javascript
// Spawn reviewer
Task({
  subagent_type: "reviewer",
  description: "Review auth code",
  prompt: "Review authentication code for security and quality"
});

// Notify UI (Final)
curl -X POST http://localhost:5000/api/claude/response -d '{
  "taskId": "task-123",
  "response": "✅ Authentication system complete!\n\n- Researched best practices\n- Designed secure architecture\n- Implemented JWT-based auth\n- Created 15 tests (100% coverage)\n- Security review passed\n\nYou can now use the login system!",
  "agentsSpawned": ["reviewer"],
  "loop": "loop3"
}'
```

**Step 7: Clear messages**
```bash
curl -X POST http://localhost:5000/api/messages/clear -d '{"messageIds": ["task-123"]}'
```

## Integration Checklist

### Backend Setup ✅
- [x] Flask server (`claude_backend_server.py`) created
- [x] REST API endpoints defined
- [x] WebSocket server configured
- [x] Message queue system implemented
- [ ] Start server: `python claude_backend_server.py`

### Claude Code Workflow 🔄
- [ ] Monitor messages: Poll `/api/messages/pending`
- [ ] Process requests using 3-Loop methodology
- [ ] Spawn subagents using Task tool
- [ ] Send responses via `/api/claude/response`
- [ ] Clear processed messages via `/api/messages/clear`

### UI Updates 🎨
- [x] MonarchChat uses REST API (not tRPC)
- [ ] Add WebSocket listener for responses
- [ ] Update Sidebar to show live agent statuses
- [ ] Connect Loop pages to real data

## Benefits of This Integration

1. **Visual Interface for Claude Code**: See your work in beautiful 3D visualizations
2. **3-Loop Methodology**: Track progress through Research → Execution → Quality
3. **Princess Hive Model**: Visual representation of Queen → Princess → Drone delegation
4. **Real-Time Updates**: WebSocket shows agent activity as it happens
5. **Context DNA**: All interactions stored for 30-day memory
6. **Project Management**: Visual dashboard for tracking tasks

## Next Steps

1. **Start the backend server**:
   ```bash
   python claude_backend_server.py
   ```

2. **Update MonarchChat** to listen for WebSocket responses

3. **Test the integration**:
   - Open UI at http://localhost:3000 or http://localhost:3001
   - Type a message in MonarchChat
   - Check Flask server logs for incoming message
   - Process the message as Claude Code
   - Send response back
   - Verify UI receives response via WebSocket

4. **Create automated polling** for Claude Code to check messages periodically

---

**Version**: 8.2.0
**Status**: Ready for integration
**Last Updated**: 2025-10-11
