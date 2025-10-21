"""
SPEK Platform Backend Server (Demo)

Simple Flask server to demonstrate agent integration with Atlantis UI.
This is a minimal implementation for testing the UI - full implementation in Week 26.

Version: 8.1.0 (Week 25 Demo)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os

# Add src to path to import agents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Mock project context (TODO: Connect to real Context DNA storage)
current_project = {
    "id": "demo-project-1",
    "type": None,  # 'new' | 'existing'
    "folder_path": None,
    "name": "Demo Project"
}

# Mock agent statuses
agent_statuses = {
    "queen": {"status": "idle", "name": "Queen", "emoji": "👑"},
    "coder": {"status": "idle", "name": "Coder", "emoji": "💼"},
    "tester": {"status": "idle", "name": "Tester", "emoji": "🧪"},
    "reviewer": {"status": "idle", "name": "Reviewer", "emoji": "📝"},
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "8.1.0"})

@app.route('/api/project/new', methods=['POST'])
def create_new_project():
    """Initialize new project"""
    data = request.get_json()
    current_project["type"] = "new"
    current_project["name"] = data.get("name", "New Project")
    current_project["id"] = f"project-{id(current_project)}"

    # TODO: Initialize Queen agent with project context
    print(f"📝 New project created: {current_project['name']}")

    return jsonify({
        "success": True,
        "projectId": current_project["id"],
        "message": "New project initialized! Queen is ready to help."
    })

@app.route('/api/project/existing', methods=['POST'])
def load_existing_project():
    """Load existing project from folder"""
    data = request.get_json()
    folder_path = data.get("folderPath")

    current_project["type"] = "existing"
    current_project["folder_path"] = folder_path
    current_project["name"] = os.path.basename(folder_path)
    current_project["id"] = f"project-{id(current_project)}"

    # TODO: Start vectorization process
    print(f"📁 Loading project from: {folder_path}")

    # Emit progress updates via WebSocket
    socketio.emit('project:analysis', {
        "stage": "started",
        "progress": 0,
        "message": "Queen is analyzing your codebase..."
    })

    return jsonify({
        "success": True,
        "projectId": current_project["id"],
        "analysisId": f"analysis-{id(current_project)}",
        "message": "Project analysis started!"
    })

@app.route('/api/monarch/chat', methods=['POST'])
def monarch_chat():
    """Send message to Queen agent"""
    data = request.get_json()
    user_message = data.get("message")

    # TODO: Send to actual Queen agent
    print(f"👤 User: {user_message}")

    # Mock Queen response
    queen_response = f"👑 Queen: I received your message '{user_message}'. I'm ready to help coordinate your project!"

    print(f"👑 Queen: {queen_response}")

    # Emit to WebSocket for real-time update
    socketio.emit('monarch:message', {
        "role": "assistant",
        "content": queen_response,
        "timestamp": "2025-10-11T00:00:00Z"
    })

    return jsonify({
        "success": True,
        "response": queen_response
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print("🔌 Client connected to WebSocket")
    emit('connection:status', {"status": "connected", "message": "Welcome to the Hive!"})

    # Send initial agent statuses
    emit('agents:status', {"agents": agent_statuses})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print("🔌 Client disconnected from WebSocket")

@socketio.on('subscribe:agents')
def handle_subscribe_agents():
    """Subscribe to agent status updates"""
    emit('agents:status', {"agents": agent_statuses})

if __name__ == '__main__':
    print("=" * 60)
    print("SPEK Platform Backend Server (Demo)")
    print("=" * 60)
    print("REST API: http://localhost:5000")
    print("WebSocket: ws://localhost:5000")
    print("Frontend: http://localhost:3000")
    print("=" * 60)
    print("\nServer ready! Connect from Atlantis UI.\n")

    # Run server (socketio.run handles both HTTP and WebSocket)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
