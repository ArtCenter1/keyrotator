#!/usr/bin/env python3
"""
KeyRotator Setup Script

Quick setup for KeyRotator Mission Control.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return False
    print(f"OK: Python {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        print("Installing dependencies...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            )
            print("OK: Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install dependencies")
            return False
    else:
        print("WARNING: requirements.txt not found")
        return False


def create_config_directory():
    """Create config directory if it doesn't exist."""
    config_dir = Path.home() / ".keyrotator"
    config_dir.mkdir(exist_ok=True)
    print(f"OK: Config directory: {config_dir}")
    return True


def main():
    """Main setup function."""
    print("Setting up KeyRotator Mission Control")
    print("=" * 50)

    if not check_python_version():
        return False

    if not install_dependencies():
        return False

    if not create_config_directory():
        return False

    print()
    print("Setup complete!")
    print()
    print("To start KeyRotator:")
    print("  python app.py")
    print()
    print("Then visit: http://localhost:8000/api/dashboard")
    print()
    print("Happy coding!")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
