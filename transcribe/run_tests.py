#!/usr/bin/env python3
"""
Test runner script for transcribe package
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite"""

    # Change to project directory
    project_dir = Path(__file__).parent

    print("Running transcribe package tests...")
    print(f"Project directory: {project_dir}")
    print("-" * 50)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
    ]

    try:
        result = subprocess.run(cmd, cwd=project_dir, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("uv pip install -e '.[test]'")
        return 1


def run_quick_tests():
    """Run quick tests only (excluding slow/integration tests)"""

    project_dir = Path(__file__).parent

    print("Running quick tests...")
    print("-" * 30)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-m",
        "not slow",
        "--cov=src",
        "--cov-report=term-missing",
        "-v",
    ]

    try:
        result = subprocess.run(cmd, cwd=project_dir, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install test dependencies:")
        print("uv pip install -e '.[test]'")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run transcribe package tests")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick tests only (exclude slow tests)"
    )

    args = parser.parse_args()

    if args.quick:
        exit_code = run_quick_tests()
    else:
        exit_code = run_tests()

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

    sys.exit(exit_code)
