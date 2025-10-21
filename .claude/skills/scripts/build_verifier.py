#!/usr/bin/env python3
"""
Build Verifier - Atomic Skill Helper Script

Runs build command and validates success, bundle size, and output.
Supports: npm (Next.js, Vite, etc.), Python build systems

VERSION: 1.0.0
USAGE: python build_verifier.py [--framework auto|npm|python] [--max-bundle-mb 10]
"""

import subprocess
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


class BuildVerifier:
    """Atomic skill helper for verifying builds."""

    BUILD_COMMANDS = {
        "npm": "npm run build",
        "next": "npm run build",
        "vite": "npm run build",
        "python": "python setup.py build"
    }

    def __init__(self, framework: str = "auto", max_bundle_mb: float = 10.0, timeout: int = 600):
        self.framework = framework if framework != "auto" else self.detect_framework()
        self.max_bundle_mb = max_bundle_mb
        self.timeout = timeout

    def detect_framework(self) -> str:
        """Auto-detect build framework from project files."""
        if Path("package.json").exists():
            with open("package.json") as f:
                content = f.read()
                if "next" in content:
                    return "next"
                elif "vite" in content:
                    return "vite"
                else:
                    return "npm"

        if Path("setup.py").exists():
            return "python"

        return "npm"  # Fallback

    def get_build_dir(self) -> Optional[Path]:
        """Get build output directory based on framework."""
        if self.framework == "next":
            return Path(".next")
        elif self.framework in ["vite", "npm"]:
            return Path("dist")
        elif self.framework == "python":
            return Path("build")
        return None

    def calculate_bundle_size(self) -> float:
        """Calculate total bundle size in MB."""
        build_dir = self.get_build_dir()
        if not build_dir or not build_dir.exists():
            return 0.0

        total_size = 0
        for file in build_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size

        return total_size / (1024 * 1024)  # Convert to MB

    def check_build_errors(self, stdout: str, stderr: str) -> list:
        """Extract build errors from output."""
        errors = []

        # Common error patterns
        error_patterns = [
            r'ERROR\s+(.+)',
            r'Error:\s+(.+)',
            r'✘\s+(.+)',
            r'Failed to compile',
            r'Module not found',
            r'Cannot find module'
        ]

        combined_output = stdout + stderr

        for pattern in error_patterns:
            matches = re.findall(pattern, combined_output, re.MULTILINE)
            errors.extend(matches)

        return errors[:10]  # Return first 10 errors

    def _build_response(
        self,
        success: bool,
        bundle_too_large: bool,
        exit_code: int,
        bundle_size_mb: float,
        errors: list,
        command: str,
        stdout: str,
        stderr: str
    ) -> Dict[str, Any]:
        """Build response dictionary with recommendation."""
        response = {
            "skill": "build-verifier",
            "success": success and not bundle_too_large,
            "exit_code": exit_code,
            "bundle_size_mb": round(bundle_size_mb, 2),
            "max_bundle_mb": self.max_bundle_mb,
            "bundle_ok": not bundle_too_large,
            "errors": errors,
            "error_count": len(errors),
            "framework": self.framework,
            "command": command,
            "stdout": stdout[:500],
            "stderr": stderr[:500] if stderr else ""
        }

        # Add recommendation
        if success and not bundle_too_large:
            response["recommendation"] = "Build successful ✅ Proceed to next gate"
        elif not success:
            response["recommendation"] = f"Fix {len(errors)} build errors before proceeding"
        elif bundle_too_large:
            response["recommendation"] = f"Bundle size {bundle_size_mb:.1f}MB exceeds {self.max_bundle_mb}MB limit. Optimize bundle."
        else:
            response["recommendation"] = "Build issues detected. Review output."

        return response

    def run(self) -> Dict[str, Any]:
        """Execute build and return structured results."""
        command = self.BUILD_COMMANDS.get(self.framework, "npm run build")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode

            # Calculate bundle size
            bundle_size_mb = self.calculate_bundle_size()

            # Check for errors
            errors = self.check_build_errors(stdout, stderr)

            # Determine success
            success = exit_code == 0 and len(errors) == 0

            # Check bundle size
            bundle_too_large = bundle_size_mb > self.max_bundle_mb

            return self._build_response(
                success, bundle_too_large, exit_code, bundle_size_mb,
                errors, command, stdout, stderr
            )

        except subprocess.TimeoutExpired:
            return {
                "skill": "build-verifier",
                "success": False,
                "error": f"Build exceeded {self.timeout}s timeout",
                "recommendation": "Build taking too long. Check for infinite loops or optimize build process.",
                "framework": self.framework
            }
        except Exception as e:
            return {
                "skill": "build-verifier",
                "success": False,
                "error": str(e),
                "recommendation": f"Fix build execution error: {str(e)}",
                "framework": self.framework
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Verifier - Atomic Skill Helper")
    parser.add_argument("--framework", default="auto", choices=["auto", "npm", "next", "vite", "python"],
                       help="Build framework (default: auto-detect)")
    parser.add_argument("--max-bundle-mb", type=float, default=10.0,
                       help="Maximum bundle size in MB (default: 10)")
    parser.add_argument("--timeout", type=int, default=600,
                       help="Timeout in seconds (default: 600)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    verifier = BuildVerifier(
        framework=args.framework,
        max_bundle_mb=args.max_bundle_mb,
        timeout=args.timeout
    )
    result = verifier.run()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"BUILD VERIFIER - {result['framework'].upper()}")
        print(f"{'='*60}\n")

        if result["success"]:
            print(f"✅ Status: BUILD SUCCESSFUL")
            print(f"📦 Bundle Size: {result.get('bundle_size_mb', 0):.2f} MB")
            print(f"📊 Limit: {result.get('max_bundle_mb', 10):.2f} MB")
            print(f"✅ Bundle OK: Within limit")
        else:
            print(f"❌ Status: BUILD FAILED")
            if result.get('error_count', 0) > 0:
                print(f"❌ Errors: {result['error_count']}")
                print(f"\n❌ Build Errors:")
                for error in result.get('errors', [])[:5]:
                    print(f"   - {error}")
            if result.get('bundle_size_mb', 0) > 0:
                print(f"\n📦 Bundle Size: {result.get('bundle_size_mb', 0):.2f} MB")
                if not result.get('bundle_ok', True):
                    print(f"⚠️  Bundle exceeds {result.get('max_bundle_mb', 10):.2f} MB limit!")

        print(f"\n🔧 Recommendation: {result['recommendation']}\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
