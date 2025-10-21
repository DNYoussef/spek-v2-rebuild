"""Quick test of Gemini CLI functionality (Week 6 Day 4)

Tests basic Gemini CLI command execution.
"""

import subprocess
import sys

print("=== Gemini CLI Quick Test ===\n")

# Test 1: Version check
print("[1/2] Checking Gemini CLI version...")
try:
    result = subprocess.run(
        "gemini --version",
        capture_output=True,
        text=True,
        timeout=5,
        shell=True
    )
    print(f"  [OK] Gemini CLI version: {result.stdout.strip()}")
except Exception as e:
    print(f"  [FAIL] Version check failed: {e}")
    sys.exit(1)

# Test 2: Simple prompt (may timeout if interactive)
print("\n[2/2] Testing simple prompt...")
print("  [INFO] Gemini CLI may be interactive - testing with short timeout")

try:
    result = subprocess.run(
        'gemini --prompt "What is 2+2? Answer with just the number."',
        capture_output=True,
        text=True,
        timeout=10,
        shell=True
    )

    if result.returncode == 0:
        response = result.stdout.strip()
        print(f"  [OK] Response: {response[:100]}")
    else:
        print(f"  [WARN] Non-zero exit code: {result.returncode}")
        print(f"  [INFO] stderr: {result.stderr[:200]}")

except subprocess.TimeoutExpired:
    print("  [WARN] Command timed out - CLI may be interactive or waiting for input")
    print("  [INFO] This is expected for some CLI versions")
except Exception as e:
    print(f"  [FAIL] Prompt test failed: {e}")

print("\n=== Test Complete ===")
print("\n[INFO] If CLI is interactive, we'll need to use a different approach for training.")
print("[INFO] Consider using DSPy with a different LM backend (OpenAI, Claude, etc.)")
