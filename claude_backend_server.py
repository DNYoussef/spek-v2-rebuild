"""
SPEK Platform - Claude Code Backend Integration

This server integrates the Atlantis UI with this Claude Code instance.
Claude acts as the Queen agent, delegating tasks to specialized subagents.

Architecture:
- Flask REST API receives messages from UI
- This Claude Code instance processes requests
- Task tool spawns Princess/Drone agents as needed
- WebSocket broadcasts real-time updates to UI
- 3-Loop methodology coordinates workflow

Version: 8.2.0 (Week 26 - Claude Code Integration)
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import queue

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"])

# Message queue for Claude Code to process
# UI sends messages here, Claude Code processes them
message_queue = queue.Queue()
response_queue = queue.Queue()

# Current project context
project_context = {
    "id": None,
    "type": None,  # 'new' | 'existing'
    "folder_path": None,
    "name": None,
    "created_at": None
}

# Active agents (tracked for UI visualization)
active_agents = {
    "queen": {
        "id": "queen",
        "name": "Queen (Claude Code)",
        "status": "idle",
        "emoji": "👑",
        "current_task": None,
        "loop": None
    }
}

# Task tracking
tasks = {}

def broadcast_agent_status(agent_id, status, task=None, loop=None):
    """Broadcast agent status to UI via WebSocket"""
    if agent_id not in active_agents:
        active_agents[agent_id] = {
            "id": agent_id,
            "name": agent_id.replace("_", " ").title(),
            "status": status,
            "emoji": get_agent_emoji(agent_id),
            "current_task": task,
            "loop": loop
        }
    else:
        active_agents[agent_id]["status"] = status
        active_agents[agent_id]["current_task"] = task
        active_agents[agent_id]["loop"] = loop

    socketio.emit('agent:status', {
        "agentId": agent_id,
        "status": status,
        "task": task,
        "loop": loop,
        "timestamp": datetime.now().isoformat()
    })

def get_agent_emoji(agent_id):
    """Get emoji for agent type"""
    emoji_map = {
        "queen": "👑",
        "princess_dev": "💎",
        "princess_quality": "✨",
        "princess_coordination": "🔮",
        "coder": "💼",
        "tester": "🧪",
        "reviewer": "📝",
        "researcher": "🔬",
        "architect": "🏛️",
        "debugger": "🐛",
        "docs_writer": "📚",
        "devops": "🚀"
    }
    return emoji_map.get(agent_id, "🐝")

def broadcast_task_update(task_id, progress, status, message=None):
    """Broadcast task progress to UI"""
    if task_id in tasks:
        tasks[task_id]["progress"] = progress
        tasks[task_id]["status"] = status
        tasks[task_id]["updated_at"] = datetime.now().isoformat()

    socketio.emit('task:update', {
        "taskId": task_id,
        "progress": progress,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "8.2.0",
        "backend": "Claude Code Integration",
        "queen_status": active_agents["queen"]["status"]
    })

@app.route('/api/project/new', methods=['POST'])
def create_new_project():
    """Initialize new project"""
    data = request.get_json()

    project_context["id"] = f"project-{int(time.time())}"
    project_context["type"] = "new"
    project_context["name"] = data.get("name", "New Project")
    project_context["folder_path"] = os.getcwd()
    project_context["created_at"] = datetime.now().isoformat()

    # Notify Claude Code via file
    write_message_for_claude({
        "type": "project_created",
        "project": project_context,
        "timestamp": datetime.now().isoformat()
    })

    broadcast_agent_status("queen", "working", "Initializing new project", "loop1")

    return jsonify({
        "success": True,
        "projectId": project_context["id"],
        "message": "New project initialized. Queen is ready to coordinate!"
    })

@app.route('/api/project/existing', methods=['POST'])
def load_existing_project():
    """
    Load existing project - NO COPYING

    User selects folder in UI, we store file list and metadata.
    Analysis reads from original location via file paths.
    """
    data = request.get_json()
    folder_name = data.get("folderName")
    file_list = data.get("fileList", [])

    print(f"\n{'='*60}")
    print(f"📁 LOADING EXISTING PROJECT")
    print(f"{'='*60}")
    print(f"Folder: {folder_name}")
    print(f"Files: {len(file_list)} detected")
    print(f"Note: NO project copying - reading from original location")
    print(f"{'='*60}\n")

    project_context["id"] = f"project-{int(time.time())}"
    project_context["type"] = "existing"
    project_context["folder_path"] = None  # Browser security: can't access absolute path
    project_context["folder_name"] = folder_name
    project_context["name"] = folder_name
    project_context["file_list"] = file_list  # Store file metadata
    project_context["file_count"] = len(file_list)
    project_context["created_at"] = datetime.now().isoformat()

    # Notify Claude Code
    write_message_for_claude({
        "type": "project_loaded",
        "project": project_context,
        "timestamp": datetime.now().isoformat()
    })

    broadcast_agent_status("queen", "working", "Analyzing existing project", "loop1")

    # Start analysis (Claude Code will receive this)
    socketio.emit('project:analysis', {
        "stage": "started",
        "progress": 0,
        "message": f"Queen is analyzing {len(file_list)} files from {folder_name}..."
    })

    return jsonify({
        "success": True,
        "projectId": project_context["id"],
        "analysisId": f"analysis-{int(time.time())}",
        "fileCount": len(file_list),
        "message": f"Project analysis started for {folder_name} ({len(file_list)} files)!"
    })

@app.route('/api/monarch/chat', methods=['POST'])
def monarch_chat():
    """
    Receive user message and forward to Claude Code (Queen agent)

    This is the main entry point - when user types in the UI,
    this endpoint receives it and Claude Code processes it.
    """
    data = request.get_json()
    user_message = data.get("message")
    project_id = data.get("projectId", project_context.get("id"))

    print(f"\n{'='*60}")
    print(f"📨 MESSAGE FROM UI")
    print(f"{'='*60}")
    print(f"User: {user_message}")
    print(f"Project: {project_id}")
    print(f"{'='*60}\n")

    # Create task
    task_id = f"task-{int(time.time())}"
    tasks[task_id] = {
        "id": task_id,
        "description": user_message,
        "status": "pending",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "project_id": project_id
    }

    # Write message for Claude Code to process
    write_message_for_claude({
        "type": "user_message",
        "task_id": task_id,
        "message": user_message,
        "project": project_context,
        "timestamp": datetime.now().isoformat()
    })

    # Update Queen status
    broadcast_agent_status("queen", "working", user_message, "loop2")
    broadcast_task_update(task_id, 10, "processing", "Queen is analyzing your request...")

    # Return immediate acknowledgment
    # The actual response will come via WebSocket when Claude processes it
    return jsonify({
        "success": True,
        "taskId": task_id,
        "response": "👑 Queen received your message. Processing...",
        "message": "Task queued for processing. Watch the sidebar for agent activity!"
    })

@app.route('/api/claude/response', methods=['POST'])
def claude_response():
    """
    Claude Code calls this endpoint to send responses back to UI

    When Claude finishes processing, it should call this endpoint
    to send the response back to the user via WebSocket.
    """
    data = request.get_json()
    task_id = data.get("taskId")
    response_text = data.get("response")
    agents_spawned = data.get("agentsSpawned", [])
    loop = data.get("loop", "loop2")

    print(f"\n{'='*60}")
    print(f"📤 RESPONSE FROM CLAUDE CODE")
    print(f"{'='*60}")
    print(f"Task: {task_id}")
    print(f"Response: {response_text[:100]}...")
    print(f"Agents spawned: {agents_spawned}")
    print(f"{'='*60}\n")

    # Update task status
    if task_id in tasks:
        broadcast_task_update(task_id, 100, "completed", "Task completed!")

    # Update Queen status
    broadcast_agent_status("queen", "idle", None, None)

    # Update spawned agents
    for agent_id in agents_spawned:
        broadcast_agent_status(agent_id, "working", f"Working on task {task_id}", loop)

    # Send response to UI via WebSocket
    socketio.emit('monarch:message', {
        "role": "assistant",
        "content": response_text,
        "taskId": task_id,
        "agentsSpawned": agents_spawned,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"success": True})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print("🔌 UI connected to WebSocket")
    emit('connection:status', {
        "status": "connected",
        "message": "Welcome to the Hive! Queen is ready."
    })

    # Send current agent statuses
    emit('agents:status', {"agents": active_agents})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print("🔌 UI disconnected from WebSocket")

@socketio.on('subscribe:agents')
def handle_subscribe_agents():
    """Subscribe to agent status updates"""
    emit('agents:status', {"agents": active_agents})

def write_message_for_claude(message_data):
    """
    Write message to file for Claude Code to read and process

    This creates a .claude_messages/ directory with JSON files
    that Claude Code can monitor and process.
    """
    os.makedirs(".claude_messages", exist_ok=True)

    filename = f".claude_messages/message-{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(message_data, f, indent=2)

    print(f"📝 Message written for Claude Code: {filename}")
    return filename

@app.route('/api/messages/pending', methods=['GET'])
def get_pending_messages():
    """
    Claude Code calls this to get pending messages to process

    Returns all unprocessed messages from the UI.
    """
    messages = []
    if os.path.exists(".claude_messages"):
        for filename in os.listdir(".claude_messages"):
            if filename.endswith(".json"):
                filepath = os.path.join(".claude_messages", filename)
                with open(filepath, 'r') as f:
                    messages.append(json.load(f))

    return jsonify({"messages": messages})

@app.route('/api/messages/clear', methods=['POST'])
def clear_processed_messages():
    """
    Clear processed messages

    Claude Code calls this after processing messages.
    """
    data = request.get_json()
    message_ids = data.get("messageIds", [])

    if os.path.exists(".claude_messages"):
        for filename in os.listdir(".claude_messages"):
            os.remove(os.path.join(".claude_messages", filename))

    return jsonify({"success": True, "cleared": len(message_ids)})

@app.route('/api/claude/agent-spawned', methods=['POST'])
def agent_spawned():
    """
    Claude Code calls this when spawning a new agent (Princess or Drone)

    Broadcasts the event to UI via WebSocket so users see agent activity.
    """
    data = request.get_json()
    agent_id = data.get("agentId")
    task_id = data.get("taskId")
    loop = data.get("loop", "loop2")
    parent_agent = data.get("parentAgent", "queen")

    print(f"\n{'='*60}")
    print(f"🐝 AGENT SPAWNED")
    print(f"{'='*60}")
    print(f"Agent: {agent_id}")
    print(f"Parent: {parent_agent}")
    print(f"Task: {task_id}")
    print(f"Loop: {loop}")
    print(f"{'='*60}\n")

    # Update active agents
    broadcast_agent_status(agent_id, "spawned", f"Spawned by {parent_agent}", loop)

    # Broadcast spawn event
    socketio.emit('agent:spawned', {
        "agentId": agent_id,
        "parentAgent": parent_agent,
        "taskId": task_id,
        "loop": loop,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"success": True})

@app.route('/api/claude/task-progress', methods=['POST'])
def task_progress():
    """
    Claude Code calls this to report task progress

    Shows percentage completion (0-100%) and status message.
    """
    data = request.get_json()
    task_id = data.get("taskId")
    agent_id = data.get("agentId")
    progress = data.get("progress", 0)  # 0-100
    message = data.get("message", "")

    print(f"📊 Task Progress: {agent_id} → {progress}% - {message}")

    # Update task
    broadcast_task_update(task_id, progress, "in_progress", message)

    # Update agent status
    broadcast_agent_status(agent_id, "working", message, None)

    return jsonify({"success": True})

@app.route('/api/claude/task-completed', methods=['POST'])
def task_completed():
    """
    Claude Code calls this when a task is complete

    Contains final results from Princess/Drone agents.
    """
    data = request.get_json()
    task_id = data.get("taskId")
    agent_id = data.get("agentId")
    result = data.get("result", {})

    print(f"\n{'='*60}")
    print(f"✅ TASK COMPLETED")
    print(f"{'='*60}")
    print(f"Agent: {agent_id}")
    print(f"Task: {task_id}")
    print(f"Result: {result}")
    print(f"{'='*60}\n")

    # Update task status
    broadcast_task_update(task_id, 100, "completed", "Task completed successfully!")

    # Update agent status
    broadcast_agent_status(agent_id, "completed", None, None)

    # Broadcast completion
    socketio.emit('task:completed', {
        "taskId": task_id,
        "agentId": agent_id,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"success": True})

@app.route('/api/claude/agent-error', methods=['POST'])
def agent_error():
    """
    Claude Code calls this when an agent encounters an error

    Allows graceful error handling and UI notification.
    """
    data = request.get_json()
    agent_id = data.get("agentId")
    task_id = data.get("taskId")
    error_message = data.get("error", "Unknown error")

    print(f"\n{'='*60}")
    print(f"❌ AGENT ERROR")
    print(f"{'='*60}")
    print(f"Agent: {agent_id}")
    print(f"Task: {task_id}")
    print(f"Error: {error_message}")
    print(f"{'='*60}\n")

    # Update agent status
    broadcast_agent_status(agent_id, "error", error_message, None)

    # Broadcast error
    socketio.emit('agent:error', {
        "agentId": agent_id,
        "taskId": task_id,
        "error": error_message,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"success": True})

@app.route('/api/project/analyze', methods=['POST'])
def analyze_project():
    """
    Start project analysis for existing project

    IMPORTANT: This reads from ORIGINAL location, does NOT copy project.
    Uses file list from project_context (provided by UI during folder selection).

    Triggers:
    1. File metadata scan (from UI-provided list)
    2. Pattern detection (code structure, dependencies)
    3. Context DNA creation
    4. Agent spawning for analysis
    """
    data = request.get_json()
    project_id = data.get("projectId", project_context.get("id"))

    # Get project info (no folder_path due to browser security)
    folder_name = project_context.get("folder_name", "Unknown")
    file_list = project_context.get("file_list", [])

    print(f"\n{'='*60}")
    print(f"🔍 PROJECT ANALYSIS STARTED")
    print(f"{'='*60}")
    print(f"Project: {project_id}")
    print(f"Folder: {folder_name}")
    print(f"Files: {len(file_list)}")
    print(f"Note: Reading from ORIGINAL location (no copying)")
    print(f"{'='*60}\n")

    # Create analysis task
    analysis_id = f"analysis-{int(time.time())}"

    # Write message for Claude Code
    write_message_for_claude({
        "type": "project_analysis",
        "analysis_id": analysis_id,
        "project_id": project_id,
        "folder_name": folder_name,
        "file_list": file_list,
        "file_count": len(file_list),
        "timestamp": datetime.now().isoformat()
    })

    # Broadcast analysis start
    socketio.emit('project:analysis', {
        "analysisId": analysis_id,
        "projectId": project_id,
        "stage": "started",
        "progress": 0,
        "message": f"Queen is analyzing {len(file_list)} files from {folder_name}..."
    })

    return jsonify({
        "success": True,
        "analysisId": analysis_id,
        "fileCount": len(file_list),
        "message": f"Analysis started. Queen will spawn agents to analyze {folder_name}."
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🐝 SPEK Platform - Claude Code Backend")
    print("=" * 60)
    print("REST API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    print("Frontend: http://localhost:3000 or http://localhost:3001")
    print("=" * 60)
    print("\n👑 Queen Agent: This Claude Code instance")
    print("📨 Messages from UI will appear below")
    print("🐝 Subagents will be spawned using Task tool")
    print("=" * 60)
    print("\nServer ready! Open the Atlantis UI to start.\n")

    # Run server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
