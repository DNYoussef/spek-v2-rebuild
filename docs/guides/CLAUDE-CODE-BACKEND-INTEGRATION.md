# Claude Code Backend Integration

**Version**: 8.2.0 (Week 26)
**Date**: 2025-10-11
**Status**: IMPLEMENTATION GUIDE

---

## 🎯 System Architecture

This document explains how **THIS Claude Code instance** acts as the Queen agent backend.

### The Flow

```
User (UI) → Flask Server → .claude_messages/ → THIS Claude Code (Queen)
                                                         ↓
                                        Uses Task tool to spawn Princess agents
                                                         ↓
                                        Princess spawns Drone agents via Task tool
                                                         ↓
                                        Results flow back → Flask → UI (WebSocket)
```

###  Key Concept

**Each Task tool invocation spawns a NEW Claude Code instance.**

- **Queen** = THIS Claude Code instance you're talking to right now
- **Princess** = New Claude Code instance spawned via Task tool
- **Drone** = New Claude Code instance spawned by Princess via Task tool

---

## 🚀 How to Activate This System

### Step 1: Start Flask Backend

```bash
python claude_backend_server.py
```

This starts:
- REST API at `http://localhost:5000`
- WebSocket server for real-time updates

### Step 2: Start Atlantis UI

```bash
cd atlantis-ui
npm run dev
```

UI will be at `http://localhost:3000`

### Step 3: Claude Code as Queen

**IMPORTANT**: This step requires the human operator (you) to manually trigger.

When a message arrives in `.claude_messages/`:

1. **Option A: Manual Processing** (Week 26 MVP)
   - Run: `python scripts/claude_message_monitor.py --once`
   - This reads the message and prints instructions
   - YOU (the human) then tell THIS Claude Code instance to process it
   - Example: "Process the message from .claude_messages/message-123.json"

2. **Option B: Automated Processing** (Future - requires Claude API)
   - Setup Claude API key
   - Message monitor automatically sends to Claude API
   - Claude processes and responds

---

## 👑 Queen's Workflow (This Claude Code Instance)

When you (the user) send a message in the UI, here's what happens:

### 1. Message Arrival

```
UI Chat → HTTP POST localhost:5000/api/monarch/chat
       → Flask writes to .claude_messages/message-123.json
```

### 2. Human Operator Alert

```
$ python scripts/claude_message_monitor.py --once

📨 New message detected:
   Task ID: task-1234567890
   Message: "Create a Python calculator app"
   Project: New Project

📋 Instructions for Claude Code:
   Tell Claude: "Process task-1234567890: Create a Python calculator app"
```

### 3. Queen Processing (You tell THIS Claude Code)

You say: **"Process task-1234567890: Create a Python calculator app"**

THIS Claude Code (Queen) does:

```python
from src.agents.queen_orchestrator import QueenOrchestrator

queen = QueenOrchestrator(project_context={...})
result = queen.process_request("Create a Python calculator app", "task-1234567890")

# Result contains:
# - Which Princess to spawn (princess-dev)
# - What prompt to give the Princess
# - Instructions for using Task tool
```

### 4. Queen Spawns Princess (You use Task tool)

Queen responds with:

```
👑 I need to delegate this to Princess-Dev.

Please use Task tool to spawn:
- subagent_type: "princess-dev"
- description: "Development coordination"
- prompt: "[detailed Princess instructions]"
```

**You then invoke the Task tool** in this Claude Code session:

```
Task tool:
  subagent_type: princess-dev
  description: Coordinate calculator app development
  prompt: """
  You are Princess-Dev. Build a Python calculator app.

  Steps:
  1. Spawn Coder agent (Task tool)
  2. Spawn Tester agent (Task tool)
  3. Spawn Reviewer agent (Task tool)
  4. Aggregate results
  5. Report back to Queen
  """
```

### 5. Princess Spawns Drones (Automatic via Task tool)

