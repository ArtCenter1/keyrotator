#!/usr/bin/env python3
"""
KeyRotator Mission Control

Professional API key management dashboard for development environments.
Manage multiple API keys across providers with automatic rotation and monitoring.

Usage:
    python app.py

Or run directly:
    python -m keyrotator.app
"""

import sys
import os
from pathlib import Path

# Add the keyrotator package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from keyrotator import KeyRotatorApp


def main():
    """Main entry point for KeyRotator."""
    print("🚀 Starting KeyRotator Mission Control...")

    # Create and run the app
    app = KeyRotatorApp()
    app.run()


if __name__ == "__main__":
    main()
