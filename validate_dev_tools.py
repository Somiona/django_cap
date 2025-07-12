#!/usr/bin/env python3

"""
Development script to validate ruff and ty configuration.
This script tests the linting and type checking setup.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print(f"✓ {description} passed")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ {description} failed")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            return False
    except FileNotFoundError:
        print(f"✗ {description} failed: Command not found")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False


def main():
    """Main function to validate development tools."""
    print("Validating django-cap development tools")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print(
            "Error: pyproject.toml not found. "
            "Run this script from the django_cap directory."
        )
        return 1

    # Test commands
    tests = [
        (["ruff", "--version"], "ruff version check"),
        (["ty", "--version"], "ty version check"),
        (["ruff", "check", "--no-fix", "."], "ruff linting check"),
        (["ruff", "format", "--check", "."], "ruff formatting check"),
        (["ty", "--config-file", "pyproject.toml", "."], "ty type checking"),
    ]

    passed = 0
    failed = 0

    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        print("\nTo install the development tools, run:")
        print("  pip install -e .[dev]")
        print("  # or")
        print("  make dev-setup")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