The Princess Claude Code instance uses Task tool to spawn:
- **Coder** drone: "Write calculator.py"
- **Tester** drone: "Write test_calculator.py"
- **Reviewer** drone: "Review code quality"

Each Drone is a NEW Claude Code instance.

### 6. Results Flow Back

```
Drone (Coder) → Princess → Queen → Flask → UI (WebSocket)
```

---

## 🔧 Flask Backend Enhancements Needed

### New Endpoints

1. **POST /api/claude/agent-spawned**
   - Called when Queen spawns Princess
   - Broadcasts via WebSocket to UI

2. **POST /api/claude/task-progress**
   - Called periodically with progress updates
   - Shows 0-100% completion

3. **POST /api/claude/task-completed**
   - Called when all Drones finish
   - Contains final results

### WebSocket Events

```javascript
// UI listens for these events

socket.on('agent:spawned', (data) => {
  // data: { agentId: 'princess-dev', taskId: 'task-123', loop: 'loop2' }
  // Update sidebar to show Princess is working
});

socket.on('agent:progress', (data) => {
  // data: { agentId: 'coder', progress: 50, message: 'Writing functions...' }
  // Update progress bar
});

socket.on('agent:completed', (data) => {
  // data: { agentId: 'coder', result: {...} }
  // Mark agent as done
});
```

---

## 📋 Detailed Example: "Create a Todo App"

### Step 1: User Types in UI

```
MonarchChat: "Create a todo app with Python Flask backend"
```

### Step 2: Flask Receives

```python
# claude_backend_server.py
@app.route('/api/monarch/chat', methods=['POST'])
def monarch_chat():
    message = request.json['message']  # "Create a todo app..."

    # Write to .claude_messages/
    write_message_for_claude({
        "type": "user_message",
        "task_id": "task-999",
        "message": message,
        "project": {...}
    })
```

### Step 3: Human Operator Notified

```bash
$ python scripts/claude_message_monitor.py --once

📨 MESSAGE READY FOR CLAUDE CODE
Task: task-999
Message: "Create a todo app with Python Flask backend"

🤖 TELL CLAUDE CODE:
"Process task-999: Create a todo app with Python Flask backend"
```

### Step 4: Queen (This Claude Code) Processes

**Human says to Claude**: "Process task-999: Create a todo app with Python Flask backend"

**Claude (Queen) responds**:

```
👑 Analyzing your request...

📊 Analysis:
- Intent: Development & Implementation
- Loop: Loop 2 (Execution)
- Princess needed: princess-dev

🔮 Delegating to Princess-Dev...

Please use Task tool with these parameters:

subagent_type: princess-dev
description: Build todo app with Flask
prompt: """
You are Princess-Dev. Your task: Create a todo app with Python Flask backend.

Project Context:
- Type: New project
- Name: Todo App

Steps:
1. Use Task tool to spawn Coder agent: "Write Flask backend for todo app"
2. Use Task tool to spawn Tester agent: "Write tests for todo app"
3. Use Task tool to spawn Reviewer agent: "Review todo app code"
4. Aggregate results
5. Report back to Queen
"""
```

### Step 5: Human Invokes Task Tool

**Human clicks Task tool in Claude Code UI**:

```
Tool: Task
Parameters:
  subagent_type: princess-dev
  description: Build todo app
  prompt: [paste from above]
```

**New Claude Code instance spawns** (Princess-Dev).

### Step 6: Princess-Dev Spawns Drones

**Princess-Dev Claude Code instance** uses Task tool 3 times:

```
// Princess-Dev's actions:

1. Task tool → spawn Coder
   Result: "I've written app.py and models.py"

2. Task tool → spawn Tester
   Result: "I've written 15 tests, all passing"

3. Task tool → spawn Reviewer
   Result: "Code looks good, 98% NASA compliance"
```

### Step 7: Princess-Dev Reports to Queen

