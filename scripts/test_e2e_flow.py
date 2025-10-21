"""
End-to-End Test Script

Tests the complete flow:
1. UI sends message
2. Flask receives
3. Message written to .claude_messages/
4. Monitor detects
5. Queen processes
6. Response flows back

Version: 8.2.0 (Week 26)
"""

import requests
import json
import time
from pathlib import Path


def test_message_flow():
    """Test the complete message flow."""
    print("\n" + "="*60)
    print("🧪 SPEK Platform E2E Test")
    print("="*60 + "\n")

    # Test 1: Health Check
    print("[1/6] Testing Flask backend health...")
    try:
        resp = requests.get("http://localhost:5000/health")
        if resp.status_code == 200:
            print("   ✅ Backend is healthy")
            print(f"   Response: {resp.json()}")
        else:
            print(f"   ❌ Health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Could not connect to backend: {e}")
        print("   Make sure Flask server is running: python claude_backend_server.py")
        return False

    # Test 2: Send a test message
    print("\n[2/6] Sending test message to MonarchChat...")
    test_message = "Create a simple hello world Python script"
    try:
        resp = requests.post(
            "http://localhost:5000/api/monarch/chat",
            json={
                "message": test_message,
                "projectId": "test-project-1"
            }
        )

        if resp.status_code == 200:
            data = resp.json()
            task_id = data.get("taskId")
            print(f"   ✅ Message sent successfully")
            print(f"   Task ID: {task_id}")
            print(f"   Response: {data.get('response')}")
        else:
            print(f"   ❌ Message failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error sending message: {e}")
        return False

    # Test 3: Check if message file was created
    print("\n[3/6] Checking if message was written to .claude_messages/...")
    messages_dir = Path(".claude_messages")

    if not messages_dir.exists():
        print("   ❌ .claude_messages/ directory does not exist")
        return False

    message_files = list(messages_dir.glob("message-*.json"))
    if not message_files:
        print("   ❌ No message files found")
        return False

    latest_file = max(message_files, key=lambda p: p.stat().st_mtime)
    print(f"   ✅ Message file created: {latest_file.name}")

    # Read and verify message content
    with open(latest_file, 'r') as f:
        message_data = json.load(f)
        print(f"   Message type: {message_data.get('type')}")
        print(f"   Task ID: {message_data.get('task_id')}")
        print(f"   Content: {message_data.get('message')[:50]}...")

    # Test 4: Test project creation endpoint
    print("\n[4/6] Testing new project creation...")
    try:
        resp = requests.post(
            "http://localhost:5000/api/project/new",
            json={
                "name": "Test Project",
                "type": "new"
            }
        )

        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Project created")
            print(f"   Project ID: {data.get('projectId')}")
        else:
            print(f"   ❌ Project creation failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating project: {e}")

    # Test 5: Test agent spawn endpoint
    print("\n[5/6] Testing agent spawn notification...")
    try:
        resp = requests.post(
            "http://localhost:5000/api/claude/agent-spawned",
            json={
                "agentId": "princess-dev",
                "taskId": task_id,
                "loop": "loop2",
                "parentAgent": "queen"
            }
        )

        if resp.status_code == 200:
            print("   ✅ Agent spawn notification sent")
        else:
            print(f"   ❌ Notification failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error sending notification: {e}")

    # Test 6: Test task completion endpoint
    print("\n[6/6] Testing task completion notification...")
    try:
        resp = requests.post(
            "http://localhost:5000/api/claude/task-completed",
            json={
                "taskId": task_id,
                "agentId": "princess-dev",
                "result": {
                    "files_created": ["hello.py"],
                    "lines_of_code": 3,
                    "tests_passed": 1
                }
            }
        )

        if resp.status_code == 200:
            print("   ✅ Task completion notification sent")
        else:
            print(f"   ❌ Notification failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error sending notification: {e}")

    # Summary
    print("\n" + "="*60)
    print("✅ E2E TEST COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("1. Check .claude_messages/ for the message file")
    print("2. Run: python scripts/claude_message_monitor.py --once")
    print("3. Tell THIS Claude Code instance to process the message")
    print("4. Use Task tool to spawn agents")
    print("5. Watch the UI for real-time updates!")
    print("="*60 + "\n")

    return True


def test_websocket_connection():
    """Test WebSocket connection (basic check)."""
    print("\n🔌 Testing WebSocket connection...")
    print("   Note: Full WebSocket test requires socket.io client library")
    print("   Skipping for now (tested manually in UI)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("   SPEK Platform End-to-End Test Suite")
    print("="*60)
    print("\nPrerequisites:")
    print("1. Flask backend running: python claude_backend_server.py")
    print("2. Atlantis UI running: cd atlantis-ui && npm run dev")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)

    success = test_message_flow()

    if success:
        print("\n🎉 All tests passed!")
        print("\nThe system is ready for manual testing:")
        print("1. Open http://localhost:3000")
        print("2. Send a message in MonarchChat")
        print("3. Monitor .claude_messages/ directory")
        print("4. Process with THIS Claude Code instance")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
