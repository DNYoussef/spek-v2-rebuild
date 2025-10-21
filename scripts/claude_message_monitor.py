"""
Claude Message Monitor

Monitors .claude_messages/ directory for incoming messages from the UI.
When a message arrives, this script:
1. Reads the JSON message
2. Formats it as a prompt for Claude Code (this instance)
3. Processes the request through Queen orchestrator
4. Sends response back to Flask server

This is the bridge between the Flask backend and Claude Code.

Version: 8.2.0 (Week 26)
"""

import os
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ClaudeMessageMonitor:
    """Monitors .claude_messages/ and processes incoming messages."""

    def __init__(self, messages_dir: str = ".claude_messages", flask_url: str = "http://localhost:5000"):
        self.messages_dir = Path(messages_dir)
        self.flask_url = flask_url
        self.processed_messages = set()

        # Create messages directory if it doesn't exist
        self.messages_dir.mkdir(exist_ok=True)

        print(f"📡 Claude Message Monitor initialized")
        print(f"   Watching: {self.messages_dir.absolute()}")
        print(f"   Flask backend: {flask_url}")

    def get_pending_messages(self) -> list[Path]:
        """Get all unprocessed message files."""
        message_files = []

        if not self.messages_dir.exists():
            return message_files

        for filepath in self.messages_dir.glob("message-*.json"):
            if filepath.name not in self.processed_messages:
                message_files.append(filepath)

        return sorted(message_files)

    def read_message(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Read and parse a message file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return None

    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message through Queen orchestrator.

        This is where we hand off to the Queen agent to:
        1. Analyze the request
        2. Determine which agents to spawn
        3. Coordinate the work
        4. Aggregate results
        """
        message_type = message_data.get("type")

        if message_type == "user_message":
            return self.process_user_message(message_data)
        elif message_type == "project_created":
            return self.process_project_created(message_data)
        elif message_type == "project_loaded":
            return self.process_project_loaded(message_data)
        else:
            return {
                "success": False,
                "error": f"Unknown message type: {message_type}"
            }

    def process_user_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user message from the chat interface.

        This is the main entry point - user typed something in MonarchChat.
        """
        task_id = message_data.get("task_id")
        user_message = message_data.get("message")
        project_context = message_data.get("project", {})

        print(f"\n{'='*60}")
        print(f"👑 QUEEN PROCESSING MESSAGE")
        print(f"{'='*60}")
        print(f"Task ID: {task_id}")
        print(f"Message: {user_message}")
        print(f"Project: {project_context.get('name', 'None')}")
        print(f"{'='*60}\n")

        # Import Queen orchestrator
        try:
            from src.agents.queen_orchestrator import QueenOrchestrator

            # Create Queen instance
            queen = QueenOrchestrator(project_context=project_context)

            # Process the request
            result = queen.process_request(user_message, task_id)

            return {
                "success": True,
                "task_id": task_id,
                "response": result["response"],
                "agents_spawned": result.get("agents_spawned", []),
                "loop": result.get("loop", "loop2")
            }

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "task_id": task_id,
                "response": f"Error: {str(e)}",
                "error": str(e)
            }

    def process_project_created(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new project initialization."""
        project = message_data.get("project", {})

        print(f"\n🌸 NEW PROJECT INITIALIZED")
        print(f"   Name: {project.get('name')}")
        print(f"   Path: {project.get('folder_path')}")

        # For new projects, we'll start with Loop 1 (Research & Planning)
        return {
            "success": True,
            "message": "New project initialized. Ready for Loop 1 (Research & Planning).",
            "next_loop": "loop1"
        }

    def process_project_loaded(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle existing project loading."""
        project = message_data.get("project", {})

        print(f"\n📁 EXISTING PROJECT LOADED")
        print(f"   Name: {project.get('name')}")
        print(f"   Path: {project.get('folder_path')}")

        # For existing projects, we need to analyze the codebase
        # This would trigger vectorization and Context DNA creation
        return {
            "success": True,
            "message": "Analyzing existing project. This may take a moment...",
            "analysis_started": True
        }

    def send_response_to_flask(self, response_data: Dict[str, Any]) -> bool:
        """Send processed response back to Flask server."""
        try:
            url = f"{self.flask_url}/api/claude/response"

            # Add required fields if missing
            if "taskId" not in response_data and "task_id" in response_data:
                response_data["taskId"] = response_data["task_id"]

            resp = requests.post(url, json=response_data, timeout=5)

            if resp.status_code == 200:
                print(f"✅ Response sent to Flask successfully")
                return True
            else:
                print(f"❌ Flask server error: {resp.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error sending to Flask: {e}")
            return False

    def cleanup_message(self, filepath: Path):
        """Mark message as processed and optionally delete."""
        self.processed_messages.add(filepath.name)

        # Optionally delete the file
        try:
            filepath.unlink()
            print(f"🗑️  Cleaned up: {filepath.name}")
        except Exception as e:
            print(f"⚠️  Could not delete {filepath.name}: {e}")

    def run_once(self):
        """Process all pending messages once."""
        messages = self.get_pending_messages()

        if not messages:
            return 0

        processed_count = 0

        for filepath in messages:
            print(f"\n📨 Processing: {filepath.name}")

            # Read message
            message_data = self.read_message(filepath)
            if not message_data:
                continue

            # Process message
            result = self.process_message(message_data)

            # Send response back to Flask
            if result.get("success"):
                self.send_response_to_flask(result)

            # Cleanup
            self.cleanup_message(filepath)
            processed_count += 1

        return processed_count

    def run_loop(self, interval: float = 1.0):
        """Run continuous monitoring loop."""
        print(f"\n🔄 Starting monitoring loop (checking every {interval}s)")
        print("   Press Ctrl+C to stop\n")

        try:
            while True:
                self.run_once()
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitor stopped by user")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Claude Message Monitor")
    parser.add_argument("--messages-dir", default=".claude_messages", help="Directory to monitor")
    parser.add_argument("--flask-url", default="http://localhost:5000", help="Flask backend URL")
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")

    args = parser.parse_args()

    monitor = ClaudeMessageMonitor(
        messages_dir=args.messages_dir,
        flask_url=args.flask_url
    )

    if args.once:
        count = monitor.run_once()
        print(f"\n✅ Processed {count} messages")
    else:
        monitor.run_loop(interval=args.interval)


if __name__ == "__main__":
    main()