**Princess-Dev** writes result to Flask:

```python
requests.post('http://localhost:5000/api/claude/task-completed', json={
    "taskId": "task-999",
    "princess": "princess-dev",
    "drones": ["coder", "tester", "reviewer"],
    "result": {
        "files_created": ["app.py", "models.py", "test_app.py"],
        "tests_passed": 15,
        "nasa_compliance": 98
    }
})
```

### Step 8: Flask Broadcasts to UI

```javascript
// UI receives WebSocket event
socket.emit('task:completed', {
    taskId: 'task-999',
    message: '✅ Todo app created! 15 tests passing.',
    files: ['app.py', 'models.py', 'test_app.py']
});
```

### Step 9: UI Displays Result

```
MonarchChat displays:

👑 Queen: Task complete!

✅ Princess-Dev coordinated 3 agents:
   - Coder: Created app.py, models.py
   - Tester: Wrote 15 tests (all passing)
   - Reviewer: 98% NASA compliance

📁 Files created: app.py, models.py, test_app.py

🎉 Your todo app is ready!
```

---

## 🎨 UI Integration Points

### Sidebar: Agent Status Monitor

```tsx
// atlantis-ui/src/components/agents/AgentStatusMonitor.tsx

const [agents, setAgents] = useState([
  { id: 'queen', name: 'Queen', status: 'idle', emoji: '👑' },
  { id: 'princess-dev', name: 'Princess Dev', status: 'idle', emoji: '💎' },
  // ... more agents
]);

socket.on('agent:status', (data) => {
  // Update agent status (idle → working → completed)
  setAgents(prev =>
    prev.map(a =>
      a.id === data.agentId
        ? { ...a, status: data.status, currentTask: data.task }
        : a
    )
  );
});
```

### Chat: Monarch Interface

```tsx
// atlantis-ui/src/components/chat/MonarchChat.tsx

socket.on('monarch:message', (data) => {
  setMessages(prev => [...prev, {
    role: 'assistant',
    content: data.content,
    agentsSpawned: data.agentsSpawned, // ['princess-dev']
    timestamp: data.timestamp
  }]);
});
```

---

## 🚧 Current Limitations & Future Improvements

### Current (Week 26 MVP)

- **Manual Triggering**: Human operator must tell Claude Code to process messages
- **No Real-Time Progress**: Princess/Drones work independently, no progress updates
- **Basic Error Handling**: If Drone fails, no automatic retry

### Future (Post-Week 26)

- **Claude API Integration**: Automatic message processing
- **Progress Streaming**: Real-time updates from Drones
- **Smart Retries**: Auto-retry failed Drones
- **Context DNA Integration**: All messages/results stored in SQLite + Pinecone

---

## ✅ Testing Checklist

### Basic Flow Test

- [ ] UI sends message → Flask receives → .claude_messages/ created
- [ ] Human runs monitor → Message details printed
- [ ] Human tells Claude Code → Queen processes
- [ ] Queen returns Princess instructions
- [ ] Human uses Task tool → Princess spawns
- [ ] Princess uses Task tool → Drones spawn
- [ ] Results flow back to UI

### WebSocket Test

- [ ] UI connects to Flask WebSocket
- [ ] Agent status updates appear in sidebar
- [ ] Task progress shows in chat
- [ ] Completion notification appears

### Multi-Agent Test

- [ ] Princess spawns 3+ Drones concurrently
- [ ] All Drones complete successfully
- [ ] Results aggregated correctly

---

## 📚 Related Documents

- **WEEK-25-UI-COMPLETION-SUMMARY.md**: UI implementation complete
- **queen_orchestrator.py**: Queen decision logic
- **claude_message_monitor.py**: Message monitoring script
- **claude_backend_server.py**: Flask + WebSocket server

---

**Status**: 📋 Implementation guide complete - Ready for Week 26 execution
**Next**: Enhance Flask backend with new endpoints + WebSocket events
